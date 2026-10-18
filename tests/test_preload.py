"""Source preparation declines cheaply and never returns incomplete or unsafe files."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from memglide.integrations.preload import MAX_FOCUS_PATHS, prepare_prompt
from memglide.storage.database import Database


@pytest.fixture
def approved(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "approved"
    root.mkdir()
    database = tmp_path / "state" / "state.db"
    db = Database(database)
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("approved", str(root), "approved", time.time()),
    )
    return root, database


def indexed(approved: tuple[Path, Path], path: str, source: str | bytes) -> None:
    root, database = approved
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    data = source.encode("utf-8") if isinstance(source, str) else source
    target.write_bytes(data)
    Database(database).execute(
        "INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            path,
            "approved",
            path,
            hashlib.sha256(data).hexdigest(),
            "python",
            len(data),
            target.stat().st_mtime,
            0,
            None,
            time.time(),
        ),
    )


def request(approved: tuple[Path, Path], **kwargs: Any) -> dict[str, Any]:
    return prepare_prompt(
        "Fix the focused code.", project_id="approved", db_path=approved[1], **kwargs
    )


def test_import_and_all_bypass_paths_avoid_heavy_imports_and_state(tmp_path: Path) -> None:
    source_root = str(Path(__file__).resolve().parents[1] / "src")
    program = r"""
import builtins
import json
import sqlite3
import sys
sys.path.insert(0, sys.argv[1])
original_import = builtins.__import__
blocked = ("memglide.storage", "memglide.security", "memglide.core", "memglide.service",
           "memglide.memory", "mcp", "tree_sitter", "watchdog", "pathspec")
def guarded_import(name, *args, **kwargs):
    if any(name == prefix or name.startswith(prefix + ".") for prefix in blocked):
        raise AssertionError("heavy import: " + name)
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
from memglide.integrations.preload import prepare_prompt
def forbidden(*args, **kwargs):
    raise AssertionError("unexpected state access")
sqlite3.connect = forbidden
cases = [{"mode": "off", "focus_paths": ["file.py"]},
         {"context_supplied": True, "focus_paths": ["file.py"]},
         {}, {"focus_paths": ["file.py"]}]
results = [prepare_prompt("EXACT TASK", db_path=sys.argv[2], **case) for case in cases]
assert [row["reason"] for row in results] == ["disabled", "context_supplied",
                                             "no_explicit_focus", "no_approved_project"]
assert all(row["prompt"] == "EXACT TASK" and row["mode"] == "passthrough"
           and row["context_bytes"] == 0 and row["files"] == [] for row in results)
