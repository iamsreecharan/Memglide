# Fresh three-arm workflow comparison

A = standard Codex; B = Memglide source-only; C = Memglide source plus supporting tests.
Actual costs unavailable; price-equivalent estimates are separately labelled.

| Arm | Planned | Attempted | Successful | Failed grades | Completion rate |
|---|---:|---:|---:|---:|---:|
| A | 20 | 20 | 0 | 20 | 0.000000 |
| B | 20 | 20 | 0 | 20 | 0.000000 |
| C | 20 | 20 | 0 | 20 | 0.000000 |

## Measurements

Totals are unavailable when any attempted observation is unknown; RSS is non-additive.

| Metric | Arm | Mean | Median | p95 | Total | Observed |
|---|---|---:|---:|---:|---:|---:|
| input_tokens | A | 36113.200000 | 35958.500000 | 48128 | 722264 | 20 |
| input_tokens | B | 35013.300000 | 36134.000000 | 37875 | 700266 | 20 |
| input_tokens | C | 28755.050000 | 24475.000000 | 37958 | 575101 | 20 |
| cached_input_tokens | A | 23270.400000 | 22912.000000 | 34944 | 465408 | 20 |
| cached_input_tokens | B | 21651.200000 | 23040.000000 | 32128 | 433024 | 20 |
| cached_input_tokens | C | 16544 | 11648.000000 | 24064 | 330880 | 20 |
| uncached_input_tokens | A | 12842.800000 | 12990.000000 | 24319 | 256856 | 20 |
| uncached_input_tokens | B | 13362.100000 | 12921.000000 | 25156 | 267242 | 20 |
| uncached_input_tokens | C | 12211.050000 | 12919.000000 | 13894 | 244221 | 20 |
| output_tokens | A | 647.450000 | 603.500000 | 920 | 12949 | 20 |
| output_tokens | B | 602.150000 | 598.000000 | 819 | 12043 | 20 |
| output_tokens | C | 575.550000 | 571.000000 | 850 | 11511 | 20 |
| wall_time_seconds | A | 19.943276 | 19.531143 | 26.537941 | 398.865523 | 20 |
| wall_time_seconds | B | 18.567335 | 18.002563 | 24.252526 | 371.346695 | 20 |
| wall_time_seconds | C | 18.600018 | 16.148589 | 23.036123 | 372.000362 | 20 |
| end_to_end_wall_seconds | A | 19.958644 | 19.550878 | 26.550940 | 399.172880 | 20 |
| end_to_end_wall_seconds | B | 18.766308 | 18.190707 | 24.632077 | 375.326163 | 20 |
| end_to_end_wall_seconds | C | 18.812814 | 16.574339 | 23.447727 | 376.256283 | 20 |
| native_exec_wall_seconds | A | unavailable | unavailable | unavailable | unavailable | 0 |
| native_exec_wall_seconds | B | 18.300075 | 17.759979 | 24.091074 | 366.001505 | 20 |
| native_exec_wall_seconds | C | 18.335492 | 15.860969 | 22.866132 | 366.709843 | 20 |
| approval_index_wall_seconds | A | 0 | 0.000000 | 0 | 0 | 20 |
| approval_index_wall_seconds | B | 0.177152 | 0.138886 | 0.382842 | 3.543049 | 20 |
| approval_index_wall_seconds | C | 0.201935 | 0.219310 | 0.405114 | 4.038707 | 20 |
| approval_index_cpu_seconds | A | 0 | 0.000000 | 0 | 0 | 20 |
| approval_index_cpu_seconds | B | 0.053143 | 0.058828 | 0.082132 | 1.062858 | 20 |
| approval_index_cpu_seconds | C | 0.055993 | 0.046616 | 0.151860 | 1.119858 | 20 |
| context_preparation_wall_seconds | A | unavailable | unavailable | unavailable | unavailable | 0 |
| context_preparation_wall_seconds | B | 0.057509 | 0.064553 | 0.101023 | 1.150180 | 20 |
| context_preparation_wall_seconds | C | 0.059972 | 0.059042 | 0.108259 | 1.199446 | 20 |
| context_preparation_cpu_seconds | A | unavailable | unavailable | unavailable | unavailable | 0 |
| context_preparation_cpu_seconds | B | 0.057414 | 0.064552 | 0.100613 | 1.148283 | 20 |
| context_preparation_cpu_seconds | C | 0.059605 | 0.057302 | 0.105203 | 1.192095 | 20 |
| process_tree_peak_rss_bytes | A | 248131174.400000 | 231233536.000000 | 345227264 | unavailable | 20 |
| process_tree_peak_rss_bytes | B | 250999193.600000 | 245204992.000000 | 338366464 | unavailable | 20 |
| process_tree_peak_rss_bytes | C | 245325209.600000 | 226861056.000000 | 344653824 | unavailable | 20 |
| cpu_seconds | A | 5.461500 | 4.250000 | 11.660000 | 109.230000 | 20 |
| cpu_seconds | B | 4.745000 | 4.500000 | 7.480000 | 94.900000 | 20 |
| cpu_seconds | C | 5.697500 | 4.270000 | 6.940000 | 113.950000 | 20 |
| total_observed_local_cpu_seconds | A | 5.461500 | 4.250000 | 11.660000 | 109.230000 | 20 |
| total_observed_local_cpu_seconds | B | 4.798143 | 4.597011 | 7.540244 | 95.962858 | 20 |
| total_observed_local_cpu_seconds | C | 5.753493 | 4.334349 | 6.940000 | 115.069858 | 20 |
| mcp_calls | A | 0 | 0.000000 | 0 | 0 | 20 |
| mcp_calls | B | 0 | 0.000000 | 0 | 0 | 20 |
| mcp_calls | C | 0 | 0.000000 | 0 | 0 | 20 |
| model_calls | A | unavailable | unavailable | unavailable | unavailable | 0 |
| model_calls | B | unavailable | unavailable | unavailable | unavailable | 0 |
| model_calls | C | unavailable | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | A | unavailable | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | B | unavailable | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | C | unavailable | unavailable | unavailable | unavailable | 0 |
| observed_file_read_commands | A | 0.850000 | 1.000000 | 1 | 17 | 20 |
| observed_file_read_commands | B | 0.800000 | 1.000000 | 1 | 16 | 20 |
| observed_file_read_commands | C | 0.050000 | 0.000000 | 0 | 1 | 20 |
| observed_repeated_read_commands | A | 0 | 0.000000 | 0 | 0 | 20 |
| observed_repeated_read_commands | B | 0 | 0.000000 | 0 | 0 | 20 |
| observed_repeated_read_commands | C | 0 | 0.000000 | 0 | 0 | 20 |
| actual_cost_usd | A | unavailable | unavailable | unavailable | unavailable | 0 |
| actual_cost_usd | B | unavailable | unavailable | unavailable | unavailable | 0 |
| actual_cost_usd | C | unavailable | unavailable | unavailable | unavailable | 0 |
| computed_cost_usd | A | unavailable | unavailable | unavailable | unavailable | 0 |
| computed_cost_usd | B | unavailable | unavailable | unavailable | unavailable | 0 |
| computed_cost_usd | C | unavailable | unavailable | unavailable | unavailable | 0 |

