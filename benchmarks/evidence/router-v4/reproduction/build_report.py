"""Post-study offline/native evidence collector; never dispatches or reruns work.

Run only after root reviews this file, supplies final reports and authorizes
collection. Fresh staging directories retain failed collection attempts. Inputs
are JSON/explicit public evidence files, never application imports or auth state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import statistics
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local/router-v4"
OFFLINE_ARMS, NATIVE_ARMS = ("B", "V3", "C"), ("A", "B", "C")
RECEIPTS = (
    "implementation-plan.json", "diagnosis.json", "diagnosis.md", "diagnose_parser.py",
    "minimal-parser-controls.json", "exposed-parser-diagnostic.json", "development-ledger.json",
    "security-review.json", "reviewer_controls.py", "reviewer-controls.json",
    "reviewer-controls-first-pass.json", "reviewer-controls-initial-failure.json",
    "query-boundary-control-initial.json", "numeric-anchor-control-initial.json",
    "dotted-boundary-control-initial.json", "private-method-control.json",
    "owned-tests-initial.log", "owned-tests-second.log", "owned-tests-third.log",
    "owned-tests-final.log", "owned-tests-final-reviewed.log", "owned-tests-final-frozen.log",
    "owned-tests-postreview.log", "owned-tests-postreview-numeric.log", "affected.xml", "affected.log",
    "affected-initial-command.xml", "affected-initial-command.log", "cli-initial.xml", "cli-initial.log",
    "cli-final.xml", "cli-final.log", "cli-complete.xml", "cli-complete.log",
    "production-final.xml", "production-final.log", "full-python.xml", "full-python.log",
    "python311-full.xml", "python311-full.log", "frontend-unit.json", "frontend-unit.log",
    "frontend-browser.json", "frontend-browser.raw.log", "frontend-build.log", "frontend-install.log",
    "installed_smoke.py", "installed-smoke.json", "installed-smoke.stdout.log", "installed-smoke.stderr.log",
    "installed-env.log", "installed-wheel.log", "installed-dependencies.log", "wheel-build.log",
    "runtime-requirements.txt", "runtime-export.log", "bundle.log", "ruff.log", "mypy.log",
    "offline-runner-review.json", "native-runner-review.json", "native-runner-review-accounting.json",
    "native-runner-review-descendants.json", "native-runner-review-processes.json",
    "native-runner-review-reproductions.json", "native-runner-review-final.json",
    "independent-corpus-audit.json", "independent-results-audit.json", "audit_corpus.py", "audit_results.py",
    "corpus-static-audit.json", "corpus_audit.py", "corpus-spec-freeze.json",
    "post-publication-seal-verification.json", "post-study-preservation.json", "post-corpus-harness.xml",
    "post-corpus-verification.json",
    "native-corpus-review/audit.json", "native-admission.json", "native-admission-final.json", "finalize_native_audit.py",
    "native-plan-commands.md",
    "native-plan-only-command.json", "native-plan-only-receipt.json", "native-plan-only.log",
    "native-blocked-snapshot-command.json", "native-blocked-snapshot-verification.json", "native-blocked-snapshot.log",
    "record_blocked_native_plan.py",
    "final-cohort-verification.json", "build-static.json", "environment.json", "historical-preservation.json",
    "network-readiness.json", "publication-readiness.json", "publication-readiness.md",
    "collector-publication-review.json", "collector-publication-review.diff",
    "collector-negative-gate-review.json", "collector-negative-gate-review.diff",
    "collector-native-manifest-review.json", "collector-native-manifest-review.diff",
    "native_preflight.py", "native-preflight-output.log", "native-preflight-after-publish-output.log",
)
READINESS_DIRECTORIES = ("native-preflight", "native-preflight-after-publish")
NATIVE_PUBLIC_FILES = (
    "native-corpus-freeze.json", "native-corpus-freeze-v2.json", "native-tasks.json", "native-tasks-v2.json",
    "native-v2-protocol-deviation.json", "native-v2-exact-prompt.diff",
)
NATIVE_CONTROL_SUMMARIES = (
    "native-corpus-review/external-controls/control-summary.json",
    "native-corpus-review-v2/external-controls/control-summary.json",
)
NATIVE_PRIVATE_REVIEW_FILES = (
    "native-corpus-review/checkpoint.json", "native-corpus-review/python-review.json",
    "native-corpus-review/compiler-review.json",
)
FRESH_DIAGNOSTICS_FILES = (
    "more_itertools-more-py.stdout.json", "more_itertools-more-py.stderr.log",
    "more_itertools-more-pyi.stdout.json", "more_itertools-more-pyi.stderr.log",
    "more_itertools-recipes-py.stdout.json", "more_itertools-recipes-py.stderr.log",
    "more_itertools-recipes-pyi.stdout.json", "more_itertools-recipes-pyi.stderr.log",
)
RUNNER_RECEIPTS = (
    "initial-tests.xml", "initial-tests.log", "pre-review-tests.xml", "pre-review-tests.log",
    "pre-review-validation.json", "pre-review-ruff.log", "pre-review-mypy.log",
    "review-fix-tests.xml", "review-fix-tests.log", "final-tests.xml", "final-tests.log",
    "final-ruff.log", "final-mypy.log", "final-validation.json",
)
RESEARCH_LEDGERS = (
    "fetch-ledger.json", "followup-fetch-ledger.json", "endpoint-fetch-ledger.json",
    "endpoint-followup-fetch-ledger.json", "auth-endpoint-fetch-ledger.json",
    "bounds-fetch-ledger.json", "auth-refresh-fetch-ledger.json", "auth-refresh-manager-fetch-ledger.json",
)
RESEARCH_SCRIPTS = (
    "fetch_sources.py", "fetch_followup.py", "fetch_endpoint.py", "fetch_endpoint_followup.py",
    "fetch_auth_endpoint.py", "fetch_bound_docs.py", "fetch_auth_refresh.py",
    "fetch_auth_refresh_manager.py", "build_research.py", "installed-tag-resolution.json",
)
REPRODUCTION = (
    "benchmarks/router-v4-diagnosis.md", "benchmarks/router-v4-diagnosis.json",
    "benchmarks/router-v4-research.md", "benchmarks/router-v4-research.json",
    "docs/bounded-source-routing.md", "tests/test_bounded_router.py", "tests/test_auto_preload_v4.py",
    "tests/test_codex_router_v4.py", "frontend/package.json", "frontend/package-lock.json",
    ".github/workflows/verify.yml", "benchmarks/.ruff.toml",
)
NATIVE_FILES = (
    "attempt-start.json", "result.json", "prompt.txt", "command.json", "events.jsonl", "stderr.log",
    "process-identity.json", "launch-grant.json", "final.json", "preparation-request.json",
    "preparation-stdout.json", "preparation-stderr.log", "changes.patch", "git-status.txt", "captured-files.json",
    "grade/command.json", "grade/stdout.json", "grade/stderr.log",
)
OFFLINE_METRICS = (
    "setup_plus_preparation_wall_seconds", "preparation_wall_seconds", "setup_cpu_seconds", "preparation_cpu_seconds",
    "setup_waited_child_cpu_seconds", "preparation_waited_child_cpu_seconds", "self_peak_rss_bytes",
    "max_waited_child_rss_bytes", "process_wall_seconds", "context_bytes", "selected_source_bytes",
)
NATIVE_METRICS = (
    "end_to_end_wall_seconds", "native_exec_wall_seconds", "approval_index_wall_seconds",
    "context_preparation_wall_seconds", "input_tokens", "cached_input_tokens", "uncached_input_tokens",
    "output_tokens", "process_tree_peak_rss_bytes", "cpu_seconds", "total_observed_local_cpu_seconds",
    "mcp_calls", "model_calls", "repeated_file_reads", "observed_file_read_commands", "observed_repeated_read_commands",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def regular(path: Path) -> bytes:
    if path.is_symlink() or path.resolve(strict=True) != path.absolute() or not path.is_file():
        raise ValueError(f"not a canonical regular file: {path}")
    if path.stat().st_size > 64_000_000:
        raise ValueError("individual evidence exceeded collector cap")
    return path.read_bytes()


def load(path: Path) -> Any:
    return json.loads(regular(path), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def save(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def numeric(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(value)


def summary(values: list[Any], planned: int) -> dict[str, Any]:
    known = [value for value in values if numeric(value)]
    return {"observed": len(known), "missing_of_planned": planned - len(known),
            "mean": statistics.mean(known) if known else None, "median": statistics.median(known) if known else None,
            "minimum": min(known) if known else None, "maximum": max(known) if known else None}


def strict_success(row: dict[str, Any]) -> bool:
    return (row.get("attempted") is True and row.get("status") == "completed"
            and row.get("grader", {}).get("success") is True and row.get("treatment_valid") is True
            and row.get("preload_treatment_fidelity", {}).get("valid") is True
            and row.get("native_execution_validity", {}).get("valid") is True)


def native_outcomes(report: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for arm in NATIVE_ARMS:
        rows = [row for row in report["runs"] if row["configuration"] == arm]
        attempted = [row for row in rows if row.get("attempted") is True]
        successes = sum(strict_success(row) for row in attempted)
        costs = []
        for row in attempted:
            estimate = row.get("api_price_equivalent", {})
            value = estimate.get("native_reported_price_equivalent_usd")
            # A numeric placeholder is not a priced measurement without complete
            # whole-attempt usage. Failed but fully observed attempts still count.
            costs.append(value if numeric(value) and value >= 0 and estimate.get("usage_evidence", {}).get("coverage_complete") is True else None)
        full_cost = sum(costs) if attempted and all(numeric(value) for value in costs) else None
        known = [value for value in costs if numeric(value)]
        result[arm] = {
            "planned": len(rows), "attempted": len(attempted), "unrun": len(rows) - len(attempted),
            "status": "UNRUN" if not attempted else "attempted",
            "strict_successes": successes if attempted else None,
            "strict_success_rate": successes / len(attempted) if attempted else None,
            "historical_tariff_scenario": {"attempts_including_failures": len(attempted), "usage_priced_attempts": len(known),
                                           "known_subtotal_usd": sum(known) if known else None, "complete_total_usd": full_cost,
                                           "cost_per_strict_success_usd": full_cost / successes if full_cost is not None and successes else None,
                                           "actual_billed_charges_usd": None, "current_rates_verified": False,
                                           "unavailable_reason": "UNRUN: no observed attempt usage" if not attempted else "Complete usage/pricing or a strict-success denominator is missing" if full_cost is None or not successes else None},
            "reported_arm_metrics": report.get("arms", {}).get(arm, {}).get("metrics", {}) if attempted else {},
        }
    return result


def readiness_history(publication: dict[str, Any]) -> list[dict[str, Any]]:
    history = []
    declared = publication.get("preflight_history", [])
    directories = []
    for entry in declared:
        parts = PurePosixPath(entry.get("receipt_path", "")).parts
        if (len(parts) != 4 or parts[:2] != (".local", "router-v4") or parts[3] != "receipt.json"
                or not parts[2].startswith("native-preflight") or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in parts[2])):
            raise ValueError("access receipt escaped explicit local readiness namespace")
        directories.append(parts[2])
    if len(directories) != len(set(directories)) or not set(READINESS_DIRECTORIES) <= set(directories):
        raise ValueError("both original access attempts must be preserved without duplicates")
    for directory in directories:
        path = LOCAL / directory / "receipt.json"
        receipt = load(path)
        history.append({"directory": directory, "receipt_sha256": sha(regular(path)), "receipt": receipt,
                        "ready": receipt.get("ready"),
                        "wall_seconds": receipt.get("result", {}).get("wall_time_seconds"),
                        "observed_completed_turns": receipt.get("usage", {}).get("completed_turns"),
                        "usage_coverage_complete": receipt.get("usage", {}).get("coverage_complete") is True,
                        "actual_model_calls": receipt.get("result", {}).get("telemetry", {}).get("model_calls"),
                        "actual_billed_charges": receipt.get("actual_billed_charges")})
    if publication.get("native_preflight_attempts") != len(history) or {item["receipt_sha256"] for item in declared} != {item["receipt_sha256"] for item in history}:
        raise ValueError("current publication receipt does not bind both retained access attempts")
    return history


def validate_native_rows(report: dict[str, Any], plan: dict[str, Any]) -> None:
    expected = plan.get("runs", plan.get("assignments", []))
    actual = report.get("runs", [])
    identity = lambda row: (row.get("run_id"), row.get("task_id"), row.get("repeat"), row.get("configuration"))
    planned, observed = [identity(row) for row in expected], [identity(row) for row in actual]
    if (len(planned) != 72 or len(set(planned)) != 72 or len(observed) != 72
            or len(set(observed)) != 72 or set(planned) != set(observed)
            or any(type(row.get("attempted")) is not bool for row in actual)
            or any(sum(row.get("configuration") == arm for row in actual) != 24 for arm in NATIVE_ARMS)):
        raise ValueError("native rows do not retain every unique frozen assignment including UNRUN")


def offline_findings(report: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    arms = report["summary"]["arms"]
    counts = {arm: arms[arm]["positive"]["scope_or_control_passes"] for arm in OFFLINE_ARMS}
    necessary_gain = counts["C"] > 0 and counts["C"] > counts["V3"]
    reasons: dict[str, dict[str, dict[str, int]]] = {}
    for kind in ("positive", "abstention_control"):
        reasons[kind] = {}
        for arm in OFFLINE_ARMS:
            values: dict[str, int] = {}
            for row in report["rows"]:
                if row["arm"] == arm and row["kind"] == kind:
                    preparation = (row.get("observation") or {}).get("preparation", {})
                    reason = preparation.get("reason", "not_observed")
                    values[reason] = values.get(reason, 0) + 1
            reasons[kind][arm] = values
    preloaded = sum((row.get("observation") or {}).get("preparation", {}).get("mode") == "preloaded" for row in report["rows"])
    passthrough = sum((row.get("observation") or {}).get("preparation", {}).get("mode") == "passthrough" for row in report["rows"])
    tasks = []
    for task in plan["positive_tasks"]:
        outcomes = {}
        for arm in OFFLINE_ARMS:
            rows = [row for row in report["rows"] if row["task_id"] == task["id"] and row["arm"] == arm]
            outcomes[arm] = {"complete": sum(row.get("worker_completed") is True and row.get("fidelity", {}).get("valid") is True
                                               and row.get("scope_grade", {}).get("declared_scope_complete") is True for row in rows),
                             "planned": plan["repeats"],
                             "modes_and_reasons": sorted({((row.get("observation") or {}).get("preparation", {}).get("mode", "not_observed"),
                                                          (row.get("observation") or {}).get("preparation", {}).get("reason", "not_observed")) for row in rows})}
        tasks.append({"task_id": task["id"], "repository": task["repository"],
                      "required_paths": plan["grading"][task["id"]]["required_paths"], "outcomes": outcomes})
    return {"selection_improvement_gate": {"status": "FAILED" if not necessary_gain else "REQUIRES_INDEPENDENT_ELIGIBILITY_REVIEW",
                                           "necessary_positive_inclusion_gain_observed": necessary_gain,
                                           "positive_scope_passes": counts, "native_dispatch_authorized_by_collector": False,
                                           "reason": "No positive automatic inclusion gain over preserved v3; zero C inclusion cannot justify the native comparison." if not necessary_gain else "The collector never issues native eligibility; independent frozen criteria still apply."},
            "reason_counts": reasons, "complete_source_deliveries": preloaded, "exact_original_task_passthroughs": passthrough,
            "per_positive_task": tasks,
            "interpretation": "Envelope integrity includes passthrough. Source-unavailable and budget reasons are observed labels, not causal proof; all missing bundles remain in the denominator."}


def native_control_projection(path: Path) -> dict[str, Any]:
    data = load(path)
    allowed = ("success", "executed", "checks", "task_digest", "grader_script_sha256", "backend_script_sha256",
               "fixture_hashes_digest", "returncode", "source_and_git_unchanged_by_grader")
    rows = {task: {kind: {key: result[key] for key in allowed if key in result}
                   for kind, result in results.items() if kind in {"baseline_result", "reference_result"}}
            for task, results in data["results"].items()}
    baseline = sum(results.get("baseline_result", {}).get("executed") is True
                   and results.get("baseline_result", {}).get("success") is False for results in rows.values())
    reference = sum(results.get("reference_result", {}).get("executed") is True
                    and results.get("reference_result", {}).get("success") is True for results in rows.values())
    return {"schema_version": 1, "publication": "Allowlisted outcome/count/hash projection; exact original remains local",
            "original_path": str(path.relative_to(ROOT)), "original_sha256": sha(regular(path)),
            "executed": data.get("executed"), "success": data.get("success"), "tasks": data.get("tasks"),
            "controls": data.get("controls"), "baseline_expected_failures": baseline, "reference_passes": reference,
            "results": rows, "scope": "Standard replay only; not an adversarial grader-isolation check"}


def native_corpus_publication() -> dict[str, Any]:
    original_path, amended_path = (LOCAL / name for name in NATIVE_PUBLIC_FILES[:2])
    original, amended = load(original_path), load(amended_path)
    if sha(regular(amended_path)) != "41007f644ce2b171bccadf1d9eb43e27c0bd89570148f1643f2922522ea0c1b8":
        raise ValueError("v2 native outer seal changed after independent review")
    if amended["original_native_corpus_seal_sha256"] != sha(regular(original_path)):
        raise ValueError("amended native seal does not bind the preserved original")
    for outer, name in ((original, "native-tasks.json"), (amended, "native-tasks-v2.json")):
        if Path(outer["public_tasks_path"]) != LOCAL / name or outer["public_tasks_sha256"] != sha(regular(LOCAL / name)):
            raise ValueError("native public spec is not the sealed original/amendment")
    for key, name in (("protocol_deviation", "native-v2-protocol-deviation.json"), ("exact_prompt_diff", "native-v2-exact-prompt.diff")):
        if Path(amended[key + "_path"]) != LOCAL / name or amended[key + "_sha256"] != sha(regular(LOCAL / name)):
            raise ValueError("native amendment disclosure changed after review")
    audit_path, admission_path = LOCAL / "native-corpus-review/audit.json", LOCAL / "native-admission-final.json"
    if (sha(regular(audit_path)) != "1529e919afbecbd8bd14ec7c3737bac218dba4d7dbcf0abef5553a9a590848da"
            or sha(regular(admission_path)) != "8618a589e61d5bb465c48d840ca3aebdd0ccb573937e74b3d1ca467bba251369"):
        raise ValueError("final native audit/admission changed after independent review")
    return {"original_outer_sha256": sha(regular(original_path)), "amended_outer_sha256": sha(regular(amended_path)),
            "original_public_tasks_sha256": original["public_tasks_sha256"], "amended_public_tasks_sha256": amended["public_tasks_sha256"],
            "private_file_manifests": {"original": original["private_file_hashes"], "amended": amended["private_file_hashes"]},
            "protocol_deviation": load(LOCAL / "native-v2-protocol-deviation.json"),
            "independent_audit": load(audit_path), "final_admission": load(admission_path),
            "native_prompt_bytes_untouched_before_offline": False,
            "independent_standard_replays": [native_control_projection(LOCAL / name) for name in NATIVE_CONTROL_SUMMARIES]}


class Archive:
    def __init__(self, root: Path, *, private_files: set[Path], release_native_oracles: bool) -> None:
        root.mkdir()
        self.root, self.files, self.missing = root, [], []
        self.by_target: dict[str, str] = {}
        self.private_files, self.release_native_oracles = private_files, release_native_oracles
        self.withheld: list[dict[str, Any]] = []

    def add(self, source: Path, target: str, *, expected: str | None = None, optional: bool = False) -> None:
        parts = PurePosixPath(target).parts
        denied = {"..", ".git", ".venv", "venv", "node_modules", "worktrees", "codex-state", "auth.json", "credentials.json"}
        private_source_parts = denied | {".codex", "oauth.json", "tokens.json"}
        if (not parts or PurePosixPath(target).is_absolute() or PurePosixPath(target).as_posix() != target
                or any(part in denied for part in parts)
                or any(part in private_source_parts for part in source.parts)
                or source.name.endswith((".db", ".sqlite", ".sqlite3", ".sqlite-wal", ".sqlite-shm", ".whl", ".tar", ".tar.gz", ".zip", ".so"))
                or target.endswith((".db", ".sqlite", ".sqlite3", ".whl", ".tar", ".tar.gz", ".zip", ".so"))):
            raise ValueError("outside explicit evidence allowlist")
        if not source.exists() and optional:
            self.missing.append({"source": str(source), "target": target})
            return
        data = regular(source)
        actual = sha(data)
        if expected is not None and actual != expected:
            raise ValueError(f"frozen evidence hash mismatch: {source}")
        if source.absolute() in self.private_files and not self.release_native_oracles:
            self.withheld.append({"source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
                                  "sha256": actual, "bytes": len(data), "reason": "Private native oracle/control or mixed review withheld; exact original retained locally"})
            return
        if target in self.by_target:
            if self.by_target[target] != actual:
                raise ValueError("evidence target collision")
            return
        destination = self.root / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
        self.by_target[target] = actual
        self.files.append({"path": target, "sha256": actual, "bytes": len(data),
                           "source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source)})


def source_allowed(path: str) -> bool:
    return ((path.startswith("src/memglide/") or path.startswith("benchmarks/") or path.startswith("tests/"))
            and path.endswith((".py", ".md", ".json"))) or path in {"pyproject.toml", "uv.lock"}


def collect(args: argparse.Namespace, offline: dict[str, Any], plan: dict[str, Any], native: dict[str, Any], archive: Archive) -> None:
    for source, target in ((args.offline_report, "offline/report.json"), (args.offline_plan, "offline/plan.json"),
                           (args.offline_report.parent / "plan-input.json", "offline/plan-input.json"),
                           (args.offline_freeze, "freeze/offline-policy-freeze.json"),
                           (args.native_public_report or args.native_report,
                            "native/report-published-projection.json" if args.native_public_report else "native/report.json"),
                           (args.native_plan, "native/plan.json"),
                           (args.native_freeze, "freeze/native-policy-freeze.json"),
                           (Path(__file__).resolve(), "reproduction/build_report.py")):
        archive.add(source, target)
    if args.native_public_report:
        archive.add(args.native_report, "native/report-exact-original.json")
    if sha(regular(args.offline_report.parent / "plan-input.json")) != offline["plan_sha256"]:
        raise ValueError("offline report does not match original retained plan bytes")
    if regular(args.offline_plan) != regular(args.offline_report.parent / "plan-input.json"):
        raise ValueError("standalone offline plan changed after study")
    if load(args.offline_freeze) != plan["policy_freeze"]:
        raise ValueError("standalone offline freeze differs from original plan")
    diagnostics = load(args.fresh_diagnostics)
    if diagnostics.get("original_report_sha256") != sha(regular(args.offline_report)):
        raise ValueError("post-study diagnosis does not bind the exact original offline report")
    archive.add(args.fresh_diagnostics, "post-study-diagnostics/diagnosis.json")
    archive.add(LOCAL / "analyze_fresh_failures.py", "post-study-diagnostics/analyze_fresh_failures.py")
    for name in FRESH_DIAGNOSTICS_FILES:
        archive.add(args.fresh_diagnostics.parent / name, "post-study-diagnostics/" + name)
    for name in RECEIPTS:
        archive.add(LOCAL / name, "validation/" + name, optional=True)
    native_corpus_publication()
    for name in NATIVE_PUBLIC_FILES:
        archive.add(LOCAL / name, "native/corpus/" + name)
    for index, name in enumerate(NATIVE_CONTROL_SUMMARIES, start=1):
        source = LOCAL / name
        archive.private_files.add(source.absolute())
        archive.add(source, f"native/corpus/private-control-summary-v{index}.json")
        projection = archive.root.parent / f"native-controls-v{index}-public-projection.json"
        save(projection, native_control_projection(source))
        archive.add(projection, f"native/corpus/standard-controls-v{index}-public-projection.json")
    for name in NATIVE_PRIVATE_REVIEW_FILES:
        source = LOCAL / name
        archive.private_files.add(source.absolute())
        archive.add(source, "native/corpus/private-review/" + source.name, optional=True)
    for name in RUNNER_RECEIPTS:
        archive.add(ROOT / ".local/router-v4-runner" / name, "validation/offline-runner/" + name, optional=True)
    for name in REPRODUCTION:
        archive.add(ROOT / name, "reproduction/" + name, optional=True)
    native_freeze = load(args.native_freeze)
    seals = [plan["policy_freeze"]["seal"], native_freeze.get("native_policy", native_freeze.get("seal", {}))]
    for seal in seals:
        for path, expected in seal.get("files", {}).items():
            if not source_allowed(path):
                raise ValueError("unexpected frozen source closure file")
            archive.add(ROOT / path, "reproduction/" + path, expected=expected)
    for key, descriptor in plan["inputs"].items():
        if key not in {"tasks", "controls", "grading", "provenance"}:
            raise ValueError("unexpected offline public/private input")
        archive.add(Path(descriptor["path"]), "offline/corpus/" + key + ".json", expected=descriptor["sha256"])
    for path, expected in plan["fixture_hashes"].items():
        archive.add(Path(plan["fixtures"]) / path, "corpus/fixtures/" + path, expected=expected)
    for item in plan["assignments"]:
        directory = f"run-{item['ordinal']:04d}"
        for name in ("request.json", "result.json", "stdout.log", "stderr.log"):
            archive.add(args.offline_report.parent / "runs" / directory / name,
                        f"offline/runs/{directory}/{name}", optional=True)
    for name in ("report.md", "metadata.json", "state.json", "experiment-log.jsonl",
                 "execution-preflight.json", "final-response-schema.json"):
        archive.add(args.native_report.parent / name, "native/" + name, optional=True)
    for row in native["runs"]:
        if not row.get("attempted"):
            continue
        directory = Path(row["artifacts"])
        if not directory.is_relative_to(args.native_report.parent / "runs"):
            raise ValueError("native artifacts escaped declared run root")
        for name in NATIVE_FILES:
            if name.startswith("grade/"):
                archive.private_files.add((directory / name).absolute())
            archive.add(directory / name, "native/runs/" + directory.name + "/" + name, optional=True)
    archive.add(args.publication_receipt, "access-preflight/current-publication-readiness.json")
    publication = load(args.publication_receipt)
    by_receipt = {item["receipt_path"]: item for item in publication.get("preflight_history", [])}
    for attempt in readiness_history(publication):
        directory = attempt["directory"]
        descriptor = by_receipt.get(f".local/router-v4/{directory}/receipt.json", {})
        for name in ("start.json", "receipt.json", "schema.json"):
            archive.add(LOCAL / directory / name, f"access-preflight/{directory}/{name}",
                        expected=descriptor.get("receipt_sha256") if name == "receipt.json" else None)
        for name in ("process-identity.json", "command.json", "stderr.log", "prompt.txt", "launch-grant.json", "events.jsonl"):
            archive.add(LOCAL / directory / "attempt" / name, f"access-preflight/{directory}/attempt/{name}",
                        expected=descriptor.get("stderr_sha256" if name == "stderr.log" else "events_sha256" if name == "events.jsonl" else ""))
    research = LOCAL / "research"
    for name in RESEARCH_LEDGERS:
        if not (research / name).exists():
            archive.add(research / name, "research/" + name, optional=True)
            continue
        ledger = load(research / name)
        archive.add(research / name, "research/" + name)
        rows = ledger if isinstance(ledger, list) else ledger.get("requests", ledger.get("rows", []))
        for row in rows:
            snapshot = row.get("snapshot")
            if snapshot:
                if not isinstance(snapshot, str) or Path(snapshot).name != snapshot or not snapshot.endswith(".txt"):
                    raise ValueError("unsafe public research snapshot path")
                archive.add(research / snapshot, "research/" + snapshot, expected=row["sha256"])
    for name in RESEARCH_SCRIPTS:
        archive.add(research / name, "research/" + name, optional=True)
    for specification in args.extra_file:
        source, target = specification.split("=", 1)
        candidate = (ROOT / source).absolute()
        if not candidate.is_relative_to(ROOT):
            raise ValueError("additional evidence must be an explicit file in this checkout")
        archive.add(candidate, "additional/" + target)
    if args.release_native_oracles:
        if args.native_grader_root is None:
            raise ValueError("publishing private grading needs its explicit root")
        hashes = native.get("metadata", {}).get("frozen_manifest", {}).get("grader_files", {})
        for path, expected in hashes.items():
            archive.add(args.native_grader_root / path, "native/private-grading/" + path, expected=expected)


def fmt(value: Any, scale: float = 1) -> str:
    return f"{value * scale:.3f}" if numeric(value) else "—"


def cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def pair(metric: dict[str, Any], scale: float = 1) -> str:
    return fmt(metric.get("mean"), scale) + " / " + fmt(metric.get("median"), scale)


def markdown(data: dict[str, Any], plan: dict[str, Any]) -> str:
    offline, native, outcomes = data["offline_report"], data["native_report"], data["native_outcomes"]
    findings = data["offline_findings"]
    diagnosed_tasks = data["fresh_posthoc_diagnostics"].get("tasks", [])
    impossible_bundles = sum(row.get("declared_bundle_fits_cap") is False for row in diagnosed_tasks)
    attempted = sum(record["attempted"] for record in outcomes.values())
    lines = ["# Memglide router v4: source selection, native readiness and honest limits", "",
             "This report preserves the new offline cohort and the separately planned native coding comparison. "
             "Offline source inclusion is a declared-scope proxy, not coding correctness or semantic dependency completeness. "
             "No claim that Memglide beats Codex on tokens, money, latency or code quality follows without completed matched native tasks.", "",
             f"**Selection-improvement gate: {findings['selection_improvement_gate']['status']}.** "
             f"C delivered the declared positive scope in {findings['selection_improvement_gate']['positive_scope_passes']['C']}/24 observations, "
             f"preserved V3 in {findings['selection_improvement_gate']['positive_scope_passes']['V3']}/24 and known-path B in {findings['selection_improvement_gate']['positive_scope_passes']['B']}/24. "
             "This failed offline admission is a separate blocker: fixing network access alone would not make the current native comparison eligible. "
             "No eligibility receipt is fabricated and no native dispatch is authorized by this collector.", "",
             f"The main measured constraint is a mismatched complete-source budget: **{impossible_bundles}/12 declared bundles cannot fit the frozen 12,000-byte envelope**. "
             "The three feasible bundles still yield no C inclusion, exposing remaining ranking/ambiguity limits. "
             "Detailed post-study diagnosis below separates byte accounting and captured frontiers from newly reproduced parser failures; none replaces an original outcome.", "",
             f"Native status: **{'UNRUN' if not attempted else 'attempted; see strict outcomes below'}**. "
             f"{sum(record['planned'] for record in outcomes.values())} assignments were planned, {attempted} attempted, "
             f"{sum(record['unrun'] for record in outcomes.values())} remain unrun. Unknown token usage and charges are not zero.", "",
             ("The native record is a **report-only blocked-plan snapshot**, not a completed execution report or a model response. "
              "It preserves every actual frozen assignment and all blockers; original pending plan/state/metadata were retained unchanged."
              if data["native_report_publication"]["blocked_plan_snapshot"] else
              "Native record type is retained explicitly in JSON; only attempted rows can support observed execution metrics."), "",
             "## Five observed v3 misses and the bounded repair hypothesis", "",
             "The exposed v3 cohort is development evidence now. These five misses are original negative outcomes, not replaced runs. "
             "A guard repair does not prove that a previously blocked target would rank first or that all five cases are solved.", "",
             "| Prior task | Observed mechanism | Observed receipt | Still unknown |", "| --- | --- | --- | --- |"]
    for row in data["diagnosis"].get("misses", []):
        lines.append("| " + " | ".join(cell(row.get(key, "—")) for key in ("task_id", "mechanism", "observed_reason", "unknown")) + " |")
    lines.extend(["", "V4 preserves complete current-source delivery, existing defaults and old policies. The proposed extension admits only typed, same-hash "
                  "nonproduction parse-only exceptions; applies supported production scope before metadata saturation; and uses a bounded lexical necessary-condition "
                  "stage before the unchanged AST candidate cap. It reads more potential sources locally and guards rejected competitors. "
                  "Synthetic regression/security passes establish only their tested contracts, not fresh held-out accuracy or coding savings.", "",
                  "## Fresh offline comparison", "",
                  f"{len(plan['positive_tasks'])} positives and {len(plan['controls'])} separate normative controls, B/V3/C and two repeats "
                  f"give {len(plan['assignments'])} planned observations. {len(offline['rows'])} original rows are retained; "
                  f"{offline['summary']['unrun_assignments']} are unrun. B receives private oracle-known existing paths; human discovery cost is unmeasured. "
                  "Automatic worker inputs omit target paths, task IDs and grades. Complete source is independently checked against byte-preserved canonical Git.", "",
                  "| Arm | Positive scope passes / planned | Consistent positive tasks | Control bypasses / planned | Envelope integrity, including passthrough | Worker / evaluator errors |",
                  "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for arm in OFFLINE_ARMS:
        item = offline["summary"]["arms"][arm]
        pos, controls = item["positive"], item["abstention_control"]
        lines.append(f"| {arm} | {pos['scope_or_control_passes']}/{pos['planned']} | {len(pos['consistent_tasks_all_repeats'])}/{len(plan['positive_tasks'])} | "
                     f"{controls['scope_or_control_passes']}/{controls['planned']} | {item['fidelity_passes']}/{item['planned']} | {item['worker_errors']} / {item['evaluator_errors']} |")
    lines.extend(["", f"The {len(offline['rows'])} envelope checks include {findings['complete_source_deliveries']} complete-source deliveries and "
                  f"{findings['exact_original_task_passthroughs']} unchanged original-task passthroughs. "
                  "A 100% envelope-integrity rate therefore does not mean that source was retrieved or that coding tasks were solved. "
                  "A safe positive bypass remains a miss. Controls do not offset positive misses; safety/index availability declines are not evidence of semantic discrimination. "
                  "The JSON retains every reason, missing/extra source path and individual receipt.", "",
                  "### Negative inclusion and bundle-availability findings", "",
                  "The known-path control also failed to deliver most declared bundles under the unchanged safety and size/context rules. "
                  "Those original negatives remain in all denominators. `source_unavailable` does not establish a specific root cause; it must not be silently relabeled a context-budget failure. "
                  "Any later diagnostic is post-study evidence, not a replacement outcome or permission to retune this exposed cohort.", "",
                  "| Stratum | Arm | Observed preparation reason | Original observations |", "| --- | --- | --- | ---: |"])
    for kind, arms in findings["reason_counts"].items():
        for arm, values in arms.items():
            for reason, count in sorted(values.items()):
                lines.append(f"| {kind} | {arm} | {cell(reason)} | {count} |")
    lines.extend(["", "| Positive task / repository | Declared source bundle | B | V3 | C |", "| --- | --- | --- | --- | --- |"])
    for task in findings["per_positive_task"]:
        values = [task["task_id"] + " / " + task["repository"], ", ".join(task["required_paths"])]
        for arm in OFFLINE_ARMS:
            outcome = task["outcomes"][arm]
            values.append(f"{outcome['complete']}/{outcome['planned']}; " + "; ".join(mode + "/" + reason for mode, reason in outcome["modes_and_reasons"]))
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    diagnostics = data["fresh_posthoc_diagnostics"]
    feasible = [row for row in diagnostics.get("tasks", []) if row.get("declared_bundle_fits_cap") is True]
    infeasible = [row for row in diagnostics.get("tasks", []) if row.get("declared_bundle_fits_cap") is False]
    lines.extend(["", "### Post-study diagnosis: budget feasibility, frontier and ranking", "",
                  f"Post-study byte accounting finds **{len(infeasible)}/12 declared whole-source bundles exceed the frozen 12,000-byte envelope cap**. "
                  f"Only {', '.join(row['task_id'] for row in feasible)} fit. "
                  "Eight declared raw bodies already exceed the cap; t10 has 11,540 raw bytes but a 12,059-byte framed/escaped envelope. "
                  "The primary 12-task/24-observation denominators remain unchanged. Even the three feasible bundles were delivered by B in both repeats and by C in neither; "
                  "that narrower statement is a post-hoc diagnostic, not a replacement benchmark or promotion result.", "",
                  "| Task | Declared raw source bytes | Framed whole-source bytes | Fits 12,000-byte cap |", "| --- | ---: | ---: | --- |"])
    for row in diagnostics.get("tasks", []):
        raw_bytes = sum(source["raw_bytes"] for source in row.get("declared_sources", []))
        lines.append(f"| {row['task_id']} | {raw_bytes} | {row['single_declared_bundle_json_bytes']} | {row['declared_bundle_fits_cap']} |")
    lines.extend(["", "Recorded coarse frontiers retain 27/28 possible files for t01/t02, still above the unchanged 24-file AST cap. "
                  "The formal t05/t06 reason is generic `runtime_syntax_unavailable`: a **new**, separately retained single-file parser diagnostic finds "
                  "452/488 runtime-plus-declaration units for more.py/more.pyi against a 256-unit limit, while both recipes files parse successfully. "
                  "The original private parser stderr was not retained; this new controlled reproduction supports a mechanism but is not the original batch telemetry, "
                  "a timed comparison or proof of every causal detail. It parses source as data, never imports or executes it.", "",
                  "For feasible bundles, t07 ranks the declared arrays module below MultiRootTree/util and then cannot prepare the chosen source; "
                  "t08 ranks Set first but declines the margin; t12 declines ambiguity between the utility and wrapper. "
                  "These traces expose ranking/abstention limits, not proof that simply lowering a threshold or dropping a competitor would be correct. "
                  "No source, protocol, task, safety cap or original formal outcome was retuned or replaced for these diagnostics.", ""])
    lines.extend(["",
                  "### Offline local overhead", "",
                  "Cells are mean / median. Time/CPU are milliseconds, RSS is MiB. Setup includes approval/index; preparation is the API. "
                  "Imports/startup, worktree creation, independent grading and report writing are outside API timers. Worker lifetime includes startup/serialization/cleanup. "
                  "Parent and waited-child CPU are separate; SELF and maximum child peaks are not incremental memory and must not be summed. "
                  "Observed coverage/missing fields remain in JSON. These local times are not full coding-task latency.", ""])
    lines.extend(["| Positive-task local metric | B mean ms | V3 mean ms | C mean ms | C versus V3 mean change |", "| --- | ---: | ---: | ---: | ---: |"])
    for metric in ("preparation_wall_seconds", "setup_plus_preparation_wall_seconds"):
        means = [offline["summary"]["arms"][arm]["positive"]["metrics"][metric]["mean"] for arm in OFFLINE_ARMS]
        relative = f"{(means[2] / means[1] - 1) * 100:+.2f}%" if numeric(means[1]) and means[1] > 0 and numeric(means[2]) else "—"
        lines.append("| " + metric + " | " + " | ".join(fmt(value, 1000) for value in means) + " | " + relative + " |")
    lines.extend(["", "The additional local work produced no observed automatic inclusion gain in this cohort. "
                  "Zero added context from misses is not measured token or money savings. Paired intervals and per-task variability below remain descriptive and scoped to local preparation.", ""])
    for kind in ("positive", "abstention_control"):
        lines.extend([f"#### {kind}", "", "| Arm | Setup+prep wall | Prep wall | Setup CPU | Prep CPU | Child setup CPU | Child prep CPU | SELF RSS | Max child RSS | Worker lifetime | Added bytes |",
                      "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
        for arm in OFFLINE_ARMS:
            metrics = offline["summary"]["arms"][arm][kind]["metrics"]
            columns = [pair(metrics.get(name, {}), 1 / 1_048_576 if "rss_bytes" in name else 1 if name == "context_bytes" else 1000)
                       for name in OFFLINE_METRICS if name != "selected_source_bytes"]
            lines.append("| " + arm + " | " + " | ".join(columns) + " |")
        lines.append("")
    lines.extend(["### Offline paired uncertainty", "",
                  "C-minus-B/V3 effects are copied from the frozen runner. The primary 2,000-draw bootstrap resamples repository clusters "
                  "and retains their tasks/repeats. Missing pairs, cluster counts and per-task effects are explicit. Small intervals are exploratory, "
                  "unadjusted for multiple comparisons, and do not establish generalization. Shared source bundles and imperfect OS/provider caches remain limits.", "",
                  "| Contrast / stratum / metric | Repositories / pairs | Mean delta | Median delta | Mean 95% interval | Median 95% interval |",
                  "| --- | ---: | ---: | ---: | --- | --- |"])
    for key, effect in offline["summary"]["paired_effects"].items():
        scale = 1000 if key.endswith("seconds") else 1 / 1_048_576 if key.endswith("rss_bytes") else 1
        ci = lambda name: "—" if effect.get(name) is None else "[" + ", ".join(fmt(value, scale) for value in effect[name]) + "]"
        lines.append(f"| {cell(key)} | {effect['repository_clusters']} / {effect['pairs']} | {fmt(effect['mean_delta'], scale)} | "
                     f"{fmt(effect['median_delta'], scale)} | {ci('mean_bootstrap95')} | {ci('median_bootstrap95')} |")
    lines.extend(["", "## Native coding comparison and actual spend", "",
                  "A is bare Codex, B is oracle-known-path source-only, and C is automatic v4 source-only. Native task prompts are distinct from offline queries "
                  "while repositories may be shared, which is disclosed exposure. Strict native success requires a completed valid exact-model stream, complete source treatment, "
                  "protected-file integrity and independent behavior grading. Failed attempts remain in the cost numerator. A structured final answer alone is not a correctness grade.", "",
                  "The native graders have known coverage limits: Python candidate code runs in the assertion process, so procedural separation alone does not establish "
                  "resistance to candidate interference with result reporting; n02's gzip-level preservation is not directly asserted. "
                  "Independent replay observed the expected 12 baseline failures and 12 reference passes with unchanged hashes, but those controls do not demonstrate "
                  "comprehensive or adversarial grading. A proposed synthetic tampering check was rejected by automatic review and remains **UNRUN**; no tested exploit is claimed. "
                  "Future native dispatch is also blocked on grader hardening, independently of the failed selection gate and access denial.", "",
                  "The native public manifest was amended **after** the offline cohort and **before** any native plan/dispatch: n06's slash-separated prose "
                  "`key/reverse/nonempty` became `key, reverse, and nonempty` so the frozen validator would not treat it as a source path. "
                  "This is a documented protocol deviation, not untouched pre-offline prompt bytes. The original manifest, authority's 75-file SHA seal and all earlier seals remain retained; "
                  "the separate v2 manifest/authority seal changes task-digest bindings and paths while preserving source, grader, reference and vendored file bytes. "
                  "The author reran 24 standard controls and the independent reviewer separately replayed 24 for each version; repeated controls are not additional coding tasks. "
                  "The six original integrity controls are historical and were not rerun for v2. Public replay evidence contains explicit outcome/count/hash projections only; "
                  "private reference bodies and oracle-control details remain local. The independent author received no selector outcomes.", "",
                  "The complete static review also limits protected-file scopes (they can reject valid broader refactors), host filesystem isolation, "
                  "independently authenticated compiler provenance/API closure, and the unfinished full TypeScript semantic-oracle review. "
                  "The six exact findings and the rejected-check status are retained in the hash-verified audit, not relabeled comprehensive correctness.", "",
                  "| Arm | State | Planned | Attempted | Unrun | Strict successes | Success rate | Historical-scenario cost / strict success | Actual charges |",
                  "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for arm, outcome in outcomes.items():
        lines.append(f"| {arm} | {outcome['status']} | {outcome['planned']} | {outcome['attempted']} | {outcome['unrun']} | "
                     f"{fmt(outcome['strict_successes'])} | {fmt(outcome['strict_success_rate'])} | "
                     f"{fmt(outcome['historical_tariff_scenario']['cost_per_strict_success_usd'])} | — |")
    lines.extend(["", "No attempted runs means no measured coding-success rate, model usage, full task latency or cost per success. "
                  "Native API-price equivalents, if present, are historical tariff scenarios from frozen pricing evidence; current applicability and actual account charges are unknown. "
                  "One unavailable attempt cost makes the complete aggregate and cost per success unavailable. Known partial subtotals are labeled separately. "
                  "Native-reported zero cache writes can be an upstream decoding default and do not prove zero provider cache writes.", "",
                  f"There are **{len(data['native_readiness_history'])} separately counted real access invocations**, including the check after publication. "
                  "The two original checks timed out with HTTP CONNECT 403 and no completed-turn usage. Their underlying provider calls, token usage and charges are unknown, "
                  "so whole-experiment spend remains **unknown**, even when formal assignments are all unrun.", "",
                  "The newer configuration **was published** with `chatgpt.com`, `auth.openai.com` and `developers.openai.com`. "
                  "The post-publication diagnostic recorded that the attached worker still enforced the original source version/policy, with all three hosts absent. "
                  "Publishing did not establish that worker migration; the second denied readiness check observed no usable connection. "
                  "The earlier network-readiness.json is preserved as a historical pre-publication receipt, not current publication status. "
                  "Proxy denial does not verify credential validity or expiry. The collector launches nothing and performs no retry.", "",
                  f"Latest retained publication/readiness receipt: ready = **{data['current_publication_readiness'].get('ready')}**; "
                  f"blocker = {cell(data['current_publication_readiness'].get('blocker', 'none recorded'))}. "
                  "Exact published/attached version IDs, host membership and diagnostic timestamps are retained in JSON and the separately archived receipt.", "",
                  "| Access attempt | Ready | Local wall seconds | Completed turns observed | Whole usage coverage | Provider calls | Billed charges |",
                  "| --- | --- | ---: | ---: | --- | ---: | ---: |"])
    for attempt in data["native_readiness_history"]:
        lines.append(f"| {attempt['directory']} | {attempt['ready']} | {fmt(attempt['wall_seconds'])} | "
                     f"{attempt['observed_completed_turns']} | {attempt['usage_coverage_complete']} | {fmt(attempt['actual_model_calls'])} | {fmt(attempt['actual_billed_charges'])} |")
    lines.extend(["",
                  "The configured dollar gate is a soft pre-launch admission check with historical possible-write assumptions and a reserve, not a hard invoice cap. "
                  "Any later admission needs a completed meaningful readiness observation, frozen model/settings/graders and an estimated maximum budget. "
                  "No matched completed native cohort means no claim of Codex outperformance.", "",
                  "### Observed native metrics", "",
                  "Cells are mean / median as reported; unavailable values remain unavailable. Full instrumented task time includes cold B/C indexing, preparation and native execution, "
                  "and excludes worktree construction and independent behavioral grading. Process sampling describes local CPU/RSS only and can miss short-lived processes. "
                  "Repeated-read commands are heuristic intent proxies, not actual filesystem reads; underlying model-call counts and billed cost remain unavailable unless explicitly observed.", "",
                  "| Metric | A | B | C |", "| --- | ---: | ---: | ---: |"])
    for name in NATIVE_METRICS:
        values = [pair(outcomes[arm]["reported_arm_metrics"].get(name, {})) if outcomes[arm]["attempted"] else "UNRUN" for arm in NATIVE_ARMS]
        lines.append("| " + name + " | " + " | ".join(values) + " |")
    lines.extend(["", "Native paired effects and per-task variability are retained verbatim in JSON. With no complete matched observations, they cannot establish an effect. "
                  "The source engine parses repository data only; external behavioral graders explicitly execute code in the separately authorized coding benchmark. "
                  "That execution is not a source-retrieval feature. Private grading is outside indexed roots; this is procedural separation rather than an OS read-access boundary.", "",
                  "## Validation, development failures and evidence", "",
                  "Development regressions, reviewer counterexamples, component/CLI/application/frontend/browser/installed checks and actual fresh held-out outcomes are separate evidence. "
                  "Focused or repeated runtime counts overlap full suites and are not summed. Initial failures and repair receipts are retained, including unavailable raw output noted by their ledgers.", "",
                  "After formal timing, a new `benchmarks/.ruff.toml` exempted immutable upstream fixture code from application lint. "
                  "Its first child-config version caused eight I001 import-classification errors; explicitly restoring the root `src` classification fixed this new configuration only. "
                  "This was a verification-process repair, not an application defect or a frozen-fixture/code change. "
                  "The 57-case post-corpus harness run overlaps the existing 2,341-case suite and is not added to that distinct-case count. "
                  "Post-study preservation independently rehashed the frozen closure and prior archive; exact receipts remain separate from performance observations.", "",
                  "Latest owner synthetic development ledger: "
                  f"**{data['development_ledger'].get('final_tests', {}).get('passed', 'unavailable')} passed**, "
                  f"{data['development_ledger'].get('final_tests', {}).get('failed', 'unavailable')} failed. "
                  "This is a development regression count, not a fresh task count or additional distinct full-suite total.", "",
                  "| XML receipt | Passed | Failures / errors / skipped |", "| --- | ---: | ---: |"])
    for name, counts in data["validation_xml"].items():
        lines.append(f"| {cell(name)} | {counts['passed']} | {counts['failures']} / {counts['errors']} / {counts['skipped']} |")
    lines.extend(["", "The complete diagnosis, development ledger, reviewer controls, research fetch successes/failures and final audit receipts are archived. "
                  "No synthetic count is relabeled a held-out task. Original v3 history remains unchanged; preservation is independently recorded. "
                  "Safety checks and exact source delivery do not prove SaaS multi-tenant operational readiness or a universally optimal architecture.", "",
                  "## Every original offline observation", "",
                  "| # | Task | Arm | Kind | Outcome | Mode / reason | Prep ms | Worker ms | Added bytes |",
                  "| ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: |"])
    index = {row["ordinal"]: row for row in offline["rows"]}
    for assignment in plan["assignments"]:
        row = index.get(assignment["ordinal"], {})
        prep = (row.get("observation") or {}).get("preparation", {})
        valid = row.get("worker_completed") is True and row.get("fidelity", {}).get("valid") is True
        field = "declared_scope_complete" if assignment["kind"] == "positive" else "expected_bypass"
        status = "UNRUN" if not row else "invalid/error" if not valid else "scope/control pass" if row.get("scope_grade", {}).get(field) is True else "miss/unexpected preload"
        values = [assignment["ordinal"], assignment["task_id"], assignment["arm"], assignment["kind"], status,
                  prep.get("mode", "—") + " / " + prep.get("reason", "—"), fmt(row.get("metrics", {}).get("preparation_wall_seconds"), 1000),
                  fmt(row.get("process_wall_seconds"), 1000), fmt(row.get("metrics", {}).get("context_bytes"))]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.extend(["", "## Every planned native assignment", "",
                  "| Run | Task | Arm | Repeat | Attempted | Outcome | Strict success | Full instrumented time s | Historical-scenario USD |",
                  "| --- | --- | --- | ---: | --- | --- | --- | ---: | ---: |"])
    for row in native["runs"]:
        attempted_row = row.get("attempted") is True
        values = [row.get("run_id", "—"), row.get("task_id", "—"), row["configuration"], row.get("repeat", "—"), attempted_row,
                  row.get("status") if attempted_row else "UNRUN", strict_success(row) if attempted_row else "unavailable",
                  fmt(row.get("end_to_end_wall_seconds")) if attempted_row else "—",
                  fmt(row.get("api_price_equivalent", {}).get("native_reported_price_equivalent_usd")) if attempted_row else "—"]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.extend(["", "## Reproduction and next experiments", "",
                  "The JSON includes every original row, raw summaries/paired uncertainty, planned denominator, unknown metric and audit. "
                  "`evidence/router-v4/ledger.json` hashes the explicit archive allowlist; no databases, Git internals, worktrees, environments, auth state, "
                  "token values, dependency trees, wheels or binary archives are collected. Any failed collection remains in a separately named local staging directory. "
                  "Historical studies are not overwritten. Private native oracle bodies are "
                  + ("published by explicit collector flag after cohort retirement." if data["private_oracles_published"] else "withheld; their frozen SHA manifest and independently verified control counts may be public, while reference bodies and raw oracle controls remain local. Any published projection is labeled, never called exact raw evidence."), "",
                  "Native report publication: **" + ("declared public projection; exact original remains local and hashed" if data["native_report_publication"]["is_projection"] else "exact report-only blocked-plan snapshot" if data["native_report_publication"]["blocked_plan_snapshot"] else "exact original report") + "**. "
                  "Projection provenance, if used, records both hashes and does not replace the locally preserved full artifact.", "",
                  "Check out the recorded frozen commits, use `uv sync --frozen`, restore the archived public corpus and licenses at the documented benchmark paths, "
                  "and follow the generic frozen protocols using **new** freeze/plan/output directories. Original absolute paths and timestamps are evidence, not portable executable plans. "
                  "Restore local helper scripts to their original `.local/router-v4` locations or adapt new copies; never execute them in-place expecting old absolute paths to work. "
                  "The collector itself only reads finished artifacts. Do not execute upstream package install/build hooks during indexing.", "",
                  "Use the fresh offline results to decide whether another frozen candidate is justified. Diagnose new misses without calling exposed tasks a fresh tuning holdout. "
                  "After a meaningful network state change, repeat only the bounded readiness check; preserve that canary's usage/spend separately. "
                  "The current selection-improvement gate failed, so do not run its planned native comparison even if connectivity becomes usable. "
                  "A future candidate needs a new frozen evaluation with independently justified admission; preserve this cohort and every current native UNRUN assignment. "
                  "Only an eligible future matched comparison can measure strict cost per successful task, all failed-attempt spend, "
                  "cached/uncached/output usage and full instrumented time; keep v4 opt-in unless that evidence supports promotion.", ""])
    return "\n".join(lines)


def xml_counts(path: Path) -> dict[str, int]:
    tree = ET.fromstring(regular(path))
    suites = [item for item in tree.iter("testsuite") if not item.findall("testsuite")]
    result = {key: sum(int(item.get(key, "0")) for item in suites) for key in ("tests", "failures", "errors", "skipped")}
    result["passed"] = result["tests"] - sum(result[key] for key in ("failures", "errors", "skipped"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline-report", type=Path, default=ROOT / ".local/router-v4-offline/report.json")
    parser.add_argument("--offline-plan", type=Path, default=ROOT / ".local/router-v4-offline-plan/plan.json")
    parser.add_argument("--offline-freeze", type=Path, default=ROOT / ".local/router-v4-policy-freeze/policy-freeze.json")
    parser.add_argument("--fresh-diagnostics", type=Path, default=LOCAL / "fresh-failure-diagnostics/diagnosis.json")
    parser.add_argument("--native-report", type=Path, default=ROOT / ".local/router-v4-native-blocked/report.json")
    parser.add_argument("--native-plan", type=Path, help="Defaults to the native report's sibling plan.json")
    parser.add_argument("--native-public-report", type=Path, help="Optional reviewed projection omitting only private oracle answers; original stays local and hashed")
    parser.add_argument("--publication-receipt", type=Path, default=LOCAL / "publication-readiness.json")
    parser.add_argument("--native-freeze", type=Path, required=True)
    parser.add_argument("--native-grader-root", type=Path)
    parser.add_argument("--release-native-oracles", action="store_true")
    parser.add_argument("--private-file", type=Path, action="append", default=[], help="Exact local oracle/control or mixed-audit bodies to hash but withhold; no semantic redaction is inferred")
    parser.add_argument("--extra-file", action="append", default=[], help="Explicit root-relative source=archive-relative target; no recursive collection")
    parser.add_argument("--prefix", type=Path, default=ROOT / "benchmarks/router-v4-assessment")
    parser.add_argument("--evidence", type=Path, default=ROOT / "benchmarks/evidence/router-v4")
    args = parser.parse_args()
    for key, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, key, value.absolute())
    if args.native_plan is None:
        args.native_plan = args.native_report.parent / "plan.json"
    if args.evidence.exists() or any(args.prefix.with_suffix(suffix).exists() for suffix in (".json", ".md")):
        raise ValueError("final outputs must be new; previous collections are never overwritten")
    number = 1
    while (LOCAL / f"collection-{number:03d}").exists():
        number += 1
    staging = LOCAL / f"collection-{number:03d}"
    staging.mkdir()
    receipt = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "status": "started", "collector_sha256": sha(regular(Path(__file__).resolve()))}
    save(staging / "start.json", receipt)
    try:
        offline, plan, native = load(args.offline_report), load(args.offline_plan), load(args.native_public_report or args.native_report)
        if len(plan["assignments"]) != 96:
            raise ValueError("collector requires all96 offline plans and72 native rows including UNRUN")
        validate_native_rows(native, load(args.native_plan))
        publication = load(args.publication_receipt)
        history = readiness_history(publication)
        private_files = {path.absolute() for path in args.private_file}
        if args.native_public_report:
            private_files.add(args.native_report)
            private_files.update(args.native_report.parent / name for name in ("metadata.json", "state.json", "report.md", "execution-preflight.json"))
            private_files.update(Path(row["artifacts"]) / "result.json" for row in native["runs"] if row.get("attempted") and row.get("artifacts"))
        elif args.native_report in private_files and not args.release_native_oracles:
            raise ValueError("a private original native report requires a reviewed public projection")
        archive = Archive(staging / "evidence", private_files=private_files,
                          release_native_oracles=args.release_native_oracles)
        collect(args, offline, plan, native, archive)
        data = {"version": "router-v4-assessment-1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "offline_report": offline, "offline_assignments": plan["assignments"],
                "offline_findings": offline_findings(offline, plan), "native_report": native,
                "native_corpus_publication": native_corpus_publication(),
                "fresh_posthoc_diagnostics": load(args.fresh_diagnostics),
                "native_report_publication": {"is_projection": args.native_public_report is not None,
                                              "record_kind": native.get("record_kind"),
                                              "blocked_plan_snapshot": native.get("record_kind") == "blocked_native_plan_snapshot"
                                                                       and native.get("metadata", {}).get("report_only_projection") is True,
                                              "original_sha256": sha(regular(args.native_report)),
                                              "published_sha256": sha(regular(args.native_public_report or args.native_report)),
                                              "scope": "Only root-reviewed omission of private oracle answers is allowed; exact original remains local."},
                "native_outcomes": native_outcomes(native), "diagnosis": load(LOCAL / "diagnosis.json"),
                "historical_prepublication_network_readiness": load(LOCAL / "network-readiness.json"),
                "current_publication_readiness": publication, "native_readiness_history": history,
                "original_native_preflight": history[0]["receipt"],
                "development_ledger": load(LOCAL / "development-ledger.json"), "historical_preservation": load(LOCAL / "historical-preservation.json"),
                "validation_xml": {item["path"]: xml_counts(staging / "evidence" / item["path"]) for item in archive.files if item["path"].endswith(".xml")},
                "private_oracles_published": args.release_native_oracles, "withheld_local_native_oracle_files": archive.withheld,
                "native_frozen_private_file_sha256": native.get("metadata", {}).get("frozen_manifest", {}).get("grader_files", {}),
                "default_promotion": False,
                "native_grade_coverage_limits": {"baseline_reference_replay": "12 expected baseline failures and 12 reference passes; not proof of adversarial grading",
                                                 "known_static_limits": load(LOCAL / "native-corpus-review/audit.json")["known_limits"],
                                                 "python_candidate_in_assertion_process": True,
                                                 "gzip_level_preservation_directly_asserted": False,
                                                 "synthetic_tampering_check_status": "UNRUN_AUTOMATIC_REVIEW_REJECTED",
                                                 "automatic_review_stated_reason": "possible cybersecurity risk",
                                                 "tested_exploit_claimed": False,
                                                 "future_native_grader_hardening_required": True},
                "verification_process_notes": ["The post-study benchmark lint config initially caused 8 I001 import-classification errors; only the new config was repaired, outside frozen source/fixture seals.",
                                               "The 57-case post-corpus harness overlaps the existing 2341-case suite; counts are not added.",
                                               "Original source-scope outcomes, failed gate, all denominators and both failed access receipts are preserved."],
                "whole_experiment_billed_cost_usd": None, "whole_experiment_price_equivalent_usd": None,
                "unknown_spend_reason": "Both retained access checks have incomplete usage; unknown preflight spend is never replaced by zero.",
                "collector_dispatched_model_or_policy_requests": 0, "archive_files": len(archive.files), "missing_optional_evidence": archive.missing,
                "limits": ["Offline scope is not coding correctness or semantic completeness.", "No native attempted assignment means native success/usage/cost effects remain unknown, not zero.",
                           "Historical tariff equivalents are scenario estimates, not current verified rates or invoices.", "Whole-experiment spend includes separate canaries with unknown usage and remains unknown.",
                           "Synthetic regressions are not fresh heldout results. Private grader execution is an explicit coding-benchmark activity; source retrieval parses data only.",
                           "The native v2 punctuation repair occurred after offline evaluation, before native planning; its prompts are not an untouched pre-offline byte freeze.",
                           "Native replay controls do not establish comprehensive/adversarial grading; the proposed tampering check was rejected and remains unrun."]}
        save(staging / "evidence/ledger.json", {"version": 1, "files": archive.files, "missing_optional": archive.missing,
                                               "ledger_and_standalone_assessment_not_self_hashed": True})
        data["ledger_sha256"] = sha(regular(staging / "evidence/ledger.json"))
        save(staging / "assessment.json", data)
        (staging / "assessment.md").write_text(markdown(data, plan), encoding="utf-8")
        # All construction precedes publication; failed staging directories remain.
        shutil.move(str(staging / "evidence"), args.evidence)
        (staging / "assessment.json").rename(args.prefix.with_suffix(".json"))
        (staging / "assessment.md").rename(args.prefix.with_suffix(".md"))
        save(staging / "result.json", {"status": "completed", "evidence": str(args.evidence), "assessment": str(args.prefix),
                                      "files": len(archive.files), "offline_report_sha256": sha(regular(args.offline_report)), "native_report_sha256": sha(regular(args.native_report))})
        print(json.dumps({"status": "completed", "assessment": str(args.prefix), "files": len(archive.files)}))
    except BaseException as error:
        save(staging / "failure.json", {"status": "failed", "type": type(error).__name__, "error": str(error), "preserved_staging": str(staging)})
        raise


if __name__ == "__main__":
    main()
