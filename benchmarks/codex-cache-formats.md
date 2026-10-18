# Fresh twenty-task format comparison: Memglide legacy (A) / compact-prefix (B)

A = Memglide legacy; B = Memglide compact-prefix. Neither arm is standard Codex. Fresh twenty-task format comparison.

Costs and underlying model-call counts remain unavailable. All original assignments are retained.

| Configuration | Planned | Attempted | Successful completion | Behavior grade passes | Completion rate |
|---|---:|---:|---:|---:|---:|
| A | 20 | 20 | 20 | 20 | 1.0000 |
| B | 20 | 20 | 20 | 20 | 1.0000 |

## Measurements

Totals are unavailable when any attempted run is missing that measurement. RSS is non-additive.

| Metric | A mean | B mean | A median | B median | A p95 | B p95 | A total | B total | A observed | B observed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| input_tokens | 50076.7500 | 49071.3000 | 48625.0000 | 48321.0000 | 63106 | 62375 | 1001535 | 981426 | 20/20 | 20/20 |
| cached_input_tokens | 36307.2000 | 34764.8000 | 35136.0000 | 34880.0000 | 48640 | 48896 | 726144 | 695296 | 20/20 | 20/20 |
| uncached_input_tokens | 13769.5500 | 14306.5000 | 13544.0000 | 13454.0000 | 25258 | 25519 | 275391 | 286130 | 20/20 | 20/20 |
| output_tokens | 790.7500 | 742.6000 | 799.0000 | 725.5000 | 1013 | 1064 | 15815 | 14852 | 20/20 | 20/20 |
| wall_time_seconds | 29.4036 | 26.1428 | 27.5426 | 26.3483 | 39.1689 | 33.0940 | 588.0712 | 522.8559 | 20/20 | 20/20 |
| end_to_end_wall_seconds | 29.6856 | 26.3733 | 27.6685 | 26.6990 | 39.4917 | 33.4491 | 593.7124 | 527.4653 | 20/20 | 20/20 |
| native_exec_wall_seconds | 29.0887 | 25.8486 | 27.2936 | 26.1135 | 38.9138 | 32.5955 | 581.7747 | 516.9717 | 20/20 | 20/20 |
| approval_index_wall_seconds | 0.2479 | 0.2177 | 0.2033 | 0.1919 | 0.5870 | 0.4770 | 4.9575 | 4.3541 | 20/20 | 20/20 |
| approval_index_cpu_seconds | 0.0597 | 0.0604 | 0.0616 | 0.0508 | 0.1169 | 0.1207 | 1.1943 | 1.2086 | 20/20 | 20/20 |
| context_preparation_wall_seconds | 0.0740 | 0.0748 | 0.0682 | 0.0669 | 0.1354 | 0.2204 | 1.4808 | 1.4956 | 20/20 | 20/20 |
| context_preparation_cpu_seconds | 0.0705 | 0.0716 | 0.0626 | 0.0657 | 0.1291 | 0.2130 | 1.4107 | 1.4313 | 20/20 | 20/20 |
| process_tree_peak_rss_bytes | 268895027.2000 | 265621094.4000 | 267644928.0000 | 260048896.0000 | 335212544 | 315559936 | unavailable | unavailable | 20/20 | 20/20 |
| cpu_seconds | 7.7500 | 6.3065 | 7.3600 | 6.0300 | 15.8500 | 8.8700 | 155.0000 | 126.1300 | 20/20 | 20/20 |
| total_observed_local_cpu_seconds | 7.8097 | 6.3669 | 7.4275 | 6.0896 | 15.9646 | 8.9346 | 156.1943 | 127.3386 | 20/20 | 20/20 |
| mcp_calls | 0 | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 | 20/20 | 20/20 |
| model_calls | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/20 | 0/20 |
| repeated_file_reads | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/20 | 0/20 |
| observed_file_read_commands | 0.9500 | 0.8500 | 1.0000 | 1.0000 | 1 | 1 | 19 | 17 | 20/20 | 20/20 |
| observed_repeated_read_commands | 0 | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 | 20/20 | 20/20 |
| actual_cost_usd | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/20 | 0/20 |
| computed_cost_usd | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/20 | 0/20 |

