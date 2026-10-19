"""Collect an explicit offline-v3 evidence allowlist and write an honest assessment.

This is a post-study collector, not a benchmark dispatcher. It never imports the
application, executes indexed source, queries a model or reruns an observation.
Run only after the operator reviews this file and the formal audit is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local/router-v3"
ARMS = ("B", "V1", "V2", "C")
KINDS = ("all", "positive", "abstention_control")
METRICS = (
    "setup_plus_preparation_wall_seconds", "preparation_wall_seconds",
    "preparation_cpu_seconds", "setup_cpu_seconds",
    "setup_waited_child_cpu_seconds", "preparation_waited_child_cpu_seconds",
    "self_peak_rss_bytes", "max_waited_child_rss_bytes", "context_bytes",
    "selected_source_bytes", "process_wall_seconds",
)
VALIDATION_FILES = (
    "full-python.xml", "full-python.log", "full-python-before-corpus.xml", "full-python-before-corpus.log",
    "corpus-schema-regression.xml", "affected-initial.xml", "affected-final.xml",
    "integration-initial.xml", "integration-final.xml", "python311-compatibility.xml",
    "python311-router.xml", "python311-full.xml", "python311-full.log",
    "python311-full-initial.xml", "python311-full-initial.log",
    "final-cohort-verification.json", "frontend-unit.json", "frontend-browser.json",
    "frontend-browser.raw.log", "installed-smoke-initial.json",
    "installed-smoke-initial.stdout.log", "installed-smoke-initial.stderr.log",
    "installed_smoke-initial.py", "installed-smoke.json", "installed-smoke.stdout.log",
    "installed-smoke.stderr.log", "installed_smoke.py", "security-review.json",
    "runner-review.json", "independent-corpus-audit.json", "audit_corpus.py", "audit_results.py",
    "posthoc-diagnostics.json", "posthoc-diagnostics.py",
    "final-compatibility-review.json",
    "build-static.json", "environment.json", "dev-attempts.json", "owned-tests-final.log",
    "source-resilience-initial.xml", "automatic-v3-runner-unit.xml",
    "automatic-v3-runner-unit-final.xml", "automatic-v3-runner-unit-final-2.xml",
    "automatic-v3-runner-unit-final-3.xml", "runner-unit-final.xml",
    "runtime-requirements.txt", "runtime-export.log", "actionlint/download.json",
    "actionlint/actionlint_1.7.7_checksums.txt", "actionlint/result.log",
)
RESEARCH_FILES = (
    "fetch_sources.py", "fetch-ledger.json", "followup-fetch-ledger.json",
    "jsonl-followup-fetch-ledger.json", "repoformer-readme.txt", "repocoder-readme.txt",
    "repocoder-search-code.txt", "repocoder-build-vector.txt", "sqlite-fts5-bm25.txt",
    "typescript-38-type-imports.txt", "typescript-50-modules.txt", "tree-sitter-query-syntax.txt",
    "tree-sitter-typescript-node-types.txt", "tree-sitter-python-node-types.txt",
    "cpython-311-ast.txt", "cpython-312-ast.txt", "codex-exec-doc.txt",
    "codex-exec-cli.txt", "codex-exec-lib.txt", "codex-exec-jsonl.txt",
)
REPRODUCTION_FILES = (
    "benchmarks/router-v3-research.md", "benchmarks/router-v3-research.json",
    "docs/runtime-aware-routing.md", "tests/test_runtime_evidence.py",
    "tests/test_auto_preload_v3.py", "tests/test_codex_router_v3.py",
    "tests/test_source_resilience.py", "tests/test_benchmark_corpus_warm.py", ".github/workflows/verify.yml",
    "frontend/package.json", "frontend/package-lock.json",
)
FAILURE_NOTES = [
    "Owner development: 43 passed/6 failed, then 48 passed/3 failed; the final owned run passed 51. dev-attempts.json records causes. Original stdout was not saved and is not reconstructed.",
    "First root integration run: 89 passed/1 failed because a tamper fixture did not change any bytes. The new fixture was corrected; final 90 passed.",
    "First affected run: 348 passed/1 failed because the formerly unknown version v3 became valid. The unknown-version assertion was retained with v99; final 349 passed.",
    "Initial installed-wheel smoke reached 17 checks, then received the correct HTTP 403 because the helper omitted the required request header. Initial script, receipt and logs remain; final helper supplies the header and explicitly tests rejection, with 20 checks passing.",
    "Earlier runner synthetic receipts are retained alongside final receipts; these development observations are not held-out benchmark assignments.",
    "After the frozen cohort finished, the first complete Python 3.11 run with the fresh corpus had 2,187 passed/1 failed: an older tasks*.json corpus validator assumed every manifest was a dictionary, while frozen v3 uses a declared list schema. This post-study minimal test-only schema normalization retained every freshness assertion; its targeted regression and both complete runtime suites were rerun with the corpus present. No frozen production, runner or corpus bytes changed. The earlier Python 3.12 run passed 2,188 before corpus creation and is separately labeled.",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def regular(path: Path, maximum: int = 64_000_000) -> bytes:
    if path.is_symlink() or path.resolve(strict=True) != path.absolute() or not path.is_file():
        raise ValueError(f"not a canonical regular file: {path}")
    data = path.read_bytes()
    if len(data) > maximum:
        raise ValueError(f"file exceeded collector cap: {path}")
    return data


def load(path: Path) -> Any:
    return json.loads(regular(path), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def write_json(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def number(value: Any) -> bool:
    return type(value) in {float, int} and math.isfinite(value)


def good(row: dict[str, Any]) -> bool:
    return row.get("worker_completed") is True and row.get("fidelity", {}).get("valid") is True


def stats(values: list[float | int], planned: int) -> dict[str, Any]:
    return {"observed": len(values), "missing_of_planned": planned - len(values),
            "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "minimum": min(values) if values else None, "maximum": max(values) if values else None}


def summaries(rows: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    grading = plan["grading"]
    output = {}
    for kind in KINDS:
        output[kind] = {}
        for arm in ARMS:
            planned = [item for item in plan["assignments"] if item["arm"] == arm
                       and (kind == "all" or grading[item["task_id"]]["kind"] == kind)]
            selected = [row for row in rows if row["arm"] == arm
                        and (kind == "all" or grading[row["task_id"]]["kind"] == kind)]
            metrics = {}
            for metric in METRICS:
                values = [row.get("process_wall_seconds") if metric == "process_wall_seconds"
                          else row.get("metrics", {}).get(metric) for row in selected]
                metrics[metric] = stats([value for value in values if number(value)], len(planned))
            decisions, reasons = {}, {}
            for row in selected:
                preparation = (row.get("observation") or {}).get("preparation", {})
                automatic = preparation.get("automatic_selection", {})
                for destination, value in ((decisions, automatic.get("decision", "not_observed_or_known_paths")),
                                           (reasons, automatic.get("reason", preparation.get("reason", "not_observed")))):
                    destination[value] = destination.get(value, 0) + 1
            output[kind][arm] = {
                "planned": len(planned), "attempted": len(selected), "unrun": len(planned) - len(selected),
                "valid_delivery": sum(good(row) for row in selected),
                "positive_complete": sum(good(row) and row.get("scope_grade", {}).get("declared_scope_complete") is True for row in selected),
                "control_expected_bypasses": sum(good(row) and row.get("scope_grade", {}).get("expected_bypass") is True for row in selected),
                "worker_errors": sum(row.get("worker_completed") is not True for row in selected),
                "fidelity_or_evaluator_errors": sum(row.get("worker_completed") is True and not good(row) for row in selected),
                "decisions": decisions, "reasons": reasons, "metrics": metrics,
            }
    return output


def xml_counts(path: Path) -> dict[str, Any]:
    root = ET.fromstring(regular(path))
    suites = [item for item in root.iter("testsuite") if not item.findall("testsuite")]
    counts = {key: sum(int(item.get(key, "0")) for item in suites) for key in ("tests", "failures", "errors", "skipped")}
    counts["passed"] = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    return counts


class Archive:
    def __init__(self, root: Path) -> None:
        if root.exists() or root.is_symlink() or root.resolve(strict=False) != root.absolute():
            raise ValueError("evidence output must be a new canonical directory")
        root.mkdir()
        self.root, self.files, self.missing = root, [], []

    def add(self, source: Path, target: str, *, expected: str | None = None, optional: bool = False) -> None:
        parts = PurePosixPath(target).parts
        if (not parts or target != PurePosixPath(target).as_posix() or PurePosixPath(target).is_absolute()
                or any(part in {"..", ".git", ".venv", "venv", "worktrees", "node_modules"} for part in parts)
                or target.endswith((".db", ".sqlite", ".sqlite3", ".whl", ".tar.gz", ".zip"))):
            raise ValueError(f"outside evidence allowlist: {target}")
        if not source.exists() and optional:
            self.missing.append({"source": str(source), "target": target})
            return
        data = regular(source)
        if expected is not None and digest(data) != expected:
            raise ValueError(f"frozen evidence hash differs: {source}")
        destination = self.root / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
        self.files.append({"path": target, "sha256": digest(data), "bytes": len(data),
                           "source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source)})

    def readme(self) -> None:
        text = """# Offline router-v3 evidence

