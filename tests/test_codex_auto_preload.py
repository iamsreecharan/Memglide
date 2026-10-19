"""Opt-in discovery forwards complete verified source through one native exec."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

from memglide.integrations import codex_preload
from memglide.integrations.preload import _COMPACT_NOTICE, TASK_SEPARATOR


@pytest.fixture
def automatic_native(tmp_path: Path):
    with tempfile.TemporaryDirectory(prefix="memglide-auto-native-") as directory:
        executable = Path(directory) / "codex"
        executable.write_text(
            f"#!{sys.executable}\n"
            "import json,os,sys\nfrom pathlib import Path\n"
            "payload=sys.stdin.buffer.read().decode('utf-8')\n"
            "record={'stdin':payload,'argv':sys.argv,'environment':"
            "{key:os.environ.get(key) for key in "
            "('CODEX_HOME','HTTP_PROXY','SSL_CERT_FILE','MEMGLIDE_AUTO_TEST_AUTH')},"
            "'report':json.loads(Path(os.environ['MEMGLIDE_AUTO_REPORT']).read_text())}\n"
            "with open(os.environ['MEMGLIDE_AUTO_CAPTURE'],'a') as stream:\n"
            " stream.write(json.dumps(record)+'\\n')\n"
            "raise SystemExit(19)\n"
        )
        executable.chmod(0o700)
        repository = tmp_path / "repository"
        repository.mkdir()
        (repository / ".git").mkdir()
        report = tmp_path / "automatic-preparation.json"
        capture = tmp_path / "native-capture.jsonl"
        environment = {
            **os.environ,
            "CODEX_HOME": str(tmp_path / "synthetic-native-home"),
            "HTTP_PROXY": "http://synthetic-proxy.invalid:8080",
            "SSL_CERT_FILE": str(tmp_path / "synthetic-ca.pem"),
            "MEMGLIDE_AUTO_TEST_AUTH": "synthetic-private-auth-not-for-reports",
            "MEMGLIDE_AUTO_REPORT": str(report),
            "MEMGLIDE_AUTO_CAPTURE": str(capture),
        }
        yield {
            "executable": executable,
            "repository": repository,
            "report": report,
            "capture": capture,
            "environment": environment,
        }


def automatic_launch(native: dict[str, Any], arguments: list[str]):
    return subprocess.run(
        [
            sys.executable, "-I", "-m", "memglide.integrations.codex_preload",
            "--codex-executable", str(native["executable"]),
            "--preparation-report", str(native["report"]), *arguments,
        ],
        cwd=native["repository"],
        env=native["environment"],
        capture_output=True,
        text=True,
        timeout=20,
    )


def automatic_preparation(prompt: str, context_format: str = "compact-prefix") -> dict[str, Any]:
    from memglide.integrations.preload import _EXPLANATION

    source = "def calculate_total(values):\n    return sum(values)\n"
    file = {
        "path": "totals.py", "sha256": hashlib.sha256(source.encode()).hexdigest(),
        "start_line": 1, "end_line": len(source.splitlines()),
    }
    if context_format == "compact-prefix":
        prepared = (
            json.dumps(
                {"notice": _COMPACT_NOTICE,
                 "memglide_sources": [{"path": file["path"], "content": source}]},
                ensure_ascii=False, separators=(",", ":"),
            )
            + TASK_SEPARATOR + prompt
        )
    else:
        prepared = prompt + "\n\n" + _EXPLANATION + json.dumps(
            {"memglide_sources": [{**file, "content": source}]},
            ensure_ascii=False, separators=(",", ":"),
        )
    context_bytes = len(prepared.encode()) - len(prompt.encode())
    return {
        "prompt": prepared, "mode": "preloaded", "reason": "verified_task_sources",
        "task_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prepared_prompt_sha256": hashlib.sha256(prepared.encode()).hexdigest(),
        "files": [file], "context_bytes": context_bytes,
        "preparation_wall_seconds": 0.002, "preparation_cpu_seconds": 0.001,
        "context_format": context_format,
        "prompt_layout": "source_prefix" if context_format == "compact-prefix" else "task_suffix",
        "automatic_selection": {
            "version": 1, "policy_version": "deterministic-source-v1",
            "decision": "FOCUSED_SOURCE", "reason": "verified_task_sources",
            "selected_paths": [file["path"]], "source_versions": {file["path"]: file["sha256"]},
            "ranked_candidates": [{
                "path": file["path"], "score": 37.0, "reason": "matching identifier",
                "evidence_terms": ["total"], "explicit_anchor": False,
            }],
            "estimated_added_tokens": math.ceil(context_bytes / 3),
            "token_estimate_method":
                "ceil(UTF-8 added context bytes / 3); planning proxy, not measured usage",
            "discovery_wall_seconds": 0.001, "discovery_cpu_seconds": 0.001,
            "index_refresh_wall_seconds": 0.0001, "retrieval_wall_seconds": 0.0002,
            "source_preparation_wall_seconds": 0.0003, "auxiliary_model_calls": 0,
            "provided_source_paths": [],
            "static_dependency_coverage":
                "bounded direct resolved production targets; not global completeness",
            "candidate_files_considered": 1, "omitted_candidate_files": 0,
            "dependency_paths_considered": 0, "index_refreshed": True,
            "unresolved_dependency_count": 0, "candidate_generation_limit_reached": False,
        },
    }


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_complete_automatic_preparation_validates_without_model_visible_receipt(context_format):
    value = automatic_preparation("Fix totals.", context_format)
    prepared, report = codex_preload._validated_automatic_preparation(
        value, "Fix totals.", context_format, max_context_bytes=12000, max_added_tokens=4000,
    )
    assert prepared == value["prompt"]
    assert report["files"] == value["files"]
    assert report["automatic_selection"] == value["automatic_selection"]
    assert "automatic_selection" not in prepared
    assert "calculate_total" not in json.dumps(report)


@pytest.mark.parametrize("field, replacement", [
    ("version", True), ("policy_version", "unknown"), ("decision", []),
    ("decision", "SKIP"), ("decision", "FULL_SOURCE"),
    ("reason", ""), ("reason", "different_reason"),
    ("selected_paths", ["outside.py"]), ("selected_paths", ["../outside.py"]),
    ("selected_paths", ["totals.py", "totals.py"]),
    ("source_versions", {"totals.py": "0" * 64}),
    ("estimated_added_tokens", -1), ("estimated_added_tokens", True),
    ("token_estimate_method", "actual billed tokens"),
    ("auxiliary_model_calls", 1), ("auxiliary_model_calls", False),
    ("discovery_wall_seconds", float("nan")),
    ("discovery_cpu_seconds", float("inf")),
    ("index_refresh_wall_seconds", -1), ("retrieval_wall_seconds", True),
    ("source_preparation_wall_seconds", "fast"),
    ("provided_source_paths", ["/outside.py"]),
    ("provided_source_paths", ["totals.py"]),
    ("static_dependency_coverage", "globally complete"),
    ("candidate_files_considered", True), ("candidate_files_considered", 0),
    ("omitted_candidate_files", -1), ("omitted_candidate_files", 1),
    ("dependency_paths_considered", 20001), ("index_refreshed", 1),
    ("index_refreshed", False), ("ranked_candidates", []),
    ("unresolved_dependency_count", -1), ("candidate_generation_limit_reached", 1),
])
def test_malformed_automatic_receipt_is_rejected(field, replacement):
    value = automatic_preparation("Task")
    value["automatic_selection"][field] = replacement
    with pytest.raises(ValueError):
        codex_preload._validated_automatic_preparation(
            value, "Task", "compact-prefix", max_context_bytes=12000, max_added_tokens=4000,
        )


@pytest.mark.parametrize("mutation", ["missing", "unknown", "ranking", "ranking_duplicate"])
def test_unbounded_or_unrecognized_receipt_fields_are_rejected(mutation):
    value = automatic_preparation("Task")
    receipt = value["automatic_selection"]
    if mutation == "missing":
        del receipt["index_refreshed"]
    elif mutation == "unknown":
        receipt["source_content"] = "must not leak through a private receipt"
    elif mutation == "ranking":
        receipt["ranked_candidates"][0]["evidence_terms"] = ["x" * 129]
    else:
        receipt["ranked_candidates"] *= 2
    with pytest.raises(ValueError):
        codex_preload._validated_automatic_preparation(
            value, "Task", "compact-prefix", max_context_bytes=12000, max_added_tokens=4000,
        )


@pytest.mark.parametrize("budget", ["bytes", "tokens"])
def test_discovery_cannot_forward_over_budget_preparation(budget):
    value = automatic_preparation("Task")
    with pytest.raises(ValueError, match="budget"):
        codex_preload._validated_automatic_preparation(
            value, "Task", "compact-prefix",
            max_context_bytes=1 if budget == "bytes" else 12000,
            max_added_tokens=1 if budget == "tokens" else 4000,
        )


def test_legacy_auto_source_content_must_match_its_complete_file_hash():
    value = automatic_preparation("Task", "legacy")
    value["prompt"] = value["prompt"].replace("return sum(values)", "return max(values)")
    value["prepared_prompt_sha256"] = hashlib.sha256(value["prompt"].encode()).hexdigest()
    with pytest.raises(ValueError, match="complete-file metadata"):
        codex_preload._validated_automatic_preparation(
            value, "Task", "legacy", max_context_bytes=12000, max_added_tokens=4000,
        )


def test_legacy_auto_source_cannot_hide_duplicate_json_content_keys():
    value = automatic_preparation("Task", "legacy")
    value["prompt"] = value["prompt"].replace('"content":', '"content":"hidden source", "content":')
    value["prepared_prompt_sha256"] = hashlib.sha256(value["prompt"].encode()).hexdigest()
    value["context_bytes"] = len(value["prompt"].encode()) - len(b"Task")
    value["automatic_selection"]["estimated_added_tokens"] = math.ceil(value["context_bytes"] / 3)
    with pytest.raises(ValueError, match="noncanonical source envelope"):
        codex_preload._validated_automatic_preparation(
            value, "Task", "legacy", max_context_bytes=12000, max_added_tokens=4000,
        )


@pytest.mark.parametrize("argument", ["--focus", "--support"])
def test_automatic_and_known_path_modes_cannot_be_mixed(automatic_native, argument):
    result = automatic_launch(automatic_native, ["--discover", argument, "totals.py", "Task"])
    assert result.returncode == 1 and "cannot be combined" in result.stderr
    assert not automatic_native["report"].exists()
    assert not automatic_native["capture"].exists()


@pytest.mark.parametrize("bypass", ["off", "supplied", "no_project", "missing_database"])
def test_automatic_bypass_preserves_native_options_environment_and_exact_task(
    automatic_native, tmp_path, bypass,
):
    prompt = "Fix totals; retain $HOME and `literal` task text. λ"
    missing = tmp_path / "uncreated" / "state.db"
    arguments = ["--discover", "--db", str(missing)]
    if bypass == "off":
        arguments += ["--mode", "off", "--project", "approved"]
    elif bypass == "supplied":
        arguments += ["--context-supplied", "--project", "approved"]
    elif bypass == "missing_database":
        arguments += ["--project", "approved"]
    native_options = ["--json", "--model", "synthetic-model", "-c", 'mcp_servers.keep.command="kept"']
    result = automatic_launch(automatic_native, [*arguments, prompt, "--", *native_options])
    assert result.returncode == 19, result.stderr
    records = automatic_native["capture"].read_text().splitlines()
    assert len(records) == 1
    observed = json.loads(records[0])
    assert observed["stdin"] == prompt
    assert observed["argv"] == [str(automatic_native["executable"]), "exec", *native_options, "--", "-"]
    assert observed["environment"] == {
        key: automatic_native["environment"][key]
        for key in ("CODEX_HOME", "HTTP_PROXY", "SSL_CERT_FILE", "MEMGLIDE_AUTO_TEST_AUTH")
    }
    report = observed["report"]
    assert report["version"] == 4
    assert report["preparation"]["automatic_selection"]["decision"] == "SKIP"
    assert report["preparation"]["automatic_selection"]["auxiliary_model_calls"] == 0
    assert report["preparation"]["files"] == []
    assert not missing.parent.exists()
    assert "synthetic-private-auth" not in automatic_native["report"].read_text()
    assert automatic_native["report"].stat().st_mode & 0o777 == 0o600


def test_malformed_automatic_receipt_stops_before_exec_or_success_report(
    automatic_native, monkeypatch, capsys,
):
    import memglide.integrations.auto_preload as automatic

    value = automatic_preparation("Task")
    value["automatic_selection"]["source_versions"]["totals.py"] = "0" * 64
    monkeypatch.setattr(automatic, "prepare_task_prompt", lambda *args, **kwargs: copy.deepcopy(value))
    monkeypatch.setattr(codex_preload, "_find_codex", lambda *args: str(automatic_native["executable"]))
    executions = []
    monkeypatch.setattr(codex_preload.os, "execve", lambda *args: executions.append(args))
    status = codex_preload.main([
        "--discover", "--preparation-report", str(automatic_native["report"]), "Task",
    ])
    assert status == 1 and "inconsistent source evidence" in capsys.readouterr().err
    assert not executions and not automatic_native["report"].exists()


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_natural_language_discovery_delivers_complete_current_source_once(
    automatic_native, tmp_path, context_format,
):
    from memglide.core.indexer import Indexer
    from memglide.storage.database import Database

    repository = automatic_native["repository"]
    subprocess.run(["git", "init", "-q", str(repository)], check=True, capture_output=True)
    source = "def calculate_invoice_subtotal(values):\n    return sum(values)\n"
    (repository / "billing.py").write_text(source)
    (repository / "headers.py").write_text("def parse_header(text):\n    return text.split(':')\n")
    database = tmp_path / "approved-state.db"
    db = Database(database)
    project = Indexer(db).add_project(str(repository))
    prompt = "Correct invoice subtotal rounding and add regression coverage."
    result = automatic_launch(automatic_native, [
        "--discover", "--context-format", context_format, "--project", project["id"],
        "--db", str(database), prompt, "--", "--json", "--model", "synthetic-model",
    ])
    assert result.returncode == 19, result.stderr
    records = automatic_native["capture"].read_text().splitlines()
    assert len(records) == 1
    observed = json.loads(records[0])
    report = observed["report"]
    receipt = report["preparation"]["automatic_selection"]
    assert report["version"] == 4
    assert receipt["decision"] == "FOCUSED_SOURCE"
    assert receipt["selected_paths"] == ["billing.py"]
    assert receipt["source_versions"] == {"billing.py": hashlib.sha256(source.encode()).hexdigest()}
    assert receipt["auxiliary_model_calls"] == 0
    assert "billing.py" not in prompt and "headers.py" not in observed["stdin"]
    if context_format == "compact-prefix":
        envelope = json.loads(observed["stdin"].removesuffix(TASK_SEPARATOR + prompt))
    else:
        from memglide.integrations.preload import _EXPLANATION

        envelope = json.loads(observed["stdin"].removeprefix(prompt + "\n\n" + _EXPLANATION))
    assert [(item["path"], item["content"]) for item in envelope["memglide_sources"]] == [
        ("billing.py", source),
    ]
    assert report["native_stdin"]["sha256"] == hashlib.sha256(observed["stdin"].encode()).hexdigest()
    assert source not in automatic_native["report"].read_text()
    assert db.one("SELECT count(*) AS n FROM sessions")["n"] == 0
    assert db.one("SELECT count(*) AS n FROM memories")["n"] == 0


@pytest.mark.parametrize("tokens", ["0", "85335"])
def test_invalid_automatic_token_cap_prevents_exec(automatic_native, tokens):
    result = automatic_launch(automatic_native, ["--discover", "--max-added-tokens", tokens, "Task"])
    assert result.returncode == 1 and "max_added_tokens" in result.stderr
    assert not automatic_native["report"].exists() and not automatic_native["capture"].exists()


def test_discovery_off_avoids_sdk_memory_parser_state_and_network(tmp_path):
    program = """
import builtins,json,sys
original=builtins.__import__
blocked=('memglide.storage','memglide.security','memglide.service','memglide.core',
         'memglide.memory','mcp','tree_sitter','watchdog','pathspec')
def guarded(name,*args,**kwargs):
    if any(name == prefix or name.startswith(prefix+'.') for prefix in blocked):
        raise AssertionError('unexpected heavy import '+name)
    return original(name,*args,**kwargs)
builtins.__import__=guarded
from memglide.integrations import codex_preload
captured=[]
codex_preload._find_codex=lambda *args: '/installed/codex'
codex_preload.os.dup2=lambda *args,**kwargs: None
codex_preload.os.execve=lambda *args: captured.append(args)
assert codex_preload.main(['--discover','--mode','off','--project','approved',
                          '--db',sys.argv[1],'Task']) == 0
assert len(captured)==1
assert not any(name.startswith(blocked) for name in sys.modules)
print(json.dumps({'execs':len(captured),'heavy_imports':0}))
"""
    database = tmp_path / "uncreated" / "state.db"
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(database)], capture_output=True,
        text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"execs": 1, "heavy_imports": 0}
    assert not database.parent.exists()
