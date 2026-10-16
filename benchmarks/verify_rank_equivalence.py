"""Check current IDF ranks against retained strategy observations; no model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks.compare_components import capture_provenance
from benchmarks.corpus import task_definitions
from benchmarks.retrieval_experiment import load_holdout
from memglide.service import Service

ROOT = Path(__file__).resolve().parents[1]


def verify(reference: Path, output: Path, state: Path) -> dict:
    if output.exists() or state.exists():
        raise ValueError("Use fresh output and state paths to preserve previous evidence")
    baseline = json.loads(reference.read_text())
    fixture_root = Path(baseline["provenance"]["raw_artifacts"]) / "fixtures"
    queries = {query["id"]: query for query in [*task_definitions(), *load_holdout()["queries"]]}
    before = capture_provenance()
    services: dict[str, tuple[Service, str]] = {}
    rows = []
    try:
        for prior in baseline["runs"]:
            if prior["strategy"] != "idf_lexical":
                continue
            query = queries[prior["query_id"]]
            repository = query["repository"]
            if repository not in services:
                service = Service(state / repository / "memglide.db")
                project = service.indexer.add_project(str(fixture_root / repository))
                services[repository] = service, project["id"]
            service, project_id = services[repository]
            hits = service.indexer.search(project_id, query["prompt"], limit=100, refresh=False)
            candidates = [
                {
                    key: hit.get(key)
                    for key in ("path", "symbol", "score", "reason", "start_line", "end_line")
                }
                for hit in hits
            ]
            rows.append(
                {
                    "query_id": prior["query_id"],
                    "split": prior["split"],
                    "equal": candidates == prior["ranked_candidates"],
                    "prior": prior["ranked_candidates"],
                    "current": candidates,
                }
            )
    finally:
        for service, _ in services.values():
            service.close()
    after = capture_provenance()
    report = {
        "scope": "Exact candidate/rank/score equivalence after document-frequency optimization. Previously evaluated development/validation queries; no independent new holdout, model calls or timing comparison.",
        "reference": str(reference),
        "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
        "queries": len(rows),
        "all_equal": bool(rows) and all(row["equal"] for row in rows),
        "source_before": before,
        "source_after": after,
        "source_unchanged": before["source_tree_sha256"] == after["source_tree_sha256"],
        "runs": rows,
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference", type=Path, default=ROOT / "benchmarks/retrieval-strategies.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.reference, args.output, args.state)
    print(json.dumps({key: result[key] for key in ("queries", "all_equal", "source_unchanged")}))
    raise SystemExit(not (result["all_equal"] and result["source_unchanged"]))
