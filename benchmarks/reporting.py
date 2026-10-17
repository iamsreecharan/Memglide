"""A/B benchmark reports that retain missing telemetry and unsuccessful runs."""

from __future__ import annotations

import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONFIGURATIONS = ("A", "B")
NON_ATTEMPTS = {"not_run", "unrun", "blocked", "skipped", "prerequisite_blocked"}
METRIC_NAMES = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "model_calls",
    "mcp_calls",
    "memglide_mcp_calls",
    "observed_mcp_calls",
    "observed_memglide_mcp_calls",
    "wall_time_seconds",
    "end_to_end_wall_seconds",
    "setup_wall_seconds",
    "setup_cpu_seconds",
    "repeated_file_reads",
    "observed_file_read_commands",
    "observed_repeated_read_commands",
    "actual_cost_usd",
    "computed_cost_usd",
    "process_tree_peak_rss_bytes",
    "cpu_seconds",
    "memglide_peak_rss_bytes",
    "memglide_cpu_seconds",
    "context_freshness",
    "retrieval_completeness",
    "probe_target_path_coverage_fraction",
    "probe_expected_symbol_coverage_fraction",
)


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _metrics(run: dict[str, Any]) -> dict[str, int | float | None]:
    telemetry = run.get("telemetry") or {}
    usage = telemetry.get("usage") or {}
    overhead = run.get("overhead") or {}
    context = run.get("context_metrics") or {}
    probe = run.get("context_probe") or {}
    complete_mcp = telemetry.get("mcp_counts_complete") is True
    metrics: dict[str, Any] = {
        **{
            name: usage.get(name)
            for name in ("input_tokens", "cached_input_tokens", "output_tokens")
        },
        "model_calls": telemetry.get("model_calls"),
        "mcp_calls": telemetry.get("mcp_call_count") if complete_mcp else None,
        "memglide_mcp_calls": telemetry.get("memglide_mcp_call_count") if complete_mcp else None,
        "observed_mcp_calls": telemetry.get("mcp_call_count"),
        "observed_memglide_mcp_calls": telemetry.get("memglide_mcp_call_count"),
        "wall_time_seconds": run.get("wall_time_seconds"),
        "end_to_end_wall_seconds": run.get("end_to_end_wall_seconds"),
        "setup_wall_seconds": (run.get("setup") or {}).get("wall_seconds"),
        "setup_cpu_seconds": (run.get("setup") or {}).get("cpu_seconds"),
        "repeated_file_reads": telemetry.get("repeated_file_reads"),
        "observed_file_read_commands": telemetry.get("observed_file_read_commands"),
        "observed_repeated_read_commands": telemetry.get("observed_repeated_read_commands"),
        "actual_cost_usd": run.get("actual_cost_usd"),
        "computed_cost_usd": run.get("computed_cost_usd"),
        **{
            name: overhead.get(name)
            for name in (
                "process_tree_peak_rss_bytes",
                "cpu_seconds",
                "memglide_peak_rss_bytes",
                "memglide_cpu_seconds",
            )
        },
        "context_freshness": context.get("context_freshness"),
        "retrieval_completeness": context.get("retrieval_completeness"),
        "probe_target_path_coverage_fraction": probe.get("target_path_coverage_fraction"),
        "probe_expected_symbol_coverage_fraction": probe.get("expected_symbol_coverage_fraction"),
    }
    return {name: value if _number(value) else None for name, value in metrics.items()}


def _attempted(run: dict[str, Any]) -> bool:
    if isinstance(run.get("attempted"), bool):
        return run["attempted"]
    return run.get("status", "not_run") not in NON_ATTEMPTS


def _successful(run: dict[str, Any]) -> bool | None:
    # Only an external grader can establish completion. Agent claims are excluded.
    success = (run.get("grader") or {}).get("success")
    return success if isinstance(success, bool) else None


