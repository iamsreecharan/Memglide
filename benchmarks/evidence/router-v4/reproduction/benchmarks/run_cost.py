"""Ten fresh matched tasks: standard Codex (A), compact-prefix Memglide (B).

Importing this module starts no requests. Raw supported native JSON telemetry is
kept independently of a separately labelled price-equivalent cost assessment.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path, PurePosixPath
from typing import Any

from benchmarks import run as legacy
from benchmarks import run_cache_formats as formats
from benchmarks import run_daily as common
from benchmarks import run_v2 as durable
from benchmarks.compare_components import capture_provenance

ROOT = common.ROOT
LABELS = {"A": "Standard Codex", "B": "Memglide compact-prefix"}


def codex_command(
    executable: str, worktree: Path, schema: Path, final: Path, model: str, effort: str
) -> list[str]:
    """Codex 0.159.2 Config.service_tier supports explicit standard routing."""
    native = common.codex_command(executable, worktree, schema, final, model, effort)
    return native[:-1] + ["-c", 'service_tier="default"', "-"]


def corpus_module() -> Any:
    return importlib.import_module("benchmarks.corpus_cost")


def load_tasks(path: Path) -> list[dict[str, Any]]:
    tasks = legacy.load_tasks(path)
    repositories = corpus_module().REPOSITORIES
    for task in tasks:
        identifier = task.get("repository")
        if identifier not in repositories or repositories[identifier][0] != task["language"]:
            raise ValueError("Unknown or language-mismatched cost-comparison repository")
        if not isinstance(task.get("prompt"), str) or not task["prompt"].strip():
            raise ValueError("Task prompt must not be empty")
        paths = task.get("focus_paths")
        if (
            not isinstance(paths, list)
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
            raise ValueError("Source scope must contain unique canonical relative paths")
        if type(task.get("context_supplied")) is not bool:
            raise ValueError("context_supplied must be an explicit boolean")
    return tasks


def make_plan(tasks: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    original = common.make_plan(tasks, 1, seed)
    plan: list[dict[str, Any]] = []
    for index in range(0, len(original), 2):
        first = "A" if index // 2 % 2 == 0 else "B"
        for arm in (first, "B" if first == "A" else "A"):
            row = {**original[index], "configuration": arm, "order": len(plan) + 1}
            row["run_id"] = f"cost-{row['task_id']}-r1-{arm}"
            row["context_format"] = "compact-prefix" if arm == "B" else None
            plan.append(row)
    return plan


def frozen_manifest(
    tasks_path: Path, tasks: list[dict[str, Any]], settings: dict[str, Any]
) -> dict[str, Any]:
    value = common.frozen_manifest(tasks_path, tasks, settings)
    for name in (
        "benchmarks/run_cost.py",
        "benchmarks/run_cache_formats.py",
        "benchmarks/corpus.py",
        "benchmarks/corpus_cost.py",
    ):
        path = ROOT / name
        if path.is_symlink():
            raise ValueError("Frozen runner/grader cannot be a symlink")
        value["files"][name] = common.digest(path.read_bytes())
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
            destination, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Frozen cost fixture"
        )
        repositories[identifier] = {
            "path": str(destination),
            "commit": legacy.git(destination, "rev-parse", "HEAD"),
            "tree": legacy.git(destination, "rev-parse", "HEAD^{tree}"),
        }
        persist(repositories)
    return repositories


def treatment_fidelity(
    result: dict[str, Any], task: dict[str, Any], prompt: str, repository: dict[str, str]
) -> dict[str, Any]:
    if result["configuration"] == "B":
        return formats.format_fidelity(result, task, prompt, repository)
    if result.get("execution_outcome_unknown"):
        return {"valid": None, "reason": "Interrupted standard-Codex outcome is unknown"}
    reasons = []
    artifacts = Path(result["artifacts"])
    try:
        if json.loads((artifacts / "command.json").read_text()) != result["native_command"]:
            reasons.append("Standard Codex command differs from frozen native arguments")
        if (artifacts / "prompt.txt").read_bytes() != prompt.encode("utf-8"):
            reasons.append("Standard Codex stdin differs from the exact common task prompt")
        if (artifacts / "preparation.json").exists() or (artifacts / "memglide.db").exists():
            reasons.append("Standard Codex unexpectedly contains Memglide preparation state")
        telemetry = result.get("telemetry", {})
        if telemetry.get("mcp_counts_complete") is not True or telemetry.get("mcp_call_count") != 0:
            reasons.append("Complete MCP-free standard-Codex native stream is absent")
    except (OSError, ValueError, TypeError, KeyError) as error:
        reasons.append("Invalid standard-Codex delivery evidence: " + type(error).__name__)
    return {
        "valid": not reasons,
        "reason": "; ".join(reasons)
        if reasons
        else "Direct native invocation receives exact common task stdin; no Memglide preparation or MCP",
        "mode": "standard",
        "context_format": None,
        "source_file_count": 0,
        "source_hashes": {},
        "context_bytes": 0,
        "actual_model_prompt_sha256": common.digest(prompt.encode()),
        "common_task_prompt_sha256": common.digest(prompt.encode()),
    }


def begin_attempt(
    output: Path,
    row: dict[str, Any],
    task: dict[str, Any],
    state: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Seal unknown cold B indexing before setup, including crash recovery."""
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
    prompt = common.task_prompt(task)
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
        if attempt["configuration"] == "B" and not task["context_supplied"] and task["focus_paths"]:
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
            formats.preload_command(
                native, artifacts, task, "compact-prefix", result["setup"].get("project_id")
            )
            if attempt["configuration"] == "B"
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
            "B launcher boundary before report-write/exec handoff through native exit; A has no launcher boundary"
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
    report = common.build_report(rows, tasks, metadata)
    report.update(
        report_version="cost-1",
        configuration_labels=LABELS,
        comparison_kind="Fresh ten-task standard Codex / compact-prefix Memglide comparison",
    )
    report["limitations"].insert(
        0,
        "A invokes standard native Codex directly. B invokes the production compact-prefix launcher, with cold approval/index for eight source-focused tasks and exact-prompt bypass for two supplied-context controls. Ten fresh tasks and one balanced repeat give twenty original assignments. No auxiliary model or configured MCP is used; this measures the conditional source-preload integration, not MCP retrieval or cross-session memory.",
    )
    report["limitations"].append(
        "Raw actual_cost_usd and computed_cost_usd remain null. Any separately published price-equivalent estimate uses cited per-million rates and observed uncached/cached/output usage; it is not attributable billing or a subscription charge. Unknown usage cannot be costed as zero.",
    )
    return report


