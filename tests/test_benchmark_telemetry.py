"""Benchmark evidence must come from CLI events and external grading, not claims."""

from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

# Benchmarks are repository tooling, deliberately outside the installable wheel.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
reporting = import_module("benchmarks.reporting")
telemetry = import_module("benchmarks.telemetry")
build_report, render_markdown, write_report = (
    reporting.build_report,
    reporting.render_markdown,
    reporting.write_report,
)
observed_read_paths, parse_codex_jsonl = telemetry.observed_read_paths, telemetry.parse_codex_jsonl


def jsonl(*events: dict) -> str:
    return "\n".join(json.dumps(event) for event in events)


def completed(input_tokens: int = 100, cached: int = 40, output: int = 10) -> dict:
    return {
        "type": "turn.completed",
        "usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached,
            "output_tokens": output,
        },
    }


def mcp_event(lifecycle: str, status: str, identifier: str = "item_2") -> dict:
    event = {
        "type": lifecycle,
        "item": {
            "id": identifier,
            "type": "mcp_tool_call",
            "server": "memglide",
            "tool": "get_context",
            "arguments": {"query": "find parse function"},
            "status": status,
        },
    }
    if status == "completed":
        event["item"]["result"] = {
            "content": [{"type": "text", "text": '{"items": [], "retrieval_id": "r-1"}'}],
            "structured_content": {"items": [], "retrieval_id": "r-1"},
        }
    return event


def test_usage_and_mcp_lifecycle_are_observed_once(tmp_path: Path) -> None:
    log = tmp_path / "codex.jsonl"
    log.write_text(
        jsonl(
            {"type": "thread.started", "thread_id": "fixture-thread"},
            {"type": "turn.started"},
            mcp_event("item.started", "in_progress"),
            mcp_event("item.updated", "in_progress"),
            mcp_event("item.completed", "completed"),
            {
                "type": "item.completed",
                "item": {
                    "id": "message",
                    "type": "agent_message",
                    "text": json.dumps(
                        {
                            "input_tokens": 999999,
                            "actual_cost_usd": 123,
                            "success": True,
                        }
                    ),
                },
            },
            completed(),
            completed(20, 5, 3),
        )
    )
    result = parse_codex_jsonl(log)
    assert result["usage"] == {
        "input_tokens": 120,
        "cached_input_tokens": 45,
        "output_tokens": 13,
    }
    assert result["completed_turns"] == 2
    assert result["mcp_call_count"] == 1
    assert result["memglide_mcp_call_count"] == 1
    assert result["mcp_calls"][0]["completed"] is True
    assert result["memglide_successful_get_context_count"] == 1
    assert result["model_calls"] is None
    assert result["actual_cost_usd"] is None


def test_failed_and_incomplete_runs_never_invent_missing_usage() -> None:
    result = parse_codex_jsonl(
        jsonl(
            {"type": "thread.started", "thread_id": "fixture-thread"},
            mcp_event("item.started", "in_progress"),
            {"type": "turn.failed", "error": {"message": "Provider authentication rejected"}},
        )
    )
    assert result["failed_turns"] == 1
    assert result["usage"] == {
        key: None for key in ("input_tokens", "cached_input_tokens", "output_tokens")
    }
    assert result["mcp_calls"][0]["completed"] is False
    assert result["mcp_counts_complete"] is False
    assert result["errors"][0]["error"]["message"] == "Provider authentication rejected"
    assert result["stream_terminal"] is True
    empty = parse_codex_jsonl("")
    assert empty["mcp_call_count"] is None
    assert empty["repeated_file_reads"] is None
    assert empty["completed_turns"] == 0
    assert empty["model_calls"] is None


