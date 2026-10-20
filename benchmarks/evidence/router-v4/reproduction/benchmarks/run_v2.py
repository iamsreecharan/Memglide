"""Durable, frozen 40-task Codex A/B experiment with compact Memglide tools.

Every original assignment survives interruption. Resume never overwrites an
attempt, and optional retries are supplemental observations, not replacements.
Model requests are made only by invoking this module, never on import.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from benchmarks import run as legacy
from benchmarks.compare_components import capture_provenance
from benchmarks.reporting import build_report, write_report
from benchmarks.telemetry import parse_codex_jsonl

ROOT = legacy.ROOT
COMMON_INSTRUCTIONS = """Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.
If Memglide MCP tools are available, use fetch_context once with your task query before editing. Reuse complete returned source instead of reading it again unless additional evidence is needed. Use verify_context only if you are uncertain whether another process changed the source or need to validate older context before using it again. Your own edits make earlier context stale; a final verification is not required. Otherwise use ordinary source tools. Do not claim token or cost savings.
"""
STRICT_COMMON_INSTRUCTIONS = """Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.
If Memglide MCP tools are available, use fetch_context once with your task query before editing. Reuse complete returned source instead of reading it again unless additional evidence is needed. Use verify_context once after editing; stale context caused by your edits is expected and does not require fetching again unless you need more evidence. Otherwise use ordinary source tools. Do not claim token or cost savings.
"""
APPROVED_TOOLS = ("fetch_context", "verify_context")
REPOSITORIES = {
    "ledger-python-v2": "python",
    "workflow-python-v2": "python",
    "stream-typescript-v2": "typescript",
    "config-typescript-v2": "typescript",
}
TERMINAL = {
    "completed",
    "failed",
    "timeout",
    "execution_failed",
    "invalid_treatment",
    "harness_error",
    "interrupted",
    "blocked",
}


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: Any, *, immutable: bool = False) -> None:
    """Install a complete, fsynced document; immutable records cannot replace one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.pending"
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if immutable:
            os.link(temporary, path)
            temporary.unlink()
        else:
            os.replace(temporary, path)
        _sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def experiment_lock(output: Path) -> Iterator[None]:
    """An OS lock dies with the launcher; a stale PID file cannot prevent resume."""
    with (output / ".runner.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another runner owns this output directory") from error
        yield


def read_log(output: Path) -> list[dict[str, Any]]:
    records = []
    previous = None
    for sequence, path in enumerate(sorted((output / "attempt-log").glob("*.json")), 1):
        record = json.loads(path.read_text())
        recorded_digest = record.get("sha256")
        body = {key: value for key, value in record.items() if key != "sha256"}
        if (
            path.name != f"{sequence:06d}.json"
            or body.get("sequence") != sequence
            or body.get("previous_sha256") != previous
            or digest(canonical(body)) != recorded_digest
        ):
            raise ValueError(f"Immutable attempt log integrity failure at {path.name}")
        records.append(record)
        previous = recorded_digest
    return records


def append_log(output: Path, event: str, **data: Any) -> dict[str, Any]:
    records = read_log(output)
    body = {
        "sequence": len(records) + 1,
        "previous_sha256": records[-1]["sha256"] if records else None,
        "recorded_at": legacy.utc_now(),
        "event": event,
        **data,
    }
    record = {**body, "sha256": digest(canonical(body))}
    atomic_json(output / "attempt-log" / f"{body['sequence']:06d}.json", record, immutable=True)
    return record


def common_instructions(require_verification: bool = False) -> str:
    return STRICT_COMMON_INSTRUCTIONS if require_verification else COMMON_INSTRUCTIONS


def task_prompt(task: dict[str, Any], require_verification: bool = False) -> str:
    return common_instructions(require_verification) + "\nTask:\n" + task["prompt"] + "\n"


def required_operations(require_verification: bool = False) -> list[str]:
    return ["fetch_context", "verify_context"] if require_verification else ["fetch_context"]


def load_tasks(path: Path, corpus: str = "v2") -> list[dict[str, Any]]:
    tasks = legacy.load_tasks(path)
    for task in tasks:
        repository: Any = task.get("repository")
        if corpus == "v2" and REPOSITORIES.get(repository) != task["language"]:
            raise ValueError(f"Unknown or language-mismatched repository: {repository!r}")
        if not isinstance(task.get("prompt"), str) or not task["prompt"].strip():
            raise ValueError("Each task needs a nonempty prompt")
    return tasks


