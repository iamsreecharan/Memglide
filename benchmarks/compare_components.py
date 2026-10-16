"""Compare retained independent MCP probes without implying a Codex benefit.

The original observations are embedded verbatim. Pairing requires matching
fixture commits, target declarations, task prompts, and actual retrieval settings.
Missing evidence is not replaced with zero and invalid pairs have no deltas.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import statistics
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# name, nested source path, whether an increase is desirable
METRICS = (
    ("target_file_coverage", ("natural_prompt_retrieval", "target_file_coverage_fraction"), True),
    (
        "expected_symbol_coverage",
        ("natural_prompt_retrieval", "expected_symbol_coverage_fraction"),
        True,
    ),
    (
        "declaration_visible_coverage",
        ("natural_prompt_retrieval", "expected_declaration_visible_fraction"),
        True,
    ),
    ("natural_hashes_current", ("natural_prompt_hash_freshness", "all_hashes_current"), True),
    ("old_passport_detected_edit", ("controlled_freshness", "old_passport_detected_edit"), True),
    ("updated_target_sha_matches", ("controlled_freshness", "updated_target_sha_matches"), True),
    (
        "updated_edit_marker_visible",
        ("controlled_freshness", "updated_target_contains_edit_marker"),
        True,
    ),
    (
        "updated_evidence_hashes_current",
        ("controlled_freshness", "updated_evidence_hashes", "all_hashes_current"),
        True,
    ),
    ("index_wall_seconds", ("index", "wall_seconds"), False),
    ("index_client_cpu_seconds", ("index", "client_cpu_seconds"), False),
    ("mcp_transport_wall_seconds", ("mcp_transport_wall_seconds",), False),
    (
        "natural_retrieval_wall_seconds",
        ("_derived", "natural_retrieval_wall_seconds"),
        False,
    ),
    ("server_sampled_cpu_seconds", ("local_server_overhead", "sampled_cpu_seconds"), False),
    (
        "server_sampled_peak_rss_bytes",
        ("local_server_overhead", "sampled_peak_rss_bytes"),
        False,
    ),
)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def capture_provenance(root: Path = ROOT) -> dict[str, Any]:
    """Capture public source hashes before running a candidate probe.

    This does not attest an earlier process. Reconstructed historical metadata
    must be explicitly marked as reconstructed rather than runtime observation.
    """
    source_files = {
        str(path.relative_to(root)): _digest(path.read_bytes())
        for path in sorted((root / "src/memglide").rglob("*.py"))
    }
    measurement_files = {
        str(path.relative_to(root)): _digest(path.read_bytes())
        for path in (root / "benchmarks/probe.py", root / "benchmarks/corpus.py")
        if path.is_file()
    }
    try:
        head = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.PIPE
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--", "src/memglide"],
            text=True,
            stderr=subprocess.PIPE,
        ).splitlines()
    except (OSError, subprocess.CalledProcessError):
        head, dirty = None, None
    return {
        "captured_at": datetime.now(UTC).isoformat(),
        "attestation": "captured_source_state_before_probe",
        "git_head": head,
        "source_dirty_entries": dirty,
        "source_files": source_files,
        "source_tree_sha256": _digest(json.dumps(source_files, sort_keys=True).encode()),
        "measurement_files": measurement_files,
        "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state",
    }


def _read_artifact(path: str, artifact_base: Path) -> dict[str, Any] | None:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = artifact_base / candidate
    # Reports are data. An artifact pointer must not turn comparison into an
    # arbitrary host-file reader, including through a symlink outside its root.
    if not candidate.resolve().is_relative_to(artifact_base.resolve()):
        return None
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _identity(result: dict[str, Any], artifact_base: Path) -> tuple[dict[str, Any], list[str]]:
    retrieval = result.get("natural_prompt_retrieval", {})
    identity: dict[str, Any] = {
        "language": result.get("language"),
        "baseline_commit": result.get("baseline_commit"),
        "expected_target_files": retrieval.get("expected_target_files"),
        "expected_symbols": retrieval.get("expected_symbols"),
    }
    # An explicit identity can be captured by a harness without local artifacts.
    # Existing reports instead attest these fields from the actual SDK requests.
    supplied = result.get("probe_identity", {})
    records = []
    session_task = None
    for call in result.get("mcp_calls", []):
        artifact = _read_artifact(call["artifact"], artifact_base) if call.get("artifact") else None
        if artifact is None:
            continue
        arguments = artifact.get("arguments", {})
        if call.get("name") == "start_session":
            session_task = arguments.get("task")
        if call.get("name") == "get_context":
            records.append({key: arguments.get(key) for key in ("query", "level", "budget")})
    if records:
        identity["retrieval_requests"] = records
        identity["session_task"] = session_task
        identity["settings_evidence"] = "retained_actual_sdk_arguments"
    else:
        identity["retrieval_requests"] = supplied.get("retrieval_requests")
        identity["session_task"] = supplied.get("session_task")
        identity["settings_evidence"] = "explicit_harness_identity" if supplied else "unavailable"
    missing = [
        key
        for key in (
            "language",
            "baseline_commit",
            "expected_target_files",
            "expected_symbols",
            "retrieval_requests",
            "session_task",
        )
        if identity.get(key) is None or identity.get(key) == []
    ]
    errors = [f"missing_identity:{key}" for key in missing]
    requests = identity.get("retrieval_requests") or []
    if any(
        request.get(key) is None for request in requests for key in ("query", "level", "budget")
    ):
        errors.append("incomplete_retrieval_settings")
    if requests and identity.get("session_task") != requests[0].get("query"):
        errors.append("session_task_differs_from_natural_query")
    return identity, errors


def _metric(result: dict[str, Any] | None, path: tuple[str, ...]) -> float | int | None:
    if result is None:
        return None
    if path[0] == "_derived":
        call = next(
            (item for item in result.get("mcp_calls", []) if item.get("name") == "get_context"),
            {},
        )
        value = call.get("wall_seconds")
    else:
        value: Any = result
        for key in path:
            value = value.get(key) if isinstance(value, dict) else None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)) and math.isfinite(value):
        return value
    return None


def _distribution(values: list[float | int | None]) -> dict[str, Any]:
    measured = [item for item in values if item is not None]
    return {
        "count": len(measured),
        "missing": len(values) - len(measured),
        "mean": statistics.mean(measured) if measured else None,
        "median": statistics.median(measured) if measured else None,
        "min": min(measured) if measured else None,
        "max": max(measured) if measured else None,
    }


def _index(results: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    indexed, errors = {}, []
    for position, result in enumerate(results):
        task_id = result.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"missing_task_id_at_position:{position}")
        elif task_id in indexed:
            errors.append(f"duplicate_task_id:{task_id}")
        else:
            indexed[task_id] = result
    return indexed, errors


def compare_reports(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    artifact_base: Path = ROOT,
    baseline_provenance: dict[str, Any] | None = None,
    candidate_provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Retain every observation and calculate deltas only for attested pairs."""
    before, baseline_errors = _index(baseline.get("results", []))
    after, candidate_errors = _index(candidate.get("results", []))
    errors = [f"baseline:{item}" for item in baseline_errors]
    errors.extend(f"candidate:{item}" for item in candidate_errors)
    provenance = {
        "baseline": baseline_provenance or baseline.get("provenance"),
        "candidate": candidate_provenance or candidate.get("provenance"),
    }
    old_measurement = (provenance["baseline"] or {}).get("measurement_files")
    new_measurement = (provenance["candidate"] or {}).get("measurement_files")
    if old_measurement and new_measurement and old_measurement != new_measurement:
        errors.append("measurement_source_files_changed")
    task_ids = sorted(before.keys() | after.keys())
    pairs, regressions = [], []
    for task_id in task_ids:
        old, new = before.get(task_id), after.get(task_id)
        reasons = []
        if old is None:
            reasons.append("missing_baseline_task")
        if new is None:
            reasons.append("missing_candidate_task")
        old_identity, old_errors = _identity(old or {}, artifact_base)
        new_identity, new_errors = _identity(new or {}, artifact_base)
        reasons.extend(f"baseline:{item}" for item in old_errors)
        reasons.extend(f"candidate:{item}" for item in new_errors)
        for key in old_identity.keys() - {"settings_evidence"}:
            if old_identity[key] != new_identity[key]:
                reasons.append(f"changed_identity:{key}")
        if baseline_errors or candidate_errors:
            reasons.append("ambiguous_report_task_identity")
        if "measurement_source_files_changed" in errors:
            reasons.append("measurement_source_files_changed")
        measurements = {}
        pair_regressions = []
        for name, path, higher_better in METRICS:
            old_value, new_value = _metric(old, path), _metric(new, path)
            delta = (
                new_value - old_value
                if not reasons and old_value is not None and new_value is not None
                else None
            )
            regression = delta is not None and (delta < 0 if higher_better else delta > 0)
            measurements[name] = {
                "baseline": old_value,
                "candidate": new_value,
                "candidate_minus_baseline": delta,
                "higher_is_better": higher_better,
                "regression": regression,
            }
            if regression:
                entry = {"task_id": task_id, "metric": name, **measurements[name]}
                regressions.append(entry)
                pair_regressions.append(name)
        if not reasons and old.get("status") == "passed" and new.get("status") != "passed":
            entry = {
                "task_id": task_id,
                "metric": "component_status",
                "baseline": old.get("status"),
                "candidate": new.get("status"),
                "regression": True,
            }
            regressions.append(entry)
            pair_regressions.append("component_status")
        pairs.append(
            {
                "task_id": task_id,
                "comparable": not reasons,
                "invalid_reasons": reasons,
                "baseline_identity": old_identity,
                "candidate_identity": new_identity,
                "baseline_status": old.get("status") if old else None,
                "candidate_status": new.get("status") if new else None,
                "baseline_error": old.get("error") if old else None,
                "candidate_error": new.get("error") if new else None,
                "measurements": measurements,
                "regression_metrics": pair_regressions,
            }
        )
    warnings = []
    for arm, source in provenance.items():
        if not source:
            warnings.append(f"{arm} source version was not recorded; source attribution is limited")
        elif "reconstruct" in str(source.get("attestation", "")).lower():
            warnings.append(f"{arm} source provenance is reconstructed, not a runtime attestation")
    if not task_ids:
        errors.append("no_tasks_observed")
    aggregates = {}
    for name, path, higher_better in METRICS:
        aggregates[name] = {
            "higher_is_better": higher_better,
            "baseline_all_observed": _distribution(
                [_metric(result, path) for result in baseline.get("results", [])]
            ),
            "candidate_all_observed": _distribution(
                [_metric(result, path) for result in candidate.get("results", [])]
            ),
            "paired_candidate_minus_baseline": _distribution(
                [pair["measurements"][name]["candidate_minus_baseline"] for pair in pairs]
            ),
        }
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": "Independent MCP component before/after comparison; NOT live Codex A/B",
        "comparison_valid": not errors and bool(pairs) and all(p["comparable"] for p in pairs),
        "errors": errors,
        "warnings": warnings,
        "provenance": provenance,
        "attestations": {
            "same_task_id_set": set(before) == set(after)
            and not baseline_errors
            and not candidate_errors,
            "all_pair_fixture_prompt_targets_and_settings_match": bool(pairs)
            and all(pair["comparable"] for pair in pairs),
            "measurement_source_hashes_match": (
                old_measurement == new_measurement if old_measurement and new_measurement else None
            ),
            "baseline_source_attestation": (provenance["baseline"] or {}).get("attestation"),
            "candidate_source_attestation": (provenance["candidate"] or {}).get("attestation"),
            "comparison_valid_scope": "Paired request/fixture compatibility, not statistical significance, complete source attribution, or proof of coding benefit",
        },
        "methodology": {
            "pairing": "Exact task ID, language, immutable fixture commit, expected declarations, session prompt and actual retrieval query/level/budget sequence",
            "coverage": "Declared target-file and declaration visibility proxies; not semantic completeness or coding success",
            "resources": "Single sequential observations, not randomized repeated performance trials. Sampled CPU is an observed lower bound; sampled RSS may double-count shared pages. Every numerical increase in time/CPU/RSS is listed as an observed regression, without claiming statistical significance.",
            "source_provenance": "Source capture and historical reconstruction are distinguished; unknown versions remain unknown",
            "caching": "Fresh databases per probe; provider cache is irrelevant because no model is invoked. Host filesystem caches are uncontrolled.",
            "token_budget": "Configured estimated-token budget; not measured or billed model tokens",
        },
        "summary": {
            "baseline_tasks_observed": len(baseline.get("results", [])),
            "candidate_tasks_observed": len(candidate.get("results", [])),
            "task_union": len(task_ids),
            "comparable_pairs": sum(pair["comparable"] for pair in pairs),
            "invalid_pairs": sum(not pair["comparable"] for pair in pairs),
            "tasks_with_regressions": sorted({entry["task_id"] for entry in regressions}),
            "regression_observations": len(regressions),
        },
        "aggregates": aggregates,
        "paired_results": pairs,
        "all_regressions": regressions,
        "unavailable": {
            "actual_model_input_tokens": None,
            "actual_model_cached_input_tokens": None,
            "actual_model_output_tokens": None,
            "actual_model_calls": None,
            "actual_model_cost_usd": None,
            "cost_per_successful_coding_task": None,
            "coding_task_success_rate": None,
            "semantic_context_completeness": None,
        },
        "baseline_observations": copy.deepcopy(baseline),
        "candidate_observations": copy.deepcopy(candidate),
    }


