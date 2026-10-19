"""Reproducible offline comparison of retrieval strategies, without a model request.

The Atlas development prompts are unchanged. Orion holdout queries are locked
before the first measurement. A primary target is one manually declared relevant
file, not a complete relevance judgment or proof of sufficient coding context.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import statistics
import subprocess
import time
import types
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from benchmarks.corpus import build_repository, task_definitions
from memglide.core.query import term_variants, tokens
from memglide.service import Service

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_PATH = ROOT / "benchmarks/retrieval_holdout.json"
HOLDOUT_SHA256 = "7c4d343fccc6e1b06badc702c2480d8c0151573be9f1fde2281e8a1e9073ba20"
LEGACY_REVISION = "39e8df30565783a686270f8a6f422e56e41e3776"
STRATEGIES = ("legacy", "idf_lexical", "bm25_files", "rrf", "rrf_mmr")
COMPLEXITY = {"idf_lexical": 0, "bm25_files": 1, "rrf": 2, "rrf_mmr": 3}
SELECTION_POLICY = (
    "Development set only: require all queries valid; maximize mean context target-file "
    "coverage at level 2 / budget 8000, then primary file hit@1, then primary-file MRR. "
    "Exact ties prefer IDF lexical, then BM25 files, then RRF, then RRF+MMR. "
    "The frozen legacy policy is a comparator, not an eligible new default. "
    "Write the selection lock before evaluating any holdout query. Do not tune on holdout."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_holdout(path: Path = HOLDOUT_PATH) -> dict[str, Any]:
    if digest(path) != HOLDOUT_SHA256:
        raise ValueError(
            "Holdout changed after pre-measurement lock; create a new version and disclose it"
        )
    manifest = json.loads(path.read_text(encoding="utf-8"))
    ids = [query["id"] for query in manifest["queries"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Holdout query identifiers must be unique")
    return manifest


def write_holdout_repository(manifest: dict[str, Any], name: str, destination: Path) -> None:
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Repository destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    for relative, source in manifest["repositories"][name]["files"].items():
        target = destination / relative
        if destination.resolve() not in target.resolve().parents:
            raise ValueError("Fixture path escapes repository")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")


def unique_paths(candidates: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(candidate["path"] for candidate in candidates))


def ranking_metrics(paths: list[str], target: str) -> dict[str, Any]:
    # Unique files, so ten declarations from a file count as one retrieved file.
    paths = list(dict.fromkeys(paths))
    rank = paths.index(target) + 1 if target in paths else None
    return {
        "primary_target_rank": rank,
        "primary_file_hit_at_1": int(rank is not None and rank <= 1),
        "primary_file_hit_at_3": int(rank is not None and rank <= 3),
        "primary_file_hit_at_5": int(rank is not None and rank <= 5),
        "primary_file_reciprocal_rank": 1 / rank if rank is not None else 0.0,
    }


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    if k < 1:
        raise ValueError("RRF k must be positive")
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, path in enumerate(dict.fromkeys(ranking), 1):
            scores[path] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def mmr_diversify(
    ranked: list[tuple[str, float]], documents: dict[str, str], relevance_weight: float = 0.85
) -> list[tuple[str, float]]:
    """Greedy MMR using token-set Jaccard redundancy; no embedding or synonym model."""
    if not 0 <= relevance_weight <= 1:
        raise ValueError("MMR relevance weight must be between zero and one")
    if not ranked:
        return []
    highest = max(score for _, score in ranked) or 1.0
    terms = {path: set(tokens(documents.get(path, ""))) for path, _ in ranked}
    pending = list(ranked)
    selected: list[tuple[str, float]] = []
    while pending:

        def utility(item: tuple[str, float]) -> float:
            path, score = item
            redundancy = max(
                (
                    len(terms[path] & terms[other]) / max(len(terms[path] | terms[other]), 1)
                    for other, _ in selected
                ),
                default=0.0,
            )
            return relevance_weight * score / highest - (1 - relevance_weight) * redundancy

        chosen = min(pending, key=lambda item: (-utility(item), item[0]))
        selected.append(chosen)
        pending.remove(chosen)
    # Preserve the chosen order when production context applies numeric scores.
    return [(path, float(len(selected) - rank)) for rank, (path, _) in enumerate(selected)]


def bm25_candidates(service: Service, project_id: str, query: str) -> list[dict[str, Any]]:
    words = sorted(set(tokens(query)))
    if not words:
        return []
    expression = " OR ".join(
        "(" + " OR ".join('"' + variant + '"' for variant in term_variants(word)) + ")"
        for word in words
    )
    # All variants come from the safe tokenizer; user query syntax is never SQL/FTS syntax.
    rows = service.db.rows(
        "SELECT path,bm25(file_search,0.0,3.0,2.0,1.0) AS rank FROM file_search "
        "WHERE file_search MATCH ? AND project_id=? ORDER BY rank,path LIMIT 100",
        (expression, project_id),
    )
    project = service.db.project(project_id)
    output = []
    largest = max((-row["rank"] for row in rows), default=1.0) or 1.0
    for row in rows:
        file = service.db.one(
            "SELECT * FROM files WHERE project_id=? AND path=?", (project_id, row["path"])
        )
        if file:
            item = service.indexer._candidate(
                project,
                file,
                100 * -row["rank"] / largest,
                "weighted FTS5 BM25 file retrieval; relative maximum normalization",
                snippet_limit=1600,
            )
            if item:
                output.append(item)
    return output


def strategy_candidates(
    service: Service,
    project_id: str,
    query: str,
    strategy: str,
    legacy_search: Callable[..., list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if strategy == "legacy":
        return legacy_search(project_id, query, limit=100, refresh=False)
    lexical = service.indexer.search(project_id, query, limit=100, refresh=False)
    if strategy == "idf_lexical":
        return lexical
    sparse = bm25_candidates(service, project_id, query)
    if strategy == "bm25_files":
        return sparse
    if strategy not in {"rrf", "rrf_mmr"}:
        raise ValueError("Unknown retrieval strategy: " + strategy)
    fused = reciprocal_rank_fusion([unique_paths(lexical), unique_paths(sparse)])
    representatives: dict[str, dict[str, Any]] = {}
    # A relevant lexical declaration is a more focused representative than its whole file.
    for item in lexical + sparse:
        representatives.setdefault(item["path"], item)
    if strategy == "rrf_mmr":
        documents = {
            row["path"]: row["content"]
            for row in service.db.rows(
                "SELECT path,content FROM file_search WHERE project_id=?", (project_id,)
            )
        }
        fused = mmr_diversify(fused, documents)
        scale = 100 / max(len(fused), 1)
    else:
        scale = 3000.0  # RRF scores ~0.03; put them on a comparable context score scale.
    return [
        {**representatives[path], "score": score * scale, "reason": strategy + " file fusion"}
        for path, score in fused
    ]


def frozen_legacy_indexer(db: Any) -> tuple[Any, str]:
    """Load the trusted committed baseline, never code from an indexed fixture."""
    source = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", LEGACY_REVISION + ":src/memglide/core/indexer.py"]
    )
    module = types.ModuleType("memglide_benchmark_frozen_indexer")
    exec(compile(source, "<trusted committed baseline indexer>", "exec"), module.__dict__)
    return module.Indexer(db), hashlib.sha256(source).hexdigest()


def evaluate_query(
    service: Service,
    project_id: str,
    query: dict[str, Any],
    split: str,
    strategy: str,
    legacy_search: Callable[..., list[dict[str, Any]]],
    artifacts: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "query_id": query["id"],
        "split": split,
        "strategy": strategy,
        "language": query["language"],
        "repository": query["repository"],
        "prompt": query["prompt"],
        "primary_target": query["primary_target"],
        "target_files": query["target_files"],
        "status": "error",
        "errors": [],
    }
    started = time.perf_counter()
    original_search = service.indexer.search
    session = None
    try:
        before_cpu = time.process_time()
        candidates = strategy_candidates(
            service, project_id, query["prompt"], strategy, legacy_search
        )
        result["search_wall_seconds"] = time.perf_counter() - started
        result["search_process_cpu_seconds"] = time.process_time() - before_cpu
        paths = unique_paths(candidates)
        result.update(ranking_metrics(paths, query["primary_target"]))
        result["ranked_unique_files"] = paths
        result["ranked_candidates"] = [
            {
                key: item.get(key)
                for key in ("path", "symbol", "score", "reason", "start_line", "end_line")
            }
            for item in candidates
        ]
        session = service.memory.start_session(project_id, query["prompt"])

        # All policies use the same current context implementation, level, budget,
        # source tree, empty session memory, and deterministic downstream reranker.
        def chosen_search(
            _project: str, _query: str, limit: int = 20, **_kwargs: Any
        ) -> list[dict[str, Any]]:
            return copy.deepcopy(candidates[:limit])

        service.indexer.search = chosen_search
        context_started = time.perf_counter()
        context = service.context.get_context(session["id"], query["prompt"], level=2, budget=8000)
        result["context_wall_seconds"] = time.perf_counter() - context_started
        returned = {item["path"] for item in context["items"]}
        targets = set(query["target_files"])
        result["context_target_file_coverage"] = len(targets & returned) / len(targets)
        result["context_primary_target_has_source"] = any(
            item["path"] == query["primary_target"] and bool(item.get("snippet"))
            for item in context["items"]
        )
        result["context_returned_files"] = sorted(returned)
        result["context_estimated_planning_tokens"] = context["estimated_tokens"]
        result["context_truncated"] = context["truncated"]
        result["context_warnings"] = context.get("warnings", [])
        result["status"] = "ok"
        write_json(artifacts / "context.json", context)
    except Exception as exc:
        result["errors"].append(type(exc).__name__ + ": " + str(exc))
    finally:
        service.indexer.search = original_search
        if session:
            service.memory.end_session(session["id"])
    result["total_wall_seconds"] = time.perf_counter() - started
    write_json(artifacts / "result.json", result)
    return result


METRICS = (
    "primary_file_hit_at_1",
    "primary_file_hit_at_3",
    "primary_file_hit_at_5",
    "primary_file_reciprocal_rank",
    "context_target_file_coverage",
    "context_primary_target_has_source",
    "search_wall_seconds",
    "search_process_cpu_seconds",
    "context_wall_seconds",
    "context_estimated_planning_tokens",
)


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "planned_queries": len(rows),
        "valid_queries": sum(row["status"] == "ok" for row in rows),
        "error_queries": [row["query_id"] for row in rows if row["status"] != "ok"],
        "primary_file_misses_at_1": [
            row["query_id"]
            for row in rows
            if row["status"] == "ok" and not row["primary_file_hit_at_1"]
        ],
        "context_target_file_misses": [
            row["query_id"]
            for row in rows
            if row["status"] == "ok" and row["context_target_file_coverage"] < 1
        ],
    }
    for name in METRICS:
        values = [
            float(row[name]) for row in rows if row.get(name) is not None and row["status"] == "ok"
        ]
        summary[name] = {
            "n": len(values),
            "missing": len(rows) - len(values),
            "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
        }
    return summary


def select_strategy(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    eligible = {
        name: value
        for name, value in summaries.items()
        if name in COMPLEXITY
        and value["planned_queries"] > 0
        and value["planned_queries"] == value["valid_queries"]
    }
    if not eligible:
        return {
            "strategy": None,
            "reason": "No candidate completed every development query",
            "policy": SELECTION_POLICY,
        }

    def key(name: str) -> tuple[float, ...]:
        summary = eligible[name]
        return (
            summary["context_target_file_coverage"]["mean"],
            summary["primary_file_hit_at_1"]["mean"],
            summary["primary_file_reciprocal_rank"]["mean"],
            -COMPLEXITY[name],
        )

    selected = max(eligible, key=key)
    return {
        "strategy": selected,
        "development_selection_key": key(selected),
        "policy": SELECTION_POLICY,
    }


def init_git(root: Path) -> str:
    environment = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Memglide retrieval experiment",
        "GIT_COMMITTER_NAME": "Memglide retrieval experiment",
        "GIT_AUTHOR_EMAIL": "benchmark@example.invalid",
        "GIT_COMMITTER_EMAIL": "benchmark@example.invalid",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
    }
    for arguments in (
        ("init", "-q"),
        ("add", "."),
        ("-c", "commit.gpgsign=false", "commit", "-q", "-m", "Locked retrieval fixture"),
    ):
        subprocess.run(
            ["git", "-C", str(root), *arguments], check=True, env=environment, capture_output=True
        )
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Offline retrieval strategy experiment",
        "",
        report["scope"],
        "",
        "No model was called. This experiment measures local retrieval proxies; it does not establish coding-task success, token savings, or monetary savings.",
        "",
        "## Method",
        "",
        report["selection"]["policy"],
        "",
        "Same immutable fixture commits, unchanged prompts, common current index/context implementation, empty session memory, context level 2 and estimated planning-token budget 8000. Candidate order rotates deterministically across queries; local filesystem/SQLite caches are shared and not flushed. Timings are descriptive local measurements, not model execution time.",
        "",
        "Holdout: " + report["holdout_creation_policy"],
        "Validation reuse: "
        + (report.get("validation_reuse_reason") or "First evaluation of the locked holdout."),
        "",
        "Declared-file hit@k and reciprocal rank deduplicate files before ranking. One declared primary relevant file is used; other retrieved files may also be relevant. Context file coverage can include structural references; the source-visible column separately requires a nonempty snippet. Neither proves semantic completeness.",
        "",
        "Strategies: frozen legacy mixed symbol/file search; current IDF lexical mixed search; FTS5 BM25 file-only search (path/identifier/content weights 3/2/1); RRF of unique-file lexical and BM25 ranks (k=60, best lexical declaration represents a file); RRF+MMR (token Jaccard, relevance weight 0.85). Scores are calibrated constants documented in the script. All include the common downstream context reranker.",
        "",
        "Selected on development only: **"
        + str(report["selection"]["strategy"])
        + "**. Selection was saved before evaluating holdout. This is experimental evidence; production adoption also requires exact-reference/security integration checks.",
        "",
        "## Aggregate results",
        "",
        "| Split | Strategy | Valid/planned | File hit@1 | hit@3 | hit@5 | MRR | Context file coverage | Primary source visible | Search mean / median ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split, summaries in report["summary"].items():
        for strategy, summary in summaries.items():

            def percent(metric: str) -> str:
                value = summary[metric]["mean"]
                return "unavailable" if value is None else f"{100 * value:.1f}%"

            timing = summary["search_wall_seconds"]
            time_text = (
                "unavailable"
                if timing["mean"] is None
                else f"{1000 * timing['mean']:.2f} / {1000 * timing['median']:.2f}"
            )
            mrr = summary["primary_file_reciprocal_rank"]["mean"]
            lines.append(
                f"| {split} | {strategy} | {summary['valid_queries']}/{summary['planned_queries']} | "
                + " | ".join(
                    percent(metric)
                    for metric in (
                        "primary_file_hit_at_1",
                        "primary_file_hit_at_3",
                        "primary_file_hit_at_5",
                    )
                )
                + f" | {mrr:.4f} | {percent('context_target_file_coverage')} | {percent('context_primary_target_has_source')} | {time_text} |"
                if mrr is not None
                else f"| {split} | {strategy} | 0/{summary['planned_queries']} | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |"
            )
    lines += [
        "",
        "## Every individual query and failure",
        "",
        "Every planned candidate/query result is retained in JSON, including ranked files, scores, context evidence, timings and exceptions. The table retains all top-one misses and context misses; an empty cell means none.",
        "",
        "| Split | Strategy | Top-one misses | Context file misses | Errors |",
        "|---|---|---|---|---|",
    ]
    for split, summaries in report["summary"].items():
        for strategy, summary in summaries.items():
            lines.append(
                f"| {split} | {strategy} | {', '.join(summary['primary_file_misses_at_1'])} | {', '.join(summary['context_target_file_misses'])} | {', '.join(summary['error_queries'])} |"
            )
    lines += [
        "",
        "## Provenance",
        "",
        "```json",
        json.dumps(report["provenance"], indent=2),
        "```",
        "",
        "## Limits",
        "",
        "Synthetic small repositories, manually declared primary positives, paired language intents, one deterministic ranking per query, warm shared local caches, and common current indexing/context mean these results are not a broad estimate of coding productivity. Source comments often contain domain terms; query wording is independently authored but not sampled from real users. The holdout is visible to repository readers and is procedurally locked rather than secret. Reported local CPU is current-process time, excluding parser-worker startup; exact local memory overhead is not measured here. Existing SDK probes and full product tests complement this ranking experiment. Actual Codex benefit remains unmeasured until authenticated A/B model runs can execute.",
        "",
    ]
    return "\n".join(lines)


def run_experiment(
    output: Path, report_prefix: Path, validation_reuse_reason: str | None = None
) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise ValueError("Use an empty output directory to preserve previous experiments")
    output.mkdir(parents=True, exist_ok=True)
    manifest = load_holdout()
    source_files = [
        ROOT / "src/memglide/core/indexer.py",
        ROOT / "src/memglide/core/context.py",
        ROOT / "src/memglide/core/query.py",
        Path(__file__).resolve(),
    ]
    source_hashes = {str(path.relative_to(ROOT)): digest(path) for path in source_files}
    commits = {}
    rows = []
    legacy_hash = None
    selection = None
    for split in ("development", "holdout"):
        queries = (
            [{**task, "primary_target": task["target_files"][0]} for task in task_definitions()]
            if split == "development"
            else manifest["queries"]
        )
        repositories = list(dict.fromkeys(query["repository"] for query in queries))
        for repository in repositories:
            repository_queries = [query for query in queries if query["repository"] == repository]
            worktree = output / "fixtures" / repository
            if split == "development":
                build_repository(repository_queries[0]["language"], worktree)
            else:
                write_holdout_repository(manifest, repository, worktree)
            commits[repository] = init_git(worktree)
            service = Service(output / "states" / repository / "memglide.db")
            try:
                project = service.indexer.add_project(str(worktree))
                legacy, legacy_hash = frozen_legacy_indexer(service.db)
                for index, query in enumerate(repository_queries):
                    ordered = list(
                        STRATEGIES[index % len(STRATEGIES) :]
                        + STRATEGIES[: index % len(STRATEGIES)]
                    )
                    for order, strategy in enumerate(ordered):
                        row = evaluate_query(
                            service,
                            project["id"],
                            query,
                            split,
                            strategy,
                            legacy.search,
                            output / "queries" / query["id"] / strategy,
                        )
                        row["execution_order_within_query"] = order
                        rows.append(row)
            finally:
                service.close()
        if split == "development":
            summaries = {
                strategy: aggregate([row for row in rows if row["strategy"] == strategy])
                for strategy in STRATEGIES
            }
            selection = {
                **select_strategy(summaries),
                "selected_at_utc": datetime.now(UTC).isoformat(),
                "holdout_sha256": HOLDOUT_SHA256,
            }
            write_json(output / "selection-before-holdout.json", selection)
    changed = [
        str(path.relative_to(ROOT))
        for path in source_files
        if digest(path) != source_hashes[str(path.relative_to(ROOT))]
    ]
    if changed:
        raise RuntimeError(
            "Source changed during experiment; results cannot be finalized: " + ", ".join(changed)
        )
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "scope": "Offline paired retrieval-policy experiment: 24 unchanged Atlas development prompts and 24 prelocked Orion holdout queries across Python and TypeScript. This is separate from the Codex A/B coding benchmark and the full old/new MCP component probes.",
        "holdout_creation_policy": manifest["creation_policy"],
        "validation_reuse_reason": validation_reuse_reason,
        "holdout_previously_evaluated": bool(validation_reuse_reason),
        "selection": selection,
        "settings": {
            "context_level": 2,
            "estimated_planning_token_budget": 8000,
            "rrf_k": 60,
            "mmr_relevance_weight": 0.85,
            "bm25_column_weights": [0, 3, 2, 1],
            "model_requests": 0,
            "fixture_code_executed": False,
        },
        "summary": {
            split: {
                strategy: aggregate(
                    [row for row in rows if row["split"] == split and row["strategy"] == strategy]
                )
                for strategy in STRATEGIES
            }
            for split in ("development", "holdout")
        },
        "provenance": {
            "source_sha256": source_hashes,
            "holdout_sha256": HOLDOUT_SHA256,
            "legacy_commit": LEGACY_REVISION,
            "legacy_indexer_sha256": legacy_hash,
            "fixture_commits": commits,
            "raw_artifacts": str(output),
            "selection_lock": str(output / "selection-before-holdout.json"),
            "ranking_baseline_scope": "Frozen legacy search uses the same current index and context implementation as other policies; it is not the entire former V1 service.",
        },
        "runs": rows,
    }
    write_json(report_prefix.with_suffix(".json"), report)
    report_prefix.with_suffix(".md").write_text(markdown_report(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".local/benchmarks/retrieval-strategies"
    )
    parser.add_argument(
        "--report-prefix", type=Path, default=ROOT / "benchmarks/retrieval-strategies"
    )
    parser.add_argument(
        "--validation-reuse-reason", help="Disclose any previous evaluation of the locked holdout"
    )
    args = parser.parse_args()
    report = run_experiment(
        args.output.resolve(), args.report_prefix.resolve(), args.validation_reuse_reason
    )
    print(
        json.dumps(
            {
                "selected_strategy": report["selection"]["strategy"],
                "runs": len(report["runs"]),
                "report": str(args.report_prefix.with_suffix(".md")),
            }
        )
    )


if __name__ == "__main__":
    main()
