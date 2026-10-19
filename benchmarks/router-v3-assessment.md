# Runtime-aware source router v3: independent offline assessment

Frozen application commit: `b653d6b46d98d8c90f89131c520791df4b396452`. Comparison integrity: **True**.

This study measures complete-source selection and local preparation, not completed coding tasks. No Codex/model was dispatched; model token usage, cache reads/writes, cost per coding success and actual billed charges are unavailable. It cannot establish a faster or cheaper coding agent or a best retrieval architecture.

## Measured negative efficiency result

The positive-task means below include every positive assignment, including safe selection misses. They measure local preparation, not full coding-task time. The v3-versus-v2 addition is more local work; a target-inclusion gain is not a latency win.

| Positive-task metric | V2 mean ms | C mean ms | Relative mean change | Paired mean C−V2 95% interval ms |
| --- | ---: | ---: | ---: | --- |
| preparation_wall_seconds | 141.669 | 151.590 | +7.00% | [-1.312, 28.485] |
| setup_plus_preparation_wall_seconds | 443.831 | 448.815 | +1.12% | [-11.240, 25.856] |

These small unadjusted intervals are descriptive/exploratory, include zero where shown, and do not establish unchanged latency or a generalizable effect. The known-path baseline and all repeated observations remain in the full tables below.

## Design and observed scope

The frozen plan contains 12 tasks, four arms and two repeats: 96 assignments. 96 original observations are retained; 0 assignments are unrun. B is complete source from caller-known paths, V1/V2 are frozen compatibility selectors, and C is opt-in v3. Automatic arms receive no target paths or grading data. All use identical public task text, isolated ordinal worktrees, new processes/databases, 12,000 context bytes and a 4,000 estimated-token cap where applicable. The latter is a planning proxy, not measured model usage.

Positive targets and negative controls are reported separately. A complete declared target bundle is a scope proxy, not semantic dependency completeness, a repaired program, coding correctness or code quality. A safe positive bypass is a miss. Negative bypasses never offset positive misses. B is an oracle baseline: human path-discovery cost is unmeasured.

## Positive inclusion and negative controls

| Arm | Positive complete / planned | Negative bypass / planned | Valid delivery / planned | Worker / evaluator errors |
| --- | ---: | ---: | ---: | ---: |
| B | 16/16 | 8/8 | 24/24 | 0 / 0 |
| V1 | 0/16 | 8/8 | 24/24 | 0 / 0 |
| V2 | 4/16 | 8/8 | 24/24 | 0 / 0 |
| C | 6/16 | 8/8 | 24/24 | 0 / 0 |

V3 completed declared positive scope consistently for **3/8 tasks**, versus V2 2/8, V1 0/8 and known-path B 8/8. Repeated runs are repeated measurements, not additional independent tasks. An extra complete task is a narrow observed inclusion improvement; the remaining misses keep v3 experimental.

### Observed selection and bypass categories

These are emitted receipt reasons, not an independently established causal diagnosis. An index/policy safety decline remains a positive miss. A control bypass caused by an incomplete index does not prove that semantic task intent was recognized.

| Stratum | Arm | Reason | Original observations |
| --- | --- | --- | ---: |
| positive | B | explicit_focus | 16 |
| positive | V1 | candidate_limit_reached | 2 |
| positive | V1 | incomplete_index | 4 |
| positive | V1 | weak_lexical_evidence | 10 |
| positive | V2 | ambiguous_candidates | 2 |
| positive | V2 | automatic_verified_source | 4 |
| positive | V2 | candidate_limit_reached | 2 |
| positive | V2 | evidence_candidate_limit | 2 |
| positive | V2 | incomplete_index | 4 |
| positive | V2 | source_lexical_language_unavailable | 2 |
| positive | C | automatic_verified_source | 6 |
| positive | C | candidate_limit_reached | 2 |
| positive | C | evidence_candidate_limit | 2 |
| positive | C | incomplete_index | 4 |
| positive | C | runtime_language_unavailable | 2 |
| abstention_control | B | disabled | 8 |
| abstention_control | V1 | incomplete_index | 2 |
| abstention_control | V1 | no_production_match | 2 |
| abstention_control | V1 | weak_lexical_evidence | 4 |
| abstention_control | V2 | incomplete_index | 2 |
| abstention_control | V2 | no_production_match | 2 |
| abstention_control | V2 | weak_lexical_evidence | 4 |
| abstention_control | C | incomplete_index | 2 |
| abstention_control | C | no_production_match | 2 |
| abstention_control | C | weak_lexical_evidence | 4 |

### Every positive task's declared scope

Hits count valid complete required-path inclusion across two original repeats. Modes/reasons summarize those repeats without replacing any individual record. Repeated required bundles remain visible; the declared paths were kept private from automatic workers.

