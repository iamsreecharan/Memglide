# Task-aware router v2: final assessment

**The new automatic policy did not improve Memglide on its fresh test. It failed the fixed offline gate and is not promoted. No live Codex A/B/C requests were made.**

The existing known-path source path is preserved. Automatic discovery remains opt-in with its original v1 default; experimental v2 requires `--selection-policy v2` or `selection_policy="v2"`. V1 is retained for compatibility, not claimed efficient. Memory remains explicit. A fixed-width identifier-normalization fix addresses a separate resource defect.

## What was implemented and tested

V2 inspects bounded current identifier evidence, combines project/candidate term frequencies, compares distinct evidence rather than saturated-score ratios, and uses the existing pinned Tree-sitter grammars in one isolated local worker for JavaScript/TypeScript. It adds no selection LLM call and preserves complete-source safety, ignores, approvals, source hashes and exact fallback. [Implementation guide](../docs/task-aware-router.md), [research and resolved security/resource findings](router-v2-research.md).

The policy, corpus, protocol, graders, pricing, toolchain and assignments were frozen at `1dc88123a1705bd40cc5815dd6f5964185600844` before the first fresh selection. Twelve independently authored issue-only tasks cover four complete unfamiliar upstream snapshots: blinker, cachetools, defu and hookable. These are small controlled mutation tasks, six Python/six TypeScript. There are two repeats and all six arm permutations are balanced. No hidden answer, repair path or descriptive task identifier enters C's query or agent-visible worktree name.

Independent grading controls passed for all 12 defective baselines, reference restorations and partial/wrong fixes (36 expected outcomes). The fixed offline gate required C to preload on at least 50% of unique tasks and cover at least 75% of B-preparable scopes, with both repeats qualifying. It filters no individual formal task. [Frozen protocol](automatic-v2-protocol.md) and [preregistration](evidence/router-v2/plan/preregistration.json).

## Fresh offline outcomes

| Arm | Observations | Source delivered | Complete declared scope | Mean cold setup + prep (s) | Median (s) | Mean added bytes |
|---|---:|---:|---:|---:|---:|---:|
| B | 24 | 24 | 24 | 1.216337 | 0.872407 | 2507.17 |
| V1 | 24 | 0 | 0 | 1.357629 | 1.043358 | 0.00 |
| C | 24 | 2 | 0 | 2.098610 | 1.452500 | 317.17 |

B delivered the declared source on **12/12 tasks in both repeats**. C preloaded on **1/12**, but both preloads selected `src/types.ts` instead of the required runtime implementation `src/defu.ts`: complete target delivery was **0/12**. C skipped 22/24 observations. V1 skipped 24/24. The fixed eligibility result is **false**. This is source-selection failure, not 24 measured native coding failures.

All **72/72 source or exact-passthrough fidelity checks passed**. A current, faithfully quoted file can still be irrelevant. The original task and ordinary agent tools remain available after fallback.

| C reason | Observations |
|---|---:|
| `ambiguous_candidates` | 10 |
| `source_preparation_context_budget_exceeded` | 4 |
| `source_preparation_source_unavailable` | 6 |
| `automatic_verified_source` | 2 |
| `discovery_unavailable` | 2 |

## Time, CPU and uncertainty

C mean local preparation was **72.54% longer than B** and **54.58% longer than V1** in this cohort. No native task time was measured. The paired effects below subtract baseline time from C time; positive is slower. Bootstrap intervals resample 12 task clusters, keeping both repeats together (2,000 seeded draws). They describe this small corpus, not all repositories.

| Comparison | Mean paired difference (s) | Median paired difference (s) | 95% task-cluster interval for mean (s) |
|---|---:|---:|---|
| C_vs_B | +0.882274 | +0.528312 | [+0.334072, +1.415736] |
| C_vs_V1 | +0.740982 | +0.387259 | [+0.403516, +1.141821] |

| Arm | Mean parent CPU (s) | Mean waited preparation child CPU (s), separate |
|---|---:|---:|
| B | 0.720920 | 0.340620 |
| V1 | 0.818246 | 0.419435 |
| C | 1.193451 | 0.759263 |

Parent CPU excludes child work. Waited-child CPU uses the OS counter around approval/index/preparation and includes synchronous Git/parser workers, excluding later audit/native/grading and un-waited children. These are not an exact combined resource total. Local preparation includes cold approval/index, secure refresh and retrieval even on SKIP. Cache state and shared-host scheduling remain uncontrolled.