## C_over_A

Verified pairs: 20; excluded: 0.

| Metric | Overall mean ratio | Paired difference mean | Paired difference median |
|---|---:|---:|---:|
| input_tokens | 0.796248 | -7358.150000 | -11539.500000 |
| cached_input_tokens | 0.710946 | -6726.400000 | -9984.000000 |
| uncached_input_tokens | 0.950809 | -631.750000 | -217.000000 |
| output_tokens | 0.888949 | -71.900000 | -75.000000 |
| wall_time_seconds | 0.932646 | -1.343258 | -2.535382 |
| end_to_end_wall_seconds | 0.942590 | -1.145830 | -2.340098 |
| native_exec_wall_seconds | unavailable | unavailable | unavailable |
| approval_index_wall_seconds | unavailable | 0.201935 | 0.219310 |
| approval_index_cpu_seconds | unavailable | 0.055993 | 0.046616 |
| context_preparation_wall_seconds | unavailable | unavailable | unavailable |
| context_preparation_cpu_seconds | unavailable | unavailable | unavailable |
| process_tree_peak_rss_bytes | 0.988692 | -2805964.800000 | -2406400.000000 |
| cpu_seconds | 1.043212 | 0.236000 | 0.060000 |
| total_observed_local_cpu_seconds | 1.053464 | 0.291993 | 0.144181 |
| mcp_calls | unavailable | 0 | 0.000000 |
| model_calls | unavailable | unavailable | unavailable |
| repeated_file_reads | unavailable | unavailable | unavailable |
| observed_file_read_commands | 0.058824 | -0.800000 | -1.000000 |
| observed_repeated_read_commands | unavailable | 0 | 0.000000 |
| actual_cost_usd | unavailable | unavailable | unavailable |
| computed_cost_usd | unavailable | unavailable | unavailable |

