"""Local synthetic preparation CPU/RSS probe; no model or agent dispatch exists.

Run only on a quiet host: python -m benchmarks.profile_router_v2 --output NEW_DIR.
The public astronomy task is development calibration, never held-out evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ARMS = ("B", "V1", "C")
TASK = "Orbital phase should clamp negative elapsed duration to zero before wrapping."
TARGET = "orbital_phase.py"
SCOPE = (
    "Fresh worker Python process; SELF peak RSS includes interpreter, imports, fixture setup, "
    "approval/index and preparation. Not incremental preparation memory or RSS savings. "
    "Own-process CPU excludes Git/parser children; waited-child CPU is separate. "
    "Child peak is maximum waited child, not a simultaneous sum; never add peaks. Local "
    "synthetic development fixtures, not held-out coding outcomes or model economics."
)


def _new_directory(path: Path) -> Path:
    path = path.absolute()
    if path.resolve(strict=False) != path or not path.parent.is_dir():
        raise ValueError("artifact directory requires a canonical existing parent")
    path.mkdir(exist_ok=False)
    return path


def plan(repeats: int, sizes: list[int]) -> list[dict[str, Any]]:
    if type(repeats) is not int or not 1 <= repeats <= 6:
        raise ValueError("repeats must be between 1 and 6")
    if not sizes or len(sizes) > 2 or len(set(sizes)) != len(sizes):
        raise ValueError("provide one or two distinct fixture sizes")
    if any(type(size) is not int or not 2 <= size <= 100 for size in sizes):
        raise ValueError("fixture files must be between 2 and 100")
    rows: list[dict[str, Any]] = []
    for repeat in range(repeats):
        for size_index, files in enumerate(sizes):
            offset = repeat % 3
            order = ARMS[offset:] + ARMS[:offset]
            if size_index % 2:
                order = tuple(reversed(order))
            rows.extend({"repeat": repeat + 1, "files": files, "arm": arm} for arm in order)
    return rows


def fixture(root: Path, files: int, file_bytes: int) -> dict[str, str]:
    if type(files) is not int or not 2 <= files <= 100:
        raise ValueError("fixture files must be between 2 and 100")
    if type(file_bytes) is not int or not 128 <= file_bytes <= 16_384:
        raise ValueError("file bytes must be between 128 and 16384")
    sources = {}
    for index in range(files):
        name = TARGET if index == 0 else f"coordinate_bin_{index:03}.py"
        source = (
            "def orbital_phase(period, elapsed):\n    return elapsed % period\n"
            if index == 0 else f"def coordinate_bin_{index:03}(value):\n    return value + {index}\n"
        )
        source += "#" + "x" * (file_bytes - len(source.encode()) - 2) + "\n"
        (root / name).write_text(source, encoding="utf-8", newline="")
        sources[name] = source
    return sources


def fidelity(response: dict[str, Any], sources: dict[str, str]) -> dict[str, Any]:
    """Independently compare complete delivered bytes to this controlled fixture."""
    from memglide.integrations.preload import TASK_SEPARATOR

    selected = [row["path"] for row in response.get("files", [])]
    exact = False
    if response.get("mode") == "passthrough":
        exact = response.get("prompt") == TASK and not selected
    else:
        try:
            bundle = json.loads(response["prompt"].split(TASK_SEPARATOR, 1)[0])
            delivered = bundle["memglide_sources"]
            exact = (
                response["prompt"].endswith(TASK_SEPARATOR + TASK)
                and len(delivered) == len(selected) == len(set(selected))
                and {row["path"] for row in delivered} == set(selected)
                and all(row["content"] == sources.get(row["path"]) for row in delivered)
                and all(
                    row["sha256"] == hashlib.sha256(sources[row["path"]].encode()).hexdigest()
                    for row in response["files"]
                )
            )
        except (ValueError, KeyError, TypeError):
            exact = False
    return {"exact_treatment_fidelity": exact, "expected_target_delivered": selected == [TARGET]}


def peak_rss() -> dict[str, Any]:
    if sys.platform != "linux":
        return {"bytes": None, "reason": "Linux-only ru_maxrss scaling; unavailable here"}
    import resource

    return {
        "bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "reason": "observed Linux ru_maxrss KiB multiplied by 1024",
    }


def child_usage() -> dict[str, Any]:
    if sys.platform != "linux":
        return {"cpu_seconds": None, "peak_rss_bytes": None}
    import resource

    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"cpu_seconds": usage.ru_utime + usage.ru_stime, "peak_rss_bytes": usage.ru_maxrss * 1024}


def _cpu_difference(after: dict[str, Any], before: dict[str, Any]) -> float | None:
    return None if after["cpu_seconds"] is None else after["cpu_seconds"] - before["cpu_seconds"]


def worker(directory: Path, arm: str, files: int, file_bytes: int) -> dict[str, Any]:
    if arm not in ARMS:
        raise ValueError("unknown arm")
    child_wall, child_cpu = time.perf_counter(), time.process_time()
    children_started = child_usage()
    directory = _new_directory(directory)
    root = directory / "repository"
    root.mkdir()
    sources = fixture(root, files, file_bytes)
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True, timeout=10)
    from memglide.core.indexer import Indexer
    from memglide.integrations.preload import prepare_prompt
    from memglide.storage.database import Database
    if arm != "B":
        from memglide.integrations.auto_preload import prepare_task_prompt

    database = Database(directory / "state" / "state.db")
    index_wall, index_cpu = time.perf_counter(), time.process_time()
    project = Indexer(database).add_project(str(root))["id"]
    indexed_wall, indexed_cpu = time.perf_counter(), time.process_time()
    children_indexed = child_usage()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    response = (
        prepare_prompt(TASK, project_id=project, db_path=database.path,
                       focus_paths=[TARGET], context_format="compact-prefix")
        if arm == "B" else
        prepare_task_prompt(TASK, project_id=project, db_path=database.path, enabled=True,
                            selection_policy="v1" if arm == "V1" else "v2")
    )
    elapsed_wall, elapsed_cpu = time.perf_counter() - started_wall, time.process_time() - started_cpu
    children_prepared = child_usage()
    rss = peak_rss()  # Capture before independent fidelity validation/report serialization.
    return {
        "arm": arm, "fixture_files": files, "fixture_source_bytes": sum(len(s.encode()) for s in sources.values()),
        "fixture_sha256": hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest(),
        "setup_wall_seconds": indexed_wall - child_wall,
        "setup_cpu_seconds": indexed_cpu - child_cpu,
        "setup_waited_children_cpu_seconds": _cpu_difference(children_indexed, children_started),
        "initial_index_wall_seconds": indexed_wall - index_wall,
        "initial_index_cpu_seconds": indexed_cpu - index_cpu,
        "preparation_wall_seconds": elapsed_wall, "preparation_cpu_seconds": elapsed_cpu,
        "preparation_waited_children_cpu_seconds": _cpu_difference(children_prepared, children_indexed),
        "setup_max_waited_child_rss_bytes": children_indexed["peak_rss_bytes"],
        "whole_max_waited_child_rss_bytes": children_prepared["peak_rss_bytes"],
        "waited_child_peak_scope": "maximum waited child over process lifetime; not simultaneous sum; do not add parent and child peaks",
        "child_wall_through_preparation_seconds": time.perf_counter() - child_wall,
        "child_cpu_through_preparation_seconds": time.process_time() - child_cpu,
        "peak_python_self_rss_bytes": rss["bytes"], "peak_rss_method": rss["reason"],
        "decision": response.get("automatic_selection", {}).get("decision", "FOCUSED_SOURCE" if response["mode"] == "preloaded" else "SKIP"),
        "reason": response["reason"], "selected_paths": [row["path"] for row in response["files"]],
        "context_bytes": response["context_bytes"], "source_versions": {row["path"]: row["sha256"] for row in response["files"]},
        "api_retrieval_wall_seconds": response.get("automatic_selection", {}).get("retrieval_wall_seconds"),
        "model_calls": 0, "scope": SCOPE, **fidelity(response, sources),
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for files in sorted({row["files"] for row in rows}):
        for arm in ARMS:
            selected = [row for row in rows if row["files"] == files and row["arm"] == arm]
            valid = [row["observation"] for row in selected if row.get("observation") is not None]
            summary: dict[str, Any] = {"files": files, "arm": arm, "attempts": len(selected), "observed": len(valid), "failed_workers": len(selected) - len(valid)}
            for key in ("setup_wall_seconds", "setup_cpu_seconds", "setup_waited_children_cpu_seconds", "preparation_wall_seconds", "preparation_cpu_seconds", "preparation_waited_children_cpu_seconds", "peak_python_self_rss_bytes", "whole_max_waited_child_rss_bytes", "context_bytes"):
                values = [row[key] for row in valid if row[key] is not None]
                summary[key] = {"mean": statistics.mean(values), "median": statistics.median(values)} if values else None
            summary["fidelity_passes"] = sum(row["exact_treatment_fidelity"] for row in valid)
            summary["expected_selection_passes"] = sum(row["expected_target_delivered"] for row in valid)
            summaries.append(summary)
    return summaries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--files", type=int, nargs="+", default=[8, 100])
    parser.add_argument("--file-bytes", type=int, default=2048)
    parser.add_argument("--worker", choices=ARMS, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    assignments = plan(args.repeats, args.files)
    if not 128 <= args.file_bytes <= 16_384:
        parser.error("file bytes must be between 128 and 16384")
    if args.worker:
        if len(args.files) != 1:
            parser.error("worker requires exactly one fixture size")
        print(json.dumps(worker(args.output, args.worker, args.files[0], args.file_bytes), sort_keys=True))
        return 0
    output = _new_directory(args.output)
    rows = []
    for index, assignment in enumerate(assignments):
        label = f"{index + 1:03}-{assignment['arm']}-{assignment['files']}"
        command = [sys.executable, "-m", "benchmarks.profile_router_v2", "--worker", assignment["arm"], "--output", str(output / label), "--files", str(assignment["files"]), "--file-bytes", str(args.file_bytes)]
        launched = time.perf_counter()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=90)
            (output / (label + ".stdout.log")).write_text(process.stdout, encoding="utf-8")
            (output / (label + ".stderr.log")).write_text(process.stderr, encoding="utf-8")
            observation = json.loads(process.stdout) if process.returncode == 0 else None
            rows.append({**assignment, "worker_process_wall_seconds": time.perf_counter() - launched, "returncode": process.returncode, "observation": observation})
        except (subprocess.SubprocessError, ValueError, OSError) as exc:
            if isinstance(exc, subprocess.TimeoutExpired):
                for suffix, captured in (("stdout", exc.stdout), ("stderr", exc.stderr)):
                    value = captured.decode("utf-8", errors="replace") if isinstance(captured, bytes) else captured or ""
                    (output / (label + "." + suffix + ".log")).write_text(value, encoding="utf-8")
            rows.append({**assignment, "observation": None, "error": type(exc).__name__ + ": " + str(exc)})
    report = {"version": 1, "task": TASK, "scope": SCOPE, "file_bytes": args.file_bytes,
              "python_version": sys.version, "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cache_conditions": "fresh Python/database per observation; OS cache uncontrolled; no provider requests",
              "model_calls": 0, "assignments": rows, "summary": summarize(rows)}
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(output / "report.json"))
    return int(any(row.get("observation") is None or not row["observation"]["exact_treatment_fidelity"] or not row["observation"]["expected_target_delivered"] for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
