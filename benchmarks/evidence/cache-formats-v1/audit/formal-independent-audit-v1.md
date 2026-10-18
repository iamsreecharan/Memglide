# Independent legacy/compact-prefix audit

**Verdict: FAIL**.

Audit artifacts preserve every invocation, including any initial auditor errors.

Checked 5,138 assertions; 40 errors and 0 notes.

20 tasks; 40 original slots; 40 attempts; 20 verified pairs.

| Arm | Planned | Attempted | Successful completion | Execution statuses |
|---|---:|---:|---:|---|
| A | 20 | 20 | 20 | {"completed": 20} |
| B | 20 | 20 | 20 | {"completed": 20} |

Successful completion requires completed execution, a passing external grade and valid treatment. Failed, invalid and interrupted assignments remain visible.

| Metric | A mean | B mean | A median | B median |
|---|---:|---:|---:|---:|
| input_tokens | 50076.8 | 49071.3 | 48625 | 48321 |
| cached_input_tokens | 36307.2 | 34764.8 | 35136 | 34880 |
| uncached_input_tokens | 13769.5 | 14306.5 | 13544 | 13454 |
| output_tokens | 790.75 | 742.6 | 799 | 725.5 |
| end_to_end_wall_seconds | 29.6856 | 26.3733 | 27.6685 | 26.699 |
| mcp_calls | 0 | 0 | 0 | 0 |

## Limits

- Known-file utility-edit microbenchmark: four small synthetic repositories, twenty distinct focus sets, one repeat. It does not test repeated different tasks on unchanged same files.
- A is Memglide legacy and B is Memglide compact-prefix; neither is standard Codex. No old-cohort baseline is a matched comparison.
- Prepared-prompt reconstruction validates frozen source bytes and launcher forwarding records; it does not prove provider-side receipt or model attention.
- The task prompt is identical before treatment; preloading intentionally changes the actual native prompt.
- No billed costs, cost per successful task, underlying provider model-call counts or actual filesystem I/O trace are supplied.
- Cached input is included in total input; uncached input is derived by subtraction.
- RSS/CPU reproduce sampled local observations, not remote inference overhead; read-command fields remain proxies.
- The auditor never imports Memglide or benchmark code, opens credentials/databases/native state, reruns tests or calls a model.

## Audit errors

- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-warmup-moving-average-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-warmup-moving-average-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-unique-intersection-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-unique-intersection-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-fractional-sample-variance-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-fractional-sample-variance-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-hex-color-lengths-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-hex-color-lengths-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-histogram-boundary-slots-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-histogram-boundary-slots-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-last-value-fallback-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-last-value-fallback-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-folded-header-spacing-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-folded-header-spacing-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-strict-integer-range-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-strict-integer-range-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-consecutive-run-groups-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-consecutive-run-groups-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-stable-feed-merge-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-stable-feed-merge-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-quoted-display-backslash-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-quoted-display-backslash-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-missing-not-falsy-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-missing-not-falsy-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-colon-password-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-colon-password-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-signed-left-rotation-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-collections-signed-left-rotation-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-form-space-encoding-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-form-space-encoding-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-utf8-header-word-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-utf8-header-word-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-required-whitespace-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-required-whitespace-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-reply-subject-preservation-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-mailroom-reply-subject-preservation-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-strict-calendar-date-r1-A"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-ts-cache-forms-strict-calendar-date-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-negative-baseline-change-r1-B"}
- {"code": "actual_format_launcher_and_identical_native_options", "run_id": "fmt-py-cache-metrics-negative-baseline-change-r1-A"}
