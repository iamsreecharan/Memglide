"""Indexed history and foreign-key operations keep their existing isolation."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from memglide.core.indexer import Indexer
from memglide.storage.database import Database

NEW_INDEXES = (
    "symbol_files",
    "session_projects",
    "memory_source_paths",
    "retrieval_sessions",
    "retrieval_projects",
    "retrieval_created",
    "passport_sessions",
    "event_projects",
    "event_created",
)


def seed(db: Database) -> None:
    with db.connect() as conn:
        for project in ("p0", "p1"):
            conn.execute(
                "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,1)",
                (project, "/unused/" + project, project),
            )
            for number, path in enumerate(("shared.py", "other.py")):
                file_id = f"{project}-file{number}"
                conn.execute(
                    "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (file_id, project, path, "digest", "python", 10, 1.0, 1, None, 1.0),
                )
                conn.execute(
                    "INSERT INTO symbols VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        file_id + "-symbol", project, file_id, path, "value", "value",
                        "function", "def value():", 1, 2, 1,
                    ),
                )
                conn.execute(
                    "INSERT INTO file_search(project_id,path,identifiers,content) "
                    "VALUES(?,?,?,?)",
                    (project, path, "value", "def value(): return 1"),
                )
            conn.execute(
                "INSERT INTO events VALUES(?,?,NULL,'repository_indexed','{}',1)",
                (project + "-project-event", project),
            )
            for number in range(2):
                session = f"{project}-s{number}"
                memory = session + "-memory"
                retrieval = session + "-retrieval"
                conn.execute(
                    "INSERT INTO sessions VALUES(?,?,?,1,1,2,3,NULL)",
                    (session, project, "A task"),
                )
                conn.execute(
                    "INSERT INTO memories VALUES(?,?,?,?,?,1,1,0,?)",
                    (memory, session, "decision", "A claim", "A source", memory),
                )
                conn.execute(
                    "INSERT INTO memory_sources VALUES(?,'shared.py','digest')", (memory,)
                )
                conn.execute(
                    "INSERT INTO retrievals VALUES(?,?,?,'value',1,1000,10,1,'{}')",
                    (retrieval, session, project),
                )
                conn.execute(
                    "INSERT INTO passports VALUES(?,?,?)",
                    (
                        retrieval, session,
                        json.dumps({"status": "Current", "selected_files": ["shared.py"]}),
                    ),
                )
                conn.execute(
                    "INSERT INTO events VALUES(?,?,?,'context_retrieved','{}',1)",
                    (session + "-event", project, session),
                )


def plan(db: Database, query: str, params: tuple[Any, ...]) -> str:
    return "\n".join(
        str(row["detail"]) for row in db.rows("EXPLAIN QUERY PLAN " + query, params)
    )


@pytest.mark.parametrize(
    ("query", "params", "index"),
    [
        ("DELETE FROM files WHERE id=?", ("p0-file0",), "symbol_files"),
        (
            "SELECT * FROM sessions WHERE project_id=? ORDER BY created_at DESC,id",
            ("p0",), "session_projects",
        ),
        (
            "SELECT ms.memory_id FROM memory_sources ms "
            "JOIN memories m ON m.id=ms.memory_id JOIN sessions s ON s.id=m.session_id "
            "WHERE s.project_id=? AND ms.path=?",
            ("p0", "shared.py"), "memory_source_paths",
        ),
        ("DELETE FROM sessions WHERE id=?", ("p0-s0",), "retrieval_sessions"),
        (
            "SELECT p.retrieval_id,p.data FROM passports p "
            "JOIN retrievals r ON r.id=p.retrieval_id WHERE r.project_id=?",
            ("p0",), "retrieval_projects",
        ),
        (
            "SELECT id,session_id,project_id,query,level,budget,estimated_tokens,created_at "
            "FROM retrievals ORDER BY created_at DESC LIMIT 20",
            (), "retrieval_created",
        ),
        ("DELETE FROM sessions WHERE id=?", ("p0-s0",), "passport_sessions"),
        (
            "SELECT * FROM events WHERE project_id=? ORDER BY created_at DESC LIMIT 500",
            ("p0",), "event_projects",
        ),
        (
            "SELECT * FROM events ORDER BY created_at DESC LIMIT 500",
            (), "event_created",
        ),
    ],
)
def test_real_history_and_cascade_queries_use_bounded_index_access(
    tmp_path: Path, query: str, params: tuple[Any, ...], index: str
) -> None:
    db = Database(tmp_path / "state.db")
    seed(db)
    details = plan(db, query, params)
    assert index in details
    if "ORDER BY" in query:
        assert "TEMP B-TREE" not in details


def snapshot(conn: sqlite3.Connection) -> dict[str, list[tuple[Any, ...]]]:
    tables = (
        "schema_migrations", "projects", "files", "symbols", "sessions", "memories",
        "memory_sources", "retrievals", "passports", "events", "settings", "file_search",
    )
    return {table: [tuple(row) for row in conn.execute(f"SELECT * FROM {table}")] for table in tables}


def test_existing_database_adds_indexes_without_rewriting_records(tmp_path: Path) -> None:
    path = tmp_path / "existing.db"
    db = Database(path)
    seed(db)
    with db.connect() as conn:
        for index in NEW_INDEXES:
            conn.execute(f"DROP INDEX {index}")
        original = snapshot(conn)
    old_plan = plan(db, "SELECT * FROM events ORDER BY created_at DESC LIMIT 500", ())
    assert "TEMP B-TREE" in old_plan

    upgraded = Database(path)
    with upgraded.connect() as conn:
        assert snapshot(conn) == original
        names = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master")}
        assert set(NEW_INDEXES) <= names
    assert "TEMP B-TREE" not in plan(
        upgraded, "SELECT * FROM events ORDER BY created_at DESC LIMIT 500", ()
    )
    # Reopening repeatedly is additive and idempotent for both data and DDL.
    with Database(path).connect() as conn:
        assert snapshot(conn) == original


def test_indexed_invalidation_and_cascades_preserve_other_project_and_session(
    tmp_path: Path,
) -> None:
    db = Database(tmp_path / "state.db")
    seed(db)
    with db.connect() as conn:
        Indexer._invalidate(conn, "p0", {"shared.py"})
    assert db.one("SELECT stale FROM memories WHERE id='p0-s0-memory'") == {"stale": 1}
    assert db.one("SELECT stale FROM memories WHERE id='p1-s0-memory'") == {"stale": 0}
    for project, expected in (("p0", "Stale"), ("p1", "Current")):
        row = db.one("SELECT data FROM passports WHERE retrieval_id=?", (project + "-s0-retrieval",))
        assert row is not None and json.loads(row["data"])["status"] == expected

    db.execute("DELETE FROM files WHERE id='p0-file0'")
    assert db.one("SELECT id FROM symbols WHERE id='p0-file0-symbol'") is None
    assert db.one("SELECT id FROM symbols WHERE id='p0-file1-symbol'") is not None
    assert db.one("SELECT id FROM symbols WHERE id='p1-file0-symbol'") is not None

    db.execute("DELETE FROM sessions WHERE id='p0-s0'")
    for table, column, value in (
        ("memories", "id", "p0-s0-memory"),
        ("memory_sources", "memory_id", "p0-s0-memory"),
        ("retrievals", "id", "p0-s0-retrieval"),
        ("passports", "retrieval_id", "p0-s0-retrieval"),
        ("events", "id", "p0-s0-event"),
    ):
        assert db.one(f"SELECT * FROM {table} WHERE {column}=?", (value,)) is None
    assert db.one("SELECT id FROM sessions WHERE id='p0-s1'") is not None
    assert db.one("SELECT id FROM events WHERE id='p0-project-event'") is not None

    Indexer(db).remove_project("p0")
    assert db.rows("SELECT id FROM projects") == [{"id": "p1"}]
    assert db.rows("SELECT DISTINCT project_id FROM file_search") == [{"project_id": "p1"}]
    assert len(db.rows("SELECT * FROM files")) == 2
    assert len(db.rows("SELECT * FROM symbols")) == 2
    assert len(db.rows("SELECT * FROM sessions")) == 2
    assert len(db.rows("SELECT * FROM memories")) == 2
    assert len(db.rows("SELECT * FROM memory_sources")) == 2
    assert len(db.rows("SELECT * FROM retrievals")) == 2
    assert len(db.rows("SELECT * FROM passports")) == 2
    assert len(db.rows("SELECT * FROM events")) == 3
    assert db.rows("PRAGMA foreign_key_check") == []
