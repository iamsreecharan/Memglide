# Authenticated Codex A/B assessment

**Memglide did not provide a measured benefit on this task corpus.** In 47 verified pairs, B used **2.751× total input tokens**, **1.405× output tokens** and **1.465× Codex-plus-index time** compared with A. Every graded attempt passed in both configurations; no correctness advantage was observed. Actual charges and cost per successfully completed task remain unavailable.

The [primary Markdown](codex-ab-authenticated.md) and [primary JSON](codex-ab-authenticated.json) preserve all 96 individual attempts. This [assessment JSON](live-ab-assessment.json) adds complete statistics, nearest-rank p95 and language/repeat/order strata. The [raw-evidence manifest](evidence/live-ab-v1/manifest.json) identifies retained events, commands, grading and changes. Earlier authentication-blocked and component reports remain historical evidence.

## Protocol and interruption

A is standard Codex; B uses the same `gpt-6.1-sol` model, `low` reasoning effort, structured output schema, prompts and workspace sandbox with scoped Memglide MCP enabled. Native `codex-cli 0.159.2` emitted JSONL usage/tool events. Each attempt started in a fresh worktree at the same per-language seed commit. Application commit `12ade2381b25412fff41a3348aadf34a8c824715` and source digest `20cc181bc45cecacc6e96f40e4a470112dd1581212eac7acece46c44f7270454` stayed unchanged.

The 24 task IDs are twelve mirrored Python/TypeScript maintenance intents in two small synthetic repositories. They were already used as Atlas ranking-development data. This is a frozen live-agent comparison on seen tasks, not a new held-out benchmark. Two repeats are correlated. Each B attempt received a fresh index with no prior session or memories, so persistent memory reuse is untested.

Arm order was counterbalanced per task and reversed on repeat two. OS/provider caches could not be reset. An exec-server transport disconnect interrupted order 90 (`ts-lru-eviction-r2-B`) before `get_context` and independent grading. Its partial evidence remains in the primary report; no usage, elapsed time, exit code or CPU was reconstructed. Orders 91–96 resumed unchanged after a pause. Original in-memory campaign metadata was also lost; the recovery record distinguishes retained prelaunch/source evidence from later host observations.

| Outcome, all attempted runs | A | B |
| --- | ---: | ---: |
| Planned / attempted | 48 / 48 | 48 / 48 |
| Completed CLI runs / externally graded passes | 48 / 48 | 47 / 47 |
| Interrupted, ungraded | 0 | 1 |
| Grader passes / all attempted | 48/48 (100%) | 47/48 (97.917%) |
| Grader passes / graded only | 48/48 (100%) | 47/47 (100%) |
| Verified intended MCP treatment | 48/48 | 47/48 |

The lower all-attempt B completion rate includes a harness interruption, not an established model or application defect. External graders exercise target-task behavior, unchanged visible smoke tests, protected files/Git metadata and TypeScript compilation. They do not prove arbitrary repository correctness.

## Usage and local execution measurements

Means, medians and p95 use observed values only. The denominator shows telemetry coverage among all 48 attempts per arm. P95 is the nearest rank, `ceil(0.95*n)` in ascending observations; these are descriptive statistics without confidence intervals. CLI input includes cached input; cached input is a subset and must not be added to total input. Uncached input below is the validated arithmetic difference.

