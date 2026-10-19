# Router v2 formal analysis

All original assignments and raw individual outcomes remain in the accompanying JSON.

| Primary arm | Planned | Attempted | Unrun | Strict successes | Estimated USD/success | Mean seconds | Median seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 24 | 0 | 24 | 0 | None | None | None |
| B | 24 | 0 | 24 | 0 | None | None | None |
| C | 24 | 0 | 24 | 0 | None | None | None |

| C preparation stratum | Task/repeat groups | C attempted | C successes | C estimated USD/success |
|---|---:|---:|---:|---:|
| preloaded | 0 | 0 | 0 | None |
| SKIP | 0 | 0 | 0 | None |
| unobserved_or_inconsistent | 24 | 0 | 0 | None |

| Identical-prompt control | Matching pairs | Missing hashes | Different prompts | Metric | Mean paired difference | Median paired difference | Bootstrap 95% mean interval |
|---|---:|---:|---:|---|---:|---:|---|
| C_vs_A | 0 | 24 | 0 | full_task_seconds | None | None | None |
| C_vs_A | 0 | 24 | 0 | estimated_api_equivalent_usd | None | None | None |
| C_vs_B | 0 | 24 | 0 | full_task_seconds | None | None | None |
| C_vs_B | 0 | 24 | 0 | estimated_api_equivalent_usd | None | None | None |

Negative paired differences favor C for cost/time; missing values remain unavailable. Complete per-task effects, excluded pairs, telemetry coverage, failed-attempt costs and sensitivity bounds are in JSON.

- Primary results include every planned assignment, failure and unrun row; no original is replaced.
- Costs are API-price equivalents, not actual billed charges. Missing attempted cost makes complete cost per success unavailable; known subtotals remain disclosed.
- C strata use preparation decisions made before model execution, never task outcomes. Different strata contain different tasks and are descriptive, not randomized causal contrasts.
- Identical-prompt controls require matching non-null SHA-256 values within the same task and repeat. Their outcome differences cannot establish better source selection; provider/cache variation and local preparation overhead may remain.
- B receives author-known source paths. Human discovery time for those oracle paths is unmeasured and excluded; this is an informative baseline, not a complete automatic workflow cost.
- Task-cluster bootstrap intervals describe this finite corpus, not all repositories. Cache equivalence, avoided investigation and actual billed savings are unproven.
