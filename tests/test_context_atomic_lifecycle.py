"""Retrieval evidence commits only while its owning session is active."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterator

import pytest

from memglide.service import Service
from memglide.storage.database import DomainError


@pytest.fixture
def lifecycle(tmp_path: Path) -> Iterator[tuple[Service, str]]:
    repo = tmp_path / "repository"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "module.py").write_text("def verify():\n    return True\n")
    service = Service(tmp_path / "state" / "memglide.db")
    project = service.indexer.add_project(str(repo))
    session = service.memory.start_session(project["id"], "verify")
    try:
        yield service, session["id"]
    finally:
        service.close()


def session_row(service: Service, session_id: str) -> dict[str, Any] | None:
    return service.db.one("SELECT * FROM sessions WHERE id=?", (session_id,))


def assert_no_evidence(service: Service) -> None:
    assert service.db.rows("SELECT * FROM retrievals") == []
    assert service.db.rows("SELECT * FROM passports") == []
    assert service.db.rows("SELECT * FROM events WHERE type='context_retrieved'") == []


@pytest.mark.parametrize("transition", ["end", "expire"])
def test_transition_before_final_evidence_gate_cannot_commit_or_renew(
    lifecycle: tuple[Service, str], monkeypatch: pytest.MonkeyPatch, transition: str
) -> None:
    service, session_id = lifecycle
    original_gate = service.memory._active_write
    calls = 0
    state_after_transition = None

    @contextmanager
    def transition_before_gate(*args: Any, **kwargs: Any):
        nonlocal calls, state_after_transition
        calls += 1
        # The first gate is the existing explicit memory recall activity. The
        # second is publication after source capture and freshness validation.
        if calls == 2:
            if transition == "end":
                service.memory.end_session(session_id)
            else:
                service.db.execute("UPDATE sessions SET expires_at=0 WHERE id=?", (session_id,))
            state_after_transition = session_row(service, session_id)
        with original_gate(*args, **kwargs) as transaction:
            yield transaction

    monkeypatch.setattr(service.memory, "_active_write", transition_before_gate)
    with pytest.raises(DomainError, match="ended" if transition == "end" else "expired") as error:
        service.context.get_context(session_id, "verify", 2, 8000)
    assert error.value.status == 410
    assert state_after_transition is not None
    assert session_row(service, session_id) == state_after_transition
    assert_no_evidence(service)
    # Failed gates release their write lock so later local work can proceed.
    service.db.execute("UPDATE sessions SET task='still writable' WHERE id=?", (session_id,))


class ConnectionProxy:
    def __init__(self, connection: sqlite3.Connection, before_execute: Any):
        self.connection = connection
        self.before_execute = before_execute

    def execute(self, sql: str, parameters: Any = ()):
        self.before_execute(self.connection, sql)
        return self.connection.execute(sql, parameters)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.connection, name)


@pytest.mark.parametrize("transition", ["end", "expire"])
def test_competing_lifecycle_write_cannot_slip_between_validation_and_insert(
    lifecycle: tuple[Service, str], monkeypatch: pytest.MonkeyPatch, transition: str
) -> None:
    service, session_id = lifecycle
    original_connect = service.db.connect
    observed = []

    def compete(connection: sqlite3.Connection, sql: str) -> None:
        if not sql.startswith("INSERT INTO retrievals"):
            return
        # Use a real second SQLite connection with no wait, making the race
        # deterministic. Before the fix it could end/expire the session here;
        # the atomic gate now owns the write lock through evidence publication.
        assert connection.in_transaction
        with closing(sqlite3.connect(service.db.path, timeout=0)) as rival:
            rival.execute("PRAGMA busy_timeout=0")
            update = "ended_at=1" if transition == "end" else "expires_at=0"
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                rival.execute(f"UPDATE sessions SET {update} WHERE id=?", (session_id,))
        observed.append(transition)

    @contextmanager
    def connect():
        with original_connect() as connection:
            yield ConnectionProxy(connection, compete)

    monkeypatch.setattr(service.db, "connect", connect)
    result = service.context.get_context(session_id, "verify", 2, 8000)
    assert observed == [transition]
    assert result["passport"]["source_freshness"] == "Current"
    assert service.memory.status(session_id)["active"]


@pytest.mark.parametrize("event_logging", [True, False])
def test_success_commits_matching_evidence_and_respects_event_setting(
    lifecycle: tuple[Service, str], event_logging: bool
) -> None:
    service, session_id = lifecycle
    service.update_settings({"event_logging": event_logging})
    result = service.context.get_context(session_id, "verify", 2, 8000)
    retrieval = service.db.one("SELECT * FROM retrievals WHERE id=?", (result["retrieval_id"],))
    passport = service.db.one(
        "SELECT * FROM passports WHERE retrieval_id=?", (result["retrieval_id"],)
    )
    assert retrieval is not None and json.loads(retrieval["result_json"]) == result
    assert passport is not None and json.loads(passport["data"]) == result["passport"]
    events = service.db.rows("SELECT * FROM events WHERE type='context_retrieved'")
    assert len(events) == int(event_logging)
    if events:
        assert events[0]["session_id"] == session_id
        assert json.loads(events[0]["detail"])["retrieval_id"] == result["retrieval_id"]
    assert service.memory.status(session_id)["active"]


def test_failed_passport_insert_rolls_back_history_activity_and_event(
    lifecycle: tuple[Service, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session_id = lifecycle
    original_connect = service.db.connect
    state_before_failure = None

    def fail(connection: sqlite3.Connection, sql: str) -> None:
        nonlocal state_before_failure
        if sql.startswith("INSERT INTO passports"):
            row = connection.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            assert row is not None
            state_before_failure = dict(row)
            raise sqlite3.OperationalError("fixture passport write failure")

    @contextmanager
    def connect():
        with original_connect() as connection:
            yield ConnectionProxy(connection, fail)

    monkeypatch.setattr(service.db, "connect", connect)
    with pytest.raises(sqlite3.OperationalError, match="fixture passport write failure"):
        service.context.get_context(session_id, "verify", 2, 8000)
    assert_no_evidence(service)
    assert state_before_failure is not None
    assert session_row(service, session_id) == state_before_failure
    service.db.execute(
        "UPDATE sessions SET task='writable after rollback' WHERE id=?", (session_id,)
    )
