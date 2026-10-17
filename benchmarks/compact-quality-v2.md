# Compact context: development budget evaluation

These are reused Atlas development tasks, not the new 40-task evaluation or model A/B results. Complete bodies require every original source line at the correct range; symbol declarations alone do not pass.

Source snapshot stable: **True**. Source SHA-256: `e1fd0dfc1646e46a9585cac447d135fc88f3b1e3258d6e37652629bcb90a9ab5`.

| Profile | Valid | Complete primary | Direct local helpers | Integration callers | All declared bodies | Mean JSON bytes | Median retrieval ms | p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_4000 | 48/48 | 48/48 | 4/4 | 28/28 | 48/48 | 11,087.83 | 166.43 | 308.80 |
| compact_1200 | 44/48 | 0/48 | 0/4 | 0/28 | 0/48 | 394.45 | 146.04 | 272.42 |
| compact_2000 | 48/48 | 28/48 | 0/4 | 18/28 | 24/48 | 1,686.67 | 160.63 | 365.55 |
| compact_4000 | 48/48 | 48/48 | 4/4 | 28/28 | 48/48 | 5,346.04 | 154.28 | 370.80 |

Development recommendation: **compact_4000** is the lowest tested compact budget that preserves every complete body returned by full_4000 in every matched observation without retrieval errors. This rule does not declare the rich comparator complete or establish model savings.

The full_4000 comparator uses the current engine and rich transport at budget 4000. It is not a rerun of the historical V1 application. Compact profiles use the same current engine at level 2 with repeated transport metadata removed. Fresh empty sessions are used for every observation, with balanced/reversed profile order and common warm OS/SQLite caches. Timing includes session creation and retrieval; excludes indexing, MCP startup, networking and model execution.

Source hashes are independently computed from file bytes. Controlled edit and deletion probes compare the old response hashes with changed disk content, then require the exact changed-path set to be reported stale. All probe results and failures appear in JSON.
Host CPU and operating-system caches were shared with development activity; local timing is descriptive and cannot establish a controlled speed improvement.

Freshness probes: 16/16 correctly detected changed/deleted sources; 15/15 refreshed responses with returned source hashes matched independently hashed current files. 1 refreshed responses had no source hashes to verify.

No model was called. JSON bytes and server planning estimates are not billed tokens or cost. Local helper ground truth includes only the local tokens implementation called by search; runtime, standard-library, transitive dependencies and general semantic sufficiency are not judged. Integration callers are separately declared because several task prompts require DocumentService behavior. Previously used tasks can guide a default, but cannot establish held-out performance or Codex savings.

## Incomplete tasks

- full_4000: none
- compact_1200: py-and-search, py-billing-rounding, py-boolean-config, py-cursor-pagination, py-idempotent-events, py-lru-eviction, py-optimistic-revision, py-scope-authorization, py-selective-retry, py-storage-containment, py-transitive-dependencies, py-ttl-boundary, ts-and-search, ts-billing-rounding, ts-boolean-config, ts-cursor-pagination, ts-idempotent-events, ts-lru-eviction, ts-optimistic-revision, ts-scope-authorization, ts-transitive-dependencies, ts-ttl-boundary
- compact_2000: py-and-search, py-boolean-config, py-cursor-pagination, py-scope-authorization, py-storage-containment, py-ttl-boundary, ts-and-search, ts-boolean-config, ts-cursor-pagination, ts-scope-authorization, ts-storage-containment, ts-ttl-boundary
- compact_4000: none
