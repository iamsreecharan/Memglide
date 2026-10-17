# Memglide refinement assessment

The local application checks pass, and component measurements show lower observed MCP workflow time. Retrieval is still incomplete on some tasks. **No coding-task, billed-token or monetary benefit versus standard Codex has been established:** the live provider preflight returns HTTP 401, leaving all 96 planned coding runs unrun.

The [JSON evidence index](refinements.json), [detailed final Markdown](refinement-final-results.md) and [detailed final JSON](refinement-final-results.json) retain individual observations, means, medians, p95, failures, source hashes and limitations. The final application source digest is `20cc181bc45cecacc6e96f40e4a470112dd1581212eac7acece46c44f7270454`.

## Changes and application verification

- Context/passport requests load one defensive settings snapshot. Serialization work is reduced while live source safety/hash checks remain. Exact JSON budget estimates and next-request settings visibility have regression coverage.
- Lexical ranking separates generic workflow prose from task behavior, retains acceptance criteria and explicit references, and recognizes implementation/test/documentation requests. Level 2 focuses recognized task roles on four primary files while preserving anchors and dependency expansion. Unclassified inspection queries and broad requests bypass that cap; omissions remain visible.
- Memory mutations, active-session validation, TTL refreshes and events commit atomically. Expiration cleanup cannot delete a concurrently renewed session. Ended-session event history remains readable without extending TTL. Settings reject invalid JSON type coercions.
- Dashboard mutations retain their original targets across selection changes and cleanup. Session creation rechecks the current project after asynchronous refresh. Memory drafts, error handling and modal keyboard focus have regression coverage.
- A/B comparisons reject missing or mismatched commit/prompt identities and source changes. Missing telemetry remains unavailable.

**376 Python tests, 24 frontend tests and three production Chromium workflows passed: 403 distinct checks**, without counting repeat executions twice. Python includes 69 security/storage cases, real STDIO MCP coverage of all 14 tools, transport, lifecycle, indexing, context and benchmark-harness checks. Frozen installation/lock verification, Ruff format/check, mypy, strict TypeScript and the production build passed. Distribution checks and exact commands are recorded in [validation](validation-refined.md) and its [JSON](validation-refined.json).

Pre-fix lifecycle races, frontend regressions, query-role failure and selector failures remain in [evidence](evidence/). The four independent selector regressions failed before the guard fix and then passed; [proof](evidence/selector-guard-proof.json) retains both executions. An initial query-test temporary-directory setup error is also retained separately. These diagnostic failures are not model coding outcomes.

## Retrieval quality and the failed first candidate

The previously used Atlas development tasks selected the refined ranking: target-file hit@1 was 12/24, versus shipped ranking 6/24 and legacy 8/24; reciprocal rank was 0.7500, 0.4597 and 0.5453. All three retained target/declaration coverage. [All three development trials](refinement-final-results.md) remain available; these are seen tuning data.

The first locked Meridian evaluation used 24 new task IDs across four domains and Python/TypeScript repositories with at least 85 files each. Three policies and two repeats produced 144 valid observations. The two languages mirror twelve intents; repeats are correlated. Frozen old ranking/query modules share the current packer, so this is a ranking comparison, not three complete historical applications.

That [first fresh result](refinement-retrieval.md) exposed a selection regression: four matching documentation files could exclude available implementation bodies. Synthetic file basenames could also become false declaration anchors. The [diagnosis](evidence/refinement-initial-diagnosis.md) found all 48 declared direct-call edges correctly resolved; selection and budget competition were the main issues.

We corrected those narrow guards with independently authored regression fixtures and replayed the same locked queries. **The follow-up is [reused validation](refinement-replay.md), not a new unseen evaluation.** Ranking was not retuned after the first result. Refined and shipped ranking have identical quality on these inspection prompts; the new ranking heuristics do not activate there.

| Refined policy, same 24 task IDs | First fresh candidate | Guard-fix replay |
| --- | ---: | ---: |
| Complete primary body | 16/24 | 24/24 |
| Complete declared helper bodies | 20/48 | 39/48 |
| Primary plus both helpers complete | 8/24 | 15/24 |
| Target file ranked first | 8/24 | 8/24 |
| Mean returned files | 10.250 | 16.625 |
| Mean JSON bytes | 17,568.75 | 22,904.13 |
| Packing median / p95, seconds | 0.1885 / 0.3171 | 0.2207 / 0.3247 |

Seven tasks gained complete declared-body coverage, with no refined-policy body-coverage regressions in this replay. **Nine tasks still lack a required helper.** More returned evidence increases bytes and median packing time. Body inclusion only covers declared fixture expectations; it does not establish semantic completeness or successful coding.

