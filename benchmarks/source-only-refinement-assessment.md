# Source-only request-local policy refinement

**The complete known-path source architecture is preserved. This change reuses compiled ignore specifications within one preparation request; current policy/source reads and normal prompt bytes remain unchanged. No model benefit is claimed.**

The exact baseline is `391d86e64e53cf79d99824e1b5a63e4d70f0ae1b` (`9ae8595b4b5f97993dcf177d78d090db5f1e0f6fdb8ce2e2da5e3d766d69afac`); candidate source is `916dfcf1360dc3c2c207fd67dd5cea210dc88c194a2bd7e12a5e90e1d584ef1b`. The frozen local comparison is valid: **True**; final source seal unchanged: **True**.

There are 72 performance workers and six separate diagnostic workers. Each fixture has 12 paired fresh workers per arm. Five warm inner calls form one worker mean, not 60 independent samples. Synthetic approval tables avoid indexing; this is not a coding-agent, real-indexing or model-cost benchmark.

## What improved and what remains uncertain

| Area | Result |
|---|---|
| Repeated policy compilation | Confirmed reduction: typical 6→3 and dense 2→1 per call. |
| Complete source and prompt fidelity | Preserved across all 78 workers, 468 preparation calls and 24 fallback controls. |
| Current source/policy read counters | Equal across arms in all 36 separately instrumented calls from six diagnostic workers; timing workers were uninstrumented. |
| Typical warm mean preparation | 14.726→14.420 ms (−2.08%); the paired mean interval includes zero. Typical first-call mean increased 15.49%. |
| Dense warm preparation | Median 31.607→25.920 ms, with a negative paired-median interval; mean 32.834→36.163 ms (+10.14%), with a mean interval spanning zero. |
| No-ignore control | An apparent 77.9% mean decrease despite zero changed compilations is dominated by a long baseline call; its median is essentially unchanged. No cache speedup is inferred. |
| Whole-worker peak memory | Median unchanged at 15.25 MiB for noignore/typical; dense rose from 15.875 to 16.0 MiB. This is not an incremental allocation estimate. |
| New model tokens, cost or whole-task performance | Unmeasured. The same complete source/task bytes are preserved; no new model savings are claimed. |

**There is no reliable overall mean-latency win in this experiment.** Every primary first/warm mean wall/own-CPU interval includes zero. The dense median result is scoped to this fixture and does not erase its worse mean.

The baseline no-ignore worker `015-performance-noignore-baseline` contained a 717.253 ms warm call (715.070 ms own CPU). Candidate dense worker `018-performance-dense-candidate` contained a 552.853 ms call (520.648 ms own CPU). Every outlier remains included. Their causes are unknown: no per-call GC, syscall or scheduling trace was collected, and own CPU also increased. Neither a host-scheduling explanation nor a cache-induced tail regression is established.

The shipped change is a bounded reduction in duplicated compilation, with preserved source delivery and safety checks. General latency, token and model-cost improvements remain unproven. Next, replicate on realistic ignore layouts and collect separate diagnostic phase traces; do not replace this cohort with a more favorable repeat.

## Per-fixture API timing and own CPU

All timing/CPU values below are milliseconds. Negative paired deltas favor the candidate. First calls include first lazy imports. Warm observations are worker means. Bootstrap intervals resample 12 paired worker units with 2,000 seeded draws; host/cache uncertainty remains. Intervals are unadjusted across the multiple fixture/phase/metric comparisons; favorable median results are exploratory.