The second repeat was slower in all three arms. The exact cause is unknown; these timings retain that variation. Tasks share four repositories (often the same repair file), so task-cluster intervals do not capture all repository correlation.

| Arm | Repeat 1 mean (s) | Repeat 2 mean (s) |
|---|---:|---:|
| B | 0.795657 | 1.637016 |
| V1 | 0.891108 | 1.824150 |
| C | 1.469993 | 2.727228 |

## Why selection failed — posthoc diagnosis

The target appeared somewhere in every recorded C candidate list; only **4/24 observations (2/12 tasks)** ranked it first, and 18/24 ranked it within three. Candidate recall did not translate to a correct bundle. These diagnostic cutoffs were inspected after rejection and are not a newly validated policy.

- Broad callers and public API/type vocabulary outranked the actual small helpers. TypeScript type aliases and Python stubs can receive ordinary identifier weight. Both positive selections were type-only source, showing that token rarity and channel agreement do not establish runtime usefulness.
- Six `source_unavailable` observations chose blinker's 19,132-byte broad implementation, above the 12,000-byte complete-file cap, instead of the 1,628–1,668-byte required helper. Current-source/hash checks were valid; this was not evidence of stale files.
- Four budget declines combined hookable's caller, types and helper into 13,822–13,827 raw bytes before JSON overhead. That exceeded the complete-source budget. Removing safety caps or truncating the bundle would conceal the failure.
- Inherited Python signature slices can contain leading body comments, contaminating the supposed declaration channel. Code-body comment exclusion alone does not clean this metadata. `args`/`kwargs`/compound-name vocabulary also poorly matches natural-language requirements.
- Two second-repeat observations returned generic `discovery_unavailable` after ranking but before dependency counters. The aged global two-second metadata-reader budget is a plausible cause when it resumes after parsing; the exact exception was not retained and is **not proven**. Typed phase/error diagnostics remain needed.

The [independent offline audit](evidence/router-v2/audit/independent-offline-audit.json) verified all 72 immutable rows, source/prompt reconstruction, controls and paired statistics; the [posthoc diagnosis](evidence/router-v2/audit/posthoc-selection-diagnosis.json) preserves exact size/ranking observations and uncertainty.

These limitations are not presented as fixed by lowering thresholds. The v2 evidence policy was not tuned or rerun on these exposed tasks. After rejection, only compatibility defaults/help/docstrings and explicit-v2 test fixtures were changed. The frozen study remains reproducible at its original revision.

## Local memory and synthetic profile

A separate 18-observation Python-only development profile used fresh workers, 8/100 files, 2,048 bytes per file and three repeats per arm. All 18 expected target deliveries and full-source fidelity checks passed; all arms added 2,229 bytes. These easier fixtures did not predict held-out usefulness.

| Files | Arm | Mean API preparation (s) | Median (s) | Median whole-process Python SELF peak (MiB) |
|---:|---|---:|---:|---:|
| 8 | B | 0.006933 | 0.007576 | 16.000 |
| 8 | V1 | 0.158092 | 0.084260 | 16.375 |
| 8 | C | 0.096644 | 0.095196 | 16.375 |
| 100 | B | 0.011711 | 0.009345 | 17.125 |
| 100 | V1 | 0.245101 | 0.250512 | 17.500 |
| 100 | C | 0.279699 | 0.261982 | 17.500 |

C's median preparation was slower than V1 at both sizes. The eight-file mean favored C because of V1 variability; it is not a consistent speed improvement. Whole-process RSS includes imports, fixture, index and preparation, not incremental router memory. Child peaks are separate maxima and must not be added to SELF peaks. This Python profile does not measure the TypeScript worker's peak memory. OS/cache/shared-host activity was uncontrolled, including possible overlap with a local analyzer unit check. [All 18 raw observations and worker logs](evidence/router-v2/profile/report.json).

## Native A/B/C, tokens and money

The user authorized the proposed 72 native assignments after disclosure of an **$18.59 estimated API-equivalent planning allowance** (not a billed maximum or hard cap). The preregistered technical gate failed, so **zero were dispatched**. All 72 planned assignments are retained as unrun, 24 per A/B/C. There were no live failures, retries, replacements or selectively dropped tasks. No new backend authentication claim is made.

