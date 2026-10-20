"""Run public checks with bounded logs, explicit evidence, and real exit status.

This module executes an explicit argument vector without a shell. It is not an
execution sandbox: callers must provide the working directory and the operating
system isolation appropriate for their command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import queue
import re
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO

MODES = ("full", "success_summary", "counts_and_failures", "structured")
ENVIRONMENT_KEYS = frozenset(
    {
        "CI",
        "NO_COLOR",
        "PYTHONDONTWRITEBYTECODE",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
        "PYTHONPATH",
        "NODE_PATH",
    }
)
_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_CONSOLE_BYTES = 16384
_CLI_RECEIPT_KEYS = (
    "success",
    "kind",
    "passed",
    "failed",
    "raw_exit_code",
    "exit_code",
    "failure_kind",
    "timed_out",
    "output_limit_exceeded",
    "stdout_log",
    "stderr_log",
    "stdout_sha256",
    "stderr_sha256",
    "command",
    "output_mode",
    "log_capture_limit_bytes",
)


def _nonnegative(value: object) -> bool:
    return type(value) is int and value >= 0


def counts(stdout: str, stderr: str) -> tuple[int | None, int | None]:
    """Read common runner summaries; absent evidence remains unknown."""
    clean_stdout = _ANSI.sub("", stdout)
    text = clean_stdout + "\n" + _ANSI.sub("", stderr)
    try:
        data = json.loads(clean_stdout)
    except (ValueError, TypeError):
        data = None
    if isinstance(data, dict):
        passed, failed = data.get("numPassedTests"), data.get("numFailedTests")
        if (
            _nonnegative(data.get("numTotalTests"))
            and _nonnegative(passed)
            and _nonnegative(failed)
        ):
            return passed, failed
        stats = data.get("stats")
        if (
            isinstance(stats, dict)
            and _nonnegative(stats.get("passes"))
            and _nonnegative(stats.get("failures"))
        ):
            return stats["passes"], stats["failures"]
    # Vitest's Test Files row counts files, whereas Tests counts behavior.
    rows = re.findall(r"(?m)^\s*Tests\s+([^\n]+)", text)
    scope = rows[-1] if rows else text
    passed = re.findall(r"(\d+)\s+passed\b", scope)
    failed = re.findall(r"(\d+)\s+failed\b", scope)
    if passed or failed:
        return (int(passed[-1]) if passed else 0, int(failed[-1]) if failed else 0)
    passed = re.findall(r"(\d+)\s+passing\b", scope)
    failed = re.findall(r"(\d+)\s+failing\b", scope)
    if passed or failed:
        return (int(passed[-1]) if passed else 0, int(failed[-1]) if failed else 0)
    passed = re.findall(r"(?m)^#\s+pass\s+(\d+)\s*$", text)
    failed = re.findall(r"(?m)^#\s+fail\s+(\d+)\s*$", text)
    if passed or failed:
        return (int(passed[-1]) if passed else 0, int(failed[-1]) if failed else 0)
    ran = re.findall(r"Ran\s+(\d+)\s+tests?\b", text)
    verdict = re.findall(r"(?m)^(OK|FAILED)(?:\s+\(([^\n]*)\))?\s*$", text)
    if ran and verdict:
        status, details = verdict[-1]
        failures = sum(int(n) for n in re.findall(r"(?:failures|errors)=(\d+)", details))
        skipped = sum(int(n) for n in re.findall(r"skipped=(\d+)", details))
        if status == "FAILED" and failures == 0:
            return None, None
        return max(0, int(ran[-1]) - failures - skipped), failures
    # All-skipped summaries do not establish an executed behavioral check.
    if re.search(r"\b(?:no tests ran|no tests found|\d+ skipped)\b", text, re.I):
        return 0, 0
    return None, None


def _environment(updates: Mapping[str, str] | None) -> dict[str, str]:
    environment = os.environ.copy()
    if updates is None:
        return environment
    if not isinstance(updates, Mapping):
        raise ValueError("env_updates must be a mapping")
    for key, value in updates.items():
        if not isinstance(key, str) or key not in ENVIRONMENT_KEYS:
            raise ValueError("Environment override is not an allowed check setting: " + str(key))
        if not isinstance(value, str) or "\x00" in value:
            raise ValueError("Environment override values must be strings without NUL bytes")
        environment[key] = value
    return environment


def _terminate_group(process: subprocess.Popen[bytes]) -> None:
    """Clean our private process group, including descendants after parent exit."""
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        # Python's stdlib has no portable Windows descendant-job primitive.
        # The direct child is still bounded; report the cleanup scope below.
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            process.kill()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=1)


def _capture(
    process: subprocess.Popen[bytes],
    streams: dict[str, BinaryIO],
    timeout_seconds: float,
    max_output_bytes: int,
) -> dict[str, Any]:
    events: queue.Queue[tuple[str, bytes | None]] = queue.Queue(maxsize=8)
    stop = threading.Event()
    errors: list[str] = []

    def read_pipe(name: str, pipe: BinaryIO) -> None:
        try:
            while not stop.is_set():
                chunk = os.read(pipe.fileno(), 65536)
                if not chunk:
                    break
                while not stop.is_set():
                    try:
                        events.put((name, chunk), timeout=0.05)
                        break
                    except queue.Full:
                        continue
        except OSError as error:
            if not stop.is_set():
                errors.append(type(error).__name__ + ": " + str(error))
        finally:
            while not stop.is_set():
                try:
                    events.put((name, None), timeout=0.05)
                    break
                except queue.Full:
                    continue

    assert process.stdout is not None and process.stderr is not None
    threads = [
        threading.Thread(target=read_pipe, args=(name, pipe), daemon=True)
        for name, pipe in (("stdout", process.stdout), ("stderr", process.stderr))
    ]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout_seconds
    drain_deadline = None
    timed_out = exceeded = incomplete = False
    captured = observed = 0
    remaining_streams = len(threads)
    try:
        while remaining_streams or process.poll() is None:
            now = time.monotonic()
            if drain_deadline is None and now >= deadline:
                timed_out = True
                _terminate_group(process)
                drain_deadline = time.monotonic() + 1
            elif drain_deadline is None and process.poll() is not None:
                # A detached writer cannot keep this completed check open.
                _terminate_group(process)
                drain_deadline = time.monotonic() + 1
            if drain_deadline is not None and now >= drain_deadline:
                incomplete = bool(remaining_streams)
                break
            try:
                name, chunk = events.get(timeout=0.05)
            except queue.Empty:
                continue
            if chunk is None:
                remaining_streams -= 1
                continue
            observed += len(chunk)
            retained = chunk[: max(0, max_output_bytes - captured)]
            streams[name].write(retained)
            captured += len(retained)
            if len(retained) != len(chunk) and not exceeded:
                exceeded = True
                _terminate_group(process)
                drain_deadline = time.monotonic() + 1
    finally:
        _terminate_group(process)
        stop.set()
        for pipe in (process.stdout, process.stderr):
            pipe.close()
        for thread in threads:
            thread.join(timeout=0.25)
        incomplete = incomplete or any(thread.is_alive() for thread in threads)
    return {
        "raw_exit_code": process.returncode,
        "timed_out": timed_out,
        "output_limit_exceeded": exceeded,
        "captured_output_bytes": captured,
        "observed_output_bytes": observed,
        "capture_incomplete": incomplete,
        "capture_errors": errors,
    }


def _cli_status(raw: int | None) -> int:
    if raw is None:
        return 127
    return raw if raw >= 0 else min(255, 128 - raw)


def run_check(
    argv: Sequence[str],
    cwd: Path | str,
    log_root: Path | str | None = None,
    output_mode: str = "counts_and_failures",
    kind: str = "tests",
    expected_tests: int | None = None,
    timeout_seconds: float = 45,
    max_output_bytes: int = 1048576,
    env_updates: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run one bounded command and return a log-hash-bound receipt.

    ``raw_exit_code`` preserves Popen's actual status, including negative POSIX
    signals. ``exit_code`` is shell-compatible and is nonzero for missing test
    evidence, a count regression, output overflow, or a timeout even if the
    child exits zero. Output limits apply to both raw streams combined.
    """
    if output_mode not in MODES or kind not in ("tests", "typecheck"):
        raise ValueError("Invalid check mode or kind")
    if isinstance(argv, (str, bytes)) or not isinstance(argv, Sequence) or not argv:
        raise ValueError("An explicit nonempty argument vector is required")
    if any(not isinstance(arg, str) or not arg or "\x00" in arg for arg in argv):
        raise ValueError("Arguments must be nonempty strings without NUL bytes")
    if (
        type(timeout_seconds) not in (int, float)
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
    ):
        raise ValueError("timeout_seconds must be finite and positive")
    if type(max_output_bytes) is not int or max_output_bytes <= 0:
        raise ValueError("max_output_bytes must be a positive integer")
    if expected_tests is not None and (
        type(expected_tests) is not int or expected_tests <= 0 or kind != "tests"
    ):
        raise ValueError("expected_tests must be a positive integer for behavioral tests")
    environment = _environment(env_updates)
    root = Path(cwd).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Check cwd must be a directory")
    logs = Path(log_root) if log_root is not None else root / ".memglide-check"
    if not logs.is_absolute():
        logs = root / logs
    logs = Path(os.path.abspath(logs))
    if logs.is_relative_to(root):
        # Repository-provided aliases must not redirect retained check output.
        # Explicit caller-selected external artifact roots remain supported.
        component = root
        for part in logs.relative_to(root).parts:
            component = component / part
            if component.is_symlink():
                raise ValueError("Internal check log roots must not traverse symlinks")
    logs = logs.resolve()
    logs.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="check-", dir=logs))
    stdout_log, stderr_log = directory / "stdout.log", directory / "stderr.log"
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    launch_error = None
    capture: dict[str, Any]
    with stdout_log.open("wb") as stdout_file, stderr_log.open("wb") as stderr_file:
        try:
            process = subprocess.Popen(
                list(argv),
                cwd=root,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
                start_new_session=os.name == "posix",
            )
        except OSError as error:
            launch_error = type(error).__name__ + ": " + str(error)
            content = launch_error.encode("utf-8", errors="replace")
            stderr_file.write(content[:max_output_bytes])
            capture = {
                "raw_exit_code": None,
                "timed_out": False,
                "output_limit_exceeded": len(content) > max_output_bytes,
                "captured_output_bytes": min(len(content), max_output_bytes),
                "observed_output_bytes": len(content),
                "capture_incomplete": False,
                "capture_errors": [],
            }
        else:
            try:
                capture = _capture(
                    process,
                    {"stdout": stdout_file, "stderr": stderr_file},
                    float(timeout_seconds),
                    max_output_bytes,
                )
            finally:
                # Cover interruption or an unexpected reader-setup failure too.
                _terminate_group(process)
    raw_stdout, raw_stderr = stdout_log.read_bytes(), stderr_log.read_bytes()
    stdout, stderr = (
        raw_stdout.decode("utf-8", errors="replace"),
        raw_stderr.decode("utf-8", errors="replace"),
    )
    passed, failed = counts(stdout, stderr)
    failure = None
    if launch_error:
        failure = "launch_error"
    elif capture["timed_out"]:
        failure = "timeout"
    elif capture["output_limit_exceeded"]:
        failure = "output_limit"
    elif capture["capture_incomplete"] or capture["capture_errors"]:
        failure = "capture_incomplete"
    elif capture["raw_exit_code"] != 0:
        failure = "command_failed"
    elif kind == "tests" and (passed is None or passed + (failed or 0) == 0):
        failure = "no_executed_test_evidence"
    elif kind == "tests" and failed:
        failure = "test_failure"
    elif kind == "tests" and expected_tests is not None and (passed or 0) < expected_tests:
        failure = "test_count_below_declared_baseline"
    status = _cli_status(capture["raw_exit_code"])
    if failure is not None and status == 0:
        status = 1
    receipt = {
        "success": failure is None,
        "kind": kind,
        "passed": passed,
        "failed": failed,
        "exit_code": status,
        "failure_kind": failure,
        **capture,
        "stdout_log": str(stdout_log),
        "stderr_log": str(stderr_log),
        "stdout_sha256": hashlib.sha256(raw_stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(raw_stderr).hexdigest(),
        "command": list(argv),
        "cwd": str(root),
        "output_mode": output_mode,
        "expected_tests": expected_tests,
        "timeout_seconds": timeout_seconds,
        "log_capture_limit_bytes": max_output_bytes,
        "environment_override_keys": sorted(env_updates or {}),
        "process_cleanup_scope": "process_group" if os.name == "posix" else "direct_child",
        "started_at": started_at,
        "wall_seconds": time.monotonic() - started,
    }
    receipt_path = directory / "receipt.json"
    receipt_bytes = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
    receipt_path.write_bytes(receipt_bytes)
    return {
        **receipt,
        "receipt_log": str(receipt_path),
        "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "_stdout": stdout,
        "_stderr": stderr,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "--output-mode", choices=MODES, default="counts_and_failures")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--log-root", type=Path)
    parser.add_argument("--kind", choices=("tests", "typecheck"), default="tests")
    parser.add_argument("--expected-tests", type=int)
    parser.add_argument("--timeout-seconds", type=float, default=45)
    parser.add_argument("--max-output-bytes", type=int, default=1048576)
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Override an allowed nonsecret check setting; repeat as needed",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    updates = {}
    for item in args.env:
        key, separator, value = item.partition("=")
        if not separator or key not in ENVIRONMENT_KEYS:
            parser.error("--env requires an allowed NAME=VALUE check setting")
        updates[key] = value
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        result = run_check(
            command,
            args.cwd,
            args.log_root,
            args.output,
            args.kind,
            args.expected_tests,
            args.timeout_seconds,
            args.max_output_bytes,
            updates,
        )
    except (ValueError, OSError) as error:
        parser.error(str(error))
    stdout, stderr = result["_stdout"], result["_stderr"]
    display = {key: result[key] for key in _CLI_RECEIPT_KEYS}
    if display["failed"] is None:
        display["failed"] = 0
    for key in ("stdout_log", "stderr_log"):
        path = Path(display[key])
        try:
            display[key] = str(path.relative_to(result["cwd"]))
        except ValueError:
            # Explicit external artifact roots keep their unambiguous path.
            pass
    if args.output == "structured":
        if not result["success"]:
            display["diagnostic"] = (stdout + ("\n" + stderr if stderr else ""))[:_CONSOLE_BYTES]
    elif args.output == "full" or not result["success"]:
        diagnostic = stdout + ("\n" + stderr if stderr else "")
        print(diagnostic[:_CONSOLE_BYTES], end="\n")
        if len(diagnostic) > _CONSOLE_BYTES:
            print(
                "Console display bounded; complete bounded raw logs retained at the receipt paths."
            )
    print(json.dumps(display, separators=(",", ":")))
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