The ledger hashes an explicit allowlist. Files are exact original evidence except
this generated guide. Logs and JSON retain original absolute paths. There are no
databases, worktrees, Git internals, environments, credentials or binary packages.
Historical evidence was not replaced. Model/coding outcomes are not measured.

Reproduction requires the application commit in freeze/policy-freeze.json and
`uv sync --frozen` in that checkout. Restore corpus/tasks.json to
benchmarks/tasks_automatic_v3.json, corpus/grading.json to
benchmarks/automatic-v3-grading.json, corpus/provenance.json to
benchmarks/automatic-v3-provenance.json and corpus/fixtures/ to
benchmarks/automatic-v3-fixtures/. Keep the archived originals unchanged.

Follow reproduction/benchmarks/automatic-v3-protocol.md, using new freeze, plan
and output directories. A new plan must reconstruct canonical Git roots and
fresh worktrees at current absolute paths; copying the old plan is insufficient.
Do not execute upstream repository source, hooks, builds, tests or packages.

Archived local helpers are evidence, not installed entry points. Restore the
collector to .local/router-v3/build_report.py in the checkout before invoking it.
Other audit/smoke helpers may also depend on their documented .local locations
or original absolute inputs. Adapt a new copy for reproduction and retain the
original bytes; do not expect helpers to work directly inside this archive.
Timestamps, absolute paths and timings are not expected to be byte-identical in
a new run. Compare verified source bytes and declared outcomes instead.

