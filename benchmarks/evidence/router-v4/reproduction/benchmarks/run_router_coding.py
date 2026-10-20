"""Fresh native A/B/C coding study. Import and default planning make no requests.

Private oracle paths are used only by B and external grading. C preparation runs
in a separate child whose request cannot contain private task fields.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from itertools import permutations
from pathlib import Path
from typing import Any, TypeGuard

from benchmarks import estimate_cost as prices
from benchmarks import run as legacy
from benchmarks import run_automatic_v3 as offline
from benchmarks import run_automatic_v4 as hardened
from benchmarks import run_cost as native
from benchmarks import run_daily as common
from benchmarks import run_v2 as durable
from benchmarks.telemetry import parse_codex_jsonl

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "benchmarks/router-coding-protocol.md"
ARMS = ("A", "B", "C")
LABELS = {
    "A": "Bare native Codex",
    "B": "Oracle-known-path source-only",
    "C": "Automatic v4 source-only",
}
SETTINGS: dict[str, Any] = {
    "context_format": "compact-prefix",
    "max_context_bytes": 12000,
    "max_added_tokens": 4000,
}
MODEL, EFFORT, VERSION = "gpt-6.1-sol", "low", "codex-cli 0.159.2"
MAX_LAUNCHES = 72
TRUSTED_BOOTSTRAP = "import runpy,sys;root=sys.argv[1];sys.path[:0]=[root,root+'/src'];sys.argv=['benchmarks.run_router_coding',*sys.argv[2:]];runpy.run_module('benchmarks.run_router_coding',run_name='__main__')"
COMMON_INSTRUCTIONS = (
    common.COMMON_INSTRUCTIONS
    + "Python, Node with native TypeScript support, and the installed TypeScript compiler (tsc) are available. Use installed development tools; do not install packages from the network.\n"
)

# A Linux supervisor remains alive to kill the inherited private group on parent
# death. Its durable launch grant prevents ungranted delayed native dispatch.
PROCESS_WRAPPER = """import ctypes,os,signal,sys,subprocess
def stop_private_group(signum,frame):
    os.killpg(os.getpgrp(),signal.SIGKILL)
