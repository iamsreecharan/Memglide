"""Conservative telemetry from Codex's supported ``exec --json`` event stream.

This module deliberately does not treat the model's final structured response as
telemetry. Usage comes only from ``turn.completed.usage``. Those events do not
expose the number of underlying inference/API requests, provider invoiced cost,
CPU, RSS, or a complete filesystem read trace; these remain unavailable.
"""

from __future__ import annotations

import json
import re
import shlex
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, cast

USAGE_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens")
READ_METHOD = (
    "Heuristic command-intent proxy from successful command_execution items containing literal "
    "cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, "
    "scripts, directory searches, MCP reads, and internal reads are excluded. A repeated "
    "command names a path recognized in an earlier command. Unquoted shell newlines are "
    "command separators; quoted newlines stay argument data and are excluded as paths. "
    "This is not an I/O trace, "
    "an actual read count, or a guaranteed lower bound on filesystem reads."
)


def _literal_path(value: str) -> bool:
    return (
        bool(value)
        and not value.startswith("-")
        and not any(character in value for character in "*$`?{}<>\n")
    )


def _separate_unquoted_newlines(command: str) -> str:
    """Keep shell newlines as separators without splitting quoted argument data.

    shlex normally treats LF as whitespace, accidentally joining a following
    ``git diff`` into preceding ``cat`` operands. Retaining LF before the inserted
    semicolon also ends shlex comments correctly. This is lexical normalization,
    not shell evaluation; unquoted/double-quoted backslash-LF is a continuation.
    """
    normalized: list[str] = []
    quote: str | None = None
    comment = False
    index = 0
    while index < len(command):
        character = command[index]
        if comment:
            if character == "\n":
                normalized.append("\n;\n")
                comment = False
            else:
                normalized.append(character)
            index += 1
            continue
        if quote == "'":
            normalized.append(character)
            if character == "'":
                quote = None
            index += 1
            continue
        if character == "\\" and index + 1 < len(command):
            following = command[index + 1]
            if following != "\n":
                normalized.extend((character, following))
            index += 2
            continue
        if quote == '"':
            normalized.append(character)
            if character == '"':
                quote = None
        elif character in {"'", '"'}:
            normalized.append(character)
            quote = character
        elif character == "#":
            normalized.append(character)
            comment = True
        elif character == "\n":
            normalized.append("\n;\n")
        else:
            normalized.append(character)
        index += 1
    return "".join(normalized)


def _command_segments(command: str, *, _wrapper_depth: int = 0) -> list[list[str]]:
    """Parse literal shell commands, without executing any user/model text."""
    try:
        lexer = shlex.shlex(
            _separate_unquoted_newlines(command), posix=True, punctuation_chars=";&|<>"
        )
        lexer.whitespace_split = True
        segments: list[list[str]] = [[]]
        for token in lexer:
            if token in {";", "&&"}:
                segments.append([])
            elif token and all(character in ";&|<>" for character in token):
                # Redirections and conditional/piped execution are too ambiguous.
                return []
            else:
                segments[-1].append(token)
        segments = [segment for segment in segments if segment]
        # Only unwrap a standalone shell command. Flattening a shell alongside
        # outer commands would incorrectly let an inner `cd` change their scope.
        if len(segments) == 1 and len(segments[0]) == 3:
            executable, option, inner = segments[0]
            if Path(executable).name in {"bash", "sh", "zsh"} and option in {"-c", "-lc"}:
                if _wrapper_depth >= 4:
                    return []
                return _command_segments(inner, _wrapper_depth=_wrapper_depth + 1)
        return segments
    except ValueError:
        return []


def observed_read_paths(command: str) -> list[str]:
    """Return a narrow, documented heuristic; never an exhaustive read trace."""
    paths: list[str] = []
    directory = PurePosixPath(".")
    for words in _command_segments(command):
        if not words:
            continue
        executable, *arguments = words
        executable = Path(executable).name
        if executable == "cd" and len(arguments) == 1 and _literal_path(arguments[0]):
            directory = directory / arguments[0]
            continue
        candidates: list[str] = []
        if executable == "cat":
            # Only non-option arguments. stdin has no traceable path.
            candidates = [argument for argument in arguments if _literal_path(argument)]
        elif executable == "sed" and len(arguments) >= 3 and arguments[0] == "-n":
            # Restrict to a single literal print expression, without scripts/-f/-i.
            expression = arguments[1]
            if expression.endswith("p") and all(c in "0123456789,$p" for c in expression):
                candidates = arguments[2:]
        elif executable in {"head", "tail"}:
            index = 0
            while index < len(arguments):
                argument = arguments[index]
                if argument in {"-n", "-c", "--lines", "--bytes"}:
                    index += 2
                elif argument.startswith("-"):
                    index += 1
                else:
                    candidates.append(argument)
                    index += 1
        elif executable == "rg" and "--files" not in arguments:
            # A simple literal pattern and literal file operands only. More complex
            # invocations are omitted rather than pretending to trace every read.
            arguments = [a for a in arguments if a not in {"-n", "--line-number", "-i", "-F"}]
            if len(arguments) >= 2 and not arguments[0].startswith("-"):
                candidates = arguments[1:]
        for candidate in candidates:
            if not _literal_path(candidate) or candidate in {".", "..", "-"}:
                continue
            # File-like requirement avoids counting directory searches as file reads.
            if executable == "rg" and not PurePosixPath(candidate).suffix:
                continue
            path = PurePosixPath(candidate)
            paths.append(str(path if path.is_absolute() else directory / path))
    return paths


