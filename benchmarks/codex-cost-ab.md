# Fresh ten-task cost study: standard Codex (A) / compact-prefix Memglide (B)

A = standard Codex; B = Memglide compact-prefix. Raw costs are unavailable; a separately labelled price-equivalent assessment may use observed native usage.

Costs and underlying model-call counts remain unavailable. All original assignments are retained.

| Configuration | Planned | Attempted | Successful completion | Behavior grade passes | Completion rate |
|---|---:|---:|---:|---:|---:|
| A | 10 | 10 | 10 | 10 | 1.0000 |
| B | 10 | 10 | 10 | 10 | 1.0000 |

## Measurements

Totals are unavailable when any attempted run is missing that measurement. RSS is non-additive.

| Metric | A mean | B mean | A median | B median | A p95 | B p95 | A total | B total | A observed | B observed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| input_tokens | 47315.5000 | 47149.7000 | 48065.0000 | 48361.5000 | 61930 | 61248 | 473155 | 471497 | 10/10 | 10/10 |
| cached_input_tokens | 33408 | 33228.8000 | 34752.0000 | 32128.0000 | 48384 | 56320 | 334080 | 332288 | 10/10 | 10/10 |
| uncached_input_tokens | 13907.5000 | 13920.9000 | 13625.5000 | 12888.5000 | 24400 | 26174 | 139075 | 139209 | 10/10 | 10/10 |
| output_tokens | 807.1000 | 716.9000 | 798.5000 | 725.0000 | 1014 | 982 | 8071 | 7169 | 10/10 | 10/10 |
| wall_time_seconds | 26.4663 | 23.8907 | 25.3223 | 22.8211 | 31.1615 | 31.6895 | 264.6634 | 238.9073 | 10/10 | 10/10 |
| end_to_end_wall_seconds | 26.4778 | 24.2035 | 25.3336 | 23.1285 | 31.1684 | 33.1289 | 264.7777 | 242.0346 | 10/10 | 10/10 |
| native_exec_wall_seconds | unavailable | 23.5741 | unavailable | 22.4310 | unavailable | 31.4618 | unavailable | 235.7408 | 0/10 | 10/10 |
| approval_index_wall_seconds | 0 | 0.2745 | 0.0000 | 0.1421 | 0 | 1.1498 | 0 | 2.7448 | 10/10 | 10/10 |
| approval_index_cpu_seconds | 0 | 0.0430 | 0.0000 | 0.0417 | 0 | 0.1232 | 0 | 0.4297 | 10/10 | 10/10 |
| context_preparation_wall_seconds | unavailable | 0.0770 | unavailable | 0.0690 | unavailable | 0.1948 | unavailable | 0.7696 | 0/10 | 10/10 |
| context_preparation_cpu_seconds | unavailable | 0.0763 | unavailable | 0.0686 | unavailable | 0.1948 | unavailable | 0.7635 | 0/10 | 10/10 |
| process_tree_peak_rss_bytes | 267495424 | 258041856 | 286154752.0000 | 255768576.0000 | 315035648 | 355786752 | unavailable | unavailable | 10/10 | 10/10 |
| cpu_seconds | 7.5370 | 5.7260 | 6.4500 | 5.5250 | 15.1000 | 9.9600 | 75.3700 | 57.2600 | 10/10 | 10/10 |
| total_observed_local_cpu_seconds | 7.5370 | 5.7690 | 6.4500 | 5.5686 | 15.1000 | 10.0832 | 75.3700 | 57.6897 | 10/10 | 10/10 |
| mcp_calls | 0 | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 | 10/10 | 10/10 |
| model_calls | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/10 | 0/10 |
| repeated_file_reads | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/10 | 0/10 |
| observed_file_read_commands | 1.3000 | 0.9000 | 1.0000 | 1.0000 | 2 | 2 | 13 | 9 | 10/10 | 10/10 |
| observed_repeated_read_commands | 0 | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 | 10/10 | 10/10 |
| actual_cost_usd | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/10 | 0/10 |
| computed_cost_usd | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/10 | 0/10 |

