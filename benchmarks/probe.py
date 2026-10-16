"""Measure real Memglide MCP components independently of the Codex A/B runs.

These probes are official SDK clients, not Codex model sessions.  Declared-file
and symbol coverage is a narrow retrieval proxy, not semantic completeness.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from benchmarks.corpus import build_repository, task_definitions
from benchmarks.run import ProcessSampler
from memglide.service import Service

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _git(root: Path, *arguments: str, env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *arguments],
        env=env,
        text=True,
        stderr=subprocess.PIPE,
    ).strip()


def _make_seed(language: str, root: Path) -> str:
    build_repository(language, root)
    environment = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Memglide benchmark",
        "GIT_COMMITTER_NAME": "Memglide benchmark",
        "GIT_AUTHOR_EMAIL": "benchmark@example.invalid",
        "GIT_COMMITTER_EMAIL": "benchmark@example.invalid",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
    }
    _git(root, "init", "-q")
    _git(root, "add", ".")
    _git(
        root,
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "-m",
        "Atlas corpus baseline",
        env=environment,
    )
    return _git(root, "rev-parse", "HEAD")


def coverage_proxy(task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Match a declared symbol inside its declared file, not by loose suffix."""
    expected_paths = set(task["target_files"])
    returned_paths = {item["path"] for item in context["items"]}
    matched_symbols = []
    visible_declarations = []
    for expected in task["expected_symbols"]:
        # Corpus metadata: source-directory.module.Class.method (or function).
        directory, module, local_name = expected.split(".", 2)
        suffix = ".py" if task["language"] == "python" else ".ts"
        path = f"{directory}/{module}{suffix}"
        if any(
            item["path"] == path and item.get("symbol") == local_name for item in context["items"]
        ):
            matched_symbols.append(expected)
        declaration = re.compile(
            r"^\s*(?:export\s+)?(?:async\s+)?(?:def\s+|function\s+)?"
            + re.escape(local_name.rsplit(".", 1)[-1])
            + r"\s*(?:<[^>]+>)?\s*\(",
            re.MULTILINE,
        )
        if any(
            item["path"] == path and declaration.search(item.get("snippet", ""))
            for item in context["items"]
        ):
            visible_declarations.append(expected)
    return {
        "expected_target_files": sorted(expected_paths),
        "retrieved_target_files": sorted(expected_paths & returned_paths),
        "target_file_coverage_fraction": len(expected_paths & returned_paths) / len(expected_paths)
        if expected_paths
        else None,
        "expected_symbols": task["expected_symbols"],
        "retrieved_expected_symbols": sorted(matched_symbols),
        "expected_symbol_coverage_fraction": len(matched_symbols) / len(task["expected_symbols"])
        if task["expected_symbols"]
        else None,
        "visible_expected_declarations": sorted(visible_declarations),
        "expected_declaration_visible_fraction": len(visible_declarations)
        / len(task["expected_symbols"])
        if task["expected_symbols"]
        else None,
        "returned_files": sorted(returned_paths),
        "returned_item_count": len(context["items"]),
        "passport_status": context["passport"]["status"],
        "warnings": context.get("warnings", []),
        "truncated": context.get("truncated"),
        "scope": "Declared file / exact symbol identity / declaration visible in snippet proxies. Whole-file or class evidence can contain a declaration without its exact symbol identity. None establishes complete method bodies or semantic context completeness.",
    }


def verify_hashes(context: dict[str, Any], worktree: Path) -> dict[str, Any]:
    checks = []
    for item in context["items"]:
        target = (worktree / item["path"]).resolve()
        contained = worktree.resolve() in target.parents
        actual = (
            hashlib.sha256(target.read_bytes()).hexdigest()
            if contained and target.is_file()
            else None
        )
        checks.append(
            {
                "path": item["path"],
                "symbol": item.get("symbol"),
                "returned_sha256": item.get("hash"),
                "actual_sha256": actual,
                "matches": actual is not None and actual == item.get("hash"),
            }
        )
    return {
        "checked_items": len(checks),
        "all_hashes_current": bool(checks) and all(item["matches"] for item in checks),
        "items": checks,
    }


def component_checks(result: dict[str, Any]) -> dict[str, bool]:
    freshness = result.get("controlled_freshness", {})
    return {
        "natural_retrieval_hashes_current": result.get("natural_prompt_hash_freshness", {}).get(
            "all_hashes_current", False
        ),
        "old_passport_detected_edit": freshness.get("old_passport_detected_edit", False),
        "updated_target_sha_matches": freshness.get("updated_target_sha_matches", False),
        "updated_target_contains_edit_marker": freshness.get(
            "updated_target_contains_edit_marker", False
        ),
        "updated_source_freshness_current": freshness.get("updated_source_freshness") == "Current",
        "updated_evidence_hashes_current": freshness.get("updated_evidence_hashes", {}).get(
            "all_hashes_current", False
        ),
    }


