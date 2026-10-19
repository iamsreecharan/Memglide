# Three-arm workflow cost assessment

A: Standard Codex; B: Memglide source-only; C: Memglide source plus support.

**All dollars are API-price equivalents, not actual bills.** Each original attempt is priced once; pair views are references, not additional spend.

| Arm | Attempts | Successful assignments | USD / successful task | Total estimated USD |
|---|---:|---:|---:|---:|
| A | 20 | 20 | 0.029961 | 0.599212 |
| B | 20 | 20 | 0.029219 | 0.584384 |
| C | 20 | 20 | 0.030541 | 0.610830 |

| Comparison | Cost / success saving % | Possible-write saving range % | Paired outcomes |
|---|---:|---|---|
| C_over_A | -1.939 | -17.663 to 11.741 | {"baseline_cheaper": 9, "candidate_cheaper": 11, "equal": 0, "unavailable": 0} |
| C_over_B | -4.525 | -20.648 to 9.577 | {"baseline_cheaper": 9, "candidate_cheaper": 11, "equal": 0, "unavailable": 0} |
| B_over_A | 2.475 | -12.736 to 15.562 | {"baseline_cheaper": 9, "candidate_cheaper": 11, "equal": 0, "unavailable": 0} |

Prespecified promotion gate passed: **False**. Keep support explicitly optional; do not promote defaults.

- Focused cost/full-time mean or median regresses or is unavailable overall or in a repeat

## Individual attempts

| Run | Arm | Success | Input | Cached | Output | Estimated USD | Full seconds |
|---|---|---|---:|---:|---:|---:|---:|
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r1-A | A | True | 49,068 | 35,328 | 1,017 | 0.041183 | 35.832 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r1-C | C | True | 49,125 | 35,456 | 983 | 0.040714 | 25.846 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r1-B | B | True | 62,346 | 48,384 | 1,149 | 0.044252 | 32.798 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r1-A | A | True | 24,891 | 20,608 | 592 | 0.016547 | 17.068 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r1-B | B | True | 25,032 | 11,648 | 753 | 0.035463 | 19.443 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r1-C | C | True | 25,033 | 20,608 | 769 | 0.018601 | 18.758 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r1-B | B | True | 36,249 | 32,256 | 492 | 0.016132 | 16.507 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r1-C | C | True | 36,490 | 23,424 | 544 | 0.033914 | 20.984 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r1-A | A | True | 36,221 | 23,168 | 607 | 0.034493 | 17.332 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r1-C | C | True | 37,481 | 32,640 | 765 | 0.020596 | 21.432 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r1-B | B | True | 36,835 | 23,424 | 605 | 0.035214 | 18.107 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r1-A | A | True | 36,790 | 23,424 | 648 | 0.035554 | 18.116 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r1-B | B | True | 37,648 | 23,808 | 857 | 0.038631 | 22.267 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r1-A | A | True | 37,496 | 23,552 | 904 | 0.039283 | 20.246 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r1-C | C | True | 38,225 | 24,064 | 921 | 0.039938 | 20.950 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r1-C | C | True | 51,344 | 34,048 | 1,093 | 0.048927 | 32.009 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r1-A | A | True | 37,116 | 20,352 | 1,011 | 0.045673 | 23.472 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r1-B | B | True | 37,119 | 32,640 | 798 | 0.020202 | 24.908 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-A | A | True | 37,119 | 23,296 | 1,253 | 0.042506 | 26.157 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-C | C | True | 37,498 | 32,640 | 1,170 | 0.024680 | 26.265 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-B | B | True | 51,056 | 45,568 | 1,397 | 0.029503 | 30.197 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r1-A | A | True | 37,340 | 32,384 | 844 | 0.021590 | 23.280 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r1-B | B | True | 37,858 | 23,680 | 903 | 0.039754 | 23.530 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r1-C | C | True | 25,401 | 20,864 | 748 | 0.018640 | 16.631 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r1-B | B | True | 36,520 | 32,256 | 821 | 0.019964 | 23.938 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r1-C | C | True | 78,444 | 63,232 | 1,195 | 0.048697 | 29.125 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r1-A | A | True | 49,862 | 33,152 | 1,048 | 0.047215 | 24.894 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r1-C | C | True | 24,670 | 20,608 | 456 | 0.014745 | 14.873 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r1-B | B | True | 36,932 | 32,384 | 550 | 0.017834 | 18.019 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r1-A | A | True | 36,473 | 32,128 | 527 | 0.017173 | 15.532 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r2-B | B | True | 36,839 | 32,384 | 895 | 0.021098 | 20.323 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r2-C | C | True | 49,143 | 35,456 | 1,001 | 0.040930 | 25.860 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r2-A | A | True | 49,101 | 44,288 | 985 | 0.023905 | 25.183 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r2-C | C | True | 24,990 | 17,920 | 727 | 0.023202 | 16.039 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r2-B | B | True | 25,001 | 11,648 | 714 | 0.035011 | 17.522 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r2-A | A | True | 24,994 | 20,608 | 730 | 0.018133 | 17.774 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r2-A | A | True | 36,241 | 32,128 | 510 | 0.016539 | 15.263 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r2-C | C | True | 24,640 | 20,608 | 541 | 0.015535 | 14.514 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r2-B | B | True | 36,428 | 32,256 | 591 | 0.017480 | 17.720 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r2-A | A | True | 36,861 | 20,480 | 638 | 0.041190 | 16.046 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r2-B | B | True | 36,949 | 32,384 | 670 | 0.019068 | 17.450 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r2-C | C | True | 37,146 | 23,680 | 664 | 0.035940 | 17.165 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r2-C | C | True | 38,238 | 33,024 | 863 | 0.022360 | 38.909 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r2-A | A | True | 37,449 | 20,480 | 873 | 0.044716 | 20.049 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r2-B | B | True | 37,745 | 23,808 | 897 | 0.039225 | 22.060 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r2-B | B | True | 37,116 | 32,640 | 842 | 0.020636 | 19.353 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r2-A | A | True | 50,621 | 45,440 | 1,206 | 0.026966 | 25.350 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r2-C | C | True | 37,819 | 20,992 | 1,039 | 0.046143 | 21.343 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r2-B | B | True | 37,095 | 20,480 | 1,073 | 0.046008 | 22.080 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r2-C | C | True | 80,144 | 73,728 | 1,448 | 0.034685 | 33.706 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r2-A | A | True | 50,325 | 45,312 | 1,167 | 0.026227 | 25.450 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r2-C | C | True | 37,972 | 33,024 | 837 | 0.021568 | 21.259 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r2-B | B | True | 37,326 | 20,608 | 721 | 0.042707 | 20.539 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r2-A | A | True | 37,609 | 32,512 | 851 | 0.021955 | 17.834 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r2-A | A | True | 49,114 | 44,672 | 778 | 0.021131 | 18.982 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r2-C | C | True | 49,490 | 33,152 | 780 | 0.043791 | 19.803 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r2-B | B | True | 49,554 | 41,344 | 848 | 0.029034 | 22.974 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r2-A | A | True | 36,498 | 32,128 | 528 | 0.017233 | 15.550 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r2-B | B | True | 36,624 | 32,384 | 545 | 0.017168 | 14.187 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r2-C | C | True | 36,828 | 32,512 | 534 | 0.017223 | 15.435 |

