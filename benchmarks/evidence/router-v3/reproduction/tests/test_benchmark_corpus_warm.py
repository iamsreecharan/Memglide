"""Independent correctness, stage reset and grader integrity for warm sequences."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import corpus_warm as corpus  # noqa: E402


def test_manifest_fresh_balanced_and_complete():
    tasks = corpus.tasks()
    manifest = json.loads((Path(__file__).parents[1] / "benchmarks/tasks_warm.json").read_text())
    assert manifest == {"corpus_version": corpus.CORPUS_VERSION, "sequences": 12, "tasks": tasks}
    assert len(tasks) == len({t["id"] for t in tasks}) == 36
    assert Counter(t["language"] for t in tasks) == {"python": 18, "typescript": 18}
    assert len(corpus.sequences()) == len(corpus.REPOSITORIES) == 12
    assert len({s["family"] for s in corpus.sequences()}) == 12
    assert sum(t["source_change_control"] for t in tasks) == 1
    old_ids = set()
    for path in (Path(__file__).parents[1] / "benchmarks").glob("tasks*.json"):
        if path.name != "tasks_warm.json":
            historical = json.loads(path.read_text())
            # Both manifest schemas are supported; inspect every task rather
            # than omitting list-based corpora from the freshness check.
            historical_tasks = (
                historical if isinstance(historical, list) else historical.get("tasks", [])
            )
            old_ids.update(t["id"] for t in historical_tasks)
    assert not old_ids.intersection(t["id"] for t in tasks)
    for task in tasks:
        assert task["focus_paths"] == task["target_files"]
        assert (
            len(task["focus_paths"]) == len(task["support_paths"]) == len(task["memory_paths"]) == 1
        )
        files = corpus._repository_files(task["sequence_id"], task["stage"])
        assert all(
            path in files
            for path in task["focus_paths"] + task["support_paths"] + task["memory_paths"]
        )
        assert json.dumps(task["test_argv"]) in task["prompt"]
        assert "Memglide" not in task["prompt"]
        assert "READ-ONLY" in task["prompt"]
        assert "EXACT contiguous quote" in task["prompt"]
        assert not any("held_out" in path or "reference" in path for path in files)
        assert len(files) >= 30


def _hashes(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize("sequence", corpus.sequences(), ids=lambda s: s["id"])
def test_snapshots_deterministic_and_previous_tasks_reference_fixed(tmp_path, sequence):
    specs = [s for s in corpus.SPECS if s["sequence_id"] == sequence["id"]]
    for stage in (1, 2, 3):
        first, second = tmp_path / f"{stage}a", tmp_path / f"{stage}b"
        corpus.build_stage(sequence["id"], stage, first)
        corpus.build_stage(sequence["id"], stage, second)
        assert _hashes(first) == _hashes(second)
        for spec in specs:
            expected = spec["reference"] if spec["stage"] < stage else spec["baseline"]
            assert (first / corpus._source_path(spec)).read_text() == expected
        with pytest.raises(ValueError, match="empty"):
            corpus.build_stage(sequence["id"], stage, first)
    first_docs = corpus._repository_files(sequence["id"], 1)
    last_docs = corpus._repository_files(sequence["id"], 3)
    differences = {p for p in first_docs if p.startswith("docs/") and first_docs[p] != last_docs[p]}
    assert differences == (
        {"docs/decisions/labels-contract.md"} if sequence["id"] == "py-warm-labels" else set()
    )


@pytest.mark.parametrize("task", corpus.tasks(), ids=lambda t: t["id"])
def test_baseline_rejected_reference_passes_and_smokes_are_clean(tmp_path, task):
    root = tmp_path / "repo"
    corpus.build_stage(task["sequence_id"], task["stage"], root)
    baseline = corpus.grade(task["id"], root, tmp_path / "baseline")
    assert not baseline["success"]
    assert baseline["commands"][0]["exit_code"] != 0
    assert baseline["commands"][0]["counts"].get("tests") == 2
    assert baseline["protected_files_unchanged"]
    assert baseline["commands"][1]["counts"].get("tests") == 6
    assert all(row["exit_code"] == 0 for row in baseline["commands"][1:]), baseline
    corpus._apply_reference_fix(task["id"], root)
    reference = corpus.grade(task["id"], root, tmp_path / "reference")
    assert reference["success"], reference
    assert reference["test_count"] == 8


@pytest.mark.parametrize("language", ["python", "typescript"])
@pytest.mark.parametrize("tamper_kind", ["test", "doc", "other-production", "config"])
def test_correct_source_cannot_hide_protected_file_tampering(tmp_path, language, tamper_kind):
    task = next(t for t in corpus.tasks() if t["language"] == language)
    root = tmp_path / "repo"
    corpus.build_stage(task["sequence_id"], task["stage"], root)
    corpus._apply_reference_fix(task["id"], root)
    if tamper_kind == "test":
        target = task["support_paths"][0]
    elif tamper_kind == "doc":
        target = task["memory_paths"][0]
    elif tamper_kind == "config":
        target = "README.md"
    else:
        target = next(
            t["focus_paths"][0]
            for t in corpus.tasks()
            if t["sequence_id"] == task["sequence_id"] and t["stage"] == 2
        )
    content = (root / target).read_text()
    comment = (
        "\n# altered\n"
        if target.endswith(".py")
        else "\n// altered\n"
        if target.endswith((".ts", ".mjs"))
        else "\nAltered.\n"
    )
    (root / target).write_text(content + comment)
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["commands"][0]["exit_code"] == 0
    assert not result["protected_files_unchanged"]
    assert not result["success"]


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_exit_zero_without_tests_rejected(tmp_path, language):
    task = next(t for t in corpus.tasks() if t["language"] == language)
    root = tmp_path / "repo"
    corpus.build_stage(task["sequence_id"], task["stage"], root)
    source = root / task["focus_paths"][0]
    early = (
        "import os\nos._exit(0)\n"
        if language == "python"
        else 'Function("return process")().exit(0);\n'
    )
    source.write_text(early + source.read_text())
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert all(row["exit_code"] == 0 for row in result["commands"])
    assert result["protected_files_unchanged"]
    assert not result["test_execution_complete"]
    assert not result["success"]


@pytest.mark.parametrize("language", ["python", "typescript"])
def test_added_regression_file_allowed(tmp_path, language):
    task = next(t for t in corpus.tasks() if t["language"] == language)
    root = tmp_path / "repo"
    corpus.build_stage(task["sequence_id"], task["stage"], root)
    corpus._apply_reference_fix(task["id"], root)
    name = (
        "tests/test_new_regression.py" if language == "python" else "tests/new_regression.test.mjs"
    )
    text = (
        "import unittest\nclass New(unittest.TestCase):\n    def test_new(self): self.assertEqual(4,2+2)\n"
        if language == "python"
        else 'import test from "node:test";import assert from "node:assert/strict";test("new regression",()=>assert.equal(4,2+2));\n'
    )
    (root / name).write_text(text)
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["success"], result
    assert result["test_count"] == 9


def test_source_change_control_updates_actual_policy_and_rejects_old_quote():
    task = next(t for t in corpus.tasks() if t["source_change_control"])
    path = task["memory_paths"][0]
    before = corpus._repository_files(task["sequence_id"], 2)[path]
    after = corpus._repository_files(task["sequence_id"], 3)[path]
    assert "retain the FIRST row" in before
    assert "retain the LAST row" in after
    assert hashlib.sha256(before.encode()).hexdigest() != hashlib.sha256(after.encode()).hexdigest()
    assert "retain the FIRST row" not in after


def test_invalid_ids_stages_and_grading_inside_worktree_rejected(tmp_path):
    with pytest.raises(ValueError, match="unsupported sequence"):
        corpus.build_stage("missing", 1, tmp_path / "bad")
    with pytest.raises(ValueError, match="stage"):
        corpus.build_stage(corpus.sequences()[0]["id"], 4, tmp_path / "bad-stage")
    task = corpus.tasks()[0]
    corpus.build_stage(task["sequence_id"], 1, tmp_path / "repo")
    with pytest.raises(ValueError, match="outside"):
        corpus.grade(task["id"], tmp_path / "repo", tmp_path / "repo/oracle")
    with pytest.raises(ValueError, match="unknown task"):
        corpus.grade("missing", tmp_path / "repo", tmp_path / "out")


@pytest.mark.parametrize(
    ("task_id", "old", "new"),
    [
        (
            "py-warm-intervals-s3",
            "if start == end:",
            "if False:",
        ),
        (
            "py-warm-redaction-s2",
            "return {key:redact_field(key,value) for key,value in record.items()}",
            "record.update({key:redact_field(key,value) for key,value in record.items()}); return record",
        ),
        (
            "ts-warm-paths-s1",
            'if(parts.includes("..")) throw new Error("parent segment");',
            "",
        ),
        (
            "ts-warm-versions-s3",
            "compare_versions(value,best)>0",
            "compare_versions(value,best)>=0",
        ),
    ],
)
def test_partial_fixes_do_not_pass_external_behavior(tmp_path, task_id, old, new):
    task = next(t for t in corpus.tasks() if t["id"] == task_id)
    root = tmp_path / "repo"
    corpus.build_stage(task["sequence_id"], task["stage"], root)
    corpus._apply_reference_fix(task_id, root)
    path = root / task["focus_paths"][0]
    source = path.read_text()
    assert source.count(old) == 1
    path.write_text(source.replace(old, new))
    result = corpus.grade(task_id, root, tmp_path / "grade")
    assert result["protected_files_unchanged"]
    assert all(command["exit_code"] == 0 for command in result["commands"][1:])
    assert result["commands"][0]["exit_code"] != 0
    assert not result["success"]


@pytest.mark.parametrize("language", ["python", "typescript"])
@pytest.mark.parametrize("kind", ["module", "configuration", "test-symlink"])
def test_unapproved_new_files_rejected_even_with_correct_source(tmp_path, language, kind):
    task = next(t for t in corpus.tasks() if t["language"] == language)
    root = tmp_path / "repo"
    corpus.build_stage(task["sequence_id"], task["stage"], root)
    corpus._apply_reference_fix(task["id"], root)
    if kind == "module":
        name = "unapproved.py" if language == "python" else "src/unapproved.ts"
        (root / name).write_text("# unexpected\n" if language == "python" else "// unexpected\n")
    elif kind == "configuration":
        name = "new-config.json"
        (root / name).write_text("{}\n")
    else:
        name = "tests/test_symlink.py" if language == "python" else "tests/symlink.test.mjs"
        (root / name).symlink_to(root / task["support_paths"][0])
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert all(row["exit_code"] == 0 for row in result["commands"])
    assert result["protected_files_unchanged"]
    assert not result["new_files_valid"]
    assert name in result["unexpected_files"]
    assert not result["success"]
