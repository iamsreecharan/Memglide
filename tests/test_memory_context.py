"""Lifecycle, authoritative source checks, isolation and complete-response budgets."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from memglide.core.context import ContextEngine, estimate_tokens
from memglide.core.indexer import Indexer
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import Database, DomainError


class FixtureIndexer:
    def __init__(self, root: Path):
        self.root = root

    def _candidate(
        self, path: str, name: str, start: int, end: int, score: int = 10
    ) -> dict[str, Any]:
        return {
            "id": name,
            "path": path,
            "name": name,
            "symbol": name,
            "qualified_name": name,
            "start_line": start,
            "end_line": end,
            "signature": f"def {name}():",
            "language": "python",
            "hash": hashlib.sha256((self.root / path).read_bytes()).hexdigest(),
            "kind": "function",
            "score": score,
            "reason": "Exact symbol match",
        }

    def search(self, project_id: str, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if query == "missing":
            return []
        return [
            self._candidate("auth.py", "authenticate", 1, 2),
            self._candidate("auth.py", "authenticate", 1, 2),
            self._candidate("auth.py", "helper", 4, 5, 1),
        ]

    def dependencies(
        self, project_id: str, symbol_or_path: str, direction: str = "both", *, refresh: bool = True
    ) -> list[dict[str, Any]]:
        return [
            {
                "source_file": "auth.py",
                "source_symbol": "authenticate",
                "target_file": "tokens.py",
                "target_symbol": "verify",
                "kind": "call",
                "reference": "verify",
                "resolved": True,
            },
            {
                "source_file": "auth.py",
                "source_symbol": "authenticate",
                "target_file": None,
                "target_symbol": None,
                "kind": "call",
                "reference": "plugin.check",
                "resolved": False,
            },
        ]

    def get_symbol(self, project_id: str, symbol: str, *, refresh: bool = True) -> dict[str, Any]:
        if symbol == "verify":
            return self._candidate("tokens.py", "verify", 1, 2)
        if symbol == "tests/test_auth.py":
            return self._candidate(symbol, "test_auth", 1, 2)
        if symbol == "authenticate":
            return self._candidate("auth.py", "authenticate", 1, 2)
        raise DomainError("Unknown symbol", 404)


@pytest.fixture
def env(tmp_path: Path) -> tuple[Database, MemoryEngine, ContextEngine, Path, str]:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "auth.py").write_text(
        "def authenticate():\n    return verify()\n\ndef helper():\n    return True\n"
    )
    (root / "tokens.py").write_text("def verify():\n    return True\n")
    (root / "tests").mkdir()
    (root / "tests/test_auth.py").write_text("def test_auth():\n    assert True\n")
    db = Database(tmp_path / "state/db.sqlite")
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("project", str(root), "repo", time.time()),
    )
    # Related test discovery consults index metadata rather than scanning source trees.
    db.execute(
        "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
        ("test-file", "project", "tests/test_auth.py", "x", "python", 1, 0, 1, None, 0),
    )
    memory = MemoryEngine(db)
    context = ContextEngine(db, FixtureIndexer(root), memory)
    session_id = memory.start_session("project", "authenticate")["id"]
    return db, memory, context, root, session_id


def test_status_never_refreshes_and_lifetime_is_capped(
    env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    db, memory, _, _, session_id = env
    original = memory.status(session_id)
    monkeypatch.setattr("memglide.memory.engine.time.time", lambda: original["created_at"] + 100)
    assert memory.status(session_id)["last_activity"] == original["last_activity"]
    memory.list_sessions()
    assert memory.status(session_id)["expires_at"] == original["expires_at"]
    db.execute(
        "UPDATE sessions SET absolute_expires_at=? WHERE id=?",
        (original["created_at"] + 200, session_id),
    )
    memory.save_memory(session_id, "observation", "Checked current behavior", "agent")
    assert memory.status(session_id)["expires_at"] == original["created_at"] + 200
    monkeypatch.setattr("memglide.memory.engine.time.time", lambda: original["created_at"] + 201)
    with pytest.raises(DomainError, match="expired") as exc:
        memory.status(session_id)
    assert exc.value.status == 410
    assert db.one("SELECT * FROM sessions WHERE id=?", (session_id,)) is None


def test_sources_provenance_dedup_updates_and_stale_checks(env: Any) -> None:
    _, memory, _, root, session = env
    first = memory.save_memory(
        session, "verified_fix", "Authentication is fixed", "agent:test-run", [{"path": "auth.py"}]
    )
    duplicate = memory.save_memory(
        session, "verified_fix", "Authentication  is fixed", "agent:recheck", [{"path": "auth.py"}]
    )
    assert duplicate["id"] == first["id"] and duplicate["deduplicated"]
    assert first["provenance"] == "agent:test-run" and first["freshness"] == "Current"
    assert len(first["sources"][0]["hash"]) == 64
    updated = memory.update_memory(
        session, first["id"], "Authentication verified", "agent:unit-test"
    )
    assert updated["provenance"] == "agent:unit-test"
    (root / "auth.py").write_text("def authenticate():\n    return False\n")
    stale = memory.recall_memory(session, "Authentication", "verified_fix")[0]
    assert stale["stale"] and stale["freshness"] == "Stale"
    assert not stale["sources"][0]["current"]
    with pytest.raises(DomainError, match="changed"):
        memory.save_memory(session, "observation", "Old claim", "agent", first["sources"])
    memory.delete_memory(session, first["id"])
    assert memory.recall_memory(session) == []


def test_missing_deleted_source_and_memory_session_isolation(env: Any) -> None:
    _, memory, _, root, session = env
    saved = memory.save_memory(
        session, "decision", "Use auth module", "agent", [{"path": "auth.py"}]
    )
    second = memory.start_session("project")["id"]
    assert memory.recall_memory(second) == []
    with pytest.raises(DomainError, match="Unknown memory"):
        memory.update_memory(second, saved["id"], "Overwrite")
    (root / "auth.py").unlink()
    assert memory.recall_memory(session)[0]["stale"]


def test_memory_rejects_secret_paths_and_missing_provenance(env: Any) -> None:
    _, memory, _, _, session = env
    with pytest.raises(DomainError, match="provenance"):
        memory.save_memory(session, "observation", "Finding", "")
    with pytest.raises(DomainError, match="relative"):
        memory.save_memory(session, "observation", "Finding", "agent", [{"path": "../outside.py"}])
    with pytest.raises(DomainError, match="credentials"):
        memory.save_memory(session, "observation", "api_key = 'abcdefghijk12345'", "agent")
    with pytest.raises(DomainError, match="credentials"):
        memory.save_memory(session, "observation", "access_token: abcdefghijk12345", "agent")


def test_expiration_and_immediate_clear_cascade_all_task_data(env: Any) -> None:
    db, memory, context, _, session = env
    memory.save_memory(
        session, "observation", "authenticate checked", "agent", [{"path": "auth.py"}]
    )
    context.get_context(session, "authenticate")
    assert db.one("SELECT count(*) n FROM passports")["n"] == 1
    memory.clear_session(session)
    for table in ("sessions", "memories", "memory_sources", "retrievals", "passports", "events"):
        assert db.one(f"SELECT count(*) n FROM {table}")["n"] == 0
    second = memory.start_session("project")["id"]
    memory.save_memory(second, "error", "An error", "agent")
    db.execute("UPDATE sessions SET expires_at=0 WHERE id=?", (second,))
    assert memory.cleanup()["deleted_sessions"] == 1
    assert db.one("SELECT count(*) n FROM memories")["n"] == 0


def test_ended_session_history_remains_until_expiry(env: Any) -> None:
    db, memory, _, _, session = env
    assert not memory.end_session(session)["active"]
    assert memory.cleanup()["deleted_sessions"] == 0
    assert memory.list_sessions()[0]["active"] is False
    assert db.one("SELECT * FROM events WHERE type='session_ended'") is not None
    with pytest.raises(DomainError, match="ended"):
        memory.save_memory(session, "observation", "Late mutation", "agent")


def test_progressive_evidence_exact_ranking_dedup_and_dependencies(env: Any) -> None:
    _, _, context, _, session = env
    first = context.get_context(session, "authenticate", level=1)
    assert first["items"][0]["symbol"] == "authenticate"
    assert len(first["items"]) == 2
    assert not first["items"][0]["snippet"]
    assert first["passport"]["status"] == "Partial"
    assert first["passport"]["unresolved_dependencies"][0]["reference"] == "plugin.check"
    second = context.expand_context(session, first["retrieval_id"])
    assert second["level"] == 2
    assert "return verify()" in second["items"][0]["snippet"]
    assert "tokens.py" in {item["path"] for item in second["items"]}
    third = context.expand_context(session, second["retrieval_id"])
    assert third["level"] == 3
    assert "tests/test_auth.py" in third["passport"]["related_tests"]
    assert all(item["full_source"] for item in third["items"])
    assert len([item for item in third["items"] if item["path"] == "auth.py"]) == 1


@pytest.mark.parametrize("budget", [1000, 1800, 4000])
def test_budget_counts_complete_response_including_passport(env: Any, budget: int) -> None:
    _, memory, context, _, session = env
    for i in range(4):
        memory.save_memory(
            session,
            "verified_fix",
            f"authenticate fix {i}: " + "evidence " * 100,
            "agent:tests",
            [{"path": "auth.py"}],
        )
    result = context.get_context(session, "authenticate", level=3, budget=budget)
    assert estimate_tokens(result) == result["estimated_tokens"]
    assert result["estimated_tokens"] <= budget
    assert result["passport"]["estimated_tokens_returned"] == result["estimated_tokens"]
    if budget == 1000:
        assert result["truncated"]


def test_small_budget_errors_and_cross_session_passport_isolation(env: Any) -> None:
    _, memory, context, _, session = env
    with pytest.raises(DomainError, match="budget"):
        context.get_context(session, "authenticate", budget=128)
    first = context.get_context(session, "authenticate")
    second_session = memory.start_session("project")["id"]
    with pytest.raises(DomainError, match="Unknown Context Passport"):
        context.get_passport(second_session, first["retrieval_id"])
    with pytest.raises(DomainError, match="Unknown retrieval"):
        context.expand_context(second_session, first["retrieval_id"])


def test_passport_revalidates_sources_without_refreshing_activity(env: Any) -> None:
    db, memory, context, root, session = env
    result = context.get_context(session, "authenticate", level=2)
    last_activity = memory.status(session)["last_activity"]
    (root / "auth.py").write_text("def authenticate():\n    return False\n")
    passport = context.get_passport(session, result["retrieval_id"])
    assert passport["status"] == "Stale"
    assert "auth.py" in passport["stale_files"]
    assert "auth.py" not in passport["verified_source_hashes"]
    assert memory.status(session)["last_activity"] == last_activity
    persisted = json.loads(
        db.one("SELECT data FROM passports WHERE retrieval_id=?", (result["retrieval_id"],))["data"]
    )
    assert persisted["source_freshness"] == "Stale"


def test_stale_memories_are_not_selected_as_current_evidence(env: Any) -> None:
    _, memory, context, _, session = env
    saved = memory.save_memory(
        session, "verified_fix", "authenticate fix verified", "agent:tests", [{"path": "auth.py"}]
    )
    memory.invalidate_memory(session, saved["id"])
    result = context.get_context(session, "authenticate")
    assert result["memories"] == []


def test_no_match_passport_is_explicitly_partial(env: Any) -> None:
    _, _, context, _, session = env
    result = context.get_context(session, "missing")
    assert not result["items"]
    assert result["passport"]["status"] == "Partial"
    assert result["passport"]["recommended_next_retrievals"]


def test_concurrent_saves_deduplicate_transactionally(env: Any) -> None:
    db, memory, _, _, session = env
    with ThreadPoolExecutor(max_workers=4) as pool:
        saved = list(
            pool.map(
                lambda _: memory.save_memory(
                    session,
                    "observation",
                    "authenticate observed once",
                    "agent:concurrent",
                    [{"path": "auth.py"}],
                ),
                range(8),
            )
        )
    assert len({memory["id"] for memory in saved}) == 1
    assert db.one("SELECT count(*) n FROM memories")["n"] == 1
    assert db.one("SELECT count(*) n FROM memory_sources")["n"] == 1


def test_passport_tracks_included_memory_references_and_invalidation(env: Any) -> None:
    _, memory, context, root, session = env
    saved = memory.save_memory(
        session,
        "verified_fix",
        "authenticate verifies tokens",
        "agent:test",
        [{"path": "tokens.py"}],
    )
    result = context.get_context(session, "authenticate", level=1)
    assert saved["id"] in result["passport"]["selected_memory_ids"]
    assert "tokens.py" in result["passport"]["verified_source_hashes"]
    memory.invalidate_memory(session, saved["id"])
    assert saved["id"] in context.get_passport(session, result["retrieval_id"])["stale_memory_ids"]
    (root / "tokens.py").unlink()
    assert "tokens.py" in context.get_passport(session, result["retrieval_id"])["stale_files"]


def test_explicit_known_versions_return_current_references_without_repeating_content(
    env: Any,
) -> None:
    _, memory, context, _, session = env
    saved = memory.save_memory(
        session,
        "verified_fix",
        "authenticate verified against tests",
        "agent:test",
        [{"path": "tokens.py"}],
    )
    initial = context.get_context(session, "authenticate", level=1)
    assert initial["memories"][0]["content"] == saved["content"]
    compact = context.get_context(
        session,
        "authenticate",
        known_memory_versions={saved["id"]: saved["version"]},
    )
    reference = compact["memories"][0]
    assert reference["id"] == saved["id"] and reference["content_omitted"]
    assert "content" not in reference and "provenance" not in reference
    assert reference["freshness"] == "Current" and reference["sources"][0]["hash"]
    assert compact["estimated_tokens"] < initial["estimated_tokens"]
    assert (
        compact["passport"]["verified_source_hashes"]
        == initial["passport"]["verified_source_hashes"]
    )
    expanded = context.expand_context(
        session,
        initial["retrieval_id"],
        known_memory_versions={saved["id"]: saved["version"]},
    )
    assert expanded["memories"][0]["content_omitted"]
    # Without an explicit caller declaration, the retrieval remains self-contained.
    assert "content" in context.get_context(session, "authenticate")["memories"][0]
    # An ID alone does not identify which version an independent reader retained.
    hinted = context.get_context(session, "authenticate", known_memory_ids=[saved["id"]])
    assert hinted["memories"][0]["content"] == saved["content"]


def test_change_intent_uses_recorded_events_and_current_real_index_sources(env: Any) -> None:
    db, memory, _, root, _ = env
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    indexer = Indexer(db)
    indexer.reindex("project")
    session = memory.start_session("project")["id"]
    (root / "auth.py").write_text("def authenticate():\n    return 'new-source-version'\n")
    indexer.reindex("project")
    context = ContextEngine(db, indexer, memory)
    result = context.get_context(session, "What changed in this session?", level=2)
    assert {event["path"] for event in result["session_events"]} == {"auth.py"}
    assert result["session_events"][0]["type"] == "file_changed"
    assert "do not identify the actor" in result["session_event_scope"]
    assert result["passport"]["session_event_ids"] == [result["session_events"][0]["id"]]
    current = next(item for item in result["items"] if item["path"] == "auth.py")
    assert "new-source-version" in current["snippet"]
    assert current["hash"] == hashlib.sha256((root / "auth.py").read_bytes()).hexdigest()
    assert estimate_tokens(result) == result["estimated_tokens"] <= result["budget"]


def test_attempt_intent_includes_nonlexical_historical_claims_only_in_current_session(
    env: Any,
) -> None:
    _, memory, context, _, session = env
    failed = memory.save_memory(
        session,
        "failed_attempt",
        "Raised the pool limit to twelve; timeout persisted.",
        "agent:experiment",
    )
    error = memory.save_memory(session, "error", "Connection exhausted", "agent:stderr")
    second = memory.start_session("project")["id"]
    foreign = memory.save_memory(second, "failed_attempt", "Reset connection pool", "agent:other")
    result = context.get_context(session, "What did we already try to fix this error?")
    ids = {memory["id"] for memory in result["memories"]}
    assert failed["id"] in ids and error["id"] in ids
    assert foreign["id"] not in ids
    assert result["passport"]["status"] == "Partial"
    memory.invalidate_memory(session, failed["id"])
    stale_history = context.get_context(session, "What did we already try to fix this error?")
    assert next(item for item in stale_history["memories"] if item["id"] == failed["id"])["stale"]
    assert stale_history["passport"]["status"] == "Stale"


def test_change_history_is_budgeted_as_whole_events_and_partial_index_is_disclosed(
    env: Any,
) -> None:
    db, memory, context, _, session = env
    created = memory.status(session)["created_at"]
    for number in range(30):
        db.execute(
            "INSERT INTO events VALUES(?,?,?,?,?,?)",
            (
                f"change-{number}",
                "project",
                None,
                "file_changed",
                json.dumps({"path": "tokens.py", "deleted": False}),
                created + number / 10000,
            ),
        )
    db.execute(
        "UPDATE projects SET index_stats=? WHERE id='project'", (json.dumps({"partial": True}),)
    )
    result = context.get_context(session, "What changed in this session?", budget=1800)
    assert result["truncated"]
    assert 0 < len(result["session_events"]) < 30
    assert all(
        set(event) == {"id", "type", "created_at", "path", "deleted"}
        for event in result["session_events"]
    )
    assert any("index is partial" in warning for warning in result["warnings"])
    assert estimate_tokens(result) == result["estimated_tokens"] <= 1800
