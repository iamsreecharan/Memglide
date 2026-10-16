"""Ensure benchmark tasks are executable, independent, and honestly scored."""

import importlib.util
import json
from pathlib import Path

import pytest

_CORPUS_PATH = Path(__file__).parents[1] / "benchmarks/corpus.py"
_SPEC = importlib.util.spec_from_file_location("benchmark_corpus", _CORPUS_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_CORPUS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CORPUS)
build_repository = _CORPUS.build_repository
grade = _CORPUS.grade
task_definitions = _CORPUS.task_definitions
_apply_reference_fix = _CORPUS._apply_reference_fix


def test_manifest_matches_generator():
    manifest = json.loads((Path(__file__).parents[1] / "benchmarks/tasks.json").read_text())
    tasks = task_definitions()
    assert manifest["tasks"] == tasks
    assert len(tasks) == 24
    assert len({task["id"] for task in tasks}) == 24
    assert sum(task["language"] == "python" for task in tasks) == 12
    assert sum(task["language"] == "typescript" for task in tasks) == 12
    assert all(task["expected_symbols"] and task["target_files"] for task in tasks)
    assert all("Memglide" not in task["prompt"] for task in tasks)


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_repository_generation_is_deterministic(tmp_path, language):
    first, second = tmp_path / "first", tmp_path / "second"
    build_repository(language, first)
    build_repository(language, second)
    first_files = {
        str(path.relative_to(first)): path.read_bytes()
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        str(path.relative_to(second)): path.read_bytes()
        for path in second.rglob("*")
        if path.is_file()
    }
    assert first_files == second_files
    with pytest.raises(ValueError, match="empty"):
        build_repository(language, first)


@pytest.mark.parametrize("task", task_definitions(), ids=lambda task: task["id"])
def test_baseline_fails_behavior_and_reference_fix_passes(tmp_path, task):
    root = tmp_path / "repo"
    build_repository(task["language"], root)
    baseline = grade(task["id"], root, tmp_path / "baseline_grade")
    assert not baseline["passed"]
    assert baseline["protected_files_unchanged"]
    assert baseline["commands"][0]["exit_code"] != 0
    assert baseline["commands"][0]["counts"]["tests"] == 2
    assert all(command["exit_code"] == 0 for command in baseline["commands"][1:])
    _apply_reference_fix(task["id"], root)
    reference = grade(task["id"], root, tmp_path / "fixed_grade")
    assert reference["passed"], json.dumps(reference, indent=2)
    assert reference["test_count"] == 4


def test_modified_smoke_test_cannot_receive_credit(tmp_path):
    root = tmp_path / "repo"
    build_repository("python", root)
    _apply_reference_fix("py-ttl-boundary", root)
    (root / "tests/test_smoke.py").write_text("# erased\n")
    result = grade("py-ttl-boundary", root, tmp_path / "grade")
    assert not result["passed"]
    assert not result["protected_files_unchanged"]
    assert result["commands"][0]["exit_code"] == 0


def test_oracle_must_be_outside_agent_worktree(tmp_path):
    root = tmp_path / "repo"
    build_repository("python", root)
    with pytest.raises(ValueError, match="outside"):
        grade("py-ttl-boundary", root, root / "oracle")


def test_unknown_language_and_task_fail_explicitly(tmp_path):
    with pytest.raises(ValueError, match="unsupported language"):
        build_repository("ruby", tmp_path / "repo")
    with pytest.raises(ValueError, match="unknown task"):
        grade("missing", tmp_path / "repo", tmp_path / "grade")