def test_partial_usage_is_withheld_and_invalid_lines_stay_visible() -> None:
    partial_log = jsonl(
        completed(),
        {"type": "turn.completed", "usage": {"input_tokens": 20, "output_tokens": 2}},
    )
    result = parse_codex_jsonl(partial_log)
    assert result["usage"]["input_tokens"] == 120
    assert result["usage"]["cached_input_tokens"] is None
    assert "partial totals withheld" in result["usage_unavailable_reasons"]["cached_input_tokens"]
    malformed = parse_codex_jsonl(partial_log + "\nnot-json\n[]\n")
    assert len(malformed["parse_errors"]) == 2
    assert malformed["usage"]["input_tokens"] is None
    assert malformed["observed_completed_turn_usage"]["input_tokens"] == 120
    assert malformed["usage_coverage_complete"] is False


def test_usage_from_completed_turn_does_not_hide_an_unbilled_failed_turn() -> None:
    result = parse_codex_jsonl(
        jsonl(
            completed(),
            {"type": "turn.started"},
            {"type": "turn.failed", "error": {"message": "Connection interrupted"}},
        )
    )
    assert result["usage"]["input_tokens"] is None
    assert result["observed_completed_turn_usage"]["input_tokens"] == 100
    assert result["usage_coverage_complete"] is False


def test_successful_literal_file_reads_only_and_lifecycle_deduplication() -> None:
    def command(identifier: str, text: str, exit_code: int = 0) -> dict:
        return {
            "type": "item.completed",
            "item": {
                "id": identifier,
                "type": "command_execution",
                "command": text,
                "exit_code": exit_code,
                "status": "completed",
            },
        }

    event = command("read-1", "sed -n '1,40p' src/parser.py")
    result = parse_codex_jsonl(
        jsonl(
            event,
            event,
            command("read-2", "cat src/parser.py"),
            command("read-3", "rg -n 'def parse' src/parser.py"),
            command("search", "rg --files src"),
            command("script", "python -c 'print(open(\"src/parser.py\").read())'"),
            command("failed", "cat absent.py", 1),
            command("glob", "cat src/*.py"),
            completed(),
        )
    )
    assert result["observed_read_command_paths"] == ["src/parser.py"] * 3
    assert result["repeated_file_reads"] is None
    assert result["observed_file_read_commands"] == 3
    assert result["observed_repeated_read_commands"] == 2
    assert result["file_reads_complete"] is False
    assert "command-intent proxy" in result["file_read_method"]
    assert observed_read_paths('bash -lc "cd src && cat parser.py"') == ["src/parser.py"]
    assert observed_read_paths("cat data.py | head") == []


def run(
    task: str,
    config: str,
    success: bool | None,
    cost: float | None = None,
    invokes_memglide: bool = False,
) -> dict:
    events = [mcp_event("item.completed", "completed")] if invokes_memglide else []
    return {
        "task_id": task,
        "configuration": config,
        "repeat": 1,
        "order": 1 if config == "A" else 2,
        "starting_commit": "a" * 40,
        "prompt_sha256": "b" * 64,
        "status": "completed",
        "attempted": True,
        "grader": {"success": success},
        "actual_cost_usd": cost,
        "computed_cost_usd": None,
        "wall_time_seconds": 1.5,
        "telemetry": parse_codex_jsonl(jsonl(*events, completed())),
        "errors": [] if success else ["Held-out tests failed"],
    }


def test_cost_per_success_includes_failed_runs_and_cannot_mix_computed_cost() -> None:
    rows = [run("task-1", "A", True, 0.1), run("task-2", "A", False, 0.2)]
    report = build_report(rows, [{"id": "task-1"}, {"id": "task-2"}], {})
    aggregate = report["aggregates"]["A"]
    assert aggregate["successful_task_completion_rate"] == 0.5
    assert aggregate["actual_cost_per_successful_task_usd"]["value"] == pytest.approx(0.3)
    assert aggregate["computed_cost_per_successful_task_usd"]["value"] is None
    rows[1]["actual_cost_usd"] = None
    rows[1]["computed_cost_usd"] = 0.2
    aggregate = build_report(rows, [], {})["aggregates"]["A"]
    assert aggregate["actual_cost_per_successful_task_usd"]["value"] is None
    assert aggregate["metrics"]["actual_cost_usd"]["known_total"] == 0.1
    assert aggregate["metrics"]["actual_cost_usd"]["total"] is None
    assert aggregate["metrics"]["actual_cost_usd"]["missing"] == 1