signal.signal(signal.SIGUSR1,stop_private_group)
parent=os.getppid()
if sys.platform!='linux':sys.exit(127)
if ctypes.CDLL(None,use_errno=True).prctl(1,signal.SIGUSR1,0,0,0)!=0:sys.exit(127)
if os.getppid()!=parent:stop_private_group(0,None)
""" + durable.PROCESS_WRAPPER.replace(
    "os.execvpe(sys.argv[3],sys.argv[3:],os.environ)",
    "child=subprocess.Popen(sys.argv[3:],env=os.environ)\ncode=child.wait()\nif code<0:os.kill(os.getpid(),-code)\nsys.exit(code)",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=offline.unique_object)


def task_prompt(task: dict[str, Any]) -> str:
    """Common A/B/C task bytes deliberately contain no oracle scope section."""
    return COMMON_INSTRUCTIONS + "\nTask:\n" + task["prompt"] + "\n"


def runtime_identity() -> dict[str, Any]:
    spec = importlib.util.find_spec("memglide")
    expected = ROOT / "src/memglide/__init__.py"
    if spec is None or spec.origin is None or Path(spec.origin).resolve() != expected:
        raise ValueError("Memglide import does not resolve to the frozen production source")
    identity = {
        **offline.runtime_identity(),
        "python_executable_sha256": common.digest(Path(sys.executable).resolve().read_bytes()),
    }
    for name in ("node", "git"):
        executable = shutil.which(name)
        identity[name] = (
            {
                "path": str(Path(executable).resolve()),
                "sha256": common.digest(Path(executable).resolve().read_bytes()),
                "version": subprocess.check_output(
                    [executable, "--version"], text=True, timeout=10
                ).strip(),
            }
            if executable
            else None
        )
    compiler = ROOT / "frontend/node_modules/typescript/bin/tsc"
    identity["typescript_compiler"] = (
        {
            "path": str(compiler),
            "sha256": common.digest(compiler.read_bytes()),
            "package_sha256": common.digest((compiler.parents[1] / "package.json").read_bytes()),
        }
        if compiler.is_file()
        else None
    )
    compiler_files = list((ROOT / "frontend/node_modules/typescript/lib").glob("*.js")) + list(
        (ROOT / "frontend/node_modules/typescript/lib").glob("*.cjs")
    )
    compiler_files += list(
        (ROOT / "frontend/node_modules/@typescript").glob("typescript-*/lib/tsc")
    )
    compiler_files += list(
        (ROOT / "frontend/node_modules/@typescript").glob("typescript-*/package.json")
    )
    identity["typescript_execution_files"] = {
        str(path): common.digest(path.read_bytes()) for path in compiler_files if path.is_file()
    }
    return identity


def policy_seal() -> dict[str, Any]:
    paths = list((ROOT / "src/memglide").rglob("*.py"))
    paths += [
        Path(__file__),
        PROTOCOL,
        ROOT / "tests/test_benchmark_router_coding.py",
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
        ROOT / "benchmarks/telemetry.py",
        ROOT / "benchmarks/compare_components.py",
        ROOT / "benchmarks/reporting.py",
        ROOT / "benchmarks/run_cache_formats.py",
        ROOT / "benchmarks/__init__.py",
    ]
    paths += [
        Path(str(module.__file__))
        for module in (legacy, common, durable, offline, hardened, native, prices)
    ]
    files = {}
    for path in sorted(set(paths)):
        if path.is_symlink() or not path.is_file():
            raise ValueError("Native policy source missing or symlinked")
        files[path.relative_to(ROOT).as_posix()] = common.digest(path.read_bytes())
    return {
        "head": hardened.git(ROOT, "rev-parse", "HEAD"),
        "files": files,
        "runtime_identity": runtime_identity(),
        "source_settings": SETTINGS,
        "native_model": MODEL,
        "native_effort": EFFORT,
        "native_version": VERSION,
        "requested_service_tier": "default",
    }


def freeze_policy(path: Path) -> None:
    common.atomic_json(
        path,
        {
            "version": "router-coding-1",
            "native_policy": policy_seal(),
            "corpus_selected_or_inspected": False,
        },
        immutable=True,
    )


def verify_policy_freeze(path: Path) -> None:
    record = load_json(path)
    if (
        record.get("corpus_selected_or_inspected") is not False
        or record.get("native_policy") != policy_seal()
    ):
        raise ValueError("Native pre-corpus policy, dependencies or helpers changed after freeze")


def validate_tasks(tasks: Any, grading: Any) -> None:
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 12 or not isinstance(grading, dict):
        raise ValueError("Requires one to twelve public tasks and separate private grading")
    identifiers = []
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {"id", "repository", "language", "prompt"}:
            raise ValueError("Public task may contain only neutral identity/language/prompt fields")
        if not re.fullmatch(r"n\d{2}", task["id"]) or not re.fullmatch(
            r"r\d{2}", task["repository"]
        ):
            raise ValueError("Task and repository identifiers must be neutral nNN/rNN")
        if task["language"] not in {"python", "typescript"}:
            raise ValueError("Coding tasks must be Python or TypeScript")
        prompt = task["prompt"]
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode()) > 4000:
            raise ValueError("Public task prompt is empty or oversized")
        grade = grading.get(task["id"], {})
        paths = grade.get("known_paths")
        if (
            not isinstance(paths, list)
            or not 1 <= len(paths) <= 8
            or len(paths) != len(set(paths))
            or not all(offline.safe_relative(path) for path in paths)
        ):
            raise ValueError("Private oracle scope must contain unique safe relative paths")
        if any(path in prompt or Path(path).name in prompt for path in paths):
            raise ValueError("Public task leaks a private target path")
        if re.search(r"(?:[\w.-]+/)+[\w.-]+|\b[\w.-]+\.(?:py|pyi|ts|tsx|js|json)\b", prompt):
            raise ValueError("Public task contains a source path")
        grader = grade.get("grader", {})
        if (
            not isinstance(grader, dict)
            or not isinstance(grader.get("argv"), list)
            or not grader["argv"]
            or not all(isinstance(arg, str) and arg and "\x00" not in arg for arg in grader["argv"])
        ):
            raise ValueError("Private grade requires a structured external grader argv")
        if not number(grader.get("timeout_seconds")) or not 0 < grader["timeout_seconds"] <= 180:
            raise ValueError("External grader timeout must be bounded")
        identifiers.append(task["id"])
    if len(set(identifiers)) != len(tasks) or set(identifiers) != set(grading):
        raise ValueError("Task IDs/private grades must match uniquely")


def validate_grader_bindings(grading: dict[str, Any], private_root: Path) -> None:
    interpreters = {Path(sys.executable).resolve()}
    node = shutil.which("node")
    if node:
        interpreters.add(Path(node).resolve())
    for private in grading.values():
        argv = private["grader"]["argv"]
        executable = Path(shutil.which(argv[0]) or argv[0]).resolve()
        if executable not in interpreters or len(argv) < 2:
            raise ValueError("External grader must use the frozen Python or Node interpreter")
        script = Path(argv[1])
        if (
            not script.is_absolute()
            or script.is_symlink()
            or not script.is_file()
            or not script.resolve().is_relative_to(private_root)
        ):
            raise ValueError(
                "External grader script must be inside the complete frozen private root"
            )
        for argument in argv[2:]:
            argument.format_map(
                {"worktree": "/native-worktree", "artifacts": "/external-grade", "task_id": "n00"}
            )
            if Path(argument).is_absolute() and not Path(argument).resolve().is_relative_to(
                private_root
            ):
                raise ValueError(
                    "Grader data paths must be inside the complete frozen private root"
                )


def formal_cohort(tasks: list[dict[str, Any]], provenance: dict[str, Any], repeats: int) -> bool:
    roots = {
        value["repository_url"].removesuffix(".git").rstrip("/").lower()
        for value in provenance.values()
    }
    return (
        len(tasks) == 12
        and repeats == 2
        and sum(task["language"] == "python" for task in tasks) == 6
        and sum(task["language"] == "typescript" for task in tasks) == 6
        and len(roots) >= 6
    )


def validate_control_receipts(
    tasks: list[dict[str, Any]], grading: dict[str, Any], fixtures: Path
) -> None:
    for task in tasks:
        private = grading[task["id"]]
        task_digest = common.digest(common.canonical(task))
        if private.get("task_digest") != task_digest or private.get(
            "fixture_hashes"
        ) != offline.tree_hashes(fixtures / task["repository"]):
            raise ValueError(
                "Behavior controls are not bound to the frozen task and source fixture"
            )
        script_digest = common.digest(Path(private["grader"]["argv"][1]).read_bytes())
        for field, expected in (("baseline_result", False), ("reference_result", True)):
            receipt = private.get(field, {})
            if (
                receipt.get("success") is not expected
                or receipt.get("executed") is not True
                or type(receipt.get("checks")) is not int
                or receipt["checks"] <= 0
                or receipt.get("task_digest") != task_digest
                or receipt.get("grader_script_sha256") != script_digest
            ):
                raise ValueError(
                    "Baseline-fail/reference-pass controls lack hash-bound executed-check evidence"
                )


def make_plan(tasks: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    if type(repeats) is not int or repeats not in {1, 2}:
        raise ValueError("Only one pilot or two formal repeats are supported")
    generator = random.Random(seed)
    members, orders = list(tasks), list(permutations(ARMS))
    generator.shuffle(members)
    generator.shuffle(orders)
    rows: list[dict[str, Any]] = []
    for repeat in range(1, repeats + 1):
        for index, task in enumerate(members):
            arms = orders[index % len(orders)]
            if repeat == 2:
                arms = tuple(reversed(arms))
            for arm in arms:
                ordinal = len(rows) + 1
                rows.append(
                    {
                        "run_id": f"coding-{ordinal:04d}",
                        "task_id": task["id"],
                        "repository": task["repository"],
                        "language": task["language"],
                        "configuration": arm,
                        "repeat": repeat,
                        "order": ordinal,
                    }
                )
    return rows


def number(value: Any) -> TypeGuard[int | float]:
    return type(value) in {int, float} and math.isfinite(value)


def stop_group(process: subprocess.Popen[Any]) -> None:
    """Always clean our private group, including descendants of an exited leader."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        if process.poll() is None:
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
    process.wait(timeout=2)


def execute_codex(
    command: list[str],
    prompt: str,
    worktree: Path,
    artifacts: Path,
    timeout: float,
    environment: dict[str, str],
) -> dict[str, Any]:
    """One durably granted native launch; no probes, retries, or hidden dispatch."""
    (artifacts / "prompt.txt").write_text(prompt, encoding="utf-8")
    common.atomic_json(artifacts / "command.json", command, immutable=True)
    child_environment = {
        **environment,
        "CODEX_HOME": str(legacy.isolated_codex_state(artifacts / "codex-state", environment)),
    }
    started, timed_out, interrupted = time.monotonic(), False, False
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
                "5",
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
                if time.monotonic() - started >= min(timeout, 5):
                    raise subprocess.TimeoutExpired(command, timeout)
                time.sleep(0.01)
            if not identity_path.exists():
                raise ValueError("Native child exited before recording its identity")
            identity = load_json(identity_path)
            if identity.get("pid") != process.pid or identity.get("process_group") != process.pid:
                raise ValueError("Child identity differs from its private process group")
            common.atomic_json(artifacts / "launch-grant.json", identity, immutable=True)
            process.communicate(prompt, timeout=max(0.001, timeout - (time.monotonic() - started)))
        except subprocess.TimeoutExpired:
            timed_out = True
        except (KeyboardInterrupt, SystemExit):
            interrupted = True
        finally:
            stop_group(process)
            overhead = sampler.finish()
    ended = time.monotonic()
    return {
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "interrupted": interrupted,
        "wall_time_seconds": ended - started,
        "process_started_monotonic_seconds": started,
        "process_finished_monotonic_seconds": ended,
        "overhead": overhead,
        "telemetry": parse_codex_jsonl(artifacts / "events.jsonl"),
        "event_stream_framing": common.native_event_framing(artifacts / "events.jsonl"),
    }


