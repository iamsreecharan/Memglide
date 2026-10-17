"""Execute paired, independently graded Codex runs, retaining every result.

Run with ``uv run python -m benchmarks.run``. Model requests may incur usage.
No model-produced success claim or estimated context token count is telemetry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from benchmarks.telemetry import parse_codex_jsonl

ROOT = Path(__file__).resolve().parents[1]
COMMON_INSTRUCTIONS = """Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.
If memglide MCP tools are available, use list_projects, start_session and get_context before editing, inspect the source evidence you need, and revalidate the Context Passport after edits. Otherwise use ordinary source tools. Do not claim token or cost savings.
"""
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "tests_run": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "tests_run"],
    "additionalProperties": False,
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def host_metadata() -> dict[str, Any]:
    """Public runtime versions and configured resource limits, without env dumps."""
    versions: dict[str, str | None] = {"python": sys.version}
    for name in ("node", "npm", "git"):
        executable = shutil.which(name)
        try:
            versions[name] = (
                subprocess.check_output(
                    [executable, "--version"],
                    text=True,
                    stderr=subprocess.PIPE,
                    timeout=10,
                ).strip()
                if executable
                else None
            )
        except (OSError, subprocess.SubprocessError):
            versions[name] = None
    limits = {}
    for name in ("cpu.max", "memory.max", "memory.swap.max", "pids.max"):
        path = Path("/sys/fs/cgroup") / name
        try:
            limits[name] = path.read_text().strip()
        except OSError:
            limits[name] = None
    return {
        "tool_versions": versions,
        "logical_cpu_count": os.cpu_count(),
        "cpu_affinity_count": len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else None,
        "cgroup_v2_limits": limits,
        "resource_scope": "Local execution host; model inference resources are not exposed",
    }


def git(directory: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(directory), *arguments],
        text=True,
        stderr=subprocess.PIPE,
    ).strip()


def load_tasks(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data if isinstance(data, list) else data["tasks"]
    if len({task["id"] for task in tasks}) != len(tasks):
        raise ValueError("Task IDs must be unique")
    if any(task["language"] not in {"python", "typescript"} for task in tasks):
        raise ValueError("Only the documented Python and TypeScript fixture repositories exist")
    return tasks


def make_plan(tasks: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    """Counterbalance within pairs; alternate each task's ordering across repeats."""
    generator = random.Random(seed)
    tasks = list(tasks)
    generator.shuffle(tasks)
    first_arm = {task["id"]: generator.choice(("A", "B")) for task in tasks}
    plan = []
    for repetition in range(1, repeats + 1):
        for task in tasks:
            first = first_arm[task["id"]]
            if repetition % 2 == 0:
                first = "B" if first == "A" else "A"
            for arm in (first, "B" if first == "A" else "A"):
                plan.append(
                    {
                        "run_id": f"{task['id']}-r{repetition}-{arm}",
                        "task_id": task["id"],
                        "language": task["language"],
                        "configuration": arm,
                        "repeat": repetition,
                        "order": len(plan) + 1,
                    }
                )
    return plan


def task_prompt(task: dict[str, Any]) -> str:
    return COMMON_INSTRUCTIONS + "\nTask:\n" + task["prompt"] + "\n"


def codex_command(
    executable: str,
    worktree: Path,
    schema: Path,
    final: Path,
    model: str,
    effort: str,
    database: Path | None = None,
) -> list[str]:
    command = [
        executable,
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--color",
        "never",
        "--sandbox",
        "workspace-write",
        "--model",
        model,
        "--disable",
        "apps",
        "-c",
        f"model_reasoning_effort={json.dumps(effort)}",
        "-c",
        'web_search="disabled"',
        "-C",
        str(worktree),
        "--output-schema",
        str(schema),
        "--output-last-message",
        str(final),
    ]
    if database is None:
        command += ["-c", "mcp_servers={}"]
    else:
        launcher = str(ROOT / ".venv" / "bin" / "memglide")
        # The user authorized these tools on each run's synthetic repository and
        # isolated database. Approve only this explicit tool list; retain Codex's
        # global approval policy and workspace-write sandbox. Without this host
        # policy, unannotated MCP tools require an unavailable interactive prompt.
        approved_tools = (
            "list_projects",
            "start_session",
            "get_session_status",
            "search_code",
            "get_symbol",
            "get_dependencies",
            "get_context",
            "expand_context",
            "get_context_passport",
            "save_memory",
            "recall_memory",
            "update_memory",
            "invalidate_memory",
            "end_session",
        )
        tool_policies = ",".join(tool + '={approval_mode="approve"}' for tool in approved_tools)
        config = (
            "mcp_servers={memglide={command="
            + json.dumps(launcher)
            + ",args="
            + json.dumps(["--db", str(database), "mcp"])
            + ',required=true,startup_readiness="connection"'
            + ",startup_timeout_sec=30.0,tool_timeout_sec=45.0,enabled_tools="
            + json.dumps(approved_tools)
            + ",tools={"
            + tool_policies
            + "}}}"
        )
        command += ["-c", config]
    return command + ["-"]


