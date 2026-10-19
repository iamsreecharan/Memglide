# Warm memory benchmark

A: bare Codex. B: complete focused source, no memory. C: same source plus earlier source-verified model quotations in one active Memglide session.

Dollar values below are API list-price equivalents, not actual billed cost.

| Arm | Attempted | Successful | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|---:|
| A | 27 | 27 | 26.555574030296324 | 25.586043347997474 | 0.044036859259259264 |
| B | 27 | 27 | 24.84468358625896 | 25.061365872999886 | 0.04003586666666666 |
| C | 27 | 26 | 26.077994179077415 | 24.499674663500628 | None |

## Sequence-wide accounting

All three stages and failures are included. Unknown costs remain unavailable.

| Arm | Successful / planned sequences | Estimated USD / successful sequence |
|---|---:|---:|
| A | 9 / 24 | None |
| B | 9 / 24 | None |
| C | 8 / 24 | None |

## Observed measurements

Missing telemetry is unavailable. Cached input is included in total input; resource values describe only the local measured scope.

| Metric | Arm | Mean | Median | Total | Observed |
|---|---|---:|---:|---:|---:|
| input_tokens | A | 58800.444444444445 | 62445 | 1587612 | 27 |
| input_tokens | B | 55129.148148148146 | 49886 | 1488487 | 27 |
| input_tokens | C | 58231.61538461538 | 51925.0 | None | 26 |
| cached_input_tokens | A | 42827.851851851854 | 36224 | 1156352 | 27 |
| cached_input_tokens | B | 40926.81481481482 | 37248 | 1105024 | 27 |
| cached_input_tokens | C | 41905.230769230766 | 37120.0 | None | 26 |
| uncached_input_tokens | A | 15972.592592592593 | 14052 | 431260 | 27 |
| uncached_input_tokens | B | 14202.333333333334 | 14023 | 383463 | 27 |
| uncached_input_tokens | C | 16326.384615384615 | 14526.0 | None | 26 |
| output_tokens | A | 780.8888888888889 | 740 | 21084 | 27 |
| output_tokens | B | 753.8518518518518 | 758 | 20354 | 27 |
| output_tokens | C | 772.3076923076923 | 741.0 | None | 26 |
| wall_time_seconds | A | 26.47758720814912 | 25.51278479600296 | 714.8948546200263 | 27 |
| wall_time_seconds | B | 24.547212041813946 | 24.850720734000788 | 662.7747251289766 | 27 |
| wall_time_seconds | C | 25.48601705715387 | 23.96529440249651 | None | 26 |
| end_to_end_wall_seconds | A | 26.555574030296324 | 25.586043347997474 | 717.0004988180008 | 27 |
| end_to_end_wall_seconds | B | 24.84468358625896 | 25.061365872999886 | 670.8064568289919 | 27 |
| end_to_end_wall_seconds | C | 26.077994179077415 | 24.499674663500628 | None | 26 |
| native_exec_wall_seconds | A | 26.47758720814912 | 25.51278479600296 | 714.8948546200263 | 27 |
| native_exec_wall_seconds | B | 24.547212041813946 | 24.850720734000788 | 662.7747251289766 | 27 |
| native_exec_wall_seconds | C | 25.48601705715387 | 23.96529440249651 | None | 26 |
| approval_index_wall_seconds | A | 0 | 0 | 0 | 27 |
| approval_index_wall_seconds | B | 0.23609955318587944 | 0.23359108899603598 | 6.374687936018745 | 27 |
| approval_index_wall_seconds | C | 0.24169116800056564 | 0.21509960000184947 | None | 26 |
| approval_index_cpu_seconds | A | 0 | 0 | 0 | 27 |
| approval_index_cpu_seconds | B | 0.07707459625926903 | 0.07311085499998171 | 2.0810140990002637 | 27 |
| approval_index_cpu_seconds | C | 0.08358307865384217 | 0.07047544199999922 | None | 26 |
| context_preparation_wall_seconds | A | 2.192329648770047e-05 | 9.878000128082931e-06 | 0.0005919290051679127 | 27 |
| context_preparation_wall_seconds | B | 0.016120167185834835 | 0.01543031300388975 | 0.4352445140175405 | 27 |
| context_preparation_wall_seconds | C | 0.05450160119317633 | 0.048137665500689764 | None | 26 |
| context_preparation_cpu_seconds | A | 2.482262962749465e-05 | 9.867000017038663e-06 | 0.0006702109999423556 | 27 |
| context_preparation_cpu_seconds | B | 0.010148572333335963 | 0.009649837999972988 | 0.274011453000071 | 27 |
| context_preparation_cpu_seconds | C | 0.04751385934614839 | 0.04247176349997517 | None | 26 |
| process_tree_peak_rss_bytes | A | 281672514.3703704 | 314064896 | None | 27 |
| process_tree_peak_rss_bytes | B | 272021276.4444444 | 295608320 | None | 27 |
| process_tree_peak_rss_bytes | C | 284961083.0769231 | 313772032.0 | None | 26 |
| cpu_seconds | A | 5.6829629629629625 | 4.95 | 153.44 | 27 |
| cpu_seconds | B | 4.953703703703703 | 4.5200000000000005 | 133.75 | 27 |
| cpu_seconds | C | 5.588461538461538 | 4.85 | None | 26 |
| total_observed_local_cpu_seconds | A | 23.01047984937037 | 21.90853604799997 | 621.282955933 | 27 |
| total_observed_local_cpu_seconds | B | 20.636786685481496 | 18.781010565999992 | 557.1932405080004 | 27 |
| total_observed_local_cpu_seconds | C | 22.40048640992308 | 20.90408653300001 | None | 26 |
| mcp_calls | A | 0 | 0 | 0 | 27 |
| mcp_calls | B | 0 | 0 | 0 | 27 |
| mcp_calls | C | 0 | 0.0 | None | 26 |
| model_calls | A | None | None | None | 0 |
| model_calls | B | None | None | None | 0 |
| model_calls | C | None | None | None | 0 |
| repeated_file_reads | A | None | None | None | 0 |
| repeated_file_reads | B | None | None | None | 0 |
| repeated_file_reads | C | None | None | None | 0 |
| observed_file_read_commands | A | 1.3333333333333333 | 1 | 36 | 27 |
| observed_file_read_commands | B | 1.1481481481481481 | 1 | 31 | 27 |
| observed_file_read_commands | C | 1.4074074074074074 | 1 | 38 | 27 |
| observed_repeated_read_commands | A | 0.037037037037037035 | 0 | 1 | 27 |
| observed_repeated_read_commands | B | 0 | 0 | 0 | 27 |
| observed_repeated_read_commands | C | 0 | 0 | 0 | 27 |
| actual_cost_usd | A | None | None | None | 0 |
| actual_cost_usd | B | None | None | None | 0 |
| actual_cost_usd | C | None | None | None | 0 |
| computed_cost_usd | A | None | None | None | 0 |
| computed_cost_usd | B | None | None | None | 0 |
| computed_cost_usd | C | None | None | None | 0 |

