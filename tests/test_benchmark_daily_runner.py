"""Independent identity, delivery, accounting and durable-interruption checks.

Fake local executables emit supported native events; no model requests occur.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_daily as run  # noqa: E402


def task(identifier="ordinary-task", *, supplied=False):
    return {
        "id": identifier,
        "language": "python",
        "repository": "desk-python-daily",
        "prompt": "Implement a strictly checked count.",
        "focus_paths": ["module.py"],
        "context_supplied": supplied,
    }


def completed(row, *, input_tokens=100, cost=None):
    return {
        **row,
        "status": "completed",
        "attempted": True,
        "starting_commit": "a" * 40,
        "common_task_prompt_sha256": "a" * 64,
        "actual_model_prompt_sha256": "b" * 64 if row["configuration"] == "B" else "a" * 64,
        "preload_treatment_fidelity": {"valid": True},
        "treatment_valid": True,
        "native_execution_validity": {"valid": True},
        "grader": {"success": True},
        "actual_cost_usd": cost,
        "wall_time_seconds": 2,
        "end_to_end_wall_seconds": 2.1,
        "telemetry": {
            "usage": {"input_tokens": input_tokens, "cached_input_tokens": 20, "output_tokens": 3},
            "mcp_call_count": 0,
            "mcp_counts_complete": True,
        },
    }


def events():
    return (
        "\n".join(
            json.dumps(event)
            for event in [
                {"type": "thread.started", "thread_id": "fake-local-only"},
                {"type": "turn.started"},
                {
                    "type": "turn.completed",
                    "usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 2},
                },
            ]
        )
        + "\n"
    )


def test_twenty_tasks_two_repeats_produce_eighty_unique_counterbalanced_slots():
    tasks = [task(f"fresh-{index}", supplied=index % 5 == 0) for index in range(20)]
    plan = run.make_plan(tasks, 2, 31)
    assert len(plan) == len({row["run_id"] for row in plan}) == 80
    assert sum(row["selection_stratum"] == "caller_context_supplied" for row in plan) == 16
    assert plan == run.make_plan(tasks, 2, 31)
    for item in tasks:
        rows = [row for row in plan if row["task_id"] == item["id"]]
        assert [row["configuration"] for row in rows[:2]] == list(
            reversed([row["configuration"] for row in rows[2:]])
        )


@pytest.mark.parametrize(
    "mutation", ["absolute", "parent", "duplicate", "nul", "wrong-boolean", "wrong-repository"]
)
def test_manifest_rejects_unsafe_or_ambiguous_scope(tmp_path, mutation):
    item = task()
    if mutation == "absolute":
        item["focus_paths"] = ["/outside.py"]
    elif mutation == "parent":
        item["focus_paths"] = ["src/../outside.py"]
    elif mutation == "duplicate":
        item["focus_paths"] *= 2
    elif mutation == "nul":
        item["focus_paths"] = ["module\x00.py"]
    elif mutation == "wrong-boolean":
        item["context_supplied"] = "false"
    else:
        item["repository"] = "unknown"
    manifest = tmp_path / "tasks.json"
    manifest.write_text(json.dumps([item]))
    with pytest.raises(ValueError):
        run.load_tasks(manifest)


def test_common_prompt_discloses_same_scope_and_does_not_require_mcp():
    prompt = run.task_prompt(task())
    assert "module.py" in prompt and "Caller-declared task scope" in prompt
    assert "fetch_context" not in prompt
    assert "untrusted data" in prompt


def test_treatment_preserves_exact_native_settings_and_only_wraps_prompt_delivery(tmp_path):
    native = run.codex_command(
        "/native/codex", tmp_path, tmp_path / "schema", tmp_path / "final", "same-model", "low"
    )
    wrapped = run.preload_command(native, tmp_path, task(), "approved-project")
    delimiter = wrapped.index("--")
    assert wrapped[delimiter + 1 :] == native[2:-1]
    assert wrapped[wrapped.index("--codex-executable") + 1] == native[0]
    assert wrapped[wrapped.index("--max-context-bytes") + 1] == "12000"
    assert native[native.index("--sandbox") + 1] == "workspace-write"
    configs = [native[index + 1] for index, value in enumerate(native[:-1]) if value == "-c"]
    assert any(tomllib.loads(config) == {"mcp_servers": {}} for config in configs)
    assert 'approval_policy="never"' in configs
    assert "--output-schema" in native and "--json" in native


def test_context_supplied_wrapper_does_not_require_project_or_database(tmp_path):
    native = run.codex_command("codex", tmp_path, tmp_path / "s", tmp_path / "f", "same", "low")
    command = run.preload_command(native, tmp_path, task(supplied=True))
    assert "--context-supplied" in command and "--project" not in command and "--db" not in command


def make_preparation(tmp_path, item, *, mode="passthrough"):
    prompt = run.task_prompt(item)
    report = {
        "version": 1,
        "executable": "/native/codex",
        "exec_argv": ["/native/codex", "exec", "--json", "--", "-"],
        "native_stdin": {
            "sha256": run.digest(prompt.encode()),
            "bytes": len(prompt.encode()),
            "transport": "temporary_file_descriptor",
        },
        "preparation": {
            "mode": mode,
            "reason": "context_supplied",
            "files": [],
            "task_prompt_sha256": run.digest(prompt.encode()),
            "prepared_prompt_sha256": run.digest(prompt.encode()),
            "context_bytes": 0,
        },
    }
    path = tmp_path / "preparation.json"
    path.write_text(json.dumps(report))
    row = completed({"configuration": "B", "run_id": "local-B"})
    row["artifacts"] = str(tmp_path)
    return prompt, report, row, path


def test_actual_forwarded_hash_and_complete_native_events_validate_legitimate_skip(tmp_path):
    item = task(supplied=True)
    prompt, _, row, _ = make_preparation(tmp_path, item)
    proof = run.treatment_fidelity(row, item, prompt, {})
    assert proof["valid"] is True and proof["mode"] == "passthrough"


@pytest.mark.parametrize(
    "mutation",
    ["input-hash", "stdin-hash", "modified-skip", "mcp", "incomplete", "source-on-skip", "argv"],
)
def test_treatment_rejects_claim_without_matching_delivery_evidence(tmp_path, mutation):
    item = task(supplied=True)
    prompt, report, row, path = make_preparation(tmp_path, item)
    if mutation == "input-hash":
        report["preparation"]["task_prompt_sha256"] = "wrong"
    elif mutation == "stdin-hash":
        report["native_stdin"]["sha256"] = "wrong"
    elif mutation == "modified-skip":
        report["preparation"]["prepared_prompt_sha256"] = "wrong"
        report["native_stdin"]["sha256"] = "wrong"
    elif mutation == "mcp":
        row["telemetry"]["mcp_call_count"] = 1
    elif mutation == "incomplete":
        row["telemetry"]["mcp_counts_complete"] = False
    elif mutation == "source-on-skip":
        report["preparation"]["files"] = [{"path": "module.py", "sha256": "f" * 64}]
    else:
        report["exec_argv"][-1] = "inline source"
    path.write_text(json.dumps(report))
    assert run.treatment_fidelity(row, item, prompt, {})["valid"] is False


def test_preloaded_hash_checked_against_independent_frozen_git_source(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "module.py").write_text("def target():\n    return 0\n")
    run.legacy.git(repository, "init")
    run.legacy.git(repository, "add", ".")
    run.legacy.git(
        repository,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Frozen",
    )
    metadata = {"path": str(repository), "commit": run.legacy.git(repository, "rev-parse", "HEAD")}
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    item = task()
    prompt, report, row, path = make_preparation(artifacts, item, mode="preloaded")
    report["preparation"]["reason"] = "explicit_focus"
    report["preparation"]["context_bytes"] = 32
    report["native_stdin"]["bytes"] += 32
    report["preparation"]["files"] = [
        {
            "path": "module.py",
            "sha256": run.digest((repository / "module.py").read_bytes()),
            "start_line": 1,
            "end_line": 2,
        }
    ]
    report["preparation"]["prepared_prompt_sha256"] = "c" * 64
    report["native_stdin"]["sha256"] = "c" * 64
    path.write_text(json.dumps(report))
    assert run.treatment_fidelity(row, item, prompt, metadata)["valid"] is True
    report["preparation"]["files"][0]["sha256"] = "not-original"
    path.write_text(json.dumps(report))
    assert run.treatment_fidelity(row, item, prompt, metadata)["valid"] is False


def test_fake_native_process_requires_durable_grant_and_preserves_observed_usage(tmp_path):
    artifacts = tmp_path / "attempt"
    artifacts.mkdir()
    program = "import sys;sys.stdin.read();print(" + repr(events()) + ",end='')"
    result = run.execute_codex(
        [sys.executable, "-c", program],
        "same task",
        tmp_path,
        artifacts,
        10,
        {**os.environ, "CODEX_HOME": str(tmp_path / "no-auth")},
    )
    assert result["exit_code"] == 0 and result["timed_out"] is False
    assert result["telemetry"]["usage"] == {
        "input_tokens": 12,
        "cached_input_tokens": 4,
        "output_tokens": 2,
    }
    assert json.loads((artifacts / "process-identity.json").read_text()) == json.loads(
        (artifacts / "launch-grant.json").read_text()
    )
    assert not (artifacts / "codex-state/auth.json").exists()
    assert (
        result["process_finished_monotonic_seconds"] >= result["process_started_monotonic_seconds"]
    )


def test_fake_native_timeout_is_retained_without_invented_complete_usage(tmp_path):
    artifacts = tmp_path / "attempt"
    artifacts.mkdir()
    result = run.execute_codex(
        [sys.executable, "-c", "import time;time.sleep(20)"],
        "task",
        tmp_path,
        artifacts,
        0.1,
        {**os.environ, "CODEX_HOME": str(tmp_path / "no-auth")},
    )
    assert result["timed_out"] is True and result["exit_code"] != 0
    assert result["telemetry"]["usage"]["input_tokens"] is None
    assert result["telemetry"]["mcp_counts_complete"] is False


def test_report_retains_failed_costs_missing_telemetry_and_deliberately_different_model_prompts():
    plan = run.make_plan([task()], 2, 1)
    rows = [completed(row, cost=2) for row in plan]
    failed = next(row for row in rows if row["configuration"] == "B")
    failed.update(status="failed", grader={"success": False})
    failed["actual_cost_usd"] = 5
    report = run.build_report(rows, [task()], {})
    b = report["configurations"]["B"]
    assert b["successful_runs"] == 1 and b["actual_cost_per_successful_task_usd"]["value"] == 7
    assert report["paired_comparison"]["valid_pairs"] == 2
    assert len(report["failures"]) == 1
    assert b["metrics"]["model_calls"]["total"] is None
    assert b["metrics"]["repeated_file_reads"]["total"] is None
    assert b["metrics"]["uncached_input_tokens"]["mean"] == 80
    failed["actual_cost_usd"] = None
    assert (
        run.build_report(rows, [task()], {})["configurations"]["B"][
            "actual_cost_per_successful_task_usd"
        ]["value"]
        is None
    )


@pytest.mark.parametrize("field", ["common_task_prompt_sha256", "starting_commit"])
def test_mismatched_common_inputs_exclude_pair_without_hiding_primary_observations(field):
    rows = [completed(row) for row in run.make_plan([task()], 1, 1)]
    rows[1][field] = "different"
    report = run.build_report(rows, [task()], {})
    assert report["paired_comparison"]["valid_pairs"] == 0
    assert len(report["runs"]) == 2
    assert sum(summary["attempted_runs"] for summary in report["configurations"].values()) == 2


def test_summary_never_turns_partial_totals_into_measured_totals():
    summary = run.summarize([1, 2, None])
    assert summary["known_total"] == 3 and summary["total"] is None
    assert summary["mean"] == summary["median"] == 1.5
    assert summary["p95"] == 2 and summary["missing"] == 1
    assert run.summarize([5], additive=False)["total"] is None


def test_resuming_interrupted_original_keeps_unknown_and_does_not_requeue(tmp_path):
    row = run.make_plan([task()], 1, 1)[0]
    state = {"originals": {row["run_id"]: run.durable.pending(row)}, "supplemental": []}
    metadata = {"frozen_manifest": {"settings": {}}, "resume_count": 0}
    attempt = run.begin_attempt(tmp_path, row, state, metadata)
    artifacts = Path(attempt["artifacts"])
    (artifacts / "events.jsonl").write_text(events())
    run.recover_interrupted(tmp_path, state, metadata)
    saved = state["originals"][row["run_id"]]
    assert saved["status"] == "interrupted" and saved["attempted"] is True
    assert saved.get("pending") is False and saved["grader"]["success"] is None
    assert saved["telemetry"]["usage"]["input_tokens"] is None
    assert saved["telemetry"]["usage_coverage_complete"] is False
    result_bytes = (artifacts / "result.json").read_bytes()
    run.recover_interrupted(tmp_path, state, metadata)
    assert (artifacts / "result.json").read_bytes() == result_bytes
    assert run.durable.read_log(tmp_path)[-1]["event"] == "attempt.interrupted"


def test_result_tampering_and_frozen_source_changes_refuse_resume(tmp_path):
    row = run.make_plan([task()], 1, 1)[0]
    state = {"originals": {row["run_id"]: run.durable.pending(row)}, "supplemental": []}
    metadata = {"frozen_manifest": {"files": {"module.py": "original"}}}
    run.begin_attempt(tmp_path, row, state, metadata)
    run.recover_interrupted(tmp_path, state, metadata)
    artifact = Path(state["originals"][row["run_id"]]["artifacts"]) / "result.json"
    artifact.write_text("{}")
    with pytest.raises(ValueError, match="sealed"):
        run.recover_interrupted(tmp_path, state, metadata)
    changed = copy.deepcopy(metadata["frozen_manifest"])
    changed["files"]["module.py"] = "changed"
    with pytest.raises(ValueError, match="changed"):
        run.durable.validate_frozen(metadata, changed)


def test_existing_output_requires_explicit_resume_and_finished_resume_is_readonly(
    tmp_path, monkeypatch
):
    with pytest.raises(SystemExit):
        run.main(["--output", str(tmp_path)])
    (tmp_path / "state.json").write_text("{}")
    monkeypatch.setattr(run, "run_experiment", lambda *_: 0)
    assert run.main(["--output", str(tmp_path), "--resume"]) == 0


def test_native_cli_accepts_no_mcp_configuration_without_auth_or_model_requests(tmp_path):
    executable = shutil.which("codex")
    if executable is None:
        pytest.skip("Native CLI unavailable")
    command = run.codex_command(
        executable, tmp_path, tmp_path / "s", tmp_path / "f", "model", "low"
    )
    assert command[-1] == "-"
    # CLI inspection is entirely local and requires no device/API credentials.
    import subprocess

    (tmp_path / "empty-state").mkdir()
    native = subprocess.run(
        [executable, "-c", "mcp_servers={}", "mcp", "list", "--json"],
        env={**os.environ, "CODEX_HOME": str(tmp_path / "empty-state")},
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert native.returncode == 0 and json.loads(native.stdout) == []
    assert not (tmp_path / "empty-state/auth.json").exists()


def test_source_guard_failure_excludes_pairs_but_retains_all_attempts():
    rows = [completed(row) for row in run.make_plan([task()], 1, 7)]
    report = run.build_report(rows, [task()], {"source_unchanged_during_experiment": False})
    assert report["paired_comparison"]["valid_pairs"] == 0
    assert len(report["paired_comparison"]["excluded_pairs"]) == 1
    assert len(report["runs"]) == 2
    assert report["configurations"]["B"]["attempted_runs"] == 1


def test_failed_cold_index_does_not_become_zero_overhead():
    explicit_b = {"configuration": "B", "selection_stratum": "explicit_focus", "attempted": True}
    measured = run.metrics(explicit_b)
    assert measured["approval_index_wall_seconds"] is None
    assert measured["approval_index_cpu_seconds"] is None
    assert measured["total_observed_local_cpu_seconds"] is None
    supplied_b = {**explicit_b, "selection_stratum": "caller_context_supplied"}
    assert run.metrics(supplied_b)["approval_index_wall_seconds"] == 0
    assert run.metrics({**explicit_b, "configuration": "A"})["approval_index_cpu_seconds"] == 0


def test_mismatched_context_size_is_invalid_without_claiming_token_measurement(tmp_path):
    item = task(supplied=True)
    prompt, report, row, path = make_preparation(tmp_path, item)
    report["native_stdin"]["bytes"] += 1
    path.write_text(json.dumps(report))
    assert run.treatment_fidelity(row, item, prompt, {})["valid"] is False
    assert run.metrics(row)["input_tokens"] == 100


def test_finished_resume_is_readonly_and_does_not_request_models(tmp_path, monkeypatch):
    frozen = {"files": {"only": "fixed"}}
    metadata = {"frozen_manifest": frozen, "repositories": {}, "finished_at": "already finished"}
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))
    (tmp_path / "state.json").write_text(json.dumps({"originals": {}, "supplemental": []}))
    (tmp_path / "plan.json").write_text(json.dumps({"tasks": [], "runs": []}))
    (tmp_path / "report.json").write_text("{}")
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    monkeypatch.setattr(run, "load_tasks", lambda *_: [])
    monkeypatch.setattr(run, "frozen_manifest", lambda *_: frozen)
    monkeypatch.setattr(
        run.subprocess, "check_output", lambda *_args, **_kwargs: "fake-native-version"
    )

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Finished resume must not execute or recreate fixtures")

    monkeypatch.setattr(run, "execute_codex", forbidden)
    monkeypatch.setattr(run, "create_repositories", forbidden)
    arguments = run.parser().parse_args(["--output", str(tmp_path), "--resume"])
    assert run.run_experiment(arguments, tmp_path) == 0
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_real_launcher_delivers_complete_frozen_source_to_fake_native_stdin(tmp_path):
    worktree, artifacts = tmp_path / "worktree", tmp_path / "artifacts"
    worktree.mkdir()
    artifacts.mkdir()
    content = "def count(value):\n    return value + 1\n"
    (worktree / "module.py").write_text(content)
    run.legacy.git(worktree, "init")
    run.legacy.git(worktree, "add", ".")
    run.legacy.git(
        worktree,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Frozen",
    )
    repository = {"path": str(worktree), "commit": run.legacy.git(worktree, "rev-parse", "HEAD")}
    executable = tmp_path / "fake-native"
    # This executable is outside the worktree and performs no network/model work.
    executable.write_text(
        "#!" + sys.executable + "\nimport hashlib,json,sys\nfrom pathlib import Path\n"
        "body=sys.stdin.buffer.read()\n"
        "Path("
        + repr(str(artifacts / "received.json"))
        + ").write_text(json.dumps({'sha256':hashlib.sha256(body).hexdigest(),'text':body.decode()}))\n"
        "print(" + repr(events()) + ",end='')\n"
    )
    executable.chmod(0o700)
    setup = run.prepare_project(worktree, artifacts)
    item = task()
    prompt = run.task_prompt(item)
    native = run.codex_command(
        str(executable), worktree, artifacts / "s", artifacts / "f", "same", "low"
    )
    command = run.preload_command(native, artifacts, item, setup["project_id"])
    row = run.execute_codex(
        command,
        prompt,
        worktree,
        artifacts,
        20,
        {**os.environ, "CODEX_HOME": str(tmp_path / "no-auth")},
    )
    assert row["exit_code"] == 0, (artifacts / "stderr.log").read_text()
    row.update(configuration="B", artifacts=str(artifacts), native_command=native)
    evidence = run.treatment_fidelity(row, item, prompt, repository)
    assert evidence["valid"] is True and evidence["mode"] == "preloaded"
    received = json.loads((artifacts / "received.json").read_text())
    assert received["sha256"] == evidence["actual_model_prompt_sha256"]
    assert received["text"].startswith(prompt)
    source_json = received["text"].split('{"memglide_sources":', 1)[1]
    delivered = json.loads('{"memglide_sources":' + source_json)["memglide_sources"]
    assert delivered == [
        {
            "path": "module.py",
            "sha256": run.digest(content.encode()),
            "start_line": 1,
            "end_line": 2,
            "content": content,
        }
    ]
    raw = json.loads((artifacts / "preparation.json").read_text())
    assert "prompt" not in raw["preparation"]
    assert raw["native_exec_boundary_monotonic_seconds"] >= row["process_started_monotonic_seconds"]
    # Duplicate/missing declared paths cannot masquerade as complete delivery.
    raw["preparation"]["files"] *= 2
    (artifacts / "preparation.json").write_text(json.dumps(raw))
    assert run.treatment_fidelity(row, item, prompt, repository)["valid"] is False


@pytest.mark.parametrize("field", ["common_task_prompt_sha256", "starting_commit"])
def test_matching_but_invalid_identity_hashes_never_validate_pairs(field):
    rows = [completed(row) for row in run.make_plan([task()], 1, 2)]
    for row in rows:
        row[field] = "same-but-not-a-valid-hash"
    assert run.build_report(rows, [task()], {})["paired_comparison"]["valid_pairs"] == 0


def test_fake_native_end_to_end_preserves_external_failures_and_finished_resume(
    tmp_path, monkeypatch
):
    executable = tmp_path / "fake-native"
    executable.write_text(
        "#!" + sys.executable + "\nimport sys\n"
        "if '--version' in sys.argv:\n print('fake-native-unit-test');sys.exit(0)\n"
        "sys.stdin.buffer.read()\n"
        "from pathlib import Path\nimport json\n"
        "Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(json.dumps({'summary':'Fake local execution only','tests_run':[]}))\n"
        "print(" + repr(events()) + ",end='')\n"
    )
    executable.chmod(0o700)
    # Production source is changing concurrently in the shared test workspace;
    # this unit focuses on run lifecycle, while separate guard tests verify freezes.
    monkeypatch.setattr(run, "frozen_manifest", lambda *_: {"unit_test": "fixed"})
    output = tmp_path / "experiment"
    args = [
        "--output",
        str(output),
        "--codex",
        str(executable),
        "--codex-home",
        str(tmp_path / "no-auth"),
        "--repeats",
        "1",
        "--limit",
        "1",
    ]
    assert run.main(args) == 0
    report = json.loads((output / "report.json").read_text())
    assert len(report["runs"]) == 2 and report["paired_comparison"]["valid_pairs"] == 1
    assert all(
        row["status"] == "failed" and row["grader"]["success"] is False for row in report["runs"]
    )
    assert len(report["failures"]) == 2
    assert all(
        row["metrics"]["model_calls"] is None and row["metrics"]["actual_cost_usd"] is None
        for row in report["runs"]
    )
    assert all(row["telemetry"]["usage"]["input_tokens"] == 12 for row in report["runs"])
    assert (
        len(
            [
                record
                for record in run.durable.read_log(output)
                if record["event"] == "attempt.finished"
            ]
        )
        == 2
    )
    original_report = (output / "report.json").read_bytes()
    assert run.main([*args, "--resume"]) == 0
    assert (output / "report.json").read_bytes() == original_report


def test_completion_and_cost_denominator_require_valid_completed_execution():
    base = completed({"configuration": "B", "run_id": "sample"}, cost=2)
    rows = []
    for index, status in enumerate(
        ("completed", "timeout", "execution_failed", "invalid_treatment")
    ):
        rows.append({**copy.deepcopy(base), "run_id": str(index), "status": status})
    invalid_treatment = copy.deepcopy(base)
    invalid_treatment["treatment_valid"] = False
    rows.append(invalid_treatment)
    invalid_execution = copy.deepcopy(base)
    invalid_execution["native_execution_validity"]["valid"] = False
    rows.append(invalid_execution)
    summary = run.aggregate(rows)
    assert summary["behavior_grade_pass_count"] == 6
    assert summary["successful_runs"] == 1
    assert summary["successful_task_completion_rate"] == 1 / 6
    assert summary["actual_cost_per_successful_task_usd"]["value"] == 12


@pytest.mark.parametrize(
    "mutation",
    ["missing", "malformed", "duplicate", "extra", "wrong-tests", "wrong-summary", "symlink"],
)
def test_schema_validation_rejects_invalid_native_final_artifact(tmp_path, mutation):
    final = tmp_path / "final.json"
    final.write_text(json.dumps({"summary": "A summary, not a grade", "tests_run": []}))
    if mutation == "missing":
        final.unlink()
    elif mutation == "malformed":
        final.write_text('{"summary":')
    elif mutation == "duplicate":
        final.write_text('{"summary":"one","summary":"two","tests_run":[]}')
    elif mutation == "extra":
        final.write_text('{"summary":"one","tests_run":[],"success":true}')
    elif mutation == "wrong-tests":
        final.write_text('{"summary":"one","tests_run":[12]}')
    elif mutation == "wrong-summary":
        final.write_text('{"summary":false,"tests_run":[]}')
    else:
        actual = tmp_path / "another-file"
        final.rename(actual)
        final.symlink_to(actual)
    (tmp_path / "events.jsonl").write_text(events())
    result = {
        "exit_code": 0,
        "timed_out": False,
        "telemetry": run.parse_codex_jsonl(events()),
        "event_stream_framing": run.native_event_framing(tmp_path / "events.jsonl"),
    }
    evidence = run.native_execution_validity(result, final)
    assert evidence["valid"] is False and evidence["final_output_sha256"] is None


@pytest.mark.parametrize(
    "mutation", ["exit-status", "timeout", "truncated", "failed-turn", "malformed-event"]
)
def test_zero_exit_alone_cannot_validate_native_execution(tmp_path, mutation):
    final = tmp_path / "final.json"
    final.write_text('{"summary":"Agent claim only","tests_run":[]}')
    (tmp_path / "events.jsonl").write_text(events())
    result = {
        "exit_code": 0,
        "timed_out": False,
        "telemetry": run.parse_codex_jsonl(events()),
        "event_stream_framing": run.native_event_framing(tmp_path / "events.jsonl"),
    }
    if mutation == "exit-status":
        result["exit_code"] = 9
    elif mutation == "timeout":
        result["timed_out"] = True
    elif mutation == "truncated":
        result["telemetry"] = run.parse_codex_jsonl('{"type":"thread.started"}\n')
    elif mutation == "failed-turn":
        result["telemetry"] = run.parse_codex_jsonl(
            events() + '{"type":"turn.failed","error":{"message":"failure"}}\n'
        )
    else:
        result["telemetry"] = run.parse_codex_jsonl(events() + "broken json\n")
    assert run.native_execution_validity(result, final)["valid"] is False


def test_valid_schema_and_complete_native_stream_do_not_claim_behavior_grade(tmp_path):
    final = tmp_path / "final.json"
    final.write_text('{"summary":"No behavior claim","tests_run":[]}')
    (tmp_path / "events.jsonl").write_text(events())
    result = {
        "exit_code": 0,
        "timed_out": False,
        "telemetry": run.parse_codex_jsonl(events()),
        "event_stream_framing": run.native_event_framing(tmp_path / "events.jsonl"),
    }
    evidence = run.native_execution_validity(result, final)
    assert evidence["valid"] is True and len(evidence["final_output_sha256"]) == 64
    assert "grader" not in evidence


def sealed_state_fixture(output):
    tasks = [task()]
    plan = run.make_plan(tasks, 1, 3)
    state = {
        "originals": {row["run_id"]: run.durable.pending(row) for row in plan},
        "supplemental": [],
    }
    metadata = {}
    run.atomic_json(output / "plan.json", {"tasks": tasks, "runs": plan}, immutable=True)
    attempt = run.begin_attempt(output, plan[0], state, metadata)
    result = {**attempt, **completed(plan[0])}
    run.atomic_json(Path(attempt["artifacts"]) / "result.json", result, immutable=True)
    run.durable.finish_attempt(output, result, state, metadata)
    return tasks, plan, state


@pytest.mark.parametrize(
    "mutation",
    ["state-grade", "state-identity", "saved-plan", "start-content", "missing-state-slot"],
)
def test_resume_refuses_projection_and_plan_drift_from_sealed_evidence(tmp_path, mutation):
    tasks, plan, state = sealed_state_fixture(tmp_path)
    run.validate_saved_state(tmp_path, tasks, plan, state)
    identifier = plan[0]["run_id"]
    if mutation == "state-grade":
        state["originals"][identifier]["grader"]["success"] = False
    elif mutation == "state-identity":
        state["originals"][identifier]["configuration"] = "different"
    elif mutation == "saved-plan":
        document = json.loads((tmp_path / "plan.json").read_text())
        document["tasks"][0]["prompt"] = "Different task"
        (tmp_path / "plan.json").write_text(json.dumps(document))
    elif mutation == "start-content":
        start = tmp_path / "runs" / identifier / "attempt-start.json"
        value = json.loads(start.read_text())
        value["errors"].append("Altered immutable start")
        start.write_text(json.dumps(value))
    else:
        del state["originals"][plan[1]["run_id"]]
    with pytest.raises(ValueError):
        run.validate_saved_state(tmp_path, tasks, plan, state)


def test_crash_stale_pending_projection_recovers_original_without_new_execution(tmp_path):
    tasks = [task()]
    plan = run.make_plan(tasks, 1, 3)
    pending_state = {
        "originals": {row["run_id"]: run.durable.pending(row) for row in plan},
        "supplemental": [],
    }
    active_state = copy.deepcopy(pending_state)
    metadata = {}
    run.atomic_json(tmp_path / "plan.json", {"tasks": tasks, "runs": plan}, immutable=True)
    run.begin_attempt(tmp_path, plan[0], active_state, metadata)
    # This is the checkpoint state before a crash between durable start and projection.
    run.validate_saved_state(tmp_path, tasks, plan, pending_state)
    run.recover_interrupted(tmp_path, pending_state, metadata)
    recovered = pending_state["originals"][plan[0]["run_id"]]
    assert recovered["status"] == "interrupted" and recovered["attempted"] is True
    assert recovered.get("pending") is False and recovered["grader"]["success"] is None
    run.validate_saved_state(tmp_path, tasks, plan, pending_state)


@pytest.mark.parametrize(
    "prefix",
    [
        [],
        [{"type": "turn.started"}],
        [{"type": "thread.started"}, {"type": "turn.started"}],
        [{"type": "thread.started", "thread_id": ""}, {"type": "turn.started"}],
        [{"type": "thread.started", "thread_id": "   "}, {"type": "turn.started"}],
        [{"type": "thread.started", "thread_id": "observed"}],
    ],
)
def test_terminal_tail_cannot_hide_missing_native_thread_turn_prefix(tmp_path, prefix):
    terminal = {
        "type": "turn.completed",
        "usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 2},
    }
    stream = "\n".join(json.dumps(event) for event in [*prefix, terminal]) + "\n"
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(stream)
    final = tmp_path / "final.json"
    final.write_text('{"summary":"Native claim","tests_run":[]}')
    telemetry = run.parse_codex_jsonl(stream)
    # The historical parser recognizes the tail; the new runner independently
    # refuses to call the whole execution valid without the observed prefix.
    assert telemetry["stream_terminal"] is True
    framing = run.native_event_framing(events_path)
    result = {
        "exit_code": 0,
        "timed_out": False,
        "telemetry": telemetry,
        "event_stream_framing": framing,
    }
    assert framing["valid"] is False
    assert run.native_execution_validity(result, final)["valid"] is False
