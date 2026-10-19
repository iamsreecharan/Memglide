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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare optional approved source context, then run installed codex exec once. "
            "Put native Codex exec options after --. Existing MCP configuration is preserved."
        )
    )
    parser.add_argument("--project", help="existing approved Memglide project ID")
    parser.add_argument("--db", type=Path, help="existing Memglide database path")
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
                        "version": 3
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