def make_plan(tasks: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    repositories = {task["id"]: task["repository"] for task in tasks}
    return [
        {**row, "repository": repositories[row["task_id"]]}
        for row in legacy.make_plan(tasks, repeats, seed)
    ]


def codex_command(
    executable: str,
    worktree: Path,
    schema: Path,
    final: Path,
    model: str,
    effort: str,
    database: Path | None = None,
    project_id: str | None = None,
) -> list[str]:
    # Reuse the supported native exec/output schema and safe sandbox flags.
    command = legacy.codex_command(executable, worktree, schema, final, model, effort)[:-3]
    command += ["-c", 'approval_policy="never"']
    if database is None:
        config = "mcp_servers={}"
    else:
        if not isinstance(project_id, str) or not project_id:
            raise ValueError("The compact MCP profile requires the registered project ID")
        launcher = str(ROOT / ".venv" / "bin" / "memglide")
        tool_policies = ",".join(tool + '={approval_mode="approve"}' for tool in APPROVED_TOOLS)
        config = (
            "mcp_servers={memglide={command="
            + json.dumps(launcher)
            + ",args="
            + json.dumps(
                [
                    "--db",
                    str(database),
                    "mcp",
                    "--profile",
                    "agent",
                    "--project",
                    project_id,
                ]
            )
            + ',required=true,startup_readiness="connection",startup_timeout_sec=30.0'
            + ",tool_timeout_sec=45.0,enabled_tools="
            + json.dumps(APPROVED_TOOLS)
            + ",tools={"
            + tool_policies
            + "}}}"
        )
    return command + ["-c", config, "-"]


def frozen_manifest(
    tasks_path: Path, tasks: list[dict[str, Any]], settings: dict[str, Any]
) -> dict[str, Any]:
    paths = set((ROOT / "src/memglide").rglob("*.py"))
    paths.update(
        ROOT / name
        for name in (
            "benchmarks/run_v2.py",
            "benchmarks/run.py",
            "benchmarks/telemetry.py",
            "benchmarks/reporting.py",
            "benchmarks/compare_components.py",
            "benchmarks/context_audit_v2.py",
            "pyproject.toml",
            "uv.lock",
        )
    )
    paths.add(
        ROOT
        / (
            "benchmarks/corpus.py"
            if settings.get("corpus") == "legacy"
            else "benchmarks/corpus_v2.py"
        )
    )
    paths.add(tasks_path.resolve())
    files = {}
    for path in sorted(paths):
        if path.is_symlink():
            raise ValueError(f"Frozen source must not be a symlink: {path.name}")
        key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        files[key] = digest(path.read_bytes())
    return {
        "git_head": legacy.git(ROOT, "rev-parse", "HEAD"),
        "files": files,
        "settings": settings,
        "prompt_sha256": {
            task["id"]: digest(
                task_prompt(task, settings.get("require_verification", False)).encode()
            )
            for task in tasks
        },
        "common_instructions_sha256": digest(
            common_instructions(settings.get("require_verification", False)).encode()
        ),
    }


def validate_frozen(metadata: dict[str, Any], current: dict[str, Any]) -> None:
    if metadata["frozen_manifest"] != current:
        raise ValueError(
            "Experiment source, commit, tasks, prompts or settings changed; resume refused"
        )


def create_repositories(
    output: Path,
    tasks: list[dict[str, Any]],
    corpus: str = "v2",
    existing: dict[str, dict[str, str]] | None = None,
    persist: Any = None,
) -> dict[str, dict[str, str]]:
    build_repository: Callable[[str, Path], None]
    if corpus == "legacy":
        from benchmarks.corpus import build_repository as build_legacy_repository

        build_repository = build_legacy_repository
    else:
        from benchmarks.corpus_v2 import build_repository as build_v2_repository

        build_repository = build_v2_repository

    repositories = dict(existing or {})
    for repository_id in sorted({task["repository"] for task in tasks}):
        if repository_id in repositories:
            continue
        destination = output / "repositories" / repository_id
        if destination.exists():
            # No requests can have used an uncommitted initial fixture. Retain it
            # separately and construct a new fixed repository; never delete it.
            retained = output / "initialization-partials" / f"{repository_id}-{uuid.uuid4().hex}"
            retained.parent.mkdir(parents=True, exist_ok=True)
            destination.rename(retained)
        destination.mkdir(parents=True, exist_ok=False)
        key = (
            next(task["language"] for task in tasks if task["repository"] == repository_id)
            if corpus == "legacy"
            else repository_id
        )
        build_repository(key, destination)
        legacy.git(destination, "init", "--initial-branch=benchmark")
        legacy.git(destination, "config", "user.name", "Memglide Benchmark Fixture")
        legacy.git(destination, "config", "user.email", "benchmark@example.invalid")
        legacy.git(destination, "add", ".")
        legacy.git(
            destination, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Frozen V2 fixture"
        )
        repositories[repository_id] = {
            "path": str(destination),
            "commit": legacy.git(destination, "rev-parse", "HEAD"),
            "tree": legacy.git(destination, "rev-parse", "HEAD^{tree}"),
        }
        if persist:
            persist(repositories)
    return repositories


def verify_repositories(repositories: dict[str, dict[str, str]]) -> None:
    for repository in repositories.values():
        directory = Path(repository["path"])
        if (
            legacy.git(directory, "rev-parse", "HEAD") != repository["commit"]
            or legacy.git(directory, "rev-parse", "HEAD^{tree}") != repository["tree"]
            or legacy.git(directory, "status", "--porcelain")
        ):
            raise ValueError("A frozen fixture repository changed; resume refused")


def pending(row: dict[str, Any]) -> dict[str, Any]:
    return {**legacy.not_run(row, "Pending original assignment"), "pending": True}


def checkpoint(output: Path, state: dict[str, Any], metadata: dict[str, Any]) -> None:
    """state.json is authoritative; convenient projections can be rebuilt on resume."""
    atomic_json(output / "state.json", state)
    atomic_json(output / "runs.json", list(state["originals"].values()))
    atomic_json(output / "supplemental-runs.json", state["supplemental"])
    atomic_json(output / "metadata.json", metadata)


# No request starts until the child identity is durable AND the parent grants
# launch. A delayed wrapper whose launcher died cannot begin a request later.
PROCESS_WRAPPER = """import json,os,sys,time
from pathlib import Path
record=Path(sys.argv[1]);temporary=record.with_name('.process-identity-'+str(os.getpid())+'.pending')
fields=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()
body={'pid':os.getpid(),'process_group':os.getpgrp(),'start_ticks':int(fields[19])}
with temporary.open('x') as stream:
    json.dump(body,stream);stream.flush();os.fsync(stream.fileno())
os.link(temporary,record);temporary.unlink()
descriptor=os.open(record.parent,os.O_RDONLY|os.O_DIRECTORY)
os.fsync(descriptor);os.close(descriptor)
grant=record.with_name('launch-grant.json');deadline=time.monotonic()+float(sys.argv[2])
while not grant.exists():
    if time.monotonic()>=deadline:sys.exit(125)
    time.sleep(0.01)
approval=json.loads(grant.read_text())
if approval!=body:sys.exit(126)
os.execvpe(sys.argv[3],sys.argv[3:],os.environ)
"""


def execute_codex(
    command: list[str],
    prompt: str,
    worktree: Path,
    artifacts: Path,
    timeout: float,
    environment: dict[str, str],
) -> dict[str, Any]:
    """Native supported JSON exec with fresh auth binding and durable child identity."""
    artifacts.mkdir(parents=True, exist_ok=True)
    with (artifacts / "prompt.txt").open("x", encoding="utf-8") as stream:
        stream.write(prompt)
    atomic_json(artifacts / "command.json", command, immutable=True)
    child_environment = environment.copy()
    child_environment["CODEX_HOME"] = str(
        legacy.isolated_codex_state(artifacts / "codex-state", environment)
    )
    started, timed_out = time.perf_counter(), False
    with (
        (artifacts / "events.jsonl").open("x") as stdout,
        (artifacts / "stderr.log").open("x") as stderr,
    ):
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                PROCESS_WRAPPER,
                str(artifacts / "process-identity.json"),
                "10",
                *command,
            ],
            cwd=worktree,
            env=child_environment,
            stdin=subprocess.PIPE,
            stdout=stdout,
            stderr=stderr,
            text=True,
            start_new_session=True,
        )
        sampler = legacy.ProcessSampler(process.pid)
        sampler.start()
        try:
            identity_path = artifacts / "process-identity.json"
            while not identity_path.exists() and process.poll() is None:
                if time.perf_counter() - started >= min(timeout, 5):
                    raise subprocess.TimeoutExpired(command, timeout)
                time.sleep(0.01)
            if identity_path.exists():
                identity = json.loads(identity_path.read_text())
                if (
                    identity.get("pid") != process.pid
                    or identity.get("process_group") != process.pid
                ):
                    raise ValueError(
                        "Child launch identity did not match its private process group"
                    )
                atomic_json(artifacts / "launch-grant.json", identity, immutable=True)
            process.communicate(
                prompt, timeout=max(0.001, timeout - (time.perf_counter() - started))
            )
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
        finally:
            overhead = sampler.finish()
    return {
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "wall_time_seconds": time.perf_counter() - started,
        "overhead": overhead,
        "telemetry": parse_codex_jsonl(artifacts / "events.jsonl"),
    }


