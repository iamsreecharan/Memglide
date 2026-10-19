"""V2 runner controls with artificial metadata; no held-out queries or models."""

from __future__ import annotations

import copy
import json
import os
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_automatic_v2 as run  # noqa: E402


def tasks(count=12):
    return [
        {
            "id": f"development-{index}",
            "repository": f"fictional-{index // 3}",
            "language": "python" if index % 2 else "typescript",
            "prompt": f"Repair artificial operation {index} consistently.",
            "known_paths": [f"private/implementation_{index}.py"],
        }
        for index in range(count)
    ]


def rows(count=4):
    return [
        {
            "task_id": task["id"],
            "configuration": arm,
            "repeat": repeat,
            "context_preparation": {"mode": "preloaded"},
            "treatment_fidelity": {"valid": True},
            "declared_scope_complete_proxy": True,
        }
        for task in tasks(count)
        for repeat in (1, 2)
        for arm in run.OFFLINE_ARMS
    ]


def test_offline_plan_balances_all_six_orders_and_reverses_repeats():
    plan = run.offline_plan(tasks(), 2, 88)
    assert len(plan) == 72
    assert len({item["run_id"] for item in plan}) == 72
    assert Counter(item["configuration"] for item in plan) == {"B": 24, "C": 24, "V1": 24}
    orders = {}
    for task in tasks():
        for repeat in (1, 2):
            orders[task["id"], repeat] = tuple(
                row["configuration"]
                for row in plan
                if row["task_id"] == task["id"] and row["repeat"] == repeat
            )
        assert orders[task["id"], 2] == tuple(reversed(orders[task["id"], 1]))
    assert set(Counter(orders.values()).values()) == {4}
    assert run.offline_plan(tasks(), 2, 88) == plan


def test_agent_visible_paths_use_only_neutral_ordinals(tmp_path):
    private_task_id = "classified-language-arm-target-hint"
    repo = run.neutral_repository_path(tmp_path, 3)
    work = run.neutral_worktree_path(tmp_path, 17)
    assert repo.relative_to(tmp_path).as_posix() == "repositories/repo-0003"
    assert work.relative_to(tmp_path).as_posix() == "worktrees/work-0017"
    assert private_task_id not in str(repo) + str(work)


@pytest.mark.parametrize("ordinal", [0, -1, True, "private-task-id"])
def test_neutral_paths_reject_nonordinal_labels(tmp_path, ordinal):
    with pytest.raises(ValueError):
        run.neutral_repository_path(tmp_path, ordinal)
    with pytest.raises(ValueError):
        run.neutral_worktree_path(tmp_path, ordinal)


def test_git_worktree_pointer_contains_no_private_task_identity(tmp_path):
    repository = run.neutral_repository_path(tmp_path, 1)
    repository.mkdir(parents=True)
    (repository / "module.py").write_text("value = 1\n")
    identity = run.base._commit_fixture(repository)
    worktree = run.neutral_worktree_path(tmp_path, 5)
    run.legacy.create_worktree(identity, worktree)
    pointer = (worktree / ".git").read_text()
    assert "repositories/repo-0001/.git/worktrees/work-0005" in pointer
    assert "development-" not in pointer
    assert "typescript" not in pointer


@pytest.mark.parametrize("count,repeats", [(1, 1), (5, 2), (7, 3)])
def test_offline_plan_supports_explicit_smaller_pilots(count, repeats):
    plan = run.offline_plan(tasks(count), repeats, 1)
    assert len(plan) == count * repeats * 3
    assert len({row["run_id"] for row in plan}) == len(plan)


@pytest.mark.parametrize("arm,policy", [("C", "v2"), ("V1", "v1")])
def test_policy_is_explicit_and_selection_gets_only_public_query(
    monkeypatch, tmp_path, arm, policy
):
    calls = []

    def fake(prompt, **kwargs):
        calls.append((prompt, kwargs))
        return {"prompt": prompt, "mode": "passthrough"}

    monkeypatch.setitem(
        sys.modules, "memglide.integrations.auto_preload", SimpleNamespace(prepare_task_prompt=fake)
    )
    task = tasks(1)[0]
    prompt = run.task_prompt(task)
    run.prepare(arm, prompt, task, {"project_id": "approved"}, tmp_path)
    actual, args = calls[0]
    assert actual == prompt
    assert args["task_query"] == task["prompt"]
    assert args["task_query"] in actual
    assert args["selection_policy"] == policy
    assert "known_paths" not in args and "focus_paths" not in args
    assert task["known_paths"][0] not in str(calls)
    assert "memory" not in args