def test_invalid_b_treatment_is_retained_and_excluded_from_verified_pairs() -> None:
    rows = [
        run("task-1", "A", True),
        run("task-1", "B", False),
        run("task-2", "A", False),
        run("task-2", "B", True, invokes_memglide=True),
    ]
    report = build_report(rows, [{"id": "task-1"}, {"id": "task-2"}], {})
    assert len(report["runs"]) == 4
    assert report["aggregates"]["B"]["invalid_treatment_runs"] == 1
    assert report["aggregates"]["B"]["successful_task_completion_rate"] == 0.5
    assert report["paired_comparisons"]["valid_pair_count"] == 1
    assert report["paired_comparisons"]["pairs"][0]["A_success"] is False
    assert report["paired_comparisons"]["pairs"][0]["B_success"] is True
    assert report["aggregates"]["A"]["metrics"]["model_calls"]["mean"] is None
    markdown = render_markdown(report)
    assert "task-1" in markdown and "Held-out tests failed" in markdown
    assert "unavailable" in markdown


def test_failed_or_nonretrieval_memglide_calls_do_not_verify_b_treatment() -> None:
    failed = mcp_event("item.completed", "failed")
    failed["item"]["error"] = {"message": "No such session"}
    list_projects = mcp_event("item.completed", "completed", "item_3")
    list_projects["item"]["tool"] = "list_projects"
    row = run("task", "B", False)
    row["telemetry"] = parse_codex_jsonl(jsonl(failed, list_projects, completed()))
    report = build_report([row], [], {})
    assert report["runs"][0]["treatment_fidelity"]["valid"] is False
    assert row["telemetry"]["memglide_mcp_call_count"] == 2
    assert row["telemetry"]["memglide_successful_get_context_count"] == 0


def test_tool_error_result_and_missing_result_cannot_be_successful_retrievals() -> None:
    missing = mcp_event("item.completed", "completed")
    del missing["item"]["result"]
    row = run("task", "B", False)
    row["telemetry"] = parse_codex_jsonl(jsonl(missing, completed()))
    assert build_report([row], [], {})["runs"][0]["treatment_fidelity"]["valid"] is None
    explicit_error = mcp_event("item.completed", "completed")
    explicit_error["item"]["result"]["isError"] = True
    row["telemetry"] = parse_codex_jsonl(jsonl(explicit_error, completed()))
    assert build_report([row], [], {})["runs"][0]["treatment_fidelity"]["valid"] is False


def test_incomplete_stream_counts_are_observed_lower_bounds_not_totals() -> None:
    row = run("task", "B", False)
    row["telemetry"] = parse_codex_jsonl(
        jsonl(
            mcp_event("item.completed", "completed"),
            {"type": "turn.failed", "error": {"message": "Disconnected"}},
        )
    )
    report = build_report([row], [], {})
    metrics = report["runs"][0]["metrics"]
    assert metrics["mcp_calls"] is None
    assert metrics["observed_mcp_calls"] == 1
    assert report["runs"][0]["treatment_fidelity"]["valid"] is True
    assert metrics["input_tokens"] is None


def test_context_coverage_proxy_is_not_relabelled_semantic_completeness() -> None:
    row = run("task", "B", True, invokes_memglide=True)
    row["context_probe"] = {
        "target_path_coverage_fraction": 0.75,
        "expected_symbol_coverage_fraction": 0.5,
    }
    metrics = build_report([row], [], {})["runs"][0]["metrics"]
    assert metrics["probe_target_path_coverage_fraction"] == 0.75
    assert metrics["probe_expected_symbol_coverage_fraction"] == 0.5
    assert metrics["retrieval_completeness"] is None
    assert metrics["context_freshness"] is None


