# Offline retrieval strategy experiment

Offline paired retrieval-policy experiment: 24 unchanged Atlas development prompts and 24 prelocked Orion holdout queries across Python and TypeScript. This is separate from the Codex A/B coding benchmark and the full old/new MCP component probes.

No model was called. This experiment measures local retrieval proxies; it does not establish coding-task success, token savings, or monetary savings.

## Method

Development set only: require all queries valid; maximize mean context target-file coverage at level 2 / budget 8000, then primary file hit@1, then primary-file MRR. Exact ties prefer IDF lexical, then BM25 files, then RRF, then RRF+MMR. The frozen legacy policy is a comparator, not an eligible new default. Write the selection lock before evaluating any holdout query. Do not tune on holdout.

Same immutable fixture commits, unchanged prompts, common current index/context implementation, empty session memory, context level 2 and estimated planning-token budget 8000. Candidate order rotates deterministically across queries; local filesystem/SQLite caches are shared and not flushed. Timings are descriptive local measurements, not model execution time.

Holdout: Manually authored and locked before candidate measurement. Independent of Atlas development tasks; 12 operational intents mirrored across two languages, not 24 independent intents. Primary targets declare a relevant file, not exhaustive relevance judgments. Fixture code is indexed, never executed by this experiment.
Validation reuse: The initial locked experiment already evaluated Orion. This rerun validates an independently discovered regular-plural tokenizer bug fix; Orion is previously seen validation, not a fresh holdout. The original experiment and rejected score calibration remain retained.

Declared-file hit@k and reciprocal rank deduplicate files before ranking. One declared primary relevant file is used; other retrieved files may also be relevant. Context file coverage can include structural references; the source-visible column separately requires a nonempty snippet. Neither proves semantic completeness.

Strategies: frozen legacy mixed symbol/file search; current IDF lexical mixed search; FTS5 BM25 file-only search (path/identifier/content weights 3/2/1); RRF of unique-file lexical and BM25 ranks (k=60, best lexical declaration represents a file); RRF+MMR (token Jaccard, relevance weight 0.85). Scores are calibrated constants documented in the script. All include the common downstream context reranker.

Selected on development only: **idf_lexical**. Selection was saved before evaluating holdout. This is experimental evidence; production adoption also requires exact-reference/security integration checks.

## Aggregate results

| Split | Strategy | Valid/planned | File hit@1 | hit@3 | hit@5 | MRR | Context file coverage | Primary source visible | Search mean / median ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| development | legacy | 24/24 | 33.3% | 70.8% | 83.3% | 0.5453 | 100.0% | 100.0% | 97.60 / 75.36 |
| development | idf_lexical | 24/24 | 25.0% | 54.2% | 100.0% | 0.4597 | 100.0% | 100.0% | 102.26 / 86.83 |
| development | bm25_files | 24/24 | 4.2% | 58.3% | 91.7% | 0.3479 | 100.0% | 100.0% | 146.12 / 135.23 |
| development | rrf | 24/24 | 16.7% | 45.8% | 91.7% | 0.4049 | 100.0% | 100.0% | 180.28 / 144.23 |
| development | rrf_mmr | 24/24 | 16.7% | 45.8% | 83.3% | 0.4160 | 100.0% | 100.0% | 199.48 / 152.51 |
| holdout | legacy | 24/24 | 91.7% | 100.0% | 100.0% | 0.9583 | 100.0% | 100.0% | 47.70 / 42.95 |
| holdout | idf_lexical | 24/24 | 100.0% | 100.0% | 100.0% | 1.0000 | 100.0% | 100.0% | 43.16 / 38.10 |
| holdout | bm25_files | 24/24 | 100.0% | 100.0% | 100.0% | 1.0000 | 100.0% | 100.0% | 80.88 / 68.76 |
| holdout | rrf | 24/24 | 100.0% | 100.0% | 100.0% | 1.0000 | 100.0% | 100.0% | 86.39 / 77.98 |
| holdout | rrf_mmr | 24/24 | 100.0% | 100.0% | 100.0% | 1.0000 | 100.0% | 100.0% | 79.87 / 66.85 |

## Every individual query and failure

Every planned candidate/query result is retained in JSON, including ranked files, scores, context evidence, timings and exceptions. The table retains all top-one misses and context misses; an empty cell means none.