@pytest.mark.parametrize("arm", ["C", "V1", "unknown"])
def test_outside_prompt_queries_or_unknown_arms_are_rejected(tmp_path, arm):
    with pytest.raises(ValueError):
        run.prepare(
            arm, "different shared prompt", tasks(1)[0], {"project_id": "approved"}, tmp_path
        )


def test_shared_workflow_makes_tool_availability_equal_without_paths():
    task = tasks(1)[0]
    prompt = run.task_prompt(task)
    assert "compiler is on PATH" in prompt
    assert "Do not install" in prompt
    assert "lifecycle/build scripts" in prompt
    assert "agent-instruction" in prompt
    assert task["known_paths"][0] not in prompt
    assert str(run.ROOT) not in prompt


def test_pinned_compiler_is_first_on_native_path_for_all_arms(monkeypatch):
    monkeypatch.setenv("PATH", "/artificial/bin")
    environment = run.native_environment()
    assert (
        environment["PATH"]
        == str(run.ROOT / "frontend/node_modules/.bin") + os.pathsep + "/artificial/bin"
    )
    assert environment["CI"] == "1"
    assert environment["NO_COLOR"] == "1"


def test_toolchain_hash_includes_optional_native_compiler_binary(monkeypatch, tmp_path):
    root = tmp_path / "checkout"
    package = root / "frontend/node_modules/typescript"
    (package / "bin").mkdir(parents=True)
    (package / "bin/tsc").write_text("wrapper calls native compiler")
    (package / "package.json").write_text(json.dumps({"version": "7-development"}))
    binding = root / "frontend/node_modules/.bin/tsc"
    binding.parent.mkdir()
    binding.symlink_to(package / "bin/tsc")
    platform = root / "frontend/node_modules/@typescript/typescript-test/lib/tsc"
    platform.parent.mkdir(parents=True)
    platform.write_bytes(b"fake native compiler")
    node = tmp_path / "node"
    node.write_bytes(b"fake Node binary")
    monkeypatch.setattr(run, "ROOT", root)
    monkeypatch.setattr(run.shutil, "which", lambda name: str(node))
    monkeypatch.setattr(run.subprocess, "check_output", lambda *args, **kwargs: "v-test")
    first = run.toolchain_identity()
    key = platform.relative_to(root).as_posix()
    assert first["platform_compiler_package_files_sha256"][key] == run.common.digest(
        b"fake native compiler"
    )
    platform.write_bytes(b"mutated compiler")
    second = run.toolchain_identity()
    assert first != second


def test_partial_native_mcp_counter_is_not_a_complete_total():
    report = run.formal_report(
        [
            {
                "task_id": "x",
                "repeat": 1,
                "configuration": "A",
                "status": "interrupted",
                "attempted": True,
                "strict_success": False,
                "telemetry": {"mcp_call_count": 0, "mcp_counts_complete": False},
            }
        ]
    )
    assert (
        report["configurations"]["A"]["observed_native_telemetry"]["mcp_call_count"]["total"]
        is None
    )


@pytest.mark.parametrize(
    "started,finished,expected",
    [
        (1.5, 2.25, 0.75),
        (0.0, 0.0, 0.0),
        (None, 2.0, None),
        (1.0, None, None),
        (2.0, 1.0, None),
        (float("nan"), 2.0, None),
        (1.0, float("inf"), None),
    ],
)
def test_preparation_child_cpu_delta_is_observed_or_unavailable(started, finished, expected):
    assert run.waited_prep_child_cpu_delta(started, finished) == expected


def test_child_cpu_snapshot_adds_only_os_user_and_system_counters(monkeypatch):
    fake = SimpleNamespace(
        RUSAGE_CHILDREN=9,
        getrusage=lambda who: (
            SimpleNamespace(ru_utime=2.5, ru_stime=0.75)
            if who == 9
            else pytest.fail("Wrong resource counter")
        ),
    )
    monkeypatch.setitem(sys.modules, "resource", fake)
    assert run.waited_child_cpu_snapshot() == 3.25


def test_child_cpu_snapshot_unavailable_platform_stays_null(monkeypatch):
    monkeypatch.setitem(sys.modules, "resource", None)
    assert run.waited_child_cpu_snapshot() is None