class ProcessSampler:
    """Linux /proc sample of local child CPU and simultaneous RSS, not inference.

    Very short-lived children can escape sampling. CPU is a lower bound summed
    from the largest observed per-process CPU counter. RSS is not unique memory:
    shared pages may be counted in more than one process. No command lines saved.
    """

    def __init__(self, pid: int, interval: float = 0.05):
        self.pid = pid
        self.interval = interval
        self.stop = threading.Event()
        self.cpu: dict[tuple[int, int], float] = {}
        self.memglide_cpu: dict[tuple[int, int], float] = {}
        self.peak = 0
        self.memglide_peak = 0
        self.samples = 0
        self.available = Path("/proc/self/stat").exists()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        if self.available:
            self.thread.start()

    def _sample(self) -> None:
        records = {}
        ticks = os.sysconf("SC_CLK_TCK")
        pagesize = os.sysconf("SC_PAGE_SIZE")
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                # comm can contain spaces and parentheses; fields start after its last ')'.
                fields = (entry / "stat").read_text().rsplit(")", 1)[1].split()
                records[int(entry.name)] = {
                    "ppid": int(fields[1]),
                    "cpu": (int(fields[11]) + int(fields[12])) / ticks,
                    "start": int(fields[19]),
                    "rss": int(fields[21]) * pagesize,
                    "entry": entry,
                }
            except (OSError, ValueError, IndexError):
                continue
        descendants = {self.pid}
        while True:
            more = {pid for pid, row in records.items() if row["ppid"] in descendants}
            if more <= descendants:
                break
            descendants.update(more)
        memglide = set()
        for pid in descendants:
            row = records.get(pid)
            if row is None:
                continue
            try:
                args = (row["entry"] / "cmdline").read_bytes().split(b"\0")
                if b"mcp" in args and any(b"memglide" in argument for argument in args):
                    memglide.add(pid)
            except OSError:
                pass
        while True:
            more = {pid for pid, row in records.items() if row["ppid"] in memglide}
            if more <= memglide:
                break
            memglide.update(more)
        for pid in descendants:
            if pid in records:
                row = records[pid]
                identity = (pid, row["start"])
                self.cpu[identity] = max(self.cpu.get(identity, 0), row["cpu"])
                if pid in memglide:
                    self.memglide_cpu[identity] = max(
                        self.memglide_cpu.get(identity, 0), row["cpu"]
                    )
        self.peak = max(self.peak, sum(records[p]["rss"] for p in descendants if p in records))
        self.memglide_peak = max(
            self.memglide_peak, sum(records[p]["rss"] for p in memglide if p in records)
        )
        self.samples += 1

    def _run(self) -> None:
        while not self.stop.is_set():
            self._sample()
            self.stop.wait(self.interval)

    def finish(self) -> dict[str, Any]:
        self.stop.set()
        if self.available:
            self.thread.join(timeout=2)
        return {
            "process_tree_peak_rss_bytes": self.peak if self.cpu else None,
            "cpu_seconds": sum(self.cpu.values()) if self.cpu else None,
            "memglide_peak_rss_bytes": self.memglide_peak if self.memglide_cpu else None,
            "memglide_cpu_seconds": sum(self.memglide_cpu.values()) if self.memglide_cpu else None,
            "observed_processes": len(self.cpu),
            "observed_memglide_processes": len(self.memglide_cpu),
            "samples": self.samples,
            "sampling_interval_seconds": self.interval,
            "scope": "Local Codex process tree only; remote model CPU and memory unavailable",
            "method": (
                "/proc sampling; CPU observed lower bound, RSS shared pages can be counted "
                "multiple times; short-lived processes may be missed"
            ),
        }