def stop_orphan(artifacts: Path) -> bool:
    """Stop only the exact recorded private process group, never a reused PID."""
    path = artifacts / "process-identity.json"
    if not path.exists():
        return False  # An ungranted delayed wrapper exits without starting a request.
    identity = json.loads(path.read_text())
    pid = identity["pid"]
    if (
        not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid <= 1
        or identity["process_group"] != pid
    ):
        raise ValueError("Unsafe recorded process identity")
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        if int(fields[19]) != identity["start_ticks"]:
            return False
        if os.getpgid(pid) != pid:
            raise ValueError("Recorded process no longer owns its private process group")
        os.killpg(pid, signal.SIGTERM)
    except (FileNotFoundError, ProcessLookupError):
        return False
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            if int(fields[19]) != identity["start_ticks"] or fields[0] == "Z":
                return True
        except FileNotFoundError:
            return True
        time.sleep(0.05)
    os.killpg(pid, signal.SIGKILL)
    return True


def begin_attempt(
    output: Path,
    row: dict[str, Any],
    state: dict[str, Any],
    metadata: dict[str, Any],
    *,
    supplemental: bool = False,
) -> dict[str, Any]:
    original_id = row["run_id"]
    if supplemental:
        number = 1 + sum(
            result.get("original_run_id") == original_id for result in state["supplemental"]
        )
        attempt_id = f"{original_id}-supplemental-{number}"
    else:
        attempt_id = original_id
    artifacts = output / "runs" / attempt_id
    artifacts.mkdir(parents=True, exist_ok=False)
    result = {
        **row,
        "run_id": attempt_id,
        "original_run_id": original_id,
        "supplemental": supplemental,
        "status": "running",
        "attempted": True,
        "pending": False,
        "started_at": legacy.utc_now(),
        "artifacts": str(artifacts),
        "worktree": str(output / "worktrees" / attempt_id),
        "errors": [],
        "grader": {"success": None, "reason": "Attempt is not yet graded"},
        "actual_cost_usd": None,
        "computed_cost_usd": None,
    }
    if row["configuration"] == "B":
        require_verification = (
            metadata.get("frozen_manifest", {})
            .get("settings", {})
            .get("require_verification", False)
        )
        result["compact_protocol_fidelity"] = {
            "valid": None,
            "required_operations": required_operations(require_verification),
            "verification_policy": "required_after_edits" if require_verification else "on_demand",
        }
    atomic_json(artifacts / "attempt-start.json", result, immutable=True)
    append_log(
        output,
        "attempt.started",
        attempt_id=attempt_id,
        original_run_id=original_id,
        supplemental=supplemental,
        start_sha256=digest(canonical(result)),
    )
    if supplemental:
        state["supplemental"].append(result)
    else:
        state["originals"][original_id] = result
    metadata["last_checkpoint_at"] = legacy.utc_now()
    checkpoint(output, state, metadata)
    return result


