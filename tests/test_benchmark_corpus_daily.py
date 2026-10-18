"""Fresh daily corpus scope, behavioral separation and negative controls."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import corpus_daily as corpus  # noqa: E402


def test_manifest_is_balanced_fresh_and_scope_is_identically_disclosed():
    root = Path(__file__).parents[1]
    manifest = json.loads((root / "benchmarks/tasks_daily.json").read_text())
    tasks = corpus.task_definitions()
    assert manifest == {"corpus_version": corpus.CORPUS_VERSION, "tasks": tasks}
    assert len(tasks) == len({task["id"] for task in tasks}) == 20
    assert Counter(task["language"] for task in tasks) == {"python": 10, "typescript": 10}
    assert Counter(task["task_kind"] for task in tasks) == {
        "single-source": 8,
        "integration": 8,
        "supplied-context": 4,
    }
    old_ids = set()
    for relative in ("benchmarks/tasks.json", "benchmarks/tasks_v2.json"):
        old_ids.update(task["id"] for task in json.loads((root / relative).read_text())["tasks"])
    assert not old_ids & {task["id"] for task in tasks}
    assert Counter(task["repository"] for task in tasks) == dict.fromkeys(corpus.REPOSITORIES, 5)
    for task in tasks:
        files = corpus._repository_files(task["repository"])
        assert task["focus_paths"] == task["target_files"]
        assert all(f"- `{path}`" in task["prompt"] for path in task["focus_paths"])
        assert len(task["focus_paths"]) == (2 if task["task_kind"] == "integration" else 1)
        assert sum(len(files[path].encode()) for path in task["focus_paths"]) < 12000
        assert "Memglide" not in task["prompt"]
        if task["context_supplied"]:
            assert files[task["focus_paths"][0]] in task["prompt"]
            assert task["task_kind"] == "supplied-context"


def _fingerprints(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_generation_is_deterministic_and_oracles_are_not_in_worktree(tmp_path, repository):
    first, second = tmp_path / "first", tmp_path / "second"
    corpus.build_repository(repository, first)
    corpus.build_repository(repository, second)
    assert _fingerprints(first) == _fingerprints(second)
    assert not any("held_out" in path or "reference" in path for path in _fingerprints(first))
    for task in corpus.task_definitions():
        if task["repository"] == repository:
            assert all((first / relative).is_file() for relative in task["focus_paths"])
    with pytest.raises(ValueError, match="empty"):
        corpus.build_repository(repository, first)


@pytest.mark.parametrize("task", corpus.task_definitions(), ids=lambda task: task["id"])
def test_baseline_fails_behavior_reference_passes_all_checks(tmp_path, task):
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    baseline = corpus.grade(task["id"], root, tmp_path / "baseline")
    assert not baseline["success"]
    assert baseline["commands"][0]["exit_code"] != 0
    assert baseline["commands"][0]["counts"].get("tests") == 2
    assert baseline["protected_files_unchanged"]
    assert all(command["exit_code"] == 0 for command in baseline["commands"][1:]), baseline
    corpus._apply_reference_fix(task["id"], root)
    reference = corpus.grade(task["id"], root, tmp_path / "reference")
    assert reference["success"], reference
    assert reference["test_count"] == 7


@pytest.mark.parametrize(
    "task",
    [task for task in corpus.task_definitions() if task["task_kind"] == "integration"],
    ids=lambda task: task["id"],
)
@pytest.mark.parametrize("side", ["domain", "adapter"])
def test_each_half_of_two_source_fix_is_independently_required(tmp_path, task, side):
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root, side=side)
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert not result["success"]
    assert result["commands"][0]["exit_code"] != 0
    assert result["commands"][0]["counts"].get("tests") == 2
    assert result["protected_files_unchanged"]
    assert all(command["exit_code"] == 0 for command in result["commands"][1:]), result


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_erasing_protected_smoke_fails_even_with_correct_source(tmp_path, repository):
    task = next(task for task in corpus.task_definitions() if task["repository"] == repository)
    root = tmp_path / "repo"
    corpus.build_repository(repository, root)
    corpus._apply_reference_fix(task["id"], root)
    relative = "tests/test_smoke.py" if task["language"] == "python" else "tests/smoke.test.mjs"
    (root / relative).write_text("# erased\n" if task["language"] == "python" else "// erased\n")
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["commands"][0]["exit_code"] == 0
    assert not result["protected_files_unchanged"]
    assert not result["success"]


def test_grading_material_must_stay_outside_and_unknown_inputs_are_rejected(tmp_path):
    task = corpus.task_definitions()[0]
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    with pytest.raises(ValueError, match="outside"):
        corpus.grade(task["id"], root, root / "oracle")
    with pytest.raises(ValueError, match="unknown task"):
        corpus.grade("missing", root, tmp_path / "grade")
    with pytest.raises(ValueError, match="unsupported repository"):
        corpus.build_repository("missing", tmp_path / "invalid")
    with pytest.raises(ValueError, match="reference side"):
        corpus._apply_reference_fix(task["id"], root, side="missing")


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_production_early_exit_zero_cannot_bypass_test_execution(tmp_path, language):
    task = next(task for task in corpus.task_definitions() if task["language"] == language)
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    source = root / task["focus_paths"][0]
    early_exit = (
        "import os\nos._exit(0)\n"
        if language == "python"
        else 'Function("return process")().exit(0);\n'
    )
    source.write_text(early_exit + source.read_text())
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert all(command["exit_code"] == 0 for command in result["commands"])
    assert result["protected_files_unchanged"]
    assert not result["test_execution_complete"]
    assert not result["success"]
    assert all(not check["count_requirement_met"] for check in result["test_execution_integrity"])


@pytest.mark.parametrize("decorator", ["skip", "expectedFailure"])
def test_python_added_skipped_or_expected_failure_is_not_a_clean_pass(tmp_path, decorator):
    task = next(task for task in corpus.task_definitions() if task["language"] == "python")
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root)
    annotation = (
        '@unittest.skip("must not count as passing")'
        if decorator == "skip"
        else "@unittest.expectedFailure"
    )
    (root / "tests/test_extra.py").write_text(
        "import unittest\n\nclass ExtraTests(unittest.TestCase):\n"
        f"    {annotation}\n"
        "    def test_not_successful(self):\n        self.fail('not executed successfully')\n"
    )
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert all(command["exit_code"] == 0 for command in result["commands"])
    assert result["protected_files_unchanged"]
    assert result["test_execution_integrity"][0]["valid"]
    assert result["test_execution_integrity"][1]["count_requirement_met"]
    assert not result["test_execution_integrity"][1]["clean_summary_verified"]
    assert not result["success"]


def test_python_added_passing_regression_can_increase_smoke_count(tmp_path):
    task = next(task for task in corpus.task_definitions() if task["language"] == "python")
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root)
    (root / "tests/test_extra.py").write_text(
        "import unittest\nfrom desk.elapsed_clock import format_elapsed\n\n"
        "class ExtraTests(unittest.TestCase):\n"
        "    def test_extra(self):\n        self.assertEqual(format_elapsed(86400), '24:00:00')\n"
    )
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["success"]
    assert result["test_execution_complete"]
    assert result["commands"][1]["counts"]["tests"] == 6
    assert result["test_count"] == 8


@pytest.mark.parametrize("disposition", ["skip", "todo"])
def test_typescript_extra_skipped_or_todo_tests_are_not_a_clean_pass(tmp_path, disposition):
    task = next(task for task in corpus.task_definitions() if task["language"] == "typescript")
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root)
    source = root / task["focus_paths"][0]
    register_test = (
        "const {test} = await Function('return import(\"node:test\")')();\n"
        f'test("not successfully executed", {{{disposition}:true}}, () => {{}});\n'
    )
    source.write_text(register_test + source.read_text())
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert all(command["exit_code"] == 0 for command in result["commands"])
    assert result["protected_files_unchanged"]
    assert not result["test_execution_complete"]
    assert result["test_execution_integrity"][1]["count_requirement_met"]
    assert not result["test_execution_integrity"][1]["clean_summary_verified"]
    assert not result["success"]
