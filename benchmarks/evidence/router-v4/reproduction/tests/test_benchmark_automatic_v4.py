"""Generic v4 runner controls; no held-out corpus, selector calls or models."""

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
    "run_automatic_v4", Path(__file__).resolve().parents[1] / "benchmarks/run_automatic_v4.py"
)
assert _SPEC is not None and _SPEC.loader is not None
run = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run)


def synthetic_tasks() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    positives, controls, grading = [], [], {}
    for index in range(12):
        identifier, repository = f"t{index + 1:02d}", f"r{index // 2 + 1:02d}"
        positives.append({"id": identifier, "repository": repository,
                          "language": "python" if index < 6 else "typescript",
                          "prompt": f"Adjust arithmetic boundary behavior for operation {index}."})
        grading[identifier] = {"kind": "positive", "required_paths": [f"src/operation_{index}.py"],
                               "rationale": "Controlled synthetic source scope."}
    for index in range(4):
        identifier = f"c{index + 1:02d}"
        controls.append({"id": identifier, "repository": f"r{index + 1:02d}",
                         "language": "python" if index < 2 else "typescript",
                         "prompt": "Make this repository nicer."})
        grading[identifier] = {"kind": "abstention_control", "required_paths": [],
                               "rationale": "Normative abstention for unspecified requested behavior."}
    return positives, controls, grading


def fake_plan() -> dict[str, Any]:
    positives, controls, grading = synthetic_tasks()
    return {"positive_tasks": positives, "controls": controls, "grading": grading, "repeats": 2,
            "assignments": run.assignments(positives, controls),
            "repositories": {task["repository"]: {"path": "/canonical", "commit": "frozen"}
                             for task in positives + controls}}


def fake_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [{**assignment, "worker_completed": True, "fidelity": {"valid": True},
             "scope_grade": {"declared_scope_complete": assignment["kind"] == "positive",
                             "expected_bypass": assignment["kind"] == "abstention_control"},
             "metrics": {"preparation_wall_seconds": 1.0 if assignment["arm"] != "C" else 0.5},
             "process_wall_seconds": 2.0} for assignment in plan["assignments"]]


def test_public_private_schema_and_positive_language_root_counts() -> None:
    positives, controls, grading = synthetic_tasks()
    run.validate_tasks(positives, controls, grading)
    assert len(positives) == 12 and len(controls) == 4
    assert Counter(task["language"] for task in positives) == {"python": 6, "typescript": 6}
    assert len({task["repository"] for task in positives}) == 6


@pytest.mark.parametrize("change", ["public_target", "path_hint", "missing_positive", "control_target", "native_fix", "wrong_language", "too_few_roots", "duplicate", "unsafe_path", "missing_control"])
def test_ground_truth_leaks_and_invalid_strata_refused(change: str) -> None:
    positives, controls, grading = synthetic_tasks()
    if change == "public_target":
        positives[0]["required_paths"] = ["source.py"]
    elif change == "path_hint":
        positives[0]["prompt"] += " Inspect operation_0.py."
    elif change == "missing_positive":
        grading["t01"]["required_paths"] = []
    elif change == "control_target":
        grading["c01"]["required_paths"] = ["source.py"]
    elif change == "native_fix":
        grading["t01"]["reference_patch"] = "hidden edit"
    elif change == "wrong_language":
        positives[0]["language"] = "typescript"
    elif change == "too_few_roots":
        positives[-1]["repository"] = positives[-2]["repository"] = "r01"
    elif change == "duplicate":
        positives[1]["id"] = positives[0]["id"]
    elif change == "unsafe_path":
        grading["t01"]["required_paths"] = ["../outside.py"]
    else:
        controls.pop()
    with pytest.raises(ValueError):
        run.validate_tasks(positives, controls, grading)


def test_order_is_deterministic_and_each_task_reverses_arm_precedence() -> None:
    positives, controls, _ = synthetic_tasks()
    rows = run.assignments(positives, controls)
    assert rows == run.assignments(positives, controls)
    assert len(rows) == 96 and [row["ordinal"] for row in rows] == list(range(1, 97))
    assert len({(row["task_id"], row["repeat"], row["arm"]) for row in rows}) == 96
    for task in positives + controls:
        orders = [[row["arm"] for row in rows if row["task_id"] == task["id"] and row["repeat"] == repeat]
                  for repeat in (1, 2)]
        assert orders[0] == list(reversed(orders[1])) and set(orders[0]) == set(run.ARMS)
    for repeat in (1, 2):
        positive = [row for row in rows if row["repeat"] == repeat and row["kind"] == "positive"]
        for position in range(3):
            assert Counter(row["arm"] for row in positive if (row["ordinal"] - 1) % 3 == position) == {"B": 4, "V3": 4, "C": 4}
    assert len(run.assignments(positives, controls, 1)) == 48
    with pytest.raises(ValueError):
        run.assignments(positives, controls, 3)


