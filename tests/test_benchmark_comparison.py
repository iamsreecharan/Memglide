"""Paired component comparisons reject changed conditions and retain bad news."""

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks.compare_components import compare_reports, render_markdown  # noqa: E402


def _result(task_id="py-holdout"):
    return {
        "task_id": task_id,
        "language": "python",
        "baseline_commit": "fixed-fixture-commit",
        "status": "passed",
        "transport_status": "passed",
        "natural_prompt_retrieval": {
            "expected_target_files": ["pkg/cache.py"],
            "expected_symbols": ["pkg.cache.Cache.get"],
            "target_file_coverage_fraction": 1.0,
            "expected_symbol_coverage_fraction": 1.0,
            "expected_declaration_visible_fraction": 1.0,
        },
        "natural_prompt_hash_freshness": {"all_hashes_current": True},
        "controlled_freshness": {
            "old_passport_detected_edit": True,
            "updated_target_sha_matches": True,
            "updated_target_contains_edit_marker": True,
            "updated_evidence_hashes": {"all_hashes_current": True},
        },
        "index": {"wall_seconds": 1.0, "client_cpu_seconds": 0.5},
        "mcp_transport_wall_seconds": 4.0,
        "local_server_overhead": {"sampled_cpu_seconds": 3.0, "sampled_peak_rss_bytes": 1024},
        "probe_identity": {
            "session_task": "Find the deadline boundary defect.",
            "retrieval_requests": [
                {"query": "Find the deadline boundary defect.", "level": 2, "budget": 8000},
                {"query": "pkg/cache.py", "level": 3, "budget": 16000},
                {"query": "pkg/cache.py", "level": 3, "budget": 16000},
            ],
        },
    }


def _report(*results):
    return {"summary": {"original_measurement": "preserved"}, "results": list(results)}


@pytest.mark.parametrize("change", ["prompt", "budget", "fixture", "targets", "language"])
def test_changed_conditions_prevent_paired_deltas(change):
    baseline = _report(_result())
    candidate = copy.deepcopy(baseline)
    result = candidate["results"][0]
    if change == "prompt":
        result["probe_identity"]["retrieval_requests"][0]["query"] = "different task"
        result["probe_identity"]["session_task"] = "different task"
    elif change == "budget":
        result["probe_identity"]["retrieval_requests"][0]["budget"] = 16000
    elif change == "fixture":
        result["baseline_commit"] = "different-fixture-commit"
    elif change == "targets":
        result["natural_prompt_retrieval"]["expected_target_files"] = ["other.py"]
    else:
        result["language"] = "typescript"
    report = compare_reports(baseline, candidate)
    assert not report["comparison_valid"]
    assert report["paired_results"][0]["invalid_reasons"]
    assert all(
        item["candidate_minus_baseline"] is None
        for item in report["paired_results"][0]["measurements"].values()
    )
    assert report["aggregates"]["target_file_coverage"]["candidate_all_observed"]["count"] == 1


@pytest.mark.parametrize("missing", ["task", "settings", "task_id", "duplicate"])
def test_missing_or_ambiguous_identity_is_invalid(missing):
    baseline = _report(_result())
    candidate = copy.deepcopy(baseline)
    if missing == "task":
        candidate["results"] = []
    elif missing == "settings":
        del candidate["results"][0]["probe_identity"]
    elif missing == "task_id":
        del candidate["results"][0]["task_id"]
    else:
        candidate["results"].append(copy.deepcopy(candidate["results"][0]))
    report = compare_reports(baseline, candidate)
    assert not report["comparison_valid"]
    assert report["summary"]["comparable_pairs"] == 0
    assert report["baseline_observations"] == baseline
    assert report["candidate_observations"] == candidate


def test_regressions_and_failures_are_retained_despite_other_improvements():
    old = _result()
    new = copy.deepcopy(old)
    old["natural_prompt_retrieval"]["target_file_coverage_fraction"] = 0
    new["natural_prompt_retrieval"]["expected_declaration_visible_fraction"] = 0
    new["local_server_overhead"]["sampled_peak_rss_bytes"] = 2048
    new["mcp_transport_wall_seconds"] = 2
    new["status"] = "failed"
    new["error"] = {"type": "FreshnessError", "message": "stale source evidence"}
    report = compare_reports(_report(old), _report(new))
    assert report["comparison_valid"]
    regressions = {entry["metric"] for entry in report["all_regressions"]}
    assert regressions == {
        "declaration_visible_coverage",
        "server_sampled_peak_rss_bytes",
        "component_status",
    }
    assert (
        report["paired_results"][0]["measurements"]["target_file_coverage"][
            "candidate_minus_baseline"
        ]
        == 1
    )
    assert report["candidate_observations"]["results"][0]["error"] == new["error"]
    markdown = render_markdown(report)
    assert "stale source evidence" in markdown
    assert "server_sampled_peak_rss_bytes" in markdown
    assert "not live Codex A/B runs" in markdown


