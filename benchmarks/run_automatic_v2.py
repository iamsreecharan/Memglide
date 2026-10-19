"""Fresh selective-source evaluation; local planning/offline are the defaults.

V1 protocols, code and negative outcomes remain unchanged. Formal execution is
separately approval-recorded and requires a matching eligible offline report.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import random
import shutil
import subprocess
import time
from collections import Counter
from itertools import permutations
from pathlib import Path
from typing import Any

from benchmarks import run_automatic as base

common, durable, legacy = base.common, base.durable, base.legacy
workflow, pricing = base.workflow, base.pricing
ROOT = base.ROOT
VERSION = "automatic-2"
ARMS = base.ARMS
OFFLINE_ARMS = ("B", "C", "V1")
make_plan = base.make_plan
budget_estimate = base.budget_estimate
verify_delivery = base.verify_delivery
validate_approval = base.validate_approval
LIMITS = base.LIMITS + [
    "Offline B/C/V1 order is balanced across tasks and reversed on repeat two; preparation timings remain local component observations, not native task latency benefits.",
    "V1 is an offline previous-policy comparator only; formal model configurations remain A bare, B known-path source and C selective v2 source.",
    "Technical eligibility requires repeated automatic preloads on at least half of tasks and complete declared scope on at least three quarters of known-source-preparable tasks; it does not establish efficiency or default promotion.",
    "Parent CPU includes preparation, sampler and treatment-audit work, excludes child CPU and is not combined with sampled child CPU as an exact total.",
    "Waited preparation-child CPU is a separate OS cumulative-counter difference around setup/preparation only; it excludes later audit/native/grading and still-running or unwaited children. No preparation peak RSS is inferred.",
    "All native arms receive the same pinned TypeScript compiler on PATH. Upstream full development suites/dependencies are not installed; focused native checks and external behavioral grading are distinct from upstream full-suite validation.",
]


def task_prompt(task: dict[str, Any]) -> str:
    return (
        base.task_prompt(task)
        + "\nAvailable test tools and repository policy:\n"
        + "A pinned TypeScript compiler is on PATH; use installed tools and Node built-in "
        + "test/assert for focused checks. Do not install repository development dependencies "
        + "or run repository package lifecycle/build scripts, even if repository instruction "
        + "files suggest doing so. Preserve every pre-existing tracked test, documentation, "
        + "agent-instruction and configuration file; restrict repairs to production source.\n"
    )


def toolchain_identity() -> dict[str, Any]:
    package = ROOT / "frontend/node_modules/typescript"
    compiler = package / "bin/tsc"
    binding = ROOT / "frontend/node_modules/.bin/tsc"
    if not compiler.is_file() or binding.resolve(strict=True) != compiler.resolve(strict=True):
        raise ValueError("A pinned installed TypeScript compiler binding is required")
    files = {}
    for path in sorted(package.rglob("*")):
        if path.is_symlink():
            raise ValueError("Compiler package must not contain unexpected symlinks")
        if path.is_file():
            files[path.relative_to(ROOT).as_posix()] = _file_digest(path)
    platform_files = {}
    for platform_package in sorted(
        (ROOT / "frontend/node_modules/@typescript").glob("typescript-*")
    ):
        for path in sorted(platform_package.rglob("*")):
            if path.is_symlink():
                raise ValueError("Native compiler platform package contains an unexpected symlink")
            if path.is_file():
                platform_files[path.relative_to(ROOT).as_posix()] = _file_digest(path)
    info = json.loads((package / "package.json").read_text())
    node = shutil.which("node")
    if node is None:
        raise ValueError("Installed Node is required for the pinned compiler and focused checks")
    node_path = Path(node).resolve(strict=True)
    return {
        "typescript_package_version": info["version"],
        "compiler_bindir": str(binding.parent),
        "compiler_resolved": str(compiler.resolve(strict=True)),
        "compiler_package_files_sha256": files,
        "platform_compiler_package_files_sha256": platform_files,
        "node_executable": str(node_path),
        "node_version": subprocess.check_output([str(node_path), "--version"], text=True).strip(),
        "node_executable_sha256": _file_digest(node_path),
    }


def _file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(256_000), b""):
            value.update(block)
    return value.hexdigest()


def native_environment() -> dict[str, str]:
    return {
        **os.environ,
        "CI": "1",
        "NO_COLOR": "1",
        "PATH": str(ROOT / "frontend/node_modules/.bin")
        + os.pathsep
        + os.environ.get("PATH", os.defpath),
    }


def waited_child_cpu_snapshot() -> float | None:
    """Observed OS user+system CPU of already-waited child processes, if supported."""
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        return float(usage.ru_utime + usage.ru_stime)
    except (ImportError, AttributeError, OSError):
        return None


def waited_prep_child_cpu_delta(started: float | None, finished: float | None) -> float | None:
    if not base._number(started) or not base._number(finished) or finished < started:
        return None
    return float(finished - started)


PREPARATION_CHILD_CPU_SCOPE = (
    "OS RUSAGE_CHILDREN user+system CPU difference around synchronous repository "
    "approval/index and context preparation only; includes waited Git/parser workers, "
    "excludes still-running/unwaited children and later treatment audit, native execution "
    "and external grading. Separate from parent CPU and sampled native child CPU; "
    "no preparation peak RSS attribution."
)


def corpus() -> Any:
    return importlib.import_module("benchmarks.corpus_automatic_v2")


def neutral_repository_path(output: Path, ordinal: int) -> Path:
    if type(ordinal) is not int or ordinal < 1:
        raise ValueError("Repository ordinal must be a positive integer")
    return output / "repositories" / f"repo-{ordinal:04d}"


def neutral_worktree_path(output: Path, order: int) -> Path:
    if type(order) is not int or order < 1:
        raise ValueError("Assignment order must be a positive integer")
    return output / "worktrees" / f"work-{order:04d}"


def load_tasks() -> list[dict[str, Any]]:
    tasks = corpus().load_tasks()
    seen = set()
    for task in tasks:
        identifier = task.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.replace("-", "").replace("_", "").isalnum()
            or identifier in seen
            or not isinstance(task.get("prompt"), str)
            or not task["prompt"].strip()
            or task.get("language") not in {"python", "typescript"}
            or not isinstance(task.get("known_paths"), list)
            or not task["known_paths"]
            or not all(base._safe_relative(path) for path in task["known_paths"])
            or len(set(task["known_paths"])) != len(task["known_paths"])
        ):
            raise ValueError("Invalid or duplicate v2 task")
        if any(path in task["prompt"] for path in task["known_paths"]):
            raise ValueError("V2 public task discloses an evaluator-known target path")
        seen.add(identifier)
    if not tasks:
        raise ValueError("A v2 study needs tasks")
    return tasks


def frozen_manifest() -> dict[str, Any]:
    files = set((ROOT / "src/memglide").rglob("*.py"))
    files.update((ROOT / "benchmarks").glob("*.py"))
    for directory in ("automatic-fixtures", "automatic-v2-fixtures"):
        files.update((ROOT / "benchmarks" / directory).rglob("*"))
    files.update(
        ROOT / name
        for name in (
            "benchmarks/tasks_automatic.json",
            "benchmarks/tasks_automatic_v2.json",
            "benchmarks/automatic-protocol.md",
            "benchmarks/automatic-v2-protocol.md",
            "benchmarks/cost-pricing.json",
            "benchmarks/warm-80-analysis.json",
            "pyproject.toml",
            "uv.lock",
            "frontend/package.json",
            "frontend/package-lock.json",
        )
    )
    hashes = {}
    for path in sorted(files):
        if path.is_symlink():
            raise ValueError("Frozen v2 source or evidence cannot be a symlink")
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = common.digest(path.read_bytes())
    return {
        "git_head": legacy.git(ROOT, "rev-parse", "HEAD"),
        "files": hashes,
        "toolchain": toolchain_identity(),
    }


def create_plan(
    output: Path, *, repeats: int, seed: int, model: str, effort: str
) -> dict[str, Any]:
    tariff = json.loads((ROOT / "benchmarks/cost-pricing.json").read_text())
    if model != tariff["model"]:
        raise ValueError("New models require independently reviewed matching frozen pricing")
    output.mkdir(parents=True, exist_ok=False)
    tasks = load_tasks()
    repositories = {}
    for ordinal, task in enumerate(tasks, 1):
        directory = neutral_repository_path(output, ordinal)
        directory.mkdir(parents=True)
        corpus().build_task_repo(task["id"], directory)
        repositories[task["id"]] = base._commit_fixture(directory)
    assignments = make_plan(tasks, repeats, seed)
    plan = {
        "version": VERSION,
        "created_at": legacy.utc_now(),
        "tasks": tasks,
        "assignments": assignments,
        "offline_assignments": offline_plan(tasks, repeats, seed),
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
            "selection_policy": "v2",
            "experimental_excerpts": False,
            "memory": False,
            "mcp_servers": 0,
            "selection_model_calls": 0,
            "codex_version": "0.159.2",
            "toolchain": toolchain_identity(),
        },
        "technical_eligibility_rule": {
            "minimum_C_preloaded_unique_task_fraction": 0.5,
            "minimum_C_complete_scope_fraction_of_B_preparable_tasks": 0.75,
            "task_qualifies_only_when_all_requested_repeats_qualify": True,
            "all_delivered_source_fidelity_valid": True,
            "interpretation": "Technical operation only; not an efficiency or promotion gate",
        },
        "budget_estimate": budget_estimate(len(assignments)),
        "frozen_manifest": frozen_manifest(),
        "limitations": LIMITS,
        "execution_requires_approval_record": True,
    }
    common.atomic_json(output / "preregistration.json", plan, immutable=True)
    (output / "preregistration.sha256").write_text(
        common.digest((output / "preregistration.json").read_bytes()) + "\n"
    )
    return plan


def read_plan(directory: Path) -> dict[str, Any]:
    path = directory / "preregistration.json"
    sidecar = directory / "preregistration.sha256"
    if path.is_symlink() or sidecar.is_symlink() or not path.is_file():
        raise ValueError("V2 preregistration and seal must be regular files")
    if common.digest(path.read_bytes()) != sidecar.read_text().strip():
        raise ValueError("V2 preregistration hash changed")
    plan = json.loads(path.read_text())
    if plan.get("version") != VERSION or plan["frozen_manifest"] != frozen_manifest():
        raise ValueError("V2 frozen source, corpus, grading, pricing or Git HEAD changed")
    if plan["tasks"] != load_tasks():
        raise ValueError("V2 private/public task definitions changed")
    settings = plan["settings"]
    if plan["assignments"] != make_plan(plan["tasks"], settings["repeats"], settings["seed"]):
        raise ValueError("V2 formal assignment identity/order changed")
    if plan["offline_assignments"] != offline_plan(
        plan["tasks"], settings["repeats"], settings["seed"]
    ):
        raise ValueError("V2 offline assignment identity/order changed")
    if plan["public_prompt_sha256"] != {
        task["id"]: common.digest(task_prompt(task).encode()) for task in plan["tasks"]
    }:
        raise ValueError("V2 public prompt hashes changed")
    durable.verify_repositories(plan["repositories"])
    return plan


def prepare(
    arm: str, prompt: str, task: dict[str, Any], setup: dict[str, Any], artifacts: Path
) -> dict[str, Any]:
    if arm in {"A", "B"}:
        return base.prepare(arm, prompt, task, setup, artifacts)
    if arm not in {"C", "V1"} or task["prompt"] not in prompt:
        raise ValueError("V2 selection requires an exact public task substring")
    from memglide.integrations.auto_preload import prepare_task_prompt

    return prepare_task_prompt(
        prompt,
        task_query=task["prompt"],
        selection_policy="v2" if arm == "C" else "v1",
        project_id=setup["project_id"],
        db_path=artifacts / "memglide.db",
        enabled=True,
        max_context_bytes=12_000,
        max_added_tokens=4_000,
        context_format="compact-prefix",
    )


def offline_plan(tasks: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    generator = random.Random(seed)
    members = list(tasks)
    generator.shuffle(members)
    orders = list(permutations(OFFLINE_ARMS))
    generator.shuffle(orders)
    first = {task["id"]: orders[index % len(orders)] for index, task in enumerate(members)}
    plan: list[dict[str, Any]] = []
    for repeat in range(1, repeats + 1):
        for task in members:
            order = first[task["id"]]
            if repeat % 2 == 0:
                order = tuple(reversed(order))
            for arm in order:
                plan.append(
                    {
                        "run_id": f"offline-{task['id']}-r{repeat}-{arm}",
                        "task_id": task["id"],
                        "repository": task["repository"],
                        "language": task["language"],
                        "configuration": arm,
                        "repeat": repeat,
                        "order": len(plan) + 1,
                    }
                )
    return plan


def eligibility(
    rows: list[dict[str, Any]], expected_observations: int, repeats: int = 2
) -> dict[str, Any]:
    automatic = [row for row in rows if row["configuration"] == "C"]
    preloads = sum(
        row.get("context_preparation", {}).get("mode") == "preloaded" for row in automatic
    )
    valid = all(row.get("treatment_fidelity", {}).get("valid") is True for row in rows)
    tasks = {row["task_id"] for row in rows}
    grouped = {
        (task, arm): [row for row in rows if row["task_id"] == task and row["configuration"] == arm]
        for task in tasks
        for arm in OFFLINE_ARMS
    }

    def qualifies(task: str, arm: str, *, complete: bool = False) -> bool:
        members = grouped[task, arm]
        return bool(
            len(members) == repeats
            and {row["repeat"] for row in members} == set(range(1, repeats + 1))
            and all(
                row.get("context_preparation", {}).get("mode") == "preloaded"
                and (not complete or row.get("declared_scope_complete_proxy") is True)
                for row in members
            )
        )

    C_preloaded_tasks = {task for task in tasks if qualifies(task, "C")}
    B_preparable_tasks = {task for task in tasks if qualifies(task, "B", complete=True)}
    complete_tasks = {task for task in B_preparable_tasks if qualifies(task, "C", complete=True)}
    preload_fraction = len(C_preloaded_tasks) / len(tasks) if tasks else 0
    complete_fraction = (
        len(complete_tasks) / len(B_preparable_tasks) if B_preparable_tasks else None
    )
    return {
        "passed": bool(
            len(rows) == expected_observations
            and valid
            and preload_fraction >= 0.5
            and complete_fraction is not None
            and complete_fraction >= 0.75
        ),
        "expected_observations": expected_observations,
        "observed_observations": len(rows),
        "C_preloaded_observations": preloads,
        "unique_tasks": len(tasks),
        "C_preloaded_unique_tasks_all_repeats": sorted(C_preloaded_tasks),
        "C_preloaded_unique_task_fraction": preload_fraction,
        "B_preparable_unique_tasks_all_repeats": sorted(B_preparable_tasks),
        "C_complete_scope_on_B_preparable_tasks_all_repeats": sorted(complete_tasks),
        "C_complete_scope_fraction_of_B_preparable_tasks": complete_fraction,
        "required_preload_fraction": 0.5,
        "required_complete_scope_fraction": 0.75,
        "requested_repeats": repeats,
        "all_complete_source_or_exact_passthrough_verified": valid,
        "all_skip_rejected": bool(automatic) and preloads == 0,
        "default_promotion": False,
        "interpretation": "Minimum technical eligibility only; no native efficiency evidence or automatic promotion",
    }


def offline(plan: dict[str, Any], plan_directory: Path, output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    base._load_preparers()
    tasks = {task["id"]: task for task in plan["tasks"]}
    rows = []
    for assignment in plan["offline_assignments"]:
        task = tasks[assignment["task_id"]]
        artifacts = output / "runs" / assignment["run_id"]
        artifacts.mkdir(parents=True)
        worktree = neutral_worktree_path(output, assignment["order"])
        repository = plan["repositories"][task["id"]]
        legacy.create_worktree(repository, worktree)
        prompt = task_prompt(task)
        started, cpu_started = time.perf_counter(), time.process_time()
        prep_child_started = waited_child_cpu_snapshot()
        setup = common.prepare_project(worktree, artifacts)
        prepared = prepare(assignment["configuration"], prompt, task, setup, artifacts)
        prep_child_finished = waited_child_cpu_snapshot()
        elapsed, cpu = time.perf_counter() - started, time.process_time() - cpu_started
        fidelity = verify_delivery(prepared, prompt, repository)
        selected = {item["path"] for item in prepared.get("files", [])}
        expected = set(task["known_paths"])  # Evaluator-only, after discovery completed.
        row = {
            **assignment,
            "setup": setup,
            "context_preparation": {
                key: value for key, value in prepared.items() if key != "prompt"
            },
            "treatment_fidelity": fidelity,
            "selected_paths": sorted(selected),
            "expected_paths_evaluator_only": sorted(expected),
            "declared_scope_recall_proxy": len(expected & selected) / len(expected),
            "declared_scope_complete_proxy": expected <= selected,
            "selected_files_outside_author_scope": sorted(selected - expected),
            "cold_setup_and_preparation_seconds": elapsed,
            "cold_setup_and_preparation_parent_cpu_seconds": cpu,
            "observed_waited_prep_child_cpu_seconds": waited_prep_child_cpu_delta(
                prep_child_started, prep_child_finished
            ),
            "preparation_child_cpu_scope": PREPARATION_CHILD_CPU_SCOPE,
            "prompt_sha256": common.digest(prepared["prompt"].encode()),
            "native_model_calls": 0,
            "native_coding_success": None,
            "model_input_tokens": None,
            "actual_billed_cost_usd": None,
        }
        common.atomic_json(artifacts / "result.json", row, immutable=True)
        rows.append(row)
    summaries = {}
    for arm in OFFLINE_ARMS:
        members = [row for row in rows if row["configuration"] == arm]
        summaries[arm] = {
            "observations": len(members),
            "unique_tasks": len({row["task_id"] for row in members}),
            "complete_declared_scope_count": sum(
                row["declared_scope_complete_proxy"] for row in members
            ),
            "declared_scope_recall_proxy": common.summarize(
                [row["declared_scope_recall_proxy"] for row in members], additive=False
            ),
            "cold_setup_and_preparation_seconds": common.summarize(
                [row["cold_setup_and_preparation_seconds"] for row in members]
            ),
            "parent_cpu_seconds": common.summarize(
                [row["cold_setup_and_preparation_parent_cpu_seconds"] for row in members]
            ),
            "observed_waited_prep_child_cpu_seconds": common.summarize(
                [row["observed_waited_prep_child_cpu_seconds"] for row in members]
            ),
            "added_bytes": common.summarize(
                [row["context_preparation"]["context_bytes"] for row in members]
            ),
            "decisions": dict(
                Counter(
                    row["context_preparation"]
                    .get("automatic_selection", {})
                    .get("decision", row["context_preparation"]["mode"])
                    for row in members
                )
            ),
            "reasons": dict(Counter(row["context_preparation"]["reason"] for row in members)),
        }
    report = {
        "version": VERSION,
        "kind": "Balanced repeated offline source-discovery probe; no coding model",
        "frozen_preregistration_sha256": common.digest(
            (plan_directory / "preregistration.json").read_bytes()
        ),
        "frozen_manifest": plan["frozen_manifest"],
        "rows": rows,
        "summary": summaries,
        "technical_eligibility": eligibility(
            rows, len(plan["offline_assignments"]), plan["settings"]["repeats"]
        ),
        "model_requests": 0,
        "strict_native_success_rate": None,
        "estimated_model_cost_per_success": None,
        "actual_billed_cost_usd": None,
        "paired_local_preparation_effects": {
            f"{candidate}_vs_{baseline}": base.paired_effects(
                rows, "cold_setup_and_preparation_seconds", candidate, baseline
            )
            for candidate, baseline in (("C", "B"), ("C", "V1"))
        },
        "limitations": LIMITS,
    }
    common.atomic_json(output / "report.json", report, immutable=True)
    (output / "report.sha256").write_text(
        common.digest((output / "report.json").read_bytes()) + "\n"
    )
    (output / "report.md").write_text(
        "# V2 offline automatic source discovery\n\nNo model requests. Coverage is an evaluator-scope proxy; native correctness, tokens and cost remain unmeasured.\n\n"
        + "| Arm | Observations | Complete author scope | Mean cold preparation s | Median s | Mean added bytes |\n|---|---:|---:|---:|---:|---:|\n"
        + "\n".join(
            f"| {arm} | {value['observations']} | {value['complete_declared_scope_count']} | {value['cold_setup_and_preparation_seconds']['mean']} | {value['cold_setup_and_preparation_seconds']['median']} | {value['added_bytes']['mean']} |"
            for arm, value in summaries.items()
        )
        + "\n\nTechnical eligibility: "
        + str(report["technical_eligibility"]["passed"])
        + ". This is not default promotion.\n\n"
        + "\n".join("- " + value for value in LIMITS)
        + "\n"
    )
    return report


def validate_offline_report(
    path: Path, plan_directory: Path, plan: dict[str, Any]
) -> dict[str, Any]:
    seal = path.with_name("report.sha256")
    if path.is_symlink() or seal.is_symlink() or not path.is_file():
        raise ValueError("Expected a regular v2 offline report and seal")
    if common.digest(path.read_bytes()) != seal.read_text().strip():
        raise ValueError("V2 offline report hash changed")
    report = json.loads(path.read_text())
    if report.get("version") != VERSION or report.get(
        "frozen_preregistration_sha256"
    ) != common.digest((plan_directory / "preregistration.json").read_bytes()):
        raise ValueError("Offline report belongs to another preregistration")
    expected = plan["offline_assignments"]
    rows = report.get("rows", [])
    if len(rows) != len(expected) or any(
        any(row.get(key) != value for key, value in assignment.items())
        for row, assignment in zip(rows, expected, strict=True)
    ):
        raise ValueError("Offline observations differ from preregistered assignments")
    gate = eligibility(rows, len(expected), plan["settings"]["repeats"])
    if report.get("technical_eligibility") != gate or not gate["passed"]:
        raise ValueError("Offline automatic treatment is ineligible, including all-SKIP outcomes")
    return report


def formal_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    report = base.formal_report(rows)
    report.update(version=VERSION, limitations=LIMITS)
    for arm in ARMS:
        attempted = [row for row in rows if row["configuration"] == arm and row.get("attempted")]
        summary = report["configurations"][arm]
        summary["parent_cpu_seconds_including_treatment_audit"] = common.summarize(
            [row.get("parent_cpu_seconds") for row in attempted]
        )
        summary["observed_waited_prep_child_cpu_seconds"] = common.summarize(
            [row.get("observed_waited_prep_child_cpu_seconds") for row in attempted]
        )
        summary["preparation_child_cpu_scope"] = PREPARATION_CHILD_CPU_SCOPE
        summary["observed_native_telemetry"] = {
            key: common.summarize(
                [
                    row.get("telemetry", {}).get(key)
                    if key != "mcp_call_count"
                    or row.get("telemetry", {}).get("mcp_counts_complete") is True
                    else None
                    for row in attempted
                ]
            )
            for key in (
                "command_count",
                "observed_file_read_commands",
                "observed_repeated_read_commands",
                "model_calls",
                "repeated_file_reads",
                "mcp_call_count",
            )
        }
        summary["cpu_scope"] = (
            "Parent includes local preparation, sampling and treatment audit, excludes child CPU; native child sampling is a separate lower bound. No exact total or provider CPU."
        )
        summary["rss_scope"] = (
            "Sampled native process tree; excludes parent preparation/index peak; shared pages may double-count."
        )
        summary["read_scope"] = (
            "Command-text proxies; exact filesystem reads and underlying provider model calls remain unavailable."
        )
    return report


# Separate dispatch body keeps v1 module globals and historical behavior untouched.
def _attempt(
    row: dict[str, Any], task: dict[str, Any], plan: dict[str, Any], output: Path, executable: str
) -> dict[str, Any]:
    artifacts = output / "runs" / row["run_id"]
    artifacts.mkdir(parents=True)
    root = neutral_worktree_path(output, row["order"])
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
        prep_child_started = waited_child_cpu_snapshot()
        setup = (
            common.prepare_project(root, artifacts)
            if row["configuration"] != "A"
            else {"wall_seconds": 0, "cpu_seconds": 0}
        )
        prepared = prepare(row["configuration"], original, task, setup, artifacts)
        prep_child_finished = waited_child_cpu_snapshot()
        context_done = time.perf_counter()
        # Independent reconstruction runs outside timed product preparation/native work.
        fidelity = verify_delivery(prepared, original, repository)
        audit_done = time.perf_counter()
        common.atomic_json(
            artifacts / "preparation.json",
            {key: value for key, value in prepared.items() if key != "prompt"},
            immutable=True,
        )
        result.update(
            observed_waited_prep_child_cpu_seconds=waited_prep_child_cpu_delta(
                prep_child_started, prep_child_finished
            ),
            preparation_child_cpu_scope=PREPARATION_CHILD_CPU_SCOPE,
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
                native_environment(),
            )
        )
        result.update(
            full_task_seconds=time.perf_counter() - started - (audit_done - context_done),
            treatment_audit_seconds=audit_done - context_done,
            parent_cpu_seconds=time.process_time() - cpu,
            observed_waited_prep_child_cpu_seconds=waited_prep_child_cpu_delta(
                prep_child_started, prep_child_finished
            ),
            preparation_child_cpu_scope=PREPARATION_CHILD_CPU_SCOPE,
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


def execute(
    plan_directory: Path,
    output: Path,
    *,
    offline_report_path: Path,
    approved_estimated_budget_usd: float | None,
    authorization_reference: str | None,
    codex: str,
) -> dict[str, Any]:
    plan = read_plan(plan_directory)
    validate_approval(plan, approved_estimated_budget_usd, authorization_reference)
    offline_evidence = validate_offline_report(offline_report_path, plan_directory, plan)
    executable = shutil.which(codex)
    if not executable:
        raise ValueError("Approved v2 execution requires installed native Codex")
    native_version = subprocess.check_output([executable, "--version"], text=True).strip()
    if native_version.removeprefix("codex-cli ") != plan["settings"]["codex_version"]:
        raise ValueError("Native version differs from frozen v2 configuration")
    output.mkdir(parents=True, exist_ok=False)
    base._load_preparers()
    common.atomic_json(
        output / "approval.json",
        {
            "approved_estimated_budget_usd": approved_estimated_budget_usd,
            "authorization_reference": authorization_reference,
            "native_version": native_version,
            "plan_sha256": common.digest((plan_directory / "preregistration.json").read_bytes()),
            "offline_report_sha256": common.digest(offline_report_path.read_bytes()),
            "offline_technical_eligibility": offline_evidence["technical_eligibility"],
            "hard_cap_available": False,
        },
        immutable=True,
    )
    common.atomic_json(output / "final-response-schema.json", legacy.OUTPUT_SCHEMA, immutable=True)
    rows = []
    tasks = {task["id"]: task for task in plan["tasks"]}
    blocker = None
    source_consistent = True
    spent_upper = 0.0
    for assignment in plan["assignments"]:
        if not blocker:
            try:
                read_plan(plan_directory)
            except ValueError as error:
                blocker, source_consistent = str(error), False
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
        result = _attempt(assignment, tasks[assignment["task_id"]], plan, output, executable)
        rows.append(result)
        upper = result["price_equivalent"]["possible_write_price_upper_usd"]
        if upper is None:
            blocker = "Unknown whole-attempt cost; no further requests can be budget-accounted"
        else:
            spent_upper += upper
        blocker = result.get("shared_blocker") or blocker
        try:
            read_plan(plan_directory)
        except ValueError as error:
            blocker, source_consistent = str(error), False
    report = formal_report(rows)
    report.update(
        native_version=native_version,
        estimated_allowance_stop_reason=blocker,
        frozen_source_consistent=source_consistent,
        no_resume_or_retry=True,
        offline_report_sha256=common.digest(offline_report_path.read_bytes()),
        default_promotion=False,
    )
    common.atomic_json(output / "report.json", report, immutable=True)
    (output / "report.md").write_text(
        "# Fresh v2 automatic source formal comparison\n\nAll originals retained. Costs are API-price equivalents; actual billing is unavailable.\n\n"
        + "| Arm | Attempted | Strict successes | USD per strict success | Mean full task s | Median s |\n|---|---:|---:|---:|---:|---:|\n"
        + "\n".join(
            f"| {arm} | {value['attempted']} | {value['strict_successes']} | {value['estimated_cost_per_strict_success_usd']} | {value['full_task_seconds']['mean']} | {value['full_task_seconds']['median']} |"
            for arm, value in report["configurations"].items()
        )
        + "\n\n"
        + "\n".join("- " + value for value in LIMITS)
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
    parser.add_argument("--offline-report", type=Path)
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
    if args.command == "execute" and args.offline_report is None:
        parser.error("execute requires matching --offline-report with technical eligibility")
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
                        "planned_native_assignments": len(value["assignments"]),
                        "planned_offline_observations": len(value["offline_assignments"]),
                        "budget_estimate": value["budget_estimate"],
                        "model_requests": 0,
                    }
                )
            )
        elif args.command == "offline":
            value = offline(
                read_plan(args.plan.resolve()), args.plan.resolve(), args.output.resolve()
            )
            print(
                json.dumps(
                    {
                        "model_requests": 0,
                        "summary": value["summary"],
                        "technical_eligibility": value["technical_eligibility"],
                    }
                )
            )
        else:
            value = execute(
                args.plan.resolve(),
                args.output.resolve(),
                offline_report_path=args.offline_report.resolve(),
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