def test_freeze_records_no_corpus_and_rejects_policy_or_runtime_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seal: dict[str, Any] = {"head": "frozen", "files": {"src/example.py": "hash"}}
    runtime: dict[str, Any] = {"python": "controlled", "dependencies": {"tree-sitter-typescript": "fixed"}}
    monkeypatch.setattr(run, "policy_seal", lambda: copy.deepcopy(seal))
    monkeypatch.setattr(run.base, "runtime_identity", lambda: copy.deepcopy(runtime))
    frozen = run.freeze(tmp_path / "freeze")
    assert not frozen["corpus_selected_or_inspected"]
    run.verify_freeze(frozen)
    runtime["dependencies"]["tree-sitter-typescript"] = "changed"
    with pytest.raises(ValueError, match="after pre-corpus freeze"):
        run.verify_freeze(frozen)
    runtime["dependencies"]["tree-sitter-typescript"] = "fixed"
    seal["files"]["src/example.py"] = "changed"
    with pytest.raises(ValueError):
        run.verify_freeze(frozen)
    with pytest.raises(FileExistsError):
        run.freeze(tmp_path / "freeze")


@pytest.mark.parametrize("forbidden", [{"known_paths": []}, {"task_id": "t01"}, {"grading": {"path": "hidden"}}, {"reference_patch": "hidden"}])
def test_automatic_requests_reject_oracles_before_source_imports(tmp_path: Path, forbidden: dict[str, Any]) -> None:
    path = tmp_path / "request.json"
    run.dump(path, {"arm": "C", "prompt": "Public task", "worktree": "/unused", "settings": run.SETTINGS, **forbidden})
    with pytest.raises(ValueError, match="target/grade"):
        run.worker(path)


def test_distinct_repository_ids_cannot_relabel_one_upstream(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run.base, "validate_provenance", lambda *args: None)
    provenance = {"r01": {"repository_url": "https://github.com/owner/one"},
                  "r02": {"repository_url": "https://github.com/owner/two"}}
    run.validate_provenance(provenance, tmp_path, [])
    provenance["r02"]["repository_url"] = "https://github.com/OWNER/ONE.git/"
    with pytest.raises(ValueError, match="distinct canonical"):
        run.validate_provenance(provenance, tmp_path, [])


def test_verifier_helpers_are_pinned_and_canonical_delivery_required(monkeypatch: pytest.MonkeyPatch) -> None:
    assert run.sha(run.HELPER_PATH.read_bytes()) == run.HELPER_SHA256
    source, path, prompt = "def example(value):\r\n    return value + 1\r\n", "src/example.py", "Change arithmetic."
    def completed(command: list[str], **kwargs: Any) -> Any:
        assert command == ["git", "cat-file", "blob", "frozen:" + path]
        return subprocess.CompletedProcess(command, 0, stdout=source.encode())
    monkeypatch.setattr(run.base.subprocess, "run", completed)
    addition = json.dumps({"notice": run.base.NOTICE, "memglide_sources": [{"path": path, "content": source}]}, separators=(",", ":")) + "\n\nTask:\n"
    preparation: dict[str, Any] = {"mode": "preloaded", "prompt": addition + prompt, "context_bytes": len(addition.encode()),
                   "files": [{"path": path, "sha256": run.sha(source.encode()), "start_line": 1, "end_line": 2}]}
    repository = {"path": "/canonical", "commit": "frozen"}
    assert run.verify_delivery(preparation, prompt, repository)["selected_paths"] == [path]
    preparation["prompt"] = preparation["prompt"].replace('{"notice":', '{"memglide_sources":[],"notice":', 1)
    with pytest.raises(ValueError):
        run.verify_delivery(preparation, prompt, repository)


