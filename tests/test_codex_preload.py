"""The optional preloader forwards once to native Codex without auxiliary calls."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

from memglide.integrations import codex_preload
from memglide.storage.database import Database


@pytest.fixture
def native(tmp_path: Path):
    """The fake installed executable must be outside the checked-out repository."""
    with tempfile.TemporaryDirectory(prefix="memglide-native-") as directory:
        executable = Path(directory) / "codex"
        executable.write_text(
            f"#!{sys.executable}\n"
            "import hashlib,json,os,sys\n"
            "from pathlib import Path\n"
            "payload=sys.stdin.buffer.read()\n"
            "report=Path(os.environ['MEMGLIDE_TEST_REPORT'])\n"
            "record={'argv':sys.argv,'stdin':payload.decode('utf-8'),"
            "'stdin_sha256':hashlib.sha256(payload).hexdigest(),"
            "'report_before_exec':json.loads(report.read_text()) if report.exists() else None,"
            "'environment':{key:os.environ.get(key) for key in "
            "('CODEX_HOME','HTTP_PROXY','HTTPS_PROXY','SSL_CERT_FILE','MEMGLIDE_TEST_AUTH')}}\n"
            "with open(os.environ['MEMGLIDE_TEST_CAPTURE'],'a') as output:\n"
            " output.write(json.dumps(record)+'\\n')\n"
            "raise SystemExit(int(os.environ.get('MEMGLIDE_TEST_EXIT','17')))\n"
        )
        executable.chmod(0o700)
        repository = tmp_path / "repository"
        repository.mkdir()
        (repository / ".git").mkdir()
        report = tmp_path / "preparation.json"
        capture = tmp_path / "native.jsonl"
        codex_home = tmp_path / "native-home"
        codex_home.mkdir()
        (codex_home / "config.toml").write_text('[mcp_servers.existing]\ncommand="retained"\n')
        environment = {
            **os.environ,
            "PATH": f"{directory}{os.pathsep}{os.environ.get('PATH', '')}",
            "CODEX_HOME": str(codex_home),
            "HTTP_PROXY": "http://synthetic-proxy.invalid:8080",
            "HTTPS_PROXY": "http://synthetic-proxy.invalid:8080",
            "SSL_CERT_FILE": str(tmp_path / "synthetic-ca.pem"),
            "MEMGLIDE_TEST_AUTH": "synthetic-auth-must-not-be-reported",
            "MEMGLIDE_TEST_REPORT": str(report),
            "MEMGLIDE_TEST_CAPTURE": str(capture),
        }
        yield {
            "executable": executable,
            "repository": repository,
            "report": report,
            "capture": capture,
            "environment": environment,
        }


def launch(native: dict[str, Any], arguments: list[str], prompt_input: str | None = None):
    return subprocess.run(
        [sys.executable, "-I", "-m", "memglide.integrations.codex_preload", *arguments],
        cwd=native["repository"],
        env=native["environment"],
        input=prompt_input,
        capture_output=True,
        text=True,
        timeout=15,
    )


@pytest.mark.parametrize("source", ["positional", "stdin", "stdin_dash"])
@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_one_native_exec_preserves_prompt_options_environment_and_exit(
    native, source, context_format
):
    prompt = "Fix 'quotes', $HOME and `literal`; λ\r\nkeep the next line.\rfinal line.\n"
    options = [
        "--json",
        "--output-schema",
        "schema with spaces.json",
        "--model",
        "test-model",
        "-c",
        'model_reasoning_effort="low"',
        "-c",
        'mcp_servers.other.command="unchanged"',
    ]
    arguments = [
        "--mode",
        "off",
        "--context-format",
        context_format,
        "--preparation-report",
        str(native["report"]),
    ]
    if source == "positional":
        arguments.append(prompt)
    elif source == "stdin_dash":
        arguments.append("-")
    result = launch(
        native, [*arguments, "--", *options], None if source == "positional" else prompt
    )
    assert result.returncode == 17, result.stderr
    records = native["capture"].read_text().splitlines()
    assert len(records) == 1
    observed = json.loads(records[0])
    assert observed["argv"] == [str(native["executable"]), "exec", *options, "--", "-"]
    assert observed["stdin"] == prompt
    assert observed["environment"] == {
        key: native["environment"][key]
        for key in (
            "CODEX_HOME",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "SSL_CERT_FILE",
            "MEMGLIDE_TEST_AUTH",
        )
    }
    report = json.loads(native["report"].read_text())
    assert observed["report_before_exec"] == report
    assert report["exec_argv"] == observed["argv"]
    assert report["preparation"]["mode"] == "passthrough"
    assert report["preparation"]["reason"] == "disabled"
    if context_format == "legacy":
        assert report["version"] == 1
        assert "context_format" not in report["preparation"]
        assert "prompt_layout" not in report["preparation"]
    else:
        assert report["version"] == 2
        assert report["preparation"]["context_format"] == "compact-prefix"
        assert report["preparation"]["prompt_layout"] == "unchanged"
    assert report["preparation"]["task_prompt_sha256"] == observed["stdin_sha256"]
    assert report["preparation"]["prepared_prompt_sha256"] == observed["stdin_sha256"]
    assert report["native_stdin"] == {
        "sha256": observed["stdin_sha256"],
        "bytes": len(prompt.encode("utf-8")),
        "transport": "temporary_file_descriptor",
    }
    assert report["native_exec_boundary_monotonic_seconds"] <= time.monotonic()
    assert native["report"].stat().st_mode & 0o777 == 0o600
    assert "synthetic-auth-must-not-be-reported" not in native["report"].read_text()
    assert prompt not in native["report"].read_text()
    assert not result.stdout and not result.stderr
    assert (Path(native["environment"]["CODEX_HOME"]) / "config.toml").read_text() == (
        '[mcp_servers.existing]\ncommand="retained"\n'
    )


@pytest.mark.parametrize("context_format", ["default", "legacy"])
def test_prepared_complete_source_reaches_native_stdin_without_report_duplication(
    native, tmp_path, context_format
):
    prompt = "Fix 'totals'; λ\r\nkeep $HOME and `literal` unchanged.\r"
    repository = native["repository"]
    source = "def calculate_total(items):\n    return sum(items)\n"
    target = repository / "totals.py"
    target.write_text(source)
    database = tmp_path / "state.db"
    db = Database(database)
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("approved", str(repository), "approved", time.time()),
    )
    db.execute(
        "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            "file",
            "approved",
            "totals.py",
            hashlib.sha256(source.encode()).hexdigest(),
            "python",
            len(source),
            target.stat().st_mtime,
            0,
            None,
            time.time(),
        ),
    )
    format_arguments = [] if context_format == "default" else ["--context-format", context_format]
    result = launch(
        native,
        [
            *format_arguments,
            "--project",
            "approved",
            "--db",
            str(database),
            "--focus",
            "totals.py",
            "--preparation-report",
            str(native["report"]),
            prompt,
            "--",
            "--json",
        ],
    )
    assert result.returncode == 17, result.stderr
    observed = json.loads(native["capture"].read_text())
    report = json.loads(native["report"].read_text())
    preparation = report["preparation"]
    assert preparation["mode"] == "preloaded"
    assert preparation["files"] == [
        {
            "path": "totals.py",
            "sha256": hashlib.sha256(source.encode()).hexdigest(),
            "start_line": 1,
            "end_line": 2,
        }
    ]
    if context_format == "legacy":
        assert report["version"] == 1
        assert observed["stdin"].startswith(prompt + "\n\n")
        envelope = json.loads(observed["stdin"][observed["stdin"].index('{"memglide_sources"') :])
        assert envelope["memglide_sources"][0]["sha256"] == preparation["files"][0]["sha256"]
        assert "context_format" not in preparation and "prompt_layout" not in preparation
    else:
        from memglide.integrations.preload import _COMPACT_NOTICE, TASK_SEPARATOR

        assert report["version"] == 2
        assert preparation["context_format"] == "compact-prefix"
        assert preparation["prompt_layout"] == "source_prefix"
        assert observed["stdin"].endswith(TASK_SEPARATOR + prompt)
        envelope = json.loads(observed["stdin"].removesuffix(TASK_SEPARATOR + prompt))
        assert envelope["notice"] == _COMPACT_NOTICE
        assert set(envelope["memglide_sources"][0]) == {"path", "content"}
        assert "sha256" not in observed["stdin"]
        assert "start_line" not in observed["stdin"] and "end_line" not in observed["stdin"]
    assert envelope["memglide_sources"][0]["content"] == source
    assert "calculate_total" not in native["report"].read_text()
    assert preparation["prepared_prompt_sha256"] == observed["stdin_sha256"]


def test_large_prompt_uses_regular_stdin_and_never_process_arguments(native):
    prompt = "large task context α\n" * 16_000
    result = launch(
        native,
        ["--mode", "off", "--preparation-report", str(native["report"]), "--", "--json"],
        prompt,
    )
    assert result.returncode == 17, result.stderr
    observed = json.loads(native["capture"].read_text())
    assert observed["stdin"] == prompt
    assert len(observed["argv"]) == 5 and observed["argv"][-1] == "-"
    assert json.loads(native["report"].read_text())["native_stdin"]["bytes"] > 256_000


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
@pytest.mark.parametrize("missing_support", [False, True])
def test_support_bundle_reaches_one_native_exec_or_falls_back_whole(
    native, tmp_path, context_format, missing_support
):
    repository = native["repository"]
    sources = {
        "totals.py": "def total(items):\n    return sum(items)\n",
        "tests/test_totals.py": "from totals import total\nassert total([2, 3]) == 5\n",
    }
    database = tmp_path / "bundle-state.db"
    db = Database(database)
    db.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        ("approved", str(repository), "approved", time.time()),
    )
    for ordinal, (path, content) in enumerate(sources.items()):
        target = repository / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        if missing_support and path.startswith("tests/"):
            continue
        db.execute(
            "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                f"file-{ordinal}",
                "approved",
                path,
                hashlib.sha256(content.encode()).hexdigest(),
                "python",
                len(content),
                target.stat().st_mtime,
                0,
                None,
                time.time(),
            ),
        )
    prompt = "Fix totals and add a regression; λ\r\nkeep task bytes.\r"
    result = launch(
        native,
        [
            "--context-format",
            context_format,
            "--project",
            "approved",
            "--db",
            str(database),
            "--focus",
            "totals.py",
            "--support",
            "tests/test_totals.py",
            "--support",
            "totals.py",
            "--preparation-report",
            str(native["report"]),
            prompt,
            "--",
            "--json",
        ],
    )
    assert result.returncode == 17, result.stderr
    records = native["capture"].read_text().splitlines()
    assert len(records) == 1
    observed = json.loads(records[0])
    report = json.loads(native["report"].read_text())
    prepared = report["preparation"]
    assert report["version"] == 3
    assert prepared["focus_paths"] == ["totals.py"]
    assert prepared["support_paths"] == ["tests/test_totals.py"]
    assert report["native_stdin"]["sha256"] == observed["stdin_sha256"]
    assert "assert total" not in native["report"].read_text()
    if missing_support:
        assert observed["stdin"] == prompt
        assert prepared["mode"] == "passthrough" and prepared["files"] == []
        assert prepared["reason"] == "source_not_indexed"
    else:
        assert prepared["mode"] == "preloaded"
        assert {row["path"] for row in prepared["files"]} == set(sources)
        if context_format == "compact-prefix":
            from memglide.integrations.preload import TASK_SEPARATOR

            assert observed["stdin"].endswith(TASK_SEPARATOR + prompt)
            envelope = json.loads(observed["stdin"].removesuffix(TASK_SEPARATOR + prompt))
        else:
            assert observed["stdin"].startswith(prompt)
            envelope = json.loads(
                observed["stdin"][observed["stdin"].index('{"memglide_sources"') :]
            )
        assert {item["path"]: item["content"] for item in envelope["memglide_sources"]} == sources


@pytest.mark.parametrize("mutation", ["focus", "support", "missing", "unexpected_file"])
def test_private_support_classification_cannot_disagree_with_requested_files(mutation):
    value, _ = compact_preparation("Task")
    value.update(focus_paths=["a.py"], support_paths=["z.py"])
    if mutation == "focus":
        value["focus_paths"] = ["z.py"]
    elif mutation == "support":
        value["support_paths"] = []
    elif mutation == "missing":
        del value["support_paths"]
    else:
        value["focus_paths"] = ["a.py", "other.py"]
    with pytest.raises(ValueError):
        codex_preload._validated_preparation(
            value, "Task", "compact-prefix", focus_paths=["a.py"], support_paths=["z.py"]
        )


def test_complete_snapshot_cannot_include_unrequested_files():
    value, _ = compact_preparation("Task")
    with pytest.raises(ValueError, match="complete requested file set"):
        codex_preload._validated_preparation(value, "Task", "compact-prefix", focus_paths=["a.py"])


def test_explicit_installed_binary_and_safe_fallback_are_reported(native, tmp_path):
    result = launch(
        native,
        [
            "--codex-executable",
            str(native["executable"]),
            "--mode",
            "preload",
            "--project",
            "missing",
            "--db",
            str(tmp_path / "missing.db"),
            "--focus",
            "missing.py",
            "--preparation-report",
            str(native["report"]),
            "Original task",
        ],
    )
    assert result.returncode == 17
    assert "source preparation skipped (database_unavailable)" in result.stderr
    observed = json.loads(native["capture"].read_text())
    assert observed["stdin"] == "Original task"
    assert observed["report_before_exec"]["preparation"]["mode"] == "passthrough"
    assert not (tmp_path / "missing.db").exists()


@pytest.mark.parametrize(
    "arguments, prompt_input, diagnostic",
    [
        (["--max-context-bytes", "0", "Task"], None, "max_context_bytes"),
        (["--focus", "../outside.py", "Task"], None, "focus paths"),
        (["--codex-executable", "relative/codex", "Task"], None, "absolute installed"),
        (["--mode", "invalid", "Task"], None, "invalid choice"),
        ([], "", "task prompt must not be empty"),
    ],
)
def test_invalid_inputs_do_not_launch_or_write_success_report(
    native, arguments, prompt_input, diagnostic
):
    result = launch(
        native,
        ["--preparation-report", str(native["report"]), *arguments],
        prompt_input,
    )
    assert result.returncode != 0 and diagnostic in result.stderr
    assert not native["capture"].exists() and not native["report"].exists()


def test_report_failure_prevents_native_execution(native, tmp_path):
    result = launch(
        native,
        ["--preparation-report", str(tmp_path / "missing-directory" / "report.json"), "Task"],
    )
    assert result.returncode != 0
    assert "memglide-codex:" in result.stderr
    assert not native["capture"].exists()


def test_repository_path_and_symlink_shadows_are_skipped(native, tmp_path):
    shadow = native["repository"] / "codex"
    shadow.write_text("#!/bin/sh\nexit 99\n")
    shadow.chmod(0o700)
    outside_link = tmp_path / "bin"
    outside_link.mkdir()
    (outside_link / "codex").symlink_to(shadow)
    native["environment"]["PATH"] = os.pathsep.join(
        [str(native["repository"]), str(outside_link), str(native["executable"].parent)]
    )
    result = launch(native, ["Task"])
    assert result.returncode == 17, result.stderr
    assert json.loads(native["capture"].read_text())["argv"][0] == str(native["executable"])


def test_only_repository_binary_is_an_error(native):
    native["environment"]["PATH"] = str(native["repository"])
    result = launch(native, ["Task"])
    assert result.returncode == 127
    assert "outside the current repository" in result.stderr
    assert not native["capture"].exists()


def test_import_and_bypass_use_no_sdk_state_or_network(tmp_path):
    program = """