def preparation_worker(request: Path) -> dict[str, Any]:
    """No corpus/grading imports; the public request is C's entire task input."""
    config = load_json(request)
    arm = config.get("arm")
    expected = {"arm", "prompt", "task_query", "worktree", "settings"} | (
        {"known_paths"} if arm == "B" else set()
    )
    if set(config) != expected or arm not in {"B", "C"} or config["settings"] != SETTINGS:
        raise ValueError("Preparation request contains private metadata or invalid settings")
    worktree = Path(config["worktree"])
    if (
        not worktree.is_absolute()
        or worktree.resolve() != worktree
        or not isinstance(config["prompt"], str)
        or not isinstance(config["task_query"], str)
        or not config["task_query"].strip()
        or config["task_query"] not in config["prompt"]
        or len(config["task_query"].encode()) > 4000
    ):
        raise ValueError("Unsafe preparation worktree or prompt")
    from memglide.integrations.auto_preload import prepare_task_prompt
    from memglide.integrations.preload import prepare_prompt

    before = offline.resources()
    setup = common.prepare_project(worktree, request.parent)
    indexed = offline.resources()
    setup["waited_child_cpu_seconds"] = offline.difference(
        indexed["waited_child_cpu_seconds"], before["waited_child_cpu_seconds"]
    )
    started, cpu = time.perf_counter(), time.process_time()
    if arm == "B":
        preparation = prepare_prompt(
            config["prompt"],
            project_id=setup["project_id"],
            db_path=request.parent / "memglide.db",
            focus_paths=config["known_paths"],
            mode="auto",
            context_format=SETTINGS["context_format"],
            max_context_bytes=SETTINGS["max_context_bytes"],
        )
    else:
        preparation = prepare_task_prompt(
            config["prompt"],
            project_id=setup["project_id"],
            db_path=request.parent / "memglide.db",
            enabled=True,
            selection_policy="v4",
            task_query=config["task_query"],
            **SETTINGS,
        )
        from memglide.integrations.codex_preload import _validated_automatic_preparation

        prepared, _ = _validated_automatic_preparation(
            preparation,
            config["prompt"],
            SETTINGS["context_format"],
            max_context_bytes=SETTINGS["max_context_bytes"],
            max_added_tokens=SETTINGS["max_added_tokens"],
            selection_policy="v4",
        )
        if prepared != preparation["prompt"]:
            raise ValueError("Validated v4 ABI differs from prepared stdin")
    return {
        "preparation": preparation,
        "setup": setup,
        "timing": {
            "wall_seconds": time.perf_counter() - started,
            "cpu_seconds": time.process_time() - cpu,
            "waited_child_cpu_seconds": offline.difference(
                offline.resources()["waited_child_cpu_seconds"], indexed["waited_child_cpu_seconds"]
            ),
        },
        "source_mutations": hardened.git(worktree, "status", "--porcelain"),
        "dispatched_model_requests": 0,
    }


def prepare(
    arm: str,
    prompt: str,
    worktree: Path,
    artifacts: Path,
    known_paths: list[str] | None = None,
    *,
    task_query: str,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "arm": arm,
        "prompt": prompt,
        "task_query": task_query,
        "worktree": str(worktree),
        "settings": SETTINGS,
    }
    if arm == "B":
        request["known_paths"] = known_paths
    common.atomic_json(artifacts / "preparation-request.json", request, immutable=True)
    with (
        (artifacts / "preparation-stdout.json").open("x") as out,
        (artifacts / "preparation-stderr.log").open("x") as err,
    ):
        process = subprocess.Popen(
            [
                sys.executable,
                "-I",
                "-c",
                TRUSTED_BOOTSTRAP,
                str(ROOT),
                "--prepare-worker",
                str(artifacts / "preparation-request.json"),
            ],
            cwd=ROOT,
            env=hardened.git_environment(),
            stdout=out,
            stderr=err,
            start_new_session=True,
        )
        try:
            process.wait(timeout=90)
        finally:
            stop_group(process)
    if (
        process.returncode != 0
        or (artifacts / "preparation-stdout.json").stat().st_size > 2_000_000
    ):
        raise ValueError("Local preparation failed or exceeded its output bound")
    result = load_json(artifacts / "preparation-stdout.json")
    if result.get("source_mutations") or result.get("dispatched_model_requests") != 0:
        raise ValueError("Preparation changed source or declared model dispatch")
    return result


def fidelity(
    arm: str,
    observation: dict[str, Any] | None,
    prompt: str,
    actual: str,
    repository: dict[str, str],
    known_paths: list[str] | None = None,
) -> dict[str, Any]:
    if arm == "A":
        if observation is not None or actual != prompt:
            raise ValueError("Bare Codex task stdin changed or gained preparation")
        return {
            "valid": True,
            "mode": "standard",
            "selected_paths": [],
            "source_versions": {},
            "context_bytes": 0,
        }
    if observation is None:
        raise ValueError("Missing source preparation receipt")
    preparation = observation["preparation"]
    proof = offline.verify_delivery(preparation, prompt, repository)
    if actual != preparation["prompt"]:
        raise ValueError("Native stdin differs from independently validated preparation")
    if (
        arm == "B"
        and preparation["mode"] == "preloaded"
        and set(proof["selected_paths"]) != set(known_paths or [])
    ):
        raise ValueError("Known-path B did not supply its entire private oracle scope")
    return {
        **proof,
        "mode": preparation["mode"],
        "reason": preparation.get("reason"),
        "context_bytes": preparation["context_bytes"],
        "oracle_privileged": arm == "B",
        "automatic_selection": preparation.get("automatic_selection"),
        "preparation": {
            "preparation_wall_seconds": observation.get("timing", {}).get("wall_seconds"),
            "preparation_cpu_seconds": observation.get("timing", {}).get("cpu_seconds"),
        },
    }