## C_over_B

Verified pairs: 20; excluded: 0.

| Metric | Overall mean ratio | Paired difference mean | Paired difference median |
|---|---:|---:|---:|
| input_tokens | 0.821261 | -6258.250000 | -11718.000000 |
| cached_input_tokens | 0.764115 | -5107.200000 | -8448.000000 |
| uncached_input_tokens | 0.913857 | -1151.050000 | -238.000000 |
| output_tokens | 0.955825 | -26.600000 | -45.000000 |
| wall_time_seconds | 1.001760 | 0.032683 | -1.042646 |
| end_to_end_wall_seconds | 1.002478 | 0.046506 | -0.983935 |
| native_exec_wall_seconds | 1.001935 | 0.035417 | -1.094652 |
| approval_index_wall_seconds | 1.139896 | 0.024783 | 0.000000 |
| approval_index_cpu_seconds | 1.053629 | 0.002850 | 0.000000 |
| context_preparation_wall_seconds | 1.042833 | 0.002463 | 0.001179 |
| context_preparation_cpu_seconds | 1.038154 | 0.002191 | 0.001433 |
| process_tree_peak_rss_bytes | 0.977394 | -5673984 | -5883904.000000 |
| cpu_seconds | 1.200738 | 0.952500 | -0.060000 |
| total_observed_local_cpu_seconds | 1.199108 | 0.955350 | -0.041974 |
| mcp_calls | unavailable | 0 | 0.000000 |
| model_calls | unavailable | unavailable | unavailable |
| repeated_file_reads | unavailable | unavailable | unavailable |
| observed_file_read_commands | 0.062500 | -0.750000 | -1.000000 |
| observed_repeated_read_commands | unavailable | 0 | 0.000000 |
| actual_cost_usd | unavailable | unavailable | unavailable |
| computed_cost_usd | unavailable | unavailable | unavailable |

## B_over_A

Verified pairs: 20; excluded: 0.

| Metric | Overall mean ratio | Paired difference mean | Paired difference median |
|---|---:|---:|---:|
| input_tokens | 0.969543 | -1099.900000 | 117.000000 |
| cached_input_tokens | 0.930418 | -1619.200000 | 128.000000 |
| uncached_input_tokens | 1.040435 | 519.300000 | 2.000000 |
| output_tokens | 0.930033 | -45.300000 | -45.000000 |
| wall_time_seconds | 0.931007 | -1.375941 | -1.178007 |
| end_to_end_wall_seconds | 0.940260 | -1.192336 | -0.990583 |
| native_exec_wall_seconds | unavailable | unavailable | unavailable |
| approval_index_wall_seconds | unavailable | 0.177152 | 0.138886 |
| approval_index_cpu_seconds | unavailable | 0.053143 | 0.058828 |
| context_preparation_wall_seconds | unavailable | unavailable | unavailable |
| context_preparation_cpu_seconds | unavailable | unavailable | unavailable |
| process_tree_peak_rss_bytes | 1.011558 | 2868019.200000 | 2805760.000000 |
| cpu_seconds | 0.868809 | -0.716500 | 0.215000 |
| total_observed_local_cpu_seconds | 0.878539 | -0.663357 | 0.261049 |
| mcp_calls | unavailable | 0 | 0.000000 |
| model_calls | unavailable | unavailable | unavailable |
| repeated_file_reads | unavailable | unavailable | unavailable |
| observed_file_read_commands | 0.941176 | -0.050000 | 0.000000 |
| observed_repeated_read_commands | unavailable | 0 | 0.000000 |
| actual_cost_usd | unavailable | unavailable | unavailable |
| computed_cost_usd | unavailable | unavailable | unavailable |

## Selection strata (descriptive)

