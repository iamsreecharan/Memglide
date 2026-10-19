# Fresh confirmation three-arm workflow comparison

A = standard Codex; B = Memglide source-only; C = Memglide source plus supporting tests.
Actual costs unavailable; price-equivalent estimates are separately labelled.
This fresh confirmation follows 60 retained workflow-1 strict failures caused by edits to existing protected tests; those results remain failed and unchanged.

| Arm | Planned | Attempted | Successful | Failed grades | Completion rate |
|---|---:|---:|---:|---:|---:|
| A | 20 | 20 | 20 | 0 | 1.000000 |
| B | 20 | 20 | 20 | 0 | 1.000000 |
| C | 20 | 20 | 20 | 0 | 1.000000 |

## Measurements

Totals are unavailable when any attempted observation is unknown; RSS is non-additive.

| Metric | Arm | Mean | Median | p95 | Total | Observed |
|---|---|---:|---:|---:|---:|---:|
| input_tokens | A | 39559.450000 | 37229.500000 | 50325 | 791189 | 20 |
| input_tokens | B | 38413.600000 | 37022.000000 | 51056 | 768272 | 20 |
| input_tokens | C | 41006.050000 | 37658.500000 | 78444 | 820121 | 20 |
| cached_input_tokens | A | 30272 | 32128.000000 | 45312 | 605440 | 20 |
| cached_input_tokens | B | 29299.200000 | 32256.000000 | 45568 | 585984 | 20 |
| cached_input_tokens | C | 31584 | 32576.000000 | 63232 | 631680 | 20 |
| uncached_input_tokens | A | 9287.450000 | 5139.000000 | 16764 | 185749 | 20 |
| uncached_input_tokens | B | 9114.400000 | 6849.000000 | 16615 | 182288 | 20 |
| uncached_input_tokens | C | 9422.050000 | 6743.000000 | 16827 | 188441 | 20 |
| output_tokens | A | 835.850000 | 847.500000 | 1206 | 16717 | 20 |
| output_tokens | B | 806.050000 | 809.500000 | 1149 | 16121 | 20 |
| output_tokens | C | 853.900000 | 808.500000 | 1195 | 17078 | 20 |
| wall_time_seconds | A | 20.957443 | 19.509571 | 26.143018 | 419.148865 | 20 |
| wall_time_seconds | B | 20.950088 | 20.357942 | 29.504086 | 419.001766 | 20 |
| wall_time_seconds | C | 22.348936 | 20.967307 | 33.407815 | 446.978723 | 20 |
| end_to_end_wall_seconds | A | 20.970429 | 19.515217 | 26.157443 | 419.408578 | 20 |
| end_to_end_wall_seconds | B | 21.196199 | 20.431257 | 30.197017 | 423.923973 | 20 |
| end_to_end_wall_seconds | C | 22.545187 | 21.121429 | 33.705593 | 450.903746 | 20 |
| native_exec_wall_seconds | A | unavailable | unavailable | unavailable | unavailable | 0 |
| native_exec_wall_seconds | B | 20.624751 | 19.967357 | 29.078193 | 412.495022 | 20 |
| native_exec_wall_seconds | C | 22.065257 | 20.726338 | 32.919134 | 441.305131 | 20 |
| approval_index_wall_seconds | A | 0 | 0.000000 | 0 | 0 | 20 |
| approval_index_wall_seconds | B | 0.218756 | 0.179330 | 0.686759 | 4.375115 | 20 |
| approval_index_wall_seconds | C | 0.180866 | 0.158389 | 0.500346 | 3.617314 | 20 |
| approval_index_cpu_seconds | A | 0 | 0.000000 | 0 | 0 | 20 |
| approval_index_cpu_seconds | B | 0.056226 | 0.050465 | 0.120519 | 1.124529 | 20 |
| approval_index_cpu_seconds | C | 0.048606 | 0.049773 | 0.101318 | 0.972125 | 20 |
| context_preparation_wall_seconds | A | unavailable | unavailable | unavailable | unavailable | 0 |
| context_preparation_wall_seconds | B | 0.083960 | 0.064249 | 0.331286 | 1.679201 | 20 |
| context_preparation_wall_seconds | C | 0.067740 | 0.067757 | 0.117243 | 1.354796 | 20 |
| context_preparation_cpu_seconds | A | unavailable | unavailable | unavailable | unavailable | 0 |
| context_preparation_cpu_seconds | B | 0.083629 | 0.064292 | 0.325780 | 1.672580 | 20 |
| context_preparation_cpu_seconds | C | 0.067564 | 0.067732 | 0.117248 | 1.351277 | 20 |
| process_tree_peak_rss_bytes | A | 267506688 | 241702912.000000 | 362688512 | unavailable | 20 |
| process_tree_peak_rss_bytes | B | 263587225.600000 | 255070208.000000 | 361996288 | unavailable | 20 |
| process_tree_peak_rss_bytes | C | 267044659.200000 | 246763520.000000 | 375877632 | unavailable | 20 |
| cpu_seconds | A | 5.282500 | 4.405000 | 7.880000 | 105.650000 | 20 |
| cpu_seconds | B | 5.347000 | 4.850000 | 9.100000 | 106.940000 | 20 |
| cpu_seconds | C | 6.331500 | 4.520000 | 12.580000 | 126.630000 | 20 |
| total_observed_local_cpu_seconds | A | 5.282500 | 4.405000 | 7.880000 | 105.650000 | 20 |
| total_observed_local_cpu_seconds | B | 5.403226 | 4.916195 | 9.155159 | 108.064529 | 20 |
| total_observed_local_cpu_seconds | C | 6.380106 | 4.562529 | 12.629564 | 127.602125 | 20 |
| mcp_calls | A | 0 | 0.000000 | 0 | 0 | 20 |
| mcp_calls | B | 0 | 0.000000 | 0 | 0 | 20 |
| mcp_calls | C | 0 | 0.000000 | 0 | 0 | 20 |
| model_calls | A | unavailable | unavailable | unavailable | unavailable | 0 |
| model_calls | B | unavailable | unavailable | unavailable | unavailable | 0 |
| model_calls | C | unavailable | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | A | unavailable | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | B | unavailable | unavailable | unavailable | unavailable | 0 |
| repeated_file_reads | C | unavailable | unavailable | unavailable | unavailable | 0 |
| observed_file_read_commands | A | 0.950000 | 1.000000 | 1 | 19 | 20 |
| observed_file_read_commands | B | 1 | 1.000000 | 2 | 20 | 20 |
| observed_file_read_commands | C | 0.300000 | 0.000000 | 1 | 6 | 20 |
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
| input_tokens | 1.036568 | 1446.600000 | 307.500000 |
| cached_input_tokens | 1.043340 | 1312 | 320.000000 |
| uncached_input_tokens | 1.014493 | 134.600000 | -62.500000 |
| output_tokens | 1.021595 | 18.050000 | 4.000000 |
| wall_time_seconds | 1.066396 | 1.391493 | 0.645447 |
| end_to_end_wall_seconds | 1.075094 | 1.574758 | 0.762675 |
| native_exec_wall_seconds | unavailable | unavailable | unavailable |
| approval_index_wall_seconds | unavailable | 0.180866 | 0.158389 |
| approval_index_cpu_seconds | unavailable | 0.048606 | 0.049773 |
| context_preparation_wall_seconds | unavailable | unavailable | unavailable |
| context_preparation_cpu_seconds | unavailable | unavailable | unavailable |
| process_tree_peak_rss_bytes | 0.998273 | -462028.800000 | 624640.000000 |
| cpu_seconds | 1.198580 | 1.049000 | 0.035000 |
| total_observed_local_cpu_seconds | 1.207782 | 1.097606 | 0.064655 |
| mcp_calls | unavailable | 0 | 0.000000 |
| model_calls | unavailable | unavailable | unavailable |
| repeated_file_reads | unavailable | unavailable | unavailable |
| observed_file_read_commands | 0.315789 | -0.650000 | -1.000000 |
| observed_repeated_read_commands | unavailable | 0 | 0.000000 |
| actual_cost_usd | unavailable | unavailable | unavailable |
| computed_cost_usd | unavailable | unavailable | unavailable |

