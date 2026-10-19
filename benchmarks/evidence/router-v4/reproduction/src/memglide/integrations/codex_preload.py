"""Prepare focused local context, then replace this process with native Codex.

Importing this launcher loads only stdlib. The launcher makes no model calls,
starts no MCP server, and preserves the native executable's environment/config.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath
from typing import Any


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _find_codex(
    environment: dict[str, str], working_directory: Path, explicit: Path | None = None
) -> str:
    """Resolve an installed executable without trusting a repository PATH entry."""
    current = working_directory.resolve()
    repository = next(
        (parent for parent in (current, *current.parents) if (parent / ".git").exists()),
        current,
    )
    if explicit is not None:
        if not explicit.is_absolute():
            raise ValueError("--codex-executable must be an absolute installed executable path")
        candidates = [explicit]
    else:
        candidates = []
        for entry in environment.get("PATH", os.defpath).split(os.pathsep):
            directory = Path(entry) if entry else current
            if not directory.is_absolute():
                directory = current / directory
            candidates.append(directory / "codex")
    for candidate in candidates:
        candidate = Path(os.path.abspath(candidate))
        try:
            resolved = candidate.resolve(strict=True)
            if _inside(candidate, repository) or _inside(resolved, repository):
                continue
            if resolved.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
        except (OSError, RuntimeError):
            continue
    raise FileNotFoundError("installed codex executable not found outside the current repository")


def _hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _validate_compact_prefix(prepared: str, prompt: str, files: list[dict[str, Any]]) -> None:
    """Check the entire compact envelope against private complete-file evidence."""
    from memglide.integrations.preload import _COMPACT_NOTICE, TASK_SEPARATOR

    suffix = TASK_SEPARATOR + prompt
    if not prepared.endswith(suffix):
        raise ValueError("compact preparation modified the original task suffix")
    prefix = prepared[: -len(suffix)]
    try:
        envelope = json.loads(prefix)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("compact preparation returned invalid source JSON") from exc
    if (
        not isinstance(envelope, dict)
        or set(envelope) != {"notice", "memglide_sources"}
        or envelope["notice"] != _COMPACT_NOTICE
        or not isinstance(envelope["memglide_sources"], list)
        or len(envelope["memglide_sources"]) != len(files)
        or [item["path"] for item in files] != sorted(item["path"] for item in files)
    ):
        raise ValueError("compact preparation returned invalid source envelope")
    expected_sources = []
    for source, metadata in zip(envelope["memglide_sources"], files, strict=True):
        if (
            not isinstance(source, dict)
            or set(source) != {"path", "content"}
            or source["path"] != metadata["path"]
            or not isinstance(source["content"], str)
            or _hash(source["content"]) != metadata["sha256"]
            or len(source["content"].splitlines()) != metadata["end_line"]
        ):
            raise ValueError("compact preparation source does not match complete-file metadata")
        expected_sources.append({"path": source["path"], "content": source["content"]})
    canonical = json.dumps(
        {"notice": _COMPACT_NOTICE, "memglide_sources": expected_sources},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    if prefix != canonical:
        raise ValueError("compact preparation source JSON is not canonical")


def _validated_preparation(
    value: Any,
    prompt: str,
    context_format: str = "legacy",
    *,
    focus_paths: list[str] | None = None,
    support_paths: list[str] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Reject a malformed preparer result before launching or reporting success."""
    if not isinstance(value, dict):
        raise ValueError("preparation returned invalid metadata")
    prepared = value.get("prompt")
    mode = value.get("mode")
    reason = value.get("reason")
    files = value.get("files")
    size = value.get("context_bytes")
    if (
        not isinstance(prepared, str)
        or not isinstance(mode, str)
        or mode not in {"passthrough", "preloaded"}
        or not isinstance(reason, str)
        or not reason
        or not isinstance(files, list)
        or type(size) is not int
        or size != len(prepared.encode("utf-8")) - len(prompt.encode("utf-8"))
        or value.get("task_prompt_sha256") != _hash(prompt)
        or value.get("prepared_prompt_sha256") != _hash(prepared)
        or context_format not in {"legacy", "compact-prefix"}
        or value.get("context_format") != context_format
    ):
        raise ValueError("preparation returned invalid metadata")
    if mode == "passthrough" and (prepared != prompt or files or size):
        raise ValueError("passthrough preparation modified the task")
    if mode == "preloaded" and (not files or size <= 0):
        raise ValueError("preloaded preparation returned no source context")
    expected_layout = (
        "unchanged"
        if mode == "passthrough"
        else "source_prefix"
        if context_format == "compact-prefix"
        else "task_suffix"
    )
    if value.get("prompt_layout") != expected_layout:
        raise ValueError("preparation returned an invalid prompt layout")
    if mode == "preloaded" and context_format == "legacy" and not prepared.startswith(prompt):
        raise ValueError("legacy preparation modified the original task prefix")
    metadata_files = []
    seen_paths: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise ValueError("preparation returned invalid source metadata")
        path, digest = item.get("path"), item.get("sha256")
        first, last = item.get("start_line"), item.get("end_line")
        if (
            not isinstance(path, str)
            or not path
            or "\x00" in path
            or "\\" in path
            or PurePosixPath(path).is_absolute()
            or PurePosixPath(path).as_posix() != path
            or ".." in PurePosixPath(path).parts
            or not PurePosixPath(path).parts
            or path in seen_paths
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
            or type(first) is not int
            or first != 1
            or type(last) is not int
            or last < 0
        ):
            raise ValueError("preparation returned invalid source metadata")
        metadata_files.append(
            {"path": path, "sha256": digest, "start_line": first, "end_line": last}
        )
        seen_paths.add(path)
    requested_focus = list(dict.fromkeys(focus_paths or []))
    requested_support = [
        path for path in dict.fromkeys(support_paths or []) if path not in requested_focus
    ]
    if context_format == "compact-prefix":
        requested_focus.sort()
        requested_support.sort()
    if support_paths:
        if (
            value.get("focus_paths") != requested_focus
            or value.get("support_paths") != requested_support
        ):
            raise ValueError("preparation returned invalid focus/support classifications")
    elif "focus_paths" in value or "support_paths" in value:
        raise ValueError("preparation returned unrequested support classifications")
    if mode == "preloaded" and focus_paths is not None:
        if seen_paths != set(requested_focus + requested_support):
            raise ValueError("preparation did not deliver the complete requested file set")
    if mode == "preloaded" and context_format == "compact-prefix":
        _validate_compact_prefix(prepared, prompt, metadata_files)
    report: dict[str, Any] = {
        "mode": mode,
        "reason": reason,
        "task_prompt_sha256": _hash(prompt),
        "prepared_prompt_sha256": _hash(prepared),
        "files": metadata_files,
        "context_bytes": size,
    }
    if context_format != "legacy":
        report["context_format"] = context_format
        report["prompt_layout"] = expected_layout
    if support_paths:
        report["focus_paths"] = requested_focus
        report["support_paths"] = requested_support
    for key in ("preparation_wall_seconds", "preparation_cpu_seconds"):
        duration = value.get(key)
        if (
            not isinstance(duration, (int, float))
            or isinstance(duration, bool)
            or not math.isfinite(duration)
            or duration < 0
        ):
            raise ValueError("preparation returned invalid timing metadata")
        report[key] = duration
    return prepared, report


