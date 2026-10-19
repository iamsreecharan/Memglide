# Memglide efficiency: complete results and failed-attempt accounting

The application fixes pass their recorded engineering checks. The initial native study failed its strict test-file contract; those failures remain unchanged. A separately frozen confirmation uses ten new tasks with explicit instructions to keep original tests byte-identical and add regressions only in new files.

**A:** standard Codex. **B:** Memglide complete production source. **C:** the same source plus complete caller-selected supporting tests. All arms use the same model/settings and common task, path hints and test-command information. Support remains explicitly optional.

All dollar values below are standard API list-price equivalents from observed native usage, **not actual charges or subscription savings**. Cached input is included in total input; reasoning is included in output. Cache-write uncertainty remains reported.

## Fresh confirmation: 60 assignments

Strict outcomes: A 20/20, B 20/20, C 20/20. There are ten fresh tasks, two repeats and three arms, not sixty distinct tasks. The same application source is used in both studies.

| Arm | Attempts | Strict successes | Estimated USD/success | Mean full seconds | Median full seconds | Mean uncached input | Mean output |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 20 | 20 | 0.0299606 | 20.970 | 19.515 | 9,287.5 | 835.9 |
| B | 20 | 20 | 0.0292192 | 21.196 | 20.431 | 9,114.4 | 806.0 |
| C | 20 | 20 | 0.0305415 | 22.545 | 21.121 | 9,422.0 | 853.9 |

## Focused tasks: controls excluded

These are the eight source-focused tasks repeated twice: 16 assignments per arm. Four provided-context control assignments per arm remain in the primary results above but cannot establish a retrieval benefit.

| Arm | Attempts | Strict successes | Estimated USD/success | Mean full seconds | Median full seconds | Mean uncached input | Mean output |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 16 | 16 | 0.0312153 | 20.222 | 19.515 | 9,907.9 | 837.1 |
| B | 16 | 16 | 0.0280350 | 20.865 | 21.300 | 8,570.9 | 788.1 |
| C | 16 | 16 | 0.0304615 | 22.775 | 21.121 | 9,349.4 | 849.9 |

For C versus standard Codex, focused estimated cost per success is **2.41% lower** and mean full time is **12.63% higher**. Versus source-only B, they are **8.66% higher** and **9.16% higher**. These are observations on this small corpus, not general or actual-billing savings.

Source-only B is the best focused-task point estimate in this confirmation: **10.19% lower estimated cost per successful task** than A, but **3.18% longer mean full time**. Its median time is also longer. This is not a joint cost-and-speed win. Under independent possible cache-write attribution, its focused saving range is **-3.54% to 22.49%**; these are scenarios, not confidence intervals or actual billing.

The support ablation explains the failed promotion. On focused tasks, C reduces recognized read-command items to **0.25/run**, versus B's **1.125/run**, while total completed command items rise to **4.625/run**, versus **3.6875/run**. Fewer reads did not eliminate enough other work. C also has **9,349.375 mean ordinary-input tokens versus 8,570.875** for B, and **849.875 output tokens versus 788.125**. Those more expensive usage categories explain the higher price-equivalent cost arithmetically. The measured local CPU lower bound rises from **5.3303 to 6.7276 seconds/run**; sampled RSS does not rise proportionally. Provider inference counts and the model's internal reasons for its command choices remain unobserved. These observations support retaining support as an explicit option, not automatic expansion.

## Prespecified gate and repeat consistency

Promotion gate passed: **False**. Keep support explicitly optional; do not promote defaults. The policy was frozen before both studies; it requires complete valid original assignments and focused cost/full-time means AND medians no worse than both baselines overall and in each repeat.

- Focused cost/full-time mean or median regresses or is unavailable overall or in a repeat