| Fixture | Phase / metric | Pairs | Baseline mean | Candidate mean | Baseline median | Candidate median | Mean paired delta | Median paired delta | 95% mean-delta interval | 95% median-delta interval |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| noignore | first / wall_seconds | 12 | 73.6112 | 57.5078 | 61.1728 | 54.8195 | -16.1034 | 0.8972 | [-40.4401, 4.9259] | [-35.3301, 5.8170] |
| noignore | first / cpu_seconds | 12 | 73.5176 | 57.3889 | 61.1672 | 54.8063 | -16.1288 | 0.9055 | [-40.2122, 4.7584] | [-35.3328, 5.8178] |
| noignore | first / waited_child_cpu_seconds | 12 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | [0.0000, 0.0000] | [0.0000, 0.0000] |
| noignore | warm / wall_seconds | 12 | 17.9642 | 3.9657 | 3.5362 | 3.5615 | -13.9985 | 0.1863 | [-43.0655, 1.0661] | [-1.3415, 1.8290] |
| noignore | warm / cpu_seconds | 12 | 17.8731 | 3.9571 | 3.5312 | 3.5607 | -13.9160 | 0.1853 | [-42.8039, 1.0502] | [-1.3365, 1.8293] |
| noignore | warm / waited_child_cpu_seconds | 12 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | [0.0000, 0.0000] | [0.0000, 0.0000] |
| typical | first / wall_seconds | 12 | 78.3931 | 90.5340 | 64.6279 | 64.8923 | 12.1409 | -2.0320 | [-15.7059, 56.6058] | [-11.4342, 5.5192] |
| typical | first / cpu_seconds | 12 | 78.3741 | 90.2430 | 64.6307 | 64.8948 | 11.8689 | -2.0294 | [-15.7065, 55.7870] | [-11.4388, 5.5153] |
| typical | first / waited_child_cpu_seconds | 12 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | [0.0000, 0.0000] | [0.0000, 0.0000] |
| typical | warm / wall_seconds | 12 | 14.7262 | 14.4204 | 13.7233 | 13.0818 | -0.3057 | 0.0847 | [-2.7495, 2.5428] | [-3.6949, 1.3284] |
| typical | warm / cpu_seconds | 12 | 14.7209 | 14.4181 | 13.7239 | 13.0824 | -0.3027 | 0.0822 | [-2.7481, 2.5492] | [-3.7105, 1.3516] |
| typical | warm / waited_child_cpu_seconds | 12 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | [0.0000, 0.0000] | [0.0000, 0.0000] |
| dense | first / wall_seconds | 12 | 138.2799 | 126.1073 | 129.8075 | 118.8612 | -12.1726 | -10.9367 | [-28.1390, 5.5090] | [-34.4073, -0.0651] |
| dense | first / cpu_seconds | 12 | 138.2648 | 125.4281 | 129.8097 | 118.8664 | -12.8367 | -10.9644 | [-28.4557, 4.0121] | [-35.2275, 0.0110] |
| dense | first / waited_child_cpu_seconds | 12 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | [0.0000, 0.0000] | [0.0000, 0.0000] |
| dense | warm / wall_seconds | 12 | 32.8342 | 36.1631 | 31.6068 | 25.9198 | 3.3290 | -3.8987 | [-7.9321, 21.5785] | [-8.9826, -2.7372] |
| dense | warm / cpu_seconds | 12 | 32.8345 | 35.6112 | 31.6075 | 25.9203 | 2.7768 | -3.8965 | [-7.9429, 19.9431] | [-8.9831, -2.7364] |
| dense | warm / waited_child_cpu_seconds | 12 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | [0.0000, 0.0000] | [0.0000, 0.0000] |

- noignore: 12/12 complete valid pairs; 0 invalid/missing.
- typical: 12/12 complete valid pairs; 0 invalid/missing.
- dense: 12/12 complete valid pairs; 0 invalid/missing.

## Whole-worker resources and separate setup

RSS values describe the whole worker, including imports/setup/preparation, measured before verification. They are not incremental API allocation. Parent subprocess lifetime includes interpreter, setup, verification and serialization. Waited-child maxima are separate; no peak sums are computed.

