"""Analyze context actually returned in native Codex JSONL MCP events.

This is a response-content analysis, not a freshness experiment or a model-usage
meter. It deliberately does not read mutable worktrees after the experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from benchmarks.probe import coverage_proxy
from benchmarks.telemetry import parse_codex_jsonl

CONTEXT_TOOLS = {"get_context", "expand_context", "get_context_passport"}
LIMITATIONS = [
    "Declared target-file / exact-symbol / visible-declaration matches are narrow proxies; "
    "they do not establish complete method bodies or semantic retrieval completeness.",
    "Passport status and source_freshness are server assertions, not independently verified "
    "source versions at the instant of a live tool call.",
    "Server estimated_tokens values are planning estimates, not measured model tokens, "
    "invoiced usage, or money saved.",
    "Snippet bytes count returned item strings, including duplicates; canonical response JSON "
    "bytes do not measure transport encoding, model context size, or billed tokens.",
    "Missing/failed/unparsed tool results remain unavailable. A run with no context call is "
    "retained and does not receive invented zero-byte or freshness measurements.",
]


def _result_payload(result: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(result, dict):
        return None, "CLI tool item omitted a result object"
    structured = result.get("structured_content", result.get("structuredContent"))
    candidates = [structured] if isinstance(structured, dict) else []
    for block in result.get("content", []):
        if not isinstance(block, dict) or block.get("type") != "text":
            continue
        try:
            payload = json.loads(block.get("text", ""))
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(payload, dict):
            candidates.append(payload)
    if not candidates:
        return None, "Tool result did not expose a JSON object"
    if any(candidate != candidates[0] for candidate in candidates[1:]):
        return None, "Structured and JSON text tool result objects disagree"
    return candidates[0], None


def _passport_fields(passport: Any) -> dict[str, Any]:
    if not isinstance(passport, dict):
        passport = {}
    return {
        "server_reported_passport_status": passport.get("status"),
        "server_reported_source_freshness": passport.get("source_freshness"),
        "server_reported_missing_context": passport.get("missing_context"),
        "server_reported_recommended_next_retrievals": passport.get("recommended_next_retrievals"),
        "independently_verified_live_source_freshness": None,
    }


def analyze_context_calls(source: str | Path, task: dict[str, Any]) -> dict[str, Any]:
    """Extract completed native MCP results once per item ID; retain every failure."""
    text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    telemetry = parse_codex_jsonl(text)
    calls_by_id = {call["id"]: call for call in telemetry["mcp_calls"]}
    items: dict[str, dict[str, Any]] = {}
    valid_event_index = -1
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            continue
        valid_event_index += 1
        if event.get("type") not in {
            "item.started",
            "item.updated",
            "item.completed",
        }:
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        identifier = str(item.get("id", f"event-without-id-{valid_event_index}"))
        items[identifier] = {**items.get(identifier, {}), **item}

    calls = []
    for identifier, item in items.items():
        if (
            item.get("type") != "mcp_tool_call"
            or str(item.get("server", "")).lower() != "memglide"
            or item.get("tool") not in CONTEXT_TOOLS
        ):
            continue
        native = calls_by_id[identifier]
        row = {
            "id": identifier,
            "tool": item["tool"],
            "arguments": item.get("arguments"),
            "status": native["status"],
            "successful": native["successful"],
            "error": native["error"],
            "response_available": False,
            "unavailable_reason": None,
            "retrieval_id": None,
            "returned_level": None,
            "returned_budget": None,
            "returned_files": None,
            "returned_item_count": None,
            "returned_snippet_utf8_bytes": None,
            "canonical_response_json_bytes": None,
            "server_estimated_planning_tokens": None,
            "truncated": None,
            "warnings": None,
            "coverage_proxy": None,
            **_passport_fields(None),
        }
        if native["successful"] is not True:
            row["unavailable_reason"] = native["success_evidence"]
            calls.append(row)
            continue
        payload, unavailable = _result_payload(item.get("result"))
        if payload is None:
            row["unavailable_reason"] = unavailable
            calls.append(row)
            continue
        row.update(
            response_available=True,
            retrieval_id=payload.get("retrieval_id"),
            canonical_response_json_bytes=len(
                json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ),
        )
        passport = payload if item["tool"] == "get_context_passport" else payload.get("passport")
        row.update(_passport_fields(passport))
        if item["tool"] != "get_context_passport":
            context_items = payload.get("items")
            if not isinstance(context_items, list) or any(
                not isinstance(value, dict)
                or not isinstance(value.get("path"), str)
                or not isinstance(value.get("snippet", ""), str)
                for value in context_items
            ):
                row["response_available"] = False
                row["unavailable_reason"] = "Context response omitted a valid items array"
                calls.append(row)
                continue
            estimate = payload.get("estimated_tokens")
            row.update(
                returned_level=payload.get("level"),
                returned_budget=payload.get("budget"),
                returned_files=sorted({value["path"] for value in context_items}),
                returned_item_count=len(context_items),
                returned_snippet_utf8_bytes=sum(
                    len(value.get("snippet", "").encode("utf-8")) for value in context_items
                ),
                server_estimated_planning_tokens=estimate
                if isinstance(estimate, int) and not isinstance(estimate, bool) and estimate >= 0
                else None,
                truncated=payload.get("truncated"),
                warnings=payload.get("warnings"),
                coverage_proxy=coverage_proxy(
                    task,
                    {
                        **payload,
                        "passport": {"status": None, **passport}
                        if isinstance(passport, dict)
                        else {"status": None},
                    },
                ),
            )
        calls.append(row)

    observed_contexts = [
        call for call in calls if call["coverage_proxy"] is not None and call["response_available"]
    ]
    union_files = sorted({path for call in observed_contexts for path in call["returned_files"]})
    targets = set(task["target_files"])
    declarations = {
        value
        for call in observed_contexts
        for value in call["coverage_proxy"]["visible_expected_declarations"]
    }
    expected_symbols = task["expected_symbols"]
    return {
        "calls": calls,
        "observed_context_tool_call_count": len(calls),
        "observed_context_response_count": len(observed_contexts),
        "unavailable_context_tool_response_count": sum(
            not call["response_available"] for call in calls
        ),
        "event_stream_complete": telemetry["usage_coverage_complete"],
        "parse_errors": telemetry["parse_errors"],
        "union_returned_files": union_files if observed_contexts else None,
        "union_declared_target_file_coverage_fraction": len(targets.intersection(union_files))
        / len(targets)
        if observed_contexts and targets
        else None,
        "union_declared_declaration_visible_fraction": len(declarations) / len(expected_symbols)
        if observed_contexts and expected_symbols
        else None,
    }


def analyze_experiment(directory: Path) -> dict[str, Any]:
    tasks = {
        task["id"]: task
        for task in json.loads((directory / "plan.json").read_text(encoding="utf-8"))["tasks"]
    }
    runs = json.loads((directory / "runs.json").read_text(encoding="utf-8"))
    rows = []
    for run in runs:
        artifact = Path(run["artifacts"]) / "events.jsonl" if run.get("artifacts") else None
        if artifact is not None and not artifact.is_absolute():
            artifact = directory / artifact
        task = tasks[run["task_id"]]
        analysis = analyze_context_calls(artifact if artifact and artifact.exists() else "", task)
        rows.append(
            {
                "run_id": run["run_id"],
                "task_id": run["task_id"],
                "configuration": run["configuration"],
                "attempted": run.get("attempted"),
                "run_status": run.get("status"),
                "events_path": str(artifact) if artifact else None,
                "events_present": artifact is not None and artifact.is_file(),
                **analysis,
            }
        )
    counts = Counter(
        str(call["server_reported_passport_status"])
        for row in rows
        for call in row["calls"]
        if call["response_available"] and call["server_reported_passport_status"] is not None
    )
    return {
        "schema_version": 1,
        "source": "Native codex exec --json MCP tool lifecycle result payloads",
        "experiment": str(directory),
        "limitations": LIMITATIONS,
        "summary": {
            "planned_runs": len(rows),
            "runs_with_observed_context_response": sum(
                row["observed_context_response_count"] > 0 for row in rows
            ),
            "observed_context_tool_calls": sum(
                row["observed_context_tool_call_count"] for row in rows
            ),
            "unavailable_context_tool_responses": sum(
                row["unavailable_context_tool_response_count"] for row in rows
            ),
            "server_reported_passport_status_counts": dict(sorted(counts.items())),
        },
        "runs": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Live Codex MCP context responses",
        "",
        f"Source experiment: `{report['experiment']}`.",
        "",
        *[f"- {value}" for value in report["limitations"]],
        "",
        "| Run | Arm | Context responses | Unavailable tool results | Target-file union | Declaration union |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for run in report["runs"]:
        cells = [
            run["run_id"],
            run["configuration"],
            run["observed_context_response_count"],
            run["unavailable_context_tool_response_count"],
            run["union_declared_target_file_coverage_fraction"],
            run["union_declared_declaration_visible_fraction"],
        ]
        lines.append(
            "| "
            + " | ".join("unavailable" if value is None else str(value) for value in cells)
            + " |"
        )
    lines.extend(
        [
            "",
            "Full per-call arguments, response sizes, passport assertions, and failures are in the companion JSON.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    arguments = parser.parse_args()
    report = analyze_experiment(arguments.experiment.resolve())
    for extension in (".json", ".md"):
        if arguments.output_prefix.with_suffix(extension).exists():
            raise SystemExit("Refusing to overwrite an existing analysis artifact")
    arguments.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    arguments.output_prefix.with_suffix(".json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    arguments.output_prefix.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
