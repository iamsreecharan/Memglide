"""Local-only warm benchmark checks: no authenticated/model requests."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import corpus_warm as corpus  # noqa: E402
from benchmarks import run_warm as run  # noqa: E402
from memglide.integrations.memory_preload import prepare_memory_prompt  # noqa: E402
from memglide.service import Service  # noqa: E402
from memglide.storage.database import DomainError  # noqa: E402


def events():
    return [
        {"type": "thread.started", "thread_id": "local-fake"},
        {"type": "turn.started"},
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 100,
                "cached_input_tokens": 40,
                "output_tokens": 10,
                "cache_write_input_tokens": 0,
                "reasoning_output_tokens": 0,
            },
        },
    ]


@pytest.fixture
def source_project(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    task = corpus.sequences()[0]["tasks"][0]
    corpus.build_stage(task["sequence_id"], 1, root)
    run.legacy.git(root, "init")
    run.legacy.git(root, "add", ".")
    run.legacy.git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Fixture",
    )
    service = Service(tmp_path / "memory.db")
    project = service.indexer.add_project(str(root))
    session = service.memory.start_session(project["id"], "Local-only test")
    quote = next(
        line for line in (root / task["memory_paths"][0]).read_text().splitlines() if line.strip()
    )
    final = tmp_path / "final.json"
    final.write_text(
        json.dumps(
            {
                "summary": "Local fixture",
                "findings": [{"path": task["memory_paths"][0], "quote": quote}],
            }
        )
    )
    yield root, service, project, session, task, final
    service.close()


def test_plan_is_complete_order_balanced_and_groups_stage_dependencies():
    sequences = corpus.sequences()
    plan = run.make_plan(sequences, 2, 731)
    assert len(plan) == 216
    assert len({row["run_id"] for row in plan}) == 216
    assert Counter(row["configuration"] for row in plan) == {"A": 72, "B": 72, "C": 72}
    orders = Counter()
    for repeat in (1, 2):
        for language in ("python", "typescript"):
            subset = [
                row for row in plan if row["repeat"] == repeat and row["language"] == language
            ]
            per_sequence = {}
            for row in subset:
                if row["stage"] == 1:
                    per_sequence.setdefault(row["sequence_id"], []).append(row["configuration"])
            assert len(set(tuple(value) for value in per_sequence.values())) == 6
            orders.update("".join(value) for value in per_sequence.values())
    assert set(orders.values()) == {4}
    for index in range(0, len(plan), 3):
        assert [row["stage"] for row in plan[index : index + 3]] == [1, 2, 3]
        assert len({row["group_id"] for row in plan[index : index + 3]}) == 1
    for sequence in sequences:
        one = [
            row["configuration"]
            for row in plan
            if row["sequence_id"] == sequence["id"] and row["repeat"] == 1 and row["stage"] == 1
        ]
        two = [
            row["configuration"]
            for row in plan
            if row["sequence_id"] == sequence["id"] and row["repeat"] == 2 and row["stage"] == 1
        ]
        assert two == one[::-1]


@pytest.mark.parametrize(
    "bad",
    [
        None,
        {},
        {"summary": "x", "findings": [{}]},
        {"summary": "x", "findings": [{"path": "a", "quote": ""}]},
        {"summary": "x", "findings": [{"path": "a", "quote": "x" * 501}]},
        {"summary": "x", "findings": [], "extra": 1},
    ],
)
def test_rejects_bad_findings_schema(bad):
    assert not run.validate_findings(bad)


def test_capture_is_exact_source_supported_and_has_no_grader_argument(source_project):
    root, service, _, session, task, final = source_project
    receipt = run.capture_findings(service, session["id"], task, final, "origin-one")
    assert len(receipt["accepted"]) == 1
    assert not receipt["rejected"]
    import inspect

    assert "grade" not in inspect.signature(run.capture_findings).parameters
    memory = service.memory.get_memory_snapshot(session["id"], receipt["accepted"][0]["memory_id"])
    assert memory["content"] in (root / task["memory_paths"][0]).read_text()


@pytest.mark.parametrize("mutation", ["outside", "paraphrase"])
def test_nonquotes_are_rejected_without_memory(source_project, mutation):
    _, service, _, session, task, final = source_project
    value = json.loads(final.read_text())
    value["findings"][0]["path" if mutation == "outside" else "quote"] = (
        "not-a-current-source-value"
    )
    final.write_text(json.dumps(value))
    receipt = run.capture_findings(service, session["id"], task, final, "bad-finding")
    assert receipt["accepted"] == [] and len(receipt["rejected"]) == 1


def test_operational_capture_failure_propagates(source_project, monkeypatch):
    _, service, _, session, task, final = source_project

    def fail(*_args, **_kwargs):
        raise DomainError("session has expired")

    monkeypatch.setattr(service.memory, "save_memory", fail)
    with pytest.raises(DomainError):
        run.capture_findings(service, session["id"], task, final, "bad-operation")


def test_duplicate_capture_keeps_original_provenance_and_delivers_next_stage(
    source_project, tmp_path
):
    root, service, project, session, task, final = source_project
    output = tmp_path / "output"
    origin = output / "runs" / "origin-one"
    origin.mkdir(parents=True)
    (origin / "final.json").write_bytes(final.read_bytes())
    first = run.capture_findings(service, session["id"], task, final, "origin-one")
    captured = first["accepted"][0]
    registry = {captured["memory_id"]: captured}
    second = run.capture_findings(service, session["id"], task, final, "origin-two", registry)
    assert second["accepted"] == first["accepted"]
    ids = [captured["memory_id"]]
    source_prompt = "Current source and task"
    prepared = prepare_memory_prompt(
        source_prompt,
        db_path=service.db.path,
        project_id=project["id"],
        session_id=session["id"],
        memory_ids=ids,
    )
    repository = {"path": str(root), "commit": run.legacy.git(root, "rev-parse", "HEAD")}
    assert run.memory_delivery_fidelity(
        prepared["prompt"], source_prompt, prepared, ids, {"captures": registry}, output, repository
    )
    broken = copy.deepcopy(registry)
    broken[ids[0]]["origin_run_id"] = "origin-two"
    assert not run.memory_delivery_fidelity(
        prepared["prompt"], source_prompt, prepared, ids, {"captures": broken}, output, repository
    )


def test_unknown_dedup_origin_fails_closed(source_project):
    _, service, _, session, task, final = source_project
    run.capture_findings(service, session["id"], task, final, "origin-one")
    with pytest.raises(RuntimeError, match="original capture"):
        run.capture_findings(service, session["id"], task, final, "origin-two")


def test_canonical_reset_discards_agent_outputs_without_changing_snapshot(tmp_path):
    sequence = corpus.sequences()[0]
    tasks = sequence["tasks"]
    repositories = run.create_repositories(tmp_path, tasks, {}, lambda _value: None)
    worktree = tmp_path / "worktree"
    run.reset_stage(worktree, repositories[tasks[0]["id"]])
    (worktree / "agent-output.txt").write_text("Discard after archiving")
    corpus._apply_reference_fix(tasks[0]["id"], worktree)
    run.reset_stage(worktree, repositories[tasks[1]["id"]])
    assert not (worktree / "agent-output.txt").exists()
    assert run.legacy.git(worktree, "rev-parse", "HEAD") == repositories[tasks[1]["id"]]["commit"]
    assert not run.legacy.git(worktree, "status", "--porcelain")


def test_real_executor_uses_local_fake_process_and_durable_grant(tmp_path):
    fake = tmp_path / "fake-codex"
    final = tmp_path / "final.json"
    payload = json.dumps(events())
    fake.write_text(
        "#!/usr/bin/env python3\nimport json\nfrom pathlib import Path\n"
        + f"Path({str(final)!r}).write_text(json.dumps({{'summary':'local fake','findings':[]}}))\n"
        + f"for event in json.loads({payload!r}): print(json.dumps(event),flush=True)\n"
    )
    fake.chmod(0o700)
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    value = run.common.execute_codex(
        [str(fake)],
        "local-only",
        tmp_path,
        artifacts,
        10,
        {"PATH": "/usr/local/bin:/usr/bin:/bin", "CODEX_HOME": str(tmp_path / "no-auth")},
    )
    assert value["exit_code"] == 0
    assert (artifacts / "launch-grant.json").exists()
    assert (artifacts / "process-identity.json").exists()
    assert run.native_execution_validity(value, final)["valid"]


@pytest.fixture
def fake_experiment(tmp_path, monkeypatch):
    sequence = corpus.sequences()[0]
    tasks = sequence["tasks"]
    fake_corpus = SimpleNamespace(
        sequences=lambda: [sequence],
        build_stage=corpus.build_stage,
        grade=lambda *_args: {"success": True, "test_count": 1},
    )
    monkeypatch.setattr(run, "corpus_module", lambda: fake_corpus)
    monkeypatch.setattr(
        run,
        "frozen_manifest",
        lambda _tasks, settings: {"settings": settings, "files": {"fake": "fixture"}},
    )
    fake_codex = tmp_path / "codex-version-only"
    fake_codex.write_text("#!/bin/sh\nprintf 'codex-cli local-fake\\n'\n")
    fake_codex.chmod(0o700)
    stages = {}

    def execute(command, prompt, worktree, artifacts, timeout, environment):
        index = stages.get(str(worktree), 0)
        stages[str(worktree)] = index + 1
        task = tasks[index]
        corpus._apply_reference_fix(task["id"], worktree)
        quote = next(
            line
            for line in (worktree / task["memory_paths"][0]).read_text().splitlines()
            if line.strip()
        )
        (artifacts / "prompt.txt").write_text(prompt)
        (artifacts / "command.json").write_text(json.dumps(command))
        (artifacts / "final.json").write_text(
            json.dumps(
                {
                    "summary": "local fake",
                    "findings": [{"path": task["memory_paths"][0], "quote": quote}],
                }
            )
        )
        (artifacts / "events.jsonl").write_text(
            "\n".join(json.dumps(event) for event in events()) + "\n"
        )
        (artifacts / "stderr.log").write_text("")
        return {
            "exit_code": 0,
            "timed_out": False,
            "wall_time_seconds": 0.01,
            "overhead": {"cpu_seconds": 0.01, "process_tree_peak_rss_bytes": 1024},
            "telemetry": run.common.parse_codex_jsonl(artifacts / "events.jsonl"),
            "event_stream_framing": run.common.native_event_framing(artifacts / "events.jsonl"),
        }

    monkeypatch.setattr(run.common, "execute_codex", execute)
    arguments = argparse.Namespace(
        output=tmp_path / "study",
        model="gpt-6.1-sol",
        effort="low",
        codex=str(fake_codex),
        codex_home=None,
        timeout=10,
        repeats=1,
        seed=731,
        limit_sequences=1,
        resume=False,
    )
    arguments.output.mkdir()
    return arguments, tasks, fake_corpus


def test_complete_local_fake_study_carries_memory_with_fresh_native_stages(fake_experiment):
    arguments, tasks, _ = fake_experiment
    assert run.run_experiment(arguments, arguments.output) == 0
    report = json.loads((arguments.output / "report.json").read_text())
    assert len(report["runs"]) == 9
    assert all(row["status"] == "completed" for row in report["runs"])
    assert report["memory_observations"]["C_preloaded_memory_runs"] == 1
    stages = {row["stage"]: row for row in report["runs"] if row["configuration"] == "C"}
    assert len({row["memglide_session_id"] for row in stages.values()}) == 1
    assert stages[1]["memory_preparation"]["mode"] == "passthrough"
    assert stages[3]["memory_preparation"]["mode"] == "passthrough"
    assert stages[3]["memory_preparation"]["reason"] == "no_current_memory"
    assert all(
        item["freshness"] == "Stale"
        for item in stages[3]["memory_candidate_selection"]["candidates"]
    )
    assert stages[3]["session_cleanup"]["ended_at"] is not None
    first = [
        row for row in report["runs"] if row["stage"] == 1 and row["configuration"] in {"B", "C"}
    ]
    assert first[0]["actual_model_prompt_sha256"] == first[1]["actual_model_prompt_sha256"]
    assert report["sequence_accounting"]["C"]["successful_sequences"] == 1
    assert report["price_equivalent_assessment"]["actual_billed_cost_usd"] is None
    plan = json.loads((arguments.output / "plan.json").read_text())["runs"]
    state = json.loads((arguments.output / "state.json").read_text())
    run.validate_saved_state(arguments.output, plan, state)
    arguments.resume = True
    assert run.run_experiment(arguments, arguments.output) == 0


def test_independent_grade_failure_never_gates_quote_capture(fake_experiment):
    arguments, _, fake_corpus = fake_experiment
    fake_corpus.grade = lambda *_args: {"success": False, "test_count": 1}
    assert run.run_experiment(arguments, arguments.output) == 0
    report = json.loads((arguments.output / "report.json").read_text())
    assert len(report["failures"]) == 9
    assert report["memory_observations"]["C_preloaded_memory_runs"] == 1
    assert report["memory_observations"]["accepted_quote_instances"] == 3
    assert (
        report["sequence_accounting"]["C"]["price_equivalent_per_successful_sequence_usd"] is None
    )


def test_corrupt_saved_group_cannot_invent_memory(tmp_path):
    row = {"group_id": "group", "stage": 2}
    (tmp_path / "groups").mkdir()
    (tmp_path / "groups/group.json").write_text(
        json.dumps({"group_id": "group", "memory_ids": ["invented"], "captures": {}})
    )
    with pytest.raises(ValueError, match="immutable"):
        run.load_group(tmp_path, row, {"originals": {}})


@pytest.mark.parametrize(
    "reason",
    [
        "database_unavailable",
        "project_unavailable",
        "source_not_indexed",
        "source_excluded",
        "session_expired",
        "session_ended",
        "memory_unavailable",
        "policy_changed",
        "arbitrary_unknown",
    ],
)
def test_operational_memory_fallback_is_invalid_assignment(fake_experiment, monkeypatch, reason):
    arguments, _, _ = fake_experiment
    import memglide.integrations.memory_preload as memory_module

    def broken(prompt, **_kwargs):
        return {
            "prompt": prompt,
            "mode": "passthrough",
            "reason": reason,
            "memories": [],
            "context_bytes": 0,
        }

    monkeypatch.setattr(memory_module, "prepare_memory_prompt", broken)
    assert run.run_experiment(arguments, arguments.output) == 0
    report = json.loads((arguments.output / "report.json").read_text())
    later = [row for row in report["runs"] if row["configuration"] == "C" and row["stage"] > 1]
    assert later[0]["status"] == "invalid_treatment"
    assert later[1]["memory_preparation"]["reason"] == "no_current_memory"
    assert all(row["native_execution_validity"]["valid"] for row in later)


def test_changed_ignore_policy_cannot_capture_old_index_eligibility(source_project):
    root, service, _, session, task, final = source_project
    (root / ".gitignore").write_text(task["memory_paths"][0] + "\n")
    from memglide.integrations.preload import _Unavailable

    with pytest.raises(_Unavailable):
        run.capture_findings(service, session["id"], task, final, "ignored-now")


def test_cpu_accounting_preserves_setup_and_includes_all_parent_work():
    row = {
        "attempted": True,
        "configuration": "C",
        "setup": {"cpu_seconds": 2},
        "parent_process_cpu_seconds": 5,
        "overhead": {"cpu_seconds": 3},
    }
    values = run.metrics(row)
    assert values["approval_index_cpu_seconds"] == 2
    assert values["total_observed_local_cpu_seconds"] == 8


def test_live_candidate_filter_preserves_current_policy_among_stale_code(source_project):
    root, service, _, session, task, final = source_project
    first = run.capture_findings(service, session["id"], task, final, "policy-origin")["accepted"][
        0
    ]
    source = task["focus_paths"][0]
    content = (root / source).read_text()
    code = service.memory.save_memory(
        session["id"],
        "observation",
        content[:100],
        "Actual source quotation",
        sources=[{"path": source}],
    )
    (root / source).write_text(content + "\n")
    selection = run.select_memory_candidates(
        service, session["id"], [first["memory_id"], code["id"]]
    )
    assert selection["selected_ids"] == [first["memory_id"]]
    assert [item["freshness"] for item in selection["candidates"]] == ["Current", "Stale"]


def test_candidate_selection_is_bounded_and_unknown_memory_is_not_empty_fallback(source_project):
    _, service, _, session, _, _ = source_project
    with pytest.raises(ValueError, match="six"):
        run.select_memory_candidates(service, session["id"], [str(index) for index in range(7)])
    with pytest.raises(DomainError):
        run.select_memory_candidates(service, session["id"], ["unknown-memory"])


def test_shared_auth_blocker_stops_requests_without_retries(fake_experiment, monkeypatch):
    arguments, _, _ = fake_experiment
    original = run.common.execute_codex
    calls = []

    def blocked(*args, **kwargs):
        calls.append(1)
        result = original(*args, **kwargs)
        result["exit_code"] = 1
        result["telemetry"]["errors"] = ["401 Unauthorized"]
        return result

    monkeypatch.setattr(run.common, "execute_codex", blocked)
    assert run.run_experiment(arguments, arguments.output) == 2
    report = json.loads((arguments.output / "report.json").read_text())
    assert len(calls) == 1
    assert sum(row["attempted"] for row in report["runs"]) == 1
    assert "authentication" in report["metadata"]["shared_blocker"]


def test_whitespace_equivalent_dedup_retains_original_exact_quotation(source_project):
    root, service, _, session, task, final = source_project
    value = json.loads(final.read_text())
    original = value["findings"][0]["quote"]
    assert original + "\n" in (root / task["memory_paths"][0]).read_text()
    first = run.capture_findings(service, session["id"], task, final, "origin-one")["accepted"][0]
    value["findings"][0]["quote"] = original + "\n"
    final.write_text(json.dumps(value))
    second = run.capture_findings(
        service, session["id"], task, final, "origin-two", {first["memory_id"]: first}
    )
    assert second["accepted"] == [first]


@pytest.mark.parametrize("with_result", [False, True])
def test_pending_checkpoint_admits_valid_orphan_start_for_recovery(tmp_path, with_result):
    sequence = corpus.sequences()[0]
    row = run.make_plan([sequence], 1, 731)[0]
    state = {"originals": {row["run_id"]: run.durable.pending(row)}, "supplemental": []}
    metadata = {}
    original = copy.deepcopy(state)
    attempt = run.begin_attempt(tmp_path, row, state, metadata)
    if with_result:
        attempt.update(status="harness_error", finished_at=run.legacy.utc_now())
        run.common.atomic_json(Path(attempt["artifacts"]) / "result.json", attempt, immutable=True)
    # Simulate process death before the new state checkpoint became visible.
    run.validate_saved_state(tmp_path, [row], original)
    run.common.recover_interrupted(tmp_path, original, metadata)
    assert original["originals"][row["run_id"]]["status"] == (
        "harness_error" if with_result else "interrupted"
    )
    run.validate_saved_state(tmp_path, [row], original)


@pytest.mark.parametrize("freshness", ["Requires inspection", "unknown", None])
def test_unexpected_candidate_freshness_is_fault(freshness):
    service = SimpleNamespace(
        memory=SimpleNamespace(
            get_memory_snapshot=lambda *_args: {"freshness": freshness, "version": "version"}
        )
    )
    with pytest.raises(ValueError, match="unexpected freshness"):
        run.select_memory_candidates(service, "session", ["actual-prior-id"])


@pytest.mark.parametrize("extra_whitespace", [False, True])
def test_duplicate_findings_within_one_final_keep_first_capture_receipt(
    source_project, extra_whitespace
):
    _, service, _, session, task, final = source_project
    value = json.loads(final.read_text())
    duplicate = dict(value["findings"][0])
    if extra_whitespace:
        duplicate["quote"] += "\n"
    value["findings"].append(duplicate)
    final.write_text(json.dumps(value))
    captured = run.capture_findings(service, session["id"], task, final, "single-origin")
    assert len(captured["accepted"]) == 2
    assert captured["accepted"][0] == captured["accepted"][1]


@pytest.mark.parametrize(
    "message,expected",
    [
        ("HTTP 400 invalid schema for response_format", "unsupported_output_schema"),
        ("unsupported response_format", "unsupported_output_schema"),
        ("response schema maxItems is unsupported", "unsupported_output_schema"),
        ("HTTP 429 Too Many Requests", "explicit_rate_limit"),
    ],
)
def test_explicit_native_request_contract_failure_stops_campaign(tmp_path, message, expected):
    stream = tmp_path / "events.jsonl"
    (tmp_path / "stderr.log").write_text("")
    stream.write_text(
        "\n".join(
            json.dumps(event)
            for event in [
                {"type": "thread.started", "thread_id": "local-error"},
                {"type": "turn.started"},
                {"type": "error", "message": message},
                {"type": "turn.failed", "error": {"message": message}},
            ]
        )
        + "\n"
    )
    telemetry = run.common.parse_codex_jsonl(stream)
    assert run.shared_blocker({"exit_code": 1, "telemetry": telemetry}, tmp_path) == expected
    completed = copy.deepcopy(telemetry)
    completed["completed_turns"] = 1
    assert run.shared_blocker({"exit_code": 1, "telemetry": completed}, tmp_path) is None


def test_ordinary_task_failure_does_not_stop_campaign(tmp_path):
    (tmp_path / "stderr.log").write_text("A local test failed: invalid schema fixture")
    assert (
        run.shared_blocker({"exit_code": 0, "telemetry": {"completed_turns": 1}}, tmp_path) is None
    )


@pytest.mark.parametrize("field", ["artifacts", "worktree"])
def test_running_checkpoint_cannot_redirect_recovery_pointer(tmp_path, field):
    row = run.make_plan([corpus.sequences()[0]], 1, 731)[0]
    state = {"originals": {row["run_id"]: run.durable.pending(row)}, "supplemental": []}
    run.begin_attempt(tmp_path, row, state, {})
    run.validate_saved_state(tmp_path, [row], state)
    state["originals"][row["run_id"]][field] = str(tmp_path / "different-root")
    with pytest.raises(ValueError, match="boundary"):
        run.validate_saved_state(tmp_path, [row], state)
