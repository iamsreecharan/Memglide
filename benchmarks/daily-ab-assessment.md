# Frozen 20-task Codex comparison: assessment

**All 80 runs passed, but money savings remain unproven.** Memglide used 2.94% less total input and 6.15% less output, and took 4.76% less full execution time. It also used **27.14% more uncached input**, and total input was higher in 25 of 40 paired comparisons. These are mixed descriptive results on a narrow corpus.

This measured the legacy source-suffix launcher frozen at `6f4b6f6`, before later compact-prefix refinements. A was native Codex without Memglide; B used local source preparation. Both used `gpt-6.1-sol`, low reasoning effort, identical task prompts/focus hints and starting commits, isolated worktrees, one native process per run, and zero configured MCP calls. B actual prompts deliberately added source; common task prompts were matched, not actual model prompts.

Twenty fresh tasks span ten Python and ten TypeScript cases in four small purpose-built repositories: eight single-source, eight two-source integration and four supplied-context cases. Two repeats produced 40 A/B pairs. B delivered 32 full bundles and bypassed eight supplied-context assignments. Complete relevant source ranges from 148 to 1,372 bytes; this is a known-file utility microbenchmark.

## Primary results

| Metric | A mean | B mean | B change | A median | B median |
| --- | ---: | ---: | ---: | ---: | ---: |
| Total input tokens | 48,580.350 | 47,151.900 | -2.94% | 48,222.500 | 48,524.000 |
| Cached input tokens | 40,048.000 | 36,304.000 | -9.35% | 43,392.000 | 36,800.000 |
| Uncached input tokens | 8,532.350 | 10,847.900 | +27.14% | 5,609.500 | 10,254.000 |
| Output tokens | 865.850 | 812.600 | -6.15% | 895.500 | 855.500 |
| Full execution seconds | 21.583 | 20.557 | -4.76% | 22.803 | 20.866 |
| Approval/index seconds | 0.000 | 0.170 | Unavailable | 0.000 | 0.148 |
| Observed local CPU seconds | 5.040 | 4.968 | -1.43% | 5.075 | 4.698 |
| Sampled child RSS MiB | 243.547 | 238.614 | -2.03% | 249.748 | 245.428 |

A and B each completed 40/40 successfully. Since every assignment passed, mean token usage equals tokens per successful task here. Actual billed cost, price-equivalent cost and actual cost per successful task are **null for both configurations**. Their numerator would include failed attempts if present; no token-to-dollar estimate is presented.

Total input was 1,943,214 → 1,886,076; cached input 1,601,920 → 1,452,160; uncached input 341,294 → 433,916; output 34,634 → 32,504. Cached input is part of total input. The uncached increase is exactly `−57,138 − (−149,760) = +92,622`. Cached share fell from about 82.44% to 76.99%.

B total input was lower in 15/40 pairs and higher in 25/40; median paired difference was **+182.5 tokens**. B output was lower in 32/40 and full time was lower in 28/40. The aggregate mean gain does not describe every task. See the [primary Markdown](codex-ab-daily.md) and [JSON](codex-ab-daily.json) for every run, averages, medians, p95, totals, measurement coverage, failures and paired/selection strata.

## What the traces establish

The read-command proxy fell from 47 to 33; repeated-read-command proxies were zero in both arms. A [separate corrected diagnostic](daily-read-diagnostics.md) fixes shell-newline parsing: three B source-path mentions were git-diff operands, not production-source reads. The corrected trace recognizes no reads of B’s supplied production paths. Remaining read commands generally concern tests, repository rules and package files. This is a command-intent heuristic, never actual filesystem I/O.

Uncached input varied strongly by repeat: B was +75.20% in repeat one and −11.42% in repeat two even though every prepared prompt hash matched its other repeat. Byte-identical supplied-context controls still showed a +3.72% aggregate uncached difference. The frozen traces do not expose backend routing, eviction or per-inference cache keys. They do not support a reliable cache-benefit classifier from task size alone or a causal claim that redundant production reads caused the regression.

Source preparation itself uses no auxiliary model, embedding, reranker or MCP decision call. Underlying Codex model-call counts remain unavailable. Whole task time counts B’s cold approval/indexing, launcher and native execution; worktree creation and independent grading are excluded consistently. Parent indexing CPU is included; child CPU is a sampled lower bound and child RSS excludes parent-indexer memory and may double-count shared pages.

## Verification and limitations

All 80 original assignments completed with valid native event framing, supported structured output and independent behavioral/smoke tests. There were no failed, timed-out, interrupted, retried, supplemental or unrun formal assignments. An independent audit passed **9,884 assertions** plus 80/80 supplemental framing checks, reconstructing B stdin from frozen Git source. [Raw evidence](evidence/daily-ab-v1/manifest.json) preserves every native event stream, grade, patch and source handoff record.

[817 application/tooling tests passed](daily-validation.md) before the experiment. Pre-formal failures and fixes—corrupt-policy fallback, early-exit grading false passes, strict completion denominators, native schema/framing and resume integrity—are retained separately. They are not concealed formal failures or extra successes.

Provider and OS caches cannot be reset or proven equivalent. Counterbalanced order and actual cached-input usage limit, but do not eliminate, that uncertainty. Both configurations already solve every case, so this corpus demonstrates no success-rate advantage. No large unfamiliar-repository, cross-session memory, warm-index or universal efficiency claim is justified.

The earlier 40-task MCP experiment remains unfavorable and unchanged. It used a different treatment and corpus, so comparing its percentage with this one is not a controlled estimate of iteration gains. Original requested engineering articles and full scientific papers were blocked: 0/5 originals and 0/5 full papers read. [Official alternate reviews](daily-engineering-research.md) and [memory/repository code review](daily-memory-research.md) give exact access and reading scopes.

## Refinement after this frozen experiment

Compact, deterministic source-before-task packing removes model-visible hashes/ranges while retaining private verification and complete current code. This reduces avoidable bytes and can extend a shared forwarded prefix when unchanged files serve different tasks. It cannot force provider cache hits, and this original experiment does not measure that version. Fresh matched format tests and their outcomes must be reported separately. Keep explicit supplied-context/off gates and do not introduce another model to predict cache benefit.