def test_all_skip_is_ineligible_before_paid_dispatch():
    observations = rows()
    for row in observations:
        if row["configuration"] == "C":
            row["context_preparation"]["mode"] = "passthrough"
            row["declared_scope_complete_proxy"] = False
    gate = run.eligibility(observations, len(observations))
    assert gate["passed"] is False
    assert gate["all_skip_rejected"] is True
    assert gate["default_promotion"] is False


def test_one_delivery_cannot_pass_half_task_eligibility():
    observations = rows()
    for row in observations:
        if row["configuration"] == "C" and row["task_id"] != "development-0":
            row["context_preparation"]["mode"] = "passthrough"
            row["declared_scope_complete_proxy"] = False
    gate = run.eligibility(observations, len(observations))
    assert gate["C_preloaded_unique_task_fraction"] == 0.25
    assert gate["passed"] is False


def test_both_repeats_required_for_task_eligibility():
    observations = rows()
    for row in observations:
        if row["configuration"] == "C" and row["repeat"] == 2:
            row["context_preparation"]["mode"] = "passthrough"
    gate = run.eligibility(observations, len(observations))
    assert gate["C_preloaded_unique_task_fraction"] == 0
    assert gate["passed"] is False


def test_three_quarters_of_b_preparable_tasks_must_be_complete():
    observations = rows()
    for row in observations:
        if row["configuration"] == "C" and row["task_id"] in {"development-2", "development-3"}:
            row["declared_scope_complete_proxy"] = False
    gate = run.eligibility(observations, len(observations))
    assert gate["C_preloaded_unique_task_fraction"] == 1
    assert gate["C_complete_scope_fraction_of_B_preparable_tasks"] == 0.5
    assert gate["passed"] is False
    for row in observations:
        if row["configuration"] == "C" and row["task_id"] == "development-2":
            row["declared_scope_complete_proxy"] = True
    gate = run.eligibility(observations, len(observations))
    assert gate["C_complete_scope_fraction_of_B_preparable_tasks"] == 0.75
    assert gate["passed"] is True


def test_gate_uses_b_preparable_subset_without_dropping_primary_rows():
    observations = rows()
    for row in observations:
        if row["task_id"] in {"development-2", "development-3"} and row["configuration"] in {
            "B",
            "C",
        }:
            row["context_preparation"]["mode"] = "passthrough"
            row["declared_scope_complete_proxy"] = False
    gate = run.eligibility(observations, len(observations))
    assert gate["C_preloaded_unique_task_fraction"] == 0.5
    assert gate["C_complete_scope_fraction_of_B_preparable_tasks"] == 1
    assert gate["passed"] is True
    assert len(observations) == 24


@pytest.mark.parametrize("defect", ["fidelity", "incomplete", "no_B_preparable"])
def test_invalid_incomplete_or_unpreparable_offline_study_cannot_dispatch(defect):
    observations = rows()
    if defect == "fidelity":
        observations[0]["treatment_fidelity"]["valid"] = False
    elif defect == "incomplete":
        observations.pop()
    else:
        for row in observations:
            if row["configuration"] == "B":
                row["context_preparation"]["mode"] = "passthrough"
    assert run.eligibility(observations, 24)["passed"] is False


def test_formal_report_summarizes_proxies_and_keeps_unavailable_metrics_null():
    observations = [
        {
            "configuration": "C",
            "task_id": "x",
            "repeat": 1,
            "status": "completed",
            "attempted": True,
            "strict_success": True,
            "full_task_seconds": 3,
            "parent_cpu_seconds": 0.2,
            "telemetry": {
                "command_count": 3,
                "observed_file_read_commands": 2,
                "observed_repeated_read_commands": 1,
                "model_calls": None,
                "repeated_file_reads": None,
                "mcp_call_count": 0,
            },
            "overhead": {"cpu_seconds": 0.7, "process_tree_peak_rss_bytes": 1000},
            "estimated_api_equivalent_usd": 0.1,
        }
    ]
    report = run.formal_report(observations)
    assert report["version"] == "automatic-2"
    summary = report["configurations"]["C"]
    assert summary["observed_native_telemetry"]["observed_repeated_read_commands"]["mean"] == 1
    assert summary["observed_native_telemetry"]["model_calls"]["total"] is None
    assert summary["observed_native_telemetry"]["repeated_file_reads"]["total"] is None
    assert summary["parent_cpu_seconds_including_treatment_audit"]["mean"] == 0.2
    assert summary["local_resources"]["cpu_seconds"]["mean"] == 0.7
    assert "excludes parent" in summary["rss_scope"]
    assert report["actual_billed_cost_usd"] is None