| Task / repository | Declared required paths | B | V1 | V2 | C |
| --- | --- | --- | --- | --- | --- |
| t01 / r01 | src/humanize/filesize.py, src/humanize/i18n.py | 2/2; preloaded/explicit_focus | 0/2; passthrough/weak_lexical_evidence | 0/2; passthrough/source_lexical_language_unavailable | 0/2; passthrough/runtime_language_unavailable |
| t02 / r01 | src/humanize/lists.py | 2/2; preloaded/explicit_focus | 0/2; passthrough/weak_lexical_evidence | 0/2; passthrough/ambiguous_candidates | 2/2; preloaded/automatic_verified_source |
| t04 / r02 | src/mistune/plugins/task_lists.py | 2/2; preloaded/explicit_focus | 0/2; passthrough/candidate_limit_reached | 0/2; passthrough/candidate_limit_reached | 0/2; passthrough/candidate_limit_reached |
| t05 / r02 | src/mistune/plugins/math.py | 2/2; preloaded/explicit_focus | 0/2; passthrough/weak_lexical_evidence | 0/2; passthrough/evidence_candidate_limit | 0/2; passthrough/evidence_candidate_limit |
| t07 / r03 | src/index.ts | 2/2; preloaded/explicit_focus | 0/2; passthrough/weak_lexical_evidence | 2/2; preloaded/automatic_verified_source | 2/2; preloaded/automatic_verified_source |
| t08 / r03 | src/index.ts | 2/2; preloaded/explicit_focus | 0/2; passthrough/weak_lexical_evidence | 2/2; preloaded/automatic_verified_source | 2/2; preloaded/automatic_verified_source |
| t10 / r04 | src/utils.ts | 2/2; preloaded/explicit_focus | 0/2; passthrough/incomplete_index | 0/2; passthrough/incomplete_index | 0/2; passthrough/incomplete_index |
| t11 / r04 | src/_internal.ts | 2/2; preloaded/explicit_focus | 0/2; passthrough/incomplete_index | 0/2; passthrough/incomplete_index | 0/2; passthrough/incomplete_index |

## Local timing, CPU, memory and source volume

Each value is **mean / median**. Wall and CPU values are milliseconds; peak RSS values are MiB. Setup includes approval/index construction; preparation is the source API. Their sum excludes imports/startup, worktree creation, grading and report writing. Worker lifetime includes startup, serialization and session cleanup, including observed failed attempts. API metrics exist only when observed; JSON records coverage for every field. Parent and waited-child CPU are separate. SELF RSS is whole-worker high water, not incremental API memory; child RSS is a maximum, not a concurrent sum. Never add the two peaks.

### all

| Arm | Setup+prep wall | Prep wall | Parent setup CPU | Parent prep CPU | Child setup CPU | Child prep CPU | SELF RSS | Max child RSS | Worker lifetime | Added bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B | 303.676 / 301.946 | 3.479 / 4.282 | 208.317 / 176.141 | 3.478 / 4.282 | 65.548 / 40.983 | 0.000 / 0.000 | 24.760 / 24.953 | 22.885 / 22.398 | 429.749 / 414.905 | 2247.917 / 1850.000 |
| V1 | 423.346 / 401.663 | 119.291 / 97.925 | 210.567 / 167.690 | 106.981 / 84.056 | 66.531 / 42.046 | 10.416 / 9.691 | 24.883 / 25.055 | 25.065 / 25.500 | 540.161 / 514.987 | 0.000 / 0.000 |
| V2 | 441.780 / 403.265 | 135.315 / 129.683 | 211.587 / 176.678 | 114.735 / 90.775 | 67.097 / 41.179 | 18.664 / 9.893 | 24.890 / 25.051 | 25.064 / 25.521 | 565.247 / 515.248 | 472.333 / 0.000 |
| C | 450.256 / 418.046 | 149.350 / 132.757 | 207.310 / 175.625 | 114.323 / 92.153 | 66.392 / 40.106 | 33.075 / 12.339 | 24.887 / 25.012 | 25.105 / 25.619 | 576.036 / 540.233 | 578.333 / 0.000 |

### positive

