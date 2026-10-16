"""Protocol and isolation checks; synthetic CLI events are never benchmark data."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path

import pytest

# The benchmark is repository tooling, intentionally outside the installed wheel.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run  # noqa: E402
from benchmarks.corpus import task_definitions  # noqa: E402


def test_counterbalanced_plan_is_repeatable_and_retains_every_pair():
    tasks = task_definitions()
    plan = run.make_plan(tasks, 2, 42)
    assert plan == run.make_plan(tasks, 2, 42)
    assert len(plan) == 96
    assert len({row["run_id"] for row in plan}) == 96
    for task in tasks:
        rows = [row for row in plan if row["task_id"] == task["id"]]
        assert [row["configuration"] for row in rows[:2]] == list(
            reversed([row["configuration"] for row in rows[2:]])
        )
        assert {row["configuration"] for row in rows} == {"A", "B"}


def test_command_uses_supported_json_schema_and_same_model_settings(tmp_path):
    common = (
        "codex",
        tmp_path,
        tmp_path / "schema.json",
        tmp_path / "final.json",
        "gpt-6.1-sol",
        "low",
    )
    a = run.codex_command(*common)
    b = run.codex_command(*common, database=tmp_path / "b.db")
    assert a[:-2] == b[:-2]
    assert a[-2:] == ["mcp_servers={}", "-"]
    assert "memglide" in b[-2] and '"--db"' in b[-2]
    assert "--json" in a and "--output-schema" in a
    assert "--ignore-user-config" in a and "--ephemeral" in a
    assert a[a.index("--disable") + 1] == "apps"
    assert run.task_prompt(task_definitions()[0]) == run.task_prompt(task_definitions()[0])


def test_auth_binding_is_referenced_without_copy_and_state_is_isolated(tmp_path):
    provided = tmp_path / "provided"
    provided.mkdir()
    (provided / "auth.json").write_text("synthetic-test-binding")
    first = run.isolated_codex_state(tmp_path / "one", {"CODEX_HOME": str(provided)})
    second = run.isolated_codex_state(tmp_path / "two", {"CODEX_HOME": str(provided)})
    assert first != second
    assert (first / "auth.json").is_symlink()
    assert (first / "auth.json").resolve() == provided / "auth.json"
    assert first.stat().st_mode & 0o777 == 0o700
    assert not (first / "config.toml").exists()


def test_execute_preserves_raw_stream_and_observed_usage_without_summary_claims(tmp_path):
    code = """
