"""Check experimental isolation, metrics, locked holdout, and candidate mechanics."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.corpus import task_definitions  # noqa: E402
from benchmarks.retrieval_experiment import (  # noqa: E402
    HOLDOUT_PATH,
    HOLDOUT_SHA256,
    aggregate,
    digest,
    evaluate_query,
    frozen_legacy_indexer,
    init_git,
    load_holdout,
    mmr_diversify,
    ranking_metrics,
    reciprocal_rank_fusion,
    select_strategy,
    strategy_candidates,
    write_holdout_repository,
)
from memglide.service import Service  # noqa: E402


def test_holdout_is_locked_and_separate_from_original_prompts(tmp_path):
    manifest = load_holdout()
    assert digest(HOLDOUT_PATH) == HOLDOUT_SHA256
    assert len(manifest["queries"]) == 24
    assert {query["language"] for query in manifest["queries"]} == {"python", "typescript"}
    for language in ("python", "typescript"):
        assert sum(query["language"] == language for query in manifest["queries"]) == 12
    development_prompts = {task["prompt"] for task in task_definitions()}
    assert not development_prompts & {query["prompt"] for query in manifest["queries"]}
    for query in manifest["queries"]:
        assert query["primary_target"] in manifest["repositories"][query["repository"]]["files"]
    edited = tmp_path / "edited.json"
    edited.write_text(HOLDOUT_PATH.read_text() + "\n")
    with pytest.raises(ValueError, match="changed after"):
        load_holdout(edited)


def test_development_prompts_remain_identical_to_original_manifest():
    baseline = json.loads((HOLDOUT_PATH.parent / "tasks.json").read_text())["tasks"]
    assert task_definitions() == baseline


def test_holdout_repositories_are_deterministic_and_never_execute_fixture_code(tmp_path):
    manifest = load_holdout()
    name = "orion-python-holdout-v1"
    first, second = tmp_path / "first", tmp_path / "second"
    write_holdout_repository(manifest, name, first)
    write_holdout_repository(manifest, name, second)
    assert {
        str(path.relative_to(first)): path.read_bytes()
        for path in first.rglob("*")
        if path.is_file()
    } == {
        str(path.relative_to(second)): path.read_bytes()
        for path in second.rglob("*")
        if path.is_file()
    }
    for path in first.rglob("*.py"):
        ast.parse(path.read_text())
    with pytest.raises(ValueError, match="empty"):
        write_holdout_repository(manifest, name, first)


def test_rank_metrics_deduplicate_declarations_and_keep_missing_target():
    result = ranking_metrics(["a.py", "a.py", "b.py", "c.py"], "b.py")
    assert result["primary_target_rank"] == 2
    assert result["primary_file_hit_at_1"] == 0
    assert result["primary_file_hit_at_3"] == 1
    assert result["primary_file_reciprocal_rank"] == 0.5
    missing = ranking_metrics(["a.py"], "missing.py")
    assert missing["primary_target_rank"] is None
    assert missing["primary_file_hit_at_5"] == 0
    assert missing["primary_file_reciprocal_rank"] == 0


def test_rrf_duplicates_do_not_multiply_votes_and_ties_are_deterministic():
    fused = reciprocal_rank_fusion([["b.py", "b.py", "a.py"], ["a.py", "b.py"]])
    assert fused[0][0] == "a.py"
    assert fused[0][1] == fused[1][1]
    assert fused[0][1] == 1 / 61 + 1 / 62
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], k=0)


def test_mmr_penalizes_redundant_documents_without_inventing_candidates():
    ranked = [("a", 1.0), ("b", 0.99), ("c", 0.98)]
    result = mmr_diversify(ranked, {"a": "red orange", "b": "red orange", "c": "blue green"}, 0.5)
    assert [path for path, _ in result] == ["a", "c", "b"]
    assert [score for _, score in result] == [3, 2, 1]
    assert mmr_diversify([], {}) == []
    with pytest.raises(ValueError):
        mmr_diversify(ranked, {}, 2)


def _valid_row(strategy="idf_lexical", coverage=1.0, hit=1, rr=1.0):
    return {
        "query_id": "example",
        "strategy": strategy,
        "status": "ok",
        "primary_file_hit_at_1": hit,
        "primary_file_hit_at_3": 1,
        "primary_file_hit_at_5": 1,
        "primary_file_reciprocal_rank": rr,
        "context_target_file_coverage": coverage,
    }


def test_aggregates_keep_errors_missing_and_misses_visible():
    result = aggregate([_valid_row(coverage=0, hit=0), {"query_id": "broken", "status": "error"}])
    assert result["planned_queries"] == 2
    assert result["valid_queries"] == 1
    assert result["error_queries"] == ["broken"]
    assert result["context_target_file_misses"] == ["example"]
    assert result["primary_file_misses_at_1"] == ["example"]
    assert result["context_target_file_coverage"] == {
        "n": 1,
        "missing": 1,
        "mean": 0.0,
        "median": 0.0,
    }
    assert result["search_wall_seconds"]["mean"] is None


def test_selection_uses_declared_quality_order_and_requires_complete_development():
    summaries = {
        "legacy": aggregate([_valid_row()]),
        "idf_lexical": aggregate([_valid_row(hit=0, rr=0.5)]),
        "bm25_files": aggregate([_valid_row(hit=1)]),
        "rrf": aggregate([_valid_row(hit=1)]),
        "rrf_mmr": aggregate([_valid_row(), {"query_id": "missing", "status": "error"}]),
    }
    assert select_strategy(summaries)["strategy"] == "bm25_files"
    summaries["idf_lexical"] = aggregate([_valid_row()])
    assert select_strategy(summaries)["strategy"] == "idf_lexical"
    assert select_strategy({"legacy": summaries["legacy"]})["strategy"] is None


def test_actual_database_candidates_and_common_context_are_evaluated(tmp_path):
    manifest = load_holdout()
    name = "orion-python-holdout-v1"
    worktree = tmp_path / "repository"
    write_holdout_repository(manifest, name, worktree)
    init_git(worktree)
    service = Service(tmp_path / "state/memglide.db")
    try:
        project = service.indexer.add_project(str(worktree))
        legacy, source_hash = frozen_legacy_indexer(service.db)
        assert len(source_hash) == 64
        query = next(
            query for query in manifest["queries"] if query["id"] == "holdout-python-timetable"
        )
        original_search = service.indexer.search
        for strategy in ("legacy", "idf_lexical", "bm25_files", "rrf", "rrf_mmr"):
            candidates = strategy_candidates(
                service, project["id"], query["prompt"], strategy, legacy.search
            )
            assert candidates
            assert all((worktree / item["path"]).is_file() for item in candidates)
            result = evaluate_query(
                service,
                project["id"],
                query,
                "holdout",
                strategy,
                legacy.search,
                tmp_path / "artifacts" / strategy,
            )
            assert result["status"] == "ok", result["errors"]
            assert result["primary_file_hit_at_3"] == 1
            assert result["context_target_file_coverage"] == 1
            assert result["context_estimated_planning_tokens"] <= 8000
            assert service.indexer.search == original_search
        with pytest.raises(ValueError, match="Unknown"):
            strategy_candidates(service, project["id"], query["prompt"], "missing", legacy.search)
    finally:
        service.close()
