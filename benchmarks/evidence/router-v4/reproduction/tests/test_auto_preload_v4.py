"""Separate synthetic development mechanisms for bounded opt-in routing."""
from __future__ import annotations

import json
import subprocess

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.storage.database import Database


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "cooling.py").write_text(
        "def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n")
    db = Database(tmp_path / "state.db")
    project = Indexer(db).add_project(str(root))["id"]
    return root, db, project


def run(repository, *, policy="v4", task="Cooling window must account for flow rate and capacity.", **kwargs):
    _, db, project = repository
    return prepare_task_prompt(task, project_id=project, db_path=db.path, enabled=True,
                               selection_policy=policy, **kwargs)


def skip(result, reason):
    assert result["mode"] == "passthrough", result
    assert result["reason"] == reason, result
    assert not result["files"]


def test_nonproduction_known_syntax_error_allowed_but_v3_preserved(repository):
    root, _, _ = repository
    (root / "tests").mkdir()
    (root / "tests" / "broken.py").write_text("def unavailable(:\n")
    skip(run(repository, policy="v3"), "incomplete_index")
    result = run(repository)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["cooling.py"]
    diagnostic = result["automatic_selection"]["coarse_selection"]
    assert diagnostic["nonproduction_parse_errors_accepted"] == 1
    assert diagnostic["scope_complete"]


def test_production_parse_error_remains_fail_closed(repository):
    root, _, _ = repository
    (root / "broken.py").write_text("def unavailable(:\n")
    skip(run(repository), "incomplete_index")


@pytest.mark.parametrize("kind", ["scan", "partial", "truncated", "unreported", "unknownparse", "mismatched", "duplicate"])
def test_error_provenance_and_completeness_required(repository, monkeypatch, kind):
    root, db, project = repository
    original = Indexer.reindex

    def broken(self, project_id, full=False):
        result = original(self, project_id, full)
        if kind == "scan":
            result["errors"] = [{"path": "docs/file.md", "error": "Source could not be read"}]
        elif kind == "partial":
            result["partial"] = True
        elif kind == "truncated":
            result["errors"] = [{"path": "docs/file.md", "error": "Source could not be read"}] * 200
        else:
            message = "Tree-sitter found syntax errors; partial structural results require inspection"
            if kind == "unknownparse":
                message = "Unknown parser worker failure"
            with db.connect() as conn:
                conn.execute("UPDATE files SET parse_error=? WHERE project_id=? AND path='docs/broken.py'", (message, project))
            result["errors"] = [] if kind == "unreported" else [{"path": "docs/broken.py", "error": message}]
            if kind == "mismatched":
                result["errors"][0]["error"] = "Python parse error: different diagnostic"
            elif kind == "duplicate":
                result["errors"] *= 2
        return result

    (root / "docs").mkdir()
    (root / "docs" / "broken.py").write_text("def nothing(x):\n return x\n")
    monkeypatch.setattr(Indexer, "reindex", broken)
    skip(run(repository), "incomplete_index")


def test_nonproduction_filter_applied_before_candidate_cap(repository):
    root, _, _ = repository
    (root / "tests").mkdir()
    for index in range(105):
        (root / "tests" / f"case_{index:03}.py").write_text(
            "def cooling_window(flow_rate, capacity):\n return flow_rate / capacity\n")
    skip(run(repository, policy="v3"), "candidate_limit_reached")
    result = run(repository)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["cooling.py"]
    assert result["automatic_selection"]["coarse_selection"]["coarse_files_checked"] == 1


def test_lexically_impossible_files_reduce_ast_pool_without_topk_drop(repository):
    root, _, _ = repository
    for index in range(30):
        (root / f"unrelated_{index:02}.py").write_text(f"# cooling\ndef unrelated_{index}(x):\n return x\n")
    skip(run(repository, policy="v3"), "evidence_candidate_limit")
    result = run(repository)
    assert result["mode"] == "preloaded", result
    diagnostic = result["automatic_selection"]["coarse_selection"]
    assert diagnostic["coarse_files_checked"] == 31
    assert diagnostic["potential_supported_files"] == 1
    assert diagnostic["weak_supported_files"] == 30
    assert diagnostic["frontier_omitted"] + len(diagnostic["frontier"]) == 31
    assert result["automatic_selection"]["candidate_files_considered"] == 1


def test_possible_competitors_above_ast_cap_still_decline(repository):
    root, _, _ = repository
    for index in range(24):
        (root / f"possible_{index:02}.py").write_text(
            f"def cooling_window_{index}(flow_rate, capacity):\n return flow_rate / capacity\n")
    result = run(repository)
    skip(result, "evidence_candidate_limit")
    assert result["automatic_selection"]["coarse_selection"]["potential_supported_files"] == 25


