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
def test_one_native_exec_preserves_prompt_options_environment_and_exit(native, source):
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
    arguments = ["--mode", "off", "--preparation-report", str(native["report"])]
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


def test_prepared_complete_source_reaches_native_stdin_without_report_duplication(native, tmp_path):
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
    result = launch(
        native,
        [
            "--project",
            "approved",
            "--db",
            str(database),
            "--focus",
            "totals.py",
            "--preparation-report",
            str(native["report"]),
            "Fix the totals.",
            "--",
            "--json",
        ],
    )
    assert result.returncode == 17, result.stderr
    observed = json.loads(native["capture"].read_text())
    preparation = json.loads(native["report"].read_text())["preparation"]
    assert preparation["mode"] == "preloaded"
    assert preparation["files"] == [
        {
            "path": "totals.py",
            "sha256": hashlib.sha256(source.encode()).hexdigest(),
            "start_line": 1,
            "end_line": 2,
        }
    ]
    assert observed["stdin"].startswith("Fix the totals.\n\n")
    envelope = json.loads(observed["stdin"][observed["stdin"].index('{"memglide_sources"') :])
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
