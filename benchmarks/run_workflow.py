"""Fresh three-arm workflow study: bare Codex, source preload, source plus support.

Importing this module starts no requests. Raw supported native JSON telemetry is
kept independently of a separately labelled price-equivalent cost assessment.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import random
import shutil
import subprocess
import time
import uuid
from collections import Counter
from itertools import permutations
from pathlib import Path, PurePosixPath
from typing import Any

from benchmarks import run as legacy
from benchmarks import run_cache_formats as formats
from benchmarks import run_cost as cost
from benchmarks import run_daily as common
from benchmarks import run_v2 as durable
from benchmarks.compare_components import capture_provenance

ROOT = common.ROOT
LABELS = {"A": "Standard Codex", "B": "Memglide source-only", "C": "Memglide source plus support"}
ARMS = tuple(LABELS)


def codex_command(
    executable: str, worktree: Path, schema: Path, final: Path, model: str, effort: str
) -> list[str]:
    """Codex 0.159.2 Config.service_tier supports explicit standard routing."""
    native = common.codex_command(executable, worktree, schema, final, model, effort)
    return native[:-1] + ["-c", 'service_tier="default"', "-"]


def corpus_module() -> Any:
    return importlib.import_module("benchmarks.corpus_workflow")


def task_prompt(task: dict[str, Any]) -> str:
    return (
        common.COMMON_INSTRUCTIONS
        + "\nTask:\n"
        + task["prompt"]
        + "\n\nCaller-declared source scope (available equally to all configurations):\n"
        + "\n".join("- " + path for path in task["focus_paths"])
        + "\nCaller-declared supporting tests (available equally to all configurations):\n"
        + "\n".join("- " + path for path in task["support_paths"])
        + "\nRelevant test command argv (run from repository root):\n"
        + json.dumps(task["test_argv"], ensure_ascii=False)
        + "\n"
    )


def load_tasks(path: Path) -> list[dict[str, Any]]:
    tasks = legacy.load_tasks(path)
    repositories = corpus_module().REPOSITORIES
    for task in tasks:
        identifier = task.get("repository")
        if identifier not in repositories or repositories[identifier][0] != task["language"]:
            raise ValueError("Unknown or language-mismatched workflow-comparison repository")
        if not isinstance(task.get("prompt"), str) or not task["prompt"].strip():
            raise ValueError("Task prompt must not be empty")
        for field in ("focus_paths", "support_paths"):
            paths = task.get(field)
            if (
                not isinstance(paths, list)
                or not paths
                or any(
                    not isinstance(path, str)
                    or not path
                    or "\x00" in path
                    or "\\" in path
                    or PurePosixPath(path).is_absolute()
                    or ".." in PurePosixPath(path).parts
                    or PurePosixPath(path).as_posix() != path
                    for path in paths
                )
                or len(set(paths)) != len(paths)
            ):
                raise ValueError(
                    "Source/support scope must contain unique canonical relative paths"
                )
        if set(task["focus_paths"]) & set(task["support_paths"]):
            raise ValueError("Source and support scope must be disjoint")
        if (
            not isinstance(task.get("test_argv"), list)
            or not task["test_argv"]
            or any(
                not isinstance(arg, str) or not arg or "\x00" in arg for arg in task["test_argv"]
            )
        ):
            raise ValueError("Test command argv must contain nonempty string arguments")
        if type(task.get("context_supplied")) is not bool:
            raise ValueError("context_supplied must be an explicit boolean")
    return tasks


def make_plan(tasks: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    """Reverse each task's order on repeat two; balance pairwise precedence exactly."""
    generator = random.Random(seed)
    shuffled = list(tasks)
    generator.shuffle(shuffled)
    orders = list(permutations(ARMS))
    generator.shuffle(orders)
    first_orders = {task["id"]: orders[index % len(orders)] for index, task in enumerate(shuffled)}
    plan: list[dict[str, Any]] = []
    for repeat in range(1, repeats + 1):
        for task in shuffled:
            order = first_orders[task["id"]]
            if repeat % 2 == 0:
                order = tuple(reversed(order))
            for arm in order:
                plan.append(
                    {
                        "run_id": f"workflow-{task['id']}-r{repeat}-{arm}",
                        "task_id": task["id"],
                        "language": task["language"],
                        "repository": task["repository"],
                        "task_kind": task.get("task_kind", "unspecified"),
                        "selection_stratum": "caller_context_supplied"
                        if task["context_supplied"]
                        else "explicit_focus",
                        "configuration": arm,
                        "repeat": repeat,
                        "order": len(plan) + 1,
                        "context_format": None if arm == "A" else "compact-prefix",
                        "support_enabled": arm == "C",
                    }
                )
    return plan


