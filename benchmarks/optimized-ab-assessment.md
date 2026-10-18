# Optimized Codex A/B assessment

**The optimized Memglide configuration did not reduce total tokens, execution time or local resource use versus standard Codex on this fresh synthetic corpus.** All 80 attempts in each arm passed external grading. Across 80 verified pairs, B used **32.82% more total input tokens**, **5.31% more output tokens** and **17.88% more Codex-plus-index time**. Derived uncached input increased **2.17%** overall. Actual charges and cost per successfully completed task remain unavailable.

The [primary Markdown](codex-ab-optimized.md) and [primary JSON](codex-ab-optimized.json) retain every individual run, command/result reference, status and missing field. The [assessment JSON](optimized-ab-assessment.json) adds nearest-rank p95, complete coverage statistics, paired ratios/deltas and language/repeat/repository/order strata. The [frozen protocol](optimized-ab-protocol.md) was set before the fresh tasks were run through Codex.

## Protocol and verification

A is standard Codex. B uses the opt-in compact Memglide profile with `fetch_context` required before editing and `verify_context` available on demand. The regular fourteen-tool interface remains compatible. Both arms use `gpt-6.1-sol`, `low` reasoning effort, native `codex-cli 0.159.2`, the same structured output schema, prompts, workspace sandbox and per-repository starting commits. Frozen application commit `62e07cc98855b4cdde255395372e5d78b3a7e2a1` and source digest `5e867d309e0a24a3e52f15a1e40b837dc7a228074380a4aaa3b1419b989856f3` stayed unchanged.

The 40 task IDs cover 20 Python and 20 TypeScript tasks across four new purpose-built repositories. These tasks were excluded from retrieval tuning and development model pilots. They remain synthetic, share repository families and represent 40 tasks with correlated repeats, not 160 independent tasks. Sixteen tasks include separately graded domain and public-API defects. Source/reference-fixture validation is separate from model success.

Each attempt starts in an isolated detached worktree; B receives a fresh index, private session and database with no accepted prior memories. This measures retrieval integration and its overhead. It does not establish persistent cross-task or cross-process memory benefits. Arm order reverses per task on the second repeat. OS/provider caches cannot be reset; cached usage and order strata are retained.

| Original outcomes | A | B |
| --- | ---: | ---: |
| Planned / attempted | 80 / 80 | 80 / 80 |
| Completed CLI runs | 80 | 80 |
| External grader passes / all attempted | 80/80 (100%) | 80/80 (100%) |
| Graded-only pass rate | 100% | 100% |
| Verified intended treatment | 80/80 | 80/80 |
| Failed / invalid / ungraded / not run | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |

All 160 original attempts and 80 pairs were retained. There were no resumptions, retries or supplemental attempts in this campaign. External graders check requested behavior, public-API cases where specified, unchanged smoke tests, protected files/Git metadata and TypeScript compilation. No correctness advantage appears at this observed 100% success ceiling.

Before formal execution, 596 Python tests, 24 frontend tests and three production Chromium workflows passed: **623 distinct application and tooling checks**. A separate [independent native-stream/evidence audit](evidence/optimized-ab-independent-audit.md) ([JSON](evidence/optimized-ab-independent-audit.json)) passed **9,480 assertions**, reproducing the 160 outcomes, 80 paired comparisons, source/protocol identities and hash-chained records. Those audit assertions are not additional application tests. The [process-completion record](evidence/optimized-ab-process-completion.json) found no recorded native process still running. Re-executing the saved audit requires its documented original local artifacts; the copied reports are provenance evidence, not a self-contained replay environment.

## Actual usage and execution measurements

All reported token, timing and total-process resource metrics below have 80 observations per arm with no missing values. B-specific setup/MCP resources have 80 B observations; their A counterparts are unavailable because A has no Memglide process/setup. Means, medians and p95 are descriptive. P95 is the nearest rank, `ceil(0.95*n)` in sorted observations, without a confidence interval.

| Metric | A mean / median / p95 | B mean / median / p95 |
| --- | ---: | ---: |
| CLI total input tokens | 62,881.350 / 64,608.500 / 79,777.000 | 83,520.200 / 89,638.000 / 107,342.000 |
| CLI cached input tokens | 50,595.200 / 49,408.000 / 72,192.000 | 70,968.000 / 71,296.000 / 93,696.000 |
| Derived uncached input tokens | 12,286.150 / 13,912.000 / 25,989.000 | 12,552.200 / 9,483.000 / 19,323.000 |
| CLI output tokens | 1,422.525 / 1,346.500 / 2,068.000 | 1,498.013 / 1,415.500 / 2,128.000 |
| Codex process time (s) | 27.296 / 26.255 / 35.968 | 31.970 / 30.564 / 42.352 |
| Codex + fresh index time (s) | 27.296 / 26.255 / 35.968 | 32.178 / 30.841 / 42.453 |
| Sampled local process-tree CPU (s) | 5.354 / 4.925 / 7.820 | 7.739 / 7.235 / 11.550 |
| Sampled process-tree peak RSS (MiB) | 269.521 / 263.373 / 332.508 | 352.161 / 335.926 / 410.227 |
| Memglide CPU subset (s) | unavailable / unavailable / unavailable | 1.979 / 1.905 / 2.580 |
| Memglide peak RSS subset (MiB) | unavailable / unavailable / unavailable | 68.845 / 68.832 / 69.156 |
| Fresh-index wall time (s) | unavailable / unavailable / unavailable | 0.208 / 0.194 / 0.368 |
| Fresh-index parent-process CPU (s) | unavailable / unavailable / unavailable | 0.070 / 0.057 / 0.147 |
| Read-command intent proxy | 1.137 / 1.000 / 2.000 | 1.050 / 1.000 / 2.000 |
| Repeated-read-command intent proxy | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |

