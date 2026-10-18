# Fresh known-file utility-edit format microbenchmark

Twenty fresh tasks compare two Memglide prompt formats. This is a focused format microbenchmark, not a representative production-repository or cross-session evaluation. No model requests were used to create or refine these tasks.

- Ten Python and ten TypeScript tasks across four purpose-built repositories.
- Eight single-source tasks, eight two-source integration tasks, four supplied-source tiny fixes.
- Every focus path appears literally in the identical common prompt. Four prompts also contain the complete relevant source.
- Two independently executed held-out behavioral methods per task, five protected ordinary-use smoke methods per repository, strict TypeScript compilation, protected fixture hashes, and explicit early-exit/test-count/clean-summary guards.
- Twenty baseline failures/reference passes and sixteen domain-only/adapter-only negative controls.
- All53 corpus checks passed in36.82seconds, plus a subsequent manifest-only check after prompt spacing cleanup. Ruff passed.

Relevant source scope: 89–632bytes; mean 359.55bytes, median 318.5bytes.

## Individual tasks

| Task | Kind | Scoped source bytes |
|---|---|---:|
| py-cache-mailroom-colon-password | single-source | 632 |
| py-cache-mailroom-folded-header-spacing | single-source | 373 |
| py-cache-mailroom-reply-subject-preservation | integration | 314 |
| py-cache-mailroom-utf8-header-word | integration | 535 |
| py-cache-mailroom-quoted-display-backslash | supplied-context | 228 |
| py-cache-metrics-warmup-moving-average | single-source | 435 |
| py-cache-metrics-negative-baseline-change | single-source | 322 |
| py-cache-metrics-histogram-boundary-slots | integration | 605 |
| py-cache-metrics-fractional-sample-variance | integration | 501 |
| py-cache-metrics-missing-not-falsy | supplied-context | 136 |
| ts-cache-forms-strict-calendar-date | single-source | 266 |
| ts-cache-forms-hex-color-lengths | single-source | 118 |
| ts-cache-forms-strict-integer-range | integration | 511 |
| ts-cache-forms-form-space-encoding | integration | 315 |
| ts-cache-forms-required-whitespace | supplied-context | 89 |
| ts-cache-collections-signed-left-rotation | single-source | 283 |
| ts-cache-collections-unique-intersection | single-source | 149 |
| ts-cache-collections-consecutive-run-groups | integration | 623 |
| ts-cache-collections-stable-feed-merge | integration | 620 |
| ts-cache-collections-last-value-fallback | supplied-context | 136 |

## Limits

- Four small purpose-built repositories and known-file utility changes; not a representative large-production-repository benchmark.
- Both configurations receive exactly the same disclosed production paths; four tasks additionally supply all relevant source.
- No cross-session memory or unfamiliar-repository discovery is evaluated.
- Code scopes are naturally small and were not selected or padded against preloader limits or measured model outcomes.
- Independent grading is external to agent worktrees and guards early exits, missing tests, skips, expected failures and todo tests; it is procedural separation, not a hostile-code security boundary.
- This corpus validates correctness and integrity of the experiment; its unit-test pass count is not a live Codex performance result.

## Preserved development evidence

The original complete draft and valid initial reference/negative-control run remain under `.local/cache-v2/corpus-initial-draft` and `corpus-validation`. Before any model requests, a self-review strengthened the hex-color whitespace guard and its Unicode whitespace assertions. Revised full test logs are `corpus-pytest-1.log/xml`; final structured validation is `corpus-validation-final/validation.json`. The task author did not inspect the production formatting implementation, change old corpora, or consult A/B outcomes.

Independent fairness/oracle review found no substantive blocker. The report must retain the20distinct focus sets and one-repeat limits; this cohort cannot establish production-scale or cross-task same-file prefix reuse.