def frozen_manifest(
    tasks_path: Path, tasks: list[dict[str, Any]], settings: dict[str, Any]
) -> dict[str, Any]:
    value = common.frozen_manifest(tasks_path, tasks, settings)
    for name in (
        "benchmarks/run_workflow.py",
        "benchmarks/run_cost.py",
        "benchmarks/run_cache_formats.py",
        "benchmarks/corpus.py",
        "benchmarks/corpus_workflow.py",
        "benchmarks/corpus_cost.py",
        "benchmarks/cost-pricing.json",
        "benchmarks/estimate_cost.py",
        "benchmarks/workflow_cost.py",
        "benchmarks/workflow-protocol.md",
    ):
        path = ROOT / name
        if path.is_symlink():
            raise ValueError("Frozen runner/grader cannot be a symlink")
        value["files"][name] = common.digest(path.read_bytes())
    value["common_task_prompt_sha256"] = {
        task["id"]: common.digest(task_prompt(task).encode()) for task in tasks
    }
    return value


def create_repositories(
    output: Path, tasks: list[dict[str, Any]], existing: dict[str, Any], persist: Any
) -> dict[str, Any]:
    repositories = dict(existing)
    for identifier in sorted({task["repository"] for task in tasks}):
        if identifier in repositories:
            continue
        destination = output / "repositories" / identifier
        if destination.exists():
            retained = output / "initialization-partials" / f"{identifier}-{uuid.uuid4().hex}"
            retained.parent.mkdir(parents=True, exist_ok=True)
            destination.rename(retained)
        destination.mkdir(parents=True)
        corpus_module().build_repository(identifier, destination)
        legacy.git(destination, "init", "--initial-branch=benchmark")
        legacy.git(destination, "config", "user.name", "Memglide Cost Benchmark Fixture")
        legacy.git(destination, "config", "user.email", "benchmark@example.invalid")
        legacy.git(destination, "add", ".")
        legacy.git(
            destination, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Frozen workflow fixture"
        )
        repositories[identifier] = {
            "path": str(destination),
            "commit": legacy.git(destination, "rev-parse", "HEAD"),
            "tree": legacy.git(destination, "rev-parse", "HEAD^{tree}"),
        }
        persist(repositories)
    return repositories


def preload_command(
    native: list[str], artifacts: Path, task: dict[str, Any], project_id: str | None, arm: str
) -> list[str]:
    command = formats.preload_command(native, artifacts, task, "compact-prefix", project_id)
    if arm == "C":
        boundary = command.index("--")
        support = [part for path in task["support_paths"] for part in ("--support", path)]
        command[boundary - 1 : boundary - 1] = support
    return command


