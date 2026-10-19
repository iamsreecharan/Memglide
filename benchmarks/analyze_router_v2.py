"""Descriptive analysis of frozen formal results; never dispatches model requests."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from benchmarks import run_automatic as base

LIMITS = [
    "Primary results include every planned assignment, failure and unrun row; no original is replaced.",
    "Costs are API-price equivalents, not actual billed charges. Missing attempted cost makes complete cost per success unavailable; known subtotals remain disclosed.",
    "C strata use preparation decisions made before model execution, never task outcomes. Different strata contain different tasks and are descriptive, not randomized causal contrasts.",
    "Identical-prompt controls require matching non-null SHA-256 values within the same task and repeat. Their outcome differences cannot establish better source selection; provider/cache variation and local preparation overhead may remain.",
    "B receives author-known source paths. Human discovery time for those oracle paths is unmeasured and excluded; this is an informative baseline, not a complete automatic workflow cost.",
    "Task-cluster bootstrap intervals describe this finite corpus, not all repositories. Cache equivalence, avoided investigation and actual billed savings are unproven.",
]


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = base.formal_report(rows)
    return {key: result[key] for key in ("configurations", "paired_effects", "actual_billed_cost_usd")}


def _mode(row: dict[str, Any]) -> str:
    preparation = row.get("context_preparation") or {}
    if not isinstance(preparation, dict):
        return "unobserved_or_inconsistent"
    selection = preparation.get("automatic_selection") or {}
    if not isinstance(selection, dict):
        return "unobserved_or_inconsistent"
    decision = selection.get("decision")
    if decision == "SKIP" and preparation.get("mode") == "passthrough":
        return "SKIP"
    if decision in ("FOCUSED_SOURCE", "FULL_SOURCE") and preparation.get("mode") == "preloaded":
        return "preloaded"
    return "unobserved_or_inconsistent"


def _hash(row: dict[str, Any]) -> str | None:
    value = row.get("actual_prompt_sha256")
    return value if row["attempted"] and isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) else None


def analyze(report: dict[str, Any], *, expected_planned: int = 72) -> dict[str, Any]:
    """Preserve primary intent-to-treat outcomes and add prespecified diagnostics."""
    rows = report.get("runs") if isinstance(report, dict) else None
    if type(expected_planned) is not int or expected_planned < 3 or expected_planned % 3 or not isinstance(rows, list) or len(rows) != expected_planned:
        raise ValueError("Report must contain every expected planned assignment, including unrun rows")
    grouped: dict[tuple[str, int], dict[str, dict[str, Any]]] = {}
    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("task_id"), str) or not row["task_id"]
            or type(row.get("repeat")) is not int or row["repeat"] < 1
            or row.get("configuration") not in ("A", "B", "C")
            or type(row.get("attempted")) is not bool
            or type(row.get("strict_success")) is not bool
            or not isinstance(row.get("status"), str) or not row["status"]
            or (row["strict_success"] and not row["attempted"])
        ):
            raise ValueError("Invalid planned assignment metadata")
        for metric in ("full_task_seconds", "estimated_api_equivalent_usd"):
            value = row.get(metric)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError("Observed duration/cost must be nonnegative finite numbers or null")
        key = (row["task_id"], row["repeat"])
        members = grouped.setdefault(key, {})
        if row["configuration"] in members:
            raise ValueError("Duplicate planned assignment")
        members[row["configuration"]] = row
    if any(set(members) != {"A", "B", "C"} for members in grouped.values()):
        raise ValueError("Every planned task/repeat must retain all three arms")
    modes = {key: _mode(members["C"]) for key, members in grouped.items()}
    strata = {}
    for mode in ("preloaded", "SKIP", "unobserved_or_inconsistent"):
        selected = [row for row in rows if modes[(row["task_id"], row["repeat"])] == mode]
        strata[mode] = {"task_repeat_groups": sum(value == mode for value in modes.values()), **_summary(selected)}
    controls = {}
    for baseline in ("A", "B"):
        counts: Counter[str] = Counter()
        selected = []
        for members in grouped.values():
            left, right = _hash(members[baseline]), _hash(members["C"])
            if left is None or right is None:
                counts["missing_or_unobserved_prompt_hash_pairs"] += 1
            elif left != right:
                counts["different_prompt_pairs"] += 1
            else:
                counts["identical_prompt_pairs"] += 1
                selected.extend((members[baseline], members["C"]))
        controls[f"C_vs_{baseline}"] = {
            "planned_pairs": len(grouped),
            **{key: counts[key] for key in ("identical_prompt_pairs", "different_prompt_pairs", "missing_or_unobserved_prompt_hash_pairs")},
            **_summary(selected),
        }
    return {
        "version": "router-v2-analysis-1", "expected_planned_assignments": expected_planned,
        "planned_assignments": len(rows), "attempted_assignments": sum(row["attempted"] for row in rows),
        "unrun_assignments": sum(not row["attempted"] for row in rows),
        "runs": rows, "primary_intent_to_treat": _summary(rows),
        "c_prerequest_mode_counts": {mode: sum(value == mode for value in modes.values()) for mode in strata},
        "c_prerequest_strata": strata, "byte_identical_prompt_controls": controls,
        "actual_billed_cost_usd": None, "limitations": LIMITS,
    }


def markdown(value: dict[str, Any]) -> str:
    lines = ["# Router v2 formal analysis", "", "All original assignments and raw individual outcomes remain in the accompanying JSON.", ""]
    lines += ["| Primary arm | Planned | Attempted | Unrun | Strict successes | Estimated USD/success | Mean seconds | Median seconds |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for arm, summary in value["primary_intent_to_treat"]["configurations"].items():
        lines.append(f"| {arm} | {summary['planned']} | {summary['attempted']} | {summary['unrun']} | {summary['strict_successes']} | {summary['estimated_cost_per_strict_success_usd']} | {summary['full_task_seconds']['mean']} | {summary['full_task_seconds']['median']} |")
    lines += ["", "| C preparation stratum | Task/repeat groups | C attempted | C successes | C estimated USD/success |", "|---|---:|---:|---:|---:|"]
    for mode, stratum in value["c_prerequest_strata"].items():
        c = stratum["configurations"]["C"]
        lines.append(f"| {mode} | {stratum['task_repeat_groups']} | {c['attempted']} | {c['strict_successes']} | {c['estimated_cost_per_strict_success_usd']} |")
    lines += ["", "| Identical-prompt control | Matching pairs | Missing hashes | Different prompts | Metric | Mean paired difference | Median paired difference | Bootstrap 95% mean interval |", "|---|---:|---:|---:|---|---:|---:|---|"]
    for name, control in value["byte_identical_prompt_controls"].items():
        for metric, effect in control["paired_effects"][name].items():
            lines.append(f"| {name} | {control['identical_prompt_pairs']} | {control['missing_or_unobserved_prompt_hash_pairs']} | {control['different_prompt_pairs']} | {metric} | {effect['mean_paired_difference']} | {effect['median_paired_difference']} | {effect['mean_difference_task_cluster_bootstrap_95_percent_interval']} |")
    lines += ["", "Negative paired differences favor C for cost/time; missing values remain unavailable. Complete per-task effects, excluded pairs, telemetry coverage, failed-attempt costs and sensitivity bounds are in JSON.", "", *["- " + item for item in LIMITS], ""]
    return "\n".join(lines)


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="fresh output filename prefix")
    parser.add_argument("--expected-planned", type=int, default=72)
    args = parser.parse_args(argv)
    try:
        if args.report.is_symlink() or not args.report.is_file() or args.report.stat().st_size > 64_000_000:
            raise ValueError("Input must be a bounded regular JSON report")
        raw = args.report.read_bytes()
        report = json.loads(raw, object_pairs_hook=_unique)
        result = analyze(report, expected_planned=args.expected_planned)
        result["source_report_sha256"] = hashlib.sha256(raw).hexdigest()
        destinations = (Path(str(args.output) + ".json"), Path(str(args.output) + ".md"))
        if any(path.exists() or path.is_symlink() for path in destinations):
            raise ValueError("Output artifacts must be fresh; prior results are never overwritten")
        texts = (json.dumps(result, indent=2, allow_nan=False) + "\n", markdown(result))
        for path, content in zip(destinations, texts, strict=True):
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as error:
        parser.exit(2, f"analysis error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