| Fixture | Arm | Workers | Setup wall mean / median ms | Process lifetime mean / median ms | SELF peak mean / median MiB | Waited-child max mean / median MiB |
|---|---|---:|---|---|---|---|
| noignore | baseline | 12 | 25.4747 / 23.6550 | 371.0677 / 269.0776 | 15.2500 / 15.2500 | 0.0000 / 0.0000 |
| noignore | candidate | 12 | 28.0708 / 23.2057 | 302.4537 / 267.4733 | 15.2080 / 15.2500 | 0.0000 / 0.0000 |
| typical | baseline | 12 | 32.4657 / 31.8452 | 468.7925 / 343.8123 | 15.2396 / 15.2500 | 0.0000 / 0.0000 |
| typical | candidate | 12 | 26.8112 / 25.7470 | 387.2604 / 347.0805 | 15.2604 / 15.2500 | 0.0000 / 0.0000 |
| dense | baseline | 12 | 27.8741 / 27.3945 | 529.3790 / 494.3804 | 15.8854 / 15.8750 | 0.0000 / 0.0000 |
| dense | candidate | 12 | 25.4178 / 25.2837 | 510.0473 / 443.5606 | 15.9688 / 16.0000 | 0.0000 / 0.0000 |

## Separate diagnostic workers

These instrumented read/compile observations do not enter timing summaries. Every diagnostic has one first and five warm calls; API read attempts/bytes are not actual filesystem I/O. Exact fallback controls are retained in JSON.

| Fixture | Arm | Phase | Policy compilations per call | Policy read attempts per call | Source read attempts per call |
|---|---|---|---|---|---|
| noignore | baseline | first | 0 | 0 | 2 |
| noignore | baseline | warm | 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0 | 2, 2, 2, 2, 2 |
| noignore | candidate | first | 0 | 0 | 2 |
| noignore | candidate | warm | 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0 | 2, 2, 2, 2, 2 |
| typical | baseline | first | 6 | 6 | 8 |
| typical | baseline | warm | 6, 6, 6, 6, 6 | 6, 6, 6, 6, 6 | 8, 8, 8, 8, 8 |
| typical | candidate | first | 3 | 6 | 8 |
| typical | candidate | warm | 3, 3, 3, 3, 3 | 6, 6, 6, 6, 6 | 8, 8, 8, 8, 8 |
| dense | baseline | first | 2 | 2 | 8 |
| dense | baseline | warm | 2, 2, 2, 2, 2 | 2, 2, 2, 2, 2 | 8, 8, 8, 8, 8 |
| dense | candidate | first | 1 | 2 | 8 |
| dense | candidate | warm | 1, 1, 1, 1, 1 | 2, 2, 2, 2, 2 | 8, 8, 8, 8, 8 |

Exact stable results and source/policy read-call equality checks: `[{"fixture": "noignore", "source_policy_reads_and_fallbacks_preserved": true}, {"fixture": "typical", "source_policy_reads_and_fallbacks_preserved": true}, {"fixture": "dense", "source_policy_reads_and_fallbacks_preserved": true}]`.

## Unmatched development probes: confounded

The earlier unmatched no-ignore control mean fell from **23.10 to 10.71 ms with the same instrumented work**. That apparent improvement is not attributed to this cache. All raw before/after profiles remain under `evidence/source-only-refinement/development-unmatched/`; their inclusive instrumentation timers are not added or pooled with the balanced study.

## Historical model evidence, kept separate

Both favorable historical cohorts used this complete known-path source path. Warm's 9.055% lower API-equivalent cost and 6.892% shorter mean instrumented time are a partial, post-hoc matched sample. Confirmation's 10.19% lower focused-task cost accompanied 3.18% slower mean time; its all-task estimate was only about 2.47% lower. Cache-write scenarios can reverse rankings. These are not billed savings and are not effects of the new local cache.

New model input/cached/output tokens, provider model calls, strict native task success, model cost per success and actual charges are **unavailable**. Zero model requests were dispatched. A paid old/new model comparison would not attribute token differences to identical prompt bytes.

## Verification

The complete Python run records **2081 passed**, 0 failed, 0 errors and 0 skipped. Overlapping targeted preload/runner/security reruns are retained without adding their counts. Frontend: 24/24; browser expected passes: 3; installed smoke: 15/15 separate checks. Build/static/security receipts are retained in JSON.

