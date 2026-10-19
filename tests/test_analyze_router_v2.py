"""Artificial outcomes verify analysis denominators, strata and prompt controls."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks.analyze_router_v2 import analyze, main, markdown  # noqa: E402


def synthetic_report(tasks: int = 3) -> dict:
    rows = []
    for task in range(tasks):
        for repeat in (1, 2):
            for arm in ("A", "B", "C"):
                mode = "preloaded" if task % 2 == 0 else "SKIP"
                hash_arm = ("B" if mode == "preloaded" else "A") if arm == "C" else arm
                cost = {"A": 1.0, "B": 0.8, "C": 0.7}[arm]
                row = {
                    "task_id": f"synthetic-task-{task}", "repeat": repeat,
                    "configuration": arm, "run_id": f"synthetic-{task}-{repeat}-{arm}",
                    "attempted": True, "strict_success": True, "status": "completed",
                    "estimated_api_equivalent_usd": cost, "full_task_seconds": cost * 10,
                    "actual_prompt_sha256": hashlib.sha256(f"{task}-{repeat}-{hash_arm}".encode()).hexdigest(),
                    "native_usage": {"usage": {"input_tokens": 100, "cached_input_tokens": 20, "output_tokens": 30}},
                    "price_equivalent": {"possible_write_price_lower_usd": cost, "possible_write_price_upper_usd": cost + 0.1},
                }
                if arm == "C":
                    row["context_preparation"] = {
                        "mode": "preloaded" if mode == "preloaded" else "passthrough",
                        "automatic_selection": {"decision": "FOCUSED_SOURCE" if mode == "preloaded" else "SKIP"},
                    }
                rows.append(row)
    return {"version": "synthetic-only", "runs": rows}


def result(report: dict) -> dict:
    return analyze(report, expected_planned=len(report["runs"]))


def test_all_72_original_rows_and_failed_costs_remain_in_primary_denominator():
    report = synthetic_report(12)
    failed = next(row for row in report["runs"] if row["configuration"] == "C")
    failed.update(strict_success=False, status="failed", estimated_api_equivalent_usd=1.7)
    before = copy.deepcopy(report)
    value = analyze(report)
    assert report == before and value["runs"] == before["runs"]
    assert value["planned_assignments"] == value["attempted_assignments"] == 72
    c = value["primary_intent_to_treat"]["configurations"]["C"]
    assert c["planned"] == 24 and c["strict_successes"] == 23
    assert c["estimated_api_equivalent_usd"]["total"] == pytest.approx(23 * 0.7 + 1.7)
    assert c["estimated_cost_per_strict_success_usd"] == pytest.approx((23 * 0.7 + 1.7) / 23)
    assert value["actual_billed_cost_usd"] is None
    effect = value["primary_intent_to_treat"]["paired_effects"]["C_vs_B"]["full_task_seconds"]
    assert effect["paired_observations"] == 24 and effect["independent_task_clusters"] == 12
    assert effect["bootstrap_replicates"] == 2000


def test_unknown_failed_attempt_cost_prevents_complete_cost_per_success():
    report = synthetic_report()
    failed = next(row for row in report["runs"] if row["configuration"] == "C")
    failed.update(strict_success=False, status="failed", estimated_api_equivalent_usd=None)
    c = result(report)["primary_intent_to_treat"]["configurations"]["C"]
    assert c["strict_successes"] == 5
    assert c["estimated_api_equivalent_usd"]["missing"] == 1
    assert c["estimated_api_equivalent_usd"]["known_total"] == pytest.approx(3.5)
    assert c["estimated_api_equivalent_usd"]["total"] is None
    assert c["estimated_cost_per_strict_success_usd"] is None


def test_strata_use_prerequest_decisions_and_keep_unrun_unknown_rows():
    report = synthetic_report()
    failed = report["runs"][2]
    failed.update(strict_success=False, status="failed")
    for row in report["runs"][-3:]:
        row.update(attempted=False, strict_success=False, status="not_run")
        for field in ("actual_prompt_sha256", "context_preparation", "estimated_api_equivalent_usd", "full_task_seconds"):
            row.pop(field, None)
    value = result(report)
    assert value["unrun_assignments"] == 3 and value["attempted_assignments"] == 15
    assert value["c_prerequest_strata"]["preloaded"]["task_repeat_groups"] == 3
    assert value["c_prerequest_strata"]["preloaded"]["configurations"]["C"]["strict_successes"] == 2
    assert value["c_prerequest_strata"]["SKIP"]["task_repeat_groups"] == 2
    unknown = value["c_prerequest_strata"]["unobserved_or_inconsistent"]
    assert unknown["task_repeat_groups"] == 1
    assert all(summary["unrun"] == 1 for summary in unknown["configurations"].values())


def test_controls_require_real_matching_hashes_within_same_task_repeat():
    report = synthetic_report(4)
    report["runs"][0]["actual_prompt_sha256"] = None
    report["runs"][2]["actual_prompt_sha256"] = None
    value = result(report)
    a, b = (value["byte_identical_prompt_controls"][f"C_vs_{arm}"] for arm in ("A", "B"))
    assert a["identical_prompt_pairs"] == 4
    assert b["identical_prompt_pairs"] == 3
    assert a["missing_or_unobserved_prompt_hash_pairs"] == b["missing_or_unobserved_prompt_hash_pairs"] == 1
    assert a["planned_pairs"] == b["planned_pairs"] == 8
    effect = b["paired_effects"]["C_vs_B"]["estimated_api_equivalent_usd"]
    assert effect["paired_observations"] == 3
    assert effect["mean_paired_difference"] == pytest.approx(-0.1)
    assert effect["independent_task_clusters"] == 2


def test_zero_success_retains_cost_but_has_no_cost_per_success_ratio():
    report = synthetic_report()
    for row in report["runs"]:
        if row["configuration"] == "C":
            row.update(strict_success=False, status="failed")
    c = result(report)["primary_intent_to_treat"]["configurations"]["C"]
    assert c["estimated_api_equivalent_usd"]["total"] == pytest.approx(4.2)
    assert c["strict_successes"] == 0 and c["estimated_cost_per_strict_success_usd"] is None


@pytest.mark.parametrize("mutation", ["missing_row", "duplicate", "negative_cost", "nonfinite_time"])
def test_incomplete_or_invalid_assignment_sets_are_rejected(mutation):
    report = synthetic_report()
    planned = len(report["runs"])
    if mutation == "missing_row":
        report["runs"].pop()
    elif mutation == "duplicate":
        report["runs"][-1] = copy.deepcopy(report["runs"][-2])
    elif mutation == "negative_cost":
        report["runs"][0]["estimated_api_equivalent_usd"] = -1
    else:
        report["runs"][0]["full_task_seconds"] = float("nan")
    with pytest.raises(ValueError):
        analyze(report, expected_planned=planned)


def test_cli_writes_fresh_artifacts_and_preserves_source_and_prior_outputs(tmp_path):
    source, output = tmp_path / "synthetic-report.json", tmp_path / "analysis"
    source.write_text(json.dumps(synthetic_report()))
    original = source.read_bytes()
    args = ["--report", str(source), "--output", str(output), "--expected-planned", "18"]
    assert main(args) == 0
    written = output.with_suffix(".json").read_bytes()
    value = json.loads(written)
    assert value["source_report_sha256"] == hashlib.sha256(original).hexdigest()
    assert source.read_bytes() == original
    rendered = output.with_suffix(".md").read_text()
    assert "oracle paths" in rendered and "cannot establish better source selection" in rendered
    assert "not actual billed charges" in rendered
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert output.with_suffix(".json").read_bytes() == written
    assert markdown(value) == rendered


@pytest.mark.parametrize("unsafe", ["symlink", "duplicate_json_keys"])
def test_cli_rejects_unsafe_json_without_writing_outputs(tmp_path: Path, unsafe):
    original = tmp_path / "original.json"
    original.write_text(json.dumps(synthetic_report()))
    source = tmp_path / "source.json"
    if unsafe == "symlink":
        source.symlink_to(original)
    else:
        source.write_text('{"runs":[],"runs":[]}')
    output = tmp_path / "untouched"
    with pytest.raises(SystemExit) as error:
        main(["--report", str(source), "--output", str(output), "--expected-planned", "18"])
    assert error.value.code == 2
    assert not output.with_suffix(".json").exists() and not output.with_suffix(".md").exists()
