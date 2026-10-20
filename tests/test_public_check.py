"""Portable runner canaries: synthetic child processes only, no native models."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "src/memglide/integrations/public_check.py"
SPEC = importlib.util.spec_from_file_location("portable_public_check", MODULE)
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


def python(code: str) -> list[str]:
    return [sys.executable, "-c", code]


@pytest.mark.parametrize(
    ("stdout", "stderr", "expected"),
    [
        ("=== 12 passed, 2 skipped in 0.1s ===", "", (12, 0)),
        ("=== 2 failed, 3 passed in 0.1s ===", "", (3, 2)),
        ("=== 2 failed in 0.1s ===", "", (0, 2)),
        ("Test Files 2 passed (2)\n Tests 7 passed | 1 skipped (8)", "", (7, 0)),
        ("\x1b[32mTests 3 passed\x1b[0m", "", (3, 0)),
        (" 4 passing (1ms)\n 1 failing", "", (4, 1)),
        ("# tests 3\n# pass 2\n# fail 1\n", "", (2, 1)),
        ("", "Ran 4 tests in 0.01s\n\nOK (skipped=1)\n", (3, 0)),
        ("", "Ran 4 tests in 0.01s\n\nFAILED (failures=1, errors=1, skipped=1)\n", (1, 2)),
        ("1 skipped in 0.1s", "", (0, 0)),
        ("no tests ran in 0.1s", "", (0, 0)),
        ("", "", (None, None)),
        ('{"numTotalTests":3,"numPassedTests":2,"numFailedTests":1}', "", (2, 1)),
        ('{"stats":{"passes":3,"failures":0,"pending":1}}', "", (3, 0)),
    ],
)
def test_summary_formats(stdout, stderr, expected):
    assert check.counts(stdout, stderr) == expected


def test_real_status_and_complete_hash_bound_logs(tmp_path):
    result = check.run_check(
        python("import sys;print('3 passed');print('warning',file=sys.stderr);sys.exit(7)"),
        tmp_path,
    )
    assert result["success"] is False
    assert result["raw_exit_code"] == result["exit_code"] == 7
    assert result["failure_kind"] == "command_failed"
    assert result["passed"] == 3
    for stream, expected in (("stdout", b"3 passed\n"), ("stderr", b"warning\n")):
        raw = Path(result[stream + "_log"]).read_bytes()
        assert raw == expected
        assert result[stream + "_sha256"] == hashlib.sha256(raw).hexdigest()
    raw_receipt = Path(result["receipt_log"]).read_bytes()
    assert result["receipt_sha256"] == hashlib.sha256(raw_receipt).hexdigest()
    stored = json.loads(raw_receipt)
    assert stored["command"] == result["command"]
    assert stored["raw_exit_code"] == 7


@pytest.mark.parametrize(
    ("code", "kind", "expected", "failure"),
    [
        ("print('2 passed')", "tests", 2, None),
        ("print('1 passed')", "tests", 2, "test_count_below_declared_baseline"),
        ("print('1 failed')", "tests", None, "test_failure"),
        ("print('0 passed')", "tests", None, "no_executed_test_evidence"),
        ("print('1 skipped')", "tests", None, "no_executed_test_evidence"),
        ("pass", "tests", None, "no_executed_test_evidence"),
        ("pass", "typecheck", None, None),
    ],
)
def test_behavior_evidence_and_typechecks(tmp_path, code, kind, expected, failure):
    result = check.run_check(python(code), tmp_path, kind=kind, expected_tests=expected)
    assert result["failure_kind"] == failure
    assert result["raw_exit_code"] == 0
    assert result["success"] is (failure is None)
    assert result["exit_code"] == (0 if failure is None else 1)


def test_binary_logs_are_not_reencoded(tmp_path):
    result = check.run_check(
        python("import os;os.write(1,b'2 passed\\n\\xff');os.write(2,b'\\xfe')"), tmp_path
    )
    assert result["success"]
    assert Path(result["stdout_log"]).read_bytes() == b"2 passed\n\xff"
    assert Path(result["stderr_log"]).read_bytes() == b"\xfe"


def test_exact_cap_can_pass_but_overflow_always_fails(tmp_path):
    exact = check.run_check(
        python("import os;os.write(1,b'x'*100)"), tmp_path, kind="typecheck", max_output_bytes=100
    )
    assert exact["success"] and exact["captured_output_bytes"] == 100
    result = check.run_check(
        python("import os;os.write(1,b'a'*1000);os.write(2,b'b'*1000)"),
        tmp_path,
        kind="typecheck",
        max_output_bytes=125,
    )
    assert not result["success"]
    assert result["failure_kind"] == "output_limit"
    assert result["output_limit_exceeded"]
    assert result["captured_output_bytes"] == 125
    assert sum(Path(result[name + "_log"]).stat().st_size for name in ("stdout", "stderr")) == 125
    assert result["exit_code"] != 0


def test_timeout_retains_flushed_prefix_and_fails(tmp_path):
    started = time.monotonic()
    result = check.run_check(
        python("import time;print('before timeout',flush=True);time.sleep(10)"),
        tmp_path,
        kind="typecheck",
        timeout_seconds=0.2,
    )
    assert time.monotonic() - started < 3
    assert result["timed_out"] and not result["success"]
    assert result["failure_kind"] == "timeout"
    assert result["exit_code"] != 0
    assert Path(result["stdout_log"]).read_bytes() == b"before timeout\n"


def test_unbounded_output_is_stopped_at_the_combined_cap(tmp_path):
    started = time.monotonic()
    result = check.run_check(
        python("import os\nwhile True: os.write(1,b'x'*65536)"),
        tmp_path,
        kind="typecheck",
        max_output_bytes=257,
        timeout_seconds=2,
    )
    assert time.monotonic() - started < 3
    assert result["failure_kind"] == "output_limit"
    assert result["captured_output_bytes"] == 257
    assert Path(result["stdout_log"]).read_bytes() == b"x" * 257
    assert result["raw_exit_code"] != 0


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal escalation")
def test_timeout_escalates_for_a_child_ignoring_termination(tmp_path):
    result = check.run_check(
        python(
            "import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print('ready',flush=True);time.sleep(10)"
        ),
        tmp_path,
        kind="typecheck",
        timeout_seconds=0.2,
    )
    assert result["failure_kind"] == "timeout"
    assert result["raw_exit_code"] == -signal.SIGKILL
    assert result["exit_code"] == 128 + signal.SIGKILL


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group ownership semantics")
def test_descendant_cleanup_after_parent_exit(tmp_path):
    marker = tmp_path / "leaked-child"
    # This delayed write would prove that a child survived the check's group.
    child = (
        "import pathlib,time;time.sleep(.6);pathlib.Path("
        + repr(str(marker))
        + ").write_text('leaked')"
    )
    parent = (
        "import subprocess,sys;subprocess.Popen([sys.executable,'-c',"
        + repr(child)
        + "]);print('1 passed',flush=True)"
    )
    result = check.run_check(python(parent), tmp_path, timeout_seconds=2)
    assert result["success"]
    assert result["process_cleanup_scope"] == "process_group"
    time.sleep(0.7)
    assert not marker.exists()


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal exit status")
def test_signal_status_keeps_raw_signal_and_shell_status(tmp_path):
    result = check.run_check(
        python("import os,signal;os.kill(os.getpid(),signal.SIGTERM)"), tmp_path, kind="typecheck"
    )
    assert result["raw_exit_code"] == -signal.SIGTERM
    assert result["exit_code"] == 128 + signal.SIGTERM
    assert not result["success"]


def test_launch_failure_is_explicit_and_does_not_execute_shell(tmp_path):
    result = check.run_check([str(tmp_path / "missing; echo injected")], tmp_path, kind="typecheck")
    assert result["failure_kind"] == "launch_error"
    assert result["raw_exit_code"] is None and result["exit_code"] == 127
    assert "FileNotFoundError" in result["_stderr"]


def test_explicit_allowed_environment_and_relative_log_root(tmp_path):
    result = check.run_check(
        python("import os;print(os.environ['CI']);print('1 passed')"),
        tmp_path,
        log_root="logs",
        env_updates={"CI": "portable-check"},
    )
    assert result["success"] and result["_stdout"].startswith("portable-check\n")
    assert Path(result["stdout_log"]).is_relative_to(tmp_path / "logs")
    assert result["environment_override_keys"] == ["CI"]
    assert "portable-check" not in Path(result["receipt_log"]).read_text()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"argv": "echo 1 passed"},
        {"argv": []},
        {"argv": ["x\x00"]},
        {"timeout_seconds": 0},
        {"timeout_seconds": float("nan")},
        {"max_output_bytes": True},
        {"max_output_bytes": 0},
        {"expected_tests": 0},
        {"expected_tests": True},
        {"kind": "typecheck", "expected_tests": 1},
        {"env_updates": {"SSL_CERT_FILE": "/untrusted"}},
        {"env_updates": {"CI": None}},
        {"output_mode": "silent"},
    ],
)
def test_invalid_inputs_rejected_before_launch(tmp_path, kwargs):
    options = {"argv": python("raise AssertionError('must not launch')"), "cwd": tmp_path, **kwargs}
    with pytest.raises(ValueError):
        check.run_check(**options)
    assert not (tmp_path / ".memglide-check").exists()


def test_cli_structured_success_and_actual_failure_status(tmp_path):
    prefix = [sys.executable, str(MODULE), "--cwd", str(tmp_path), "--output", "structured"]
    success = subprocess.run(
        prefix + ["--expected-tests", "2", "--", *python("print('2 passed')")],
        capture_output=True,
        text=True,
        timeout=5,
    )
    receipt = json.loads(success.stdout)
    assert success.returncode == 0 and receipt["success"]
    assert receipt["passed"] == 2 and "_stdout" not in receipt
    failed = subprocess.run(
        prefix + ["--kind", "typecheck", "--", *python("import sys;sys.exit(9)")],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert failed.returncode == 9
    assert json.loads(failed.stdout)["raw_exit_code"] == 9


def test_cli_rejects_sensitive_environment_name(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE),
            "--cwd",
            str(tmp_path),
            "--env",
            "HTTP_PROXY=disabled",
            "--",
            *python("pass"),
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert "allowed NAME=VALUE" in result.stderr
    assert not (tmp_path / ".memglide-check").exists()


@pytest.mark.parametrize("failure", [False, True])
def test_cli_stable_receipt_interface_and_relative_paths(tmp_path, failure):
    code = "print('1 failed')" if failure else "print('1 passed')"
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE),
            "--cwd",
            str(tmp_path),
            "--output",
            "structured",
            "--",
            *python(code),
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    receipt = json.loads(result.stdout)
    expected = {
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
    }
    assert set(receipt) == expected | ({"diagnostic"} if failure else set())
    assert result.returncode == (1 if failure else 0)
    for key in ("stdout_log", "stderr_log"):
        relative = Path(receipt[key])
        assert not relative.is_absolute()
        assert relative.parts[0] == ".memglide-check"
        assert relative.parts[1].startswith("check-")
        assert (tmp_path / relative).is_file()
    stored = json.loads((tmp_path / receipt["stdout_log"]).with_name("receipt.json").read_text())
    assert "captured_output_bytes" in stored and "wall_seconds" in stored
    assert Path(stored["stdout_log"]).is_absolute()


def test_cli_external_logs_keep_absolute_paths(tmp_path):
    cwd = tmp_path / "source"
    cwd.mkdir()
    logs = tmp_path / "artifacts"
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE),
            "--cwd",
            str(cwd),
            "--log-root",
            str(logs),
            "--output",
            "structured",
            "--",
            *python("print('1 passed')"),
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0
    receipt = json.loads(result.stdout)
    assert Path(receipt["stdout_log"]).is_absolute()
    assert Path(receipt["stdout_log"]).is_relative_to(logs)


def test_cli_silent_typecheck_uses_studied_zero_failure_count(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE),
            "--cwd",
            str(tmp_path),
            "--output",
            "structured",
            "--kind",
            "typecheck",
            "--",
            *python("pass"),
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    receipt = json.loads(result.stdout)
    assert result.returncode == 0 and receipt["success"]
    assert receipt["passed"] is None and receipt["failed"] == 0
    stored = json.loads((tmp_path / receipt["stdout_log"]).with_name("receipt.json").read_text())
    assert stored["passed"] is None and stored["failed"] is None


def test_cli_console_trim_notice_matches_stable_interface(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE),
            "--cwd",
            str(tmp_path),
            "--output",
            "full",
            "--",
            *python("print('x'*17000);print('1 passed')"),
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0
    assert (
        "Console display bounded; complete bounded raw logs retained at the receipt paths."
        in result.stdout
    )
    receipt = json.loads(result.stdout.splitlines()[-1])
    assert (tmp_path / receipt["stdout_log"]).stat().st_size > 17000


@pytest.mark.parametrize("case", ["default", "nested", "absolute", "internal_alias"])
def test_repository_log_symlinks_are_rejected_before_launch(tmp_path, case):
    root = tmp_path / "source"
    root.mkdir()
    target = root / "actual-logs" if case == "internal_alias" else tmp_path / "outside"
    target.mkdir()
    if case == "default":
        (root / ".memglide-check").symlink_to(target, target_is_directory=True)
        requested = None
    else:
        (root / "logs").symlink_to(target, target_is_directory=True)
        requested = (
            root / "logs/nested"
            if case == "absolute"
            else ("logs/nested" if case == "nested" else "logs")
        )
    command = python("from pathlib import Path;Path('launched').write_text('unexpected')")
    with pytest.raises(ValueError, match="log roots must not traverse symlinks"):
        check.run_check(command, root, log_root=requested, kind="typecheck")
    assert not (root / "launched").exists()
    assert not list(target.iterdir())
