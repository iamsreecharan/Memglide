"""Reparse frozen daily traces without changing the original experiment/report.

Only committed first-party telemetry code is imported for the historical view.
Command text from event streams is parsed as data and is never executed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import posixpath
import statistics
import subprocess
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from benchmarks import telemetry

ROOT = Path(__file__).resolve().parents[1]
PROXY_KEYS = (
    "observed_file_read_commands",
    "observed_repeated_read_commands",
    "observed_read_command_paths",
    "repeated_read_command_paths",
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _baseline_telemetry(commit: str, expected_hash: str, directory: Path) -> Any:
    if (
        not isinstance(commit, str)
        or len(commit) not in {40, 64}
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        raise ValueError("Invalid frozen source commit")
    source = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", commit + ":benchmarks/telemetry.py"]
    )
    if sha256(source) != expected_hash:
        raise ValueError("Historical telemetry source does not match the frozen manifest")
    path = directory / "frozen_telemetry.py"
    path.write_bytes(source)
    specification = importlib.util.spec_from_file_location("frozen_daily_telemetry", path)
    if specification is None or specification.loader is None:
        raise ValueError("Cannot load verified historical telemetry")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _summary(values: list[int]) -> dict[str, Any]:
    return {
        "n": len(values),
        "total": sum(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
    }


def _relative(path: str, worktree: str) -> str:
    # Purely lexical normalization for auxiliary path-mention classification.
    normalized = PurePosixPath(posixpath.normpath(path))
    if normalized.is_absolute():
        try:
            normalized = normalized.relative_to(PurePosixPath(posixpath.normpath(worktree)))
        except ValueError:
            return str(normalized)
    return str(normalized)


def _path_counts(
    value: dict[str, Any], run: dict[str, Any], task: dict[str, Any]
) -> dict[str, int]:
    paths = [_relative(path, run["worktree"]) for path in value["observed_read_command_paths"]]
    focus = set(task["focus_paths"])
    test_paths = [
        path
        for path in paths
        if any(part in {"tests", "test", "__tests__"} for part in PurePosixPath(path).parts)
        or PurePosixPath(path).name.startswith("test_")
        or ".test." in PurePosixPath(path).name
        or ".spec." in PurePosixPath(path).name
    ]
    return {
        "recognized_path_mentions": len(paths),
        "declared_focus_path_mentions": sum(path in focus for path in paths),
        "test_path_mentions": len(test_paths),
        "other_path_mentions": len(paths)
        - len(test_paths)
        - sum(path in focus for path in paths if path not in test_paths),
    }


def diagnose(experiment: Path) -> dict[str, Any]:
    experiment = experiment.resolve()
    metadata_path, report_path = experiment / "metadata.json", experiment / "report.json"
    runs_path, plan_path = experiment / "runs.json", experiment / "plan.json"
    metadata = json.loads(metadata_path.read_text())
    original_report = json.loads(report_path.read_text())
    runs = json.loads(runs_path.read_text())
    plan = json.loads(plan_path.read_text())
    tasks = {task["id"]: task for task in plan["tasks"]}
    frozen = metadata["frozen_manifest"]
    source_commit = frozen["git_head"]
    source_hash = frozen["files"]["benchmarks/telemetry.py"]
    if not metadata.get("finished_at"):
        raise ValueError("Only a finished immutable experiment may be diagnosed")
    if len(runs) != len({run["run_id"] for run in runs}):
        raise ValueError("Original run identities are not unique")
    run_ids = {run["run_id"] for run in plan["runs"]}
    if {run["run_id"] for run in runs} != run_ids:
        raise ValueError("Original run assignments do not match the saved plan")
    artifacts = [metadata_path, report_path, runs_path, plan_path]
    for run in runs:
        identifier = run["run_id"]
        if (
            not isinstance(identifier, str)
            or Path(identifier).name != identifier
            or "\x00" in identifier
        ):
            raise ValueError("Unsafe original run identifier")
        artifacts.append(experiment / "runs" / identifier / "events.jsonl")
    before = {str(path.relative_to(experiment)): sha256(path.read_bytes()) for path in artifacts}
    observations = []
    with tempfile.TemporaryDirectory(prefix="memglide-frozen-telemetry-") as temporary:
        old = _baseline_telemetry(source_commit, source_hash, Path(temporary))
        for run in runs:
            stream = experiment / "runs" / run["run_id"] / "events.jsonl"
            original, corrected = old.parse_codex_jsonl(stream), telemetry.parse_codex_jsonl(stream)
            # Reproduction must match the preserved result; never relabel a
            # changing baseline as the historical experiment.
            for key in PROXY_KEYS:
                if original[key] != run["telemetry"][key]:
                    raise ValueError(
                        "Historical read proxy does not reproduce preserved run: " + run["run_id"]
                    )
            for key in ("usage", "model_calls", "mcp_call_count", "command_count", "errors"):
                if original[key] != corrected[key]:
                    raise ValueError(
                        "Read-path correction unexpectedly changed unrelated telemetry"
                    )
            changes = []
            for command in original["commands"]:
                text = command["command"]
                if not isinstance(text, str) or command["exit_code"] != 0:
                    continue
                previous, current = (
                    old.observed_read_paths(text),
                    telemetry.observed_read_paths(text),
                )
                if previous != current:
                    changes.append(
                        {
                            "command_id": command["id"],
                            "command_sha256": sha256(text.encode()),
                            "original_paths": previous,
                            "corrected_paths": current,
                            "removed_path_mentions": list(
                                (Counter(previous) - Counter(current)).elements()
                            ),
                            "added_path_mentions": list(
                                (Counter(current) - Counter(previous)).elements()
                            ),
                        }
                    )
            observations.append(
                {
                    "run_id": run["run_id"],
                    "task_id": run["task_id"],
                    "repeat": run["repeat"],
                    "configuration": run["configuration"],
                    "language": run["language"],
                    "status": run["status"],
                    "selection_stratum": run["selection_stratum"],
                    "event_stream_sha256": before[str(stream.relative_to(experiment))],
                    "original": {
                        **{key: original[key] for key in PROXY_KEYS},
                        **_path_counts(original, run, tasks[run["task_id"]]),
                    },
                    "corrected": {
                        **{key: corrected[key] for key in PROXY_KEYS},
                        **_path_counts(corrected, run, tasks[run["task_id"]]),
                    },
                    "changed_commands": changes,
                    "actual_filesystem_reads": None,
                    "actual_repeated_filesystem_reads": None,
                }
            )
    after = {str(path.relative_to(experiment)): sha256(path.read_bytes()) for path in artifacts}
    if before != after:
        raise ValueError("An immutable experiment input changed during diagnostics")
    configurations = {}
    additive = (
        "observed_file_read_commands",
        "observed_repeated_read_commands",
        "recognized_path_mentions",
        "declared_focus_path_mentions",
        "test_path_mentions",
        "other_path_mentions",
    )
    for arm in ("A", "B"):
        selected = [run for run in observations if run["configuration"] == arm]
        original, corrected = (
            {key: _summary([run[view][key] for run in selected]) for key in additive}
            for view in ("original", "corrected")
        )
        recorded_total = original_report["configurations"][arm]["metrics"][
            "observed_file_read_commands"
        ]["total"]
        if original["observed_file_read_commands"]["total"] != recorded_total:
            raise ValueError("Historical aggregate does not reproduce the published primary report")
        configurations[arm] = {
            "runs": len(selected),
            "original": original,
            "corrected": corrected,
            "changed_command_count": sum(len(run["changed_commands"]) for run in selected),
            "actual_filesystem_reads": None,
            "actual_repeated_filesystem_reads": None,
        }
    return {
        "diagnostic_version": "read-paths-2",
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": f"Offline lexical correction of original {len(runs)}-run read-command proxies; no new coding/model runs",
        "experiment_directory": str(experiment),
        "source_commit": source_commit,
        "frozen_telemetry_sha256": source_hash,
        "corrected_telemetry_sha256": sha256(Path(telemetry.__file__).read_bytes()),
        "diagnostic_builder_sha256": sha256(Path(__file__).read_bytes()),
        "immutable_inputs": {
            "checked_files": len(before),
            "unchanged": before == after,
            "sha256": before,
        },
        "configurations": configurations,
        "runs": observations,
        "limitations": [
            "Original report/raw events/results are unchanged; this versioned diagnostic does not replace the primary experiment.",
            "Read-command counts are heuristic successful command_execution items containing recognized literal read commands. Path mentions are operands inferred from command text, not actual file opens, bytes read, unique files, or guaranteed I/O lower bounds.",
            "Unquoted newlines now separate shell commands. Quoted newlines remain argument data and are excluded as literal paths; unquoted/double-quoted backslash-newline is treated as a line continuation. Redirection, here-doc, pipe, OR and background operators remain conservative exclusions.",
            "Only standalone bash/sh/zsh -c/-lc wrappers are recursively unpacked. Mixed outer/wrapper commands are not flattened, preventing a subshell cd from changing the inferred outer directory.",
            "Declared-focus/test classifications use caller-visible focus paths and lexical path normalization only; no source or grading oracle selects or reads files during these diagnostics.",
            "Actual filesystem reads and actual repeated filesystem reads remain null. These proxy corrections do not change measured native token usage, execution timing, success, CPU, memory or cost conclusions.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Versioned daily read-command diagnostics",
        "",
        report["scope"] + ".",
        "",
        f"The preserved primary report recorded **{report['configurations']['A']['original']['observed_file_read_commands']['total']} A / {report['configurations']['B']['original']['observed_file_read_commands']['total']} B** recognized read-command items. This offline diagnostic reproduces those original values with the frozen parser, then applies the newline correction to the same raw events. Actual filesystem read counts remain unavailable.",
        "",
        "| Metric | A original | A corrected | B original | B corrected |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in report["configurations"]["A"]["original"]:
        values = [
            report["configurations"][arm][view][key]["total"]
            for arm in ("A", "B")
            for view in ("original", "corrected")
        ]
        lines.append("| " + key + " | " + " | ".join(map(str, values)) + " |")
    lines += [
        "",
        "Unquoted newlines previously disappeared during shell tokenization. For example, `cat tests/test_module.py` followed by `git diff -- src/module.py` on the next line could make `git`, `diff` and the changed source path look like additional `cat` operands. The corrected parser keeps those commands separate.",
        "",
        "## Individual original runs",
        "",
        "| Run | Read-command items old/new | Path mentions old/new | Declared-focus mentions old/new | Changed commands |",
        "|---|---:|---:|---:|---:|",
    ]
    for run in report["runs"]:
        old, new = run["original"], run["corrected"]
        lines.append(
            f"| {run['run_id']} | {old['observed_file_read_commands']}/{new['observed_file_read_commands']} | {old['recognized_path_mentions']}/{new['recognized_path_mentions']} | {old['declared_focus_path_mentions']}/{new['declared_focus_path_mentions']} | {len(run['changed_commands'])} |"
        )
    lines += [
        "",
        "## Integrity and limits",
        "",
        f"Frozen parser source: `{report['source_commit']}`; SHA-256 `{report['frozen_telemetry_sha256']}`.",
        "",
        f"Corrected parser SHA-256: `{report['corrected_telemetry_sha256']}`.",
        "",
        f"All {report['immutable_inputs']['checked_files']} input files were SHA-256 checked before and after; none changed. No commands from the event streams were executed.",
        "",
    ]
    lines += ["- " + limitation for limitation in report["limitations"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=ROOT / ".local/daily-v1/formal-20-v1")
    parser.add_argument(
        "--output-prefix", type=Path, default=ROOT / "benchmarks/daily-read-diagnostics"
    )
    arguments = parser.parse_args(argv)
    prefix = arguments.output_prefix.resolve()
    json_path, markdown_path = prefix.with_suffix(".json"), prefix.with_suffix(".md")
    if json_path.exists() or markdown_path.exists():
        parser.error("Diagnostic outputs already exist; choose a fresh versioned prefix")
    report = diagnose(arguments.experiment)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("x") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    with markdown_path.open("x") as stream:
        stream.write(markdown(report))
    print(
        json.dumps(
            {
                "json": str(json_path),
                "markdown": str(markdown_path),
                "configurations": report["configurations"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