| Arm | Setup+prep wall | Prep wall | Parent setup CPU | Parent prep CPU | Child setup CPU | Child prep CPU | SELF RSS | Max child RSS | Worker lifetime | Added bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B | 306.490 / 301.946 | 5.203 / 4.689 | 208.915 / 177.149 | 5.202 / 4.689 | 65.716 / 40.983 | 0.000 / 0.000 | 24.760 / 24.953 | 22.885 / 22.398 | 430.722 / 414.905 | 3371.875 / 2834.000 |
| V1 | 424.782 / 403.347 | 121.012 / 98.792 | 210.521 / 171.612 | 108.732 / 84.698 | 66.664 / 42.046 | 10.298 / 9.641 | 24.880 / 25.055 | 25.065 / 25.500 | 540.194 / 515.023 | 0.000 / 0.000 |
| V2 | 443.831 / 403.882 | 141.669 / 129.683 | 208.527 / 176.678 | 116.907 / 90.775 | 66.354 / 40.721 | 22.918 / 10.337 | 24.880 / 25.051 | 25.067 / 25.521 | 568.299 / 515.191 | 708.500 / 0.000 |
| C | 448.815 / 400.088 | 151.590 / 132.757 | 203.955 / 170.981 | 117.202 / 92.153 | 66.693 / 40.069 | 32.412 / 12.339 | 24.890 / 25.012 | 25.094 / 25.619 | 571.736 / 515.295 | 867.500 / 0.000 |

### abstention_control

| Arm | Setup+prep wall | Prep wall | Parent setup CPU | Parent prep CPU | Child setup CPU | Child prep CPU | SELF RSS | Max child RSS | Worker lifetime | Added bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B | 298.049 / 287.892 | 0.030 / 0.031 | 207.122 / 176.141 | 0.030 / 0.031 | 65.211 / 40.492 | 0.000 / 0.000 | 24.758 / 25.072 | 22.885 / 22.398 | 427.802 / 414.959 | 0.000 / 0.000 |
| V1 | 420.475 / 379.707 | 115.849 / 94.082 | 210.657 / 166.500 | 103.478 / 81.911 | 66.263 / 40.763 | 10.653 / 10.350 | 24.888 / 25.137 | 25.064 / 25.500 | 540.097 / 514.951 | 0.000 / 0.000 |
| V2 | 437.676 / 391.779 | 122.608 / 104.245 | 217.708 / 176.144 | 110.391 / 92.735 | 68.583 / 41.896 | 10.154 / 9.333 | 24.909 / 25.199 | 25.060 / 25.500 | 559.142 / 515.248 | 0.000 / 0.000 |
| C | 453.138 / 428.787 | 144.869 / 125.338 | 214.020 / 178.071 | 108.565 / 88.108 | 65.790 / 40.251 | 34.401 / 33.358 | 24.881 / 25.064 | 25.125 / 25.617 | 584.636 / 565.041 | 0.000 / 0.000 |

## Preregistered paired effects

Differences are C minus the named baseline, copied from the frozen runner. Positive values mean more local work/bytes. Intervals use 2,000 fixed-seed task-cluster bootstrap draws retaining both repeats; paired metrics require observed valid delivery for both arms and both repeats. The intervals are unadjusted for multiple comparisons and interpreted as exploratory, not confirmatory. The task cluster does not capture repository/file dependence: eight positives share seven distinct target bundles, and two repositories are from the same unjs ecosystem. These are small authored, partly related observations, not independent production samples. OS caches and host load remain uncontrolled; balanced precedence does not equal identical cache state.