async def probe_task(task: dict[str, Any], worktree: Path, artifacts: Path) -> dict[str, Any]:
    """Register a fresh index, invoke real MCP, then test controlled invalidation."""
    artifacts.mkdir(parents=True, exist_ok=True)
    database = artifacts / "state/memglide.db"
    started = time.perf_counter()
    cpu_started = time.process_time()
    service = Service(database)
    try:
        project = service.indexer.add_project(str(worktree))
    finally:
        service.close()
    index_timing = {
        "wall_seconds": time.perf_counter() - started,
        "client_cpu_seconds": time.process_time() - cpu_started,
        "client_cpu_scope": "Current probe process registration/indexing; Git child CPU excluded",
        "index_stats": project.get("index_stats"),
    }
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "memglide.cli", "--db", str(database), "mcp"],
        env={"MEMGLIDE_HOME": str(database.parent), "PYTHONPATH": str(ROOT / "src")},
        cwd=str(worktree),
    )
    calls: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "task_id": task["id"],
        "language": task["language"],
        "baseline_commit": _git(worktree, "rev-parse", "HEAD"),
        "index": index_timing,
        "status": "failed",
        "mcp_calls": calls,
        "transport_status": "failed",
        "is_codex_invocation": False,
        "actual_model_usage": None,
        "actual_model_cost_usd": None,
    }
    sampler = ProcessSampler(os.getpid())
    sampler.start()
    transport_start = time.perf_counter()
    try:
        with (artifacts / "server.stderr.log").open("w", encoding="utf-8") as errlog:
            async with (
                stdio_client(params, errlog=errlog) as (read, write),
                ClientSession(read, write) as client,
            ):
                with anyio.fail_after(60):
                    initialized = await client.initialize()
                    tools = await client.list_tools()
                result["transport"] = {
                    "server_name": initialized.server_info.name,
                    "discovered_tools": sorted(tool.name for tool in tools.tools),
                    "initialize_and_list_tools_wall_seconds": time.perf_counter() - transport_start,
                    "sdk": "mcp.client.session.ClientSession / mcp.client.stdio.stdio_client",
                }

                async def invoke(name: str, **arguments: Any) -> dict[str, Any]:
                    call_start = time.perf_counter()
                    with anyio.fail_after(60):
                        response = await client.call_tool(name, arguments)
                    record = {
                        "name": name,
                        "wall_seconds": time.perf_counter() - call_start,
                        "is_error": bool(response.is_error),
                    }
                    path = artifacts / f"call-{len(calls) + 1:02d}-{name}.json"
                    record["artifact"] = (
                        str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
                    )
                    calls.append(record)
                    _write_json(
                        path,
                        {
                            "tool": name,
                            "arguments": arguments,
                            "response": response.model_dump(mode="json"),
                        },
                    )
                    if response.is_error or response.structured_content is None:
                        raise RuntimeError(
                            f"{name} failed or omitted structured output; inspect {path}"
                        )
                    return response.structured_content

                projects = await invoke("list_projects")
                if [item["id"] for item in projects["projects"]] != [project["id"]]:
                    raise RuntimeError(
                        "Fresh MCP database did not contain exactly its task project"
                    )
                session = await invoke(
                    "start_session", project_id=project["id"], task=task["prompt"]
                )
                natural = await invoke(
                    "get_context",
                    session_id=session["id"],
                    query=task["prompt"],
                    level=2,
                    budget=8000,
                )
                result["natural_prompt_retrieval"] = coverage_proxy(task, natural)
                result["natural_prompt_hash_freshness"] = verify_hashes(natural, worktree)
                # A separate exact-file retrieval establishes that the controlled
                # mutation was selected, even if the natural prompt missed it.
                target_path = task["target_files"][0]
                targeted = await invoke(
                    "get_context",
                    session_id=session["id"],
                    query=target_path,
                    level=3,
                    budget=16000,
                )
                before_hash = hashlib.sha256((worktree / target_path).read_bytes()).hexdigest()
                target_selected = any(item["path"] == target_path for item in targeted["items"])
                marker = f"memglide_component_freshness_{task['id'].replace('-', '_')}"
                comment = ("# " if task["language"] == "python" else "// ") + marker + "\n"
                with (worktree / target_path).open("a", encoding="utf-8") as handle:
                    handle.write("\n" + comment)
                after_hash = hashlib.sha256((worktree / target_path).read_bytes()).hexdigest()
                old_passport = await invoke(
                    "get_context_passport",
                    session_id=session["id"],
                    retrieval_id=targeted["retrieval_id"],
                )
                # get_context synchronously refreshes the index; no sleep or
                # watcher-delay assumption is used to declare freshness.
                updated = await invoke(
                    "get_context",
                    session_id=session["id"],
                    query=target_path,
                    level=3,
                    budget=16000,
                )
                current_hashes = verify_hashes(updated, worktree)
                updated_target = [item for item in updated["items"] if item["path"] == target_path]
                result["controlled_freshness"] = {
                    "target_file": target_path,
                    "target_selected_before_edit": target_selected,
                    "before_sha256": before_hash,
                    "after_sha256": after_hash,
                    "old_passport_status_after_edit": old_passport["status"],
                    "old_passport_stale_files": old_passport.get("stale_files", []),
                    "old_passport_detected_edit": target_selected
                    and old_passport["status"] == "Stale"
                    and target_path in old_passport.get("stale_files", []),
                    "updated_target_returned": bool(updated_target),
                    "updated_target_sha_matches": bool(updated_target)
                    and all(item["hash"] == after_hash for item in updated_target),
                    "updated_target_contains_edit_marker": any(
                        marker in item.get("snippet", "") for item in updated_target
                    ),
                    "updated_passport_status": updated["passport"]["status"],
                    "updated_source_freshness": updated["passport"]["source_freshness"],
                    "updated_evidence_hashes": current_hashes,
                    "edit_kind": "append comment marker, preserving executable behavior",
                }
                await invoke("end_session", session_id=session["id"])
                result["transport_status"] = "passed"
                result["checks"] = component_checks(result)
                result["status"] = "passed" if all(result["checks"].values()) else "failed"
    except Exception as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        sampled = sampler.finish()
        result["mcp_transport_wall_seconds"] = time.perf_counter() - transport_start
        result["local_server_overhead"] = {
            "sampled_cpu_seconds": sampled["memglide_cpu_seconds"],
            "sampled_peak_rss_bytes": sampled["memglide_peak_rss_bytes"],
            "samples": sampled["samples"],
            "sampling_interval_seconds": sampled["sampling_interval_seconds"],
            "scope": "Fresh Memglide MCP server and descendants only; excludes registration/indexing in probe client and remote inference",
            "method": sampled["method"],
        }
    result["mcp_call_count"] = len(calls)
    _write_json(artifacts / "result.json", result)
    return result