def recover_interrupted(output: Path, state: dict[str, Any], metadata: dict[str, Any]) -> None:
    """Retain partial native streams and reconcile crashes between result and checkpoint."""
    for directory in sorted((output / "runs").glob("*")):
        if directory.is_dir() and not (directory / "attempt-start.json").exists():
            if any(
                path.name in {"events.jsonl", "stderr.log", "result.json"}
                for path in directory.iterdir()
            ):
                raise ValueError("Attempt files exist without their durable start record")
            retained = output / "initialization-partials" / f"{directory.name}-{uuid.uuid4().hex}"
            retained.parent.mkdir(parents=True, exist_ok=True)
            directory.rename(retained)
    # A crash can occur after an immutable start record but before the state
    # projection. Recover that attempt before assigning any new artifact path.
    known = {row["run_id"] for row in state["originals"].values() if row["attempted"]}
    known.update(row["run_id"] for row in state["supplemental"])
    for start in sorted((output / "runs").glob("*/attempt-start.json")):
        candidate = json.loads(start.read_text())
        if candidate.get("run_id") in known:
            continue
        original_id = candidate.get("original_run_id")
        if original_id not in state["originals"]:
            raise ValueError("Orphan attempt does not identify a planned assignment")
        if Path(candidate.get("artifacts", "")).resolve() != start.parent.resolve():
            raise ValueError("Orphan attempt has a conflicting artifact pointer")
        if candidate.get("supplemental"):
            state["supplemental"].append(candidate)
        elif state["originals"][original_id].get("pending"):
            state["originals"][original_id] = candidate
        else:
            raise ValueError("Orphan attempt conflicts with an existing original observation")
        known.add(candidate["run_id"])
    attempts = list(state["originals"].values()) + state["supplemental"]
    logged_finishes = {
        row["attempt_id"] for row in read_log(output) if row["event"] == "attempt.finished"
    }
    for record in read_log(output):
        if record["event"] in {"attempt.finished", "attempt.interrupted"}:
            path = output / "runs" / record["attempt_id"] / "result.json"
            if digest(path.read_bytes()) != record["result_sha256"]:
                raise ValueError("A sealed attempt result changed; resume refused")
    for attempt in attempts:
        if attempt["status"] != "running":
            continue
        artifacts = Path(attempt["artifacts"])
        if stop_orphan(artifacts):
            append_log(output, "attempt.orphan_stopped", attempt_id=attempt["run_id"])
        saved_result = artifacts / "result.json"
        if saved_result.exists():
            recovered = json.loads(saved_result.read_text())
            if (
                recovered.get("run_id") != attempt["run_id"]
                or recovered.get("status") not in TERMINAL
            ):
                raise ValueError("Partial result does not identify a terminal attempt")
            attempt.clear()
            attempt.update(recovered)
            if attempt["run_id"] not in logged_finishes:
                append_log(
                    output,
                    "attempt.finished",
                    attempt_id=attempt["run_id"],
                    result_sha256=digest(saved_result.read_bytes()),
                    recovered=True,
                )
            continue
        attempt["status"] = "interrupted"
        attempt["finished_at"] = legacy.utc_now()
        attempt["errors"].append(
            "Launcher interrupted; original outcome and complete usage are unknown"
        )
        stream = artifacts / "events.jsonl"
        attempt["telemetry"] = parse_codex_jsonl(stream) if stream.exists() else {}
        # Even a terminal-looking stream cannot attest command exit, protected files,
        # or independent grade after an unobserved launcher death.
        telemetry = attempt["telemetry"]
        telemetry["usage"] = {
            key: None for key in ("input_tokens", "cached_input_tokens", "output_tokens")
        }
        telemetry["usage_coverage_complete"] = False
        telemetry["mcp_counts_complete"] = False
        telemetry["usage_unavailable_reasons"] = {
            key: "Launcher interrupted before durable completion; observed completed-turn usage is retained separately"
            for key in telemetry["usage"]
        }
        if attempt["configuration"] == "B":
            attempt["compact_protocol_fidelity"] = {
                **attempt.get("compact_protocol_fidelity", {}),
                "valid": None,
                "evidence": "Interrupted invocation results only; complete protocol is unknown",
            }
        attempt["execution_outcome_unknown"] = True
        attempt["grader"] = {
            "success": None,
            "reason": "Interrupted before durable independent grade",
        }
        atomic_json(saved_result, attempt, immutable=True)
        append_log(
            output,
            "attempt.interrupted",
            attempt_id=attempt["run_id"],
            result_sha256=digest(saved_result.read_bytes()),
        )
    metadata["resume_count"] = metadata.get("resume_count", 0) + 1
    checkpoint(output, state, metadata)


