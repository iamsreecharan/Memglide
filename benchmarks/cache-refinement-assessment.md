# Fresh legacy/compact-prefix format comparison: assessment

**Uncached input is not fixed.** Across 20 fresh matched tasks, compact-prefix used **3.90% more uncached input** than legacy. All 40 assignments passed. Aggregate total input fell 2.01%, output 6.09% and full execution time 11.16%; **money savings remain unproven**.

The aggregate input decrease comes from four supplied-context controls whose forwarded task bytes were identical. In the 16 pairs that actually received the alternative source layouts, compact-prefix input rose **0.63%** and uncached input rose **1.53%**. These descriptive results do not demonstrate a native cache benefit from the new layout.

## Scope and identity

A is **Memglide legacy task-suffix**; B is **Memglide compact-prefix**. Neither is bare Codex. Both use Codex **0.159.2**, `gpt-6.1-sol`, low reasoning effort, matched common task instructions, explicit focus paths, starting commits and native options. The source layouts intentionally change the actual preloaded model prompts. Supplied-context pairs forward identical prepared-prompt hashes.

The frozen implementation is `94998bba69a52cb95b25c52fa3747a422cd715e5`; all 24 application Python files have aggregate source hash `e777cbd53a1ca6228e5c3403ebb5cc3547834a00edac1d1f20210342740aeee4` before and after the experiment. Twenty tasks were authored after both formats were fixed: ten Python and ten TypeScript, eight single-source, eight integration and four supplied-context cases, in four small purpose-built repositories. One repeat gives 20 pairs and 40 original assignments.

Relevant source is only **89–632 UTF-8 bytes per task**; the preloaded subset is 118–632 bytes. All 20 tasks have distinct focus sets. This measures fresh known-file utility fixes; it does not directly test repeated tasks over unchanged identical files, large unfamiliar repositories, persistent memory or cross-session cache sharing.

## Complete descriptive measurements

Values below are **A → B**. Percentage change is the ratio of arm means, not the mean of paired ratios. Every observed measurement covers 20/20 assignments per arm; unavailable telemetry remains unavailable. RSS is non-additive, so no total is reported. The [primary Markdown](codex-cache-formats.md) and [JSON](codex-cache-formats.json) preserve every run, exact values, paired differences, coverage and failures.

| Metric | Mean A → B | B change | Median A → B | p95 A → B | Total A → B | Observed A / B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Total input tokens | 50,076.7500 → 49,071.3000 | -2.01% | 48,625 → 48,321 | 63,106 → 62,375 | 1,001,535 → 981,426 | 20/20 / 20/20 |
| Cached input tokens | 36,307.2000 → 34,764.8000 | -4.25% | 35,136 → 34,880 | 48,640 → 48,896 | 726,144 → 695,296 | 20/20 / 20/20 |
| Uncached input tokens | 13,769.5500 → 14,306.5000 | +3.90% | 13,544 → 13,454 | 25,258 → 25,519 | 275,391 → 286,130 | 20/20 / 20/20 |
| Output tokens | 790.7500 → 742.6000 | -6.09% | 799 → 725.5000 | 1,013 → 1,064 | 15,815 → 14,852 | 20/20 / 20/20 |
| Launcher/process seconds | 29.4036 → 26.1428 | -11.09% | 27.5426 → 26.3483 | 39.1689 → 33.0940 | 588.0712 → 522.8559 | 20/20 / 20/20 |
| Full execution seconds | 29.6856 → 26.3733 | -11.16% | 27.6685 → 26.6990 | 39.4917 → 33.4491 | 593.7124 → 527.4653 | 20/20 / 20/20 |
| Native interval seconds | 29.0887 → 25.8486 | -11.14% | 27.2936 → 26.1135 | 38.9138 → 32.5955 | 581.7747 → 516.9717 | 20/20 / 20/20 |
| Approval/index seconds | 0.2479 → 0.2177 | -12.17% | 0.2033 → 0.1919 | 0.5870 → 0.4770 | 4.9575 → 4.3541 | 20/20 / 20/20 |
| Approval/index CPU seconds | 0.0597 → 0.0604 | +1.20% | 0.0616 → 0.0508 | 0.1169 → 0.1207 | 1.1943 → 1.2086 | 20/20 / 20/20 |
| Preparation seconds | 0.0740 → 0.0748 | +1.00% | 0.0682 → 0.0669 | 0.1354 → 0.2204 | 1.4808 → 1.4956 | 20/20 / 20/20 |
| Preparation CPU seconds | 0.0705 → 0.0716 | +1.46% | 0.0626 → 0.0657 | 0.1291 → 0.2130 | 1.4107 → 1.4313 | 20/20 / 20/20 |
| Sampled child RSS bytes | 268,895,027.2000 → 265,621,094.4000 | -1.22% | 267,644,928 → 260,048,896 | 335,212,544 → 315,559,936 | unavailable → unavailable | 20/20 / 20/20 |
| Sampled child CPU seconds | 7.7500 → 6.3065 | -18.63% | 7.3600 → 6.0300 | 15.8500 → 8.8700 | 155 → 126.1300 | 20/20 / 20/20 |
| Observed local CPU seconds | 7.8097 → 6.3669 | -18.47% | 7.4275 → 6.0896 | 15.9646 → 8.9346 | 156.1943 → 127.3386 | 20/20 / 20/20 |
| MCP calls | 0 → 0 | unavailable | 0 → 0 | 0 → 0 | 0 → 0 | 20/20 / 20/20 |
| Underlying model calls | unavailable → unavailable | unavailable | unavailable → unavailable | unavailable → unavailable | unavailable → unavailable | 0/20 / 0/20 |
| Actual repeated file reads | unavailable → unavailable | unavailable | unavailable → unavailable | unavailable → unavailable | unavailable → unavailable | 0/20 / 0/20 |
| Read-command proxy | 0.9500 → 0.8500 | -10.53% | 1 → 1 | 1 → 1 | 19 → 17 | 20/20 / 20/20 |
| Repeated-read-command proxy | 0 → 0 | unavailable | 0 → 0 | 0 → 0 | 0 → 0 | 20/20 / 20/20 |
| Actual billed USD | unavailable → unavailable | unavailable | unavailable → unavailable | unavailable → unavailable | unavailable → unavailable | 0/20 / 0/20 |
| Price-equivalent USD | unavailable → unavailable | unavailable | unavailable → unavailable | unavailable → unavailable | unavailable → unavailable | 0/20 / 0/20 |