def _mcp_success(item: dict[str, Any]) -> tuple[bool | None, str]:
    if item.get("error") or item.get("status") == "failed":
        return False, "CLI recorded a tool error/failure"
    if item["lifecycle_event"] != "item.completed" or item.get("status") != "completed":
        return None, "Tool invocation did not reach a completed item"
    result = item.get("result")
    if result is None:
        return None, "Completed tool item omitted its result; application success is unavailable"
    if isinstance(result, dict):
        if result.get("isError") or result.get("is_error") or result.get("error"):
            return False, "Tool result explicitly reported an error"
        structured = result.get("structured_content", result.get("structuredContent"))
        if isinstance(structured, dict) and structured.get("error"):
            return False, "Structured tool result explicitly reported an error"
        for block in result.get("content", []):
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            try:
                value = json.loads(block.get("text", ""))
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(value, dict) and value.get("error"):
                return False, "JSON text tool result explicitly reported an error"
    return True, "Completed CLI tool item returned a result without an explicit error"


def _compact_operation_proof(item: dict[str, Any]) -> str | None:
    """Credit compact aliases only from matching actual MCP response evidence.

    Tool names and model summaries alone cannot establish that fetch_context
    returned source. Conflicting structured/text JSON results are rejected.
    """
    result = item.get("result")
    if not isinstance(result, dict):
        return None
    candidates = []
    for key in ("structured_content", "structuredContent"):
        if isinstance(result.get(key), dict):
            candidates.append(result[key])
    for block in result.get("content", []):
        if not isinstance(block, dict) or block.get("type") != "text":
            continue
        try:
            candidate = json.loads(block.get("text", ""))
        except (ValueError, TypeError):
            continue
        if isinstance(candidate, dict):
            candidates.append(candidate)
    if not candidates or any(candidate != candidates[0] for candidate in candidates[1:]):
        return None
    value = candidates[0]
    if not isinstance(value.get("retrieval_id"), str) or not value["retrieval_id"]:
        return None
    if item.get("tool") == "verify_context":
        return (
            "get_context_passport"
            if value.get("operation") == "get_context_passport"
            and isinstance(value.get("status"), str)
            and isinstance(value.get("source_freshness"), str)
            and isinstance(value.get("stale_files"), list)
            else None
        )
    if item.get("tool") != "fetch_context" or value.get("operation") != "get_context":
        return None
    source_hashes, items = value.get("source_hashes"), value.get("items")
    if not isinstance(source_hashes, dict) or not isinstance(items, list) or not items:
        return None
    source_items = 0
    for evidence in items:
        if not isinstance(evidence, dict):
            return None
        path, snippet = evidence.get("path"), evidence.get("snippet")
        if (
            not isinstance(path, str)
            or not path
            or not isinstance(snippet, str)
            or re.fullmatch(r"[0-9a-f]{64}", str(source_hashes.get(path, ""))) is None
        ):
            return None
        source_items += bool(snippet.strip())
    return "get_context" if source_items else None