| Contrast / stratum / metric | Task clusters / pairs | Mean delta | Median delta | Mean 95% interval | Median 95% interval |
| --- | ---: | ---: | ---: | --- | --- |
| C_minus_B:abstention_control:context_bytes | 4 / 8 | 0.000 bytes | 0.000 bytes | [0.000, 0.000] bytes | [0.000, 0.000] bytes |
| C_minus_B:abstention_control:preparation_cpu_seconds | 4 / 8 | 108.535 ms | 88.077 ms | [43.182, 173.887] ms | [40.167, 214.833] ms |
| C_minus_B:abstention_control:preparation_wall_seconds | 4 / 8 | 144.839 ms | 125.307 ms | [53.632, 236.046] ms | [50.290, 274.329] ms |
| C_minus_B:abstention_control:self_peak_rss_bytes | 4 / 8 | 0.123 MiB | 0.119 MiB | [-0.063, 0.310] MiB | [-0.002, 0.375] MiB |
| C_minus_B:abstention_control:setup_plus_preparation_wall_seconds | 4 / 8 | 155.089 ms | 137.236 ms | [55.004, 255.175] ms | [50.816, 292.871] ms |
| C_minus_B:positive:context_bytes | 8 / 16 | -2504.375 bytes | -1583.500 bytes | [-4629.500, -716.000] bytes | [-4472.000, 0.000] bytes |
| C_minus_B:positive:preparation_cpu_seconds | 8 / 16 | 112.000 ms | 86.291 ms | [68.670, 158.558] ms | [46.608, 185.637] ms |
| C_minus_B:positive:preparation_wall_seconds | 8 / 16 | 146.388 ms | 126.964 ms | [99.594, 192.640] ms | [58.381, 226.564] ms |
| C_minus_B:positive:self_peak_rss_bytes | 8 / 16 | 0.129 MiB | 0.238 MiB | [0.039, 0.211] MiB | [0.000, 0.246] MiB |
| C_minus_B:positive:setup_plus_preparation_wall_seconds | 8 / 16 | 142.325 ms | 124.797 ms | [97.338, 184.141] ms | [96.968, 218.552] ms |
| C_minus_V1:abstention_control:context_bytes | 4 / 8 | 0.000 bytes | 0.000 bytes | [0.000, 0.000] bytes | [0.000, 0.000] bytes |
| C_minus_V1:abstention_control:preparation_cpu_seconds | 4 / 8 | 5.086 ms | 2.754 ms | [-0.012, 10.853] ms | [-0.031, 12.389] ms |
| C_minus_V1:abstention_control:preparation_wall_seconds | 4 / 8 | 29.020 ms | 26.018 ms | [-0.410, 58.449] ms | [-0.608, 63.065] ms |
| C_minus_V1:abstention_control:self_peak_rss_bytes | 4 / 8 | -0.007 MiB | 0.002 MiB | [-0.018, 0.004] MiB | [-0.016, 0.006] MiB |
| C_minus_V1:abstention_control:setup_plus_preparation_wall_seconds | 4 / 8 | 32.664 ms | 36.054 ms | [5.282, 60.228] ms | [-1.445, 70.363] ms |
| C_minus_V1:positive:context_bytes | 8 / 16 | 867.500 bytes | 0.000 bytes | [159.000, 1771.250] bytes | [0.000, 2053.000] bytes |
| C_minus_V1:positive:preparation_cpu_seconds | 8 / 16 | 8.470 ms | 2.960 ms | [-0.092, 18.546] ms | [-2.244, 17.373] ms |
| C_minus_V1:positive:preparation_wall_seconds | 8 / 16 | 30.579 ms | 1.989 ms | [5.729, 62.387] ms | [-1.676, 71.019] ms |
| C_minus_V1:positive:self_peak_rss_bytes | 8 / 16 | 0.010 MiB | 0.000 MiB | [-0.004, 0.027] MiB | [-0.006, 0.006] MiB |
| C_minus_V1:positive:setup_plus_preparation_wall_seconds | 8 / 16 | 24.033 ms | 5.309 ms | [-7.819, 58.836] ms | [-14.401, 67.742] ms |
| C_minus_V2:abstention_control:context_bytes | 4 / 8 | 0.000 bytes | 0.000 bytes | [0.000, 0.000] bytes | [0.000, 0.000] bytes |
| C_minus_V2:abstention_control:preparation_cpu_seconds | 4 / 8 | -1.826 ms | -1.830 ms | [-4.337, 0.770] ms | [-3.122, 0.580] ms |
| C_minus_V2:abstention_control:preparation_wall_seconds | 4 / 8 | 22.261 ms | 21.243 ms | [-2.873, 47.395] ms | [-2.691, 46.963] ms |
| C_minus_V2:abstention_control:self_peak_rss_bytes | 4 / 8 | -0.028 MiB | 0.002 MiB | [-0.093, 0.006] MiB | [-0.008, 0.004] MiB |
| C_minus_V2:abstention_control:setup_plus_preparation_wall_seconds | 4 / 8 | 15.462 ms | 2.962 ms | [-9.528, 40.453] ms | [-8.224, 49.863] ms |
| C_minus_V2:positive:context_bytes | 8 / 16 | 159.000 bytes | 0.000 bytes | [0.000, 477.000] bytes | [0.000, 0.000] bytes |
| C_minus_V2:positive:preparation_cpu_seconds | 8 / 16 | 0.295 ms | 0.845 ms | [-2.148, 2.395] ms | [-3.124, 3.714] ms |
| C_minus_V2:positive:preparation_wall_seconds | 8 / 16 | 9.922 ms | 1.578 ms | [-1.312, 28.485] ms | [-1.906, 6.940] ms |
| C_minus_V2:positive:self_peak_rss_bytes | 8 / 16 | 0.010 MiB | 0.000 MiB | [-0.011, 0.043] MiB | [-0.010, 0.004] MiB |
| C_minus_V2:positive:setup_plus_preparation_wall_seconds | 8 / 16 | 4.983 ms | -2.322 ms | [-11.240, 25.856] ms | [-14.842, 11.779] ms |

## What improved, regressed or remains unproven

