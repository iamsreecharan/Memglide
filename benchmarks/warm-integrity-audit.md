# Offline warm benchmark audit

Passed: True. Complete study coverage: False.

```json
{
  "coverage": {
    "planned_rows": 216,
    "attempted": 1,
    "unrun": 215,
    "failures_retained": 1,
    "fully_priced_native_attempts": 0,
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
    "pass": 367,
    "unavailable": 25
  },
  "accounting": {
    "A": {
      "planned": 72,
      "attempted": 0,
      "strict_successes": 0,
      "strict_successful_sequences": 0,
      "known_cost_attempts": 0,
      "price_equivalent_total_usd": null,
      "price_equivalent_per_successful_task_usd": null,
      "price_equivalent_per_successful_sequence_usd": null
    },
    "B": {
      "planned": 72,
      "attempted": 0,
      "strict_successes": 0,
      "strict_successful_sequences": 0,
      "known_cost_attempts": 0,
      "price_equivalent_total_usd": null,
      "price_equivalent_per_successful_task_usd": null,
      "price_equivalent_per_successful_sequence_usd": null
    },
    "C": {
      "planned": 72,
      "attempted": 1,
      "strict_successes": 0,
      "strict_successful_sequences": 0,
      "known_cost_attempts": 0,
      "price_equivalent_total_usd": null,
      "price_equivalent_per_successful_task_usd": null,
      "price_equivalent_per_successful_sequence_usd": null
    }
  },
  "redundant_evidence_diagnostic": {
    "scope": "Offline descriptive diagnosis only; exact path+hash overlap with supplied source. Byte counts are not tokens. Never a treatment, grading, tuning or promotion signal."
  }
}
```

## Failed checks

None.

## Limits

- API price equivalents are not billing; reported cache-write zero is not upstream proof.
- Exact quotations establish textual support, not semantic truth or proof the model inspected a file.
- Unknown usage and unrun assignments remain unavailable. Partial/pilot coverage cannot establish a full-study result.