The legacy tradeoff is retained prominently: it initially supplied all bodies in 11/24 tasks, outperforming the first refined candidate's 8/24. Under the guard-fix common packer it falls to **0/24**, with dependency recall falling from 30/48 to 8/48 and mean returned files rising to 20.333. The safety change does not improve every ranking policy. Every observation and legacy regression remains in the reports.

## Actual SDK measurements

The final official-SDK client completed 24 isolated seven-call workflows: **168 actual MCP calls**, all target/declaration and controlled-edit freshness checks passed. This is independent of Codex; configured B treatment is not counted as observed model tool use.

| Metric, 24 observations per version | Shipped baseline mean / median / p95 | Final mean / median / p95 |
| --- | --- | --- |
| Startup, initialize and list tools (s) | 3.535 / 3.187 / 5.023 | 1.687 / 1.688 / 2.335 |
| First natural context request (s) | 1.069 / 0.862 / 2.539 | 0.342 / 0.324 / 0.478 |
| Whole seven-call workflow (s) | 8.247 / 7.908 / 13.150 | 3.297 / 3.127 / 4.514 |
| Sampled local server CPU (s) | 7.804 / 7.205 / 12.360 | 3.057 / 2.890 / 4.080 |
| Sampled peak RSS (bytes) | 84,048,384 / 82,808,832 / 89,575,424 | 80,957,952 / 81,221,632 / 87,810,048 |
| Returned source files | 14.083 / 14 / 15 | 8.667 / 8 / 13 |

These historical-versus-current observations match fixture commits, prompts and retrieval settings, but do not control host load or operating-system/provider caches. They establish observed local differences, not a causal speedup, statistical significance or model savings. All eight individual SDK regression observations are retained. Exact symbol identity remains 4/24 despite declarations being visible in 24/24, because class/file snippets can contain a declaration without its exact symbol identity.

A separate [counterbalanced direct experiment](context-performance.md) preserved full response equality in nine pairs and reduced mean request time in its three cases. It measured the earlier settings/serialization stage, before final ranking/selection changes. Its natural-request median worsened, and one natural pair became slower in wall time and CPU. Actual settings SELECTs fell from 75 to one; secure `read_source` calls stayed at 86. These are instrumented function/SQL calls, not exact filesystem I/O or model read telemetry. Exact measured source snapshots and all slower rows are retained.

## Codex A/B and unavailable measurements

The [latest Codex report](codex-ab-refined.md) and [JSON](codex-ab-refined.json) retain all **96 planned slots**: 24 tasks × two configurations × two repeats. Native `codex exec --json` and `--output-schema` are implemented with identical commits/prompts/model settings, isolated worktrees, counterbalanced ordering, external grading, and MCP invocation verification. The readiness request failed before coding with HTTP 401. It preceded the final guard fix; unchanged authentication was not retried merely because local selection changed.

| Requested model measurement | Actual availability |
| --- | --- |
| Input, cached input, output tokens | Unavailable; no completed coding runs |
| Provider-billed cost and cost per successful task | Unavailable; never replaced with zero or a context-size estimate |
| Underlying model/API calls | Unavailable from the supported stream |
| Actual Codex B MCP invocation | Unverified; no B coding run executed |
| Coding success rate and paired task-test results | Unavailable; unit/reference-fixture results are separate |
| Exact repeated file reads | Unavailable; command intent and component function calls are separate proxies |
| Local MCP CPU/RSS, context bytes, hashes and timing | Measured separately by the SDK/component experiments above |

Cost per successfully completed task would include unsuccessful attempts' actual costs in the numerator. With no observed coding outcomes or billing, it cannot be calculated. **No token-saving or money-saving claim is supported.**

## Remaining work

Prioritize complete primary-plus-direct-helper bundles ahead of overlapping documentation, distinguish direct-helper requests from broad caller searches, and reduce unrelated-module budget competition. Validate those changes on newly authored independent repositories before claiming general quality gains. Current safety guards preserve broader inspection evidence; they do not guarantee that every useful helper fits.

Refresh the managed environment's Codex authentication to run the live comparison. The earlier device-login attempt was blocked by the HTTP destination policy before issuing a device code; `auth.openai.com` and `chatgpt.com` were saved in the environment draft but saving does not apply/publish that draft. Preserve the supplied proxy, CA trust and credential binding. A successful login-status message alone is insufficient; the actual readiness request must complete.

All 50 recorded baseline benchmark artifacts and the initial refinement stage remain unchanged, with [baseline](evidence/refinement-baseline-preservation.json) and [stage-one](evidence/refinement-stage1-preservation.json) preservation manifests. Nothing is deployed or published as a package by these checks.
