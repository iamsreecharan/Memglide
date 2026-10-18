# Independent bare-Codex/compact-Memglide cost audit

**Verdict: PASS**.

Audit artifacts preserve every invocation, including any initial auditor errors.

Checked 4,307 assertions; 0 errors and 0 notes.

10 tasks; 20 original slots; 20 attempts; 10 verified pairs.

| Arm | Planned | Attempted | Successful completion | Execution statuses |
|---|---:|---:|---:|---|
| A | 10 | 10 | 10 | {"completed": 10} |
| B | 10 | 10 | 10 | {"completed": 10} |

Successful completion requires completed execution, a passing external grade and valid treatment. Failed, invalid and interrupted assignments remain visible.

| Metric | A mean | B mean | A median | B median |
|---|---:|---:|---:|---:|
| input_tokens | 47315.5 | 47149.7 | 48065 | 48361.5 |
| cached_input_tokens | 33408 | 33228.8 | 34752 | 32128 |
| uncached_input_tokens | 13907.5 | 13920.9 | 13625.5 | 12888.5 |
| output_tokens | 807.1 | 716.9 | 798.5 | 725 |
| end_to_end_wall_seconds | 26.4778 | 24.2035 | 25.3336 | 23.1285 |
| mcp_calls | 0 | 0 | 0 | 0 |

## Limits

- Known-file utility-edit microbenchmark: four small synthetic repositories, ten fresh tasks, one repeat. It does not test repeated different tasks on unchanged same files.
- A is standard Codex and B uses conditional upfront compact-prefix Memglide source delivery. No earlier cohort is a matched comparison.
- Prepared-prompt reconstruction validates frozen source bytes and launcher forwarding records; it does not prove provider-side receipt or model attention.
- The task prompt is identical before treatment; preloading intentionally changes the actual native prompt.
- No billed costs, cost per successful task, underlying provider model-call counts or actual filesystem I/O trace are supplied.
- Cached input is included in total input; uncached input is derived by subtraction.
- RSS/CPU reproduce sampled local observations, not remote inference overhead; read-command fields remain proxies.
- The auditor never imports Memglide or benchmark code, opens credentials/databases/native state, reruns tests or calls a model.