| Requested metric | New-study observation |
|---|---|
| Strict native completion rate and full task time | Unavailable: no attempted native tasks |
| Input, cache read/write, uncached input, output | Unavailable: no native usage events |
| Model and MCP invocations | Zero native assignments; zero auxiliary selection-model calls; live MCP intentionally outside source-preload treatment |
| Repeated file reads / avoided investigation | Unavailable; not inferred from source size |
| API-equivalent cost per successful task | Unavailable: no strict successes or observed model usage |
| Actual billed charges / savings | Unavailable; no invoice telemetry |
| Context freshness and target-scope proxy | 72/72 treatment fidelity; B 24/24 scope, C 0/24 scope |

Byte/3 added-token estimates remain planning proxies, not model input measurements. Pricing was rechecked against official sources and is preserved with reading scopes, but no dollar saving is calculated from those byte proxies. Cached input economics and cache-write sensitivity matter only when actual usage exists. The administrative [all-unrun record](evidence/router-v2/native-not-started/report.json) and [analysis](router-v2-formal-analysis.md) retain null metrics, missing pairs and zero attempts. They are **not a completed 72-run model benchmark**.

Historical incomplete source-only results (9.055% lower API-equivalent cost, 6.892% shorter mean time in a matched subset) remain in their original reports. They neither prove billed savings nor validate this automatic router.

## Engineering verification and promotion

The frozen full Python run passed **2,033** cases. The later 43-case runner run added six distinct cases; the post-study default rollback passed **324** affected cases with one new compatibility case. The union is **2,040 distinct Python cases**, not one enlarged full-suite run. **24 frontend, three production browser, and 14 separate final clean-wheel smoke checks** passed. Ruff and mypy passed. The smoke includes actual default/agent MCP clients, API/SPA, CLI, optional memory, both explicit policies and the installed native parser from an import-shadowed directory.

Initial development failures and a frontend initial-load timing failure are retained. That frontend case and the complete 24-case suite passed unchanged on rerun; no concrete frontend bug was proven. Existing protected tests/timeouts were not weakened. [Frozen validation](router-v2-validation.md) and [final default-rollback verification](router-v2-final-validation.md).

| Area | Outcome | Evidence / limit |
|---|---|---|
| Known-path complete-source delivery | preserved | 24/24 fresh preparations delivered the declared scope; all source hashes and complete bodies verified. |
| Source safety and exact fallback | preserved within checked scope | All 72 offline treatments passed independent source/passthrough fidelity reconstruction; application/security regressions and installed transports passed. Native task correctness remains unmeasured. |
| Source-controlled identifier normalization | resource defect fixed | Fixed-width boundaries replace quadratic suffix rescanning; compatibility cases and a bounded 500,000-character subprocess regression pass. No model speedup is claimed. |
| Automatic target delivery | failed; not improved | C delivered source on one of 12 tasks in both repeats, but delivered the wrong type-only file; declared target scope was complete on zero tasks. V1 also delivered zero target scopes. |
| Local preparation time | regressed in this cohort | C mean 2.098610s versus B 1.216337s and V1 1.357629s. These are cold local components, not full coding-task times. |
| Local CPU | more observed work | Mean parent CPU C 1.193451s vs B 0.720920s; separate waited-child CPU C 0.759263s vs B 0.340620s. Counters have different scopes and are not an exact total. |
| Synthetic memory and latency profile | no consistent improvement | 18/18 synthetic Python selections/fidelity passed. C preparation medians exceeded V1 at both sizes; whole-process SELF RSS was similar/slightly higher. No real-repository or TS-worker peak-memory result exists. |
| Model tokens, cache, cost per success and full task time | unproven; no native attempts | Offline eligibility failed, so all 72 planned native assignments remain unrun. No invented token or dollar measurements. |
| Automatic warm memory | disabled and unchanged | No new memory injection; existing explicit memory features and installed memory smoke remain available. |

No automatic promotion. Known-path complete source remains the practical existing option when paths are known. Bare Codex remains appropriate when the router lacks reliable task evidence. No improvement in native correctness, time or cost has been demonstrated by this new study.

## Next experiments, in order

