"""Observe later source hashes without inventing live freshness or following paths."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks import context_audit_v2 as audit  # noqa: E402


def sha(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def payload(path: str = "module.py", content: str = "def value(): return 1\n") -> dict:
    return {
        "operation": "get_context",
        "retrieval_id": "native-response-1",
        "items": [{"path": path, "snippet": content}],
        "source_hashes": {path: sha(content)},
    }


def event(value: dict | None = None, *, identifier: str = "native-1", **overrides) -> dict:
    item = {
        "id": identifier,
        "type": "mcp_tool_call",
        "server": "memglide",
        "tool": "fetch_context",
        "status": "completed",
        "result": {"content": [{"type": "text", "text": json.dumps(value or payload())}]},
        **overrides,
    }
    return {"type": "item.completed", "item": item}


def capture(tmp_path: Path, *events: dict) -> dict:
    worktree = tmp_path / "worktree"
    worktree.mkdir(exist_ok=True)
    source = tmp_path / "events.jsonl"
    source.write_text("\n".join(json.dumps(value) for value in events) + "\n")
    target = tmp_path / "snapshot.json"
    result = audit.capture_snapshot(source, worktree, target)
    assert json.loads(target.read_text()) == result
    assert result["phase"] == "post_codex_pre_grader"
    assert result["independently_verified_call_time_freshness"] is None
    return result


def source(tmp_path: Path, path: str = "module.py", content: str = "def value(): return 1\n"):
    target = tmp_path / "worktree" / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return target


def test_real_unchanged_source_matches_later_snapshot_without_call_time_claim(tmp_path):
    source(tmp_path)
    result = capture(tmp_path, event())
    row = result["calls"][0]
    assert row["native_call_id"] == "native-1"
    assert row["retrieval_id"] == "native-response-1"
    assert row["response_available"] is True
    assert row["errors"] == []
    observed = row["files"][0]
    assert observed["comparison"] == "match"
    assert observed["returned_source_sha256"] == observed["post_execution_source_sha256"]
    assert observed["observed_at_utc"] >= result["started_at_utc"]
    assert observed["observed_at_utc"] <= result["captured_at_utc"]
    assert result["comparison_counts"] == {"match": 1, "mismatch": 0, "unknown": 0}
    assert "snippet" not in row
    assert "def value()" not in json.dumps(result)


def test_own_edit_is_mismatch_without_becoming_failure_or_historical_staleness(tmp_path):
    source(tmp_path, content="def value(): return 2\n")
    result = capture(tmp_path, event())
    row = result["calls"][0]
    assert row["errors"] == []
    assert row["response_available"] is True
    assert row["files"][0]["comparison"] == "mismatch"
    assert row["files"][0]["post_execution_source_sha256"] == sha("def value(): return 2\n")
    assert any("own intended edits" in limitation for limitation in result["limitations"])


def test_deleted_source_remains_unknown(tmp_path):
    target = source(tmp_path)
    target.unlink()
    result = capture(tmp_path, event())
    observed = result["calls"][0]["files"][0]
    assert observed["comparison"] == "unknown"
    assert observed["post_execution_source_sha256"] is None
    assert observed["unavailable_reason"]


@pytest.mark.parametrize(
    "path",
    [
        "../outside.py",
        "/tmp/outside.py",
        "folder/../../outside.py",
        "C:/outside.py",
        "folder\\outside.py",
        "module.py\x00other",
        "./module.py",
        "folder//module.py",
        ".git/config.py",
        ".local/auth.py",
        "auth.json",
        "state.json",
        "context.db",
        "credentials.json",
        ".aws/credentials.py",
    ],
)
def test_unsafe_or_private_paths_are_rejected_before_source_read(tmp_path, monkeypatch, path):
    def forbidden(*_args, **_kwargs):
        pytest.fail("Unsafe/private source path must not reach a file read")

    monkeypatch.setattr(audit, "read_source", forbidden)
    result = capture(tmp_path, event(payload(path)))
    file = result["calls"][0]["files"][0]
    assert file["comparison"] == "unknown"
    assert file["post_execution_source_sha256"] is None
    assert file["unavailable_reason"]


@pytest.mark.parametrize("directory", [False, True])
def test_source_symlink_and_symlink_component_never_hash_outside(tmp_path, directory):
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "module.py").write_text("def value(): return 'outside'\n")
    if directory:
        (worktree / "linked").symlink_to(outside, target_is_directory=True)
        path = "linked/module.py"
    else:
        (worktree / "module.py").symlink_to(outside / "module.py")
        path = "module.py"
    result = capture(tmp_path, event(payload(path)))
    assert result["calls"][0]["files"][0]["comparison"] == "unknown"
    assert result["calls"][0]["files"][0]["post_execution_source_sha256"] is None


def test_symlink_swap_after_initial_validation_is_rejected(tmp_path, monkeypatch):
    target = source(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("def value(): return 'outside'\n")
    real_open = os.open

    def replace_then_open(path, flags, *args, **kwargs):
        if path == "module.py" and kwargs.get("dir_fd") is not None:
            target.unlink()
            target.symlink_to(outside)
        return real_open(path, flags, *args, **kwargs)

    # read_source checks os.open membership in supports_dir_fd; preserve that branch.
    monkeypatch.setattr(os, "supports_dir_fd", {*os.supports_dir_fd, replace_then_open})
    monkeypatch.setattr(os, "open", replace_then_open)
    result = capture(tmp_path, event())
    assert result["calls"][0]["files"][0]["comparison"] == "unknown"


def test_hash_only_paths_are_preserved_but_never_read(tmp_path, monkeypatch):
    source(tmp_path)
    value = payload()
    value["source_hashes"][".local/auth.json"] = "a" * 64
    real_read = audit.read_source
    seen = []

    def record(root, path, **kwargs):
        seen.append(path)
        return real_read(root, path, **kwargs)

    monkeypatch.setattr(audit, "read_source", record)
    result = capture(tmp_path, event(value))
    assert seen == ["module.py"]
    assert result["calls"][0]["unread_hash_only_paths"] == [".local/auth.json"]


@pytest.mark.parametrize("returned_hash", [None, "", "a" * 63, "x" * 64, 12])
def test_missing_or_invalid_hash_remains_unknown_without_read(tmp_path, monkeypatch, returned_hash):
    value = payload()
    value["source_hashes"]["module.py"] = returned_hash
    monkeypatch.setattr(
        audit, "read_source", lambda *_args, **_kwargs: pytest.fail("No valid hash")
    )
    result = capture(tmp_path, event(value))
    assert result["calls"][0]["files"][0]["comparison"] == "unknown"
    assert result["calls"][0]["files"][0]["returned_source_sha256"] is None


@pytest.mark.parametrize("encoding", ["structured_content", "structuredContent", "both"])
def test_matching_native_result_encodings_are_accepted(tmp_path, encoding):
    source(tmp_path)
    value = payload()
    result = {encoding: value} if encoding != "both" else {"structured_content": value}
    if encoding == "both":
        result["content"] = [{"type": "text", "text": json.dumps(value)}]
    captured = capture(tmp_path, event(result=result))
    assert captured["comparison_counts"]["match"] == 1


def test_conflicting_native_payloads_do_not_read_or_invent_results(tmp_path, monkeypatch):
    value = payload()
    conflicting = {**value, "retrieval_id": "different-response"}
    result = {
        "structured_content": value,
        "content": [{"type": "text", "text": json.dumps(conflicting)}],
    }
    monkeypatch.setattr(audit, "read_source", lambda *_a, **_k: pytest.fail("Ambiguous response"))
    captured = capture(tmp_path, event(result=result))
    assert captured["calls"][0]["response_available"] is False
    assert captured["calls"][0]["files"] is None
    assert captured["calls"][0]["errors"] == ["Structured and text JSON payloads disagree"]


@pytest.mark.parametrize(
    "result",
    [None, {"isError": True}, {"content": None}, {"content": [{"type": "text", "text": "bad"}]}],
)
def test_missing_failed_and_malformed_results_are_retained(tmp_path, result):
    captured = capture(tmp_path, event(result=result))
    assert captured["observed_memglide_call_count"] == 1
    assert captured["call_error_count"] == 1
    assert captured["calls"][0]["files"] is None


def test_started_completed_lifecycle_is_one_call_but_duplicate_completion_is_error(tmp_path):
    source(tmp_path)
    completed = event()
    started = {
        "type": "item.started",
        "item": {**completed["item"], "status": "in_progress", "result": None},
    }
    result = capture(tmp_path, started, completed, completed)
    assert result["observed_memglide_call_count"] == 1
    assert result["calls"][0]["event_lines"] == [1, 2, 3]
    assert result["calls"][0]["files"] is None
    assert "Duplicate" in result["calls"][0]["errors"][0]


def test_completed_call_failure_and_incomplete_other_call_are_preserved(tmp_path):
    result = capture(
        tmp_path,
        event(status="failed", error={"message": "tool failure"}),
        {"type": "item.started", "item": event(identifier="second")["item"]},
    )
    assert result["observed_memglide_call_count"] == 2
    assert result["call_error_count"] == 2
    assert [row["native_call_id"] for row in result["calls"]] == ["native-1", "second"]
    assert all(row["files"] is None for row in result["calls"])


def test_no_mcp_is_not_applicable_not_an_invented_freshness_success(tmp_path):
    captured = capture(tmp_path, {"type": "turn.completed", "usage": {}})
    assert captured["applicable"] is False
    assert captured["calls"] == []
    assert captured["comparison_counts"] == {"match": 0, "mismatch": 0, "unknown": 0}


def test_json_duplicate_keys_and_bad_lines_are_preserved_as_unknown(tmp_path):
    source_file = tmp_path / "events.jsonl"
    source_file.write_text('{"type":"turn.completed","type":"turn.failed"}\nnot json\n')
    result = audit.capture_snapshot(source_file, tmp_path, tmp_path / "snapshot.json")
    assert result["applicable"] is None
    assert len(result["event_errors"]) == 2
    assert result["calls"] == []


def test_duplicate_json_payload_keys_are_rejected(tmp_path):
    result = {"content": [{"type": "text", "text": '{"items":[],"items":[1]}'}]}
    captured = capture(tmp_path, event(result=result))
    assert captured["calls"][0]["response_available"] is False
    assert captured["calls"][0]["files"] is None


def test_immutable_output_cannot_replace_existing_evidence(tmp_path):
    captured = capture(tmp_path)
    output = tmp_path / "snapshot.json"
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        audit.capture_snapshot(tmp_path / "events.jsonl", tmp_path / "worktree", output)
    assert output.read_bytes() == original
    assert json.loads(original) == captured
    assert not list(tmp_path.glob(".source-audit-*"))


def test_binary_and_oversized_source_stays_unknown(tmp_path):
    target = source(tmp_path)
    target.write_bytes(b"\x00binary")
    captured = capture(tmp_path, event())
    assert captured["calls"][0]["files"][0]["comparison"] == "unknown"
    (tmp_path / "snapshot.json").unlink()
    target.write_bytes(b"x" * (audit.MAX_SOURCE_BYTES + 1))
    captured = capture(tmp_path, event())
    assert captured["calls"][0]["files"][0]["comparison"] == "unknown"
