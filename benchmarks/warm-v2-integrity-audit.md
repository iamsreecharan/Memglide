# Offline warm benchmark audit

Passed: False. Complete study coverage: False.

```json
{
  "coverage": {
    "planned_rows": 216,
    "attempted": 81,
    "unrun": 135,
    "failures_retained": 1,
    "fully_priced_native_attempts": 81,
    "arm_orders": {
      "CBA": 4,
      "BCA": 4,
      "ACB": 4,
      "BAC": 4,
      "CAB": 4,
      "ABC": 4
    }
  },
  "check_counts": {
    "pass": 2345,
    "fail": 7,
    "unavailable": 16
  },
  "accounting": {
    "A": {
      "planned": 72,
      "attempted": 27,
      "strict_successes": 27,
      "strict_successful_sequences": 9,
      "known_cost_attempts": 27,
      "price_equivalent_total_usd": "1.1889952",
      "price_equivalent_per_successful_task_usd": "0.04403685925925925925925925926",
      "price_equivalent_per_successful_sequence_usd": null
    },
    "B": {
      "planned": 72,
      "attempted": 27,
      "strict_successes": 27,
      "strict_successful_sequences": 9,
      "known_cost_attempts": 27,
      "price_equivalent_total_usd": "1.0809684",
      "price_equivalent_per_successful_task_usd": "0.04003586666666666666666666667",
      "price_equivalent_per_successful_sequence_usd": null
    },
    "C": {
      "planned": 72,
      "attempted": 27,
      "strict_successes": 26,
      "strict_successful_sequences": 8,
      "known_cost_attempts": 27,
      "price_equivalent_total_usd": "1.1812640",
      "price_equivalent_per_successful_task_usd": "0.04543323076923076923076923077",
      "price_equivalent_per_successful_sequence_usd": null
    }
  },
  "redundant_evidence_diagnostic": {
    "additional_source_reference_instances": 24,
    "delivered_quote_bytes": 3696,
    "scope": "Offline descriptive diagnosis only; exact path+hash overlap with supplied source. Byte counts are not tokens. Never a treatment, grading, tuning or promotion signal."
  }
}
```

## Failed checks

- fresh_native_usage_reconciled (warm-py-warm-pagination-s3-r1-C)
- priced_native_usage_reconciled (warm-py-warm-pagination-s3-r1-C)
- independent_decimal_run_price (warm-py-warm-pagination-s3-r1-C)
- actual_prompt_hash (warm-py-warm-pagination-s3-r1-C)
- independent_sequence_cost_and_success (py-warm-pagination-r1-C)
- campaign_cost_includes_failed_attempts (C)
- task_success_denominator (C)

## Limits

- API price equivalents are not billing; reported cache-write zero is not upstream proof.
- Exact quotations establish textual support, not semantic truth or proof the model inspected a file.
- Unknown usage and unrun assignments remain unavailable. Partial/pilot coverage cannot establish a full-study result.
