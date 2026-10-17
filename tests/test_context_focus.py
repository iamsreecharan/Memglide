"""Focused level-2 packing respects explicit intent and reports omitted breadth."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import pytest

from memglide.core.context import ContextEngine, estimate_tokens
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import Database, DomainError


class AllocationIndex:
    def __init__(self, root: Path):
        self.root = root
        self.with_dependency = False
        self.candidates = []
        for number in range(8):
            path = f"allocation_{number}.py"
            text = (
                f"def reserve_slot_{number}():\n    return {number}\n\n"
                f"def release_slot_{number}():\n    return -{number}\n"
            )
            (root / path).write_text(text)
            for name, start, end in (
                (f"reserve_slot_{number}", 1, 2),
                (f"release_slot_{number}", 4, 5),
            ):
                self.candidates.append(self.candidate(path, name, start, end, 100 - number))
        (root / "outside.py").write_text(
            "def outside_dependency():\n    return 'verified neighbor'\n"
        )

    def candidate(self, path: str, name: str, start: int, end: int, score: int) -> dict[str, Any]:
        return {
            "id": name,
            "path": path,
            "name": name,
            "symbol": name,
            "start_line": start,
            "end_line": end,
            "hash": hashlib.sha256((self.root / path).read_bytes()).hexdigest(),
            "score": score,
            "reason": "Matching allocation behavior",
        }

    def search(self, *_: Any, **__: Any) -> list[dict[str, Any]]:
        return [dict(candidate) for candidate in self.candidates]

    def dependencies(self, *args: Any, **__: Any) -> list[dict[str, Any]]:
        if not self.with_dependency:
            return []
        return [
            {
                "source_file": "allocation_0.py",
                "source_symbol": "reserve_slot_0",
                "target_file": "outside.py",
                "target_symbol": "outside_dependency",
                "kind": "call",
                "reference": "outside_dependency()",
                "resolved": True,
            }
        ]

    def get_symbol(self, _: str, key: str, **__: Any) -> dict[str, Any]:
        if key in {"outside.py", "outside_dependency"}:
            return self.candidate("outside.py", "outside_dependency", 1, 2, 0)
        for candidate in self.candidates:
            if key in {candidate["id"], candidate["path"]}:
                return dict(candidate)
        raise DomainError("Unknown allocation source", 404)


@pytest.fixture
def allocation(tmp_path: Path) -> tuple[ContextEngine, str, AllocationIndex]:
    root = tmp_path / "allocation"
    root.mkdir()
    db = Database(tmp_path / "state.sqlite")
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("allocation", str(root), "allocation", time.time()),
    )
    memory = MemoryEngine(db)
    session = memory.start_session("allocation", "inventory allocation behavior")["id"]
    index = AllocationIndex(root)
    return ContextEngine(db, index, memory), session, index


def paths(response: dict[str, Any]) -> set[str]:
    return {item["path"] for item in response["items"]}


def test_focus_keeps_all_nonoverlapping_symbols_in_four_primary_files(allocation: Any) -> None:
    engine, session, index = allocation
    result = engine.get_context(session, "Fix inventory allocation behavior", level=2, budget=20000)
    assert paths(result) == {f"allocation_{number}.py" for number in range(4)}
    assert len(result["items"]) == 8
    assert result["truncated"]
    assert result["passport"]["status"] == "Partial"
    warnings = [value for value in result["warnings"] if "Focused level 2" in value]
    assert len(warnings) == 1
    assert "omitted 4 primary candidate file(s)" in warnings[0]
    assert "exact symbol/path" in warnings[0] and "level 3" in warnings[0]
    assert len(warnings[0]) < 240
    assert estimate_tokens(result) == result["estimated_tokens"] <= result["budget"]
    for path, digest in result["passport"]["verified_source_hashes"].items():
        assert digest == hashlib.sha256((index.root / path).read_bytes()).hexdigest()


@pytest.mark.parametrize("kind", ["path", "symbol"])
def test_more_than_four_explicit_file_or_symbol_anchors_survive(allocation: Any, kind: str) -> None:
    engine, session, _ = allocation
    query = "Fix " + ", ".join(
        f"allocation_{number}.py" if kind == "path" else f"reserve_slot_{number}()"
        for number in range(1, 7)
    )
    result = engine.get_context(session, query, level=2, budget=20000)
    assert paths(result) == {f"allocation_{number}.py" for number in range(1, 7)}
    assert len(result["items"]) == 12
    assert any("omitted 2 primary" in warning for warning in result["warnings"])


def test_explicit_low_rank_file_reserves_slot_within_four_file_selection(allocation: Any) -> None:
    engine, session, _ = allocation
    result = engine.get_context(
        session, "Fix allocation_7.py and inventory behavior", level=2, budget=20000
    )
    assert paths(result) == {
        "allocation_0.py",
        "allocation_1.py",
        "allocation_2.py",
        "allocation_7.py",
    }


def test_resolved_caller_anchor_is_kept_even_when_query_lacks_broad_keywords(
    allocation: Any,
) -> None:
    engine, session, index = allocation
    index.candidates[-1]["reason"] = "resolved caller of requested symbol"
    result = engine.get_context(session, "Fix inventory allocation behavior", level=2, budget=20000)
    assert "allocation_7.py" in paths(result)
    assert len(paths(result)) == 4


@pytest.mark.parametrize(
    "query",
    [
        "Show all files for inventory allocation",
        "Inspect every relevant implementation for allocation",
        "List callers of reserve_slot_0",
        "Find references to reserve_slot_0",
        "Find a reference to reserve_slot_0",
        "Inspect call sites for allocation behavior",
        "Show dependencies for inventory allocation",
        "Search broadly for allocation behavior",
        "Inspect allocation across the repository",
    ],
)
def test_explicit_broad_requests_bypass_primary_focus(allocation: Any, query: str) -> None:
    engine, session, _ = allocation
    result = engine.get_context(session, query, level=2, budget=20000)
    assert len(paths(result)) == 8
    assert not any("Focused level 2" in warning for warning in result["warnings"])


@pytest.mark.parametrize("level", [1, 3])
def test_discovery_and_full_source_levels_keep_all_primary_files(
    allocation: Any, level: int
) -> None:
    engine, session, _ = allocation
    result = engine.get_context(
        session, "Fix inventory allocation behavior", level=level, budget=20000
    )
    assert len(paths(result)) == 8
    assert not any("Focused level 2" in warning for warning in result["warnings"])
    assert estimate_tokens(result) == result["estimated_tokens"] <= 20000


def test_recorded_session_changes_are_not_cut_to_four_files(allocation: Any) -> None:
    engine, session, _ = allocation
    for number in range(8):
        engine.db.event("allocation", session, "file_changed", {"path": f"allocation_{number}.py"})
    result = engine.get_context(session, "What changed in this session?", level=2, budget=20000)
    assert len(paths(result)) == len(result["session_events"]) == 8
    assert not any("Focused level 2" in warning for warning in result["warnings"])


def test_resolved_dependency_outside_primary_selection_is_still_expanded(allocation: Any) -> None:
    engine, session, index = allocation
    index.with_dependency = True
    result = engine.get_context(session, "Fix inventory allocation behavior", level=2, budget=20000)
    assert paths(result) == {f"allocation_{number}.py" for number in range(4)} | {"outside.py"}
    outside = next(item for item in result["items"] if item["path"] == "outside.py")
    assert outside["snippet"] == "def outside_dependency():\n    return 'verified neighbor'\n"
    assert outside["reason"] == "Resolved dependency of a selected candidate"
    assert outside["hash"] == hashlib.sha256((index.root / "outside.py").read_bytes()).hexdigest()


def test_focused_selection_preserves_budget_and_passport_staleness(allocation: Any) -> None:
    engine, session, index = allocation
    result = engine.get_context(session, "Fix inventory allocation behavior", level=2, budget=1800)
    assert result["items"]
    assert estimate_tokens(result) == result["estimated_tokens"] <= 1800
    assert result["truncated"] and result["passport"]["status"] == "Partial"
    changed = result["items"][0]["path"]
    (index.root / changed).write_text("# concurrent source edit\n")
    passport = engine.get_passport(session, result["retrieval_id"])
    assert passport["status"] == "Stale" and changed in passport["stale_files"]


@pytest.mark.parametrize(
    "query", ["Inspect inventory allocation behavior", "inventory allocation behavior"]
)
def test_unclassified_query_keeps_implementations_behind_documentation(
    allocation: Any, query: str
) -> None:
    engine, session, index = allocation
    documentation = []
    for number in range(6):
        path = f"docs/allocation_guide_{number}.md"
        (index.root / path).parent.mkdir(exist_ok=True)
        (index.root / path).write_text(
            "# Inventory allocation overview\nDocumentation is supporting evidence.\n"
        )
        candidate = index.candidate(path, Path(path).name, 1, 2, 200 - number)
        candidate["kind"] = "file"
        documentation.append(candidate)
    index.candidates = [*documentation, *index.candidates]
    result = engine.get_context(session, query, level=2, budget=50000)
    assert {f"allocation_{number}.py" for number in range(8)} <= paths(result)
    assert len(paths(result)) == 14
    assert not any("Focused level 2" in warning for warning in result["warnings"])
    assert estimate_tokens(result) == result["estimated_tokens"] <= 50000


@pytest.mark.parametrize("kind", ["file", None])
def test_explicit_full_path_does_not_anchor_other_synthetic_file_basenames(
    allocation: Any, kind: str | None
) -> None:
    engine, session, index = allocation
    candidates = []
    for number in range(8):
        path = f"features/tenant_{number}/service.py"
        (index.root / path).parent.mkdir(parents=True, exist_ok=True)
        (index.root / path).write_text(f"def calculate_limit_{number}():\n    return {number}\n")
        candidate = index.candidate(path, "service.py", 1, 2, 100 - number)
        if kind:
            candidate["kind"] = kind
        candidates.append(candidate)
    index.candidates = candidates
    result = engine.get_context(
        session, "Fix quota calculations in features/tenant_7/service.py", level=2, budget=20000
    )
    assert paths(result) == {f"features/tenant_{number}/service.py" for number in [0, 1, 2, 7]}
    assert any("omitted 4 primary" in warning for warning in result["warnings"])
    for item in result["items"]:
        assert item["hash"] == hashlib.sha256((index.root / item["path"]).read_bytes()).hexdigest()
