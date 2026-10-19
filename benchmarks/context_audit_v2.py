"""Independently observe returned source versions after Codex, before grading.

This deliberately makes no claim about source versions at tool-call time. A
normal successful edit can make a returned hash differ from this later snapshot.
No source content, database, auth state, or credentials are included in the audit.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from memglide.security.paths import DEFAULT_IGNORED, read_source, secret_path
from memglide.storage.database import DomainError

MAX_EVENTS_BYTES = 64 * 1024 * 1024
MAX_SOURCE_BYTES = 512_000
SOURCE_SUFFIXES = {".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
LIMITATIONS = [
    "Hashes are independently observed after Codex exits and before grading, not at retrieval time.",
    "A mismatch may result from the model's own intended edits; it is not a correctness failure "
    "or proof that the source was stale when retrieved.",
    "A match establishes equality at this later observation, not uninterrupted historical freshness.",
    "Only returned item paths with valid source hashes are read. Non-source, credential, state, "
    "database, symlink, unavailable, oversized, binary, and unsafe paths remain unknown.",
    "Returned snippets are not independently checked for complete bodies or semantic completeness.",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def _decode(text: Any) -> Any:
    return json.loads(text, object_pairs_hook=_object)


def _read_events(path: Path) -> str:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_EVENTS_BYTES:
            raise ValueError("Event input is not a regular file within the size limit")
        with os.fdopen(os.dup(descriptor), "rb") as source:
            data = source.read(MAX_EVENTS_BYTES + 1)
        if len(data) > MAX_EVENTS_BYTES:
            raise ValueError("Event input exceeds the size limit")
        return data.decode("utf-8")
    finally:
        os.close(descriptor)


def _payload(result: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(result, dict):
        return None, ["Completed tool call omitted a result object"]
    if result.get("isError") or result.get("is_error") or result.get("error"):
        return None, ["Tool result explicitly reported an application error"]
    candidates: list[dict[str, Any]] = []
    errors = []
    for key in ("structured_content", "structuredContent"):
        if key in result and result[key] is not None:
            if not isinstance(result[key], dict):
                errors.append("Structured tool result is not an object")
            else:
                candidates.append(result[key])
    blocks = result.get("content", [])
    if not isinstance(blocks, list):
        return None, ["Tool content is not an array"]
    for block in blocks:
        if not isinstance(block, dict):
            errors.append("Tool content contains a malformed block")
            continue
        if block.get("type") != "text":
            continue
        try:
            value = _decode(block.get("text"))
        except (ValueError, TypeError):
            errors.append("Text tool result is not unambiguous JSON")
            continue
        if not isinstance(value, dict):
            errors.append("Text tool result is not an object")
        else:
            candidates.append(value)
    if not candidates:
        errors.append("Tool result omitted a JSON payload")
    elif any(value != candidates[0] for value in candidates[1:]):
        errors.append("Structured and text JSON payloads disagree")
    elif candidates[0].get("error"):
        errors.append("JSON tool payload explicitly reported an application error")
    return (None, errors) if errors else (candidates[0], [])


def _source_path_error(relative: Any) -> str | None:
    if not isinstance(relative, str) or not relative or "\x00" in relative or "\\" in relative:
        return "Source path must be a nonempty relative POSIX path"
    path = PurePosixPath(relative)
    if (
        path.is_absolute()
        or ".." in path.parts
        or relative != path.as_posix()
        or re.match(r"^[A-Za-z]:", relative)
    ):
        return "Source path is absolute, traverses, or is noncanonical"
    if any(part in DEFAULT_IGNORED or part.startswith(".") for part in path.parts):
        return "Hidden, ignored, or private-state paths are excluded"
    if secret_path(relative) or path.suffix.lower() not in SOURCE_SUFFIXES:
        return "Credential, database, state, and non-source paths are excluded"
    return None


def _observe(root: Path, relative: Any, returned_hash: Any) -> dict[str, Any]:
    row = {
        "path": relative if isinstance(relative, str) else None,
        "returned_source_sha256": returned_hash
        if isinstance(returned_hash, str) and re.fullmatch(r"[0-9a-f]{64}", returned_hash)
        else None,
        "post_execution_source_sha256": None,
        "observed_at_utc": None,
        "comparison": "unknown",
        "unavailable_reason": None,
    }
    path_error = _source_path_error(relative)
    if path_error:
        row["unavailable_reason"] = path_error
    elif row["returned_source_sha256"] is None:
        row["unavailable_reason"] = "Returned source hash is missing or is not SHA-256"
    else:
        try:
            _, observed = read_source(root, relative, max_size=MAX_SOURCE_BYTES)
            row["post_execution_source_sha256"] = observed
            row["observed_at_utc"] = _utc_now()
            row["comparison"] = "match" if observed == returned_hash else "mismatch"
        except (DomainError, OSError, ValueError):
            # Do not include exception/source text, which may contain untrusted data.
            row["unavailable_reason"] = "Source unavailable or rejected by secure source policy"
    return row


def _audit_call(item: dict[str, Any], worktree: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "native_call_id": item["native_call_id"],
        "server": item.get("server"),
        "tool": item.get("tool"),
        "native_status": item.get("status"),
        "event_lines": item["event_lines"],
        "retrieval_id": None,
        "response_available": False,
        "errors": list(item["errors"]),
        "files": None,
        "returned_item_count": None,
        "unread_hash_only_paths": None,
        "independently_verified_call_time_freshness": None,
    }
    if item.get("last_event") != "item.completed" or item.get("status") != "completed":
        row["errors"].append("Tool did not reach completed status")
    if item.get("error"):
        row["errors"].append("Native CLI recorded an explicit tool error")
    if row["errors"]:
        return row
    payload, errors = _payload(item.get("result"))
    row["errors"].extend(errors)
    if payload is None:
        return row
    retrieval_id = payload.get("retrieval_id")
    if not isinstance(retrieval_id, str) or not retrieval_id:
        row["errors"].append("Payload omitted a nonempty retrieval ID")
    else:
        row["retrieval_id"] = retrieval_id
    if item.get("tool") != "fetch_context":
        row["response_available"] = not row["errors"]
        return row
    if payload.get("operation") != "get_context":
        row["errors"].append("fetch_context payload did not identify get_context")
    items, hashes = payload.get("items"), payload.get("source_hashes")
    if not isinstance(items, list) or not items or not isinstance(hashes, dict):
        row["errors"].append("Retrieval omitted nonempty items or source_hashes")
        return row
    paths: list[str] = []
    for value in items:
        if not isinstance(value, dict) or not isinstance(value.get("path"), str):
            row["errors"].append("Retrieval contains an item without a string source path")
            continue
        paths.append(value["path"])
        if not isinstance(value.get("snippet"), str) or not value["snippet"].strip():
            row["errors"].append("Retrieval contains an absent or empty source snippet")
    row["returned_item_count"] = len(items)
    row["unread_hash_only_paths"] = sorted(path for path in hashes if path not in paths)
    # Reject ambiguous/malformed responses before reading any alleged source paths.
    if row["errors"]:
        return row
    row["response_available"] = True
    row["files"] = [_observe(worktree, path, hashes.get(path)) for path in dict.fromkeys(paths)]
    return row


def _write_new(path: Path, value: dict[str, Any]) -> None:
    """Publish a complete new JSON file atomically; existing evidence is immutable."""
    descriptor, name = tempfile.mkstemp(prefix=".source-audit-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as target:
            json.dump(value, target, ensure_ascii=False, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.link(temporary, path, follow_symlinks=False)
    finally:
        temporary.unlink(missing_ok=True)


def capture_snapshot(events_path: Path, worktree: Path, outputfile: Path) -> dict[str, Any]:
    """Capture independent post-Codex/pre-grader hashes without an extra model call.

    Call once after execute_codex returns and before grading modifies the worktree.
    Existing output files are never overwritten. An empty A event stream is not
    evidence of freshness: it is explicitly not applicable to this MCP audit.
    """
    events_path, worktree, outputfile = Path(events_path), Path(worktree), Path(outputfile)
    started = _utc_now()
    started_clock = time.perf_counter()
    event_errors: list[dict[str, Any]] = []
    calls: dict[str, dict[str, Any]] = {}
    event_digest = None
    try:
        content = _read_events(events_path)
        event_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    except (OSError, ValueError):
        content = ""
        event_errors.append({"line": None, "reason": "Event input unavailable or unsafe"})
    for number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = _decode(line)
            if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                raise ValueError("Malformed native event")
        except (ValueError, TypeError):
            event_errors.append({"line": number, "reason": "Malformed or ambiguous JSON event"})
            continue
        item = event.get("item")
        if event["type"] not in {
            "item.started",
            "item.updated",
            "item.completed",
        } or not isinstance(item, dict):
            continue
        identifier = item.get("id")
        native_id = identifier if isinstance(identifier, str) and identifier else None
        key = native_id or f"missing-id-at-line-{number}"
        previous = calls.get(key)
        if previous is None and (
            item.get("type") != "mcp_tool_call" or item.get("server") != "memglide"
        ):
            continue
        errors = list(previous["errors"]) if previous else []
        if native_id is None:
            errors.append("Native call ID is missing")
        if previous and previous["last_event"] == "item.completed":
            errors.append("Duplicate or later lifecycle event after completed tool call")
        if previous and any(
            field in item and field in previous and item[field] != previous[field]
            for field in ("server", "tool", "type")
        ):
            errors.append("Native tool identity changed within one call ID")
        calls[key] = {
            **(previous or {}),
            **item,
            "native_call_id": native_id,
            "last_event": event["type"],
            "event_lines": [*(previous["event_lines"] if previous else []), number],
            "errors": errors,
        }
    rows = [_audit_call(item, worktree) for item in calls.values()]
    files = [file for row in rows for file in row["files"] or []]
    counts = Counter(file["comparison"] for file in files)
    value = {
        "schema_version": 1,
        "phase": "post_codex_pre_grader",
        "started_at_utc": started,
        "captured_at_utc": _utc_now(),
        "capture_wall_seconds": time.perf_counter() - started_clock,
        "events_sha256": event_digest,
        "applicable": bool(rows) if not event_errors else None,
        "observed_memglide_call_count": len(rows),
        "observed_fetch_context_call_count": sum(row["tool"] == "fetch_context" for row in rows),
        "response_available_count": sum(row["response_available"] for row in rows),
        "call_error_count": sum(bool(row["errors"]) for row in rows),
        "file_observation_count": len(files),
        "comparison_counts": {key: counts.get(key, 0) for key in ("match", "mismatch", "unknown")},
        "event_errors": event_errors,
        "calls": rows,
        "independently_verified_call_time_freshness": None,
        "limitations": LIMITATIONS,
    }
    _write_new(outputfile, value)
    return value