| Stratum | Arm | Attempted | Successful | Mean full seconds | Mean input |
|---|---|---:|---:|---:|---:|
| caller_context_supplied | A | 4 | 0 | 20.503343 | 33605 |
| caller_context_supplied | B | 4 | 0 | 19.294030 | 27558.750000 |
| caller_context_supplied | C | 4 | 0 | 19.285687 | 30550.250000 |
| explicit_focus | A | 16 | 0 | 19.822469 | 36740.250000 |
| explicit_focus | B | 16 | 0 | 18.634378 | 36876.937500 |
| explicit_focus | C | 16 | 0 | 18.694596 | 28306.250000 |

Permutation counts: {"ABC": 4, "ACB": 4, "BAC": 2, "BCA": 4, "CAB": 2, "CBA": 4}.

Actual cost per successful task (all attempted costs, including failures):
- A: unavailable; 20 attempted costs / 0 successful tasks. No successful tasks
- B: unavailable; 20 attempted costs / 0 successful tasks. No successful tasks
- C: unavailable; 20 attempted costs / 0 successful tasks. No successful tasks

## Individual original runs

| Run | Status | Grade | Treatment | Input | Cached | Output | Full seconds |
|---|---|---|---|---:|---:|---:|---:|
| workflow-ts-workflow-text-negative-array-offset-r1-A | failed | False | True | 36891 | 23680 | 961 | 22.620204 |
| workflow-ts-workflow-text-negative-array-offset-r1-C | failed | False | True | 36748 | 23552 | 850 | 20.445852 |
| workflow-ts-workflow-text-negative-array-offset-r1-B | failed | False | True | 23972 | 11392 | 619 | 16.860739 |
| workflow-py-workflow-form-ascii-count-field-r1-A | failed | False | True | 24406 | 11520 | 577 | 16.396245 |
| workflow-py-workflow-form-ascii-count-field-r1-B | failed | False | True | 37875 | 12544 | 836 | 24.720368 |
| workflow-py-workflow-form-ascii-count-field-r1-C | failed | False | True | 24474 | 11520 | 649 | 19.081954 |
| workflow-ts-workflow-signals-circular-angle-difference-r1-B | failed | False | True | 36049 | 11648 | 819 | 20.816941 |
| workflow-ts-workflow-signals-circular-angle-difference-r1-C | failed | False | True | 36318 | 23168 | 855 | 23.447727 |
| workflow-ts-workflow-signals-circular-angle-difference-r1-A | failed | False | True | 35951 | 22912 | 920 | 22.758157 |
| workflow-py-workflow-form-form-plus-decoding-r1-C | failed | False | True | 24318 | 11520 | 411 | 13.408102 |
| workflow-py-workflow-form-form-plus-decoding-r1-B | failed | False | True | 36253 | 23040 | 527 | 16.045380 |
| workflow-py-workflow-form-form-plus-decoding-r1-A | failed | False | True | 35822 | 22912 | 446 | 15.622677 |
| workflow-py-workflow-finance-net-flow-report-r1-B | failed | False | True | 36290 | 23168 | 556 | 19.327186 |
| workflow-py-workflow-finance-net-flow-report-r1-A | failed | False | True | 36168 | 23040 | 599 | 17.126702 |
| workflow-py-workflow-finance-net-flow-report-r1-C | failed | False | True | 24476 | 11648 | 504 | 14.661080 |
| workflow-ts-workflow-signals-threshold-hysteresis-r1-C | failed | False | True | 37958 | 24064 | 695 | 21.473428 |
| workflow-ts-workflow-signals-threshold-hysteresis-r1-A | failed | False | True | 36095 | 11776 | 780 | 19.658033 |
| workflow-ts-workflow-signals-threshold-hysteresis-r1-B | failed | False | True | 36219 | 23168 | 634 | 18.268206 |
| workflow-ts-workflow-text-path-segment-roundtrip-r1-A | failed | False | True | 35693 | 22912 | 517 | 19.579764 |
| workflow-ts-workflow-text-path-segment-roundtrip-r1-C | failed | False | True | 24174 | 20480 | 486 | 16.253946 |
| workflow-ts-workflow-text-path-segment-roundtrip-r1-B | failed | False | True | 48323 | 35200 | 627 | 17.452670 |
| workflow-py-workflow-form-query-latest-value-r1-A | failed | False | True | 36616 | 23040 | 818 | 20.609426 |
| workflow-py-workflow-form-query-latest-value-r1-B | failed | False | True | 36548 | 11392 | 658 | 20.018088 |
| workflow-py-workflow-form-query-latest-value-r1-C | failed | False | True | 24791 | 11648 | 612 | 20.168220 |
| workflow-ts-workflow-text-utf8-byte-length-r1-B | failed | False | True | 35660 | 22912 | 535 | 19.603529 |
| workflow-ts-workflow-text-utf8-byte-length-r1-C | failed | False | True | 23919 | 11520 | 448 | 14.546375 |
| workflow-ts-workflow-text-utf8-byte-length-r1-A | failed | False | True | 35508 | 22912 | 556 | 19.549137 |
| workflow-py-workflow-finance-discount-before-tax-r1-C | failed | False | True | 24210 | 11520 | 404 | 15.292663 |
| workflow-py-workflow-finance-discount-before-tax-r1-B | failed | False | True | 36008 | 32128 | 431 | 14.866140 |
| workflow-py-workflow-finance-discount-before-tax-r1-A | failed | False | True | 35839 | 22912 | 436 | 18.173914 |
| workflow-ts-workflow-text-negative-array-offset-r2-B | failed | False | True | 23989 | 11392 | 634 | 19.390545 |
| workflow-ts-workflow-text-negative-array-offset-r2-C | failed | False | True | 36616 | 23552 | 743 | 22.591175 |
| workflow-ts-workflow-text-negative-array-offset-r2-A | failed | False | True | 48806 | 35456 | 794 | 28.731804 |
| workflow-py-workflow-form-ascii-count-field-r2-C | failed | False | True | 24363 | 11520 | 562 | 15.023765 |
| workflow-py-workflow-form-ascii-count-field-r2-B | failed | False | True | 24399 | 20480 | 577 | 16.204470 |
| workflow-py-workflow-form-ascii-count-field-r2-A | failed | False | True | 24317 | 11520 | 527 | 14.265119 |
| workflow-ts-workflow-signals-circular-angle-difference-r2-A | failed | False | True | 35806 | 31872 | 763 | 19.552619 |
| workflow-ts-workflow-signals-circular-angle-difference-r2-C | failed | False | True | 36248 | 23296 | 672 | 46.368701 |
| workflow-ts-workflow-signals-circular-angle-difference-r2-B | failed | False | True | 35886 | 11392 | 746 | 24.632077 |
| workflow-py-workflow-form-form-plus-decoding-r2-A | failed | False | True | 35966 | 22912 | 465 | 16.958748 |
| workflow-py-workflow-form-form-plus-decoding-r2-B | failed | False | True | 36242 | 23040 | 528 | 17.112337 |
| workflow-py-workflow-form-form-plus-decoding-r2-C | failed | False | True | 24406 | 11520 | 483 | 14.959777 |
| workflow-py-workflow-finance-net-flow-report-r2-C | failed | False | True | 37986 | 24192 | 580 | 18.911394 |
| workflow-py-workflow-finance-net-flow-report-r2-A | failed | False | True | 36180 | 32000 | 608 | 26.550940 |
| workflow-py-workflow-finance-net-flow-report-r2-B | failed | False | True | 36318 | 32128 | 561 | 18.113209 |
| workflow-ts-workflow-signals-threshold-hysteresis-r2-B | failed | False | True | 36289 | 29312 | 672 | 22.223687 |
| workflow-ts-workflow-signals-threshold-hysteresis-r2-A | failed | False | True | 36022 | 23040 | 688 | 25.834226 |
| workflow-ts-workflow-signals-threshold-hysteresis-r2-C | failed | False | True | 37074 | 23680 | 682 | 18.489152 |
| workflow-ts-workflow-text-path-segment-roundtrip-r2-B | failed | False | True | 35831 | 23040 | 508 | 15.972473 |
| workflow-ts-workflow-text-path-segment-roundtrip-r2-C | failed | False | True | 24129 | 11520 | 449 | 15.185307 |
| workflow-ts-workflow-text-path-segment-roundtrip-r2-A | failed | False | True | 48128 | 34944 | 670 | 19.350290 |
| workflow-py-workflow-form-query-latest-value-r2-C | failed | False | True | 24775 | 8960 | 592 | 15.133374 |
| workflow-py-workflow-form-query-latest-value-r2-B | failed | False | True | 36641 | 23168 | 665 | 20.965819 |
| workflow-py-workflow-form-query-latest-value-r2-A | failed | False | True | 36529 | 11264 | 729 | 19.523523 |
| workflow-ts-workflow-text-utf8-byte-length-r2-A | failed | False | True | 35611 | 31872 | 587 | 21.966555 |
| workflow-ts-workflow-text-utf8-byte-length-r2-C | failed | False | True | 23909 | 20480 | 437 | 13.919559 |
| workflow-ts-workflow-text-utf8-byte-length-r2-B | failed | False | True | 35531 | 22912 | 482 | 16.020998 |
| workflow-py-workflow-finance-discount-before-tax-r2-A | failed | False | True | 35910 | 22912 | 508 | 14.344796 |
| workflow-py-workflow-finance-discount-before-tax-r2-B | failed | False | True | 35943 | 29568 | 428 | 16.711302 |
| workflow-py-workflow-finance-discount-before-tax-r2-C | failed | False | True | 24209 | 11520 | 397 | 16.894731 |