1. Local runtime/helper-aware ranking using already indexed AST roles, parameter/alias evidence and bounded caller/callee relationships; distinguish runtime definitions from type-only declarations without excluding types needed by type tasks. Develop on exposed/development cases, then freeze and evaluate NEW issue-only tasks; compare target ranking, bundle delivery, abstention, false inclusions and all local overhead before model spend.
2. Clean signature evidence at actual declaration boundaries, and expose safe typed phase-budget/failure diagnostics. Current inherited signature slices can contain comments; generic discovery_unavailable hides the exact exception. Independent comment-mutation and phase-timeout tests before fresh heldout work. Do not call a likely SQLite deadline cause proven without an observed error counter.
3. Plan bounded complete source bundles around the relevant helper rather than indiscriminate broad callers/import closures; keep all-or-nothing safety where complete bodies exceed caps. Fresh multi-file/large-file tasks with independent dependency grading; no threshold retuning to rescue this cohort, no silent truncation.
4. Evaluate trusted reusable index generations and explicit phase budgets to reduce duplicate cold scan/parse work, preserving authoritative source/policy checks and fallback under uncertainty. Separate cold, warm unchanged, edited, renamed, deleted, ignore-changed, symlink and race cohorts. Measure setup, retrieval, parser/Git child CPU and RSS separately.
5. After a new policy passes fresh offline coverage, run a newly frozen all-task A/B/C comparison with cost per strict success, full time, task-cluster uncertainty and byte-identical controls. New task corpus, matched model/settings, isolated environments, balanced repeats and a separately recorded planning allowance; preserve failed attempts and unknown usage.

## Every offline observation

Times include cold approval/index and preparation. “Scope” is the declared-path proxy. Full source versions, ranking evidence, phase timing, CPU counters and exact fidelity receipts are retained in the accompanying JSON and per-run records.

