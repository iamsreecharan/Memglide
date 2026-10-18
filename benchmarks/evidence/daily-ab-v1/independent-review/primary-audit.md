# Independent daily A/B audit

**Verdict: PASS**.

Audit artifacts preserve every invocation, including any initial auditor errors.

Checked 9,884 assertions; 0 errors and 0 notes.

20 tasks; 80 original slots; 80 attempts; 40 verified pairs.

| Arm | Planned | Attempted | Successful completion | Execution statuses |
|---|---:|---:|---:|---|
| A | 40 | 40 | 40 | {"completed": 40} |
| B | 40 | 40 | 40 | {"completed": 40} |

Successful completion requires completed execution, a passing external grade and valid treatment. Failed, invalid and interrupted assignments remain visible.

| Metric | A mean | B mean | A median | B median |
|---|---:|---:|---:|---:|
| input_tokens | 48580.3 | 47151.9 | 48222.5 | 48524 |
| cached_input_tokens | 40048 | 36304 | 43392 | 36800 |
| uncached_input_tokens | 8532.35 | 10847.9 | 5609.5 | 10254 |
| output_tokens | 865.85 | 812.6 | 895.5 | 855.5 |
| end_to_end_wall_seconds | 21.5832 | 20.5568 | 22.8033 | 20.8663 |
| mcp_calls | 0 | 0 | 0 | 0 |

## Limits

- Known-file utility-edit microbenchmark; four small synthetic repositories and correlated repeats.
- Prepared-prompt reconstruction validates frozen source bytes and launcher forwarding records; it does not prove provider-side receipt or model attention.
- The task prompt is identical before treatment; preloading intentionally changes the actual native prompt.
- No billed costs, cost per successful task, underlying provider model-call counts or actual filesystem I/O trace are supplied.
- Cached input is included in total input; uncached input is derived by subtraction.
- RSS/CPU reproduce sampled local observations, not remote inference overhead; read-command fields remain proxies.
- The auditor never imports Memglide or benchmark code, opens credentials/databases/native state, reruns tests or calls a model.