## Failures

- workflow-ts-workflow-text-negative-array-offset-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-negative-array-offset-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-negative-array-offset-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-ascii-count-field-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-ascii-count-field-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-ascii-count-field-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-circular-angle-difference-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-circular-angle-difference-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-circular-angle-difference-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-form-plus-decoding-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-form-plus-decoding-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-form-plus-decoding-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-net-flow-report-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-net-flow-report-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-net-flow-report-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-threshold-hysteresis-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-threshold-hysteresis-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-threshold-hysteresis-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-path-segment-roundtrip-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-path-segment-roundtrip-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-path-segment-roundtrip-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-query-latest-value-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-query-latest-value-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-query-latest-value-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-utf8-byte-length-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-utf8-byte-length-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-utf8-byte-length-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-discount-before-tax-r1-C: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-discount-before-tax-r1-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-discount-before-tax-r1-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-negative-array-offset-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-negative-array-offset-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-negative-array-offset-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-ascii-count-field-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-ascii-count-field-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-ascii-count-field-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-circular-angle-difference-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-circular-angle-difference-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-circular-angle-difference-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-form-plus-decoding-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-form-plus-decoding-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-form-plus-decoding-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-net-flow-report-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-net-flow-report-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-net-flow-report-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-threshold-hysteresis-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-threshold-hysteresis-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-signals-threshold-hysteresis-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-path-segment-roundtrip-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-path-segment-roundtrip-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-path-segment-roundtrip-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-query-latest-value-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-query-latest-value-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-form-query-latest-value-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-utf8-byte-length-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-utf8-byte-length-r2-C: failed; Protected repository tests or Git metadata changed
- workflow-ts-workflow-text-utf8-byte-length-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-discount-before-tax-r2-A: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-discount-before-tax-r2-B: failed; Protected repository tests or Git metadata changed
- workflow-py-workflow-finance-discount-before-tax-r2-C: failed; Protected repository tests or Git metadata changed