## Per-arm descriptive metrics

| Metric | Arm | Mean | Median | p95 | Complete total | Missing |
|---|---|---:|---:|---:|---:|---:|
| input_tokens | A | 39,559.450 | 37,229.500 | 50,325.000 | 791,189.000 | 0 |
| cached_input_tokens | A | 30,272.000 | 32,128.000 | 45,312.000 | 605,440.000 | 0 |
| output_tokens | A | 835.850 | 847.500 | 1,206.000 | 16,717.000 | 0 |
| cache_write_input_tokens | A | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| reasoning_output_tokens | A | 12.450 | 0.000 | 77.000 | 249.000 | 0 |
| uncached_input_tokens | A | 9,287.450 | 5,139.000 | 16,764.000 | 185,749.000 | 0 |
| ordinary_uncached_input_tokens | A | 9,287.450 | 5,139.000 | 16,764.000 | 185,749.000 | 0 |
| end_to_end_wall_seconds | A | 20.970 | 19.515 | 26.157 | 419.409 | 0 |
| total_observed_local_cpu_seconds | A | 5.282 | 4.405 | 7.880 | 105.650 | 0 |
| process_tree_peak_rss_bytes | A | 267,506,688.000 | 241,702,912.000 | 362,688,512.000 | unavailable | 0 |
| mcp_calls | A | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| observed_file_read_commands | A | 0.950 | 1.000 | 1.000 | 19.000 | 0 |
| observed_repeated_read_commands | A | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| test_count | A | 17.950 | 19.000 | 21.000 | 359.000 | 0 |
| observed_command_items | A | 3.450 | 3.000 | 5.000 | 69.000 | 0 |
| observed_file_change_items | A | 1.100 | 1.000 | 2.000 | 22.000 | 0 |
| input_tokens | B | 38,413.600 | 37,022.000 | 51,056.000 | 768,272.000 | 0 |
| cached_input_tokens | B | 29,299.200 | 32,256.000 | 45,568.000 | 585,984.000 | 0 |
| output_tokens | B | 806.050 | 809.500 | 1,149.000 | 16,121.000 | 0 |
| cache_write_input_tokens | B | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| reasoning_output_tokens | B | 14.550 | 0.000 | 35.000 | 291.000 | 0 |
| uncached_input_tokens | B | 9,114.400 | 6,849.000 | 16,615.000 | 182,288.000 | 0 |
| ordinary_uncached_input_tokens | B | 9,114.400 | 6,849.000 | 16,615.000 | 182,288.000 | 0 |
| end_to_end_wall_seconds | B | 21.196 | 20.431 | 30.197 | 423.924 | 0 |
| total_observed_local_cpu_seconds | B | 5.403 | 4.916 | 9.155 | 108.065 | 0 |
| process_tree_peak_rss_bytes | B | 263,587,225.600 | 255,070,208.000 | 361,996,288.000 | unavailable | 0 |
| mcp_calls | B | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| observed_file_read_commands | B | 1.000 | 1.000 | 2.000 | 20.000 | 0 |
| observed_repeated_read_commands | B | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| test_count | B | 17.900 | 19.000 | 20.000 | 358.000 | 0 |
| observed_command_items | B | 3.750 | 3.000 | 5.000 | 75.000 | 0 |
| observed_file_change_items | B | 1.050 | 1.000 | 1.000 | 21.000 | 0 |
| input_tokens | C | 41,006.050 | 37,658.500 | 78,444.000 | 820,121.000 | 0 |
| cached_input_tokens | C | 31,584.000 | 32,576.000 | 63,232.000 | 631,680.000 | 0 |
| output_tokens | C | 853.900 | 808.500 | 1,195.000 | 17,078.000 | 0 |
| cache_write_input_tokens | C | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| reasoning_output_tokens | C | 18.950 | 0.000 | 63.000 | 379.000 | 0 |
| uncached_input_tokens | C | 9,422.050 | 6,743.000 | 16,827.000 | 188,441.000 | 0 |
| ordinary_uncached_input_tokens | C | 9,422.050 | 6,743.000 | 16,827.000 | 188,441.000 | 0 |
| end_to_end_wall_seconds | C | 22.545 | 21.121 | 33.706 | 450.904 | 0 |
| total_observed_local_cpu_seconds | C | 6.380 | 4.563 | 12.630 | 127.602 | 0 |
| process_tree_peak_rss_bytes | C | 267,044,659.200 | 246,763,520.000 | 375,877,632.000 | unavailable | 0 |
| mcp_calls | C | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| observed_file_read_commands | C | 0.300 | 0.000 | 1.000 | 6.000 | 0 |
| observed_repeated_read_commands | C | 0.000 | 0.000 | 0.000 | 0.000 | 0 |
| test_count | C | 18.000 | 19.000 | 20.000 | 360.000 | 0 |
| observed_command_items | C | 4.500 | 4.000 | 6.000 | 90.000 | 0 |
| observed_file_change_items | C | 1.100 | 1.000 | 2.000 | 22.000 | 0 |

All per-task pairs, repeats, language/task/selection strata, gate checks, component charges and source/native fidelity are retained in JSON.

- Every dollar amount is a standard API list-price equivalent, not actual provider billing or a subscription charge.
- Cache writes reported as zero may reflect an upstream default. Conservative possible-write ranges are scenarios, not confidence intervals.
- Each native attempt is priced once. All failures and unknown attempts remain in per-arm numerators; unknown usage prevents a complete total or cost per success.
- Cached input is included in total input and reasoning is included in output; neither is billed twice.
- Completed command/file-change items are invocation/patch proxies, not provider model calls, individual file reads or unique edits. Missing telemetry remains null.
- Local CPU is a sampled lower bound; child RSS can double-count shared pages and omits parent indexing. Neither has a fabricated dollar rate.
- Provided-context controls are excluded from source-benefit promotion checks. Repeat consistency is descriptive, not statistical proof.
- Fresh small synthetic tasks with uncontrolled provider/OS caches do not establish production, long-term memory or universal efficiency gains.
