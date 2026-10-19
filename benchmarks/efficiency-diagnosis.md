# What the frozen traces say about Memglide efficiency

This is a read-only secondary analysis of **140 original runs** from three different cohorts: daily80, cache40 and cost20. The cohorts have different tasks and treatment definitions. They must stay separate; they are not a controlled architectural improvement curve. No native model request or grader was rerun. Historical reports and traces remain unchanged.

The latest cost regression is not caused by recognized redundant focused-source reads: **B already avoids those reads in every focused task**. The remaining work is repository/test investigation and edit orchestration, combined with large and incompletely controlled cache variation. Removing tests or skipping required source/security checks would weaken the result.

| Cohort | A / B | Passing runs | Mean input A / B | Mean uncached A / B | Mean output A / B | Full seconds A / B |
|---|---|---:|---:|---:|---:|---:|
| daily80 | Standard Codex / Memglide legacy suffix | 40 / 40 | 48,580.35 / 47,151.90 | 8,532.35 / 10,847.90 | 865.85 / 812.60 | 21.58 / 20.56 |
| cache40 | Memglide legacy suffix / Memglide compact prefix | 20 / 20 | 50,076.75 / 49,071.30 | 13,769.55 / 14,306.50 | 790.75 / 742.60 | 29.69 / 26.37 |
| cost20 | Standard Codex / Memglide compact prefix | 10 / 10 | 47,315.50 / 47,149.70 | 13,907.50 / 13,920.90 | 807.10 / 716.90 | 26.48 / 24.20 |

The pooled latency and output signals are favorable in each cohort. They do not establish causal savings: byte-identical controls also differ substantially, and the largest cache-format timing pair supplies about 59.55% of that experiment’s net time reduction. All outliers remain in the original and secondary results.

| Focused tasks only | daily A / B | cache-format A / B | cost A / B |
|---|---:|---:|---:|
| Runs | 32 / 32 | 16 / 16 | 8 / 8 |
| Recognized focus-read command items | 32 / 0 | 0 / 0 | 8 / 0 |
| Command items | 135 / 127 | 64 / 67 | 33 / 33 |
| File-change items | 33 / 37 | 18 / 21 | 8 / 13 |
| Discovery command items | 36 / 32 | 16 / 16 | 9 / 8 |
| Test-file-read command items | 32 / 32 | 16 / 16 | 8 / 8 |
| Native test-command items | 32 / 32 | 16 / 16 | 8 / 8 |

An observed command item can contain several shell commands. An observed file-change item can update several files. Neither count is the number of provider model calls, and no per-phase token cost is inferred from them. File-read mentions are conservative command-intent proxies, not an I/O trace.

In the latest eight focused cost tasks, both arms issue **33 command items**. B eliminates source-file reads but still discovers files and reads smoke tests in all eight. B emits **13 file-change items versus A’s eight**. For example, the edge-touch B run changes production source, adds a regression file, then corrects that file before running tests. The aggregate trace supports batching safe independent inspection and related edits as a hypothesis; it cannot prove one patch would produce a particular token saving.

Cost focus command output drops from **2,892 to 1,896 bytes per run**, while input rises from **48,645 to 50,076 tokens**. Smaller tool output is useful, but does not ensure a lower accumulated model input bill. Total input also reflects how often context is processed, prompt content and native workflow; cached versus uncached categories have different prices.

The latest B source envelope averages **771 bytes**, of which **536 bytes** are exact focused source. The remainder includes notice, paths, JSON framing and escaping. Frozen smoke tests average **1,020.5 bytes**, so preloading all tests indiscriminately could increase the prompt substantially. A combined package must be bounded, caller selected, complete, and shown to remove subsequent work rather than merely add context.

Within byte-identical provided-source controls, uncached B-minus-A spans **−11,265 to +11,337** tokens in daily80 and **−11,675 to +10,913** in cache40. The two cost controls differ by −8,387 and −1,007. Workflows can also differ in these controls. Cache residency/routing and provider request detail are unavailable; the trace cannot assign these differences to a single prefix or cache-key cause.

The existing cost report remains authoritative for dollar estimates: the source-preloaded stratum costs **4.43% more**, while the two identical-prompt controls create the pooled **2.28% lower** estimate. These are API-price equivalents, not bills. Native cache-write zero can represent an upstream default, and the existing possible-write sensitivity range remains. No actual cost or hosting rate is invented.

All 140 assignments pass their fixed external requirements, protected files remain unchanged, and no observed native command item exits nonzero. Regression tests added by the models differ in count and coverage. Passing this suite establishes these tasks only. None of these three cohorts invokes native MCP; none tests cross-session memory or demonstrates benefits from the full retrieval architecture.

The next implementation should preserve the current complete-source security/freshness boundary and API compatibility, and target these specific mechanisms:

1. Offer caller-selected, bounded test context alongside source so one safe local acquisition can replace separate source/test investigation. Keep whole-file completeness, ignore/secret checks, approval and all-or-nothing fallback. Prove the package eliminates real subsequent work before making it automatic.
2. Add a small optional workflow hint to batch independent inspection and related edits while still running required tests and checking other/newer source. Do not suppress repository instructions or hide failures.
3. Evaluate bounded explicit-file approval separately from cold full indexing; do not implicitly grant access or add a model classifier. Measure local overhead separately from model usage.
4. Test native same-thread continuation and related cross-session work under matched history rather than spoofing cache identities or assuming source prefix reuse across distinct files.
5. Use repeats, byte-identical controls and predeclared success/cost/latency checks. Keep every outlier and failure. Do not route by task kind based on four examples per stratum.

The JSON includes all 140 rows, every pair, arm/stratum summaries, paired directions, timing sensitivity, primary-report hashes and individual event-stream hashes. It records only observed telemetry; unavailable provider calls, actual reads and actual billing stay unavailable.