def execute_codex(
    command: list[str],
    prompt: str,
    worktree: Path,
    artifacts: Path,
    timeout: float,
    environment: dict[str, str],
) -> dict[str, Any]:
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(artifacts / "command.json", command)
    child_environment = environment.copy()
    child_environment["CODEX_HOME"] = str(
        isolated_codex_state(artifacts / "codex-state", environment)
    )
    started = time.perf_counter()
    timed_out = False
    with (
        (artifacts / "events.jsonl").open("w") as stdout,
        (artifacts / "stderr.log").open("w") as stderr,
    ):
        process = subprocess.Popen(
            command,
            cwd=worktree,
            env=child_environment,
            stdin=subprocess.PIPE,
            stdout=stdout,
            stderr=stderr,
            text=True,
            start_new_session=True,
        )
        sampler = ProcessSampler(process.pid)
        sampler.start()
        try:
            process.communicate(prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
        overhead = sampler.finish()
    return {
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "wall_time_seconds": time.perf_counter() - started,
        "overhead": overhead,
        "telemetry": parse_codex_jsonl(artifacts / "events.jsonl"),
    }


def common_blocker(result: dict[str, Any], artifacts: Path) -> str | None:
    """Only diagnose explicit shared blockers; ordinary task failures continue."""
    if result.get("exit_code") == 0 and result["telemetry"].get("completed_turns", 0):
        return None
    stderr = (artifacts / "stderr.log").read_text(encoding="utf-8", errors="replace")
    errors = json.dumps(result.get("telemetry", {}).get("errors", []))
    text = (stderr + "\n" + errors).lower()
    signatures = {
        "authentication": (
            "401 unauthorized",
            "authentication token",
            "not logged in",
            "invalid api key",
        ),
        "quota": ("usage limit", "quota exceeded", "insufficient_quota"),
        "unsupported_model": ("model is not supported", "model does not exist", "model_not_found"),
        "runtime_state_readonly": ("installation_id", "read-only file system"),
        "network_policy": (
            "proxyconnect",
            "tunnel connection failed: 403",
            "proxy connect",
            "403 forbidden",
        ),
        "network": (
            "failed to connect",
            "error sending request",
            "connection refused",
            "dns error",
        ),
    }
    for diagnosis, phrases in signatures.items():
        if any(phrase in text for phrase in phrases):
            return diagnosis
    return None


def create_repositories(base: Path, tasks: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    from benchmarks.corpus import build_repository

    repositories = {}
    for language in sorted({task["language"] for task in tasks}):
        destination = base / "repositories" / language
        destination.mkdir(parents=True, exist_ok=False)
        build_repository(language, destination)
        git(destination, "init", "--initial-branch=benchmark")
        git(destination, "config", "user.name", "Memglide Benchmark Fixture")
        git(destination, "config", "user.email", "benchmark@example.invalid")
        git(destination, "add", ".")
        git(
            destination, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Fixed benchmark fixture"
        )
        repositories[language] = {
            "path": str(destination),
            "commit": git(destination, "rev-parse", "HEAD"),
        }
    return repositories


def create_worktree(repository: dict[str, str], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    git(
        Path(repository["path"]),
        "worktree",
        "add",
        "--detach",
        str(destination),
        repository["commit"],
    )


def _protected_path(path: str) -> bool:
    parts = Path(path).parts
    name = Path(path).name
    return (
        any(part in {".git", "tests", "test", "__tests__"} for part in parts)
        or name.startswith("test_")
        or ".test." in name
        or ".spec." in name
    )


def protection_snapshot(worktree: Path) -> dict[str, str]:
    paths = git(worktree, "ls-files", "-z").split("\0")
    protected = [path for path in paths if path and _protected_path(path)] + [".git"]
    return {path: hashlib.sha256((worktree / path).read_bytes()).hexdigest() for path in protected}


def check_protection(worktree: Path, snapshot: dict[str, str], commit: str) -> list[str]:
    violations = []
    for path, digest in snapshot.items():
        item = worktree / path
        try:
            if item.is_symlink() or hashlib.sha256(item.read_bytes()).hexdigest() != digest:
                violations.append(path)
        except OSError:
            violations.append(path)
    try:
        if git(worktree, "rev-parse", "HEAD") != commit:
            violations.append("Git HEAD changed")
    except subprocess.CalledProcessError:
        violations.append("Git metadata unavailable")
    return sorted(set(violations))


def prepare_memglide(worktree: Path, database: Path, task: dict[str, Any]) -> dict[str, Any]:
    """Fresh index only: no sessions, retrievals, or saved agent findings."""
    from memglide.service import Service

    started = time.perf_counter()
    cpu_started = time.process_time()
    service = Service(database)
    try:
        project = service.indexer.add_project(str(worktree))
        elapsed = time.perf_counter() - started
        cpu_elapsed = time.process_time() - cpu_started
        return {
            "project_id": project["id"],
            "index_wall_seconds": elapsed,
            "wall_seconds": elapsed,
            "index_local_cpu_seconds": cpu_elapsed,
            "cpu_seconds": cpu_elapsed,
            "scope": "Required fresh project index only; no sessions or context retrieval before the model",
        }
    finally:
        service.close()


def preserve_changes(worktree: Path, artifacts: Path, base_commit: str = "HEAD") -> None:
    """Keep tracked patch plus new files without following any file symlinks."""
    (artifacts / "changes.patch").write_text(
        git(worktree, "diff", "--binary", base_commit),
        encoding="utf-8",
    )
    (artifacts / "git-status.txt").write_text(
        git(worktree, "status", "--porcelain", "--untracked-files=all") + "\n",
        encoding="utf-8",
    )
    paths = git(worktree, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    untracked = []
    with tarfile.open(artifacts / "untracked-files.tar", "w", dereference=False) as archive:
        for relative in paths:
            if not relative:
                continue
            if (
                Path(relative).is_absolute()
                or ".." in Path(relative).parts
                or ".git" in Path(relative).parts
            ):
                raise ValueError("Unsafe untracked path in Git output")
            archive.add(worktree / relative, arcname=relative, recursive=False)
            untracked.append(relative)
    write_json(artifacts / "untracked-files.json", untracked)


def not_run(row: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        **row,
        "status": "not_run",
        "attempted": False,
        "errors": [reason],
        "grader": {"success": None, "reason": "Run was not attempted"},
        "wall_time_seconds": None,
        "telemetry": {},
        "overhead": {},
        "actual_cost_usd": None,
        "computed_cost_usd": None,
    }


def isolated_codex_state(base: Path, environment: dict[str, str]) -> Path:
    """Reuse existing authentication by symlink; never read or copy its values.

    The managed runtime's supplied CODEX_HOME can be read-only, while Codex
    requires writable installation_id/state even with --ephemeral. Each request
    receives fresh local state. Only an existing auth binding is referenced.
    """
    base.mkdir(parents=True, mode=0o700, exist_ok=False)
    provided = Path(environment.get("CODEX_HOME", str(Path.home() / ".codex")))
    binding = provided / "auth.json"
    if binding.exists():
        (base / "auth.json").symlink_to(binding.resolve())
    return base


def run_task(
    row: dict[str, Any],
    task: dict[str, Any],
    repository: dict[str, str],
    output: Path,
    schema: Path,
    arguments: argparse.Namespace,
    environment: dict[str, str],
) -> dict[str, Any]:
    from benchmarks.corpus import grade

    artifacts = output / "runs" / row["run_id"]
    artifacts.mkdir(parents=True, exist_ok=False)
    worktree = output / "worktrees" / row["run_id"]
    create_worktree(repository, worktree)
    snapshot = protection_snapshot(worktree)
    prompt = task_prompt(task)
    result = {
        **row,
        "attempted": True,
        "started_at": utc_now(),
        "errors": [],
        "artifacts": str(artifacts),
        "worktree": str(worktree),
        "starting_commit": repository["commit"],
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "actual_cost_usd": None,
        "computed_cost_usd": None,
    }
    database = artifacts / "memglide.db" if row["configuration"] == "B" else None
    try:
        if database is not None:
            result["setup"] = prepare_memglide(worktree, database, task)
        command = codex_command(
            arguments.codex,
            worktree,
            schema,
            artifacts / "final.json",
            arguments.model,
            arguments.effort,
            database,
        )
        result.update(
            execute_codex(command, prompt, worktree, artifacts, arguments.timeout, environment)
        )
        violations = check_protection(worktree, snapshot, repository["commit"])
        result["protected_file_violations"] = violations
        # Preserve model changes before running any external grader/build tooling.
        preserve_changes(worktree, artifacts, repository["commit"])
        grading = grade(task["id"], worktree, artifacts)
        result["grader"] = grading
        result["treatment_valid"] = (
            (result["telemetry"].get("memglide_successful_get_context_count") or 0) > 0
            if database is not None
            else (
                result["telemetry"].get("mcp_call_count", 0) == 0
                and result["telemetry"].get("mcp_counts_complete") is True
                and result["telemetry"].get("stream_terminal") is True
                and result["telemetry"].get("completed_turns", 0) > 0
            )
        )
        if violations:
            grading["success"] = False
            result["errors"].append("Protected tests or Git metadata were modified")
        if result["timed_out"]:
            result["status"] = "timeout"
        elif result["exit_code"] != 0:
            result["status"] = "execution_failed"
        elif not result["treatment_valid"]:
            result["status"] = "invalid_treatment"
            result["errors"].append(
                "MCP tool availability/invocation did not match the intended arm"
            )
        elif not grading.get("success"):
            result["status"] = "failed"
        else:
            result["status"] = "completed"
        result["common_blocker"] = common_blocker(result, artifacts)
    except Exception as error:
        result["status"] = "harness_error"
        result["errors"].append(f"{type(error).__name__}: {error}")
        result.setdefault("grader", {"success": None, "reason": "Harness did not finish grading"})
    result["finished_at"] = utc_now()
    result["end_to_end_wall_seconds"] = (
        result["wall_time_seconds"] + result.get("setup", {}).get("index_wall_seconds", 0)
        if result.get("wall_time_seconds") is not None
        else None
    )
    write_json(artifacts / "result.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=ROOT / "benchmarks" / "tasks.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--effort", default="low")
    parser.add_argument("--codex", default=shutil.which("codex") or "codex")
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Existing authenticated state directory; no credentials are copied",
    )
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--limit", type=int, help="Smoke test: select only the first N tasks")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Use only after a successful independent preflight",
    )
    arguments = parser.parse_args(argv)
    if (
        arguments.repeats < 1
        or arguments.timeout <= 0
        or (arguments.limit is not None and arguments.limit < 1)
    ):
        parser.error("repeats, timeout and limit must be positive")
    output = (
        arguments.output
        or ROOT / ".local" / "benchmarks" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    ).resolve()
    if output.exists():
        parser.error(
            "Output directory already exists; choose a fresh output to preserve all evidence"
        )
    output.mkdir(parents=True)
    tasks = load_tasks(arguments.tasks)
    if arguments.limit:
        tasks = tasks[: arguments.limit]
    plan = make_plan(tasks, arguments.repeats, arguments.seed)
    write_json(output / "plan.json", {"tasks": tasks, "runs": plan})
    schema = output / "final-response-schema.json"
    write_json(schema, OUTPUT_SCHEMA)
    environment = os.environ.copy()
    if arguments.codex_home:
        environment["CODEX_HOME"] = str(arguments.codex_home.resolve())
    environment.update({"NO_COLOR": "1", "CI": "1", "MEMGLIDE_HOME": str(output / "state")})
    from benchmarks.compare_components import capture_provenance

    metadata = {
        "started_at": utc_now(),
        "model": arguments.model,
        "reasoning_effort": arguments.effort,
        "repeats": arguments.repeats,
        "repetitions": arguments.repeats,
        "random_seed": arguments.seed,
        "codex_version": subprocess.check_output([arguments.codex, "--version"], text=True).strip(),
        "host_python": sys.version,
        "platform": sys.platform,
        **host_metadata(),
        "memglide_source_before": capture_provenance(ROOT),
        "measurement_sha256": {
            (
                str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
            ): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                ROOT / "benchmarks/run.py",
                ROOT / "benchmarks/telemetry.py",
                ROOT / "benchmarks/reporting.py",
                ROOT / "benchmarks/corpus.py",
                arguments.tasks.resolve(),
            )
        },
        "output_directory": str(output),
        "preflight_runs": [],
        "methodology": {
            "repositories": "Two synthetic multi-module Python/TypeScript maintenance fixtures; external hidden oracles",
            "isolation": "Fresh detached Git worktree from the same per-language seed commit for every run",
            "prompt": COMMON_INSTRUCTIONS,
            "settings": "Same model, effort, output schema, sandbox and tool instructions; only Memglide MCP availability differs",
            "caching": "Fresh process/session/index per run; counterbalanced arm order. OS and provider caches are not flushable; cached input is recorded when exposed",
            "timing": "wall_time_seconds measures Codex process; B index timing is separate and included in end_to_end_wall_seconds. Independent readiness probes are excluded",
            "cost": "Actual cost and model-call count remain null unless provider telemetry exposes them; no token-price estimate is actual cost",
            "overhead": "Linux /proc samples local child processes; remote model resources unavailable",
            "failed_runs": "All planned rows and attempted failures retained; common preflight blockers stop pointless repeats",
        },
    }
    repositories = create_repositories(output, tasks)
    metadata["repositories"] = repositories
    runs = []
    blocker = None
    if not arguments.skip_preflight:
        artifacts = output / "preflight"
        worktree = output / "worktrees" / "preflight"
        create_worktree(next(iter(repositories.values())), worktree)
        command = codex_command(
            arguments.codex,
            worktree,
            schema,
            artifacts / "final.json",
            arguments.model,
            arguments.effort,
        )
        preflight = execute_codex(
            command,
            "Return a brief readiness summary and an empty tests_run array. Do not edit files or invoke tools.",
            worktree,
            artifacts,
            arguments.timeout,
            environment,
        )
        preflight["artifacts"] = str(artifacts)
        preflight["scope"] = (
            "Readiness request, excluded from task comparisons; usage retained separately"
        )
        metadata["preflight_runs"].append(preflight)
        if preflight["exit_code"] != 0 or not preflight["telemetry"].get("completed_turns"):
            diagnosis = common_blocker(preflight, artifacts) or "preflight_failed"
            blocker = f"Codex preflight failed ({diagnosis}); inspect {artifacts / 'stderr.log'} and events.jsonl"
            metadata["blockers"] = [blocker]
    task_map = {task["id"]: task for task in tasks}
    for row in plan:
        if blocker:
            result = not_run(row, blocker)
        else:
            print(f"[{row['order']}/{len(plan)}] {row['run_id']}", flush=True)
            result = run_task(
                row,
                task_map[row["task_id"]],
                repositories[row["language"]],
                output,
                schema,
                arguments,
                environment,
            )
            if result.get("common_blocker"):
                blocker = "Confirmed shared runtime blocker: " + result["common_blocker"]
                metadata["blockers"] = [blocker]
        runs.append(result)
        write_json(output / "runs.json", runs)
    metadata["finished_at"] = utc_now()
    metadata["memglide_source_after"] = capture_provenance(ROOT)
    metadata["source_unchanged_during_experiment"] = (
        metadata["memglide_source_before"]["source_tree_sha256"]
        == metadata["memglide_source_after"]["source_tree_sha256"]
    )
    write_json(output / "metadata.json", metadata)
    from benchmarks.reporting import build_report, write_report

    report = build_report(runs, tasks, metadata)
    write_report(report, output / "report.json", output / "report.md")
    print(f"Reports: {output / 'report.md'} and {output / 'report.json'}", flush=True)
    return 2 if blocker else int(any(run["status"] == "harness_error" for run in runs))


if __name__ == "__main__":
    raise SystemExit(main())
