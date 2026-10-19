"""Explicit supporting files share the bounded, fresh source snapshot boundary."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from memglide.integrations.preload import (
    MAX_FOCUS_PATHS,
    MAX_SUPPORT_PATHS,
    TASK_SEPARATOR,
    prepare_prompt,
)
from memglide.storage.database import Database

TASK = " \r\nFix the focused code.\n\nTask:\nKeep these exact task bytes.\n "


@pytest.fixture
def approved(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repository"
    root.mkdir()
    database = tmp_path / "state" / "state.db"
    Database(database).execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("approved", str(root), "approved", time.time()),
    )
    return root, database


@pytest.fixture(params=("legacy", "compact-prefix"))
def context_format(request: pytest.FixtureRequest) -> str:
    return request.param


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


def prepare(approved: tuple[Path, Path], **kwargs: Any) -> dict[str, Any]:
    return prepare_prompt(TASK, project_id="approved", db_path=approved[1], **kwargs)


def contents(response: dict[str, Any]) -> dict[str, str]:
    if response["context_format"] == "compact-prefix":
        prefix = response["prompt"][: -len(TASK_SEPARATOR + TASK)]
    else:
        prefix = response["prompt"].split("This is not memory.\n", 1)[1]
    return {row["path"]: row["content"] for row in json.loads(prefix)["memglide_sources"]}


def assert_declined(response: dict[str, Any]) -> None:
    assert response["mode"] == "passthrough"
    assert response["prompt"].encode() == TASK.encode()
    assert response["files"] == []
    assert response["context_bytes"] == 0
    assert response["prompt_layout"] == "unchanged"


def test_complete_focus_and_support_without_discovery_or_database_writes(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, context_format: str
) -> None:
    import memglide.integrations.preload as preload
    import memglide.security.paths as source_policy

    sources = {
        "src/value.py": "def value():\n    return 1\n",
        "tests/test_value.py": "# café\r\ndef test_value():\r\n    assert value() == 2\r\n",
    }
    for path, source in sources.items():
        indexed(approved, path, source)
    before = approved[1].read_bytes()
    source_reads: list[str] = []
    selections: list[tuple[str, ...]] = []
    original_read = source_policy.read_source
    original_selection = preload._selection

    def read(root: str, relative: str, maximum: int):
        source_reads.append(relative)
        return original_read(root, relative, maximum)

    def select(database: Path, project: str, paths: tuple[str, ...]):
        selections.append(paths)
        return original_selection(database, project, paths)

    monkeypatch.setattr(source_policy, "read_source", read)
    monkeypatch.setattr(preload, "_selection", select)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("unexpected process"))
    response = prepare(
        approved,
        focus_paths=["src/value.py"],
        support_paths=["tests/test_value.py"],
        context_format=context_format,
    )
    assert response["mode"] == "preloaded"
    assert response["reason"] == "explicit_focus"
    assert contents(response) == sources
    assert response["focus_paths"] == ["src/value.py"]
    assert response["support_paths"] == ["tests/test_value.py"]
    assert source_reads.count("src/value.py") == source_reads.count("tests/test_value.py") == 2
    assert len(selections) == 2
    assert all(set(paths) == set(sources) for paths in selections)
    assert approved[1].read_bytes() == before
    if context_format == "compact-prefix":
        prefix = response["prompt"][: -len(TASK_SEPARATOR + TASK)]
        assert response["prompt"].endswith(TASK_SEPARATOR + TASK)
        assert set(json.loads(prefix)) == {"notice", "memglide_sources"}
        assert all(
            set(row) == {"path", "content"} for row in json.loads(prefix)["memglide_sources"]
        )
    else:
        assert response["prompt"].startswith(TASK + "\n\n")
    for file in response["files"]:
        assert file == {
            "path": file["path"],
            "sha256": hashlib.sha256(sources[file["path"]].encode()).hexdigest(),
            "start_line": 1,
            "end_line": len(sources[file["path"]].splitlines()),
        }


def test_empty_support_preserves_existing_schema_and_prepared_bytes(
    approved: tuple[Path, Path], context_format: str
) -> None:
    indexed(approved, "b.py", "B = 2\n")
    indexed(approved, "a.py", "A = 1\n")
    arguments = {"focus_paths": ["b.py", "a.py", "b.py"], "context_format": context_format}
    original = prepare(approved, **arguments)
    for empty in ([], ()):
        explicit = prepare(approved, support_paths=empty, **arguments)
        for key in ("preparation_wall_seconds", "preparation_cpu_seconds"):
            original.pop(key, None)
            explicit.pop(key)
        assert explicit == original
        assert "focus_paths" not in explicit and "support_paths" not in explicit


def test_overlap_deduplication_and_order_are_private_classification_only(
    approved: tuple[Path, Path], context_format: str
) -> None:
    sources = {path: f"# {path}\n" for path in ("z.py", "a.py", "t_z.py", "t_a.py")}
    for path, source in sources.items():
        indexed(approved, path, source)
    response = prepare(
        approved,
        focus_paths=["z.py", "a.py", "z.py"],
        support_paths=["t_z.py", "a.py", "t_a.py", "t_z.py"],
        context_format=context_format,
    )
    assert contents(response) == sources
    if context_format == "compact-prefix":
        assert response["focus_paths"] == ["a.py", "z.py"]
        assert response["support_paths"] == ["t_a.py", "t_z.py"]
        assert [row["path"] for row in response["files"]] == sorted(sources)
    else:
        assert response["focus_paths"] == ["z.py", "a.py"]
        assert response["support_paths"] == ["t_z.py", "t_a.py"]
        assert [row["path"] for row in response["files"]] == ["z.py", "a.py", "t_z.py", "t_a.py"]
    overlap_only = prepare(
        approved, focus_paths=["a.py"], support_paths=["a.py"], context_format=context_format
    )
    plain = prepare(approved, focus_paths=["a.py"], context_format=context_format)
    assert overlap_only["prompt"] == plain["prompt"]
    assert overlap_only["support_paths"] == []
    assert overlap_only["focus_paths"] == ["a.py"]


def test_compact_bundle_is_canonical_across_request_order_and_exact_task_changes(
    approved: tuple[Path, Path],
) -> None:
    for path in ("z.py", "a.py", "t_z.py", "t_a.py"):
        indexed(approved, path, f"# {path}\n")
    first = prepare(
        approved,
        focus_paths=["z.py", "a.py"],
        support_paths=["t_z.py", "t_a.py"],
        context_format="compact-prefix",
    )
    second = prepare_prompt(
        "A different task.",
        project_id="approved",
        db_path=approved[1],
        focus_paths=["a.py", "z.py"],
        support_paths=["t_a.py", "t_z.py"],
        context_format="compact-prefix",
    )
    assert first["prompt"][: -len(TASK)] == second["prompt"][: -len("A different task.")]


def test_accepts_twelve_bounded_explicit_paths(approved: tuple[Path, Path]) -> None:
    focus = [f"source_{i}.py" for i in range(MAX_FOCUS_PATHS)]
    support = [f"test_{i}.py" for i in range(MAX_SUPPORT_PATHS)]
    for path in focus + support:
        indexed(approved, path, "# tiny\n")
    response = prepare(
        approved, focus_paths=focus, support_paths=support, context_format="compact-prefix"
    )
    assert response["mode"] == "preloaded" and len(response["files"]) == 12
    assert set(response["focus_paths"]) == set(focus)
    assert set(response["support_paths"]) == set(support)


def test_full_bundle_budget_accounts_for_envelope_and_discards_every_file(
    approved: tuple[Path, Path], context_format: str
) -> None:
    indexed(approved, "source.py", "# source must never leak partially\n")
    indexed(approved, "tests/test_source.py", "assert value() == 2\n")
    arguments = {
        "focus_paths": ["source.py"],
        "support_paths": ["tests/test_source.py"],
        "context_format": context_format,
    }
    full = prepare(approved, **arguments)
    assert full["mode"] == "preloaded"
    assert full["context_bytes"] == len(full["prompt"].encode()) - len(TASK.encode())
    exact = prepare(approved, max_context_bytes=full["context_bytes"], **arguments)
    assert exact["prompt"] == full["prompt"]
    declined = prepare(approved, max_context_bytes=full["context_bytes"] - 1, **arguments)
    assert_declined(declined)
    assert declined["reason"] == "context_budget_exceeded"
    indexed(approved, "tests/test_source.py", "#" * 12_001)
    assert_declined(prepare(approved, **arguments))


@pytest.mark.parametrize("path", ["source.py", "tests/test_source.py"])
def test_stale_index_and_restored_mtime_return_current_focus_and_support(
    approved: tuple[Path, Path], context_format: str, path: str
) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    indexed(approved, "tests/test_source.py", "assert value() == 1\n")
    target = approved[0] / path
    old = target.stat()
    updated = "# New current source or test\nVALUE = 2\n"
    target.write_text(updated)
    os.utime(target, ns=(old.st_atime_ns, old.st_mtime_ns))
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=["tests/test_source.py"],
        context_format=context_format,
    )
    assert response["mode"] == "preloaded"
    assert contents(response)[path] == updated
    metadata = next(row for row in response["files"] if row["path"] == path)
    assert metadata["sha256"] == hashlib.sha256(updated.encode()).hexdigest()


@pytest.mark.parametrize("path", ["source.py", "tests/test_source.py"])
@pytest.mark.parametrize("change", ["edit", "delete", "symlink"])
def test_changed_focus_or_support_discards_complete_bundle(
    approved: tuple[Path, Path],
    context_format: str,
    path: str,
    change: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import memglide.security.paths as source_policy

    indexed(approved, "source.py", "VALUE = 1\n")
    indexed(approved, "tests/test_source.py", "assert value() == 1\n")
    outside = tmp_path / "outside.py"
    outside.write_text("OUTSIDE SOURCE MUST NOT LEAK\n")
    original = source_policy.read_source
    count = 0

    def read(root: str, relative: str, maximum: int):
        nonlocal count
        data = original(root, relative, maximum)
        if relative == path:
            count += 1
            if count == 1:
                target = approved[0] / path
                old = target.stat()
                if change == "edit":
                    target.write_text("VALUE = 2\n")
                    os.utime(target, ns=(old.st_atime_ns, old.st_mtime_ns))
                else:
                    target.unlink()
                    if change == "symlink":
                        target.symlink_to(outside)
        return data

    monkeypatch.setattr(source_policy, "read_source", read)
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=["tests/test_source.py"],
        context_format=context_format,
    )
    assert_declined(response)
    assert response["reason"] in {"source_changed", "source_unavailable"}


@pytest.mark.parametrize("policy", [".gitignore", ".memglideignore", "approval", "settings"])
def test_policy_changes_during_support_read_discard_every_file(
    approved: tuple[Path, Path],
    context_format: str,
    policy: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import memglide.security.paths as source_policy

    indexed(approved, "source.py", "VALUE = 1\n")
    indexed(approved, "tests/test_source.py", "assert value() == 1\n")
    original = source_policy.read_source
    changed = False

    def read(root: str, relative: str, maximum: int):
        nonlocal changed
        data = original(root, relative, maximum)
        if relative == "tests/test_source.py" and not changed:
            changed = True
            if policy == "approval":
                Database(approved[1]).execute("DELETE FROM projects WHERE id='approved'")
            elif policy == "settings":
                Database(approved[1]).execute(
                    "UPDATE settings SET value=? WHERE key='ignored_directories'", ('["tests"]',)
                )
            else:
                (approved[0] / policy).write_text("# policy changed\n")
        return data

    monkeypatch.setattr(source_policy, "read_source", read)
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=["tests/test_source.py"],
        context_format=context_format,
    )
    assert_declined(response)
    assert response["reason"] in {"policy_changed", "project_unavailable"}


@pytest.mark.parametrize(
    "support,source",
    [
        ("tests/.env", "ordinary text\n"),
        ("tests/credentials.json", "{}\n"),
        ("node_modules/test.py", "assert True\n"),
        ("tests/.local/test.py", "assert True\n"),
        ("tests/test_source.py", "password = 'example-sensitive-value'\n"),
        ("tests/test_source.py", b"binary\x00data"),
        ("tests/test_source.py", b"\xff\xfe"),
    ],
)
def test_support_indexing_does_not_override_security(
    approved: tuple[Path, Path], context_format: str, support: str, source: str | bytes
) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    indexed(approved, support, source)
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=[support],
        context_format=context_format,
    )
    assert_declined(response)


@pytest.mark.parametrize("policy", [".gitignore", ".memglideignore", "settings", "nested"])
def test_current_support_ignores_override_stale_index(
    approved: tuple[Path, Path], context_format: str, policy: str
) -> None:
    indexed(approved, "source.py", "VALUE = 1\n")
    indexed(approved, "tests/private/test_source.py", "assert value() == 1\n")
    if policy == "settings":
        Database(approved[1]).execute(
            "UPDATE settings SET value=? WHERE key='ignored_directories'", ('["tests"]',)
        )
    elif policy == "nested":
        (approved[0] / "tests/.gitignore").write_text("private/\n")
    else:
        (approved[0] / policy).write_text("tests/\n")
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=["tests/private/test_source.py"],
        context_format=context_format,
    )
    assert_declined(response)
    assert response["reason"] == "source_excluded"


@pytest.mark.parametrize("state", ["unindexed", "deleted", "symlink", "ancestor_symlink"])
def test_support_unavailable_never_partially_supplies_focus(
    approved: tuple[Path, Path], context_format: str, state: str, tmp_path: Path
) -> None:
    indexed(approved, "source.py", "# focus must not leak partially\nVALUE = 1\n")
    support = "tests/test_source.py"
    indexed(approved, support, "assert value() == 1\n")
    root, database = approved
    if state == "unindexed":
        Database(database).execute("DELETE FROM files WHERE path=?", (support,))
    else:
        (root / support).unlink()
        if state in {"symlink", "ancestor_symlink"}:
            outside = tmp_path / "outside"
            outside.mkdir()
            (outside / "test_source.py").write_text("OUTSIDE SOURCE MUST NOT LEAK\n")
            if state == "symlink":
                (root / support).symlink_to(outside / "test_source.py")
            else:
                (root / "tests").rmdir()
                (root / "tests").symlink_to(outside, target_is_directory=True)
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=[support],
        context_format=context_format,
    )
    assert_declined(response)
    assert response["support_paths"] == [support]
    assert response["focus_paths"] == ["source.py"]


@pytest.mark.parametrize(
    "support",
    [
        "test.py",
        {"test.py"},
        ["test.py"] * (MAX_SUPPORT_PATHS + 1),
        ["../test.py"],
        ["/test.py"],
        ["./test.py"],
        ["a//test.py"],
        ["a\\test.py"],
        ["."],
        [""],
        [123],
        ["a\x00.py"],
        ["test_\ud800.py"],
        ["x" * 4097],
        ["/".join(["nested"] * 32 + ["test.py"])],
    ],
)
def test_support_bounds_are_checked_before_state_access(
    support: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sqlite3

    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("unexpected state"))
    with pytest.raises(ValueError, match="support"):
        prepare_prompt(TASK, focus_paths=["source.py"], support_paths=support, mode="off")


def test_support_paths_do_not_bypass_focus_approval_or_cheap_decline(tmp_path: Path) -> None:
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
cases = [{"mode": "off", "focus_paths": ["source.py"], "project_id": "approved"},
         {"context_supplied": True, "focus_paths": ["source.py"], "project_id": "approved"},
         {"project_id": "approved"}, {"focus_paths": ["source.py"]}]
results = [prepare_prompt("EXACT TASK", db_path=sys.argv[2], support_paths=["test.py"],
                          context_format=form, **case)
           for form in ("legacy", "compact-prefix") for case in cases]
assert [row["reason"] for row in results] == ["disabled", "context_supplied",
                                             "no_explicit_focus", "no_approved_project"] * 2
assert all(row["prompt"] == "EXACT TASK" and row["mode"] == "passthrough"
           and row["context_bytes"] == 0 and row["files"] == []
           and row["prompt_layout"] == "unchanged" and row["support_paths"] == ["test.py"]
           for row in results)
print(json.dumps({"cases": len(results), "heavy_imports": 0}))
"""
    database = tmp_path / "must-not-create" / "state.db"
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, source_root, str(database)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == {"cases": 8, "heavy_imports": 0}
    assert not database.parent.exists()


def test_focus_surrogates_are_rejected_before_state_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sqlite3

    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("unexpected state"))
    with pytest.raises(ValueError, match="focus"):
        prepare_prompt(TASK, project_id="approved", focus_paths=["source_\ud800.py"])


def test_maximum_support_path_depth_remains_supported(approved: tuple[Path, Path]) -> None:
    support = "/".join(["nested"] * 31 + ["test_source.py"])
    indexed(approved, "source.py", "VALUE = 1\n")
    indexed(approved, support, "assert value() == 1\n")
    response = prepare(
        approved,
        focus_paths=["source.py"],
        support_paths=[support],
        context_format="compact-prefix",
    )
    assert response["mode"] == "preloaded"
    assert contents(response)[support] == "assert value() == 1\n"