| Split | Strategy | Top-one misses | Context file misses | Errors |
|---|---|---|---|---|
| development | legacy | py-ttl-boundary, py-cursor-pagination, py-scope-authorization, py-storage-containment, py-transitive-dependencies, py-boolean-config, py-and-search, py-billing-rounding, ts-ttl-boundary, ts-cursor-pagination, ts-scope-authorization, ts-storage-containment, ts-transitive-dependencies, ts-boolean-config, ts-and-search, ts-billing-rounding |  |  |
| development | idf_lexical | py-ttl-boundary, py-lru-eviction, py-cursor-pagination, py-scope-authorization, py-storage-containment, py-transitive-dependencies, py-boolean-config, py-and-search, py-idempotent-events, ts-ttl-boundary, ts-lru-eviction, ts-cursor-pagination, ts-scope-authorization, ts-storage-containment, ts-transitive-dependencies, ts-boolean-config, ts-and-search, ts-idempotent-events |  |  |
| development | bm25_files | py-ttl-boundary, py-lru-eviction, py-cursor-pagination, py-optimistic-revision, py-scope-authorization, py-storage-containment, py-transitive-dependencies, py-selective-retry, py-boolean-config, py-and-search, py-idempotent-events, ts-ttl-boundary, ts-lru-eviction, ts-cursor-pagination, ts-optimistic-revision, ts-scope-authorization, ts-storage-containment, ts-transitive-dependencies, ts-selective-retry, ts-boolean-config, ts-and-search, ts-billing-rounding, ts-idempotent-events |  |  |
| development | rrf | py-ttl-boundary, py-lru-eviction, py-cursor-pagination, py-scope-authorization, py-storage-containment, py-transitive-dependencies, py-boolean-config, py-and-search, py-idempotent-events, ts-ttl-boundary, ts-lru-eviction, ts-cursor-pagination, ts-scope-authorization, ts-storage-containment, ts-transitive-dependencies, ts-selective-retry, ts-boolean-config, ts-and-search, ts-billing-rounding, ts-idempotent-events |  |  |
| development | rrf_mmr | py-ttl-boundary, py-lru-eviction, py-cursor-pagination, py-scope-authorization, py-storage-containment, py-transitive-dependencies, py-boolean-config, py-and-search, py-idempotent-events, ts-ttl-boundary, ts-lru-eviction, ts-cursor-pagination, ts-scope-authorization, ts-storage-containment, ts-transitive-dependencies, ts-selective-retry, ts-boolean-config, ts-and-search, ts-billing-rounding, ts-idempotent-events |  |  |
| holdout | legacy | holdout-python-receipts, holdout-typescript-receipts |  |  |
| holdout | idf_lexical |  |  |  |
| holdout | bm25_files |  |  |  |
| holdout | rrf |  |  |  |
| holdout | rrf_mmr |  |  |  |

## Provenance

```json
{
  "source_sha256": {
    "src/memglide/core/indexer.py": "39dbf06317769630c3b44044275455f9bf883f7b0b7f651a0b70efaa6348543a",
    "src/memglide/core/context.py": "d94123bf425545944c25d13c96eae30810e5cd5ba013657fdf7b86cc42f5b30d",
    "src/memglide/core/query.py": "781f44a138491a23c1283feb54f0ff6ab83b20264bc658d9776f4518b9b85567",
    "benchmarks/retrieval_experiment.py": "3a65bde1ba27eed5e379484403b2bcc09c13510b0aeaa6b3f59b54978ff0bd85"
  },
  "holdout_sha256": "7c4d343fccc6e1b06badc702c2480d8c0151573be9f1fde2281e8a1e9073ba20",
  "legacy_commit": "39e8df30565783a686270f8a6f422e56e41e3776",
  "legacy_indexer_sha256": "4f350ffa31207a448b0d5ae16006b32482fa80fb1bdce7030e8454c907adc99f",
  "fixture_commits": {
    "atlas-python-v1": "7c23e5ea8a4eb581d1de5886424fe5c7321f04ba",
    "atlas-typescript-v1": "0ead3028ec0cfba4e1a0de15f5a1f0a293338ba1",
    "orion-python-holdout-v1": "dbe2447e2ef7895e050dcae6276d50bf3a7ea3b8",
    "orion-typescript-holdout-v1": "9cf103d4eb4b6f8cee80ba92cd5c9990fce2f59f"
  },
  "raw_artifacts": "/workspace/Memglide/.local/retrieval-strategies-final",
  "selection_lock": "/workspace/Memglide/.local/retrieval-strategies-final/selection-before-holdout.json",
  "ranking_baseline_scope": "Frozen legacy search uses the same current index and context implementation as other policies; it is not the entire former V1 service."
}
```

## Limits

Synthetic small repositories, manually declared primary positives, paired language intents, one deterministic ranking per query, warm shared local caches, and common current indexing/context mean these results are not a broad estimate of coding productivity. Source comments often contain domain terms; query wording is independently authored but not sampled from real users. The holdout is visible to repository readers and is procedurally locked rather than secret. Reported local CPU is current-process time, excluding parser-worker startup; exact local memory overhead is not measured here. Existing SDK probes and full product tests complement this ranking experiment. Actual Codex benefit remains unmeasured until authenticated A/B model runs can execute.