def _summaries(results: list[dict[str, Any]]) -> dict[str, Any]:
    def distribution(values: list[float | None]) -> dict[str, Any]:
        measured = [value for value in values if value is not None]
        return {
            "count": len(measured),
            "mean": statistics.mean(measured) if measured else None,
            "median": statistics.median(measured) if measured else None,
            "min": min(measured) if measured else None,
            "max": max(measured) if measured else None,
        }

    return {
        "task_count": len(results),
        "component_checks_passed": sum(item["status"] == "passed" for item in results),
        "component_checks_failed": sum(item["status"] != "passed" for item in results),
        "transport_probe_passed": sum(item.get("transport_status") == "passed" for item in results),
        "transport_probe_failed": sum(item.get("transport_status") != "passed" for item in results),
        "mcp_tool_calls": sum(item["mcp_call_count"] for item in results),
        "natural_prompt_target_file_misses": [
            item["task_id"]
            for item in results
            if item.get("natural_prompt_retrieval", {}).get("target_file_coverage_fraction") == 0
        ],
        "target_file_coverage_fraction": distribution(
            [
                item.get("natural_prompt_retrieval", {}).get("target_file_coverage_fraction")
                for item in results
            ]
        ),
        "target_symbol_coverage_fraction": distribution(
            [
                item.get("natural_prompt_retrieval", {}).get("expected_symbol_coverage_fraction")
                for item in results
            ]
        ),
        "target_declaration_visible_fraction": distribution(
            [
                item.get("natural_prompt_retrieval", {}).get(
                    "expected_declaration_visible_fraction"
                )
                for item in results
            ]
        ),
        "natural_retrieval_all_hashes_current": sum(
            item.get("natural_prompt_hash_freshness", {}).get("all_hashes_current", False)
            for item in results
        ),
        "old_passport_detected_controlled_edit": sum(
            item.get("controlled_freshness", {}).get("old_passport_detected_edit", False)
            for item in results
        ),
        "updated_target_sha_matches": sum(
            item.get("controlled_freshness", {}).get("updated_target_sha_matches", False)
            for item in results
        ),
        "updated_target_contains_edit_marker": sum(
            item.get("controlled_freshness", {}).get("updated_target_contains_edit_marker", False)
            for item in results
        ),
        "index_wall_seconds": distribution([item["index"]["wall_seconds"] for item in results]),
        "mcp_transport_wall_seconds": distribution(
            [item["mcp_transport_wall_seconds"] for item in results]
        ),
        "mcp_server_sampled_cpu_seconds": distribution(
            [item["local_server_overhead"]["sampled_cpu_seconds"] for item in results]
        ),
        "mcp_server_sampled_peak_rss_bytes": distribution(
            [item["local_server_overhead"]["sampled_peak_rss_bytes"] for item in results]
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Memglide MCP component diagnostics",
        "",
        "These measurements use the official MCP SDK against real STDIO subprocesses. They are independent component checks, **not Codex model runs, A/B results, or evidence of token/cost savings**.",
        "",
        f"Executed {summary['task_count']} isolated task worktrees with fresh databases: {summary['transport_probe_passed']} transport probes passed, {summary['transport_probe_failed']} failed; {summary['component_checks_passed']} freshness/hash checks passed, {summary['component_checks_failed']} failed; {summary['mcp_tool_calls']} actual SDK tool calls.",
        "",
        "Natural task-prompt retrieval uses level 2 and an 8,000 estimated-token budget. Target-file and symbol coverage compare returned evidence with one declared fix location per task. This is a narrow coverage proxy; passing it does not prove context completeness or successful coding. The returned budget estimate is not billed token usage.",
        "",
        f"Mean target-file coverage: {summary['target_file_coverage_fraction']['mean']}; mean exact target-symbol identity coverage: {summary['target_symbol_coverage_fraction']['mean']}; mean expected declaration visibility in source snippets: {summary['target_declaration_visible_fraction']['mean']}. Whole-file/class evidence can contain a declaration while failing an exact symbol-identity match; declaration visibility does not establish a complete method body. All returned natural-retrieval evidence hashes matched disk in {summary['natural_retrieval_all_hashes_current']}/{summary['task_count']} task probes.",
        "",
        f"**Natural task-prompt retrieval missed the declared target file in {len(summary['natural_prompt_target_file_misses'])}/{summary['task_count']} queries:** "
        + ", ".join(f"`{task_id}`" for task_id in summary["natural_prompt_target_file_misses"])
        + ". These misses remain in every coverage statistic; the later exact-file query does not repair the natural-query score.",
        "",
        f"A separate exact-file level-3 retrieval selected a controlled comment edit. The old passport detected staleness in {summary['old_passport_detected_controlled_edit']}/{summary['task_count']} probes; updated target hashes matched in {summary['updated_target_sha_matches']}/{summary['task_count']}, and updated full-source snippets contained the marker in {summary['updated_target_contains_edit_marker']}/{summary['task_count']}.",
        "",
        "| Metric | Mean | Median | Min | Max |",
        "|---|---:|---:|---:|---:|",
    ]
    for field in (
        "index_wall_seconds",
        "mcp_transport_wall_seconds",
        "mcp_server_sampled_cpu_seconds",
        "mcp_server_sampled_peak_rss_bytes",
    ):
        row = summary[field]

        def fmt(value: Any) -> str:
            return "unavailable" if value is None else f"{value:.4f}"

        lines.append(
            f"| {field} | {fmt(row['mean'])} | {fmt(row['median'])} | {fmt(row['min'])} | {fmt(row['max'])} |"
        )
    lines.extend(
        [
            "",
            "Server CPU and RSS are sampled locally every 50 ms. CPU is an observed lower bound; short-lived processes can be missed, shared RSS pages may be counted more than once. Timings include startup, SDK operations, controlled edit and shutdown. Index registration is measured separately in the probe process. These tiny synthetic libraries do not establish production scaling behavior.",
            "",
            "| Task | Transport/hash checks | File coverage | Exact symbol coverage | Declaration visible | Old passport stale | Updated hash | Edit marker | MCP calls |",
            "|---|---|---:|---:|---:|---|---|---|---:|",
        ]
    )
    for item in report["results"]:
        retrieval, fresh = (
            item.get("natural_prompt_retrieval", {}),
            item.get("controlled_freshness", {}),
        )
        lines.append(
            f"| {item['task_id']} | {item['status']} | {retrieval.get('target_file_coverage_fraction')} | {retrieval.get('expected_symbol_coverage_fraction')} | {retrieval.get('expected_declaration_visible_fraction')} | {fresh.get('old_passport_detected_edit')} | {fresh.get('updated_target_sha_matches')} | {fresh.get('updated_target_contains_edit_marker')} | {item['mcp_call_count']} |"
        )
        if item.get("error"):
            lines.append(f"\nFailure: `{item['task_id']}`: `{item['error']}`\n")
    lines.extend(
        [
            "",
            "Raw SDK arguments/responses and server logs are retained under the reported artifact root. Every failure is included. Model input/cached/output tokens, model calls, billed cost and coding success are unavailable in this component probe and remain null. A full passport status can remain Partial when source hashes are current, because unresolved static dependencies are reported separately from freshness.",
            "",
        ]
    )
    return "\n".join(lines)


def reanalyze_report(path: Path) -> dict[str, Any]:
    """Recompute explicitly defined coverage/check fields from retained evidence.

    No MCP requests are issued and measured timings/usage remain untouched.
    This permits analysis corrections without silently rerunning measurements.
    """
    report = json.loads(path.read_text())
    tasks = {task["id"]: task for task in task_definitions()}
    for result in report["results"]:
        first_context = next(
            (call for call in result["mcp_calls"] if call["name"] == "get_context"), None
        )
        if first_context:
            call_path = Path(first_context["artifact"])
            if not call_path.is_absolute():
                call_path = ROOT / call_path
            response = json.loads(call_path.read_text())["response"]["structured_content"]
            result["natural_prompt_retrieval"] = coverage_proxy(tasks[result["task_id"]], response)
        result["transport_status"] = "failed" if result.get("error") else "passed"
        result["checks"] = component_checks(result)
        result["status"] = (
            "passed"
            if result["transport_status"] == "passed" and all(result["checks"].values())
            else "failed"
        )
        raw_root = Path(report["artifact_root"])
        if not raw_root.is_absolute():
            raw_root = ROOT / raw_root
        _write_json(raw_root / "runs" / result["task_id"] / "result.json", result)
    report["summary"] = _summaries(report["results"])
    report["reanalyzed_at"] = datetime.now(UTC).isoformat()
    report["reanalysis_note"] = (
        "Coverage proxies and component check statuses recomputed from retained SDK responses and hash observations. No MCP calls or timing/overhead measurements repeated."
    )
    _write_json(path, report)
    path.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    return report


async def run_probes(
    artifacts: Path, output: Path, selected_tasks: list[str] | None = None
) -> dict[str, Any]:
    artifacts = artifacts.resolve()
    artifacts.mkdir(parents=True, exist_ok=False)
    seeds, commits = {}, {}
    for language in ("python", "typescript"):
        seeds[language] = artifacts / "seeds" / language
        commits[language] = _make_seed(language, seeds[language])
    results = []
    for task in task_definitions():
        if selected_tasks and task["id"] not in selected_tasks:
            continue
        worktree = artifacts / "worktrees" / task["id"]
        worktree.parent.mkdir(parents=True, exist_ok=True)
        _git(
            seeds[task["language"]],
            "worktree",
            "add",
            "--detach",
            str(worktree),
            commits[task["language"]],
        )
        result = await probe_task(task, worktree, artifacts / "runs" / task["id"])
        results.append(result)
        print(
            json.dumps(
                {
                    "task_id": task["id"],
                    "status": result["status"],
                    "file_coverage": result.get("natural_prompt_retrieval", {}).get(
                        "target_file_coverage_fraction"
                    ),
                    "stale_detected": result.get("controlled_freshness", {}).get(
                        "old_passport_detected_edit"
                    ),
                }
            ),
            flush=True,
        )
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": "Independent real MCP component probes; no Codex model invocations or A/B savings evidence",
        "artifact_root": str(artifacts.relative_to(ROOT))
        if artifacts.is_relative_to(ROOT)
        else str(artifacts),
        "baseline_commits": commits,
        "summary": _summaries(results),
        "results": results,
        "actual_model_input_tokens": None,
        "actual_model_cached_input_tokens": None,
        "actual_model_output_tokens": None,
        "actual_model_calls": None,
        "actual_model_cost_usd": None,
        "cost_per_successful_coding_task": None,
        "coding_task_success_rate": None,
        "semantic_context_completeness": None,
    }
    _write_json(output.with_suffix(".json"), report)
    output.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks/component-probe")
    parser.add_argument("--task", action="append")
    args = parser.parse_args()
    completed = asyncio.run(run_probes(args.artifacts, args.output, args.task))
    raise SystemExit(bool(completed["summary"]["component_checks_failed"]))
