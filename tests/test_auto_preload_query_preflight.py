"""Reject ineligible v4 queries before opening or refreshing project state."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations import auto_preload, preload


def oversized_query(count: int = 65) -> str:
    return " ".join(f"lexeme{index:03d}" for index in range(count))


@pytest.mark.parametrize(
    "query", [oversized_query(), "x" * 129], ids=["too-many-terms", "too-long-term"]
)
def test_ineligible_v4_query_never_opens_or_refreshes_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, query: str
) -> None:
    database = tmp_path / "state.db"
    database.touch()

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("ineligible query accessed project state")

    monkeypatch.setattr(preload, "_selection", forbidden)
    monkeypatch.setattr(auto_preload, "_preflight", forbidden)
    monkeypatch.setattr(auto_preload, "_existing_database", forbidden)
    monkeypatch.setattr(sqlite3, "connect", forbidden)
    monkeypatch.setattr(Indexer, "reindex", forbidden)
    result = auto_preload.prepare_task_prompt(
        query, enabled=True, selection_policy="v4", project_id="p", db_path=database
    )
    assert result["reason"] == "insufficient_task_evidence"
    assert result["mode"] == "passthrough"
    assert result["prompt"] == query
    assert result["files"] == []
    receipt = result["automatic_selection"]
    assert receipt["index_refreshed"] is False
    assert receipt["index_refresh_wall_seconds"] == 0
    assert receipt["retrieval_wall_seconds"] == 0
    assert receipt["source_preparation_wall_seconds"] == 0
    assert receipt["auxiliary_model_calls"] == 0
    assert database.read_bytes() == b""


def test_ineligible_v4_query_does_not_probe_missing_database(tmp_path: Path) -> None:
    database = tmp_path / "absent" / "state.db"
    result = auto_preload.prepare_task_prompt(
        oversized_query(), enabled=True, selection_policy="v4", project_id="p", db_path=database
    )
    assert result["reason"] == "insufficient_task_evidence"
    assert not database.parent.exists()


class ReachedProjectState(Exception):
    pass


@pytest.mark.parametrize(
    "query", [oversized_query(64), "x" * 128], ids=["max-terms", "max-term-length"]
)
def test_exact_v4_bounds_remain_eligible_for_state_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, query: str
) -> None:
    database = tmp_path / "state.db"
    database.touch()

    def reached(*args: Any, **kwargs: Any) -> Any:
        raise ReachedProjectState

    monkeypatch.setattr(preload, "_selection", reached)
    with pytest.raises(ReachedProjectState):
        auto_preload.prepare_task_prompt(
            query, enabled=True, selection_policy="v4", project_id="p", db_path=database
        )


@pytest.mark.parametrize("policy", ["v1", "v2", "v3"])
def test_prior_policies_keep_their_state_access_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, policy: str
) -> None:
    database = tmp_path / "state.db"
    database.touch()

    def reached(*args: Any, **kwargs: Any) -> Any:
        raise ReachedProjectState

    monkeypatch.setattr(preload, "_selection", reached)
    with pytest.raises(ReachedProjectState):
        auto_preload.prepare_task_prompt(
            oversized_query(), enabled=True, selection_policy=policy, project_id="p", db_path=database
        )