## Limitations

- All original assignments, failures and unknown interruptions are retained; no automatic retries. Successful completion requires external behavior grade, treatment and native schema validity.
- A is direct standard Codex. B adds complete caller-selected production files. C adds those files plus complete caller-selected supporting tests. All arms receive identical common prompts, path hints and test argv. No auxiliary model or configured MCP is used.
- Ten fresh purpose-built tasks, five Python/five TypeScript, are repeated twice in isolated worktrees/native state/databases. Repeat two reverses each task's arm order; pairwise precedence is balanced but provider and operating-system caches are uncontrolled.
- Source hashes attest complete current selected files at preparation, not semantic completeness or later edits. Supporting tests are task-author-selected and equally disclosed to every arm; this is not autonomous repository discovery or cross-session memory.
- Full time includes cold approval/index and launcher/native work, excluding worktree construction and grading. CPU is a local observed lower bound; child RSS excludes parent indexing, may miss short-lived children and double-count shared pages.
- Actual cost, model calls and filesystem reads remain unavailable. Cached input is included within total input. Separately labelled price-equivalent estimates must include failed attempts and exclude unknown usage from zero-cost assumptions.
- Paired comparisons require matching commits/common prompts, valid treatment, valid native completion and unchanged frozen source; primary intent-to-treat per-arm aggregates retain all originals regardless of pair eligibility.
