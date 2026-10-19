# Three-arm workflow cost assessment

A: Standard Codex; B: Memglide source-only; C: Memglide source plus support.

**All dollars are API-price equivalents, not actual bills.** Each original attempt is priced once; pair views are references, not additional spend.

| Arm | Attempts | Successful assignments | USD / successful task | Total estimated USD |
|---|---:|---:|---:|---:|
| A | 20 | 0 | unavailable | 0.689743 |
| B | 20 | 0 | unavailable | 0.698216 |
| C | 20 | 0 | unavailable | 0.636640 |

| Comparison | Cost / success saving % | Possible-write saving range % | Paired outcomes |
|---|---:|---|---|
| C_over_A | unavailable | unavailable to unavailable | {"baseline_cheaper": 5, "candidate_cheaper": 15, "equal": 0, "unavailable": 0} |
| C_over_B | unavailable | unavailable to unavailable | {"baseline_cheaper": 9, "candidate_cheaper": 11, "equal": 0, "unavailable": 0} |
| B_over_A | unavailable | unavailable to unavailable | {"baseline_cheaper": 9, "candidate_cheaper": 11, "equal": 0, "unavailable": 0} |

Prespecified promotion gate passed: **False**. Keep support explicitly optional; do not promote defaults.

- Every original arm must complete successfully with valid source/native fidelity
- Focused cost/full-time mean or median regresses or is unavailable overall or in a repeat

## Individual attempts