def preload_fidelity(
    result: dict[str, Any], task: dict[str, Any], prompt: str, repository: dict[str, str]
) -> dict[str, Any]:
    """Reconstruct each complete source from frozen Git, independently of production API."""
    if result.get("execution_outcome_unknown"):
        return {
            "valid": None,
            "reason": "Interrupted original delivery outcome is unknown",
            "context_format": "compact-prefix",
        }
    try:
        report = json.loads((Path(result["artifacts"]) / "preparation.json").read_text())
        preparation, stdin = report["preparation"], report["native_stdin"]
        support = sorted(task["support_paths"]) if result["configuration"] == "C" else []
        focus = sorted(task["focus_paths"])
        expected_paths = sorted(set(focus + support))
        reasons = []
        if type(report.get("version")) is not int or report["version"] != (3 if support else 2):
            reasons.append("Preparation report version differs from assigned support treatment")
        if preparation.get("context_format") != "compact-prefix":
            reasons.append("Compact format identity is missing")
        if support:
            if (
                preparation.get("focus_paths") != focus
                or preparation.get("support_paths") != support
            ):
                reasons.append("Focus/support classification differs from exact caller scope")
        elif "support_paths" in preparation or "focus_paths" in preparation:
            reasons.append("Source-only treatment unexpectedly adds support classification")
        if preparation.get("task_prompt_sha256") != common.digest(prompt.encode()):
            reasons.append("Common task prompt hash differs")
        native = result["native_command"]
        if report["exec_argv"] != [*native[:-1], "--", "-"] or report["executable"] != native[0]:
            reasons.append("Native forwarded settings differ from frozen command")
        telemetry = result.get("telemetry", {})
        if telemetry.get("mcp_counts_complete") is not True or telemetry.get("mcp_call_count") != 0:
            reasons.append("Complete MCP-free native stream is absent")
        mode, files = preparation["mode"], preparation["files"]
        if mode == "passthrough":
            prepared = prompt
            if not task["context_supplied"]:
                reasons.append("Focused treatment did not preload complete assigned files")
            if files or preparation.get("context_bytes") != 0:
                reasons.append("Passthrough claims added source")
            if task["context_supplied"] and preparation.get("reason") != "context_supplied":
                reasons.append("Caller-context bypass reason differs")
            if preparation.get("prompt_layout") != "unchanged":
                reasons.append("Passthrough layout differs")
        elif mode == "preloaded":
            if task["context_supplied"]:
                reasons.append("Source unexpectedly added to supplied-context control")
            sources = []
            for relative in expected_paths:
                data = subprocess.check_output(
                    ["git", "-C", repository["path"], "show", repository["commit"] + ":" + relative]
                )
                content = data.decode("utf-8")
                sources.append(
                    {
                        "path": relative,
                        "sha256": common.digest(data),
                        "start_line": 1,
                        "end_line": len(content.splitlines()),
                        "content": content,
                    }
                )
            expected_metadata = [
                {key: item[key] for key in ("path", "sha256", "start_line", "end_line")}
                for item in sources
            ]
            if files != expected_metadata or any(
                type(item.get("start_line")) is not int or type(item.get("end_line")) is not int
                for item in files
            ):
                reasons.append(
                    "Complete-source provenance differs from independent frozen Git bytes"
                )
            prepared = formats.reconstruct_prompt(prompt, sources, "compact-prefix")
            if preparation.get("prompt_layout") != "source_prefix":
                reasons.append("Compact source-prefix layout identity differs")
        else:
            raise ValueError("Unknown preparation mode")
        context_bytes = len(prepared.encode()) - len(prompt.encode())
        prepared_hash = common.digest(prepared.encode())
        if (
            type(preparation.get("context_bytes")) is not int
            or not 0 <= context_bytes <= 12000
            or preparation["context_bytes"] != context_bytes
        ):
            reasons.append("Added context differs from bounded independent reconstruction")
        if (
            preparation.get("prepared_prompt_sha256") != prepared_hash
            or stdin.get("sha256") != prepared_hash
        ):
            reasons.append("Native stdin hash differs from independent reconstruction")
        if (
            type(stdin.get("bytes")) is not int
            or stdin["bytes"] != len(prepared.encode())
            or stdin.get("transport") != "temporary_file_descriptor"
        ):
            reasons.append("Native stdin size/transport differs")
        command = json.loads((Path(result["artifacts"]) / "command.json").read_text())
        expected_command = preload_command(
            native,
            Path(result["artifacts"]),
            task,
            result.get("setup", {}).get("project_id"),
            result["configuration"],
        )
        if command != expected_command:
            reasons.append(
                "Recorded launcher command differs from assigned focus/support treatment"
            )
        return {
            "valid": not reasons,
            "reason": "; ".join(reasons)
            if reasons
            else "Independent frozen Git complete-source reconstruction matches launcher stdin and native options",
            "context_format": "compact-prefix",
            "mode": mode,
            "selection_reason": preparation.get("reason"),
            "preparation": preparation,
            "source_file_count": len(files),
            "source_hashes": {item["path"]: item["sha256"] for item in files},
            "context_bytes": context_bytes,
            "actual_model_prompt_sha256": prepared_hash,
            "common_task_prompt_sha256": common.digest(prompt.encode()),
            "native_exec_boundary_monotonic_seconds": report.get(
                "native_exec_boundary_monotonic_seconds"
            ),
        }
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        return {
            "valid": False,
            "reason": "Invalid workflow delivery evidence: " + type(error).__name__,
            "context_format": "compact-prefix",
        }


