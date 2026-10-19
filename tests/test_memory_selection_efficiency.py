"""Discard impossible memory matches before reading their source references."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Iterator

import pytest

import memglide.memory.engine as memory_module
from memglide.core.context import ContextEngine
from memglide.service import Service
from memglide.storage.database import DomainError


@pytest.fixture
def workspace(tmp_path: Path) -> Iterator[tuple[Service, str, Path]]:
    root = tmp_path / "repository"
    root.mkdir()
    for name in ("relevant.py", "shared.py", "unrelated.py", "changing.py"):
        (root / name).write_text("def fixture():\n    return True\n")
    service = Service(tmp_path / "state" / "memglide.db")
    service.db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES('project',?,'fixture',0)",
        (str(root),),
    )
    session = service.memory.start_session("project", "verify")
    try:
        yield service, session["id"], root
    finally:
        service.close()


def save(
    service: Service,
    session_id: str,
    content: str,
    *,
    category: str = "observation",
    path: str | None = "relevant.py",
    provenance: str = "inspected fixture",
    stale: bool = False,
) -> dict[str, Any]:
    memory = service.memory.save_memory(
        session_id, category, content, provenance, [] if path is None else [{"path": path}]
    )
    count = service.db.one("SELECT count(*) AS count FROM memories")
    assert count is not None
    # Explicit unequal timestamps make rank equivalence independent of clocks
    # and random IDs while still exercising category/freshness precedence.
    stamp = 1000 + count["count"]
    service.db.execute(
        "UPDATE memories SET created_at=?,updated_at=?,stale=? WHERE id=?",
        (stamp, stamp, int(stale), memory["id"]),
    )
    return memory


def full_recall_reference(
    context: ContextEngine, session_id: str, query: str, task: str, intent: str | None = None
) -> list[dict[str, Any]]:
    """Pre-optimization selection oracle, which validates every saved claim."""
    terms = context._words(query + " " + task)
    ranked = []
    for memory in context.memory.recall_memory(session_id):
        history = intent == "prior_attempts" and memory["category"] in {
            "failed_attempt",
            "error",
            "verified_fix",
        }
        if memory["stale"] and not history:
            continue
        overlap = len(terms & context._words(memory["content"]))
        if terms and not overlap and not history:
            continue
        score = overlap + (3 if memory["freshness"] == "Current" else 0)
        score += 100 if history else 0
        score += int(memory["category"] == "verified_fix")
        ranked.append((score, memory))
    ranked.sort(key=lambda pair: (-pair[0], -pair[1]["updated_at"], pair[1]["id"]))
    return [
        {key: value for key, value in memory.items() if key not in {"session_id", "deduplicated"}}
        for _, memory in ranked[:10]
    ]


def count_reads(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    original = memory_module.read_source
    reads: list[str] = []

    def counted(root: str, path: str, max_size: int):
        reads.append(path)
        return original(root, path, max_size)

    monkeypatch.setattr(memory_module, "read_source", counted)
    return reads


@pytest.mark.parametrize(
    ("query", "task", "intent"),
    [
        ("verify", "", None),
        ("buses", "", None),
        ("cacheEntries", "", None),
        ("", "verify", None),
        ("", "", None),
        ("the and", "", None),
        ("what did we already try", "", "prior_attempts"),
        ("migration", "verify", None),
        ("unknown", "", None),
    ],
)
def test_selected_output_is_identical_to_full_recall_reference(
    workspace: tuple[Service, str, Path], query: str, task: str, intent: str | None
) -> None:
    service, session_id, _ = workspace
    for i in range(18):
        save(service, session_id, f"Verify cache_entry bus behavior {i}", stale=i < 5)
    save(service, session_id, "Verify behavior without source", path=None)
    save(service, session_id, "Migration decision", category="decision", path="unrelated.py")
    save(service, session_id, "Unrelated submitted claim", provenance="verify cacheEntries buses")
    for i, category in enumerate(("failed_attempt", "error", "verified_fix", "open_issue")):
        save(
            service, session_id, f"Unrelated historical finding {i}", category=category, stale=True
        )
    actual = service.context._select_memories(session_id, query, task, intent)
    expected = full_recall_reference(service.context, session_id, query, task, intent)
    assert actual == expected


def test_irrelevant_claims_do_not_read_sources_but_every_relevant_candidate_is_validated(
    workspace: tuple[Service, str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session_id, _ = workspace
    for i in range(40):
        save(service, session_id, f"Migration observation {i}", path="shared.py")
    for i in range(15):
        save(service, session_id, f"Verify behavior {i}", stale=i < 3)
    reads = count_reads(monkeypatch)
    actual = service.context._select_memories(session_id, "verify", "")
    assert len(actual) == 10
    assert Counter(reads) == {"relevant.py": 15}
    reads.clear()
    assert actual == full_recall_reference(service.context, session_id, "verify", "")
    assert Counter(reads) == {"relevant.py": 15, "shared.py": 40}


def test_newer_stale_candidates_cannot_prevent_top_ten_refill(
    workspace: tuple[Service, str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session_id, root = workspace
    current = [save(service, session_id, f"Verify stable finding {i}") for i in range(12)]
    for i in range(15):
        save(service, session_id, f"Verify obsolete finding {i}", path="changing.py")
    (root / "changing.py").write_text("def fixture():\n    return False\n")
    reads = count_reads(monkeypatch)
    actual = service.context._select_memories(session_id, "verify", "")
    assert len(actual) == 10
    assert {memory["id"] for memory in actual} <= {memory["id"] for memory in current}
    assert Counter(reads) == {"relevant.py": 12, "changing.py": 15}
    assert actual == full_recall_reference(service.context, session_id, "verify", "")


@pytest.mark.parametrize("later_check", ["relevant_context", "public_recall", "snapshot"])
def test_skipped_unrelated_claim_is_revalidated_when_it_becomes_relevant(
    workspace: tuple[Service, str, Path],
    monkeypatch: pytest.MonkeyPatch,
    later_check: str,
) -> None:
    service, session_id, root = workspace
    saved = save(service, session_id, "Migration previously succeeded", path="unrelated.py")
    (root / "unrelated.py").write_text("def fixture():\n    return False\n")
    reads = count_reads(monkeypatch)
    assert service.context._select_memories(session_id, "verify", "") == []
    assert reads == []
    assert service.db.one("SELECT stale FROM memories WHERE id=?", (saved["id"],)) == {"stale": 0}
    if later_check == "relevant_context":
        assert service.context._select_memories(session_id, "migration", "") == []
    elif later_check == "public_recall":
        assert service.memory.recall_memory(session_id)[0]["stale"]
    else:
        assert service.memory.get_memory_snapshot(session_id, saved["id"])["stale"]
    assert reads == ["unrelated.py"]
    assert service.db.one("SELECT stale FROM memories WHERE id=?", (saved["id"],)) == {"stale": 1}


def test_provenance_only_overlap_is_not_context_relevance_and_public_recall_stays_and_filtered(
    workspace: tuple[Service, str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session_id, _ = workspace
    saved = save(service, session_id, "Migration finding", provenance="verified alpha beta")
    reads = count_reads(monkeypatch)
    assert service.context._select_memories(session_id, "alpha", "") == []
    assert reads == []
    assert service.memory.recall_memory(session_id, "alpha beta")[0]["id"] == saved["id"]
    assert reads == ["relevant.py"]
    assert service.memory.recall_memory(session_id, "alpha absent") == []
    assert service.memory.recall_memory(session_id, "alpha", "decision") == []
    assert reads == ["relevant.py"]


def test_relevant_source_is_read_again_on_every_request(
    workspace: tuple[Service, str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session_id, root = workspace
    save(service, session_id, "Verify current behavior")
    reads = count_reads(monkeypatch)
    assert len(service.context._select_memories(session_id, "verify", "")) == 1
    (root / "relevant.py").write_text("def fixture():\n    return False\n")
    assert service.context._select_memories(session_id, "verify", "") == []
    assert reads == ["relevant.py", "relevant.py"]


def test_candidate_helper_checks_session_before_predicate_and_does_not_revive_ended_session(
    workspace: tuple[Service, str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, session_id, _ = workspace
    save(service, session_id, "Verify behavior")
    ended = service.memory.end_session(session_id)
    calls: list[dict[str, Any]] = []

    def predicate(memory: dict[str, Any]) -> bool:
        calls.append(memory)
        return True

    reads = count_reads(monkeypatch)
    with pytest.raises(DomainError, match="ended") as error:
        service.memory._recall_context_candidates(session_id, predicate)
    assert error.value.status == 410
    assert calls == reads == []
    assert service.memory.history_status(session_id)["expires_at"] == ended["expires_at"]
