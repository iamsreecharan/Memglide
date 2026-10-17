"""Fresh-corpus generation, behavioral separation and reference validation."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import corpus_v2 as corpus  # noqa: E402


def test_manifest_has_forty_new_tasks_and_four_repositories():
    path = Path(__file__).parents[1] / "benchmarks/tasks_v2.json"
    manifest = json.loads(path.read_text())
    tasks = corpus.task_definitions()
    assert manifest == {"corpus_version": corpus.CORPUS_VERSION, "tasks": tasks}
    assert len(tasks) == len({task["id"] for task in tasks}) == 40
    assert sum(task["language"] == "python" for task in tasks) == 20
    assert sum(task["language"] == "typescript" for task in tasks) == 20
    old_ids = {task["id"] for task in json.loads(path.with_name("tasks.json").read_text())["tasks"]}
    assert not old_ids & {task["id"] for task in tasks}
    for repository in corpus.REPOSITORIES:
        assert sum(task["repository"] == repository for task in tasks) == 10
    assert all(len(task["target_files"]) == len(task["expected_symbols"]) == 2 for task in tasks)
    assert all("Memglide" not in task["prompt"] for task in tasks)


def _fingerprints(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_generation_is_deterministic_and_does_not_expose_oracles(tmp_path, repository):
    first, second = tmp_path / "first", tmp_path / "second"
    corpus.build_repository(repository, first)
    corpus.build_repository(repository, second)
    assert _fingerprints(first) == _fingerprints(second)
    assert not any("held_out" in path or "reference" in path for path in _fingerprints(first))
    for task in corpus.task_definitions():
        if task["repository"] == repository:
            assert all((first / path).is_file() for path in task["target_files"])
    with pytest.raises(ValueError, match="empty"):
        corpus.build_repository(repository, first)


@pytest.mark.parametrize("task", corpus.task_definitions(), ids=lambda task: task["id"])
def test_all_baselines_fail_external_behavior_and_reference_passes(tmp_path, task):
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    baseline = corpus.grade(task["id"], root, tmp_path / "baseline")
    assert not baseline["success"]
    assert baseline["protected_files_unchanged"]
    assert baseline["commands"][0]["exit_code"] != 0
    assert baseline["commands"][0]["counts"].get("tests") == 2
    assert all(command["exit_code"] == 0 for command in baseline["commands"][1:]), baseline
    corpus._apply_reference_fix(task["id"], root)
    reference = corpus.grade(task["id"], root, tmp_path / "reference")
    assert reference["success"], reference
    assert reference["test_count"] == 12


@pytest.mark.parametrize("repository", corpus.REPOSITORIES)
def test_protected_smoke_tampering_fails_even_with_correct_code(tmp_path, repository):
    task = next(task for task in corpus.task_definitions() if task["repository"] == repository)
    root = tmp_path / "repo"
    corpus.build_repository(repository, root)
    corpus._apply_reference_fix(task["id"], root)
    smoke = root / (
        "tests/test_smoke.py" if task["language"] == "python" else "tests/smoke.test.mjs"
    )
    smoke.write_text("# erased\n" if task["language"] == "python" else "// erased\n")
    result = corpus.grade(task["id"], root, tmp_path / "grade")
    assert result["commands"][0]["exit_code"] == 0
    assert not result["protected_files_unchanged"]
    assert not result["success"]


def test_grading_material_must_be_outside_worktree(tmp_path):
    task = corpus.task_definitions()[0]
    root = tmp_path / "repo"
    corpus.build_repository(task["repository"], root)
    with pytest.raises(ValueError, match="outside"):
        corpus.grade(task["id"], root, root / "oracle")
    with pytest.raises(ValueError, match="unknown task"):
        corpus.grade("missing", root, tmp_path / "grade")
    with pytest.raises(ValueError, match="unsupported repository"):
        corpus.build_repository("missing", tmp_path / "invalid")


@pytest.mark.parametrize(
    "spec",
    [spec for spec in corpus.SPECS if spec["slug"] in corpus.FACADE_BASELINES],
    ids=lambda spec: spec["slug"],
)
@pytest.mark.parametrize("side", ["domain", "adapter"])
def test_each_half_of_coordinated_fix_is_independently_required(tmp_path, spec, side):
    root = tmp_path / "repo"
    corpus.build_repository(spec["repository"], root)
    language, family = corpus.REPOSITORIES[spec["repository"]]
    directory, suffix = (family, "py") if language == "python" else ("src", "ts")
    if side == "domain":
        (root / directory / f"{spec['slug'].replace('-', '_')}.{suffix}").write_text(
            spec["reference"]
        )
    else:
        api = root / directory / f"api.{suffix}"
        api.write_text(
            api.read_text().replace(corpus._facade(spec), corpus._facade(spec, reference=True))
        )
    result = corpus.grade(corpus._task_id(spec), root, tmp_path / "grade")
    assert not result["success"]
    assert result["protected_files_unchanged"]
    assert all(command["exit_code"] == 0 for command in result["commands"][1:])
