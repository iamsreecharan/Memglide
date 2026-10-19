# Independent review: local efficiency improved; the warm study is authentication-blocked

The new native warm-memory comparison did **not** complete. Its first original assignment failed during authentication, before any completed model turn; the remaining **215 assignments were not run**. This cohort establishes neither a warm-memory benefit nor a warm-memory regression. Token, cost and successful-task latency comparisons remain unavailable.

This review read the retained [native report](codex-warm-ab.json), its Markdown counterpart, the [offline integrity audit](warm-integrity-audit.json), the [local-efficiency assessment](saas-efficiency-assessment.md) and its component reports. It made no model requests, changed no application or benchmark code, and inspected no credential values. The published native JSON was byte-identical to the original local report at review: SHA-256 `d789402887d599ca8ddf548a3bd24fd87b30edb19052889a5decf4122929e176`.

## What actually ran

| Observation | Result |
| --- | ---: |
| Planned original assignments | 216: 72 per arm |
| Attempted assignments | 1, in C at stage one |
| Assignments not run | 215 |
| Completed model turns | 0 |
| Strict successful tasks / full sequences | 0 / 0 |
| Fully priced native attempts | 0 |
| Prior memory requested / delivered | 0 / 0 |
| Quotes captured | 0 |
| Offline audit checks passed / unavailable | 367 / 25 |
| Complete study coverage | False |

The original failed run is `warm-ts-warm-paths-s1-r1-C`. The native process exited with code 1 and reported: “Your access token could not be refreshed because you have since logged out or signed in to another account. Please sign in again.” The harness recognized the shared authentication blocker and stopped further requests. This is an execution failure, not an observed failure to solve the coding task.

During subsequent recovery, the task owner first observed a proxy failure starting device login, then successfully reached the supported device-login flow. Browser authorization was still awaiting the user at this review update. That improvement establishes device-login reachability, not successful authentication or a completed coding turn, and does not change this cohort's counts. No temporary device code is retained in this report.

The one source-preparation fidelity check passed. There was no prior memory at stage one, so the new memory-reuse behavior was never exercised. There is no observed A/B pair, no observed B/C pair and no measured stage-one B/C prompt-parity control.

The recorded **2.493797863 seconds** of instrumented full wall time and **2.021673350 seconds** of native wall time describe that failed authentication attempt. They are not successful-task latency or evidence that C is faster or slower. The observed local CPU/RSS likewise concern a failing client process. Input, cached input, output, actual inference-call count, complete observed MCP-call count, actual billing and estimated cost per success remain unavailable. A configuration with zero MCP servers is not proof of complete runtime call telemetry after an early failure.

The audit's `passed=true` means its available integrity checks passed; `complete=false` and 25 unavailable checks prevent interpreting it as a completed benchmark. The failed promotion gate reflects missing comparative evidence. It is not a measured rejection of memory performance. The report's “0 / 24 successful / planned sequences” rows must not be presented as 24 evaluated failures per arm.

## What the local evidence does support

The new component results are useful, with narrower scope than model or SaaS efficiency:

- **Unchanged graph refresh:** mean component wall time fell from 0.715832 to 0.631705 seconds, an 11.75% point reduction; graph updates fell from 1,198 to zero per refresh, while both arms still made 600 secure source reads. The baseline emulates the former unconditional resolver branch inside current code, rather than the whole historical application.
- **Unchanged scan allocation:** mean peak Python allocations fell from 21,525,591 to 1,601,119 bytes, a 92.56% reduction in this instrumented fixture. This is `tracemalloc`, not process RSS. Both arms still made 40 secure reads of the 20 MiB source fixture. Graph/scan probes briefly overlapped and host/cache conditions were uncontrolled; keep their timing results separate.
- **Scheduler/dashboard bookkeeping:** the virtual scheduler fixture used 120 to 12 database connections and decoded 68,877,900 to 48 JSON bytes, with the same 75 no-op scan calls. The compared dashboard response stayed equal while event rows fetched fell from 500 to 20. These are bounded bookkeeping observations, not live daemon or native-task speedups.
- **Database tradeoff:** the repeated SQLite probe reduced selected history and foreign-key work, but nine indexes added 839,680 bytes. One event append rose from 44 to 55 VM instructions. VM instructions are neither milliseconds nor tokens, and this is not a measured write-throughput percentage.

The engineering validation receipt reports one complete **1,626-case Python run** and two later recovery cases passing separately: **1,628 distinct verified Python cases**, not a single 1,628-case full run. It also reports 24 frontend and three real Chromium cases, plus separate installed-package CLI/API/SPA/MCP checks. Targeted test totals overlap the full suite and should not be added again. These checks validate the recorded functionality; they do not establish native model savings or hosted production readiness.

The earlier source-only estimated-cost results belong to a different frozen implementation and cohort. Keep their successful and failed runs visible, but do not apply their percentages to these new changes.

## Publication corrections

Replace “native study pending,” “being prepared,” or “no new native outcome” with **“native study attempted and authentication-blocked: one retained failed assignment, 215 unrun; no comparative outcome.”** Put that status before performance tables when sharing the native report. Preserve the original generated report and raw evidence; this review provides the explanatory status without regrading or rewriting them.

The current assessment's reference to a “pending full-suite status” is stale: its own validation receipt records the completed 1,626-case run and two later cases. Update that wording while retaining the initial interrupted fixture failure. State the actual blocker in the public summary, rather than leaving readers to infer it from generic missing-final-output errors.

Keep “no new native benefit established,” “actual billed savings unknown” and “memory remains optional.” Avoid calling either the blocked benchmark or the local component results a completed 216-run comparison, a universal efficiency win or a production-ready hosted SaaS.

## Recovery without replacing the failed original

1. If device login remains denied, publish the saved cloud-environment network change through the supported environment settings workflow. The executor policy snapshot inspected during this review was restricted and did not include `auth.openai.com`; later, the task owner successfully reached device login. Prefer that actual command result over stale or incomplete readiness metadata. A saved draft is not proof of an enforced change, and later reachability does not prove which configuration action occurred. This review made no new login or network request.
2. Complete the pending supported device-login flow in the browser, then check `codex login status` in the intended environment. If that flow expires, initiate `codex login --device-auth` again. Keep credentials in their normal binding; do not copy or publish authentication files, disable TLS verification or bypass the proxy. Do not treat an issued device code as completed authorization.
3. Preserve this blocked cohort and its failed original exactly. After authentication works, start a **new explicitly identified cohort with fresh runtime state and output directory**. Do not retry or replace this cohort's first original, relabel its 215 unrun assignments as attempted, or pool its failure timing with successful-task latency. Any separate authentication preflight must be labelled separately.
4. Freeze the application, corpus, protocol and configuration before that cohort; retain all attempts and grade independently. Run timed native assignments after CPU-heavy engineering checks finish. Compare full-sequence cost per strict successful sequence and mean/median time, including setup, memory capture/retrieval and cleanup. Keep actual billing null unless attributable billing data is obtained.

The defensible current conclusion is that Memglide performs less measured local work while preserving the checked source behavior. Whether its optional memory reduces end-to-end coding cost or time remains unanswered.
