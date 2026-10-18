"""Compare source payload bytes and local preparation, never provider cache hits."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

from memglide.core.indexer import Indexer
from memglide.integrations.preload import _EXPLANATION, TASK_SEPARATOR, prepare_prompt
from memglide.storage.database import Database


def common_prefix(left: bytes, right: bytes) -> int:
    return next(
        (i for i, pair in enumerate(zip(left, right)) if pair[0] != pair[1]),
        min(len(left), len(right)),
    )


def summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "p95": ordered[max(0, (len(ordered) * 95 + 99) // 100 - 1)],
    }


def run(output: Path, repeats: int) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    repository = output / "fixture"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    sources = {
        "calc.py": 'def total(values):\n    return sum(values)\n\ndef mean(values):\n    """Compute a café order mean, or None for no values."""\n    return total(values) / len(values) if values else None\n',
        "format.ts": "export const label = (value: number): string => String(value);\nexport const decorate = (value: number): string => `[${label(value)}]`;\n",
    }
    for name, body in sources.items():
        (repository / name).write_text(body, encoding="utf-8")
    database = output / "state.db"
    started = time.perf_counter()
    project = Indexer(Database(database)).add_project(str(repository))
    setup = time.perf_counter() - started
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    rows: list[dict[str, Any]] = []
    stable: dict[tuple[str, str], dict[str, Any]] = {}
    cases = {"single": ["calc.py"], "two_sources": ["format.ts", "calc.py"]}
    randomizer = random.Random(20261018)
    for case, paths in cases.items():
        for repeat in range(repeats):
            formats = ["legacy", "compact-prefix"]
            randomizer.shuffle(formats)
            for context_format in formats:
                value = prepare_prompt(
                    "Implement the next task with these files.",
                    project_id=project["id"],
                    db_path=database,
                    focus_paths=paths,
                    context_format=context_format,
                )
                assert value["mode"] == "preloaded"
                task = "Implement the next task with these files."
                raw = (
                    value["prompt"].removesuffix(TASK_SEPARATOR + task)
                    if context_format == "compact-prefix"
                    else value["prompt"][len(task) + 2 + len(_EXPLANATION) :]
                )
                evidence = json.loads(raw)["memglide_sources"]
                assert {row["path"]: row["content"] for row in evidence} == {
                    path: sources[path] for path in paths
                }
                assert {item["path"]: item["sha256"] for item in value["files"]} == {
                    path: hashlib.sha256(sources[path].encode()).hexdigest() for path in paths
                }
                rows.append(
                    {
                        "case": case,
                        "repeat": repeat + 1,
                        "format": context_format,
                        "context_bytes": value["context_bytes"],
                        "wall_seconds": value["preparation_wall_seconds"],
                        "cpu_seconds": value["preparation_cpu_seconds"],
                    }
                )
                stable[case, context_format] = value
    comparisons = []
    for case, paths in cases.items():
        for context_format in ("legacy", "compact-prefix"):
            left = prepare_prompt(
                "Alpha follow-up task.",
                project_id=project["id"],
                db_path=database,
                focus_paths=paths,
                context_format=context_format,
            )
            right = prepare_prompt(
                "Beta follow-up task.",
                project_id=project["id"],
                db_path=database,
                focus_paths=list(reversed(paths)),
                context_format=context_format,
            )
            if context_format == "compact-prefix":
                assert left["prompt"].endswith(TASK_SEPARATOR + "Alpha follow-up task.")
                assert right["prompt"].endswith(TASK_SEPARATOR + "Beta follow-up task.")
            observations = [r for r in rows if r["case"] == case and r["format"] == context_format]
            comparisons.append(
                {
                    "case": case,
                    "format": context_format,
                    "samples": len(observations),
                    "added_context_bytes": stable[case, context_format]["context_bytes"],
                    "raw_source_bytes": sum(len(sources[path].encode()) for path in paths),
                    "same_source_different_task_common_prefix_bytes": common_prefix(
                        left["prompt"].encode(), right["prompt"].encode()
                    ),
                    "wall_seconds": summary([r["wall_seconds"] for r in observations]),
                    "cpu_seconds": summary([r["cpu_seconds"] for r in observations]),
                }
            )
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before
    report = {
        "version": 1,
        "scope": "Local preparation component only; complete source bytes, native forwarded prompt prefix bytes and already imported API time. No Codex/model calls, measured model tokens, actual cache hits, billing or end-to-end speed claims.",
        "cold_approval_index_wall_seconds": setup,
        "source_hashes": {p: hashlib.sha256(s.encode()).hexdigest() for p, s in sources.items()},
        "database_unchanged": True,
        "rows": rows,
        "comparisons": comparisons,
        "provider_cached_tokens": None,
        "provider_uncached_tokens": None,
        "actual_cost_usd": None,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Compact source-prefix component comparison",
        "",
        report["scope"],
        "",
        "| Case | Format | Added bytes | Shared prefix bytes across changed tasks | Median local API ms |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in comparisons:
        lines.append(
            f"| {item['case']} | {item['format']} | {item['added_context_bytes']} | {item['same_source_different_task_common_prefix_bytes']} | {item['wall_seconds']['median'] * 1000:.3f} |"
        )
    lines += [
        "",
        "Common-prefix bytes concern the forwarded task only. Codex adds native instructions/history and controls session affinity. These byte measurements do not establish provider cache reuse or a live uncached-token reduction. Source ordering is canonical only in compact-prefix format. No stale source, missing code, cache-threshold padding or model classifier is introduced.",
        "",
    ]
    (output / "report.md").write_text("\n".join(lines))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repeats", type=int, default=40)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    result = run(args.output.resolve(), args.repeats)
    print(
        json.dumps(
            {
                "observations": len(result["rows"]),
                "database_unchanged": result["database_unchanged"],
            }
        )
    )


if __name__ == "__main__":
    main()
