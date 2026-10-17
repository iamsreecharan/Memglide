"""Request optimizations retain settings isolation, source freshness and exact budgets."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any

import pytest

import memglide.core.context as context_module
from memglide.core.context import ContextEngine, estimate_tokens
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import Database, DomainError


class FixedIndex:
    def __init__(self, root: Path):
        self.candidates = []
        for name in ("first.py", "second.py"):
            text = (root / name).read_text()
            self.candidates.append(
                {
                    "path": name,
                    "name": name[:-3],
                    "start_line": 1,
                    "end_line": len(text.splitlines()),
                    "hash": hashlib.sha256(text.encode()).hexdigest(),
                    "score": 10 if name == "first.py" else 5,
                }
            )

    def search(self, *_: Any, **__: Any) -> list[dict[str, Any]]:
        return [dict(candidate) for candidate in self.candidates]

    def dependencies(self, *_: Any, **__: Any) -> list[dict[str, Any]]:
        return []

    def get_symbol(self, *_: Any, **__: Any) -> dict[str, Any]:
        raise DomainError("No dependencies", 404)


@pytest.fixture
def request_engine(tmp_path: Path) -> tuple[ContextEngine, str, Path]:
    root = tmp_path / "repository"
    root.mkdir()
    for name in ("first", "second"):
        (root / f"{name}.py").write_text(f"def {name}():\n    return 'inventory'\n")
    db = Database(tmp_path / "state/db.sqlite")
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("inventory", str(root), "inventory", time.time()),
    )
    memory = MemoryEngine(db)
    session = memory.start_session("inventory", "inventory correctness")["id"]
    return ContextEngine(db, FixedIndex(root), memory), session, root


def test_retrieval_reads_settings_once_and_discards_snapshot(
    request_engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine, session, _ = request_engine
    original = engine.db.rows
    settings_reads = []

    def rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if sql == "SELECT * FROM settings":
            settings_reads.append(sql)
        return original(sql, params)

    monkeypatch.setattr(engine.db, "rows", rows)
    first = engine.get_context(session, "inventory", level=2)
    assert len(settings_reads) == 1
    engine.db.execute(
        "UPDATE settings SET value=? WHERE key='context_token_budget'", (json.dumps(1800),)
    )
    second = engine.get_context(session, "inventory", level=2)
    assert len(settings_reads) == 2
    assert first["budget"] == 4000
    assert second["budget"] == 1800
    assert estimate_tokens(second) == second["estimated_tokens"] <= 1800
    engine.get_passport(session, first["retrieval_id"])
    assert len(settings_reads) == 3


def test_concurrent_settings_update_is_consistent_within_request(
    request_engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine, session, _ = request_engine
    original = context_module.read_source
    changed = False

    def read(root: str, relative: str, max_size: int = 512000) -> tuple[str, str]:
        nonlocal changed
        if not changed:
            changed = True
            worker = threading.Thread(
                target=engine.db.execute,
                args=(
                    "UPDATE settings SET value=? WHERE key='context_token_budget'",
                    (json.dumps(1800),),
                ),
            )
            worker.start()
            worker.join(timeout=5)
            assert not worker.is_alive()
        return original(root, relative, max_size)

    monkeypatch.setattr(context_module, "read_source", read)
    first = engine.get_context(session, "inventory", level=2)
    second = engine.get_context(session, "inventory", level=2)
    assert first["budget"] == 4000
    assert second["budget"] == 1800
    assert [item["hash"] for item in first["items"]] == [item["hash"] for item in second["items"]]


def test_concurrent_source_edit_is_not_hidden_by_request_settings_scope(
    request_engine: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine, session, repository = request_engine
    original = context_module.read_source

    def read(root: str, relative: str, max_size: int = 512000) -> tuple[str, str]:
        result = original(root, relative, max_size)
        if relative == "first.py":
            (repository / "second.py").write_text("def second():\n    return 'edited'\n")
        return result

    monkeypatch.setattr(context_module, "read_source", read)
    result = engine.get_context(session, "inventory", level=2)
    assert [item["path"] for item in result["items"]] == ["first.py"]
    assert any(
        "Source changed or is unavailable: second.py" in value for value in result["warnings"]
    )
    (repository / "first.py").write_text("def first():\n    return 'newer'\n")
    passport = engine.get_passport(session, result["retrieval_id"])
    assert passport["status"] == "Stale"
    assert passport["stale_files"] == ["first.py"]


def test_settings_scope_is_thread_local_nested_and_exception_safe(tmp_path: Path) -> None:
    db = Database(tmp_path / "state.sqlite")
    other = Database(tmp_path / "other.sqlite")
    observed = []
    with pytest.raises(RuntimeError, match="request failed"):
        with db.settings_snapshot():
            db.execute("UPDATE settings SET value='1800' WHERE key='context_token_budget'")

            def concurrent() -> None:
                with db.settings_snapshot():
                    observed.append(db.settings()["context_token_budget"])

            worker = threading.Thread(target=concurrent)
            worker.start()
            worker.join(timeout=5)
            assert not worker.is_alive()
            with db.settings_snapshot():
                assert db.settings()["context_token_budget"] == 4000
            assert other.settings()["context_token_budget"] == 4000
            raise RuntimeError("request failed")
    assert observed == [1800]
    assert db.settings()["context_token_budget"] == 1800


def test_snapshot_callers_cannot_mutate_the_request_view(tmp_path: Path) -> None:
    db = Database(tmp_path / "state.sqlite")
    with db.settings_snapshot() as outer:
        outer["context_token_budget"] = 256
        outer["retrieval_weights"]["task_overlap"] = 999
        outer["ignored_directories"].append("src")
        direct = db.settings()
        assert direct["context_token_budget"] == 4000
        assert direct["retrieval_weights"]["task_overlap"] == 0.3
        assert direct["ignored_directories"] == []
        direct["retrieval_weights"]["exact_symbol"] = 0
        with db.settings_snapshot() as nested:
            assert nested["retrieval_weights"]["exact_symbol"] == 120
            nested["retrieval_weights"]["identifier"] = 0
        assert db.settings()["retrieval_weights"]["identifier"] == 35
    assert db.settings()["retrieval_weights"]["task_overlap"] == 0.3


def test_next_request_and_passport_observe_new_source_size_policy(request_engine: Any) -> None:
    engine, session, repository = request_engine
    source = repository / "first.py"
    source.write_text(source.read_text() + "# inventory evidence\n" * 80)
    engine.indexer = FixedIndex(repository)
    before = engine.get_context(session, "inventory", level=2, budget=8000)
    assert "first.py" in {item["path"] for item in before["items"]}
    engine.db.execute("UPDATE settings SET value='1024' WHERE key='max_file_size'")
    after = engine.get_context(session, "inventory", level=2, budget=8000)
    assert [item["path"] for item in after["items"]] == ["second.py"]
    assert any("Source changed or is unavailable: first.py" in value for value in after["warnings"])
    passport = engine.get_passport(session, before["retrieval_id"])
    assert passport["status"] == "Stale"
    assert passport["stale_files"] == ["first.py"]


@pytest.mark.parametrize("size", [0, 10, 250, 2800, 2900, 29900])
def test_estimate_fixed_point_matches_full_utf8_serialization(size: int) -> None:
    response = {
        "estimated_tokens": 0,
        "passport": {"estimated_tokens_returned": 0},
        "snippet": "é🙂文" * size,
    }
    ContextEngine._refresh_estimate(response)
    assert estimate_tokens(response) == response["estimated_tokens"]
    assert response["passport"]["estimated_tokens_returned"] == response["estimated_tokens"]
