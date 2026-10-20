"""Installed selected-workflow boundary controls; native exec is intercepted.

Staged for post-closure installation. These tests import the actual installed
launcher and never compile or apply a draft patch.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations import codex_preload as launcher
from memglide.integrations import command_provider, public_check, workflow_policy, workflow_preload
from memglide.storage.database import Database


def intercept_native(monkeypatch):
    calls = []
    stdin = []
    monkeypatch.setattr(launcher, "_find_codex", lambda *args: "/installed/codex")

    class InterceptedOS:
        def __getattr__(self, name):
            return getattr(os, name)

        def dup2(self, descriptor, target, *, inheritable=True):
            assert target == 0 and inheritable is True
            with os.fdopen(os.dup(descriptor), "rb") as stream:
                stdin.append(stream.read())
            return target

        def execve(self, executable, argv, environment):
            calls.append((executable, argv))

    # Keep pytest/subprocess OS operations intact; intercept this module only.
    monkeypatch.setattr(launcher, "os", InterceptedOS())
    return calls, stdin


@pytest.fixture
def verified_project(tmp_path):
    root = tmp_path / "actual-project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "cooling.py").write_text(
        "def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n"
    )
    database = Database(tmp_path / "private-state.db")
    project = Indexer(database).add_project(str(root))["id"]
    receipt = tmp_path / "explicitly-verified.json"
    provider = command_provider.verify_public_commands(
        [{"name": "public tests", "kind": "tests",
          "argv": [sys.executable, "-c", "print('2 passed')"]}],
        project_id=project, db_path=database.path, receipt_path=receipt,
    )
    return root, database, project, receipt, provider


def selected_options(verified_project):
    _, database, project, receipt, provider = verified_project
    return [
        "--discover", "--selection-policy", "v4", "--workflow-policy", "selected",
        "--project", project, "--db", str(database.path),
        "--public-check-receipt", str(receipt),
        "--public-check-sha256", provider.trusted_sha256,
    ]


def test_default_path_preserves_actual_stdin_native_argv_and_report(monkeypatch, tmp_path):
    calls, stdin = intercept_native(monkeypatch)
    monkeypatch.setattr(
        workflow_policy, "selected_policy",
        lambda: pytest.fail("default path consulted optional policy"),
    )
    task = "Exact original task.\r\n"
    report_path = tmp_path / "report.json"
    assert launcher.main([
        "--mode", "off", "--preparation-report", str(report_path), task,
        "--", "--model", "example",
    ]) == 0
    assert stdin == [task.encode()]
    assert calls == [
        ("/installed/codex", ["/installed/codex", "exec", "--model", "example", "--", "-"])
    ]
    report = json.loads(report_path.read_text())
    assert report["version"] == 2
    assert "workflow" not in report["preparation"]
    assert report["native_stdin"]["sha256"] == hashlib.sha256(stdin[0]).hexdigest()


@pytest.mark.parametrize("options", [
    ["--workflow-policy", "selected"],
    ["--public-check-receipt", "/external/check.json"],
    ["--public-check-sha256", "0" * 64],
    ["--public-check-receipt", "/external/check.json", "--public-check-sha256", "0" * 64],
    ["--discover", "--selection-policy", "v3", "--workflow-policy", "selected",
     "--project", "p", "--db", "/external/state.db"],
    ["--discover", "--selection-policy", "v4", "--workflow-policy", "selected",
     "--context-format", "legacy", "--project", "p", "--db", "/external/state.db"],
])
def test_unsupported_or_partial_optin_fails_before_native(monkeypatch, options):
    calls, stdin = intercept_native(monkeypatch)
    assert launcher.main([*options, "task"]) == 1
    assert calls == [] and stdin == []


def test_verified_optin_reaches_actual_native_stdin_without_running_checks(
    verified_project, monkeypatch, tmp_path,
):
    root, _, _, _, _ = verified_project
    monkeypatch.chdir(root)
    monkeypatch.setattr(
        public_check, "run_check", lambda *args, **kwargs: pytest.fail("preparation ran a check")
    )
    calls, stdin = intercept_native(monkeypatch)
    task = "Cooling window must account for flow rate and capacity."
    report_path = tmp_path / "prepared.json"
    assert launcher.main([
        *selected_options(verified_project), "--preparation-report", str(report_path), task,
        "--", "--model", "example",
    ]) == 0
    report = json.loads(report_path.read_text())
    assert report["version"] == 5
    workflow = report["preparation"]["workflow"]
    assert workflow["decision"] == "PREPARED"
    assert workflow["config"] == workflow_policy.selected_policy()
    assert workflow["public_tests"] == []
    assert stdin[0].decode().endswith("\n\nTask:\n" + task)
    assert 'Public baseline: {"exit_code":0,"tests":2}' in stdin[0].decode()
    actual_sha = hashlib.sha256(stdin[0]).hexdigest()
    assert report["native_stdin"]["sha256"] == actual_sha
    assert report["preparation"]["prepared_prompt_sha256"] == actual_sha
    assert workflow["prepared_prompt_sha256"] == actual_sha
    assert calls == [
        ("/installed/codex", ["/installed/codex", "exec", "--model", "example", "--", "-"])
    ]


def test_invalid_receipt_pin_stops_before_native(verified_project, monkeypatch):
    monkeypatch.chdir(verified_project[0])
    calls, stdin = intercept_native(monkeypatch)
    options = selected_options(verified_project)
    options[options.index("--public-check-sha256") + 1] = "0" * 64
    assert launcher.main([
        *options, "Cooling window must account for flow rate and capacity."
    ]) == 1
    assert calls == [] and stdin == []


def test_stale_test_binding_keeps_v4_source_without_command_facts(
    verified_project, monkeypatch, tmp_path,
):
    root, _, _, _, _ = verified_project
    (root / "test_new.py").write_text("def test_new():\n    assert True\n")
    monkeypatch.chdir(root)
    monkeypatch.setattr(
        public_check, "run_check", lambda *args, **kwargs: pytest.fail("preparation ran a check")
    )
    calls, stdin = intercept_native(monkeypatch)
    report_path = tmp_path / "stale.json"
    assert launcher.main([
        *selected_options(verified_project), "--preparation-report", str(report_path),
        "Cooling window must account for flow rate and capacity.",
    ]) == 0
    report = json.loads(report_path.read_text())
    assert report["preparation"]["mode"] == "preloaded"
    assert report["preparation"]["workflow"]["decision"] == "SKIP"
    assert report["preparation"]["workflow"]["reason"] == (
        "verified_public_command_provider_stale_or_unavailable"
    )
    assert "Verified public checks" not in stdin[0].decode()
    assert "memglide_sources" in stdin[0].decode()
    assert len(calls) == 1


@pytest.mark.parametrize("gate", [["--mode", "off"], ["--context-supplied"]])
def test_passthrough_does_not_load_optional_state(monkeypatch, tmp_path, gate):
    calls, stdin = intercept_native(monkeypatch)

    def forbidden(*args, **kwargs):
        pytest.fail("passthrough consulted optional state")

    monkeypatch.setattr(command_provider, "load_verified_provider", forbidden)
    monkeypatch.setattr(workflow_policy, "selected_policy", forbidden)
    monkeypatch.setattr(workflow_preload, "augment_preparation", forbidden)
    absent_db = tmp_path / "must-not-exist.db"
    absent_receipt = tmp_path / "must-not-exist.json"
    report_path = tmp_path / "passthrough.json"
    task = "Exact unchanged task.\r\n"
    assert launcher.main([
        "--discover", "--selection-policy", "v4", "--workflow-policy", "selected",
        "--project", "not-opened", "--db", str(absent_db),
        "--public-check-receipt", str(absent_receipt),
        "--public-check-sha256", "0" * 64,
        "--preparation-report", str(report_path), *gate, task,
    ]) == 0
    assert stdin == [task.encode()]
    assert not absent_db.exists() and not absent_receipt.exists()
    report = json.loads(report_path.read_text())
    assert report["preparation"]["mode"] == "passthrough"
    assert report["native_stdin"]["sha256"] == hashlib.sha256(stdin[0]).hexdigest()
    assert calls == [("/installed/codex", ["/installed/codex", "exec", "--", "-"])]