def test_missing_measurements_remain_null_and_have_no_false_regression():
    old, new = _result(), _result()
    del new["local_server_overhead"]
    new["index"]["wall_seconds"] = float("nan")
    report = compare_reports(_report(old), _report(new))
    cpu = report["aggregates"]["server_sampled_cpu_seconds"]
    assert cpu["baseline_all_observed"]["count"] == 1
    assert cpu["candidate_all_observed"] == {
        "count": 0,
        "missing": 1,
        "mean": None,
        "median": None,
        "min": None,
        "max": None,
    }
    assert cpu["paired_candidate_minus_baseline"]["mean"] is None
    assert report["paired_results"][0]["measurements"]["index_wall_seconds"]["candidate"] is None
    assert not report["all_regressions"]
    assert all(value is None for value in report["unavailable"].values())
    assert "unavailable" in render_markdown(report)


def test_actual_sdk_arguments_override_unverified_supplied_settings(tmp_path):
    old, new = _result(), _result()
    for name, arguments in (
        ("start_session", {"task": "actual prompt"}),
        ("get_context", {"query": "actual prompt", "level": 2, "budget": 8000}),
    ):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps({"tool": name, "arguments": arguments}))
        for result in (old, new):
            result.setdefault("mcp_calls", []).append(
                {"name": name, "artifact": str(path), "wall_seconds": 0.1}
            )
    new["probe_identity"]["retrieval_requests"][0]["budget"] = 9999
    report = compare_reports(_report(old), _report(new), artifact_base=tmp_path)
    assert report["comparison_valid"]
    identity = report["paired_results"][0]["candidate_identity"]
    assert identity["settings_evidence"] == "retained_actual_sdk_arguments"
    assert identity["retrieval_requests"][0]["budget"] == 8000
    assert identity["session_task"] == "actual prompt"


@pytest.mark.parametrize("symlink", [False, True])
def test_artifact_pointers_outside_declared_root_cannot_override_settings(tmp_path, symlink):
    inside = tmp_path / "allowed"
    inside.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text(
        json.dumps({"arguments": {"query": "untrusted", "level": 2, "budget": 1234}})
    )
    pointer = outside
    if symlink:
        pointer = inside / "escape.json"
        pointer.symlink_to(outside)
    old, new = _result(), _result()
    for result in (old, new):
        result["mcp_calls"] = [{"name": "get_context", "artifact": str(pointer)}]
    new["probe_identity"]["retrieval_requests"][0]["budget"] = 9999
    report = compare_reports(_report(old), _report(new), artifact_base=inside)
    assert not report["comparison_valid"]
    assert report["paired_results"][0]["candidate_identity"]["settings_evidence"] == (
        "explicit_harness_identity"
    )


def test_source_version_is_never_inferred_from_current_checkout():
    baseline, candidate = _report(_result()), _report(_result())
    report = compare_reports(
        baseline,
        candidate,
        baseline_provenance={"attestation": "reconstructed_from_git", "git_head": "old"},
        candidate_provenance={
            "attestation": "captured_source_state_before_probe",
            "git_head": "new",
        },
    )
    assert any("reconstructed" in warning for warning in report["warnings"])
    assert report["provenance"]["baseline"]["git_head"] == "old"
    assert report["baseline_observations"]["summary"] == baseline["summary"]
    report["baseline_observations"]["results"][0]["status"] = "mutated copy"
    assert baseline["results"][0]["status"] == "passed"


def test_changed_measurement_code_invalidates_deltas_without_hiding_values():
    report = compare_reports(
        _report(_result()),
        _report(_result()),
        baseline_provenance={"measurement_files": {"benchmarks/probe.py": "old"}},
        candidate_provenance={"measurement_files": {"benchmarks/probe.py": "changed"}},
    )
    assert not report["comparison_valid"]
    assert "measurement_source_files_changed" in report["errors"]
    assert report["aggregates"]["index_wall_seconds"]["baseline_all_observed"]["mean"] == 1
    assert (
        report["aggregates"]["index_wall_seconds"]["paired_candidate_minus_baseline"]["mean"]
        is None
    )
