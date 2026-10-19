"""Experimental excerpts remain separate from complete-file context preparation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from memglide.integrations.preload import TASK_SEPARATOR, prepare_prompt
from memglide.integrations.source_excerpts import prepare_symbol_excerpt
from memglide.storage.database import Database


@pytest.fixture
def approved(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "approved"
    root.mkdir()
    database = tmp_path / "state" / "state.db"
    Database(database).execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("approved", str(root), "approved", time.time()),
    )
    return root, database


def indexed(approved: tuple[Path, Path], source: str, path: str = "source.py") -> None:
    root, database = approved
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.encode("utf-8"))
    Database(database).execute(
        "INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            path,
            "approved",
            path,
            hashlib.sha256(source.encode()).hexdigest(),
            "python",
            len(source.encode()),
            target.stat().st_mtime,
            0,
            None,
            time.time(),
        ),
    )


def request(approved: tuple[Path, Path], **kwargs: Any) -> dict[str, Any]:
    arguments = {
        "project_id": "approved",
        "db_path": approved[1],
        "source_path": "source.py",
        "symbol": "total",
        "enabled": True,
    }
    arguments.update(kwargs)
    return prepare_symbol_excerpt("Fix total.\n", **arguments)


def envelope(response: dict[str, Any]) -> dict[str, Any]:
    return json.loads(response["prompt"].split(TASK_SEPARATOR)[0])


def selected_units(response: dict[str, Any]) -> list[dict[str, Any]]:
    contents = envelope(response)["memglide_excerpts"][0]["declarations"]
    return [
        {**metadata, "content": content}
        for metadata, content in zip(response["files"][0]["units"], contents, strict=True)
    ]


def test_disabled_import_has_no_heavy_imports_or_database_access(tmp_path: Path) -> None:
    source_root = str(Path(__file__).resolve().parents[1] / "src")
    program = r"""
import builtins
import sqlite3
import sys
sys.path.insert(0, sys.argv[1])
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.startswith(("memglide.storage", "memglide.security", "pathspec", "tree_sitter")):
        raise AssertionError(name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from memglide.integrations.source_excerpts import prepare_symbol_excerpt
sqlite3.connect = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("state"))
result = prepare_symbol_excerpt("EXACT", project_id="x", db_path=sys.argv[2],
                                source_path="file.py", symbol="f")