| Run | Arm | Success | Input | Cached | Output | Estimated USD | Full seconds |
|---|---|---|---:|---:|---:|---:|---:|
| workflow-ts-workflow-text-negative-array-offset-r1-A | A | False | 36,891 | 23,680 | 961 | 0.038400 | 22.620 |
| workflow-ts-workflow-text-negative-array-offset-r1-C | C | False | 36,748 | 23,552 | 850 | 0.037247 | 20.446 |
| workflow-ts-workflow-text-negative-array-offset-r1-B | B | False | 23,972 | 11,392 | 619 | 0.032489 | 16.861 |
| workflow-py-workflow-form-ascii-count-field-r1-A | A | False | 24,406 | 11,520 | 577 | 0.032694 | 16.396 |
| workflow-py-workflow-form-ascii-count-field-r1-B | B | False | 37,875 | 12,544 | 836 | 0.060276 | 24.720 |
| workflow-py-workflow-form-ascii-count-field-r1-C | C | False | 24,474 | 11,520 | 649 | 0.033550 | 19.082 |
| workflow-ts-workflow-signals-circular-angle-difference-r1-B | B | False | 36,049 | 11,648 | 819 | 0.058157 | 20.817 |
| workflow-ts-workflow-signals-circular-angle-difference-r1-C | C | False | 36,318 | 23,168 | 855 | 0.037167 | 23.448 |
| workflow-ts-workflow-signals-circular-angle-difference-r1-A | A | False | 35,951 | 22,912 | 920 | 0.037569 | 22.758 |
| workflow-py-workflow-form-form-plus-decoding-r1-C | C | False | 24,318 | 11,520 | 411 | 0.030858 | 13.408 |
| workflow-py-workflow-form-form-plus-decoding-r1-B | B | False | 36,253 | 23,040 | 527 | 0.034000 | 16.045 |
| workflow-py-workflow-form-form-plus-decoding-r1-A | A | False | 35,822 | 22,912 | 446 | 0.032571 | 15.623 |
| workflow-py-workflow-finance-net-flow-report-r1-B | B | False | 36,290 | 23,168 | 556 | 0.034121 | 19.327 |
| workflow-py-workflow-finance-net-flow-report-r1-A | A | False | 36,168 | 23,040 | 599 | 0.034550 | 17.127 |
| workflow-py-workflow-finance-net-flow-report-r1-C | C | False | 24,476 | 11,648 | 504 | 0.031861 | 14.661 |
| workflow-ts-workflow-signals-threshold-hysteresis-r1-C | C | False | 37,958 | 24,064 | 695 | 0.037144 | 21.473 |
| workflow-ts-workflow-signals-threshold-hysteresis-r1-A | A | False | 36,095 | 11,776 | 780 | 0.057616 | 19.658 |
| workflow-ts-workflow-signals-threshold-hysteresis-r1-B | B | False | 36,219 | 23,168 | 634 | 0.034759 | 18.268 |
| workflow-ts-workflow-text-path-segment-roundtrip-r1-A | A | False | 35,693 | 22,912 | 517 | 0.033023 | 19.580 |
| workflow-ts-workflow-text-path-segment-roundtrip-r1-C | C | False | 24,174 | 20,480 | 486 | 0.014296 | 16.254 |
| workflow-ts-workflow-text-path-segment-roundtrip-r1-B | B | False | 48,323 | 35,200 | 627 | 0.036036 | 17.453 |
| workflow-py-workflow-form-query-latest-value-r1-A | A | False | 36,616 | 23,040 | 818 | 0.037636 | 20.609 |
| workflow-py-workflow-form-query-latest-value-r1-B | B | False | 36,548 | 11,392 | 658 | 0.058031 | 20.018 |
| workflow-py-workflow-form-query-latest-value-r1-C | C | False | 24,791 | 11,648 | 612 | 0.033571 | 20.168 |
| workflow-ts-workflow-text-utf8-byte-length-r1-B | B | False | 35,660 | 22,912 | 535 | 0.033137 | 19.604 |
| workflow-ts-workflow-text-utf8-byte-length-r1-C | C | False | 23,919 | 11,520 | 448 | 0.030430 | 14.546 |
| workflow-ts-workflow-text-utf8-byte-length-r1-A | A | False | 35,508 | 22,912 | 556 | 0.033043 | 19.549 |
| workflow-py-workflow-finance-discount-before-tax-r1-C | C | False | 24,210 | 11,520 | 404 | 0.030572 | 15.293 |
| workflow-py-workflow-finance-discount-before-tax-r1-B | B | False | 36,008 | 32,128 | 431 | 0.015283 | 14.866 |
| workflow-py-workflow-finance-discount-before-tax-r1-A | A | False | 35,839 | 22,912 | 436 | 0.032505 | 18.174 |
| workflow-ts-workflow-text-negative-array-offset-r2-B | B | False | 23,989 | 11,392 | 634 | 0.032673 | 19.391 |
| workflow-ts-workflow-text-negative-array-offset-r2-C | C | False | 36,616 | 23,552 | 743 | 0.035913 | 22.591 |
| workflow-ts-workflow-text-negative-array-offset-r2-A | A | False | 48,806 | 35,456 | 794 | 0.038186 | 28.732 |
| workflow-py-workflow-form-ascii-count-field-r2-C | C | False | 24,363 | 11,520 | 562 | 0.032458 | 15.024 |
| workflow-py-workflow-form-ascii-count-field-r2-B | B | False | 24,399 | 20,480 | 577 | 0.015656 | 16.204 |
| workflow-py-workflow-form-ascii-count-field-r2-A | A | False | 24,317 | 11,520 | 527 | 0.032016 | 14.265 |
| workflow-ts-workflow-signals-circular-angle-difference-r2-A | A | False | 35,806 | 31,872 | 763 | 0.018685 | 19.553 |
| workflow-ts-workflow-signals-circular-angle-difference-r2-C | C | False | 36,248 | 23,296 | 672 | 0.034954 | 46.369 |
| workflow-ts-workflow-signals-circular-angle-difference-r2-B | B | False | 35,886 | 11,392 | 746 | 0.057587 | 24.632 |
| workflow-py-workflow-form-form-plus-decoding-r2-A | A | False | 35,966 | 22,912 | 465 | 0.033049 | 16.959 |
| workflow-py-workflow-form-form-plus-decoding-r2-B | B | False | 36,242 | 23,040 | 528 | 0.033988 | 17.112 |
| workflow-py-workflow-form-form-plus-decoding-r2-C | C | False | 24,406 | 11,520 | 483 | 0.031754 | 14.960 |
| workflow-py-workflow-finance-net-flow-report-r2-C | C | False | 37,986 | 24,192 | 580 | 0.035807 | 18.911 |
| workflow-py-workflow-finance-net-flow-report-r2-A | A | False | 36,180 | 32,000 | 608 | 0.017640 | 26.551 |
| workflow-py-workflow-finance-net-flow-report-r2-B | B | False | 36,318 | 32,128 | 561 | 0.017203 | 18.113 |
| workflow-ts-workflow-signals-threshold-hysteresis-r2-B | B | False | 36,289 | 29,312 | 672 | 0.023605 | 22.224 |
| workflow-ts-workflow-signals-threshold-hysteresis-r2-A | A | False | 36,022 | 23,040 | 688 | 0.035148 | 25.834 |
| workflow-ts-workflow-signals-threshold-hysteresis-r2-C | C | False | 37,074 | 23,680 | 682 | 0.035976 | 18.489 |
| workflow-ts-workflow-text-path-segment-roundtrip-r2-B | B | False | 35,831 | 23,040 | 508 | 0.032966 | 15.972 |
| workflow-ts-workflow-text-path-segment-roundtrip-r2-C | C | False | 24,129 | 11,520 | 449 | 0.030860 | 15.185 |
| workflow-ts-workflow-text-path-segment-roundtrip-r2-A | A | False | 48,128 | 34,944 | 670 | 0.036562 | 19.350 |
| workflow-py-workflow-form-query-latest-value-r2-C | C | False | 24,775 | 8,960 | 592 | 0.038446 | 15.133 |
| workflow-py-workflow-form-query-latest-value-r2-B | B | False | 36,641 | 23,168 | 665 | 0.035913 | 20.966 |
| workflow-py-workflow-form-query-latest-value-r2-A | A | False | 36,529 | 11,264 | 729 | 0.058946 | 19.524 |
| workflow-ts-workflow-text-utf8-byte-length-r2-A | A | False | 35,611 | 31,872 | 587 | 0.016535 | 21.967 |
| workflow-ts-workflow-text-utf8-byte-length-r2-C | C | False | 23,909 | 20,480 | 437 | 0.013276 | 13.920 |
| workflow-ts-workflow-text-utf8-byte-length-r2-B | B | False | 35,531 | 22,912 | 482 | 0.032349 | 16.021 |
| workflow-py-workflow-finance-discount-before-tax-r2-A | A | False | 35,910 | 22,912 | 508 | 0.033367 | 14.345 |
| workflow-py-workflow-finance-discount-before-tax-r2-B | B | False | 35,943 | 29,568 | 428 | 0.019987 | 16.711 |
| workflow-py-workflow-finance-discount-before-tax-r2-C | C | False | 24,209 | 11,520 | 397 | 0.030500 | 16.895 |