def test_canonical_and_worktree_bytes_ignore_upstream_attributes_and_global_filters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    source = b"VALUE = 1\r\n# retained CRLF\r\n"
    (root / "source.py").write_bytes(source)
    (root / ".gitattributes").write_text("*.py text eol=lf filter=marker working-tree-encoding=UTF-16\n")
    global_config = tmp_path / "global-config"
    marker = tmp_path / "external-filter-executed"
    global_config.write_text('[core]\n autocrlf = true\n[filter "marker"]\n clean = "touch ' + str(marker) + '"\n required = true\n')
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(global_config))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.autocrlf")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
    expected = run.tree_hashes(root)
    run.initialize_repository(root)
    commit = run.git(root, "rev-parse", "HEAD")
    run.verify_repository(root, commit, expected)
    assert run.canonical_hashes(root, commit) == expected
    assert not marker.exists()
    worktree = tmp_path / "worktree"
    run.git(root, "worktree", "add", "--detach", str(worktree), commit)
    assert (worktree / "source.py").read_bytes() == source
    assert not marker.exists()
    changed = dict(expected)
    changed["source.py"] = run.sha(source.replace(b"\r\n", b"\n"))
    with pytest.raises(ValueError, match="blobs differ"):
        run.verify_repository(root, commit, changed)
    (root / ".git/info/attributes").write_text("* text\n")
    with pytest.raises(ValueError, match="attributes changed"):
        run.verify_repository(root, commit, expected)


