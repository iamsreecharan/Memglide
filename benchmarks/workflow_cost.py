"""Three-arm workflow accounting from observed fresh-run usage, never billing.

Parse each attempted native stream once through the conservative estimator. Pair
views reference the same attempts; their exposure must never be added as spend.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from benchmarks import estimate_cost as cost

ARMS = ("A", "B", "C")
COMPARISONS = (("C", "A"), ("C", "B"), ("B", "A"))
COST_KEY = "native_reported_price_equivalent_usd"
COST_KEYS = (COST_KEY, "possible_write_price_lower_usd", "possible_write_price_upper_usd")
PROMOTION_POLICY = {
    "version": "workflow-promotion-1",
    "candidate": "C",
    "baselines": ["A", "B"],
    "benefit_population": "explicit_focus; provided-context controls excluded",
    "required_repeats": [1, 2],
    "correctness": "Every original candidate assignment succeeds with verified source/native fidelity",
    "coverage": "Complete unique matched A/B/C triplets for every task and repeat; no missing or unknown cost",
    "nonregression": "Focused cost per attempt and full execution time: candidate mean AND median <= each baseline overall AND in each repeat",
    "consequence": "Failure or unknown evidence keeps support explicitly optional; no default promotion",
    "interpretation": "Prespecified finite-corpus acceptance rule, not statistical proof or a production guarantee",
}


def _saving(baseline: Any, candidate: Any) -> float | None:
    if cost._number(baseline) and cost._number(candidate) and baseline > 0:
        return (baseline - candidate) / baseline * 100
    return None


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = cost.aggregate(rows)
    for key in ("observed_command_items", "observed_file_change_items"):
        result["metrics"][key] = cost.summarize([row["metrics"].get(key) for row in rows])
    return result


def _proxies(path: Path, complete: bool) -> dict[str, int | None]:
    empty: dict[str, int | None] = {
        "observed_command_items": None,
        "observed_file_change_items": None,
    }
    if not complete or path.is_symlink():
        return empty
    try:
        items: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            item = event.get("item")
            if event.get("type") != "item.completed" or not isinstance(item, dict):
                continue
            kind = item.get("type")
            if kind not in {"command_execution", "file_change"}:
                continue
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier:
                return empty
            items[identifier] = kind
        return {
            "observed_command_items": sum(kind == "command_execution" for kind in items.values()),
            "observed_file_change_items": sum(kind == "file_change" for kind in items.values()),
        }
    except (OSError, ValueError, TypeError, AttributeError):
        return empty


def _fidelity(row: dict[str, Any]) -> bool:
    evidence = row.get("raw_fidelity", {})
    if not isinstance(evidence, dict):
        return False
    preparation = evidence.get("preload_treatment_fidelity")
    native = evidence.get("native_execution_validity")
    return (
        evidence.get("treatment_valid") is True
        and isinstance(preparation, dict)
        and preparation.get("valid") is True
        and isinstance(native, dict)
        and native.get("valid") is True
    )


def _pair_reasons(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[str]:
    if len(left) != 1 or len(right) != 1:
        return ["A unique original assignment is absent in one or both arms"]
    reasons = []
    if not all(_fidelity(row) for row in (*left, *right)):
        reasons.append("Source/treatment/native fidelity is not established")
    for name, lengths in (("starting_commit", (40, 64)), ("common_task_prompt_sha256", (64,))):
        a = (left[0].get("raw_fidelity") or {}).get(name)
        b = (right[0].get("raw_fidelity") or {}).get(name)
        if (
            not isinstance(a, str)
            or len(a) not in lengths
            or any(character not in "0123456789abcdef" for character in a)
            or a != b
        ):
            reasons.append("Missing or different " + name)
    return reasons


def _comparison(
    rows: list[dict[str, Any]], candidate: str, baseline: str, source_unchanged: bool
) -> dict[str, Any]:
    arms = {
        arm: _aggregate([row for row in rows if row["configuration"] == arm])
        for arm in (baseline, candidate)
    }
    index: defaultdict[tuple[str, int], defaultdict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        if row["configuration"] in arms:
            index[row["task_id"], row["repeat"]][row["configuration"]].append(row)
    pairs = []
    for (task_id, repeat), entries in sorted(index.items()):
        left, right = entries[baseline], entries[candidate]
        reasons = _pair_reasons(left, right)
        if not source_unchanged:
            reasons.append("Unchanged frozen source is not established")
        a, b = (
            _aggregate(values)["cost_statistics"][COST_KEY]["total"] for values in (left, right)
        )
        available = not reasons and cost._number(a) and cost._number(b)
        pairs.append(
            {
                "task_id": task_id,
                "repeat": repeat,
                "baseline_run_ids": [row["run_id"] for row in left],
                "candidate_run_ids": [row["run_id"] for row in right],
                "valid": not reasons,
                "reasons": reasons,
                "candidate_minus_baseline_usd": b - a if available else None,
                "saving_percent": _saving(a, b) if available else None,
            }
        )
    a_cost, b_cost = (arms[arm]["cost_per_successful_task_usd"] for arm in (baseline, candidate))
    deltas = [pair["candidate_minus_baseline_usd"] for pair in pairs]
    return {
        "baseline": baseline,
        "candidate": candidate,
        "configurations": arms,
        "cost_per_success_saving_percent": {
            key: _saving(a_cost[key], b_cost[key]) for key in COST_KEYS
        },
        "write_uncertainty_saving_range": {
            "lower_saving_percent": _saving(
                a_cost["possible_write_price_lower_usd"], b_cost["possible_write_price_upper_usd"]
            ),
            "upper_saving_percent": _saving(
                a_cost["possible_write_price_upper_usd"], b_cost["possible_write_price_lower_usd"]
            ),
            "scope": "Independent worst-case write scenarios, not a confidence interval",
        },
        "paired_cost_delta_usd": cost.summarize(deltas),
        "paired_outcomes": {
            "candidate_cheaper": sum(cost._number(delta) and delta < 0 for delta in deltas),
            "baseline_cheaper": sum(cost._number(delta) and delta > 0 for delta in deltas),
            "equal": sum(delta == 0 for delta in deltas),
            "unavailable": sum(delta is None for delta in deltas),
        },
        "pairs": pairs,
        "view_provenance": {
            "configuration_remapping": None,
            "baseline": baseline,
            "candidate": candidate,
            "run_ids": [row["run_id"] for row in rows if row["configuration"] in arms],
            "scope": "References to already priced original attempts; not additional spend or native requests",
        },
    }


def promotion_gate(
    rows: list[dict[str, Any]],
    expected_task_ids: list[str] | None = None,
    *,
    source_unchanged: bool = True,
) -> dict[str, Any]:
    reasons = []
    if not source_unchanged:
        reasons.append("Unchanged frozen source is not established")
    tasks = set(expected_task_ids or [row["task_id"] for row in rows])
    if not tasks or {row["repeat"] for row in rows} != {1, 2}:
        reasons.append("Both prespecified repeats 1 and 2 are required")
    index: defaultdict[tuple[str, int], defaultdict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        index[row["task_id"], row["repeat"]][row["configuration"]].append(row)
    for task in sorted(tasks):
        for repeat in (1, 2):
            entries = index[task, repeat]
            if set(entries) != set(ARMS) or any(len(entries[arm]) != 1 for arm in ARMS):
                reasons.append(f"Missing or duplicate original triplet: {task}/r{repeat}")
            elif any(_pair_reasons(entries[baseline], entries["C"]) for baseline in ("A", "B")):
                reasons.append(f"Unmatched source/native provenance: {task}/r{repeat}")
            elif len({entries[arm][0].get("selection_stratum") for arm in ARMS}) != 1:
                reasons.append(f"Different selection strata: {task}/r{repeat}")
    if any(not row.get("success") or not _fidelity(row) for row in rows):
        reasons.append(
            "Every original arm must complete successfully with valid source/native fidelity"
        )
    if any(
        not cost._number(value) or value < 0
        for value in (row.get("cost", {}).get(COST_KEY) for row in rows)
    ):
        reasons.append(
            "Every original arm, including provided-context controls, needs a known finite nonnegative estimated cost"
        )
    if any(
        row.get("selection_stratum") not in {"explicit_focus", "caller_context_supplied"}
        for row in rows
    ):
        reasons.append("Every task needs a declared focused or provided-control stratum")
    focused = [row for row in rows if row.get("selection_stratum") == "explicit_focus"]
    if not focused:
        reasons.append("No source-focused benefit population; controls cannot establish benefit")
    checks = []
    for baseline in ("A", "B"):
        for scope, selected in (
            ("overall", focused),
            ("repeat_1", [row for row in focused if row["repeat"] == 1]),
            ("repeat_2", [row for row in focused if row["repeat"] == 2]),
        ):
            for metric in (COST_KEY, "end_to_end_wall_seconds"):
                values = {
                    arm: [
                        row["cost"].get(metric)
                        if metric == COST_KEY
                        else row["metrics"].get(metric)
                        for row in selected
                        if row["configuration"] == arm
                    ]
                    for arm in (baseline, "C")
                }
                complete = all(
                    values[arm] and all(cost._number(value) for value in values[arm])
                    for arm in values
                )
                summaries = {arm: cost.summarize(items) for arm, items in values.items()}
                for statistic in ("mean", "median"):
                    a, c = summaries[baseline][statistic], summaries["C"][statistic]
                    passed = bool(complete and c <= a)
                    checks.append(
                        {
                            "baseline": baseline,
                            "scope": scope,
                            "metric": metric,
                            "statistic": statistic,
                            "baseline_value": a,
                            "candidate_value": c,
                            "passed": passed,
                        }
                    )
    if not all(check["passed"] for check in checks):
        reasons.append(
            "Focused cost/full-time mean or median regresses or is unavailable overall or in a repeat"
        )
    return {
        "policy": copy.deepcopy(PROMOTION_POLICY),
        "passed": not reasons,
        "reasons": reasons,
        "checks": checks,
        "action": "Eligible for review on this finite corpus"
        if not reasons
        else "Keep support explicitly optional; do not promote defaults",
        "control_exclusion": "caller_context_supplied rows affect correctness/coverage, not benefit checks",
    }


def assess(
    report: dict[str, Any], pricing: dict[str, Any], *, events_root: Path | None = None
) -> dict[str, Any]:
    if any(row.get("configuration") not in ARMS for row in report["runs"]):
        raise ValueError("Workflow accounting requires only original A/B/C configurations")
    # The shared parser accepts all raw rows. Its historical A/B summary is not
    # used here; every stream is strictly priced exactly once, including C.
    parsed = cost.assess(report, pricing, events_root=events_root)
    rows = parsed["runs"]
    raw_by_id = {row["run_id"]: row for row in report["runs"] if row.get("attempted")}
    for row in rows:
        raw = raw_by_id[row["run_id"]]
        row["raw_fidelity"] = copy.deepcopy(
            {
                name: raw.get(name)
                for name in (
                    "treatment_valid",
                    "preload_treatment_fidelity",
                    "native_execution_validity",
                    "starting_commit",
                    "common_task_prompt_sha256",
                    "native_command",
                )
            }
        )
        path = (
            events_root / row["run_id"] / "events.jsonl"
            if events_root is not None
            else Path(raw["artifacts"]) / "events.jsonl"
        )
        row["metrics"].update(_proxies(path, row["native_usage"]["coverage_complete"]))
    source_unchanged = report.get("metadata", {}).get("source_unchanged_during_experiment") is True
    configurations = {
        arm: _aggregate([row for row in rows if row["configuration"] == arm]) for arm in ARMS
    }
    strata = {
        field: {
            stratum: {
                arm: _aggregate(
                    [
                        row
                        for row in rows
                        if row["configuration"] == arm and str(row.get(field)) == stratum
                    ]
                )
                for arm in ARMS
            }
            for stratum in sorted({str(row.get(field)) for row in rows})
        }
        for field in ("repeat", "selection_stratum", "language", "task_kind")
    }
    return {
        "assessment_version": "workflow-cost-1",
        "generated_at": datetime.now(UTC).isoformat(),
        "comparison_kind": report.get("comparison_kind"),
        "configuration_labels": copy.deepcopy(report.get("configuration_labels", {})),
        "pricing": copy.deepcopy(pricing),
        "actual_billed_cost_usd": None,
        "formula": parsed["formula"],
        "unique_attempts": len(rows),
        "accounting_provenance": {
            "native_usage_parse_count": len(rows),
            "configuration_remapping": None,
            "all_attempt_run_ids": [row["run_id"] for row in rows],
            "pair_exposure_is_additional_spend": False,
        },
        "configurations": configurations,
        "strata": strata,
        "comparisons": {
            candidate + "_over_" + baseline: _comparison(
                rows, candidate, baseline, source_unchanged
            )
            for candidate, baseline in COMPARISONS
        },
        "promotion_gate": promotion_gate(
            rows,
            [task["id"] for task in report.get("tasks", [])] or None,
            source_unchanged=source_unchanged,
        ),
        "runs": rows,
        "failures": [row for row in rows if not row["success"]],
        "limitations": [
            "Every dollar amount is a standard API list-price equivalent, not actual provider billing or a subscription charge.",
            "Cache writes reported as zero may reflect an upstream default. Conservative possible-write ranges are scenarios, not confidence intervals.",
            "Each native attempt is priced once. All failures and unknown attempts remain in per-arm numerators; unknown usage prevents a complete total or cost per success.",
            "Cached input is included in total input and reasoning is included in output; neither is billed twice.",
            "Completed command/file-change items are invocation/patch proxies, not provider model calls, individual file reads or unique edits. Missing telemetry remains null.",
            "Local CPU is a sampled lower bound; child RSS can double-count shared pages and omits parent indexing. Neither has a fabricated dollar rate.",
            "Provided-context controls are excluded from source-benefit promotion checks. Repeat consistency is descriptive, not statistical proof.",
            "Fresh small synthetic tasks with uncontrolled provider/OS caches do not establish production, long-term memory or universal efficiency gains.",
        ],
    }


def markdown(assessment: dict[str, Any]) -> str:
    def value(number: Any, places: int = 6) -> str:
        return f"{number:,.{places}f}" if cost._number(number) else "unavailable"

    lines = [
        "# Three-arm workflow cost assessment",
        "",
        "; ".join(f"{arm}: {assessment['configuration_labels'].get(arm, arm)}" for arm in ARMS)
        + ".",
        "",
        "**All dollars are API-price equivalents, not actual bills.** Each original attempt is priced once; pair views are references, not additional spend.",
        "",
        "| Arm | Attempts | Successful assignments | USD / successful task | Total estimated USD |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        summary = assessment["configurations"][arm]
        lines.append(
            f"| {arm} | {summary['attempts']} | {summary['successful_assignments']} | {value(summary['cost_per_successful_task_usd'][COST_KEY])} | {value(summary['cost_statistics'][COST_KEY]['total'])} |"
        )
    lines += [
        "",
        "| Comparison | Cost / success saving % | Possible-write saving range % | Paired outcomes |",
        "|---|---:|---|---|",
    ]
    for name, comparison in assessment["comparisons"].items():
        sensitivity = comparison["write_uncertainty_saving_range"]
        lines.append(
            f"| {name} | {value(comparison['cost_per_success_saving_percent'][COST_KEY], 3)} | {value(sensitivity['lower_saving_percent'], 3)} to {value(sensitivity['upper_saving_percent'], 3)} | {json.dumps(comparison['paired_outcomes'], sort_keys=True)} |"
        )
    gate = assessment["promotion_gate"]
    lines += [
        "",
        f"Prespecified promotion gate passed: **{gate['passed']}**. {gate['action']}.",
        "",
        *["- " + reason for reason in gate["reasons"]],
        "",
        "## Individual attempts",
        "",
        "| Run | Arm | Success | Input | Cached | Output | Estimated USD | Full seconds |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in assessment["runs"]:
        m = row["metrics"]
        lines.append(
            f"| {row['run_id']} | {row['configuration']} | {row['success']} | {value(m.get('input_tokens'), 0)} | {value(m.get('cached_input_tokens'), 0)} | {value(m.get('output_tokens'), 0)} | {value(row['cost'][COST_KEY])} | {value(m.get('end_to_end_wall_seconds'), 3)} |"
        )
    lines += [
        "",
        "## Per-arm descriptive metrics",
        "",
        "| Metric | Arm | Mean | Median | p95 | Complete total | Missing |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        for name, summary in assessment["configurations"][arm]["metrics"].items():
            lines.append(
                f"| {name} | {arm} | {value(summary['mean'], 3)} | {value(summary['median'], 3)} | {value(summary['p95'], 3)} | {value(summary['total'], 3)} | {summary['missing']} |"
            )
    lines += [
        "",
        "All per-task pairs, repeats, language/task/selection strata, gate checks, component charges and source/native fidelity are retained in JSON.",
        "",
        *["- " + limitation for limitation in assessment["limitations"]],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--events-root", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    arguments = parser.parse_args(argv)
    paths = [arguments.output_prefix.with_suffix(suffix) for suffix in (".json", ".md")]
    if any(path.exists() for path in paths):
        raise FileExistsError("Choose a new output prefix; existing evidence is immutable")
    report_bytes, pricing_bytes = arguments.report.read_bytes(), arguments.pricing.read_bytes()
    document = json.loads(pricing_bytes)
    result = assess(
        json.loads(report_bytes),
        document.get("pricing", document),
        events_root=arguments.events_root,
    )
    result["provenance"] = {
        "primary_report_sha256": cost.digest(report_bytes),
        "pricing_document_sha256": cost.digest(pricing_bytes),
        "workflow_estimator_sha256": cost.digest(Path(__file__).read_bytes()),
        "shared_estimator_sha256": cost.digest(Path(cost.__file__).read_bytes()),
    }
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths[1].write_text(markdown(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "unique_attempts": result["unique_attempts"],
                "failures": len(result["failures"]),
                "promotion_gate_passed": result["promotion_gate"]["passed"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
