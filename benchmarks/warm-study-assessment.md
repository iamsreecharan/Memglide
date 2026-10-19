# Warm-memory study: blocked by authentication

The 216-assignment comparison was launched against frozen commit `58ba0545187dbfb5270df246109bb81295718063`. **The first original failed authentication before any completed model turn; the remaining 215 assignments were not run.** No warm-memory token, latency, completion-rate or cost benefit has been established. Actual billing and API-price-equivalent totals remain unavailable, not zero.

## Planned comparison and capability

The frozen [protocol](warm-protocol.md) uses 12 three-task sequences, six Python and six TypeScript repositories, three arms and two repeats: 216 original assignments. A has bare Codex tools, B adds focused current source, and C adds quotations actually produced by its earlier tasks. All arms request the same paid structured findings output. C pays preparation, memory writing, source verification and cleanup; capture never uses hidden grading outcomes. Each stage begins at the same author-frozen canonical commit across arms, independently of earlier model success. Independent behavioral tests and protected-file checks grade every attempted solution. All six arm orders are balanced, with fresh worktrees/state/databases and reversed order in repeat two. Provider and OS caches remain uncontrolled.

The [real capability check](warm-memory-prerequisite.md) passed nine checks: memory survives a service restart and fresh agent processes **only while the same Memglide session remains active**. A fresh Memglide session inherits no memories. Ended/expired sessions cannot be restored; preparation does not renew TTL. Source changes invalidate citations. The defaults remain 60 minutes idle and eight hours absolute. This supported same-day workflow is narrower than durable cross-session memory.

The small synthetic repositories do not establish behavior on large unfamiliar codebases. All three arms configure zero MCP servers. B and C call production Python preload services; A has bare Codex tools. MCP functionality was validated separately. They do not measure native MCP efficiency or full CLI launcher startup. Full instrumented time includes independent treatment audits, while native time is reported separately.

## Observed outcome

| Observation | Result |
| --- | --- |
| Planned assignments | 216 (72 per arm) |
| Attempted | 1: C, TypeScript paths, stage 1, repeat 1 |
| Native failure | Exit 1, authentication refresh failure; no timeout |
| Completed native turns | 0 |
| Unrun | 215 |
| Warm stages attempted / quotations captured | 0 / 0 |
| Input, cached input, output tokens | Unavailable |
| Model calls, actual bill, estimated cost per success | Unavailable |
| Valid A/B/C efficacy comparison | Unavailable |

The exact native error was:

> Your access token could not be refreshed because you have since logged out or signed in to another account. Please sign in again.

`codex login status` had reported “Logged in using ChatGPT”; that local status did not establish backend authorization. The failed native process took 2.022 seconds; instrumented full time was 2.494 seconds. Those timings describe a failed authentication attempt, not coding-task or product latency. External grading ran on the unchanged intentionally buggy baseline: the two held-out checks failed, while six existing smoke tests and the type check passed. That is retained evidence, not a solution-quality result.

The [raw Markdown](codex-warm-ab.md) and [JSON](codex-warm-ab.json) retain every planned row, original error, grading artifact and unavailable value. They are byte-for-byte copies of the generated reports. A raw parity flag of false means no matched pair was observed here; it does not establish a prompt mismatch. Likewise `not_prepared` describes unrun rows, not measured fallback failures.

## Independent audit and decision

The offline [integrity audit](warm-integrity-audit.md) passed **367 checks**, with **25 unavailable checks** and **complete coverage false**. It verifies plan retention, the original launch records, source identity, failure evidence and conservative accounting. An integrity pass is not an efficacy pass. Neither cost per successful task nor cost per successful sequence can be computed with unknown usage and no successful sequences.

Keep source-only defaults. The optional memory adapter remains experimental. The separately measured [local efficiency changes](saas-efficiency-assessment.md) and [engineering checks](saas-efficiency-validation.md) remain valid within their stated component/test scope; they do not substitute for this blocked native experiment. Hosted SaaS readiness remains unproven.

## Restore access and run a fresh cohort

Device login was attempted with `codex login --device-auth` and also failed. A noncredential network probe confirmed `Tunnel connection failed: 403 Forbidden` for `auth.openai.com`. No credential contents were read or copied.

The onboarding configuration draft now adds `auth.openai.com` while preserving its ten existing custom domains, including `chatgpt.com`. Saving the draft was confirmed, with `requires_publish=true`; saving alone does not establish application or publication. A later actual device-login request reached the authentication server and is waiting for user authorization. Runtime metadata still reports unknown network-policy state, so configuration activation is unconfirmed. If the change remains pending, review/save it in environment settings and publish the environment. Complete device sign-in in the same environment:

```sh
codex login --device-auth
```

A new study must use a fresh output directory and retain this blocked cohort:

```sh
uv run python -m benchmarks.run_warm \
  --output .local/warm-v2 --model gpt-6.1-sol --effort low \
  --repeats 2 --timeout 180
uv run python -m benchmarks.audit_warm \
  --report .local/warm-v2/report.json --artifact-root .local/warm-v2 \
  --output benchmarks/warm-v2-integrity-audit
```

Do not replace the failed original: `--resume` does not reissue it. A new cohort must still preserve all failures, independently grade outcomes, report means/medians and individual runs, verify actual delivered memory, and include every known failed-attempt cost in both cost numerators, dividing by strictly successful tasks or sequences respectively. No cost estimate is justified until native usage is available. Future model/backend authorization or quota issues remain possible and must be diagnosed from the actual response.

[Machine-readable assessment](warm-study-assessment.json) · [Evidence ZIP](memglide-warm-evidence.zip)
