"""A memory ID cannot stand in for the exact claim delivered to a caller."""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path
from typing import Any

import pytest

from memglide.memory.engine import MemoryEngine
from memglide.service import Service
from memglide.storage.database import DomainError


@pytest.fixture
def versioned_memory(tmp_path: Path):
    repo = tmp_path / "repository"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "auth.py").write_text("def authenticate_user(token):\n    return bool(token)\n")
    service = Service(tmp_path / "state" / "memory.sqlite")
    project = service.indexer.add_project(str(repo))
    session = service.memory.start_session(project["id"], "authenticate_user")
    memory = service.memory.save_memory(
        session["id"],
        "observation",
        "authenticate_user requires an existing token",
        "inspected auth.py",
        [{"path": "auth.py"}],
    )
    yield service, project, session, memory, repo
    service.close()


@pytest.mark.parametrize("field", ["category", "content", "provenance", "sources"])
def test_exact_claim_version_covers_all_submitted_evidence(field: str) -> None:
    original: dict[str, Any] = {
        "category": "observation",
        "content": "The exact claim",
        "provenance": "inspected module.py",
        "sources": [{"path": "module.py", "hash": "a" * 64}],
    }
    modified = copy.deepcopy(original)
    if field == "sources":
        modified["sources"][0]["hash"] = "b" * 64
    else:
        modified[field] += " changed"
    assert MemoryEngine.version(modified) != MemoryEngine.version(original)
    # Unrelated live observations and clocks must not rewrite a submitted version.
    observed = copy.deepcopy(original)
    observed.update(id="memory", updated_at=0, stale=True, freshness="Stale")
    observed["sources"][0].update(current_hash="b" * 64, current=False)
    assert MemoryEngine.version(observed) == MemoryEngine.version(original)
    whitespace = {**original, "content": "The  exact claim"}
    assert MemoryEngine.version(whitespace) != MemoryEngine.version(original)


def test_memory_snapshot_is_owned_and_does_not_extend_ttl(versioned_memory: Any) -> None:
    service, project, session, memory, _ = versioned_memory
    before = service.memory.status(session["id"])
    snapshot = service.memory.get_memory_snapshot(session["id"], memory["id"])
    after = service.memory.status(session["id"])
    assert snapshot["version"] == memory["version"]
    assert before["last_activity"] == after["last_activity"]
    assert before["expires_at"] == after["expires_at"]
    other = service.memory.start_session(project["id"], "foreign session")
    with pytest.raises(DomainError, match="Unknown memory") as error:
        service.memory.get_memory_snapshot(other["id"], memory["id"])
    assert error.value.status == 404
    service.memory.end_session(session["id"])
    with pytest.raises(DomainError, match="ended"):
        service.memory.get_memory_snapshot(session["id"], memory["id"])