| Item | Observed result and limit |
| --- | --- |
| C declared positive inclusion versus B | lower: 6/16 versus 16/16; descriptive scope counts, not coding success. |
| C declared positive inclusion versus V1 | higher: 6/16 versus 0/16; descriptive scope counts, not coding success. |
| C declared positive inclusion versus V2 | higher: 6/16 versus 4/16; descriptive scope counts, not coding success. |
| Complete-source safety | Canonical Git bytes, hashes, whole-file ranges and exact task suffix are independently checked. Synthetic security controls and production tests are separate evidence. |
| Local efficiency | Mean/median paired effects and uncertainty above; selection misses, setup costs and failed attempts remain visible. No blanket latency win is inferred. |
| Model efficiency and actual billing | Unmeasured: no input/cached/uncached/output tokens, avoided reads, model cost per success or billed-charge comparison. |
| Product readiness | Local tests and installed transport smoke do not establish hosted multi-tenant operational readiness, semantic completeness or an optimal architecture. |
| Defaults and memory | Known-path source delivery is preserved; automatic v3 remains explicit/experimental, v1 is the compatibility default, and automatic warm-memory injection stays disabled. |

## Validation and preserved failures

The primary Python 3.12 complete suite is one run. The full Python 3.11 run is a separate runtime check, not additional distinct tests; targeted compatibility and focused receipts overlap those full runs and are not added to a larger total. Final full-runtime receipts cover the completed tree with the fresh corpus; the earlier Python 3.12 run preceded corpus creation. The corpus-schema validator repair occurred after the frozen offline cohort and changed only test schema normalization, not its freshness assertions or frozen production/runner/corpus. Frontend, browser and installed-smoke counts are separate surfaces, not a pooled success claim.

| Receipt | Passed | Failed / errors / skipped |
| --- | ---: | ---: |
| full-python.xml | 2188 | 0 / 0 / 0 |
| full-python-before-corpus.xml | 2188 | 0 / 0 / 0 |
| corpus-schema-regression.xml | 1 | 0 / 0 / 0 |
| affected-initial.xml | 348 | 1 / 0 / 0 |
| affected-final.xml | 349 | 0 / 0 / 0 |
| integration-initial.xml | 89 | 1 / 0 / 0 |
| integration-final.xml | 90 | 0 / 0 / 0 |
| python311-compatibility.xml | 191 | 0 / 0 / 0 |
| python311-router.xml | 148 | 0 / 0 / 0 |
| python311-full.xml | 2188 | 0 / 0 / 0 |
| python311-full-initial.xml | 2187 | 1 / 0 / 0 |
| source-resilience-initial.xml | 4 | 0 / 0 / 0 |
| automatic-v3-runner-unit.xml | 39 | 0 / 0 / 0 |
| automatic-v3-runner-unit-final.xml | 41 | 0 / 0 / 0 |
| automatic-v3-runner-unit-final-2.xml | 41 | 0 / 0 / 0 |
| automatic-v3-runner-unit-final-3.xml | 41 | 0 / 0 / 0 |
| runner-unit-final.xml | 41 | 0 / 0 / 0 |

Frontend unit: **24 passed**, 0 failed; production browser: **3 passed**, 0 unexpected, 0 flaky; final installed-wheel/API/SPA/default-and-agent MCP/CLI smoke: **20/20 checks passed**, as retained receipts describe. The complete Python 3.11 runtime and its overlapping targeted compatibility runs are recorded separately. Lint, typing, wheel reconstruction, frozen dependency install and checksum-verified actionlint are in build-static.json. Remote GitHub CI execution is not established by the local workflow check.

Separate synthetic source safety controls: **6/6 passed**; aggregate receipt passed = **True**. These controls are not added to scope-success or timing denominators.

- Owner development: 43 passed/6 failed, then 48 passed/3 failed; the final owned run passed 51. dev-attempts.json records causes. Original stdout was not saved and is not reconstructed.
- First root integration run: 89 passed/1 failed because a tamper fixture did not change any bytes. The new fixture was corrected; final 90 passed.
- First affected run: 348 passed/1 failed because the formerly unknown version v3 became valid. The unknown-version assertion was retained with v99; final 349 passed.
- Initial installed-wheel smoke reached 17 checks, then received the correct HTTP 403 because the helper omitted the required request header. Initial script, receipt and logs remain; final helper supplies the header and explicitly tests rejection, with 20 checks passing.
- Earlier runner synthetic receipts are retained alongside final receipts; these development observations are not held-out benchmark assignments.
- After the frozen cohort finished, the first complete Python 3.11 run with the fresh corpus had 2,187 passed/1 failed: an older tasks*.json corpus validator assumed every manifest was a dictionary, while frozen v3 uses a declared list schema. This post-study minimal test-only schema normalization retained every freshness assertion; its targeted regression and both complete runtime suites were rerun with the corpus present. No frozen production, runner or corpus bytes changed. The earlier Python 3.12 run passed 2,188 before corpus creation and is separately labeled.

Research refreshed official source/docs, not all complete papers. The archive retains exact snapshots, fetch hashes and one failed 404 followed by the discovered successful JSONL source. Mutable upstream URLs are identified by inspected hashes; competitor results are not Memglide measurements. See [research](router-v3-research.md) for the reading scope and remaining syntactic/semantic limits.

