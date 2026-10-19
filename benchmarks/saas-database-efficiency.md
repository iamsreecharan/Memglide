# SQLite history and lifecycle efficiency

This local component probe measures SQLite VM instructions, query plans and B-tree storage. It makes no model calls and measures no milliseconds, tokens, model cost or SaaS throughput.

All 3 requested attempts are retained. Each creates the same 100-project fixture, including 5,000 rows in each main child table and 10,000 events. The old-schema simulation drops only the nine new indexes; existing indexes, schema, data, query arguments and insertion order stay the same. No ANALYZE, cache or planner forcing is used. The indexed phase restores those exact definitions. Every measured mutation rolls back. A full data digest, foreign-key check and quick_check verify the fixture survives.

| Attempt | Query | Before VM instructions | After VM instructions | Same rows |
| --- | --- | ---: | ---: | --- |
| 1 | global_recent_events | 152,509 | 5,508 | True |
| 1 | project_recent_events | 31,912 | 1,216 | True |
| 1 | global_recent_retrievals | 85,149 | 268 | True |
| 1 | project_sessions | 16,312 | 863 | True |
| 1 | source_invalidation_lookup | 15,820 | 1,024 | True |
| 1 | delete_file_cascade | 35,067 | 80 | True |
| 1 | delete_session_cascade | 70,310 | 368 | True |

Attempt 1 storage: 839,680 bytes in the nine new indexes; database 3,686,400 → 4,526,080 bytes. One rolled-back event append takes 44 → 55 VM instructions. The extra write work and index storage are a real tradeoff; this is one insert shape, not a measured write-throughput percentage.

| Attempt | Query | Before VM instructions | After VM instructions | Same rows |
| --- | --- | ---: | ---: | --- |
| 2 | global_recent_events | 152,509 | 5,508 | True |
| 2 | project_recent_events | 31,912 | 1,216 | True |
| 2 | global_recent_retrievals | 85,149 | 268 | True |
| 2 | project_sessions | 16,312 | 863 | True |
| 2 | source_invalidation_lookup | 15,820 | 1,024 | True |
| 2 | delete_file_cascade | 35,067 | 80 | True |
| 2 | delete_session_cascade | 70,310 | 368 | True |

Attempt 2 storage: 839,680 bytes in the nine new indexes; database 3,686,400 → 4,526,080 bytes. One rolled-back event append takes 44 → 55 VM instructions. The extra write work and index storage are a real tradeoff; this is one insert shape, not a measured write-throughput percentage.

| Attempt | Query | Before VM instructions | After VM instructions | Same rows |
| --- | --- | ---: | ---: | --- |
| 3 | global_recent_events | 152,509 | 5,508 | True |
| 3 | project_recent_events | 31,912 | 1,216 | True |
| 3 | global_recent_retrievals | 85,149 | 268 | True |
| 3 | project_sessions | 16,312 | 863 | True |
| 3 | source_invalidation_lookup | 15,820 | 1,024 | True |
| 3 | delete_file_cascade | 35,067 | 80 | True |
| 3 | delete_session_cascade | 70,310 | 368 | True |

Attempt 3 storage: 839,680 bytes in the nine new indexes; database 3,686,400 → 4,526,080 bytes. One rolled-back event append takes 44 → 55 VM instructions. The extra write work and index storage are a real tradeoff; this is one insert shape, not a measured write-throughput percentage.

Plans, complete per-query observations and per-index storage are in the JSON. New indexes remove temporary ordering trees for the measured history queries and full child-table scans for the measured foreign-key cascades. Composite project/session-leading indexes also serve foreign-key checks; existing prefix indexes are reused instead of duplicated. Upgrades use additive IF NOT EXISTS DDL and do not rewrite stored claims, source text or public responses.

Limitations: fixed synthetic data and one SQLite version; index selectivity and VM programs vary by workload and engine. Before always precedes after because the fixture is upgraded in place. Warm caches do not establish elapsed-time improvement here. The first upgrade must build indexes and can take a database write lock. Real-world billing, model latency and hosted scalability remain unknown.

An earlier exploratory probe is recorded separately in the JSON. Its global recent-event query reported 152,775 → 5,508 instructions, versus 152,509 → 5,508 in these runs; the other six query pairs, append counts and index sizes matched. Its fixture setup and preliminary inspections were not frozen, so it is not pooled into the repeated observations or treated as independent model evidence.

Reproduce without changing these results:

```sh
uv run python -m benchmarks.saas_database_efficiency --output /tmp/memglide-db-probe
```

The output stem must be unused. All requested runs, including errors, are written before the process reports failure. No automatic retry or attempt replacement occurs.