def _fidelity(run: dict[str, Any]) -> dict[str, Any]:
    telemetry = run.get("telemetry") or {}
    count = telemetry.get("memglide_mcp_call_count")
    if count is None:
        return {
            "valid": None,
            "memglide_invoked": None,
            "reason": "No observable MCP event stream; treatment fidelity is unknown",
        }
    complete = telemetry.get("mcp_counts_complete") is True
    invoked = count > 0 if count or complete else None
    retrievals = telemetry.get("memglide_successful_get_context_count")
    unknown_retrievals = telemetry.get("memglide_get_context_success_unknown_count")
    if run.get("configuration") == "B":
        if isinstance(run.get("compact_protocol_fidelity"), dict):
            fetches = telemetry.get("memglide_successful_fetch_context_count")
            verifications = telemetry.get("memglide_successful_verify_context_count")
            # Existing compact rows predate on-demand verification and required
            # both operations. Never reinterpret those preserved experiments.
            required = run["compact_protocol_fidelity"].get(
                "required_operations", ["fetch_context", "verify_context"]
            )
            if run.get("execution_outcome_unknown") is True:
                valid, reason = None, "Interrupted compact attempt has an unknown complete outcome"
            elif required not in (["fetch_context"], ["fetch_context", "verify_context"]):
                valid, reason = False, "Unsupported compact protocol requirement marker"
            elif (
                _number(fetches)
                and fetches > 0
                and (
                    "verify_context" not in required or _number(verifications) and verifications > 0
                )
            ):
                valid, reason = (
                    True,
                    "Observed compact source retrieval and every operation required by its frozen policy",
                )
            elif not complete:
                valid, reason = (
                    None,
                    "Compact retrieval/revalidation is unverified in an incomplete event stream",
                )
            else:
                valid, reason = (
                    False,
                    "Compact protocol is missing successful results required by its frozen policy",
                )
        elif _number(retrievals) and retrievals > 0:
            valid, reason = True, "Observed completed, error-free Memglide get_context result"
        elif unknown_retrievals or not complete:
            valid, reason = (
                None,
                (
                    "Successful get_context is unverified: result evidence or stream coverage is incomplete"
                ),
            )
        else:
            valid, reason = False, "No successful Memglide get_context call was observed"
    elif (telemetry.get("mcp_call_count") or 0) > 0:
        valid, reason = (
            False,
            "Unexpected MCP invocation contaminated the MCP-disabled configuration",
        )
    elif complete:
        valid, reason = True, "Complete event stream contains no MCP invocation"
    else:
        valid, reason = (
            None,
            "Incomplete event stream cannot establish absence of Memglide invocation",
        )
    return {
        "valid": valid,
        "memglide_invoked": invoked,
        "successful_get_context_calls": retrievals,
        "reason": reason,
    }


def _summary(values: list[Any]) -> dict[str, Any]:
    observed = [value for value in values if _number(value)]
    missing = len(values) - len(observed)
    return {
        "n": len(observed),
        "missing": missing,
        "mean": statistics.mean(observed) if observed else None,
        "median": statistics.median(observed) if observed else None,
        "min": min(observed) if observed else None,
        "max": max(observed) if observed else None,
        "known_total": sum(observed) if observed else None,
        "total": sum(observed) if observed and not missing else None,
    }


def _cost_per_success(
    attempted: list[dict[str, Any]],
    successful_count: int,
    metric: str,
) -> dict[str, Any]:
    costs = [run["metrics"].get(metric) for run in attempted]
    if not attempted:
        reason = "No attempted coding runs"
    elif not all(_number(cost) for cost in costs):
        reason = "Cost is unavailable for one or more attempted runs, including failed runs"
    elif successful_count == 0:
        reason = "No successfully completed tasks; cost per success is undefined"
    else:
        return {
            "value": sum(costs) / successful_count,
            "reason": None,
            "attempted_runs_in_numerator": len(attempted),
            "successful_runs_in_denominator": successful_count,
        }
    return {
        "value": None,
        "reason": reason,
        "attempted_runs_in_numerator": len(attempted),
        "successful_runs_in_denominator": successful_count,
    }


