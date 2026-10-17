"""Synthetic report fixtures test evidence handling, never product performance."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import refinement_reporting as reporting  # noqa: E402


def component(task_id: str = "example", *, status: str = "passed") -> dict:
    return {
        "task_id": task_id,
        "language": "python",
        "baseline_commit": "fixture-commit",
        "status": status,
        "transport_status": "passed" if status == "passed" else "failed",
        "error": {"message": "synthetic failure"} if status != "passed" else None,
        "probe_identity": {
            "session_task": "find cache",
            "retrieval_requests": [{"query": "find cache", "level": 2, "budget": 8000}],
        },
        "transport": {"initialize_and_list_tools_wall_seconds": 5.0},
        "index": {"wall_seconds": 0.5},
        "mcp_transport_wall_seconds": 10.0,
        "mcp_calls": [{"name": "get_context", "wall_seconds": 1.0}],
        "natural_prompt_retrieval": {
            "returned_files": ["src/cache.py", "tests/test_cache.py", "README.md"],
            "returned_item_count": 4,
            "expected_target_files": ["src/cache.py"],
            "expected_symbols": ["src.cache.Cache.get"],
            "target_file_coverage_fraction": 1.0,
            "expected_declaration_visible_fraction": 1.0,
        },
    }


def test_p95_counts_missing_without_treating_invalid_observations_as_zero() -> None:
    values = list(range(1, 21)) + [None, True, "invalid", float("nan"), float("inf")]
    result = reporting.distribution(values)
    assert result["n"] == 20 and result["missing"] == 5
    assert result["mean"] == 10.5 and result["median"] == 10.5
    assert result["p95"] == 19
    assert reporting.distribution([None])["mean"] is None


def test_sdk_stages_are_separate_and_complete_body_recall_is_never_invented() -> None:
    baseline, candidate = {"results": [component()]}, {"results": [component()]}
    report = reporting.build_report(baseline, candidate)
    comparison = report["component_comparison"]
    assert comparison["comparison_valid"] is True
    metrics = comparison["observations"]["candidate"][0]["metrics"]
    assert metrics["startup_initialize_list_tools_wall_seconds"] == 5
    assert metrics["first_natural_retrieval_wall_seconds"] == 1
    assert metrics["seven_call_workflow_wall_seconds"] == 10
    assert metrics["returned_file_count"] == 3
    assert metrics["declared_target_file_precision"] == pytest.approx(1 / 3)
    assert not any("complete_body" in name for name in metrics)
    assert report["unavailable_from_component_measurements"]["actual_model_input_tokens"] is None
    assert report["savings_claim_supported_by_component_measurements"] is False


def test_invalid_fixture_identity_withholds_every_extra_paired_delta() -> None:
    baseline, candidate = {"results": [component()]}, {"results": [component()]}
    candidate["results"][0]["baseline_commit"] = "changed-commit"
    candidate["results"][0]["transport"]["initialize_and_list_tools_wall_seconds"] = 1
    result = reporting.component_comparison(baseline, candidate)
    assert result["comparison_valid"] is False
    assert result["paired_observations"][0]["candidate_minus_baseline"] == dict.fromkeys(
        reporting.COMPONENT_METRICS
    )
    assert (
        result["summaries"]["startup_initialize_list_tools_wall_seconds"]["candidate"]["mean"] == 1
    )


def test_failed_observations_and_partial_measurements_remain_visible() -> None:
    failed = component("failed", status="failed")
    del failed["transport"]
    del failed["natural_prompt_retrieval"]
    report = reporting.build_report(
        {"results": [component(), failed]}, {"results": [component(), copy.deepcopy(failed)]}
    )
    comparison = report["component_comparison"]
    assert comparison["status_counts"]["candidate"] == {"passed": 1, "failed": 1}
    summary = comparison["summaries"]["returned_file_count"]["candidate"]
    assert summary["n"] == 1 and summary["missing"] == 1
    assert "synthetic failure" in reporting.render_markdown(report)


def test_fresh_declared_recall_and_direct_timing_keep_failure_denominators() -> None:
    retrieval = {
        "observations": [
            {
                "query_id": "one",
                "strategy": "current",
                "status": "ok",
                "required_dependency_complete_body_recall": 0.5,
                "all_required_bodies_present": False,
            },
            {"query_id": "two", "strategy": "current", "status": "error", "errors": ["failed"]},
        ]
    }
    timing = {
        "runs": [
            {"case": "natural", "repeat": 1, "status": "ok", "wall_seconds": 2.0},
            {"case": "natural", "repeat": 2, "status": "error", "error": "timed out"},
        ]
    }
    result = reporting.build_report(
        {"results": []}, {"results": []}, retrieval=retrieval, timing_candidate=timing
    )
    selected = result["retrieval_evaluation"]["summaries"]["current"]
    assert selected["observations"] == 2 and selected["status_counts"]["error"] == 1
    metric = selected["metrics"]["required_dependency_complete_body_recall"]
    assert metric["n"] == 1 and metric["missing"] == 1 and metric["mean"] == 0.5
    assert selected["metrics"]["all_required_bodies_present"]["mean"] == 0
    measured = result["direct_timings"]["candidate"]["summaries"]["natural"]
    assert measured["wall_seconds"]["n"] == 1 and measured["wall_seconds"]["missing"] == 1
    assert result["retrieval_evaluation"]["original_report"] == retrieval
    assert result["direct_timings"]["candidate"]["original_report"] == timing


def test_cli_preserves_previous_artifacts_and_hashes_inputs(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"results": [component()]}), encoding="utf-8")
    prefix = tmp_path / "fresh-report"
    arguments = [
        "--component-baseline",
        str(source),
        "--component-candidate",
        str(source),
        "--output-prefix",
        str(prefix),
    ]
    assert reporting.main(arguments) == 0
    original = prefix.with_suffix(".json").read_bytes()
    report = json.loads(original)
    assert len(report["input_artifacts"]["component_baseline"]["sha256"]) == 64
    with pytest.raises(SystemExit, match="2"):
        reporting.main(arguments)
    assert prefix.with_suffix(".json").read_bytes() == original


def test_explicitly_changed_sdk_source_invalidates_extra_deltas() -> None:
    report = {"results": [component()]}
    result = reporting.component_comparison(
        report, report, candidate_provenance={"source_unchanged_during_probe": False}
    )
    assert result["comparison_valid"] is False
    assert result["paired_observations"][0]["comparable"] is False
    assert result["summaries"]["returned_file_count"]["paired_candidate_minus_baseline"]["n"] == 0


def timing_fixture() -> dict:
    return {
        "protocol_sha256": "p" * 64,
        "fixture": {"files": {"cache.py": "source-hash"}},
        "frozen_source_sha256": {"indexer": "same-indexer"},
        "runs": [
            {
                "pair_id": "natural:1",
                "case": "natural",
                "request": {"query": "find cache", "level": 2, "budget": 8000},
                "status": "ok",
                "wall_seconds": 2.0,
                "cpu_seconds": 1.5,
                "result": {
                    "session_id": "before-session",
                    "retrieval_id": "before-retrieval",
                    "passport": {"recommended_next_retrievals": ["expand_context(before-session)"]},
                    "items": [{"path": "cache.py", "snippet": "def get(): return 1"}],
                },
            }
        ],
    }


def test_direct_pairs_require_identical_requests_and_complete_output_equivalence() -> None:
    baseline, candidate = timing_fixture(), timing_fixture()
    candidate["runs"][0]["result"]["session_id"] = "after-session"
    candidate["runs"][0]["result"]["retrieval_id"] = "after-retrieval"
    candidate["runs"][0]["result"]["passport"]["recommended_next_retrievals"] = [
        "expand_context(after-session)"
    ]
    candidate["runs"][0]["wall_seconds"] = 1
    paired = reporting.timing_comparison(baseline, candidate)
    assert paired["valid_pair_count"] == 1
    assert paired["paired_candidate_minus_baseline"]["wall_seconds"]["mean"] == -1
    candidate["runs"][0]["wall_seconds"] = 3
    paired = reporting.timing_comparison(baseline, candidate)
    assert paired["all_observed_pair_regressions"] == [
        {"pair_id": "natural:1", "metric": "wall_seconds", "candidate_minus_baseline": 1}
    ]
    assert {item["statistic"] for item in paired["all_observed_summary_regressions"]} == {
        "mean",
        "median",
        "p95",
    }
    candidate["runs"][0]["result"]["items"][0]["snippet"] = "def get(): return"
    paired = reporting.timing_comparison(baseline, candidate)
    assert paired["valid_pair_count"] == 0
    assert "outputs differ" in paired["pairs"][0]["invalid_reasons"][0]
    assert paired["paired_candidate_minus_baseline"]["wall_seconds"]["mean"] is None


def test_changed_direct_protocol_and_duplicate_pair_ids_fail_closed() -> None:
    baseline, candidate = timing_fixture(), timing_fixture()
    candidate["protocol_sha256"] = "different"
    candidate["runs"].append(copy.deepcopy(candidate["runs"][0]))
    result = reporting.timing_comparison(baseline, candidate)
    assert result["comparison_valid"] is False and result["valid_pair_count"] == 0
    assert any("duplicate" in error for error in result["shared_errors"])
    assert result["paired_candidate_minus_baseline"]["wall_seconds"]["n"] == 0


def test_reused_validation_and_historical_timing_source_are_explicit() -> None:
    timing = timing_fixture()
    timing["owned_source_sha256"] = {"context": "earlier-context-source"}
    result = reporting.build_report(
        {"results": []},
        {"results": []},
        retrieval={
            "status": "valid",
            "holdout_previously_evaluated": True,
            "validation_reuse_reason": "Regression replay after a concrete truncation bug fix",
            "observations": [],
        },
        timing_candidate=timing,
        candidate_provenance={
            "source_files": {"src/memglide/core/context.py": "new-context-source"}
        },
    )
    assert result["retrieval_evaluation"]["holdout_previously_evaluated"] is True
    assert result["direct_timings"]["candidate_context_source_matches_sdk_candidate"] is False
    text = reporting.render_markdown(result)
    assert "Previously evaluated retrieval validation" in text
    assert "not independent unseen evidence" in text
    assert "earlier implementation" in text
