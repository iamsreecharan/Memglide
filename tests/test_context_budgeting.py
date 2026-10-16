"""Source evidence stays useful when dependency graphs have large fan-out."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import pytest

from memglide.core.context import ContextEngine, estimate_tokens
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import Database, DomainError


class WarehouseIndex:
    def __init__(self, root: Path, *, references: int = 80):
        self.root = root
        self.references = references

    def candidate(self, path: str, name: str, score: int) -> dict[str, Any]:
        text = (self.root / path).read_text()
        return {
            "id": name,
            "path": path,
            "name": name,
            "symbol": name,
            "signature": f"def {name}(units):",
            "start_line": 1,
            "end_line": len(text.splitlines()),
            "hash": hashlib.sha256(text.encode()).hexdigest(),
            "language": "python",
            "kind": "function",
            "score": score,
            "reason": "Matched inventory reservation",
        }

    def search(self, project_id: str, query: str, limit: int = 20) -> list[dict[str, Any]]:
        return [
            self.candidate("quota.py", "reserve_units", 50),
            self.candidate("ledger.py", "available_units", 10),
        ]

    def dependencies(
        self, project_id: str, key: str, direction: str = "both", *, refresh: bool = True
    ) -> list[dict[str, Any]]:
        return [
            {
                "source_file": "quota.py",
                "source_symbol": "reserve_units",
                "target_file": None,
                "target_symbol": None,
                "kind": "call",
                # Prefixes deliberately match: IDs must represent the full text.
                "reference": "inventory_registry.resolve("
                + "nested_expression, " * 250
                + str(i)
                + ")",
                "resolved": False,
            }
            for i in range(self.references)
        ]

    def get_symbol(self, project_id: str, key: str, *, refresh: bool = True) -> dict[str, Any]:
        raise DomainError("No independently resolved neighbor", 404)


@pytest.fixture
def warehouse(tmp_path: Path) -> tuple[ContextEngine, str, WarehouseIndex]:
    root = tmp_path / "warehouse"
    root.mkdir()
    (root / "quota.py").write_text(
        "def reserve_units(units):\n    available = units - 2\n    return max(0, available)\n"
    )
    (root / "ledger.py").write_text("def available_units(units):\n    return units + 1\n")
    db = Database(tmp_path / "state/db.sqlite")
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("warehouse", str(root), "warehouse", time.time()),
    )
    memory = MemoryEngine(db)
    index = WarehouseIndex(root)
    session = memory.start_session("warehouse", "inventory reservation correctness")["id"]
    return ContextEngine(db, index, memory), session, index


def test_large_graph_cannot_displace_direct_source(warehouse: Any) -> None:
    context, session, _ = warehouse
    result = context.get_context(session, "inventory reservation", level=2, budget=1800)
    assert [item["path"] for item in result["items"]] == ["quota.py", "ledger.py"]
    assert "return max(0, available)" in result["items"][0]["snippet"]
    assert "return units + 1" in result["items"][1]["snippet"]
    summary = result["passport"]["dependency_summary"]
    assert summary["total_references"] == 80
    assert summary["omitted_references"] > 0
    assert summary["estimated_graph_tokens"] <= summary["graph_token_budget"]
    assert result["passport"]["status"] == "Partial"
    assert any("get_dependencies" in warning for warning in result["warnings"])
    assert estimate_tokens(result) == result["estimated_tokens"] <= 1800


def test_previews_are_bounded_identifiable_and_budget_all_serialized_copies(warehouse: Any) -> None:
    context, session, index = warehouse
    # Give the requested implementations enough substance for graph previews to
    # earn a useful allowance; raising the requested budget alone is insufficient.
    for path in ("quota.py", "ledger.py"):
        source = index.root / path
        source.write_text(source.read_text() + "    # inventory consistency documentation\n" * 80)
    result = context.get_context(session, "inventory reservation", level=2, budget=12000)
    deps = result["dependencies"]
    assert len(deps) >= 2
    assert len({dep["id"] for dep in deps}) == len(deps)
    assert all(len(dep["reference"]) <= 160 for dep in deps)
    assert all(dep["preview_truncated_fields"] == ["reference"] for dep in deps)
    assert all(dep["reference_length"] > 4000 for dep in deps)
    passport = result["passport"]
    assert deps == passport["dependencies"] == passport["unresolved_dependencies"]
    summary = passport["dependency_summary"]
    assert summary["truncated_previews"] == len(deps)
    assert summary["estimated_graph_tokens"] <= summary["graph_token_budget"] == 1200
    # The graph allowance counts all three copies, rather than counting one
    # Python object and overlooking serialization in the embedded passport.
    assert estimate_tokens(deps) * 3 < summary["estimated_graph_tokens"]
    repeated = context.get_context(session, "inventory reservation", level=2, budget=12000)
    assert [dep["id"] for dep in repeated["dependencies"]] == [dep["id"] for dep in deps]
    assert estimate_tokens(result) == result["estimated_tokens"]


def test_large_budget_does_not_inflate_small_source_answer_with_graph(warehouse: Any) -> None:
    context, session, _ = warehouse
    result = context.get_context(session, "inventory reservation", level=2, budget=12000)
    summary = result["passport"]["dependency_summary"]
    assert summary["graph_token_budget"] <= 512
    assert summary["estimated_graph_tokens"] < result["estimated_tokens"] * 0.4
    assert all(item["snippet"] for item in result["items"])


def test_reference_collection_reports_more_than_previous_hundred_cap(warehouse: Any) -> None:
    context, session, index = warehouse
    index.references = 143
    result = context.get_context(session, "inventory reservation", level=2, budget=4000)
    summary = result["passport"]["dependency_summary"]
    assert summary["total_references"] == 143
    assert summary["returned_references"] + summary["omitted_references"] == 143
    assert summary["unresolved_references"] == 143


@pytest.mark.parametrize("budget", [1000, 1600, 4000])
def test_small_budgets_include_complete_metadata_and_omission_notices(
    warehouse: Any, budget: int
) -> None:
    context, session, _ = warehouse
    result = context.get_context(session, "inventory reservation", level=2, budget=budget)
    assert estimate_tokens(result) == result["estimated_tokens"] <= budget
    assert result["passport"]["estimated_tokens_returned"] == result["estimated_tokens"]
    assert result["passport"]["status"] == "Partial"
    summary = result["passport"]["dependency_summary"]
    assert summary["estimated_graph_tokens"] <= summary["graph_token_budget"]
    assert summary["omitted_references"]
    assert any("partial" in warning for warning in result["warnings"])


def test_tests_share_the_graph_cap_and_disclose_omissions(warehouse: Any) -> None:
    context, session, index = warehouse
    index.references = 0
    for i in range(50):
        path = f"tests/test_quota_inventory_{i:02d}.py"
        (index.root / "tests").mkdir(exist_ok=True)
        (index.root / path).write_text("def test_reservation():\n    assert True\n")
        context.db.execute(
            "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
            (f"test-{i}", "warehouse", path, "hash", "python", 1, 0, 1, None, 0),
        )
    result = context.get_context(session, "inventory reservation", level=2, budget=1800)
    passport = result["passport"]
    summary = passport["dependency_summary"]
    assert summary["omitted_related_tests"] > 0
    assert len(passport["related_tests"]) + summary["omitted_related_tests"] == 50
    assert summary["estimated_graph_tokens"] <= summary["graph_token_budget"]
    assert all(item["snippet"] for item in result["items"])
    assert passport["status"] == "Partial"
