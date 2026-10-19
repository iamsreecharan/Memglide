"""Safe failure categories distinguish unavailable work from successful discovery."""

from __future__ import annotations

import sqlite3

import pytest
from test_auto_preload import repository as repository

from memglide.core.indexer import Indexer
from memglide.integrations.auto_preload import prepare_task_prompt


@pytest.mark.parametrize(
    ("code", "reason"),
    [(sqlite3.SQLITE_INTERRUPT, "index_refresh_query_budget"),
     (sqlite3.SQLITE_BUSY, "index_refresh_database_locked"),
     (sqlite3.SQLITE_LOCKED, "index_refresh_database_locked"),
     (sqlite3.SQLITE_CORRUPT, "index_refresh_database_unavailable")],
)
def test_runtime_sqlite_failure_is_typed_without_exception_details(repository, monkeypatch, code, reason):
    _, db, project = repository

    def fail(*args, **kwargs):
        error = sqlite3.OperationalError("PRIVATE SQL SECRET /private/example")
        error.sqlite_errorcode = code
        raise error

    monkeypatch.setattr(Indexer, "reindex", fail)
    prompt = "Correct retry delay handling for negative attempts."
    result = prepare_task_prompt(
        prompt, db_path=db.path, project_id=project, enabled=True, selection_policy="v3",
    )
    assert result["reason"] == reason
    assert result["prompt"] == prompt and result["files"] == []
    assert result["automatic_selection"]["decision"] == "SKIP"
    assert result["automatic_selection"]["auxiliary_model_calls"] == 0
    assert "PRIVATE" not in str(result)
    assert "/private" not in str(result)


@pytest.mark.parametrize("policy", ["v1", "v2"])
def test_older_failure_receipts_keep_their_contract(repository, monkeypatch, policy):
    _, db, project = repository

    def fail(*args, **kwargs):
        raise sqlite3.OperationalError("private")

    monkeypatch.setattr(Indexer, "reindex", fail)
    prompt = "Correct retry delay handling for negative attempts."
    result = prepare_task_prompt(
        prompt, db_path=db.path, project_id=project, enabled=True, selection_policy=policy,
    )
    assert result["prompt"] == prompt and result["files"] == []
    assert result["reason"] == "discovery_unavailable"
