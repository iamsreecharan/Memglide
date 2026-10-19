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
    "final-cohort-verification.json", "build-static.json", "environment.json", "historical-preservation.json",
    "network-readiness.json", "native_preflight.py", "native-preflight-output.log",
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
    ".github/workflows/verify.yml",
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
        costs = [row.get("api_price_equivalent", {}).get("native_reported_price_equivalent_usd") for row in attempted]
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
                                           "actual_billed_charges_usd": None},
            "reported_arm_metrics": report.get("arms", {}).get(arm, {}).get("metrics", {}),
        }
    return result


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
                                  "sha256": actual, "bytes": len(data), "reason": "Unrun native oracle body withheld; exact original retained locally"})
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
    for name in RECEIPTS:
        archive.add(LOCAL / name, "validation/" + name, optional=True)
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
    for name in ("report.md", "plan.json", "metadata.json", "state.json", "experiment-log.jsonl",
                 "execution-preflight.json", "final-response-schema.json"):
        archive.add(args.native_report.parent / name, "native/" + name, optional=True)
    for row in native["runs"]:
        if not row.get("attempted"):
            continue
        directory = Path(row["artifacts"])
        if not directory.is_relative_to(args.native_report.parent / "runs"):
            raise ValueError("native artifacts escaped declared run root")
        for name in NATIVE_FILES:
            archive.add(directory / name, "native/runs/" + directory.name + "/" + name, optional=True)
    for name in ("start.json", "receipt.json", "schema.json"):
        archive.add(LOCAL / "native-preflight" / name, "access-preflight/" + name)
    for name in ("process-identity.json", "command.json", "stderr.log", "prompt.txt", "launch-grant.json", "events.jsonl"):
        archive.add(LOCAL / "native-preflight/attempt" / name, "access-preflight/attempt/" + name)
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
    attempted = sum(record["attempted"] for record in outcomes.values())
    lines = ["# Memglide router v4: source selection, native readiness and honest limits", "",
             "This report preserves the new offline cohort and the separately planned native coding comparison. "
             "Offline source inclusion is a declared-scope proxy, not coding correctness or semantic dependency completeness. "
             "No claim that Memglide beats Codex on tokens, money, latency or code quality follows without completed matched native tasks.", "",
             f"Native status: **{'UNRUN' if not attempted else 'attempted; see strict outcomes below'}**. "
             f"{sum(record['planned'] for record in outcomes.values())} assignments were planned, {attempted} attempted, "
             f"{sum(record['unrun'] for record in outcomes.values())} remain unrun. Unknown token usage and charges are not zero.", "",
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
                  "| Arm | Positive scope passes / planned | Consistent positive tasks | Control bypasses / planned | Valid deliveries | Worker / evaluator errors |",
                  "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for arm in OFFLINE_ARMS:
        item = offline["summary"]["arms"][arm]
        pos, controls = item["positive"], item["abstention_control"]
        lines.append(f"| {arm} | {pos['scope_or_control_passes']}/{pos['planned']} | {len(pos['consistent_tasks_all_repeats'])}/{len(plan['positive_tasks'])} | "
                     f"{controls['scope_or_control_passes']}/{controls['planned']} | {item['fidelity_passes']}/{item['planned']} | {item['worker_errors']} / {item['evaluator_errors']} |")
    lines.extend(["", "A safe positive bypass remains a miss. Controls do not offset positive misses; safety/index availability declines are not evidence of semantic discrimination. "
                  "The JSON retains every reason, missing/extra source path and individual receipt.", "",
                  "### Offline local overhead", "",
                  "Cells are mean / median. Time/CPU are milliseconds, RSS is MiB. Setup includes approval/index; preparation is the API. "
                  "Imports/startup, worktree creation, independent grading and report writing are outside API timers. Worker lifetime includes startup/serialization/cleanup. "
                  "Parent and waited-child CPU are separate; SELF and maximum child peaks are not incremental memory and must not be summed. "
                  "Observed coverage/missing fields remain in JSON. These local times are not full coding-task latency.", ""])
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
                  "The original access canary is a separate real invocation: it timed out with HTTP CONNECT 403 from the inherited proxy and no completed-turn usage. "
                  "Its provider calls, token usage and charges are unknown, so whole-experiment spend remains **unknown**, even if formal assignments are all unrun. "
                  "The network receipt lists `chatgpt.com`, `auth.openai.com` and `developers.openai.com`; the saved draft requires publication and is not evidence of applied connectivity. "
                  "Login status alone does not establish a usable provider connection. The collector launches nothing and performs no retry.", "",
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
                  "Native report publication: **" + ("declared public projection; exact original remains local and hashed" if data["native_report_publication"]["is_projection"] else "exact original report") + "**. "
                  "Projection provenance, if used, records both hashes and does not replace the locally preserved full artifact.", "",
                  "Check out the recorded frozen commits, use `uv sync --frozen`, restore the archived public corpus and licenses at the documented benchmark paths, "
                  "and follow the generic frozen protocols using **new** freeze/plan/output directories. Original absolute paths and timestamps are evidence, not portable executable plans. "
                  "Restore local helper scripts to their original `.local/router-v4` locations or adapt new copies; never execute them in-place expecting old absolute paths to work. "
                  "The collector itself only reads finished artifacts. Do not execute upstream package install/build hooks during indexing.", "",
                  "Use the fresh offline results to decide whether another frozen candidate is justified. Diagnose new misses without calling exposed tasks a fresh tuning holdout. "
                  "After a meaningful network state change, repeat only the bounded readiness check; preserve that canary's usage/spend separately. "
                  "Run the already frozen matched native plan only when admission controls are satisfied. Compare strict cost per successful task, all failed-attempt spend, "
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
    parser.add_argument("--offline-plan", type=Path, default=ROOT / ".local/router-v4-plan/plan.json")
    parser.add_argument("--offline-freeze", type=Path, default=ROOT / ".local/router-v4-policy-freeze/policy-freeze.json")
    parser.add_argument("--native-report", type=Path, default=ROOT / ".local/router-v4-native/report.json")
    parser.add_argument("--native-public-report", type=Path, help="Optional reviewed projection omitting only private oracle answers; original stays local and hashed")
    parser.add_argument("--native-freeze", type=Path, required=True)
    parser.add_argument("--native-grader-root", type=Path)
    parser.add_argument("--release-native-oracles", action="store_true")
    parser.add_argument("--private-file", type=Path, action="append", default=[], help="Exact local oracle/control bodies to hash but withhold unless cohort retirement is explicit")
    parser.add_argument("--extra-file", action="append", default=[], help="Explicit root-relative source=archive-relative target; no recursive collection")
    parser.add_argument("--prefix", type=Path, default=ROOT / "benchmarks/router-v4-assessment")
    parser.add_argument("--evidence", type=Path, default=ROOT / "benchmarks/evidence/router-v4")
    args = parser.parse_args()
    for key, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, key, value.absolute())
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
        if len(plan["assignments"]) != 96 or len(native["runs"]) != 72:
            raise ValueError("collector requires all96 offline plans and72 native rows including UNRUN")
        private_files = {path.absolute() for path in args.private_file}
        if args.native_public_report:
            private_files.add(args.native_report)
        archive = Archive(staging / "evidence", private_files=private_files,
                          release_native_oracles=args.release_native_oracles)
        collect(args, offline, plan, native, archive)
        data = {"version": "router-v4-assessment-1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "offline_report": offline, "offline_assignments": plan["assignments"], "native_report": native,
                "native_report_publication": {"is_projection": args.native_public_report is not None,
                                              "original_sha256": sha(regular(args.native_report)),
                                              "published_sha256": sha(regular(args.native_public_report or args.native_report)),
                                              "scope": "Only root-reviewed omission of private oracle answers is allowed; exact original remains local."},
                "native_outcomes": native_outcomes(native), "diagnosis": load(LOCAL / "diagnosis.json"),
                "network_readiness": load(LOCAL / "network-readiness.json"), "original_native_preflight": load(LOCAL / "native-preflight/receipt.json"),
                "development_ledger": load(LOCAL / "development-ledger.json"), "historical_preservation": load(LOCAL / "historical-preservation.json"),
                "validation_xml": {item["path"]: xml_counts(staging / "evidence" / item["path"]) for item in archive.files if item["path"].endswith(".xml")},
                "private_oracles_published": args.release_native_oracles, "withheld_local_native_oracle_files": archive.withheld,
                "native_frozen_private_file_sha256": native.get("metadata", {}).get("frozen_manifest", {}).get("grader_files", {}),
                "default_promotion": False,
                "whole_experiment_billed_cost_usd": None, "whole_experiment_price_equivalent_usd": None,
                "unknown_spend_reason": "Original access preflight has incomplete usage; unknown preflight spend is never replaced by zero.",
                "collector_dispatched_model_or_policy_requests": 0, "archive_files": len(archive.files), "missing_optional_evidence": archive.missing,
                "limits": ["Offline scope is not coding correctness or semantic completeness.", "No native attempted assignment means native success/usage/cost effects remain unknown, not zero.",
                           "Historical tariff equivalents are scenario estimates, not current verified rates or invoices.", "Whole-experiment spend includes separate canaries with unknown usage and remains unknown.",
                           "Synthetic regressions are not fresh heldout results. Private grader execution is an explicit coding-benchmark activity; source retrieval parses data only."]}
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
