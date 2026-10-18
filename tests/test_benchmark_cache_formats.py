"""Format experiment checks use fake local executables, never actual model calls."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_cache_formats as run  # noqa: E402
from memglide.integrations.preload import prepare_prompt  # noqa: E402


def task(identifier="format-task", *, supplied=False):
    return {
        "id": identifier,
        "language": "python",
        "repository": "desk-python-daily",
        "prompt": "Implement the named behavior.",
        "focus_paths": ["zeta.py", "alpha.py"],
        "context_supplied": supplied,
    }


def test_twenty_pairs_are_exactly_order_balanced_and_each_format_runs_every_task():
    tasks = [task(str(index), supplied=index % 5 == 0) for index in range(20)]
    plan = run.make_plan(tasks, 318)
    assert len(plan) == len({row["run_id"] for row in plan}) == 40
    assert sum(row["configuration"] == "A" for row in plan[::2]) == 10
    assert sum(row["configuration"] == "B" for row in plan[::2]) == 10
    assert sum(row["selection_stratum"] == "caller_context_supplied" for row in plan) == 8
    for item in tasks:
        rows = [row for row in plan if row["task_id"] == item["id"]]
        assert {row["context_format"] for row in rows} == {"legacy", "compact-prefix"}
        assert len(rows) == 2 and all(row["repeat"] == 1 for row in rows)
    assert plan == run.make_plan(tasks, 318)


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


def proof(delivery, arm, *, supplied=False):
    worktree, artifacts, setup, repository = delivery
    item = task(supplied=supplied)
    prompt = run.common.task_prompt(item)
    context_format = run.FORMATS[arm]
    value = prepare_prompt(
        prompt,
        project_id=setup["project_id"],
        db_path=artifacts / "memglide.db",
        focus_paths=item["focus_paths"],
        context_supplied=supplied,
        context_format=context_format,
    )
    metadata = {
        key: value[key]
        for key in (
            "mode",
            "reason",
            "task_prompt_sha256",
            "prepared_prompt_sha256",
            "files",
            "context_bytes",
            "preparation_wall_seconds",
            "preparation_cpu_seconds",
        )
    }
    if context_format == "compact-prefix":
        metadata.update(context_format=context_format, prompt_layout=value["prompt_layout"])
    native = run.common.codex_command(
        "/native/codex", worktree, artifacts / "s", artifacts / "f", "same", "low"
    )
    report = {
        "version": 1 if arm == "A" else 2,
        "preparation": metadata,
        "executable": native[0],
        "exec_argv": [*native[:-1], "--", "-"],
        "native_stdin": {
            "sha256": run.common.digest(value["prompt"].encode()),
            "bytes": len(value["prompt"].encode()),
            "transport": "temporary_file_descriptor",
        },
    }
    path = artifacts / "preparation.json"
    path.write_text(json.dumps(report))
    row = {
        "configuration": arm,
        "artifacts": str(artifacts),
        "native_command": native,
        "telemetry": {"mcp_counts_complete": True, "mcp_call_count": 0},
    }
    return item, prompt, row, report, path, repository


@pytest.mark.parametrize("arm", ["A", "B"])
def test_independent_git_reconstruction_matches_actual_preparer_exact_utf8_bytes(delivery, arm):
    item, prompt, row, _, _, repository = proof(delivery, arm)
    result = run.format_fidelity(row, item, prompt, repository)
    assert result["valid"] is True and result["mode"] == "preloaded"
    assert result["source_file_count"] == 2 and result["context_format"] == run.FORMATS[arm]


@pytest.mark.parametrize("arm", ["A", "B"])
def test_both_formats_forward_identical_task_on_supplied_context(delivery, arm):
    item, prompt, row, _, _, repository = proof(delivery, arm, supplied=True)
    result = run.format_fidelity(row, item, prompt, repository)
    assert result["valid"] is True and result["mode"] == "passthrough"
    assert result["actual_model_prompt_sha256"] == run.common.digest(prompt.encode())
    assert result["context_bytes"] == 0


@pytest.mark.parametrize(
    "mutation",
    [
        "source-hash",
        "omit-helper",
        "wrong-prompt",
        "wrong-version",
        "wrong-bytes",
        "native-settings",
        "mcp",
    ],
)
@pytest.mark.parametrize("arm", ["A", "B"])
def test_private_metadata_cannot_replace_complete_matching_delivery(delivery, arm, mutation):
    item, prompt, row, report, path, repository = proof(delivery, arm)
    if mutation == "source-hash":
        report["preparation"]["files"][0]["sha256"] = "a" * 64
    elif mutation == "omit-helper":
        report["preparation"]["files"].pop()
    elif mutation == "wrong-prompt":
        report["native_stdin"]["sha256"] = report["preparation"]["prepared_prompt_sha256"] = (
            "b" * 64
        )
    elif mutation == "wrong-version":
        report["version"] = 2 if arm == "A" else 1
    elif mutation == "wrong-bytes":
        report["native_stdin"]["bytes"] += 1
    elif mutation == "native-settings":
        report["exec_argv"][report["exec_argv"].index("--model") + 1] = "different-model"
    else:
        row["telemetry"]["mcp_call_count"] = 1
    path.write_text(json.dumps(report))
    assert run.format_fidelity(row, item, prompt, repository)["valid"] is False


def test_new_runner_guard_freezes_transitive_helpers_without_modifying_old_runner(tmp_path):
    path = run.ROOT / "benchmarks/tasks_daily.json"
    tasks = run.load_tasks(path, "daily")[:1]
    frozen = run.frozen_manifest(path, tasks, {"corpus": "daily"})
    expected = {
        "benchmarks/run_cache_formats.py",
        "benchmarks/run_daily.py",
        "benchmarks/run_v2.py",
        "benchmarks/run.py",
        "benchmarks/telemetry.py",
        "benchmarks/corpus.py",
        "benchmarks/corpus_daily.py",
        "benchmarks/compare_components.py",
    }
    assert expected <= set(frozen["files"])
    assert sum(name.startswith("src/memglide/") for name in frozen["files"]) >= 24
    changed = copy.deepcopy(frozen)
    changed["files"]["benchmarks/run_cache_formats.py"] = "different"
    with pytest.raises(ValueError, match="changed"):
        run.durable.validate_frozen({"frozen_manifest": frozen}, changed)


def test_formats_keep_same_native_flags_and_explicit_format_assignment(tmp_path):
    native = run.common.codex_command(
        "/native/codex", tmp_path, tmp_path / "s", tmp_path / "f", "same", "low"
    )
    for context_format in run.FORMATS.values():
        command = run.preload_command(native, tmp_path, task(), context_format, "approved")
        assert command[command.index("--context-format") + 1] == context_format
        assert command[command.index("--") + 1 :] == native[2:-1]
        assert command[command.index("--max-context-bytes") + 1] == "12000"


def test_fake_native_end_to_end_uses_two_formats_and_retains_independent_failures(
    tmp_path, monkeypatch
):
    executable = tmp_path / "fake-native"
    events = [
        {"type": "thread.started", "thread_id": "fake-local"},
        {"type": "turn.started"},
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 2},
        },
    ]
    stream = "\n".join(json.dumps(event) for event in events) + "\n"
    executable.write_text(
        "#!" + sys.executable + "\nimport sys,json\nfrom pathlib import Path\n"
        "if '--version' in sys.argv:\n print('fake-native-unit-test');sys.exit(0)\n"
        "sys.stdin.buffer.read()\nPath(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(json.dumps({'summary':'Local fake only','tests_run':[]}))\n"
        "print(" + repr(stream) + ",end='')\n"
    )
    executable.chmod(0o700)
    monkeypatch.setattr(run, "frozen_manifest", lambda *_: {"unit_test": "fixed"})
    output = tmp_path / "experiment"
    args = [
        "--output",
        str(output),
        "--corpus",
        "daily",
        "--limit",
        "1",
        "--codex",
        str(executable),
        "--codex-home",
        str(tmp_path / "no-auth"),
    ]
    assert run.main(args) == 0
    report = json.loads((output / "report.json").read_text())
    assert report["comparison_kind"].startswith("Development")
    assert report["configuration_labels"] == run.LABELS
    assert len(report["runs"]) == 2 and report["paired_comparison"]["valid_pairs"] == 1
    assert {row["preload_treatment_fidelity"]["context_format"] for row in report["runs"]} == set(
        run.FORMATS.values()
    )
    assert all(
        row["status"] == "failed" and row["grader"]["success"] is False for row in report["runs"]
    )
    assert all(
        row["setup"]["wall_seconds"] > 0 and row["native_execution_validity"]["valid"]
        for row in report["runs"]
    )
    assert all(
        row["metrics"]["actual_cost_usd"] is None and row["metrics"]["model_calls"] is None
        for row in report["runs"]
    )
    retained = (output / "report.json").read_bytes()
    assert run.main([*args, "--resume"]) == 0
    assert (output / "report.json").read_bytes() == retained
    assert "Neither arm is standard Codex" in (output / "report.md").read_text()


def test_only_one_primary_repeat_is_supported(tmp_path):
    with pytest.raises(SystemExit):
        run.main(["--output", str(tmp_path / "new"), "--repeats", "2"])


@pytest.mark.parametrize("blocker", ["source", "authentication"])
def test_shared_blocker_stops_new_requests_and_retains_unrun_assignments(
    tmp_path, monkeypatch, blocker
):
    marker = tmp_path / "native-invocations"
    executable = tmp_path / "fake-native"
    executable.write_text(
        "#!" + sys.executable + "\nimport sys,json\nfrom pathlib import Path\n"
        "if '--version' in sys.argv:\n print('fake-native-unit-test');sys.exit(0)\n"
        "sys.stdin.buffer.read()\n"
        "marker=Path("
        + repr(str(marker))
        + ")\nmarker.write_text(str(int(marker.read_text())+1) if marker.exists() else '1')\n"
        + (
            "print('401 Unauthorized: local fake rejection',file=sys.stderr)\nsys.exit(1)\n"
            if blocker == "authentication"
            else "Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(json.dumps({'summary':'Local fake','tests_run':[]}))\n"
            "print(json.dumps({'type':'thread.started','thread_id':'fake'}))\nprint(json.dumps({'type':'turn.started'}))\n"
            "print(json.dumps({'type':'turn.completed','usage':{'input_tokens':12,'cached_input_tokens':4,'output_tokens':2}}))\n"
        )
    )
    executable.chmod(0o700)
    if blocker == "source":
        monkeypatch.setattr(
            run,
            "frozen_manifest",
            lambda *_: {"unit_test_source": "changed" if marker.exists() else "original"},
        )
    else:
        monkeypatch.setattr(run, "frozen_manifest", lambda *_: {"unit_test_source": "fixed"})
    output = tmp_path / "experiment"
    args = [
        "--output",
        str(output),
        "--corpus",
        "daily",
        "--limit",
        "2",
        "--codex",
        str(executable),
        "--codex-home",
        str(tmp_path / "no-auth"),
    ]
    assert run.main(args) == 2
    assert marker.read_text() == "1"
    report = json.loads((output / "report.json").read_text())
    assert len(report["runs"]) == 4
    assert sum(row["attempted"] for row in report["runs"]) == 1
    assert sum(row["status"] == "not_run" for row in report["runs"]) == 3
    assert report["metadata"]["shared_blocker"]
    assert sum(summary["successful_runs"] for summary in report["configurations"].values()) == 0
    if blocker == "source":
        assert report["metadata"]["source_guard_failure"]
        assert report["paired_comparison"]["valid_pairs"] == 0


def test_fresh_corpus_defaults_route_twenty_new_tasks_to_balanced_format_pairs():
    path = run.ROOT / "benchmarks/tasks_cache.json"
    tasks = run.load_tasks(path, "cache")
    assert len(tasks) == 20
    assert sum(item["language"] == "python" for item in tasks) == 10
    assert len({item["repository"] for item in tasks}) == 4
    assert sum(item["context_supplied"] for item in tasks) == 4
    assert all(not item["repository"].endswith("daily") for item in tasks)
    plan = run.make_plan(tasks, 20261018)
    assert len(plan) == 40 and sum(row["configuration"] == "A" for row in plan[::2]) == 10
    for item in tasks:
        common_prompt = run.common.task_prompt(item)
        assert all(path in common_prompt for path in item["focus_paths"])
    arguments = run.parser().parse_args(["--output", "/tmp/never-executed-unit-test"])
    assert arguments.corpus == "cache" and arguments.repeats == 1


def test_fresh_corpus_and_transitive_grader_are_frozen_and_report_is_labelled(tmp_path):
    path = run.ROOT / "benchmarks/tasks_cache.json"
    tasks = run.load_tasks(path, "cache")
    frozen = run.frozen_manifest(path, tasks, {"corpus": "cache"})
    assert {
        "benchmarks/corpus_cache.py",
        "benchmarks/corpus.py",
        "benchmarks/tasks_cache.json",
    } <= set(frozen["files"])
    report = run.build_report([], tasks, {"corpus": "cache"})
    run.write_report(report, tmp_path)
    written = json.loads((tmp_path / "report.json").read_text())
    assert written["configuration_labels"] == {
        "A": "Memglide legacy",
        "B": "Memglide compact-prefix",
    }
    assert written["comparison_kind"] == "Fresh twenty-task format comparison"
    assert "Neither arm is standard Codex" in (tmp_path / "report.md").read_text()


@pytest.mark.parametrize("arm", ["A", "B"])
@pytest.mark.parametrize("supplied", [False, True])
def test_actual_orphan_recovery_keeps_both_formats_setup_and_fidelity_unknown(
    tmp_path, arm, supplied
):
    import subprocess
    import time

    item = task(supplied=supplied)
    plan = run.make_plan([item], 19)
    row = next(row for row in plan if row["configuration"] == arm)
    state = {
        "originals": {assignment["run_id"]: run.durable.pending(assignment) for assignment in plan},
        "supplemental": [],
    }
    metadata = {"resume_count": 0}
    run.common.atomic_json(tmp_path / "plan.json", {"tasks": [item], "runs": plan}, immutable=True)
    attempt = run.begin_format_attempt(tmp_path, row, item, state, metadata)
    artifacts = Path(attempt["artifacts"])
    start = json.loads((artifacts / "attempt-start.json").read_text())
    expected_setup = {
        "wall_seconds": 0 if supplied else None,
        "cpu_seconds": 0 if supplied else None,
    }
    assert start["setup"] == expected_setup
    assert start["preload_treatment_fidelity"]["valid"] is None
    # A real live private process group survives an uncompleted launcher state.
    # Even a terminal-looking usage stream cannot establish its completed outcome.
    stream = "\n".join(
        json.dumps(event)
        for event in [
            {"type": "thread.started", "thread_id": "orphan-local-only"},
            {"type": "turn.started"},
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 12, "cached_input_tokens": 4, "output_tokens": 2},
            },
        ]
    )
    program = "import time;print(" + repr(stream) + ",flush=True);time.sleep(30)"
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
                program,
            ],
            stdout=stdout,
            stderr=stderr,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + 5
            identity_path = artifacts / "process-identity.json"
            while not identity_path.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            identity = json.loads(identity_path.read_text())
            run.common.atomic_json(artifacts / "launch-grant.json", identity, immutable=True)
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
    assert measured["approval_index_wall_seconds"] == (0 if supplied else None)
    assert measured["approval_index_cpu_seconds"] == (0 if supplied else None)
    assert measured["total_observed_local_cpu_seconds"] is None
    assert not state["originals"][row["run_id"]].get("pending")
    run.common.validate_saved_state(tmp_path, [item], plan, state)


def test_format_report_limits_describe_both_preloading_arms_and_distinct_focus_sets():
    report = run.build_report([], [], {"corpus": "cache"})
    joined = "\n".join(report["limitations"])
    assert "including B skips" not in joined
    assert "when B preloads source" not in joined
    assert "hidden oracle chooses B paths" not in joined
    assert "either format" in joined
    assert "distinct source-focus sets" in joined
    assert "does not directly test cross-task prefix reuse" in joined
