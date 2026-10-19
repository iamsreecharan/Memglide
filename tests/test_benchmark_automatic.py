"""Offline preregistration/dispatch safeguards; no authenticated model requests."""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import run_automatic as run  # noqa: E402


def tasks():
    return [
        {
            "id": f"heldout-{index}",
            "repository": f"repository-{index // 3}",
            "language": "python" if index < 6 else "typescript",
            "prompt": f"Repair public operation {index} without changing its public contract.",
            "known_paths": [f"private/source_{index}.py"],
        }
        for index in range(12)
    ]


def test_plan_has_all_assignments_balanced_orders_and_reversed_repeats():
    plan = run.make_plan(tasks(), 2, 71)
    assert len(plan) == 72
    assert len({row["run_id"] for row in plan}) == 72
    assert Counter(row["configuration"] for row in plan) == {"A": 24, "B": 24, "C": 24}
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


def test_common_prompt_contains_no_private_paths_or_target_metadata():
    task = tasks()[0]
    task["reference_fix"] = "DO NOT LEAK THIS FIX"
    task["hidden_assertions"] = "DO NOT LEAK THIS ASSERTION"
    prompt = run.task_prompt(task)
    assert task["prompt"] in prompt
    assert task["known_paths"][0] not in prompt
    assert task["id"] not in prompt
    assert task["reference_fix"] not in prompt
    assert task["hidden_assertions"] not in prompt


@pytest.mark.parametrize(
    "change",
    [
        {"known_paths": ["../escape.py"]},
        {"known_paths": ["/absolute.py"]},
        {"known_paths": ["back\\slash.py"]},
        {"known_paths": ["same.py", "same.py"]},
        {"known_paths": []},
        {"prompt": "Read private/source_0.py and fix it"},
        {"id": "../bad"},
        {"language": "shell"},
    ],
)
def test_task_loader_rejects_unsafe_scope_or_path_leak(monkeypatch, change):
    value = [{**tasks()[0], **change}]
    monkeypatch.setattr(run, "corpus", lambda: SimpleNamespace(load_tasks=lambda: value))
    with pytest.raises(ValueError):
        run.load_tasks()


def test_duplicate_task_ids_rejected(monkeypatch):
    value = [tasks()[0], tasks()[0]]
    monkeypatch.setattr(run, "corpus", lambda: SimpleNamespace(load_tasks=lambda: value))
    with pytest.raises(ValueError):
        run.load_tasks()


def test_c_selection_does_not_receive_task_object_or_known_paths(monkeypatch, tmp_path):
    calls = []

    def selection(prompt, **kwargs):
        calls.append((prompt, kwargs))
        return {
            "prompt": prompt,
            "mode": "passthrough",
            "reason": "insufficient_evidence",
            "files": [],
            "context_bytes": 0,
        }

    module = SimpleNamespace(prepare_task_prompt=selection)
    monkeypatch.setitem(sys.modules, "memglide.integrations.auto_preload", module)
    task = tasks()[0]
    public_prompt = run.task_prompt(task)
    result = run.prepare("C", public_prompt, task, {"project_id": "approved-project"}, tmp_path)
    assert result["reason"] == "insufficient_evidence"
    assert calls[0][0] == public_prompt
    assert calls[0][1]["task_query"] == task["prompt"]
    assert calls[0][1]["task_query"] in calls[0][0]
    assert calls[0][1]["enabled"] is True
    assert "focus_paths" not in calls[0][1]
    assert "known_paths" not in calls[0][1]
    assert "private" not in str(calls[0])
    assert "memory" not in calls[0][1]


