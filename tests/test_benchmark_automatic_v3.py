"""Offline-v3 harness controls; no upstream corpus, policy queries or models."""

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
    "run_automatic_v3", Path(__file__).resolve().parents[1] / "benchmarks/run_automatic_v3.py"
)
assert _SPEC is not None and _SPEC.loader is not None
run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run)


def synthetic_tasks() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tasks, grading = [], {}
    for index in range(12):
        identifier, repository = f"t{index + 1:02d}", f"r{index // 3 + 1:02d}"
        control = index % 3 == 2
        tasks.append({"id": identifier, "repository": repository,
                      "language": "python" if index < 6 else "typescript",
                      "prompt": "Clarify this repository." if control else f"Adjust arithmetic boundary behavior for operation {index}."})
        grading[identifier] = {"kind": "abstention_control" if control else "positive",
                               "required_paths": [] if control else [f"src/operation_{index}.py"],
                               "rationale": "Deliberately underspecified synthetic control." if control else "Synthetic declaration scope."}
    return tasks, grading


def test_public_private_schema_is_separate_and_control_counts_fixed() -> None:
    tasks, grading = synthetic_tasks()
    run.validate_tasks(tasks, grading)
    assert len(tasks) == 12
    assert Counter(grade["kind"] for grade in grading.values()) == {"positive": 8, "abstention_control": 4}


@pytest.mark.parametrize("change", ["public_target", "path_hint", "missing_positive", "control_target", "missing_control_rationale", "duplicate", "unsafe_path"])
def test_task_or_oracle_leakage_and_invalid_ground_truth_refused(change: str) -> None:
    tasks, grading = synthetic_tasks()
    if change == "public_target":
        tasks[0]["required_paths"] = grading["t01"]["required_paths"]
    elif change == "path_hint":
        tasks[0]["prompt"] += " Inspect operation_0.py."
    elif change == "missing_positive":
        grading["t01"]["required_paths"] = []
    elif change == "control_target":
        grading["t03"]["required_paths"] = ["source.py"]
    elif change == "missing_control_rationale":
        grading["t03"]["rationale"] = ""
    elif change == "duplicate":
        tasks[1]["id"] = tasks[0]["id"]
    else:
        grading["t01"]["required_paths"] = ["../outside.py"]
    with pytest.raises(ValueError):
        run.validate_tasks(tasks, grading)


def test_four_arm_balanced_pair_precedence_and_neutral_unique_ordinals() -> None:
    tasks, _ = synthetic_tasks()
    rows = run.order(tasks)
    assert len(rows) == 96 and [row["ordinal"] for row in rows] == list(range(1, 97))
    assert len({(row["task_id"], row["arm"], row["repeat"]) for row in rows}) == 96
    assert rows == run.order(tasks)
    for task in tasks:
        first = [row["arm"] for row in rows if row["task_id"] == task["id"] and row["repeat"] == 1]
        second = [row["arm"] for row in rows if row["task_id"] == task["id"] and row["repeat"] == 2]
        assert first == list(reversed(second)) and set(first) == set(run.ARMS)
    with pytest.raises(ValueError):
        run.order(tasks, repeats=3)


@pytest.mark.parametrize("path", [".", "../escape.py", "/outside.py", "a//b.py", "a\\b.py", "a/\ud800.py"])
def test_unsafe_relative_targets_rejected(path: str) -> None:
    assert not run.safe_relative(path)


def test_snapshot_refuses_symlinks_and_oversized_files(tmp_path: Path) -> None:
    (tmp_path / "code.py").write_text("VALUE = 1\n")
    assert run.tree_hashes(tmp_path) == {"code.py": run.sha(b"VALUE = 1\n")}
    (tmp_path / "link.py").symlink_to(tmp_path / "code.py")
    with pytest.raises(ValueError, match="symlinks"):
        run.tree_hashes(tmp_path)
    (tmp_path / "link.py").unlink()
    (tmp_path / "oversized").write_bytes(b"x" * 512_001)
    with pytest.raises(ValueError, match="bounds"):
        run.tree_hashes(tmp_path)


def test_output_refuses_existing_and_symlink_ancestor(tmp_path: Path) -> None:
    output = run.new_directory(tmp_path / "new")
    (output / "keep").write_text("original")
    with pytest.raises(FileExistsError):
        run.new_directory(output)
    link = tmp_path / "link"
    link.symlink_to(output, target_is_directory=True)
    with pytest.raises(ValueError):
        run.new_directory(link / "nested")
    assert (output / "keep").read_text() == "original"