@pytest.mark.parametrize("strong", [False, True])
def test_unsupported_frontier_never_silently_discarded(repository, strong):
    root, _, _ = repository
    (root / "maintain.sh").write_text("echo 'cooling window'\n" if strong else "echo 'cooling'\n")
    result = run(repository)
    diagnostic = result["automatic_selection"]["coarse_selection"]
    assert diagnostic["unsupported_production_files"] == 1
    if strong:
        skip(result, "unsupported_competitor")
        assert diagnostic["potential_unsupported_files"] == 1
    else:
        assert result["mode"] == "preloaded", result
        assert diagnostic["weak_unsupported_files"] == 1
    assert diagnostic["scope_complete"]


def test_explicit_unsupported_path_blocks_even_when_body_weak(repository):
    root, _, _ = repository
    (root / "maintain.sh").write_text("echo hello\n")
    skip(run(repository, task="Adjust maintain.sh and check cooling window flow rate capacity."),
         "unsupported_competitor")


@pytest.mark.parametrize("target", ["rejected", "parse_exception"])
@pytest.mark.parametrize("change", ["edit", "delete", "policy", "symlink"])
def test_every_coarse_and_parse_exception_version_guarded_until_delivery(repository, monkeypatch, target, change):
    import memglide.integrations.preload as module
    root, _, _ = repository
    path = root / "unrelated.py"
    path.write_text("# cooling\ndef unrelated(x):\n return x\n")
    if target == "parse_exception":
        (root / "tests").mkdir()
        path = root / "tests" / "broken.py"
        path.write_text("def unavailable(:\n")
    original = module.prepare_prompt

    def mutate(*args, **kwargs):
        result = original(*args, **kwargs)
        if kwargs.get("mode") == "off":
            return result
        if change == "edit":
            path.write_text("# changed\n")
        elif change == "delete":
            path.unlink()
        elif change == "policy":
            (root / ".memglideignore").write_text(path.relative_to(root).as_posix() + "\n")
        else:
            path.unlink()
            path.symlink_to(root.parent / "outside.py")
        return result

    monkeypatch.setattr(module, "prepare_prompt", mutate)
    result = run(repository)
    assert result["mode"] == "passthrough", result
    assert result["reason"] in {"ranking_source_changed", "policy_changed", "discovery_unavailable"}


def test_coarse_metadata_pool_cap_is_not_raised(repository):
    root, _, _ = repository
    for index in range(100):
        (root / f"maintain_{index:03}.sh").write_text("echo hello\n")
    skip(run(repository), "coarse_candidate_limit")


def test_coarse_body_byte_cap_is_not_raised(repository):
    root, _, _ = repository
    for index in range(9):
        (root / f"unrelated_{index}.py").write_text("# cooling\n#" + "x" * 240_000 + "\n")
    skip(run(repository), "coarse_source_budget")


def test_coarse_diagnostics_present_for_disabled_and_generic_without_state(tmp_path):
    missing = tmp_path / "missing.db"
    for kwargs in ({}, {"enabled": True, "project_id": "unknown"}):
        result = prepare_task_prompt("Please fix the bug", db_path=missing, selection_policy="v4", **kwargs)
        diagnostic = result["automatic_selection"]["coarse_selection"]
        assert not diagnostic["scope_complete"]
        assert diagnostic["coarse_files_checked"] == 0
        assert diagnostic["coarse_bytes"] == 0
        assert not missing.exists()


def test_receipt_contains_no_source_or_query_text(repository):
    result = run(repository)
    receipt = json.dumps(result["automatic_selection"])
    assert "return flow_rate / capacity" not in receipt
    assert "Cooling window must account" not in receipt


def test_coarse_phase_does_not_spend_next_sql_reader_budget(repository, monkeypatch):
    import memglide.integrations.bounded_router as module
    original = module.discover_scoped_candidates

    def expire(reader, *args):
        result = original(reader, *args)
        reader.deadline = 0
        return result

    monkeypatch.setattr(module, "discover_scoped_candidates", expire)
    result = run(repository)
    assert result["mode"] == "preloaded", result


@pytest.mark.parametrize("mutation", ["settings", "index", "root"])
def test_coarse_to_syntax_phase_rechecks_full_policy_and_index_identity(repository, monkeypatch, mutation):
    import memglide.integrations.bounded_router as module
    root, db, project = repository
    original = module.discover_scoped_candidates

    def change(reader, *args):
        result = original(reader, *args)
        with db.connect() as conn:
            if mutation == "settings":
                conn.execute("UPDATE settings SET value='4000' WHERE key='max_file_size'")
            elif mutation == "index":
                conn.execute("UPDATE projects SET indexed_at='changed' WHERE id=?", (project,))
            else:
                conn.execute("UPDATE projects SET path=? WHERE id=?", (str(root.parent), project))
        return result

    monkeypatch.setattr(module, "discover_scoped_candidates", change)
    skip(run(repository), "ranking_policy_changed" if mutation == "settings" else "index_changed")
