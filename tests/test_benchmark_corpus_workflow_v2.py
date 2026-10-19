"""Workflow corpus balance, behavioral independence and grader integrity."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import corpus_workflow_v2 as corpus  # noqa: E402


def test_manifest_is_fresh_balanced_and_common_scope_complete():
    root = Path(__file__).parents[1]
    tasks = corpus.task_definitions()
    assert json.loads((root / "benchmarks/tasks_workflow_v2.json").read_text()) == {
        "corpus_version": corpus.CORPUS_VERSION,
        "tasks": tasks,
    }
    assert len(tasks) == len({task["id"] for task in tasks}) == 10
    assert Counter(task["language"] for task in tasks) == {"python": 5, "typescript": 5}
    assert Counter(task["task_kind"] for task in tasks) == {
        "single-source": 4,
        "integration": 4,
        "supplied-context": 2,
    }
    assert len(corpus.REPOSITORIES) == 4
    previous = set()
    for file in [
        "tasks.json",
        "tasks_v2.json",
        "tasks_daily.json",
        "tasks_cache.json",
        "tasks_cost.json",
        "tasks_workflow.json",
    ]:
        previous.update(
            task["id"] for task in json.loads((root / "benchmarks" / file).read_text())["tasks"]
        )
    assert not previous & {task["id"] for task in tasks}
    for task in tasks:
        assert task["target_files"] == task["focus_paths"]
        assert len(task["support_paths"]) == 1
        assert len(task["focus_paths"]) == (2 if task["task_kind"] == "integration" else 1)
        files = corpus._repository_files(task["repository"])
        assert not set(task["focus_paths"]) & set(task["support_paths"])
        for path in task["focus_paths"] + task["support_paths"]:
            assert f"- `{path}`" in task["prompt"]
            assert path in files
            if task["context_supplied"]:
                assert files[path] in task["prompt"]
        assert json.dumps(task["test_argv"]) in task["prompt"]
        assert "Memglide" not in task["prompt"]
        assert (
            sum(len(files[path].encode()) for path in task["focus_paths"] + task["support_paths"])
            < 11_000
        )
        assert len(task["prompt"].encode()) < 12_000


def _fingerprints(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_generation_deterministic_no_oracles_in_worktree(tmp_path, repository):
    first, second = tmp_path / "first", tmp_path / "second"
    corpus.build_repository(repository, first)
    corpus.build_repository(repository, second)
    assert _fingerprints(first) == _fingerprints(second)
    assert not any("held_out" in path or "reference" in path for path in _fingerprints(first))
    with pytest.raises(ValueError, match="empty"):
        corpus.build_repository(repository, first)


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_declared_public_test_argv_runs_in_clean_starting_repository(tmp_path, repository):
    root = tmp_path / "repo"
    corpus.build_repository(repository, root)
    task = next(row for row in corpus.tasks() if row["repository"] == repository)
    environment = dict(__import__("os").environ)
    environment.update(PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1")
    result = corpus._command(task["test_argv"], root, tmp_path / "declared", environment)
    assert result["exit_code"] == 0, result
    total = result["counts"].get("tests")
    if total is None and task["language"] == "typescript":
        # Node 24's public default reporter is spec; the independent grader
        # explicitly requests TAP. Both execute the same complete suite.
        output = Path(result["stdout_path"]).read_text()
        match = __import__("re").search(r"^ℹ tests (\d+)$", output, __import__("re").MULTILINE)
        assert match is not None, output
        total = int(match.group(1))
    assert total == 5 * sum(row["repository"] == repository for row in corpus.SPECS)
    assert not (root / "build").exists()
    assert not (root / "dist").exists()


@pytest.mark.parametrize("task", corpus.task_definitions(), ids=lambda task: task["id"])
def test_baseline_rejected_reference_passes_all_checks(tmp_path, task):
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    baseline = corpus.grade(task["id"], root, tmp_path / "baseline")
    assert not baseline["success"]
    assert baseline["commands"][0]["exit_code"] != 0
    assert baseline["commands"][0]["counts"].get("tests") == 2
    assert baseline["protected_files_unchanged"]
    assert all(c["exit_code"] == 0 for c in baseline["commands"][1:]), baseline
    corpus._apply_reference_fix(task["id"], root)
    reference = corpus.grade(task["id"], root, tmp_path / "reference")
    assert reference["success"], reference
    assert reference["test_count"] == 2 + 5 * sum(
        s["repository"] == task["repository"] for s in corpus.SPECS
    )


@pytest.mark.parametrize(
    "task",
    [t for t in corpus.task_definitions() if t["task_kind"] == "integration"],
    ids=lambda task: task["id"],
)
@pytest.mark.parametrize("side", ["domain", "adapter"])
def test_integration_each_half_independently_needed(tmp_path, task, side):
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root, side=side)
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert not result["success"]
    assert result["commands"][0]["exit_code"] != 0
    assert result["commands"][0]["counts"].get("tests") == 2
    assert result["protected_files_unchanged"]
    assert all(c["exit_code"] == 0 for c in result["commands"][1:]), result


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_erasing_support_file_rejected_despite_correct_source(tmp_path, repository):
    task = next(t for t in corpus.task_definitions() if t["repository"] == repository)
    root = tmp_path / "repo"
    corpus.build_repository(repository, root)
    corpus._apply_reference_fix(task["id"], root)
    (root / task["support_paths"][0]).write_text(
        "# erased\n" if task["language"] == "python" else "// erased\n"
    )
    grade = corpus.grade(task["id"], root, tmp_path / "grade")
    assert grade["commands"][0]["exit_code"] == 0
    assert not grade["protected_files_unchanged"]
    assert not grade["success"]


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_production_exit_zero_cannot_fake_test_completion(tmp_path, language):
    task = next(t for t in corpus.task_definitions() if t["language"] == language)
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
    assert all(c["exit_code"] == 0 for c in result["commands"])
    assert result["protected_files_unchanged"]
    assert not result["test_execution_complete"]
    assert not result["success"]
    assert all(not check["count_requirement_met"] for check in result["test_execution_integrity"])


@pytest.mark.parametrize("decorator", ["skip", "expectedFailure"])
def test_added_skip_or_expected_failure_is_not_clean_pass(tmp_path, decorator):
    task = next(t for t in corpus.task_definitions() if t["language"] == "python")
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root)
    decoration = '@unittest.skip("not run")' if decorator == "skip" else "@unittest.expectedFailure"
    (root / "tests/test_extra.py").write_text(
        "import unittest\nclass Extra(unittest.TestCase):\n    "
        + decoration
        + "\n    def test_extra(self):\n        self.fail()\n"
    )
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["commands"][0]["exit_code"] == 0
    assert not result["success"]
    assert not result["test_execution_complete"]


def test_oracle_separation_unknown_inputs_and_reference_sides(tmp_path):
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
def test_new_regression_file_allowed_without_touching_frozen_tests(tmp_path, language):
    task = next(t for t in corpus.tasks() if t["language"] == language)
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root)
    name = (
        "tests/test_new_regression.py" if language == "python" else "tests/new_regression.test.mjs"
    )
    content = (
        "import unittest\nclass AddedRegression(unittest.TestCase):\n    def test_new(self): self.assertEqual(2+2,4)\n"
        if language == "python"
        else 'import test from "node:test";import assert from "node:assert/strict";\ntest("new regression",()=>assert.equal(2+2,4));\n'
    )
    (root / name).write_text(content)
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["success"], result
    assert result["protected_files_unchanged"]
    ordinary = 5 * sum(spec["repository"] == task["repository"] for spec in corpus.SPECS)
    assert result["commands"][1]["counts"]["tests"] == ordinary + 1


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_existing_test_append_rejected_even_when_every_behavior_test_passes(tmp_path, language):
    task = next(t for t in corpus.tasks() if t["language"] == language)
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    corpus._apply_reference_fix(task["id"], root)
    original = root / task["support_paths"][0]
    before = original.read_bytes()
    original.write_bytes(
        before + (b"\n# Added comment\n" if language == "python" else b"\n// Added comment\n")
    )
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert all(command["exit_code"] == 0 for command in result["commands"]), result
    assert result["test_execution_complete"]
    assert not result["protected_files_unchanged"]
    assert not result["success"]


def test_every_instruction_layer_requires_new_file_only_regressions():
    for task in corpus.tasks():
        files = corpus._repository_files(task["repository"])
        for text in (task["prompt"], files["AGENTS.md"]):
            assert "READ-ONLY" in text
            assert "keep their bytes identical" in text
            assert "ONLY in NEW test files" in text
            assert "never append to, rewrite, rename, or delete existing tests" in text
