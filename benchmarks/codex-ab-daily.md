# Ordinary-task Codex / Memglide A/B report

Costs and underlying model-call counts remain unavailable. All original assignments are retained.

| Configuration | Planned | Attempted | Successful completion | Behavior grade passes | Completion rate |
|---|---:|---:|---:|---:|---:|
| A | 40 | 40 | 40 | 40 | 1.0000 |
| B | 40 | 40 | 40 | 40 | 1.0000 |

## Measurements

Totals are unavailable when any attempted run is missing that measurement. RSS is non-additive.

| Metric | A mean | B mean | A median | B median | A p95 | B p95 | A total | B total | A observed | B observed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| input_tokens | 48580.3500 | 47151.9000 | 48222.5000 | 48524.0000 | 62689 | 63438 | 1943214 | 1886076 | 40/40 | 40/40 |
| cached_input_tokens | 40048 | 36304 | 43392.0000 | 36800.0000 | 56320 | 55424 | 1601920 | 1452160 | 40/40 | 40/40 |
| uncached_input_tokens | 8532.3500 | 10847.9000 | 5609.5000 | 10254.0000 | 14433 | 25875 | 341294 | 433916 | 40/40 | 40/40 |
| output_tokens | 865.8500 | 812.6000 | 895.5000 | 855.5000 | 1310 | 1216 | 34634 | 32504 | 40/40 | 40/40 |
| wall_time_seconds | 21.5713 | 20.3760 | 22.7895 | 20.6116 | 28.1915 | 26.1305 | 862.8534 | 815.0397 | 40/40 | 40/40 |
| end_to_end_wall_seconds | 21.5832 | 20.5568 | 22.8033 | 20.8663 | 28.1982 | 26.2660 | 863.3290 | 822.2732 | 40/40 | 40/40 |
| native_exec_wall_seconds | unavailable | 20.1418 | unavailable | 20.4153 | unavailable | 25.9274 | unavailable | 805.6726 | 0/40 | 40/40 |
| approval_index_wall_seconds | 0 | 0.1696 | 0.0000 | 0.1479 | 0 | 0.3615 | 0 | 6.7825 | 40/40 | 40/40 |
| approval_index_cpu_seconds | 0 | 0.0502 | 0.0000 | 0.0491 | 0 | 0.0901 | 0 | 2.0094 | 40/40 | 40/40 |
| context_preparation_wall_seconds | unavailable | 0.0537 | unavailable | 0.0479 | unavailable | 0.1124 | unavailable | 2.1486 | 0/40 | 40/40 |
| context_preparation_cpu_seconds | unavailable | 0.0537 | unavailable | 0.0479 | unavailable | 0.1124 | unavailable | 2.1471 | 0/40 | 40/40 |
| process_tree_peak_rss_bytes | 255377612.8000 | 250204774.4000 | 261879808.0000 | 257349632.0000 | 314556416 | 315674624 | unavailable | unavailable | 40/40 | 40/40 |
| cpu_seconds | 5.0400 | 4.9177 | 5.0750 | 4.6500 | 6.8900 | 7.9100 | 201.6000 | 196.7100 | 40/40 | 40/40 |
| total_observed_local_cpu_seconds | 5.0400 | 4.9680 | 5.0750 | 4.6977 | 6.8900 | 7.9826 | 201.6000 | 198.7194 | 40/40 | 40/40 |
| mcp_calls | 0 | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 | 40/40 | 40/40 |
| model_calls | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/40 | 0/40 |
| repeated_file_reads | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/40 | 0/40 |
| observed_file_read_commands | 1.1750 | 0.8250 | 1.0000 | 1.0000 | 2 | 1 | 47 | 33 | 40/40 | 40/40 |
| observed_repeated_read_commands | 0 | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 | 40/40 | 40/40 |
| actual_cost_usd | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/40 | 0/40 |
| computed_cost_usd | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0/40 | 0/40 |

Actual cost per successful task (all attempted costs, including failures):
- A: unavailable; 40 attempted costs / 40 successful tasks. Cost unavailable for one or more attempts; no estimate substituted
- B: unavailable; 40 attempted costs / 40 successful tasks. Cost unavailable for one or more attempts; no estimate substituted

## Matched pairs

Verified matched pairs: 40; excluded pairs: 0.