A and B each completed **20/20** successfully with independent passing behavior/smoke grades, validated treatment and valid native framing/schema. There were no formal failures, timeouts, interruptions, retries, supplemental assignments or unrun slots. Successful completion and behavior-grade counts are separate, with every original assignment retained.

Cached input is a subset of total input. The exact arithmetic is `−20,109 total − (−30,848 cached) = +10,739 uncached` tokens. Cached share fell **72.50% → 70.85%**. Mean uncached input rose 536.95 tokens; its paired median difference was +35.5 tokens.

B total input was lower in **14/20** pairs, uncached input in **10/20**, output in **11/20** (one tie), full time in **15/20**, observed local CPU in **13/20** and sampled RSS in **14/20**. The largest time reduction, the consecutive-run-groups pair, contributes 39.449 of the net 66.247 seconds (59.55%). It remains included. A single repeat and variable native work/cache reuse limit generalization.

Actual billed cost, applicable price-equivalent cost, cost per successful task and underlying model-call counts remain **null**. All attempted costs would enter the numerator, including failures if present; 20 successful tasks form each denominator. No token-to-dollar estimate is substituted.

## Selection and order controls

| Descriptive stratum | Pairs | Input mean A → B | Input change | Uncached mean A → B | Uncached change | Full seconds mean A → B | Time change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Explicit focus / source prepared | 16 | 51,469.1875 → 51,793.8125 | +0.63% | 14,949.1875 → 15,177.8125 | +1.53% | 31.8951 → 28.1823 | −11.64% |
| Caller context already supplied | 4 | 44,507 → 38,181.25 | −14.21% | 9,051 → 10,821.25 | +19.56% | 20.8476 → 19.1372 | −8.20% |

Both formats bypass all source/state work in the supplied-context stratum and add zero bytes. Its **+19.56% uncached** change and **−14.21% total input** change occur despite identical forwarded task bytes. They demonstrate that byte identity does not hold observed native usage or provider reuse constant. The focused stratum's +5,194 total-input tokens is outweighed by controls' −25,303 tokens. These strata are descriptive; subtracting controls would not establish a causal adjusted effect.

Each task has adjacent A/B executions; the sequence alternates AB and BA, ten pairs of each. Each order contains eight focused and two supplied-context pairs. B uncached input was **−3.63% in A-first pairs** and **+12.22% in B-first pairs**. Different task subsets and stochastic execution prevent attributing this difference to order alone.

Every assignment uses fresh worktree, native local state and Memglide database. Required cold project approval/index work is included for preloads and bypassed for supplied-context cases. Provider and OS caches are uncontrolled; counterbalanced order and actual cached-token telemetry expose some variation without proving equivalent cache conditions.