def run_attempt(
    attempt: dict[str, Any],
    task: dict[str, Any],
    repository: dict[str, str],
    output: Path,
    arguments: argparse.Namespace,
    environment: dict[str, str],
) -> dict[str, Any]:
    if arguments.corpus == "legacy":
        from benchmarks.corpus import grade
    else:
        from benchmarks.corpus_v2 import grade

    result = {**attempt, "errors": list(attempt["errors"])}
    artifacts, worktree = Path(attempt["artifacts"]), Path(attempt["worktree"])
    result.update(
        starting_commit=repository["commit"],
        prompt_sha256=digest(task_prompt(task, arguments.require_verification).encode()),
    )
    try:
        legacy.create_worktree(repository, worktree)
        snapshot = legacy.protection_snapshot(worktree)
        database = artifacts / "memglide.db" if attempt["configuration"] == "B" else None
        if database is not None:
            result["setup"] = legacy.prepare_memglide(worktree, database, task)
        command = codex_command(
            arguments.codex,
            worktree,
            output / "final-response-schema.json",
            artifacts / "final.json",
            arguments.model,
            arguments.effort,
            database,
            result.get("setup", {}).get("project_id"),
        )
        # execute_codex opens only fresh files in this never-reused attempt directory.
        result.update(
            execute_codex(
                command,
                task_prompt(task, arguments.require_verification),
                worktree,
                artifacts,
                arguments.timeout,
                environment,
            )
        )
        # This independent observation happens after the coding process exits;
        # source mismatch from the model's own edits is expected, not a grade
        # failure or evidence that context was stale when originally retrieved.
        from benchmarks.context_audit_v2 import capture_snapshot

        audit_started, audit_cpu_started = time.perf_counter(), time.process_time()
        try:
            result["post_execution_context_audit"] = capture_snapshot(
                artifacts / "events.jsonl",
                worktree,
                artifacts / "post-execution-source-audit.json",
            )
        except Exception as error:
            result["post_execution_context_audit"] = {
                "available": False,
                "error_type": type(error).__name__,
                "scope": "Independent post-execution source comparison unavailable",
            }
            result["errors"].append("Independent post-execution source audit unavailable")
        result["post_execution_audit_wall_seconds"] = time.perf_counter() - audit_started
        result["post_execution_audit_cpu_seconds"] = time.process_time() - audit_cpu_started
        violations = legacy.check_protection(worktree, snapshot, repository["commit"])
        result["protected_file_violations"] = violations
        legacy.preserve_changes(worktree, artifacts, repository["commit"])
        result["grader"] = grade(task["id"], worktree, artifacts)
        telemetry = result["telemetry"]
        if database is not None:
            result["treatment_valid"] = (
                telemetry.get("memglide_successful_fetch_context_count") or 0
            ) > 0 and (
                not arguments.require_verification
                or (telemetry.get("memglide_successful_verify_context_count") or 0) > 0
            )
            result["compact_protocol_fidelity"] = {
                "valid": result["treatment_valid"],
                "required_operations": required_operations(arguments.require_verification),
                "verification_policy": "required_after_edits"
                if arguments.require_verification
                else "on_demand",
                "successful_fetch_context_calls": telemetry.get(
                    "memglide_successful_fetch_context_count"
                ),
                "successful_verify_context_calls": telemetry.get(
                    "memglide_successful_verify_context_count"
                ),
                "evidence": "Parsed actual MCP invocation results; not the final model summary",
            }
        else:
            result["treatment_valid"] = (
                telemetry.get("mcp_call_count") == 0
                and telemetry.get("mcp_counts_complete") is True
                and telemetry.get("completed_turns", 0) > 0
            )
        if violations:
            result["grader"]["success"] = False
            result["errors"].append("Protected tests or Git metadata changed")
        if result["timed_out"]:
            result["status"] = "timeout"
        elif result["exit_code"] != 0:
            result["status"] = "execution_failed"
        elif not result["treatment_valid"]:
            result["status"] = "invalid_treatment"
            result["errors"].append(
                "Required MCP operation evidence did not match the frozen arm policy"
            )
        elif not result["grader"].get("success"):
            result["status"] = "failed"
        else:
            result["status"] = "completed"
        result["common_blocker"] = legacy.common_blocker(result, artifacts)
    except Exception as error:
        result["status"] = "harness_error"
        result["errors"].append(f"{type(error).__name__}: {error}")
        result.setdefault("grader", {"success": None, "reason": "Harness did not finish grading"})
    result["finished_at"] = legacy.utc_now()
    result["end_to_end_wall_seconds"] = (
        result["wall_time_seconds"] + result.get("setup", {}).get("index_wall_seconds", 0)
        if result.get("wall_time_seconds") is not None
        else None
    )
    atomic_json(artifacts / "result.json", result, immutable=True)
    return result