| Metric | A observed | A mean / median / p95 | B observed | B mean / median / p95 |
| --- | ---: | ---: | ---: | ---: |
| CLI total input tokens | 48/48 | 54,826.312 / 48,864.500 / 75,435.000 | 47/48 | 150,408.936 / 143,169.000 / 174,811.000 |
| CLI cached input tokens | 48/48 | 41,144.000 / 36,224.000 / 56,576.000 | 47/48 | 121,344.000 / 113,152.000 / 150,016.000 |
| Derived uncached input tokens | 48/48 | 13,682.312 / 13,976.000 / 25,716.000 | 47/48 | 29,064.936 / 29,957.000 / 44,612.000 |
| CLI output tokens | 48/48 | 1,032.812 / 987.000 / 1,352.000 | 47/48 | 1,439.532 / 1,415.000 / 1,839.000 |
| Codex process time (s) | 48/48 | 24.005 / 23.071 / 42.035 | 47/48 | 34.650 / 33.906 / 42.100 |
| Codex + fresh index time (s) | 48/48 | 24.005 / 23.071 / 42.035 | 47/48 | 34.843 / 33.994 / 42.209 |
| Sampled total local CPU (s) | 48/48 | 5.232 / 3.990 / 19.620 | 47/48 | 9.939 / 8.250 / 14.270 |
| Sampled process-tree peak RSS (MiB) | 48/48 | 243.287 / 262.578 / 311.957 | 47/48 | 360.904 / 346.062 / 412.855 |
| B Memglide CPU subset (s) | 0/48 | unavailable / unavailable / unavailable | 47/48 | 4.003 / 3.430 / 7.220 |
| B Memglide peak RSS subset (MiB) | 0/48 | unavailable / unavailable / unavailable | 47/48 | 78.917 / 72.801 / 85.941 |
| B fresh-index time (s) | 0/48 | unavailable / unavailable / unavailable | 47/48 | 0.193 / 0.185 / 0.326 |
| Read-command intent proxy | 48/48 | 1.292 / 1.000 / 2.000 | 48/48 | 1.500 / 1.000 / 2.000 |
| Repeated-read-command intent proxy | 48/48 | 0.042 / 0.000 / 0.000 | 48/48 | 0.042 / 0.000 / 0.000 |

| Additive usage | A full 48-run total | B known 47-run subtotal | B full 48-run total |
| --- | ---: | ---: | ---: |
| Total input tokens | 2,631,663 | 7,069,220 | unavailable |
| Cached input tokens | 1,974,912 | 5,703,168 | unavailable |
| Uncached input tokens | 656,751 | 1,366,052 | unavailable |
| Output tokens | 49,575 | 67,658 | unavailable |

B has larger input, cached input and output in every verified pair. More cached input does not imply fewer tokens or lower cost: the uncached component also increased. All 47 observed B streams plus the interrupted partial stream contain **260 observed MCP calls**. The 47 complete B streams contain 258 calls; the full 48-attempt count remains unknown. A has zero MCP calls in all 48 complete streams. B has 78 successful `get_context` calls across 47 runs, independently verifying treatment delivery.

Full underlying model/API call counts, provider invoiced cost and verified-price computed cost are unavailable. Completed CLI turns are not model-call counts. **Actual cost per successful task is null for both arms:** the numerator must include every attempted cost, including failed/interrupted attempts, and those costs are not exposed. The excluded readiness request reported 10,945 input, zero cached and 42 output tokens; it is retained separately rather than attributed to coding tasks.

Codex-plus-index time excludes worktree preparation, external grading and report generation. `/proc` CPU is an observed lower bound; RSS can double-count shared pages and miss short-lived peaks. Memglide is already part of the total process tree and must not be added again. Setup CPU excludes parser-worker CPU. Read-command counts omit MCP, internal, directory and script reads; the interrupted stream contributes only its partial observed command count. Exact repeated filesystem I/O remains unavailable.

## Matched comparisons

The interrupted pair is excluded from resource deltas, leaving 47 verified pairs; all 96 attempts remain in unconditional outcomes. Ratios below divide the sum of matched B measurements by the sum of matched A measurements. This differs from averaging individual B/A ratios. RSS compares matched means and is not a cumulative memory total.

| Metric | Matched A mean | Matched B mean | Mean B − A | Ratio B/A | B lower / equal / higher |
| --- | ---: | ---: | ---: | ---: | ---: |
| Total input tokens | 54,674.681 | 150,408.936 | 95,734.255 | 2.751 | 0 / 0 / 47 |
| Cached input tokens | 40,815.660 | 121,344.000 | 80,528.340 | 2.973 | 0 / 0 / 47 |
| Uncached input tokens | 13,859.021 | 29,064.936 | 15,205.915 | 2.097 | 1 / 0 / 46 |
| Output tokens | 1,024.872 | 1,439.532 | 414.660 | 1.405 | 0 / 0 / 47 |
| Codex time (s) | 23.779 | 34.650 | 10.871 | 1.457 | 3 / 0 / 44 |
| Codex + index time (s) | 23.779 | 34.843 | 11.063 | 1.465 | 3 / 0 / 44 |
| Local CPU (s) | 5.034 | 9.939 | 4.905 | 1.974 | 3 / 0 / 44 |
| Peak process RSS (MiB) | 242.741 | 360.904 | 118.163 | 1.487 | 0 / 0 / 47 |

B was slower in 44/47 pairs and faster in three. Pair-ratio summaries, deltas, medians and p95 remain in the assessment JSON. No statistical significance or causal production speedup is claimed.