## What improved, and what remains a hypothesis

The 16 preloads per format deliver the same **24 complete files / 6,602 raw source bytes**. Compact-prefix additions total **10,426 bytes**, versus legacy's **15,118**: a real **4,692-byte / 31.04% envelope reduction**. Canonical sorted path/content JSON and a short untrusted-source notice precede the exact original task. Full hashes and line ranges remain private; the launcher validates the complete source envelope and exact task bytes. Approval, ignore policy, byte limits and current source/policy hash rechecks remain in place. An all-or-nothing fallback forwards the task unchanged if complete requested source cannot fit.

That establishes fewer forwarded bytes and stable leading bytes when the same unchanged source is reused. It does not convert bytes to native tokens, prove provider receipt/attention or establish a cache hit. The new corpus does not exercise the same-file reuse condition needed to directly measure that proposed prefix advantage.

The [research review](cache-refinement-research.md) pins official Codex 0.159.2 client functions and the official OpenAI caching notebook, with exact access/reading scopes in [JSON](cache-refinement-research.json). Static-before-variable guidance supports the layout. Native session-affinity logic shows why identical supplied text cannot guarantee sharing across fresh sessions. The recorded runs do not reveal actual backend keys, selected affinity branches, routing or retention; assigning the measured regression to any one of them would be an unproven causal claim. Selected functions/blocks were read, not the entire native client.

The earlier legacy experiment independently showed uncached changes of **+75.20%** and **−11.42%** across repeats even though all 20 prepared-prompt hashes matched. Together with fresh identical-byte controls, this supports a limited finding of unstable observed cache reuse. It does not support a reliable classifier that predicts cache benefit from task or source size.

Read-command proxies total **19 → 17**; repeated-read-command proxies are zero in both arms. These are heuristic command-intent observations, not actual filesystem I/O or a guaranteed lower bound. Native MCP invocation counts are zero. Deterministic preparation adds no auxiliary model, embedding or reranking call; underlying native provider calls remain unknown. No stale-source cache, prompt padding, spoofed session ID or invented cache-key flag is used.

## Validation and preserved history

The [independent v2 audit](evidence/cache-formats-v1/audit/formal-independent-audit-v2.json) passed **5,138 assertions**, with zero errors or notes, covering all 40 attempts and 20 verified pairs. The [v1 failure](evidence/cache-formats-v1/audit/formal-independent-audit-v1.json) is preserved: its exact-command expectation reversed the two option groups `--context-format` and `--mode auto`, causing 40 auditor mismatches. V2 corrects the expected order to match the frozen runner and every recorded command; no check was suppressed and no model assignment or metric was rerun or replaced.

[988 distinct application/tooling tests passed](cache-refinement-validation.md): **961 Python, 24 frontend and 3 production Chromium**, with zero failures, errors or skips. Ruff, formatting, mypy, wheel/sdist checks and clean installed API/CLI checks passed. All 24 runtime Python files and 19 compiled assets match the tested wheel. Twelve additional installed functional assertions and two trusted fake native executions are smoke checks, not additional test cases or model measurements.

Full execution time includes cold approval/index, preparation/launcher and native execution, excluding worktree creation and independent grading. Preparation is contained within launcher/process time; do not add it again. Observed CPU includes parent approval/index CPU plus sampled child CPU. Child CPU is a lower bound; sampled RSS excludes the parent indexer, can miss short-lived children and can double-count shared pages. No remote inference CPU/RAM is exposed.

The [80-run legacy comparison](codex-ab-daily.md) and its [assessment](daily-ab-assessment.md) remain unchanged, attached to frozen legacy commit `6f4b6f6`: bare Codex versus legacy Memglide, all 80 passed, total input −2.94%, uncached +27.14%, full time −4.76%. It has different arms, corpus, repeats and execution time from this format comparison. **27.14% → 3.90% is not a controlled estimate of an iteration gain.**

## Recommendation

Keep source preloading an **experimental opt-in** and preserve explicit `off`, caller-context-supplied and missing-focus/project bypasses. The wrapper defaults to compact-prefix when invoked; the Python preparation API and historical runner preserve legacy compatibility. Compact formatting is defensible as a smaller exact-source envelope, while cache and cost benefits remain unproven.

Do not introduce another model to classify cache benefit or weaken freshness checks to improve a metric. A next targeted evaluation should use repeated tasks over unchanged same files with matched independent histories, retain all attempts and measure total/cached/uncached usage, full time and independent success. Fresh-session and same-session results must stay separate; sharing A/B history would contaminate the comparison.