| Baseline | Scope | Metric | Statistic | Baseline | C | Passed |
|---|---|---|---|---:|---:|---|
| A | overall | native_reported_price_equivalent_usd | mean | 0.0312153 | 0.0304615 | True |
| A | overall | native_reported_price_equivalent_usd | median | 0.0307294 | 0.0292972 | True |
| A | overall | end_to_end_wall_seconds | mean | 20.2220065 | 22.7751005 | False |
| A | overall | end_to_end_wall_seconds | median | 19.5152169 | 21.1214287 | False |
| A | repeat_1 | native_reported_price_equivalent_usd | mean | 0.0354360 | 0.0312673 | True |
| A | repeat_1 | native_reported_price_equivalent_usd | median | 0.0374188 | 0.0292972 | True |
| A | repeat_1 | end_to_end_wall_seconds | mean | 21.1286258 | 22.7834678 | False |
| A | repeat_1 | end_to_end_wall_seconds | median | 21.7628943 | 21.2080493 | True |
| A | repeat_2 | native_reported_price_equivalent_usd | mean | 0.0269946 | 0.0296558 | False |
| A | repeat_2 | native_reported_price_equivalent_usd | median | 0.0240912 | 0.0285226 | False |
| A | repeat_2 | end_to_end_wall_seconds | mean | 19.3153872 | 22.7667332 | False |
| A | repeat_2 | end_to_end_wall_seconds | median | 18.4079036 | 20.5310786 | False |
| B | overall | native_reported_price_equivalent_usd | mean | 0.0280350 | 0.0304615 | False |
| B | overall | native_reported_price_equivalent_usd | median | 0.0248352 | 0.0292972 | False |
| B | overall | end_to_end_wall_seconds | mean | 20.8648100 | 22.7751005 | False |
| B | overall | end_to_end_wall_seconds | median | 21.2996430 | 21.1214287 | True |
| B | repeat_1 | native_reported_price_equivalent_usd | mean | 0.0271542 | 0.0312673 | False |
| B | repeat_1 | native_reported_price_equivalent_usd | median | 0.0248524 | 0.0292972 | False |
| B | repeat_1 | end_to_end_wall_seconds | mean | 22.1841302 | 22.7834678 | False |
| B | repeat_1 | end_to_end_wall_seconds | median | 22.8986553 | 21.2080493 | True |
| B | repeat_2 | native_reported_price_equivalent_usd | mean | 0.0289158 | 0.0296558 | False |
| B | repeat_2 | native_reported_price_equivalent_usd | median | 0.0248352 | 0.0285226 | False |
| B | repeat_2 | end_to_end_wall_seconds | mean | 19.5454897 | 22.7667332 | False |
| B | repeat_2 | end_to_end_wall_seconds | median | 19.9461472 | 20.5310786 | False |

## Why tokens, time and cost can diverge

The current tariff prices ordinary input at $2/M, cached reads at $0.10/M, cache writes at $2.50/M and output at $10/M. One ordinary input token costs as much as twenty cached-input tokens. Reducing cheap cached tokens while increasing ordinary input can therefore raise estimated cost. These component charges show the arithmetic directly.

| Arm | Ordinary-input USD | Cached-read USD | Cache-write USD | Output USD |
|---|---:|---:|---:|---:|
| A | 0.3714980 | 0.0605440 | 0.0000000 | 0.1671700 |
| B | 0.3645760 | 0.0585984 | 0.0000000 | 0.1612100 |
| C | 0.3768820 | 0.0631680 | 0.0000000 | 0.1707800 |

Complete source/support delivery can remove discovery or read commands, but adds first-message source. A common source substring inside a changed native user message does not establish a reusable provider message-ending cache boundary. The installed native CLI exposes no inspected arbitrary multi-message or explicit-breakpoint input surface. Provider/OS caches remain uncontrolled. See the [primary-source research and exact reading scopes](efficiency-research.md).

Completed commands, read-command matches and patch items are proxies; provider model calls and actual filesystem reads are not observable. They cannot be silently relabelled as model-call savings.

| Metric | A mean | B mean | C mean |
|---|---:|---:|---:|
| input_tokens | 39,559.450 | 38,413.600 | 41,006.050 |
| cached_input_tokens | 30,272.000 | 29,299.200 | 31,584.000 |
| ordinary_uncached_input_tokens | 9,287.450 | 9,114.400 | 9,422.050 |
| output_tokens | 835.850 | 806.050 | 853.900 |
| observed_command_items | 3.450 | 3.750 | 4.500 |
| observed_file_read_commands | 0.950 | 1.000 | 0.300 |
| observed_repeated_read_commands | 0.000 | 0.000 | 0.000 |
| total_observed_local_cpu_seconds | 5.282 | 5.403 | 6.380 |
| process_tree_peak_rss_bytes | 267,506,688.000 | 263,587,225.600 | 267,044,659.200 |
| mcp_calls | 0.000 | 0.000 | 0.000 |

Local CPU is a measured lower bound; sampled child RSS omits parent indexing and can double-count shared pages. Cold B/C approval and indexing are included in full time. No fabricated hosting-dollar rate or server-side resource metric is used.

## Original failed study: all 60 attempts preserved

All 60 native executions and treatments were valid, and every external behavior/smoke/type-check command passed. All 60 assignments remain strict failures because existing test files changed. The prompt permitted regression tests while saying to preserve existing tests; it did not state the byte-level prohibition explicitly. We clarified future instructions, retained the strict grader, and used new tasks. No original result was regraded. See the [contract issue](workflow-contract-issue.md), [original report](codex-workflow-ab.md) and [original cost assessment](workflow-assessment.md).

