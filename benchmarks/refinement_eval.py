"""Evaluate the prelocked Meridian corpus only after a caller-supplied source freeze.

No model is called and indexed source is never executed. Both rankers share the
same current index and context packer; this is not a complete V1/V2 comparison.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import statistics
import subprocess
import time
import types
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from benchmarks.compare_components import capture_provenance
from benchmarks.refinement_corpus import MANIFEST_SHA256, ROOT, load_manifest, write_repository
from benchmarks.retrieval_experiment import init_git, write_json
from memglide.service import Service

STRATEGIES = ("refined", "previous", "legacy")
FROZEN_REVISIONS = {
    "previous": "b51a26234656c647f12da3ad63d8bc1fe9380c58",
    "legacy": "39e8df30565783a686270f8a6f422e56e41e3776",
}
PROTOCOL_PATH = ROOT / "benchmarks/refinement_protocol.json"
PROTOCOL_SHA256 = "070daffd810a4bba7016e68a248932b8033ed6e4915325b67f0641df2b5228b2"
METRICS = (
    "primary_file_hit_at_1",
    "primary_file_reciprocal_rank",
    "required_file_recall",
    "primary_complete_body_coverage",
    "required_dependency_complete_body_recall",
    "all_required_bodies_present",
    "context_declared_file_precision",
    "context_returned_file_count",
    "context_returned_item_count",
    "context_output_json_bytes",
    "context_estimated_planning_tokens",
    "search_wall_seconds",
    "search_process_cpu_seconds",
    "context_wall_seconds",
    "context_process_cpu_seconds",
    "search_plus_context_wall_seconds",
)


def load_protocol() -> dict[str, Any]:
    if hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest() != PROTOCOL_SHA256:
        raise ValueError("Evaluation protocol changed after its pre-measurement lock")
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def measurement_provenance() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (
            ROOT / "benchmarks/refinement_corpus.py",
            ROOT / "benchmarks/refinement_holdout.json",
            ROOT / "benchmarks/refinement_protocol.json",
            Path(__file__).resolve(),
        )
    }


def evaluation_label(reuse_reason: str | None, requested: str | None = None) -> str:
    """Keep replay evidence from being described as a first fresh evaluation."""
    reused = bool(reuse_reason and reuse_reason.strip())
    if reuse_reason is not None and not reused:
        raise ValueError("A validation reuse reason must not be empty")
    if requested not in {None, "first_fresh_evaluation", "reused_validation"}:
        raise ValueError("Unknown evaluation label")
    if requested == "first_fresh_evaluation" and reused:
        raise ValueError("Previously evaluated validation cannot be labeled fresh")
    if requested == "reused_validation" and not reused:
        raise ValueError("Reused validation requires a disclosure reason")
    return requested or ("reused_validation" if reused else "first_fresh_evaluation")


def frozen_indexer(db: Any, strategy: str) -> tuple[Any, dict[str, Any]]:
    """Load trusted committed indexer/query code, never fixture repository code."""
    if strategy not in FROZEN_REVISIONS:
        raise ValueError("Only explicitly frozen trusted revisions may be loaded")
    revision = FROZEN_REVISIONS[strategy]
    source = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", revision + ":src/memglide/core/indexer.py"]
    )
    module = types.ModuleType("memglide_refinement_frozen_" + strategy)
    exec(compile(source, "<trusted committed indexer>", "exec"), module.__dict__)
    provenance: dict[str, Any] = {
        "revision": revision,
        "indexer_sha256": hashlib.sha256(source).hexdigest(),
        "query_sha256": None,
    }
    query_imports = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module == "memglide.core.query"
    ]
    if query_imports:
        query_source = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", revision + ":src/memglide/core/query.py"]
        )
        query_module = types.ModuleType("memglide_refinement_frozen_query_" + strategy)
        exec(
            compile(query_source, "<trusted committed query helpers>", "exec"),
            query_module.__dict__,
        )
        for statement in query_imports:
            for imported in statement.names:
                module.__dict__[imported.asname or imported.name] = getattr(
                    query_module, imported.name
                )
        provenance["query_sha256"] = hashlib.sha256(query_source).hexdigest()
    return module.Indexer(db), provenance


def body_evidence(label: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    """Require continuous expected body coverage with exact immutable source lines.

    Several matching snippets may jointly cover a body, but an uncovered line,
    altered source, an empty structural reference or graph edge never suffices.
    """
    expected = label["text"].splitlines()
    first, last = label["start_line"], label["end_line"]
    matching: set[int] = set()
    intervals = []
    for item in items:
        if item.get("path") != label["path"] or not item.get("snippet"):
            continue
        start = item.get("start_line")
        end = item.get("end_line")
        if type(start) is not int or type(end) is not int:
            continue
        lines = item["snippet"].splitlines()
        # A declared range cannot bless a snippet that silently omits lines.
        if end < start or len(lines) != end - start + 1:
            continue
        covered = []
        for number in range(max(first, start), min(last, end) + 1):
            if lines[number - start] == expected[number - first]:
                matching.add(number)
                covered.append(number)
        if covered:
            intervals.append({"start_line": start, "end_line": end, "matching_body_lines": covered})
    required = set(range(first, last + 1))
    return {
        "path": label["path"],
        "symbol": label["symbol"],
        "start_line": first,
        "end_line": last,
        "complete": matching == required,
        "missing_lines": sorted(required - matching),
        "interval_evidence": intervals,
    }


def context_metrics(context: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
    items = context.get("items", [])
    returned = {item["path"] for item in items}
    required = set(query["required_files"])
    positives = required | set(query["optional_relevant_files"])
    primary = body_evidence(query["primary_body"], items)
    dependencies = [body_evidence(label, items) for label in query["required_dependency_bodies"]]
    complete_dependencies = sum(item["complete"] for item in dependencies)
    return {
        "required_file_recall": len(returned & required) / len(required),
        "primary_complete_body_coverage": int(primary["complete"]),
        "required_dependency_complete_body_recall": complete_dependencies / len(dependencies),
        "all_required_bodies_present": int(
            primary["complete"] and complete_dependencies == len(dependencies)
        ),
        "context_declared_file_precision": (
            len(returned & positives) / len(returned) if returned else None
        ),
        "context_returned_file_count": len(returned),
        "context_returned_item_count": len(items),
        "context_output_json_bytes": len(
            json.dumps(context, ensure_ascii=False, separators=(",", ":")).encode()
        ),
        "context_estimated_planning_tokens": context.get("estimated_tokens"),
        "context_returned_files": sorted(returned),
        "context_declared_unrelated_files": sorted(returned - positives),
        "context_truncated": context.get("truncated"),
        "context_warnings": context.get("warnings", []),
        "primary_body_evidence": primary,
        "dependency_body_evidence": dependencies,
    }


def evaluate_query(
    service: Service,
    project_id: str,
    query: dict[str, Any],
    strategy: str,
    legacy_search: Callable[..., list[dict[str, Any]]],
    previous_search: Callable[..., list[dict[str, Any]]],
    repeat: int,
    artifacts: Path,
) -> dict[str, Any]:
    if strategy not in STRATEGIES:
        raise ValueError("Unknown candidate policy")
    row: dict[str, Any] = {
        "query_id": query["id"],
        "repository": query["repository"],
        "language": query["language"],
        "domain": query["domain"],
        "strategy": strategy,
        "repeat": repeat,
        "prompt": query["prompt"],
        "status": "error",
        "errors": [],
        "artifacts": str(artifacts),
    }
    original_search = service.indexer.search
    session = None
    try:
        search = {"refined": original_search, "legacy": legacy_search, "previous": previous_search}[
            strategy
        ]
        started, cpu_started = time.perf_counter(), time.process_time()
        candidates = search(project_id, query["prompt"], limit=100, refresh=False)
        row["search_wall_seconds"] = time.perf_counter() - started
        row["search_process_cpu_seconds"] = time.process_time() - cpu_started
        paths = list(dict.fromkeys(item["path"] for item in candidates))
        rank = (
            paths.index(query["primary_target"]) + 1 if query["primary_target"] in paths else None
        )
        row.update(
            {
                "primary_file_rank": rank,
                "primary_file_hit_at_1": int(rank == 1),
                "primary_file_reciprocal_rank": 1 / rank if rank else 0.0,
                "ranked_unique_files": paths,
                "ranked_candidates": [
                    {
                        key: item.get(key)
                        for key in ("path", "symbol", "score", "reason", "start_line", "end_line")
                    }
                    for item in candidates
                ],
            }
        )
        session = service.memory.start_session(project_id, query["prompt"])

        def fixed_search(
            _project_id: str, _query: str, limit: int = 20, **_kwargs: Any
        ) -> list[dict[str, Any]]:
            return copy.deepcopy(candidates[:limit])

        service.indexer.search = fixed_search
        started, cpu_started = time.perf_counter(), time.process_time()
        context = service.context.get_context(session["id"], query["prompt"], level=2, budget=8000)
        row["context_wall_seconds"] = time.perf_counter() - started
        row["context_process_cpu_seconds"] = time.process_time() - cpu_started
        row["search_plus_context_wall_seconds"] = (
            row["search_wall_seconds"] + row["context_wall_seconds"]
        )
        row.update(context_metrics(context, query))
        write_json(artifacts / "context.json", context)
        row["status"] = "ok"
    except Exception as exc:
        row["errors"].append(type(exc).__name__ + ": " + str(exc))
    finally:
        service.indexer.search = original_search
        if session:
            try:
                service.memory.end_session(session["id"])
            except Exception as exc:
                row["status"] = "error"
                row["errors"].append("Session cleanup: " + type(exc).__name__ + ": " + str(exc))
    write_json(artifacts / "result.json", row)
    return row


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if row["status"] == "ok"]
    result: dict[str, Any] = {
        "planned_observations": len(rows),
        "valid_observations": len(valid),
        "error_observations": [
            {key: row[key] for key in ("query_id", "repeat", "errors")}
            for row in rows
            if row["status"] != "ok"
        ],
        "incomplete_body_observations": [
            {
                key: row[key]
                for key in (
                    "query_id",
                    "repeat",
                    "primary_body_evidence",
                    "dependency_body_evidence",
                )
            }
            for row in valid
            if not row["all_required_bodies_present"]
        ],
    }
    for metric in METRICS:
        values = sorted(float(row[metric]) for row in valid if row.get(metric) is not None)
        result[metric] = {
            "n": len(values),
            "missing": len(rows) - len(values),
            "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "p50": statistics.median(values) if values else None,
            "p95": values[math.ceil(0.95 * len(values)) - 1] if values else None,
        }
    return result


def markdown_report(report: dict[str, Any]) -> str:
    reused = report.get("evaluation_label") == "reused_validation"
    lines = [
        "# Reused retrieval validation" if reused else "# Fresh procedural retrieval validation",
        "",
        report["scope"],
        "",
        "No model calls, coding-task outcomes, billed tokens or costs are measured here. Context bytes are measured; planning tokens remain an engine estimate.",
        "",
        "All candidates share the current context packer. Previous means frozen shipped b51a262 ranking and legacy means frozen 39e8df3 ranking, not either complete former service. The holdout validates a previously frozen choice; it does not select or tune the default.",
        "",
        "Report status: " + report["status"],
        "",
        "| Policy | Valid/planned | File hit@1 | Complete primary body | Declared dependency body recall | All required bodies | Declared file precision | Mean files | Mean JSON bytes | Packing p50/p95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if reused:
        lines[2:2] = [
            "**REUSED VALIDATION:** " + report["validation_reuse_reason"],
            "",
            "The first fresh results remain preserved separately. This replay follows a failure-triggered fix and is not a new independent holdout.",
            "",
        ]
    for strategy, summary in report["summary"].items():

        def mean(key: str, percent: bool = False) -> str:
            value = summary[key]["mean"]
            return (
                "unavailable" if value is None else (f"{value:.1%}" if percent else f"{value:.2f}")
            )

        timing = summary["context_wall_seconds"]
        timing_text = (
            "unavailable"
            if timing["n"] == 0
            else f"{timing['p50'] * 1000:.2f}/{timing['p95'] * 1000:.2f}"
        )
        lines.append(
            f"| {strategy} | {summary['valid_observations']}/{summary['planned_observations']} | "
            + " | ".join(
                mean(key, True)
                for key in (
                    "primary_file_hit_at_1",
                    "primary_complete_body_coverage",
                    "required_dependency_complete_body_recall",
                    "all_required_bodies_present",
                    "context_declared_file_precision",
                )
            )
            + f" | {mean('context_returned_file_count')} | {mean('context_output_json_bytes')} | {timing_text} |"
        )
    lines += [
        "",
        "## Every individual observation",
        "",
        "| Query | Repeat | Policy | Status | Complete primary | Dependency recall | Declared precision | Files | Bytes |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["observations"]:
        values = [
            row.get(key)
            for key in (
                "primary_complete_body_coverage",
                "required_dependency_complete_body_recall",
                "context_declared_file_precision",
                "context_returned_file_count",
                "context_output_json_bytes",
            )
        ]
        lines.append(
            f"| {row['query_id']} | {row['repeat']} | {row['strategy']} | {row['status']} | "
            + " | ".join("unavailable" if value is None else str(value) for value in values)
            + " |"
        )
    lines += ["", "## Failures", ""]
    failures = [row for row in report["observations"] if row["status"] != "ok"]
    if failures:
        for row in failures:
            lines.append(
                f"- {row['query_id']} / repeat {row['repeat']} / {row['strategy']}: "
                + "; ".join(row["errors"])
            )
    else:
        lines.append(
            "No runner errors. Complete-body misses remain visible in every observation and the JSON evidence; an error-free run does not imply sufficient context."
        )
    lines += ["", "## Limitations", ""]
    lines.extend("- " + limitation for limitation in report["limitations"])
    lines += [
        "",
        "## Freeze and provenance",
        "",
        "```json",
        json.dumps(report["provenance"], indent=2),
        "```",
        "",
    ]
    return "\n".join(lines)


def run_evaluation(
    output: Path,
    report_prefix: Path,
    frozen_source_sha256: str,
    freeze_note: str,
    repeats: int = 2,
    validation_reuse_reason: str | None = None,
    requested_evaluation_label: str | None = None,
) -> dict[str, Any]:
    label = evaluation_label(validation_reuse_reason, requested_evaluation_label)
    if repeats < 1:
        raise ValueError("At least one repeat is required")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Use an empty output directory; prior observations must be preserved")
    if report_prefix.with_suffix(".json").exists() or report_prefix.with_suffix(".md").exists():
        raise ValueError("Use a new report prefix; prior reports must be preserved")
    manifest = load_manifest()
    protocol = load_protocol()
    before = capture_provenance()
    measurement_before = measurement_provenance()
    if before["source_tree_sha256"] != frozen_source_sha256:
        raise ValueError("Source differs from caller's pre-evaluation ranking/context freeze")
    if not freeze_note.strip():
        raise ValueError("A source-freeze note is required")
    output.mkdir(parents=True, exist_ok=True)
    lock = {
        "locked_at_utc": datetime.now(UTC).isoformat(),
        "manifest_sha256": MANIFEST_SHA256,
        "original_protocol_sha256": manifest["protocol_sha256"],
        "protocol_sha256": PROTOCOL_SHA256,
        "source_tree_sha256": frozen_source_sha256,
        "freeze_note": freeze_note,
        "validation_reuse_reason": validation_reuse_reason,
        "evaluation_label": label,
        "measurement_files_sha256": measurement_before,
    }
    write_json(output / "pre-evaluation-lock.json", lock)
    rows, fixtures = [], {}
    frozen_sources = {}
    for name, repository in manifest["repositories"].items():
        fixture = output / "fixtures" / name
        queries = [query for query in manifest["queries"] if query["repository"] == name]
        service = None
        try:
            write_repository(manifest, name, fixture)
            commit = init_git(fixture)
            service = Service(output / "states" / name / "memglide.db", watch=False)
            project = service.indexer.add_project(str(fixture))
            legacy, frozen_sources["legacy"] = frozen_indexer(service.db, "legacy")
            previous, frozen_sources["previous"] = frozen_indexer(service.db, "previous")
            fixtures[name] = {
                "commit": commit,
                "file_count": repository["file_count"],
                "source_utf8_bytes": repository["source_utf8_bytes"],
                "index_stats": project.get("index_stats"),
            }
            for repeat in range(1, repeats + 1):
                for index, query in enumerate(queries):
                    offset = index % len(STRATEGIES)
                    order = list(STRATEGIES[offset:] + STRATEGIES[:offset])
                    if repeat % 2 == 0:
                        order.reverse()
                    for position, strategy in enumerate(order):
                        row = evaluate_query(
                            service,
                            project["id"],
                            query,
                            strategy,
                            legacy.search,
                            previous.search,
                            repeat,
                            output / "queries" / query["id"] / f"repeat-{repeat}" / strategy,
                        )
                        row["execution_order_within_query"] = position
                        rows.append(row)
                        write_json(output / "observations-so-far.json", rows)
        except Exception as exc:
            error = "Fixture/setup failure: " + type(exc).__name__ + ": " + str(exc)
            fixtures.setdefault(name, {})["setup_error"] = error
            completed = {(row["query_id"], row["strategy"], row["repeat"]) for row in rows}
            for repeat in range(1, repeats + 1):
                for query in queries:
                    for strategy in STRATEGIES:
                        if (query["id"], strategy, repeat) not in completed:
                            rows.append(
                                {
                                    **{
                                        key: query[key]
                                        for key in ("repository", "language", "domain", "prompt")
                                    },
                                    "query_id": query["id"],
                                    "strategy": strategy,
                                    "repeat": repeat,
                                    "status": "not_run",
                                    "errors": [error],
                                    "artifacts": None,
                                }
                            )
            write_json(output / "observations-so-far.json", rows)
        finally:
            if service is not None:
                service.close()
    after = capture_provenance()
    measurement_after = measurement_provenance()
    unchanged = before["source_tree_sha256"] == after["source_tree_sha256"]
    measurement_unchanged = measurement_before == measurement_after
    report = {
        "schema_version": 1,
        "evaluation_label": label,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "scope": "24 locked retrieval tasks across Python/TypeScript, four domains and two 85+ file synthetic repositories, with ambiguous identifiers and docs/tests/read-model overlap. Exact source bodies and two declared direct dependency implementations are judged independently of declaration visibility.",
        "status": (
            "invalid_source_changed"
            if not unchanged or not measurement_unchanged
            else "completed_with_errors"
            if any(row["status"] != "ok" for row in rows)
            else "valid"
        ),
        "holdout_previously_evaluated": bool(validation_reuse_reason),
        "validation_reuse_reason": validation_reuse_reason,
        "protocol": protocol,
        "summary": {
            strategy: aggregate([row for row in rows if row["strategy"] == strategy])
            for strategy in STRATEGIES
        },
        "observations": rows,
        "limitations": [
            manifest["creation_policy"],
            "Two language fixtures mirror the same twelve intents, so observations are correlated. Repeats measure variability, not extra independent tasks.",
            "Complete body means exact fixture lines; declared dependency coverage excludes transitive and language/runtime dependencies and does not prove semantic task sufficiency.",
            "Declared precision uses explicit fixture-scope positives; documentation or tests can be useful to a real coding task despite falling outside this task's source-implementation judgment.",
            "Search uses an already indexed immutable fixture with refresh=False. Packing excludes initial ranking and session creation/cleanup. Shared local caches are not flushed; cold startup is not measured.",
            "Current-process CPU excludes parser workers. No exact physical file-read count, sampled memory overhead, model usage or billed cost is available from this local runner.",
            "After first evaluation this corpus becomes seen validation. Any subsequent evaluation must disclose reuse, and tuning requires a separately authored fresh holdout.",
        ],
        "provenance": {
            "manifest_sha256": MANIFEST_SHA256,
            "original_protocol_sha256": manifest["protocol_sha256"],
            "protocol_sha256": PROTOCOL_SHA256,
            "source_before": before,
            "source_after": after,
            "source_unchanged_during_evaluation": unchanged,
            "measurement_files_before": measurement_before,
            "measurement_files_after": measurement_after,
            "measurement_unchanged_during_evaluation": measurement_unchanged,
            "frozen_ranker_sources": frozen_sources,
            "fixtures": fixtures,
            "pre_evaluation_lock": lock,
            "raw_artifacts": str(output),
        },
    }
    report_prefix.parent.mkdir(parents=True, exist_ok=True)
    write_json(report_prefix.with_suffix(".json"), report)
    report_prefix.with_suffix(".md").write_text(markdown_report(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report-prefix", type=Path, required=True)
    parser.add_argument("--frozen-source-sha256", required=True)
    parser.add_argument("--freeze-note", required=True)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--validation-reuse-reason")
    parser.add_argument(
        "--evaluation-label", choices=("first_fresh_evaluation", "reused_validation")
    )
    args = parser.parse_args()
    report = run_evaluation(
        args.output.resolve(),
        args.report_prefix.resolve(),
        args.frozen_source_sha256,
        args.freeze_note,
        args.repeats,
        args.validation_reuse_reason,
        args.evaluation_label,
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "observations": len(report["observations"]),
                "summary": {
                    strategy: {
                        "valid": summary["valid_observations"],
                        "planned": summary["planned_observations"],
                        "all_required_bodies_present_mean": summary["all_required_bodies_present"][
                            "mean"
                        ],
                        "declared_file_precision_mean": summary["context_declared_file_precision"][
                            "mean"
                        ],
                        "context_wall_seconds_p50": summary["context_wall_seconds"]["p50"],
                        "context_wall_seconds_p95": summary["context_wall_seconds"]["p95"],
                    }
                    for strategy, summary in report["summary"].items()
                },
            }
        )
    )


if __name__ == "__main__":
    main()