def grade_external(
    spec: dict[str, Any], worktree: Path, artifacts: Path, task_id: str
) -> dict[str, Any]:
    if artifacts == worktree or worktree in artifacts.parents:
        raise ValueError("Independent grader artifacts must be outside native worktree")
    artifacts.mkdir()
    substitutions = {"worktree": str(worktree), "artifacts": str(artifacts), "task_id": task_id}
    argv = [arg.format_map(substitutions) for arg in spec["argv"]]
    common.atomic_json(artifacts / "command.json", argv, immutable=True)
    with (artifacts / "stdout.json").open("x") as out, (artifacts / "stderr.log").open("x") as err:
        process = subprocess.Popen(
            argv, cwd=artifacts, stdout=out, stderr=err, start_new_session=True
        )
        timed_out = False
        try:
            process.wait(timeout=spec["timeout_seconds"])
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            stop_group(process)
    try:
        if (artifacts / "stdout.json").stat().st_size > 2_000_000:
            raise ValueError("Oversized grader output")
        result = load_json(artifacts / "stdout.json")
        if (
            not isinstance(result, dict)
            or type(result.get("success")) is not bool
            or type(result.get("checks")) is not int
            or result["checks"] <= 0
        ):
            raise ValueError(
                "Grader must return an explicit success boolean and positive executed-check count"
            )
    except (OSError, ValueError) as error:
        result = {
            "success": False,
            "infrastructure_error": type(error).__name__ + ": " + str(error),
        }
    result.update(exit_code=process.returncode, timed_out=timed_out, artifacts=str(artifacts))
    result["success"] = result["success"] and process.returncode == 0 and not timed_out
    return result


def protected_manifest_violations(worktree: Path, manifest: Any) -> list[str]:
    if manifest is None:
        return []
    if not isinstance(manifest, dict):
        raise ValueError("Private protected manifest must map relative paths to SHA256")
    violations = []
    for relative, expected in manifest.items():
        if not offline.safe_relative(relative) or not common._hex_digest(expected):
            raise ValueError("Invalid protected-manifest path or digest")
        path = worktree / relative
        try:
            if path.is_symlink() or common.digest(path.read_bytes()) != expected:
                violations.append(relative)
        except OSError:
            violations.append(relative)
    return violations


def git_metadata_snapshot(worktree: Path) -> dict[str, str]:
    common_dir = Path(hardened.git(worktree, "rev-parse", "--git-common-dir"))
    git_dir = Path(hardened.git(worktree, "rev-parse", "--absolute-git-dir"))
    if not common_dir.is_absolute():
        common_dir = worktree / common_dir
    paths = [
        common_dir / "config",
        common_dir / "info/attributes",
        git_dir / "info/attributes",
        git_dir / "HEAD",
        git_dir / "commondir",
        git_dir / "gitdir",
    ]
    for directory in (common_dir / "refs", common_dir / "hooks"):
        paths.extend(path for path in directory.rglob("*") if path.is_file() or path.is_symlink())
    snapshot = {}
    for path in paths:
        if path.is_symlink():
            raise ValueError("Unsafe Git metadata symlink")
        if path.exists():
            snapshot[str(path.resolve())] = common.digest(path.read_bytes())
    return snapshot


def git_metadata_violations(worktree: Path, expected: dict[str, str]) -> list[str]:
    reasons = []
    try:
        if git_metadata_snapshot(worktree) != expected:
            reasons.append("Git configuration, hooks, refs or worktree identity changed")
        if hardened.git(
            worktree, "diff", "--no-ext-diff", "--no-textconv", "--cached", "--name-only"
        ):
            reasons.append("Git index contains staged changes")
    except (OSError, ValueError, subprocess.SubprocessError):
        reasons.append("Git metadata unavailable or unsafe")
    return reasons


def protection_snapshot(worktree: Path) -> dict[str, str]:
    paths = hardened.git(worktree, "ls-files", "-z").split("\0")
    return {
        path: common.digest((worktree / path).read_bytes())
        for path in paths
        if path and legacy._protected_path(path)
    } | {".git": common.digest((worktree / ".git").read_bytes())}


def source_hashes(root: Path) -> dict[str, str]:
    hashes = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            raise ValueError("Fixture/worktree source may not be symlinked")
        if path.is_file():
            hashes[relative.as_posix()] = common.digest(path.read_bytes())
    return hashes


def check_protection(worktree: Path, expected: dict[str, str], commit: str) -> list[str]:
    reasons = protected_manifest_violations(worktree, expected)
    if hardened.git(worktree, "rev-parse", "HEAD") != commit:
        reasons.append("Git HEAD changed")
    return reasons


def preserve_changes(
    worktree: Path, artifacts: Path, repository: dict[str, Any], safe_metadata: bool
) -> None:
    patch = (
        hardened.git_bytes(
            worktree, "diff", "--no-ext-diff", "--no-textconv", "--binary", repository["commit"]
        )
        if safe_metadata
        else b""
    )
    (artifacts / "changes.patch").write_bytes(patch)
    status = (
        hardened.git(worktree, "status", "--porcelain", "--untracked-files=all")
        if safe_metadata
        else "Git metadata changed; raw regular-file capture retained instead of invoking diff/status"
    )
    (artifacts / "git-status.txt").write_text(status + "\n")
    paths = []
    with tarfile.open(artifacts / "worktree-files.tar", "w", dereference=False) as archive:
        for path in sorted(worktree.rglob("*")):
            relative = path.relative_to(worktree).as_posix()
            if (
                ".git" in path.relative_to(worktree).parts
                or not offline.safe_relative(relative)
                or path.is_dir()
            ):
                continue
            archive.add(path, arcname=relative, recursive=False)
            paths.append(relative)
    common.atomic_json(artifacts / "captured-files.json", paths, immutable=True)


def cost_record(artifacts: Path, result: dict[str, Any], pricing: dict[str, Any]) -> dict[str, Any]:
    content = (artifacts / "events.jsonl").read_text()
    parsed = prices.parse_native_usage(content)
    if parsed.get("coverage_complete") and (
        parsed["usage"].get("input_tokens") == 0 or parsed["usage"].get("output_tokens") == 0
    ):
        parsed["errors"].append(
            "Zero input/output counters cannot attest measured usage for a structured coding response"
        )
        parsed["coverage_complete"] = False
        parsed["usage"] = dict.fromkeys(prices.USAGE_KEYS)
    for line in content.splitlines():
        try:
            event = json.loads(line)
            item = event.get("item", {}) if isinstance(event, dict) else {}
            if isinstance(item, dict) and (
                item.get("type") == "error"
                or str(item.get("message", "")).lower().startswith("model rerouted:")
            ):
                parsed["errors"].append(
                    "Native diagnostic error/model-reroute item invalidates exact-model execution"
                )
                parsed["coverage_complete"] = False
                parsed["usage"] = dict.fromkeys(prices.USAGE_KEYS)
        except (ValueError, TypeError):
            pass  # The independent parser already rejects malformed event JSON.
    if result.get("timed_out") or result.get("interrupted") or result.get("exit_code") != 0:
        parsed["coverage_complete"] = False
        parsed["usage"] = dict.fromkeys(prices.USAGE_KEYS)
    return {"usage_evidence": parsed, **prices.price_usage(parsed, pricing)}


