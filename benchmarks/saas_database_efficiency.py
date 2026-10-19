"""Measure SQLite VM work and storage on one unchanged, synthetic local fixture.

Run with ``uv run python -m benchmarks.saas_database_efficiency --output /tmp/db-probe``.
The output stem must be unused: existing observations are never overwritten.
This makes no model requests and measures neither elapsed time nor model savings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from memglide.storage.database import Database

NEW_INDEXES = (
    "symbol_files", "session_projects", "memory_source_paths", "retrieval_sessions",
    "retrieval_projects", "retrieval_created", "passport_sessions", "event_projects",
    "event_created",
)
TABLES = (
    "projects", "files", "symbols", "sessions", "memories", "memory_sources",
    "retrievals", "passports", "events", "settings", "file_search", "schema_migrations",
)
QUERIES: dict[str, tuple[str, tuple[Any, ...]]] = {
    "global_recent_events": (
        "SELECT * FROM events ORDER BY created_at DESC LIMIT 500", (),
    ),
    "project_recent_events": (
        "SELECT * FROM events WHERE project_id=? ORDER BY created_at DESC LIMIT 500", ("p99",),
    ),
    "global_recent_retrievals": (
        "SELECT id,session_id,project_id,query,level,budget,estimated_tokens,created_at "
        "FROM retrievals ORDER BY created_at DESC LIMIT 20", (),
    ),
    "project_sessions": (
        "SELECT * FROM sessions WHERE project_id=? ORDER BY created_at DESC,id", ("p99",),
    ),
    "source_invalidation_lookup": (
        "SELECT ms.memory_id FROM memory_sources ms JOIN memories m ON m.id=ms.memory_id "
        "JOIN sessions s ON s.id=m.session_id WHERE s.project_id=? AND ms.path=?",
        ("p99", "file0.py"),
    ),
    "delete_file_cascade": ("DELETE FROM files WHERE id=?", ("p99-f0",)),
    "delete_session_cascade": ("DELETE FROM sessions WHERE id=?", ("p99-s0",)),
}
EVENT_APPEND = (
    "INSERT INTO events VALUES(?,?,?,?,?,?)",
    ("new-write-event", "p99", "p99-s0", "context_retrieved", "{}", 6000.0),
)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def seed(conn: sqlite3.Connection) -> None:
    """Same fixed data, insertion order and valid relationships for both phases."""
    conn.execute("UPDATE schema_migrations SET applied_at=0")
    for p in range(100):
        project = f"p{p}"
        conn.execute(
            "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,1)",
            (project, "/unused/" + project, project),
        )
        for number in range(50):
            ident = f"{project}-{number}"
            file_id, session = f"{project}-f{number}", f"{project}-s{number}"
            name, stamp = f"file{number}.py", float(p * 50 + number)
            conn.execute(
                "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
                (file_id, project, name, "digest", "python", 20, stamp, 1, None, stamp),
            )
            conn.execute(
                "INSERT INTO symbols VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    ident, project, file_id, name, "value", "value", "function",
                    "def value():", 1, 2, 1,
                ),
            )
            conn.execute(
                "INSERT INTO sessions VALUES(?,?,?,?,?,?,?,NULL)",
                (session, project, "task", stamp, stamp, 1e12, 1e12),
            )
            conn.execute(
                "INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?)",
                (ident, session, "decision", "A claim", "A source", stamp, stamp, 0, ident),
            )
            conn.execute("INSERT INTO memory_sources VALUES(?,?,?)", (ident, name, "digest"))
            conn.execute(
                "INSERT INTO retrievals VALUES(?,?,?,?,?,?,?,?,?)",
                (ident, session, project, "value", 1, 1000, 10, stamp, "{}"),
            )
            conn.execute("INSERT INTO passports VALUES(?,?,?)", (ident, session, "{}"))
            for event in range(2):
                conn.execute(
                    "INSERT INTO events VALUES(?,?,?,?,?,?)",
                    (f"{ident}-{event}", project, session, "context_retrieved", "{}", stamp),
                )


def data_fingerprint(conn: sqlite3.Connection) -> str:
    # Ignore row traversal order, which a new index can legitimately change.
    records = {
        table: sorted(tuple(row) for row in conn.execute(f"SELECT * FROM {table}"))
        for table in TABLES
    }
    return fingerprint(records)


def measure(
    conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]
) -> dict[str, Any]:
    """Count one SQLite progress callback per VM instruction, including cascades.

    Transaction control, EXPLAIN, integrity checks and rollback are outside the
    measured statement. Every mutation rolls back, so later probes see identical
    data. Progress callbacks add overhead; timings are deliberately not reported.
    """
    steps = 0

    def tick() -> int:
        nonlocal steps
        steps += 1
        return 0

    conn.execute("BEGIN")
    try:
        conn.set_progress_handler(tick, 1)
        rows = [tuple(row) for row in conn.execute(sql, params)]
    finally:
        conn.set_progress_handler(None, 0)
        conn.rollback()
    return {
        "vm_steps": steps,
        "returned_rows": len(rows),
        "result_multiset_sha256": fingerprint(sorted(rows)),
        "plan": [
            row["detail"] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params)
        ],
    }


def probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="memglide-db-probe-") as directory:
        db = Database(Path(directory) / "state.db")
        with db.connect() as conn:
            definitions = {
                row["name"]: row["sql"]
                for row in conn.execute("SELECT name,sql FROM sqlite_master WHERE type='index'")
                if row["name"] in NEW_INDEXES
            }
            if set(definitions) != set(NEW_INDEXES):
                raise ValueError("Expected exactly the nine candidate index definitions")
            for name in NEW_INDEXES:
                conn.execute(f"DROP INDEX {name}")
            seed(conn)
        with db.connect() as conn:
            result: dict[str, Any] = {
                "status": "ok",
                "fixture_counts": {
                    table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                    for table in TABLES
                },
                "queries": {},
                "data_sha256_before": data_fingerprint(conn),
                "database_bytes_before": (
                    conn.execute("PRAGMA page_count").fetchone()[0]
                    * conn.execute("PRAGMA page_size").fetchone()[0]
                ),
            }
            for label, (sql, params) in QUERIES.items():
                result["queries"][label] = {"before": measure(conn, sql, params)}
            result["event_append"] = {"before": measure(conn, *EVENT_APPEND)}
            for name in NEW_INDEXES:
                conn.execute(definitions[name])
            for label, (sql, params) in QUERIES.items():
                row = result["queries"][label]
                row["after"] = measure(conn, sql, params)
                row["same_result_multiset"] = (
                    row["before"]["result_multiset_sha256"]
                    == row["after"]["result_multiset_sha256"]
                )
            result["event_append"]["after"] = measure(conn, *EVENT_APPEND)
            sizes = {
                row["name"]: row["bytes"]
                for row in conn.execute(
                    "SELECT name,sum(pgsize) AS bytes FROM dbstat GROUP BY name"
                )
            }
            result["index_storage_bytes"] = {name: sizes[name] for name in NEW_INDEXES}
            result["new_index_bytes"] = sum(result["index_storage_bytes"].values())
            result["database_bytes_after"] = (
                conn.execute("PRAGMA page_count").fetchone()[0]
                * conn.execute("PRAGMA page_size").fetchone()[0]
            )
            result["data_sha256_after"] = data_fingerprint(conn)
            result["data_unchanged"] = (
                result["data_sha256_before"] == result["data_sha256_after"]
            )
            result["foreign_key_violations"] = [tuple(r) for r in conn.execute("PRAGMA foreign_key_check")]
            result["integrity"] = conn.execute("PRAGMA quick_check").fetchone()[0]
            if not result["data_unchanged"] or not all(
                row["same_result_multiset"] for row in result["queries"].values()
            ) or result["foreign_key_violations"] or result["integrity"] != "ok":
                result["status"] = "failed_validation"
            return result


def render(report: dict[str, Any]) -> str:
    lines = [
        "# SQLite history and lifecycle efficiency",
        "",
        "This local component probe measures SQLite VM instructions, query plans and B-tree "
        "storage. It makes no model calls and measures no milliseconds, tokens, model cost "
        "or SaaS throughput.",
        "",
        f"All {len(report['attempts'])} requested attempts are retained. Each creates the same "
        "100-project fixture, including 5,000 rows in each main child table and 10,000 events. "
        "The old-schema simulation drops only the nine new indexes; existing indexes, schema, "
        "data, query arguments and insertion order stay the same. No ANALYZE, cache or "
        "planner forcing is used. The indexed phase restores those exact definitions. "
        "Every measured mutation rolls back. A full data digest, foreign-key check and "
        "quick_check verify the fixture survives.",
        "",
    ]
    for number, attempt in enumerate(report["attempts"], 1):
        lines += [
            "| Attempt | Query | Before VM instructions | After VM instructions | Same rows |",
            "| --- | --- | ---: | ---: | --- |",
        ]
        if attempt["status"] == "error":
            lines.append(f"| {number} | ERROR: {attempt['error']} | — | — | unknown |")
            continue
        for label, row in attempt["queries"].items():
            lines.append(
                f"| {number} | {label} | {row['before']['vm_steps']:,} | "
                f"{row['after']['vm_steps']:,} | {row['same_result_multiset']} |"
            )
        append = attempt["event_append"]
        lines += [
            "",
            f"Attempt {number} storage: {attempt['new_index_bytes']:,} bytes in the nine new "
            f"indexes; database {attempt['database_bytes_before']:,} → "
            f"{attempt['database_bytes_after']:,} bytes. One rolled-back event append takes "
            f"{append['before']['vm_steps']} → {append['after']['vm_steps']} VM instructions. "
            "The extra write work and index storage are a real tradeoff; this is one insert "
            "shape, not a measured write-throughput percentage.",
            "",
        ]
    lines += [
        "Plans, complete per-query observations and per-index storage are in the JSON. "
        "New indexes remove temporary ordering trees for the measured history queries "
        "and full child-table scans for the measured foreign-key cascades. Composite "
        "project/session-leading indexes also serve foreign-key checks; existing prefix "
        "indexes are reused instead of duplicated. Upgrades use additive IF NOT EXISTS "
        "DDL and do not rewrite stored claims, source text or public responses.",
        "",
        "Limitations: fixed synthetic data and one SQLite version; index selectivity and "
        "VM programs vary by workload and engine. Before always precedes after because "
        "the fixture is upgraded in place. Warm caches do not establish elapsed-time "
        "improvement here. The first upgrade must build indexes and can take a database "
        "write lock. Real-world billing, model latency and hosted scalability remain unknown.",
        "",
        "An earlier exploratory probe is recorded separately in the JSON. Its global recent-event "
        "query reported 152,775 → 5,508 instructions, versus 152,509 → 5,508 in these runs; "
        "the other six query pairs, append counts and index sizes matched. Its fixture setup "
        "and preliminary inspections were not frozen, so it is not pooled into the repeated "
        "observations or treated as independent model evidence.",
        "",
        "Reproduce without changing these results:",
        "",
        "```sh",
        "uv run python -m benchmarks.saas_database_efficiency --output /tmp/memglide-db-probe",
        "```",
        "",
        "The output stem must be unused. All requested runs, including errors, are written "
        "before the process reports failure. No automatic retry or attempt replacement occurs.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Unused output filename stem")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 20:
        parser.error("--repeats must be between 1 and 20")
    json_path, md_path = args.output.with_suffix(".json"), args.output.with_suffix(".md")
    if json_path.exists() or md_path.exists():
        parser.error("Output exists; use an unused stem to preserve every observation")
    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sqlite_version": sqlite3.sqlite_version,
        "measurement": "SQLite VM progress callbacks at instruction interval 1; not time or tokens",
        "old_schema_simulation": "Only the nine named indexes are dropped before seeding",
        "index_names": NEW_INDEXES,
        "queries": QUERIES,
        "event_append_query": EVENT_APPEND,
        "exploratory_probe": {
            "scope": "Preliminary same-scale fixture; setup and inspections not frozen",
            "global_recent_events": [152775, 5508],
            "project_recent_events": [31912, 1216],
            "global_recent_retrievals": [85149, 268],
            "project_sessions": [16312, 863],
            "source_invalidation_lookup": [15820, 1024],
            "delete_file_cascade": [35067, 80],
            "delete_session_cascade": [70310, 368],
            "new_index_bytes": 839680,
            "event_append": [44, 55],
        },
        "attempts": [],
    }
    for number in range(args.repeats):
        try:
            attempt = probe()
        except Exception as exc:
            attempt = {"status": "error", "error": f"{type(exc).__name__}: {exc}"}
        report["attempts"].append({"attempt": number + 1, **attempt})
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render(report), encoding="utf-8")
    if any(attempt["status"] != "ok" for attempt in report["attempts"]):
        raise SystemExit("Probe failure retained in the output reports")
    print(json.dumps({"report": str(json_path), "attempts": len(report["attempts"])}))


if __name__ == "__main__":
    main()