## C_over_B

Verified pairs: 20; excluded: 0.

| Metric | Overall mean ratio | Paired difference mean | Paired difference median |
|---|---:|---:|---:|
| input_tokens | 1.067488 | 2592.450000 | 222.500000 |
| cached_input_tokens | 1.077982 | 2284.800000 | 192.000000 |
| uncached_input_tokens | 1.033754 | 307.650000 | -216.500000 |
| output_tokens | 1.059364 | 47.850000 | 14.500000 |
| wall_time_seconds | 1.066771 | 1.398848 | 0.265131 |
| end_to_end_wall_seconds | 1.063643 | 1.348989 | 0.217356 |
| native_exec_wall_seconds | 1.069844 | 1.440505 | 0.384889 |
| approval_index_wall_seconds | 0.826793 | -0.037890 | 0.000000 |
| approval_index_cpu_seconds | 0.864473 | -0.007620 | 0.000000 |
| context_preparation_wall_seconds | 0.806810 | -0.016220 | 0.000118 |
| context_preparation_cpu_seconds | 0.807900 | -0.016065 | 0.000118 |
| process_tree_peak_rss_bytes | 1.013117 | 3457433.600000 | 1085440.000000 |
| cpu_seconds | 1.184122 | 0.984500 | -0.130000 |
| total_observed_local_cpu_seconds | 1.180796 | 0.976880 | -0.112838 |
| mcp_calls | unavailable | 0 | 0.000000 |
| model_calls | unavailable | unavailable | unavailable |
| repeated_file_reads | unavailable | unavailable | unavailable |
| observed_file_read_commands | 0.300000 | -0.700000 | -1.000000 |
| observed_repeated_read_commands | unavailable | 0 | 0.000000 |
| actual_cost_usd | unavailable | unavailable | unavailable |
| computed_cost_usd | unavailable | unavailable | unavailable |