def strict_native_validity(
    result: dict[str, Any], final: Path, usage_evidence: dict[str, Any]
) -> dict[str, Any]:
    validity = common.native_execution_validity(result, final)
    if usage_evidence.get("coverage_complete") is not True or usage_evidence.get("errors"):
        validity["valid"] = False
        validity["reasons"].append(
            "Independent native lifecycle/usage parser rejected complete execution: "
            + "; ".join(usage_evidence.get("errors", []))
        )
    return validity


def run_attempt(
    attempt: dict[str, Any],
    task: dict[str, Any],
    private: dict[str, Any],
    repository: dict[str, str],
    output: Path,
    args: argparse.Namespace,
    pricing: dict[str, Any],
) -> dict[str, Any]:
    result = {
        **attempt,
        "errors": list(attempt["errors"]),
        "model_calls": None,
        "actual_cost_usd": None,
        "computed_cost_usd": None,
    }
    artifacts, worktree = Path(result["artifacts"]), Path(result["worktree"])
    prompt, arm = task_prompt(task), result["configuration"]
    result.update(
        starting_commit=repository["commit"],
        common_task_prompt_sha256=common.digest(prompt.encode()),
        configuration_label=LABELS[arm],
        setup={"wall_seconds": 0, "cpu_seconds": 0},
    )
    try:
        worktree.parent.mkdir(parents=True, exist_ok=True)
        hardened.git(
            Path(repository["path"]),
            "worktree",
            "add",
            "--detach",
            str(worktree),
            repository["commit"],
        )
        if source_hashes(worktree) != repository["retained_file_sha256"]:
            raise ValueError("Fresh native worktree differs from exact retained fixture bytes")
        snapshot = protection_snapshot(worktree)
        git_snapshot = git_metadata_snapshot(worktree)
        if protected_manifest_violations(worktree, private.get("protected_manifest")):
            raise ValueError("Baseline source differs from private protected manifest")
        started = time.monotonic()
        observation = (
            prepare(
                arm,
                prompt,
                worktree,
                artifacts,
                private["known_paths"] if arm == "B" else None,
                task_query=task["prompt"],
            )
            if arm != "A"
            else None
        )
        actual = observation["preparation"]["prompt"] if observation else prompt
        proof = fidelity(
            arm,
            observation,
            prompt,
            actual,
            repository,
            private["known_paths"] if arm == "B" else None,
        )
        result.update(
            preload_treatment_fidelity=proof,
            treatment_valid=True,
            actual_model_prompt_sha256=common.digest(actual.encode()),
        )
        if observation:
            result["setup"], result["preparation_timing"] = (
                observation["setup"],
                observation["timing"],
            )
        command = native.codex_command(
            args.codex,
            worktree,
            output / "final-response-schema.json",
            artifacts / "final.json",
            MODEL,
            EFFORT,
        )
        result["native_command"] = command
        environment = {
            **hardened.git_environment(),
            "NO_COLOR": "1",
            "CI": "1",
            "MEMGLIDE_HOME": str(artifacts / "memglide-home"),
            "PATH": str(ROOT / "frontend/node_modules/.bin")
            + os.pathsep
            + os.environ.get("PATH", ""),
        }
        if args.codex_home:
            environment["CODEX_HOME"] = str(args.codex_home.resolve())
        result.update(
            execute_codex(command, actual, worktree, artifacts, args.timeout, environment)
        )
        result["end_to_end_wall_seconds"] = time.monotonic() - started
        result["native_execution_validity"] = common.native_execution_validity(
            result, artifacts / "final.json"
        )
        no_mcp = (
            result["telemetry"].get("mcp_counts_complete") is True
            and result["telemetry"].get("mcp_call_count") == 0
        )
        if not no_mcp:
            result["treatment_valid"] = result["preload_treatment_fidelity"]["valid"] = False
            result["errors"].append("Complete MCP-free native stream is absent")
        if (artifacts / "prompt.txt").read_bytes() != actual.encode() or load_json(
            artifacts / "command.json"
        ) != command:
            result["treatment_valid"] = result["preload_treatment_fidelity"]["valid"] = False
            result["errors"].append("Retained native input/command differs from validated handoff")
        result["protected_file_violations"] = sorted(
            set(
                check_protection(worktree, snapshot, repository["commit"])
                + protected_manifest_violations(worktree, private.get("protected_manifest"))
                + git_metadata_violations(worktree, git_snapshot)
            )
        )
        preserve_changes(
            worktree, artifacts, repository, not git_metadata_violations(worktree, git_snapshot)
        )
        result["api_price_equivalent"] = cost_record(artifacts, result, pricing)
        result["native_execution_validity"] = strict_native_validity(
            result, artifacts / "final.json", result["api_price_equivalent"]["usage_evidence"]
        )
        result["grader"] = grade_external(
            private["grader"], worktree, artifacts / "grade", task["id"]
        )
        result["protected_file_violations"] = sorted(
            set(
                result["protected_file_violations"]
                + check_protection(worktree, snapshot, repository["commit"])
                + protected_manifest_violations(worktree, private.get("protected_manifest"))
                + git_metadata_violations(worktree, git_snapshot)
            )
        )
        if result["protected_file_violations"]:
            result["grader"]["success"] = False
            result["errors"].append("Protected tests or Git metadata changed")
        result["status"] = (
            "interrupted"
            if result["interrupted"]
            else "timeout"
            if result["timed_out"]
            else "execution_failed"
            if result["native_execution_validity"]["valid"] is not True
            else "harness_error"
            if result["grader"].get("infrastructure_error") or result["grader"].get("timed_out")
            else "invalid_treatment"
            if result["treatment_valid"] is not True
            else "failed"
            if result["grader"]["success"] is not True
            else "completed"
        )
        result["common_blocker"] = legacy.common_blocker(result, artifacts)
        if result["status"] == "harness_error":
            result["errors"].append(
                "Independent grader infrastructure failed; further native launches must stop"
            )
    except (KeyboardInterrupt, SystemExit):
        result.update(status="interrupted", execution_outcome_unknown=True)
        result["errors"].append("Interrupted; no automatic retry")
    except Exception as error:
        result["status"] = "harness_error"
        result["errors"].append(type(error).__name__ + ": " + str(error))
    result["finished_at"] = legacy.utc_now()
    common.atomic_json(artifacts / "result.json", result, immutable=True)
    return result