Initial failed XML receipts: `[]`.

The [independent read-only audit](evidence/source-only-refinement/audit/independent-profile-audit.json)
reconstructed all 78 original workers, 468 exact source/prompt observations,
24 fallback controls and all 18 statistical summaries. It confirms the frozen
source seals, balanced order and compiler/read counts. All original observations
remain in the primary results. Its leave-one-pair-out values and order strata
are post-hoc sensitivity diagnostics, not replacement estimates or explanations
of the outliers. Bootstrap intervals are unadjusted for multiple comparisons.

The typical warm −2.08% above is a ratio of arm means; the mean paired percentage
change is +1.01% and the paired median delta is +0.085 ms. These summaries answer
different questions. Neither the arm medians nor the ratio of arm means should
be presented as the median or mean paired percentage effect.

## Every original worker

The raw requests, stdout/stderr, result receipts and frozen preparer snapshots are allowlisted in the artifact ledger. All failures and missing metrics remain visible; diagnostics are not silently pooled into performance.

| # | Kind | Fixture | Repeat | Arm | Valid | First wall ms | Warm worker mean wall ms | Worker lifetime ms | Error |
|---:|---|---|---:|---|---|---:|---:|---:|---|
| 1 | performance | typical | 3 | candidate | True | 377.2760 | 25.5943 | 968.6253 |  |
| 2 | performance | typical | 3 | baseline | True | 144.0399 | 13.8502 | 893.6379 |  |
| 3 | performance | typical | 8 | candidate | True | 80.4630 | 15.1211 | 369.5989 |  |
| 4 | performance | typical | 8 | baseline | True | 61.6796 | 20.6556 | 367.0495 |  |
| 5 | performance | typical | 9 | candidate | True | 71.7311 | 17.2401 | 368.1920 |  |
| 6 | performance | typical | 9 | baseline | True | 81.3573 | 16.4688 | 419.3226 |  |
| 7 | performance | dense | 7 | baseline | True | 146.0423 | 45.3472 | 723.0897 |  |
| 8 | performance | dense | 7 | candidate | True | 130.4750 | 40.5293 | 572.0512 |  |
| 9 | performance | typical | 2 | candidate | True | 64.4936 | 14.9622 | 369.7248 |  |
| 10 | performance | typical | 2 | baseline | True | 67.5762 | 13.0767 | 317.7910 |  |
| 11 | performance | typical | 5 | candidate | True | 67.9097 | 15.7983 | 368.2177 |  |
| 12 | performance | typical | 5 | baseline | True | 81.1520 | 16.8908 | 373.1256 |  |
| 13 | performance | dense | 10 | candidate | True | 123.9023 | 27.1131 | 468.7310 |  |
| 14 | performance | dense | 10 | baseline | True | 128.2226 | 34.3447 | 522.5636 |  |
| 15 | performance | noignore | 6 | baseline | True | 163.6090 | 175.9700 | 1526.0355 |  |
| 16 | performance | noignore | 6 | candidate | True | 56.1596 | 4.0083 | 328.7128 |  |
| 17 | performance | dense | 8 | baseline | True | 172.0776 | 39.3703 | 620.6538 |  |
| 18 | performance | dense | 8 | candidate | True | 126.1772 | 135.7598 | 1050.0043 |  |
| 19 | performance | dense | 12 | candidate | True | 163.5853 | 30.6822 | 585.9217 |  |
| 20 | performance | dense | 12 | baseline | True | 215.5171 | 33.8871 | 625.6470 |  |
| 21 | performance | typical | 1 | candidate | True | 84.5960 | 11.1748 | 320.3571 |  |
| 22 | performance | typical | 1 | baseline | True | 136.0417 | 18.1201 | 1382.5907 |  |
| 23 | performance | dense | 5 | baseline | True | 161.1987 | 40.2526 | 762.1390 |  |
| 24 | performance | dense | 5 | candidate | True | 161.1966 | 29.5189 | 527.8545 |  |
| 25 | performance | typical | 10 | baseline | True | 60.5770 | 10.9093 | 375.9329 |  |
| 26 | performance | typical | 10 | candidate | True | 54.5947 | 11.6579 | 268.9818 |  |
| 27 | performance | noignore | 2 | baseline | True | 62.9502 | 3.1656 | 272.6142 |  |
| 28 | performance | noignore | 2 | candidate | True | 66.6584 | 5.3128 | 382.8277 |  |
| 29 | performance | noignore | 8 | candidate | True | 49.1998 | 2.9094 | 266.1637 |  |
| 30 | performance | noignore | 8 | baseline | True | 64.8211 | 3.3172 | 317.2364 |  |
| 31 | performance | dense | 2 | baseline | True | 131.3925 | 26.9959 | 471.8353 |  |
| 32 | performance | dense | 2 | candidate | True | 108.4783 | 24.7265 | 418.3902 |  |
| 33 | performance | noignore | 5 | baseline | True | 59.3954 | 2.7664 | 267.6246 |  |
| 34 | performance | noignore | 5 | candidate | True | 64.4570 | 5.5264 | 317.2413 |  |
| 35 | performance | noignore | 4 | baseline | True | 49.0525 | 3.7551 | 215.6245 |  |
| 36 | performance | noignore | 4 | candidate | True | 53.4795 | 3.0551 | 267.6643 |  |
| 37 | performance | dense | 11 | candidate | True | 113.8201 | 22.4135 | 416.6070 |  |
| 38 | performance | dense | 11 | baseline | True | 113.9483 | 38.9649 | 516.9255 |  |
| 39 | performance | dense | 3 | candidate | True | 111.0441 | 22.2075 | 367.9049 |  |
| 40 | performance | dense | 3 | baseline | True | 99.5466 | 25.5878 | 418.6824 |  |
| 41 | performance | noignore | 10 | candidate | True | 65.3926 | 6.0275 | 366.6841 |  |
| 42 | performance | noignore | 10 | baseline | True | 43.3879 | 4.1248 | 217.8155 |  |
| 43 | performance | typical | 6 | baseline | True | 54.8406 | 12.4335 | 267.7373 |  |
| 44 | performance | typical | 6 | candidate | True | 65.2910 | 11.9847 | 317.3276 |  |
| 45 | performance | noignore | 9 | candidate | True | 50.8020 | 3.1146 | 218.6516 |  |
| 46 | performance | noignore | 9 | baseline | True | 52.7159 | 2.8831 | 240.9343 |  |
| 47 | performance | dense | 6 | baseline | True | 111.7245 | 26.1702 | 418.4710 |  |
| 48 | performance | dense | 6 | candidate | True | 170.3664 | 36.7037 | 568.3802 |  |
| 49 | performance | typical | 7 | baseline | True | 85.7213 | 13.5964 | 320.5752 |  |
| 50 | performance | typical | 7 | candidate | True | 52.6746 | 11.6185 | 277.9530 |  |
| 51 | performance | typical | 4 | baseline | True | 56.8811 | 12.4271 | 319.4406 |  |
| 52 | performance | typical | 4 | candidate | True | 56.9215 | 13.0451 | 325.9691 |  |
| 53 | performance | noignore | 11 | candidate | True | 44.0748 | 5.2607 | 228.9074 |  |
| 54 | performance | noignore | 11 | baseline | True | 122.0839 | 4.2745 | 320.9151 |  |
| 55 | performance | dense | 4 | candidate | True | 112.0538 | 21.8154 | 403.2762 |  |
| 56 | performance | dense | 4 | baseline | True | 118.7649 | 26.2326 | 418.7703 |  |
| 57 | performance | noignore | 12 | candidate | True | 43.5143 | 2.0749 | 219.1822 |  |
| 58 | performance | noignore | 12 | baseline | True | 72.4446 | 4.0580 | 270.5307 |  |
| 59 | performance | typical | 11 | baseline | True | 51.1913 | 11.1439 | 270.9141 |  |
| 60 | performance | typical | 11 | candidate | True | 50.2099 | 13.1185 | 372.5185 |  |
| 61 | performance | dense | 9 | baseline | True | 148.5580 | 27.5301 | 426.2106 |  |
| 62 | performance | dense | 9 | candidate | True | 94.9846 | 24.2878 | 368.7876 |  |
| 63 | performance | noignore | 1 | baseline | True | 49.7087 | 2.7057 | 216.8958 |  |
| 64 | performance | noignore | 1 | candidate | True | 56.2810 | 2.8467 | 267.2824 |  |
| 65 | performance | dense | 1 | candidate | True | 97.2039 | 18.1999 | 372.6588 |  |
| 66 | performance | dense | 1 | baseline | True | 112.3661 | 29.3265 | 427.5603 |  |
| 67 | performance | noignore | 3 | candidate | True | 49.4620 | 2.7740 | 244.0750 |  |
| 68 | performance | noignore | 3 | baseline | True | 91.1918 | 5.6272 | 366.6549 |  |
| 69 | performance | typical | 12 | baseline | True | 59.6588 | 17.1415 | 317.3928 |  |
| 70 | performance | typical | 12 | candidate | True | 60.2468 | 11.7295 | 319.6587 |  |
| 71 | performance | noignore | 7 | baseline | True | 51.9735 | 2.9229 | 219.9310 |  |
| 72 | performance | noignore | 7 | candidate | True | 90.6121 | 4.6783 | 522.0525 |  |
| 73 | diagnostic | noignore | 1 | baseline | True | unavailable | unavailable | 618.1089 |  |
| 74 | diagnostic | noignore | 1 | candidate | True | unavailable | unavailable | 690.6031 |  |
| 75 | diagnostic | typical | 1 | baseline | True | unavailable | unavailable | 821.8034 |  |
| 76 | diagnostic | typical | 1 | candidate | True | unavailable | unavailable | 450.5101 |  |
| 77 | diagnostic | dense | 1 | baseline | True | unavailable | unavailable | 972.4777 |  |
| 78 | diagnostic | dense | 1 | candidate | True | unavailable | unavailable | 829.2369 |  |