| Additive metric | A complete total | B complete total |
| --- | ---: | ---: |
| Total input tokens | 5,030,508 | 6,681,616 |
| Cached input tokens | 4,047,616 | 5,677,440 |
| Derived uncached input tokens | 982,892 | 1,004,176 |
| Output tokens | 113,802 | 119,841 |
| Codex + index seconds | 2,183.713 | 2,574.230 |
| Actual MCP invocations | 0 | 80 |

Cached input is a subset of total input and must not be added to it. Derived uncached input subtracts cached input after validating the observed fields. The much smaller uncached-input difference does not establish a monetary benefit: verified prices and provider invoiced charges are absent. Both actual and verified-price computed **cost per successful task remain null**, with 80 externally successful runs in each denominator and all 80 attempted costs required in each numerator. No unavailable cost is replaced with zero.

There are **160 task CLI invocations**, not a measured count of underlying model/API calls. The complete native event streams record **80 successful `fetch_context` calls** in B, zero MCP calls in A and no tool failures. `verify_context` was never used, consistent with its on-demand policy; this does not validate its live model use or make a claim about final-edit chronology.

Codex-plus-index time excludes worktree preparation, post-exit auditing, independent grading and report writing. The readiness request is separate from task comparisons. `/proc` sampling gives CPU lower bounds and RSS peaks that can miss short-lived processes and count shared pages more than once. Memglide is already inside total process-tree resources. Index setup has separately measured wall and parent-process CPU; its peak RSS and parser-worker CPU are unavailable.

Observed read-command fields are narrow command-intent proxies. They omit internal, MCP, script and directory reads and cannot establish actual or exact repeated filesystem I/O. The native stream records 336 command items in A and 331 in B (4.200 versus 4.138 per attempt), alongside the 80 added B MCP calls. Ordinary command workflows continued; the net five-command difference does not establish causal replacement or savings.

## Matched outcomes and mixed signals

Ratios divide the sum of matched B observations by the sum of matched A observations. For peak RSS this is the ratio of paired means, not a cumulative memory total. Mean/median individual B/A ratios and all missing counts are retained separately in JSON.

| Metric | Mean B − A | B/A ratio | B lower / equal / higher |
| --- | ---: | ---: | ---: |
| Total input tokens | 20,638.850 | 1.32822 | 8 / 0 / 72 |
| Cached input tokens | 20,372.800 | 1.40266 | 7 / 0 / 73 |
| Uncached input tokens | 266.050 | 1.02165 | 31 / 0 / 49 |
| Output tokens | 75.487 | 1.05307 | 26 / 0 / 54 |
| Codex time (s) | 4.674 | 1.17123 | 11 / 0 / 69 |
| Codex + index time (s) | 4.881 | 1.17883 | 10 / 0 / 70 |
| Local process CPU (s) | 2.384 | 1.44532 | 6 / 0 / 74 |
| Peak process RSS (MiB) | 82.639 | 1.30662 | 1 / 0 / 79 |

B used less total input in 8/80 pairs and less uncached input in 31/80. It was faster including indexing in 10/80 pairs. These individual wins remain visible alongside the worse overall results. Sampled local CPU increased 44.53% and peak RSS means increased 30.66%; this experiment shows no local-overhead benefit versus standard Codex.

| Paired stratum | Pairs | Input B/A | Uncached B/A | Output B/A | Codex + index B/A |
| --- | ---: | ---: | ---: | ---: | ---: |
| language: python | 40 | 1.424 | 1.076 | 1.049 | 1.187 |
| language: typescript | 40 | 1.245 | 0.977 | 1.057 | 1.171 |
| repeat: 1 | 40 | 1.293 | 1.008 | 1.055 | 1.192 |
| repeat: 2 | 40 | 1.364 | 1.037 | 1.052 | 1.165 |
| repository: config-typescript-v2 | 20 | 1.185 | 0.955 | 1.045 | 1.160 |
| repository: ledger-python-v2 | 20 | 1.415 | 1.040 | 1.038 | 1.200 |
| repository: stream-typescript-v2 | 20 | 1.311 | 1.002 | 1.070 | 1.183 |
| repository: workflow-python-v2 | 20 | 1.434 | 1.112 | 1.061 | 1.173 |
| arm_order: A_first | 40 | 1.318 | 0.938 | 1.066 | 1.205 |
| arm_order: B_first | 40 | 1.339 | 1.108 | 1.041 | 1.154 |