Actual cost per successful task (all attempted costs, including failures):
- A: unavailable; 20 attempted costs / 20 successful tasks. Cost unavailable for one or more attempts; no estimate substituted
- B: unavailable; 20 attempted costs / 20 successful tasks. Cost unavailable for one or more attempts; no estimate substituted

## Matched pairs

Verified matched pairs: 20; excluded pairs: 0.

| Metric | B/A overall mean | Paired B−A mean | Paired B−A median | Observed pairs |
|---|---:|---:|---:|---:|
| input_tokens | 0.9799 | -1005.4500 | -442.0000 | 20 |
| cached_input_tokens | 0.9575 | -1542.4000 | -256.0000 | 20 |
| uncached_input_tokens | 1.0390 | 536.9500 | 35.5000 | 20 |
| output_tokens | 0.9391 | -48.1500 | -6.0000 | 20 |
| wall_time_seconds | 0.8891 | -3.2608 | -1.1730 | 20 |
| end_to_end_wall_seconds | 0.8884 | -3.3124 | -1.2484 | 20 |
| native_exec_wall_seconds | 0.8886 | -3.2402 | -1.0362 | 20 |
| approval_index_wall_seconds | 0.8783 | -0.0302 | -0.0036 | 20 |
| approval_index_cpu_seconds | 1.0120 | 0.0007 | -0.0007 | 20 |
| context_preparation_wall_seconds | 1.0100 | 0.0007 | 0.0000 | 20 |
| context_preparation_cpu_seconds | 1.0146 | 0.0010 | 0.0007 | 20 |
| process_tree_peak_rss_bytes | 0.9878 | -3273932.8000 | -6195200.0000 | 20 |
| cpu_seconds | 0.8137 | -1.4435 | -0.9350 | 20 |
| total_observed_local_cpu_seconds | 0.8153 | -1.4428 | -0.8232 | 20 |
| mcp_calls | unavailable | 0 | 0.0000 | 20 |
| model_calls | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | unavailable | unavailable | unavailable | 0 |
| observed_file_read_commands | 0.8947 | -0.1000 | 0.0000 | 20 |
| observed_repeated_read_commands | unavailable | 0 | 0.0000 | 20 |
| actual_cost_usd | unavailable | unavailable | unavailable | 0 |
| computed_cost_usd | unavailable | unavailable | unavailable | 0 |

## Selection strata (descriptive)

| Stratum | Arm | Attempted | Successful | Mean full seconds | Mean input |
|---|---|---:|---:|---:|---:|
| caller_context_supplied | A | 4 | 4 | 20.8476 | 44507 |
| caller_context_supplied | B | 4 | 4 | 19.1372 | 38181.2500 |
| explicit_focus | A | 16 | 16 | 31.8951 | 51469.1875 |
| explicit_focus | B | 16 | 16 | 28.1823 | 51793.8125 |

## Individual original runs

