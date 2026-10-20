"""Source-role regressions exercise the full bounded v4 preparation path."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.storage.database import Database

TASK = "Cooling window must account for flow rate and capacity."
PRODUCTION = "def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n"


@pytest.fixture
def repository(tmp_path: Path) -> tuple[Path, Database, str]:
    root = tmp_path / "repository"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "cooling.py").write_text(PRODUCTION)
    database = Database(tmp_path / "state.db")
    project = Indexer(database).add_project(str(root))["id"]
    return root, database, project


def prepare(repository: tuple[Path, Database, str]) -> dict:
    _, database, project = repository
    return prepare_task_prompt(
        TASK,
        enabled=True,
        selection_policy="v4",
        project_id=project,
        db_path=database.path,
    )


def add(repository: tuple[Path, Database, str], path: str, source: str) -> None:
    target = repository[0] / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source)


def assert_selected_production(result: dict) -> None:
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["cooling.py"]
    assert result["files"][0]["path"] == "cooling.py"
    assert PRODUCTION in result["prompt"].replace("\\n", "\n")


@pytest.mark.parametrize("filename", ["test.py", "tests.py", "TESTS.py"])
def test_canonical_test_module_does_not_compete_with_production(repository, filename):
    # Identical clean function evidence would otherwise create an ambiguous tie.
    add(repository, filename, PRODUCTION)
    assert_selected_production(prepare(repository))


@pytest.mark.parametrize("directory", ["demo", "demos"])
def test_known_demo_syntax_error_is_not_a_production_index_failure(repository, directory):
    add(repository, directory + "/legacy.py", "print 'old demonstration'\n")
    result = prepare(repository)
    assert_selected_production(result)
    diagnostic = result["automatic_selection"]["coarse_selection"]
    assert diagnostic["nonproduction_parse_errors_accepted"] == 1
    assert diagnostic["scope_complete"] is True


@pytest.mark.parametrize("directory", ["demo", "demos"])
def test_unsupported_demo_script_is_not_a_production_frontier(repository, directory):
    add(repository, directory + "/inspect.sh", "echo 'cooling window flow rate capacity'\n")
    result = prepare(repository)
    assert_selected_production(result)
    assert result["automatic_selection"]["coarse_selection"]["unsupported_production_files"] == 0


@pytest.mark.parametrize("path", ["src/demo.py", "src/contest.py", "src/testimony.py"])
def test_similarly_named_production_still_competes_and_abstains(repository, path):
    add(repository, path, PRODUCTION)
    result = prepare(repository)
    assert result["mode"] == "passthrough", result
    assert result["reason"] == "ambiguous_candidates"
    assert result["prompt"] == TASK
    assert result["files"] == []


@pytest.mark.parametrize("path", ["src/demo.sh", "src/tests_runner.sh"])
def test_real_unsupported_production_frontier_still_blocks(repository, path):
    add(repository, path, "echo 'cooling window flow rate capacity'\n")
    result = prepare(repository)
    assert result["mode"] == "passthrough", result
    assert result["reason"] == "unsupported_competitor"
    assert result["prompt"] == TASK
    assert result["automatic_selection"]["coarse_selection"]["potential_unsupported_files"] == 1


@pytest.mark.parametrize("directory", ["demo_tools", "demos_factory"])
def test_similar_directory_prefix_does_not_hide_production_parse_error(repository, directory):
    add(repository, directory + "/legacy.py", "print 'broken production'\n")
    result = prepare(repository)
    assert result["mode"] == "passthrough", result
    assert result["reason"] == "incomplete_index"
    assert result["prompt"] == TASK