## Cost sensitivity

Ranges permit unknown cache-write attribution; they are scenarios, not confidence intervals or billed amounts.

| Arm | Point USD / successful task | Possible-write lower | Possible-write upper |
|---|---:|---:|---:|
| A | 0.044036859259259264 | 0.044036859259259264 | 0.052023155555555554 |
| B | 0.04003586666666666 | 0.04003586666666666 | 0.047137033333333335 |
| C | None | None | None |

## Repeat 1

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 27 / 27 | 26.555574030296324 | 25.586043347997474 | 0.044036859259259264 |
| B | 27 / 27 | 24.84468358625896 | 25.061365872999886 | 0.04003586666666666 |
| C | 26 / 27 | 26.077994179077415 | 24.499674663500628 | None |

## Repeat 2

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 0 / 0 | None | None | None |
| B | 0 / 0 | None | None | None |
| C | 0 / 0 | None | None | None |

## cold_stage_1

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 9 / 9 | 26.808715824222116 | 26.30109031200118 | 0.04237497777777778 |
| B | 9 / 9 | 25.296107186777387 | 25.439673321001465 | 0.04274848888888889 |
| C | 9 / 9 | 27.379871081665947 | 27.83666574900417 | 0.03777724444444444 |

## warm_stage_2_3

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 18 / 18 | 26.42900313333343 | 24.86243232400375 | 0.0448678 |
| B | 18 / 18 | 24.618971785999747 | 24.029287243 | 0.03867955555555555 |
| C | 17 / 18 | 25.388765230648193 | 24.068813336001767 | None |

## Memory observations

```json
{
  "C_requested_prior_memory_runs": 16,
  "C_preloaded_memory_runs": 16,
  "C_fallback_reasons": {
    "no_prior_memory": 9,
    "no_current_memory": 1,
    "not_prepared": 46
  },
  "accepted_quote_instances": 28,
  "rejected_quote_instances": 0
}
```

## Default-promotion decision

Passed: False; failed checks: 22. All216 unique original assignments must be attempted
Memory remains explicit and optional unless every predeclared acceptance check passes. Mixed results do not establish universal cost or speed savings.