## B_over_A

Verified pairs: 20; excluded: 0.

| Metric | Overall mean ratio | Paired difference mean | Paired difference median |
|---|---:|---:|---:|
| input_tokens | 0.971035 | -1145.850000 | 107.000000 |
| cached_input_tokens | 0.967865 | -972.800000 | 64.000000 |
| uncached_input_tokens | 0.981367 | -173.050000 | -29.500000 |
| output_tokens | 0.964348 | -29.800000 | 0.500000 |
| wall_time_seconds | 0.999649 | -0.007355 | 0.323550 |
| end_to_end_wall_seconds | 1.010766 | 0.225770 | 0.827621 |
| native_exec_wall_seconds | unavailable | unavailable | unavailable |
| approval_index_wall_seconds | unavailable | 0.218756 | 0.179330 |
| approval_index_cpu_seconds | unavailable | 0.056226 | 0.050465 |
| context_preparation_wall_seconds | unavailable | unavailable | unavailable |
| context_preparation_cpu_seconds | unavailable | unavailable | unavailable |
| process_tree_peak_rss_bytes | 0.985348 | -3919462.400000 | -550912.000000 |
| cpu_seconds | 1.012210 | 0.064500 | 0.370000 |
| total_observed_local_cpu_seconds | 1.022854 | 0.120726 | 0.449027 |
| mcp_calls | unavailable | 0 | 0.000000 |
| model_calls | unavailable | unavailable | unavailable |
| repeated_file_reads | unavailable | unavailable | unavailable |
| observed_file_read_commands | 1.052632 | 0.050000 | 0.000000 |
| observed_repeated_read_commands | unavailable | 0 | 0.000000 |
| actual_cost_usd | unavailable | unavailable | unavailable |
| computed_cost_usd | unavailable | unavailable | unavailable |

## Selection strata (descriptive)

| Stratum | Arm | Attempted | Successful | Mean full seconds | Mean input |
|---|---|---:|---:|---:|---:|
| caller_context_supplied | A | 4 | 4 | 23.964118 | 37013.500000 |
| caller_context_supplied | B | 4 | 4 | 22.521753 | 37304.500000 |
| caller_context_supplied | C | 4 | 4 | 21.625534 | 37072.750000 |
| explicit_focus | A | 16 | 16 | 20.222006 | 40195.937500 |
| explicit_focus | B | 16 | 16 | 20.864810 | 38690.875000 |
| explicit_focus | C | 16 | 16 | 22.775100 | 41989.375000 |