def test_blocked_tasks_generate_rows_with_nulls_instead_of_fake_zeroes(tmp_path: Path) -> None:
    tasks = [{"id": f"task-{index}", "language": "python"} for index in range(24)]
    report = build_report([], tasks, {"repeats": 2, "blockers": ["Provider unavailable"]})
    assert len(report["runs"]) == 96
    assert report["aggregates"]["A"]["attempted_runs"] == 0
    assert report["aggregates"]["A"]["successful_task_completion_rate"] is None
    assert report["aggregates"]["A"]["metrics"]["input_tokens"]["planned_missing"] == 48
    assert report["aggregates"]["A"]["metrics"]["input_tokens"]["attempted_missing"] == 0
    assert report["runs"][0]["metrics"]["input_tokens"] is None
    assert report["runs"][0]["treatment_fidelity"]["valid"] is None
    assert report["conclusions"]["savings_claim_supported"] is False
    write_report(report, tmp_path / "report.json", tmp_path / "report.md")
    saved = json.loads((tmp_path / "report.json").read_text())
    assert saved["aggregates"]["B"]["metrics"]["mcp_calls"]["total"] is None
    assert "task-23" in (tmp_path / "report.md").read_text()


def test_ungrounded_agent_success_does_not_become_grader_success() -> None:
    row = run("task", "A", None)
    row["structured_response"] = {"success": True}
    row["status"] = "execution_failed"
    report = build_report([row], [], {})
    assert report["aggregates"]["A"]["successful_runs"] == 0
    assert report["aggregates"]["A"]["ungraded_runs"] == 1
    assert report["aggregates"]["A"]["successful_task_completion_rate"] == 0


@pytest.mark.parametrize("field", ["starting_commit", "prompt_sha256"])
@pytest.mark.parametrize("mismatch", [False, True])
def test_unverified_or_unequal_pair_identity_withholds_deltas(field: str, mismatch: bool) -> None:
    rows = [run("task", "A", True), run("task", "B", False, invokes_memglide=True)]
    if mismatch:
        rows[1][field] = "different"
    else:
        del rows[1][field]
    report = build_report(rows, [], {"source_unchanged_during_experiment": True})
    paired = report["paired_comparisons"]
    assert paired["valid_pair_count"] == 0
    assert field in paired["excluded_pairs"][0]["reason"]
    assert paired["B_minus_A"]["input_tokens"]["mean"] is None
    assert report["aggregates"]["B"]["attempted_runs"] == 1
    assert report["aggregates"]["B"]["failed_grades"] == 1
    assert report["runs"][1]["metrics"]["input_tokens"] == 100


def test_explicit_runtime_source_change_invalidates_all_pairs_but_retains_observations() -> None:
    rows = [run("task", "A", True, 0.1), run("task", "B", False, 0.2, invokes_memglide=True)]
    report = build_report(rows, [], {"source_unchanged_during_experiment": False})
    paired = report["paired_comparisons"]
    assert paired["valid_pair_count"] == 0
    assert "source changed" in paired["excluded_pairs"][0]["reason"]
    assert report["aggregates"]["B"]["metrics"]["actual_cost_usd"]["total"] == 0.2
    assert report["aggregates"]["B"]["failed_grades"] == 1
    assert "source changed" in render_markdown(report)


def test_matching_input_identity_is_reported_and_missing_source_attestation_stays_unknown() -> None:
    rows = [run("task", "A", True), run("task", "B", True, invokes_memglide=True)]
    report = build_report(rows, [], {})
    paired = report["paired_comparisons"]
    assert paired["valid_pair_count"] == 1
    assert paired["pairs"][0]["verified_input_identity"] == {
        "starting_commit": "a" * 40,
        "prompt_sha256": "b" * 64,
    }
    assert paired["source_unchanged_during_experiment"] is None


def test_equal_placeholder_strings_do_not_establish_input_identity() -> None:
    rows = [run("task", "A", True), run("task", "B", True, invokes_memglide=True)]
    for row in rows:
        row["starting_commit"] = "unknown"
        row["prompt_sha256"] = "unknown"
    report = build_report(rows, [], {})
    assert report["paired_comparisons"]["valid_pair_count"] == 0
    assert "Invalid starting_commit" in report["paired_comparisons"]["excluded_pairs"][0]["reason"]