## Every original assignment

| Run | Status | Grade | Input | Cached | Output | Instrumented full seconds | Memory mode |
|---|---|---|---:|---:|---:|---:|---|
| warm-ts-warm-paths-s1-r1-C | completed | True | 75455 | 61056 | 839 | 32.57221275899792 | passthrough |
| warm-ts-warm-paths-s2-r1-C | completed | True | 50626 | 23936 | 848 | 24.040354098004173 | preloaded |
| warm-ts-warm-paths-s3-r1-C | completed | True | 65099 | 37120 | 707 | 22.81564928300213 | preloaded |
| warm-ts-warm-paths-s1-r1-B | completed | True | 75128 | 60800 | 838 | 26.51055524899857 | passthrough |
| warm-ts-warm-paths-s2-r1-B | completed | True | 49735 | 35712 | 840 | 28.759984821001126 | passthrough |
| warm-ts-warm-paths-s3-r1-B | completed | True | 62802 | 48896 | 772 | 28.607375834995764 | passthrough |
| warm-ts-warm-paths-s1-r1-A | completed | True | 62150 | 35968 | 952 | 26.30109031200118 | passthrough |
| warm-ts-warm-paths-s2-r1-A | completed | True | 89665 | 61568 | 966 | 30.077088979996915 | passthrough |
| warm-ts-warm-paths-s3-r1-A | completed | True | 49527 | 35456 | 758 | 23.326708686996426 | passthrough |
| warm-ts-warm-quota-s1-r1-B | completed | True | 62339 | 36992 | 525 | 20.203196738999395 | passthrough |
| warm-ts-warm-quota-s2-r1-B | completed | True | 49559 | 35840 | 665 | 21.68797196199739 | passthrough |
| warm-ts-warm-quota-s3-r1-B | completed | True | 62933 | 48768 | 686 | 22.922211293996952 | passthrough |
| warm-ts-warm-quota-s1-r1-C | completed | True | 49377 | 35712 | 528 | 19.072976780000317 | passthrough |
| warm-ts-warm-quota-s2-r1-C | completed | True | 63228 | 36608 | 655 | 24.265656044000934 | preloaded |
| warm-ts-warm-quota-s3-r1-C | completed | True | 52033 | 37632 | 704 | 20.77718072499556 | preloaded |
| warm-ts-warm-quota-s1-r1-A | completed | True | 48934 | 35328 | 510 | 16.64102175500011 | passthrough |
| warm-ts-warm-quota-s2-r1-A | completed | True | 62461 | 35456 | 678 | 19.698764528002357 | passthrough |
| warm-ts-warm-quota-s3-r1-A | completed | True | 62550 | 36224 | 672 | 32.216683245998865 | passthrough |
| warm-ts-warm-routing-s1-r1-A | completed | True | 62545 | 48128 | 944 | 31.447345496999333 | passthrough |
| warm-ts-warm-routing-s2-r1-A | completed | True | 63362 | 57856 | 865 | 24.78611646200443 | passthrough |
| warm-ts-warm-routing-s3-r1-A | completed | True | 62859 | 36224 | 767 | 33.93116175299656 | passthrough |
| warm-ts-warm-routing-s1-r1-C | completed | True | 76767 | 61952 | 977 | 27.83666574900417 | passthrough |
| warm-ts-warm-routing-s2-r1-C | completed | True | 77946 | 62976 | 859 | 27.151386901998194 | preloaded |
| warm-ts-warm-routing-s3-r1-C | completed | True | 65083 | 50432 | 738 | 23.867451480000454 | preloaded |
| warm-ts-warm-routing-s1-r1-B | completed | True | 49929 | 23424 | 939 | 25.439673321001465 | passthrough |
| warm-ts-warm-routing-s2-r1-B | completed | True | 50022 | 35840 | 872 | 22.99720861300011 | passthrough |
| warm-ts-warm-routing-s3-r1-B | completed | True | 63112 | 36480 | 714 | 22.55201921099797 | passthrough |
| warm-py-warm-labels-s1-r1-C | completed | True | 49825 | 35712 | 962 | 29.209996320001665 | passthrough |
| warm-py-warm-labels-s2-r1-C | completed | True | 64404 | 59008 | 734 | 25.46524017900083 | preloaded |
| warm-py-warm-labels-s3-r1-C | completed | True | 49915 | 32896 | 744 | 21.767714779001835 | passthrough |
| warm-py-warm-labels-s1-r1-B | completed | True | 49676 | 35712 | 861 | 22.799133553999127 | passthrough |
| warm-py-warm-labels-s2-r1-B | completed | True | 49642 | 44672 | 673 | 21.221976481996535 | passthrough |
| warm-py-warm-labels-s3-r1-B | completed | True | 63038 | 37248 | 685 | 25.061365872999886 | passthrough |
| warm-py-warm-labels-s1-r1-A | completed | True | 62679 | 54528 | 978 | 35.06503832299495 | passthrough |
| warm-py-warm-labels-s2-r1-A | completed | True | 62802 | 48640 | 721 | 26.469932357002108 | passthrough |
| warm-py-warm-labels-s3-r1-A | completed | True | 49636 | 35584 | 699 | 24.938748186003068 | passthrough |
| warm-ts-warm-headers-s1-r1-B | completed | True | 49591 | 23424 | 758 | 28.416678661000333 | passthrough |
| warm-ts-warm-headers-s2-r1-B | completed | True | 63370 | 49024 | 915 | 28.32640961300058 | passthrough |
| warm-ts-warm-headers-s3-r1-B | completed | True | 49761 | 35840 | 655 | 25.27688591000333 | passthrough |
| warm-ts-warm-headers-s1-r1-A | completed | True | 62162 | 57088 | 740 | 25.586043347997474 | passthrough |
| warm-ts-warm-headers-s2-r1-A | completed | True | 63524 | 35584 | 1064 | 30.85510004999378 | passthrough |
| warm-ts-warm-headers-s3-r1-A | completed | True | 49695 | 35712 | 681 | 21.384404661002918 | passthrough |
| warm-ts-warm-headers-s1-r1-C | completed | True | 61918 | 35968 | 681 | 25.653968027996598 | passthrough |
| warm-ts-warm-headers-s2-r1-C | completed | True | 64933 | 36352 | 1073 | 32.14499257699936 | preloaded |
| warm-ts-warm-headers-s3-r1-C | completed | True | 51429 | 24192 | 665 | 21.587648398002784 | preloaded |
| warm-py-warm-retries-s1-r1-B | completed | True | 50639 | 45440 | 570 | 21.87239421599952 | passthrough |
| warm-py-warm-retries-s2-r1-B | completed | True | 49501 | 35712 | 672 | 22.795620925004187 | passthrough |
| warm-py-warm-retries-s3-r1-B | completed | True | 63933 | 49280 | 901 | 26.701618818995485 | passthrough |
| warm-py-warm-retries-s1-r1-C | completed | True | 49803 | 41856 | 626 | 22.482912224993925 | passthrough |
| warm-py-warm-retries-s2-r1-C | completed | True | 50435 | 36352 | 682 | 21.33346347600309 | preloaded |
| warm-py-warm-retries-s3-r1-C | completed | True | 65702 | 59776 | 914 | 33.93421124800079 | preloaded |
| warm-py-warm-retries-s1-r1-A | completed | True | 62636 | 48512 | 589 | 28.19168804399669 | passthrough |
| warm-py-warm-retries-s2-r1-A | completed | True | 62526 | 57472 | 693 | 24.498546872004226 | passthrough |
| warm-py-warm-retries-s3-r1-A | completed | True | 63853 | 45824 | 990 | 28.33804670599784 | passthrough |
| warm-py-warm-priority-s1-r1-A | completed | True | 62092 | 48256 | 612 | 24.606047942004807 | passthrough |
| warm-py-warm-priority-s2-r1-A | completed | True | 49536 | 35584 | 785 | 24.39857210899936 | passthrough |
| warm-py-warm-priority-s3-r1-A | completed | True | 49622 | 32256 | 932 | 27.278771558005246 | passthrough |
| warm-py-warm-priority-s1-r1-C | completed | True | 49703 | 35712 | 760 | 28.121702420001384 | passthrough |
| warm-py-warm-priority-s2-r1-C | completed | True | 64153 | 49792 | 805 | 23.681602781005495 | preloaded |
| warm-py-warm-priority-s3-r1-C | completed | True | 51817 | 37120 | 845 | 24.068813336001767 | preloaded |
| warm-py-warm-priority-s1-r1-B | completed | True | 49564 | 44672 | 716 | 22.136030567999114 | passthrough |
| warm-py-warm-priority-s2-r1-B | completed | True | 49886 | 44672 | 863 | 27.67358971900103 | passthrough |
| warm-py-warm-priority-s3-r1-B | completed | True | 49700 | 44672 | 823 | 30.54359054800443 | passthrough |
| warm-ts-warm-clocks-s1-r1-C | completed | True | 49662 | 44672 | 1025 | 33.82023774999834 | passthrough |
| warm-ts-warm-clocks-s2-r1-C | completed | True | 50463 | 33664 | 704 | 24.69384202999936 | preloaded |
| warm-ts-warm-clocks-s3-r1-C | completed | True | 51116 | 24832 | 773 | 35.708294288000616 | preloaded |
| warm-ts-warm-clocks-s1-r1-A | completed | True | 63063 | 36864 | 1042 | 31.864925072004553 | passthrough |
| warm-ts-warm-clocks-s2-r1-A | completed | True | 49420 | 41984 | 732 | 23.40318112300156 | passthrough |
| warm-ts-warm-clocks-s3-r1-A | completed | True | 62445 | 54016 | 779 | 35.02360058599879 | passthrough |
| warm-ts-warm-clocks-s1-r1-B | completed | True | 63321 | 57856 | 1036 | 33.87988129199948 | passthrough |
| warm-ts-warm-clocks-s2-r1-B | completed | True | 49557 | 32384 | 641 | 22.239152572998137 | passthrough |
| warm-ts-warm-clocks-s3-r1-B | completed | True | 63029 | 48896 | 791 | 26.884209086005285 | passthrough |
| warm-py-warm-pagination-s1-r1-B | completed | True | 49820 | 32384 | 763 | 26.407421080999484 | passthrough |
| warm-py-warm-pagination-s2-r1-B | completed | True | 49343 | 35712 | 528 | 18.255433288999484 | passthrough |
| warm-py-warm-pagination-s3-r1-B | completed | True | 49557 | 44672 | 652 | 20.63486757499777 | passthrough |
| warm-py-warm-pagination-s1-r1-A | completed | True | 49353 | 35456 | 672 | 21.57524212499993 | passthrough |
| warm-py-warm-pagination-s2-r1-A | completed | True | 49228 | 35456 | 595 | 22.110644780994335 | passthrough |
| warm-py-warm-pagination-s3-r1-A | completed | True | 49287 | 35328 | 668 | 22.985983755002962 | passthrough |
| warm-py-warm-pagination-s1-r1-C | completed | True | 49529 | 44672 | 683 | 27.648167703999206 | passthrough |
| warm-py-warm-pagination-s2-r1-C | completed | True | 63601 | 49536 | 549 | 24.305507297001895 | preloaded |
| warm-py-warm-pagination-s3-r1-C | interrupted | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r2-A | not_run | None | None | None | None | None | None |