def _aggregate(runs: list[dict[str, Any]]) -> dict[str, Any]:
    attempted = [run for run in runs if run["attempted"]]
    successful_count = sum(run["successful"] is True for run in attempted)
    graded_count = sum(run["successful"] is not None for run in attempted)
    metrics = {
        name: _summary([run["metrics"].get(name) for run in attempted]) for name in METRIC_NAMES
    }
    for name, metric in metrics.items():
        metric["attempted_missing"] = metric["missing"]
        metric["planned_missing"] = len(runs) - metric["n"]
        if name.endswith("rss_bytes") or name in {
            "context_freshness",
            "retrieval_completeness",
            "probe_target_path_coverage_fraction",
            "probe_expected_symbol_coverage_fraction",
        }:
            metric["total"] = None
            metric["known_total"] = None
            metric["total_unavailable_reason"] = "This metric is not additive across runs"
    return {
        "planned_runs": len(runs),
        "attempted_runs": len(attempted),
        "not_run": len(runs) - len(attempted),
        "graded_runs": graded_count,
        "successful_runs": successful_count,
        "failed_grades": sum(run["successful"] is False for run in attempted),
        "ungraded_runs": len(attempted) - graded_count,
        "execution_status_counts": dict(Counter(run.get("status", "not_run") for run in runs)),
        "successful_task_completion_rate": successful_count / len(attempted) if attempted else None,
        "completion_rate_denominator": "All attempted runs, including ungraded execution failures",
        "graded_only_success_rate": successful_count / graded_count if graded_count else None,
        "valid_treatment_runs": sum(
            run["treatment_fidelity"]["valid"] is True for run in attempted
        ),
        "invalid_treatment_runs": sum(
            run["treatment_fidelity"]["valid"] is False for run in attempted
        ),
        "unknown_treatment_runs": sum(
            run["treatment_fidelity"]["valid"] is None for run in attempted
        ),
        "metrics": metrics,
        "actual_cost_per_successful_task_usd": _cost_per_success(
            attempted, successful_count, "actual_cost_usd"
        ),
        "computed_cost_per_successful_task_usd": _cost_per_success(
            attempted, successful_count, "computed_cost_usd"
        ),
    }


