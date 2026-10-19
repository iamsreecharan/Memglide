"""Publish explicit local source-only receipts after profiling and validation.

Formatter/copier only: never runs a test, preparer, repository, login or model.
Fresh output is mandatory. Run only after every required final receipt exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local/source-only-refinement"
PROFILE = ROOT / ".local/source-only-refinement-balanced"
EVIDENCE = ROOT / "benchmarks/evidence/source-only-refinement"
BASELINE_SHA = "9ae8595b4b5f97993dcf177d78d090db5f1e0f6fdb8ce2e2da5e3d766d69afac"
FIXTURES = ("noignore", "typical", "dense")
ARMS = ("baseline", "candidate")
REQUIRED = (
    ("validation", "security-review.json"),
    ("validation", "full-python.xml"),
    ("validation", "runner-unit.xml"),
    ("validation", "runner-unit-final.xml"),
    ("validation", "frontend-unit.json"),
    ("validation", "frontend-browser.json"),
    ("validation", "installed-smoke.json"),
    ("validation", "build-static.json"),
    ("validation", "environment.json"),
    ("history", "baseline-audit.json"),
    ("history", "baseline-audit.md"),
)
OPTIONAL_INITIAL = (
    "full-python-initial.xml", "runner-unit-initial.xml",
    "frontend-unit-initial.json", "frontend-browser-initial.json",
    "installed-smoke-initial.json",
)
DEVELOPMENT = ("baseline-profile.json", "after-profile.json", "profile_preload.py", "preload-policy-cache.xml")
REPRODUCTION = (
    "benchmarks/profile_source_only.py", "benchmarks/source-only-refinement-protocol.md",
    "tests/test_profile_source_only.py", "tests/test_preload_policy_cache.py",
    "docs/source-only-refinement.md", "pyproject.toml", "uv.lock",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_safe(path: Path) -> bytes:
    path = path.absolute()
    if not path.is_relative_to(ROOT) or path.resolve(strict=True) != path:
        raise ValueError(f"Only canonical regular project files are allowed: {path}")
    forbidden = {"auth.json", "credentials.json", "codex-state", "node_modules", "worktrees", "repositories", ".git"}
    if any(part.lower() in forbidden for part in path.relative_to(ROOT).parts):
        raise ValueError("Auth, indexed worktree and dependency state cannot be published")
    if not path.is_file() or path.stat().st_size > 64_000_000:
        raise ValueError(f"Missing or oversized explicit receipt: {path}")
    return path.read_bytes()


def xml_summary(content: bytes) -> tuple[dict[str, Any], set[str]]:
    cases = {}
    failures = []
    for case in ET.fromstring(content).iter("testcase"):
        identity = case.get("classname", "") + "::" + case.get("name", "")
        if identity in cases:
            raise ValueError("Duplicate test identity inside one XML receipt")
        state = "failed" if case.find("failure") is not None else "error" if case.find("error") is not None else "skipped" if case.find("skipped") is not None else "passed"
        cases[identity] = state
        if state in {"failed", "error"}:
            failures.append({"case": identity, "state": state})
    counts = Counter(cases.values())
    return {"cases": len(cases), **{state: counts[state] for state in ("passed", "failed", "error", "skipped")}, "failures": failures}, set(cases)


def numbers(values: list[Any]) -> dict[str, Any]:
    known = [value for value in values if type(value) in (int, float)]
    return {"n": len(known), "missing": len(values) - len(known), "mean": statistics.mean(known) if known else None, "median": statistics.median(known) if known else None, "min": min(known) if known else None, "max": max(known) if known else None}


def phase_value(observation: dict[str, Any], phase: str, metric: str) -> float | None:
    calls = [call for call in observation.get("calls", []) if call.get("phase") == phase]
    expected = 1 if phase == "first" else 5
    values = [call.get("timing", {}).get(metric) if call.get("timing") else None for call in calls]
    if len(values) != expected or any(value is None for value in values):
        return None
    return statistics.mean(values)


def build(args: argparse.Namespace) -> dict[str, Any]:
    profile = args.profile.absolute()
    inputs = args.inputs.absolute()
    development = args.development.absolute()
    output_json = ROOT / "benchmarks/source-only-refinement-assessment.json"
    output_md = ROOT / "benchmarks/source-only-refinement-assessment.md"
    if any(path.exists() or path.is_symlink() for path in (EVIDENCE, output_json, output_md)):
        raise ValueError("Fresh report outputs required; existing evidence will not be overwritten")
    # Check all required inputs before creating public output directories.
    required = [(profile / "report.json"), (profile / "manifest.json")]
    required += [inputs / name for _, name in REQUIRED]
    required += [development / name for name in DEVELOPMENT]
    for path in required:
        read_safe(path)
    report = json.loads(read_safe(profile / "report.json"))
    manifest = json.loads(read_safe(profile / "manifest.json"))
    if report["manifest"] != manifest or manifest["baseline_sha256"] != BASELINE_SHA:
        raise ValueError("Profile manifest or exact trusted baseline differs")
    if manifest.get("repeats") != 12 or manifest.get("warm_calls") != 5 or manifest.get("pilot") is not False:
        raise ValueError("This publication requires the frozen 12-pair formal LOCAL profile")
    observations = report["observations"]
    assignments = manifest["assignments"]
    if len(observations) != 78 or len(assignments) != 78:
        raise ValueError("Retain all 72 performance and six diagnostic originals")
    paths_to_copy: list[tuple[str, Path]] = [
        ("profile/report.json", profile / "report.json"),
        ("profile/manifest.json", profile / "manifest.json"),
    ]
    for arm in ARMS:
        path = profile / "snapshots" / (arm + ".py")
        if digest(read_safe(path)) != manifest[arm + "_sha256"]:
            raise ValueError("Frozen preparer snapshot changed")
        paths_to_copy.append(("profile/snapshots/" + path.name, path))
    compact = []
    for ordinal, (row, assignment) in enumerate(zip(observations, assignments, strict=True), 1):
        if assignment.get("kind") not in {"performance", "diagnostic"} or assignment.get("fixture") not in FIXTURES or assignment.get("arm") not in ARMS or type(assignment.get("repeat")) is not int or not 1 <= assignment["repeat"] <= 12:
            raise ValueError("Invalid worker classification/fixture/ordinal in manifest")
        if any(row.get(key) != value for key, value in assignment.items()):
            raise ValueError("Worker identity/order differs from frozen assignment")
        expected = f"{ordinal:03}-{assignment['kind']}-{assignment['fixture']}-{assignment['arm']}"
        if row["artifact_directory"] != expected:
            raise ValueError("Worker artifact pointer is not the immutable expected directory")
        directory = profile / expected
        if json.loads(read_safe(directory / "result.json")) != row:
            raise ValueError("Original worker result changed")
        request = json.loads(read_safe(directory / "request.json"))
        if request != {**assignment, "snapshot_sha256": manifest[assignment["arm"] + "_sha256"]}:
            raise ValueError("Worker request differs from frozen assignment/snapshot")
        for filename in ("request.json", "result.json", "stdout.log", "stderr.log"):
            path = directory / filename
            if path.exists():
                read_safe(path)
                paths_to_copy.append(("profile/" + expected + "/" + filename, path))
        observed = row.get("observation") or {}
        compact.append({
            "ordinal": ordinal, **assignment, "artifact_directory": "profile/" + expected,
            "valid": row["valid"], "returncode": row.get("returncode"), "error": row.get("error"),
            "process_wall_seconds": row.get("process_wall_seconds"),
            "first": {metric: phase_value(observed, "first", metric) for metric in ("wall_seconds", "cpu_seconds", "waited_child_cpu_seconds")},
            "warm_worker_mean": {metric: phase_value(observed, "warm", metric) for metric in ("wall_seconds", "cpu_seconds", "waited_child_cpu_seconds")},
            "within_worker_warm_variation": observed.get("warm_worker_aggregates"),
            "setup": observed.get("setup"), "resources": observed.get("resources"),
            "calls_recorded": len(observed.get("calls", [])),
            "full_fidelity_calls": sum(call.get("fidelity") is True for call in observed.get("calls", [])),
            "diagnostic_call_counts": [{"phase": call["phase"], "ordinal": call["ordinal"], "counts": call.get("counts"), "fidelity": call.get("fidelity")} for call in observed.get("calls", [])] if row["kind"] == "diagnostic" else None,
            "fallback_controls": observed.get("controls"),
        })
    performance = [row for row in compact if row["kind"] == "performance"]
    diagnostics = [row for row in compact if row["kind"] == "diagnostic"]
    if len(performance) != 72 or len(diagnostics) != 6:
        raise ValueError("Performance and diagnostic units were mixed")
    resources = {}
    for fixture in FIXTURES:
        resources[fixture] = {}
        for arm in ARMS:
            members = [row for row in performance if row["fixture"] == fixture and row["arm"] == arm]
            resources[fixture][arm] = {
                "workers": len(members),
                "subprocess_lifetime_seconds": numbers([row["process_wall_seconds"] for row in members]),
                "setup_wall_seconds": numbers([(row.get("setup") or {}).get("wall_seconds") for row in members]),
                "setup_own_cpu_seconds": numbers([(row.get("setup") or {}).get("cpu_seconds") for row in members]),
                "whole_worker_self_peak_rss_bytes": numbers([(row.get("resources") or {}).get("self_peak_rss_bytes") for row in members]),
                "maximum_waited_child_rss_bytes_separate": numbers([(row.get("resources") or {}).get("max_waited_child_rss_bytes") for row in members]),
            }
    raw = {}
    for group, name in REQUIRED:
        path = inputs / name
        raw[name] = read_safe(path)
        paths_to_copy.append((group + "/" + name, path))
    optional = []
    for name in OPTIONAL_INITIAL:
        path = inputs / name
        if path.exists():
            raw[name] = read_safe(path)
            optional.append(name)
            paths_to_copy.append(("validation/initial/" + name, path))
    for name in DEVELOPMENT:
        paths_to_copy.append(("development-unmatched/" + name, development / name))
    for name in REPRODUCTION:
        paths_to_copy.append(("reproduction/" + name, ROOT / name))
    paths_to_copy.append(("reproduction/build_report.py", Path(__file__).absolute()))
    paths_to_copy.append(("reproduction/installed_smoke.py", inputs / "installed_smoke.py"))
    full, full_ids = xml_summary(raw["full-python.xml"])
    targeted = []
    initial_failures = []
    for name, content in raw.items():
        if name.endswith(".xml") and name != "full-python.xml":
            stats, ids = xml_summary(content)
            observation = {"path": name, **stats, "overlap_with_full_suite": len(ids & full_ids), "not_added_to_full_count": True}
            targeted.append(observation)
            if stats["failed"] or stats["error"]:
                initial_failures.append(observation)
    unit = json.loads(raw["frontend-unit.json"])
    browser = json.loads(raw["frontend-browser.json"])
    smoke = json.loads(raw["installed-smoke.json"])
    security = json.loads(raw["security-review.json"])
    if security["source_files"]["src/memglide/integrations/preload.py"] != manifest["candidate_sha256"]:
        raise ValueError("Security review does not describe the frozen candidate")
    build_static = json.loads(raw["build-static.json"])
    checks = smoke.get("checks", {})
    if not isinstance(checks, dict) or any(type(value) is not bool for value in checks.values()):
        raise ValueError("Smoke receipt requires an explicit Boolean check map")
    validation = {
        "full_python_run": full,
        "targeted_runs_not_summed": targeted,
        "retained_initial_xml_failures": initial_failures,
        "frontend_unit": {key: unit[key] for key in ("numTotalTests", "numPassedTests", "numFailedTests", "numPendingTests", "success")},
        "frontend_browser": {"stats": browser["stats"], "errors": browser.get("errors", [])},
        "installed_smoke_checks_separate": {"count": len(checks), "passed": sum(checks.values()), "expected": args.expected_installed_checks, "all_passed": smoke.get("all_passed") is True and all(checks.values()), "model_requests": smoke.get("model_requests"), "checks": checks},
        "security_review": security,
        "build_static": build_static,
        "optional_initial_receipts": optional,
        "count_rule": "One full Python suite count; overlapping 107-case preload and 19-case runner/other reruns are retained separately, never added. Frontend/browser and installed smoke have separate denominators.",
    }
    validation["all_final_behavior_receipts_passed"] = bool(
        full["cases"] > 0 and full["failed"] == full["error"] == 0
        and unit["success"] is True and unit["numPassedTests"] == unit["numTotalTests"]
        and browser["stats"]["expected"] > 0 and browser["stats"]["unexpected"] == browser["stats"]["flaky"] == 0
        and not browser.get("errors") and security.get("all_checks_passed") is True
        and smoke.get("all_passed") is True and all(checks.values())
        and len(checks) == args.expected_installed_checks
    )
    before = json.loads(read_safe(development / "baseline-profile.json"))
    after = json.loads(read_safe(development / "after-profile.json"))
    control_key = "no_ignore_one_source"
    unmatched = {
        "baseline": before, "candidate": after,
        "interpretation": "Unmatched development probes with uncontrolled timing/cache/host variation; not a causal before/after result and not pooled with the balanced experiment.",
        "noignore_negative_control": {
            "baseline_mean_ms": before["cases"][control_key]["uninstrumented_10_warm_api_wall_seconds"]["mean"] * 1000,
            "candidate_mean_ms": after["cases"][control_key]["uninstrumented_10_warm_api_wall_seconds"]["mean"] * 1000,
            "same_instrumented_work": before["cases"][control_key]["instrumented_counts"] == after["cases"][control_key]["instrumented_counts"],
            "interpretation": "23.10 to 10.71 ms on the unchanged-work control demonstrates confounding; do not attribute that apparent gain to policy caching.",
        },
    }
    baseline_audit = json.loads(raw["baseline-audit.json"])
    result = {
        "version": "source-only-refinement-assessment-1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "conclusion": "Request-local policy compilation refinement; only per-fixture local preparation evidence is assessed. Exact model-visible source/task bytes and current read checks are preserved; no new model benefit is measured.",
        "baseline_commit": manifest["baseline_commit"], "baseline_source_sha256": manifest["baseline_sha256"], "candidate_source_sha256": manifest["candidate_sha256"],
        "frozen_manifest": manifest, "seal_unchanged": report["seal_unchanged"],
        "local_profile_summary": report["summary"],
        "local_resource_summaries_by_fixture": resources,
        "individual_original_workers": compact,
        "source_fidelity_observations": {
            "recorded_calls": sum(row["calls_recorded"] for row in compact),
            "stable_fidelity_calls": sum(row["full_fidelity_calls"] for row in compact),
            "fallback_control_observations_separate": sum(len(row["fallback_controls"] or []) for row in diagnostics),
            "exact_fallback_controls": sum(control.get("exact_fallback") is True for row in diagnostics for control in (row["fallback_controls"] or [])),
            "not_coding_task_correctness": True,
        },
        "failures": [row for row in compact if not row["valid"]],
        "unit_of_analysis": "12 paired fresh workers per fixture; each worker's five inner warm calls reduce to one mean. There are not 60 independent warm samples per arm/fixture.",
        "diagnostic_units_separate": diagnostics,
        "unmatched_development_probe": unmatched,
        "historical_baseline_evidence_not_pooled": baseline_audit,
        "engineering_validation": validation,
        "model_input_tokens": None, "cached_input_tokens": None, "cache_write_tokens": None,
        "output_tokens": None, "provider_model_calls": None, "native_coding_success_rate": None,
        "native_end_to_end_task_seconds": None, "estimated_model_cost_per_strict_success": None,
        "actual_billed_cost": None, "dispatched_model_requests": report["dispatched_model_requests"],
        "limits": [
            "Synthetic source-only development fixtures and minimal SQLite approval tables; no real repository indexing, AST/Tree-sitter, held-out coding tasks or native agents ran in this local profile.",
            "First-call API timing includes first lazy imports; warm uses one mean per worker. Diagnostic instrumentation, fallbacks, setup and subprocess lifetime are separate from primary API timings.",
            "No fixture-weighted overall performance headline is computed. Fixture-specific variation, failures, missing pairs and no-effect controls remain visible.",
            "Whole-worker Linux SELF peak RSS includes interpreter/imports/setup/preparation and is not incremental API memory. Maximum waited-child RSS is separate, not simultaneous total; never add peaks.",
            "Own CPU excludes children; waited child CPU is a separate observed counter. OS caches and shared-host load remain uncontrolled.",
            "Stable normal prompt bytes, source hashes and current source/policy read-call counts match. These are API read-call observations, not filesystem or storage I/O counts.",
            "Identical native input/settings make a paid old/new model test non-attributable for this compiled-ignore cache. Local effects do not establish new token, cache-hit, billing or native-task savings.",
            "Historical 9.055% lower estimated cost is a partial post-hoc matched warm cohort; 10.19% belongs to focused confirmation tasks while its all-task difference is about 2.47%. Those corpora are not pooled or attributed to this refinement.",
        ],
    }
    # All explicit payloads have been validated; publish the allowlist only.
    ledger = []
    seen = set()
    for relative, source in paths_to_copy:
        if relative in seen:
            raise ValueError("Duplicate evidence destination")
        seen.add(relative)
        content = read_safe(source)
        destination = EVIDENCE / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(content)
        ledger.append({"path": destination.relative_to(ROOT).as_posix(), "source": source.relative_to(ROOT).as_posix(), "bytes": len(content), "sha256": digest(content)})
    ledger_path = EVIDENCE / "artifact-ledger.json"
    ledger_path.write_text(json.dumps({"version": 1, "files": ledger}, indent=2) + "\n")
    result["artifact_ledger"] = ledger_path.relative_to(ROOT).as_posix()
    result["artifact_ledger_sha256"] = digest(ledger_path.read_bytes())
    with output_json.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    with output_md.open("x", encoding="utf-8") as stream:
        stream.write(markdown(result))
    return result


def fmt(value: Any, scale: float = 1) -> str:
    return "unavailable" if value is None else f"{value * scale:.4f}"


def markdown(result: dict[str, Any]) -> str:
    summary = result["local_profile_summary"]
    validation = result["engineering_validation"]
    lines = [
        "# Source-only request-local policy refinement", "",
        "**The complete known-path source architecture is preserved. This change reuses compiled ignore specifications within one preparation request; current policy/source reads and normal prompt bytes remain unchanged. No model benefit is claimed.**", "",
        f"The exact baseline is `{result['baseline_commit']}` (`{result['baseline_source_sha256']}`); candidate source is `{result['candidate_source_sha256']}`. The frozen local comparison is valid: **{summary['comparison_valid']}**; final source seal unchanged: **{result['seal_unchanged']}**.", "",
        "There are 72 performance workers and six separate diagnostic workers. Each fixture has 12 paired fresh workers per arm. Five warm inner calls form one worker mean, not 60 independent samples. Synthetic approval tables avoid indexing; this is not a coding-agent, real-indexing or model-cost benchmark.", "",
        "## Per-fixture API timing and own CPU", "",
        "All timing/CPU values below are milliseconds. Negative paired deltas favor the candidate. First calls include first lazy imports. Warm observations are worker means. Bootstrap intervals resample 12 paired worker units with 2,000 seeded draws; host/cache uncertainty remains.", "",
        "| Fixture | Phase / metric | Pairs | Baseline mean | Candidate mean | Baseline median | Candidate median | Mean paired delta | Median paired delta | 95% mean-delta interval | 95% median-delta interval |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    coverage_notes = []
    for fixture in FIXTURES:
        value = summary["fixtures"][fixture]
        for phase in ("first", "warm"):
            for metric in ("wall_seconds", "cpu_seconds", "waited_child_cpu_seconds"):
                effect = value["effects"][phase + "_" + metric]
                interval = lambda key: "unavailable" if effect[key] is None else "[" + ", ".join(fmt(number, 1000) for number in effect[key]) + "]"
                cells = [fixture, phase + " / " + metric, str(effect["pairs"])] + [fmt(effect[key], 1000) for key in ("baseline_mean", "candidate_mean", "baseline_median", "candidate_median", "mean_delta", "median_delta")] + [interval("mean_delta_bootstrap95"), interval("median_delta_bootstrap95")]
                lines.append("| " + " | ".join(cells) + " |")
        coverage_notes.append(f"- {fixture}: {value['complete_valid_pairs']}/{value['planned_pairs']} complete valid pairs; {value['invalid_or_missing_pairs']} invalid/missing.")
    lines += [""] + coverage_notes
    lines += ["", "## Whole-worker resources and separate setup", "", "RSS values describe the whole worker, including imports/setup/preparation, measured before verification. They are not incremental API allocation. Parent subprocess lifetime includes interpreter, setup, verification and serialization. Waited-child maxima are separate; no peak sums are computed.", "", "| Fixture | Arm | Workers | Setup wall mean / median ms | Process lifetime mean / median ms | SELF peak mean / median MiB | Waited-child max mean / median MiB |", "|---|---|---:|---|---|---|---|"]
    for fixture, arms in result["local_resource_summaries_by_fixture"].items():
        for arm, value in arms.items():
            pair = lambda key, scale: fmt(value[key]["mean"], scale) + " / " + fmt(value[key]["median"], scale)
            lines.append(f"| {fixture} | {arm} | {value['workers']} | {pair('setup_wall_seconds',1000)} | {pair('subprocess_lifetime_seconds',1000)} | {pair('whole_worker_self_peak_rss_bytes',1/1048576)} | {pair('maximum_waited_child_rss_bytes_separate',1/1048576)} |")
    lines += ["", "## Separate diagnostic workers", "", "These instrumented read/compile observations do not enter timing summaries. Every diagnostic has one first and five warm calls; API read attempts/bytes are not actual filesystem I/O. Exact fallback controls are retained in JSON.", "", "| Fixture | Arm | Phase | Policy compilations per call | Policy read attempts per call | Source read attempts per call |", "|---|---|---|---|---|---|"]
    for row in result["diagnostic_units_separate"]:
        for phase in ("first", "warm"):
            calls = [call for call in row["diagnostic_call_counts"] if call["phase"] == phase]
            values = lambda key: ", ".join(str((call["counts"] or {}).get(key)) for call in calls)
            lines.append(f"| {row['fixture']} | {row['arm']} | {phase} | {values('policy_compilations')} | {values('policy_read_attempts')} | {values('source_read_attempts')} |")
    lines += ["", "Exact stable results and source/policy read-call equality checks: `" + json.dumps(summary["diagnostic_checks"], sort_keys=True) + "`.", "", "## Unmatched development probes: confounded", "", "The earlier unmatched no-ignore control mean fell from **23.10 to 10.71 ms with the same instrumented work**. That apparent improvement is not attributed to this cache. All raw before/after profiles remain under `evidence/source-only-refinement/development-unmatched/`; their inclusive instrumentation timers are not added or pooled with the balanced study.", "", "## Historical model evidence, kept separate", "", "Both favorable historical cohorts used this complete known-path source path. Warm's 9.055% lower API-equivalent cost and 6.892% shorter mean instrumented time are a partial, post-hoc matched sample. Confirmation's 10.19% lower focused-task cost accompanied 3.18% slower mean time; its all-task estimate was only about 2.47% lower. Cache-write scenarios can reverse rankings. These are not billed savings and are not effects of the new local cache.", "", "New model input/cached/output tokens, provider model calls, strict native task success, model cost per success and actual charges are **unavailable**. Zero model requests were dispatched. A paid old/new model comparison would not attribute token differences to identical prompt bytes.", "", "## Verification", "", f"The complete Python run records **{validation['full_python_run']['passed']} passed**, {validation['full_python_run']['failed']} failed, {validation['full_python_run']['error']} errors and {validation['full_python_run']['skipped']} skipped. Overlapping targeted preload/runner/security reruns are retained without adding their counts. Frontend: {validation['frontend_unit']['numPassedTests']}/{validation['frontend_unit']['numTotalTests']}; browser expected passes: {validation['frontend_browser']['stats']['expected']}; installed smoke: {validation['installed_smoke_checks_separate']['passed']}/{validation['installed_smoke_checks_separate']['count']} separate checks. Build/static/security receipts are retained in JSON.", "", "Initial failed XML receipts: `" + json.dumps(validation["retained_initial_xml_failures"], sort_keys=True) + "`.", "", "## Every original worker", "", "The raw requests, stdout/stderr, result receipts and frozen preparer snapshots are allowlisted in the artifact ledger. All failures and missing metrics remain visible; diagnostics are not silently pooled into performance.", "", "| # | Kind | Fixture | Repeat | Arm | Valid | First wall ms | Warm worker mean wall ms | Worker lifetime ms | Error |", "|---:|---|---|---:|---|---|---:|---:|---:|---|"]
    for row in result["individual_original_workers"]:
        lines.append(f"| {row['ordinal']} | {row['kind']} | {row['fixture']} | {row['repeat']} | {row['arm']} | {row['valid']} | {fmt(row['first']['wall_seconds'],1000)} | {fmt(row['warm_worker_mean']['wall_seconds'],1000)} | {fmt(row['process_wall_seconds'],1000)} | {row['error'] or ''} |")
    lines += ["", "## Limits and next experiments", ""] + ["- " + value for value in result["limits"]]
    lines += ["", "Next: replicate local effects on realistic known-path ignore layouts and edited-policy/race controls while preserving exact source bytes and all fresh reads. Only a separately frozen change to model-visible representation or workflow warrants fresh native cost-per-success evaluation.", "", "[Detailed JSON](source-only-refinement-assessment.json) · [Artifact ledger](evidence/source-only-refinement/artifact-ledger.json)", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=PROFILE)
    parser.add_argument("--inputs", type=Path, default=LOCAL)
    parser.add_argument("--development", type=Path, default=ROOT / ".local/known-path-audit")
    parser.add_argument("--expected-installed-checks", type=int, default=15)
    result = build(parser.parse_args())
    print(json.dumps({"comparison_valid": result["local_profile_summary"]["comparison_valid"], "workers": len(result["individual_original_workers"]), "model_requests": result["dispatched_model_requests"]}))
    return 0 if result["local_profile_summary"]["comparison_valid"] and result["engineering_validation"]["all_final_behavior_receipts_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
