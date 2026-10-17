"""Live context reporting must distinguish visible evidence from unavailable claims."""

from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
analysis = import_module("benchmarks.live_context_analysis")

TASK = {
    "id": "py-case",
    "language": "python",
    "target_files": ["atlas/cache.py"],
    "expected_symbols": ["atlas.cache.Cache.get"],
}


def context(*, snippet: str = "    def get(self):\n        return 'é'\n") -> dict:
    return {
        "retrieval_id": "retrieval-one",
        "level": 2,
        "budget": 4000,
        "estimated_tokens": 700,
        "items": [{"path": "atlas/cache.py", "symbol": "Cache.get", "snippet": snippet}],
        "truncated": False,
        "warnings": [],
        "passport": {"status": "Sufficient", "source_freshness": "Current"},
    }


def event(payload: dict | None, *, tool: str = "get_context", identifier: str = "i-1") -> dict:
    return {
        "type": "item.completed",
        "item": {
            "id": identifier,
            "type": "mcp_tool_call",
            "server": "memglide",
            "tool": tool,
            "arguments": {"query": "cache", "level": 2, "budget": 4000},
            "status": "completed",
            "result": {
                "structured_content": payload,
                "content": [{"type": "text", "text": json.dumps(payload)}],
            }
            if payload is not None
            else None,
        },
    }


def jsonl(*events: dict) -> str:
    return "\n".join(json.dumps(value) for value in events)


def terminal() -> dict:
    return {
        "type": "turn.completed",
        "usage": {"input_tokens": 10, "cached_input_tokens": 0, "output_tokens": 5},
    }


def test_native_response_coverage_bytes_and_server_assertions() -> None:
    payload = context()
    result = analysis.analyze_context_calls(jsonl(event(payload), terminal()), TASK)
    row = result["calls"][0]
    assert row["response_available"] is True
    assert row["returned_snippet_utf8_bytes"] == len(payload["items"][0]["snippet"].encode())
    assert row["server_estimated_planning_tokens"] == 700
    assert row["coverage_proxy"]["expected_symbol_coverage_fraction"] == 1
    assert result["union_declared_target_file_coverage_fraction"] == 1
    assert result["union_declared_declaration_visible_fraction"] == 1
    assert row["server_reported_source_freshness"] == "Current"
    assert row["independently_verified_live_source_freshness"] is None
    assert "semantic" in row["coverage_proxy"]["scope"]


def test_repeated_lifecycle_updates_do_not_count_same_call_twice() -> None:
    completed = event(context())
    started = {
        "type": "item.started",
        "item": {**completed["item"], "status": "in_progress", "result": None},
    }
    result = analysis.analyze_context_calls(jsonl(started, completed, terminal()), TASK)
    assert result["observed_context_tool_call_count"] == 1
    assert result["observed_context_response_count"] == 1


@pytest.mark.parametrize("mode", ["failed", "incomplete", "omitted-result"])
def test_failures_and_omitted_results_keep_unavailable_fields(mode: str) -> None:
    value = event(None)
    if mode == "failed":
        value["item"].update(status="failed", error={"message": "requires approval"})
    elif mode == "incomplete":
        value["type"] = "item.started"
        value["item"]["status"] = "in_progress"
    result = analysis.analyze_context_calls(jsonl(value, terminal()), TASK)
    assert result["unavailable_context_tool_response_count"] == 1
    assert result["union_declared_target_file_coverage_fraction"] is None
    row = result["calls"][0]
    assert row["returned_item_count"] is None
    assert row["server_estimated_planning_tokens"] is None
    assert row["unavailable_reason"]


def test_conflicting_structured_and_text_results_fail_closed() -> None:
    value = event(context())
    value["item"]["result"]["content"][0]["text"] = json.dumps({**context(), "budget": 9000})
    result = analysis.analyze_context_calls(jsonl(value, terminal()), TASK)
    assert result["calls"][0]["response_available"] is False
    assert "disagree" in result["calls"][0]["unavailable_reason"]


def test_text_only_results_and_empty_context_are_measurable() -> None:
    payload = {**context(), "items": []}
    value = event(payload)
    value["item"]["result"]["structured_content"] = None
    result = analysis.analyze_context_calls(jsonl(value, terminal()), TASK)
    assert result["observed_context_response_count"] == 1
    assert result["calls"][0]["returned_item_count"] == 0
    assert result["calls"][0]["returned_snippet_utf8_bytes"] == 0
    assert result["union_declared_target_file_coverage_fraction"] == 0


def test_passport_only_call_is_not_mistaken_for_context() -> None:
    value = event({"status": "Stale", "source_freshness": "Stale"}, tool="get_context_passport")
    result = analysis.analyze_context_calls(jsonl(value, terminal()), TASK)
    assert result["observed_context_response_count"] == 0
    assert result["calls"][0]["response_available"] is True
    assert result["calls"][0]["server_reported_passport_status"] == "Stale"
    assert result["calls"][0]["returned_files"] is None


def test_no_context_call_or_agent_self_report_does_not_invent_measurements() -> None:
    text = jsonl(
        {
            "type": "item.completed",
            "item": {"type": "agent_message", "text": json.dumps(context())},
        },
        terminal(),
    )
    result = analysis.analyze_context_calls(text, TASK)
    assert result["calls"] == []
    assert result["union_returned_files"] is None


def test_truncated_stream_preserves_observed_response_and_parse_failure() -> None:
    result = analysis.analyze_context_calls(jsonl(event(context())) + "\nbad-json\n", TASK)
    assert result["observed_context_response_count"] == 1
    assert result["event_stream_complete"] is False
    assert len(result["parse_errors"]) == 1


def test_malformed_items_not_counted_as_zero_coverage() -> None:
    result = analysis.analyze_context_calls(
        jsonl(event({**context(), "items": [{"path": None}]})), TASK
    )
    assert result["observed_context_response_count"] == 0
    assert result["calls"][0]["coverage_proxy"] is None
    assert result["union_declared_target_file_coverage_fraction"] is None


def test_declared_symbol_must_be_in_declared_file() -> None:
    payload = context()
    payload["items"][0]["path"] = "atlas/other.py"
    result = analysis.analyze_context_calls(jsonl(event(payload), terminal()), TASK)
    assert result["union_declared_target_file_coverage_fraction"] == 0
    assert result["union_declared_declaration_visible_fraction"] == 0


def test_experiment_keeps_both_arms_and_unrun_rows(tmp_path: Path) -> None:
    (tmp_path / "plan.json").write_text(json.dumps({"tasks": [TASK]}))
    artifact = tmp_path / "b-run"
    artifact.mkdir()
    (artifact / "events.jsonl").write_text(jsonl(event(context()), terminal()))
    (tmp_path / "runs.json").write_text(
        json.dumps(
            [
                {"run_id": "a", "task_id": "py-case", "configuration": "A", "attempted": False},
                {
                    "run_id": "b",
                    "task_id": "py-case",
                    "configuration": "B",
                    "attempted": True,
                    "artifacts": str(artifact),
                },
            ]
        )
    )
    report = analysis.analyze_experiment(tmp_path)
    assert len(report["runs"]) == 2
    assert report["runs"][0]["union_returned_files"] is None
    assert report["summary"]["runs_with_observed_context_response"] == 1
    assert report["summary"]["server_reported_passport_status_counts"] == {"Sufficient": 1}
    assert "unavailable" in analysis.render_markdown(report)