import json, sys
sys.stdin.read()
print(json.dumps({'type':'thread.started','thread_id':'test-only'}))
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':20,'cached_input_tokens':4,'output_tokens':3}}))
sys.stderr.write('synthetic diagnostic')
"""
    result = run.execute_codex(
        [sys.executable, "-c", code],
        "synthetic prompt",
        tmp_path,
        tmp_path / "artifacts",
        5,
        {},
    )
    assert result["exit_code"] == 0 and not result["timed_out"]
    assert result["telemetry"]["usage"]["input_tokens"] == 20
    assert result["telemetry"]["actual_cost_usd"] is None
    assert result["telemetry"]["model_calls"] is None
    assert (tmp_path / "artifacts" / "stderr.log").read_text() == "synthetic diagnostic"


def test_timeout_retains_failure_and_missing_usage(tmp_path):
    result = run.execute_codex(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        "",
        tmp_path,
        tmp_path / "timeout",
        0.03,
        {},
    )
    assert result["timed_out"] and result["exit_code"] != 0
    assert result["telemetry"]["usage"]["input_tokens"] is None
    assert result["wall_time_seconds"] < 5


def test_git_worktrees_start_at_identical_commits_and_test_tampering_is_rejected(tmp_path):
    task = task_definitions()[0]
    repository = run.create_repositories(tmp_path, [task])["python"]
    a, b = tmp_path / "a", tmp_path / "b"
    run.create_worktree(repository, a)
    run.create_worktree(repository, b)
    assert run.git(a, "rev-parse", "HEAD") == run.git(b, "rev-parse", "HEAD")
    assert (a / task["target_files"][0]).read_bytes() == (b / task["target_files"][0]).read_bytes()
    snapshot = run.protection_snapshot(a)
    (a / task["target_files"][0]).write_text("# legitimate source change\n")
    assert run.check_protection(a, snapshot, repository["commit"]) == []
    protected = next(path for path in snapshot if path.startswith("tests/"))
    (a / protected).write_text("# tampered\n")
    assert protected in run.check_protection(a, snapshot, repository["commit"])


def _fake_execution(command, prompt, worktree, artifacts, timeout, environment):
    target = worktree / "atlas" / "cache.py"
    target.write_text(target.read_text().replace("if now > expires:", "if now >= expires:"))
    (artifacts / "events.jsonl").write_text("", encoding="utf-8")
    (artifacts / "stderr.log").write_text("", encoding="utf-8")
    return {
        "exit_code": 0,
        "timed_out": False,
        "wall_time_seconds": 1.0,
        "overhead": {},
        "telemetry": {
            "completed_turns": 1,
            "mcp_call_count": 0,
            "memglide_mcp_call_count": 0,
            "errors": [],
            "stream_terminal": True,
            "mcp_counts_complete": True,
        },
    }


@pytest.mark.parametrize("arm,expected_status", [("A", "completed"), ("B", "invalid_treatment")])
def test_independent_grader_and_missing_mcp_calls_govern_outcome(
    tmp_path, monkeypatch, arm, expected_status
):
    task = task_definitions()[0]
    repository = run.create_repositories(tmp_path, [task])["python"]
    monkeypatch.setattr(run, "execute_codex", _fake_execution)
    row = {
        "run_id": f"fake-{arm}",
        "task_id": task["id"],
        "configuration": arm,
        "repeat": 1,
        "order": 1,
        "language": "python",
    }
    args = argparse.Namespace(codex="fake", model="same", effort="low", timeout=5)
    result = run.run_task(row, task, repository, tmp_path, tmp_path / "schema", args, {})
    assert result["status"] == expected_status, result
    assert result["grader"]["success"] is True
    assert result["actual_cost_usd"] is None
    assert (Path(result["artifacts"]) / "changes.patch").is_file()
    if arm == "B":
        assert result["treatment_valid"] is False
        assert result["setup"]["index_wall_seconds"] > 0
        from memglide.service import Service

        service = Service(Path(result["artifacts"]) / "memglide.db")
        try:
            assert service.db.rows("SELECT * FROM sessions") == []
            assert service.db.rows("SELECT * FROM retrievals") == []
        finally:
            service.close()


def test_new_source_and_regression_tests_are_preserved_without_following_links(tmp_path):
    task = task_definitions()[0]
    repository = run.create_repositories(tmp_path, [task])["python"]
    worktree, artifacts = tmp_path / "worktree", tmp_path / "artifacts"
    run.create_worktree(repository, worktree)
    snapshot = run.protection_snapshot(worktree)
    (worktree / "atlas" / "new_source.py").write_text("result = 42\n")
    staged = worktree / "atlas" / "cache.py"
    staged.write_text(staged.read_text() + "# staged source evidence\n")
    run.git(worktree, "add", "atlas/cache.py")
    (worktree / "tests" / "test_new.py").write_text("# new regression test\n")
    (worktree / "atlas" / "external-link.py").symlink_to("/does/not/exist")
    assert run.check_protection(worktree, snapshot, repository["commit"]) == []
    artifacts.mkdir()
    run.preserve_changes(worktree, artifacts)
    assert "staged source evidence" in (artifacts / "changes.patch").read_text()
    with tarfile.open(artifacts / "untracked-files.tar") as archive:
        assert archive.getmember("atlas/external-link.py").issym()
        assert archive.extractfile("atlas/new_source.py").read() == b"result = 42\n"
        assert "tests/test_new.py" in archive.getnames()


def test_common_blocker_does_not_misclassify_ordinary_task_failure(tmp_path):
    (tmp_path / "stderr.log").write_text("unit test assertion failed")
    result = {"exit_code": 1, "telemetry": {"errors": [], "completed_turns": 0}}
    assert run.common_blocker(result, tmp_path) is None
    (tmp_path / "stderr.log").write_text("Proxy CONNECT failed: 403 Forbidden")
    assert run.common_blocker(result, tmp_path) == "network_policy"


def test_failed_preflight_retains_all_planned_rows_without_repeated_requests(tmp_path, monkeypatch):
    calls = []

    def preflight(command, prompt, worktree, artifacts, timeout, environment):
        calls.append(command)
        artifacts.mkdir(parents=True)
        (artifacts / "stderr.log").write_text("Proxy CONNECT failed: 403 Forbidden")
        return {
            "exit_code": 1,
            "wall_time_seconds": 0.1,
            "telemetry": {
                "completed_turns": 0,
                "errors": [],
                "usage": {"input_tokens": None, "cached_input_tokens": None, "output_tokens": None},
            },
        }

    monkeypatch.setattr(run, "execute_codex", preflight)
    original = run.subprocess.check_output

    def check_output(command, *args, **kwargs):
        return (
            "fake-cli-test-only\n"
            if command == ["fake", "--version"]
            else original(command, *args, **kwargs)
        )

    monkeypatch.setattr(run.subprocess, "check_output", check_output)
    output = tmp_path / "result"
    assert run.main(["--codex", "fake", "--output", str(output), "--repeats", "2"]) == 2
    assert len(calls) == 1
    report = json.loads((output / "report.json").read_text())
    assert len(report["runs"]) == 96
    assert all(row["status"] == "not_run" and not row["attempted"] for row in report["runs"])
    assert report["aggregates"]["A"]["metrics"]["input_tokens"]["mean"] is None
    assert report["aggregates"]["B"]["actual_cost_per_successful_task_usd"]["value"] is None
    assert report["metadata"]["preflight_runs"][0]["exit_code"] == 1