@pytest.mark.parametrize("change", ["content", "provenance"])
def test_memory_update_changes_version_even_when_clock_is_unchanged(
    versioned_memory: Any, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    service, _, session, memory, _ = versioned_memory
    monkeypatch.setattr("memglide.memory.engine.time.time", lambda: memory["updated_at"])
    updated = service.memory.update_memory(
        session["id"],
        memory["id"],
        memory["content"] + " after correction" if change == "content" else memory["content"],
        memory["provenance"] + " after review" if change == "provenance" else None,
    )
    assert updated["updated_at"] == memory["updated_at"]
    assert updated["version"] != memory["version"]


@pytest.mark.parametrize("change", ["content", "provenance", "delete", "invalidate"])
def test_passport_detects_changed_or_removed_selected_claim(
    versioned_memory: Any, change: str
) -> None:
    service, _, session, memory, _ = versioned_memory
    result = service.context.get_context(session["id"], "authenticate_user", 2, 16000)
    assert result["passport"]["selected_memory_versions"][memory["id"]] == memory["version"]
    if change in {"content", "provenance"}:
        service.memory.update_memory(
            session["id"],
            memory["id"],
            memory["content"] + " after correction" if change == "content" else memory["content"],
            memory["provenance"] + " after review" if change == "provenance" else None,
        )
    elif change == "delete":
        service.memory.delete_memory(session["id"], memory["id"])
    else:
        service.memory.invalidate_memory(session["id"], memory["id"])
    passport = service.context.get_passport(session["id"], result["retrieval_id"])
    assert passport["status"] == "Stale"
    assert memory["id"] in passport["stale_memory_ids"]


def test_known_version_does_not_hide_a_corrected_memory(versioned_memory: Any) -> None:
    service, project, session, memory, _ = versioned_memory
    initial = service.context.get_context(session["id"], "authenticate_user", 2, 16000)
    assert initial["memories"][0]["content"] == memory["content"]
    known = service.context.get_context(
        session["id"],
        "authenticate_user",
        2,
        16000,
        known_memory_versions={memory["id"]: memory["version"]},
    )
    assert known["memories"][0]["content_omitted"]
    assert known["memories"][0]["version"] == memory["version"]
    updated = service.memory.update_memory(
        session["id"], memory["id"], "authenticate_user accepts a corrected token", "reviewed"
    )
    corrected = service.context.get_context(
        session["id"],
        "authenticate_user",
        2,
        16000,
        known_memory_versions={memory["id"]: memory["version"]},
    )
    assert corrected["memories"][0]["content"] == updated["content"]
    assert corrected["memories"][0]["version"] == updated["version"]
    assert not corrected["memories"][0].get("content_omitted", False)
    compact = service.context.get_context(
        session["id"],
        "authenticate_user",
        2,
        16000,
        known_memory_versions={memory["id"]: updated["version"]},
    )
    assert compact["memories"][0]["content_omitted"]
    other = service.memory.start_session(project["id"], "authenticate_user")
    foreign = service.context.get_context(
        other["id"],
        "authenticate_user",
        2,
        16000,
        known_memory_versions={memory["id"]: updated["version"]},
    )
    assert foreign["memories"] == []


def test_unseen_known_id_returns_complete_evidence(versioned_memory: Any) -> None:
    service, _, session, memory, _ = versioned_memory
    result = service.context.get_context(
        session["id"], "authenticate_user", 2, 16000, [memory["id"]]
    )
    assert result["memories"][0]["content"] == memory["content"]
    assert result["memories"][0]["provenance"] == memory["provenance"]


def test_another_reader_cannot_make_old_client_version_current(versioned_memory: Any) -> None:
    service, _, session, memory, _ = versioned_memory
    old_client = service.context.get_context(session["id"], "authenticate_user", 2, 16000)
    old_version = old_client["memories"][0]["version"]
    updated = service.memory.update_memory(
        session["id"], memory["id"], "authenticate_user accepts a corrected token", "reviewed"
    )
    # A second reader receiving B does not prove that the first reader knows B.
    another_reader = service.context.get_context(session["id"], "authenticate_user", 2, 16000)
    assert another_reader["memories"][0]["version"] == updated["version"]
    id_only = service.context.get_context(
        session["id"], "authenticate_user", 2, 16000, known_memory_ids=[memory["id"]]
    )
    assert id_only["memories"][0]["content"] == updated["content"]
    assert not id_only["memories"][0].get("content_omitted", False)
    stale_client = service.context.get_context(
        session["id"],
        "authenticate_user",
        2,
        16000,
        known_memory_versions={memory["id"]: old_version},
    )
    assert stale_client["memories"][0]["content"] == updated["content"]
    assert not stale_client["memories"][0].get("content_omitted", False)
    current_client = service.context.get_context(
        session["id"],
        "authenticate_user",
        2,
        16000,
        known_memory_versions={memory["id"]: updated["version"]},
    )
    assert current_client["memories"][0]["content_omitted"]
    assert "content" not in current_client["memories"][0]
    assert current_client["memories"][0]["version"] == updated["version"]


@pytest.mark.parametrize(
    "versions",
    [
        {"memory": "not-a-version"},
        {"": "a" * 64},
        {"x" * 129: "a" * 64},
        {"memory": "A" * 64},
        {str(index): "a" * 64 for index in range(1001)},
        [],
    ],
)
def test_known_versions_reject_malformed_or_unbounded_acknowledgments(
    versioned_memory: Any, versions: Any
) -> None:
    service, _, session, _, _ = versioned_memory
    with pytest.raises(DomainError, match="known_memory_versions"):
        service.context.get_context(
            session["id"], "authenticate_user", known_memory_versions=versions
        )
    assert service.db.one("SELECT count(*) n FROM retrievals")["n"] == 0
