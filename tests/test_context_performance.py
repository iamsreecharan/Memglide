"""Performance pair validation never treats changed or failed evidence as equivalent."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks.context_performance import compare_pairs  # noqa: E402


def row() -> dict:
    return {
        "pair_id": "natural:1",
        "status": "ok",
        "request": {"query": "inventory", "level": 2, "budget": 4000},
        "result": {
            "retrieval_id": "a" * 32,
            "session_id": "b" * 32,
            "estimated_tokens": 100,
            "items": [{"path": "inventory.py", "hash": "digest", "snippet": "return units"}],
            "passport": {"next": "expand_context(" + "a" * 32 + ")"},
        },
    }


def test_equivalence_ignores_only_volatile_request_identifiers() -> None:
    before = row()
    after = deepcopy(before)
    after["result"]["retrieval_id"] = "c" * 32
    after["result"]["session_id"] = "d" * 32
    after["result"]["passport"]["next"] = "expand_context(" + "c" * 32 + ")"
    assert compare_pairs([before], [after])["all_equivalent"]
    after["result"]["items"][0]["hash"] = "changed"
    assert not compare_pairs([before], [after])["all_equivalent"]


@pytest.mark.parametrize(
    "case", ["missing", "failed", "different_request", "duplicate", "no_result"]
)
def test_invalid_pair_cannot_validate_performance_equivalence(case: str) -> None:
    before, after = row(), row()
    old_rows, new_rows = [before], [after]
    if case == "missing":
        new_rows = []
    elif case == "failed":
        after["status"] = "failed"
    elif case == "different_request":
        after["request"]["budget"] = 8000
    elif case == "duplicate":
        old_rows.append(deepcopy(before))
    elif case == "no_result":
        del after["result"]
    assert not compare_pairs(old_rows, new_rows)["all_equivalent"]
