"""Cost-study runner checks use local fakes, never live model requests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_cost as run  # noqa: E402
from memglide.integrations.preload import prepare_prompt  # noqa: E402


def task(identifier="cost-task", *, supplied=False):
    return {
        "id": identifier,
        "language": "python",
        "repository": "unit-test-only",
        "prompt": "Implement the named behavior.",
        "focus_paths": ["zeta.py", "alpha.py"],
        "context_supplied": supplied,
    }


@pytest.fixture
def delivery(tmp_path):
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    (worktree / "zeta.py").write_text("def zeta():\n    return '雪'\n")
    (worktree / "alpha.py").write_text("def alpha():\n    return 1\n")
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
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    setup = run.common.prepare_project(worktree, artifacts)
    repository = {"path": str(worktree), "commit": run.legacy.git(worktree, "rev-parse", "HEAD")}
    return worktree, artifacts, setup, repository


def compact_proof(delivery, *, supplied=False):
    worktree, artifacts, setup, repository = delivery
    item = task(supplied=supplied)
    prompt = run.common.task_prompt(item)
    prepared = prepare_prompt(
        prompt,
        project_id=setup["project_id"],
        db_path=artifacts / "memglide.db",
        focus_paths=item["focus_paths"],
        context_supplied=supplied,
        context_format="compact-prefix",
    )
    keys = (
        "mode",
        "reason",
        "task_prompt_sha256",
        "prepared_prompt_sha256",
        "files",
        "context_bytes",
        "preparation_wall_seconds",
        "preparation_cpu_seconds",
        "context_format",
        "prompt_layout",
    )
    native = run.codex_command(
        "/native/codex", worktree, artifacts / "s", artifacts / "f", "same", "low"
    )
    report = {
        "version": 2,
        "preparation": {key: prepared[key] for key in keys},
        "executable": native[0],
        "exec_argv": [*native[:-1], "--", "-"],
        "native_stdin": {
            "sha256": run.common.digest(prepared["prompt"].encode()),
            "bytes": len(prepared["prompt"].encode()),
            "transport": "temporary_file_descriptor",
        },
    }
    path = artifacts / "preparation.json"
    path.write_text(json.dumps(report))
    row = {
        "configuration": "B",
        "artifacts": str(artifacts),
        "native_command": native,
        "telemetry": {"mcp_counts_complete": True, "mcp_call_count": 0},
    }
    return item, prompt, row, report, path, repository


def test_ten_pairs_use_distinct_assignments_exactly_balanced_order_and_explicit_treatment():
    tasks = [task(str(index), supplied=index % 5 == 0) for index in range(10)]
    plan = run.make_plan(tasks, 20261018)
    assert len(plan) == len({row["run_id"] for row in plan}) == 20
    assert sum(row["configuration"] == "A" for row in plan[::2]) == 5
    assert sum(row["configuration"] == "B" for row in plan[::2]) == 5
    assert sum(row["selection_stratum"] == "caller_context_supplied" for row in plan) == 4
    for item in tasks:
        rows = [row for row in plan if row["task_id"] == item["id"]]
        assert {row["configuration"]: row["context_format"] for row in rows} == {
            "A": None,
            "B": "compact-prefix",
        }
        assert len(rows) == 2 and all(row["repeat"] == 1 for row in rows)
    assert plan == run.make_plan(tasks, 20261018)


@pytest.mark.parametrize("supplied", [False, True])
def test_compact_delivery_matches_independent_full_git_bytes_and_bypasses_exactly(
    delivery, supplied
):
    item, prompt, row, _, _, repository = compact_proof(delivery, supplied=supplied)
    result = run.treatment_fidelity(row, item, prompt, repository)
    assert result["valid"] is True
    assert result["mode"] == ("passthrough" if supplied else "preloaded")
    assert result["source_file_count"] == (0 if supplied else 2)
    assert result["context_format"] == "compact-prefix"
    if supplied:
        assert result["actual_model_prompt_sha256"] == run.common.digest(prompt.encode())
        assert result["context_bytes"] == 0


@pytest.mark.parametrize(
    "mutation", ["hash", "helper", "prompt", "version", "bytes", "flags", "mcp"]
)
def test_compact_assignment_rejects_missing_source_or_forged_delivery(delivery, mutation):
    item, prompt, row, report, path, repository = compact_proof(delivery)
    if mutation == "hash":
        report["preparation"]["files"][0]["sha256"] = "a" * 64
    elif mutation == "helper":
        report["preparation"]["files"].pop()
    elif mutation == "prompt":
        report["preparation"]["prepared_prompt_sha256"] = report["native_stdin"]["sha256"] = (
            "b" * 64
        )
    elif mutation == "version":
        report["version"] = 1
    elif mutation == "bytes":
        report["native_stdin"]["bytes"] += 1
    elif mutation == "flags":
        report["exec_argv"][report["exec_argv"].index("--model") + 1] = "different"
    else:
        row["telemetry"]["mcp_call_count"] = 1
    path.write_text(json.dumps(report))
    assert run.treatment_fidelity(row, item, prompt, repository)["valid"] is False


@pytest.mark.parametrize("mutation", [None, "command", "prompt", "prep", "database", "mcp"])
def test_standard_cannot_accidentally_receive_memglide_augmentation(tmp_path, mutation):
    item = task()
    prompt = run.common.task_prompt(item)
    native = run.codex_command(
        "/native/codex", tmp_path, tmp_path / "s", tmp_path / "f", "same", "low"
    )
    (tmp_path / "command.json").write_text(json.dumps(native))
    (tmp_path / "prompt.txt").write_text(prompt)
    row = {
        "configuration": "A",
        "artifacts": str(tmp_path),
        "native_command": native,
        "telemetry": {"mcp_counts_complete": True, "mcp_call_count": 0},
    }
    if mutation == "command":
        (tmp_path / "command.json").write_text(json.dumps(["wrapper", *native]))
    elif mutation == "prompt":
        (tmp_path / "prompt.txt").write_text(prompt + "extra source")
    elif mutation == "prep":
        (tmp_path / "preparation.json").write_text("{}")
    elif mutation == "database":
        (tmp_path / "memglide.db").touch()
    elif mutation == "mcp":
        row["telemetry"]["mcp_call_count"] = 1
    proof = run.treatment_fidelity(row, item, prompt, {})
    assert proof["valid"] is (mutation is None)
    assert proof["context_format"] is None and proof["source_file_count"] == 0
    assert proof["actual_model_prompt_sha256"] == run.common.digest(prompt.encode())


def test_both_arms_freeze_same_native_standard_tier_and_b_explicitly_selects_compact(tmp_path):
    native = run.codex_command(
        "/native/codex", tmp_path, tmp_path / "s", tmp_path / "f", "same", "low"
    )
    assert native[-3:] == ["-c", 'service_tier="default"', "-"]
    wrapped = run.formats.preload_command(native, tmp_path, task(), "compact-prefix", "approved")
    assert wrapped[wrapped.index("--context-format") + 1] == "compact-prefix"
    assert wrapped[wrapped.index("--") + 1 :] == native[2:-1]
    assert wrapped[wrapped.index("--max-context-bytes") + 1] == "12000"


def test_frozen_manifest_includes_new_and_transitive_sources_and_detects_drift():
    path = run.ROOT / "benchmarks/tasks_cost.json"
    tasks = run.load_tasks(path)
    frozen = run.frozen_manifest(path, tasks, {"corpus": "cost"})
    assert {
        "benchmarks/run_cost.py",
        "benchmarks/run_cache_formats.py",
        "benchmarks/run_daily.py",
        "benchmarks/run_v2.py",
        "benchmarks/run.py",
        "benchmarks/telemetry.py",
        "benchmarks/corpus.py",
        "benchmarks/corpus_cost.py",
        "benchmarks/tasks_cost.json",
        "benchmarks/reporting.py",
        "benchmarks/compare_components.py",
        "pyproject.toml",
        "uv.lock",
    } <= set(frozen["files"])
    assert sum(name.startswith("src/memglide/") for name in frozen["files"]) >= 24
    changed = copy.deepcopy(frozen)
    changed["files"]["benchmarks/run_cost.py"] = "different"
    with pytest.raises(ValueError, match="changed"):
        run.durable.validate_frozen({"frozen_manifest": frozen}, changed)


def fake_native(path, *, reject=False):
    events = [
        {"type": "thread.started", "thread_id": "local-fake"},
        {"type": "turn.started"},
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 12,
                "cached_input_tokens": 4,
                "output_tokens": 2,
                "cache_write_input_tokens": 0,
                "reasoning_output_tokens": 1,
            },
        },
    ]
    program = (
        "#!" + sys.executable + "\nimport sys,json\nfrom pathlib import Path\n"
        "if '--version' in sys.argv:\n print('fake-native-unit-test');sys.exit(0)\n"
        "stdin=sys.stdin.buffer.read()\n"
        "Path(sys.argv[sys.argv.index('--output-last-message')+1]).with_name('actual-stdin.txt').write_bytes(stdin)\n"
    )
    if reject:
        program += "print('401 Unauthorized: local fake rejection',file=sys.stderr)\nsys.exit(1)\n"
    else:
        program += (
            "Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(json.dumps({'summary':'Local fake only','tests_run':[]}))\n"
            + "print("
            + repr("\n".join(json.dumps(event) for event in events) + "\n")
            + ",end='')\n"
        )
    path.write_text(program)
    path.chmod(0o700)


def test_fake_native_full_runner_executes_direct_a_and_compact_b_retains_failed_grades(
    tmp_path, monkeypatch
):
    executable = tmp_path / "fake-native"
    fake_native(executable)
    monkeypatch.setattr(run, "frozen_manifest", lambda *_: {"unit_test": "fixed"})
    output = tmp_path / "experiment"
    args = [
        "--output",
        str(output),
        "--limit",
        "1",
        "--model",
        "same",
        "--codex",
        str(executable),
        "--codex-home",
        str(tmp_path / "no-auth"),
    ]
    assert run.main(args) == 0
    report = json.loads((output / "report.json").read_text())
    assert report["configuration_labels"] == run.LABELS
    assert len(report["runs"]) == 2 and report["paired_comparison"]["valid_pairs"] == 1
    for row in report["runs"]:
        artifacts = Path(row["artifacts"])
        actual = (artifacts / "actual-stdin.txt").read_bytes()
        assert run.common.digest(actual) == row["actual_model_prompt_sha256"]
        assert row["status"] == "failed" and row["grader"]["success"] is False
        assert row["native_execution_validity"]["valid"] is True
        assert (
            row["metrics"]["actual_cost_usd"] is None
            and row["metrics"]["computed_cost_usd"] is None
        )
        if row["configuration"] == "A":
            assert actual == (artifacts / "prompt.txt").read_bytes()
            assert row["setup"] == {"wall_seconds": 0, "cpu_seconds": 0}
            assert json.loads((artifacts / "command.json").read_text()) == row["native_command"]
            assert not (artifacts / "memglide.db").exists()
        else:
            assert actual.endswith((artifacts / "prompt.txt").read_bytes())
            assert row["preload_treatment_fidelity"]["context_format"] == "compact-prefix"
            assert row["setup"]["wall_seconds"] > 0
    retained = (output / "report.json").read_bytes()
    assert run.main([*args, "--resume"]) == 0
    assert (output / "report.json").read_bytes() == retained


@pytest.mark.parametrize("blocker", ["source", "authentication"])
def test_shared_blockers_stop_future_requests_and_keep_all_original_assignments(
    tmp_path, monkeypatch, blocker
):
    executable = tmp_path / "fake-native"
    fake_native(executable, reject=blocker == "authentication")
    output = tmp_path / "experiment"
    monkeypatch.setattr(
        run,
        "frozen_manifest",
        lambda *_: {
            "source": "changed" if blocker == "source" and (output / "runs").exists() else "fixed"
        },
    )
    assert (
        run.main(
            [
                "--output",
                str(output),
                "--limit",
                "2",
                "--model",
                "same",
                "--codex",
                str(executable),
                "--codex-home",
                str(tmp_path / "no-auth"),
            ]
        )
        == 2
    )
    report = json.loads((output / "report.json").read_text())
    assert len(report["runs"]) == 4
    assert sum(row["attempted"] for row in report["runs"]) == 1
    assert sum(row["status"] == "not_run" for row in report["runs"]) == 3
    assert report["metadata"]["shared_blocker"]
    if blocker == "source":
        assert report["paired_comparison"]["valid_pairs"] == 0


@pytest.mark.parametrize("arm", ["A", "B"])
@pytest.mark.parametrize("supplied", [False, True])
def test_actual_orphan_recovery_preserves_unknown_b_indexing_and_completed_tail_is_not_actual_usage(
    tmp_path, arm, supplied
):
    item = task(supplied=supplied)
    plan = run.make_plan([item], 19)
    row = next(row for row in plan if row["configuration"] == arm)
    state = {
        "originals": {assignment["run_id"]: run.durable.pending(assignment) for assignment in plan},
        "supplemental": [],
    }
    metadata = {"resume_count": 0}
    run.common.atomic_json(tmp_path / "plan.json", {"tasks": [item], "runs": plan}, immutable=True)
    attempt = run.begin_attempt(tmp_path, row, item, state, metadata)
    artifacts = Path(attempt["artifacts"])
    expected_setup = {
        "wall_seconds": 0 if arm == "A" or supplied else None,
        "cpu_seconds": 0 if arm == "A" or supplied else None,
    }
    assert json.loads((artifacts / "attempt-start.json").read_text())["setup"] == expected_setup
    stream = "\n".join(
        json.dumps(event)
        for event in [
            {"type": "thread.started", "thread_id": "local-orphan"},
            {"type": "turn.started"},
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 2},
            },
        ]
    )
    with (
        (artifacts / "events.jsonl").open("w") as stdout,
        (artifacts / "stderr.log").open("w") as stderr,
    ):
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                run.durable.PROCESS_WRAPPER,
                str(artifacts / "process-identity.json"),
                "5",
                sys.executable,
                "-c",
                "import time;print(" + repr(stream) + ",flush=True);time.sleep(30)",
            ],
            stdout=stdout,
            stderr=stderr,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + 5
            identity = artifacts / "process-identity.json"
            while not identity.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            run.common.atomic_json(
                artifacts / "launch-grant.json", json.loads(identity.read_text()), immutable=True
            )
            while (
                "turn.completed" not in (artifacts / "events.jsonl").read_text()
                and time.monotonic() < deadline
            ):
                time.sleep(0.01)
            assert process.poll() is None
            run.common.validate_saved_state(tmp_path, [item], plan, state)
            run.common.recover_interrupted(tmp_path, state, metadata)
            process.wait(timeout=5)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
    result = json.loads((artifacts / "result.json").read_text())
    assert result["status"] == "interrupted" and result["execution_outcome_unknown"] is True
    assert result["setup"] == expected_setup
    assert result["preload_treatment_fidelity"]["valid"] is None
    assert result["native_execution_validity"]["valid"] is None
    assert result["telemetry"]["usage"]["input_tokens"] is None
    assert result["telemetry"]["observed_completed_turn_usage"]["input_tokens"] == 12
    measured = run.common.metrics(result)
    assert measured["approval_index_wall_seconds"] == expected_setup["wall_seconds"]
    assert measured["total_observed_local_cpu_seconds"] is None
    run.common.validate_saved_state(tmp_path, [item], plan, state)


def test_cost_report_is_explicitly_standard_vs_compact_with_unknown_raw_costs(tmp_path):
    report = run.build_report([], [], {})
    run.write_report(report, tmp_path)
    assert report["configuration_labels"] == run.LABELS
    text = (tmp_path / "report.md").read_text()
    assert "standard Codex (A) / compact-prefix Memglide (B)" in text
    assert "Neither arm is standard Codex" not in text
    assert "price-equivalent" in text
    assert "Unknown usage cannot be costed as zero" in text


def test_ten_task_corpus_is_default_and_cli_does_not_silently_pick_model(tmp_path):
    tasks = run.load_tasks(run.ROOT / "benchmarks/tasks_cost.json")
    assert len(tasks) == 10 and sum(task["language"] == "python" for task in tasks) == 5
    assert sum(task["context_supplied"] for task in tasks) == 2
    with pytest.raises(SystemExit):
        run.parser().parse_args(["--output", str(tmp_path / "never-executed")])
    with pytest.raises(SystemExit):
        run.parser().parse_args(
            ["--output", str(tmp_path / "never-executed"), "--model", "same", "--repeats", "2"]
        )