## Per-arm descriptive metrics

| Metric | Arm | Mean | Median | p95 | Complete total | Missing |
|---|---|---:|---:|---:|---:|---:|
| input_tokens | A | 36,113.200 | 35,958.500 | 48,128.000 | 722,264.000 | 0 |
| cached_input_tokens | A | 23,270.400 | 22,912.000 | 34,944.000 | 465,408.000 | 0 |
| output_tokens | A | 647.450 | 603.500 | 920.000 | 12,949.000 | 0 |
| cache_write_input_tokens | A | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| reasoning_output_tokens | A | 4.250 | 0.000 | 20.000 | 85.000 | 0 |
| uncached_input_tokens | A | 12,842.800 | 12,990.000 | 24,319.000 | 256,856.000 | 0 |
| ordinary_uncached_input_tokens | A | 12,842.800 | 12,990.000 | 24,319.000 | 256,856.000 | 0 |
| end_to_end_wall_seconds | A | 19.959 | 19.551 | 26.551 | 399.173 | 0 |
| total_observed_local_cpu_seconds | A | 5.462 | 4.250 | 11.660 | 109.230 | 0 |
| process_tree_peak_rss_bytes | A | 248,131,174.400 | 231,233,536.000 | 345,227,264.000 | unavailable | 0 |
| mcp_calls | A | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| observed_file_read_commands | A | 0.850 | 1.000 | 1.000 | 17.000 | 0 |
| observed_repeated_read_commands | A | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| test_count | A | 18.050 | 19.000 | 21.000 | 361.000 | 0 |
| observed_command_items | A | 2.950 | 3.000 | 4.000 | 59.000 | 0 |
| observed_file_change_items | A | 1.100 | 1.000 | 2.000 | 22.000 | 0 |
| input_tokens | B | 35,013.300 | 36,134.000 | 37,875.000 | 700,266.000 | 0 |
| cached_input_tokens | B | 21,651.200 | 23,040.000 | 32,128.000 | 433,024.000 | 0 |
| output_tokens | B | 602.150 | 598.000 | 819.000 | 12,043.000 | 0 |
| cache_write_input_tokens | B | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| reasoning_output_tokens | B | 4.250 | 0.000 | 18.000 | 85.000 | 0 |
| uncached_input_tokens | B | 13,362.100 | 12,921.000 | 25,156.000 | 267,242.000 | 0 |
| ordinary_uncached_input_tokens | B | 13,362.100 | 12,921.000 | 25,156.000 | 267,242.000 | 0 |
| end_to_end_wall_seconds | B | 18.766 | 18.191 | 24.632 | 375.326 | 0 |
| total_observed_local_cpu_seconds | B | 4.798 | 4.597 | 7.540 | 95.963 | 0 |
| process_tree_peak_rss_bytes | B | 250,999,193.600 | 245,204,992.000 | 338,366,464.000 | unavailable | 0 |
| mcp_calls | B | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| observed_file_read_commands | B | 0.800 | 1.000 | 1.000 | 16.000 | 0 |
| observed_repeated_read_commands | B | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| test_count | B | 18.050 | 19.000 | 21.000 | 361.000 | 0 |
| observed_command_items | B | 3.050 | 3.000 | 4.000 | 61.000 | 0 |
| observed_file_change_items | B | 1.250 | 1.000 | 2.000 | 25.000 | 0 |
| input_tokens | C | 28,755.050 | 24,475.000 | 37,958.000 | 575,101.000 | 0 |
| cached_input_tokens | C | 16,544.000 | 11,648.000 | 24,064.000 | 330,880.000 | 0 |
| output_tokens | C | 575.550 | 571.000 | 850.000 | 11,511.000 | 0 |
| cache_write_input_tokens | C | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| reasoning_output_tokens | C | 4.750 | 0.000 | 21.000 | 95.000 | 0 |
| uncached_input_tokens | C | 12,211.050 | 12,919.000 | 13,894.000 | 244,221.000 | 0 |
| ordinary_uncached_input_tokens | C | 12,211.050 | 12,919.000 | 13,894.000 | 244,221.000 | 0 |
| end_to_end_wall_seconds | C | 18.813 | 16.574 | 23.448 | 376.256 | 0 |
| total_observed_local_cpu_seconds | C | 5.753 | 4.334 | 6.940 | 115.070 | 0 |
| process_tree_peak_rss_bytes | C | 245,325,209.600 | 226,861,056.000 | 344,653,824.000 | unavailable | 0 |
| mcp_calls | C | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| observed_file_read_commands | C | 0.050 | 0.000 | 0.000 | 1.000 | 0 |
| observed_repeated_read_commands | C | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| test_count | C | 17.900 | 19.000 | 21.000 | 358.000 | 0 |
| observed_command_items | C | 3.350 | 3.000 | 4.000 | 67.000 | 0 |
| observed_file_change_items | C | 1.150 | 1.000 | 2.000 | 23.000 | 0 |

All per-task pairs, repeats, language/task/selection strata, gate checks, component charges and source/native fidelity are retained in JSON.

- Every dollar amount is a standard API list-price equivalent, not actual provider billing or a subscription charge.
- Cache writes reported as zero may reflect an upstream default. Conservative possible-write ranges are scenarios, not confidence intervals.
- Each native attempt is priced once. All failures and unknown attempts remain in per-arm numerators; unknown usage prevents a complete total or cost per success.
- Cached input is included in total input and reasoning is included in output; neither is billed twice.
- Completed command/file-change items are invocation/patch proxies, not provider model calls, individual file reads or unique edits. Missing telemetry remains null.
- Local CPU is a sampled lower bound; child RSS can double-count shared pages and omits parent indexing. Neither has a fabricated dollar rate.
- Provided-context controls are excluded from source-benefit promotion checks. Repeat consistency is descriptive, not statistical proof.
- Fresh small synthetic tasks with uncontrolled provider/OS caches do not establish production, long-term memory or universal efficiency gains.
