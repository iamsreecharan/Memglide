"""Dashboard polling requests only the records it actually displays."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest

from memglide.service import Service
from memglide.storage.database import DomainError


@pytest.fixture
def dashboard(tmp_path: Path):
    service = Service(tmp_path / "state.db")
    service.db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES('p',?,'fixture',?)",
        (str(tmp_path), time.time()),
    )
    service.memory.start_session("p", "active task")
    ended = service.memory.start_session("p", "ended task")
    service.memory.end_session(ended["id"])
    with service.db.connect() as conn:
        conn.executemany(
            "INSERT INTO events VALUES(?,'p',NULL,'fixture',?,?)",
            [(f"event-{n}", '{"fixture":true}', n) for n in range(600)],
        )
    try:
        yield service
    finally:
        service.close()


def test_overview_reuses_sessions_and_fetches_only_twenty_events(dashboard: Service) -> None:
    with (
        patch.object(
            dashboard.memory, "list_sessions", wraps=dashboard.memory.list_sessions
        ) as lists,
        patch.object(dashboard.db, "rows", wraps=dashboard.db.rows) as queries,
    ):
        response = dashboard.overview()
    assert lists.call_count == 1
    assert response["counts"]["sessions"] == 1
    assert len(response["sessions"]) == 2
    assert len(response["recent_events"]) == 20
    event_queries = [
        call for call in queries.call_args_list if call.args[0].startswith("SELECT * FROM events")
    ]
    assert len(event_queries) == 1 and event_queries[0].args[1] == (20,)
    assert response["recent_events"] == dashboard.events()[:20]


def test_event_limit_preserves_filters_order_and_default_cap(dashboard: Service) -> None:
    assert len(dashboard.events()) == 500
    short = dashboard.events(project_id="p", event_type="fixture", limit=3)
    assert [row["id"] for row in short] == ["event-599", "event-598", "event-597"]
    assert all(row["detail"] == {"fixture": True} for row in short)


@pytest.mark.parametrize("limit", [0, -1, 501, True, 1.5, "20", None])
def test_invalid_limits_are_rejected_without_cleanup(dashboard: Service, limit: int) -> None:
    with patch.object(dashboard.memory, "cleanup") as cleanup:
        with pytest.raises(DomainError, match="Event limit"):
            dashboard.events(limit=limit)
    cleanup.assert_not_called()
