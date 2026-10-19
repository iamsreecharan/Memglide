"""Money arithmetic and missing-usage handling; no model requests or billing."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import estimate_cost as cost  # noqa: E402


@pytest.fixture
def pricing():
    return {
        "model": "exact-model",
        "service_tier": "standard",
        "context_threshold_tokens": 272000,
        "per_million_usd": {
            "uncached_input": 2,
            "cached_input": 0.1,
            "cache_write_input": 2.5,
            "output": 10,
        },
    }


def usage(**changes):
    return {
        "input_tokens": 100,
        "cached_input_tokens": 40,
        "cache_write_input_tokens": 0,
        "output_tokens": 10,
        "reasoning_output_tokens": 5,
        **changes,
    }


def stream(*rows):
    events = [{"type": "thread.started", "thread_id": "fake-thread"}]
    for row in rows or (usage(),):
        events += [{"type": "turn.started"}, {"type": "turn.completed", "usage": row}]
    return "\n".join(json.dumps(event) for event in events) + "\n"


def test_cached_input_is_subset_and_reasoning_is_not_billed_twice(pricing):
    result = cost.price_usage(cost.parse_native_usage(stream()), pricing)
    assert result["actual_billed_cost_usd"] is None
    assert result["native_reported_price_equivalent_usd"] == pytest.approx(0.000224)
    assert result["possible_write_price_lower_usd"] == pytest.approx(0.000224)
    assert result["possible_write_price_upper_usd"] == pytest.approx(0.000254)
    other = cost.price_usage(
        cost.parse_native_usage(stream(usage(reasoning_output_tokens=0))), pricing
    )
    assert other == result


def test_cache_writes_replace_ordinary_input_and_are_not_additive(pricing):
    result = cost.price_usage(
        cost.parse_native_usage(stream(usage(cache_write_input_tokens=60))), pricing
    )
    # Official shape I100/C40/W60/O10/R5: ordinary input is zero.
    assert result["native_reported_price_equivalent_usd"] == pytest.approx(0.000254)
    assert result["possible_write_price_lower_usd"] == result["possible_write_price_upper_usd"]


def test_multiple_thread_cumulative_totals_are_not_double_charged(pricing):
    final = usage(
        input_tokens=180,
        cached_input_tokens=70,
        cache_write_input_tokens=20,
        output_tokens=18,
        reasoning_output_tokens=7,
    )
    parsed = cost.parse_native_usage(stream(usage(), final))
    assert parsed["coverage_complete"] is False
    assert parsed["completed_turns"] == 2
    assert parsed["observed_completed_turn_usage"] == final
    assert parsed["usage"] == dict.fromkeys(cost.USAGE_KEYS)
    assert cost.price_usage(parsed, pricing)["native_reported_price_equivalent_usd"] is None


@pytest.mark.parametrize(
    "changes",
    [
        {"input_tokens": -1},
        {"input_tokens": True},
        {"cached_input_tokens": None},
        {"output_tokens": 1.5},
        {"cached_input_tokens": 101},
        {"cache_write_input_tokens": 61},
        {"cache_write_input_tokens": None},
        {"cache_write_input_tokens": -1},
        {"reasoning_output_tokens": 11},
        {"reasoning_output_tokens": None},
        {"reasoning_output_tokens": False},
    ],
)
def test_inconsistent_or_invalid_usage_never_becomes_estimated_zero(pricing, changes):
    parsed = cost.parse_native_usage(stream(usage(**changes)))
    assert parsed["coverage_complete"] is False
    result = cost.price_usage(parsed, pricing)
    assert result["native_reported_price_equivalent_usd"] is None
    assert result["possible_write_price_lower_usd"] is None
    assert result["possible_write_price_upper_usd"] is None


def test_missing_cache_writes_are_scenarios_without_a_point(pricing):
    row = usage()
    del row["cache_write_input_tokens"]
    del row["reasoning_output_tokens"]
    parsed = cost.parse_native_usage(stream(row))
    assert parsed["coverage_complete"] is True
    assert parsed["usage"]["cache_write_input_tokens"] is None
    result = cost.price_usage(parsed, pricing)
    assert result["native_reported_price_equivalent_usd"] is None
    assert result["possible_write_price_lower_usd"] == pytest.approx(0.000224)
    assert result["possible_write_price_upper_usd"] == pytest.approx(0.000254)


@pytest.mark.parametrize("missing", ["input_tokens", "cached_input_tokens", "output_tokens"])
def test_missing_required_usage_is_unknown(pricing, missing):
    row = usage()
    del row[missing]
    parsed = cost.parse_native_usage(stream(row))
    assert parsed["coverage_complete"] is False
    assert cost.price_usage(parsed, pricing)["native_reported_price_equivalent_usd"] is None


@pytest.mark.parametrize(
    "transform",
    [
        lambda s: "",
        lambda s: s + "{broken\n",
        lambda s: "\n".join(s.splitlines()[1:]),
        lambda s: s.replace('{"type": "turn.started"}\n', ""),
        lambda s: s + s.splitlines()[-1] + "\n",
        lambda s: s + '{"type":"turn.started"}\n',
        lambda s: s + '{"type":"item.completed","item":{}}\n',
        lambda s: s + '{"type":"unknown"}\n',
        lambda s: s + '{"type":"error","message":"simulated"}\n',
        lambda s: s + '{"type":"turn.started"}\n{"type":"turn.failed"}\n',
        lambda s: s.replace('"type": "turn.completed"', '"type": "turn.failed"'),
    ],
)
def test_partial_duplicate_and_failed_streams_never_have_complete_cost(pricing, transform):
    parsed = cost.parse_native_usage(transform(stream()))
    assert parsed["coverage_complete"] is False
    result = cost.price_usage(parsed, pricing)
    assert result["native_reported_price_equivalent_usd"] is None


def test_completed_usage_before_a_failure_is_retained_but_not_full_cost(pricing):
    parsed = cost.parse_native_usage(stream() + '{"type":"turn.started"}\n{"type":"turn.failed"}\n')
    assert parsed["observed_completed_turn_usage"]["input_tokens"] == 100
    assert parsed["usage"]["input_tokens"] is None
    assert cost.price_usage(parsed, pricing)["native_reported_price_equivalent_usd"] is None


def test_duplicate_json_fields_do_not_silently_override_invalid_usage():
    text = stream().replace('"input_tokens": 100', '"input_tokens": -1, "input_tokens": 100')
    parsed = cost.parse_native_usage(text)
    assert parsed["coverage_complete"] is False
    assert any("invalid JSON" in item for item in parsed["errors"])


def test_long_context_cannot_be_charged_at_short_rates(pricing):
    at_limit = cost.parse_native_usage(stream(usage(input_tokens=272000)))
    over = cost.parse_native_usage(stream(usage(input_tokens=272001)))
    assert cost.price_usage(at_limit, pricing)["native_reported_price_equivalent_usd"] is not None
    result = cost.price_usage(over, pricing)
    assert result["native_reported_price_equivalent_usd"] is None
    assert result["possible_write_price_upper_usd"] is None
    assert "per-request" in result["reason"]


def raw_row(tmp_path, identifier, *, arm="A", success=True, task="task", data=None):
    artifacts = tmp_path / identifier
    artifacts.mkdir()
    (artifacts / "events.jsonl").write_text(stream(data or usage()))
    return {
        "run_id": identifier,
        "task_id": task,
        "repeat": 1,
        "configuration": arm,
        "artifacts": str(artifacts),
        "native_command": ["/installed/codex", "exec", "--ephemeral", "-"],
        "attempted": True,
        "status": "completed" if success else "failed",
        "language": "python",
        "grader": {"success": success, "test_count": 2},
        "treatment_valid": True,
        "preload_treatment_fidelity": {"valid": True},
        "native_execution_validity": {"valid": True},
        "telemetry": {"usage": {key: (data or usage())[key] for key in cost.BASE_KEYS}},
        "metrics": {"end_to_end_wall_seconds": 2, "process_tree_peak_rss_bytes": 512},
    }


def report(rows):
    return {
        "metadata": {
            "model": "exact-model",
            "frozen_manifest": {"settings": {"requested_service_tier": "default"}},
        },
        "runs": rows,
    }


@pytest.mark.parametrize(
    "command",
    [
        None,
        [],
        ["codex", "exec", "resume", "thread", "-"],
        ["codex", "exec", "-"],
        ["codex", "exec", "--ephemeral", "resume", "thread", "-"],
    ],
)
def test_resumed_or_unproven_thread_usage_never_becomes_incremental_cost(
    tmp_path, pricing, command
):
    row = raw_row(tmp_path, "resumed")
    row["native_command"] = command
    assessment = cost.assess(report([row]), pricing)
    assert assessment["runs"][0]["cost"]["native_reported_price_equivalent_usd"] is None
    assert (
        assessment["configurations"]["A"]["cost_per_successful_task_usd"][
            "native_reported_price_equivalent_usd"
        ]
        is None
    )


def test_unknown_outcome_cannot_price_a_complete_but_unsealed_stream(tmp_path, pricing):
    row = raw_row(tmp_path, "unknown", success=False)
    row["execution_outcome_unknown"] = True
    assessment = cost.assess(report([row]), pricing)
    assert assessment["runs"][0]["cost"]["native_reported_price_equivalent_usd"] is None


def test_failed_attempts_count_in_numerator_and_successful_assignments_once(tmp_path, pricing):
    rows = [
        raw_row(tmp_path, "failed", success=False),
        raw_row(tmp_path, "success"),
        raw_row(tmp_path, "other-success", task="other"),
    ]
    result = cost.assess(report(rows), pricing)
    a = result["configurations"]["A"]
    assert a["attempts"] == 3 and a["assignments"] == a["successful_assignments"] == 2
    assert a["cost_statistics"]["native_reported_price_equivalent_usd"]["total"] == pytest.approx(
        0.000672
    )
    assert a["cost_per_successful_task_usd"][
        "native_reported_price_equivalent_usd"
    ] == pytest.approx(0.000336)
    assert len(result["failures"]) == 1
    assert a["metrics"]["process_tree_peak_rss_bytes"]["total"] is None


def test_unknown_failed_attempt_makes_whole_cost_per_success_unknown(tmp_path, pricing):
    rows = [raw_row(tmp_path, "failed", success=False), raw_row(tmp_path, "success")]
    (tmp_path / "failed" / "events.jsonl").write_text('{"type":"thread.started","thread_id":"t"}\n')
    rows[0]["telemetry"]["usage"] = dict.fromkeys(cost.BASE_KEYS)
    result = cost.assess(report(rows), pricing)
    a = result["configurations"]["A"]
    assert a["cost_statistics"]["native_reported_price_equivalent_usd"][
        "known_total"
    ] == pytest.approx(0.000224)
    assert a["cost_statistics"]["native_reported_price_equivalent_usd"]["total"] is None
    assert a["cost_per_successful_task_usd"]["native_reported_price_equivalent_usd"] is None


def test_independent_native_usage_must_reconcile_with_primary_report(tmp_path, pricing):
    row = raw_row(tmp_path, "one")
    row["telemetry"]["usage"]["input_tokens"] += 1
    result = cost.assess(report([row]), pricing)
    assert result["runs"][0]["primary_usage_reconciled"] is False
    assert result["runs"][0]["cost"]["native_reported_price_equivalent_usd"] is None


@pytest.mark.parametrize("bad_artifact", ["missing", "invalid-utf8", "symlink"])
def test_invalid_native_artifact_cannot_disappear_from_cost_numerator(
    tmp_path, pricing, bad_artifact
):
    row = raw_row(tmp_path, "one")
    events = tmp_path / "one" / "events.jsonl"
    if bad_artifact == "missing":
        events.unlink()
    elif bad_artifact == "invalid-utf8":
        events.write_bytes(b"\xff")
    else:
        original = tmp_path / "original.jsonl"
        events.rename(original)
        events.symlink_to(original)
    result = cost.assess(report([row]), pricing)
    assert result["configurations"]["A"]["attempts"] == 1
    assert result["runs"][0]["cost"]["native_reported_price_equivalent_usd"] is None


def test_savings_uses_cost_per_success_and_keeps_worst_case_write_range(tmp_path, pricing):
    rows = [raw_row(tmp_path, "a"), raw_row(tmp_path, "b", arm="B", data=usage(input_tokens=90))]
    result = cost.assess(report(rows), pricing, events_root=tmp_path)
    assert result["cost_per_success_saving_percent"][
        "native_reported_price_equivalent_usd"
    ] == pytest.approx(100 * 20 / 224)
    assert result["paired_cost_outcomes"] == {
        "B_cheaper": 1,
        "A_cheaper": 0,
        "equal": 0,
        "unavailable": 0,
    }
    limits = result["write_uncertainty_saving_range"]
    assert limits["lower_saving_percent"] < 0 < limits["upper_saving_percent"]
    assert result["actual_billed_cost_usd"] is None
    assert "not actual bills" in cost.markdown(result)


@pytest.mark.parametrize("change", ["model", "tier", "duplicate-run"])
def test_wrong_pricing_context_or_duplicate_attempts_are_rejected(tmp_path, pricing, change):
    row = raw_row(tmp_path, "one")
    doc = report([row])
    if change == "model":
        pricing["model"] = "different-model"
    elif change == "tier":
        doc["metadata"]["frozen_manifest"]["settings"]["requested_service_tier"] = "priority"
    else:
        doc["runs"].append(copy.deepcopy(row))
    with pytest.raises(ValueError):
        cost.assess(doc, pricing)


@pytest.mark.parametrize("bad", [None, True, -1, "NaN", "Infinity", "nonsense"])
def test_invalid_rates_are_rejected(pricing, bad):
    pricing["per_million_usd"]["output"] = bad
    with pytest.raises(ValueError):
        cost.validate_pricing(pricing)


def test_zero_usage_is_available_and_zero_success_has_no_per_success_cost(tmp_path, pricing):
    data = {key: 0 for key in cost.USAGE_KEYS}
    row = raw_row(tmp_path, "zero", success=False, data=data)
    result = cost.assess(report([row]), pricing)
    a = result["configurations"]["A"]
    assert a["cost_statistics"]["native_reported_price_equivalent_usd"]["total"] == 0
    assert a["cost_per_successful_task_usd"]["native_reported_price_equivalent_usd"] is None
    assert result["cost_per_success_saving_percent"]["native_reported_price_equivalent_usd"] is None


def test_cost_components_and_strata_reconcile_without_pricing_local_cpu(tmp_path, pricing):
    rows = [raw_row(tmp_path, "one"), raw_row(tmp_path, "two", arm="B")]
    rows[0]["selection_stratum"] = rows[1]["selection_stratum"] = "explicit_focus"
    result = cost.assess(report(rows), pricing)
    components = result["configurations"]["A"]["native_reported_cost_components_usd"]
    assert sum(part["total"] for part in components.values()) == pytest.approx(0.000224)
    stratum = result["strata"]["selection_stratum"]["explicit_focus"]
    assert stratum["native_reported_cost_per_success_saving_percent"] == 0
    assert "cpu" not in components


def test_cli_preserves_input_and_refuses_to_overwrite_either_output(tmp_path, pricing, monkeypatch):
    row = raw_row(tmp_path, "one")
    source = tmp_path / "source.json"
    rates = tmp_path / "prices.json"
    source.write_text(json.dumps(report([row])))
    rates.write_text(json.dumps(pricing))
    original = source.read_bytes()
    prefix = tmp_path / "assessment"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "estimate_cost",
            "--report",
            str(source),
            "--pricing",
            str(rates),
            "--output-prefix",
            str(prefix),
        ],
    )
    assert cost.main() == 0
    output = json.loads(prefix.with_suffix(".json").read_text())
    assert output["provenance"]["primary_report_sha256"] == cost.digest(original)
    assert source.read_bytes() == original
    prefix.with_suffix(".json").unlink()
    with pytest.raises(FileExistsError):
        cost.main()
    assert not prefix.with_suffix(".json").exists()
