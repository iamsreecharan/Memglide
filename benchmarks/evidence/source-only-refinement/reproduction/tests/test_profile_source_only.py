"""Bounded source-only harness controls; no real performance cohort is executed."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "profile_source_only", Path(__file__).resolve().parents[1] / "benchmarks/profile_source_only.py"
)
assert _SPEC is not None and _SPEC.loader is not None
probe = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(probe)


def test_balanced_seeded_paired_units_and_separate_instrumentation() -> None:
    rows = probe.assignments()
    perf = [row for row in rows if row["kind"] == "performance"]
    assert len(perf) == 72 and len(rows) == 78
    assert probe.assignments() == rows and probe.assignments(seed=1) != rows
    for kind in probe.FIXTURES:
        selected = [row for row in perf if row["fixture"] == kind]
        assert Counter(row["arm"] for row in selected[::2]) == {"baseline": 6, "candidate": 6}
        for first, second in zip(selected[::2], selected[1::2], strict=True):
            assert first["repeat"] == second["repeat"]
            assert first["arm"] != second["arm"]
    assert len({(row["fixture"], row["repeat"], row["arm"]) for row in perf}) == 72


@pytest.mark.parametrize("repeats,seed", [(0, 1), (13, 1), (True, 1), (12, -1), (12, 2**32)])
def test_resource_bounds(repeats: int, seed: int) -> None:
    with pytest.raises(ValueError):
        probe.assignments(repeats, seed)


def test_typical_dense_exact_source_control_and_8k_policy() -> None:
    typical, short = probe.fixture("typical")
    dense, long = probe.fixture("dense")
    assert dense == typical and len(dense) == 4
    assert len(short) == 3 and len(long) == 1
    assert len(long[".gitignore"].encode()) == 8192
    assert probe.canonical(typical) == probe.canonical(dense)
    assert len(probe.fixture("noignore")[0]) == 1
    with pytest.raises(ValueError):
        probe.fixture("not-a-fixture")


def test_canonical_complete_source_and_stable_fields_are_not_forgiven() -> None:
    sources, _ = probe.fixture("typical")
    expected = probe.canonical(sources)
    content = json.loads(expected["prompt"].split("\n\nTask:\n")[0])
    assert {row["path"]: row["content"] for row in content["memglide_sources"]} == sources
    assert expected["context_format"] == "compact-prefix"
    assert probe.stable({**expected, "preparation_wall_seconds": 9.9, "preparation_cpu_seconds": 1}) == expected
    wrong = {**expected, "reason": "different"}
    assert probe.stable(wrong) != expected
    assert probe.stable({**expected, "new_unverified_field": True}) != expected


def test_output_is_new_canonical_and_never_overwritten(tmp_path: Path) -> None:
    directory = probe.new_directory(tmp_path / "new")
    (directory / "keep").write_text("original")
    with pytest.raises(FileExistsError):
        probe.new_directory(directory)
    link = tmp_path / "link"
    link.symlink_to(directory, target_is_directory=True)
    with pytest.raises(ValueError):
        probe.new_directory(link / "nested")
    assert (directory / "keep").read_text() == "original"


@pytest.mark.parametrize("failure", ["exit", "timeout", "malformed", "oversized"])
def test_subprocess_errors_and_original_logs_are_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    def fake_run(command: list[str], **kwargs: Any) -> Any:
        assert command[:3] == [probe.sys.executable, "-m", "benchmarks.profile_source_only"]
        kwargs["stderr"].write(b"original diagnostic")
        if failure == "timeout":
            kwargs["stdout"].write(b"partial original output")
            raise subprocess.TimeoutExpired(command, 30)
        payload = b"{bad json" if failure == "malformed" else b'x' * (probe.MAX_LOG_BYTES + 1) if failure == "oversized" else b'{"valid":false,"calls":[]}'
        kwargs["stdout"].write(payload)
        return subprocess.CompletedProcess(command, 1 if failure == "exit" else 0)

    monkeypatch.setattr(probe.subprocess, "run", fake_run)
    result = probe.run_child(tmp_path / "request.json", tmp_path)
    assert result["valid"] is False
    assert (tmp_path / "stderr.log").read_bytes() == b"original diagnostic"
    assert (tmp_path / "stdout.log").stat().st_size > 0
    if failure == "exit":
        assert result["returncode"] == 1 and result["observation"] == {"valid": False, "calls": []}
    else:
        assert result["observation"] is None and "error" in result


def test_seal_drift_refuses_dispatch_and_preserves_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    states = iter([{"head": "first", "files": {}}, {"head": "changed", "files": {}}])
    monkeypatch.setattr(probe, "seal", lambda: next(states))
    monkeypatch.setattr(probe, "baseline", lambda: ("trusted-test-commit", b"# trusted test snapshot\n"))
    monkeypatch.setattr(probe, "run_child", lambda *args: pytest.fail("must not dispatch"))
    output = tmp_path / "drift"
    with pytest.raises(ValueError, match="before dispatch"):
        probe.run(output, repeats=1)
    assert (output / "manifest.json").exists()
    assert not (output / "report.json").exists()


def test_all_failed_original_workers_remain_in_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(probe, "seal", lambda: {"head": "fixed", "files": {}})
    monkeypatch.setattr(probe, "baseline", lambda: ("trusted-test-commit", b"# trusted test snapshot\n"))
    calls = []

    def failure(request: Path, directory: Path) -> dict[str, Any]:
        calls.append(json.loads(request.read_text()))
        (directory / "stderr.log").write_text("original failed worker")
        return {"valid": False, "observation": None, "error": "original failure"}

    monkeypatch.setattr(probe, "run_child", failure)
    report = probe.run(tmp_path / "failed", repeats=1)
    assert len(calls) == len(report["observations"]) == 12
    assert all(row["error"] == "original failure" for row in report["observations"])
    assert report["summary"]["attempts"] == 6 and report["summary"]["valid_workers"] == 0
    assert not report["summary"]["comparison_valid"]
    assert report["estimated_model_cost"] is None and report["actual_billed_charges"] is None
    assert report["dispatched_model_requests"] == 0


def good_rows() -> list[dict[str, Any]]:
    rows = []
    for assignment in probe.assignments(repeats=1):
        times = 10 if assignment["arm"] == "baseline" else 8
        diagnostic = assignment["kind"] == "diagnostic"
        calls = [{"phase": "first" if index == 0 else "warm", "stable_result": {"exact": True},
                  "timing": None if diagnostic else {"wall_seconds": times, "cpu_seconds": times, "waited_child_cpu_seconds": None},
                  "counts": {key: 0 for key in ("policy_read_attempts", "policy_successful_reads", "policy_read_bytes", "source_read_attempts", "source_successful_reads", "source_read_bytes")}}
                 for index in range(6)]
        rows.append({**assignment, "valid": True, "observation": {"calls": calls, "controls": []}})
    return rows


def test_summary_uses_worker_pair_not_five_inner_calls_and_retains_failures() -> None:
    rows = good_rows()
    summary = probe.summarize(rows, repeats=1)
    assert summary["comparison_valid"]
    effect = summary["fixtures"]["typical"]["effects"]["warm_wall_seconds"]
    assert effect["pairs"] == 1 and effect["mean_delta"] == -2
    assert effect["mean_paired_percent_change"] == -20
    assert effect["baseline_median"] == 10 and effect["candidate_median"] == 8
    assert effect["mean_delta_bootstrap95"] == effect["median_delta_bootstrap95"] == [-2, -2]
    assert "worker" in effect["interval_unit"]
    rows[0]["valid"] = False
    failed = probe.summarize(rows, repeats=1)
    assert failed["attempts"] == 6 and failed["valid_workers"] == 5
    assert not failed["comparison_valid"]
    assert sum(row["invalid_or_missing_pairs"] for row in failed["fixtures"].values()) == 1


def test_instrumentation_detects_read_or_fallback_changes() -> None:
    rows = good_rows()
    row = next(row for row in rows if row["kind"] == "diagnostic" and row["arm"] == "candidate")
    row["observation"]["calls"][0]["counts"]["source_read_attempts"] = 1
    assert not probe.summarize(rows, repeats=1)["comparison_valid"]
    rows = good_rows()
    row = next(row for row in rows if row["kind"] == "diagnostic" and row["arm"] == "candidate")
    row["observation"]["controls"] = [{"different": True}]
    assert not probe.summarize(rows, repeats=1)["comparison_valid"]


def test_worker_false_fidelity_and_explicit_compact_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = tmp_path / "worker"
    directory.mkdir()
    snapshots = tmp_path / "snapshots"
    snapshots.mkdir()
    data = probe.SOURCE.read_bytes()
    (snapshots / "candidate.py").write_bytes(data)
    request = directory / "request.json"
    probe.write_json(request, {"arm": "candidate", "fixture": "noignore", "kind": "performance", "snapshot_sha256": probe.digest(data)})
    expected = probe.canonical(probe.fixture("noignore")[0])
    invocation = []

    def fake_prepare(prompt: str, **kwargs: Any) -> dict[str, Any]:
        assert prompt == probe.TASK and kwargs["context_format"] == "compact-prefix"
        invocation.append(kwargs)
        result = copy.deepcopy(expected)
        if len(invocation) == 2:
            result["prompt"] = "incorrect clipped source"
        return result

    monkeypatch.setattr(probe, "_load_preparer", lambda *args: fake_prepare)
    observation = probe.worker(request)
    assert len(invocation) == 6 and not observation["valid"]
    assert len(observation["calls"]) == 6 and observation["calls"][1]["fidelity"] is False
    assert observation["source_versions"] == {"engine.py": expected["files"][0]["sha256"]}


def test_unsupported_resource_units_and_empty_effects_are_not_estimated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(probe.sys, "platform", "win32")
    assert all(value is None for value in probe.resources().values())
    assert probe.paired_effect([], [])["mean_delta_bootstrap95"] is None
    assert probe.paired_effect([], [])["median_delta_bootstrap95"] is None
    with pytest.raises(ValueError):
        probe.paired_effect([1], [])