Actual cost per successful task (all attempted costs, including failures):
- A: unavailable; 10 attempted costs / 10 successful tasks. Cost unavailable for one or more attempts; no estimate substituted
- B: unavailable; 10 attempted costs / 10 successful tasks. Cost unavailable for one or more attempts; no estimate substituted

## Matched pairs

Verified matched pairs: 10; excluded pairs: 0.

| Metric | B/A overall mean | Paired B−A mean | Paired B−A median | Observed pairs |
|---|---:|---:|---:|---:|
| input_tokens | 0.9965 | -165.8000 | -57.5000 | 10 |
| cached_input_tokens | 0.9946 | -179.2000 | -320.0000 | 10 |
| uncached_input_tokens | 1.0010 | 13.4000 | -146.5000 | 10 |
| output_tokens | 0.8882 | -90.2000 | -122.0000 | 10 |
| wall_time_seconds | 0.9027 | -2.5756 | -2.5444 | 10 |
| end_to_end_wall_seconds | 0.9141 | -2.2743 | -2.3105 | 10 |
| native_exec_wall_seconds | unavailable | unavailable | unavailable | 0 |
| approval_index_wall_seconds | unavailable | 0.2745 | 0.1421 | 10 |
| approval_index_cpu_seconds | unavailable | 0.0430 | 0.0417 | 10 |
| context_preparation_wall_seconds | unavailable | unavailable | unavailable | 0 |
| context_preparation_cpu_seconds | unavailable | unavailable | unavailable | 0 |
| process_tree_peak_rss_bytes | 0.9647 | -9453568 | 1187840.0000 | 10 |
| cpu_seconds | 0.7597 | -1.8110 | -0.7900 | 10 |
| total_observed_local_cpu_seconds | 0.7654 | -1.7680 | -0.7483 | 10 |
| mcp_calls | unavailable | 0 | 0.0000 | 10 |
| model_calls | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | unavailable | unavailable | unavailable | 0 |
| observed_file_read_commands | 0.6923 | -0.4000 | -0.5000 | 10 |
| observed_repeated_read_commands | unavailable | 0 | 0.0000 | 10 |
| actual_cost_usd | unavailable | unavailable | unavailable | 0 |
| computed_cost_usd | unavailable | unavailable | unavailable | 0 |

## Selection strata (descriptive)

| Stratum | Arm | Attempted | Successful | Mean full seconds | Mean input |
|---|---|---:|---:|---:|---:|
| caller_context_supplied | A | 2 | 2 | 27.0009 | 41998.5000 |
| caller_context_supplied | B | 2 | 2 | 18.8873 | 35445.5000 |
| explicit_focus | A | 8 | 8 | 26.3470 | 48644.7500 |
| explicit_focus | B | 8 | 8 | 25.5325 | 50075.7500 |

## Individual original runs

