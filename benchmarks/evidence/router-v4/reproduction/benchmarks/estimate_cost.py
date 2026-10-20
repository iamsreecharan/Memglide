"""Reproducible API-price equivalents from native Codex usage, never billing.

Read only the supported native JSONL usage events, independently of the primary
benchmark parser. Cached reads and writes are exclusive subsets of total input;
reasoning is a subset of output. Unknown attempts never become zero-cost runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeGuard

BASE_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens")
EXTRA_KEYS = ("cache_write_input_tokens", "reasoning_output_tokens")
USAGE_KEYS = BASE_KEYS + EXTRA_KEYS
RATE_KEYS = ("uncached_input", "cached_input", "cache_write_input", "output")
MILLION = Decimal(1_000_000)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _count(value: Any) -> TypeGuard[int]:
    return type(value) is int and value >= 0


def _number(value: Any) -> TypeGuard[int | float]:
    return type(value) in (int, float) and math.isfinite(value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON object key")
        value[key] = item
    return value


def parse_native_usage(content: str) -> dict[str, Any]:
    """Validate lifecycle framing and every completed turn's native usage.

    A failed or unfinished turn can incur unreported usage. Its whole-attempt
    cost remains unknown, while already completed turns remain visible. Multiple
    native completed-turn counters are thread-cumulative. Multiple totals cannot
    establish fresh per-attempt spend without a verified baseline/reset history,
    so they remain unknown rather than being summed. Optional fields stay unknown.
    """
    errors: list[str] = []
    events = []
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line, object_pairs_hook=_unique_object)
            if not isinstance(value, dict) or not isinstance(value.get("type"), str):
                raise ValueError("not an event object")
            events.append(value)
        except (ValueError, TypeError):
            errors.append(f"line {line_number}: invalid JSON event")
    if not events or events[0].get("type") != "thread.started":
        errors.append("Stream must begin with thread.started")
    thread_seen = False
    active = False
    completed: list[dict[str, Any]] = []
    failed_turns = 0
    for index, event in enumerate(events):
        kind = event["type"]
        if kind == "thread.started":
            if (
                thread_seen
                or index != 0
                or not isinstance(event.get("thread_id"), str)
                or not event["thread_id"]
            ):
                errors.append("Invalid or repeated thread.started")
            thread_seen = True
        elif kind == "turn.started":
            if not thread_seen or active:
                errors.append("turn.started outside a fresh turn boundary")
            active = True
        elif kind == "turn.completed":
            if not active:
                errors.append("turn.completed without a matching turn.started")
            active = False
            usage = event.get("usage")
            if not isinstance(usage, dict):
                errors.append("Completed turn omitted its usage object")
                completed.append(dict.fromkeys(USAGE_KEYS))
                continue
            row: dict[str, Any] = {key: usage.get(key) for key in USAGE_KEYS}
            for key in BASE_KEYS:
                if not _count(row[key]):
                    errors.append(f"Completed turn has invalid {key}")
            for key in EXTRA_KEYS:
                if key in usage and not _count(row[key]):
                    errors.append(f"Completed turn has invalid {key}")
            if all(_count(row[key]) for key in BASE_KEYS):
                if row["cached_input_tokens"] > row["input_tokens"]:
                    errors.append("Cached input exceeds total input")
                if _count(row["cache_write_input_tokens"]) and (
                    row["cached_input_tokens"] + row["cache_write_input_tokens"]
                    > row["input_tokens"]
                ):
                    errors.append("Cached reads plus writes exceed total input")
                if _count(row["reasoning_output_tokens"]) and (
                    row["reasoning_output_tokens"] > row["output_tokens"]
                ):
                    errors.append("Reasoning output exceeds total output")
            completed.append(row)
        elif kind == "turn.failed":
            failed_turns += 1
            if not active:
                errors.append("turn.failed without a matching turn.started")
            active = False
            errors.append("Failed turn may have unreported billable usage")
        elif kind in {"item.started", "item.updated", "item.completed"}:
            if not active:
                errors.append("Item event outside an active turn")
        elif kind == "error":
            errors.append("Native stream emitted an error event")
        else:
            errors.append(f"Unsupported native event type: {kind}")
    if active or not events or events[-1]["type"] != "turn.completed":
        errors.append("Stream lacks a completed terminal turn")
    if not completed:
        errors.append("No completed turn usage")
    if len(completed) > 1:
        errors.append("Multiple thread-cumulative totals require verified baseline accounting")
    observed = {
        key: completed[-1][key] if completed and _count(completed[-1][key]) else None
        for key in USAGE_KEYS
    }
    complete = not errors
    return {
        "coverage_complete": complete,
        "errors": errors,
        "event_count": len(events),
        "completed_turns": len(completed),
        "failed_turns": failed_turns,
        "completed_turn_usage": completed,
        "observed_completed_turn_usage": observed,
        "usage": observed if complete else dict.fromkeys(USAGE_KEYS),
        "cache_write_reporting": (
            "Native-reported values; CLI/provider decoding may default omitted upstream "
            "cache writes to zero. A reported zero does not prove the provider supplied zero."
        ),
    }


def validate_pricing(pricing: dict[str, Any]) -> dict[str, Decimal]:
    if not isinstance(pricing.get("model"), str) or not pricing["model"]:
        raise ValueError("Pricing requires an exact model identifier")
    if pricing.get("service_tier") not in {"standard", "default"}:
        raise ValueError("Only explicitly requested standard/default service is supported")
    if not _count(pricing.get("context_threshold_tokens")):
        raise ValueError("Pricing requires a nonnegative short-context threshold")
    rates = pricing.get("per_million_usd")
    if not isinstance(rates, dict):
        raise ValueError("Missing per-million USD rates")
    parsed = {}
    for key in RATE_KEYS:
        value = rates.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValueError(f"Missing or invalid {key} rate")
        try:
            rate = Decimal(str(value))
        except ArithmeticError as error:
            raise ValueError(f"Invalid {key} rate") from error
        if not rate.is_finite() or rate < 0:
            raise ValueError(f"Invalid {key} rate")
        parsed[key] = rate
    return parsed


def _price(usage: dict[str, int], writes: int, rates: dict[str, Decimal]) -> float:
    ordinary = usage["input_tokens"] - usage["cached_input_tokens"] - writes
    return float(
        (
            ordinary * rates["uncached_input"]
            + usage["cached_input_tokens"] * rates["cached_input"]
            + writes * rates["cache_write_input"]
            + usage["output_tokens"] * rates["output"]
        )
        / MILLION
    )


def price_usage(parsed: dict[str, Any], pricing: dict[str, Any]) -> dict[str, Any]:
    rates = validate_pricing(pricing)
    result: dict[str, Any] = {
        "actual_billed_cost_usd": None,
        "native_reported_price_equivalent_usd": None,
        "possible_write_price_lower_usd": None,
        "possible_write_price_upper_usd": None,
        "native_reported_components_usd": dict.fromkeys(RATE_KEYS),
        "reason": None,
        "cache_write_assumption": (
            "Point uses native-reported cache writes. Sensitivity permits every noncached "
            "input token to be a cache write, because upstream-omitted writes may decode as zero."
        ),
    }
    if parsed.get("coverage_complete") is not True:
        result["reason"] = "Whole-attempt usage is incomplete; unknown spend is not zero"
        return result
    usage = parsed["usage"]
    if usage["input_tokens"] > pricing["context_threshold_tokens"]:
        result["reason"] = (
            "Run input exceeds short-request threshold; native turn totals do not identify "
            "per-request long-context pricing. No short-rate estimate substituted."
        )
        return result
    noncached = usage["input_tokens"] - usage["cached_input_tokens"]
    writes = usage["cache_write_input_tokens"]
    if writes is not None:
        result["native_reported_price_equivalent_usd"] = _price(usage, writes, rates)
        counts = {
            "uncached_input": noncached - writes,
            "cached_input": usage["cached_input_tokens"],
            "cache_write_input": writes,
            "output": usage["output_tokens"],
        }
        result["native_reported_components_usd"] = {
            key: float(counts[key] * rates[key] / MILLION) for key in RATE_KEYS
        }
    else:
        result["reason"] = "Native stream omitted cache-write counts; only scenarios are available"
    lower_reported_writes = writes if writes is not None else 0
    scenarios = [_price(usage, lower_reported_writes, rates), _price(usage, noncached, rates)]
    result["possible_write_price_lower_usd"] = min(scenarios)
    result["possible_write_price_upper_usd"] = max(scenarios)
    return result


def summarize(values: list[Any], *, additive: bool = True) -> dict[str, Any]:
    observed = sorted(value for value in values if _number(value))
    return {
        "n": len(observed),
        "missing": len(values) - len(observed),
        "mean": statistics.mean(observed) if observed else None,
        "median": statistics.median(observed) if observed else None,
        "min": min(observed) if observed else None,
        "max": max(observed) if observed else None,
        "p95": observed[max(0, math.ceil(len(observed) * 0.95) - 1)] if observed else None,
        "known_total": sum(observed) if observed and additive else None,
        "total": sum(observed) if observed and len(observed) == len(values) and additive else None,
    }


def _success(row: dict[str, Any]) -> bool:
    return (
        row.get("status") == "completed"
        and row.get("grader", {}).get("success") is True
        and row.get("treatment_valid") is True
        and row.get("preload_treatment_fidelity", {}).get("valid") is True
        and row.get("native_execution_validity", {}).get("valid") is True
    )


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    assignments = defaultdict(list)
    for row in rows:
        assignments[(row["task_id"], row["repeat"], row["configuration"])].append(row)
    successful = sum(any(row["success"] for row in attempts) for attempts in assignments.values())
    keys = (
        "native_reported_price_equivalent_usd",
        "possible_write_price_lower_usd",
        "possible_write_price_upper_usd",
    )
    costs = {key: summarize([row["cost"][key] for row in rows]) for key in keys}
    return {
        "attempts": len(rows),
        "assignments": len(assignments),
        "successful_assignments": successful,
        "successful_attempts": sum(row["success"] for row in rows),
        "completion_rate": successful / len(assignments) if assignments else None,
        "cost_statistics": costs,
        "cost_per_successful_task_usd": {
            key: value["total"] / successful if value["total"] is not None and successful else None
            for key, value in costs.items()
        },
        "cost_denominator": "Successful distinct (task, repeat, configuration) assignments",
        "cost_numerator": "All attempted runs supplied in report.runs, including supplied failures/retries",
        "actual_billed_cost_usd": None,
        "native_reported_cost_components_usd": {
            key: summarize([row["cost"]["native_reported_components_usd"][key] for row in rows])
            for key in RATE_KEYS
        },
        "metrics": {
            key: summarize(
                [row["metrics"].get(key) for row in rows], additive="rss_bytes" not in key
            )
            for key in (
                *USAGE_KEYS,
                "uncached_input_tokens",
                "ordinary_uncached_input_tokens",
                "end_to_end_wall_seconds",
                "total_observed_local_cpu_seconds",
                "process_tree_peak_rss_bytes",
                "mcp_calls",
                "observed_file_read_commands",
                "observed_repeated_read_commands",
                "test_count",
            )
        },
    }


def _saving(a: Any, b: Any) -> float | None:
    return (a - b) / a * 100 if _number(a) and _number(b) and a > 0 else None


def assess(
    report: dict[str, Any], pricing: dict[str, Any], *, events_root: Path | None = None
) -> dict[str, Any]:
    """Derive a new assessment without modifying the source report or raw events."""
    validate_pricing(pricing)
    metadata = report.get("metadata", {})
    settings = metadata.get("frozen_manifest", {}).get("settings", {})
    if metadata.get("model") != pricing["model"]:
        raise ValueError("Exact benchmark model does not match pricing model")
    if settings.get("requested_service_tier") != "default":
        raise ValueError("Frozen requested service tier does not match pricing")
    rows = []
    run_ids = set()
    for raw in report["runs"]:
        if not raw.get("attempted"):
            continue
        run_id = raw["run_id"]
        if run_id in run_ids or Path(run_id).name != run_id or run_id in {".", ".."}:
            raise ValueError("Duplicate or unsafe run identifier")
        run_ids.add(run_id)
        path = (
            events_root / run_id / "events.jsonl"
            if events_root is not None
            else Path(raw["artifacts"]) / "events.jsonl"
        )
        content = path.read_bytes() if path.is_file() and not path.is_symlink() else None
        try:
            parsed = (
                parse_native_usage(content.decode("utf-8"))
                if content is not None
                else {
                    "coverage_complete": False,
                    "errors": ["Native events artifact is missing or a symlink"],
                    "usage": dict.fromkeys(USAGE_KEYS),
                }
            )
        except UnicodeDecodeError:
            parsed = {
                "coverage_complete": False,
                "errors": ["Native events artifact is not valid UTF-8"],
                "usage": dict.fromkeys(USAGE_KEYS),
            }
        command = raw.get("native_command")
        fresh = (
            isinstance(command, list)
            and len(command) > 1
            and command[1] == "exec"
            and "--ephemeral" in command
            and "resume" not in command[2:]
            and raw.get("execution_outcome_unknown") is not True
        )
        if not fresh:
            parsed["coverage_complete"] = False
            parsed["errors"].append(
                "Fresh ephemeral native execution is not established; resumed cumulative usage "
                "cannot be charged as this attempt's incremental cost"
            )
            parsed["usage"] = dict.fromkeys(USAGE_KEYS)
        primary_usage = raw.get("telemetry", {}).get("usage", {})
        reconciliation = all(
            parsed["usage"].get(key) == primary_usage.get(key) for key in BASE_KEYS
        )
        if not reconciliation:
            parsed["coverage_complete"] = False
            parsed["errors"].append("Independent I/C/O totals differ from primary report")
            parsed["usage"] = dict.fromkeys(USAGE_KEYS)
        cost = price_usage(parsed, pricing)
        usage = parsed["usage"]
        metrics = {**raw.get("metrics", {}), **usage}
        metrics["uncached_input_tokens"] = (
            usage["input_tokens"] - usage["cached_input_tokens"]
            if usage["input_tokens"] is not None and usage["cached_input_tokens"] is not None
            else None
        )
        metrics["ordinary_uncached_input_tokens"] = (
            metrics["uncached_input_tokens"] - usage["cache_write_input_tokens"]
            if metrics["uncached_input_tokens"] is not None
            and usage["cache_write_input_tokens"] is not None
            else None
        )
        metrics["test_count"] = raw.get("grader", {}).get("test_count")
        rows.append(
            {
                "run_id": run_id,
                "task_id": raw["task_id"],
                "repeat": raw["repeat"],
                "configuration": raw["configuration"],
                "language": raw.get("language"),
                "task_kind": raw.get("task_kind"),
                "selection_stratum": raw.get("selection_stratum"),
                "order": raw.get("order"),
                "status": raw.get("status"),
                "success": _success(raw),
                "grader_success": raw.get("grader", {}).get("success"),
                "attempt_errors": raw.get("errors", []),
                "events_sha256": digest(content) if content is not None else None,
                "native_usage": parsed,
                "primary_usage_reconciled": reconciliation,
                "metrics": metrics,
                "cost": cost,
            }
        )
    configurations = {
        arm: aggregate([row for row in rows if row["configuration"] == arm]) for arm in ("A", "B")
    }
    pair_index: defaultdict[tuple[str, int], defaultdict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        pair_index[(row["task_id"], row["repeat"])][row["configuration"]].append(row)
    pairs = []
    for (task_id, repeat), arms in sorted(pair_index.items()):
        totals = {arm: aggregate(arms.get(arm, [])) for arm in ("A", "B")}
        a = totals["A"]["cost_statistics"]["native_reported_price_equivalent_usd"]["total"]
        b = totals["B"]["cost_statistics"]["native_reported_price_equivalent_usd"]["total"]
        pairs.append(
            {
                "task_id": task_id,
                "repeat": repeat,
                "arms": totals,
                "saving_percent": _saving(a, b),
                "B_minus_A_usd": b - a if _number(a) and _number(b) else None,
            }
        )
    cost_keys = configurations["A"]["cost_per_successful_task_usd"]
    savings = {
        key: _saving(
            configurations["A"]["cost_per_successful_task_usd"][key],
            configurations["B"]["cost_per_successful_task_usd"][key],
        )
        for key in cost_keys
    }
    a_cost = configurations["A"]["cost_per_successful_task_usd"]
    b_cost = configurations["B"]["cost_per_successful_task_usd"]
    sensitivity = {
        "lower_saving_percent": _saving(
            a_cost["possible_write_price_lower_usd"], b_cost["possible_write_price_upper_usd"]
        ),
        "upper_saving_percent": _saving(
            a_cost["possible_write_price_upper_usd"], b_cost["possible_write_price_lower_usd"]
        ),
        "scope": "Independent worst-case write attribution in the two arms; not a confidence interval",
    }
    strata: dict[str, dict[str, dict[str, Any]]] = {}
    for field in ("selection_stratum", "task_kind", "language"):
        strata[field] = {}
        for stratum in sorted({str(row.get(field)) for row in rows}):
            stratum_arms = {
                arm: aggregate(
                    [
                        row
                        for row in rows
                        if row["configuration"] == arm and str(row.get(field)) == stratum
                    ]
                )
                for arm in ("A", "B")
            }
            strata[field][stratum] = {
                "configurations": stratum_arms,
                "native_reported_cost_per_success_saving_percent": _saving(
                    stratum_arms["A"]["cost_per_successful_task_usd"][
                        "native_reported_price_equivalent_usd"
                    ],
                    stratum_arms["B"]["cost_per_successful_task_usd"][
                        "native_reported_price_equivalent_usd"
                    ],
                ),
            }
    return {
        "assessment_version": "codex-cost-1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "comparison_kind": report.get("comparison_kind"),
        "configuration_labels": report.get("configuration_labels", {}),
        "pricing": pricing,
        "actual_billed_cost_usd": None,
        "billing_unavailable_reason": "Native Codex JSONL does not expose attributable provider invoices or subscription charges",
        "formula": "((I-C-W)*uncached_rate + C*cached_rate + W*write_rate + O*output_rate)/1,000,000; R is already included in O",
        "configurations": configurations,
        "cost_per_success_saving_percent": savings,
        "write_uncertainty_saving_range": sensitivity,
        "paired_cost_delta_usd": summarize([pair["B_minus_A_usd"] for pair in pairs]),
        "strata": strata,
        "paired_cost_outcomes": {
            "B_cheaper": sum(_number(p["B_minus_A_usd"]) and p["B_minus_A_usd"] < 0 for p in pairs),
            "A_cheaper": sum(_number(p["B_minus_A_usd"]) and p["B_minus_A_usd"] > 0 for p in pairs),
            "equal": sum(p["B_minus_A_usd"] == 0 for p in pairs),
            "unavailable": sum(p["B_minus_A_usd"] is None for p in pairs),
        },
        "runs": rows,
        "pairs": pairs,
        "failures": [row for row in rows if not row["success"]],
        "limitations": [
            "All USD values are published API-price equivalents, not measured billing or subscription charges.",
            "Native-reported cache writes may default upstream omissions to zero; show conservative write sensitivity, not certainty about provider cache creation.",
            "No point estimate is invented when writes are absent, usage is incomplete, or short-context pricing cannot be established.",
            "Every attempted row supplied in report.runs contributes to the numerator; any unknown supplied attempt makes the whole-arm total and cost per success unavailable. Callers must include every attempt; this parser cannot discover omitted retries or supplementary ledgers.",
            "Reasoning output is included in output, and cached reads/writes are included in total input; none are counted twice.",
            "Ten fresh tasks, one balanced trial per arm, synthetic small repositories, and uncontrolled backend/OS caches limit generalization; the range is not statistical uncertainty.",
            "Local CPU/RSS/time overhead is reported but has no attributable dollar rate and is not included as fabricated spending. Peak RSS totals have no physical interpretation.",
            "Requested default service tier is frozen; realized provider tier/routing and actual per-request model calls are unavailable from this stream.",
            "This estimator requires fresh ephemeral native executions. Resumed or multiple-turn cumulative counters require separate verified baseline/delta accounting and are not summed as incremental spend.",
        ],
    }


def markdown(assessment: dict[str, Any]) -> str:
    def value(number: Any, places: int = 6) -> str:
        return f"{number:,.{places}f}" if _number(number) else "unavailable"

    lines = [
        "# Ten-task Codex / Memglide cost assessment",
        "",
        "A is standard Codex. B is Memglide compact-prefix source preparation. "
        "All dollar amounts below are **API-price equivalents, not actual bills**.",
        "",
        "Native usage is independently parsed and reconciled with the original report. "
        "Cached reads and writes are exclusive input subsets; reasoning is already output. "
        "Failed attempts remain in the cost numerator.",
        "",
        "```text",
        assessment["formula"],
        "```",
        "",
        f"Model: `{assessment['pricing']['model']}`; requested tier: "
        f"`{assessment['pricing']['service_tier']}`. Short-request threshold: "
        f"{assessment['pricing']['context_threshold_tokens']:,} input tokens.",
        "",
        "| Per million tokens | USD |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {key} | ${rate} |" for key, rate in assessment["pricing"]["per_million_usd"].items()
    )
    lines += ["", "| Measure | A: Codex | B: Memglide |", "|---|---:|---:|"]
    for label, getter in (
        (
            "Successful assignments / attempts",
            lambda a: f"{a['successful_assignments']} / {a['attempts']}",
        ),
        (
            "Total estimated model USD",
            lambda a: value(a["cost_statistics"]["native_reported_price_equivalent_usd"]["total"]),
        ),
        (
            "Mean estimated USD / attempt",
            lambda a: value(a["cost_statistics"]["native_reported_price_equivalent_usd"]["mean"]),
        ),
        (
            "Median estimated USD / attempt",
            lambda a: value(a["cost_statistics"]["native_reported_price_equivalent_usd"]["median"]),
        ),
        (
            "Estimated USD / successful task",
            lambda a: value(
                a["cost_per_successful_task_usd"]["native_reported_price_equivalent_usd"]
            ),
        ),
        (
            "Possible-write lower USD / successful task",
            lambda a: value(a["cost_per_successful_task_usd"]["possible_write_price_lower_usd"]),
        ),
        (
            "Possible-write upper USD / successful task",
            lambda a: value(a["cost_per_successful_task_usd"]["possible_write_price_upper_usd"]),
        ),
    ):
        lines.append(
            f"| {label} | {getter(assessment['configurations']['A'])} | {getter(assessment['configurations']['B'])} |"
        )
    saving = assessment["cost_per_success_saving_percent"]["native_reported_price_equivalent_usd"]
    limits = assessment["write_uncertainty_saving_range"]
    lines += [
        "",
        f"Native-reported price-equivalent saving per successful task: **{value(saving, 2)}%** "
        "(positive means B costs less).",
        f"Conservative possible-write saving range: {value(limits['lower_saving_percent'], 2)}% "
        f"to {value(limits['upper_saving_percent'], 2)}%. This is a scenario range, not a confidence interval.",
        "",
        "| Run | Success | Input | Cached | Writes | Output | Estimated USD | Full seconds |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(assessment["runs"], key=lambda r: r.get("order") or 0):
        m = row["metrics"]
        lines.append(
            f"| {row['run_id']} | {row['success']} | {value(m.get('input_tokens'), 0)} | "
            f"{value(m.get('cached_input_tokens'), 0)} | {value(m.get('cache_write_input_tokens'), 0)} | "
            f"{value(m.get('output_tokens'), 0)} | "
            f"{value(row['cost']['native_reported_price_equivalent_usd'])} | "
            f"{value(m.get('end_to_end_wall_seconds'), 3)} |"
        )
    lines += ["", "| Metric (mean / median / total) | A | B |", "|---|---:|---:|"]
    for key in assessment["configurations"]["A"]["metrics"]:
        cells = []
        for arm in ("A", "B"):
            m = assessment["configurations"][arm]["metrics"][key]
            cells.append(" / ".join(value(m[k], 3) for k in ("mean", "median", "total")))
        lines.append(f"| {key} | {cells[0]} | {cells[1]} |")
    lines += ["", "| Estimated cost component (total USD) | A | B |", "|---|---:|---:|"]
    for key in RATE_KEYS:
        cells = [
            value(
                assessment["configurations"][arm]["native_reported_cost_components_usd"][key][
                    "total"
                ]
            )
            for arm in ("A", "B")
        ]
        lines.append(f"| {key} | {cells[0]} | {cells[1]} |")
    lines += [
        "",
        "| Descriptive stratum | A USD / success | B USD / success | Saving % |",
        "|---|---:|---:|---:|",
    ]
    for field, groups in assessment["strata"].items():
        for name, group in groups.items():
            cells = [
                value(
                    group["configurations"][arm]["cost_per_successful_task_usd"][
                        "native_reported_price_equivalent_usd"
                    ]
                )
                for arm in ("A", "B")
            ]
            lines.append(
                f"| {field}: {name} | {cells[0]} | {cells[1]} | "
                f"{value(group['native_reported_cost_per_success_saving_percent'], 2)} |"
            )
    lines += ["", "| Task | B − A estimated USD | Saving % |", "|---|---:|---:|"]
    lines.extend(
        f"| {pair['task_id']} | {value(pair['B_minus_A_usd'])} | {value(pair['saving_percent'], 2)} |"
        for pair in assessment["pairs"]
    )
    lines += [
        "",
        f"Paired cost outcomes: `{json.dumps(assessment['paired_cost_outcomes'], sort_keys=True)}`.",
        "",
        f"Failed/unknown attempts: {len(assessment['failures'])}.",
        "",
    ]
    lines.extend(f"- {item}" for item in assessment["limitations"])
    lines += [
        "",
        "Full pricing citations, source hashes, every run, paired deltas, missing values and failures are retained in the companion JSON.",
        "",
    ]
    for source in assessment["pricing"].get("provenance", []):
        lines += [
            f"- Pricing source: {source['url']} (retrieved {source.get('retrieved_at_utc', 'unknown')}; SHA-256 `{source.get('body_sha256', 'unknown')}`)."
        ]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--events-root", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()
    report_bytes, pricing_bytes = args.report.read_bytes(), args.pricing.read_bytes()
    pricing_document = json.loads(pricing_bytes)
    pricing = pricing_document.get("pricing", pricing_document)
    result = assess(json.loads(report_bytes), pricing, events_root=args.events_root)
    result["provenance"] = {
        "primary_report_sha256": digest(report_bytes),
        "pricing_document_sha256": digest(pricing_bytes),
        "estimator_sha256": digest(Path(__file__).read_bytes()),
    }
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = (
        (".json", json.dumps(result, indent=2, ensure_ascii=False) + "\n"),
        (".md", markdown(result)),
    )
    for extension, _ in outputs:
        destination = args.output_prefix.with_suffix(extension)
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing assessment: {destination}")
    for extension, content in outputs:
        destination = args.output_prefix.with_suffix(extension)
        destination.write_text(content, encoding="utf-8")
    print(
        json.dumps(
            {
                "runs": len(result["runs"]),
                "failures": len(result["failures"]),
                "saving_percent": result["cost_per_success_saving_percent"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
