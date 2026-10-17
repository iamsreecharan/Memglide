"""Transport validation and retained-history behavior beyond retrieval ranking."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from memglide.api.app import create_app
from memglide.service import Service
from memglide.storage.database import DomainError

HEADER = {"X-Memglide-Request": "1"}


@pytest.fixture
def lifecycle(tmp_path: Path):
    service = Service(tmp_path / "state" / "memory.db")
    for project_id in ("alpha", "beta"):
        root = tmp_path / project_id
        root.mkdir()
        service.db.execute(
            "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
            (project_id, str(root), project_id, 1.0),
        )
    session = service.memory.start_session("alpha", "Inspect retained history")
    yield service, session
    service.close()


def test_ended_session_events_remain_readable_without_extending_lifetime(lifecycle: Any) -> None:
    service, session = lifecycle
    service.memory.save_memory(session["id"], "observation", "Recorded evidence", "test")
    service.memory.end_session(session["id"])
    before = service.db.one("SELECT * FROM sessions WHERE id=?", (session["id"],))
    with TestClient(create_app(service), base_url="http://localhost:8765") as client:
        response = client.get(
            "/api/events", params={"project_id": "alpha", "session_id": session["id"]}
        )
        assert response.status_code == 200, response.text
        events = response.json()
        assert {"session_started", "memory_saved", "session_ended"} <= {
            event["type"] for event in events
        }
        assert all(event["session_id"] == session["id"] for event in events)
        assert client.get(f"/api/sessions/{session['id']}").status_code == 410
        denied = client.post(
            f"/api/sessions/{session['id']}/memories",
            json={"category": "observation", "content": "Too late", "provenance": "test"},
            headers=HEADER,
        )
        assert denied.status_code == 410
    after = service.db.one("SELECT * FROM sessions WHERE id=?", (session["id"],))
    assert after == before


def test_history_keeps_ownership_and_expiration_boundaries(lifecycle: Any) -> None:
    service, session = lifecycle
    service.memory.end_session(session["id"])
    with pytest.raises(DomainError) as foreign:
        service.events(project_id="beta", session_id=session["id"])
    assert foreign.value.status == 404
    service.db.execute("UPDATE sessions SET expires_at=0 WHERE id=?", (session["id"],))
    # Events performs expiration cleanup before lookup, so removed history is 404.
    with pytest.raises(DomainError) as expired:
        service.events(session_id=session["id"])
    assert expired.value.status == 404
    assert service.db.rows("SELECT * FROM events WHERE session_id=?", (session["id"],)) == []
    replacement = service.memory.start_session("alpha")
    service.memory.end_session(replacement["id"])
    service.memory.clear_session(replacement["id"])
    with pytest.raises(DomainError) as cleared:
        service.events(session_id=replacement["id"])
    assert cleared.value.status == 404


@pytest.mark.parametrize(
    "values",
    [
        {"session_ttl_minutes": True},
        {"session_ttl_minutes": "10"},
        {"max_session_hours": 2.0},
        {"context_token_budget": "8000"},
        {"max_file_size": 2048.0},
        {"watch_enabled": "false"},
        {"event_logging": 0},
        {"retrieval_weights": {"identifier": True}},
        {"retrieval_weights": {"identifier": "35"}},
    ],
)
def test_http_settings_reject_coercion_and_preserve_state(lifecycle: Any, values: Any) -> None:
    service, _ = lifecycle
    before = service.settings()
    with pytest.raises(DomainError):
        service.update_settings(values)
    with TestClient(create_app(service), base_url="http://localhost:8765") as client:
        response = client.put("/api/settings", json=values, headers=HEADER)
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == "validation_error"
        assert service.settings() == before


def test_http_settings_accept_normal_json_types_and_partial_weight_updates(lifecycle: Any) -> None:
    service, _ = lifecycle
    before = service.settings()
    with TestClient(create_app(service), base_url="http://localhost:8765") as client:
        response = client.put(
            "/api/settings",
            json={
                "session_ttl_minutes": 30,
                "watch_enabled": False,
                "retrieval_weights": {"identifier": 20, "full_text": 2.5},
            },
            headers=HEADER,
        )
        assert response.status_code == 200, response.text
        current = response.json()
        assert current["session_ttl_minutes"] == 30
        assert current["watch_enabled"] is False
        assert current["retrieval_weights"]["identifier"] == 20
        assert current["retrieval_weights"]["full_text"] == 2.5
        assert (
            current["retrieval_weights"]["exact_symbol"]
            == before["retrieval_weights"]["exact_symbol"]
        )


@pytest.mark.parametrize("operation", ["save", "update", "invalidate", "delete", "touch"])
def test_session_end_between_initial_check_and_write_rejects_mutation(
    lifecycle: Any, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    service, session = lifecycle
    memory = service.memory.save_memory(
        session["id"], "observation", "Original claim", "original provenance"
    )
    original_status = service.memory.status
    ended = False

    def end_after_initial_check(session_id: str, project_id: str | None = None):
        nonlocal ended
        result = original_status(session_id, project_id)
        if not ended:
            ended = True
            service.db.execute("UPDATE sessions SET ended_at=1 WHERE id=?", (session_id,))
        return result

    before_memory = service.db.rows("SELECT * FROM memories")
    before_session = service.db.one("SELECT * FROM sessions WHERE id=?", (session["id"],))
    monkeypatch.setattr(service.memory, "status", end_after_initial_check)
    with pytest.raises(DomainError, match="ended") as error:
        if operation == "save":
            service.memory.save_memory(session["id"], "decision", "New late claim", "test")
        elif operation == "update":
            service.memory.update_memory(session["id"], memory["id"], "Changed late claim")
        elif operation == "invalidate":
            service.memory.invalidate_memory(session["id"], memory["id"])
        elif operation == "delete":
            service.memory.delete_memory(session["id"], memory["id"])
        else:
            service.memory.touch(session["id"])
    assert error.value.status == 410
    assert service.db.rows("SELECT * FROM memories") == before_memory
    after_session = service.db.one("SELECT * FROM sessions WHERE id=?", (session["id"],))
    assert after_session["expires_at"] == before_session["expires_at"]
    assert after_session["last_activity"] == before_session["last_activity"]


def test_content_only_update_preserves_concurrently_corrected_provenance(
    lifecycle: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session = lifecycle
    memory = service.memory.save_memory(
        session["id"], "observation", "Original claim", "original provenance"
    )
    original_settings = service.db.settings
    corrected = False

    def correct_before_write_lock():
        nonlocal corrected
        if not corrected:
            corrected = True
            service.db.execute(
                "UPDATE memories SET provenance=? WHERE id=?",
                ("concurrently corrected provenance", memory["id"]),
            )
        return original_settings()

    monkeypatch.setattr(service.db, "settings", correct_before_write_lock)
    updated = service.memory.update_memory(session["id"], memory["id"], "Corrected claim")
    assert updated["content"] == "Corrected claim"
    assert updated["provenance"] == "concurrently corrected provenance"


def test_old_expiration_snapshot_cannot_delete_concurrently_renewed_session(
    lifecycle: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session = lifecycle
    memory = service.memory.save_memory(
        session["id"], "observation", "Retain evidence after renewal", "test"
    )
    instant = time.time()
    service.db.execute(
        "UPDATE sessions SET expires_at=? WHERE id=?", (instant + 0.1, session["id"])
    )
    original_one = service.db.one
    renewed = False

    def renew_after_old_snapshot(query: str, params: tuple[Any, ...] = ()):
        nonlocal renewed
        row = original_one(query, params)
        if not renewed and query == "SELECT * FROM sessions WHERE id=?":
            renewed = True
            # Model a valid useful request just before the old deadline, then the
            # status reader crossing that deadline with its outdated snapshot.
            service.db.execute(
                "UPDATE sessions SET last_activity=?,expires_at=? WHERE id=?",
                (instant + 0.05, instant + 600, session["id"]),
            )
        return row

    monkeypatch.setattr(service.db, "one", renew_after_old_snapshot)
    monkeypatch.setattr("memglide.memory.engine.time.time", lambda: instant + 1)
    current = service.memory.status(session["id"])
    assert current["active"]
    assert current["expires_at"] == instant + 600
    assert current["last_activity"] == instant + 0.05
    assert service.db.one("SELECT id FROM memories WHERE id=?", (memory["id"],)) is not None


@pytest.mark.parametrize("transition", ["end", "expire"])
def test_source_capture_finishing_after_lifecycle_transition_cannot_save_claim(
    lifecycle: Any, monkeypatch: pytest.MonkeyPatch, transition: str
) -> None:
    service, session = lifecycle
    source = Path(service.db.project("alpha")["path"]) / "module.py"
    source.write_text("def verify():\n    return True\n")
    original_capture = service.memory._capture_sources

    def capture_then_transition(project_id: str, sources: list[dict[str, Any]]):
        captured = original_capture(project_id, sources)
        assert captured[0]["path"] == "module.py" and len(captured[0]["hash"]) == 64
        if transition == "end":
            service.memory.end_session(session["id"])
        else:
            service.db.execute("UPDATE sessions SET expires_at=0 WHERE id=?", (session["id"],))
        return captured

    monkeypatch.setattr(service.memory, "_capture_sources", capture_then_transition)
    with pytest.raises(DomainError, match="ended" if transition == "end" else "expired") as error:
        service.memory.save_memory(
            session["id"],
            "verified_fix",
            "verify returns True",
            "Inspected module.py",
            [{"path": "module.py"}],
        )
    assert error.value.status == 410
    assert service.db.rows("SELECT * FROM memories") == []
    assert service.db.rows("SELECT * FROM memory_sources") == []
    assert service.db.rows("SELECT * FROM events WHERE type='memory_saved'") == []
    if transition == "expire":
        assert service.memory.cleanup()["deleted_sessions"] == 1


def test_duplicate_update_rolls_back_claim_lifetime_and_event(lifecycle: Any) -> None:
    service, session = lifecycle
    service.memory.save_memory(session["id"], "observation", "Existing claim", "test")
    second = service.memory.save_memory(session["id"], "observation", "Other claim", "test")
    before_session = service.db.one("SELECT * FROM sessions WHERE id=?", (session["id"],))
    with pytest.raises(DomainError) as duplicate:
        service.memory.update_memory(session["id"], second["id"], "Existing claim")
    assert duplicate.value.status == 409
    assert (
        service.memory.get_memory_snapshot(session["id"], second["id"])["content"] == "Other claim"
    )
    assert service.db.one("SELECT * FROM sessions WHERE id=?", (session["id"],)) == before_session
    assert service.db.rows("SELECT * FROM events WHERE type='memory_updated'") == []