| Run | Status | External grade | Treatment | Input | Cached | Output | Full seconds | Mode |
|---|---|---|---|---:|---:|---:|---:|---|
| cost-ts-cost-ledger-memo-empty-only-r1-A | completed | True | True | 48050 | 34816 | 570 | 31.1684 | standard |
| cost-ts-cost-ledger-memo-empty-only-r1-B | completed | True | True | 35011 | 22784 | 290 | 17.2099 | passthrough |
| cost-py-cost-inventory-pack-ceiling-r1-B | completed | True | True | 35880 | 31872 | 576 | 20.5647 | passthrough |
| cost-py-cost-inventory-pack-ceiling-r1-A | completed | True | True | 35947 | 23552 | 703 | 22.8333 | standard |
| cost-ts-cost-geometry-edge-touch-r1-A | completed | True | True | 36368 | 22784 | 906 | 29.6909 | standard |
| cost-ts-cost-geometry-edge-touch-r1-B | completed | True | True | 61248 | 56320 | 964 | 33.1289 | preloaded |
| cost-py-cost-inventory-aggregate-stock-r1-B | completed | True | True | 47822 | 43520 | 564 | 21.3323 | preloaded |
| cost-py-cost-inventory-aggregate-stock-r1-A | completed | True | True | 47870 | 43392 | 762 | 24.5092 | standard |
| cost-py-cost-reports-weighted-mean-r1-A | completed | True | True | 61930 | 47616 | 947 | 30.1587 | standard |
| cost-py-cost-reports-weighted-mean-r1-B | completed | True | True | 48682 | 32384 | 809 | 24.3473 | preloaded |
| cost-ts-cost-geometry-normalized-bounds-r1-B | completed | True | True | 49214 | 23040 | 982 | 32.0117 | preloaded |
| cost-ts-cost-geometry-normalized-bounds-r1-A | completed | True | True | 48570 | 34688 | 983 | 26.1579 | standard |
| cost-ts-cost-ledger-receipt-quantity-r1-A | completed | True | True | 61476 | 48384 | 1014 | 29.4174 | standard |
| cost-ts-cost-ledger-receipt-quantity-r1-B | completed | True | True | 49033 | 23168 | 897 | 26.5500 | preloaded |
| cost-py-cost-inventory-reorder-inclusive-r1-B | completed | True | True | 48485 | 23424 | 744 | 24.3043 | preloaded |
| cost-py-cost-inventory-reorder-inclusive-r1-A | completed | True | True | 48080 | 23680 | 721 | 24.2584 | standard |
| cost-ts-cost-ledger-signed-cents-r1-A | completed | True | True | 36125 | 20096 | 835 | 24.3050 | standard |
| cost-ts-cost-ledger-signed-cents-r1-B | completed | True | True | 47884 | 41088 | 637 | 21.9526 | preloaded |
| cost-py-cost-reports-csv-quoted-cell-r1-B | completed | True | True | 48238 | 34688 | 706 | 20.6330 | preloaded |
| cost-py-cost-reports-csv-quoted-cell-r1-A | completed | True | True | 48739 | 35072 | 630 | 22.2784 | standard |

## Failures

None.

## Protocol and limits

- A invokes standard native Codex directly. B invokes the production compact-prefix launcher, with cold approval/index for eight source-focused tasks and exact-prompt bypass for two supplied-context controls. Ten fresh tasks and one balanced repeat give twenty original assignments. No auxiliary model or configured MCP is used; this measures the conditional source-preload integration, not MCP retrieval or cross-session memory.
- Primary intent-to-treat aggregates retain every original assignment, including B skips and failures; descriptive selection strata do not establish causality.
- Common task instructions, explicit scope and starting commits match within each pair. Actual model prompts intentionally differ when B preloads source; this is the experimental treatment, not prompt identity.
- Purpose-built small ordinary-task repositories are not production-repository or cross-session-memory evidence. Explicit focus paths are supplied equally to A and B; no hidden oracle chooses B paths.
- Fresh local Codex state, worktree and Memglide database per run; required cold project approval/index cost included. OS and provider caches cannot be controlled, provider hits observed and order counterbalanced.
- Native MCP calls should be zero in both arms. Pre-execution source delivery is measured by launcher forwarding/source hash records, not MCP invocation or an assertion that the model attended to it.
- Execution time includes approval/index, launcher and native process, excludes worktree creation and independent grading. Native interval exists only when a monotonic launcher boundary is observed, and includes report-write/exec handoff.
- Linux child-process RSS sampling excludes indexer in the parent, may miss short-lived children and double-count shared pages. CPU counters are observed local lower bounds; no inference-server resource telemetry exists.
- Actual model-call counts, actual filesystem read counts and actual billing unavailable. Read-command proxies are labelled separately. Cached input is a subset of total input, not additional input.
- Source snapshot hashes attest frozen pre-execution source delivery, not semantic completeness or later freshness. No auxiliary model is used for deterministic selection; native event totals cannot reveal hidden provider-internal calls.
- Successful completion requires completed status, independent passing behavior grade, validated treatment and native execution/schema validity. Separate behavior-grade passes do not inflate the completion or cost denominator.
- Interrupted original observations remain unknown and are not silently retried. All failed attempts and raw supported JSON events are preserved.
- Raw actual_cost_usd and computed_cost_usd remain null. Any separately published price-equivalent estimate uses cited per-million rates and observed uncached/cached/output usage; it is not attributable billing or a subscription charge. Unknown usage cannot be costed as zero.