The post-study test-only corpus schema compatibility repair is archived as
reproduction/tests/test_benchmark_corpus_warm.py. It retains the freshness check
while accepting the declared list manifest. Use that validator for the final
mixed-schema full-suite verification; it is outside the unchanged frozen
production, runner and corpus seals. Original before-corpus/failed receipts are
preserved separately from the final complete-tree verification on both runtimes.

The collector only reads completed observations; it cannot start a model study.
Supply its independent formal-audit path and new evidence/report output paths.
The ledger deliberately excludes itself and the standalone assessment files to
avoid circular hashes. Post-hoc diagnostics, if present, remain separately
labeled and do not revise original outcomes or establish causal attribution.
"""
        data = text.encode()
        with (self.root / "README.md").open("xb") as stream:
            stream.write(data)
        self.files.append({"path": "README.md", "sha256": digest(data), "bytes": len(data),
                           "source": "generated archive guide; no observed measurement"})


def archive_inputs(args: argparse.Namespace, plan: dict[str, Any], report: dict[str, Any], audit: dict[str, Any]) -> Archive:
    archive = Archive(args.evidence)
    for source, target in ((args.report, "formal/report.json"), (args.plan, "plan/plan.json"),
                           (args.report.parent / "plan-input.json", "formal/plan-input.json"),
                           (args.controls, "controls/safety-controls.json"),
                           (args.formal_audit, "validation/independent-formal-audit.json"),
                           (args.policy_freeze, "freeze/policy-freeze.json"),
                           (Path(__file__).resolve(), "reproduction/build_report.py")):
        archive.add(source, target)
    if digest(regular(args.plan)) != report["plan_sha256"] or regular(args.plan) != regular(args.report.parent / "plan-input.json"):
        raise ValueError("formal report does not reference the exact retained input plan")
    for name in VALIDATION_FILES:
        archive.add(LOCAL / name, "validation/" + name,
                    optional=name not in {"full-python.xml", "full-python.log", "python311-full.xml",
                                          "python311-full.log", "final-cohort-verification.json"})
    for name in RESEARCH_FILES:
        archive.add(LOCAL / "research" / name, "research/" + name)
    for name in REPRODUCTION_FILES:
        archive.add(ROOT / name, "reproduction/" + name, optional=True)
    archive.add(LOCAL / "plan.json", "reproduction/implementation-plan.json", optional=True)
    for path, expected in plan["policy_freeze"]["seal"]["files"].items():
        if not (path.startswith("src/memglide/") and path.endswith(".py") or path in {
                "benchmarks/run_automatic_v3.py", "benchmarks/automatic-v3-protocol.md",
                "tests/test_benchmark_automatic_v3.py", "pyproject.toml", "uv.lock"}):
            raise ValueError("unexpected policy-seal path")
        archive.add(ROOT / path, "reproduction/" + path, expected=expected)
    for key, basename, expected in (("tasks", "tasks.json", plan["tasks_sha256"]),
                                     ("grading", "grading.json", plan["grading_sha256"]),
                                     ("provenance", "provenance.json", plan["provenance_sha256"])):
        archive.add(Path(plan["corpus_inputs"][key]), "corpus/" + basename, expected=expected)
    fixtures = Path(plan["corpus_inputs"]["fixtures"])
    for relative, expected in plan["fixture_hashes"].items():
        archive.add(fixtures / relative, "corpus/fixtures/" + relative, expected=expected)
    for assignment in plan["assignments"]:
        identifier = f"run-{assignment['ordinal']:04d}"
        for name in ("request.json", "result.json", "stdout.log", "stderr.log"):
            archive.add(args.report.parent / "runs" / identifier / name,
                        f"formal/runs/{identifier}/{name}",
                        expected=audit.get("raw_receipt_sha256", {}).get(f"runs/{identifier}/{name}"), optional=True)
    for name in ("acquisition.json", "corpus-authoring.json", "corpus-static-validation.json"):
        archive.add(ROOT / ".local/router-v3-upstream" / name, "upstream/" + name)
    for source in args.upstream_receipt:
        if (not source.is_relative_to(ROOT / ".local/router-v3-upstream") or source.suffix not in {".json", ".log", ".txt", ".py"}):
            raise ValueError("upstream receipts must be explicit public text under .local/router-v3-upstream")
        archive.add(source, "upstream/" + source.relative_to(ROOT / ".local/router-v3-upstream").as_posix())
    archive.readme()
    return archive


def fmt(value: Any, scale: float = 1) -> str:
    return f"{value * scale:.3f}" if number(value) else "—"


def cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def mean_median(metric: dict[str, Any], scale: float = 1) -> str:
    return fmt(metric["mean"], scale) + " / " + fmt(metric["median"], scale)


def markdown(assessment: dict[str, Any], plan: dict[str, Any]) -> str:
    report, groups = assessment["formal_report"], assessment["stratified"]
    integrity = assessment["comparison_integrity"]
    lines = ["# Runtime-aware source router v3: independent offline assessment", "",
             f"Frozen application commit: `{assessment['source_commit']}`. Comparison integrity: **{integrity}**.", "",
             "This study measures complete-source selection and local preparation, not completed coding tasks. "
             "No Codex/model was dispatched; model token usage, cache reads/writes, cost per coding success and actual billed charges are unavailable. "
             "It cannot establish a faster or cheaper coding agent or a best retrieval architecture.", "",
             "## Design and observed scope", "",
             f"The frozen plan contains {len(plan['tasks'])} tasks, four arms and two repeats: {len(plan['assignments'])} assignments. "
             f"{len(report['rows'])} original observations are retained; {report['summary']['unrun_assignments']} assignments are unrun. "
             "B is complete source from caller-known paths, V1/V2 are frozen compatibility selectors, and C is opt-in v3. "
             "Automatic arms receive no target paths or grading data. All use identical public task text, isolated ordinal worktrees, new processes/databases, "
             "12,000 context bytes and a 4,000 estimated-token cap where applicable. The latter is a planning proxy, not measured model usage.", "",
             "Positive targets and negative controls are reported separately. A complete declared target bundle is a scope proxy, not semantic dependency completeness, "
             "a repaired program, coding correctness or code quality. A safe positive bypass is a miss. Negative bypasses never offset positive misses. "
             "B is an oracle baseline: human path-discovery cost is unmeasured.", "",
             "## Positive inclusion and negative controls", "",
             "| Arm | Positive complete / planned | Negative bypass / planned | Valid delivery / planned | Worker / evaluator errors |",
             "| --- | ---: | ---: | ---: | ---: |"]
    negative = ["## Measured negative efficiency result", "",
                "The positive-task means below include every positive assignment, including safe selection misses. "
                "They measure local preparation, not full coding-task time. The v3-versus-v2 addition is more local work; a target-inclusion gain is not a latency win.", "",
                "| Positive-task metric | V2 mean ms | C mean ms | Relative mean change | Paired mean C−V2 95% interval ms |",
                "| --- | ---: | ---: | ---: | --- |"]
    for metric in ("preparation_wall_seconds", "setup_plus_preparation_wall_seconds"):
        before = groups["positive"]["V2"]["metrics"][metric]["mean"]
        after = groups["positive"]["C"]["metrics"][metric]["mean"]
        relative = f"{(after / before - 1) * 100:+.2f}%" if number(before) and before > 0 and number(after) else "—"
        paired = report["summary"]["paired_effects"]["C_minus_V2:positive:" + metric]
        interval = paired["mean_bootstrap95"]
        shown = "—" if interval is None else "[" + ", ".join(fmt(value, 1000) for value in interval) + "]"
        negative.append(f"| {metric} | {fmt(before, 1000)} | {fmt(after, 1000)} | {relative} | {shown} |")
    negative.extend(["", "These small unadjusted intervals are descriptive/exploratory, include zero where shown, and do not establish unchanged latency or a generalizable effect. "
                     "The known-path baseline and all repeated observations remain in the full tables below.", ""])
    insertion = lines.index("## Design and observed scope")
    lines[insertion:insertion] = negative
    for arm in ARMS:
        pos, control, all_rows = groups["positive"][arm], groups["abstention_control"][arm], groups["all"][arm]
        lines.append(f"| {arm} | {pos['positive_complete']}/{pos['planned']} | {control['control_expected_bypasses']}/{control['planned']} | "
                     f"{all_rows['valid_delivery']}/{all_rows['planned']} | {all_rows['worker_errors']} / {all_rows['fidelity_or_evaluator_errors']} |")
    consistency = report["summary"]["arms"]
    lines.extend(["", f"V3 completed declared positive scope consistently for **{consistency['C']['consistent_tasks_both_repeats']['positive']}/8 tasks**, "
                  f"versus V2 {consistency['V2']['consistent_tasks_both_repeats']['positive']}/8, V1 {consistency['V1']['consistent_tasks_both_repeats']['positive']}/8 "
                  f"and known-path B {consistency['B']['consistent_tasks_both_repeats']['positive']}/8. "
                  "Repeated runs are repeated measurements, not additional independent tasks. An extra complete task is a narrow observed inclusion improvement; "
                  "the remaining misses keep v3 experimental.", "", "### Observed selection and bypass categories", "",
                  "These are emitted receipt reasons, not an independently established causal diagnosis. An index/policy safety decline remains a positive miss. "
                  "A control bypass caused by an incomplete index does not prove that semantic task intent was recognized.", "",
                  "| Stratum | Arm | Reason | Original observations |", "| --- | --- | --- | ---: |"])
    for kind in ("positive", "abstention_control"):
        for arm in ARMS:
            for reason, count in sorted(groups[kind][arm]["reasons"].items()):
                lines.append(f"| {kind} | {arm} | {cell(reason)} | {count} |")
    lines.extend(["", "### Every positive task's declared scope", "",
                  "Hits count valid complete required-path inclusion across two original repeats. Modes/reasons summarize those repeats without replacing any individual record. "
                  "Repeated required bundles remain visible; the declared paths were kept private from automatic workers.", "",
                  "| Task / repository | Declared required paths | B | V1 | V2 | C |",
                  "| --- | --- | --- | --- | --- | --- |"])
    for task in plan["tasks"]:
        target = plan["grading"][task["id"]]
        if target["kind"] != "positive":
            continue
        outcomes = []
        for arm in ARMS:
            members = [row for row in report["rows"] if row["task_id"] == task["id"] and row["arm"] == arm]
            hits = sum(good(row) and row.get("scope_grade", {}).get("declared_scope_complete") is True for row in members)
            modes = sorted({((row.get("observation") or {}).get("preparation", {}).get("mode", "not_observed"),
                            (row.get("observation") or {}).get("preparation", {}).get("reason", "not_observed")) for row in members})
            outcomes.append(f"{hits}/2; " + "; ".join(mode + "/" + reason for mode, reason in modes))
        values = [task["id"] + " / " + task["repository"], ", ".join(target["required_paths"]), *outcomes]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.extend(["", "## Local timing, CPU, memory and source volume", "",
                  "Each value is **mean / median**. Wall and CPU values are milliseconds; peak RSS values are MiB. "
                  "Setup includes approval/index construction; preparation is the source API. Their sum excludes imports/startup, worktree creation, grading and report writing. "
                  "Worker lifetime includes startup, serialization and session cleanup, including observed failed attempts. API metrics exist only when observed; JSON records coverage for every field. "
                  "Parent and waited-child CPU are separate. SELF RSS is whole-worker high water, not incremental API memory; child RSS is a maximum, not a concurrent sum. Never add the two peaks.", ""])
    for kind in KINDS:
        lines.extend([f"### {kind}", "", "| Arm | Setup+prep wall | Prep wall | Parent setup CPU | Parent prep CPU | Child setup CPU | Child prep CPU | SELF RSS | Max child RSS | Worker lifetime | Added bytes |",
                      "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
        for arm in ARMS:
            values = groups[kind][arm]["metrics"]
            columns = [mean_median(values[name], scale) for name, scale in (
                ("setup_plus_preparation_wall_seconds", 1000), ("preparation_wall_seconds", 1000),
                ("setup_cpu_seconds", 1000), ("preparation_cpu_seconds", 1000),
                ("setup_waited_child_cpu_seconds", 1000), ("preparation_waited_child_cpu_seconds", 1000),
                ("self_peak_rss_bytes", 1 / 1_048_576), ("max_waited_child_rss_bytes", 1 / 1_048_576),
                ("process_wall_seconds", 1000), ("context_bytes", 1))]
            lines.append("| " + arm + " | " + " | ".join(columns) + " |")
        lines.append("")
    lines.extend(["## Preregistered paired effects", "",
                  "Differences are C minus the named baseline, copied from the frozen runner. Positive values mean more local work/bytes. "
                  "Intervals use 2,000 fixed-seed task-cluster bootstrap draws retaining both repeats; paired metrics require observed valid delivery for both arms and both repeats. "
                  "The intervals are unadjusted for multiple comparisons and interpreted as exploratory, not confirmatory. "
                  "The task cluster does not capture repository/file dependence: eight positives share seven distinct target bundles, and two repositories are from the same unjs ecosystem. "
                  "These are small authored, partly related observations, not independent production samples. OS caches and host load remain uncontrolled; balanced precedence does not equal identical cache state.", "",
                  "| Contrast / stratum / metric | Task clusters / pairs | Mean delta | Median delta | Mean 95% interval | Median 95% interval |",
                  "| --- | ---: | ---: | ---: | --- | --- |"])
    for key, values in report["summary"]["paired_effects"].items():
        scale = 1000 if key.endswith("seconds") else 1 / 1_048_576 if key.endswith("rss_bytes") else 1
        unit = " ms" if key.endswith("seconds") else " MiB" if key.endswith("rss_bytes") else " bytes"
        interval = lambda name: "—" if values[name] is None else "[" + ", ".join(fmt(value, scale) for value in values[name]) + "]" + unit
        lines.append(f"| {cell(key)} | {values['task_clusters']} / {values['pairs']} | {fmt(values['mean_delta'], scale)}{unit} | "
                     f"{fmt(values['median_delta'], scale)}{unit} | {interval('mean_bootstrap95')} | {interval('median_bootstrap95')} |")
    lines.extend(["", "## What improved, regressed or remains unproven", "",
                  "| Item | Observed result and limit |", "| --- | --- |"])
    c = groups["positive"]["C"]
    for baseline in ("B", "V1", "V2"):
        other = groups["positive"][baseline]
        delta = c["positive_complete"] - other["positive_complete"]
        label = "higher" if delta > 0 else "lower" if delta < 0 else "equal"
        lines.append(f"| C declared positive inclusion versus {baseline} | {label}: {c['positive_complete']}/{c['planned']} versus "
                     f"{other['positive_complete']}/{other['planned']}; descriptive scope counts, not coding success. |")
    lines.extend(["| Complete-source safety | Canonical Git bytes, hashes, whole-file ranges and exact task suffix are independently checked. Synthetic security controls and production tests are separate evidence. |",
                  "| Local efficiency | Mean/median paired effects and uncertainty above; selection misses, setup costs and failed attempts remain visible. No blanket latency win is inferred. |",
                  "| Model efficiency and actual billing | Unmeasured: no input/cached/uncached/output tokens, avoided reads, model cost per success or billed-charge comparison. |",
                  "| Product readiness | Local tests and installed transport smoke do not establish hosted multi-tenant operational readiness, semantic completeness or an optimal architecture. |",
                  "| Defaults and memory | Known-path source delivery is preserved; automatic v3 remains explicit/experimental, v1 is the compatibility default, and automatic warm-memory injection stays disabled. |", "",
                  "## Validation and preserved failures", "",
                  "The primary Python 3.12 complete suite is one run. The full Python 3.11 run is a separate runtime check, not additional distinct tests; "
                  "targeted compatibility and focused receipts overlap those full runs and are not added to a larger total. "
                  "Final full-runtime receipts cover the completed tree with the fresh corpus; the earlier Python 3.12 run preceded corpus creation. "
                  "The corpus-schema validator repair occurred after the frozen offline cohort and changed only test schema normalization, not its freshness assertions or frozen production/runner/corpus. "
                  "Frontend, browser and installed-smoke counts are separate surfaces, not a pooled success claim.", "",
                  "| Receipt | Passed | Failed / errors / skipped |", "| --- | ---: | ---: |"])
    for name, counts in assessment["validation"]["xml"].items():
        lines.append(f"| {cell(name)} | {counts['passed']} | {counts['failures']} / {counts['errors']} / {counts['skipped']} |")
    surfaces = assessment["validation"]["surfaces"]
    safety = assessment["synthetic_controls"]
    safety_rows = safety.get("rows", [])
    lines.extend(["", f"Frontend unit: **{surfaces['frontend_unit_passed']} passed**, {surfaces['frontend_unit_failed']} failed; "
                  f"production browser: **{surfaces['browser_passed']} passed**, {surfaces['browser_unexpected']} unexpected, {surfaces['browser_flaky']} flaky; "
                  f"final installed-wheel/API/SPA/default-and-agent MCP/CLI smoke: **{surfaces['installed_checks_passed']}/{surfaces['installed_checks_total']} checks passed**, as retained receipts describe. "
                  "The complete Python 3.11 runtime and its overlapping targeted compatibility runs are recorded separately. Lint, typing, wheel reconstruction, frozen dependency install and checksum-verified actionlint are in build-static.json. "
                  "Remote GitHub CI execution is not established by the local workflow check.", ""])
    lines.extend([f"Separate synthetic source safety controls: **{sum(row.get('passed') is True for row in safety_rows)}/{len(safety_rows)} passed**; "
                  f"aggregate receipt passed = **{safety.get('passed')}**. These controls are not added to scope-success or timing denominators.", ""])
    lines.extend("- " + note for note in FAILURE_NOTES)
    lines.extend(["", "Research refreshed official source/docs, not all complete papers. The archive retains exact snapshots, fetch hashes and one failed 404 followed by the discovered successful JSONL source. "
                  "Mutable upstream URLs are identified by inspected hashes; competitor results are not Memglide measurements. "
                  "See [research](router-v3-research.md) for the reading scope and remaining syntactic/semantic limits.", "",
                  "## Every original assignment", "",
                  "No retries or replacements are pooled. Unrun assignments are displayed explicitly; JSON and raw request/result/stdout/stderr preserve detailed receipts and errors.", "",
                  "| # | Task | Arm | Kind | Outcome | Decision | Prep ms | Worker ms | Added bytes | Selected paths |",
                  "| ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |"])
    by_ordinal = {row["ordinal"]: row for row in report["rows"]}
    for item in plan["assignments"]:
        row = by_ordinal.get(item["ordinal"])
        kind = plan["grading"][item["task_id"]]["kind"]
        preparation = ((row or {}).get("observation") or {}).get("preparation", {})
        automatic = preparation.get("automatic_selection", {})
        outcome = "unrun" if row is None else "worker error" if not row.get("worker_completed") else "integrity/evaluator error" if not good(row) else (
            "complete scope" if row.get("scope_grade", {}).get("declared_scope_complete") is True else "expected bypass" if row.get("scope_grade", {}).get("expected_bypass") is True else "positive miss" if kind == "positive" else "unexpected preload")
        metrics = (row or {}).get("metrics", {})
        paths = ", ".join((row or {}).get("fidelity", {}).get("selected_paths", [])) or "—"
        values = [item["ordinal"], item["task_id"], item["arm"], kind, outcome,
                  automatic.get("decision", preparation.get("mode", "—")), fmt(metrics.get("preparation_wall_seconds"), 1000),
                  fmt((row or {}).get("process_wall_seconds"), 1000), fmt(metrics.get("context_bytes")), paths]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.extend(["", "## Evidence, reproduction and next experiments", "",
                  f"The [JSON assessment](router-v3-assessment.json) retains the original full report, all individual rows, derived strata, missing values and audit receipts. "
                  f"The [evidence ledger](evidence/router-v3/ledger.json) hashes an explicit allowlist of {assessment['archive_file_count']} files; "
                  "the ledger excludes itself and these standalone assessment files to avoid circular hashes. Databases, worktrees, Git internals, environments, authentication and wheel/archive binaries are excluded. "
                  "Historical reports and raw studies remain untouched.", "",
                  "Post-hoc index/candidate diagnostics, if archived, are kept separate from the frozen cohort; emitted bypass reasons alone are not causal proof. "
                  "The independent formal audit also retains repository-cluster sensitivity; four repository clusters give limited uncertainty information and do not repair correlated target bundles.", "",
                  "To reproduce: check out the recorded application commit; install the frozen lock with `uv sync --frozen`; "
                  "use the archived retained corpus, task/private-grade/provenance files and generic runner. Preserve the original policy freeze and plan; "
                  "create a **new** policy freeze and **new** plan/output directories for a reproduction, because commits and absolute canonical paths differ. "
                  "Follow `benchmarks/automatic-v3-protocol.md`: freeze, plan, controls, then run. Never execute downloaded upstream code. "
                  "Use this collector with a new evidence directory/output prefix and an independent formal-audit path; it does not dispatch agents or rerun tasks.", "",
                  "Next, diagnose these preserved misses without treating this exposed cohort as a fresh tuning holdout. Add development regressions from the failure mechanism, "
                  "then freeze the revised policy before authoring a new independent cohort with more unrelated repositories and target bundles. "
                  "If offline inclusion and overhead justify it, preregister a separate matched bare-Codex/known-path/automatic model study with independent coding graders, "
                  "actual available usage accounting, complete failed-attempt spend, equivalent-cache controls, an estimated maximum budget and a frozen plan. "
                  "Only that study can test cost per successfully completed coding task. Keep v3 opt-in until such evidence supports promotion.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / ".local/router-v3-offline/report.json")
    parser.add_argument("--plan", type=Path, default=ROOT / ".local/router-v3-plan/plan.json")
    parser.add_argument("--controls", type=Path, default=ROOT / ".local/router-v3-controls/safety-controls.json")
    parser.add_argument("--policy-freeze", type=Path, default=ROOT / ".local/router-v3-policy-freeze/policy-freeze.json")
    parser.add_argument("--formal-audit", type=Path, required=True)
    parser.add_argument("--upstream-receipt", type=Path, action="append", default=[])
    parser.add_argument("--evidence", type=Path, default=ROOT / "benchmarks/evidence/router-v3")
    parser.add_argument("--output-prefix", type=Path, default=ROOT / "benchmarks/router-v3-assessment")
    args = parser.parse_args()
    for name in ("report", "plan", "controls", "policy_freeze", "formal_audit", "evidence", "output_prefix"):
        setattr(args, name, getattr(args, name).absolute())
    args.upstream_receipt = [path.absolute() for path in args.upstream_receipt]
    if any(args.output_prefix.with_suffix(suffix).exists() for suffix in (".md", ".json")):
        raise ValueError("refusing to overwrite existing assessments")
    report, plan, controls, audit = load(args.report), load(args.plan), load(args.controls), load(args.formal_audit)
    if load(args.policy_freeze) != plan["policy_freeze"]:
        raise ValueError("standalone policy freeze differs from exact formal input")
    if len(plan["assignments"]) != 96 or len(plan["tasks"]) != 12 or plan["repeats"] != 2:
        raise ValueError("collector expects the frozen 96-assignment formal study")
    archive = archive_inputs(args, plan, report, audit)
    unit, browser, installed = (load(LOCAL / name) for name in ("frontend-unit.json", "frontend-browser.json", "installed-smoke.json"))
    validation = {"xml": {name: xml_counts(LOCAL / name) for name in VALIDATION_FILES if name.endswith(".xml") and (LOCAL / name).is_file()},
                  "surfaces": {"frontend_unit_passed": unit["numPassedTests"], "frontend_unit_failed": unit["numFailedTests"],
                               "browser_passed": browser["stats"]["expected"], "browser_unexpected": browser["stats"]["unexpected"],
                               "browser_flaky": browser["stats"]["flaky"], "installed_checks_total": len(installed["checks"]),
                               "installed_checks_passed": sum(value is True for value in installed["checks"].values()),
                               "installed_all_passed": installed["all_passed"]},
                  "counting": "The Python 3.12 full count is primary. The Python 3.11 full run is a separate runtime check; targeted/focused receipts overlap. No counts are pooled.",
                  "development_failure_notes": FAILURE_NOTES, "owner_development": load(LOCAL / "dev-attempts.json"),
                  "build_static": load(LOCAL / "build-static.json"), "environment": load(LOCAL / "environment.json")}
    audit_clear = any(audit.get(key) is True for key in ("passed", "all_checks_passed", "review_clearance", "audit_passed")) and not audit.get("blocking_findings") and not audit.get("errors")
    audit_binding = {"cohort_report_matches": audit.get("cohort_report_sha256") == digest(regular(args.report)),
                     "plan_matches": audit.get("plan_sha256") == digest(regular(args.plan)),
                     "policy_freeze_matches": audit.get("policy_freeze_sha256") == digest(regular(args.policy_freeze))}
    assessment = {
        "version": "router-v3-assessment-1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": plan["policy_freeze"]["seal"]["head"], "formal_report": report,
        "assignments": plan["assignments"], "stratified": summaries(report["rows"], plan),
        "validation": validation, "synthetic_controls": controls, "independent_formal_audit": audit,
        "audit_binding": audit_binding,
        "comparison_integrity": report["summary"]["integrity_complete"] is True and report["seal_unchanged"] is True and audit_clear and all(audit_binding.values()),
        "control_failures_not_removed": True, "default_promotion": False,
        "model_metrics": {name: None for name in ("input_tokens", "cached_input_tokens", "cache_write_tokens", "uncached_input_tokens", "output_tokens", "coding_task_success", "cost_per_success", "estimated_api_equivalent_cost", "actual_billed_charges", "avoided_file_reads", "native_task_latency")},
        "dispatched_model_requests": report["dispatched_model_requests"],
        "limits": ["Author-declared source scope is not coding correctness or semantic dependency completeness.",
                   "Eight positive tasks share seven target bundles; four repositories include two related unjs projects. Task bootstrap does not capture that dependence.",
                   "Four subjective abstention controls do not represent production task prevalence.",
                   "Observed local preparation/resources do not measure Codex token use, cost, avoided investigation or whole coding latency.",
                   "Known-path baseline human discovery cost is unmeasured. OS cache and host load are not equivalent-cache proof.",
                   "Runtime/declaration classification and intent are syntactic heuristics; no globally optimal architecture claim."],
        "archive_file_count": len(archive.files), "optional_missing_receipts": archive.missing,
    }
    ledger = {"version": 1, "files": archive.files, "optional_missing": archive.missing,
              "excluded": ["databases", "worktrees", ".git", "venvs", "authentication", "wheel/archive binaries"],
              "self_and_standalone_assessment_hashes_excluded": True}
    write_json(args.evidence / "ledger.json", ledger)
    assessment["ledger_sha256"] = digest(regular(args.evidence / "ledger.json"))
    write_json(args.output_prefix.with_suffix(".json"), assessment)
    args.output_prefix.with_suffix(".md").write_text(markdown(assessment, plan), encoding="utf-8")
    print(json.dumps({"assessment": str(args.output_prefix), "files": len(archive.files), "comparison_integrity": assessment["comparison_integrity"]}))


if __name__ == "__main__":
    main()
