"""An unchanged secure scan must not rewrite identical dependency graph targets."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

import pytest

import memglide.core.indexer as indexer_module
from memglide.core.indexer import GRAPH_RESOLUTION_VERSION, Indexer
from memglide.storage.database import Database


@pytest.fixture
def repository(tmp_path: Path) -> tuple[Path, Indexer, Database, str]:
    root = tmp_path / "repository"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "helper.py").write_text("def allowed(value):\n    return value > 0\n")
    (root / "app.py").write_text(
        "from helper import allowed\n\ndef authenticate(value):\n    return allowed(value)\n"
    )
    db = Database(tmp_path / "state.sqlite")
    indexer = Indexer(db)
    project_id = indexer.add_project(str(root))["id"]
    return root, indexer, db, project_id


def _edges(db: Database, project_id: str) -> list[dict[str, Any]]:
    return db.rows(
        "SELECT * FROM dependencies WHERE project_id=? ORDER BY id", (project_id,)
    )


def _resolver_spy(indexer: Indexer, monkeypatch: pytest.MonkeyPatch) -> list[int]:
    original = indexer._resolve
    changed_rows: list[int] = []

    def resolve(conn: sqlite3.Connection, project_id: str) -> None:
        before = conn.total_changes
        original(conn, project_id)
        changed_rows.append(conn.total_changes - before)

    monkeypatch.setattr(indexer, "_resolve", resolve)
    return changed_rows


def test_noop_scan_preserves_graph_without_writes_and_still_reads_every_source(
    repository: tuple[Path, Indexer, Database, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, indexer, db, project_id = repository
    before = _edges(db, project_id)
    assert before and all(edge["resolved"] for edge in before)
    changes = _resolver_spy(indexer, monkeypatch)
    reads: list[str] = []
    original_read = indexer_module.read_source

    def read(root: Any, path: str, maximum: int) -> tuple[str, str]:
        reads.append(path)
        return original_read(root, path, maximum)

    monkeypatch.setattr(indexer_module, "read_source", read)
    stats = indexer.reindex(project_id)
    assert stats["indexed"] == stats["deleted"] == 0
    assert stats["unchanged"] == 2
    assert stats["graph_resolution_version"] == GRAPH_RESOLUTION_VERSION
    assert changes == []
    assert sorted(reads) == ["app.py", "helper.py"]
    assert _edges(db, project_id) == before
    # Public search refreshes source eligibility and still returns current bytes.
    assert indexer.search(project_id, "authenticate")[0]["current"] is True
    assert changes == []


@pytest.mark.parametrize("change", ["target_edit", "target_remove", "target_add", "source_edit"])
def test_graph_refreshes_for_target_and_source_changes(
    repository: tuple[Path, Indexer, Database, str],
    monkeypatch: pytest.MonkeyPatch,
    change: str,
) -> None:
    root, indexer, db, project_id = repository
    # Start with an unresolved import for the target-addition case.
    if change == "target_add":
        (root / "helper.py").unlink()
        indexer.reindex(project_id)
        assert not any(edge["resolved"] for edge in _edges(db, project_id))
    changes = _resolver_spy(indexer, monkeypatch)
    if change == "target_edit":
        target = root / "helper.py"
        timestamp = target.stat()
        target.write_text("def blocked(value):\n    return value > 0\n")
        # Equal size and restored timestamps cannot hide the changed declaration.
        os.utime(target, ns=(timestamp.st_atime_ns, timestamp.st_mtime_ns))
    elif change == "target_remove":
        (root / "helper.py").unlink()
    elif change == "target_add":
        (root / "helper.py").write_text("def allowed(value):\n    return value > 0\n")
    else:
        (root / "app.py").write_text(
            "from helper import allowed as check\n\ndef authenticate(value):\n"
            "    return check(value)\n"
        )
    indexer.reindex(project_id)
    assert len(changes) == 1 and changes[0] > 0
    edges = _edges(db, project_id)
    assert len(edges) == 2
    if change in {"target_edit", "target_remove"}:
        assert not any(edge["resolved"] for edge in edges)
    else:
        assert all(edge["resolved"] for edge in edges)
        assert all(edge["target_file"] == "helper.py" for edge in edges)
        if change == "source_edit":
            assert any(edge["reference"] == "check" for edge in edges)
    frozen = _edges(db, project_id)
    indexer.reindex(project_id)
    assert len(changes) == 1 and _edges(db, project_id) == frozen


def test_source_addition_and_removal_preserve_other_graph_edges(
    repository: tuple[Path, Indexer, Database, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, indexer, db, project_id = repository
    original = _edges(db, project_id)
    changes = _resolver_spy(indexer, monkeypatch)
    added = root / "second.py"
    added.write_text("from helper import allowed\n\ndef second(value):\n    return allowed(value)\n")
    indexer.reindex(project_id)
    edges = _edges(db, project_id)
    assert len(changes) == 1 and len(edges) == 4
    assert all(edge["resolved"] for edge in edges)
    assert [edge for edge in edges if edge["source_file"] == "app.py"] == original
    added.unlink()
    indexer.reindex(project_id)
    assert len(changes) == 2 and _edges(db, project_id) == original


@pytest.mark.parametrize("old_version", [None, 0, GRAPH_RESOLUTION_VERSION + 1])
def test_legacy_or_different_resolver_version_refreshes_once_without_source_changes(
    repository: tuple[Path, Indexer, Database, str],
    monkeypatch: pytest.MonkeyPatch,
    old_version: int | None,
) -> None:
    _, indexer, db, project_id = repository
    project = db.project(project_id)
    stats = json.loads(project["index_stats"])
    if old_version is None:
        stats.pop("graph_resolution_version")
    else:
        stats["graph_resolution_version"] = old_version
    db.execute("UPDATE projects SET index_stats=? WHERE id=?", (json.dumps(stats), project_id))
    db.execute(
        "UPDATE dependencies SET resolved=0,target_symbol=NULL,target_file=NULL WHERE project_id=?",
        (project_id,),
    )
    changes = _resolver_spy(indexer, monkeypatch)
    result = indexer.reindex(project_id)
    assert result["indexed"] == 0 and result["unchanged"] == 2
    assert result["graph_resolution_version"] == GRAPH_RESOLUTION_VERSION
    assert changes == [2]
    assert all(edge["resolved"] for edge in _edges(db, project_id))
    indexer.reindex(project_id)
    assert changes == [2]


def test_full_reindex_refreshes_graph_and_lexical_migration_alone_does_not(
    repository: tuple[Path, Indexer, Database, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, indexer, db, project_id = repository
    before = _edges(db, project_id)
    changes = _resolver_spy(indexer, monkeypatch)
    stats = json.loads(db.project(project_id)["index_stats"])
    stats.pop("search_index_version")
    db.execute("UPDATE projects SET index_stats=? WHERE id=?", (json.dumps(stats), project_id))
    refreshed = indexer.reindex(project_id)
    assert refreshed["search_index_refreshed"] == 2 and changes == []
    assert _edges(db, project_id) == before
    indexer.reindex(project_id, full=True)
    assert changes == [2] and _edges(db, project_id) == before


def test_dynamic_calls_stay_unresolved_through_noop_and_source_edit(
    repository: tuple[Path, Indexer, Database, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, indexer, db, project_id = repository
    path = root / "dynamic.py"
    path.write_text("def dispatch(callback, value):\n    return callback(value)\n")
    indexer.reindex(project_id)
    changes = _resolver_spy(indexer, monkeypatch)
    unresolved = [edge for edge in _edges(db, project_id) if edge["source_file"] == "dynamic.py"]
    assert unresolved and all(not edge["resolved"] for edge in unresolved)
    indexer.reindex(project_id)
    assert changes == []
    path.write_text("def dispatch(callback, value):\n    return callback(value + 1)\n")
    indexer.reindex(project_id)
    assert len(changes) == 1
    current = [edge for edge in _edges(db, project_id) if edge["source_file"] == "dynamic.py"]
    assert current and all(not edge["resolved"] for edge in current)


def test_changed_ignore_policy_removes_and_restores_dependency_target(
    repository: tuple[Path, Indexer, Database, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, indexer, db, project_id = repository
    changes = _resolver_spy(indexer, monkeypatch)
    policy = root / ".memglideignore"
    policy.write_text("helper.py\n")
    indexer.reindex(project_id)
    assert len(changes) == 1
    assert not any(edge["resolved"] for edge in _edges(db, project_id))
    policy.unlink()
    indexer.reindex(project_id)
    assert len(changes) == 2
    assert all(edge["resolved"] for edge in _edges(db, project_id))


def test_scan_releases_only_live_verified_unchanged_bodies_and_defaults_to_full_source(
    repository: tuple[Path, Indexer, Database, str]
) -> None:
    root, indexer, db, project_id = repository
    settings = db.settings()
    complete, ignored, errors = indexer._scan(root, settings)
    assert all(body for body, _ in complete.values())
    known = {path: pair[1] for path, pair in complete.items()}
    (root / "helper.py").write_text("def allowed(value):\n    return value < 0\n")
    (root / "new.py").write_text("NEW_VALUE = 4\n")
    thin, thin_ignored, thin_errors = indexer._scan(root, settings, known_hashes=known)
    assert thin["app.py"] == ("", complete["app.py"][1])
    assert thin["helper.py"][0] == (root / "helper.py").read_text()
    assert thin["helper.py"][1] != known["helper.py"]
    assert thin["new.py"][0] == "NEW_VALUE = 4\n"
    assert thin_ignored == ignored and thin_errors == errors
    indexer.reindex(project_id)
    # Unchanged search source and durable FTS payloads remain complete.
    assert "return allowed(value)" in indexer.get_symbol(project_id, "authenticate")["snippet"]
    assert db.one(
        "SELECT content FROM file_search WHERE project_id=? AND path='app.py'", (project_id,)
    ) == {"content": (root / "app.py").read_text()}


@pytest.mark.parametrize("limit", ["bytes", "files"])
def test_releasing_bodies_does_not_relax_real_byte_or_file_resource_limits(
    repository: tuple[Path, Indexer, Database, str],
    monkeypatch: pytest.MonkeyPatch,
    limit: str,
) -> None:
    root, indexer, db, _ = repository
    complete, _, _ = indexer._scan(root, db.settings())
    known = {path: pair[1] for path, pair in complete.items()}
    if limit == "bytes":
        monkeypatch.setattr(
            indexer_module, "MAX_INDEX_BYTES", len(complete["app.py"][0].encode("utf-8"))
        )
    else:
        monkeypatch.setattr(indexer_module, "MAX_INDEXED_FILES", 1)
    full, ignored, errors = indexer._scan(root, db.settings())
    thin, thin_ignored, thin_errors = indexer._scan(root, db.settings(), known_hashes=known)
    assert set(full) == set(thin) == {"app.py"}
    assert thin["app.py"] == ("", full["app.py"][1])
    assert thin_ignored == ignored and thin_errors == errors
    assert any("resource limit" in error["error"] for error in thin_errors)


def test_full_rebuild_retains_all_bodies_for_parsing(
    repository: tuple[Path, Indexer, Database, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, indexer, _, project_id = repository
    original = indexer_module.parse_sources
    parsed: list[dict[str, str]] = []

    def parse(sources: dict[str, str]) -> Any:
        parsed.append(dict(sources))
        return original(sources)

    monkeypatch.setattr(indexer_module, "parse_sources", parse)
    indexer.reindex(project_id)
    assert parsed == [{}]
    indexer.reindex(project_id, full=True)
    assert parsed[-1] == {
        "app.py": (root / "app.py").read_text(),
        "helper.py": (root / "helper.py").read_text(),
    }