def _pairs(runs: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    indexed: dict[tuple[Any, Any], dict[str, list[dict[str, Any]]]] = {}
    for run in runs:
        key = (run.get("task_id"), run.get("repeat", 1))
        indexed.setdefault(key, {}).setdefault(run["configuration"], []).append(run)
    pairs: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for (task_id, repeat), configurations in indexed.items():
        if any(len(configurations.get(config, [])) != 1 for config in CONFIGURATIONS):
            excluded.append(
                {"task_id": task_id, "repeat": repeat, "reason": "A unique A/B pair is absent"}
            )
            continue
        first, second = (configurations[config][0] for config in CONFIGURATIONS)
        if not all(
            run["attempted"] and run["treatment_fidelity"]["valid"] is True
            for run in (first, second)
        ):
            excluded.append(
                {
                    "task_id": task_id,
                    "repeat": repeat,
                    "reason": "Both configurations must be attempted with verified treatment",
                }
            )
            continue
        identity_reasons = []
        identity = {}
        for field in ("starting_commit", "prompt_sha256"):
            a, b = first.get(field), second.get(field)
            if not isinstance(a, str) or not a or not isinstance(b, str) or not b:
                identity_reasons.append(f"Missing {field}; input equality is unverified")
            elif not all(
                len(value) in ({40, 64} if field == "starting_commit" else {64})
                and all(character in "0123456789abcdef" for character in value)
                for value in (a, b)
            ):
                identity_reasons.append(f"Invalid {field}; input equality is unverified")
            elif a != b:
                identity_reasons.append(f"Different {field}; input equality is invalid")
            else:
                identity[field] = a
        if metadata.get("source_unchanged_during_experiment") is False:
            identity_reasons.append("Memglide runtime source changed during the experiment")
        if identity_reasons:
            excluded.append(
                {
                    "task_id": task_id,
                    "repeat": repeat,
                    "reason": "; ".join(identity_reasons),
                    "identity_errors": identity_reasons,
                }
            )
            continue
        differences: dict[str, Any] = {}
        for name in METRIC_NAMES:
            a, b = first["metrics"].get(name), second["metrics"].get(name)
            differences[name] = b - a if _number(a) and _number(b) else None
        pairs.append(
            {
                "task_id": task_id,
                "repeat": repeat,
                "A_success": first["successful"],
                "B_success": second["successful"],
                "A_order": first.get("order"),
                "B_order": second.get("order"),
                "verified_input_identity": identity,
                "B_minus_A": differences,
            }
        )
    return {
        "valid_pair_count": len(pairs),
        "pairs": pairs,
        "excluded_pairs": excluded,
        "difference_definition": "B minus A; negative is less resource use, not proof of task benefit",
        "identity_scope": "Equal recorded starting commits and prompt hashes, plus verified MCP treatment. Missing identity evidence excludes a pair. Explicitly changed runtime source excludes every pair; absent runtime source attestation remains unknown.",
        "source_unchanged_during_experiment": metadata.get("source_unchanged_during_experiment"),
        "B_minus_A": {
            name: _summary([pair["B_minus_A"].get(name) for pair in pairs]) for name in METRIC_NAMES
        },
    }


def build_report(
    runs: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Build JSON-safe results without inventing data for unexecuted tasks.

    ``actual_cost_usd`` must be provider-returned billed cost. Separately computed
    pricing requires verified rates, pricing source/date, and usage in metadata.
    Missing planned runs are made explicit so failed/blocked cases stay visible.
    """
    rows = [dict(run) for run in runs]
    expected_repeats = metadata.get("repeats", 1)
    if not isinstance(expected_repeats, int) or expected_repeats < 1:
        raise ValueError("metadata.repeats must be a positive integer")
    present = {(run.get("task_id"), run.get("configuration"), run.get("repeat", 1)) for run in rows}
    for task in tasks:
        task_id = task.get("id", task.get("task_id"))
        for repeat in range(1, expected_repeats + 1):
            for configuration in CONFIGURATIONS:
                if (task_id, configuration, repeat) not in present:
                    rows.append(
                        {
                            "task_id": task_id,
                            "configuration": configuration,
                            "repeat": repeat,
                            "order": None,
                            "status": "not_run",
                            "attempted": False,
                            "errors": ["No run record; prerequisites or execution are incomplete"],
                        }
                    )
    for row in rows:
        if row.get("configuration") not in CONFIGURATIONS:
            raise ValueError("Run configuration must be A or B")
        row["attempted"] = _attempted(row)
        row["successful"] = _successful(row)
        row["treatment_fidelity"] = _fidelity(row)
        row["metrics"] = _metrics(row)

    aggregates = {
        config: _aggregate([row for row in rows if row["configuration"] == config])
        for config in CONFIGURATIONS
    }
    valid_aggregates = {
        config: _aggregate(
            [
                row
                for row in rows
                if row["configuration"] == config and row["treatment_fidelity"]["valid"] is True
            ]
        )
        for config in CONFIGURATIONS
    }
    paired = _pairs(rows, metadata)
    limitations = [
        "No savings claim follows from a shorter response or fewer returned context characters.",
        "Completed Codex turns are not the number of underlying model/API calls.",
        "Absent provider invoiced cost is null. Computed list-price cost, if supplied, is separate.",
        "Metric averages and medians use observed values; n and missing counts accompany them.",
        "Failed and ungraded attempts remain in completion-rate and cost-per-success accounting.",
        "Actual repeated filesystem reads are unavailable. Observed read-command fields are "
        "heuristics for command intent, not actual I/O measurements or guaranteed I/O lower bounds.",
        "MCP invocation is checked from tool events, independent of model self-report.",
        "B treatment fidelity requires a completed, error-free Memglide get_context result; "
        "failed calls and calls to other tools do not verify retrieval treatment.",
        "Paired comparisons require identical recorded starting commits and prompt SHA-256 values. "
        "Missing or unequal identities and explicitly changed runtime source exclude paired deltas; "
        "all raw attempts, failures and unconditional aggregates remain visible.",
        "MCP total counts are withheld for incomplete event streams; observed counts are lower bounds.",
        "Retrieval completeness and freshness require separate ground-truth observations; null is unknown.",
        "Independent target-path/symbol coverage probes are labelled proxies; they do not measure "
        "semantic completeness or establish what source context the coding model used.",
        "Sampled process CPU is an observed lower bound; sampled RSS peaks may miss short-lived "
        "processes and count shared pages repeatedly. Remote inference resources are unavailable.",
        "A/B prompt caching cannot generally be reset at the provider; run order and observed cached tokens matter.",
        "Synthetic fixture tasks do not establish performance on arbitrary production repositories.",
    ]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "tasks": tasks,
        "runs": rows,
        "aggregates": aggregates,
        "verified_treatment_aggregates": valid_aggregates,
        "paired_comparisons": paired,
        "limitations": limitations,
        "conclusions": {
            "verified_pair_count": paired["valid_pair_count"],
            "savings_claim_supported": False,
            "interpretation": (
                "No verified A/B coding pairs completed; performance and savings are undetermined."
                if not paired["valid_pair_count"]
                else "Observed results are descriptive. Assess task success, full cost coverage, treatment "
                "fidelity, sample size, cache order, and task representativeness before claiming savings."
            ),
        },
    }


def _display(value: Any) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: dict[str, Any]) -> str:
    """Render all runs, not only successful or fidelity-valid observations."""
    aggregates = report["aggregates"]
    lines = [
        "# Memglide Codex A/B benchmark",
        "",
        report["conclusions"]["interpretation"],
        "",
        "A = standard Codex. B = same Codex settings with Memglide. "
        "Success is determined by the external grader. Missing measurements are `unavailable`, not zero.",
        "",
        "## Protocol and environment",
        "",
        "```json",
        json.dumps(report["metadata"], indent=2, sort_keys=True),
        "```",
        "",
        "## Overall results (all runs)",
        "",
        "| Measure | A | B |",
        "| --- | ---: | ---: |",
    ]
    summary_fields = (
        ("Planned runs", "planned_runs"),
        ("Attempted runs", "attempted_runs"),
        ("Not run", "not_run"),
        ("Graded runs", "graded_runs"),
        ("Successful runs", "successful_runs"),
        ("Failed grades", "failed_grades"),
        ("Ungraded attempts", "ungraded_runs"),
        ("Task completion rate", "successful_task_completion_rate"),
        ("Invalid treatment runs", "invalid_treatment_runs"),
        ("Unknown treatment runs", "unknown_treatment_runs"),
    )
    for label, key in summary_fields:
        lines.append(
            f"| {label} | {_display(aggregates['A'][key])} | {_display(aggregates['B'][key])} |"
        )
    for kind, label in (
        ("actual", "Actual provider cost per success (USD)"),
        ("computed", "Computed pricing cost per success (USD)"),
    ):
        key = f"{kind}_cost_per_successful_task_usd"
        lines.append(
            f"| {label} | {_display(aggregates['A'][key]['value'])} | "
            f"{_display(aggregates['B'][key]['value'])} |"
        )
    lines.extend(
        [
            "",
            "Cost per success includes all attempted-run costs, including failures. "
            "It is unavailable when any attempted-run cost is missing or no task succeeds.",
            "",
            "## Measurements",
            "",
            "Means/medians include observed values only. Coverage columns show observed n / "
            "missing among attempted runs / missing among all planned runs. "
            "Totals are withheld when coverage is incomplete and for non-additive metrics.",
            "",
            "| Metric | A mean | A median | A n / attempted missing / planned missing | A total | B mean | B median | B n / attempted missing / planned missing | B total |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name in METRIC_NAMES:
        cells: list[str] = [name]
        for config in CONFIGURATIONS:
            metric = aggregates[config]["metrics"][name]
            cells.extend(
                [
                    _display(metric["mean"]),
                    _display(metric["median"]),
                    f"{metric['n']} / {metric['attempted_missing']} / {metric['planned_missing']}",
                    _display(metric["total"]),
                ]
            )
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "## Individual runs",
            "",
            "| Task | Config | Repeat | Order | Status | Grader success | MCP calls | Memglide calls | Treatment valid | Input | Cached | Output | Seconds | Errors |",
            "| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for run in report["runs"]:
        metrics = run["metrics"]
        values = [
            run.get("task_id"),
            run["configuration"],
            run.get("repeat", 1),
            run.get("order"),
            run.get("status"),
            run["successful"],
            metrics["mcp_calls"],
            metrics["memglide_mcp_calls"],
            run["treatment_fidelity"]["valid"],
            metrics["input_tokens"],
            metrics["cached_input_tokens"],
            metrics["output_tokens"],
            metrics["wall_time_seconds"],
            "; ".join(str(e) for e in run.get("errors", [])),
        ]
        lines.append("| " + " | ".join(_display(value) for value in values) + " |")
    lines.extend(
        [
            "",
            "### Per-run costs, reads, and local overhead",
            "",
            "CPU values are sampled process CPU seconds (an observed lower bound); "
            "RSS values are sampled peaks in bytes. Short-lived processes may be missed. "
            "RSS may count shared pages more than once. "
            "Process-tree measurements include Codex and its observed children. "
            "Memglide-specific measurements cover only processes identified by the runner. "
            "Actual read counts are unavailable; command-intent proxy metrics appear separately.",
            "",
            "| Task / configuration / repeat | Model calls | Repeated reads | Actual USD | Computed USD | Tree peak RSS | Tree CPU sec | Memglide peak RSS | Memglide CPU sec | Freshness | Completeness |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for run in report["runs"]:
        metrics = run["metrics"]
        values = [f"{run.get('task_id')} / {run['configuration']} / {run.get('repeat', 1)}"]
        values.extend(
            metrics.get(key)
            for key in (
                "model_calls",
                "repeated_file_reads",
                "actual_cost_usd",
                "computed_cost_usd",
                "process_tree_peak_rss_bytes",
                "cpu_seconds",
                "memglide_peak_rss_bytes",
                "memglide_cpu_seconds",
                "context_freshness",
                "retrieval_completeness",
            )
        )
        lines.append("| " + " | ".join(_display(value) for value in values) + " |")
    lines.extend(
        [
            "",
            "### MCP invocation evidence",
            "",
            "Calls are deduplicated by CLI item ID across started/updated/completed events. "
            "A call that starts and fails is still an observed invocation. "
            "Enabled server configuration alone does not establish invocation.",
            "",
        ]
    )
    for run in report["runs"]:
        calls = (run.get("telemetry") or {}).get("mcp_calls", [])
        if calls:
            descriptions = [
                f"{call.get('server')}.{call.get('tool')} "
                f"(status={call.get('status')}, completed={call.get('completed')})"
                for call in calls
            ]
            lines.append(
                f"- {_display(run.get('task_id'))} / {run['configuration']} / repeat "
                f"{run.get('repeat', 1)}: " + "; ".join(descriptions)
            )
    if not any((run.get("telemetry") or {}).get("mcp_calls") for run in report["runs"]):
        lines.append("No MCP invocations are present in the available raw event streams.")
    paired = report["paired_comparisons"]
    lines.extend(
        [
            "",
            "## Paired differences",
            "",
            f"Verified attempted A/B pairs: **{paired['valid_pair_count']}**. "
            "Differences are B minus A. Failed tasks remain in paired observations.",
            "",
            "| Metric | Mean difference | Median difference | Pairs with measurements | Missing |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, metric in paired["B_minus_A"].items():
        lines.append(
            f"| {name} | {_display(metric['mean'])} | {_display(metric['median'])} | "
            f"{metric['n']} | {metric['missing']} |"
        )
    if paired["excluded_pairs"]:
        lines.extend(
            ["", "Excluded pairs (still retained in the individual and overall results):", ""]
        )
        lines.extend(
            f"- {_display(pair['task_id'])} repeat {pair['repeat']}: {pair['reason']}"
            for pair in paired["excluded_pairs"]
        )
    lines.extend(["", "## Failures and treatment fidelity", ""])
    failures = [
        run
        for run in report["runs"]
        if run["successful"] is not True or run["treatment_fidelity"]["valid"] is not True
    ]
    if not failures:
        lines.append("Every recorded run passed its external grader and treatment check.")
    for run in failures:
        lines.append(
            f"- {_display(run.get('task_id'))} / {run['configuration']} / repeat "
            f"{run.get('repeat', 1)}: status {_display(run.get('status'))}; grader "
            f"success {_display(run['successful'])}; "
            f"{run['treatment_fidelity']['reason']}. "
            + "; ".join(str(error) for error in run.get("errors", []))
        )
    lines.extend(["", "## Evidence and limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    lines.extend(
        [
            "",
            "Full per-run grader output, raw-event paths, process measurements, "
            "unavailable reasons, and task definitions are retained in the accompanying JSON report.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: dict[str, Any], json_path: str | Path, markdown_path: str | Path) -> None:
    json_path, markdown_path = Path(json_path), Path(markdown_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