| Run | Status | External grade | Treatment | Input | Cached | Output | Full seconds | Mode |
|---|---|---|---|---:|---:|---:|---:|---|
| fmt-py-cache-metrics-warmup-moving-average-r1-A | completed | True | True | 48554 | 23296 | 746 | 33.2872 | preloaded |
| fmt-py-cache-metrics-warmup-moving-average-r1-B | completed | True | True | 48585 | 35072 | 745 | 24.3636 | preloaded |
| fmt-ts-cache-collections-unique-intersection-r1-B | completed | True | True | 47550 | 34432 | 622 | 21.3846 | preloaded |
| fmt-ts-cache-collections-unique-intersection-r1-A | completed | True | True | 47815 | 34688 | 599 | 23.3537 | preloaded |
| fmt-py-cache-metrics-fractional-sample-variance-r1-A | completed | True | True | 49283 | 35456 | 828 | 33.5687 | preloaded |
| fmt-py-cache-metrics-fractional-sample-variance-r1-B | completed | True | True | 62375 | 48000 | 924 | 31.4214 | preloaded |
| fmt-ts-cache-forms-hex-color-lengths-r1-B | completed | True | True | 47669 | 34560 | 660 | 23.2590 | preloaded |
| fmt-ts-cache-forms-hex-color-lengths-r1-A | completed | True | True | 48303 | 43648 | 907 | 30.3451 | preloaded |
| fmt-py-cache-metrics-histogram-boundary-slots-r1-A | completed | True | True | 63059 | 48640 | 975 | 29.1516 | preloaded |
| fmt-py-cache-metrics-histogram-boundary-slots-r1-B | completed | True | True | 62176 | 48896 | 872 | 28.0930 | preloaded |
| fmt-ts-cache-collections-last-value-fallback-r1-B | completed | True | True | 23057 | 11392 | 242 | 15.1699 | passthrough |
| fmt-ts-cache-collections-last-value-fallback-r1-A | completed | True | True | 48113 | 43904 | 568 | 25.2978 | passthrough |
| fmt-py-cache-mailroom-folded-header-spacing-r1-A | completed | True | True | 48878 | 35072 | 809 | 22.9078 | preloaded |
| fmt-py-cache-mailroom-folded-header-spacing-r1-B | completed | True | True | 48178 | 34816 | 706 | 30.6464 | preloaded |
| fmt-ts-cache-forms-strict-integer-range-r1-B | completed | True | True | 48933 | 34944 | 1187 | 33.4491 | preloaded |
| fmt-ts-cache-forms-strict-integer-range-r1-A | completed | True | True | 63597 | 57984 | 1443 | 39.4917 | preloaded |
| fmt-ts-cache-collections-consecutive-run-groups-r1-A | completed | True | True | 63106 | 24960 | 1013 | 69.7737 | preloaded |
| fmt-ts-cache-collections-consecutive-run-groups-r1-B | completed | True | True | 49077 | 35328 | 863 | 30.3247 | preloaded |
| fmt-ts-cache-collections-stable-feed-merge-r1-B | completed | True | True | 62431 | 49280 | 1064 | 30.1406 | preloaded |
| fmt-ts-cache-collections-stable-feed-merge-r1-A | completed | True | True | 49639 | 36480 | 951 | 30.8418 | preloaded |
| fmt-py-cache-mailroom-quoted-display-backslash-r1-A | completed | True | True | 47508 | 43392 | 575 | 21.7511 | passthrough |
| fmt-py-cache-mailroom-quoted-display-backslash-r1-B | completed | True | True | 35509 | 20480 | 517 | 20.3128 | passthrough |
| fmt-py-cache-metrics-missing-not-falsy-r1-B | completed | True | True | 47484 | 34432 | 563 | 22.1620 | passthrough |
| fmt-py-cache-metrics-missing-not-falsy-r1-A | completed | True | True | 47511 | 22784 | 563 | 22.2781 | passthrough |
| fmt-py-cache-mailroom-colon-password-r1-A | completed | True | True | 48604 | 35072 | 816 | 26.1855 | preloaded |
| fmt-py-cache-mailroom-colon-password-r1-B | completed | True | True | 48683 | 35072 | 834 | 28.1688 | preloaded |
| fmt-ts-cache-collections-signed-left-rotation-r1-B | completed | True | True | 61447 | 47616 | 846 | 30.0641 | preloaded |
| fmt-ts-cache-collections-signed-left-rotation-r1-A | completed | True | True | 48499 | 24192 | 789 | 34.3944 | preloaded |
| fmt-ts-cache-forms-form-space-encoding-r1-A | completed | True | True | 48628 | 35072 | 753 | 26.0054 | preloaded |
| fmt-ts-cache-forms-form-space-encoding-r1-B | completed | True | True | 48120 | 34816 | 643 | 25.6398 | preloaded |
| fmt-py-cache-mailroom-utf8-header-word-r1-B | completed | True | True | 48836 | 22912 | 910 | 37.0586 | preloaded |
| fmt-py-cache-mailroom-utf8-header-word-r1-A | completed | True | True | 49538 | 35584 | 921 | 29.9514 | preloaded |
| fmt-ts-cache-forms-required-whitespace-r1-A | completed | True | True | 34896 | 31744 | 251 | 14.0636 | passthrough |
| fmt-ts-cache-forms-required-whitespace-r1-B | completed | True | True | 46675 | 43136 | 342 | 18.9041 | passthrough |
| fmt-py-cache-mailroom-reply-subject-preservation-r1-B | completed | True | True | 48339 | 34944 | 671 | 24.9165 | preloaded |
| fmt-py-cache-mailroom-reply-subject-preservation-r1-A | completed | True | True | 48715 | 35200 | 617 | 25.7148 | preloaded |
| fmt-ts-cache-forms-strict-calendar-date-r1-A | completed | True | True | 48622 | 43904 | 945 | 25.9264 | preloaded |
| fmt-ts-cache-forms-strict-calendar-date-r1-B | completed | True | True | 48303 | 22784 | 997 | 27.7583 | preloaded |
| fmt-py-cache-metrics-negative-baseline-change-r1-B | completed | True | True | 47999 | 32384 | 644 | 24.2282 | preloaded |
| fmt-py-cache-metrics-negative-baseline-change-r1-A | completed | True | True | 48667 | 35072 | 746 | 29.4225 | preloaded |