## Failures

- warm-py-warm-pagination-s3-r1-C: interrupted; Launcher interrupted; original outcome and complete usage are unknown

## Limitations

- C reuses one active default-expiration Memglide session across three fresh native Codex processes; ended/expired Memglide sessions and arbitrary cross-session persistence are not tested.
- Twelve three-task sequences, two repeats, three arms produce 216 original assignments. Small purpose-built repositories do not establish production-wide or large-repository performance.
- Every stage starts from its independently frozen canonical source commit; earlier model patches never carry into later tasks. All arms receive the same task, path hints, test command, final findings schema, model and native settings.
- All arms share a paid findings-output request; A has bare tools under this matched workflow, not an unconstrained ordinary summary-only prompt. Findings output is charged in every arm, not free extraction.
- Only model-produced current-source quotations are captured. Neither grading outcomes nor hidden grader/reference data select, repair or create memories. Exact quotations establish textual source support, not semantic truth.
- Memory absence, stale quotations and bounded-context fallback are retained intent-to-treat outcomes. No failed assignment is retried or replaced. Independent grading never gates capture.
- B and C both pay initial approval/index and per-stage reindex cost; C also pays session creation, source-quote capture, validation, preparation and explicit end-session cleanup. Instrumented full wall time and parent CPU additionally include independent treatment audit work: frozen-Git source reconstruction and C prior-final/source-envelope verification. Native wall time is reported separately. Fixture reset, external grading, shared product API imports and the long-lived harness startup are excluded; instrumented time is not pure product latency.
- Fresh isolated worktrees, native state and databases are used per sequence/arm/repeat. Native processes are fresh per stage. Provider/OS cache state is uncontrolled; no cache header/session tampering is used.
- All arms configure zero MCP servers. This measures source/memory preloading, not native MCP efficiency. MCP functionality is tested separately.
- Actual billing, provider inference-call counts, actual filesystem reads and provider resource use are unavailable. Dollars are labelled API list-price equivalents from observed native usage; missing usage is never zero.
- Local CPU is an observed lower bound; sampled native child RSS excludes parent preparation/indexing, can miss short-lived children and double-count shared pages. Command/read-command items are proxies.
- Reported zero cache writes may be upstream parser defaults. Possible-write ranges are scenarios, not confidence intervals or actual subscription savings.
