# Memglide MCP component diagnostics

These measurements use the official MCP SDK against real STDIO subprocesses. They are independent component checks, **not Codex model runs, A/B results, or evidence of token/cost savings**.

Executed 24 isolated task worktrees with fresh databases: 24 transport probes passed, 0 failed; 24 freshness/hash checks passed, 0 failed; 168 actual SDK tool calls.

Natural task-prompt retrieval uses level 2 and an 8,000 estimated-token budget. Target-file and symbol coverage compare returned evidence with one declared fix location per task. This is a narrow coverage proxy; passing it does not prove context completeness or successful coding. The returned budget estimate is not billed token usage.

Mean target-file coverage: 0.6666666666666666; mean exact target-symbol identity coverage: 0.3333333333333333; mean expected declaration visibility in source snippets: 0.625. Whole-file/class evidence can contain a declaration while failing an exact symbol-identity match; declaration visibility does not establish a complete method body. All returned natural-retrieval evidence hashes matched disk in 24/24 task probes.

**Natural task-prompt retrieval missed the declared target file in 8/24 queries:** `py-scope-authorization`, `py-storage-containment`, `py-transitive-dependencies`, `ts-scope-authorization`, `ts-storage-containment`, `ts-transitive-dependencies`, `ts-boolean-config`, `ts-and-search`. These misses remain in every coverage statistic; the later exact-file query does not repair the natural-query score.

A separate exact-file level-3 retrieval selected a controlled comment edit. The old passport detected staleness in 24/24 probes; updated target hashes matched in 24/24, and updated full-source snippets contained the marker in 24/24.

| Metric | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|
| index_wall_seconds | 0.2750 | 0.2450 | 0.1153 | 1.0383 |
| mcp_transport_wall_seconds | 5.1211 | 5.0498 | 4.1302 | 7.3371 |
| mcp_server_sampled_cpu_seconds | 4.8046 | 4.7550 | 3.8700 | 6.7800 |
| mcp_server_sampled_peak_rss_bytes | 81954816.0000 | 80902144.0000 | 74858496.0000 | 90370048.0000 |

Server CPU and RSS are sampled locally every 50 ms. CPU is an observed lower bound; short-lived processes can be missed, shared RSS pages may be counted more than once. Timings include startup, SDK operations, controlled edit and shutdown. Index registration is measured separately in the probe process. These tiny synthetic libraries do not establish production scaling behavior.

| Task | Transport/hash checks | File coverage | Exact symbol coverage | Declaration visible | Old passport stale | Updated hash | Edit marker | MCP calls |
|---|---|---:|---:|---:|---|---|---|---:|
| py-ttl-boundary | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| py-lru-eviction | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-cursor-pagination | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-optimistic-revision | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-scope-authorization | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-storage-containment | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-transitive-dependencies | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-selective-retry | passed | 1.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-boolean-config | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| py-and-search | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-billing-rounding | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| py-idempotent-events | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| ts-ttl-boundary | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| ts-lru-eviction | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-cursor-pagination | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-optimistic-revision | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-scope-authorization | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-storage-containment | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-transitive-dependencies | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-selective-retry | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-boolean-config | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-and-search | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-billing-rounding | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| ts-idempotent-events | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |

Raw SDK arguments/responses and server logs are retained under the reported artifact root. Every failure is included. Model input/cached/output tokens, model calls, billed cost and coding success are unavailable in this component probe and remain null. A full passport status can remain Partial when source hashes are current, because unresolved static dependencies are reported separately from freshness.