def test_a_does_not_import_or_access_preparation_state(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Bare A accessed a preparation module")

    monkeypatch.setattr(run.importlib, "import_module", forbidden)
    assert run.prepare("A", "task", tasks()[0], {}, tmp_path)["prompt"] == "task"


def test_c_cannot_supply_a_query_outside_the_actual_shared_prompt(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        pytest.fail("Mismatched public query reached production selection")

    monkeypatch.setitem(
        sys.modules,
        "memglide.integrations.auto_preload",
        SimpleNamespace(prepare_task_prompt=forbidden),
    )
    with pytest.raises(ValueError, match="verbatim"):
        run.prepare(
            "C", "Different shared native prompt", tasks()[0], {"project_id": "approved"}, tmp_path
        )


@pytest.mark.parametrize("amount", [None, 0, -1, 18.58, float("nan"), float("inf"), True])
def test_execute_budget_requires_explicit_finite_sufficient_approval(amount):
    with pytest.raises(ValueError):
        run.validate_approval(
            {"budget_estimate": {"estimated_campaign_high_usd": 18.59}}, amount, "New user approval"
        )


@pytest.mark.parametrize("reference", [None, "", "  "])
def test_execute_requires_new_approval_reference(reference):
    with pytest.raises(ValueError):
        run.validate_approval(
            {"budget_estimate": {"estimated_campaign_high_usd": 18.59}}, 20, reference
        )


def test_approval_guard_precedes_executable_lookup_or_native_command(monkeypatch, tmp_path):
    monkeypatch.setattr(
        run,
        "read_plan",
        lambda directory: {"budget_estimate": {"estimated_campaign_high_usd": 18.59}},
    )

    def forbidden(*args, **kwargs):
        pytest.fail("Native executable touched before new approval")

    monkeypatch.setattr(run.shutil, "which", forbidden)
    monkeypatch.setattr(run.subprocess, "check_output", forbidden)
    with pytest.raises(ValueError):
        run.execute(
            tmp_path,
            tmp_path / "out",
            approved_estimated_budget_usd=None,
            authorization_reference=None,
            codex="codex",
        )
    assert not (tmp_path / "out").exists()


def test_default_command_is_plan_and_cannot_dispatch_native(monkeypatch, tmp_path):
    called = []

    def local_plan(*args, **kwargs):
        called.append("plan")
        return {"assignments": [], "budget_estimate": {}}

    monkeypatch.setattr(run, "create_plan", local_plan)
    monkeypatch.setattr(
        run, "execute", lambda *args, **kwargs: pytest.fail("Default dispatched a model")
    )
    assert run.main(["--output", str(tmp_path / "plan")]) == 0
    assert called == ["plan"]


def test_offline_cli_cannot_dispatch_native(monkeypatch, tmp_path):
    monkeypatch.setattr(run, "read_plan", lambda directory: {})
    monkeypatch.setattr(run, "offline", lambda *args: {"summary": {}})
    monkeypatch.setattr(
        run, "execute", lambda *args, **kwargs: pytest.fail("Offline dispatched a model")
    )
    assert (
        run.main(["offline", "--plan", str(tmp_path), "--output", str(tmp_path / "offline")]) == 0
    )


def test_budget_is_historical_estimate_not_billing_or_guaranteed_cap():
    result = run.budget_estimate(72)
    assert result["historical_completed_observations"] == 80
    assert result["estimated_campaign_high_usd"] == pytest.approx(18.59)
    assert result["hard_cap_available"] is False
    assert result["planning_multiplier"] == 3


def test_fallback_treatment_preserves_exact_prompt_and_no_partial_evidence():
    value = {"prompt": "exact original", "mode": "passthrough", "files": [], "context_bytes": 0}
    assert run.verify_delivery(value, "exact original", {})["valid"] is True
    changed = {**value, "prompt": "modified"}
    with pytest.raises(ValueError):
        run.verify_delivery(changed, "exact original", {})
    with pytest.raises(ValueError):
        run.verify_delivery({**value, "files": [{"path": "partial.py"}]}, "exact original", {})


def observed(task, repeat, arm, metric, *, success=True, cost=1.0):
    return {
        "task_id": task,
        "repeat": repeat,
        "configuration": arm,
        "attempted": True,
        "strict_success": success,
        "status": "completed" if success else "failed",
        "full_task_seconds": metric,
        "estimated_api_equivalent_usd": cost,
    }


def test_paired_uncertainty_clusters_repeats_by_task_and_retains_variability():
    rows = []
    for task, delta in (("x", -2), ("y", 4)):
        for repeat in (1, 2):
            rows.extend([observed(task, repeat, "A", 10), observed(task, repeat, "C", 10 + delta)])
    report = run.paired_effects(rows, "full_task_seconds", "C", "A")
    assert report["paired_observations"] == 4
    assert report["independent_task_clusters"] == 2
    assert report["mean_paired_difference"] == 1
    assert report["median_paired_difference"] == 1
    assert report["per_task_differences"] == {"x": [-2, -2], "y": [4, 4]}
    assert report["mean_difference_task_cluster_bootstrap_95_percent_interval"] == [-2, 4]


def test_failed_attempt_cost_is_in_success_denominator_and_unknown_is_not_zero():
    rows = [observed("x", 1, "C", 10, cost=2), observed("y", 1, "C", 12, success=False, cost=3)]
    report = run.formal_report(rows)
    assert report["configurations"]["C"]["estimated_cost_per_strict_success_usd"] == 5
    rows[1]["estimated_api_equivalent_usd"] = None
    report = run.formal_report(rows)
    assert report["configurations"]["C"]["estimated_cost_per_strict_success_usd"] is None
    assert report["configurations"]["C"]["estimated_api_equivalent_usd"]["known_total"] == 2
    assert report["actual_billed_cost_usd"] is None


def test_unrun_and_interrupted_originals_remain_visible_and_no_false_success():
    rows = [
        observed("x", 1, "A", 1),
        {
            "task_id": "y",
            "repeat": 1,
            "configuration": "A",
            "status": "not_run",
            "attempted": False,
            "strict_success": False,
        },
        {
            "task_id": "z",
            "repeat": 1,
            "configuration": "C",
            "status": "interrupted",
            "attempted": True,
            "strict_success": False,
        },
    ]
    report = run.formal_report(rows)
    assert report["runs"] == rows
    assert report["configurations"]["A"]["planned"] == 2
    assert report["configurations"]["A"]["attempted"] == 1
    assert report["configurations"]["C"]["strict_successes"] == 0
    assert report["configurations"]["C"]["estimated_cost_per_strict_success_usd"] is None


def test_preregistration_rejects_hash_or_frozen_source_changes(monkeypatch, tmp_path):
    plan = {
        "version": run.VERSION,
        "frozen_manifest": {"files": {"code.py": "old"}},
        "tasks": [],
        "assignments": [],
        "settings": {"repeats": 2, "seed": 1},
        "repositories": {},
    }
    path = tmp_path / "preregistration.json"
    path.write_text(json.dumps(plan))
    (tmp_path / "preregistration.sha256").write_text(run.common.digest(path.read_bytes()))
    monkeypatch.setattr(run, "frozen_manifest", lambda: {"files": {"code.py": "new"}})
    with pytest.raises(ValueError, match="changed"):
        run.read_plan(tmp_path)
    original = copy.deepcopy(plan)
    original["tasks"] = ["changed"]
    path.write_text(json.dumps(original))
    with pytest.raises(ValueError, match="hash"):
        run.read_plan(tmp_path)


def test_model_change_cannot_reuse_other_models_frozen_tariff(tmp_path):
    with pytest.raises(ValueError, match="pricing"):
        run.create_plan(tmp_path / "plan", repeats=2, seed=1, model="different-model", effort="low")
    assert not (tmp_path / "plan").exists()


def test_interrupt_stops_original_and_keeps_whole_attempt_cost_unknown(monkeypatch, tmp_path):
    row = {"run_id": "interrupted-A", "task_id": "x", "configuration": "A", "repeat": 1}
    stopped = []
    monkeypatch.setattr(
        run.legacy, "create_worktree", lambda repository, root: root.mkdir(parents=True)
    )
    monkeypatch.setattr(run.legacy, "protection_snapshot", lambda root: {})
    monkeypatch.setattr(run.workflow, "codex_command", lambda *args: ["forbidden-fake"])

    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(run.common, "execute_codex", interrupted)
    monkeypatch.setattr(run.durable, "stop_orphan", lambda artifacts: stopped.append(artifacts))
    result = run._attempt(
        row,
        {"id": "x", "prompt": "task"},
        {
            "repositories": {"x": {}},
            "settings": {"model": "fake", "effort": "low", "timeout_seconds": 1},
        },
        tmp_path,
        "fake",
    )
    assert result["status"] == "interrupted"
    assert result["execution_outcome_unknown"] is True
    assert result["strict_success"] is False
    assert result["estimated_api_equivalent_usd"] is None
    assert set(result["native_usage"]["usage"].values()) == {None}
    assert len(stopped) == 1
    assert (tmp_path / "runs/interrupted-A/attempt-start.json").exists()
    assert (tmp_path / "runs/interrupted-A/result.json").exists()


def test_preregistered_source_drift_retains_every_unrun_original(monkeypatch, tmp_path):
    plan = {
        "budget_estimate": {
            "estimated_campaign_high_usd": 1,
            "planning_high_per_assignment_usd": 0.1,
        },
        "settings": {"codex_version": "0.159.2"},
        "tasks": [{"id": "x"}],
        "assignments": [
            {"task_id": "x", "repeat": 1, "configuration": arm, "run_id": "x-" + arm}
            for arm in run.ARMS
        ],
    }
    calls = []

    def read(directory):
        calls.append(directory)
        if len(calls) > 1:
            raise ValueError("source changed")
        return plan

    monkeypatch.setattr(run, "read_plan", read)
    monkeypatch.setattr(run, "_load_preparers", lambda: None)
    monkeypatch.setattr(run.shutil, "which", lambda executable: "/fake/codex")
    monkeypatch.setattr(run.subprocess, "check_output", lambda *args, **kwargs: "codex-cli 0.159.2")
    monkeypatch.setattr(
        run, "_attempt", lambda *args: pytest.fail("Source drift dispatched a model")
    )
    directory = tmp_path / "plan"
    directory.mkdir()
    (directory / "preregistration.json").write_text("{}")
    report = run.execute(
        directory,
        tmp_path / "results",
        approved_estimated_budget_usd=2,
        authorization_reference="new approval",
        codex="fake",
    )
    assert len(report["runs"]) == 3
    assert {row["status"] for row in report["runs"]} == {"not_run"}
    assert {row["reason"] for row in report["runs"]} == {"source changed"}
    assert report["estimated_allowance_stop_reason"] == "source changed"