## Failures

None.

## Protocol and limits

- A is Memglide legacy task-suffix context; B is Memglide compact-prefix context. Neither arm is standard Codex. These twenty tasks were authored after both formats were fixed and were not used for format tuning. One balanced repeat gives forty original assignments; small purpose-built tasks do not establish production-scale or money savings.
- Primary intent-to-treat aggregates retain every original assignment, including skips in either format and failures; descriptive selection strata do not establish causality.
- Common task instructions, explicit scope and starting commits match within each pair. Actual model prompts intentionally differ between legacy and compact-prefix source layouts; caller-context bypasses forward the identical common prompt.
- Purpose-built small ordinary-task repositories are not production-repository or cross-session-memory evidence. Explicit focus paths are supplied equally to A and B; no hidden oracle chooses either format's paths.
- Fresh local Codex state, worktree and Memglide database per run; required cold project approval/index cost included. OS and provider caches cannot be controlled, provider hits observed and order counterbalanced.
- Native MCP calls should be zero in both arms. Pre-execution source delivery is measured by launcher forwarding/source hash records, not MCP invocation or an assertion that the model attended to it.
- Execution time includes approval/index, launcher and native process, excludes worktree creation and independent grading. Native interval exists only when a monotonic launcher boundary is observed, and includes report-write/exec handoff.
- Linux child-process RSS sampling excludes indexer in the parent, may miss short-lived children and double-count shared pages. CPU counters are observed local lower bounds; no inference-server resource telemetry exists.
- Actual model-call counts, actual filesystem read counts and actual billing unavailable. Read-command proxies are labelled separately. Cached input is a subset of total input, not additional input.
- Source snapshot hashes attest frozen pre-execution source delivery, not semantic completeness or later freshness. No auxiliary model is used for deterministic selection; native event totals cannot reveal hidden provider-internal calls.
- Successful completion requires completed status, independent passing behavior grade, validated treatment and native execution/schema validity. Separate behavior-grade passes do not inflate the completion or cost denominator.
- Interrupted original observations remain unknown and are not silently retried. All failed attempts and raw supported JSON events are preserved.
- The twenty fresh tasks have distinct source-focus sets and one repeat. This tests source-format tradeoffs on fresh small fixes; it does not directly test cross-task prefix reuse over unchanged identical source files.