def budget_reason(
    rows: list[dict[str, Any]], preflight_cost: float, args: argparse.Namespace, elapsed: float
) -> str | None:
    attempted = [row for row in rows if row.get("attempted")]
    if len(attempted) >= args.max_attempts:
        return "Hard maximum native assignment attempts reached"
    if elapsed + args.timeout + 90 + 180 >= args.max_wall_seconds:
        return "Session wall-time circuit breaker reached"
    if attempted and (
        attempted[-1].get("grader", {}).get("infrastructure_error")
        or attempted[-1].get("grader", {}).get("timed_out")
    ):
        return "Independent grader infrastructure failure; stop before another native launch"
    costs = [
        row.get("api_price_equivalent", {}).get("possible_write_price_upper_usd")
        for row in attempted
    ]
    if not all(number(cost) for cost in costs):
        return "Unknown attempt usage/cost; stop before another native launch"
    if preflight_cost + sum(costs) + args.attempt_reserve_usd > args.max_estimated_usd:
        return "Soft API-price-equivalent admission budget reached"
    if attempted and attempted[-1].get("common_blocker"):
        return "Shared runtime blocker: " + attempted[-1]["common_blocker"]
    if attempted and attempted[-1].get("status") in {
        "interrupted",
        "harness_error",
        "invalid_treatment",
    }:
        return "Harness/interruption/treatment failure; investigate before further launches"
    return None


def settings(args: argparse.Namespace, version: str) -> dict[str, Any]:
    return {
        "model": MODEL,
        "effort": EFFORT,
        "requested_service_tier": "default",
        "codex_version": version,
        "codex_executable": args.codex,
        "codex_binary_sha256": common.digest(Path(args.codex).read_bytes()),
        "codex_home_binding_directory": str(args.codex_home.resolve()) if args.codex_home else None,
        "repeats": args.repeats,
        "seed": args.seed,
        "timeout": args.timeout,
        "max_attempts": args.max_attempts,
        "max_estimated_usd": args.max_estimated_usd,
        "attempt_reserve_usd": args.attempt_reserve_usd,
        "max_wall_seconds": args.max_wall_seconds,
        "source_settings": SETTINGS,
    }


def frozen_manifest(
    args: argparse.Namespace, tasks: list[dict[str, Any]], configuration: dict[str, Any]
) -> dict[str, Any]:
    paths = list((ROOT / "src/memglide").rglob("*.py")) + [
        Path(__file__),
        PROTOCOL,
        ROOT / "tests/test_benchmark_router_coding.py",
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
    ]
    paths += [
        Path(str(module.__file__))
        for module in (legacy, common, durable, offline, hardened, native, prices)
    ]
    paths += [
        ROOT / "benchmarks/telemetry.py",
        ROOT / "benchmarks/compare_components.py",
        ROOT / "benchmarks/reporting.py",
        ROOT / "benchmarks/run_cache_formats.py",
        ROOT / "benchmarks/__init__.py",
        args.tasks,
        args.grading,
        args.provenance,
        args.pricing,
        Path(args.codex),
    ]
    if args.policy_freeze:
        paths.append(args.policy_freeze)
    files = {}
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError("Frozen source/input missing or symlinked")
        files[str(path.resolve())] = common.digest(path.read_bytes())
    return {
        "git_head": hardened.git(ROOT, "rev-parse", "HEAD"),
        "files": files,
        "fixtures": offline.tree_hashes(args.fixtures),
        "grader_files": offline.tree_hashes(args.grader_root),
        "settings": configuration,
        "runtime_identity": runtime_identity(),
        "common_task_prompt_sha256": {
            task["id"]: common.digest(task_prompt(task).encode()) for task in tasks
        },
    }


def create_repositories(
    output: Path, tasks: list[dict[str, Any]], fixtures: Path
) -> dict[str, Any]:
    repositories = {}
    for index, identifier in enumerate(sorted({task["repository"] for task in tasks}), 1):
        source, destination = fixtures / identifier, output / "repositories" / f"repo-{index:04d}"
        shutil.copytree(source, destination)
        hardened.initialize_repository(destination)
        retained = offline.tree_hashes(source)
        commit = hardened.git(destination, "rev-parse", "HEAD")
        hardened.verify_repository(destination, commit, retained)
        repositories[identifier] = {
            "path": str(destination),
            "commit": commit,
            "tree": hardened.git(destination, "rev-parse", "HEAD^{tree}"),
            "retained_file_sha256": retained,
        }
    return repositories


def verify_repositories(repositories: dict[str, Any]) -> None:
    for repository in repositories.values():
        root = Path(repository["path"])
        hardened.verify_repository(root, repository["commit"], repository["retained_file_sha256"])
        if (
            hardened.git(root, "rev-parse", "HEAD") != repository["commit"]
            or hardened.git(root, "rev-parse", "HEAD^{tree}") != repository["tree"]
            or source_hashes(root) != repository["retained_file_sha256"]
        ):
            raise ValueError("Frozen canonical source repository changed")


def validate_preflight(receipt: Any) -> float:
    expected = {
        "ready": True,
        "codex_version": VERSION,
        "model": MODEL,
        "reasoning_effort": EFFORT,
        "requested_service_tier": "default",
        "auth_binding_ready": True,
        "native_supported_flags_verified": True,
        "v4_offline_gate_passed": True,
    }
    if not isinstance(receipt, dict) or any(
        receipt.get(key) != value for key, value in expected.items()
    ):
        raise ValueError(
            "Execution requires a successful runtime and v4 offline eligibility preflight receipt"
        )
    if (
        type(receipt.get("native_preflight_attempts")) is not int
        or receipt["native_preflight_attempts"] < 1
        or not number(receipt.get("preflight_price_equivalent_upper_usd"))
        or receipt["preflight_price_equivalent_upper_usd"] < 0
    ):
        raise ValueError(
            "Every separately labelled native preflight invocation must be counted and current admission usage estimated"
        )
    return receipt["preflight_price_equivalent_upper_usd"]


def measured_metrics(row: dict[str, Any]) -> dict[str, Any]:
    metrics = common.metrics(row)
    timing = row.get("preparation_timing", {})
    metrics["context_preparation_wall_seconds"] = timing.get("wall_seconds")
    metrics["context_preparation_cpu_seconds"] = timing.get("cpu_seconds")
    if row.get("configuration") == "A" and row.get("attempted"):
        metrics["context_preparation_wall_seconds"] = 0
        metrics["context_preparation_cpu_seconds"] = 0
    components = [
        metrics.get("cpu_seconds"),
        metrics.get("approval_index_cpu_seconds"),
        metrics.get("context_preparation_cpu_seconds"),
    ]
    if row.get("configuration") != "A":
        components += [
            row.get("setup", {}).get("waited_child_cpu_seconds"),
            timing.get("waited_child_cpu_seconds"),
        ]
    metrics["total_observed_local_cpu_seconds"] = (
        sum(components) if all(number(value) for value in components) else None
    )
    metrics["api_price_equivalent_usd"] = row.get("api_price_equivalent", {}).get(
        "native_reported_price_equivalent_usd"
    )
    return metrics


