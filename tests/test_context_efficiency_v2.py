"""Request-local source snapshots reduce duplicate work without hiding source edits."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

import memglide.core.context as context_module
from memglide.core.context import ContextEngine, estimate_tokens
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import Database, DomainError


class RepeatedSourceIndex:
    def __init__(self, root: Path):
        self.root = root
        self.candidates = [
            self.candidate("inventory.py", f"reserve_{index}", index * 3 + 1, index * 3 + 2)
            for index in range(8)
        ]

    def candidate(self, path: str, name: str, start: int, end: int) -> dict[str, Any]:
        return {
            "id": name,
            "path": path,
            "name": name,
            "symbol": name,
            "signature": f"def {name}():",
            "start_line": start,
            "end_line": end,
            "hash": hashlib.sha256((self.root / path).read_bytes()).hexdigest(),
            "language": "python",
            "kind": "function",
            "score": 10,
            "reason": "Inventory source",
        }

    def search(self, *_: Any, **__: Any) -> list[dict[str, Any]]:
        return [dict(candidate) for candidate in self.candidates]

    def dependencies(self, *_: Any, **__: Any) -> list[dict[str, Any]]:
        return []

    def get_symbol(self, *_: Any, **__: Any) -> dict[str, Any]:
        raise DomainError("No dependency", 404)


@pytest.fixture
def engine(tmp_path: Path) -> tuple[ContextEngine, str, Path]:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "inventory.py").write_text(
        "\n".join(f"def reserve_{index}():\n    return {index}\n" for index in range(8))
    )
    (root / "ledger.py").write_text("def remaining():\n    return 99\n")
    db = Database(tmp_path / "state/db.sqlite")
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("inventory", str(root), "inventory", time.time()),
    )
    memory = MemoryEngine(db)
    session = memory.start_session("inventory", "inventory correctness")["id"]
    return ContextEngine(db, RepeatedSourceIndex(root), memory), session, root


def normalize(response: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(response).replace(response["retrieval_id"], "<retrieval>"))


def test_snapshot_preserves_all_evidence_and_exact_budget_with_fewer_secure_reads(
    engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    context, session, _ = engine
    original = context_module.read_source
    reads = []

    def read(root: str, path: str, max_size: int) -> tuple[str, str]:
        reads.append(path)
        return original(root, path, max_size)

    monkeypatch.setattr(context_module, "read_source", read)
    result = context.get_context(session, "inventory", level=2, budget=8000)
    assert reads == ["inventory.py", "inventory.py"]
    assert len(result["items"]) == 8
    assert [item["snippet"] for item in result["items"]] == [
        f"def reserve_{index}():\n    return {index}\n" for index in range(8)
    ]
    assert estimate_tokens(result) == result["estimated_tokens"] <= 8000

    # Compare the complete response with uncached reads, not just file coverage.
    def uncached(self: Any, path: str) -> tuple[str, str]:
        return context_module.read_source(self.root, path, self.max_size)

    monkeypatch.setattr(context_module._RequestSources, "read", uncached)
    reads.clear()
    repeated = context.get_context(session, "inventory", level=2, budget=8000)
    assert len(reads) == 9
    assert normalize(result) == normalize(repeated)


@pytest.mark.parametrize("change", ["edit", "same_size_restored_mtime", "delete", "symlink"])
def test_packing_race_removes_obsolete_evidence_and_rebuilds_passport(
    engine: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, change: str
) -> None:
    context, session, root = engine
    context.indexer.candidates.append(context.indexer.candidate("ledger.py", "remaining", 1, 2))
    outside = tmp_path / "outside.py"
    outside.write_text("OUTSIDE SOURCE MUST NEVER BE RETURNED\n")
    original = context_module.read_source
    changed = False

    def read(project_root: str, path: str, max_size: int) -> tuple[str, str]:
        nonlocal changed
        result = original(project_root, path, max_size)
        if path == "ledger.py" and not changed:
            changed = True
            target = root / "inventory.py"
            if change == "edit":
                target.write_text("def changed():\n    return 'new source'\n")
            elif change == "same_size_restored_mtime":
                before = target.stat()
                target.write_text(target.read_text().replace("return 0", "return 9"))
                os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns))
                assert target.stat().st_size == before.st_size
                assert target.stat().st_mtime_ns == before.st_mtime_ns
            else:
                target.unlink()
                if change == "symlink":
                    target.symlink_to(outside)
        return result

    monkeypatch.setattr(context_module, "read_source", read)
    result = context.get_context(session, "inventory", level=2, budget=8000)
    assert {item["path"] for item in result["items"]} == {"ledger.py"}
    passport = result["passport"]
    assert passport["status"] == "Partial"
    assert result["truncated"]
    assert [source["path"] for source in passport["selected_files"]] == ["ledger.py"]
    assert {source["path"] for source in passport["selected_symbols"]} == {"ledger.py"}
    assert set(passport["verified_source_hashes"]) == {"ledger.py"}
    assert any("inventory.py; reindex and retry" in warning for warning in result["warnings"])
    assert "OUTSIDE SOURCE" not in json.dumps(result)
    assert estimate_tokens(result) == result["estimated_tokens"] <= 8000
    stored = context.get_passport(session, result["retrieval_id"])
    assert stored == passport


def test_new_requests_never_reuse_previous_source_snapshot(engine: Any) -> None:
    context, session, root = engine
    first = context.get_context(session, "inventory", level=2, budget=8000)
    original_hash = first["items"][0]["hash"]
    source = root / "inventory.py"
    source.write_text(source.read_text().replace("return 0", "return 100"))
    outdated = context.get_context(session, "inventory", level=2, budget=8000)
    assert outdated["items"] == []
    assert any("Source changed" in warning for warning in outdated["warnings"])
    context.indexer = RepeatedSourceIndex(root)
    current = context.get_context(session, "inventory", level=2, budget=8000)
    assert current["items"][0]["hash"] != original_hash
    assert "return 100" in current["items"][0]["snippet"]
    assert context.get_passport(session, first["retrieval_id"])["status"] == "Stale"


def test_each_candidate_still_requires_its_own_matching_indexed_hash(engine: Any) -> None:
    context, session, _ = engine
    context.indexer.candidates[1]["hash"] = "0" * 64
    result = context.get_context(session, "inventory", level=2, budget=8000)
    assert "reserve_1" not in {item["symbol"] for item in result["items"]}
    assert len(result["items"]) == 7
    assert any("Source changed" in warning for warning in result["warnings"])


def test_full_source_budget_fallback_preserves_original_structural_range(
    engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    context, session, root = engine
    source = root / "inventory.py"
    source.write_text(source.read_text() + "# extensive implementation\n" * 600)
    context.indexer = RepeatedSourceIndex(root)
    context.indexer.candidates = context.indexer.candidates[:1]
    original = context_module.read_source
    reads = []

    def read(project_root: str, path: str, max_size: int) -> tuple[str, str]:
        reads.append(path)
        return original(project_root, path, max_size)

    monkeypatch.setattr(context_module, "read_source", read)
    result = context.get_context(session, "inventory", level=3, budget=1600)
    assert reads == ["inventory.py", "inventory.py"]
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["snippet"] == ""
    assert item["start_line"] == 1 and item["end_line"] == 2
    assert item["full_source"] is False
    assert "implementation omitted by token budget" in item["reason"]
    assert estimate_tokens(result) == result["estimated_tokens"] <= 1600


def test_changed_source_also_removes_selected_source_backed_memory(
    engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    context, session, root = engine
    memory = context.memory.save_memory(
        session,
        "verified_fix",
        "Inventory reserve_0 currently returns zero.",
        "Independent fixture assertion",
        [{"path": "inventory.py"}],
    )
    original = context._build_passport
    changed = False

    def passport(*args: Any, **kwargs: Any) -> None:
        nonlocal changed
        original(*args, **kwargs)
        if args[0]["memories"] and not changed:
            changed = True
            (root / "inventory.py").write_text("def reserve_0():\n    return 10\n")

    monkeypatch.setattr(context, "_build_passport", passport)
    result = context.get_context(session, "inventory", level=2, budget=8000)
    assert changed
    assert result["items"] == []
    assert result["memories"] == []
    assert memory["id"] not in result["passport"]["selected_memory_ids"]
    assert result["passport"]["selected_files"] == []
    assert result["passport"]["verified_source_hashes"] == {}
    assert result["passport"]["status"] == "Partial"
    assert estimate_tokens(result) == result["estimated_tokens"]


def test_request_snapshot_memory_is_bounded(engine: Any) -> None:
    context, _, root = engine
    # The cap concerns additional snapshots; secure reads still enforce the
    # configured source-size policy for files that are not retained in it.
    sources = context_module._RequestSources(str(root), context.db.settings()["max_file_size"])
    sources.cached_bytes = 8 * 1024 * 1024
    assert sources.read("inventory.py")[0].startswith("def reserve_0")
    assert sources.contents == {}
    sources.clear()
    assert sources.cached_bytes == 0


def file_candidate(index: RepeatedSourceIndex, path: str) -> dict[str, Any]:
    return {
        **index.candidate(path, path, 1, len((index.root / path).read_text().splitlines())),
        "kind": "file",
    }


def test_small_exception_does_not_block_complete_parent_file_body(engine: Any) -> None:
    context, session, root = engine
    source = root / "inventory.py"
    source.write_text(
        "class ConflictError(Exception):\n    pass\n\n"
        "class Repository:\n"
        "    def update(self, expected_revision):\n"
        "        if expected_revision != self.revision:\n"
        "            raise ConflictError('revision conflict')\n"
        "        self.revision += 1\n"
    )
    index = RepeatedSourceIndex(root)
    index.candidates = [
        {
            **index.candidate("inventory.py", "ConflictError", 1, 2),
            "kind": "class",
            "score": 50,
        },
        file_candidate(index, "inventory.py"),
    ]
    context.indexer = index
    result = context.get_context(session, "inventory", level=2, budget=4000)
    assert len(result["items"]) == 1
    assert result["items"][0]["snippet"] == source.read_text()
    assert "def update(self, expected_revision):" in result["items"][0]["snippet"]
    assert result["passport"]["selected_symbols"][0]["end_line"] == 8
    assert estimate_tokens(result) == result["estimated_tokens"] <= 4000


def test_complete_superset_replaces_multiple_contained_units_without_duplicate_code(
    engine: Any,
) -> None:
    context, session, root = engine
    context.indexer.candidates = [
        *[{**candidate, "score": 50} for candidate in context.indexer.candidates[:2]],
        file_candidate(context.indexer, "inventory.py"),
    ]
    result = context.get_context(session, "inventory", level=2, budget=8000)
    assert len(result["items"]) == 1
    assert result["items"][0]["snippet"] == (root / "inventory.py").read_text()
    assert result["items"][0]["snippet"].count("def reserve_0") == 1
    assert not result["truncated"]
    assert len(result["passport"]["selected_symbols"]) == 1


def test_superset_that_exceeds_budget_leaves_existing_body_and_passport_intact(engine: Any) -> None:
    context, session, root = engine
    source = root / "inventory.py"
    source.write_text(source.read_text() + "# extensive irrelevant implementation\n" * 600)
    index = RepeatedSourceIndex(root)
    first = {**index.candidates[0], "score": 50}
    index.candidates = [first]
    context.indexer = index
    baseline = context.get_context(session, "inventory", level=2, budget=1600)
    index.candidates.append(file_candidate(index, "inventory.py"))
    result = context.get_context(session, "inventory", level=2, budget=1600)
    assert result["items"] == baseline["items"]
    assert result["passport"]["selected_files"] == baseline["passport"]["selected_files"]
    assert result["passport"]["selected_symbols"] == baseline["passport"]["selected_symbols"]
    assert (
        result["passport"]["verified_source_hashes"]
        == baseline["passport"]["verified_source_hashes"]
    )
    assert "extensive irrelevant" not in result["items"][0]["snippet"]
    assert result["truncated"]
    assert any("Budget omitted 1" in warning for warning in result["warnings"])
    assert estimate_tokens(result) == result["estimated_tokens"] <= 1600


@pytest.mark.parametrize("outer,inner", [((1, 8), (3, 5)), ((1, 5), (4, 8)), ((1, 5), (1, 5))])
def test_contained_equal_and_partial_overlaps_do_not_duplicate_or_discard_existing_lines(
    engine: Any, outer: tuple[int, int], inner: tuple[int, int]
) -> None:
    context, session, _ = engine
    index = context.indexer
    index.candidates = [
        index.candidate("inventory.py", "existing", *outer),
        index.candidate("inventory.py", "later", *inner),
    ]
    result = context.get_context(session, "inventory", level=2, budget=8000)
    assert len(result["items"]) == 1
    assert result["items"][0]["symbol"] == "existing"
    assert (result["items"][0]["start_line"], result["items"][0]["end_line"]) == outer
    assert estimate_tokens(result) == result["estimated_tokens"] <= 8000


def test_edit_during_superset_trial_is_rejected_by_final_source_verification(
    engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    context, session, root = engine
    context.indexer.candidates = [
        {**context.indexer.candidates[0], "score": 50},
        file_candidate(context.indexer, "inventory.py"),
    ]
    original = context._build_passport
    changed = False

    def passport(*args: Any, **kwargs: Any) -> None:
        nonlocal changed
        original(*args, **kwargs)
        if any(item["kind"] == "file" for item in args[0]["items"]) and not changed:
            changed = True
            (root / "inventory.py").write_text("def changed():\n    return 9\n")

    monkeypatch.setattr(context, "_build_passport", passport)
    result = context.get_context(session, "inventory", level=2, budget=4000)
    assert changed
    assert result["items"] == []
    assert result["passport"]["selected_files"] == []
    assert result["passport"]["verified_source_hashes"] == {}
    assert result["passport"]["status"] == "Partial"
    assert estimate_tokens(result) == result["estimated_tokens"] <= 4000
