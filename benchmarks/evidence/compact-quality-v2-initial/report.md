# Compact context: development budget evaluation

These are reused Atlas development tasks, not the new 40-task evaluation or model A/B results. Complete bodies require every original source line at the correct range; symbol declarations alone do not pass.

Source snapshot stable: **True**. Source SHA-256: `6ee9d76626ac62c3bcc1b776147c5eb767ca7f5ac037952e29cfe23cb68ba369`.

| Profile | Valid | Complete primary | Direct local helpers | Integration callers | All declared bodies | Mean JSON bytes | Median retrieval ms | p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_4000 | 24/24 | 22/24 | 2/2 | 14/14 | 22/24 | 11,188.29 | 169.29 | 385.09 |
| compact_1200 | 22/24 | 0/24 | 0/2 | 0/13 | 0/24 | 394.45 | 158.33 | 492.35 |
| compact_2000 | 24/24 | 11/24 | 0/2 | 12/14 | 9/24 | 1,790.29 | 182.39 | 738.31 |
| compact_4000 | 24/24 | 22/24 | 2/2 | 14/14 | 22/24 | 5,291.83 | 186.43 | 658.66 |

The full_4000 comparator uses the current engine and rich transport at budget 4000. It is not a rerun of the historical V1 application. Compact profiles use the same current engine at level 2 with repeated transport metadata removed. Fresh empty sessions are used for every observation, with balanced/reversed profile order and common warm OS/SQLite caches. Timing includes session creation and retrieval; excludes indexing, MCP startup, networking and model execution.

Source hashes are independently computed from file bytes. Controlled edit and deletion probes compare the old response hashes with changed disk content, then require the exact changed-path set to be reported stale. All probe results and failures appear in JSON.

Freshness probes: 16/16 correctly detected changed/deleted sources; 15/16 refreshed responses matched independently hashed current files.

No model was called. JSON bytes and server planning estimates are not billed tokens or cost. Local helper ground truth includes only the local tokens implementation called by search; runtime, standard-library, transitive dependencies and general semantic sufficiency are not judged. Integration callers are separately declared because several task prompts require DocumentService behavior. Previously used tasks can guide a default, but cannot establish held-out performance or Codex savings.

## Incomplete tasks

- full_4000: py-optimistic-revision, ts-optimistic-revision
- compact_1200: py-and-search, py-billing-rounding, py-boolean-config, py-cursor-pagination, py-idempotent-events, py-lru-eviction, py-optimistic-revision, py-scope-authorization, py-selective-retry, py-storage-containment, py-transitive-dependencies, py-ttl-boundary, ts-and-search, ts-billing-rounding, ts-boolean-config, ts-cursor-pagination, ts-idempotent-events, ts-lru-eviction, ts-optimistic-revision, ts-scope-authorization, ts-transitive-dependencies, ts-ttl-boundary
- compact_2000: py-and-search, py-boolean-config, py-cursor-pagination, py-optimistic-revision, py-scope-authorization, py-selective-retry, py-storage-containment, py-ttl-boundary, ts-and-search, ts-cursor-pagination, ts-optimistic-revision, ts-scope-authorization, ts-selective-retry, ts-storage-containment, ts-ttl-boundary
- compact_4000: py-optimistic-revision, ts-optimistic-revision
