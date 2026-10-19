"""Only exact selected evidence references invalidate a retained passport."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from memglide.core.indexer import Indexer
from memglide.service import Service
from memglide.storage.database import Database


@pytest.fixture
def database(tmp_path: Path) -> Database:
    db = Database(tmp_path / "state" / "memglide.db")
    with db.connect() as conn:
        for project in ("project", "foreign"):
            conn.execute(
                "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,0)",
                (project, str(tmp_path / project), project),
            )
            conn.execute(
                "INSERT INTO sessions VALUES(?,?,'task',0,0,99999999999,99999999999,NULL)",
                (project, project),
            )
    return db


def retain(db: Database, passport: dict[str, Any], *, project: str = "project") -> None:
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO retrievals VALUES(?, ?, ?, 'task', 2, 4000, 10, 0, '{}')",
            (project, project, project),
        )
        conn.execute(
            "INSERT INTO passports VALUES(?,?,?)", (project, project, json.dumps(passport))
        )


def invalidate(db: Database, paths: set[str]) -> dict[str, Any]:
    with db.connect() as conn:
        Indexer._invalidate(conn, "project", paths)
    row = db.one("SELECT data FROM passports WHERE retrieval_id='project'")
    assert row is not None
    return json.loads(row["data"])


@pytest.mark.parametrize(
    "metadata",
    [
        {"selected_files": [{"path": "extra.py", "hash": "hash"}]},
        {"selected_files": ["extra.py"]},
        {"verified_source_hashes": {"extra.py": "hash"}},
        {"selected_symbols": [{"path": "extra.py", "symbol": "extra"}]},
        {"selected_files": [{"path": "nested/a.py", "hash": "hash"}]},
        {"query": "Consider a.py after inspecting current evidence"},
        {"missing_context": ["a.py was deliberately omitted"]},
        {"dependencies": [{"source_file": "extra.py", "target_file": "a.py"}]},
    ],
)
def test_unselected_source_mentions_do_not_invalidate(
    database: Database, metadata: dict[str, Any]
) -> None:
    passport = {"status": "Current", "source_freshness": "Current", **metadata}
    retain(database, passport)
    assert invalidate(database, {"a.py"}) == passport


@pytest.mark.parametrize(
    "metadata",
    [
        {"selected_files": [{"path": "a.py", "hash": "hash"}]},
        {"selected_files": ["a.py"]},
        {"verified_source_hashes": {"a.py": "hash"}},
        {"selected_symbols": [{"path": "a.py", "symbol": "a"}]},
    ],
)
def test_exact_selected_source_references_invalidate(
    database: Database, metadata: dict[str, Any]
) -> None:
    retain(database, {"status": "Current", "source_freshness": "Current", **metadata})
    passport = invalidate(database, {"a.py"})
    assert passport["status"] == passport["source_freshness"] == "Stale"
    assert passport["stale_files"] == ["a.py"]
    assert passport["missing_context"] == ["Source changed: a.py"]


def test_unicode_and_quoted_paths_invalidate_exactly_and_warnings_stay_bounded(
    database: Database,
) -> None:
    paths = {'quoted".py', "模块.py"}
    retain(
        database,
        {
            "status": "Current",
            "selected_files": [{"path": path, "hash": "hash"} for path in sorted(paths)],
            "missing_context": ["Existing gap"],
        },
    )
    first = invalidate(database, paths)
    second = invalidate(database, paths)
    assert first == second
    assert first["stale_files"] == sorted(paths)
    assert first["missing_context"] == [
        "Existing gap",
        *(f"Source changed: {path}" for path in sorted(paths)),
    ]


def test_selected_memory_sources_invalidate_without_crossing_project_ownership(
    database: Database,
) -> None:
    with database.connect() as conn:
        for project in ("project", "foreign"):
            conn.execute(
                "INSERT INTO memories VALUES(?,?,'observation','claim','test',0,0,0,?)",
                (project, project, project),
            )
            conn.execute("INSERT INTO memory_sources VALUES(?,'a.py','hash')", (project,))
    retain(database, {"status": "Current", "selected_memory_ids": ["project"]})
    retain(
        database,
        {"status": "Current", "selected_files": [{"path": "a.py", "hash": "hash"}]},
        project="foreign",
    )
    passport = invalidate(database, {"a.py"})
    assert passport["stale_files"] == ["a.py"]
    assert database.one("SELECT stale FROM memories WHERE id='project'") == {"stale": 1}
    assert database.one("SELECT stale FROM memories WHERE id='foreign'") == {"stale": 0}
    foreign = database.one("SELECT data FROM passports WHERE retrieval_id='foreign'")
    assert foreign is not None and json.loads(foreign["data"])["status"] == "Current"


def test_foreign_memory_id_does_not_invalidate_project_passport(database: Database) -> None:
    with database.connect() as conn:
        conn.execute(
            "INSERT INTO memories VALUES('memory','foreign','observation','claim','test',0,0,0,'fp')"
        )
        conn.execute("INSERT INTO memory_sources VALUES('memory','a.py','hash')")
    passport = {"status": "Current", "selected_memory_ids": ["memory"]}
    retain(database, passport)
    assert invalidate(database, {"a.py"}) == passport


def test_actual_retrieval_retains_freshness_until_its_selected_file_changes(tmp_path: Path) -> None:
    repo = tmp_path / "repository"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "a.py").write_text("def a():\n    return 1\n")
    (repo / "extra.py").write_text("def extra():\n    return 2\n")
    service = Service(tmp_path / "state" / "memglide.db")
    try:
        project = service.indexer.add_project(str(repo))
        session = service.memory.start_session(project["id"], "extra")
        result = service.context.get_context(session["id"], "extra", 2, 8000)
        assert [file["path"] for file in result["passport"]["selected_files"]] == ["extra.py"]
        assert result["passport"]["source_freshness"] == "Current"

        (repo / "a.py").write_text("def a():\n    return 3\n")
        service.indexer.reindex(project["id"])
        unchanged = service.context.get_passport(session["id"], result["retrieval_id"])
        assert unchanged == result["passport"]

        (repo / "extra.py").write_text("def extra():\n    return 4\n")
        service.indexer.reindex(project["id"])
        stale = service.context.get_passport(session["id"], result["retrieval_id"])
        assert stale["source_freshness"] == "Stale"
        assert stale["stale_files"] == ["extra.py"]
    finally:
        service.close()