def test_freeze_is_pre_corpus_and_policy_drift_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seal = {"head": "frozen-test", "files": {"src/test.py": "hash"}}
    monkeypatch.setattr(run, "policy_seal", lambda: copy.deepcopy(seal))
    record = run.freeze(tmp_path / "freeze")
    assert record["corpus_selected_or_inspected"] is False
    run.verify_freeze(record)
    seal["files"]["src/test.py"] = "changed"
    with pytest.raises(ValueError, match="after pre-corpus freeze"):
        run.verify_freeze(record)


def test_runtime_and_provenance_cannot_drift_after_freeze(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seal = {"head": "fixed", "files": {}}
    monkeypatch.setattr(run, "policy_seal", lambda: seal)
    record = run.freeze(tmp_path / "freeze")
    record["dependencies"]["tree-sitter-typescript"] = "changed"
    with pytest.raises(ValueError):
        run.verify_freeze(record)
    tasks, _ = synthetic_tasks()
    provenance = {}
    for identifier in {task["repository"] for task in tasks}:
        root = tmp_path / identifier
        root.mkdir()
        (root / "LICENSE").write_text("Controlled test fixture license")
        (root / "source.py").write_text("VALUE = 1\n")
        provenance[identifier] = {"commit": "1" * 40, "archive_sha256": "2" * 64,
                                  "repository_url": "https://github.com/fictional/test-owned",
                                  "archive_url": "https://codeload.github.com/fictional/test-owned/tar.gz/" + "1" * 40,
                                  "tracked_tree_status": "complete", "exclusions": [], "license_paths": ["LICENSE"],
                                  "retained_file_sha256": run.tree_hashes(root)}
    run.validate_provenance(provenance, tmp_path, tasks)
    (tmp_path / "r01" / "source.py").write_text("VALUE = 2\n")
    with pytest.raises(ValueError, match="hashes differ"):
        run.validate_provenance(provenance, tmp_path, tasks)


def test_auto_worker_rejects_any_target_or_task_identifier_before_imports(tmp_path: Path) -> None:
    request = tmp_path / "request.json"
    for forbidden in ({"known_paths": []}, {"task_id": "t01"}, {"grading": {"path": "secret"}}):
        run.dump(request, {"arm": "C", "prompt": "Public task", "worktree": "/unused", "settings": run.SETTINGS, **forbidden})
        with pytest.raises(ValueError, match="target metadata"):
            run.worker(request)


SOURCE = "def example(value):\r\n    return value + 1\r\n"
PATH = "src/example.py"


def prepared() -> dict[str, Any]:
    prompt = "Change example arithmetic."
    addition = json.dumps({"notice": run.NOTICE, "memglide_sources": [{"path": PATH, "content": SOURCE}]}, separators=(",", ":")) + "\n\nTask:\n"
    return {"mode": "preloaded", "prompt": addition + prompt, "context_bytes": len(addition.encode()),
            "files": [{"path": PATH, "sha256": run.sha(SOURCE.encode()), "start_line": 1, "end_line": 2}]}


def fake_git_bytes(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    commands = []

    def completed(command: list[str], **kwargs: Any) -> Any:
        commands.append(command)
        assert command == ["git", "cat-file", "blob", "frozen-commit:" + PATH]
        assert kwargs["cwd"] == "/canonical" and kwargs["timeout"] == 10
        return subprocess.CompletedProcess(command, 0, stdout=SOURCE.encode())

    monkeypatch.setattr(run.subprocess, "run", completed)
    return commands


def test_complete_bytes_hashes_ranges_reconstructed_from_canonical_git(monkeypatch: pytest.MonkeyPatch) -> None:
    commands = fake_git_bytes(monkeypatch)
    verified = run.verify_delivery(prepared(), "Change example arithmetic.", {"path": "/canonical", "commit": "frozen-commit"})
    assert verified == {"valid": True, "selected_paths": [PATH], "source_versions": {PATH: run.sha(SOURCE.encode())}, "selected_source_bytes": len(SOURCE.encode())}
    assert len(commands) == 1


@pytest.mark.parametrize("change", ["clipped", "hash", "range", "task", "budget", "duplicate", "path_escape", "notice", "duplicate_json", "noncanonical"])
def test_false_fidelity_never_qualifies_as_useful_context(monkeypatch: pytest.MonkeyPatch, change: str) -> None:
    fake_git_bytes(monkeypatch)
    result = prepared()
    if change == "clipped":
        result["prompt"] = result["prompt"].replace("value + 1", "value")
    elif change == "hash":
        result["files"][0]["sha256"] = "0" * 64
    elif change == "range":
        result["files"][0]["end_line"] = 1
    elif change == "task":
        result["prompt"] += " changed task"
    elif change == "budget":
        result["context_bytes"] -= 1
    elif change == "duplicate":
        result["files"].append(copy.deepcopy(result["files"][0]))
    elif change == "path_escape":
        result["files"][0]["path"] = "../escape.py"
    elif change == "duplicate_json":
        result["prompt"] = result["prompt"].replace('{"notice":', '{"memglide_sources":[{"path":"extra.py","content":"extra"}],"notice":', 1)
    elif change == "noncanonical":
        raw = result["prompt"].split("\n\nTask:\n")[0]
        result["prompt"] = json.dumps(json.loads(raw), indent=2) + "\n\nTask:\nChange example arithmetic."
    else:
        result["prompt"] = result["prompt"].replace("Complete snapshot", "Partial snapshot")
    with pytest.raises((ValueError, AssertionError)):
        run.verify_delivery(result, "Change example arithmetic.", {"path": "/canonical", "commit": "frozen-commit"})


def test_passthrough_and_positive_miss_are_distinct_from_negative_control_pass() -> None:
    result = {"mode": "passthrough", "prompt": "EXACT", "files": [], "context_bytes": 0}
    fidelity = run.verify_delivery(result, "EXACT", {})
    assert run.grade_scope(fidelity, {"kind": "positive", "required_paths": [PATH]})["declared_scope_complete"] is False
    assert run.grade_scope(fidelity, {"kind": "abstention_control", "required_paths": []})["expected_bypass"] is True
    result["prompt"] += "modified"
    with pytest.raises(ValueError):
        run.verify_delivery(result, "EXACT", {})


@pytest.mark.parametrize("failure", ["exit", "timeout", "malformed", "interrupt"])
def test_original_worker_failure_logs_preserved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    class Process:
        returncode = 1 if failure == "exit" else 0

        def wait(self, timeout: int) -> int:
            if failure == "timeout":
                raise subprocess.TimeoutExpired("controlled-test-worker", timeout)
            if failure == "interrupt":
                raise KeyboardInterrupt
            return self.returncode

    def failed(command: list[str], **kwargs: Any) -> Any:
        assert command[:4] == [run.sys.executable, "-m", "benchmarks.run_automatic_v3", "worker"]
        kwargs["stdout"].write(b"original partial" if failure != "exit" else b'{"source_mutations":"","preparation":{}}')
        kwargs["stderr"].write(b"original failure")
        assert kwargs["start_new_session"] == (run.os.name == "posix")
        return Process()

    stopped = []
    monkeypatch.setattr(run.subprocess, "Popen", failed)
    monkeypatch.setattr(run, "stop_process_group", lambda process: stopped.append(process))
    result = run.run_child(tmp_path / "request.json", tmp_path)
    assert not result["worker_completed"]
    assert (tmp_path / "stdout.log").stat().st_size > 0
    assert (tmp_path / "stderr.log").read_text() == "original failure"
    assert len(stopped) == 1  # Includes abnormal exit after the main worker ends.


def test_process_group_cleanup_targets_only_the_started_group(monkeypatch: pytest.MonkeyPatch) -> None:
    if run.os.name != "posix":
        pytest.skip("POSIX group cleanup control")
    signals, waits = [], []

    class Process:
        pid = 123456789

        def wait(self, timeout: int) -> None:
            waits.append(timeout)

    monkeypatch.setattr(run.os, "killpg", lambda pid, sig: signals.append((pid, sig)))
    run.stop_process_group(Process())
    assert signals == [(123456789, run.signal.SIGTERM), (123456789, run.signal.SIGKILL)]
    assert waits == [2, 2]


def fake_rows(tasks: list[dict[str, Any]], grading: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for assignment in run.order(tasks):
        scope = grading[assignment["task_id"]]
        control = scope["kind"] == "abstention_control"
        rows.append({**assignment, "worker_completed": True, "fidelity": {"valid": True},
                     "scope_grade": {"declared_scope_complete": None if control else True, "expected_bypass": True if control else None},
                     "metrics": {"preparation_wall_seconds": 1.0},
                     "observation": {"preparation": {"mode": "passthrough" if control else "preloaded"}}})
    return rows


def test_planned_denominators_failed_and_unrun_are_not_hidden(monkeypatch: pytest.MonkeyPatch) -> None:
    tasks, grading = synthetic_tasks()
    monkeypatch.setattr(run, "clustered_effect", lambda pairs: {"task_clusters": len(pairs), "pairs": sum(len(values) for values in pairs.values())})
    rows = fake_rows(tasks, grading)
    complete = run.summarize(rows, tasks, grading, 2)
    assert complete["integrity_complete"] and complete["arms"]["C"]["positive_complete"] == 16
    assert complete["arms"]["C"]["control_expected_bypasses"] == 8
    assert complete["arms"]["C"]["consistent_tasks_both_repeats"] == {"positive": 8, "abstention_control": 4}
    failed = next(row for row in rows if row["arm"] == "C")
    failed["worker_completed"] = False
    failed["fidelity"] = {"valid": False}
    # A previously written successful grade must not count after integrity fails.
    failed.pop("metrics")
    rows.pop(next(index for index, row in enumerate(rows) if row["arm"] == "V2"))
    result = run.summarize(rows, tasks, grading, 2)
    assert not result["integrity_complete"] and result["unrun_assignments"] == 1
    assert result["arms"]["C"]["planned"] == 24 and result["arms"]["C"]["worker_errors"] == 1
    assert result["arms"]["V2"]["observed"] == 23 and result["arms"]["V2"]["planned"] == 24
    assert result["arms"]["C"]["metrics"]["preparation_wall_seconds"]["missing_of_planned"] == 1
    assert sum(result["arms"]["C"][key] for key in ("positive_complete", "control_expected_bypasses")) == 23
    assert "actual_order_counts" in result and "language_strata" in result


def test_task_cluster_intervals_retain_repeats_and_unknown_is_null(monkeypatch: pytest.MonkeyPatch) -> None:
    effect = run.clustered_effect({"t01": [(10, 8), (11, 9)], "t02": [(20, 18), (21, 19)]})
    assert effect["task_clusters"] == 2 and effect["pairs"] == 4
    assert effect["mean_delta"] == effect["median_delta"] == -2
    assert effect["mean_bootstrap95"] == effect["median_bootstrap95"] == [-2, -2]
    assert "retaining both repeats" in effect["interval_unit"]
    monkeypatch.setattr(run.sys, "platform", "darwin")
    assert all(value is None for value in run.resources().values())
    assert run.clustered_effect({})["mean_delta"] is None


def test_grading_error_retains_original_worker_observation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tasks, grading = synthetic_tasks()
    assignment = {"ordinal": 1, "task_id": "t01", "arm": "C", "repeat": 1}
    plan = {"tasks": tasks, "grading": grading, "repeats": 2, "assignments": [assignment],
            "repositories": {"r01": {"path": "/canonical", "commit": "frozen"}}}
    plan_path = tmp_path / "plan.json"
    run.dump(plan_path, plan)
    original_plan = plan_path.read_bytes()
    original = {"preparation": {"prompt": "wrong"}, "source_mutations": ""}
    monkeypatch.setattr(run, "verify_plan", lambda *args: None)
    monkeypatch.setattr(run, "git", lambda *args: "")
    def completed_then_drift(*args: Any) -> dict[str, Any]:
        plan_path.write_text('{"changed":true}\n')
        return {"worker_completed": True, "observation": copy.deepcopy(original)}

    monkeypatch.setattr(run, "run_child", completed_then_drift)
    monkeypatch.setattr(run, "verify_delivery", lambda *args: (_ for _ in ()).throw(ValueError("bad source fidelity")))
    monkeypatch.setattr(run, "clustered_effect", lambda pairs: {"pairs": 0})
    report = run.evaluate(plan_path, tmp_path / "report")
    assert report["rows"][0]["observation"] == original
    assert report["rows"][0]["worker_completed"] is True
    assert report["rows"][0]["fidelity"]["valid"] is False
    assert report["seal_unchanged"] is False and "plan file changed" in report["seal_error"]
    assert report["plan_sha256"] == run.sha(original_plan)
    assert (tmp_path / "report" / "plan-input.json").read_bytes() == original_plan
    assert report["summary"]["unrun_assignments"] == 95
    assert report["actual_billed_charges"] is None and report["coding_task_success"] is None
    assert report["dispatched_model_requests"] == 0


def test_interrupted_worker_writes_partial_report_with_unrun_plan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tasks, grading = synthetic_tasks()
    assignments = run.order(tasks)
    repositories = {task["repository"]: {"path": "/canonical", "commit": "frozen"} for task in tasks}
    plan = {"tasks": tasks, "grading": grading, "repeats": 2, "assignments": assignments, "repositories": repositories}
    plan_path = tmp_path / "plan.json"
    run.dump(plan_path, plan)
    monkeypatch.setattr(run, "verify_plan", lambda *args: None)
    monkeypatch.setattr(run, "git", lambda *args: "")
    monkeypatch.setattr(run, "run_child", lambda *args: {"worker_completed": False, "interrupted": True, "process_wall_seconds": 3.0, "error": "KeyboardInterrupt"})
    monkeypatch.setattr(run, "clustered_effect", lambda pairs: {"pairs": 0})
    report = run.evaluate(plan_path, tmp_path / "report")
    assert report["interrupted"] and len(report["rows"]) == 1
    assert report["summary"]["unrun_assignments"] == 95
    assert not report["summary"]["integrity_complete"]
    arm = report["rows"][0]["arm"]
    assert report["summary"]["arms"][arm]["all_attempted_process_wall_seconds"]["mean"] == 3.0
    assert (tmp_path / "report" / "report.json").exists()
