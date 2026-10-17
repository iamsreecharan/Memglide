"""Compare fixed rankers on previously evaluated Atlas development queries.

This experiment is for development selection. It is not an unseen validation
set, a model coding benchmark, or evidence of actual billed-token savings.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import UTC, datetime
from pathlib import Path

from benchmarks.compare_components import capture_provenance
from benchmarks.corpus import task_definitions
from benchmarks.probe import _make_seed, coverage_proxy
from benchmarks.refinement_eval import frozen_indexer
from benchmarks.retrieval_experiment import ranking_metrics, unique_paths
from memglide.service import Service


def run(output: Path) -> dict:
    if output.exists():
        raise ValueError("Use a fresh output directory to preserve measurements")
    output.mkdir(parents=True)
    before = capture_provenance()
    rows = []
    commits, versions = {}, {}
    for language in ("python", "typescript"):
        repository = output / language
        commits[language] = _make_seed(language, repository)
        service = Service(output / (language + "-state") / "memglide.db")
        try:
            project = service.indexer.add_project(str(repository))
            searches = {"refined": service.indexer.search}
            for policy in ("previous", "legacy"):
                indexer, versions[policy] = frozen_indexer(service.db, policy)
                searches[policy] = indexer.search
            original = service.indexer.search
            for task in task_definitions():
                if task["language"] != language:
                    continue
                for policy, search in searches.items():
                    hits = search(project["id"], task["prompt"], limit=100, refresh=False)

                    def fixed_search(*_args, **kwargs):
                        return hits[: kwargs.get("limit", 20)]

                    service.indexer.search = fixed_search
                    session = service.memory.start_session(project["id"], task["prompt"])
                    try:
                        context = service.context.get_context(
                            session["id"], task["prompt"], level=2, budget=8000
                        )
                        coverage = coverage_proxy(task, context)
                        rows.append(
                            {
                                "task_id": task["id"],
                                "policy": policy,
                                **ranking_metrics(unique_paths(hits), task["target_files"][0]),
                                "file_coverage": coverage["target_file_coverage_fraction"],
                                "declaration_visible": coverage[
                                    "expected_declaration_visible_fraction"
                                ],
                                "context_files": coverage["returned_files"],
                                "context_file_count": len(coverage["returned_files"]),
                                "estimated_planning_tokens": context["estimated_tokens"],
                                "output_json_bytes": len(
                                    json.dumps(context, ensure_ascii=False).encode()
                                ),
                                "ranked_candidates": [
                                    {
                                        key: hit.get(key)
                                        for key in ("path", "symbol", "score", "reason")
                                    }
                                    for hit in hits
                                ],
                            }
                        )
                        (output / "runs.json").write_text(json.dumps(rows, indent=2) + "\n")
                    finally:
                        service.memory.end_session(session["id"])
                        service.indexer.search = original
        finally:
            service.close()
    after = capture_provenance()
    report = {
        "created_at": datetime.now(UTC).isoformat(),
        "scope": "Previously evaluated Atlas development tasks, frozen rankers and common current context packer. No model calls or timing comparisons. Legacy is eligible; no unseen results used for ranking selection.",
        "selection_priority": "Preserve target-file/declaration coverage, then improve primary-file MRR/hit@1 and reduce context bytes/files. Legacy, previous and refined are all comparators eligible for default selection. Unseen evaluation is separate and cannot be used for iterative tuning.",
        "commits": commits,
        "frozen_rankers": versions,
        "source_before": before,
        "source_after": after,
        "source_unchanged": before["source_tree_sha256"] == after["source_tree_sha256"],
        "summary": {
            policy: {
                name: statistics.mean(row[name] for row in rows if row["policy"] == policy)
                for name in (
                    "primary_file_hit_at_1",
                    "primary_file_reciprocal_rank",
                    "file_coverage",
                    "declaration_visible",
                    "context_file_count",
                    "estimated_planning_tokens",
                    "output_json_bytes",
                )
            }
            for policy in ("refined", "previous", "legacy")
        },
        "runs": rows,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    completed = run(args.output.resolve())
    raise SystemExit(not completed["source_unchanged"])