| Order | Task / repeat | Arm | Decision | Scope complete | Cold prep (s) | Added bytes | Reason |
|---:|---|---|---|---|---:|---:|---|
| 1 | defu-array-precedence / 1 | V1 | SKIP | False | 0.705824 | 0 | weak_lexical_evidence |
| 2 | defu-array-precedence / 1 | C | SKIP | False | 0.885938 | 0 | ambiguous_candidates |
| 3 | defu-array-precedence / 1 | B | preloaded | True | 0.571773 | 2371 | explicit_focus |
| 4 | defu-class-instance-boundaries / 1 | C | SKIP | False | 1.197343 | 0 | ambiguous_candidates |
| 5 | defu-class-instance-boundaries / 1 | V1 | SKIP | False | 0.811800 | 0 | weak_lexical_evidence |
| 6 | defu-class-instance-boundaries / 1 | B | preloaded | True | 0.440070 | 750 | explicit_focus |
| 7 | hookable-observer-snapshots / 1 | B | preloaded | True | 0.647676 | 4054 | explicit_focus |
| 8 | hookable-observer-snapshots / 1 | V1 | SKIP | False | 0.723291 | 0 | weak_lexical_evidence |
| 9 | hookable-observer-snapshots / 1 | C | SKIP | False | 1.177097 | 0 | source_preparation_context_budget_exceeded |
| 10 | blinker-bound-receiver-identity / 1 | C | SKIP | False | 0.711896 | 0 | source_preparation_source_unavailable |
| 11 | blinker-bound-receiver-identity / 1 | B | preloaded | True | 0.491864 | 1913 | explicit_focus |
| 12 | blinker-bound-receiver-identity / 1 | V1 | SKIP | False | 0.559896 | 0 | weak_lexical_evidence |
| 13 | hookable-serial-awaiting / 1 | V1 | SKIP | False | 0.743463 | 0 | ambiguous_candidates |
| 14 | hookable-serial-awaiting / 1 | B | preloaded | True | 1.353100 | 4005 | explicit_focus |
| 15 | hookable-serial-awaiting / 1 | C | SKIP | False | 1.684149 | 0 | ambiguous_candidates |
| 16 | blinker-bound-weak-references / 1 | B | preloaded | True | 0.680274 | 1893 | explicit_focus |
| 17 | blinker-bound-weak-references / 1 | C | SKIP | False | 1.881059 | 0 | source_preparation_source_unavailable |
| 18 | blinker-bound-weak-references / 1 | V1 | SKIP | False | 0.587203 | 0 | weak_lexical_evidence |
| 19 | cachetools-positional-type-tags / 1 | V1 | SKIP | False | 1.262637 | 0 | weak_lexical_evidence |
| 20 | cachetools-positional-type-tags / 1 | C | SKIP | False | 1.348630 | 0 | ambiguous_candidates |
| 21 | cachetools-positional-type-tags / 1 | B | preloaded | True | 1.223952 | 2235 | explicit_focus |
| 22 | defu-nullish-fallback / 1 | C | FOCUSED_SOURCE | False | 1.239281 | 3806 | automatic_verified_source |
| 23 | defu-nullish-fallback / 1 | V1 | SKIP | False | 0.803983 | 0 | weak_lexical_evidence |
| 24 | defu-nullish-fallback / 1 | B | preloaded | True | 0.712077 | 2353 | explicit_focus |
| 25 | cachetools-keyword-order / 1 | B | preloaded | True | 1.407253 | 2253 | explicit_focus |
| 26 | cachetools-keyword-order / 1 | V1 | SKIP | False | 1.337701 | 0 | weak_lexical_evidence |
| 27 | cachetools-keyword-order / 1 | C | SKIP | False | 1.435722 | 0 | ambiguous_candidates |
| 28 | blinker-value-sender-identity / 1 | C | SKIP | False | 0.703961 | 0 | source_preparation_source_unavailable |
| 29 | blinker-value-sender-identity / 1 | B | preloaded | True | 0.397445 | 1933 | explicit_focus |
| 30 | blinker-value-sender-identity / 1 | V1 | SKIP | False | 0.744554 | 0 | weak_lexical_evidence |
| 31 | cachetools-method-receiver-exclusion / 1 | V1 | SKIP | False | 1.291844 | 0 | weak_lexical_evidence |
| 32 | cachetools-method-receiver-exclusion / 1 | B | preloaded | True | 0.721456 | 2267 | explicit_focus |
| 33 | cachetools-method-receiver-exclusion / 1 | C | SKIP | False | 3.905567 | 0 | ambiguous_candidates |
| 34 | hookable-nested-hook-names / 1 | B | preloaded | True | 0.900947 | 4059 | explicit_focus |
| 35 | hookable-nested-hook-names / 1 | C | SKIP | False | 1.469277 | 0 | source_preparation_context_budget_exceeded |
| 36 | hookable-nested-hook-names / 1 | V1 | SKIP | False | 1.121096 | 0 | weak_lexical_evidence |
| 37 | defu-array-precedence / 2 | B | preloaded | True | 1.455628 | 2371 | explicit_focus |
| 38 | defu-array-precedence / 2 | C | SKIP | False | 4.611673 | 0 | ambiguous_candidates |
| 39 | defu-array-precedence / 2 | V1 | SKIP | False | 3.198452 | 0 | weak_lexical_evidence |
| 40 | defu-class-instance-boundaries / 2 | B | preloaded | True | 1.005763 | 750 | explicit_focus |
| 41 | defu-class-instance-boundaries / 2 | V1 | SKIP | False | 3.251528 | 0 | weak_lexical_evidence |
| 42 | defu-class-instance-boundaries / 2 | C | SKIP | False | 5.438714 | 0 | discovery_unavailable |
| 43 | hookable-observer-snapshots / 2 | C | SKIP | False | 2.942899 | 0 | source_preparation_context_budget_exceeded |
| 44 | hookable-observer-snapshots / 2 | V1 | SKIP | False | 1.442974 | 0 | weak_lexical_evidence |
| 45 | hookable-observer-snapshots / 2 | B | preloaded | True | 0.946608 | 4054 | explicit_focus |
| 46 | blinker-bound-receiver-identity / 2 | V1 | SKIP | False | 0.789052 | 0 | weak_lexical_evidence |
| 47 | blinker-bound-receiver-identity / 2 | B | preloaded | True | 4.059847 | 1913 | explicit_focus |
| 48 | blinker-bound-receiver-identity / 2 | C | SKIP | False | 1.181085 | 0 | source_preparation_source_unavailable |
| 49 | hookable-serial-awaiting / 2 | C | SKIP | False | 7.615226 | 0 | discovery_unavailable |
| 50 | hookable-serial-awaiting / 2 | B | preloaded | True | 5.284989 | 4005 | explicit_focus |
| 51 | hookable-serial-awaiting / 2 | V1 | SKIP | False | 3.627946 | 0 | ambiguous_candidates |
| 52 | blinker-bound-weak-references / 2 | V1 | SKIP | False | 2.259648 | 0 | weak_lexical_evidence |
| 53 | blinker-bound-weak-references / 2 | C | SKIP | False | 1.548405 | 0 | source_preparation_source_unavailable |
| 54 | blinker-bound-weak-references / 2 | B | preloaded | True | 1.174073 | 1893 | explicit_focus |
| 55 | cachetools-positional-type-tags / 2 | B | preloaded | True | 2.211041 | 2235 | explicit_focus |
| 56 | cachetools-positional-type-tags / 2 | C | SKIP | False | 2.884797 | 0 | ambiguous_candidates |
| 57 | cachetools-positional-type-tags / 2 | V1 | SKIP | False | 1.884602 | 0 | weak_lexical_evidence |
| 58 | defu-nullish-fallback / 2 | B | preloaded | True | 0.968693 | 2353 | explicit_focus |
| 59 | defu-nullish-fallback / 2 | V1 | SKIP | False | 1.516929 | 0 | weak_lexical_evidence |
| 60 | defu-nullish-fallback / 2 | C | FOCUSED_SOURCE | False | 1.905905 | 3806 | automatic_verified_source |
| 61 | cachetools-keyword-order / 2 | C | SKIP | False | 1.633157 | 0 | ambiguous_candidates |
| 62 | cachetools-keyword-order / 2 | V1 | SKIP | False | 1.675883 | 0 | weak_lexical_evidence |
| 63 | cachetools-keyword-order / 2 | B | preloaded | True | 0.843866 | 2253 | explicit_focus |
| 64 | blinker-value-sender-identity / 2 | V1 | SKIP | False | 0.481428 | 0 | weak_lexical_evidence |
| 65 | blinker-value-sender-identity / 2 | B | preloaded | True | 0.326511 | 1933 | explicit_focus |
| 66 | blinker-value-sender-identity / 2 | C | SKIP | False | 0.646651 | 0 | source_preparation_source_unavailable |
| 67 | cachetools-method-receiver-exclusion / 2 | C | SKIP | False | 1.167240 | 0 | ambiguous_candidates |
| 68 | cachetools-method-receiver-exclusion / 2 | B | preloaded | True | 0.701283 | 2267 | explicit_focus |
| 69 | cachetools-method-receiver-exclusion / 2 | V1 | SKIP | False | 0.965621 | 0 | weak_lexical_evidence |
| 70 | hookable-nested-hook-names / 2 | V1 | SKIP | False | 0.795738 | 0 | weak_lexical_evidence |
| 71 | hookable-nested-hook-names / 2 | C | SKIP | False | 1.150979 | 0 | source_preparation_context_budget_exceeded |
| 72 | hookable-nested-hook-names / 2 | B | preloaded | True | 0.665890 | 4059 | explicit_focus |

