# Warm memory benchmark

A: bare Codex. B: complete focused source, no memory. C: same source plus earlier source-verified model quotations in one active Memglide session.

Dollar values below are API list-price equivalents, not actual billed cost.

| Arm | Attempted | Successful | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|---:|
| A | 0 | 0 | None | None | None |
| B | 0 | 0 | None | None | None |
| C | 1 | 0 | 2.493797863004147 | 2.493797863004147 | None |

## Sequence-wide accounting

All three stages and failures are included. Unknown costs remain unavailable.

| Arm | Successful / planned sequences | Estimated USD / successful sequence |
|---|---:|---:|
| A | 0 / 24 | None |
| B | 0 / 24 | None |
| C | 0 / 24 | None |

## Observed measurements

Missing telemetry is unavailable. Cached input is included in total input; resource values describe only the local measured scope.

| Metric | Arm | Mean | Median | Total | Observed |
|---|---|---:|---:|---:|---:|
| input_tokens | A | None | None | None | 0 |
| input_tokens | B | None | None | None | 0 |
| input_tokens | C | None | None | None | 0 |
| cached_input_tokens | A | None | None | None | 0 |
| cached_input_tokens | B | None | None | None | 0 |
| cached_input_tokens | C | None | None | None | 0 |
| uncached_input_tokens | A | None | None | None | 0 |
| uncached_input_tokens | B | None | None | None | 0 |
| uncached_input_tokens | C | None | None | None | 0 |
| output_tokens | A | None | None | None | 0 |
| output_tokens | B | None | None | None | 0 |
| output_tokens | C | None | None | None | 0 |
| wall_time_seconds | A | None | None | None | 0 |
| wall_time_seconds | B | None | None | None | 0 |
| wall_time_seconds | C | 2.0216733499983093 | 2.0216733499983093 | 2.0216733499983093 | 1 |
| end_to_end_wall_seconds | A | None | None | None | 0 |
| end_to_end_wall_seconds | B | None | None | None | 0 |
| end_to_end_wall_seconds | C | 2.493797863004147 | 2.493797863004147 | 2.493797863004147 | 1 |
| native_exec_wall_seconds | A | None | None | None | 0 |
| native_exec_wall_seconds | B | None | None | None | 0 |
| native_exec_wall_seconds | C | 2.0216733499983093 | 2.0216733499983093 | 2.0216733499983093 | 1 |
| approval_index_wall_seconds | A | None | None | None | 0 |
| approval_index_wall_seconds | B | None | None | None | 0 |
| approval_index_wall_seconds | C | 0.39930724800069584 | 0.39930724800069584 | 0.39930724800069584 | 1 |
| approval_index_cpu_seconds | A | None | None | None | 0 |
| approval_index_cpu_seconds | B | None | None | None | 0 |
| approval_index_cpu_seconds | C | 0.080119877 | 0.080119877 | 0.080119877 | 1 |
| context_preparation_wall_seconds | A | None | None | None | 0 |
| context_preparation_wall_seconds | B | None | None | None | 0 |
| context_preparation_wall_seconds | C | 0.013160449001588859 | 0.013160449001588859 | 0.013160449001588859 | 1 |
| context_preparation_cpu_seconds | A | None | None | None | 0 |
| context_preparation_cpu_seconds | B | None | None | None | 0 |
| context_preparation_cpu_seconds | C | 0.00721410599999972 | 0.00721410599999972 | 0.00721410599999972 | 1 |
| process_tree_peak_rss_bytes | A | None | None | None | 0 |
| process_tree_peak_rss_bytes | B | None | None | None | 0 |
| process_tree_peak_rss_bytes | C | 84246528 | 84246528 | None | 1 |
| cpu_seconds | A | None | None | None | 0 |
| cpu_seconds | B | None | None | None | 0 |
| cpu_seconds | C | 1.48 | 1.48 | 1.48 | 1 |
| total_observed_local_cpu_seconds | A | None | None | None | 0 |
| total_observed_local_cpu_seconds | B | None | None | None | 0 |
| total_observed_local_cpu_seconds | C | 2.8028758419999997 | 2.8028758419999997 | 2.8028758419999997 | 1 |
| mcp_calls | A | None | None | None | 0 |
| mcp_calls | B | None | None | None | 0 |
| mcp_calls | C | None | None | None | 0 |
| model_calls | A | None | None | None | 0 |
| model_calls | B | None | None | None | 0 |
| model_calls | C | None | None | None | 0 |
| repeated_file_reads | A | None | None | None | 0 |
| repeated_file_reads | B | None | None | None | 0 |
| repeated_file_reads | C | None | None | None | 0 |
| observed_file_read_commands | A | None | None | None | 0 |
| observed_file_read_commands | B | None | None | None | 0 |
| observed_file_read_commands | C | 0 | 0 | 0 | 1 |
| observed_repeated_read_commands | A | None | None | None | 0 |
| observed_repeated_read_commands | B | None | None | None | 0 |
| observed_repeated_read_commands | C | 0 | 0 | 0 | 1 |
| actual_cost_usd | A | None | None | None | 0 |
| actual_cost_usd | B | None | None | None | 0 |
| actual_cost_usd | C | None | None | None | 0 |
| computed_cost_usd | A | None | None | None | 0 |
| computed_cost_usd | B | None | None | None | 0 |
| computed_cost_usd | C | None | None | None | 0 |

