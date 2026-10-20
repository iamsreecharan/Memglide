"""Commands-only cards use real approval/provider/freshness boundaries, no models."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations import (
    auto_preload,
    codex_preload,
    command_provider,
    public_check,
    workflow_policy,
    workflow_preload,
)
from memglide.storage.database import Database

TASK = "Cooling window must account for flow rate and capacity."
BODY = "def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n"


@pytest.fixture
def ambiguous(tmp_path):
    root = tmp_path / "approved-project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for name in ("alpha.py", "bravo.py"):
        (root / name).write_text(BODY)
    (root / "tests").mkdir()
    (root / "tests/test_public.py").write_text("def test_public():\n    assert True\n")
    database = Database(tmp_path / "state.db")
    project = Indexer(database).add_project(str(root))["id"]
    base = auto_preload.prepare_task_prompt(TASK, project_id=project, db_path=database.path,
        enabled=True, selection_policy="v4", context_format="compact-prefix")
    assert base["mode"] == "passthrough" and base["reason"] == "ambiguous_candidates", base
    receipt = tmp_path / "explicit-checks.json"
    provider = command_provider.verify_public_commands(
        [{"name": "public checks π", "kind": "tests",
          "argv": [sys.executable, "-c", "print('2 passed')"]}],
        project_id=project, db_path=database.path, receipt_path=receipt)
    return root, database, project, base, provider, receipt


def augment(fixture, *, config=None, provider=True, **kwargs):
    _, database, project, base, verified, _ = fixture
    return workflow_preload.augment_preparation(base, TASK, project_id=project,
        db_path=database.path, config=config or workflow_policy.commands_first_policy(),
        provider=verified if provider else None, **kwargs)


def validate(fixture, value, *, provider=True, **kwargs):
    _, database, project, base, verified, _ = fixture
    return workflow_preload.validate_workflow_preparation(value, base, TASK,
        project_id=project, db_path=database.path, config=workflow_policy.commands_first_policy(),
        provider=verified if provider else None, **kwargs)


def test_command_only_preserves_decline_and_verified_counts_without_running_checks(ambiguous, monkeypatch):
    monkeypatch.setattr(public_check, "run_check", lambda *a, **k: pytest.fail("preparation executed checks"))
    base = deepcopy(ambiguous[3])
    value = augment(ambiguous)
    assert value["mode"] == "commands_only" and value["files"] == []
    assert value["automatic_selection"] == base["automatic_selection"]
    assert value["workflow"]["source_decline_reason"] == "ambiguous_candidates"
    assert value["workflow"]["production"] == value["workflow"]["public_tests"] == []
    assert value["_workflow_payload"]["production"] == value["_workflow_payload"]["tests"] == []
    assert 'Public baseline: {"exit_code":0,"tests":2}' in value["prompt"]
    assert BODY not in value["prompt"] and value["prompt"].endswith("\n\nTask:\n" + TASK)
    prompt, report = validate(ambiguous, value)
    assert prompt == value["prompt"] and report["mode"] == "commands_only"
    assert report["automatic_selection"]["decision"] == "SKIP"
    assert ambiguous[3] == base


def test_selected_and_default_still_preserve_exact_abstention(ambiguous):
    _, database, project, base, verified, _ = ambiguous
    for config in (None, workflow_policy.selected_policy()):
        assert workflow_preload.augment_preparation(base, TASK, project_id=project,
            db_path=database.path, config=config, provider=verified) is base
    old = {'command_card': 'commands_counts', 'public_tests': 'none', 'regression_stage': 'ordinary',
        'compatibility_review': 'ordinary', 'check_output': 'full', 'verification': 'full_final',
        'diagnostics': 'ordinary', 'layout': 'v4_compact', 'differential': 'none'}
    assert workflow_policy.selected_policy() == old
    assert workflow_policy.signature(old) == hashlib.sha256(json.dumps(old,
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with pytest.raises(ValueError):
        workflow_policy.validate({**old, "source_selection": "anything"})


@pytest.mark.parametrize("failure", ["missing", "public_test", "new_source", "receipt"])
def test_missing_or_stale_evidence_returns_original_task(ambiguous, failure):
    root, _, _, _, verified, _ = ambiguous
    if failure == "public_test":
        (root / "tests/test_public.py").write_text("def test_changed():\n    assert True\n")
    elif failure == "new_source":
        (root / "unselected.py").write_text("unrelated = 1\n")
    elif failure == "receipt":
        verified.receipt["commands"][0]["baseline"]["tests"] = 999
    value = augment(ambiguous, provider=failure != "missing")
    assert value["prompt"] == TASK and value["mode"] == "passthrough"
    assert value["workflow"]["decision"] == "SKIP"
    if failure in {"missing", "public_test", "receipt"}:
        assert validate(ambiguous, value, provider=failure != "missing")[0] == TASK


@pytest.mark.parametrize("mutation", ["test", "new_source", "config", "remove_competitor"])
def test_final_handoff_rechecks_unselected_tree_and_full_decline(ambiguous, mutation):
    root = ambiguous[0]
    value = augment(ambiguous)
    if mutation == "test":
        (root / "tests/test_public.py").write_text("def test_changed():\n    assert True\n")
    elif mutation == "new_source":
        (root / "unselected.py").write_text("unrelated = 1\n")
    elif mutation == "config":
        (root / ".gitignore").write_text("bravo.py\n")
    else:
        (root / "bravo.py").unlink()
    with pytest.raises(ValueError):
        validate(ambiguous, value)


@pytest.mark.parametrize("part", ["prompt", "counts", "files", "mode", "decline", "source_injection"])
def test_final_handoff_rejects_tampering_even_recomputed_hashes(ambiguous, part):
    value = augment(ambiguous)
    if part == "prompt":
        value["prompt"] += "\ninjected instruction"
    elif part == "counts":
        value["workflow"]["commands"][0]["baseline"]["tests"] = 999
    elif part == "files":
        value["files"] = [{"path": "alpha.py", "sha256": hashlib.sha256(BODY.encode()).hexdigest()}]
    elif part == "mode":
        value["mode"] = "preloaded"
    elif part == "decline":
        value["automatic_selection"]["reason"] = "no_production_match"
    else:
        value["_workflow_payload"]["production"] = [{"path": "alpha.py", "content": BODY,
            "sha256": hashlib.sha256(BODY.encode()).hexdigest(), "kind": "production",
            "complete": True, "start_line": 1, "end_line": 2}]
        value["prompt"] = workflow_preload._render(**value["_workflow_payload"])
    sha = hashlib.sha256(value["prompt"].encode()).hexdigest()
    value["prepared_prompt_sha256"] = value["workflow"]["prepared_prompt_sha256"] = sha
    with pytest.raises(ValueError):
        validate(ambiguous, value)


def test_whole_context_caps_keep_task_exact_without_truncation(ambiguous):
    value = augment(ambiguous)
    added = value["context_bytes"]
    assert added == len(value["prompt"].encode()) - len(TASK.encode())
    assert added > len(value["prompt"]) - len(TASK)
    assert validate(ambiguous, value, max_context_bytes=added)[0] == value["prompt"]
    for caps in ({"max_context_bytes": added - 1}, {"max_added_tokens": (added - 1) // 3}):
        declined = augment(ambiguous, **caps)
        assert declined["prompt"] == TASK
        assert declined["workflow"]["reason"] == "workflow_context_budget"
        assert validate(ambiguous, declined, **caps)[0] == TASK


def test_preloaded_commands_first_keeps_all_complete_source(ambiguous):
    root, database, project, _, _, _ = ambiguous
    (root / "bravo.py").unlink()
    base = auto_preload.prepare_task_prompt(TASK, project_id=project, db_path=database.path,
        enabled=True, selection_policy="v4", context_format="compact-prefix")
    assert base["mode"] == "preloaded"
    verified = command_provider.verify_public_commands(
        [{"name": "public checks", "argv": [sys.executable, "-c", "print('2 passed')"]}],
        project_id=project, db_path=database.path, receipt_path=root.parent / "refreshed.json")
    fixture = root, database, project, base, verified, root.parent / "refreshed.json"
    value = augment(fixture)
    assert value["mode"] == "preloaded" and value["files"] == base["files"]
    assert value["_workflow_payload"]["production"][0]["content"] == BODY
    assert "source_decline_reason" not in value["workflow"]
    assert validate(fixture, value)[0] == value["prompt"]
    selected = augment(fixture, config=workflow_policy.selected_policy())
    assert "without repeating checks before editing" not in selected["prompt"]
    assert selected["_workflow_payload"]["production"] == value["_workflow_payload"]["production"]


@pytest.mark.parametrize("when", ["before_prepare", "before_handoff"])
@pytest.mark.parametrize("change", ["delete", "modify"])
def test_changed_verified_tool_never_reexecutes_or_delivers_stale_card(ambiguous, tmp_path, monkeypatch, when, change):
    root, database, project, base, _, _ = ambiguous
    executable = tmp_path / "explicit-check"
    executable.write_text("#!" + sys.executable + "\nprint('2 passed')\n")
    executable.chmod(0o700)
    receipt = tmp_path / "tool-verification.json"
    verified = command_provider.verify_public_commands(
        [{"name": "public checks", "argv": [str(executable)]}],
        project_id=project, db_path=database.path, receipt_path=receipt)
    fixture = root, database, project, base, verified, receipt
    value = augment(fixture) if when == "before_handoff" else None
    if change == "delete":
        executable.unlink()
    else:
        executable.write_text("#!" + sys.executable + "\nprint('999 passed')\n")
    monkeypatch.setattr(public_check, "run_check", lambda *a, **k: pytest.fail("reran checks"))
    if value is None:
        declined = augment(fixture)
        assert declined["prompt"] == TASK and declined["workflow"]["decision"] == "SKIP"
        assert validate(fixture, declined)[0] == TASK
    else:
        with pytest.raises(ValueError):
            validate(fixture, value)


def test_provider_cannot_be_reused_for_another_approved_project(ambiguous, tmp_path):
    _, database, _, _, verified, _ = ambiguous
    root = tmp_path / "second-project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for name in ("alpha.py", "bravo.py"):
        (root / name).write_text(BODY)
    project = Indexer(database).add_project(str(root))["id"]
    base = auto_preload.prepare_task_prompt(TASK, project_id=project, db_path=database.path,
        enabled=True, selection_policy="v4", context_format="compact-prefix")
    fixture = root, database, project, base, verified, ambiguous[-1]
    value = augment(fixture)
    assert value["prompt"] == TASK
    assert value["workflow"]["reason"] == "verified_public_command_provider_stale_or_unavailable"


def test_final_freshness_runs_after_materialization(ambiguous, monkeypatch):
    value = augment(ambiguous)
    materialize = workflow_preload._materialize

    def change_after_render(*args, **kwargs):
        result = materialize(*args, **kwargs)
        (ambiguous[0] / "tests/test_public.py").write_text("def test_new():\n    assert True\n")
        return result

    monkeypatch.setattr(workflow_preload, "_materialize", change_after_render)
    with pytest.raises(ValueError, match="stale"):
        validate(ambiguous, value)


def test_fallback_still_revalidates_source_decline(ambiguous):
    value = augment(ambiguous, provider=False)
    (ambiguous[0] / "bravo.py").unlink()
    with pytest.raises(ValueError, match="Full v4 source-selection"):
        validate(ambiguous, value, provider=False)


@pytest.mark.parametrize("gate,task", [({"mode": "off"}, TASK), ({"context_supplied": True}, TASK),
    ({}, "x" * 4001), ({}, "the and for")])
def test_explicit_and_query_gates_never_open_state(tmp_path, monkeypatch, gate, task):
    absent = tmp_path / "never-created.db"
    base = auto_preload.prepare_task_prompt(task, project_id="absent", db_path=absent,
        enabled=True, selection_policy="v4", context_format="compact-prefix", **gate)
    monkeypatch.setattr(workflow_preload, "_selection", lambda *a, **k: pytest.fail("opened DB"))
    monkeypatch.setattr(auto_preload, "prepare_task_prompt", lambda *a, **k: pytest.fail("reopened discovery"))
    config = workflow_policy.commands_first_policy()
    assert workflow_preload.augment_preparation(base, task, project_id="absent", db_path=absent,
        config=config) is base
    assert workflow_preload.validate_workflow_preparation(base, base, task, project_id="absent",
        db_path=absent, config=config)[0] == task
    assert not absent.exists()


def test_cli_delivers_command_only_stdin_and_report(ambiguous, monkeypatch, tmp_path):
    _, database, project, _, verified, receipt = ambiguous
    stdin, calls = [], []
    monkeypatch.setattr(codex_preload, "_find_codex", lambda *a: "/installed/codex")
    monkeypatch.setattr(public_check, "run_check", lambda *a, **k: pytest.fail("preparation executed checks"))

    class InterceptedOS:
        def __getattr__(self, name):
            return getattr(os, name)

        def dup2(self, descriptor, target, *, inheritable=True):
            assert target == 0 and inheritable
            with os.fdopen(os.dup(descriptor), "rb") as stream:
                stdin.append(stream.read())

        def execve(self, executable, argv, environment):
            calls.append((executable, argv, environment))

    monkeypatch.setattr(codex_preload, "os", InterceptedOS())
    report_path = tmp_path / "handoff.json"
    assert codex_preload.main(["--discover", "--selection-policy", "v4", "--workflow-policy",
        "commands-first", "--project", project, "--db", str(database.path),
        "--public-check-receipt", str(receipt), "--public-check-sha256", verified.trusted_sha256,
        "--preparation-report", str(report_path), TASK, "--", "--model", "example"]) == 0
    report = json.loads(report_path.read_text())
    assert len(stdin) == len(calls) == 1
    assert calls[0][:2] == ("/installed/codex", ["/installed/codex", "exec", "--model", "example", "--", "-"])
    assert calls[0][2] == dict(os.environ)
    assert report["version"] == 5 and report["preparation"]["mode"] == "commands_only"
    actual_hash = hashlib.sha256(stdin[0]).hexdigest()
    assert actual_hash == report["native_stdin"]["sha256"] == report["preparation"]["prepared_prompt_sha256"]
    assert report["preparation"]["workflow"]["prepared_prompt_sha256"] == actual_hash
    assert report["native_stdin"]["bytes"] == len(stdin[0])


@pytest.mark.parametrize("gate,task", [(["--mode", "off"], TASK + "\r\n"),
    (["--context-supplied"], TASK), ([], "x" * 4001), ([], "the and for")])
def test_cli_early_gates_do_not_load_policy_provider_or_database(tmp_path, monkeypatch, gate, task):
    native = tmp_path / "installed-codex"
    native.write_text("#!/bin/sh\nexit 0\n")
    native.chmod(0o700)
    calls = []

    def forbidden(*args, **kwargs):
        pytest.fail("early gate opened optional workflow state")

    monkeypatch.setattr(command_provider, "load_verified_provider", forbidden)
    monkeypatch.setattr(workflow_policy, "commands_first_policy", forbidden)
    monkeypatch.setattr(workflow_preload, "commands_only_eligible", forbidden)
    monkeypatch.setattr(workflow_preload, "augment_preparation", forbidden)
    monkeypatch.setattr(codex_preload, "_find_codex", lambda *a: str(native))

    class InterceptedOS:
        def __getattr__(self, name):
            return getattr(os, name)

        def dup2(self, descriptor, target, *, inheritable=True):
            with os.fdopen(os.dup(descriptor), "rb") as stream:
                calls.append(stream.read())

        def execve(self, *args):
            return None

    monkeypatch.setattr(codex_preload, "os", InterceptedOS())
    absent_db = tmp_path / "never-created.db"
    absent_receipt = tmp_path / "never-opened.json"
    assert codex_preload.main(["--discover", "--selection-policy", "v4", "--workflow-policy",
        "commands-first", "--project", "not-opened", "--db", str(absent_db),
        "--public-check-receipt", str(absent_receipt), "--public-check-sha256", "0" * 64,
        *gate, task]) == 0
    assert calls == [task.encode()] and not absent_db.exists() and not absent_receipt.exists()


def test_actual_cli_process_hands_exact_bytes_to_executable(ambiguous, tmp_path):
    root, database, project, _, verified, receipt = ambiguous
    capture = tmp_path / "captured-native.json"
    native = tmp_path / "installed-codex"
    native.write_text("#!" + sys.executable + "\nimport json, sys\nfrom pathlib import Path\n"
        + "Path(" + repr(str(capture)) + ").write_text(json.dumps({'argv':sys.argv[1:],"
        + "'stdin':sys.stdin.buffer.read().decode('utf-8')}))\n")
    native.chmod(0o700)
    report_path = tmp_path / "actual-report.json"
    result = subprocess.run([sys.executable, "-m", "memglide.integrations.codex_preload",
        "--codex-executable", str(native), "--discover", "--selection-policy", "v4",
        "--workflow-policy", "commands-first", "--project", project, "--db", str(database.path),
        "--public-check-receipt", str(receipt), "--public-check-sha256", verified.trusted_sha256,
        "--preparation-report", str(report_path), "-", "--", "--model", "example"],
        input=TASK.encode(), capture_output=True, cwd=root, check=True)
    assert result.stdout == b"" and result.stderr == b""
    actual = json.loads(capture.read_text())
    report = json.loads(report_path.read_text())
    assert actual["argv"] == ["exec", "--model", "example", "--", "-"]
    assert report["preparation"]["mode"] == "commands_only"
    assert actual["stdin"].endswith("\n\nTask:\n" + TASK)
    assert 'Public baseline: {"exit_code":0,"tests":2}' in actual["stdin"]
    assert hashlib.sha256(actual["stdin"].encode()).hexdigest() == report["native_stdin"]["sha256"]
    assert report["native_stdin"]["bytes"] == len(actual["stdin"].encode())