Permutation counts: {"ABC": 4, "ACB": 4, "BAC": 2, "BCA": 4, "CAB": 2, "CBA": 4}.

Actual cost per successful task (all attempted costs, including failures):
- A: unavailable; 20 attempted costs / 20 successful tasks. Cost unavailable for one or more attempts; no estimate substituted
- B: unavailable; 20 attempted costs / 20 successful tasks. Cost unavailable for one or more attempts; no estimate substituted
- C: unavailable; 20 attempted costs / 20 successful tasks. Cost unavailable for one or more attempts; no estimate substituted

## Individual original runs

| Run | Status | Grade | Treatment | Input | Cached | Output | Full seconds |
|---|---|---|---|---:|---:|---:|---:|
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r1-A | completed | True | True | 49068 | 35328 | 1017 | 35.831847 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r1-C | completed | True | True | 49125 | 35456 | 983 | 25.845517 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r1-B | completed | True | True | 62346 | 48384 | 1149 | 32.798357 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r1-A | completed | True | True | 24891 | 20608 | 592 | 17.068185 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r1-B | completed | True | True | 25032 | 11648 | 753 | 19.443341 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r1-C | completed | True | True | 25033 | 20608 | 769 | 18.757972 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r1-B | completed | True | True | 36249 | 32256 | 492 | 16.507221 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r1-C | completed | True | True | 36490 | 23424 | 544 | 20.983783 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r1-A | completed | True | True | 36221 | 23168 | 607 | 17.331962 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r1-C | completed | True | True | 37481 | 32640 | 765 | 21.432316 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r1-B | completed | True | True | 36835 | 23424 | 605 | 18.107470 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r1-A | completed | True | True | 36790 | 23424 | 648 | 18.116150 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r1-B | completed | True | True | 37648 | 23808 | 857 | 22.266847 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r1-A | completed | True | True | 37496 | 23552 | 904 | 20.246123 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r1-C | completed | True | True | 38225 | 24064 | 921 | 20.950222 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r1-C | completed | True | True | 51344 | 34048 | 1093 | 32.008519 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r1-A | completed | True | True | 37116 | 20352 | 1011 | 23.471683 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r1-B | completed | True | True | 37119 | 32640 | 798 | 24.907859 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-A | completed | True | True | 37119 | 23296 | 1253 | 26.157443 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-C | completed | True | True | 37498 | 32640 | 1170 | 26.264758 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-B | completed | True | True | 51056 | 45568 | 1397 | 30.197017 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r1-A | completed | True | True | 37340 | 32384 | 844 | 23.279666 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r1-B | completed | True | True | 37858 | 23680 | 903 | 23.530464 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r1-C | completed | True | True | 25401 | 20864 | 748 | 16.630759 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r1-B | completed | True | True | 36520 | 32256 | 821 | 23.937663 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r1-C | completed | True | True | 78444 | 63232 | 1195 | 29.124575 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r1-A | completed | True | True | 49862 | 33152 | 1048 | 24.893774 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r1-C | completed | True | True | 24670 | 20608 | 456 | 14.872810 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r1-B | completed | True | True | 36932 | 32384 | 550 | 18.018500 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r1-A | completed | True | True | 36473 | 32128 | 527 | 15.532207 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r2-B | completed | True | True | 36839 | 32384 | 895 | 20.323301 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r2-C | completed | True | True | 49143 | 35456 | 1001 | 25.859527 |
| workflow-v2-ts-workflow2-contracts-unicode-common-prefix-r2-A | completed | True | True | 49101 | 44288 | 985 | 25.182858 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r2-C | completed | True | True | 24990 | 17920 | 727 | 16.039123 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r2-B | completed | True | True | 25001 | 11648 | 714 | 17.522014 |
| workflow-v2-py-workflow2-codec-roman-subtractive-r2-A | completed | True | True | 24994 | 20608 | 730 | 17.773584 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r2-A | completed | True | True | 36241 | 32128 | 510 | 15.263302 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r2-C | completed | True | True | 24640 | 20608 | 541 | 14.513996 |
| workflow-v2-ts-workflow2-coordinates-manhattan-symmetric-r2-B | completed | True | True | 36428 | 32256 | 591 | 17.720305 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r2-A | completed | True | True | 36861 | 20480 | 638 | 16.045981 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r2-B | completed | True | True | 36949 | 32384 | 670 | 17.450425 |
| workflow-v2-py-workflow2-codec-glob-literal-escape-r2-C | completed | True | True | 37146 | 23680 | 664 | 17.165274 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r2-C | completed | True | True | 38238 | 33024 | 863 | 38.908838 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r2-A | completed | True | True | 37449 | 20480 | 873 | 20.048604 |
| workflow-v2-py-workflow2-similarity-jaccard-stable-selection-r2-B | completed | True | True | 37745 | 23808 | 897 | 22.060073 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r2-B | completed | True | True | 37116 | 32640 | 842 | 19.353081 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r2-A | completed | True | True | 50621 | 45440 | 1206 | 25.349794 |
| workflow-v2-ts-workflow2-coordinates-bounded-cardinal-neighbors-r2-C | completed | True | True | 37819 | 20992 | 1039 | 21.342806 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r2-B | completed | True | True | 37095 | 20480 | 1073 | 22.079659 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r2-C | completed | True | True | 80144 | 73728 | 1448 | 33.705593 |
| workflow-v2-ts-workflow2-contracts-natural-stable-sort-r2-A | completed | True | True | 50325 | 45312 | 1167 | 25.449781 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r2-C | completed | True | True | 37972 | 33024 | 837 | 21.259075 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r2-B | completed | True | True | 37326 | 20608 | 721 | 20.539213 |
| workflow-v2-py-workflow2-codec-unsigned-varint-batch-r2-A | completed | True | True | 37609 | 32512 | 851 | 17.833977 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r2-A | completed | True | True | 49114 | 44672 | 778 | 18.981830 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r2-C | completed | True | True | 49490 | 33152 | 780 | 19.803083 |
| workflow-v2-ts-workflow2-contracts-luhn-checksum-r2-B | completed | True | True | 49554 | 41344 | 848 | 22.973793 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r2-A | completed | True | True | 36498 | 32128 | 528 | 15.549829 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r2-B | completed | True | True | 36624 | 32384 | 545 | 14.187369 |
| workflow-v2-py-workflow2-similarity-bit-hamming-distance-r2-C | completed | True | True | 36828 | 32512 | 534 | 15.435201 |

