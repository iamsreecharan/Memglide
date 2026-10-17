"""Compact agent workflows retain actual source evidence and ownership checks."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from memglide.core.agent_context import AgentContext
from memglide.core.context import estimate_tokens
from memglide.service import Service
from memglide.storage.database import DomainError


def build_agent_service(tmp_path: Path) -> tuple[Service, Path, str]:
    root = tmp_path / "approved"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "inventory.py").write_text(
        "def canonical_name(value: str) -> str:\n"
        "    return value.strip().casefold()\n\n"
        "def add_item(items: dict[str, int], name: str, count: int) -> None:\n"
        "    key = canonical_name(name)\n"
        "    items[key] = items.get(key, 0) + count\n"
    )
    service = Service(tmp_path / "state/memglide.db")
    project = service.indexer.add_project(str(root))
    return service, root, project["id"]


@pytest.fixture
def agent_service(tmp_path: Path):
    service, root, project_id = build_agent_service(tmp_path)
    yield service, root, project_id
    service.close()


def test_first_fetch_combines_session_and_real_context_without_losing_code(
    agent_service: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _, project_id = agent_service
    adapter = AgentContext(service, project_id)
    original = service.context.get_context
    calls: list[dict[str, Any]] = []

    def record(*args: Any, **kwargs: Any) -> dict[str, Any]:
        result = original(*args, **kwargs)
        calls.append(result)
        return result

    monkeypatch.setattr(service.context, "get_context", record)
    assert service.memory.list_sessions() == []
    compact = adapter.fetch("Fix add_item in inventory.py")
    full = calls[0]
    assert len(calls) == 1
    assert len(service.memory.list_sessions(project_id)) == 1
    assert compact["operation"] == "get_context"
    assert compact["retrieval_id"] == full["retrieval_id"]
    assert compact["items"]
    assert [item["snippet"] for item in compact["items"]] == [
        item["snippet"] for item in full["items"]
    ]
    assert any("items[key] =" in item["snippet"] for item in compact["items"])
    assert compact["source_hashes"] == full["passport"]["verified_source_hashes"]
    assert estimate_tokens(compact) <= 4000
    assert len(json.dumps(compact)) < len(json.dumps(full))
    assert not {"session_id", "project_id", "passport", "query", "complete"} & compact.keys()
    adapter.fetch("canonical_name")
    assert len(service.memory.list_sessions(project_id)) == 1


@pytest.mark.parametrize("query", ["", "  ", "é" * 2001])
def test_invalid_query_does_not_create_an_empty_session(agent_service: Any, query: str) -> None:
    service, _, project_id = agent_service
    adapter = AgentContext(service, project_id)
    with pytest.raises(DomainError):
        adapter.fetch(query)
    assert service.memory.list_sessions() == []


@pytest.mark.parametrize("budget", [True, 255, 100001, 1.5])
def test_invalid_budget_does_not_start_a_session(agent_service: Any, budget: Any) -> None:
    service, _, project_id = agent_service
    with pytest.raises(DomainError, match="budget"):
        AgentContext(service, project_id).fetch("add_item", budget=budget)
    assert service.memory.list_sessions() == []


def test_only_this_server_can_verify_its_retrievals(agent_service: Any) -> None:
    service, _, project_id = agent_service
    first = AgentContext(service, project_id)
    second = AgentContext(service, project_id)
    retrieval = first.fetch("add_item")["retrieval_id"]
    with pytest.raises(DomainError, match="this server"):
        second.verify(retrieval)
    second.fetch("canonical_name")
    with pytest.raises(DomainError, match="this server"):
        second.verify(retrieval)
    assert first.verify()["retrieval_id"] == retrieval
    with pytest.raises(DomainError):
        AgentContext(service, "unregistered")
    assert len(service.indexer.list_projects()) == 1


def test_no_argument_verification_checks_real_hashes_after_edit(agent_service: Any) -> None:
    service, root, project_id = agent_service
    adapter = AgentContext(service, project_id)
    result = adapter.fetch("add_item")
    assert adapter.verify()["source_freshness"] == "Current"
    source = root / "inventory.py"
    source.write_text(source.read_text().replace("+ count", "+ max(0, count)"))
    verified = adapter.verify()
    assert verified["operation"] == "get_context_passport"
    assert verified["retrieval_id"] == result["retrieval_id"]
    assert verified["source_freshness"] == "Stale"
    assert verified["stale_files"] == ["inventory.py"]
    refreshed = adapter.fetch("add_item")
    assert any("max(0, count)" in item["snippet"] for item in refreshed["items"])
    assert adapter.verify()["retrieval_id"] == refreshed["retrieval_id"]
    assert adapter.verify()["source_freshness"] == "Current"
    assert adapter.verify(result["retrieval_id"])["source_freshness"] == "Stale"


def test_ended_session_cannot_be_verified_or_reused_for_old_retrieval(agent_service: Any) -> None:
    service, _, project_id = agent_service
    adapter = AgentContext(service, project_id)
    old = adapter.fetch("add_item")["retrieval_id"]
    session = service.memory.list_sessions(project_id)[0]
    service.memory.end_session(session["id"])
    with pytest.raises(DomainError, match="ended"):
        adapter.verify()
    current = adapter.fetch("canonical_name")["retrieval_id"]
    assert current != old
    with pytest.raises(DomainError, match="this server"):
        adapter.verify(old)
    assert adapter.verify()["retrieval_id"] == current
    adapter.close()
    assert not any(row["active"] for row in service.memory.list_sessions(project_id))


def test_compact_response_retains_partial_and_index_failure_warnings(
    agent_service: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _, project_id = agent_service
    service.db.execute(
        "UPDATE projects SET index_stats=? WHERE id=?",
        (json.dumps({"partial": True, "errors": [{"path": "unreadable.py"}]}), project_id),
    )
    # Keep the recorded failed-index state rather than replacing it with a
    # successful scan of this intentionally small fixture.
    monkeypatch.setattr(service.indexer, "reindex", lambda *_args, **_kwargs: {})
    result = AgentContext(service, project_id).fetch("add_item")
    assert result["status"] == "Partial"
    assert any("partial" in warning for warning in result["warnings"])
    assert any("error" in warning for warning in result["warnings"])


def test_project_query_cannot_register_or_read_an_outside_root(
    agent_service: Any, tmp_path: Path
) -> None:
    service, _, project_id = agent_service
    outside = tmp_path / "outside.py"
    outside.write_text("OUTSIDE_PRIVATE_SENTINEL = 918273645\n")
    result = AgentContext(service, project_id).fetch(str(outside))
    assert "OUTSIDE_PRIVATE_SENTINEL" not in json.dumps(result)
    assert len(service.indexer.list_projects()) == 1


def test_synchronous_fetch_discovers_new_files_without_background_watcher(
    agent_service: Any,
) -> None:
    service, root, project_id = agent_service
    adapter = AgentContext(service, project_id)
    adapter.fetch("add_item")
    (root / "new_rules.py").write_text("def stock_floor(value):\n    return max(0, value)\n")
    current = adapter.fetch("stock_floor")
    assert any(
        item["path"] == "new_rules.py" and "return max(0, value)" in item["snippet"]
        for item in current["items"]
    )


@pytest.mark.parametrize("replacement", ["delete", "symlink"])
def test_verify_rejects_deleted_or_symlink_replaced_sources(
    agent_service: Any, tmp_path: Path, replacement: str
) -> None:
    service, root, project_id = agent_service
    adapter = AgentContext(service, project_id)
    adapter.fetch("add_item")
    path = root / "inventory.py"
    path.unlink()
    if replacement == "symlink":
        outside = tmp_path / "outside.py"
        outside.write_text("UNAPPROVED_SOURCE_SENTINEL = 1\n")
        path.symlink_to(outside)
    stale = adapter.verify()
    assert stale["stale_files"] == ["inventory.py"]
    assert stale["source_freshness"] == "Stale"
    refreshed = adapter.fetch("add_item")
    assert not any(item["path"] == "inventory.py" for item in refreshed["items"])
    assert "UNAPPROVED_SOURCE_SENTINEL" not in json.dumps(refreshed)
