"""Auditable v4 native harness controls; all executables are local fakes."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_router_coding as run  # noqa: E402


def public(index=1):
    return {
        "id": f"n{index:02d}",
        "repository": f"r{index:02d}",
        "language": "python" if index % 2 else "typescript",
        "prompt": "Correct the boundary calculation while preserving public behavior.",
    }


def private():
    return {
        "known_paths": ["src/calculation.py"],
        "grader": {
            "argv": [sys.executable, "external.py", "{worktree}", "{artifacts}"],
            "timeout_seconds": 10,
        },
    }


def bounds(**changes):
    return argparse.Namespace(
        **(
            {
                "max_attempts": 72,
                "timeout": 180,
                "max_wall_seconds": 18000,
                "attempt_reserve_usd": 0.25,
                "max_estimated_usd": 20,
            }
            | changes
        )
    )


def test_balanced_three_arm_orders_reverse_without_identity_leaks():
    tasks = [public(index) for index in range(1, 13)]
    rows = run.make_plan(tasks, 2, 17)
    assert len(rows) == len({row["run_id"] for row in rows}) == 72
    assert rows == run.make_plan(tasks, 2, 17)
    for task in tasks:
        found = [row for row in rows if row["task_id"] == task["id"]]
        assert [row["configuration"] for row in found[:3]] == list(
            reversed([row["configuration"] for row in found[3:]])
        )
    for repeat in (1, 2):
        for arm in run.ARMS:
            assert [
                sum(
                    row["repeat"] == repeat
                    and row["configuration"] == arm
                    and (row["order"] - 1) % 3 == position
                    for row in rows
                )
                for position in range(3)
            ] == [4, 4, 4]
    assert all(row["run_id"].startswith("coding-") and "n01" not in row["run_id"] for row in rows)


@pytest.mark.parametrize(
    "mutation",
    ["target-path", "basename", "extra-public", "unsafe-private", "duplicate", "unknown-grader"],
)
def test_public_private_contract_rejects_leaks_or_unsafe_input(mutation):
    task, grade = public(), private()
    if mutation == "target-path":
        task["prompt"] += " src/calculation.py"
    elif mutation == "basename":
        task["prompt"] += " calculation.py"
    elif mutation == "extra-public":
        task["known_paths"] = ["src/calculation.py"]
    elif mutation == "unsafe-private":
        grade["known_paths"] = ["../outside.py"]
    elif mutation == "duplicate":
        grade["known_paths"] *= 2
    else:
        grade["grader"]["argv"] = "python arbitrary.py"
    with pytest.raises(ValueError):
        run.validate_tasks([task], {task["id"]: grade})


def test_path_free_prompt_is_common_and_has_no_oracle_section():
    task = public()
    run.validate_tasks([task], {task["id"]: private()})
    prompt = run.task_prompt(task)
    assert task["prompt"] in prompt and "calculation.py" not in prompt
    assert "Caller-declared" not in prompt and "untrusted data" in prompt
    native = run.native.codex_command(
        "codex", Path("/work"), Path("/schema"), Path("/final"), run.MODEL, run.EFFORT
    )
    assert "--json" in native and "--output-schema" in native
    assert 'service_tier="default"' in native and "mcp_servers={}" in native
    assert 'approval_policy="never"' in native


def test_c_worker_rejects_private_fields_before_any_indexing(tmp_path):
    request = tmp_path / "request.json"
    request.write_text(
        json.dumps(
            {
                "arm": "C",
                "prompt": "public",
                "worktree": str(tmp_path),
                "settings": run.SETTINGS,
                "known_paths": ["hidden.py"],
            }
        )
    )
    with pytest.raises(ValueError, match="private metadata"):
        run.preparation_worker(request)
    assert not (tmp_path / "memglide.db").exists()


def test_legitimate_passthrough_is_valid_and_modified_stdin_is_not():
    prompt = "A common task"
    observation = {
        "preparation": {
            "mode": "passthrough",
            "reason": "not_confident",
            "prompt": prompt,
            "files": [],
            "context_bytes": 0,
        }
    }
    proof = run.fidelity("C", observation, prompt, prompt, {})
    assert proof["valid"] and proof["mode"] == "passthrough"
    with pytest.raises(ValueError, match="Native stdin"):
        run.fidelity("C", observation, prompt, prompt + "leak", {})
    with pytest.raises(ValueError):
        run.fidelity("A", observation, prompt, prompt, {})


def test_budget_accounts_failures_unknowns_preflight_and_hard_attempt_limit():
    failed = {
        "attempted": True,
        "status": "failed",
        "api_price_equivalent": {"possible_write_price_upper_usd": 1},
    }
    assert run.budget_reason([failed], 0.1, bounds(), 0) is None
    assert "Unknown" in run.budget_reason([{"attempted": True}], 0, bounds(), 0)
    assert "admission budget" in run.budget_reason([failed], 18.9, bounds(), 0)
    assert "maximum" in run.budget_reason([failed] * 72, 0, bounds(), 0)
    assert "wall-time" in run.budget_reason([], 0, bounds(), 17900)
    assert "grader infrastructure" in run.budget_reason(
        [{**failed, "status": "execution_failed", "grader": {"infrastructure_error": "malformed"}}],
        0,
        bounds(),
        0,
    )
    assert "grader infrastructure" in run.budget_reason(
        [{**failed, "grader": {"timed_out": True}}], 0, bounds(), 0
    )


def test_failed_preflight_cannot_authorize_another_request():
    with pytest.raises(ValueError, match="preflight receipt"):
        run.validate_preflight(
            {
                "ready": False,
                "native_preflight_attempts": 1,
                "preflight_price_equivalent_upper_usd": None,
                "blocker": "network_policy_connect_403",
            }
        )


def test_blocked_preflight_records_every_unrun_slot_and_never_dispatches(tmp_path):
    fixtures, private_root = tmp_path / "fixtures", tmp_path / "private"
    repository = fixtures / "r01"
    repository.mkdir(parents=True)
    private_root.mkdir()
    (repository / "module.py").write_text("VALUE = 1\n")
    (repository / "LICENSE").write_text("Synthetic local test control\n")
    public_path, grading_path = tmp_path / "tasks.json", private_root / "grading.json"
    public_path.write_text(json.dumps([public()]))
    spec = private()
    spec["known_paths"] = ["module.py"]
    grader_script = private_root / "grader.py"
    grader_script.write_text("import json\nprint(json.dumps({'success':False,'checks':1}))\n")
    spec["grader"]["argv"] = [sys.executable, str(grader_script), "{worktree}", "{artifacts}"]
    grading_path.write_text(json.dumps({"n01": spec}))
    provenance = tmp_path / "provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "r01": {
                    "commit": "a" * 40,
                    "archive_sha256": "b" * 64,
                    "repository_url": "https://github.com/synthetic/control",
                    "archive_url": "https://codeload.github.com/synthetic/control/tar.gz/"
                    + "a" * 40,
                    "tracked_tree_status": "complete",
                    "exclusions": [],
                    "license_paths": ["LICENSE"],
                    "retained_file_sha256": run.offline.tree_hashes(repository),
                }
            }
        )
    )
    receipt = tmp_path / "preflight.json"
    receipt.write_text(
        json.dumps(
            {
                "ready": False,
                "native_preflight_attempts": 1,
                "preflight_price_equivalent_upper_usd": None,
                "blocker": "HTTP CONNECT 403; missing usage remains unknown",
            }
        )
    )
    marker, codex = tmp_path / "must-not-dispatch", tmp_path / "codex"
    codex.write_text(
        "#!"
        + sys.executable
        + "\nimport sys\nfrom pathlib import Path\nif sys.argv[1:]==['--version']: print('codex-cli 0.159.2')\nelse: Path("
        + repr(str(marker))
        + ").touch()\n"
    )
    codex.chmod(0o700)
    output = tmp_path / "study"
    args = [
        "--tasks",
        str(public_path),
        "--grading",
        str(grading_path),
        "--grader-root",
        str(private_root),
        "--fixtures",
        str(fixtures),
        "--provenance",
        str(provenance),
        "--pricing",
        str(run.ROOT / "benchmarks/cost-pricing.json"),
        "--output",
        str(output),
        "--codex",
        str(codex),
        "--preflight",
        str(receipt),
        "--execute",
    ]
    assert run.main(args) == 2
    report = run.load_json(output / "report.json")
    assert len(report["runs"]) == 6 and all(
        row["status"] == "not_run" and not row["attempted"] for row in report["runs"]
    )
    assert not marker.exists()
    assert report["metadata"]["preflight_receipt"]["preflight_price_equivalent_upper_usd"] is None
    assert "HTTP CONNECT 403" in report["metadata"]["stop_reason"]
    assert all(report["arms"][arm]["api_price_equivalent"]["total_usd"] is None for arm in run.ARMS)
    before = {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}
    assert run.main(args + ["--resume"]) == 0
    assert {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()} == before
    assert not marker.exists()


def fake_native(tmp_path, *, hang=False):
    script = tmp_path / "fake.py"
    script.write_text(
        "import json,sys,time\n"
        + (
            "time.sleep(30)\n"
            if hang
            else "print(json.dumps({'type':'thread.started','thread_id':'local-fake'}))\nprint(json.dumps({'type':'turn.started'}))\nprint(json.dumps({'type':'turn.completed','usage':{'input_tokens':12,'cached_input_tokens':4,'cache_write_input_tokens':0,'output_tokens':2}}))\n"
        )
    )
    return [sys.executable, str(script)]


def test_native_launch_has_durable_identity_grant_and_complete_fake_usage(tmp_path):
    artifacts, worktree, auth = tmp_path / "artifacts", tmp_path / "work", tmp_path / "binding"
    artifacts.mkdir()
    worktree.mkdir()
    auth.mkdir()
    (auth / "auth.json").write_text("never-read-control")
    command = fake_native(tmp_path)
    result = run.execute_codex(
        command, "public stdin", worktree, artifacts, 5, {**os.environ, "CODEX_HOME": str(auth)}
    )
    assert result["exit_code"] == 0 and not result["timed_out"]
    assert run.load_json(artifacts / "process-identity.json") == run.load_json(
        artifacts / "launch-grant.json"
    )
    assert (artifacts / "codex-state/auth.json").is_symlink()
    assert result["telemetry"]["usage"]["input_tokens"] == 12
    assert (artifacts / "prompt.txt").read_text() == "public stdin"


def test_timeout_stops_exact_native_process_group(tmp_path):
    artifacts, worktree = tmp_path / "artifacts", tmp_path / "work"
    artifacts.mkdir()
    worktree.mkdir()
    result = run.execute_codex(
        fake_native(tmp_path, hang=True), "public", worktree, artifacts, 0.15, dict(os.environ)
    )
    assert result["timed_out"] and result["wall_time_seconds"] < 6
    identity = run.load_json(artifacts / "process-identity.json")
    with pytest.raises(ProcessLookupError):
        os.kill(identity["pid"], 0)


def test_grader_runs_outside_worktree_and_requires_explicit_boolean(tmp_path):
    root = tmp_path / "work"
    root.mkdir()
    script = tmp_path / "grader.py"
    script.write_text(
        "import json,os\nprint(json.dumps({'success':True,'checks':2,'evidence':os.getcwd()}))\n"
    )
    grade = run.grade_external(
        {"argv": [sys.executable, str(script)], "timeout_seconds": 5},
        root,
        tmp_path / "grade",
        "n01",
    )
    assert grade["success"] and grade["checks"] == 2
    assert grade["evidence"] == str(tmp_path / "grade")


def test_git_metadata_config_and_staging_are_protected(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "source.py").write_text("VALUE = 1\n")
    run.legacy.git(root, "init")
    run.legacy.git(root, "add", ".")
    run.legacy.git(
        root,
        "-c",
        "user.name=Control",
        "-c",
        "user.email=control@example.invalid",
        "commit",
        "-m",
        "Control",
    )
    expected = run.git_metadata_snapshot(root)
    assert run.git_metadata_violations(root, expected) == []
    (root / "source.py").write_text("VALUE = 2\n")
    run.legacy.git(root, "add", ".")
    assert "Git index contains staged changes" in run.git_metadata_violations(root, expected)
    run.legacy.git(root, "config", "user.name", "Changed")
    assert any("configuration" in reason for reason in run.git_metadata_violations(root, expected))


def test_zero_check_grader_cannot_pass(tmp_path):
    root = tmp_path / "work"
    root.mkdir()
    script = tmp_path / "grader.py"
    script.write_text("import json\nprint(json.dumps({'success':True,'checks':0}))\n")
    grade = run.grade_external(
        {"argv": [sys.executable, str(script)], "timeout_seconds": 5},
        root,
        tmp_path / "grade",
        "n01",
    )
    assert grade["success"] is False and "positive executed-check" in grade["infrastructure_error"]


def test_parent_death_wrapper_prohibits_ungranted_late_launch(tmp_path):
    identity = tmp_path / "process-identity.json"
    marker = tmp_path / "must-not-exist"
    child = run.subprocess.Popen(
        [
            sys.executable,
            "-c",
            run.PROCESS_WRAPPER,
            str(identity),
            ".1",
            sys.executable,
            "-c",
            "from pathlib import Path; Path(" + repr(str(marker)) + ").touch()",
        ],
        start_new_session=True,
    )
    try:
        child.wait(timeout=3)
    finally:
        run.stop_group(child)
    assert child.returncode == 125 and not marker.exists()


@pytest.mark.parametrize(
    "mutation", ["duplicate-thread", "cumulative-totals", "rerouted-model", "zero-usage"]
)
def test_native_lifecycle_diagnostics_and_default_zero_usage_cannot_succeed(tmp_path, mutation):
    usage = {
        "input_tokens": 12,
        "cached_input_tokens": 4,
        "cache_write_input_tokens": 0,
        "output_tokens": 2,
    }
    events = [{"type": "thread.started", "thread_id": "fake"}, {"type": "turn.started"}]
    if mutation == "duplicate-thread":
        events.append({"type": "thread.started", "thread_id": "duplicate"})
    elif mutation == "rerouted-model":
        events.append(
            {
                "type": "item.completed",
                "item": {
                    "id": "diagnostic",
                    "type": "error",
                    "message": "model rerouted: gpt-6.1-sol -> another-model (capacity)",
                },
            }
        )
    elif mutation == "zero-usage":
        usage = {key: 0 for key in usage}
    events.append({"type": "turn.completed", "usage": usage})
    if mutation == "cumulative-totals":
        events.extend([{"type": "turn.started"}, {"type": "turn.completed", "usage": usage}])
    (tmp_path / "events.jsonl").write_text("\n".join(json.dumps(event) for event in events) + "\n")
    final = tmp_path / "final.json"
    final.write_text(json.dumps({"summary": "Fake structured result", "tests_run": []}))
    result = {
        "exit_code": 0,
        "timed_out": False,
        "interrupted": False,
        "telemetry": run.parse_codex_jsonl(tmp_path / "events.jsonl"),
        "event_stream_framing": run.common.native_event_framing(tmp_path / "events.jsonl"),
    }
    cost = run.cost_record(
        tmp_path, result, run.load_json(run.ROOT / "benchmarks/cost-pricing.json")
    )
    assert cost["native_reported_price_equivalent_usd"] is None
    assert run.strict_native_validity(result, final, cost["usage_evidence"])["valid"] is False
    if mutation == "zero-usage":
        assert cost["usage_evidence"]["observed_completed_turn_usage"]["input_tokens"] == 0


def test_c_query_is_exact_public_task_and_uses_strict_production_abi(tmp_path, monkeypatch):
    from memglide.integrations import auto_preload, codex_preload

    task = public()
    prompt, observed = run.task_prompt(task), {}
    request = tmp_path / "request.json"
    request.write_text(
        json.dumps(
            {
                "arm": "C",
                "prompt": prompt,
                "task_query": task["prompt"],
                "worktree": str(tmp_path),
                "settings": run.SETTINGS,
            }
        )
    )
    monkeypatch.setattr(
        run.common,
        "prepare_project",
        lambda *args: {"project_id": "test", "cpu_seconds": 0, "wall_seconds": 0},
    )
    monkeypatch.setattr(run.hardened, "git", lambda *args: "")

    def fake_prepare(value, **kwargs):
        observed.update(kwargs)
        return {
            "prompt": value,
            "mode": "passthrough",
            "reason": "control",
            "files": [],
            "context_bytes": 0,
        }

    def fake_validate(value, common_prompt, context_format, **kwargs):
        observed["validated_policy"] = kwargs["selection_policy"]
        assert value["prompt"] == common_prompt == prompt
        return prompt, {}

    monkeypatch.setattr(auto_preload, "prepare_task_prompt", fake_prepare)
    monkeypatch.setattr(codex_preload, "_validated_automatic_preparation", fake_validate)
    result = run.preparation_worker(request)
    assert observed["task_query"] == task["prompt"] and observed["task_query"] != prompt
    assert observed["selection_policy"] == observed["validated_policy"] == "v4"
    assert "known_paths" not in observed and result["dispatched_model_requests"] == 0


def test_native_fixture_git_ignores_external_filters_and_preserves_crlf(tmp_path, monkeypatch):
    fixtures = tmp_path / "fixtures"
    source = fixtures / "r01"
    source.mkdir(parents=True)
    (source / "module.py").write_bytes(b"VALUE = 1\r\n")
    (source / ".gitattributes").write_text("*.py filter=trap text eol=lf\n")
    marker, global_config = tmp_path / "must-not-run", tmp_path / "global-config"
    global_config.write_text(
        '[filter "trap"]\n clean = touch '
        + str(marker)
        + "; cat\n smudge = touch "
        + str(marker)
        + "; cat\n[core]\n autocrlf = true\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(global_config))
    output = tmp_path / "output"
    repositories = run.create_repositories(output, [public()], fixtures)
    repository = repositories["r01"]
    worktree = output / "worktrees" / "control"
    worktree.parent.mkdir(parents=True)
    run.hardened.git(
        Path(repository["path"]), "worktree", "add", "--detach", str(worktree), repository["commit"]
    )
    assert run.source_hashes(worktree) == run.offline.tree_hashes(source)
    run.verify_repositories(repositories)
    assert not marker.exists()


def test_grader_must_be_bound_to_private_root_and_formal_cohort_is_enforced(tmp_path):
    root, outside = tmp_path / "private", tmp_path / "outside.py"
    root.mkdir()
    outside.write_text("pass\n")
    spec = private()
    spec["grader"]["argv"] = [sys.executable, str(outside)]
    with pytest.raises(ValueError, match="frozen private root"):
        run.validate_grader_bindings({"n01": spec}, root)
    tasks = [public(index) for index in range(1, 13)]
    provenance = {
        f"r{index:02d}": {"repository_url": f"https://github.com/owner/repo{index}"}
        for index in range(1, 13)
    }
    assert run.formal_cohort(tasks, provenance, 2)
    assert not run.formal_cohort([{**task, "language": "python"} for task in tasks], provenance, 2)
    assert not run.formal_cohort(
        tasks, {key: {"repository_url": "https://github.com/one/root"} for key in provenance}, 2
    )


def test_parent_death_stops_native_and_term_ignoring_tool_descendant(tmp_path):
    identity, descendant = tmp_path / "process-identity.json", tmp_path / "descendant.pid"
    target, launcher = tmp_path / "target.py", tmp_path / "launcher.py"
    target.write_text(
        "import subprocess,sys,time\nfrom pathlib import Path\nchild=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'])\nPath("
        + repr(str(descendant))
        + ").write_text(str(child.pid))\ntime.sleep(30)\n"
    )
    launcher.write_text(
        "import json,subprocess,sys,time\nfrom pathlib import Path\nprocess=subprocess.Popen([sys.executable,'-c',"
        + repr(run.PROCESS_WRAPPER)
        + ","
        + repr(str(identity))
        + ",'5',sys.executable,"
        + repr(str(target))
        + "],start_new_session=True)\nrecord=Path("
        + repr(str(identity))
        + ")\nwhile not record.exists(): time.sleep(.01)\nrecord.with_name('launch-grant.json').write_text(record.read_text())\ntime.sleep(30)\n"
    )
    process = run.subprocess.Popen([sys.executable, str(launcher)])
    group = None
    try:
        deadline = time.monotonic() + 5
        while not descendant.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert descendant.exists()
        group = run.load_json(identity)["process_group"]
        child_pid = int(descendant.read_text())
        process.kill()
        process.wait(timeout=3)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                state = Path(f"/proc/{child_pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
            except FileNotFoundError:
                break
            if state == "Z":
                break
            time.sleep(0.01)
        else:
            pytest.fail("Native tool descendant survived launcher death")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)
        if group:
            try:
                os.killpg(group, signal.SIGKILL)
            except ProcessLookupError:
                pass