## Failures

None.

## Limitations

- This fresh confirmation follows sixty retained failed workflow-1 originals; they are not replaced or regraded. Existing test files must remain byte-for-byte unchanged; optional regressions belong only in new files.
- All original assignments, failures and unknown interruptions are retained; no automatic retries. Successful completion requires external behavior grade, treatment and native schema validity.
- A is direct standard Codex. B adds complete caller-selected production files. C adds those files plus complete caller-selected supporting tests. All arms receive identical common prompts, path hints and test argv. No auxiliary model or configured MCP is used.
- Ten fresh purpose-built tasks, five Python/five TypeScript, are repeated twice in isolated worktrees/native state/databases. Repeat two reverses each task's arm order; pairwise precedence is balanced but provider and operating-system caches are uncontrolled.
- Source hashes attest complete current selected files at preparation, not semantic completeness or later edits. Supporting tests are task-author-selected and equally disclosed to every arm; this is not autonomous repository discovery or cross-session memory.
- Full time includes cold approval/index and launcher/native work, excluding worktree construction and grading. CPU is a local observed lower bound; child RSS excludes parent indexing, may miss short-lived children and double-count shared pages.
- Actual cost, model calls and filesystem reads remain unavailable. Cached input is included within total input. Separately labelled price-equivalent estimates must include failed attempts and exclude unknown usage from zero-cost assumptions.
- Paired comparisons require matching commits/common prompts, valid treatment, valid native completion and unchanged frozen source; primary intent-to-treat per-arm aggregates retain all originals regardless of pair eligibility.