| Arm | Attempts | Strict successes | Estimated USD/success | Mean full seconds | Median full seconds | Mean uncached input | Mean output |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 20 | 0 | unavailable | 19.959 | 19.551 | 12,842.8 | 647.5 |
| B | 20 | 0 | unavailable | 18.766 | 18.191 | 13,362.1 | 602.1 |
| C | 20 | 0 | unavailable | 18.813 | 16.574 | 12,211.0 | 575.5 |

The original promotion gate also failed cost/time checks independently of its correctness failure. The fresh corpus is not a controlled same-task iteration comparison with the original one. Their efficacy and latency outcomes must remain separate.

In the fresh confirmation, every treatment passed independent fidelity checks. The 16 focused B assignments delivered **24 complete file instances**; C delivered **40**, including 16 support-file instances. These are repeated deliveries across task/repeat assignments, not unique repository files. Exact source bodies, line ranges and hashes matched each frozen starting commit. Four provided-context assignments per arm retained the original task unchanged. This verifies completeness of the caller-selected evidence, not global semantic recall across an unfamiliar repository.

## Campaign cost per success: every attempted dollar included

This financial view includes all 120 original assignments, 40 per arm, including all initial protected-file failures. It does not pool task corpora to claim an efficacy or latency gain. Unknown cost would make a complete total unavailable; zero successful assignments yields unavailable cost per success.

| Arm | Attempts | Strict successes | Strict failures | Estimated attempted USD | Estimated USD/success |
|---|---:|---:|---:|---:|---:|
| A | 40 | 20 | 20 | 1.2889548 | 0.0644477 |
| B | 40 | 20 | 20 | 1.2826008 | 0.0641300 |
| C | 40 | 20 | 20 | 1.2474700 | 0.0623735 |

The [campaign JSON](efficiency-assessment.json) retains all 120 tagged original costs and success flags, exact per-study source/report hashes, unknown-cost coverage and possible-write totals. Each native invocation appears once in that financial numerator. Pair views do not add spend.

## Implemented improvements and limits

Exact-reference passport invalidation replaces filename substring matching. Retrieval/passport/event/activity publication is atomic under the active-session gate. Memory selection avoids freshness reads for irrelevant claims while preserving eligible-source validation and ranking. A measured local fixture reduced secure source-reader calls 55→15 with identical selected evidence; 1,200 synthetic selection cases also matched. These are component results, separate from native token/dollar outcomes.

The optional support bundle uses the same approval, current ignore policy, complete-file secure reads, final hashes and shared size cap. Missing/unsafe/changed/oversized evidence produces original-prompt passthrough. Empty support preserves prior bytes and schemas. No model classifier, automatic repository discovery or source-executed test command is added. Resumed/possibly cumulative usage is rejected by cost accounting unless its fresh scope is established. Concurrent pytest invocations use unique temporary directories.

[Engineering validation](efficiency-validation.md) records 1,443 distinct verified cases: the earlier full 1,340 Python/24 frontend/3 browser run and 76 new confirmation-benchmark cases, with unchanged App source. Combined mypy covers 60 modules. Installed CLI/API/SPA and default/agent MCP checks passed. Initial oracle, fixture, type-check and launcher failures remain in evidence.

All native arms intentionally use zero configured MCP calls. This evaluates the source-preload workflow. It does not establish model efficiency for MCP, large production repositories or cross-session memory. Actual billing, provider model-call counts, filesystem reads and server resources remain unknown. Reported zero cache writes can reflect an upstream default; the JSON retains possible-write scenarios, not confidence intervals.

The next useful improvements are supported per-request usage/cache-write telemetry and realistic related-task/large-repository evaluations. Automatic source omission based only on a hash or session ID remains unjustified because compaction may remove retained context. Do not add unmeasured embedding/LLM/graph workers or promote support based on a favorable aggregate.

## Complete individual evidence

- [Fresh confirmation: individual runs, grades and aggregate metrics](codex-workflow-confirmation.md)
- [Fresh confirmation: every estimated run cost, means, medians, p95, failures and pair/stratum data](workflow-confirmation-assessment.md)
- [Original 60 runs](codex-workflow-ab.md) and [all original costs](workflow-assessment.md)
- [Fresh protocol](workflow-protocol-v2.md), [original protocol](workflow-protocol.md), [architecture](../docs/efficiency-architecture.md), and [downloadable full bundle](memglide-efficiency-report.zip)