def parse_codex_jsonl(source: str | Path) -> dict[str, Any]:
    """Parse an event file (Path), or JSONL content (str), retaining failures.

    A malformed line never becomes usage. Duplicate lifecycle items are counted
    once by ID. A started but incomplete MCP call remains visible as incomplete.
    """
    content = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    events: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                raise ValueError("Event must be an object with a string type")
            events.append(event)
        except (json.JSONDecodeError, ValueError) as error:
            parse_errors.append({"line": line_number, "error": str(error)})

    turns = [event for event in events if event["type"] == "turn.completed"]
    usage_rows = [event.get("usage") for event in turns]
    usage: dict[str, int | None] = {}
    missing_usage: dict[str, str] = {}
    for key in USAGE_KEYS:
        values = [row.get(key) if isinstance(row, dict) else None for row in usage_rows]
        if values and all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in values
        ):
            usage[key] = sum(cast(list[int], values))
        else:
            usage[key] = None
            missing_usage[key] = (
                "No turn.completed usage was emitted"
                if not values
                else "At least one completed turn omitted a valid usage field; partial totals withheld"
            )

    observed_completed_usage = dict(usage)
    failed_turn_count = sum(event["type"] == "turn.failed" for event in events)
    terminal = bool(events and events[-1]["type"] in {"turn.completed", "turn.failed"})
    coverage_complete = bool(events and terminal and not failed_turn_count and not parse_errors)
    if not coverage_complete:
        for key in USAGE_KEYS:
            usage[key] = None
            missing_usage[key] = (
                "Total usage unavailable: event stream is empty, truncated, contains unparsed "
                "lines, or includes a failed turn whose usage may be unreported"
            )

    items: dict[str, dict[str, Any]] = {}
    for index, event in enumerate(events):
        item = event.get("item")
        if not isinstance(item, dict) or event["type"] not in {
            "item.started",
            "item.updated",
            "item.completed",
        }:
            continue
        identifier = str(item.get("id", f"event-without-id-{index}"))
        previous = items.get(identifier, {})
        items[identifier] = {**previous, **item, "lifecycle_event": event["type"]}

    mcp_calls: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []
    file_reads: list[str] = []
    read_command_count = 0
    repeated_read_command_count = 0
    previously_named_paths: set[str] = set()
    for identifier, item in items.items():
        if item.get("type") == "mcp_tool_call":
            success, success_reason = _mcp_success(item)
            compact_operation = _compact_operation_proof(item) if success is True else None
            mcp_calls.append(
                {
                    "id": identifier,
                    "server": item.get("server"),
                    "tool": item.get("tool"),
                    "status": item.get("status", "incomplete"),
                    "completed": item["lifecycle_event"] == "item.completed",
                    "error": item.get("error"),
                    "successful": success,
                    "success_evidence": success_reason,
                    "verified_compact_operation": compact_operation,
                }
            )
        elif item.get("type") == "command_execution":
            command = item.get("command")
            commands.append(
                {
                    "id": identifier,
                    "command": command,
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status", "incomplete"),
                }
            )
            if isinstance(command, str) and item.get("exit_code") == 0:
                paths = observed_read_paths(command)
                if paths:
                    read_command_count += 1
                    if any(path in previously_named_paths for path in paths):
                        repeated_read_command_count += 1
                    previously_named_paths.update(paths)
                    file_reads.extend(paths)

    errors = [event for event in events if event["type"] in {"error", "turn.failed"}]
    frequencies = Counter(file_reads)
    return {
        "source": "codex exec --json; turn.completed usage and item lifecycle events",
        "event_count": len(events),
        "parse_errors": parse_errors,
        "completed_turns": len(turns),
        "failed_turns": failed_turn_count,
        "stream_terminal": terminal,
        "usage": usage,
        "usage_unavailable_reasons": missing_usage,
        "observed_completed_turn_usage": observed_completed_usage,
        "usage_coverage_complete": coverage_complete,
        "usage_scope": "Complete parsed stream only; partial observed turn usage is stored separately",
        "model_calls": None,
        "model_calls_unavailable_reason": (
            "Codex exec JSONL exposes completed turns, not underlying provider/API model calls"
        ),
        "actual_cost_usd": None,
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "mcp_call_count": len(mcp_calls) if events else None,
        "mcp_calls": mcp_calls,
        "mcp_counts_complete": coverage_complete,
        "mcp_count_scope": (
            "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound"
        ),
        "memglide_mcp_call_count": sum(
            str(call.get("server", "")).lower() == "memglide" for call in mcp_calls
        )
        if events
        else None,
        "memglide_successful_get_context_count": sum(
            str(call.get("server", "")).lower() == "memglide"
            and (
                call.get("tool") == "get_context"
                or call.get("tool") == "fetch_context"
                and call.get("verified_compact_operation") == "get_context"
            )
            and call["successful"] is True
            for call in mcp_calls
        )
        if events
        else None,
        "memglide_successful_fetch_context_count": sum(
            str(call.get("server", "")).lower() == "memglide"
            and call.get("tool") == "fetch_context"
            and call.get("verified_compact_operation") == "get_context"
            and call["successful"] is True
            for call in mcp_calls
        )
        if events
        else None,
        "memglide_successful_verify_context_count": sum(
            str(call.get("server", "")).lower() == "memglide"
            and call.get("tool") == "verify_context"
            and call.get("verified_compact_operation") == "get_context_passport"
            and call["successful"] is True
            for call in mcp_calls
        )
        if events
        else None,
        "memglide_get_context_success_unknown_count": sum(
            str(call.get("server", "")).lower() == "memglide"
            and call.get("tool") == "get_context"
            and call["successful"] is None
            for call in mcp_calls
        )
        if events
        else None,
        "command_count": len(commands) if events else None,
        "commands": commands,
        "repeated_file_reads": None,
        "repeated_file_reads_unavailable_reason": (
            "Codex JSONL does not expose a filesystem I/O trace; command text cannot establish actual reads"
        ),
        "observed_file_read_commands": read_command_count if events else None,
        "observed_repeated_read_commands": repeated_read_command_count if events else None,
        "observed_read_command_paths": file_reads,
        "repeated_read_command_paths": {
            path: count for path, count in frequencies.items() if count > 1
        },
        "file_reads_complete": False,
        "file_read_method": READ_METHOD,
        "errors": errors,
    }