def build_report(
    rows: list[dict[str, Any]], tasks: list[dict[str, Any]], metadata: dict[str, Any]
) -> dict[str, Any]:
    arms = {}
    for arm in ARMS:
        members = [row for row in rows if row["configuration"] == arm]
        attempted = [row for row in members if row.get("attempted")]
        successes = sum(prices._success(row) for row in attempted)
        costs = [
            row.get("api_price_equivalent", {}).get("native_reported_price_equivalent_usd")
            for row in attempted
        ]
        upper = [
            row.get("api_price_equivalent", {}).get("possible_write_price_upper_usd")
            for row in attempted
        ]
        total = sum(costs) if attempted and all(number(cost) for cost in costs) else None
        arms[arm] = {
            **common.aggregate(members),
            "completion_rate_scope": "successful_task_completion_rate is conditional on attempted assignments; unrun correctness is unknown",
            "planned_assignment_execution_coverage": len(attempted) / len(members)
            if members
            else None,
            "observed_success_yield_per_planned_assignment": successes / len(members)
            if members and attempted
            else None,
            "metrics": {
                name: common.summarize(
                    [measured_metrics(row).get(name) for row in attempted],
                    additive="rss_bytes" not in name,
                )
                for name in common.METRICS
            },
            "api_price_equivalent": {
                "known_total_usd": sum(cost for cost in costs if number(cost))
                if attempted
                else None,
                "total_usd": total,
                "coverage_attempts": sum(number(cost) for cost in costs),
                "attempts_including_failures": len(attempted),
                "cost_per_success_usd": total / successes
                if total is not None and successes
                else None,
                "possible_write_upper_total_usd": sum(upper)
                if attempted and all(number(cost) for cost in upper)
                else None,
            },
            "source_delivery_counts": {
                mode: sum(
                    row.get("preload_treatment_fidelity", {}).get("mode") == mode
                    for row in attempted
                )
                for mode in ("standard", "preloaded", "passthrough")
            },
        }
    indexed = {(row["task_id"], row["repeat"], row["configuration"]): row for row in rows}
    paired = {}
    for baseline in ("A", "B"):
        for metric in (
            "end_to_end_wall_seconds",
            "input_tokens",
            "cached_input_tokens",
            "uncached_input_tokens",
            "output_tokens",
            "api_price_equivalent_usd",
        ):
            clusters: dict[str, list[tuple[float, float]]] = {}
            for task in tasks:
                values: list[tuple[float, float]] = []
                for repeat in range(1, metadata["repeats"] + 1):
                    first, second = (
                        indexed.get((task["id"], repeat, arm), {}) for arm in (baseline, "C")
                    )
                    left, right = (measured_metrics(row).get(metric) for row in (first, second))
                    if (
                        first.get("attempted")
                        and second.get("attempted")
                        and number(left)
                        and number(right)
                    ):
                        values.append((float(left), float(right)))
                if len(values) == metadata["repeats"]:
                    clusters[task["id"]] = values
            paired[f"C_minus_{baseline}:{metric}"] = offline.clustered_effect(clusters)
    paired_success = {}
    for baseline in ("A", "B"):
        counts = {"both": 0, "C_only": 0, "baseline_only": 0, "neither": 0, "unpaired_or_unrun": 0}
        for task in tasks:
            for repeat in range(1, metadata["repeats"] + 1):
                first, second = (
                    indexed.get((task["id"], repeat, arm), {}) for arm in (baseline, "C")
                )
                if not first.get("attempted") or not second.get("attempted"):
                    counts["unpaired_or_unrun"] += 1
                    continue
                a, c = prices._success(first), prices._success(second)
                counts[
                    "both" if a and c else "C_only" if c else "baseline_only" if a else "neither"
                ] += 1
        paired_success["C_vs_" + baseline] = counts
    return {
        "version": "router-coding-1",
        "configuration_labels": LABELS,
        "metadata": metadata,
        "tasks": tasks,
        "arms": arms,
        "paired_effects": paired,
        "paired_strict_success": paired_success,
        "runs": rows,
        "actual_billing_usd": None,
        "pricing_interpretation": "Historically verified tariff scenario from the frozen pricing evidence; current applicability and actual account charges are unknown unless separately refreshed evidence establishes them.",
        "preflight_accounting": {
            "native_invocations": metadata.get("preflight_receipt", {}).get(
                "native_preflight_attempts"
            ),
            "current_admission_upper_usd": metadata.get("preflight_receipt", {}).get(
                "preflight_price_equivalent_upper_usd"
            ),
            "history": metadata.get("preflight_receipt", {}).get("preflight_history"),
            "all_study_spend_usd": None,
            "scope": "Formal-attempt API equivalents are separate from all preflight invocations. Any earlier failed preflight with unknown usage leaves whole-study spending unknown.",
        },
        "default_promotion": False,
        "limitations": [
            "B receives privileged oracle-known paths unavailable to A/C; C versus A is the path-free automatic integration comparison.",
            "All assignments including skips/failures remain in intent-to-treat results; behavioral passes require native integrity, source fidelity and protected-file checks for completion.",
            "Cold B/C production approval/index, preparation and native execution are timed; independent grading/worktree creation are excluded.",
            "Provider/OS caches are uncontrolled; order is counterbalanced, native state/worktrees are fresh, and cached input is observed separately.",
            "Model call counts and actual billing are unknown. Separate verified-rate API equivalents include failed attempts and remain null with missing usage; they do not measure invoiced savings.",
            "Dollar budget is a soft pre-launch admission breaker using possible-write estimates and a reserve, not a hard provider charge limit.",
            "Private grading is kept outside every indexed/agent worktree; this is procedural separation, not an OS read-access security boundary.",
            "This evaluates upfront source preparation without MCP or automatic memory. No benefit or default promotion is assumed.",
        ],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    for name in ("tasks", "grading", "grader-root", "fixtures", "provenance", "pricing", "output"):
        result.add_argument("--" + name, required=True, type=Path)
    result.add_argument("--preflight", type=Path)
    result.add_argument("--policy-freeze", type=Path)
    result.add_argument("--codex", default=shutil.which("codex") or "codex")
    result.add_argument("--codex-home", type=Path)
    result.add_argument("--repeats", type=int, choices=(1, 2), default=2)
    result.add_argument("--seed", type=int, default=20261019)
    result.add_argument("--timeout", type=float, default=180)
    result.add_argument("--max-attempts", type=int, default=72)
    result.add_argument("--max-estimated-usd", type=float, default=20)
    result.add_argument("--attempt-reserve-usd", type=float, default=0.25)
    result.add_argument("--max-wall-seconds", type=float, default=18000)
    result.add_argument(
        "--execute",
        action="store_true",
        help="Dispatch the already-authorized native experiment; default writes a plan only",
    )
    result.add_argument("--resume", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == "--prepare-worker":
        print(json.dumps(preparation_worker(Path(argv[1])), ensure_ascii=False))
        return 0
    if len(argv) == 2 and argv[0] == "--freeze-policy":
        freeze_policy(Path(argv[1]).resolve())
        return 0
    arguments = parser().parse_args(argv)
    for name in ("tasks", "grading", "grader_root", "fixtures", "provenance", "pricing", "output"):
        setattr(arguments, name, getattr(arguments, name).resolve())
    if (
        not 0 < arguments.timeout <= 180
        or not 0 < arguments.max_attempts <= MAX_LAUNCHES
        or not all(
            number(value) and value > 0
            for value in (
                arguments.max_estimated_usd,
                arguments.attempt_reserve_usd,
                arguments.max_wall_seconds,
            )
        )
    ):
        raise ValueError(
            "Native launch/time/budget bounds must be positive and within hard ceilings"
        )
    arguments.codex = str(
        Path(shutil.which(arguments.codex) or arguments.codex).resolve(strict=True)
    )
    version = subprocess.check_output([arguments.codex, "--version"], text=True, timeout=10).strip()
    if version != VERSION:
        raise ValueError("Native version differs from the supported pinned CLI")
    tasks, grading, pricing = (
        load_json(arguments.tasks),
        load_json(arguments.grading),
        load_json(arguments.pricing),
    )
    validate_tasks(tasks, grading)
    validate_grader_bindings(grading, arguments.grader_root)
    if arguments.policy_freeze:
        arguments.policy_freeze = arguments.policy_freeze.resolve()
        verify_policy_freeze(arguments.policy_freeze)
    prices.validate_pricing(pricing)
    if (
        pricing["model"] != MODEL
        or arguments.grading != arguments.grader_root
        and arguments.grader_root not in arguments.grading.parents
    ):
        raise ValueError("Pricing model mismatch or private manifest outside frozen grader root")
    if any(
        arguments.grader_root == arguments.fixtures / task["repository"]
        or arguments.grader_root.is_relative_to(arguments.fixtures / task["repository"])
        for task in tasks
    ):
        raise ValueError("Private grading must be outside every fixture root")
    provenance = load_json(arguments.provenance)
    hardened.validate_provenance(provenance, arguments.fixtures, tasks)
    plan = make_plan(tasks, arguments.repeats, arguments.seed)
    configuration = settings(arguments, version)
    frozen = frozen_manifest(arguments, tasks, configuration)
    output = arguments.output
    if not arguments.resume:
        output.mkdir(parents=True, exist_ok=False)
    with durable.experiment_lock(output):
        if arguments.resume:
            metadata, state = load_json(output / "metadata.json"), load_json(output / "state.json")
            durable.validate_frozen(metadata, frozen)
            common.validate_saved_state(output, tasks, plan, state)
            repositories = metadata["repositories"]
            verify_repositories(repositories)
            if metadata.get("finished_at"):
                print(f"Finished study retained; no new launches. {output / 'report.json'}")
                return 0
            common.recover_interrupted(output, state, metadata)
        else:
            repositories = create_repositories(output, tasks, arguments.fixtures)
            metadata = {
                "version": "router-coding-1",
                "started_at": legacy.utc_now(),
                "frozen_manifest": frozen,
                "repeats": arguments.repeats,
                "repositories": repositories,
                "resume_count": 0,
                "pilot": not formal_cohort(tasks, provenance, arguments.repeats),
                "planned_assignments": len(plan),
                "native_preflight_accounted_separately": True,
                "native_pre_corpus_freeze_verified": bool(arguments.policy_freeze),
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
        if not arguments.execute:
            print(
                f"Plan only: {len(plan)} native assignments; zero model requests. {output / 'plan.json'}"
            )
            return 0
        if metadata.get("finished_at"):
            print(f"Finished study retained; no new launches. {output / 'report.json'}")
            return 0
        preflight_cost, preflight_blocker = 0.0, None
        if not arguments.preflight:
            preflight_blocker = (
                "No runtime/offline preflight receipt; zero native assignment launches permitted"
            )
        else:
            receipt = load_json(arguments.preflight)
            metadata["preflight_receipt"] = receipt
            if (output / "execution-preflight.json").exists():
                if load_json(output / "execution-preflight.json") != receipt:
                    raise ValueError("Sealed execution preflight changed")
            else:
                common.atomic_json(output / "execution-preflight.json", receipt, immutable=True)
            try:
                preflight_cost = validate_preflight(receipt)
                if not arguments.policy_freeze:
                    preflight_blocker = "No native pre-corpus policy seal; zero native assignment launches permitted"
                else:
                    validate_control_receipts(tasks, grading, arguments.fixtures)
                    metadata["independent_behavior_controls_verified"] = True
            except ValueError as error:
                preflight_blocker = (
                    str(error)
                    + ": "
                    + str(receipt.get("blocker", "preflight unavailable or failed"))
                )
        started = time.monotonic()
        previous_elapsed = metadata.get("session_elapsed_wall_seconds", 0)
        task_map, blocker = (
            {task["id"]: task for task in tasks},
            metadata.get("stop_reason") or preflight_blocker,
        )
        for row in plan:
            if not state["originals"][row["run_id"]].get("pending"):
                continue
            blocker = blocker or budget_reason(
                list(state["originals"].values()),
                preflight_cost,
                arguments,
                previous_elapsed + time.monotonic() - started,
            )
            if blocker:
                state["originals"][row["run_id"]] = legacy.not_run(row, blocker)
                continue
            try:
                durable.validate_frozen(metadata, frozen_manifest(arguments, tasks, configuration))
                verify_repositories(repositories)
            except ValueError as error:
                blocker = str(error)
                state["originals"][row["run_id"]] = legacy.not_run(row, blocker)
                continue
            print(
                f"[{row['order']}/{len(plan)}] {row['run_id']} {LABELS[row['configuration']]}",
                flush=True,
            )
            attempt = common.begin_attempt(output, row, state, metadata)
            result = run_attempt(
                attempt,
                task_map[row["task_id"]],
                grading[row["task_id"]],
                repositories[row["repository"]],
                output,
                arguments,
                pricing,
            )
            durable.finish_attempt(output, result, state, metadata)
            try:
                durable.validate_frozen(metadata, frozen_manifest(arguments, tasks, configuration))
            except ValueError as error:
                blocker = str(error)
        metadata.update(
            finished_at=legacy.utc_now(),
            stop_reason=blocker,
            session_elapsed_wall_seconds=previous_elapsed + time.monotonic() - started,
        )
        durable.checkpoint(output, state, metadata)
        report = build_report(list(state["originals"].values()), tasks, metadata)
        common.atomic_json(output / "report.json", report, immutable=True)
        (output / "report.md").write_text(
            "# Fresh automatic source coding study\n\n"
            + "\n".join(
                f"- {LABELS[arm]}: {report['arms'][arm]['successful_runs']}/{report['arms'][arm]['attempted_runs']} strict completed attempts; {report['arms'][arm]['not_run']} unrun."
                for arm in ARMS
            )
            + "\n\n"
            + "\n\n".join(report["limitations"])
            + "\n"
        )
        durable.append_log(
            output,
            "experiment.finished",
            report_sha256=common.digest((output / "report.json").read_bytes()),
        )
        return 2 if blocker else 0


if __name__ == "__main__":
    raise SystemExit(main())