## Every original assignment

No retries or replacements are pooled. Unrun assignments are displayed explicitly; JSON and raw request/result/stdout/stderr preserve detailed receipts and errors.

| # | Task | Arm | Kind | Outcome | Decision | Prep ms | Worker ms | Added bytes | Selected paths |
| ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | t12 | V2 | abstention_control | expected bypass | SKIP | 60.519 | 565.480 | 0.000 | — |
| 2 | t12 | B | abstention_control | expected bypass | passthrough | 0.033 | 515.157 | 0.000 | — |
| 3 | t12 | C | abstention_control | expected bypass | SKIP | 57.552 | 565.347 | 0.000 | — |
| 4 | t12 | V1 | abstention_control | expected bypass | SKIP | 58.104 | 514.929 | 0.000 | — |
| 5 | t08 | V2 | positive | complete scope | FOCUSED_SOURCE | 126.861 | 414.728 | 2834.000 | src/index.ts |
| 6 | t08 | V1 | positive | positive miss | SKIP | 55.170 | 314.591 | 0.000 | — |
| 7 | t08 | B | positive | complete scope | preloaded | 4.489 | 268.199 | 2834.000 | src/index.ts |
| 8 | t08 | C | positive | complete scope | FOCUSED_SOURCE | 126.189 | 415.095 | 2834.000 | src/index.ts |
| 9 | t03 | B | abstention_control | expected bypass | passthrough | 0.028 | 364.575 | 0.000 | — |
| 10 | t03 | C | abstention_control | expected bypass | SKIP | 196.696 | 565.007 | 0.000 | — |
| 11 | t03 | V1 | abstention_control | expected bypass | SKIP | 131.991 | 514.973 | 0.000 | — |
| 12 | t03 | V2 | abstention_control | expected bypass | SKIP | 147.971 | 514.958 | 0.000 | — |
| 13 | t06 | V1 | abstention_control | expected bypass | SKIP | 225.783 | 865.916 | 0.000 | — |
| 14 | t06 | C | abstention_control | expected bypass | SKIP | 280.126 | 970.407 | 0.000 | — |
| 15 | t06 | V2 | abstention_control | expected bypass | SKIP | 228.498 | 866.333 | 0.000 | — |
| 16 | t06 | B | abstention_control | expected bypass | passthrough | 0.034 | 615.448 | 0.000 | — |
| 17 | t11 | V2 | positive | positive miss | SKIP | 57.191 | 565.163 | 0.000 | — |
| 18 | t11 | C | positive | positive miss | SKIP | 62.309 | 515.132 | 0.000 | — |
| 19 | t11 | B | positive | complete scope | preloaded | 3.928 | 515.055 | 739.000 | src/_internal.ts |
| 20 | t11 | V1 | positive | positive miss | SKIP | 61.782 | 515.157 | 0.000 | — |
| 21 | t10 | C | positive | positive miss | SKIP | 57.347 | 565.272 | 0.000 | — |
| 22 | t10 | B | positive | complete scope | preloaded | 4.563 | 464.943 | 4472.000 | src/utils.ts |
| 23 | t10 | V2 | positive | positive miss | SKIP | 57.447 | 514.864 | 0.000 | — |
| 24 | t10 | V1 | positive | positive miss | SKIP | 65.791 | 515.045 | 0.000 | — |
| 25 | t09 | B | abstention_control | expected bypass | passthrough | 0.027 | 264.311 | 0.000 | — |
| 26 | t09 | V1 | abstention_control | expected bypass | SKIP | 49.967 | 314.521 | 0.000 | — |
| 27 | t09 | V2 | abstention_control | expected bypass | SKIP | 54.888 | 315.244 | 0.000 | — |
| 28 | t09 | C | abstention_control | expected bypass | SKIP | 50.317 | 315.185 | 0.000 | — |
| 29 | t01 | C | positive | positive miss | SKIP | 139.058 | 515.069 | 0.000 | — |
| 30 | t01 | V1 | positive | positive miss | SKIP | 139.270 | 565.869 | 0.000 | — |
| 31 | t01 | B | positive | complete scope | preloaded | 7.239 | 364.920 | 9096.000 | src/humanize/filesize.py, src/humanize/i18n.py |
| 32 | t01 | V2 | positive | positive miss | SKIP | 132.504 | 464.814 | 0.000 | — |
| 33 | t02 | C | positive | complete scope | FOCUSED_SOURCE | 249.322 | 615.203 | 1272.000 | src/humanize/lists.py |
| 34 | t02 | V2 | positive | positive miss | SKIP | 166.422 | 514.871 | 0.000 | — |
| 35 | t02 | V1 | positive | positive miss | SKIP | 137.424 | 465.054 | 0.000 | — |
| 36 | t02 | B | positive | complete scope | preloaded | 4.757 | 364.586 | 1272.000 | src/humanize/lists.py |
| 37 | t07 | V1 | positive | positive miss | SKIP | 52.399 | 314.697 | 0.000 | — |
| 38 | t07 | V2 | positive | complete scope | FOCUSED_SOURCE | 119.888 | 414.888 | 2834.000 | src/index.ts |
| 39 | t07 | C | positive | complete scope | FOCUSED_SOURCE | 121.620 | 364.820 | 2834.000 | src/index.ts |
| 40 | t07 | B | positive | complete scope | preloaded | 4.216 | 264.505 | 2834.000 | src/index.ts |
| 41 | t04 | B | positive | complete scope | preloaded | 5.899 | 615.165 | 2428.000 | src/mistune/plugins/task_lists.py |
| 42 | t04 | C | positive | positive miss | SKIP | 231.357 | 818.976 | 0.000 | — |
| 43 | t04 | V2 | positive | positive miss | SKIP | 237.980 | 865.753 | 0.000 | — |
| 44 | t04 | V1 | positive | positive miss | SKIP | 233.160 | 865.874 | 0.000 | — |
| 45 | t05 | V1 | positive | positive miss | SKIP | 226.951 | 815.601 | 0.000 | — |
| 46 | t05 | C | positive | positive miss | SKIP | 229.501 | 817.978 | 0.000 | — |
| 47 | t05 | B | positive | complete scope | preloaded | 6.225 | 665.749 | 3300.000 | src/mistune/plugins/math.py |
| 48 | t05 | V2 | positive | positive miss | SKIP | 229.056 | 865.773 | 0.000 | — |
| 49 | t12 | V1 | abstention_control | expected bypass | SKIP | 57.207 | 515.016 | 0.000 | — |
| 50 | t12 | C | abstention_control | expected bypass | SKIP | 56.542 | 514.899 | 0.000 | — |
| 51 | t12 | B | abstention_control | expected bypass | passthrough | 0.033 | 465.193 | 0.000 | — |
| 52 | t12 | V2 | abstention_control | expected bypass | SKIP | 58.957 | 515.292 | 0.000 | — |
| 53 | t08 | C | positive | complete scope | FOCUSED_SOURCE | 126.457 | 414.630 | 2834.000 | src/index.ts |
| 54 | t08 | B | positive | complete scope | preloaded | 4.348 | 264.389 | 2834.000 | src/index.ts |
| 55 | t08 | V1 | positive | positive miss | SKIP | 51.133 | 314.692 | 0.000 | — |
| 56 | t08 | V2 | positive | complete scope | FOCUSED_SOURCE | 119.130 | 364.530 | 2834.000 | src/index.ts |
| 57 | t03 | V2 | abstention_control | expected bypass | SKIP | 149.100 | 515.205 | 0.000 | — |
| 58 | t03 | V1 | abstention_control | expected bypass | SKIP | 130.059 | 464.951 | 0.000 | — |
| 59 | t03 | C | abstention_control | expected bypass | SKIP | 193.124 | 565.076 | 0.000 | — |
| 60 | t03 | B | abstention_control | expected bypass | passthrough | 0.029 | 364.726 | 0.000 | — |
| 61 | t06 | B | abstention_control | expected bypass | passthrough | 0.032 | 568.391 | 0.000 | — |
| 62 | t06 | V2 | abstention_control | expected bypass | SKIP | 229.159 | 866.172 | 0.000 | — |
| 63 | t06 | C | abstention_control | expected bypass | SKIP | 274.361 | 866.725 | 0.000 | — |
| 64 | t06 | V1 | abstention_control | expected bypass | SKIP | 222.676 | 815.979 | 0.000 | — |
| 65 | t11 | V1 | positive | positive miss | SKIP | 59.913 | 515.001 | 0.000 | — |
| 66 | t11 | B | positive | complete scope | preloaded | 4.156 | 464.890 | 739.000 | src/_internal.ts |
| 67 | t11 | C | positive | positive miss | SKIP | 56.001 | 515.459 | 0.000 | — |
| 68 | t11 | V2 | positive | positive miss | SKIP | 62.418 | 515.304 | 0.000 | — |
| 69 | t10 | V1 | positive | positive miss | SKIP | 56.886 | 515.052 | 0.000 | — |
| 70 | t10 | V2 | positive | positive miss | SKIP | 60.221 | 515.777 | 0.000 | — |
| 71 | t10 | B | positive | complete scope | preloaded | 4.620 | 464.974 | 4472.000 | src/utils.ts |
| 72 | t10 | C | positive | positive miss | SKIP | 58.315 | 514.842 | 0.000 | — |
| 73 | t09 | C | abstention_control | expected bypass | SKIP | 50.235 | 314.442 | 0.000 | — |
| 74 | t09 | V2 | abstention_control | expected bypass | SKIP | 51.773 | 314.455 | 0.000 | — |
| 75 | t09 | V1 | abstention_control | expected bypass | SKIP | 51.008 | 314.493 | 0.000 | — |
| 76 | t09 | B | abstention_control | expected bypass | passthrough | 0.027 | 264.616 | 0.000 | — |
| 77 | t01 | V2 | positive | positive miss | SKIP | 135.929 | 515.078 | 0.000 | — |
| 78 | t01 | B | positive | complete scope | preloaded | 7.249 | 364.701 | 9096.000 | src/humanize/filesize.py, src/humanize/i18n.py |
| 79 | t01 | V1 | positive | positive miss | SKIP | 135.089 | 464.663 | 0.000 | — |
| 80 | t01 | C | positive | positive miss | SKIP | 141.353 | 514.822 | 0.000 | — |
| 81 | t02 | B | positive | complete scope | preloaded | 5.250 | 364.717 | 1272.000 | src/humanize/lists.py |
| 82 | t02 | V1 | positive | positive miss | SKIP | 131.793 | 464.712 | 0.000 | — |
| 83 | t02 | V2 | positive | positive miss | SKIP | 175.756 | 565.104 | 0.000 | — |
| 84 | t02 | C | positive | complete scope | FOCUSED_SOURCE | 237.960 | 565.055 | 1272.000 | src/humanize/lists.py |
| 85 | t07 | B | positive | complete scope | preloaded | 4.160 | 264.431 | 2834.000 | src/index.ts |
| 86 | t07 | C | positive | complete scope | FOCUSED_SOURCE | 121.160 | 364.549 | 2834.000 | src/index.ts |
| 87 | t07 | V2 | positive | complete scope | FOCUSED_SOURCE | 119.736 | 364.601 | 2834.000 | src/index.ts |
| 88 | t07 | V1 | positive | positive miss | SKIP | 52.699 | 314.519 | 0.000 | — |
| 89 | t04 | V1 | positive | positive miss | SKIP | 241.507 | 866.815 | 0.000 | — |
| 90 | t04 | V2 | positive | positive miss | SKIP | 241.199 | 815.971 | 0.000 | — |
| 91 | t04 | C | positive | positive miss | SKIP | 233.829 | 815.455 | 0.000 | — |
| 92 | t04 | B | positive | complete scope | preloaded | 6.145 | 615.266 | 2428.000 | src/mistune/plugins/task_lists.py |
| 93 | t05 | V2 | positive | positive miss | SKIP | 224.960 | 815.562 | 0.000 | — |
| 94 | t05 | B | positive | complete scope | preloaded | 5.999 | 565.071 | 3300.000 | src/mistune/plugins/math.py |
| 95 | t05 | C | positive | positive miss | SKIP | 233.670 | 815.427 | 0.000 | — |
| 96 | t05 | V1 | positive | positive miss | SKIP | 235.218 | 815.755 | 0.000 | — |