| Paired stratum | Pairs | Input B/A | Output B/A | Codex + index B/A | Mean time B − A (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| language: python | 24 | 2.907 | 1.423 | 1.446 | 10.940 |
| language: typescript | 23 | 2.603 | 1.387 | 1.487 | 11.192 |
| repeat: 1 | 24 | 2.616 | 1.377 | 1.399 | 10.087 |
| repeat: 2 | 23 | 2.897 | 1.434 | 1.543 | 12.082 |
| arm_order: A_first | 23 | 2.784 | 1.396 | 1.436 | 10.269 |
| arm_order: B_first | 24 | 2.721 | 1.413 | 1.493 | 11.825 |
| execution_phase: original_orders_1_to_90 | 44 | 2.745 | 1.397 | 1.458 | 10.972 |
| execution_phase: resumed_orders_91_to_96 | 3 | 2.846 | 1.525 | 1.584 | 12.408 |

All-attempt language, repeat, first/second-position and interruption-phase strata, including ungraded outcomes and missing counts, are in JSON. Resume strata contain only three pairs and cannot isolate a pause effect. Repeats/languages share intents, and ordering does not remove provider/OS-cache confounding.

## Retrieved context and freshness

The [live context report](codex-live-context.md) and [per-call JSON](codex-live-context.json) retain 158 context/passport invocations: 78 `get_context`, 76 `get_context_passport` and four `expand_context`. Two expansions omitted the required `session_id` argument and failed. These model tool-argument mistakes are retained; they are not demonstrated application failures. Of the 156 available tool results, 80 contain source-context responses. These include the declared target file in 80/80 and a visible expected declaration in 78/80. Each of 47 B run unions contains both, while the interrupted B run has no source response and receives no invented zero-size or freshness score.

Available responses carry 109 `Partial` and 47 `Stale` passport assertions; source-freshness assertions are 109 `Current` and 47 `Stale`. These are server reports, not independently verified live hashes at the exact call time. Complete primary/helper bodies and semantic retrieval completeness remain unknown. Target/declaration proxies do not prove what evidence the model relied on. The 80 returned source responses contain 766,532 canonical JSON bytes and 246,824 snippet UTF-8 bytes; duplicates are included and these byte counts are not model tokens or transport bytes.

## Supplemental retry

The [separate retry](codex-ab-authenticated-supplemental.md) and [JSON](codex-ab-authenticated-supplemental.json) passed external grading with verified MCP treatment. It took 40.415 seconds for Codex (40.656 with indexing), reporting 142,207 input, 111,872 cached-input and 1,832 output tokens. Its actual campaign attempt was 97, despite retaining original task/order identity 90. It has no new A comparator, contributes to none of the primary totals/rates/pairs and does not replace the interrupted row. All 24 task IDs already had at least one observed B grader pass in the primary experiment; the original primary outcome remains 47/48.

## Causes and improvements

Observed B behavior added discovery/session/context/passport interactions while ordinary source-reading commands continued. Mandatory protocol steps, schemas, overlapping response metadata and repeated context are plausible contributors to higher token use on these small tasks. The usage stream does not attribute tokens to those causes, so their individual contributions are hypotheses. Fresh indexing averaged 0.193 seconds, much less than the 11.063-second paired time gap; index setup alone cannot explain it. Two failed expansions added work, but their isolated effect is unavailable.

Prioritize these follow-ups and test each on a newly authored frozen corpus:

1. Return compact primary-plus-direct-helper evidence and passport references; avoid repeating unchanged source and metadata. Preserve complete bodies and stale detection while measuring actual CLI usage.
2. Reduce discovery round trips and clarify required expansion arguments. Counterbalance protocol variants instead of assuming that a shorter tool response saves money.
3. Test warm project indexes and explicit accepted memories across related tasks as separate experiments with matched cache conditions.
4. Use larger unfamiliar repositories and harder multi-step tasks to avoid the current graded-success ceiling. Judge complete helper bodies, precision and freshness independently.
5. Persist timing/process metadata incrementally and test interrupted/resumed campaigns; retain original failures and keep retries separate.
6. Obtain verified pricing or provider invoiced costs and calculate cost per success using every attempted cost before making monetary claims.

Current evidence supports local application functionality and measured retrieval delivery. It does not support token, latency, money or coding-success improvements versus standard Codex on this benchmark.
