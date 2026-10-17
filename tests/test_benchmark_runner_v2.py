"""Protocol/durability checks using synthetic CLI events, never model requests."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_v2 as run  # noqa: E402
from benchmarks.reporting import build_report  # noqa: E402
from benchmarks.telemetry import parse_codex_jsonl  # noqa: E402


def fetch_payload():
    return {
        "operation": "get_context",
        "retrieval_id": "synthetic-retrieval",
        "items": [{"path": "module.py", "snippet": "def target(): return 1"}],
        "source_hashes": {"module.py": "a" * 64},
    }


def verify_payload():
    return {
        "operation": "get_context_passport",
        "retrieval_id": "synthetic-retrieval",
        "status": "Stale",
        "source_freshness": "Stale",
        "stale_files": ["module.py"],
    }


def event_stream(*tools, incomplete=False):
    events = [{"type": "thread.started", "thread_id": "unit-test-only"}]
    for index, (tool, result) in enumerate(tools):
        events.append(
            {
                "type": "item.completed",
                "item": {
                    "id": f"test-{index}",
                    "type": "mcp_tool_call",
                    "server": "memglide",
                    "tool": tool,
                    "status": "completed",
                    "result": result,
                },
            }
        )
    if not incomplete:
        events.append(
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 20,
                    "cached_input_tokens": 4,
                    "output_tokens": 3,
                },
            }
        )
    return "\n".join(json.dumps(event) for event in events) + "\n"


def text_result(payload):
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def test_forty_tasks_two_repeats_are_repository_routed_and_counterbalanced():
    tasks = [
        {
            "id": f"{repository}-{number}",
            "repository": repository,
            "language": language,
            "prompt": "Synthetic plan only",
        }
        for repository, language in run.REPOSITORIES.items()
        for number in range(10)
    ]
    plan = run.make_plan(tasks, 2, 20261017)
    assert len(plan) == len({row["run_id"] for row in plan}) == 160
    assert plan == run.make_plan(tasks, 2, 20261017)
    assert {row["repository"] for row in plan} == set(run.REPOSITORIES)
    for task in tasks:
        rows = [row for row in plan if row["task_id"] == task["id"]]
        assert [row["configuration"] for row in rows[:2]] == list(
            reversed([row["configuration"] for row in rows[2:]])
        )
        assert len({run.task_prompt(task) for _ in rows}) == 1


def test_compact_config_differs_only_in_two_scoped_mcp_tools(tmp_path):
    args = ("codex", tmp_path, tmp_path / "schema", tmp_path / "final", "same-model", "low")
    baseline = run.codex_command(*args)
    treatment = run.codex_command(*args, database=tmp_path / "b.db", project_id="project-1")
    assert baseline[:-2] == treatment[:-2]
    assert tomllib.loads(baseline[-2]) == {"mcp_servers": {}}
    server = tomllib.loads(treatment[-2])["mcp_servers"]["memglide"]
    assert server["enabled_tools"] == ["fetch_context", "verify_context"]
    assert server["tools"] == {tool: {"approval_mode": "approve"} for tool in run.APPROVED_TOOLS}
    assert server["args"] == [
        "--db",
        str(tmp_path / "b.db"),
        "mcp",
        "--profile",
        "agent",
        "--project",
        "project-1",
    ]
    assert server["required"] and server["startup_readiness"] == "connection"
    assert 'approval_policy="never"' in treatment
    assert treatment[treatment.index("--sandbox") + 1] == "workspace-write"
    assert "--json" in treatment and "--output-schema" in treatment
    with pytest.raises(ValueError, match="project ID"):
        run.codex_command(*args, database=tmp_path / "b.db")


def test_native_codex_accepts_compact_config_without_auth_or_model_requests(tmp_path):
    executable = shutil.which("codex")
    if executable is None:
        pytest.skip("Native Codex is unavailable")
    state = tmp_path / "empty-auth-state"
    state.mkdir()
    command = run.codex_command(
        executable,
        tmp_path,
        tmp_path / "s",
        tmp_path / "f",
        "same",
        "low",
        tmp_path / "b.db",
        "test-project",
    )
    completed = subprocess.run(
        [executable, "-c", command[-2], "mcp", "get", "memglide", "--json"],
        cwd=tmp_path,
        env={**os.environ, "CODEX_HOME": str(state)},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert completed.returncode == 0, completed.stderr
    server = json.loads(completed.stdout)
    assert set(server["enabled_tools"]) == set(run.APPROVED_TOOLS)
    assert not (state / "auth.json").exists()


@pytest.mark.parametrize("encoding", ["text", "structured_content", "structuredContent", "both"])
def test_actual_compact_response_proves_retrieval_once_for_all_native_encodings(encoding):
    payload = fetch_payload()
    result = text_result(payload) if encoding in {"text", "both"} else {}
    if encoding != "text":
        result["structured_content" if encoding == "both" else encoding] = payload
    telemetry = parse_codex_jsonl(event_stream(("fetch_context", result)))
    assert telemetry["memglide_successful_fetch_context_count"] == 1
    assert telemetry["memglide_successful_get_context_count"] == 1
    assert telemetry["mcp_call_count"] == 1
    assert telemetry["actual_cost_usd"] is None and telemetry["model_calls"] is None


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong-operation",
        "empty-items",
        "missing-hash",
        "empty-snippet",
        "conflicting-copies",
        "explicit-error",
    ],
)
def test_tool_name_or_model_claim_cannot_prove_compact_retrieval(mutation):
    payload = fetch_payload()
    if mutation == "wrong-operation":
        payload["operation"] = "model-says-success"
    elif mutation == "empty-items":
        payload["items"] = []
    elif mutation == "missing-hash":
        payload["source_hashes"] = {}
    elif mutation == "empty-snippet":
        payload["items"][0]["snippet"] = ""
    result = text_result(payload)
    if mutation == "conflicting-copies":
        result["structured_content"] = {**payload, "retrieval_id": "different"}
    if mutation == "explicit-error":
        result["isError"] = True
    telemetry = parse_codex_jsonl(event_stream(("fetch_context", result)))
    assert telemetry["memglide_successful_fetch_context_count"] == 0
    assert telemetry["memglide_successful_get_context_count"] == 0


@pytest.mark.parametrize("required_marker", [None, ["fetch_context", "verify_context"]])
def test_missing_compact_verification_excludes_pair_without_falsifying_retrieval_count(
    required_marker,
):
    baseline = parse_codex_jsonl(event_stream())
    treatment = parse_codex_jsonl(event_stream(("fetch_context", text_result(fetch_payload()))))
    rows = [
        {
            "task_id": "test",
            "configuration": arm,
            "repeat": 1,
            "status": "completed",
            "attempted": True,
            "grader": {"success": True},
            "starting_commit": "a" * 40,
            "prompt_sha256": "b" * 64,
            "telemetry": telemetry,
            **(
                {
                    "compact_protocol_fidelity": {
                        "valid": True,
                        **(
                            {"required_operations": required_marker}
                            if required_marker is not None
                            else {}
                        ),
                    }
                }
                if arm == "B"
                else {}
            ),
        }
        for arm, telemetry in (("A", baseline), ("B", treatment))
    ]
    report = build_report(rows, [{"id": "test"}], {"repeats": 1})
    assert report["runs"][1]["telemetry"]["memglide_successful_get_context_count"] == 1
    assert report["runs"][1]["treatment_fidelity"]["valid"] is False
    assert report["paired_comparisons"]["valid_pair_count"] == 0
    # Legacy retrieval-only protocol keeps its documented semantics.
    del rows[1]["compact_protocol_fidelity"]
    assert (
        build_report(rows, [{"id": "test"}], {"repeats": 1})["paired_comparisons"][
            "valid_pair_count"
        ]
        == 1
    )


def test_stale_after_ownedits_is_valid_revalidation_not_a_forced_refetch():
    telemetry = parse_codex_jsonl(
        event_stream(
            ("fetch_context", text_result(fetch_payload())),
            ("verify_context", text_result(verify_payload())),
        )
    )
    assert telemetry["memglide_successful_fetch_context_count"] == 1
    assert telemetry["memglide_successful_verify_context_count"] == 1
    assert telemetry["memglide_successful_get_context_count"] == 1


def test_real_source_plus_structural_placeholder_is_retrieval_but_all_empty_is_not():
    payload = fetch_payload()
    payload["items"].append({"path": "helper.py", "snippet": "", "symbol": "helper"})
    payload["source_hashes"]["helper.py"] = "b" * 64
    telemetry = parse_codex_jsonl(event_stream(("fetch_context", text_result(payload))))
    assert telemetry["memglide_successful_fetch_context_count"] == 1
    payload["items"][0]["snippet"] = ""
    telemetry = parse_codex_jsonl(event_stream(("fetch_context", text_result(payload))))
    assert telemetry["memglide_successful_fetch_context_count"] == 0


def test_atomic_documents_and_attempt_log_cannot_overwrite_sealed_evidence(tmp_path):
    path = tmp_path / "sealed.json"
    run.atomic_json(path, {"value": 1}, immutable=True)
    with pytest.raises(FileExistsError):
        run.atomic_json(path, {"value": 2}, immutable=True)
    assert json.loads(path.read_text()) == {"value": 1}
    first = run.append_log(tmp_path, "first")
    second = run.append_log(tmp_path, "second")
    assert second["previous_sha256"] == first["sha256"]
    assert len(run.read_log(tmp_path)) == 2
    corrupted = tmp_path / "attempt-log/000001.json"
    corrupted.write_text(corrupted.read_text().replace('"first"', '"changed"'))
    with pytest.raises(ValueError, match="integrity"):
        run.read_log(tmp_path)


def test_real_native_wrapper_records_process_before_exec_and_retains_json_stream(tmp_path):
    code = "import json,sys;sys.stdin.read();print(json.dumps({'type':'turn.completed','usage':{'input_tokens':20,'cached_input_tokens':4,'output_tokens':3}}))"
    artifacts = tmp_path / "synthetic-artifacts"
    result = run.execute_codex(
        [sys.executable, "-c", code], "unit-only", tmp_path, artifacts, 5, {}
    )
    assert result["exit_code"] == 0
    assert json.loads((artifacts / "process-identity.json").read_text())["pid"] > 1
    assert result["telemetry"]["usage"]["input_tokens"] == 20
    original = (artifacts / "events.jsonl").read_bytes()
    with pytest.raises(FileExistsError):
        run.execute_codex([sys.executable, "-c", code], "again", tmp_path, artifacts, 5, {})
    assert (artifacts / "events.jsonl").read_bytes() == original


def test_resume_can_stop_only_the_recorded_orphan_and_refuses_reused_pid(tmp_path):
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            run.PROCESS_WRAPPER,
            str(tmp_path / "process-identity.json"),
            "10",
            sys.executable,
            "-c",
            "import time; time.sleep(30)",
        ],
        start_new_session=True,
    )
    try:
        deadline = time.monotonic() + 5
        while not (tmp_path / "process-identity.json").exists():
            assert time.monotonic() < deadline
            time.sleep(0.01)
        identity = json.loads((tmp_path / "process-identity.json").read_text())
        original_start = identity["start_ticks"]
        identity["start_ticks"] += 1
        run.atomic_json(tmp_path / "process-identity.json", identity)
        assert run.stop_orphan(tmp_path) is False and process.poll() is None
        identity["start_ticks"] = original_start
        run.atomic_json(tmp_path / "process-identity.json", identity)
        assert run.stop_orphan(tmp_path) is True
        process.wait(timeout=5)
        assert process.returncode != 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def test_delayed_wrapper_cannot_start_a_request_after_launcher_dies_before_identity(tmp_path):
    artifacts = tmp_path / "delayed-artifacts"
    barrier, forbidden = tmp_path / "parent-started-child", tmp_path / "native-request-started"
    launcher_code = f"""