## Reproduction and limits

Use the frozen source revision and locked toolchain recorded in `evidence/router-v2/plan/preregistration.json`; regenerate into fresh plan/output directories. The final documentation/default-rollback commit intentionally differs from that frozen HEAD, so the archived plan is a historical record, not a dispatchable plan for an arbitrary later checkout. No model command should be used to bypass the failed eligibility gate. The original corpus controls and complete Git-blob byte checks remain archived.

- Twelve controlled mutation tasks across four complete small upstream snapshots, six Python/six TypeScript; not a random sample or proof about larger repositories. Two repeats are not 24 independent tasks.
- Expected paths are an independent author-declared repair-scope proxy. Scope coverage is not semantic dependency completeness, native correctness, or an assessment that an agent cannot solve the original task after fallback.
- Known-path B is an oracle baseline: manual source discovery effort is unmeasured and excluded. No invented avoided work is credited to C.
- Caches and shared-host scheduling are uncontrolled. Balanced execution order does not establish equivalent provider or OS cache state. Cold setup/preparation excludes fixture/worktree creation, imports, independent reconstruction and grading.
- The local profile uses synthetic Python only. SELF RSS includes interpreter, imports, fixture/index/setup/preparation; child peak is a separate maximum, not simultaneous total or incremental preparation allocation. TS parser peak RSS was not measured.
- The offline runner seals its source manifest before dispatch but has no per-observation/end-of-offline source guard. Operator sequencing and the frozen Git snapshot support this run; they are not an independently timestamped proof of runtime immutability.
- Posthoc ranks and cause analyses were inspected only after the fixed gate failed. These tasks are now exposed and must not be reused as independent confirmation for a changed policy.
- Actual billing, native model telemetry, cost per successful coding task and end-to-end coding latency are unavailable because native execution was not initiated. Historical API-equivalent savings are not transferred to this policy.

[Machine-readable detailed report](router-v2-assessment.json) includes every offline and planned native row, all profile observations and metric summaries. [Evidence ledger](evidence/router-v2/artifact-ledger.json) hashes allowlisted artifacts; no auth, Codex state, runtime databases, dependencies or indexed worktrees are included. Historical reports and raw outcomes are preserved unchanged.