def _write_report(destination: Path, report: dict[str, Any]) -> None:
    """Durably replace one explicitly selected report, without exposing its text."""
    temporary: str | None = None
    try:
        descriptor, temporary = tempfile.mkstemp(
            prefix=".memglide-preparation-", dir=destination.parent
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
        # Linux supports directory fsync; the report was already atomic if a
        # different platform rejects directory descriptors or synchronization.
        try:
            directory = os.open(destination.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(directory)
        except OSError:
            pass
        finally:
            os.close(directory)
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def _validated_automatic_preparation(
    value: Any,
    prompt: str,
    context_format: str,
    *,
    max_context_bytes: int,
    max_added_tokens: int,
    selection_policy: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Validate local selection evidence before reporting or forwarding source.

    The additional receipt is private observation, not model-visible context.
    In particular, a selector cannot claim a path/hash without delivering exactly
    that complete file through the ordinary source-preparation ABI.
    """
    from memglide.integrations.preload import MAX_FOCUS_PATHS, MAX_PATH_COMPONENTS

    if not isinstance(value, dict) or not isinstance(value.get("automatic_selection"), dict):
        raise ValueError("automatic preparation returned invalid selection metadata")
    receipt = value["automatic_selection"]
    if selection_policy is not None and (
        not isinstance(selection_policy, str) or selection_policy not in {"v1", "v2", "v3", "v4"}
    ):
        raise ValueError("automatic preparation received an unrecognized selection policy")
    fields = {
        "version", "policy_version", "decision", "reason", "selected_paths", "source_versions",
        "ranked_candidates", "estimated_added_tokens", "token_estimate_method",
        "discovery_wall_seconds", "discovery_cpu_seconds", "index_refresh_wall_seconds",
        "retrieval_wall_seconds", "source_preparation_wall_seconds", "auxiliary_model_calls",
        "provided_source_paths", "static_dependency_coverage",
        "candidate_files_considered", "omitted_candidate_files", "dependency_paths_considered",
        "index_refreshed", "unresolved_dependency_count", "candidate_generation_limit_reached",
    }
    if receipt.get("policy_version") == "deterministic-source-v4":
        fields.add("coarse_selection")
    if set(receipt) != fields:
        raise ValueError("automatic preparation returned invalid selection fields")

    def valid_path(path: Any) -> bool:
        return (
            isinstance(path, str)
            and bool(path)
            and len(path) <= 4096
            and "\x00" not in path
            and "\\" not in path
            and not any(0xD800 <= ord(character) <= 0xDFFF for character in path)
            and not PurePosixPath(path).is_absolute()
            and PurePosixPath(path).as_posix() == path
            and ".." not in PurePosixPath(path).parts
            and 1 <= len(PurePosixPath(path).parts) <= MAX_PATH_COMPONENTS
        )

    if receipt["policy_version"] == "deterministic-source-v4":
        coarse = receipt["coarse_selection"]
        coarse_fields = {
            "version", "scope", "supported_production_files", "unsupported_production_files",
            "coarse_files_checked", "coarse_bytes", "potential_supported_files",
            "weak_supported_files", "potential_unsupported_files", "weak_unsupported_files",
            "nonproduction_parse_errors_accepted", "coarse_wall_seconds", "scope_complete",
            "frontier", "frontier_omitted",
        }
        if not isinstance(coarse, dict) or set(coarse) != coarse_fields:
            raise ValueError("automatic preparation returned invalid coarse selection fields")
        bounds = {
            "supported_production_files": 20_000, "unsupported_production_files": 20_000,
            "coarse_files_checked": 100, "coarse_bytes": 2_097_152,
            "potential_supported_files": 100, "weak_supported_files": 100,
            "potential_unsupported_files": 100, "weak_unsupported_files": 100,
            "nonproduction_parse_errors_accepted": 100, "frontier_omitted": 100,
        }
        duration = coarse["coarse_wall_seconds"]
        frontier = coarse["frontier"]
        if (
            type(coarse["version"]) is not int or coarse["version"] != 1
            or coarse["scope"] != "supported-production-lexical-upper-bound-v1"
            or type(coarse["scope_complete"]) is not bool
            or any(type(coarse[key]) is not int or not 0 <= coarse[key] <= bound
                   for key, bound in bounds.items())
            or type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0
            or not isinstance(frontier, list) or len(frontier) > 4
        ):
            raise ValueError("automatic preparation returned invalid coarse selection metadata")
        classifications = {"potential_supported", "potential_unsupported", "lexically_impossible"}
        reasons = {"possible_explicit_anchor", "two_term_upper_bound", "insufficient_upper_bound"}
        for item in frontier:
            if (
                not isinstance(item, dict)
                or set(item) != {"path", "sha256", "classification", "reason"}
                or not valid_path(item["path"])
                or not isinstance(item["sha256"], str) or len(item["sha256"]) != 64
                or any(char not in "0123456789abcdef" for char in item["sha256"])
                or not isinstance(item["classification"], str)
                or item["classification"] not in classifications
                or not isinstance(item["reason"], str) or item["reason"] not in reasons
            ):
                raise ValueError("automatic preparation returned invalid coarse frontier")
        classified = sum(coarse[key] for key in (
            "potential_supported_files", "weak_supported_files",
            "potential_unsupported_files", "weak_unsupported_files",
        ))
        if (
            classified != coarse["coarse_files_checked"]
            or coarse["coarse_files_checked"] + coarse["nonproduction_parse_errors_accepted"] > 100
            or coarse["frontier_omitted"] + len(frontier) != coarse["coarse_files_checked"]
            or len({item["path"] for item in frontier}) != len(frontier)
            or coarse["potential_supported_files"] + coarse["weak_supported_files"]
            > coarse["supported_production_files"]
            or coarse["potential_unsupported_files"] + coarse["weak_unsupported_files"]
            > coarse["unsupported_production_files"]
            or (value.get("mode") == "preloaded" and (
                not coarse["scope_complete"] or not 1 <= coarse["potential_supported_files"] <= 24
                or coarse["potential_unsupported_files"]
                or receipt["candidate_files_considered"] != coarse["potential_supported_files"]
            ))
        ):
            raise ValueError("automatic preparation returned inconsistent coarse selection counts")

    selected = receipt["selected_paths"]
    provided = receipt["provided_source_paths"]
    if any(
        not isinstance(paths, list)
        or len(paths) > MAX_FOCUS_PATHS
        or any(not valid_path(path) for path in paths)
        or len(set(paths)) != len(paths)
        for paths in (selected, provided)
    ):
        raise ValueError("automatic preparation returned invalid source paths")
    expected_method = (
        "ceil(UTF-8 added context bytes / 3); planning proxy, not measured usage"
    )
    if (
        type(receipt["version"]) is not int
        or receipt["version"] != 1
        or not isinstance(receipt["policy_version"], str)
        or receipt["policy_version"] not in {
            "deterministic-source-v1", "deterministic-source-v2", "deterministic-source-v3",
            "deterministic-source-v4",
        }
        or not isinstance(receipt["decision"], str)
        or receipt["decision"] not in {"SKIP", "FOCUSED_SOURCE", "FULL_SOURCE"}
        or not isinstance(receipt["reason"], str)
        or not 1 <= len(receipt["reason"]) <= 2048
        or receipt["reason"] != value.get("reason")
        or receipt["token_estimate_method"] != expected_method
        or type(receipt["auxiliary_model_calls"]) is not int
        or receipt["auxiliary_model_calls"] != 0
        or receipt["static_dependency_coverage"]
        != "bounded direct resolved production targets; not global completeness"
    ):
        raise ValueError("automatic preparation returned invalid decision metadata")
    for field in (
        "discovery_wall_seconds", "discovery_cpu_seconds", "index_refresh_wall_seconds",
        "retrieval_wall_seconds", "source_preparation_wall_seconds",
    ):
        duration = receipt[field]
        if (
            not isinstance(duration, (int, float))
            or isinstance(duration, bool)
            or not math.isfinite(duration)
            or duration < 0
        ):
            raise ValueError("automatic preparation returned invalid timing metadata")
    for field in (
        "candidate_files_considered", "omitted_candidate_files", "dependency_paths_considered",
        "unresolved_dependency_count",
    ):
        if type(receipt[field]) is not int or not 0 <= receipt[field] <= 20_000:
            raise ValueError("automatic preparation returned invalid discovery counts")
    if (
        type(receipt["index_refreshed"]) is not bool
        or type(receipt["candidate_generation_limit_reached"]) is not bool
    ):
        raise ValueError("automatic preparation returned invalid refresh metadata")
    candidates = receipt["ranked_candidates"]
    if not isinstance(candidates, list) or len(candidates) > 12:
        raise ValueError("automatic preparation returned invalid ranking metadata")
    for candidate in candidates:
        if (
            not isinstance(candidate, dict)
            or set(candidate) != {"path", "score", "reason", "evidence_terms", "explicit_anchor"}
            or not valid_path(candidate["path"])
            or not isinstance(candidate["score"], (int, float))
            or isinstance(candidate["score"], bool)
            or not math.isfinite(candidate["score"])
            or candidate["score"] < 0
            or not isinstance(candidate["reason"], str)
            or not 1 <= len(candidate["reason"]) <= 2048
            or type(candidate["explicit_anchor"]) is not bool
            or not isinstance(candidate["evidence_terms"], list)
            or len(candidate["evidence_terms"]) > 64
            or any(
                not isinstance(term, str) or not 1 <= len(term) <= 128
                for term in candidate["evidence_terms"]
            )
        ):
            raise ValueError("automatic preparation returned invalid ranking metadata")
    if len({candidate["path"] for candidate in candidates}) != len(candidates):
        raise ValueError("automatic preparation returned duplicate ranking paths")
    if (
        receipt["candidate_files_considered"] < len(candidates)
        or (
            candidates
            and receipt["omitted_candidate_files"]
            != max(0, receipt["candidate_files_considered"] - len(candidates))
        )
        or provided  # The launcher has no caller-supplied source-body mapping.
    ):
        raise ValueError("automatic preparation returned inconsistent discovery metadata")
    prepared, report = _validated_preparation(
        value, prompt, context_format, focus_paths=selected
    )
    versions = receipt["source_versions"]
    expected_versions = {item["path"]: item["sha256"] for item in report["files"]}
    estimate = receipt["estimated_added_tokens"]
    if (
        not isinstance(versions, dict)
        or versions != expected_versions
        or selected != [item["path"] for item in report["files"]]
        or type(estimate) is not int
        or estimate != math.ceil(report["context_bytes"] / 3)
        or estimate > max_added_tokens
        or report["context_bytes"] > max_context_bytes
        or (receipt["decision"] == "SKIP") != (report["mode"] == "passthrough")
        or (receipt["decision"] == "SKIP" and (selected or versions or estimate))
        or (
            report["mode"] == "preloaded"
            and (
                not candidates
                or not receipt["index_refreshed"]
                or candidates[0]["path"] not in selected
                or (receipt["decision"] == "FULL_SOURCE")
                != (receipt["dependency_paths_considered"] > 0)
            )
        )
    ):
        raise ValueError("automatic preparation returned inconsistent source evidence or budget")
    if report["mode"] == "preloaded" and context_format == "legacy":
        from memglide.integrations.preload import _EXPLANATION

        prefix = prompt + "\n\n" + _EXPLANATION
        try:
            envelope = json.loads(prepared.removeprefix(prefix))
        except (json.JSONDecodeError, RecursionError) as exc:
            raise ValueError("automatic preparation returned invalid source envelope") from exc
        if not prepared.startswith(prefix) or not isinstance(envelope, dict):
            raise ValueError("automatic preparation returned invalid source envelope")
        if prepared != prefix + json.dumps(envelope, ensure_ascii=False, separators=(",", ":")):
            raise ValueError("automatic preparation returned noncanonical source envelope")
        sources = envelope.get("memglide_sources")
        if (
            set(envelope) != {"memglide_sources"}
            or not isinstance(sources, list)
            or len(sources) != len(report["files"])
        ):
            raise ValueError("automatic preparation returned invalid source envelope")
        for source, metadata in zip(sources, report["files"], strict=True):
            if (
                not isinstance(source, dict)
                or set(source) != {"path", "sha256", "start_line", "end_line", "content"}
                or not isinstance(source["content"], str)
                or any(source.get(key) != expected for key, expected in metadata.items())
                or _hash(source["content"]) != metadata["sha256"]
                or len(source["content"].splitlines()) != metadata["end_line"]
            ):
                raise ValueError("automatic preparation source does not match complete-file metadata")
    # Preserve source-integrity diagnostics before checking the requested policy.
    # Both checks must pass before any report is written or native exec occurs.
    if (
        selection_policy is not None
        and receipt["policy_version"] != "deterministic-source-" + selection_policy
    ):
        raise ValueError("automatic preparation returned invalid decision metadata")
    report["automatic_selection"] = receipt
    return prepared, report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare optional approved source context, then run installed codex exec once. "
            "Put native Codex exec options after --. Existing MCP configuration is preserved."
        )
    )
    parser.add_argument("--project", help="existing approved Memglide project ID")
    parser.add_argument("--db", type=Path, help="existing Memglide database path")
    parser.add_argument(
        "--discover",
        action="store_true",
        help="opt in to bounded local task-to-source discovery without supplied target paths",
    )
    parser.add_argument(
        "--selection-policy",
        choices=("v1", "v2", "v3", "v4"),
        default=None,
        help="local --discover policy; default v1, v2/v3/v4 are explicit experiments",
    )
    parser.add_argument("--focus", action="append", default=[], help="relative indexed source path")
    parser.add_argument(
        "--support",
        action="append",
        default=[],
        help="optional relative indexed support file, such as the task's existing tests",
    )
    parser.add_argument("--context-supplied", action="store_true", help="skip source preparation")
    parser.add_argument("--mode", choices=("auto", "off", "preload"), default="auto")
    parser.add_argument(
        "--context-format",
        choices=("legacy", "compact-prefix"),
        default="compact-prefix",
        help="source layout; compact-prefix is experimental, legacy preserves the original layout",
    )
    parser.add_argument("--max-context-bytes", type=int, default=12_000)
    parser.add_argument(
        "--max-added-tokens",
        type=int,
        default=4000,
        help="planning estimate cap for --discover; not measured model token usage",
    )
    parser.add_argument(
        "--preparation-report", type=Path, help="write private JSON before native exec"
    )
    parser.add_argument("--codex-executable", type=Path, help="absolute installed Codex executable")
    parser.add_argument("prompt", nargs="?", help="task prompt; omitted or - reads stdin")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Return only for input/preparation/exec errors; success becomes native Codex."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    separator = arguments.index("--") if "--" in arguments else len(arguments)
    options = _parser().parse_args(arguments[:separator])
    native_options = arguments[separator + 1 :] if separator < len(arguments) else []
    try:
        if options.discover and (options.focus or options.support):
            raise ValueError("--discover cannot be combined with --focus or --support")
        if options.selection_policy is not None and not options.discover:
            raise ValueError("--selection-policy requires --discover")
        prompt = options.prompt
        if prompt is None or prompt == "-":
            if sys.stdin.isatty():
                raise ValueError("provide a task prompt or pipe UTF-8 prompt text on stdin")
            # TextIOWrapper.read() normalizes CRLF/CR; UTF-8 decoding the raw
            # bytes preserves the caller's task exactly on passthrough paths.
            prompt = sys.stdin.buffer.read().decode("utf-8")
        if not prompt:
            raise ValueError("task prompt must not be empty")
        if "\x00" in prompt or any("\x00" in option for option in native_options):
            raise ValueError("task prompt and Codex arguments cannot contain NUL bytes")
        environment = dict(os.environ)
        executable = _find_codex(environment, Path.cwd(), options.codex_executable)
        # This dependency also imports only stdlib until scoped preparation is
        # requested. No SDK, Service, MCP, model classifier, or login is started.
        if options.discover:
            from memglide.integrations.auto_preload import prepare_task_prompt

            preparation = prepare_task_prompt(
                prompt,
                project_id=options.project,
                db_path=options.db,
                enabled=True,
                context_supplied=options.context_supplied,
                mode=options.mode,
                max_context_bytes=options.max_context_bytes,
                context_format=options.context_format,
                max_added_tokens=options.max_added_tokens,
                selection_policy=options.selection_policy or "v1",
            )
            prepared, metadata = _validated_automatic_preparation(
                preparation,
                prompt,
                options.context_format,
                max_context_bytes=options.max_context_bytes,
                max_added_tokens=options.max_added_tokens,
                selection_policy=options.selection_policy or "v1",
            )
        else:
            from memglide.integrations.preload import prepare_prompt

            preparation = prepare_prompt(
                prompt,
                project_id=options.project,
                db_path=options.db,
                focus_paths=options.focus,
                support_paths=options.support,
                context_supplied=options.context_supplied,
                mode=options.mode,
                max_context_bytes=options.max_context_bytes,
                context_format=options.context_format,
            )
            prepared, metadata = _validated_preparation(
                preparation,
                prompt,
                options.context_format,
                focus_paths=options.focus,
                support_paths=options.support,
            )
        command = [executable, "exec", *native_options, "--", "-"]
        prepared_bytes = prepared.encode("utf-8")
        # A regular file cannot deadlock on a full pipe buffer, and passing '-'
        # avoids both per-argument limits and exposing source in process argv.
        with tempfile.TemporaryFile(mode="w+b") as native_input:
            native_input.write(prepared_bytes)
            native_input.flush()
            native_input.seek(0)
            if options.preparation_report is not None:
                _write_report(
                    options.preparation_report,
                    {
                        "version": 4
                        if options.discover
                        else 3
                        if options.support
                        else 1
                        if options.context_format == "legacy"
                        else 2,
                        "preparation": metadata,
                        "executable": executable,
                        "exec_argv": command,
                        "native_stdin": {
                            "sha256": _hash(prepared),
                            "bytes": len(prepared_bytes),
                            "transport": "temporary_file_descriptor",
                        },
                        "native_exec_boundary_monotonic_seconds": time.monotonic(),
                    },
                )
            if options.mode == "preload" and metadata["mode"] == "passthrough":
                print(
                    f"memglide-codex: source preparation skipped ({metadata['reason']}); "
                    "forwarding unchanged task",
                    file=sys.stderr,
                )
            os.dup2(native_input.fileno(), 0, inheritable=True)
            os.execve(executable, command, environment)
        return 0  # Unreachable for the native os.execve implementation.
    except FileNotFoundError as exc:
        print(f"memglide-codex: {exc}", file=sys.stderr)
        return 127
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        print(f"memglide-codex: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