import builtins, json, sys
original=builtins.__import__
blocked=('memglide.storage','memglide.security','memglide.service','memglide.core',
         'mcp','tree_sitter','watchdog','pathspec')
def guarded(name,*args,**kwargs):
    if any(name == prefix or name.startswith(prefix+'.') for prefix in blocked):
        raise AssertionError('unexpected heavy import '+name)
    return original(name,*args,**kwargs)
builtins.__import__=guarded
from memglide.integrations import codex_preload
import memglide.integrations.preload
captured=[]
codex_preload._find_codex=lambda *args: '/installed/codex'
codex_preload.os.dup2=lambda *args,**kwargs: None
codex_preload.os.execve=lambda *args: captured.append(args)
assert codex_preload.main(['--context-supplied','--project','approved',
                          '--focus','known.py','--db',sys.argv[1],'Task']) == 0
assert len(captured)==1
assert captured[0][1] == ['/installed/codex','exec','--','-']
assert not any(name.startswith(blocked) for name in sys.modules)
print(json.dumps({'execs':len(captured),'heavy_imports':0}))
"""
    database = tmp_path / "uncreated" / "state.db"
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(database)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"execs": 1, "heavy_imports": 0}
    assert not database.parent.exists()


def test_invalid_preparer_result_cannot_be_reported_as_success(native, monkeypatch, capsys):
    import memglide.integrations.preload as preload

    monkeypatch.setattr(codex_preload, "_find_codex", lambda *args: str(native["executable"]))
    monkeypatch.setattr(preload, "prepare_prompt", lambda *args, **kwargs: {"mode": "preloaded"})
    executed = []
    monkeypatch.setattr(codex_preload.os, "execve", lambda *args: executed.append(args))
    result = codex_preload.main(["--preparation-report", str(native["report"]), "Task"])
    assert result == 1 and "invalid metadata" in capsys.readouterr().err
    assert not executed and not native["report"].exists()


def test_failed_atomic_replace_preserves_prior_report_and_cleans_temporary(tmp_path, monkeypatch):
    report = tmp_path / "report.json"
    report.write_text("prior content\n")

    def denied(*args):
        raise PermissionError("synthetic report failure")

    monkeypatch.setattr(codex_preload.os, "replace", denied)
    with pytest.raises(PermissionError, match="synthetic report failure"):
        codex_preload._write_report(report, {"version": 1})
    assert report.read_text() == "prior content\n"
    assert list(tmp_path.iterdir()) == [report]


def compact_preparation(prompt: str) -> tuple[dict[str, Any], dict[str, Any]]:
    from memglide.integrations.preload import _COMPACT_NOTICE, TASK_SEPARATOR

    sources = [
        {"path": "a.py", "content": "def first():\n    return 'λ'\n"},
        {"path": "z.py", "content": "# source may itself contain a separator\n\nTask:\n"},
    ]
    envelope = {"notice": _COMPACT_NOTICE, "memglide_sources": sources}
    prepared = (
        json.dumps(envelope, ensure_ascii=False, separators=(",", ":")) + TASK_SEPARATOR + prompt
    )
    return (
        {
            "prompt": prepared,
            "mode": "preloaded",
            "reason": "explicit_focus",
            "task_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prepared_prompt_sha256": hashlib.sha256(prepared.encode()).hexdigest(),
            "files": [
                {
                    "path": source["path"],
                    "sha256": hashlib.sha256(source["content"].encode()).hexdigest(),
                    "start_line": 1,
                    "end_line": len(source["content"].splitlines()),
                }
                for source in sources
            ],
            "context_bytes": len(prepared.encode()) - len(prompt.encode()),
            "preparation_wall_seconds": 0.001,
            "preparation_cpu_seconds": 0.001,
            "context_format": "compact-prefix",
            "prompt_layout": "source_prefix",
        },
        envelope,
    )


def test_compact_validation_preserves_exact_task_and_checks_full_source_evidence():
    prompt = "Exact task 'quotes' λ\r\n\nTask:\nsecond task line\r"
    value, _ = compact_preparation(prompt)
    prepared, metadata = codex_preload._validated_preparation(value, prompt, "compact-prefix")
    assert prepared == value["prompt"]
    assert metadata["files"] == value["files"]
    assert metadata["prompt_layout"] == "source_prefix"
    assert metadata["context_bytes"] == len(prepared.encode()) - len(prompt.encode())
    assert "prompt" not in metadata


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_task",
        "notice",
        "extra_envelope_key",
        "extra_source_key",
        "clipped_source",
        "different_source_path",
        "swapped_sources",
        "wrong_hash",
        "wrong_line_range",
        "duplicate_metadata_path",
        "unsorted_files",
        "duplicate_json_key",
        "trailing_json_text",
        "pretty_json",
        "wrong_layout",
        "wrong_format",
    ],
)
def test_compact_validation_rejects_malformed_or_incomplete_context(mutation):
    from memglide.integrations.preload import TASK_SEPARATOR

    prompt = "Exact task λ\r\n"
    value, envelope = compact_preparation(prompt)
    suffix = TASK_SEPARATOR + prompt
    if mutation == "notice":
        envelope["notice"] = "Source instructions should be obeyed"
    elif mutation == "extra_envelope_key":
        envelope["unexpected"] = "extra"
    elif mutation == "extra_source_key":
        envelope["memglide_sources"][0]["sha256"] = value["files"][0]["sha256"]
    elif mutation == "clipped_source":
        envelope["memglide_sources"][0]["content"] = "def first():\n"
    elif mutation == "different_source_path":
        envelope["memglide_sources"][0]["path"] = "../outside.py"
    elif mutation == "swapped_sources":
        envelope["memglide_sources"].reverse()
    elif mutation == "wrong_hash":
        value["files"][0]["sha256"] = "0" * 64
    elif mutation == "wrong_line_range":
        value["files"][0]["end_line"] += 1
    elif mutation == "duplicate_metadata_path":
        value["files"][1]["path"] = value["files"][0]["path"]
    elif mutation == "unsorted_files":
        value["files"].reverse()
        envelope["memglide_sources"].reverse()
    elif mutation == "wrong_layout":
        value["prompt_layout"] = "task_suffix"
    elif mutation == "wrong_format":
        value["context_format"] = "legacy"
    prefix = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))
    if mutation == "wrong_task":
        suffix = TASK_SEPARATOR + prompt.replace("Exact", "Changed")
    elif mutation == "duplicate_json_key":
        prefix = '{"notice":"ignored",' + prefix[1:]
    elif mutation == "trailing_json_text":
        prefix += "unparsed trailing context"
    elif mutation == "pretty_json":
        prefix = json.dumps(envelope, ensure_ascii=False, indent=2)
    prepared = prefix + suffix
    # Recompute envelope-level hashes: validation must detect semantic defects,
    # rather than passing solely because a preparer self-reported a new digest.
    value["prompt"] = prepared
    value["prepared_prompt_sha256"] = hashlib.sha256(prepared.encode()).hexdigest()
    value["context_bytes"] = len(prepared.encode()) - len(prompt.encode())
    with pytest.raises(ValueError, match="compact|preparation"):
        codex_preload._validated_preparation(value, prompt, "compact-prefix")


def test_legacy_validation_rejects_task_replacement_but_keeps_report_schema():
    prompt = "Original task"
    value, _ = compact_preparation(prompt)
    prepared = prompt + "\n\nLegacy source context"
    value.update(
        prompt=prepared,
        prepared_prompt_sha256=hashlib.sha256(prepared.encode()).hexdigest(),
        context_bytes=len(prepared.encode()) - len(prompt.encode()),
        context_format="legacy",
        prompt_layout="task_suffix",
    )
    result, metadata = codex_preload._validated_preparation(value, prompt, "legacy")
    assert result == prepared
    assert "context_format" not in metadata and "prompt_layout" not in metadata
    value["prompt"] = "Changed task" + prepared[len(prompt) :]
    value["prepared_prompt_sha256"] = hashlib.sha256(value["prompt"].encode()).hexdigest()
    value["context_bytes"] = len(value["prompt"].encode()) - len(prompt.encode())
    with pytest.raises(ValueError, match="original task prefix"):
        codex_preload._validated_preparation(value, prompt, "legacy")
