from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import corpus_automatic as corpus  # noqa: E402


def test_heldout_tasks_are_path_free_and_real_upstream() -> None:
    tasks = corpus.load_tasks()
    assert len(tasks) == len({task["id"] for task in tasks}) == 12
    assert {task["language"] for task in tasks} == {"python", "typescript"}
    assert len({task["repository"] for task in tasks}) == 4
    for task in tasks:
        assert len(task["known_paths"]) == 1
        assert task["known_paths"] == task["focus_paths"]
        assert task["known_paths"][0] not in task["prompt"]
        assert "src/" not in task["prompt"]
        assert "reference" not in task["prompt"]


def test_manifest_is_reproducible() -> None:
    manifest = json.loads(corpus.MANIFEST.read_text())
    assert manifest["tasks"] == corpus.load_tasks()
    assert manifest["corpus_version"] == corpus.CORPUS_VERSION


def test_frozen_upstream_provenance_and_license_bytes() -> None:
    manifest = json.loads((corpus.FIXTURES / "provenance.json").read_text())
    assert len(manifest["repositories"]) == 4
    for repository in manifest["repositories"]:
        assert len(repository["commit"]) == 40
        assert repository["upstream_url"].startswith("https://github.com/")
        assert repository["file_count"] == len(repository["files"])
        assert any("LICENSE" in name for name in repository["files"])
        total = 0
        for name, receipt in repository["files"].items():
            path = corpus.FIXTURES / repository["repository"] / name
            assert path.is_file() and not path.is_symlink()
            data = path.read_bytes()
            assert len(data) == receipt["bytes"]
            assert hashlib.sha256(data).hexdigest() == receipt["sha256"]
            total += len(data)
        assert total == repository["bytes"]


@pytest.mark.parametrize("task", corpus.load_tasks(), ids=lambda task: task["id"])
def test_builder_contains_only_upstream_tree_and_one_defect(tmp_path: Path, task: dict) -> None:
    root = tmp_path / "repository"
    receipt = corpus.build_task_repo(task["id"], root)
    original = corpus.FIXTURES / task["repository"]
    original_names = {path.relative_to(original) for path in original.rglob("*") if path.is_file()}
    actual_names = {path.relative_to(root) for path in root.rglob("*") if path.is_file()}
    assert actual_names == original_names
    changed = [
        name
        for name in original_names
        if (root / name).read_bytes() != (original / name).read_bytes()
    ]
    assert [name.as_posix() for name in changed] == task["known_paths"]
    assert len(receipt["source_tree_sha256"]) == 64
    assert not any("held_out" in str(name) for name in actual_names)
    corpus.apply_reference_fix(root, task["id"])
    assert all(
        (root / name).read_bytes() == (original / name).read_bytes() for name in original_names
    )
    with pytest.raises(ValueError, match="empty"):
        corpus.build_task_repo(task["id"], root)


@pytest.mark.parametrize("task_id", ["itsdangerous-base64-padding", "mitt-handler-append-order"])
def test_baseline_fails_and_upstream_reference_passes(tmp_path: Path, task_id: str) -> None:
    root = tmp_path / "repository"
    corpus.build_task_repo(task_id, root)
    baseline = corpus.grade_task(root, task_id, artifact_dir=tmp_path / "baseline")
    assert not baseline["success"]
    assert baseline["test_count"] == 8
    corpus.apply_reference_fix(root, task_id)
    reference = corpus.grade_task(root, task_id, artifact_dir=tmp_path / "reference")
    assert reference["success"]
    assert reference["test_count"] == 8


def test_grader_rejects_tracked_test_tampering_without_execution(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    task_id = "itsdangerous-base64-padding"
    corpus.build_task_repo(task_id, root)
    corpus.apply_reference_fix(root, task_id)
    (root / "tests/test_itsdangerous/test_encoding.py").write_text(
        "raise RuntimeError('tampered')\n"
    )
    result = corpus.grade_task(root, task_id, artifact_dir=tmp_path / "grade")
    assert not result["success"]
    assert not result["protected_files_unchanged"]
    assert result["commands"] == []


def test_grader_rejects_symlink_escape_before_execution(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    task_id = "itsdangerous-base64-padding"
    corpus.build_task_repo(task_id, root)
    outside = tmp_path / "outside.py"
    outside.write_text("raise RuntimeError('never execute')\n")
    source = root / "src/itsdangerous/encoding.py"
    source.unlink()
    source.symlink_to(outside)
    result = corpus.grade_task(root, task_id, artifact_dir=tmp_path / "grade")
    assert not result["success"]
    assert "src/itsdangerous/encoding.py" in result["unexpected_files"]
    assert result["commands"] == []


def test_grader_requires_external_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    corpus.build_task_repo("itsdangerous-base64-padding", root)
    with pytest.raises(ValueError, match="outside"):
        corpus.grade_task(root, "itsdangerous-base64-padding", artifact_dir=root / "grading")


def test_grader_detects_exit_zero_before_test_execution(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    task_id = "itsdangerous-base64-padding"
    corpus.build_task_repo(task_id, root)
    (root / "src/itsdangerous/encoding.py").write_text("import os\nos._exit(0)\n")
    result = corpus.grade_task(root, task_id, artifact_dir=tmp_path / "grade")
    assert not result["success"]
    assert all(command["exit_code"] == 0 for command in result["commands"])
    assert not any(check["valid"] for check in result["test_execution_integrity"])


def test_unknown_task_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown"):
        corpus.build_task_repo("does-not-exist", tmp_path)


def test_frozen_paths_include_complete_snapshots_and_private_grader() -> None:
    paths = corpus.frozen_files()
    assert Path(corpus.__file__) in paths
    assert corpus.MANIFEST in paths
    assert len(corpus.fixture_paths()) > 170
    assert all(path.is_file() for path in paths)