def test_ineligible_offline_blocks_before_native_binary_lookup(monkeypatch, tmp_path):
    monkeypatch.setattr(
        run, "read_plan", lambda path: {"budget_estimate": {"estimated_campaign_high_usd": 18.59}}
    )
    monkeypatch.setattr(
        run, "validate_offline_report", lambda *args: (_ for _ in ()).throw(ValueError("all-SKIP"))
    )
    monkeypatch.setattr(
        run.shutil,
        "which",
        lambda *args: pytest.fail("Ineligible offline study reached native binary"),
    )
    with pytest.raises(ValueError, match="all-SKIP"):
        run.execute(
            tmp_path,
            tmp_path / "out",
            offline_report_path=tmp_path / "report.json",
            approved_estimated_budget_usd=18.59,
            authorization_reference="User continuation after allowance",
            codex="codex",
        )
    assert not (tmp_path / "out").exists()


def test_no_approval_record_blocks_before_offline_validation_or_native(monkeypatch, tmp_path):
    monkeypatch.setattr(
        run, "read_plan", lambda path: {"budget_estimate": {"estimated_campaign_high_usd": 18.59}}
    )
    monkeypatch.setattr(
        run, "validate_offline_report", lambda *args: pytest.fail("Approval record was bypassed")
    )
    with pytest.raises(ValueError):
        run.execute(
            tmp_path,
            tmp_path / "out",
            offline_report_path=tmp_path / "report.json",
            approved_estimated_budget_usd=None,
            authorization_reference=None,
            codex="codex",
        )


def test_default_and_offline_commands_never_dispatch_native(monkeypatch, tmp_path):
    called = []
    monkeypatch.setattr(
        run,
        "create_plan",
        lambda *args, **kwargs: {
            "assignments": [],
            "offline_assignments": [],
            "budget_estimate": {},
        },
    )
    monkeypatch.setattr(run, "read_plan", lambda *args: {})
    monkeypatch.setattr(run, "offline", lambda *args: {"summary": {}, "technical_eligibility": {}})
    monkeypatch.setattr(run, "execute", lambda *args, **kwargs: called.append("FORBIDDEN"))
    assert run.main(["--output", str(tmp_path / "plan")]) == 0
    assert (
        run.main(["offline", "--plan", str(tmp_path), "--output", str(tmp_path / "offline")]) == 0
    )
    assert called == []


def test_fresh_corpus_is_not_imported_or_read_on_module_import(monkeypatch):
    import importlib

    calls = []
    original = run.importlib.import_module

    def guarded(name, *args, **kwargs):
        if name == "benchmarks.corpus_automatic_v2":
            calls.append(name)
            pytest.fail("Module import accessed held-out corpus")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(run.importlib, "import_module", guarded)
    importlib.reload(run)
    assert calls == []


def test_load_rejects_target_path_in_public_prompt_without_real_corpus(monkeypatch):
    fake = tasks(1)
    fake[0]["prompt"] = "Repair " + fake[0]["known_paths"][0]
    monkeypatch.setattr(run, "corpus", lambda: SimpleNamespace(load_tasks=lambda: fake))
    with pytest.raises(ValueError, match="target path"):
        run.load_tasks()


def test_offline_report_binding_and_gate_are_recomputed(monkeypatch, tmp_path):
    directory = tmp_path / "plan"
    directory.mkdir()
    (directory / "preregistration.json").write_text("frozen plan")
    observations = rows()
    assignments = [
        {key: row[key] for key in ("task_id", "configuration", "repeat")} for row in observations
    ]
    plan = {"offline_assignments": assignments, "settings": {"repeats": 2}}
    report = {
        "version": run.VERSION,
        "frozen_preregistration_sha256": run.common.digest(b"frozen plan"),
        "rows": observations,
        "technical_eligibility": run.eligibility(observations, 24),
    }
    path = tmp_path / "report.json"

    def save(value):
        path.write_text(json.dumps(value))
        (tmp_path / "report.sha256").write_text(run.common.digest(path.read_bytes()))

    save(report)
    assert run.validate_offline_report(path, directory, plan)["technical_eligibility"]["passed"]
    changed = copy.deepcopy(report)
    changed["technical_eligibility"]["passed"] = False
    save(changed)
    with pytest.raises(ValueError, match="ineligible"):
        run.validate_offline_report(path, directory, plan)
    changed = copy.deepcopy(report)
    changed["frozen_preregistration_sha256"] = "another plan"
    save(changed)
    with pytest.raises(ValueError, match="another preregistration"):
        run.validate_offline_report(path, directory, plan)
