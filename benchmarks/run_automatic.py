"""Preregister, inspect offline, or explicitly dispatch a source-discovery study.

The default command is ``plan``. Neither plan nor offline uses Codex, credentials,
or a model. Execute requires a reviewed frozen plan and explicit budget approval.
Budget figures are estimates of API-price equivalents, never a hard billing cap.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import random
import shutil
import statistics
import subprocess
import time
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path, PurePosixPath
from typing import Any, TypeGuard

from benchmarks import estimate_cost as pricing
from benchmarks import run as legacy
from benchmarks import run_daily as common
from benchmarks import run_v2 as durable
from benchmarks import run_workflow_v2 as workflow

ROOT = common.ROOT
ARMS = ("A", "B", "C")
LABELS = {
    "A": "Bare Codex",
    "B": "Existing complete source using private author-known paths",
    "C": "Opt-in automatic discovery and conditional complete-source preload",
}
VERSION = "automatic-1"
LIMITS = [
    "Offline target coverage is an author-scope proxy, not semantic completeness or coding correctness.",
    "No new native model usage, task success, token saving, latency benefit or billed saving exists until an explicitly approved formal execution.",
    "The upstream repositories and intentionally injected defects are controlled workloads; size and source-snapshot coverage are disclosed, not described as representative production work.",
    "Provider and operating-system caches cannot be equivalently reset; order balancing does not establish identical caching.",
    "Native JSONL does not reveal actual billing, underlying inference-call counts, actual filesystem reads or provider CPU/memory.",
    "Native-reported zero cache writes may be a parser default; possible-write sensitivity bounds are scenarios, not confidence intervals.",
    "Budget approval is an estimated API-equivalent allowance, not a guaranteed spend ceiling; Codex exec exposes no hard total-turn token cap here.",
    "All automatic-selection abstentions and failed or interrupted attempts remain in primary intent-to-treat results; originals are never retried.",
]


def corpus() -> Any:
    return importlib.import_module("benchmarks.corpus_automatic")


def _safe_relative(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and "\x00" not in value
        and "\\" not in value
        and not PurePosixPath(value).is_absolute()
        and ".." not in PurePosixPath(value).parts
        and PurePosixPath(value).as_posix() == value
    )


def load_tasks() -> list[dict[str, Any]]:
    tasks = corpus().load_tasks()
    identifiers: set[str] = set()
    for task in tasks:
        identifier = task.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.replace("-", "").replace("_", "").isalnum()
            or identifier in identifiers
            or not isinstance(task.get("prompt"), str)
            or not task["prompt"].strip()
            or task.get("language") not in {"python", "typescript"}
            or not isinstance(task.get("known_paths"), list)
            or not task["known_paths"]
            or not all(_safe_relative(value) for value in task["known_paths"])
            or len(set(task["known_paths"])) != len(task["known_paths"])
        ):
            raise ValueError("Malformed or duplicated automatic-study task")
        identifiers.add(identifier)
        # This explicit guard prevents accidentally reusing historical path-hint tasks.
        if any(path in task["prompt"] for path in task["known_paths"]):
            raise ValueError("Public task discloses a private known source path")
    if not tasks:
        raise ValueError("A study requires tasks")
    return tasks


def task_prompt(task: dict[str, Any]) -> str:
    """Only public task text; no scope, support path, reference or oracle metadata."""
    return (
        common.COMMON_INSTRUCTIONS
        + "\nExplicit test-file policy:\n"
        + workflow.TEST_FILE_POLICY
        + "\nTask:\n"
        + task["prompt"]
        + "\n"
    )


def make_plan(tasks: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    generator = random.Random(seed)
    members = list(tasks)
    generator.shuffle(members)
    orders = list(permutations(ARMS))
    generator.shuffle(orders)
    first = {task["id"]: orders[index % len(orders)] for index, task in enumerate(members)}
    rows: list[dict[str, Any]] = []
    for repeat in range(1, repeats + 1):
        for task in members:
            order = first[task["id"]]
            if repeat % 2 == 0:
                order = tuple(reversed(order))
            for arm in order:
                rows.append(
                    {
                        "run_id": f"auto-{task['id']}-r{repeat}-{arm}",
                        "task_id": task["id"],
                        "repository": task["repository"],
                        "language": task["language"],
                        "configuration": arm,
                        "repeat": repeat,
                        "order": len(rows) + 1,
                    }
                )
    return rows


def frozen_manifest() -> dict[str, Any]:
    """Freeze application and every benchmark helper, fixture, grader and tariff."""
    files = set((ROOT / "src/memglide").rglob("*.py"))
    files.update((ROOT / "benchmarks").glob("*.py"))
    files.update((ROOT / "benchmarks/automatic-fixtures").rglob("*"))
    files.update(
        ROOT / name
        for name in (
            "benchmarks/tasks_automatic.json",
            "benchmarks/automatic-protocol.md",
            "benchmarks/cost-pricing.json",
            "benchmarks/warm-80-analysis.json",
            "pyproject.toml",
            "uv.lock",
        )
    )
    hashed = {}
    for path in sorted(files):
        if path.is_symlink():
            raise ValueError("Frozen source or fixture cannot be a symlink")
        if path.is_file():
            hashed[path.relative_to(ROOT).as_posix()] = common.digest(path.read_bytes())
    return {"git_head": legacy.git(ROOT, "rev-parse", "HEAD"), "files": hashed}


def budget_estimate(assignments: int) -> dict[str, Any]:
    historical = json.loads((ROOT / "benchmarks/warm-80-analysis.json").read_text())
    values = [
        row["cost"]["possible_write_price_upper_usd"]
        for row in historical["all_planned_runs"]
        if row.get("status") == "completed"
        and isinstance(row.get("cost", {}).get("possible_write_price_upper_usd"), (float, int))
    ]
    if not values:
        raise ValueError("No measured historical cost observations for estimate")
    high = max(values) * 3
    return {
        "kind": "Planning estimate of API list-price equivalents, not a billed or guaranteed maximum",
        "historical_completed_observations": len(values),
        "historical_possible_write_maximum_usd": max(values),
        "planning_multiplier": 3,
        "planning_high_per_assignment_usd": high,
        "estimated_campaign_high_usd": math.ceil(high * assignments * 100) / 100,
        "planned_assignments": assignments,
        "source": "benchmarks/warm-80-analysis.json; observed completed originals only",
        "hard_cap_available": False,
        "limitations": "Unfamiliar work can exceed historical spend; no hard total-turn token cap. Actual invoices remain unavailable.",
    }


def _commit_fixture(root: Path) -> dict[str, str]:
    legacy.git(root, "init", "--initial-branch=benchmark")
    legacy.git(root, "config", "user.name", "Memglide Automatic Evaluation")
    legacy.git(root, "config", "user.email", "benchmark@example.invalid")
    legacy.git(root, "add", ".")
    legacy.git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Frozen task baseline")
    return {
        "path": str(root),
        "commit": legacy.git(root, "rev-parse", "HEAD"),
        "tree": legacy.git(root, "rev-parse", "HEAD^{tree}"),
    }


def create_plan(
    output: Path, *, repeats: int, seed: int, model: str, effort: str
) -> dict[str, Any]:
    tariff = json.loads((ROOT / "benchmarks/cost-pricing.json").read_text())
    if model != tariff["model"]:
        raise ValueError("A new model requires separately reviewed and frozen matching pricing")
    output.mkdir(parents=True, exist_ok=False)
    tasks = load_tasks()
    repositories = {}
    for task in tasks:
        root = output / "repositories" / task["id"]
        root.mkdir(parents=True)
        corpus().build_task_repo(task["id"], root)
        repositories[task["id"]] = _commit_fixture(root)
    assignments = make_plan(tasks, repeats, seed)
    plan = {
        "version": VERSION,
        "created_at": legacy.utc_now(),
        "tasks": tasks,
        "assignments": assignments,
        "repositories": repositories,
        "public_prompt_sha256": {
            task["id"]: common.digest(task_prompt(task).encode()) for task in tasks
        },
        "settings": {
            "model": model,
            "effort": effort,
            "service_tier": "default",
            "repeats": repeats,
            "seed": seed,
            "timeout_seconds": 180,
            "context_max_bytes": 12_000,
            "automatic_max_added_tokens": 4_000,
            "experimental_excerpts": False,
            "memory": False,
            "mcp_servers": 0,
            "selection_model_calls": 0,
            "codex_version": "0.159.2",
        },
        "budget_estimate": budget_estimate(len(assignments)),
        "frozen_manifest": frozen_manifest(),
        "limitations": LIMITS,
        "native_execution_approved": False,
    }
    common.atomic_json(output / "preregistration.json", plan, immutable=True)
    (output / "preregistration.sha256").write_text(
        common.digest((output / "preregistration.json").read_bytes()) + "\n"
    )
    return plan


def read_plan(directory: Path) -> dict[str, Any]:
    file = directory / "preregistration.json"
    if file.is_symlink() or not file.is_file():
        raise ValueError("Expected a regular frozen preregistration file")
    if (
        common.digest(file.read_bytes())
        != (directory / "preregistration.sha256").read_text().strip()
    ):
        raise ValueError("Frozen preregistration hash changed")
    plan = json.loads(file.read_text())
    if plan.get("version") != VERSION or plan["frozen_manifest"] != frozen_manifest():
        raise ValueError("Preregistered source, grading, pricing or Git HEAD changed")
    if plan["tasks"] != load_tasks():
        raise ValueError("Preregistered task definitions changed")
    if plan["assignments"] != make_plan(
        plan["tasks"], plan["settings"]["repeats"], plan["settings"]["seed"]
    ):
        raise ValueError("Preregistered assignment identity/order changed")
    durable.verify_repositories(plan["repositories"])
    return plan


def prepare(
    arm: str, prompt: str, task: dict[str, Any], setup: dict[str, Any], artifacts: Path
) -> dict[str, Any]:
    if arm == "A":
        return {
            "prompt": prompt,
            "mode": "passthrough",
            "reason": "bare_baseline",
            "files": [],
            "context_bytes": 0,
        }
    if arm == "B":
        from memglide.integrations.preload import prepare_prompt

        return prepare_prompt(
            prompt,
            project_id=setup["project_id"],
            db_path=artifacts / "memglide.db",
            focus_paths=task["known_paths"],
            max_context_bytes=12_000,
            context_format="compact-prefix",
        )
    if task["prompt"] not in prompt:
        raise ValueError("Automatic public task query must be present verbatim in shared prompt")
    from memglide.integrations.auto_preload import prepare_task_prompt

    # No task object or author-known path crosses this production API boundary.
    return prepare_task_prompt(
        prompt,
        task_query=task["prompt"],
        project_id=setup["project_id"],
        db_path=artifacts / "memglide.db",
        enabled=True,
        max_context_bytes=12_000,
        max_added_tokens=4_000,
        context_format="compact-prefix",
    )


def _load_preparers() -> None:
    """Shared imports occur outside observed per-task API preparation time."""
    for module in (
        "memglide.core.indexer",
        "memglide.storage.database",
        "memglide.integrations.preload",
        "memglide.integrations.auto_preload",
    ):
        importlib.import_module(module)


def verify_delivery(
    preparation: dict[str, Any], prompt: str, repository: dict[str, str]
) -> dict[str, Any]:
    """Independently compare delivered complete bytes with the frozen starting Git tree."""
    from memglide.integrations.codex_preload import _validate_compact_prefix

    files = preparation.get("files", [])
    actual = preparation.get("prompt")
    if not isinstance(actual, str) or not isinstance(files, list):
        raise ValueError("Preparation lacks valid prompt/files")
    if preparation.get("mode") == "passthrough":
        if actual != prompt or files or preparation.get("context_bytes") != 0:
            raise ValueError("Passthrough modified task or attached partial evidence")
        return {"valid": True, "mode": "passthrough", "complete_source_files": 0}
    if preparation.get("mode") != "preloaded":
        raise ValueError("Unknown preparation treatment")
    _validate_compact_prefix(actual, prompt, files)
    envelope = json.loads(actual[: -len("\n\nTask:\n" + prompt)])
    for metadata, delivered in zip(files, envelope["memglide_sources"], strict=True):
        path = metadata.get("path")
        if not _safe_relative(path):
            raise ValueError("Unsafe selected source path")
        source = subprocess.check_output(
            ["git", "show", repository["commit"] + ":" + path], cwd=repository["path"]
        )
        if delivered["content"].encode() != source or metadata.get("sha256") != common.digest(
            source
        ):
            raise ValueError("Delivered source differs from frozen complete source")
    if len(actual.encode()) - len(prompt.encode()) != preparation.get("context_bytes"):
        raise ValueError("Preparation added-byte accounting differs from actual stdin")
    return {"valid": True, "mode": "preloaded", "complete_source_files": len(files)}


def offline(plan: dict[str, Any], output: Path) -> dict[str, Any]:
    """No native execution; compare private expected scope only after preparation."""
    output.mkdir(parents=True, exist_ok=False)
    _load_preparers()
    rows = []
    for task in plan["tasks"]:
        for arm in ("B", "C"):
            artifacts = output / "runs" / f"{task['id']}-{arm}"
            artifacts.mkdir(parents=True)
            root = output / "worktrees" / f"{task['id']}-{arm}"
            repository = plan["repositories"][task["id"]]
            legacy.create_worktree(repository, root)
            prompt = task_prompt(task)
            started, cpu = time.perf_counter(), time.process_time()
            setup = common.prepare_project(root, artifacts)
            prepared = prepare(arm, prompt, task, setup, artifacts)
            elapsed, cpu_elapsed = time.perf_counter() - started, time.process_time() - cpu
            fidelity = verify_delivery(prepared, prompt, repository)
            # Private expected paths are not consulted until discovery is finished.
            selected = [item["path"] for item in prepared.get("files", [])]
            expected = set(task["known_paths"])
            row = {
                "task_id": task["id"],
                "repository": task["repository"],
                "language": task["language"],
                "configuration": arm,
                "setup": setup,
                "context_preparation": {
                    key: value for key, value in prepared.items() if key != "prompt"
                },
                "treatment_fidelity": fidelity,
                "selected_paths": selected,
                "expected_paths_evaluator_only": sorted(expected),
                "declared_scope_recall_proxy": len(expected & set(selected)) / len(expected),
                "declared_scope_complete_proxy": expected <= set(selected),
                "selected_files_outside_author_scope": sorted(set(selected) - expected),
                "cold_setup_and_preparation_seconds": elapsed,
                "cold_setup_and_preparation_parent_cpu_seconds": cpu_elapsed,
                "prompt_sha256": common.digest(prepared["prompt"].encode()),
                "native_model_calls": 0,
                "native_coding_success": None,
                "actual_billed_cost_usd": None,
                "model_input_tokens": None,
            }
            common.atomic_json(artifacts / "result.json", row, immutable=True)
            rows.append(row)
    report: dict[str, Any] = {
        "version": VERSION,
        "kind": "Offline source-selection and full-source-fidelity probe; no coding model",
        "rows": rows,
        "summary": {
            arm: {
                "tasks": sum(row["configuration"] == arm for row in rows),
                "complete_declared_scope_count": sum(
                    row["declared_scope_complete_proxy"]
                    for row in rows
                    if row["configuration"] == arm
                ),
                "declared_scope_recall_proxy": common.summarize(
                    [
                        row["declared_scope_recall_proxy"]
                        for row in rows
                        if row["configuration"] == arm
                    ],
                    additive=False,
                ),
                "cold_setup_and_preparation_seconds": common.summarize(
                    [
                        row["cold_setup_and_preparation_seconds"]
                        for row in rows
                        if row["configuration"] == arm
                    ]
                ),
                "added_bytes": common.summarize(
                    [
                        row["context_preparation"]["context_bytes"]
                        for row in rows
                        if row["configuration"] == arm
                    ]
                ),
                "decisions": dict(
                    Counter(
                        row["context_preparation"]
                        .get("automatic_selection", {})
                        .get("decision", row["context_preparation"]["mode"])
                        for row in rows
                        if row["configuration"] == arm
                    )
                ),
            }
            for arm in ("B", "C")
        },
        "model_requests": 0,
        "strict_native_success_rate": None,
        "estimated_model_cost_per_success": None,
        "actual_billed_cost_usd": None,
        "limitations": LIMITS,
    }
    common.atomic_json(output / "report.json", report, immutable=True)
    (output / "report.md").write_text(
        "# Offline automatic source-selection probe\n\nNo model requests were made. Target coverage is a proxy; coding correctness, tokens and cost are unmeasured.\n\n"
        + "| Arm | Tasks | Complete author scope | Mean cold preparation seconds | Mean added bytes |\n|---|---:|---:|---:|---:|\n"
        + "\n".join(
            f"| {arm} | {value['tasks']} | {value['complete_declared_scope_count']} | {value['cold_setup_and_preparation_seconds']['mean']} | {value['added_bytes']['mean']} |"
            for arm, value in report["summary"].items()
        )
        + "\n\n"
        + "\n".join("- " + item for item in LIMITS)
        + "\n"
    )
    return report


def paired_effects(
    rows: list[dict[str, Any]], metric: str, candidate: str, baseline: str, *, seed: int = 20261019
) -> dict[str, Any]:
    """Cluster bootstrap resamples tasks, retaining their repeated paired effects."""
    indexed = {(row["task_id"], row["repeat"], row["configuration"]): row for row in rows}
    clusters: defaultdict[str, list[float]] = defaultdict(list)
    excluded = []
    for task, repeat in sorted({(row["task_id"], row["repeat"]) for row in rows}):
        a, b = indexed.get((task, repeat, baseline)), indexed.get((task, repeat, candidate))
        left, right = (a or {}).get(metric), (b or {}).get(metric)
        if not _number(left) or not _number(right):
            excluded.append(
                {"task_id": task, "repeat": repeat, "reason": "Missing observed pair metric"}
            )
            continue
        clusters[task].append(float(right) - float(left))
    values = [value for members in clusters.values() for value in members]
    samples = []
    median_samples = []
    if len(clusters) > 1:
        generator = random.Random(seed)
        names = sorted(clusters)
        for _ in range(2_000):
            drawn = [value for _ in names for value in clusters[generator.choice(names)]]
            samples.append(statistics.mean(drawn))
            median_samples.append(statistics.median(drawn))
        samples.sort()
        median_samples.sort()
    return {
        "candidate": candidate,
        "baseline": baseline,
        "metric": metric,
        "paired_observations": len(values),
        "independent_task_clusters": len(clusters),
        "mean_paired_difference": statistics.mean(values) if values else None,
        "median_paired_difference": statistics.median(values) if values else None,
        "per_task_differences": dict(clusters),
        "mean_difference_task_cluster_bootstrap_95_percent_interval": [samples[49], samples[1949]]
        if samples
        else None,
        "median_difference_task_cluster_bootstrap_95_percent_interval": [
            median_samples[49],
            median_samples[1949],
        ]
        if median_samples
        else None,
        "bootstrap_replicates": 2_000 if samples else 0,
        "excluded_pairs": excluded,
        "interpretation": "Exploratory finite-corpus uncertainty; task clusters are not a random sample of all repositories.",
    }


def validate_approval(plan: dict[str, Any], amount: float | None, reference: str | None) -> None:
    required = plan["budget_estimate"]["estimated_campaign_high_usd"]
    if not _number(amount) or amount < required:
        raise ValueError(
            f"Explicit newly approved estimated budget of at least USD {required} is required"
        )
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError(
            "Record the user's new approval reference; existing historical authorization is insufficient"
        )


def _number(value: Any) -> TypeGuard[int | float]:
    return type(value) in (float, int) and math.isfinite(value)


def _attempt(
    row: dict[str, Any], task: dict[str, Any], plan: dict[str, Any], output: Path, executable: str
) -> dict[str, Any]:
    artifacts = output / "runs" / row["run_id"]
    artifacts.mkdir(parents=True)
    root = output / "worktrees" / row["run_id"]
    result = {
        **row,
        "status": "running",
        "attempted": True,
        "strict_success": False,
        "artifacts": str(artifacts),
        "actual_billed_cost_usd": None,
        "errors": [],
    }
    common.atomic_json(artifacts / "attempt-start.json", result, immutable=True)
    durable.append_log(
        output,
        "attempt.started",
        attempt_id=row["run_id"],
        start_sha256=common.digest(common.canonical(result)),
    )
    repository = plan["repositories"][task["id"]]
    try:
        legacy.create_worktree(repository, root)
        snapshot = legacy.protection_snapshot(root)
        original = task_prompt(task)
        started, cpu = time.perf_counter(), time.process_time()
        setup = (
            common.prepare_project(root, artifacts)
            if row["configuration"] != "A"
            else {"wall_seconds": 0, "cpu_seconds": 0}
        )
        prepared = prepare(row["configuration"], original, task, setup, artifacts)
        context_done = time.perf_counter()
        # Independent reconstruction runs outside timed product preparation/native work.
        fidelity = verify_delivery(prepared, original, repository)
        audit_done = time.perf_counter()
        common.atomic_json(
            artifacts / "preparation.json",
            {key: value for key, value in prepared.items() if key != "prompt"},
            immutable=True,
        )
        command = workflow.codex_command(
            executable,
            root,
            output / "final-response-schema.json",
            artifacts / "final.json",
            plan["settings"]["model"],
            plan["settings"]["effort"],
        )
        result.update(
            common.execute_codex(
                command,
                prepared["prompt"],
                root,
                artifacts,
                plan["settings"]["timeout_seconds"],
                {**os.environ, "CI": "1", "NO_COLOR": "1"},
            )
        )
        result.update(
            full_task_seconds=time.perf_counter() - started - (audit_done - context_done),
            treatment_audit_seconds=audit_done - context_done,
            parent_cpu_seconds=time.process_time() - cpu,
            setup=setup,
            context_preparation={key: value for key, value in prepared.items() if key != "prompt"},
            treatment_fidelity=fidelity,
            common_task_prompt_sha256=common.digest(original.encode()),
            actual_prompt_sha256=common.digest(prepared["prompt"].encode()),
        )
        validity = common.native_execution_validity(result, artifacts / "final.json")
        violations = legacy.check_protection(root, snapshot, repository["commit"])
        legacy.preserve_changes(root, artifacts, repository["commit"])
        grade = corpus().grade_task(root, task["id"], artifact_dir=artifacts / "grade")
        result.update(
            native_execution_validity=validity, protected_file_violations=violations, grader=grade
        )
        result["strict_success"] = bool(
            validity["valid"]
            and fidelity["valid"]
            and not violations
            and grade.get("success", grade.get("passed")) is True
            and result["telemetry"].get("mcp_call_count") == 0
            and result["telemetry"].get("mcp_counts_complete") is True
        )
        result["status"] = "completed" if result["strict_success"] else "failed"
        result["shared_blocker"] = legacy.common_blocker(result, artifacts)
    except BaseException as error:
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            durable.stop_orphan(artifacts)
            result.update(
                status="interrupted",
                execution_outcome_unknown=True,
                shared_blocker="User or launcher interruption; originals will not be retried",
            )
        else:
            result["status"] = "harness_error"
        result["errors"].append(f"{type(error).__name__}: {error}")
    stream = artifacts / "events.jsonl"
    try:
        if stream.is_symlink() or (stream.exists() and stream.stat().st_size > 64_000_000):
            raise ValueError("Unsafe or oversized native evidence stream")
        parsed = (
            pricing.parse_native_usage(stream.read_text())
            if stream.exists()
            else {"coverage_complete": False}
        )
    except (OSError, ValueError, UnicodeError) as error:
        parsed = {"coverage_complete": False, "errors": [f"Native usage unavailable: {error}"]}
    if result.get("execution_outcome_unknown"):
        parsed["coverage_complete"] = False
        parsed["usage"] = dict.fromkeys(pricing.USAGE_KEYS)
    result["native_usage"] = parsed
    result["price_equivalent"] = pricing.price_usage(
        parsed, json.loads((ROOT / "benchmarks/cost-pricing.json").read_text())
    )
    result["estimated_api_equivalent_usd"] = result["price_equivalent"][
        "native_reported_price_equivalent_usd"
    ]
    common.atomic_json(artifacts / "result.json", result, immutable=True)
    durable.append_log(
        output,
        "attempt.finished",
        attempt_id=row["run_id"],
        result_sha256=common.digest((artifacts / "result.json").read_bytes()),
    )
    return result


def formal_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    arms = {}
    for arm in ARMS:
        members = [row for row in rows if row["configuration"] == arm]
        attempted = [row for row in members if row.get("attempted")]
        successful = sum(row.get("strict_success") is True for row in attempted)
        costs = common.summarize([row.get("estimated_api_equivalent_usd") for row in attempted])
        arms[arm] = {
            "planned": len(members),
            "attempted": len(attempted),
            "strict_successes": successful,
            "strict_success_rate_of_attempted": successful / len(attempted) if attempted else None,
            "unrun": len(members) - len(attempted),
            "statuses": dict(Counter(row["status"] for row in members)),
            "full_task_seconds": common.summarize(
                [row.get("full_task_seconds") for row in attempted]
            ),
            "estimated_api_equivalent_usd": costs,
            "estimated_cost_per_strict_success_usd": costs["total"] / successful
            if costs["total"] is not None and successful
            else None,
            "actual_billed_cost_per_success_usd": None,
            "native_usage": {
                key: common.summarize(
                    [row.get("native_usage", {}).get("usage", {}).get(key) for row in attempted]
                )
                for key in pricing.USAGE_KEYS
            },
            "input_minus_cached_read_tokens": common.summarize(
                [
                    usage["input_tokens"] - usage["cached_input_tokens"]
                    if _number(usage.get("input_tokens"))
                    and _number(usage.get("cached_input_tokens"))
                    else None
                    for usage in (row.get("native_usage", {}).get("usage", {}) for row in attempted)
                ]
            ),
            "possible_write_sensitivity_cost_per_success_usd": {
                bound: total / successful
                if (
                    total := common.summarize(
                        [row.get("price_equivalent", {}).get(bound) for row in attempted]
                    )["total"]
                )
                is not None
                and successful
                else None
                for bound in ("possible_write_price_lower_usd", "possible_write_price_upper_usd")
            },
            "local_resources": {
                metric: common.summarize([row.get("overhead", {}).get(metric) for row in attempted])
                for metric in ("cpu_seconds", "process_tree_peak_rss_bytes")
            },
        }
    return {
        "version": VERSION,
        "runs": rows,
        "configurations": arms,
        "actual_billed_cost_usd": None,
        "paired_effects": {
            f"{candidate}_vs_{base}": {
                metric: paired_effects(rows, metric, candidate, base)
                for metric in ("full_task_seconds", "estimated_api_equivalent_usd")
            }
            for candidate, base in (("B", "A"), ("C", "A"), ("C", "B"))
        },
        "limitations": LIMITS,
    }


def execute(
    plan_directory: Path,
    output: Path,
    *,
    approved_estimated_budget_usd: float | None,
    authorization_reference: str | None,
    codex: str,
) -> dict[str, Any]:
    plan = read_plan(plan_directory)
    validate_approval(plan, approved_estimated_budget_usd, authorization_reference)
    executable = shutil.which(codex)
    if not executable:
        raise ValueError("Approved execution requires an installed native Codex executable")
    native_version = subprocess.check_output([executable, "--version"], text=True).strip()
    if native_version.removeprefix("codex-cli ") != plan["settings"]["codex_version"]:
        raise ValueError("Native executable version differs from preregistered configuration")
    output.mkdir(parents=True, exist_ok=False)
    _load_preparers()
    common.atomic_json(
        output / "approval.json",
        {
            "approved_estimated_budget_usd": approved_estimated_budget_usd,
            "authorization_reference": authorization_reference,
            "native_version": native_version,
            "plan_sha256": common.digest((plan_directory / "preregistration.json").read_bytes()),
            "hard_cap_available": False,
        },
        immutable=True,
    )
    common.atomic_json(output / "final-response-schema.json", legacy.OUTPUT_SCHEMA, immutable=True)
    rows = []
    tasks = {task["id"]: task for task in plan["tasks"]}
    blocker = None
    spent_upper = 0.0
    for assignment in plan["assignments"]:
        if not blocker:
            try:
                read_plan(plan_directory)
            except ValueError as error:
                blocker = str(error)
        if (
            not blocker
            and spent_upper + plan["budget_estimate"]["planning_high_per_assignment_usd"]
            > approved_estimated_budget_usd
        ):
            blocker = "Estimated API-equivalent allowance exhausted; no new original dispatched"
        if blocker:
            rows.append(
                {
                    **assignment,
                    "status": "not_run",
                    "attempted": False,
                    "strict_success": False,
                    "reason": blocker,
                }
            )
            continue
        row = _attempt(assignment, tasks[assignment["task_id"]], plan, output, executable)
        rows.append(row)
        upper = row["price_equivalent"]["possible_write_price_upper_usd"]
        if upper is None:
            blocker = "Unknown whole-attempt cost; cannot continue estimated-budget accounting"
        else:
            spent_upper += upper
        blocker = row.get("shared_blocker") or blocker
        try:
            read_plan(plan_directory)
        except ValueError as error:
            blocker = str(error)
    report = formal_report(rows)
    report.update(
        native_version=native_version,
        estimated_allowance_stop_reason=blocker,
        no_resume_or_retry=True,
    )
    common.atomic_json(output / "report.json", report, immutable=True)
    (output / "report.md").write_text(
        "# Automatic context formal comparison\n\nAll original assignments, including failures and unrun rows, are retained in report.json. Dollar figures are API-price equivalents; actual billing is unavailable.\n\n| Arm | Attempted | Strict successes | Estimated USD per strict success | Mean full seconds |\n|---|---:|---:|---:|---:|\n"
        + "\n".join(
            f"| {arm} | {value['attempted']} | {value['strict_successes']} | {value['estimated_cost_per_strict_success_usd']} | {value['full_task_seconds']['mean']} |"
            for arm, value in report["configurations"].items()
        )
        + "\n"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("plan", "offline", "execute"), nargs="?", default="plan"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--effort", default="low")
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--approved-estimated-budget-usd", type=float)
    parser.add_argument("--authorization-reference")
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("repeats must be positive")
    if args.command != "plan" and args.plan is None:
        parser.error("offline/execute requires --plan")
    try:
        if args.command == "plan":
            value = create_plan(
                args.output.resolve(),
                repeats=args.repeats,
                seed=args.seed,
                model=args.model,
                effort=args.effort,
            )
            print(
                json.dumps(
                    {
                        "planned_assignments": len(value["assignments"]),
                        "budget_estimate": value["budget_estimate"],
                        "model_requests": 0,
                    }
                )
            )
        elif args.command == "offline":
            value = offline(read_plan(args.plan.resolve()), args.output.resolve())
            print(json.dumps({"model_requests": 0, "summary": value["summary"]}))
        else:
            value = execute(
                args.plan.resolve(),
                args.output.resolve(),
                approved_estimated_budget_usd=args.approved_estimated_budget_usd,
                authorization_reference=args.authorization_reference,
                codex=args.codex,
            )
            print(json.dumps({"configurations": value["configurations"]}))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(2, str(error) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