## Limits and next experiments

- Synthetic source-only development fixtures and minimal SQLite approval tables; no real repository indexing, AST/Tree-sitter, held-out coding tasks or native agents ran in this local profile.
- First-call API timing includes first lazy imports; warm uses one mean per worker. Diagnostic instrumentation, fallbacks, setup and subprocess lifetime are separate from primary API timings.
- No fixture-weighted overall performance headline is computed. Fixture-specific variation, failures, missing pairs and no-effect controls remain visible.
- Whole-worker Linux SELF peak RSS includes interpreter/imports/setup/preparation and is not incremental API memory. Maximum waited-child RSS is separate, not simultaneous total; never add peaks.
- Own CPU excludes children; waited child CPU is a separate observed counter. OS caches and shared-host load remain uncontrolled.
- Stable normal prompt bytes and source hashes match across all 468 calls. Current source/policy read-call counts match across the 36 instrumented diagnostic calls only. These are API read-call observations, not filesystem or storage I/O counts.
- Identical native input/settings make a paid old/new model test non-attributable for this compiled-ignore cache. Local effects do not establish new token, cache-hit, billing or native-task savings.
- Historical 9.055% lower estimated cost is a partial post-hoc matched warm cohort; 10.19% belongs to focused confirmation tasks while its all-task difference is about 2.47%. Those corpora are not pooled or attributed to this refinement.

Next: replicate local effects on realistic known-path ignore layouts and edited-policy/race controls while preserving exact source bytes and all fresh reads. Only a separately frozen change to model-visible representation or workflow warrants fresh native cost-per-success evaluation.

[Detailed JSON](source-only-refinement-assessment.json) · [Artifact ledger](evidence/source-only-refinement/artifact-ledger.json)