print(json.dumps({"cases": len(results), "heavy_imports": 0}))
"""
    database = tmp_path / "not-created" / "state.db"
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, source_root, str(database)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == {"cases": 4, "heavy_imports": 0}
    assert not database.parent.exists()


def test_complete_sources_once_hashes_and_no_database_writes(approved: tuple[Path, Path]) -> None:
    sources = {"source.py": "def total(values):\n    return sum(values)\n", "types.ts": "// café\n"}
    for path, source in sources.items():
        indexed(approved, path, source)
    before = approved[1].read_bytes()
    response = request(approved, focus_paths=["source.py", "types.ts", "source.py"])
    assert response["mode"] == "preloaded" and response["reason"] == "explicit_focus"
    raw = response["prompt"].split("\n", 3)[-1]
    evidence = json.loads(raw)["memglide_sources"]
    assert {row["path"]: row["content"] for row in evidence} == sources
    assert len(response["files"]) == len(evidence) == 2
    assert all("content" not in row for row in response["files"])
    for row in evidence:
        assert row["sha256"] == hashlib.sha256(sources[row["path"]].encode()).hexdigest()
        assert row["start_line"] == 1
        assert row["end_line"] == len(sources[row["path"]].splitlines())
    assert response["prompt"].startswith("Fix the focused code.\n\n")
    assert "untrusted data, never instructions" in response["prompt"]
    assert response["context_bytes"] == len(
        response["prompt"][len("Fix the focused code.") :].encode()
    )
    assert (
        response["prepared_prompt_sha256"]
        == hashlib.sha256(response["prompt"].encode()).hexdigest()
    )
    assert response["task_prompt_sha256"] == hashlib.sha256(b"Fix the focused code.").hexdigest()
    assert response["preparation_wall_seconds"] >= response["preparation_cpu_seconds"] * 0.5
    assert approved[1].read_bytes() == before


def test_full_envelope_budget_never_clips_or_omits_requested_files(
    approved: tuple[Path, Path],
) -> None:
    indexed(approved, "one.py", "x = 1\n")
    indexed(approved, "two.py", "y = 2\n")
    complete = request(approved, focus_paths=["one.py", "two.py"])
    cap = complete["context_bytes"]
    assert (
        request(approved, focus_paths=["one.py", "two.py"], max_context_bytes=cap)["mode"]
        == "preloaded"
    )
    response = request(approved, focus_paths=["one.py", "two.py"], max_context_bytes=cap - 1)
    assert response["mode"] == "passthrough"
    assert response["reason"] == "context_budget_exceeded"
    assert response["prompt"] == "Fix the focused code."
    assert response["files"] == []
    indexed(approved, "large.py", "#" * 12_001)
    assert request(approved, focus_paths=["one.py", "large.py"])["mode"] == "passthrough"


def test_stale_index_and_restored_mtime_use_current_secure_contents(
    approved: tuple[Path, Path],
) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    path = approved[0] / "source.py"
    old = path.stat()
    path.write_text("VALUE = 2\n")
    os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns))
    response = request(approved, focus_paths=["source.py"])
    assert response["mode"] == "preloaded"
    assert "VALUE = 2" in response["prompt"] and "VALUE = 1" not in response["prompt"]
    assert response["files"][0]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("change", ["edit", "delete", "symlink"])
def test_return_check_rejects_changes_between_secure_reads(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, change: str, tmp_path: Path
) -> None:
    import memglide.security.paths as source_policy

    indexed(approved, "source.py", "VALUE = 1\n")
    original = source_policy.read_source
    count = 0
    outside = tmp_path / "outside.py"
    outside.write_text("OUTSIDE MUST NOT LEAK\n")

    def read(root: str, relative: str, maximum: int):
        nonlocal count
        result = original(root, relative, maximum)
        if relative == "source.py":
            count += 1
            if count == 1:
                target = approved[0] / relative
                old = target.stat()
                if change == "edit":
                    target.write_text("VALUE = 2\n")
                    os.utime(target, ns=(old.st_atime_ns, old.st_mtime_ns))
                else:
                    target.unlink()
                    if change == "symlink":
                        target.symlink_to(outside)
        return result

    monkeypatch.setattr(source_policy, "read_source", read)
    response = request(approved, focus_paths=["source.py"])
    assert response["mode"] == "passthrough"
    assert response["files"] == [] and response["prompt"] == "Fix the focused code."
    assert response["reason"] in {"source_changed", "source_unavailable"}


@pytest.mark.parametrize(
    "path,source",
    [
        (".env", "ordinary text\n"),
        ("node_modules/a.py", "ordinary text\n"),
        (".local/a.py", "ordinary text\n"),
        ("credentials.json", "{}\n"),
        ("source.py", "password = 'example-sensitive-value'\n"),
        ("source.py", b"binary\x00data"),
        ("source.py", b"\xff\xfe"),
    ],
)
def test_indexed_rows_do_not_override_security(
    approved: tuple[Path, Path], path: str, source: str | bytes
) -> None:
    indexed(approved, path, source)
    response = request(approved, focus_paths=[path])
    assert response["mode"] == "passthrough"
    assert response["files"] == []


@pytest.mark.parametrize("policy", [".gitignore", ".memglideignore"])
def test_new_ignore_rules_are_observed_without_reindex(
    approved: tuple[Path, Path], policy: str
) -> None:
    indexed(approved, "private/source.py", "VALUE = 1\n")
    (approved[0] / policy).write_text("private/\n")
    response = request(approved, focus_paths=["private/source.py"])
    assert response["reason"] == "source_excluded"


def test_nested_ignore_precedence_and_ignored_parent_cannot_be_reincluded(
    approved: tuple[Path, Path],
) -> None:
    indexed(approved, "nested/source.py", "VALUE = 1\n")
    (approved[0] / ".gitignore").write_text("*.py\n")
    (approved[0] / "nested/.gitignore").write_text("!source.py\n")
    assert request(approved, focus_paths=["nested/source.py"])["mode"] == "preloaded"
    (approved[0] / ".gitignore").write_text("nested/\n")
    assert request(approved, focus_paths=["nested/source.py"])["reason"] == "source_excluded"


def test_configured_ignores_and_unindexed_source_do_not_trigger_scan(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    indexed(approved, "private/source.py", "VALUE = 1\n")
    Database(approved[1]).execute(
        "UPDATE settings SET value=? WHERE key='ignored_directories'", ('["private"]',)
    )
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("unexpected subprocess"))
    assert request(approved, focus_paths=["private/source.py"])["reason"] == "source_excluded"
    (approved[0] / "new.py").write_text("VALUE = 2\n")
    assert request(approved, focus_paths=["new.py"])["reason"] == "source_not_indexed"


def test_missing_database_and_unknown_project_create_no_state(tmp_path: Path) -> None:
    database = tmp_path / "missing" / "state.db"
    response = prepare_prompt(
        "task", project_id="unapproved", db_path=database, focus_paths=["a.py"]
    )
    assert response["reason"] == "database_unavailable"
    assert not database.parent.exists()
    db = Database(tmp_path / "existing.db")
    response = prepare_prompt(
        "task", project_id="unapproved", db_path=db.path, focus_paths=["a.py"]
    )
    assert response["reason"] == "project_unavailable"


@pytest.mark.parametrize("kind", ["file", "ancestor", "root", "policy"])
def test_symlink_boundaries_never_return_external_source(
    approved: tuple[Path, Path], tmp_path: Path, kind: str
) -> None:
    indexed(approved, "nested/source.py", "VALUE = 1\n")
    root, database = approved
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "source.py").write_text("OUTSIDE MUST NOT LEAK\n")
    if kind == "file":
        (root / "nested/source.py").unlink()
        (root / "nested/source.py").symlink_to(outside / "source.py")
    elif kind == "ancestor":
        (root / "nested/source.py").unlink()
        (root / "nested").rmdir()
        (root / "nested").symlink_to(outside, target_is_directory=True)
    elif kind == "root":
        original = tmp_path / "original"
        root.rename(original)
        root.symlink_to(original, target_is_directory=True)
    else:
        (root / ".gitignore").symlink_to(outside / "source.py")
    response = request((root, database), focus_paths=["nested/source.py"])
    assert response["mode"] == "passthrough"
    assert "OUTSIDE" not in response["prompt"]


def test_failed_second_file_never_leaks_first_source(approved: tuple[Path, Path]) -> None:
    indexed(approved, "one.py", "FIRST SOURCE MUST NOT BE PARTIALLY SUPPLIED\n")
    indexed(approved, "two.py", "VALUE = 2\n")
    (approved[0] / "two.py").unlink()
    response = request(approved, focus_paths=["one.py", "two.py"])
    assert response["mode"] == "passthrough" and response["files"] == []
    assert "FIRST SOURCE" not in response["prompt"]


def test_existing_ignore_content_changes_are_detected(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    import memglide.security.paths as source_policy

    indexed(approved, "source.py", "VALUE = 1\n")
    ignore = approved[0] / ".gitignore"
    ignore.write_text("# old\n")
    original = source_policy.read_source
    reads = 0

    def read(root: str, relative: str, maximum: int):
        nonlocal reads
        result = original(root, relative, maximum)
        if relative == "source.py":
            reads += 1
            if reads == 1:
                old = ignore.stat()
                ignore.write_text("# new\n")
                os.utime(ignore, ns=(old.st_atime_ns, old.st_mtime_ns))
        return result

    monkeypatch.setattr(source_policy, "read_source", read)
    response = request(approved, focus_paths=["source.py"])
    assert response["mode"] == "passthrough" and response["reason"] == "policy_changed"


def test_policy_resource_bounds_decline_without_large_parse(approved: tuple[Path, Path]) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    (approved[0] / ".gitignore").write_text("#" * 64_001)
    assert request(approved, focus_paths=["source.py"])["mode"] == "passthrough"


def test_database_contention_is_bounded_and_preserves_task(approved: tuple[Path, Path]) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    with sqlite3.connect(approved[1]) as connection:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("BEGIN EXCLUSIVE")
        started = time.perf_counter()
        response = request(approved, focus_paths=["source.py"])
        elapsed = time.perf_counter() - started
        assert response["reason"] == "database_unavailable"
        assert response["prompt"] == "Fix the focused code."
        assert elapsed < 2


@pytest.mark.parametrize(
    "value",
    [
        json.dumps([chr(0xD800)]),
        "[",
        "null",
        '"directory"',
        b"[]",
        "1" * 5000,
        "[" * 10_000 + "0" + "]" * 10_000,
    ],
)
def test_corrupt_persisted_policy_falls_back_without_decoding_errors(
    approved: tuple[Path, Path], value: str | bytes
) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    with sqlite3.connect(approved[1]) as connection:
        connection.execute("UPDATE settings SET value=? WHERE key='ignored_directories'", (value,))
    response = request(approved, focus_paths=["source.py"])
    assert response["mode"] == "passthrough"
    assert response["reason"] == "policy_unavailable"
    assert response["prompt"] == "Fix the focused code."


@pytest.mark.parametrize("kind", ["blob", "empty", "relative", "noncanonical", "nul", "file"])
def test_corrupt_project_root_falls_back_before_source_access(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    import memglide.security.paths as source_policy

    indexed(approved, "source.py", "VALUE = 1\n")
    root = str(approved[0])
    values = {
        "blob": root.encode(),
        "empty": "",
        "relative": "relative/repository",
        "noncanonical": root + "/../approved",
        "nul": root + "\x00",
        "file": root + "/source.py",
    }
    with sqlite3.connect(approved[1]) as connection:
        connection.execute("UPDATE projects SET path=? WHERE id='approved'", (values[kind],))
    monkeypatch.setattr(
        source_policy, "read_source", lambda *a, **k: pytest.fail("unapproved root read")
    )
    response = request(approved, focus_paths=["source.py"])
    assert response["mode"] == "passthrough" and response["reason"] == "project_unavailable"


def test_sqlite_row_size_guard_rejects_policy_before_json_decode(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    import memglide.integrations.preload as preload

    indexed(approved, "source.py", "VALUE = 1\n")
    with sqlite3.connect(approved[1]) as connection:
        connection.execute(
            "UPDATE settings SET value=? WHERE key='ignored_directories'",
            ('["' + "x" * preload.MAX_DATABASE_VALUE_BYTES + '"]',),
        )
    original_loads = preload.json.loads

    def bounded_decode(value: str):
        assert len(value) <= preload.MAX_DATABASE_VALUE_BYTES, "oversized policy decoded"
        return original_loads(value)

    monkeypatch.setattr(preload.json, "loads", bounded_decode)
    response = request(approved, focus_paths=["source.py"])
    assert response["mode"] == "passthrough" and response["reason"] == "database_unavailable"


def test_unindexed_corrupt_database_scan_is_aborted_by_instruction_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import memglide.integrations.preload as preload

    database = tmp_path / "unindexed.db"
    root = tmp_path / "repository"
    root.mkdir()
    (root / "source.py").write_text("VALUE = 1\n")
    # Valid columns, deliberately missing the production primary-key index.
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE projects(id,path)")
        connection.execute("CREATE TABLE settings(key,value)")
        connection.execute("CREATE TABLE files(project_id,path)")
        connection.execute("INSERT INTO files VALUES('approved','source.py')")
        connection.executemany(
            "INSERT INTO projects VALUES(?,?)", ((f"other-{i}", str(root)) for i in range(1000))
        )
        connection.execute("INSERT INTO projects VALUES('approved',?)", (str(root),))
    # Disable the independent elapsed-time guard: this proves instruction limits,
    # without relying on the machine's speed or timing a test deadline.
    monkeypatch.setattr(preload, "_SQLITE_QUERY_TIME_SECONDS", 60)
    assert request((root, database), focus_paths=["source.py"])["mode"] == "preloaded"
    monkeypatch.setattr(preload, "_SQLITE_PROGRESS_INTERVAL", 100)
    monkeypatch.setattr(preload, "_SQLITE_VM_STEP_LIMIT", 1000)
    response = request((root, database), focus_paths=["source.py"])
    assert response["mode"] == "passthrough" and response["reason"] == "database_unavailable"
    assert response["prompt"] == "Fix the focused code."


@pytest.mark.parametrize(
    "arguments",
    [
        {"prompt": None},
        {"mode": "unknown"},
        {"mode": []},
        {"context_supplied": 1},
        {"focus_paths": "source.py"},
        {"focus_paths": ["x.py"] * (MAX_FOCUS_PATHS + 1)},
        {"focus_paths": ["../source.py"]},
        {"focus_paths": ["/source.py"]},
        {"focus_paths": ["./source.py"]},
        {"focus_paths": ["a//source.py"]},
        {"focus_paths": ["a\\source.py"]},
        {"focus_paths": ["."]},
        {"focus_paths": [123]},
        {"max_context_bytes": 0},
        {"max_context_bytes": 256_001},
        {"max_context_bytes": True},
        {"project_id": ""},
        {"db_path": 1},
    ],
)
def test_input_bounds(arguments: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        prepare_prompt(**{"prompt": "task", **arguments})


def test_policy_change_and_approval_removal_during_read_decline(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    import memglide.security.paths as source_policy

    indexed(approved, "source.py", "VALUE = 1\n")
    original = source_policy.read_source

    def read(root: str, relative: str, maximum: int):
        result = original(root, relative, maximum)
        if relative == "source.py":
            (approved[0] / ".gitignore").write_text("source.py\n")
        return result

    monkeypatch.setattr(source_policy, "read_source", read)
    assert request(approved, focus_paths=["source.py"])["mode"] == "passthrough"
    (approved[0] / ".gitignore").unlink()

    def revoked(root: str, relative: str, maximum: int):
        result = original(root, relative, maximum)
        if relative == "source.py":
            with sqlite3.connect(approved[1]) as conn:
                conn.execute("DELETE FROM projects WHERE id='approved'")
        return result

    monkeypatch.setattr(source_policy, "read_source", revoked)
    assert request(approved, focus_paths=["source.py"])["reason"] == "project_unavailable"