def _format(value: Any) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Independent MCP component before/after comparison",
        "",
        "These real SDK probes are **not live Codex A/B runs**. They establish no token savings, monetary savings, coding success rate, cost per completed task, or semantic context completeness. Those measurements remain unavailable.",
        "",
        f"Comparison validity: **{report['comparison_valid']}**. Observed {summary['baseline_tasks_observed']} baseline and {summary['candidate_tasks_observed']} candidate tasks; {summary['comparable_pairs']} comparable pairs and {summary['invalid_pairs']} invalid pairs. Invalid or unavailable pairs have no computed deltas. Both complete input reports, including their original summaries and failures, are embedded in the JSON.",
        "",
        "Source provenance:",
        "",
    ]
    for arm, source in report["provenance"].items():
        source = source or {}
        lines.append(
            f"- {arm}: {_format(source.get('attestation'))}; git HEAD `{_format(source.get('git_head'))}`; source digest `{_format(source.get('source_tree_sha256'))}`."
        )
    for warning in report["warnings"]:
        lines.append(f"- Limitation: {warning}.")
    for error in report["errors"]:
        lines.append(f"- Invalid comparison: `{_format(error)}`.")
    lines += ["", "Protocol and interpretation:", ""]
    lines.extend(f"- {value}." for value in report["methodology"].values())
    lines += [
        "",
        "All observed values are summarized below; paired deltas use only matching tasks and available measurements. A negative delta favors the candidate for runtime and resources; a positive delta favors the candidate for coverage and freshness. Counts and missing measurements are explicit.",
        "",
        "| Metric | Baseline n/missing | Mean | Median | Candidate n/missing | Mean | Median | Paired delta n/missing | Mean delta | Median delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, values in report["aggregates"].items():
        old, new, delta = (
            values["baseline_all_observed"],
            values["candidate_all_observed"],
            values["paired_candidate_minus_baseline"],
        )
        lines.append(
            f"| {name} | {old['count']}/{old['missing']} | {_format(old['mean'])} | {_format(old['median'])} | {new['count']}/{new['missing']} | {_format(new['mean'])} | {_format(new['median'])} | {delta['count']}/{delta['missing']} | {_format(delta['mean'])} | {_format(delta['median'])} |"
        )
    lines += [
        "",
        "Every task and any retained failure:",
        "",
        "| Task | Comparable | Baseline / candidate status | File coverage before / after | Declaration visible before / after | Natural hashes before / after | Regression metrics |",
        "|---|---|---|---|---|---|---|",
    ]
    for pair in report["paired_results"]:
        metrics = pair["measurements"]

        def both(name: str) -> str:
            return f"{_format(metrics[name]['baseline'])} / {_format(metrics[name]['candidate'])}"

        lines.append(
            f"| {pair['task_id']} | {pair['comparable']} | {_format(pair['baseline_status'])} / {_format(pair['candidate_status'])} | {both('target_file_coverage')} | {both('declaration_visible_coverage')} | {both('natural_hashes_current')} | {', '.join(pair['regression_metrics']) or 'none observed'} |"
        )
        if pair["invalid_reasons"]:
            lines += [
                "",
                f"Invalid pair `{pair['task_id']}`: {_format(pair['invalid_reasons'])}.",
                "",
            ]
        if pair["baseline_error"] or pair["candidate_error"]:
            lines += [
                "",
                f"Retained failure `{pair['task_id']}`: baseline {_format(pair['baseline_error'])}; candidate {_format(pair['candidate_error'])}.",
                "",
            ]
    lines += [
        "",
        f"All {summary['regression_observations']} observed regressions (including every runtime/resource increase):",
        "",
        "| Task | Metric | Baseline | Candidate | Candidate minus baseline |",
        "|---|---|---:|---:|---:|",
    ]
    for entry in report["all_regressions"]:
        lines.append(
            f"| {entry['task_id']} | {entry['metric']} | {_format(entry['baseline'])} | {_format(entry['candidate'])} | {_format(entry.get('candidate_minus_baseline'))} |"
        )
    if not report["all_regressions"]:
        lines.append("| none observed | — | — | — | — |")
    lines += [
        "",
        "Full per-task settings, source hash manifests, min/max distributions, measurements, deltas, invalid-pair reasons, input reports and all failures are retained in the companion JSON. Faster component queries do not establish faster or cheaper completed coding tasks.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-base", type=Path, default=ROOT)
    parser.add_argument("--baseline-provenance", type=Path)
    parser.add_argument("--candidate-provenance", type=Path)
    args = parser.parse_args()
    destinations = {args.output.with_suffix(suffix).resolve() for suffix in (".json", ".md")}
    if destinations & {args.baseline.resolve(), args.candidate.resolve()}:
        parser.error("--output must preserve both input reports; choose a different output stem")

    def load_provenance(path: Path, explicit: Path | None) -> dict[str, Any] | None:
        target = explicit or path.with_suffix(".provenance.json")
        return json.loads(target.read_text()) if target.is_file() else None

    report = compare_reports(
        json.loads(args.baseline.read_text()),
        json.loads(args.candidate.read_text()),
        artifact_base=args.artifact_base,
        baseline_provenance=load_provenance(args.baseline, args.baseline_provenance),
        candidate_provenance=load_provenance(args.candidate, args.candidate_provenance),
    )
    report["input_files"] = {
        arm: {"path": str(path), "sha256": _digest(path.read_bytes())}
        for arm, path in (("baseline", args.baseline), ("candidate", args.candidate))
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    args.output.with_suffix(".md").write_text(render_markdown(report))
    print(json.dumps({"comparison_valid": report["comparison_valid"], **report["summary"]}))


if __name__ == "__main__":
    main()
