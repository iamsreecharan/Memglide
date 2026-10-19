"""Paired synthetic search-cost check; no coding model or source parsing occurs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

from memglide.core import indexer as indexing
from memglide.service import Service


class _SearchRun(TypedDict):
    case: str
    policy: str
    repeat: int
    order_within_pair: int
    query_characters: int
    wall_seconds: float
    process_cpu_seconds: float
    returned_paths: list[str]
    returned_count: int


class _SearchReport(TypedDict):
    created_at: str
    scope: str
    files: int
    source_bytes: int
    document_sha256: str
    terms_per_document: int
    build_seconds: float
    source_sha256: str
    repeats: int
    runs: list[_SearchRun]
    conditions: str


def run(output: Path, files: int, repeats: int) -> _SearchReport:
    if output.exists():
        raise ValueError("Use a new output directory to retain all measurements")
    output.mkdir(parents=True)
    source = " ".join(f"w{number:04d}" for number in range(650)) + "\n"
    terms = source.strip().split()
    root = output / "repository"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    service = Service(output / "state" / "memglide.db")
    original_limit = indexing.MAX_FTS_RANK_TERMS
    try:
        project = service.indexer.add_project(str(root))
        built = time.perf_counter()
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        rows = []
        for number in range(files):
            path = f"document_{number:05d}.txt"
            (root / path).write_text(source)
            rows.append(
                (
                    f"file{number}",
                    project["id"],
                    path,
                    source_hash,
                    "text",
                    len(source),
                    0,
                    0,
                    None,
                    0,
                )
            )
        with service.db.connect() as conn:
            conn.executemany("INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)", rows)
            conn.executemany(
                "INSERT INTO file_search VALUES(?,?,?,?)",
                [(project["id"], row[2], "", source) for row in rows],
            )
        queries = {
            "short_common": " ".join(terms[:8]),
            "long_absent": " ".join(f"z{number:04d}" for number in range(650)),
            "long_common": source.strip(),
        }
        report: _SearchReport = {
            "created_at": datetime.now(UTC).isoformat(),
            "scope": "Paired FTS ranking/source-serialization stress check on manually populated fixture index; no symbols, repository rescan, source parsing, model requests or cost measurements. Not an end-to-end indexing benchmark.",
            "files": files,
            "source_bytes": files * len(source.encode()),
            "document_sha256": source_hash,
            "terms_per_document": len(terms),
            "build_seconds": time.perf_counter() - built,
            "source_sha256": hashlib.sha256(Path(indexing.__file__).read_bytes()).hexdigest(),
            "repeats": repeats,
            "runs": [],
            "conditions": "Same process, SQLite database, source bytes and queries; alternate policy order per repetition. Local caches shared and not flushed; CPU uses process_time. Remote resources unavailable.",
        }
        for repetition in range(1, repeats + 1):
            order = (
                ("all_terms", "informative_32")
                if repetition % 2
                else ("informative_32", "all_terms")
            )
            for case, query in queries.items():
                for policy in order:
                    indexing.MAX_FTS_RANK_TERMS = 10000 if policy == "all_terms" else 32
                    started, cpu_started = time.perf_counter(), time.process_time()
                    hits = service.indexer.search(project["id"], query, limit=20, refresh=False)
                    row: _SearchRun = {
                        "case": case,
                        "policy": policy,
                        "repeat": repetition,
                        "order_within_pair": order.index(policy) + 1,
                        "query_characters": len(query),
                        "wall_seconds": time.perf_counter() - started,
                        "process_cpu_seconds": time.process_time() - cpu_started,
                        "returned_paths": [hit["path"] for hit in hits],
                        "returned_count": len(hits),
                    }
                    report["runs"].append(row)
                    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
                    print(
                        json.dumps(
                            {key: value for key, value in row.items() if key != "returned_paths"}
                        ),
                        flush=True,
                    )
        return report
    finally:
        indexing.MAX_FTS_RANK_TERMS = original_limit
        service.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--files", default=20000, type=int)
    parser.add_argument("--repeats", default=2, type=int)
    arguments = parser.parse_args()
    if arguments.files < 1 or arguments.repeats < 1:
        parser.error("files and repeats must be positive")
    run(arguments.output.resolve(), arguments.files, arguments.repeats)
