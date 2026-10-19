"""Development-only compact-context budgets against exact Atlas source bodies.

This deliberately reuses the OLD 24 Atlas tasks. It never opens corpus_v2 or
calls a coding model. Source text is parsed as data, never imported or executed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from benchmarks.corpus import PYTHON_SOURCES, TYPESCRIPT_SOURCES, build_repository, task_definitions
from benchmarks.refinement_eval import body_evidence
from memglide.core.agent_context import AgentContext
from memglide.core.context import estimate_tokens
from memglide.service import Service

ROOT = Path(__file__).resolve().parents[1]
PROFILES = (
    ("full_4000", 4000),
    ("compact_1200", 1200),
    ("compact_2000", 2000),
    ("compact_4000", 4000),
)
INTEGRATION_CALLERS = {
    "ttl-boundary": ("cached_document", "cachedDocument"),
    "cursor-pagination": ("list_documents", "listDocuments"),
    "scope-authorization": ("authorized", "authorized"),
    "storage-containment": ("storage_key", "storageKey"),
    "transitive-dependencies": ("dependencies_for", "dependenciesFor"),
    "boolean-config": ("feature_enabled", "featureEnabled"),
    "and-search": ("search_documents", "searchDocuments"),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_state() -> dict[str, Any]:
    files = {
        str(p.relative_to(ROOT)): sha256(p) for p in sorted((ROOT / "src/memglide").rglob("*.py"))
    }
    return {
        "files": files,
        "tree_sha256": hashlib.sha256(canonical_bytes(files)).hexdigest(),
        "tree_hash_method": "sha256(sorted compact UTF-8 JSON of relative Python source paths and hashes)",
    }


def source_label(path: str, source: str, symbol: str, language: str) -> dict[str, Any]:
    """Independent fixture oracle; does not reuse Memglide's structural parser.

    Python uses the standard AST. The immutable Atlas TS fixtures have top-level
    functions and two-space-indented methods with matching brace lines, including
    one-line methods. This narrow fixture grammar is not a general TS parser.
    """
    lines = source.splitlines()
    if language == "python":
        node: Any = ast.parse(source)
        for part in symbol.split("."):
            node = next(
                child
                for child in node.body
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                and child.name == part
            )
        first, last = node.lineno, node.end_lineno
    else:
        method = "." in symbol
        name = symbol.rsplit(".", 1)[-1]
        pattern = (
            rf"^  {re.escape(name)}\s*(?:<[^>]+>)?\("
            if method
            else rf"^export function {re.escape(name)}\s*(?:<[^>]+>)?\("
        )
        start = next(i for i, line in enumerate(lines) if re.search(pattern, line))
        if method and lines[start].rstrip().endswith("}"):
            end = start
        else:
            closing = "  }" if method else "}"
            end = next(i for i in range(start + 1, len(lines)) if lines[i] == closing)
        first, last = start + 1, end + 1
    text = "\n".join(lines[first - 1 : last])
    return {
        "path": path,
        "symbol": symbol,
        "start_line": first,
        "end_line": last,
        "text": text,
        "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
    }


def labels_for(task: dict[str, Any]) -> dict[str, Any]:
    language = task["language"]
    sources = PYTHON_SOURCES if language == "python" else TYPESCRIPT_SOURCES
    path = task["target_files"][0]
    symbol = task["expected_symbols"][0].split(".", 2)[2]
    primary = source_label(path, sources[path], symbol, language)
    helpers = []
    if task["oracle_id"] == "and-search":
        helpers.append(source_label(path, sources[path], "tokens", language))
    callers = []
    if task["oracle_id"] in INTEGRATION_CALLERS:
        caller = INTEGRATION_CALLERS[task["oracle_id"]][language == "typescript"]
        service_path = "atlas/service.py" if language == "python" else "src/service.ts"
        callers.append(
            source_label(service_path, sources[service_path], "DocumentService." + caller, language)
        )
    return {"primary": primary, "direct_local_helpers": helpers, "integration_callers": callers}


def independent_hashes(root: Path, response: dict[str, Any]) -> dict[str, Any]:
    hashes = response.get(
        "source_hashes", response.get("passport", {}).get("verified_source_hashes", {})
    )
    evidence = []
    for relative, claimed in sorted(hashes.items()):
        path = root / relative
        contained = not path.is_symlink() and path.resolve().is_relative_to(root.resolve())
        actual = sha256(path) if contained and path.is_file() else None
        evidence.append(
            {
                "path": relative,
                "claimed_sha256": claimed,
                "actual_sha256": actual,
                "matches": claimed == actual,
            }
        )
    return {
        "files": evidence,
        "all_match": all(row["matches"] for row in evidence) if evidence else None,
    }


def evaluate_one(
    service: Service,
    project: str,
    root: Path,
    task: dict[str, Any],
    profile: str,
    budget: int,
    repeat: int,
    artifacts: Path,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "task_id": task["id"],
        "language": task["language"],
        "profile": profile,
        "budget": budget,
        "repeat": repeat,
        "status": "error",
        "errors": [],
    }
    adapter, session = None, None
    try:
        before_wall, before_cpu = time.perf_counter(), time.process_time()
        if profile.startswith("compact_"):
            adapter = AgentContext(service, project)
            response = adapter.fetch(task["prompt"], budget=budget)
        else:
            session = service.memory.start_session(project, task["prompt"])["id"]
            response = service.context.get_context(session, task["prompt"], level=2, budget=budget)
        row["wall_seconds"] = time.perf_counter() - before_wall
        row["process_cpu_seconds"] = time.process_time() - before_cpu
        labels = labels_for(task)
        items = response["items"]
        primary = body_evidence(labels["primary"], items)
        helpers = [body_evidence(label, items) for label in labels["direct_local_helpers"]]
        callers = [body_evidence(label, items) for label in labels["integration_callers"]]
        row.update(
            status="ok",
            primary_body=primary,
            direct_local_helper_bodies=helpers,
            integration_caller_bodies=callers,
            all_declared_bodies_present=all(
                item["complete"] for item in [primary, *helpers, *callers]
            ),
            canonical_json_bytes=len(canonical_bytes(response)),
            snippet_bytes=sum(len(item["snippet"].encode()) for item in items),
            planning_estimate=estimate_tokens(response),
            unique_file_count=len({item["path"] for item in items}),
            item_count=len(items),
            returned_files=sorted({item["path"] for item in items}),
            source_hash_comparison=independent_hashes(root, response),
            source_freshness=response.get(
                "source_freshness", response.get("passport", {}).get("source_freshness")
            ),
            truncated=response.get("truncated"),
            warnings=response.get("warnings", []),
            billed_input_tokens=None,
            billed_cost=None,
        )
        artifacts.mkdir(parents=True)
        (artifacts / "context.json").write_bytes(canonical_bytes(response) + b"\n")
    except Exception as error:
        row["errors"].append(type(error).__name__ + ": " + str(error))
    finally:
        if adapter is not None:
            adapter.close()
        elif session is not None:
            service.memory.end_session(session)
    return row


def freshness_check(
    base: Path, language: str, profile: str, budget: int, mutation: str
) -> dict[str, Any]:
    root = base / "fixture"
    build_repository(language, root)
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    service = Service(base / "state.sqlite")
    adapter = None
    session = None
    result: dict[str, Any] = {
        "language": language,
        "profile": profile,
        "budget": budget,
        "mutation": mutation,
        "status": "error",
    }
    try:
        project = service.indexer.add_project(str(root))["id"]
        target = "atlas/search.py" if language == "python" else "src/search.ts"
        if profile.startswith("compact_"):
            adapter = AgentContext(service, project)
            old = adapter.fetch(target, budget=budget)
        else:
            session = service.memory.start_session(project, target)["id"]
            old = service.context.get_context(session, target, level=2, budget=budget)
        before = independent_hashes(root, old)
        path = root / target
        old_hash = sha256(path)
        if mutation == "edit":
            path.write_text(
                path.read_text()
                + ("\n# " if language == "python" else "\n// ")
                + "Independent freshness mutation 93018627\n"
            )
        else:
            path.unlink()
        expected_stale = [
            entry["path"]
            for entry in independent_hashes(root, old)["files"]
            if not entry["matches"]
        ]
        checked = (
            adapter.verify(old["retrieval_id"])
            if adapter is not None
            else service.context.get_passport(cast(str, session), old["retrieval_id"])
        )
        refreshed = (
            adapter.fetch(target, budget=budget)
            if adapter is not None
            else service.context.get_context(cast(str, session), target, level=2, budget=budget)
        )
        fresh_hashes = independent_hashes(root, refreshed)
        new_target_hash = sha256(path) if path.exists() else None
        result.update(
            status="ok",
            initial_hashes=before,
            original_target_sha256=old_hash,
            current_target_sha256=new_target_hash,
            independently_changed=old_hash != new_target_hash,
            expected_stale_files=expected_stale,
            observed_stale_files=checked.get("stale_files", []),
            stale_detection_correct=bool(expected_stale)
            and checked["source_freshness"] == "Stale"
            and set(checked.get("stale_files", [])) == set(expected_stale),
            refreshed_hashes=fresh_hashes,
            refreshed_hashes_correct=fresh_hashes["all_match"],
            deleted_target_absent=mutation != "delete"
            or not any(item["path"] == target for item in refreshed["items"]),
        )
    except Exception as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    finally:
        if adapter is not None:
            adapter.close()
        elif session is not None:
            service.memory.end_session(session)
        service.close()
    return result


def metric_summary(values: list[float | int]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "n": len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "p95": ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)] if ordered else None,
    }


def aggregate(rows: list[dict[str, Any]], profile: str) -> dict[str, Any]:
    assigned = [row for row in rows if row["profile"] == profile]
    valid = [row for row in assigned if row["status"] == "ok"]
    helpers = [body for row in valid for body in row["direct_local_helper_bodies"]]
    callers = [body for row in valid for body in row["integration_caller_bodies"]]
    oracle = {task["id"]: labels_for(task) for task in task_definitions()}
    return {
        "planned": len(assigned),
        "valid": len(valid),
        "complete_primary_bodies": sum(row["primary_body"]["complete"] for row in valid),
        "complete_direct_local_helpers": sum(body["complete"] for body in helpers),
        "declared_direct_local_helpers": sum(
            len(oracle[row["task_id"]]["direct_local_helpers"]) for row in assigned
        ),
        "complete_integration_callers": sum(body["complete"] for body in callers),
        "declared_integration_callers": sum(
            len(oracle[row["task_id"]]["integration_callers"]) for row in assigned
        ),
        "all_declared_bodies_present": sum(row["all_declared_bodies_present"] for row in valid),
        "all_source_hashes_correct": sum(
            row["source_hash_comparison"]["all_match"] is True for row in valid
        ),
        "metrics": {
            name: metric_summary([row[name] for row in valid])
            for name in (
                "canonical_json_bytes",
                "snippet_bytes",
                "planning_estimate",
                "unique_file_count",
                "item_count",
                "wall_seconds",
                "process_cpu_seconds",
            )
        },
        "errors": [row for row in assigned if row["status"] != "ok"],
        "incomplete_task_ids": sorted(
            {row["task_id"] for row in valid if not row["all_declared_bodies_present"]}
        ),
    }


def body_preservation(rows: list[dict[str, Any]], profile: str) -> dict[str, Any]:
    """Compare each declared body; matching aggregate totals cannot hide swaps."""
    baseline = {
        (row["task_id"], row["repeat"]): row for row in rows if row["profile"] == "full_4000"
    }
    pairs = []

    def bodies(row: dict[str, Any]) -> dict[tuple[str, str], bool]:
        return {
            (body["path"], body["symbol"]): body["complete"]
            for body in [
                row["primary_body"],
                *row["direct_local_helper_bodies"],
                *row["integration_caller_bodies"],
            ]
        }

    for row in rows:
        if row["profile"] != profile:
            continue
        old = baseline.get((row["task_id"], row["repeat"]))
        comparable = bool(old and old["status"] == row["status"] == "ok")
        missing = []
        if comparable and old is not None:
            candidate = bodies(row)
            missing = [
                {"path": path, "symbol": symbol}
                for (path, symbol), complete in bodies(old).items()
                if complete and not candidate.get((path, symbol), False)
            ]
        pairs.append(
            {
                "task_id": row["task_id"],
                "repeat": row["repeat"],
                "comparable": comparable,
                "all_baseline_complete_bodies_preserved": comparable and not missing,
                "lost_complete_bodies": missing,
            }
        )
    return {
        "pairs": pairs,
        "all_comparable": bool(pairs) and all(pair["comparable"] for pair in pairs),
        "all_baseline_complete_bodies_preserved": bool(pairs)
        and all(pair["all_baseline_complete_bodies_preserved"] for pair in pairs),
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Compact context: development budget evaluation",
        "",
        "These are reused Atlas development tasks, not the new 40-task evaluation or model A/B results. Complete bodies require every original source line at the correct range; symbol declarations alone do not pass.",
        "",
        f"Source snapshot stable: **{report['source_snapshot_stable']}**. Source SHA-256: `{report['source_before']['tree_sha256']}`.",
        "",
        "| Profile | Valid | Complete primary | Direct local helpers | Integration callers | All declared bodies | Mean JSON bytes | Median retrieval ms | p95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, _ in PROFILES:
        value = report["summaries"][name]
        metrics = value["metrics"]
        timing = metrics["wall_seconds"]

        def fmt(number: float | None, scale: int = 1) -> str:
            return f"{number * scale:,.2f}" if number is not None else "unavailable"

        lines.append(
            f"| {name} | {value['valid']}/{value['planned']} | {value['complete_primary_bodies']}/{value['planned']} | {value['complete_direct_local_helpers']}/{value['declared_direct_local_helpers']} | {value['complete_integration_callers']}/{value['declared_integration_callers']} | {value['all_declared_bodies_present']}/{value['planned']} | {fmt(metrics['canonical_json_bytes']['mean'])} | {fmt(timing['median'], 1000)} | {fmt(timing['p95'], 1000)} |"
        )
    lines += [
        "",
        f"Development recommendation: **{report['recommended_profile'] or 'none'}** is the lowest tested compact budget that preserves every complete body returned by full_4000 in every matched observation without retrieval errors. This rule does not declare the rich comparator complete or establish model savings.",
    ]
    lines += [
        "",
        "The full_4000 comparator uses the current engine and rich transport at budget 4000. It is not a rerun of the historical V1 application. Compact profiles use the same current engine at level 2 with repeated transport metadata removed. Fresh empty sessions are used for every observation, with balanced/reversed profile order and common warm OS/SQLite caches. Timing includes session creation and retrieval; excludes indexing, MCP startup, networking and model execution.",
        "",
        "Source hashes are independently computed from file bytes. Controlled edit and deletion probes compare the old response hashes with changed disk content, then require the exact changed-path set to be reported stale. All probe results and failures appear in JSON.",
        "Host CPU and operating-system caches were shared with development activity; local timing is descriptive and cannot establish a controlled speed improvement.",
        "",
    ]
    probes = report["freshness_checks"]
    checked_refreshes = [p for p in probes if p.get("refreshed_hashes_correct") is not None]
    lines.append(
        f"Freshness probes: {sum(p.get('stale_detection_correct', False) for p in probes)}/{len(probes)} correctly detected changed/deleted sources; {sum(p['refreshed_hashes_correct'] for p in checked_refreshes)}/{len(checked_refreshes)} refreshed responses with returned source hashes matched independently hashed current files. {len(probes) - len(checked_refreshes)} refreshed responses had no source hashes to verify."
    )
    lines += [
        "",
        "No model was called. JSON bytes and server planning estimates are not billed tokens or cost. Local helper ground truth includes only the local tokens implementation called by search; runtime, standard-library, transitive dependencies and general semantic sufficiency are not judged. Integration callers are separately declared because several task prompts require DocumentService behavior. Previously used tasks can guide a default, but cannot establish held-out performance or Codex savings.",
        "",
        "## Incomplete tasks",
        "",
    ]
    for name, _ in PROFILES:
        lines.append(
            f"- {name}: {', '.join(report['summaries'][name]['incomplete_task_ids']) or 'none'}"
        )
    if not report["source_snapshot_stable"]:
        lines += [
            "",
            "**Source changed during this measurement set. Do not treat these results as a comparison of a frozen candidate; rerun after the source freeze.**",
        ]
    return "\n".join(lines) + "\n"


def run(output: Path, repeats: int = 2) -> dict[str, Any]:
    if output.exists():
        raise ValueError("Use a new output directory; observations are never overwritten")
    output.mkdir(parents=True)
    before = source_state()
    tasks = task_definitions()
    rows, fixtures, services, projects = [], {}, {}, {}
    try:
        for language in ("python", "typescript"):
            root = output / language / "fixture"
            build_repository(language, root)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            service = Service(output / language / "state.sqlite")
            services[language] = service
            fixtures[language] = root
            projects[language] = service.indexer.add_project(str(root))["id"]
        for repeat in range(1, repeats + 1):
            for index, task in enumerate(tasks):
                profiles = list(
                    PROFILES[index % len(PROFILES) :] + PROFILES[: index % len(PROFILES)]
                )
                if repeat % 2 == 0:
                    profiles.reverse()
                for profile, budget in profiles:
                    row = evaluate_one(
                        services[task["language"]],
                        projects[task["language"]],
                        fixtures[task["language"]],
                        task,
                        profile,
                        budget,
                        repeat,
                        output / "responses" / f"{task['id']}-{profile}-r{repeat}",
                    )
                    rows.append(row)
                    print(
                        f"{len(rows)}/{len(tasks) * repeats * len(PROFILES)} {task['id']} {profile} {row['status']}",
                        flush=True,
                    )
    finally:
        for service in services.values():
            service.close()
    freshness = [
        freshness_check(
            output / "freshness" / f"{language}-{profile}-{mutation}",
            language,
            profile,
            budget,
            mutation,
        )
        for language in ("python", "typescript")
        for profile, budget in PROFILES
        for mutation in ("edit", "delete")
    ]
    after = source_state()
    preservation = {
        profile: body_preservation(rows, profile)
        for profile, _ in PROFILES
        if profile.startswith("compact_")
    }
    recommended = next(
        (
            profile
            for profile, _ in PROFILES
            if profile.startswith("compact_")
            and preservation[profile]["all_baseline_complete_bodies_preserved"]
        ),
        None,
    )
    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "evaluation_label": "reused_development_only_no_model",
        "task_count": len(tasks),
        "repeats": repeats,
        "source_before": before,
        "source_after": after,
        "source_snapshot_stable": before == after,
        "harness_sha256": sha256(Path(__file__)),
        "corpus_sha256": sha256(ROOT / "benchmarks/corpus.py"),
        "body_evidence_evaluator_sha256": sha256(ROOT / "benchmarks/refinement_eval.py"),
        "protocol": {
            "scope": "Only reused original Atlas 24 tasks; no corpus_v2 queries inspected or measured.",
            "queries": "Identical original task prompt text in every profile and repeat.",
            "sessions": "Fresh empty task session per observation; no stored memory or model requests.",
            "order": "Profile order rotates by task and reverses on even repeats.",
            "timing": "Session creation plus synchronous retrieval; excludes initial indexing and MCP/model startup.",
            "cpu": "Current Python process CPU only; child process CPU and resident memory are not measured.",
            "host_conditions": "Concurrent development activity and shared warm OS/SQLite caches; timings are descriptive.",
            "primary_ground_truth": "Independent Python AST or narrow immutable TypeScript fixture grammar; exact complete source lines required.",
            "helpers": "Local tokens helper called by search only; language/runtime/library dependencies are outside scope.",
            "integration_callers": "Seven explicit DocumentService entry points per language, separately judged from direct helpers.",
            "budget": "Engine UTF-8 byte planning estimate, not billed model usage. Adapter removes metadata after rich-engine budget packing.",
            "freshness": "Independent disk SHA-256 comparisons before/after edit and deletion; exact stale path sets required.",
        },
        "fixture_source_hashes": {
            language: {
                path: hashlib.sha256(text.encode()).hexdigest() for path, text in sources.items()
            }
            for language, sources in (
                ("python", PYTHON_SOURCES),
                ("typescript", TYPESCRIPT_SOURCES),
            )
        },
        "summaries": {profile: aggregate(rows, profile) for profile, _ in PROFILES},
        "complete_body_preservation": preservation,
        "recommended_profile": recommended,
        "observations": rows,
        "freshness_checks": freshness,
        "unavailable": {"billed_tokens": None, "actual_cost": None, "model_success_rate": None},
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "report.md").write_text(markdown(report))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--report-prefix", type=Path)
    arguments = parser.parse_args()
    if arguments.repeats < 1:
        parser.error("repeats must be positive")
    if arguments.report_prefix and any(
        arguments.report_prefix.with_suffix(suffix).exists() for suffix in (".md", ".json")
    ):
        parser.error("Use a new report prefix; reports are never overwritten")
    result = run(arguments.output, arguments.repeats)
    if arguments.report_prefix:
        if not result["source_snapshot_stable"]:
            raise SystemExit(
                "Source changed; retained raw measurements, declined public frozen-candidate report"
            )
        arguments.report_prefix.parent.mkdir(parents=True, exist_ok=True)
        arguments.report_prefix.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
        arguments.report_prefix.with_suffix(".md").write_text(markdown(result))


if __name__ == "__main__":
    main()
