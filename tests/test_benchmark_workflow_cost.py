"""Three-arm accounting and promotion checks use local native-event fixtures only."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import estimate_cost as native_cost  # noqa: E402
from benchmarks import workflow_cost as cost  # noqa: E402

POINT = "native_reported_price_equivalent_usd"
TIME = "end_to_end_wall_seconds"
LABELS = {"A": "standard", "B": "source-only", "C": "source-plus-support"}


@pytest.fixture
def pricing():
    return {
        "model": "exact-model",
        "service_tier": "standard",
        "context_threshold_tokens": 272000,
        "per_million_usd": {
            "uncached_input": 2,
            "cached_input": 0.1,
            "cache_write_input": 2.5,
            "output": 10,
        },
    }


def usage(**changes):
    return {
        "input_tokens": 100,
        "cached_input_tokens": 40,
        "cache_write_input_tokens": 0,
        "output_tokens": 10,
        "reasoning_output_tokens": 5,
        **changes,
    }


def stream(data):
    return (
        "\n".join(
            json.dumps(event)
            for event in (
                {"type": "thread.started", "thread_id": "fresh-fixture-thread"},
                {"type": "turn.started"},
                {"type": "turn.completed", "usage": data},
            )
        )
        + "\n"
    )


def raw_row(
    tmp_path,
    identifier,
    *,
    arm="A",
    task="task",
    repeat=1,
    success=True,
    data=None,
    stratum="explicit_focus",
):
    data = usage() if data is None else data
    artifacts = tmp_path / identifier
    artifacts.mkdir()
    (artifacts / "events.jsonl").write_text(stream(data), encoding="utf-8")
    return {
        "run_id": identifier,
        "task_id": task,
        "repeat": repeat,
        "configuration": arm,
        "selection_stratum": stratum,
        "artifacts": str(artifacts),
        "native_command": ["/installed/codex", "exec", "--ephemeral", "-"],
        "attempted": True,
        "status": "completed" if success else "failed",
        "language": "python",
        "task_kind": "repair",
        "starting_commit": "a" * 40,
        "common_task_prompt_sha256": "b" * 64,
        "grader": {"success": success, "test_count": 2},
        "treatment_valid": True,
        "preload_treatment_fidelity": {"valid": True},
        "native_execution_validity": {"valid": True},
        "telemetry": {"usage": {key: data.get(key) for key in native_cost.BASE_KEYS}},
        "metrics": {
            TIME: 2,
            "process_tree_peak_rss_bytes": 512,
            "observed_command_items": 3,
            "observed_file_change_items": 1,
        },
    }


def report(rows):
    return {
        "metadata": {
            "model": "exact-model",
            "source_unchanged_during_experiment": True,
            "frozen_manifest": {"settings": {"requested_service_tier": "default"}},
        },
        "configuration_labels": LABELS,
        "runs": rows,
    }


def gate_rows(*, task_count=3, controls=False):
    rows = []
    for task in range(task_count + int(controls)):
        for repeat in (1, 2):
            for arm in "ABC":
                rows.append(
                    {
                        "run_id": f"{task}-{repeat}-{arm}",
                        "task_id": str(task),
                        "repeat": repeat,
                        "configuration": arm,
                        "selection_stratum": (
                            "caller_context_supplied" if task == task_count else "explicit_focus"
                        ),
                        "success": True,
                        "cost": {POINT: 1 if arm == "C" else 2},
                        "metrics": {TIME: 1 if arm == "C" else 2},
                        "raw_fidelity": {
                            "treatment_valid": True,
                            "preload_treatment_fidelity": {"valid": True},
                            "native_execution_validity": {"valid": True},
                            "starting_commit": "a" * 40,
                            "common_task_prompt_sha256": "b" * 64,
                            "native_command": ["codex", "exec", "--ephemeral", "-"],
                        },
                    }
                )
    return rows


def set_measure(row, metric, value):
    row["cost" if metric == POINT else "metrics"][metric] = value


def test_sixty_unique_attempts_are_parsed_once_and_reused_for_all_comparisons(
    tmp_path, pricing, monkeypatch
):
    rows = [
        raw_row(
            tmp_path,
            f"{task}-{repeat}-{arm}",
            arm=arm,
            task=str(task),
            repeat=repeat,
            data=usage(input_tokens={"A": 100, "B": 90, "C": 80}[arm]),
            stratum="caller_context_supplied" if task < 2 else "explicit_focus",
        )
        for task in range(10)
        for repeat in (1, 2)
        for arm in "ABC"
    ]
    doc = report(rows)
    original = copy.deepcopy(doc)
    artifacts = {
        row["run_id"]: (Path(row["artifacts"]) / "events.jsonl").read_bytes() for row in rows
    }
    parse_calls = []
    parse = native_cost.parse_native_usage

    def counted(content):
        parse_calls.append(content)
        return parse(content)

    monkeypatch.setattr(native_cost, "parse_native_usage", counted)
    result = cost.assess(doc, pricing, events_root=tmp_path)
    assert len(parse_calls) == result["unique_attempts"] == len(result["runs"]) == 60
    assert len({row["run_id"] for row in result["runs"]}) == 60
    assert doc == original
    assert all(
        (Path(row["artifacts"]) / "events.jsonl").read_bytes() == artifacts[row["run_id"]]
        for row in rows
    )
    expected = {"A": 0.000224, "B": 0.000204, "C": 0.000184}
    assert set(result["configurations"]) == set("ABC")
    for arm, per_attempt in expected.items():
        group = result["configurations"][arm]
        assert group["attempts"] == group["assignments"] == group["successful_assignments"] == 20
        assert group["cost_statistics"][POINT]["total"] == pytest.approx(20 * per_attempt)
        assert group["cost_per_successful_task_usd"][POINT] == pytest.approx(per_attempt)
        assert group["metrics"]["process_tree_peak_rss_bytes"]["total"] is None
    assert sum(
        group["cost_statistics"][POINT]["total"] for group in result["configurations"].values()
    ) == pytest.approx(0.01224)
    for name, baseline, candidate in (
        ("C_over_A", "A", "C"),
        ("C_over_B", "B", "C"),
        ("B_over_A", "A", "B"),
    ):
        comparison = result["comparisons"][name]
        assert comparison["baseline"] == baseline
        assert comparison["candidate"] == candidate
        assert len(comparison["pairs"]) == 20
        assert comparison["cost_per_success_saving_percent"][POINT] == pytest.approx(
            100 * (expected[baseline] - expected[candidate]) / expected[baseline]
        )
        assert comparison["paired_outcomes"] == {
            "candidate_cheaper": 20,
            "baseline_cheaper": 0,
            "equal": 0,
            "unavailable": 0,
        }
        for pair in comparison["pairs"]:
            assert pair["valid"] is True
            assert len(pair["baseline_run_ids"]) == len(pair["candidate_run_ids"]) == 1
            assert pair["candidate_minus_baseline_usd"] == pytest.approx(
                expected[candidate] - expected[baseline]
            )
    strata = result["strata"]["selection_stratum"]
    assert set(strata) == {"explicit_focus", "caller_context_supplied"}
    assert result["actual_billed_cost_usd"] is None


@pytest.mark.parametrize("unknown_failure", [False, True])
def test_failure_retries_stay_in_numerator_and_unknown_spend_stays_unknown(
    tmp_path, pricing, unknown_failure
):
    failed = raw_row(tmp_path, "failed", success=False)
    rows = [failed, raw_row(tmp_path, "success")]
    rows += [raw_row(tmp_path, arm, arm=arm) for arm in "BC"]
    if unknown_failure:
        (tmp_path / "failed" / "events.jsonl").write_text(
            '{"type":"thread.started","thread_id":"failed"}\n'
        )
        failed["telemetry"]["usage"] = dict.fromkeys(native_cost.BASE_KEYS)
    result = cost.assess(report(rows), pricing)
    assert result["unique_attempts"] == 4
    assert [row["run_id"] for row in result["failures"]] == ["failed"]
    a = result["configurations"]["A"]
    assert a["attempts"] == 2
    assert a["assignments"] == a["successful_assignments"] == 1
    statistics = a["cost_statistics"][POINT]
    if unknown_failure:
        assert statistics["known_total"] == pytest.approx(0.000224)
        assert statistics["total"] is None
        assert a["cost_per_successful_task_usd"][POINT] is None
        assert result["comparisons"]["C_over_A"]["cost_per_success_saving_percent"][POINT] is None
    else:
        assert statistics["total"] == pytest.approx(0.000448)
        assert a["cost_per_successful_task_usd"][POINT] == pytest.approx(0.000448)
    pair = result["comparisons"]["C_over_A"]["pairs"][0]
    assert set(pair["baseline_run_ids"]) == {"failed", "success"}
    assert pair["valid"] is False
    assert pair["candidate_minus_baseline_usd"] is None
    assert result["comparisons"]["C_over_B"]["cost_per_success_saving_percent"][POINT] == 0


@pytest.mark.parametrize(
    "change",
    ["not-ephemeral", "resume", "unknown-outcome", "inconsistent-usage", "primary-mismatch"],
)
def test_inherited_native_accounting_guards_keep_invalid_attempt_cost_unknown(
    tmp_path, pricing, change
):
    row = raw_row(tmp_path, "one", arm="C")
    if change == "not-ephemeral":
        row["native_command"].remove("--ephemeral")
    elif change == "resume":
        row["native_command"].insert(2, "resume")
    elif change == "unknown-outcome":
        row["execution_outcome_unknown"] = True
    elif change == "inconsistent-usage":
        (tmp_path / "one" / "events.jsonl").write_text(stream(usage(cached_input_tokens=101)))
    else:
        row["telemetry"]["usage"]["input_tokens"] += 1
    result = cost.assess(report([row]), pricing)
    assert result["unique_attempts"] == result["configurations"]["C"]["attempts"] == 1
    assert result["runs"][0]["cost"][POINT] is None
    assert result["configurations"]["C"]["cost_statistics"][POINT]["total"] is None


def test_unknown_cache_write_point_retains_scenarios_without_inventing_cost(tmp_path, pricing):
    data = usage()
    del data["cache_write_input_tokens"]
    row = raw_row(tmp_path, "missing-writes", arm="C", data=data)
    result = cost.assess(report([row]), pricing)
    value = result["runs"][0]["cost"]
    assert value[POINT] is None
    assert value["possible_write_price_lower_usd"] == pytest.approx(0.000224)
    assert value["possible_write_price_upper_usd"] == pytest.approx(0.000254)


@pytest.mark.parametrize("change", ["model", "tier", "duplicate-run"])
def test_wrong_pricing_context_or_duplicate_native_attempt_is_rejected(tmp_path, pricing, change):
    row = raw_row(tmp_path, "one", arm="C")
    doc = report([row])
    if change == "model":
        pricing["model"] = "different-model"
    elif change == "tier":
        doc["metadata"]["frozen_manifest"]["settings"]["requested_service_tier"] = "priority"
    else:
        doc["runs"].append(copy.deepcopy(row))
    with pytest.raises(ValueError):
        cost.assess(doc, pricing)


def test_unproven_unchanged_source_retains_cost_but_invalidates_comparison_and_gate(
    tmp_path, pricing
):
    rows = [raw_row(tmp_path, arm, arm=arm) for arm in "ABC"]
    doc = report(rows)
    del doc["metadata"]["source_unchanged_during_experiment"]
    result = cost.assess(doc, pricing)
    assert result["configurations"]["C"]["cost_statistics"][POINT]["total"] == pytest.approx(
        0.000224
    )
    assert result["promotion_gate"]["passed"] is False
    for comparison in result["comparisons"].values():
        assert comparison["pairs"][0]["valid"] is False
        assert comparison["pairs"][0]["candidate_minus_baseline_usd"] is None


def test_promotion_gate_accepts_equality_and_preserves_parsed_rows():
    rows = gate_rows()
    for row in rows:
        row["cost"][POINT] = row["metrics"][TIME] = 2
    original = copy.deepcopy(rows)
    result = cost.promotion_gate(rows)
    assert result["passed"] is True
    assert result["checks"] and all(check["passed"] for check in result["checks"])
    assert {check["baseline"] for check in result["checks"]} == {"A", "B"}
    assert {check["statistic"] for check in result["checks"]} == {"mean", "median"}
    assert len({check["scope"] for check in result["checks"]}) == 3
    assert len(result["checks"]) == 24
    assert rows == original


@pytest.mark.parametrize("metric", [POINT, TIME])
@pytest.mark.parametrize("bad_statistic", ["mean", "median"])
def test_promotion_gate_requires_both_mean_and_median_for_cost_and_time(metric, bad_statistic):
    rows = gate_rows()
    baseline = [10, 10, 10] if bad_statistic == "mean" else [2, 10, 100]
    candidate = [1, 1, 100] if bad_statistic == "mean" else [1, 11, 12]
    for row in rows:
        values = candidate if row["configuration"] == "C" else baseline
        set_measure(row, metric, values[int(row["task_id"])])
    result = cost.promotion_gate(rows)
    assert result["passed"] is False
    assert any(
        check["statistic"] == bad_statistic and check["passed"] is False
        for check in result["checks"]
    )


@pytest.mark.parametrize("metric", [POINT, TIME])
def test_promotion_gate_cannot_hide_repeat_two_regression_in_pooled_improvement(metric):
    rows = gate_rows()
    for row in rows:
        value = 100 if row["configuration"] != "C" else (10 if row["repeat"] == 1 else 101)
        set_measure(row, metric, value)
    result = cost.promotion_gate(rows)
    assert result["passed"] is False
    assert any(check["passed"] for check in result["checks"])
    assert any(not check["passed"] for check in result["checks"])


def test_promotion_gate_requires_improvement_against_source_only_baseline_too():
    rows = gate_rows()
    for row in rows:
        row["cost"][POINT] = {"A": 3, "B": 1, "C": 2}[row["configuration"]]
    result = cost.promotion_gate(rows)
    assert result["passed"] is False
    assert any(check["baseline"] == "B" and not check["passed"] for check in result["checks"])


@pytest.mark.parametrize("focused_regresses", [False, True])
def test_caller_context_controls_neither_rescue_nor_defeat_focused_gate(focused_regresses):
    rows = gate_rows(controls=True)
    for row in rows:
        control = row["selection_stratum"] == "caller_context_supplied"
        candidate = row["configuration"] == "C"
        # Make the control effect dominate any accidentally pooled average.
        value = (1 if candidate else 1000) if focused_regresses else (1000 if candidate else 1)
        if not control:
            value = (3 if candidate else 2) if focused_regresses else (1 if candidate else 2)
        row["cost"][POINT] = row["metrics"][TIME] = value
    assert cost.promotion_gate(rows)["passed"] is (not focused_regresses)


@pytest.mark.parametrize("arm", "ABC")
@pytest.mark.parametrize(
    "invalid_cost", [None, -1, float("nan"), float("inf"), -float("inf"), False, "0"]
)
def test_promotion_gate_requires_complete_nonnegative_control_costs(arm, invalid_cost):
    rows = gate_rows(controls=True)
    control = next(
        row
        for row in rows
        if row["selection_stratum"] == "caller_context_supplied" and row["configuration"] == arm
    )
    control["cost"][POINT] = invalid_cost
    result = cost.promotion_gate(rows)
    assert result["passed"] is False
    assert any("including provided-context controls" in reason for reason in result["reasons"])
    # Control measurements never enter the focused benefit comparison itself.
    assert all(check["passed"] for check in result["checks"])


def test_zero_control_cost_is_known_and_does_not_influence_focused_benefit():
    rows = gate_rows(controls=True)
    for row in rows:
        if row["selection_stratum"] == "caller_context_supplied":
            row["cost"][POINT] = 0
    assert cost.promotion_gate(rows)["passed"] is True


@pytest.mark.parametrize(
    "change",
    [
        "missing-arm",
        "duplicate-assignment",
        "missing-repeat",
        "extra-repeat",
        "failed-baseline",
        "failed-candidate",
        "treatment-invalid",
        "preload-invalid",
        "native-invalid",
        "commit-mismatch",
        "prompt-mismatch",
        "unknown-cost",
        "unknown-time",
    ],
)
def test_promotion_gate_rejects_incomplete_unfaithful_or_unmeasured_focused_assignments(change):
    rows = gate_rows()
    candidate = next(row for row in rows if row["configuration"] == "C")
    if change == "missing-arm":
        rows.remove(candidate)
    elif change == "duplicate-assignment":
        duplicate = copy.deepcopy(candidate)
        duplicate["run_id"] += "-retry"
        rows.append(duplicate)
    elif change == "missing-repeat":
        rows = [row for row in rows if row["repeat"] == 1]
    elif change == "extra-repeat":
        duplicate = copy.deepcopy(candidate)
        duplicate["run_id"] += "-third"
        duplicate["repeat"] = 3
        rows.append(duplicate)
    elif change == "failed-baseline":
        rows[0]["success"] = False
    elif change == "failed-candidate":
        candidate["success"] = False
    elif change == "treatment-invalid":
        candidate["raw_fidelity"]["treatment_valid"] = False
    elif change in {"preload-invalid", "native-invalid"}:
        key = (
            "preload_treatment_fidelity"
            if change == "preload-invalid"
            else "native_execution_validity"
        )
        candidate["raw_fidelity"][key]["valid"] = False
    elif change == "commit-mismatch":
        candidate["raw_fidelity"]["starting_commit"] = "c" * 40
    elif change == "prompt-mismatch":
        candidate["raw_fidelity"]["common_task_prompt_sha256"] = "c" * 64
    elif change == "unknown-cost":
        candidate["cost"][POINT] = None
    else:
        candidate["metrics"][TIME] = None
    result = cost.promotion_gate(rows)
    assert result["passed"] is False
    assert result["reasons"]


def test_promotion_gate_requires_expected_tasks_and_unchanged_source():
    rows = gate_rows()
    assert cost.promotion_gate(rows, expected_task_ids={"0", "1", "2"})["passed"] is True
    assert (
        cost.promotion_gate(rows, expected_task_ids={"0", "1", "2", "omitted"})["passed"] is False
    )
    assert cost.promotion_gate(rows, source_unchanged=False)["passed"] is False


def test_cli_preserves_source_and_refuses_partial_output_overwrite(tmp_path, pricing):
    rows = [raw_row(tmp_path, arm, arm=arm) for arm in "ABC"]
    source = tmp_path / "source.json"
    prices = tmp_path / "pricing.json"
    source.write_text(json.dumps(report(rows)))
    prices.write_text(json.dumps(pricing))
    original = source.read_bytes()
    prefix = tmp_path / "assessment"
    argv = ["--report", str(source), "--pricing", str(prices), "--output-prefix", str(prefix)]
    assert cost.main(argv) == 0
    output = json.loads(prefix.with_suffix(".json").read_text())
    assert output["unique_attempts"] == 3
    assert output["provenance"]["primary_report_sha256"] == native_cost.digest(original)
    assert source.read_bytes() == original
    text = prefix.with_suffix(".md").read_text()
    assert "not actual bills" in text
    assert all(label in text for label in LABELS.values())
    prefix.with_suffix(".json").unlink()
    with pytest.raises(FileExistsError):
        cost.main(argv)
    assert not prefix.with_suffix(".json").exists()
    assert source.read_bytes() == original