def write_report(report: dict[str, Any], output: Path) -> None:
    common.write_report(report, output)
    text = (output / "report.md").read_text()
    text = text.replace(
        "# Ordinary-task Codex / Memglide A/B report",
        "# Fresh ten-task cost study: standard Codex (A) / compact-prefix Memglide (B)\n\n"
        "A = standard Codex; B = Memglide compact-prefix. Raw costs are unavailable; a separately labelled price-equivalent assessment may use observed native usage.",
    )
    (output / "report.md").write_text(text)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--tasks", type=Path, default=ROOT / "benchmarks/tasks_cost.json")
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--model", required=True)
    result.add_argument("--effort", default="low")
    result.add_argument("--codex", default=shutil.which("codex") or "codex")
    result.add_argument("--codex-home", type=Path)
    result.add_argument("--timeout", type=float, default=180)
    result.add_argument("--repeats", type=int, choices=(1,), default=1)
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
        "repeats": 1,
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
        "corpus": "cost",
        "comparison_kind": "Fresh ten-task standard Codex / compact-prefix Memglide comparison",
        "cache_conditions": "Fresh native state/worktree each arm; cold B approval/index except supplied controls; no A Memglide state; provider/OS caches uncontrolled, order balanced",
    }
    frozen = frozen_manifest(arguments.tasks, tasks, settings)
    environment = {**os.environ, "NO_COLOR": "1", "CI": "1", "MEMGLIDE_HOME": str(output / "state")}
    if arguments.codex_home:
        environment["CODEX_HOME"] = str(arguments.codex_home.resolve())
    plan = make_plan(tasks, arguments.seed)
    if arguments.resume:
        metadata = json.loads((output / "metadata.json").read_text())
        durable.validate_frozen(metadata, frozen)
        durable.read_log(output)
        durable.verify_repositories(metadata.get("repositories", {}))
        state = json.loads((output / "state.json").read_text())
        common.validate_saved_state(output, tasks, plan, state)
        if metadata.get("finished_at") and (output / "report.json").exists():
            print(f"Completed cost-study report retained: {output / 'report.json'}", flush=True)
            return 2 if metadata.get("shared_blocker") else 0
        common.recover_interrupted(output, state, metadata)
    else:
        metadata = {
            "started_at": legacy.utc_now(),
            "experiment_version": "cost-1",
            "corpus": "cost",
            "model": arguments.model,
            "reasoning_effort": arguments.effort,
            "repeats": 1,
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
                "treatment": "A native Codex with exact common prompt; B production compact-prefix source preload with deterministic supplied-context bypass; zero configured MCP in either arm",
                "tasks": "Ten fresh tasks, five Python/five TypeScript, one balanced repeat; twenty original assignments in the complete design",
                "identity": "Same common task prompt, source commit, model/effort/native flags; B deliberately adds current focused source on eight tasks",
                "grading": "Independent external behavior graders; native framing/schema and treatment validity separately checked",
                "timing": "Cold B approval/index+launcher+native, A native; excludes worktree creation/grading; child RSS excludes parent indexer",
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
    print(f"Cost-study reports: {output / 'report.md'} and {output / 'report.json'}", flush=True)
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