def treatment_fidelity(
    result: dict[str, Any], task: dict[str, Any], prompt: str, repository: dict[str, str]
) -> dict[str, Any]:
    if result["configuration"] == "A":
        return cost.treatment_fidelity(result, task, prompt, repository)
    return preload_fidelity(result, task, prompt, repository)


def begin_attempt(
    output: Path,
    row: dict[str, Any],
    task: dict[str, Any],
    state: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Seal unknown cold B/C indexing before setup, including crash recovery."""
    no_index = row["configuration"] == "A" or task["context_supplied"] or not task["focus_paths"]
    seeded = {
        **row,
        "setup": {
            "wall_seconds": 0 if no_index else None,
            "cpu_seconds": 0 if no_index else None,
        },
        "preload_treatment_fidelity": {
            "valid": None,
            "reason": "No durable completion of this assignment yet",
            "context_format": row["context_format"],
        },
        "native_execution_validity": {
            "valid": None,
            "reasons": ["Native completion not yet durably observed"],
        },
    }
    return common.begin_attempt(output, seeded, state, metadata)


def run_attempt(
    attempt: dict[str, Any],
    task: dict[str, Any],
    repository: dict[str, str],
    output: Path,
    arguments: argparse.Namespace,
    environment: dict[str, str],
) -> dict[str, Any]:
    result = {**attempt, "errors": list(attempt["errors"])}
    artifacts, worktree = Path(attempt["artifacts"]), Path(attempt["worktree"])
    prompt = task_prompt(task)
    result.update(
        starting_commit=repository["commit"],
        common_task_prompt_sha256=common.digest(prompt.encode()),
        actual_model_prompt_sha256=None,
        configuration_label=LABELS[attempt["configuration"]],
    )
    try:
        legacy.create_worktree(repository, worktree)
        snapshot = legacy.protection_snapshot(worktree)
        started = time.monotonic()
        if (
            attempt["configuration"] in {"B", "C"}
            and not task["context_supplied"]
            and task["focus_paths"]
        ):
            result["setup"] = common.prepare_project(worktree, artifacts)
        native = codex_command(
            arguments.codex,
            worktree,
            output / "final-response-schema.json",
            artifacts / "final.json",
            arguments.model,
            arguments.effort,
        )
        result["native_command"] = native
        command = (
            preload_command(
                native, artifacts, task, result["setup"].get("project_id"), attempt["configuration"]
            )
            if attempt["configuration"] in {"B", "C"}
            else native
        )
        result.update(
            common.execute_codex(
                command, prompt, worktree, artifacts, arguments.timeout, environment
            )
        )
        result["end_to_end_wall_seconds"] = time.monotonic() - started
        result["native_execution_validity"] = common.native_execution_validity(
            result, artifacts / "final.json"
        )
        fidelity = treatment_fidelity(result, task, prompt, repository)
        result["preload_treatment_fidelity"] = fidelity
        result["treatment_valid"] = fidelity["valid"]
        result["actual_model_prompt_sha256"] = fidelity.get("actual_model_prompt_sha256")
        boundary = fidelity.get("native_exec_boundary_monotonic_seconds")
        result["native_exec_wall_seconds"] = (
            result["process_finished_monotonic_seconds"] - boundary
            if common._number(boundary)
            and result["process_started_monotonic_seconds"]
            <= boundary
            <= result["process_finished_monotonic_seconds"]
            else None
        )
        result["native_exec_timing_scope"] = (
            "B/C launcher boundary before report-write/exec handoff through native exit; A has no launcher boundary"
        )
        violations = legacy.check_protection(worktree, snapshot, repository["commit"])
        result["protected_file_violations"] = violations
        legacy.preserve_changes(worktree, artifacts, repository["commit"])
        result["grader"] = corpus_module().grade(task["id"], worktree, artifacts)
        if violations:
            result["grader"]["success"] = False
            result["errors"].append("Protected repository tests or Git metadata changed")
        if result["timed_out"]:
            result["status"] = "timeout"
        elif result["native_execution_validity"]["valid"] is not True:
            result["status"] = "execution_failed"
            result["errors"].extend(result["native_execution_validity"]["reasons"])
        elif fidelity["valid"] is not True:
            result["status"] = "invalid_treatment"
            result["errors"].append(fidelity["reason"])
        elif result["grader"].get("success") is not True:
            result["status"] = "failed"
        else:
            result["status"] = "completed"
        result["common_blocker"] = legacy.common_blocker(result, artifacts)
    except Exception as error:
        result["status"] = "harness_error"
        result["errors"].append(f"{type(error).__name__}: {error}")
    result["finished_at"] = legacy.utc_now()
    common.atomic_json(artifacts / "result.json", result, immutable=True)
    return result


def build_report(
    rows: list[dict[str, Any]], tasks: list[dict[str, Any]], metadata: dict[str, Any]
) -> dict[str, Any]:
    configurations = {
        arm: common.aggregate([row for row in rows if row["configuration"] == arm]) for arm in ARMS
    }
    comparisons = {}
    for numerator, denominator in (("C", "A"), ("C", "B"), ("B", "A")):
        projected = [
            {**row, "configuration": "A" if row["configuration"] == denominator else "B"}
            for row in rows
            if row["configuration"] in {numerator, denominator}
        ]
        pair_report = common.build_report(projected, tasks, metadata)
        comparisons[numerator + "_over_" + denominator] = {
            "numerator": numerator,
            "denominator": denominator,
            "comparison": pair_report["comparison"],
            "paired_comparison": pair_report["paired_comparison"],
        }
    plan = sorted(rows, key=lambda row: row["order"])
    triplets = [
        "".join(row["configuration"] for row in plan[index : index + 3])
        for index in range(0, len(plan), 3)
    ]
    return {
        "report_version": "workflow-1",
        "generated_at": legacy.utc_now(),
        "metadata": metadata,
        "tasks": tasks,
        "configuration_labels": LABELS,
        "comparison_kind": "Three-arm workflow comparison: standard/source-only/source-plus-support",
        "configurations": configurations,
        "comparisons": comparisons,
        "permutation_counts": dict(Counter(triplets)),
        "strata": {
            stratum: {
                arm: common.aggregate(
                    [
                        row
                        for row in rows
                        if row["configuration"] == arm and row.get("selection_stratum") == stratum
                    ]
                )
                for arm in ARMS
            }
            for stratum in sorted({row.get("selection_stratum", "unknown") for row in rows})
        },
        "runs": [{**row, "metrics": common.metrics(row)} for row in rows],
        "failures": [row for row in rows if row.get("status") != "completed"],
        "limitations": [
            "All original assignments, failures and unknown interruptions are retained; no automatic retries. Successful completion requires external behavior grade, treatment and native schema validity.",
            "A is direct standard Codex. B adds complete caller-selected production files. C adds those files plus complete caller-selected supporting tests. All arms receive identical common prompts, path hints and test argv. No auxiliary model or configured MCP is used.",
            "Ten fresh purpose-built tasks, five Python/five TypeScript, are repeated twice in isolated worktrees/native state/databases. Repeat two reverses each task's arm order; pairwise precedence is balanced but provider and operating-system caches are uncontrolled.",
            "Source hashes attest complete current selected files at preparation, not semantic completeness or later edits. Supporting tests are task-author-selected and equally disclosed to every arm; this is not autonomous repository discovery or cross-session memory.",
            "Full time includes cold approval/index and launcher/native work, excluding worktree construction and grading. CPU is a local observed lower bound; child RSS excludes parent indexing, may miss short-lived children and double-count shared pages.",
            "Actual cost, model calls and filesystem reads remain unavailable. Cached input is included within total input. Separately labelled price-equivalent estimates must include failed attempts and exclude unknown usage from zero-cost assumptions.",
            "Paired comparisons require matching commits/common prompts, valid treatment, valid native completion and unchanged frozen source; primary intent-to-treat per-arm aggregates retain all originals regardless of pair eligibility.",
        ],
    }


def write_report(report: dict[str, Any], output: Path) -> None:
    common.atomic_json(output / "report.json", report)

    def value(item: Any) -> str:
        return (
            "unavailable"
            if item is None
            else f"{item:.6f}"
            if isinstance(item, float)
            else str(item)
        )

    lines = [
        "# Fresh three-arm workflow comparison",
        "",
        "A = standard Codex; B = Memglide source-only; C = Memglide source plus supporting tests.",
        "Actual costs unavailable; price-equivalent estimates are separately labelled.",
        "",
        "| Arm | Planned | Attempted | Successful | Failed grades | Completion rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm, summary in report["configurations"].items():
        lines.append(
            "| "
            + arm
            + " | "
            + " | ".join(
                value(summary[key])
                for key in (
                    "planned_runs",
                    "attempted_runs",
                    "successful_runs",
                    "failed_grades",
                    "successful_task_completion_rate",
                )
            )
            + " |"
        )
    lines += [
        "",
        "## Measurements",
        "",
        "Totals are unavailable when any attempted observation is unknown; RSS is non-additive.",
        "",
        "| Metric | Arm | Mean | Median | p95 | Total | Observed |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for name in common.METRICS:
        for arm in ARMS:
            measurement = report["configurations"][arm]["metrics"][name]
            lines.append(
                "| "
                + name
                + " | "
                + arm
                + " | "
                + " | ".join(value(measurement[key]) for key in ("mean", "median", "p95", "total"))
                + " | "
                + str(measurement["n"])
                + " |"
            )
    for name, compared in report["comparisons"].items():
        pairs = compared["paired_comparison"]
        lines += [
            "",
            "## " + name,
            "",
            f"Verified pairs: {pairs['valid_pairs']}; excluded: {len(pairs['excluded_pairs'])}.",
            "",
            "| Metric | Overall mean ratio | Paired difference mean | Paired difference median |",
            "|---|---:|---:|---:|",
        ]
        for metric, measurement in compared["comparison"].items():
            lines.append(
                "| "
                + metric
                + " | "
                + " | ".join(
                    value(cell)
                    for cell in (
                        measurement["B_over_A_mean"],
                        measurement["paired_difference"]["mean"],
                        measurement["paired_difference"]["median"],
                    )
                )
                + " |"
            )
        for excluded in pairs["excluded_pairs"]:
            lines.append(
                f"- Excluded {excluded['task_id']} repeat {excluded['repeat']}: "
                + "; ".join(excluded["reasons"])
            )
    lines += [
        "",
        "## Selection strata (descriptive)",
        "",
        "| Stratum | Arm | Attempted | Successful | Mean full seconds | Mean input |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for stratum, summaries in report["strata"].items():
        for arm, summary in summaries.items():
            lines.append(
                "| "
                + stratum
                + " | "
                + arm
                + " | "
                + " | ".join(
                    value(cell)
                    for cell in (
                        summary["attempted_runs"],
                        summary["successful_runs"],
                        summary["metrics"]["end_to_end_wall_seconds"]["mean"],
                        summary["metrics"]["input_tokens"]["mean"],
                    )
                )
                + " |"
            )
    lines += [
        "",
        "Permutation counts: " + json.dumps(report["permutation_counts"], sort_keys=True) + ".",
        "",
        "Actual cost per successful task (all attempted costs, including failures):",
    ]
    for arm, summary in report["configurations"].items():
        cost = summary["actual_cost_per_successful_task_usd"]
        lines.append(
            f"- {arm}: {value(cost['value'])}; {cost['attempted_runs_in_numerator']} attempted costs / {cost['successful_runs_in_denominator']} successful tasks. {cost['reason'] or ''}"
        )
    lines += [
        "",
        "## Individual original runs",
        "",
        "| Run | Status | Grade | Treatment | Input | Cached | Output | Full seconds |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["runs"]:
        m = row["metrics"]
        lines.append(
            "| "
            + " | ".join(
                value(cell)
                for cell in (
                    row["run_id"],
                    row["status"],
                    row.get("grader", {}).get("success"),
                    row.get("preload_treatment_fidelity", {}).get("valid"),
                    m["input_tokens"],
                    m["cached_input_tokens"],
                    m["output_tokens"],
                    m["end_to_end_wall_seconds"],
                )
            )
            + " |"
        )
    lines += ["", "## Failures", ""] + (
        [
            "- " + row["run_id"] + ": " + row["status"] + "; " + "; ".join(row.get("errors", []))
            for row in report["failures"]
        ]
        or ["None."]
    )
    lines += ["", "## Limitations", ""] + [
        "- " + limitation for limitation in report["limitations"]
    ]
    (output / "report.md").write_text("\n".join(lines) + "\n")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--tasks", type=Path, default=ROOT / "benchmarks/tasks_workflow.json")
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--model", required=True)
    result.add_argument("--effort", default="low")
    result.add_argument("--codex", default=shutil.which("codex") or "codex")
    result.add_argument("--codex-home", type=Path)
    result.add_argument("--timeout", type=float, default=180)
    result.add_argument("--repeats", type=int, choices=(1, 2), default=2)
    result.add_argument("--seed", type=int, default=20261018)
    result.add_argument("--limit", type=int)
    result.add_argument("--resume", action="store_true")
    return result


def run_experiment(arguments: argparse.Namespace, output: Path) -> int:
    tasks = load_tasks(arguments.tasks)
    if arguments.limit:
        tasks = tasks[: arguments.limit]
    arguments.codex = str(Path(shutil.which(arguments.codex) or arguments.codex).absolute())
    version = subprocess.check_output([arguments.codex, "--version"], text=True).strip()
    settings = {
        "model": arguments.model,
        "effort": arguments.effort,
        "repeats": arguments.repeats,
        "timeout": arguments.timeout,
        "seed": arguments.seed,
        "limit": arguments.limit,
        "codex_executable": str(Path(arguments.codex).resolve()),
        "codex_home_binding_directory": str(arguments.codex_home.resolve())
        if arguments.codex_home
        else None,
        "codex_version": version,
        "requested_service_tier": "default",
        "configuration_labels": LABELS,
        "context_max_bytes": 12000,
        "corpus": "workflow",
        "comparison_kind": "Fresh three-arm Codex / source-only / source-plus-support workflow comparison",
        "cache_conditions": "Fresh native state/worktree each arm; cold B/C approval/index except supplied controls; no A Memglide state; provider/OS caches uncontrolled; repeat-two ordering reverses repeat one",
    }
    frozen = frozen_manifest(arguments.tasks, tasks, settings)
    environment = {**os.environ, "NO_COLOR": "1", "CI": "1", "MEMGLIDE_HOME": str(output / "state")}
    if arguments.codex_home:
        environment["CODEX_HOME"] = str(arguments.codex_home.resolve())
    plan = make_plan(tasks, arguments.repeats, arguments.seed)
    if arguments.resume:
        metadata = json.loads((output / "metadata.json").read_text())
        durable.validate_frozen(metadata, frozen)
        durable.read_log(output)
        durable.verify_repositories(metadata.get("repositories", {}))
        state = json.loads((output / "state.json").read_text())
        common.validate_saved_state(output, tasks, plan, state)
        if metadata.get("finished_at") and (output / "report.json").exists():
            print(f"Completed workflow report retained: {output / 'report.json'}", flush=True)
            return 2 if metadata.get("shared_blocker") else 0
        common.recover_interrupted(output, state, metadata)
    else:
        metadata = {
            "started_at": legacy.utc_now(),
            "experiment_version": "workflow-1",
            "corpus": "workflow",
            "model": arguments.model,
            "reasoning_effort": arguments.effort,
            "repeats": arguments.repeats,
            "random_seed": arguments.seed,
            "output_directory": str(output),
            "frozen_manifest": frozen,
            "memglide_source_before": capture_provenance(ROOT),
            "resume_count": 0,
            "codex_version": version,
            "configuration_labels": LABELS,
            "comparison_kind": settings["comparison_kind"],
            **legacy.host_metadata(),
            "methodology": {
                "treatment": "A native Codex; B production compact-prefix source preload; C same launcher with caller-selected complete supporting tests; deterministic supplied-context bypass; zero configured MCP in all arms",
                "tasks": f"{len(tasks)} fresh tasks, {sum(task['language'] == 'python' for task in tasks)} Python/{sum(task['language'] == 'typescript' for task in tasks)} TypeScript, {arguments.repeats} repeats; {len(plan)} original assignments in this invocation",
                "identity": "Same common task prompt including focus/support paths and exact test argv, source commit, model/effort/native flags; B adds focused source, C focused source plus complete caller-selected tests on eight tasks",
                "grading": "Independent external behavior graders; native framing/schema and treatment validity separately checked",
                "timing": "Cold B/C approval/index+launcher+native, A native; excludes worktree creation/grading; child RSS excludes parent indexer",
                "cost": "Actual billing/model-call/actual filesystem-read counts unavailable; raw cost fields null, separately labelled cited-rate estimates only",
            },
        }
        state = {
            "originals": {row["run_id"]: durable.pending(row) for row in plan},
            "supplemental": [],
        }
        common.atomic_json(output / "plan.json", {"tasks": tasks, "runs": plan}, immutable=True)
        common.atomic_json(
            output / "final-response-schema.json", legacy.OUTPUT_SCHEMA, immutable=True
        )
        durable.checkpoint(output, state, metadata)
        durable.append_log(
            output,
            "experiment.created",
            frozen_manifest_sha256=common.digest(common.canonical(frozen)),
        )

    def persist(repositories: dict[str, Any]) -> None:
        metadata["repositories"] = repositories
        durable.checkpoint(output, state, metadata)

    repositories = create_repositories(output, tasks, metadata.get("repositories", {}), persist)
    metadata["repositories"] = repositories
    durable.checkpoint(output, state, metadata)
    task_map, blocker = {task["id"]: task for task in tasks}, metadata.get("shared_blocker")
    for row in plan:
        if not state["originals"][row["run_id"]].get("pending"):
            continue
        if blocker:
            state["originals"][row["run_id"]] = legacy.not_run(row, blocker)
            continue
        try:
            durable.validate_frozen(metadata, frozen_manifest(arguments.tasks, tasks, settings))
            durable.verify_repositories(repositories)
        except ValueError as error:
            blocker = str(error)
            metadata["source_guard_failure"] = blocker
            state["originals"][row["run_id"]] = legacy.not_run(row, blocker)
            continue
        print(
            f"[{row['order']}/{len(plan)}] {row['run_id']} {LABELS[row['configuration']]}",
            flush=True,
        )
        attempt = begin_attempt(output, row, task_map[row["task_id"]], state, metadata)
        result = run_attempt(
            attempt,
            task_map[row["task_id"]],
            repositories[row["repository"]],
            output,
            arguments,
            environment,
        )
        try:
            durable.validate_frozen(metadata, frozen_manifest(arguments.tasks, tasks, settings))
        except ValueError as error:
            blocker = str(error)
            metadata["source_guard_failure"] = blocker
        durable.finish_attempt(output, result, state, metadata)
        if result.get("common_blocker"):
            blocker = "Confirmed shared runtime blocker: " + result["common_blocker"]
    if blocker:
        metadata.update(shared_blocker=blocker, blockers=[blocker])
    metadata["finished_at"] = legacy.utc_now()
    metadata["memglide_source_after"] = capture_provenance(ROOT)
    metadata["source_unchanged_during_experiment"] = metadata["memglide_source_before"][
        "source_tree_sha256"
    ] == metadata["memglide_source_after"]["source_tree_sha256"] and not metadata.get(
        "source_guard_failure"
    )
    durable.checkpoint(output, state, metadata)
    report = build_report(list(state["originals"].values()), tasks, metadata)
    write_report(report, output)
    durable.append_log(
        output,
        "experiment.finished",
        report_sha256=common.digest((output / "report.json").read_bytes()),
    )
    print(f"Workflow reports: {output / 'report.md'} and {output / 'report.json'}", flush=True)
    return (
        2
        if blocker
        else int(any(row["status"] == "harness_error" for row in state["originals"].values()))
    )


def main(argv: list[str] | None = None) -> int:
    argument_parser = parser()
    arguments = argument_parser.parse_args(argv)
    if arguments.timeout <= 0 or arguments.limit is not None and arguments.limit < 1:
        argument_parser.error("timeout and limit must be positive")
    output = arguments.output.resolve()
    if arguments.resume:
        if not (output / "state.json").exists():
            argument_parser.error("No durable experiment checkpoint exists to resume")
    elif output.exists():
        argument_parser.error(
            "Output already exists; choose a fresh directory or explicit --resume"
        )
    else:
        output.mkdir(parents=True)
    with durable.experiment_lock(output):
        return run_experiment(arguments, output)


if __name__ == "__main__":
    raise SystemExit(main())