def finish_attempt(
    output: Path, result: dict[str, Any], state: dict[str, Any], metadata: dict[str, Any]
) -> None:
    append_log(
        output,
        "attempt.finished",
        attempt_id=result["run_id"],
        result_sha256=digest((Path(result["artifacts"]) / "result.json").read_bytes()),
    )
    if result["supplemental"]:
        index = next(
            i for i, row in enumerate(state["supplemental"]) if row["run_id"] == result["run_id"]
        )
        state["supplemental"][index] = result
    else:
        state["originals"][result["original_run_id"]] = result
    metadata["last_checkpoint_at"] = legacy.utc_now()
    checkpoint(output, state, metadata)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--tasks", type=Path, default=ROOT / "benchmarks/tasks_v2.json")
    result.add_argument("--corpus", choices=("v2", "legacy"), default="v2")
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--model", default="gpt-6.1-sol")
    result.add_argument("--effort", default="low")
    result.add_argument("--codex", default=shutil.which("codex") or "codex")
    result.add_argument("--codex-home", type=Path)
    result.add_argument("--repeats", type=int, default=2)
    result.add_argument("--timeout", type=float, default=180)
    result.add_argument("--seed", type=int, default=20261017)
    result.add_argument("--limit", type=int)
    result.add_argument("--skip-preflight", action="store_true")
    result.add_argument(
        "--require-verification",
        action="store_true",
        help="Explicit two-call ablation: require fetch_context and verify_context; default verifies on demand",
    )
    result.add_argument("--resume", action="store_true")
    result.add_argument(
        "--retry-interrupted",
        action="store_true",
        help="Supplemental retries; interrupted originals remain in the primary report",
    )
    return result


