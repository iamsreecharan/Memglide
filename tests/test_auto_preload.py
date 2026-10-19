"""Opt-in task discovery preserves complete source and conservative fallback."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations.auto_preload import MAX_ADDED_TOKENS, prepare_task_prompt
from memglide.integrations.preload import TASK_SEPARATOR, prepare_prompt
from memglide.storage.database import Database


@pytest.fixture
def repository(tmp_path: Path) -> tuple[Path, Database, str]:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "retry_delay.py").write_text(
        "def retry_delay(attempt, cap):\n    return min(cap, attempt * 2)\n", encoding="utf-8"
    )
    (root / "quota_limit.py").write_text(
        "def quota_limit(amount):\n    return max(0, amount)\n", encoding="utf-8"
    )
    db = Database(tmp_path / "state" / "state.db")
    project = Indexer(db).add_project(str(root))
    return root, db, project["id"]


def automatic(repository: tuple[Path, Database, str], **kwargs: Any) -> dict[str, Any]:
    _, db, project = repository
    return prepare_task_prompt(
        kwargs.pop("prompt", "Retry delay should clamp negative attempts to zero."),
        project_id=project,
        db_path=db.path,
        enabled=True,
        **kwargs,
    )


def skipped(result: dict[str, Any], reason: str | None = None) -> None:
    assert result["mode"] == "passthrough"
    assert result["context_bytes"] == 0
    assert result["files"] == []
    receipt = result["automatic_selection"]
    assert receipt["decision"] == "SKIP"
    assert receipt["selected_paths"] == []
    assert receipt["source_versions"] == {}
    assert receipt["estimated_added_tokens"] == 0
    assert receipt["auxiliary_model_calls"] == 0
    assert receipt["reason"] == result["reason"]
    if reason is not None:
        assert result["reason"] == reason


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_path_free_task_complete_source_and_old_api_unchanged(repository, context_format):
    root, db, project = repository
    task = "Retry delay should clamp negative attempts to zero."
    result = automatic(repository, prompt=task, context_format=context_format)
    assert result["mode"] == "preloaded", result
    expected = prepare_prompt(
        task,
        db_path=db.path,
        project_id=project,
        focus_paths=["retry_delay.py"],
        context_format=context_format,
    )
    assert result["prompt"] == expected["prompt"]
    assert result["files"] == expected["files"]
    body = (root / "retry_delay.py").read_text()
    assert result["files"][0]["sha256"] == hashlib.sha256(body.encode()).hexdigest()
    receipt = result["automatic_selection"]
    assert receipt["decision"] == "FOCUSED_SOURCE"
    assert receipt["selected_paths"] == ["retry_delay.py"]
    assert receipt["source_versions"] == {"retry_delay.py": result["files"][0]["sha256"]}
    assert receipt["ranked_candidates"][0]["explicit_anchor"] is False
    assert {"retry", "delay"} <= set(receipt["ranked_candidates"][0]["evidence_terms"])
    assert receipt["index_refresh_wall_seconds"] > 0
    assert receipt["estimated_added_tokens"] == (result["context_bytes"] + 2) // 3
    assert receipt["auxiliary_model_calls"] == 0
    assert body not in json.dumps(receipt)
    assert db.one("SELECT count(*) AS n FROM sessions")["n"] == 0
    assert db.one("SELECT count(*) AS n FROM retrievals")["n"] == 0
    if context_format == "compact-prefix":
        envelope = json.loads(result["prompt"].split(TASK_SEPARATOR)[0])
        assert envelope["memglide_sources"][0]["content"] == body


def test_disabled_supplied_generic_bypass_no_state_or_heavy_imports(tmp_path):
    source_root = str(Path(__file__).resolve().parents[1] / "src")
    program = r'''
import builtins, sqlite3, sys
sys.path.insert(0, sys.argv[1])
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if any(name == p or name.startswith(p + ".") for p in
           ("memglide.core", "memglide.storage", "memglide.security", "memglide.service",
            "memglide.memory", "mcp", "tree_sitter", "pathspec")):
        raise AssertionError("heavy import: " + name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from memglide.integrations.auto_preload import prepare_task_prompt
def forbidden(*args, **kwargs): raise AssertionError("state access")
sqlite3.connect = forbidden
cases = [{}, {"enabled":True, "mode":"off", "project_id":"p"},
         {"enabled":True, "context_supplied":True, "project_id":"p"},
         {"enabled":True}, {"enabled":True, "project_id":"p"}]
results = [prepare_task_prompt("Improve code", db_path=sys.argv[2], **case) for case in cases]
assert [r["reason"] for r in results] == ["disabled", "disabled", "context_supplied",
                                         "no_approved_project", "insufficient_task_evidence"]
assert all(r["prompt"] == "Improve code" and r["automatic_selection"]["decision"] == "SKIP"
           for r in results)
for task in ("Fix the bug", "Please make it work"):
    result = prepare_task_prompt(task, enabled=True, project_id="p", db_path=sys.argv[2])
    assert result["reason"] == "insufficient_task_evidence", result
'''
    missing = tmp_path / "not-created" / "state.db"
    subprocess.run(
        [sys.executable, "-I", "-c", program, source_root, str(missing)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert not missing.parent.exists()


@pytest.mark.parametrize("kind", ["missing", "unknown_project", "corrupt"])
def test_unapproved_or_corrupt_state_declines_without_creation(repository, tmp_path, kind):
    _, db, _ = repository
    path = tmp_path / "absent" / "state.db"
    project = "unknown"
    if kind == "corrupt":
        path = tmp_path / "corrupt.db"
        path.write_bytes(b"not SQLite")
    if kind == "unknown_project":
        path = db.path
    original = path.read_bytes() if path.exists() else None
    result = prepare_task_prompt(
        "Retry delay clamps negative attempts", project_id=project, db_path=path, enabled=True
    )
    skipped(result)
    assert (path.read_bytes() if path.exists() else None) == original


def test_ambiguous_independent_modules_abstain(repository):
    root, _, _ = repository
    (root / "other_retry.py").write_text((root / "retry_delay.py").read_text())
    skipped(automatic(repository), "ambiguous_candidates")


def test_fts_only_comment_match_is_insufficient(repository):
    root, _, _ = repository
    (root / "other.py").write_text("# banana coconut\ndef transform(x):\n    return x\n")
    skipped(automatic(repository, prompt="Fix banana coconut handling."), "weak_lexical_evidence")


def test_no_matching_source_declines(repository):
    skipped(automatic(repository, prompt="Normalize wibble zonk delimiters."), "no_production_match")


@pytest.mark.parametrize("change", ["edit", "new", "delete"])
def test_full_refresh_discovers_changed_new_and_deleted_files(repository, change):
    root, db, project = repository
    target = root / "retry_delay.py"
    if change == "edit":
        target.write_text("def retry_delay(attempt, cap):\n    return min(cap, max(0, attempt))\n")
    elif change == "new":
        target.rename(root / "renamed_retry.py")
    else:
        target.unlink()
    result = automatic(repository)
    if change == "delete":
        skipped(result)
        assert db.one("SELECT * FROM files WHERE project_id=? AND path='retry_delay.py'", (project,)) is None
    else:
        assert result["mode"] == "preloaded", result
        expected = "renamed_retry.py" if change == "new" else "retry_delay.py"
        assert result["files"][0]["path"] == expected
        assert result["files"][0]["sha256"] == hashlib.sha256((root / expected).read_bytes()).hexdigest()


@pytest.mark.parametrize("change", ["ignore", "nested_ignore", "secret", "secret_path", "symlink", "oversized"])
def test_current_policy_and_secure_source_exclusions(repository, tmp_path, change):
    root, _, _ = repository
    target = root / "retry_delay.py"
    if change == "ignore":
        (root / ".gitignore").write_text("retry_delay.py\n")
    elif change == "nested_ignore":
        nested = root / "sub"
        nested.mkdir()
        target.rename(nested / target.name)
        (nested / ".memglideignore").write_text("retry_delay.py\n")
    elif change == "secret":
        target.write_text(target.read_text() + '\napi_key = "sk-abcdefghijklmnopqrstuvwx"\n')
    elif change == "secret_path":
        hidden = root / ".aws"
        hidden.mkdir()
        target.rename(hidden / target.name)
    elif change == "symlink":
        outside = tmp_path / "outside.py"
        target.rename(outside)
        target.symlink_to(outside)
    elif change == "oversized":
        target.write_text(target.read_text() + "#" + "x" * 512_001)
    result = automatic(repository)
    skipped(result)
    assert "abcdefghijklmnopqrstuvwx" not in result["prompt"]
    assert result["automatic_selection"]["selected_paths"] == []


@pytest.mark.parametrize("path", ["tests/retry_delay.py", "fixtures/retry_delay.py", "docs/retry_delay.py", "AGENTS.md", "retry_delay.json"])
def test_automatic_source_role_excludes_nonproduction(repository, path):
    root, _, _ = repository
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    (root / "retry_delay.py").rename(target)
    skipped(automatic(repository))


def test_complete_direct_helper_bundle(repository):
    root, _, _ = repository
    (root / "retry_delay.py").write_text(
        "from clamp import clamp_negative\ndef retry_delay(attempt, cap):\n"
        "    return min(cap, clamp_negative(attempt))\n"
    )
    (root / "clamp.py").write_text("def clamp_negative(value):\n    return max(0, value)\n")
    result = automatic(repository, prompt="Fix retry_delay for negative attempts.")
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["decision"] == "FULL_SOURCE"
    assert result["automatic_selection"]["selected_paths"] == ["clamp.py", "retry_delay.py"]
    assert result["automatic_selection"]["dependency_paths_considered"] == 1


def test_required_bundle_over_budget_is_never_partially_injected(repository):
    root, _, _ = repository
    (root / "retry_delay.py").write_text(
        "from clamp import clamp_negative\ndef retry_delay(attempt, cap):\n"
        "    return min(cap, clamp_negative(attempt))\n"
    )
    (root / "clamp.py").write_text("def clamp_negative(value):\n    return max(0, value)\n" + "#" * 2000)
    result = automatic(repository, prompt="Fix retry_delay for negative attempts.", max_context_bytes=1000)
    skipped(result)
    assert result["reason"].startswith("source_preparation_")


def test_helper_fanout_is_explicitly_bounded(repository):
    root, _, _ = repository
    imports = []
    for number in range(4):
        (root / f"helper{number}.py").write_text(f"def helper{number}(x):\n    return x\n")
        imports.append(f"from helper{number} import helper{number}\n")
    (root / "retry_delay.py").write_text("".join(imports) + "def retry_delay(attempt):\n    return attempt\n")
    skipped(automatic(repository, prompt="Fix retry_delay for negative attempts."), "dependency_bundle_limit")


@pytest.mark.parametrize("limit", [1, 20])
def test_added_token_cap_counts_entire_envelope(repository, limit):
    result = automatic(repository, max_added_tokens=limit)
    skipped(result)
    assert result["reason"].startswith("source_preparation_")


def test_partial_or_error_index_abstains(repository, monkeypatch):
    original = Indexer.reindex

    def partial(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        result["partial"] = True
        return result

    monkeypatch.setattr(Indexer, "reindex", partial)
    skipped(automatic(repository), "incomplete_index")


@pytest.mark.parametrize("change", ["source", "ignore", "delete", "symlink"])
def test_post_preparation_races_discard_entire_addition(repository, monkeypatch, tmp_path, change):
    root, _, _ = repository
    import memglide.integrations.preload as preload

    original = preload.prepare_prompt

    def raced(*args, **kwargs):
        result = original(*args, **kwargs)
        if result["mode"] == "preloaded":
            target = root / "retry_delay.py"
            if change == "source":
                target.write_text("def retry_delay(attempt):\n    return 42\n")
            elif change == "ignore":
                (root / ".gitignore").write_text("retry_delay.py\n")
            elif change == "delete":
                target.unlink()
            else:
                outside = tmp_path / "outside.py"
                target.rename(outside)
                target.symlink_to(outside)
        return result

    monkeypatch.setattr(preload, "prepare_prompt", raced)
    skipped(automatic(repository))


def test_exact_already_supplied_body_suppresses_duplicate(repository):
    root, _, _ = repository
    body = (root / "retry_delay.py").read_text()
    prompt = "Fix retry_delay for negative attempts.\nretry_delay.py:\n" + body
    result = automatic(repository, prompt=prompt, provided_sources={"retry_delay.py": body})
    skipped(result, "source_already_provided")
    assert result["prompt"] == prompt
    assert result["automatic_selection"]["provided_source_paths"] == ["retry_delay.py"]


@pytest.mark.parametrize("change", ["not_in_prompt", "old_body", "wrong_path"])
def test_unverified_provided_source_does_not_suppress_fresh_source(repository, change):
    root, _, _ = repository
    body = (root / "retry_delay.py").read_text()
    prompt = "Fix retry_delay for negative attempts."
    sources = {"retry_delay.py": body}
    if change == "old_body":
        sources = {"retry_delay.py": "old source"}
        prompt += "\nretry_delay.py\nold source"
    elif change == "wrong_path":
        sources = {"unknown.py": body}
        prompt += "\nunknown.py\n" + body
    skipped(automatic(repository, prompt=prompt, provided_sources=sources))


def test_distinct_file_search_prevents_symbol_starvation_and_default_stays_unchanged(repository):
    root, db, project = repository
    (root / "many.py").write_text(
        "".join(f"def retry_delay_{n}(attempt):\n    return attempt\n" for n in range(130))
    )
    indexer = Indexer(db)
    indexer.reindex(project)
    regular = indexer._search(project, "retry delay", 100, refresh=False, metadata_only=True)
    distinct = indexer._search(
        project, "retry delay", 100, refresh=False, metadata_only=True, distinct_files=True
    )
    assert len(regular) == 100
    assert len({row["path"] for row in distinct}) == len(distinct)
    assert {"many.py", "retry_delay.py"} <= {row["path"] for row in distinct}
    assert indexer._search(
        project, "retry delay", 100, refresh=False, metadata_only=True, distinct_files=False
    ) == regular


@pytest.mark.parametrize("options", [{"enabled": 1}, {"mode": "guess"}, {"max_added_tokens": True}, {"max_added_tokens": 0}, {"max_added_tokens": MAX_ADDED_TOKENS + 1}, {"provided_sources": []}, {"provided_sources": {"a.py": ""}}])
def test_strict_argument_types(options):
    with pytest.raises(ValueError):
        prepare_task_prompt("Fix retry delay", **options)


def test_sqlite_query_failure_is_safe_fallback(repository, monkeypatch):
    import memglide.integrations.auto_preload as automatic_module

    def failed(*args, **kwargs):
        raise sqlite3.OperationalError("interrupted")

    monkeypatch.setattr(automatic_module, "_preflight", failed)
    skipped(automatic(repository), "discovery_unavailable")


@pytest.mark.parametrize("policy", [{"exact_symbol": float("nan")}, {"exact_symbol": "high"}, []])
def test_corrupt_ranking_policy_declines_before_mutating_index(repository, policy):
    _, db, project = repository
    indexed_at = db.project(project)["indexed_at"]
    db.execute("UPDATE settings SET value=? WHERE key='retrieval_weights'", (json.dumps(policy),))
    skipped(automatic(repository), "ranking_policy_unavailable")
    assert db.project(project)["indexed_at"] == indexed_at


def test_known_oversized_index_declines_before_refresh(repository):
    _, db, project = repository
    indexed_at = db.project(project)["indexed_at"]
    db.execute("UPDATE files SET size=? WHERE project_id=?", (101 * 1024 * 1024, project))
    skipped(automatic(repository), "index_resource_limit")
    assert db.project(project)["indexed_at"] == indexed_at


def test_unresolved_static_edges_are_reported_without_claiming_global_closure(repository):
    root, _, _ = repository
    (root / "retry_delay.py").write_text(
        "from unavailable_external_package import clamp_negative\n"
        "def retry_delay(attempt, cap):\n    return min(cap, clamp_negative(attempt))\n"
    )
    result = automatic(repository, prompt="Fix retry_delay for negative attempts.")
    assert result["mode"] == "preloaded", result["reason"]
    assert result["automatic_selection"]["unresolved_dependency_count"] >= 1
    assert "not global completeness" in result["automatic_selection"]["static_dependency_coverage"]


def test_ranker_time_budget_failure_records_attempted_retrieval(repository, monkeypatch):
    original = Indexer._search

    def interrupted(self, *args, **kwargs):
        if kwargs.get("distinct_files"):
            raise sqlite3.OperationalError("interrupted")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Indexer, "_search", interrupted)
    result = automatic(repository)
    skipped(result, "discovery_unavailable")
    assert result["automatic_selection"]["retrieval_wall_seconds"] > 0


def test_saturated_candidate_pool_abstains_before_ignoring_unknown_alternatives(repository, monkeypatch):
    def saturated(*args, **kwargs):
        return [{"path": "retry_delay.py"}] * 100

    monkeypatch.setattr(Indexer, "_search", saturated)
    result = automatic(repository)
    skipped(result, "candidate_limit_reached")
    assert result["automatic_selection"]["candidate_generation_limit_reached"] is True


@pytest.mark.parametrize("change", ["delete", "replace"])
def test_approval_to_refresh_database_race_never_creates_database(repository, monkeypatch, change):
    _, db, _ = repository
    import memglide.integrations.auto_preload as automatic_module

    original = automatic_module._preflight

    def raced(database, project_id):
        original(database, project_id)
        database.unlink()
        if change == "replace":
            database.write_bytes(b"replacement database must remain untouched")

    monkeypatch.setattr(automatic_module, "_preflight", raced)
    result = automatic(repository)
    skipped(result)
    if change == "delete":
        assert not db.path.exists()
    else:
        assert db.path.read_bytes() == b"replacement database must remain untouched"


def test_public_task_query_separates_wrapper_workflow_without_changing_delivered_prompt(repository):
    task = "Retry delay should clamp negative attempts to zero."
    wrapper = (
        "Follow repository rules. Run regression tests, protect tooling and describe validation.\n"
        "The workflow mentions quota limits only as an unrelated example.\n"
    )
    result = automatic(repository, prompt=wrapper + task, task_query=task)
    assert result["mode"] == "preloaded", result["reason"]
    assert result["automatic_selection"]["selected_paths"] == ["retry_delay.py"]
    assert result["prompt"].endswith(TASK_SEPARATOR + wrapper + task)
    assert "quota" not in result["automatic_selection"]["ranked_candidates"][0]["evidence_terms"]


def test_explicit_query_allows_large_actual_prompt_with_verified_supplied_source(repository):
    root, _, _ = repository
    body = (root / "retry_delay.py").read_text()
    task = "Fix retry_delay for negative attempts."
    prompt = "Workflow text. " * 400 + task + "\nretry_delay.py\n" + body
    result = automatic(repository, prompt=prompt, task_query=task, provided_sources={"retry_delay.py": body})
    skipped(result, "source_already_provided")
    assert result["prompt"] == prompt


@pytest.mark.parametrize("query", ["", "   ", "not in delivered task", 3, "x" * 4001])
def test_external_or_invalid_task_query_rejected_before_database_access(tmp_path, query):
    missing = tmp_path / "missing" / "state.db"
    with pytest.raises(ValueError, match="task_query"):
        prepare_task_prompt(
            "Fix retry delay", project_id="p", db_path=missing, enabled=True, task_query=query
        )
    assert not missing.parent.exists()