| Metric | B/A overall mean | Paired B−A mean | Paired B−A median | Observed pairs |
|---|---:|---:|---:|---:|
| input_tokens | 0.9706 | -1428.4500 | 182.5000 | 40 |
| cached_input_tokens | 0.9065 | -3744 | -3264.0000 | 40 |
| uncached_input_tokens | 1.2714 | 2315.5500 | 1211.0000 | 40 |
| output_tokens | 0.9385 | -53.2500 | -31.5000 | 40 |
| wall_time_seconds | 0.9446 | -1.1953 | -1.3445 | 40 |
| end_to_end_wall_seconds | 0.9524 | -1.0264 | -1.0799 | 40 |
| native_exec_wall_seconds | unavailable | unavailable | unavailable | 0 |
| approval_index_wall_seconds | unavailable | 0.1696 | 0.1479 | 40 |
| approval_index_cpu_seconds | unavailable | 0.0502 | 0.0491 | 40 |
| context_preparation_wall_seconds | unavailable | unavailable | unavailable | 0 |
| context_preparation_cpu_seconds | unavailable | unavailable | unavailable | 0 |
| process_tree_peak_rss_bytes | 0.9797 | -5172838.4000 | -1992704.0000 | 40 |
| cpu_seconds | 0.9757 | -0.1222 | -0.3950 | 40 |
| total_observed_local_cpu_seconds | 0.9857 | -0.0720 | -0.3257 | 40 |
| mcp_calls | unavailable | 0 | 0.0000 | 40 |
| model_calls | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | unavailable | unavailable | unavailable | 0 |
| observed_file_read_commands | 0.7021 | -0.3500 | 0.0000 | 40 |
| observed_repeated_read_commands | unavailable | 0 | 0.0000 | 40 |
| actual_cost_usd | unavailable | unavailable | unavailable | 0 |
| computed_cost_usd | unavailable | unavailable | unavailable | 0 |

## Selection strata (descriptive)

| Stratum | Arm | Attempted | Successful | Mean full seconds | Mean input |
|---|---|---:|---:|---:|---:|
| caller_context_supplied | A | 8 | 8 | 13.3289 | 30972.3750 |
| caller_context_supplied | B | 8 | 8 | 12.7617 | 29431.3750 |
| explicit_focus | A | 32 | 32 | 23.6468 | 52982.3438 |
| explicit_focus | B | 32 | 32 | 22.5056 | 51582.0312 |

## Individual original runs