import subprocess,sys
from pathlib import Path
from benchmarks import run_v2 as runner
runner.PROCESS_WRAPPER = "import time;time.sleep(0.4)\\n" + runner.PROCESS_WRAPPER.replace('+float(sys.argv[2])', '+0.2')
original_popen = subprocess.Popen
def notify(*args, **kwargs):
    child = original_popen(*args, **kwargs)
    Path({str(barrier)!r}).write_text(str(child.pid))
    return child
runner.subprocess.Popen = notify
runner.execute_codex([sys.executable,'-c',"from pathlib import Path;Path({str(forbidden)!r}).write_text('paid-request-would-start')"], 'synthetic-only', Path({str(tmp_path)!r}), Path({str(artifacts)!r}), 5, {{}})
"""
    launcher = subprocess.Popen([sys.executable, "-c", launcher_code], cwd=run.ROOT)
    child_pid = None
    try:
        deadline = time.monotonic() + 5
        while not barrier.exists():
            assert time.monotonic() < deadline
            time.sleep(0.01)
        child_pid = int(barrier.read_text())
        assert not (artifacts / "process-identity.json").exists()
        launcher.kill()
        launcher.wait(timeout=5)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            path = Path(f"/proc/{child_pid}/stat")
            if not path.exists() or path.read_text().rsplit(")", 1)[1].split()[0] == "Z":
                break
            time.sleep(0.02)
        else:
            pytest.fail("Ungrantable delayed wrapper did not terminate")
        assert (artifacts / "process-identity.json").exists()
        assert not (artifacts / "launch-grant.json").exists()
        assert not forbidden.exists()
    finally:
        if launcher.poll() is None:
            launcher.kill()
            launcher.wait()
        if child_pid:
            try:
                os.killpg(child_pid, 9)
            except ProcessLookupError:
                pass


@pytest.fixture
def isolated_experiment(tmp_path, monkeypatch):
    output = tmp_path / "synthetic-no-model-experiment"
    argv = [
        "--output",
        str(output),
        "--corpus",
        "legacy",
        "--tasks",
        str(run.ROOT / "benchmarks/tasks.json"),
        "--limit",
        "1",
        "--repeats",
        "1",
        "--skip-preflight",
        "--codex",
        sys.executable,
    ]
    monkeypatch.setattr(run, "frozen_manifest", lambda *_: {"test_only_frozen_source": True})
    monkeypatch.setattr(run.legacy, "host_metadata", lambda: {})
    monkeypatch.setattr(
        run.legacy,
        "prepare_memglide",
        lambda *_: {
            "project_id": "unit-test-only",
            "index_wall_seconds": 0,
            "wall_seconds": 0,
        },
    )
    calls = []

    def native_stub(command, prompt, worktree, artifacts, timeout, environment):
        # Verify the durable assignment and metadata exist BEFORE every request.
        metadata = json.loads((output / "metadata.json").read_text())
        state = json.loads((output / "state.json").read_text())
        assert metadata["frozen_manifest"] == {"test_only_frozen_source": True}
        assert any(
            row["status"] == "running"
            for row in list(state["originals"].values()) + state["supplemental"]
        )
        assert artifacts not in calls
        calls.append(artifacts)
        treatment = bool(tomllib.loads(command[-2])["mcp_servers"])
        tools = [("fetch_context", text_result(fetch_payload()))] if treatment else []
        if treatment and "Use verify_context once after editing;" in prompt:
            tools.append(("verify_context", text_result(verify_payload())))
        events = event_stream(*tools)
        (artifacts / "prompt.txt").write_text(prompt)
        (artifacts / "events.jsonl").write_text(events)
        (artifacts / "stderr.log").write_text("")
        return {
            "exit_code": 0,
            "timed_out": False,
            "wall_time_seconds": 0.01,
            "overhead": {},
            "telemetry": parse_codex_jsonl(events),
        }

    monkeypatch.setattr(run, "execute_codex", native_stub)
    return output, argv, calls


@pytest.mark.parametrize("require_verification", [False, True])
def test_frozen_on_demand_or_explicit_two_call_policy_is_applied_to_real_run_results(
    isolated_experiment,
    require_verification,
):
    output, argv, _ = isolated_experiment
    assert run.main(argv + (["--require-verification"] if require_verification else [])) == 0
    report = json.loads((output / "report.json").read_text())
    treatment = next(row for row in report["runs"] if row["configuration"] == "B")
    assert treatment["telemetry"]["memglide_successful_fetch_context_count"] == 1
    assert treatment["telemetry"]["memglide_successful_verify_context_count"] == int(
        require_verification
    )
    assert treatment["compact_protocol_fidelity"]["required_operations"] == run.required_operations(
        require_verification
    )
    assert treatment["treatment_fidelity"]["valid"] is True
    assert (
        treatment["status"] == "failed"
    )  # Independent baseline grader fails; MCP validity is separate.
    assert report["paired_comparisons"]["valid_pair_count"] == 1
    assert len({row["prompt_sha256"] for row in report["runs"]}) == 1
    assert len({Path(row["artifacts"], "prompt.txt").read_text() for row in report["runs"]}) == 1
    assert all(
        row["post_execution_context_audit"]["phase"] == "post_codex_pre_grader"
        for row in report["runs"]
    )
    assert all(
        Path(row["artifacts"], "post-execution-source-audit.json").exists()
        for row in report["runs"]
    )


def test_context_audit_runs_before_external_grader_and_failure_does_not_invent_task_failure(
    isolated_experiment,
    monkeypatch,
):
    output, argv, _ = isolated_experiment
    from benchmarks import context_audit_v2, corpus

    original_grade = corpus.grade
    original_native_stub = run.execute_codex
    order = []

    def successful_synthetic_edit(command, prompt, worktree, artifacts, timeout, environment):
        result = original_native_stub(command, prompt, worktree, artifacts, timeout, environment)
        # This unit-only synthetic CLI fixes the old development fixture. The
        # real external behavioral grader must then prove the code works.
        source = worktree / "atlas/cache.py"
        text = source.read_text()
        assert "if now > expires:" in text
        source.write_text(text.replace("if now > expires:", "if now >= expires:"))
        return result

    def unavailable_audit(events, worktree, destination):
        order.append(("audit", worktree))
        raise OSError("Synthetic audit-only failure")

    def checked_grade(task_id, worktree, artifacts):
        assert order[-1] == ("audit", worktree)
        order.append(("grade", worktree))
        return original_grade(task_id, worktree, artifacts)

    monkeypatch.setattr(context_audit_v2, "capture_snapshot", unavailable_audit)
    monkeypatch.setattr(corpus, "grade", checked_grade)
    monkeypatch.setattr(run, "execute_codex", successful_synthetic_edit)
    assert run.main(argv) == 0
    rows = json.loads((output / "runs.json").read_text())
    assert len(order) == 4
    assert all(row["status"] == "completed" for row in rows)
    assert all(row["post_execution_context_audit"]["available"] is False for row in rows)
    assert all(row["grader"]["success"] is True for row in rows)


def test_interrupted_original_is_preserved_and_retry_is_a_distinct_supplemental_attempt(
    isolated_experiment, monkeypatch
):
    output, argv, calls = isolated_experiment
    original_attempt = run.run_attempt

    def interrupt(attempt, *_):
        (Path(attempt["artifacts"]) / "events.jsonl").write_text(event_stream(incomplete=True))
        raise KeyboardInterrupt("Simulated launcher death before outcome/grade")

    monkeypatch.setattr(run, "run_attempt", interrupt)
    with pytest.raises(KeyboardInterrupt):
        run.main(argv)
    state = json.loads((output / "state.json").read_text())
    original = next(row for row in state["originals"].values() if row["status"] == "running")
    stream = Path(original["artifacts"]) / "events.jsonl"
    stream_digest = hashlib.sha256(stream.read_bytes()).hexdigest()
    monkeypatch.setattr(run, "run_attempt", original_attempt)
    assert run.main(argv + ["--resume", "--retry-interrupted"]) == 0
    state = json.loads((output / "state.json").read_text())
    assert state["originals"][original["run_id"]]["status"] == "interrupted"
    assert state["originals"][original["run_id"]]["grader"]["success"] is None
    assert len(state["originals"]) == 2 and len(state["supplemental"]) == 1
    assert state["supplemental"][0]["original_run_id"] == original["run_id"]
    assert state["supplemental"][0]["run_id"].endswith("-supplemental-1")
    assert stream_digest == hashlib.sha256(stream.read_bytes()).hexdigest()
    assert len(calls) == 2
    report = json.loads((output / "report.json").read_text())
    assert len(report["runs"]) == 2 and len(report["supplemental_runs"]) == 1
    assert all(row["actual_cost_usd"] is None for row in report["runs"])
    assert all(row["grader"]["success"] is not True for row in report["runs"])
    report_digest = hashlib.sha256((output / "report.json").read_bytes()).hexdigest()
    assert run.main(argv + ["--resume"]) == 0
    assert report_digest == hashlib.sha256((output / "report.json").read_bytes()).hexdigest()


def test_crash_after_sealed_result_recovers_without_reexecuting_that_assignment(
    isolated_experiment, monkeypatch
):
    output, argv, calls = isolated_experiment
    finish = run.finish_attempt
    monkeypatch.setattr(
        run, "finish_attempt", lambda *_: (_ for _ in ()).throw(KeyboardInterrupt())
    )
    with pytest.raises(KeyboardInterrupt):
        run.main(argv)
    assert len(calls) == 1
    saved = next((output / "runs").glob("*/result.json"))
    saved_hash = hashlib.sha256(saved.read_bytes()).hexdigest()
    monkeypatch.setattr(run, "finish_attempt", finish)
    assert run.main(argv + ["--resume"]) == 0
    assert len(calls) == 2
    assert hashlib.sha256(saved.read_bytes()).hexdigest() == saved_hash
    assert not json.loads((output / "supplemental-runs.json").read_text())


def test_resume_refuses_changed_protocol_before_any_further_request(
    isolated_experiment, monkeypatch
):
    output, argv, calls = isolated_experiment
    monkeypatch.setattr(run, "run_attempt", lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        run.main(argv)
    before = {str(path): path.read_bytes() for path in (output / "attempt-log").glob("*.json")}
    monkeypatch.setattr(run, "frozen_manifest", lambda *_: {"test_only_frozen_source": "changed"})
    with pytest.raises(ValueError, match="changed"):
        run.main(argv + ["--resume"])
    assert calls == []
    assert before == {
        str(path): path.read_bytes() for path in (output / "attempt-log").glob("*.json")
    }


def test_resume_recovers_start_written_before_state_projection(tmp_path):
    output = tmp_path / "experiment"
    output.mkdir()
    row = {"run_id": "task-r1-A", "task_id": "task", "configuration": "A"}
    state = {"originals": {row["run_id"]: run.pending(row)}, "supplemental": []}
    metadata = {}
    # Save a pristine projection, then simulate loss of the post-start projection.
    old_state = copy.deepcopy(state)
    attempt = run.begin_attempt(output, row, state, metadata)
    run.recover_interrupted(output, old_state, metadata)
    recovered = old_state["originals"][row["run_id"]]
    assert recovered["status"] == "interrupted"
    assert recovered["artifacts"] == attempt["artifacts"]
    assert Path(attempt["artifacts"], "attempt-start.json").exists()


def test_interrupted_terminal_looking_stream_retains_observations_but_withholds_totals(tmp_path):
    output = tmp_path / "experiment"
    output.mkdir()
    row = {"run_id": "task-r1-B", "task_id": "task", "configuration": "B"}
    state = {"originals": {row["run_id"]: run.pending(row)}, "supplemental": []}
    metadata = {}
    attempt = run.begin_attempt(output, row, state, metadata)
    (Path(attempt["artifacts"]) / "events.jsonl").write_text(
        event_stream(
            ("fetch_context", text_result(fetch_payload())),
        )
    )
    run.recover_interrupted(output, state, metadata)
    recovered = state["originals"][row["run_id"]]
    telemetry = recovered["telemetry"]
    assert telemetry["usage"]["input_tokens"] is None
    assert telemetry["observed_completed_turn_usage"]["input_tokens"] == 20
    assert telemetry["memglide_successful_get_context_count"] == 1
    assert telemetry["mcp_counts_complete"] is False
    report = build_report([recovered], [{"id": "task"}], {"repeats": 1})
    treatment = next(item for item in report["runs"] if item["configuration"] == "B")
    assert treatment["treatment_fidelity"]["valid"] is None


def test_resume_rechecks_native_cli_version_before_any_new_request(
    isolated_experiment, monkeypatch
):
    _, argv, calls = isolated_experiment
    monkeypatch.setattr(
        run,
        "frozen_manifest",
        lambda _path, _tasks, settings: {
            "test_only_frozen_source": True,
            "codex_version": settings["codex_version"],
        },
    )
    monkeypatch.setattr(run, "run_attempt", lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        run.main(argv)
    original_check_output = subprocess.check_output

    def changed_version(command, **kwargs):
        return (
            "synthetic-changed-CLI-version"
            if command == [sys.executable, "--version"]
            else original_check_output(command, **kwargs)
        )

    monkeypatch.setattr(run.subprocess, "check_output", changed_version)
    with pytest.raises(ValueError, match="changed"):
        run.main(argv + ["--resume"])
    assert calls == []