def test_repository_mapping_cannot_swap_neutral_upstream_ids(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plan = fake_plan()
    plan.update({"policy_freeze": {}, "inputs": {}, "provenance": {}, "fixtures": str(tmp_path),
                 "fixture_hashes": {}, "settings": run.SETTINGS, "plan_directory": str(tmp_path)})
    monkeypatch.setattr(run, "verify_freeze", lambda value: None)
    monkeypatch.setattr(run, "validate_tasks", lambda *args: None)
    monkeypatch.setattr(run, "validate_provenance", lambda *args: None)
    monkeypatch.setattr(run, "tree_hashes", lambda value: {})
    # Retain the input identities so reaching repository mapping is meaningful.
    values = {"tasks": "positive_tasks", "controls": "controls", "grading": "grading", "provenance": "provenance"}
    for name, field in values.items():
        path = tmp_path / (name + ".json")
        run.dump(path, plan[field])
        plan["inputs"][name] = {"path": str(path), "sha256": run.sha(path.read_bytes())}
    with pytest.raises(ValueError, match="neutral repository mapping"):
        run.verify_plan(plan)


@pytest.mark.parametrize("failure", ["exit", "timeout", "malformed", "interrupt", "cleanup"])
def test_original_failure_logs_and_process_cleanup_are_retained(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    class Process:
        returncode = 1 if failure == "exit" else 0
        def wait(self, timeout: int) -> int:
            if failure == "timeout":
                raise subprocess.TimeoutExpired("controlled-worker", timeout)
            if failure == "interrupt":
                raise KeyboardInterrupt
            return self.returncode
    def failed(command: list[str], **kwargs: Any) -> Any:
        assert command[:4] == [run.sys.executable, "-m", "benchmarks.run_automatic_v4", "worker"]
        kwargs["stdout"].write(b"original partial" if failure == "malformed" else b'{"source_mutations":""}')
        kwargs["stderr"].write(b"original failure")
        return Process()
    stopped = []
    def stop(process: Any) -> None:
        stopped.append(process)
        if failure == "cleanup":
            raise OSError("cleanup uncertainty")
    monkeypatch.setattr(run.subprocess, "Popen", failed)
    monkeypatch.setattr(run, "stop_process_group", stop)
    result = run.run_child(tmp_path / "request.json", tmp_path)
    assert result["worker_completed"] is False and len(stopped) == 1
    assert result["process_wall_seconds"] >= 0
    assert (tmp_path / "stderr.log").read_text() == "original failure"
    assert (tmp_path / "stdout.log").stat().st_size
    assert bool(result.get("halt_after_failure")) == (failure == "cleanup")


def test_summary_uses_all_planned_denominators_and_repository_cluster_uncertainty() -> None:
    plan = fake_plan()
    rows = fake_rows(plan)
    result = run.summarize(rows, plan)
    assert result["integrity_complete"] and not result["default_promotion"]
    assert result["arms"]["C"]["positive"]["scope_or_control_passes"] == 24
    assert result["arms"]["C"]["abstention_control"]["scope_or_control_passes"] == 8
    effect = result["paired_effects"]["C_minus_V3:positive:preparation_wall_seconds"]
    assert effect["repository_clusters"] == 6 and effect["pairs"] == 24
    assert effect["mean_delta"] == effect["median_delta"] == -0.5
    assert effect["mean_bootstrap95"] == effect["median_bootstrap95"] == [-0.5, -0.5]
    assert len(effect["per_task_effects"]) == 12 and not effect["missing_or_invalid_task_pairs"]
    assert result["strata_counts"]["language"]["python"]["C"]["planned"] == 16
    assert sum(result["actual_order_counts"]["1"]["C"].values()) == 16
    assert result["actual_pair_precedence"]["positive"]["1"]["B_vs_C"] == {"B_first": 6, "C_first": 6, "missing": 0}
    failed = next(row for row in rows if row["arm"] == "C" and row["kind"] == "positive")
    failed.update({"fidelity": {"valid": False}, "error": "metric evaluation failed", "process_wall_seconds": 7.0})
    failed.pop("metrics")
    rows.pop(next(index for index, row in enumerate(rows) if row["arm"] == "V3"))
    result = run.summarize(rows, plan)
    assert not result["integrity_complete"] and result["unrun_assignments"] == 1
    assert result["arms"]["C"]["positive"]["scope_or_control_passes"] == 23
    assert result["arms"]["C"]["evaluator_errors"] == 1
    assert result["arms"]["C"]["positive"]["metrics"]["process_wall_seconds"]["observed"] == 24
    assert result["arms"]["V3"]["observed"] == 31 and result["arms"]["V3"]["planned"] == 32
    assert len(result["paired_effects"]["C_minus_B:positive:preparation_wall_seconds"]["missing_or_invalid_task_pairs"]) == 1


@pytest.mark.parametrize("interrupt", [False, True])
def test_partial_report_preserves_raw_observation_initial_plan_and_missing_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, interrupt: bool) -> None:
    plan = fake_plan()
    if not interrupt:
        plan["assignments"] = plan["assignments"][:1]
    path = tmp_path / "plan.json"
    run.dump(path, plan)
    original_plan = path.read_bytes()
    original = {"preparation": {"prompt": "invalid source"}, "source_mutations": ""}
    monkeypatch.setattr(run, "verify_plan", lambda value: None)
    monkeypatch.setattr(run, "git", lambda *args: "")
    def completed(*args: Any) -> dict[str, Any]:
        path.write_text('{"changed":true}\n')
        return {"worker_completed": not interrupt, "interrupted": interrupt, "process_wall_seconds": 3.0,
                "observation": copy.deepcopy(original)}
    monkeypatch.setattr(run, "run_child", completed)
    monkeypatch.setattr(run, "verify_delivery", lambda *args: (_ for _ in ()).throw(ValueError("bad fidelity")))
    report = run.evaluate(path, tmp_path / "report")
    assert len(report["rows"]) == 1 and report["rows"][0]["observation"] == original
    assert report["summary"]["unrun_assignments"] == 95
    assert not report["summary"]["integrity_complete"] and not report["seal_unchanged"]
    assert "plan file changed" in report["seal_error"]
    assert report["plan_sha256"] == run.sha(original_plan)
    assert (tmp_path / "report" / "plan-input.json").read_bytes() == original_plan
    assert report["interrupted"] == interrupt
    assert report["actual_billed_charges"] is None and report["coding_task_success"] is None
    assert report["dispatched_model_requests"] == 0
    arm, kind = report["rows"][0]["arm"], report["rows"][0]["kind"]
    assert report["summary"]["arms"][arm][kind]["metrics"]["process_wall_seconds"]["mean"] == 3.0


def test_metric_error_never_preserves_a_success_numerator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plan = fake_plan()
    assignment = next(row for row in plan["assignments"] if row["kind"] == "positive" and row["arm"] == "C")
    plan["assignments"] = [assignment]
    path = tmp_path / "plan.json"
    run.dump(path, plan)
    monkeypatch.setattr(run, "verify_plan", lambda value: None)
    monkeypatch.setattr(run, "git", lambda *args: "")
    monkeypatch.setattr(run, "run_child", lambda *args: {"worker_completed": True, "observation": {"preparation": {}}})
    monkeypatch.setattr(run, "verify_delivery", lambda *args: {"valid": True, "selected_paths": plan["grading"][assignment["task_id"]]["required_paths"]})
    report = run.evaluate(path, tmp_path / "report")
    assert report["rows"][0]["scope_grade"]["declared_scope_complete"] is True
    assert report["rows"][0]["fidelity"]["valid"] is False
    assert report["summary"]["arms"]["C"]["positive"]["scope_or_control_passes"] == 0