def run_experiment(arguments: argparse.Namespace, output: Path) -> int:
    tasks = load_tasks(arguments.tasks, arguments.corpus)
    if arguments.limit:
        tasks = tasks[: arguments.limit]
    codex_version = subprocess.check_output([arguments.codex, "--version"], text=True).strip()
    settings = {
        "model": arguments.model,
        "effort": arguments.effort,
        "repeats": arguments.repeats,
        "timeout": arguments.timeout,
        "seed": arguments.seed,
        "limit": arguments.limit,
        "codex_executable": str(Path(shutil.which(arguments.codex) or arguments.codex).resolve()),
        "codex_home_binding_directory": str(arguments.codex_home.resolve())
        if arguments.codex_home
        else None,
        "skip_preflight": arguments.skip_preflight,
        "corpus": arguments.corpus,
        "codex_version": codex_version,
        "require_verification": arguments.require_verification,
    }
    frozen = frozen_manifest(arguments.tasks, tasks, settings)
    environment = os.environ.copy()
    if arguments.codex_home:
        environment["CODEX_HOME"] = str(arguments.codex_home.resolve())
    environment.update({"NO_COLOR": "1", "CI": "1", "MEMGLIDE_HOME": str(output / "state")})
    plan = make_plan(tasks, arguments.repeats, arguments.seed)
    if arguments.resume:
        metadata = json.loads((output / "metadata.json").read_text())
        validate_frozen(metadata, frozen)
        read_log(output)
        verify_repositories(metadata.get("repositories", {}))
        state = json.loads((output / "state.json").read_text())
        if metadata.get("finished_at") and (output / "report.json").exists():
            if arguments.retry_interrupted:
                raise ValueError(
                    "Finished reports are preserved; supplemental retries must be selected on the first resume"
                )
            print(f"Existing completed report retained: {output / 'report.json'}", flush=True)
            return 2 if metadata.get("shared_blocker") else 0
        recover_interrupted(output, state, metadata)
    else:
        metadata = {
            "started_at": legacy.utc_now(),
            "experiment_version": 2,
            "model": arguments.model,
            "reasoning_effort": arguments.effort,
            "repeats": arguments.repeats,
            "repetitions": arguments.repeats,
            "random_seed": arguments.seed,
            "output_directory": str(output),
            "frozen_manifest": frozen,
            "memglide_source_before": capture_provenance(ROOT),
            "preflight_runs": [],
            "resume_count": 0,
            "codex_version": codex_version,
            **legacy.host_metadata(),
            "methodology": {
                "repositories": "Four new multi-module fixtures; ten tasks per fixture; independent external graders"
                if arguments.corpus == "v2"
                else "Development pilot on the earlier two-fixture corpus; excluded from the fresh 40-task experiment",
                "isolation": "Fresh worktree from each task's frozen repository commit, process/session/database per arm",
                "prompt": common_instructions(arguments.require_verification),
                "settings": "Same model, effort, schema, workspace-write sandbox, global approval never and common prompt; only scoped MCP availability differs",
                "caching": "Counterbalanced paired order reverses on repeat 2; fresh local state. Provider/OS caches cannot be reset; cached tokens are observed separately",
                "timing": "CLI wall time plus B's required fresh index equals end-to-end time; external graders/readiness excluded",
                "cost": "No invoice/cost or underlying model-call telemetry is estimated",
                "context_audit": "Independent source-file hash snapshot after Codex exit and before grader/build mutations; a point observation, not call-time freshness or semantic completeness. Own-edit mismatches do not fail coding grades. Audit time is recorded separately outside Codex timing",
                "durability": "Atomic fsynced checkpoints and immutable hash-chained attempt log; interrupted originals retained; distinct supplemental retries excluded from original comparison",
                "treatment": "B requires actual compact source retrieval. Verification is "
                + (
                    "required by the explicit two-call ablation"
                    if arguments.require_verification
                    else "optional and on demand"
                )
                + "; invocation evidence does not establish chronology relative to final edits. A has no configured MCP servers",
            },
        }
        state = {"originals": {row["run_id"]: pending(row) for row in plan}, "supplemental": []}
        atomic_json(output / "plan.json", {"tasks": tasks, "runs": plan}, immutable=True)
        atomic_json(output / "final-response-schema.json", legacy.OUTPUT_SCHEMA, immutable=True)
        checkpoint(output, state, metadata)  # Before fixture setup or any model request.
        append_log(output, "experiment.created", frozen_manifest_sha256=digest(canonical(frozen)))

    def persist_repositories(repositories: dict[str, dict[str, str]]) -> None:
        metadata["repositories"] = repositories
        checkpoint(output, state, metadata)

    metadata["repositories"] = create_repositories(
        output,
        tasks,
        arguments.corpus,
        metadata.get("repositories"),
        persist_repositories,
    )
    checkpoint(output, state, metadata)

    repositories = metadata["repositories"]
    blocker = metadata.get("shared_blocker")
    if not arguments.skip_preflight and not metadata.get("preflight_complete") and not blocker:
        artifacts = output / "preflight"
        if (artifacts / "result.json").exists():
            preflight = json.loads((artifacts / "result.json").read_text())
            metadata["preflight_runs"].append(preflight)
            metadata["preflight_complete"] = True
            if preflight["exit_code"] != 0 or not preflight["telemetry"].get("completed_turns"):
                blocker = "Recovered failed preflight; preserve original evidence"
            checkpoint(output, state, metadata)
        elif artifacts.exists() or metadata.get("preflight_started_at"):
            # An interrupted readiness request is retained, not retried implicitly.
            if stop_orphan(artifacts):
                append_log(output, "preflight.orphan_stopped")
            blocker = "Interrupted preflight; preserve evidence and use a fresh experiment"
        else:
            metadata["preflight_started_at"] = legacy.utc_now()
            checkpoint(output, state, metadata)
            legacy.create_worktree(
                next(iter(repositories.values())), output / "worktrees/preflight"
            )
            command = codex_command(
                arguments.codex,
                output / "worktrees/preflight",
                output / "final-response-schema.json",
                artifacts / "final.json",
                arguments.model,
                arguments.effort,
            )
            preflight = execute_codex(
                command,
                "Return a brief readiness summary and an empty tests_run array. Do not edit files or invoke tools.",
                output / "worktrees/preflight",
                artifacts,
                arguments.timeout,
                environment,
            )
            preflight.update(
                artifacts=str(artifacts), scope="Readiness only; excluded from task comparison"
            )
            atomic_json(artifacts / "result.json", preflight, immutable=True)
            metadata["preflight_runs"].append(preflight)
            metadata["preflight_complete"] = True
            if preflight["exit_code"] != 0 or not preflight["telemetry"].get("completed_turns"):
                blocker = "Codex preflight failed: " + (
                    legacy.common_blocker(preflight, artifacts) or "preflight_failed"
                )
            checkpoint(output, state, metadata)

    task_map = {task["id"]: task for task in tasks}
    original_queue = [row for row in plan if state["originals"][row["run_id"]].get("pending")]
    retry_queue = (
        [row for row in plan if state["originals"][row["run_id"]]["status"] == "interrupted"]
        if arguments.retry_interrupted
        else []
    )
    for supplemental, queue in ((False, original_queue), (True, retry_queue)):
        for row in queue:
            if blocker:
                if not supplemental:
                    state["originals"][row["run_id"]] = legacy.not_run(row, blocker)
                continue
            try:
                validate_frozen(metadata, frozen_manifest(arguments.tasks, tasks, settings))
                verify_repositories(repositories)
            except ValueError as error:
                blocker = str(error)
                if not supplemental:
                    state["originals"][row["run_id"]] = legacy.not_run(row, blocker)
                continue
            print(
                f"[{row['order']}/{len(plan)}] {row['run_id']}"
                + (" supplemental" if supplemental else ""),
                flush=True,
            )
            attempt = begin_attempt(output, row, state, metadata, supplemental=supplemental)
            result = run_attempt(
                attempt,
                task_map[row["task_id"]],
                repositories[row["repository"]],
                output,
                arguments,
                environment,
            )
            try:
                validate_frozen(metadata, frozen_manifest(arguments.tasks, tasks, settings))
            except ValueError as error:
                blocker = str(error)
                metadata["source_guard_failure"] = blocker
            finish_attempt(output, result, state, metadata)
            if result.get("common_blocker"):
                blocker = "Confirmed shared runtime blocker: " + result["common_blocker"]
    if blocker:
        metadata["shared_blocker"] = blocker
        metadata["blockers"] = [blocker]
    metadata["finished_at"] = legacy.utc_now()
    metadata["memglide_source_after"] = capture_provenance(ROOT)
    metadata["source_unchanged_during_experiment"] = metadata["memglide_source_before"][
        "source_tree_sha256"
    ] == metadata["memglide_source_after"]["source_tree_sha256"] and not metadata.get(
        "source_guard_failure"
    )
    metadata["supplemental_attempt_count"] = len(state["supplemental"])
    checkpoint(output, state, metadata)
    report = build_report(list(state["originals"].values()), tasks, metadata)
    report["supplemental_runs"] = state["supplemental"]
    report["limitations"].append(
        "Supplemental retries never replace interrupted original assignments or enter the primary A/B aggregates. "
        "The compact fetch_context alias counts as retrieval only with observed get_context operation, nonempty source snippets and source hashes. "
        "Verification policy is frozen and explicit per run: on demand by default; --require-verification requires both calls for an ablation. Server freshness assertions are not independent semantic completeness measurements."
    )
    write_report(report, output / "report.json", output / "report.md")
    append_log(
        output, "experiment.finished", report_sha256=digest((output / "report.json").read_bytes())
    )
    print(f"Reports: {output / 'report.md'} and {output / 'report.json'}", flush=True)
    return (
        2
        if blocker
        else int(any(row["status"] == "harness_error" for row in state["originals"].values()))
    )


def main(argv: list[str] | None = None) -> int:
    argument_parser = parser()
    arguments = argument_parser.parse_args(argv)
    if (
        arguments.repeats < 1
        or arguments.timeout <= 0
        or (arguments.limit is not None and arguments.limit < 1)
    ):
        argument_parser.error("repeats, timeout and limit must be positive")
    if arguments.retry_interrupted and not arguments.resume:
        argument_parser.error("--retry-interrupted requires --resume")
    output = arguments.output.resolve()
    if arguments.resume:
        if not (output / "state.json").exists():
            argument_parser.error("No durable experiment checkpoint exists to resume")
    else:
        if output.exists():
            argument_parser.error(
                "Output already exists; use a fresh directory or explicit --resume"
            )
        output.mkdir(parents=True)
    with experiment_lock(output):
        return run_experiment(arguments, output)


if __name__ == "__main__":
    raise SystemExit(main())