## Evidence, reproduction and next experiments

The [JSON assessment](router-v3-assessment.json) retains the original full report, all individual rows, derived strata, missing values and audit receipts. The [evidence ledger](evidence/router-v3/ledger.json) hashes an explicit allowlist of 799 files; the ledger excludes itself and these standalone assessment files to avoid circular hashes. Databases, worktrees, Git internals, environments, authentication and wheel/archive binaries are excluded. Historical reports and raw studies remain untouched.

Post-hoc index/candidate diagnostics, if archived, are kept separate from the frozen cohort; emitted bypass reasons alone are not causal proof. The independent formal audit also retains repository-cluster sensitivity; four repository clusters give limited uncertainty information and do not repair correlated target bundles.

To reproduce: check out the recorded application commit; install the frozen lock with `uv sync --frozen`; use the archived retained corpus, task/private-grade/provenance files and generic runner. Preserve the original policy freeze and plan; create a **new** policy freeze and **new** plan/output directories for a reproduction, because commits and absolute canonical paths differ. Follow `benchmarks/automatic-v3-protocol.md`: freeze, plan, controls, then run. Never execute downloaded upstream code. Use this collector with a new evidence directory/output prefix and an independent formal-audit path; it does not dispatch agents or rerun tasks.

Next, diagnose these preserved misses without treating this exposed cohort as a fresh tuning holdout. Add development regressions from the failure mechanism, then freeze the revised policy before authoring a new independent cohort with more unrelated repositories and target bundles. If offline inclusion and overhead justify it, preregister a separate matched bare-Codex/known-path/automatic model study with independent coding graders, actual available usage accounting, complete failed-attempt spend, equivalent-cache controls, an estimated maximum budget and a frozen plan. Only that study can test cost per successfully completed coding task. Keep v3 opt-in until such evidence supports promotion.