## Cost sensitivity

Ranges permit unknown cache-write attribution; they are scenarios, not confidence intervals or billed amounts.

| Arm | Point USD / successful task | Possible-write lower | Possible-write upper |
|---|---:|---:|---:|
| A | None | None | None |
| B | None | None | None |
| C | None | None | None |

## Repeat 1

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 0 / 0 | None | None | None |
| B | 0 / 0 | None | None | None |
| C | 0 / 1 | 2.493797863004147 | 2.493797863004147 | None |

## Repeat 2

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 0 / 0 | None | None | None |
| B | 0 / 0 | None | None | None |
| C | 0 / 0 | None | None | None |

## cold_stage_1

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 0 / 0 | None | None | None |
| B | 0 / 0 | None | None | None |
| C | 0 / 1 | 2.493797863004147 | 2.493797863004147 | None |

## warm_stage_2_3

| Arm | Successful / attempted | Mean instrumented full seconds | Median instrumented full seconds | Estimated USD / successful task |
|---|---:|---:|---:|---:|
| A | 0 / 0 | None | None | None |
| B | 0 / 0 | None | None | None |
| C | 0 / 0 | None | None | None |

## Memory observations

```json
{
  "C_requested_prior_memory_runs": 0,
  "C_preloaded_memory_runs": 0,
  "C_fallback_reasons": {
    "no_prior_memory": 1,
    "not_prepared": 71
  },
  "accepted_quote_instances": 0,
  "rejected_quote_instances": 0
}
```

## Default-promotion decision

Passed: False; failed checks: 18. All216 unique original assignments must be attempted
Memory remains explicit and optional unless every predeclared acceptance check passes. Mixed results do not establish universal cost or speed savings.

## Every original assignment

| Run | Status | Grade | Input | Cached | Output | Instrumented full seconds | Memory mode |
|---|---|---|---:|---:|---:|---:|---|
| warm-ts-warm-paths-s1-r1-C | execution_failed | False | None | None | None | 2.493797863004147 | passthrough |
| warm-ts-warm-paths-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r1-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r1-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r1-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-paths-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-quota-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-routing-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-labels-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-headers-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-retries-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-priority-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-clocks-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-pagination-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-intervals-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-py-warm-redaction-s3-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r2-C | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r2-B | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s1-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s2-r2-A | not_run | None | None | None | None | None | None |
| warm-ts-warm-versions-s3-r2-A | not_run | None | None | None | None | None | None |

## Failures

- warm-ts-warm-paths-s1-r1-C: execution_failed; Native process did not exit successfully within timeout; Native event framing/usage is incomplete or reports an error; Invalid final structured output: ValueError

## Limitations

- C reuses one active default-expiration Memglide session across three fresh native Codex processes; ended/expired Memglide sessions and arbitrary cross-session persistence are not tested.
- Twelve three-task sequences, two repeats, three arms produce 216 original assignments. Small purpose-built repositories do not establish production-wide or large-repository performance.
- Every stage starts from its independently frozen canonical source commit; earlier model patches never carry into later tasks. All arms receive the same task, path hints, test command, final findings schema, model and native settings.
- All arms share a paid findings-output request; A has bare tools under this matched workflow, not an unconstrained ordinary summary-only prompt. Findings output is charged in every arm, not free extraction.
- Only model-produced current-source quotations are captured. Neither grading outcomes nor hidden grader/reference data select, repair or create memories. Exact quotations establish textual source support, not semantic truth.
- Memory absence, stale quotations and bounded-context fallback are retained intent-to-treat outcomes. No failed assignment is retried or replaced. Independent grading never gates capture.
- B and C both pay initial approval/index and per-stage reindex cost; C also pays session creation, source-quote capture, validation, preparation and explicit end-session cleanup. Instrumented full wall time and parent CPU additionally include independent treatment audit work: frozen-Git source reconstruction and C prior-final/source-envelope verification. Native wall time is reported separately. Fixture reset, external grading, shared product API imports and the long-lived harness startup are excluded; instrumented time is not pure product latency.
- Fresh isolated worktrees, native state and databases are used per sequence/arm/repeat. Native processes are fresh per stage. Provider/OS cache state is uncontrolled; no cache header/session tampering is used.
- All arms configure zero MCP servers. This measures source/memory preloading, not native MCP efficiency. MCP functionality is tested separately.
- Actual billing, provider inference-call counts, actual filesystem reads and provider resource use are unavailable. Dollars are labelled API list-price equivalents from observed native usage; missing usage is never zero.
- Local CPU is an observed lower bound; sampled native child RSS excludes parent preparation/indexing, can miss short-lived children and double-count shared pages. Command/read-command items are proxies.
- Reported zero cache writes may be upstream parser defaults. Possible-write ranges are scenarios, not confidence intervals or actual subscription savings.