| Run | Status | External grade | Treatment | Input | Cached | Output | Full seconds | Mode |
|---|---|---|---|---:|---:|---:|---:|---|
| py-daily-catalog-relative-indentation-r1-A | completed | True | True | 47610 | 43264 | 646 | 21.4354 | baseline |
| py-daily-catalog-relative-indentation-r1-B | completed | True | True | 48110 | 34688 | 653 | 16.7297 | preloaded |
| ts-daily-inventory-chunk-without-empty-tail-r1-A | completed | True | True | 61100 | 47360 | 900 | 27.1328 | baseline |
| ts-daily-inventory-chunk-without-empty-tail-r1-B | completed | True | True | 48488 | 43904 | 882 | 20.6328 | preloaded |
| py-daily-catalog-strict-column-projection-r1-A | completed | True | True | 48375 | 32000 | 977 | 22.6876 | baseline |
| py-daily-catalog-strict-column-projection-r1-B | completed | True | True | 48992 | 35968 | 844 | 19.5521 | preloaded |
| ts-daily-editor-html-text-escaping-r1-B | completed | True | True | 48477 | 41344 | 753 | 20.9938 | preloaded |
| ts-daily-editor-html-text-escaping-r1-A | completed | True | True | 47771 | 43392 | 783 | 22.3126 | baseline |
| py-daily-catalog-tag-normalization-r1-A | completed | True | True | 49312 | 43776 | 1321 | 26.2984 | baseline |
| py-daily-catalog-tag-normalization-r1-B | completed | True | True | 50567 | 37248 | 1149 | 25.8615 | preloaded |
| ts-daily-inventory-zero-count-plural-r1-A | completed | True | True | 23357 | 20224 | 280 | 10.6332 | baseline |
| ts-daily-inventory-zero-count-plural-r1-B | completed | True | True | 23258 | 20352 | 235 | 9.2728 | passthrough |
| py-daily-desk-rectangular-transpose-r1-A | completed | True | True | 48134 | 44288 | 891 | 21.5087 | baseline |
| py-daily-desk-rectangular-transpose-r1-B | completed | True | True | 48293 | 44416 | 782 | 19.2084 | preloaded |
| ts-daily-editor-literal-replace-all-r1-A | completed | True | True | 61320 | 47232 | 1124 | 26.0148 | baseline |
| ts-daily-editor-literal-replace-all-r1-B | completed | True | True | 63438 | 45696 | 1132 | 28.6912 | preloaded |
| ts-daily-inventory-signed-code-padding-r1-A | completed | True | True | 48264 | 34560 | 857 | 22.3941 | baseline |
| ts-daily-inventory-signed-code-padding-r1-B | completed | True | True | 62293 | 35328 | 907 | 25.5023 | preloaded |
| ts-daily-inventory-equal-length-zip-r1-A | completed | True | True | 49068 | 41600 | 1294 | 25.6162 | baseline |
| ts-daily-inventory-equal-length-zip-r1-B | completed | True | True | 49939 | 24064 | 1125 | 24.4856 | preloaded |
| py-daily-desk-label-ellipsis-r1-A | completed | True | True | 35518 | 32000 | 436 | 13.7404 | baseline |
| py-daily-desk-label-ellipsis-r1-B | completed | True | True | 35463 | 20608 | 491 | 14.3630 | passthrough |
| py-daily-catalog-saturday-weekend-r1-B | completed | True | True | 23332 | 11264 | 225 | 9.3692 | passthrough |
| py-daily-catalog-saturday-weekend-r1-A | completed | True | True | 35180 | 29440 | 394 | 13.8661 | baseline |
| py-daily-desk-elapsed-clock-r1-A | completed | True | True | 47839 | 43520 | 656 | 17.2169 | baseline |
| py-daily-desk-elapsed-clock-r1-B | completed | True | True | 47891 | 35072 | 546 | 16.7793 | preloaded |
| ts-daily-inventory-numeric-median-r1-B | completed | True | True | 48558 | 31744 | 987 | 24.9237 | preloaded |
| ts-daily-inventory-numeric-median-r1-A | completed | True | True | 48065 | 43392 | 1008 | 26.4756 | baseline |
| ts-daily-editor-whitespace-word-spans-r1-A | completed | True | True | 61979 | 56832 | 1046 | 23.0735 | baseline |
| ts-daily-editor-whitespace-word-spans-r1-B | completed | True | True | 62834 | 45952 | 1029 | 23.9042 | preloaded |
| py-daily-desk-export-line-endings-r1-A | completed | True | True | 49200 | 34944 | 1259 | 25.0607 | baseline |
| py-daily-desk-export-line-endings-r1-B | completed | True | True | 49997 | 23808 | 1062 | 22.3265 | preloaded |
| ts-daily-editor-inclusive-clamp-r1-A | completed | True | True | 48314 | 34944 | 717 | 20.3684 | baseline |
| ts-daily-editor-inclusive-clamp-r1-B | completed | True | True | 23298 | 11264 | 255 | 10.8859 | passthrough |
| py-daily-desk-calendar-month-shift-r1-B | completed | True | True | 50259 | 44928 | 1216 | 25.4819 | preloaded |
| py-daily-desk-calendar-month-shift-r1-A | completed | True | True | 63411 | 57728 | 1426 | 28.0671 | baseline |
| ts-daily-editor-crlf-line-position-r1-A | completed | True | True | 61144 | 56320 | 860 | 23.0452 | baseline |
| ts-daily-editor-crlf-line-position-r1-B | completed | True | True | 48753 | 44160 | 813 | 24.9056 | preloaded |
| py-daily-catalog-single-pass-partition-r1-B | completed | True | True | 48115 | 32384 | 779 | 21.4187 | preloaded |
| py-daily-catalog-single-pass-partition-r1-A | completed | True | True | 47931 | 44160 | 878 | 23.3425 | baseline |
| py-daily-catalog-relative-indentation-r2-B | completed | True | True | 48020 | 43520 | 664 | 17.4637 | preloaded |
| py-daily-catalog-relative-indentation-r2-A | completed | True | True | 47783 | 43904 | 675 | 17.7020 | baseline |
| ts-daily-inventory-chunk-without-empty-tail-r2-B | completed | True | True | 48069 | 34816 | 766 | 18.2935 | preloaded |
| ts-daily-inventory-chunk-without-empty-tail-r2-A | completed | True | True | 60929 | 56064 | 843 | 20.3307 | baseline |
| py-daily-catalog-strict-column-projection-r2-B | completed | True | True | 49048 | 33152 | 887 | 20.2410 | preloaded |
| py-daily-catalog-strict-column-projection-r2-A | completed | True | True | 61711 | 47616 | 1058 | 28.6636 | baseline |
| ts-daily-editor-html-text-escaping-r2-A | completed | True | True | 48122 | 34688 | 699 | 20.9269 | baseline |
| ts-daily-editor-html-text-escaping-r2-B | completed | True | True | 48217 | 22912 | 686 | 19.8977 | preloaded |
| py-daily-catalog-tag-normalization-r2-B | completed | True | True | 50855 | 36224 | 1213 | 24.5552 | preloaded |
| py-daily-catalog-tag-normalization-r2-A | completed | True | True | 49209 | 43776 | 1223 | 27.7185 | baseline |
| ts-daily-inventory-zero-count-plural-r2-B | completed | True | True | 48240 | 40704 | 650 | 16.8531 | passthrough |
| ts-daily-inventory-zero-count-plural-r2-A | completed | True | True | 23257 | 20224 | 235 | 11.8389 | baseline |
| py-daily-desk-rectangular-transpose-r2-B | completed | True | True | 48290 | 43648 | 766 | 23.0286 | preloaded |
| py-daily-desk-rectangular-transpose-r2-A | completed | True | True | 47809 | 43264 | 764 | 20.1882 | baseline |
| ts-daily-editor-literal-replace-all-r2-B | completed | True | True | 63675 | 58112 | 1188 | 24.7276 | preloaded |
| ts-daily-editor-literal-replace-all-r2-A | completed | True | True | 48711 | 35840 | 1142 | 23.7716 | baseline |
| ts-daily-inventory-signed-code-padding-r2-B | completed | True | True | 62176 | 57984 | 954 | 24.2143 | preloaded |
| ts-daily-inventory-signed-code-padding-r2-A | completed | True | True | 48181 | 43520 | 964 | 23.1712 | baseline |
| ts-daily-inventory-equal-length-zip-r2-B | completed | True | True | 63907 | 55424 | 1304 | 30.0354 | preloaded |
| ts-daily-inventory-equal-length-zip-r2-A | completed | True | True | 62689 | 48256 | 1310 | 30.8190 | baseline |
| py-daily-desk-label-ellipsis-r2-B | completed | True | True | 35270 | 31872 | 415 | 13.7708 | passthrough |
| py-daily-desk-label-ellipsis-r2-A | completed | True | True | 35527 | 23040 | 439 | 14.2308 | baseline |
| py-daily-catalog-saturday-weekend-r2-A | completed | True | True | 23336 | 20224 | 228 | 11.7260 | baseline |
| py-daily-catalog-saturday-weekend-r2-B | completed | True | True | 23301 | 17920 | 195 | 10.2703 | passthrough |
| py-daily-desk-elapsed-clock-r2-B | completed | True | True | 48023 | 43776 | 632 | 18.4861 | preloaded |
| py-daily-desk-elapsed-clock-r2-A | completed | True | True | 47842 | 43520 | 655 | 17.8475 | baseline |
| ts-daily-inventory-numeric-median-r2-A | completed | True | True | 48005 | 43392 | 991 | 24.5765 | baseline |
| ts-daily-inventory-numeric-median-r2-B | completed | True | True | 48490 | 43776 | 933 | 23.6485 | preloaded |
| ts-daily-editor-whitespace-word-spans-r2-B | completed | True | True | 49520 | 44544 | 1076 | 23.9828 | preloaded |
| ts-daily-editor-whitespace-word-spans-r2-A | completed | True | True | 61917 | 47616 | 1111 | 23.2214 | baseline |
| py-daily-desk-export-line-endings-r2-B | completed | True | True | 49312 | 44160 | 1064 | 23.0928 | preloaded |
| py-daily-desk-export-line-endings-r2-A | completed | True | True | 49190 | 34944 | 1168 | 24.7480 | baseline |
| ts-daily-editor-inclusive-clamp-r2-B | completed | True | True | 23289 | 11264 | 240 | 17.3087 | passthrough |
| ts-daily-editor-inclusive-clamp-r2-A | completed | True | True | 23290 | 0 | 239 | 10.2271 | baseline |
| py-daily-desk-calendar-month-shift-r2-A | completed | True | True | 63843 | 53504 | 1297 | 28.1982 | baseline |
| py-daily-desk-calendar-month-shift-r2-B | completed | True | True | 50707 | 36352 | 1238 | 26.2660 | preloaded |
| ts-daily-editor-crlf-line-position-r2-B | completed | True | True | 48723 | 44032 | 867 | 20.7387 | preloaded |
| ts-daily-editor-crlf-line-position-r2-A | completed | True | True | 61038 | 52352 | 922 | 22.9190 | baseline |
| py-daily-catalog-single-pass-partition-r2-A | completed | True | True | 47933 | 35200 | 918 | 20.2137 | baseline |
| py-daily-catalog-single-pass-partition-r2-B | completed | True | True | 48589 | 43776 | 901 | 20.1102 | preloaded |

## Failures

None.

## Protocol and limits

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