assert result["reason"] == "disabled" and result["prompt"] == "EXACT"
assert result["files"] == [] and result["context_bytes"] == 0
"""
    database = tmp_path / "never-created" / "state.db"
    subprocess.run(
        [sys.executable, "-I", "-c", program, source_root, str(database)],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert not database.parent.exists()


def test_exact_functions_and_constant_closure_without_complete_file_claim(
    approved: tuple[Path, Path],
) -> None:
    source = (
        '"""Whole module docs are intentionally not a function excerpt."""\n'
        "FACTOR = 2\n\n"
        "def helper(value):\n    return value * FACTOR\n\n"
        "def total(value):\n    return helper(value) + 1\n\n"
        "def unrelated(value):\n    return value - 100\n"
    )
    indexed(approved, source)
    before = approved[1].read_bytes()
    response = request(approved)
    assert response["mode"] == "experimental_excerpt"
    assert response["full_source"] is False and response["experimental"] is True
    assert response["prompt"].endswith(TASK_SEPARATOR + "Fix total.\n")
    data = envelope(response)
    assert "incomplete file" in data["notice"]
    assert "Complete snapshot" not in data["notice"]
    selected = data["memglide_excerpts"][0]
    assert selected["full_source"] is False
    assert response["files"][0]["source_sha256"] == hashlib.sha256(source.encode()).hexdigest()
    units = selected_units(response)
    assert [unit["symbol"] for unit in units] == ["FACTOR", "helper", "total"]
    assert not any(field in response["prompt"] for field in ("sha256", "start_line", "end_line"))
    lines = source.splitlines(keepends=True)
    for unit in units:
        content = "".join(lines[unit["start_line"] - 1 : unit["end_line"]])
        assert unit["content"] == content
        assert unit["sha256"] == hashlib.sha256(content.encode()).hexdigest()
    assert all("content" not in unit for unit in response["files"][0]["units"])
    assert "unrelated" not in response["prompt"]
    assert approved[1].read_bytes() == before
    assert response["context_bytes"] == len(response["prompt"].encode()) - len(b"Fix total.\n")
    assert response["model_calls"] == 0
    # Execution is limited to this controlled test-owned fixture, never upstream code.
    whole: dict[str, Any] = {}
    excerpt: dict[str, Any] = {}
    exec(compile(source, "test-owned-whole", "exec"), whole)
    exec(
        compile("\n".join(unit["content"] for unit in units), "test-owned-excerpt", "exec"),
        excerpt,
    )
    assert [whole["total"](value) for value in range(-5, 6)] == [
        excerpt["total"](value) for value in range(-5, 6)
    ]


def test_diamond_dependency_is_once_and_original_order(approved: tuple[Path, Path]) -> None:
    indexed(
        approved,
        "def leaf(value):\n    return value + 1\n\n"
        "def left(value):\n    return leaf(value)\n\n"
        "def right(value):\n    return leaf(value) + 1\n\n"
        "def total(value):\n    return left(value) + right(value)\n",
    )
    response = request(approved)
    units = selected_units(response)
    assert [unit["symbol"] for unit in units] == ["leaf", "left", "right", "total"]
    assert len({(unit["start_line"], unit["end_line"]) for unit in units}) == 4


def test_recursion_has_bounded_single_unit(approved: tuple[Path, Path]) -> None:
    indexed(
        approved,
        "def total(value):\n    if value < 1:\n        return 1\n    return value * total(value - 1)\n",
    )
    assert [unit["symbol"] for unit in selected_units(request(approved))] == ["total"]


def test_exact_utf8_crlf_string_and_range(approved: tuple[Path, Path]) -> None:
    source = 'def total(value="café\u2028ok"):\r\n    return value\r\n'
    indexed(approved, source)
    response = request(approved)
    unit = selected_units(response)[0]
    assert unit["content"] == source and unit["end_line"] == 2


@pytest.mark.parametrize(
    "source",
    [
        "import math\ndef total(value):\n    return value\n",
        "from __future__ import annotations\ndef total(value):\n    return value\n",
        "class Container:\n    pass\ndef total(value):\n    return value\n",
        "@decorate\ndef total(value):\n    return value\n",
        "async def total(value):\n    return value\n",
        "def total(value: unknown):\n    return value\n",
        "def total(value) -> int:\n    return value\n",
        "def total(value=make()):\n    return value\n",
        "def unused(value=make()):\n    return value\ndef total(value):\n    return value\n",
        "def unused(value: make()):\n    return value\ndef total(value):\n    return value\n",
        "GLOBAL = make()\ndef total(value):\n    return value\n",
        "VALUES = []\ndef total(value):\n    return value\n",
        "VALUES = {}\ndef total(value):\n    return value\n",
        "VALUE = other\ndef total(value):\n    return value\n",
        "VALUE = 1\nVALUE += 1\ndef total(value):\n    return value\n",
        "print('side effect')\ndef total(value):\n    return value\n",
        "def total(value):\n    return value.append(1)\n",
        "def total(value):\n    value[0] = 1\n    return value\n",
        "def total(value):\n    value += 1\n    return value\n",
        "def total(value):\n    return eval(value)\n",
        "def total(value):\n    exec(value)\n    return value\n",
        "def total(value):\n    return getattr(value, 'x')\n",
        "def total(value):\n    return globals()\n",
        "def total(value):\n    return locals()\n",
        "def total(value):\n    return __import__(value)\n",
        "def total(value):\n    return value()\n",
        "def total(value):\n    return (lambda x: x)(value)\n",
        "def total(value):\n    return [item for item in value]\n",
        "def total(value):\n    yield value\n",
        "def total(value):\n    global changed\n    return value\n",
        "def total(value):\n    def nested():\n        return 1\n    return value\n",
        "def total(value):\n    return missing(value)\n",
        "def unused(value):\n    return missing\ndef total(value):\n    return value\n",
        "def total(value):\n    return value\ndef total(value):\n    return value + 1\n",
        "FACTOR = 1; OTHER = 2\ndef total(value):\n    return value\n",
        "def total(válue):\n    return válue\n",
        "def ｔｏｔａｌ(value):\n    return value\n",
        "def total(value, value):\n    return value\n",
        "def total(sum):\n    return sum\n",
        "sum = 1\ndef total(value):\n    return value\n",
        "def total(value):\n    return min(**value)\n",
    ],
)
def test_unsupported_or_uncertain_modules_never_return_partial_context(
    approved: tuple[Path, Path], source: str
) -> None:
    indexed(approved, source)
    response = request(approved)
    assert response["mode"] == "passthrough" and response["prompt"] == "Fix total.\n"
    assert response["context_bytes"] == 0 and response["files"] == []


def test_dependency_cap_and_missing_symbol(approved: tuple[Path, Path]) -> None:
    indexed(
        approved,
        "A = 1\nB = 2\nC = 3\nD = 4\ndef total(value):\n    return value + A + B + C + D\n",
    )
    assert request(approved)["reason"] == "excerpt_dependency_limit"
    assert request(approved, symbol="unknown")["reason"] == "excerpt_symbol_unavailable"


@pytest.mark.parametrize("change", ["content", "delete", "unindex", "parse_error", "language"])
def test_stale_deleted_unindexed_and_incompatible_index_fallback(
    approved: tuple[Path, Path], change: str
) -> None:
    indexed(approved, "def total(value):\n    return value\n")
    root, database = approved
    if change == "content":
        (root / "source.py").write_text("def total(value):\n    return value + 1\n")
    elif change == "delete":
        (root / "source.py").unlink()
    elif change == "unindex":
        Database(database).execute("DELETE FROM files")
    elif change == "parse_error":
        Database(database).execute("UPDATE files SET parse_error='stale syntax'")
    else:
        Database(database).execute("UPDATE files SET language='typescript'")
    assert request(approved)["mode"] == "passthrough"


@pytest.mark.parametrize("ignore", [".gitignore", ".memglideignore", "setting"])
def test_current_ignore_policy_fallback(approved: tuple[Path, Path], ignore: str) -> None:
    indexed(approved, "def total(value):\n    return value\n")
    if ignore == "setting":
        Database(approved[1]).execute(
            "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
            ("ignored_directories", json.dumps(["source.py"])),
        )
    else:
        (approved[0] / ignore).write_text("source.py\n")
    assert request(approved)["reason"] == "source_excluded"


def test_sensitive_content_and_secret_paths_are_not_exposed(approved: tuple[Path, Path]) -> None:
    indexed(
        approved,
        'api_key = "sk-abcdefghijklmnopqrstuvwxyz123456789"\ndef total(value):\n    return value\n',
    )
    response = request(approved)
    assert response["mode"] == "passthrough" and "sk-" not in response["prompt"]
    indexed(approved, "def total(value):\n    return value\n", ".env/source.py")
    assert request(approved, source_path=".env/source.py")["reason"] == "source_excluded"


def test_symlink_source_and_root_do_not_escape(approved: tuple[Path, Path], tmp_path: Path) -> None:
    source = "def total(value):\n    return value\n"
    indexed(approved, source)
    outside = tmp_path / "outside.py"
    outside.write_text(source)
    (approved[0] / "source.py").unlink()
    (approved[0] / "source.py").symlink_to(outside)
    assert request(approved)["mode"] == "passthrough"
    moved = approved[0].with_name("moved")
    approved[0].rename(moved)
    approved[0].symlink_to(moved, target_is_directory=True)
    assert request(approved)["reason"] == "project_unavailable"


def test_unapproved_missing_database_and_oversized_context(
    approved: tuple[Path, Path], tmp_path: Path
) -> None:
    indexed(approved, "def total(value):\n    return value\n")
    assert request(approved, project_id="other")["reason"] == "project_unavailable"
    missing = tmp_path / "missing" / "state.db"
    assert request(approved, db_path=missing)["reason"] == "database_unavailable"
    assert not missing.parent.exists()
    assert request(approved, max_context_bytes=1)["reason"] == "context_budget_exceeded"
    indexed(approved, "#" + "x" * 64_000 + "\ndef total(value):\n    return value\n")
    assert request(approved)["mode"] == "passthrough"


@pytest.mark.parametrize("race", ["source", "index", "policy", "approval"])
def test_double_checks_catch_mid_preparation_changes(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, race: str
) -> None:
    import memglide.integrations.source_excerpts as excerpts

    indexed(approved, "def total(value):\n    return value\n")
    original_units = excerpts._units

    def changed(source: str, symbol: str) -> list[dict[str, Any]]:
        units = original_units(source, symbol)
        if race == "source":
            (approved[0] / "source.py").write_text("def total(value):\n    return value + 1\n")
        elif race == "index":
            Database(approved[1]).execute("UPDATE files SET hash=?", ("0" * 64,))
        elif race == "policy":
            (approved[0] / ".memglideignore").write_text("source.py\n")
        else:
            Database(approved[1]).execute("DELETE FROM projects")
        return units

    monkeypatch.setattr(excerpts, "_units", changed)
    response = request(approved)
    assert response["mode"] == "passthrough" and response["context_bytes"] == 0


def test_existing_complete_source_preload_is_unchanged(approved: tuple[Path, Path]) -> None:
    source = (
        "import anything\n\nclass Container:\n    pass\n\ndef total(value):\n    return value\n"
    )
    indexed(approved, source)
    assert request(approved)["mode"] == "passthrough"
    complete = prepare_prompt(
        "Fix total.",
        project_id="approved",
        db_path=approved[1],
        focus_paths=["source.py"],
        context_format="compact-prefix",
    )
    assert complete["mode"] == "preloaded"
    assert (
        json.loads(complete["prompt"].split(TASK_SEPARATOR)[0])["memglide_sources"][0]["content"]
        == source
    )


@pytest.mark.parametrize(
    "arguments",
    [
        {"source_path": "../outside.py"},
        {"source_path": "/outside.py"},
        {"source_path": "a\\b.py"},
        {"source_path": "a//b.py"},
        {"symbol": "válue"},
        {"symbol": "__builtins__"},
        {"symbol": "a.b"},
        {"symbol": "return"},
        {"enabled": 1},
        {"max_context_bytes": 0},
        {"context_format": "compact-prefix"},
    ],
)
def test_invalid_arguments_are_rejected_without_state(
    approved: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, arguments: dict[str, Any]
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("state access")

    monkeypatch.setattr(sqlite3, "connect", forbidden)
    with pytest.raises(ValueError):
        request(approved, **arguments)