TypeScript, the configuration repository and A-first strata show lower aggregate uncached input in B, while other strata increase. Total input and execution time increase in every listed stratum. Cache composition, ordering, task complexity and inference variability can affect these signals; the descriptive strata do not isolate their causes or establish significance. Full means, medians, p95, totals and coverage for language/repeat/repository/first-or-second-position groups are in JSON.

## Context, body coverage and freshness

The [actual compact-context analysis](codex-optimized-context.md) and [JSON](codex-optimized-context.json) find declared target-file coverage in 80/80 B responses and **160/160 complete declared body observations**, with zero incomplete or ineligible body observations. Each task declares two symbols, and repeated observations are correlated. Independent Python AST or the narrow TypeScript fixture scanner compares bodies with immutable starting Git blobs only when the returned file hash matches that baseline. This is evidence of those specific complete bodies, not arbitrary helper or semantic completeness. A exposes no Memglide responses and receives no invented quality score, so this does not establish a retrieval-quality advantage over A.

The average fetch returned 11.825 distinct paths for two declared target files, with mean/median canonical JSON sizes of 9,846.563/10,080 bytes. Other paths may contain useful tests, helpers or configuration; they are not all judged irrelevant. Server assertions were `Partial` in 80/80, `Current` in 80/80 and truncated in 77/80. Complete declared bodies can coexist with broader omissions. These are response bytes and server assertions, not billed tokens or independent live freshness measurements.

Independent hash audits were captured after each Codex process exited and before grader mutations. Across the 80 applicable B audits there were 793 matching returned/post-exit file hashes, 112 mismatches and 41 excluded/unknown non-source observations. All 112 mismatches named files in both exported tracked-change patches and Git status, confirming correspondence with the run's edits without reconstructing exact mutation times. Unknown paths were `tsconfig.json` (15), `package.json` (15), `README.md` (8) and `AGENTS.md` (3), excluded by the source snapshot policy. The 80 A records are explicitly not applicable. These own-edit mismatches are not automatically retrieval or coding failures. A later match establishes equality only at that later observation. **Exact live call-time freshness and semantic completeness remain unavailable.**

All 80 fetches completed after or interleaved with at least one observable command start. Commands can read or change source, so this is not a complete mutation timeline. Twelve B read-command intents mentioned 14 paths returned by an earlier fetch. A subsequent read may obtain additional or changed content; these overlaps do not establish redundant reads or actual filesystem I/O.

## Research, pilots and historical comparisons

The [research record](optimization-research-v2.md) retains 22 primary-source citations. [Development body/packing measurements](compact-quality-v2.md) and [local component measurements](optimization-component-v2.md) examine smaller responses, complete declared bodies and implementation work. Those bytes and local timing experiments are separate from measured model usage. The approximately 51.8% development-response byte reduction does not mean 51.8% fewer model tokens.

Both old-task development pilots passed grading and still used more total input and more time in B. They were excluded from the fresh 40-task campaign; neither trial was hidden.

| Old-task pilot | A input | B input | A Codex seconds | B Codex seconds | Policy |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 48,469 | 71,132 | 18.914 | 24.799 | mandatory_final |
| 2 | 48,601 | 71,063 | 17.272 | 22.004 | on_demand |

The earlier 24-task V1 results use a different corpus and protocol. Comparing their token or timing ratios with this campaign cannot establish a causal optimization effect. This experiment compares the frozen optimized treatment with standard Codex on the new corpus; it does not isolate which individual code or protocol change helped or hurt. All historical negative results remain separate evidence.

## Observed causes and next steps

B adds one compact tool interaction, connection startup and tool schema exposure. Its fresh indexing averages 0.208 seconds, much smaller than the 4.881-second matched Codex-plus-index gap, so index setup alone cannot explain the whole observed delay. The usage stream does not assign token counts to schemas, source payloads, history or reasoning. Startup, the extra model/tool interaction and overlapping context are plausible mechanisms, not separately measured causal contributions.

Priorities for another frozen evaluation:

1. Isolate schema, startup, extra-round-trip and payload effects with preregistered ablations. Use actual usage, completion and full cost coverage as outcomes.
2. Reduce overlapping source/metadata while retaining complete primary and direct-helper bodies, source safety and visible freshness limits. Recheck quality on independent repositories.
3. Test warm indexes and explicit accepted memories across related tasks, separating cold setup from recurring work and preventing answer leakage.
4. Include larger unfamiliar repositories and harder multi-step tasks to avoid the observed 100% grading ceiling. Freeze each new corpus before model runs and retain every negative result.
5. Obtain reliable pricing or provider charges before making monetary claims, including every attempted cost in cost per success.

The application passes its tested local workflows and the compact tools were actually delivered. On this corpus, the measured results support further refinement, not a token, speed, local-resource, monetary or coding-success advantage over standard Codex.
