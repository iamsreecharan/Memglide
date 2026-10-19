"""Compare real scheduler/dashboard bookkeeping against a pinned application baseline.

Uses virtual scheduler ticks and no-op indexing, not live idle-time or repository
scan measurements. No model requests. Run with uv run python -m
benchmarks.saas_scheduler_efficiency --output /path/to/report.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
import types
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import patch

from memglide.core.indexer import Indexer
from memglide.core.watcher import RepositoryWatcher
from memglide.service import Service
from memglide.storage.database import Database

BASELINE = "6de6f150aaa90fba14e49439723a8139c03217eb"
ROOT = Path(__file__).resolve().parents[1]


def old_module(relative: str, name: str) -> tuple[types.ModuleType, str]:
    source = subprocess.check_output(["git", "show", f"{BASELINE}:{relative}"], cwd=ROOT)
    module = types.ModuleType(name)
    exec(compile(source, f"{BASELINE}:{relative}", "exec"), module.__dict__)
    return module, hashlib.sha256(source).hexdigest()


class Clock:
    def __init__(self) -> None:
        self.now = 100.0
        self.remaining = 60

    def wait(self, seconds: float) -> bool:
        if not self.remaining:
            return True
        self.remaining -= 1
        self.now = round(self.now + seconds, 3)
        return False

    def monotonic(self) -> float:
        return self.now

    def is_set(self) -> bool:
        return False


def seed(db: Database) -> None:
    stats = json.dumps(
        {"ignored_files": [{"path": f"ignored-{n}", "reason": "fixture"} for n in range(1000)]}
    )
    with db.connect() as conn:
        conn.executemany(
            "INSERT INTO projects(id,path,name,created_at,index_stats) VALUES(?,?,?,?,?)",
            [(f"p{n}", f"/fixture/{n}", f"fixture-{n}", n, stats) for n in range(25)],
        )
        conn.executemany(
            "INSERT INTO events VALUES(?,'p0',NULL,'fixture','{}',?)",
            [(f"e{n}", n) for n in range(600)],
        )


def scheduler(cls: Any, db: Database) -> dict[str, Any]:
    class NoopIndex:
        def __init__(self) -> None:
            self.scans: list[str] = []

        def list_projects(self) -> list[dict[str, Any]]:
            return Indexer(db).list_projects()

        def reindex(self, pid: str) -> None:
            self.scans.append(pid)

    index = NoopIndex()
    watcher = cls(db, index)
    clock = Clock()
    watcher._stop = clock
    connections = 0
    decoded_bytes = 0
    connect = db.connect
    loads = json.loads

    @contextmanager
    def counted_connect():
        nonlocal connections
        connections += 1
        with connect() as conn:
            yield conn

    def counted_loads(value: Any, *args: Any, **kwargs: Any) -> Any:
        nonlocal decoded_bytes
        decoded_bytes += len(value.encode("utf-8")) if isinstance(value, str) else len(value)
        return loads(value, *args, **kwargs)

    with (
        patch.object(db, "connect", counted_connect),
        patch("time.monotonic", clock.monotonic),
        patch("json.loads", counted_loads),
    ):
        wall = time.perf_counter()
        cpu = time.process_time()
        watcher._run()
        cpu = time.process_time() - cpu
        wall = time.perf_counter() - wall
    return {
        "connections": connections,
        "decoded_json_bytes": decoded_bytes,
        "noop_scan_calls": len(index.scans),
        "scan_project_sequence": index.scans,
        "compute_wall_seconds": wall,
        "process_cpu_seconds": cpu,
    }


def dashboard(cls: Any, db: Database) -> tuple[dict[str, Any], dict[str, Any]]:
    service = cls(db.path)
    try:
        events_fetched = 0
        cleanup = service.memory.cleanup
        list_sessions = service.memory.list_sessions
        rows = service.db.rows

        def counted_rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
            nonlocal events_fetched
            result = rows(sql, params)
            if sql.startswith("SELECT * FROM events"):
                events_fetched += len(result)
            return result

        with (
            patch.object(service.memory, "cleanup", wraps=cleanup) as cleanups,
            patch.object(service.memory, "list_sessions", wraps=list_sessions) as lists,
            patch.object(service.db, "rows", counted_rows),
        ):
            result = service.overview()
        return (
            {
                "cleanup_calls": cleanups.call_count,
                "session_list_calls": lists.call_count,
                "event_rows_fetched": events_fetched,
            },
            result,
        )
    finally:
        service.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    old_watcher, watcher_sha = old_module("src/memglide/core/watcher.py", "old_watcher")
    old_service, service_sha = old_module("src/memglide/service.py", "old_service")
    with tempfile.TemporaryDirectory(prefix="memglide-bookkeeping-") as directory:
        db = Database(Path(directory) / "state.db")
        seed(db)
        before = scheduler(old_watcher.RepositoryWatcher, db)
        after = scheduler(RepositoryWatcher, db)
        assert before["scan_project_sequence"] == after["scan_project_sequence"]
        dash_before, response_before = dashboard(old_service.Service, db)
        dash_after, response_after = dashboard(Service, db)
        assert response_before == response_after
        result = {
            "schema_version": 1,
            "baseline_git_ref": BASELINE,
            "baseline_watcher_sha256": watcher_sha,
            "baseline_service_sha256": service_sha,
            "candidate_source_sha256": {
                name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ("src/memglide/core/watcher.py", "src/memglide/service.py")
            },
            "fixture": {
                "projects": 25,
                "ignored_report_entries_per_project": 1000,
                "events": 600,
                "virtual_ticks": 60,
                "virtual_seconds_per_tick": 0.2,
                "poll_interval_seconds": 5,
            },
            "scheduler_before": before,
            "scheduler_after": after,
            "scheduler_scan_sequence_equal": True,
            "dashboard_before": dash_before,
            "dashboard_after": dash_after,
            "dashboard_response_equal": True,
            "model_requests": 0,
            "limitations": [
                "Scheduler uses virtual time; waits and repository scans are not performed.",
                "Compute durations measure only this fixture, not live daemon or model latency.",
                "Baseline is actual pinned watcher/service source; both use current DB and imported helpers.",
                "This tests bookkeeping, not end-to-end historical application performance.",
                "No model token, billed-cost or native-task saving established.",
            ],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "scheduler_connections": [before["connections"], after["connections"]],
                "decoded_json_bytes": [before["decoded_json_bytes"], after["decoded_json_bytes"]],
                "dashboard_events": [
                    dash_before["event_rows_fetched"],
                    dash_after["event_rows_fetched"],
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
