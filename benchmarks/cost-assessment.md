# Ten-task Codex / Memglide cost assessment

A is standard Codex. B is Memglide compact-prefix source preparation. All dollar amounts below are **API-price equivalents, not actual bills**.

The pooled native-reported estimate is **2.28% lower**, but the **eight tasks that actually preload source cost 4.43% more**. The two controls with byte-identical prompts cost 33.27% less in B and account for the pooled saving. Their difference reflects uncontrolled run/cache variation and cannot be credited to Memglide source preparation. This study does not establish money savings caused by Memglide.

| Scope | A USD / successful task | B USD / successful task | B versus A |
|---|---:|---:|---:|
| All 10 tasks | $0.03922680 | $0.03833368 | 2.28% lower |
| 8 source-preloaded tasks | $0.04030540 | $0.04209265 | 4.43% higher |
| 2 identical-prompt controls | $0.03491240 | $0.02329780 | 33.27% lower |

All 20 assignments completed and passed independent grading; all native usage streams reconcile with the primary report. There were no failed attempts, retries, resumptions or supplementary runs. Measurement finished at 2026-10-18 16:41:32 UTC with frozen source unchanged.

B costs less in five pairs and more in five. The largest favorable pair, `ts-cost-ledger-signed-cents`, saves $0.0183468, **205.42% of the $0.0089312 net saving**. The largest unfavorable pair, `ts-cost-geometry-normalized-bounds`, adds $0.0234092, offsetting 262.11% of that net amount. Every pair remains included. One repeat on ten small synthetic tasks provides no statistical proof of general savings.

The dollar difference mainly comes from 902 fewer output tokens ($0.00902 less). Uncached input rises by 134 tokens ($0.000268 more), while cached input falls by 1,792 tokens ($0.0001792 less). Native-reported cache writes are zero in every run; an omitted upstream value can decode to zero. Allowing independent possible writes produces a range from **15.47% more expensive to 16.99% cheaper**, under the same Standard tariff. This is a scenario range, not measured billing or a confidence interval.

Four single-source pairs are descriptively 24.14% cheaper in B; four integration pairs are 26.08% more expensive. Repeated trials are needed to separate source preparation from model/cache variation. Keep the integration experimental and collect stronger evidence before claiming cost savings.

Native usage is independently parsed and reconciled with the original report. Cached reads and writes are exclusive input subsets; reasoning is already output. Failed attempts remain in the cost numerator.

```text
((I-C-W)*uncached_rate + C*cached_rate + W*write_rate + O*output_rate)/1,000,000; R is already included in O
```

Model: `gpt-6.1-sol`; requested tier: `standard`. Short-request threshold: 272,000 input tokens.

| Per million tokens | USD |
|---|---:|
| uncached_input | $2.0 |
| cached_input | $0.1 |
| cache_write_input | $2.5 |
| output | $10.0 |

| Measure | A: Codex | B: Memglide |
|---|---:|---:|
| Successful assignments / attempts | 10 / 10 | 10 / 10 |
| Total estimated model USD | 0.392268 | 0.383337 |
| Mean estimated USD / attempt | 0.039227 | 0.038334 |
| Median estimated USD / attempt | 0.039785 | 0.033631 |
| Estimated USD / successful task | 0.039227 | 0.038334 |
| Possible-write lower USD / successful task | 0.039227 | 0.038334 |
| Possible-write upper USD / successful task | 0.046181 | 0.045294 |

Native-reported price-equivalent saving per successful task: **2.28%** (positive means B costs less).
Conservative possible-write saving range: -15.47% to 16.99%. This is a scenario range, not a confidence interval.

| Run | Success | Input | Cached | Writes | Output | Estimated USD | Full seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| cost-ts-cost-ledger-memo-empty-only-r1-A | True | 48,050 | 34,816 | 0 | 570 | 0.035650 | 31.168 |
| cost-ts-cost-ledger-memo-empty-only-r1-B | True | 35,011 | 22,784 | 0 | 290 | 0.029632 | 17.210 |
| cost-py-cost-inventory-pack-ceiling-r1-B | True | 35,880 | 31,872 | 0 | 576 | 0.016963 | 20.565 |
| cost-py-cost-inventory-pack-ceiling-r1-A | True | 35,947 | 23,552 | 0 | 703 | 0.034175 | 22.833 |
| cost-ts-cost-geometry-edge-touch-r1-A | True | 36,368 | 22,784 | 0 | 906 | 0.038506 | 29.691 |
| cost-ts-cost-geometry-edge-touch-r1-B | True | 61,248 | 56,320 | 0 | 964 | 0.025128 | 33.129 |
| cost-py-cost-inventory-aggregate-stock-r1-B | True | 47,822 | 43,520 | 0 | 564 | 0.018596 | 21.332 |
| cost-py-cost-inventory-aggregate-stock-r1-A | True | 47,870 | 43,392 | 0 | 762 | 0.020915 | 24.509 |
| cost-py-cost-reports-weighted-mean-r1-A | True | 61,930 | 47,616 | 0 | 947 | 0.042860 | 30.159 |
| cost-py-cost-reports-weighted-mean-r1-B | True | 48,682 | 32,384 | 0 | 809 | 0.043924 | 24.347 |
| cost-ts-cost-geometry-normalized-bounds-r1-B | True | 49,214 | 23,040 | 0 | 982 | 0.064472 | 32.012 |
| cost-ts-cost-geometry-normalized-bounds-r1-A | True | 48,570 | 34,688 | 0 | 983 | 0.041063 | 26.158 |
| cost-ts-cost-ledger-receipt-quantity-r1-A | True | 61,476 | 48,384 | 0 | 1,014 | 0.041162 | 29.417 |
| cost-ts-cost-ledger-receipt-quantity-r1-B | True | 49,033 | 23,168 | 0 | 897 | 0.063017 | 26.550 |
| cost-py-cost-inventory-reorder-inclusive-r1-B | True | 48,485 | 23,424 | 0 | 744 | 0.059904 | 24.304 |
| cost-py-cost-inventory-reorder-inclusive-r1-A | True | 48,080 | 23,680 | 0 | 721 | 0.058378 | 24.258 |
| cost-ts-cost-ledger-signed-cents-r1-A | True | 36,125 | 20,096 | 0 | 835 | 0.042418 | 24.305 |
| cost-ts-cost-ledger-signed-cents-r1-B | True | 47,884 | 41,088 | 0 | 637 | 0.024071 | 21.953 |
| cost-py-cost-reports-csv-quoted-cell-r1-B | True | 48,238 | 34,688 | 0 | 706 | 0.037629 | 20.633 |
| cost-py-cost-reports-csv-quoted-cell-r1-A | True | 48,739 | 35,072 | 0 | 630 | 0.037141 | 22.278 |

| Metric (mean / median / total) | A | B |
|---|---:|---:|
| input_tokens | 47,315.500 / 48,065.000 / 473,155.000 | 47,149.700 / 48,361.500 / 471,497.000 |
| cached_input_tokens | 33,408.000 / 34,752.000 / 334,080.000 | 33,228.800 / 32,128.000 / 332,288.000 |
| output_tokens | 807.100 / 798.500 / 8,071.000 | 716.900 / 725.000 / 7,169.000 |
| cache_write_input_tokens | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |
| reasoning_output_tokens | 11.100 / 4.000 / 111.000 | 5.100 / 0.000 / 51.000 |
| uncached_input_tokens | 13,907.500 / 13,625.500 / 139,075.000 | 13,920.900 / 12,888.500 / 139,209.000 |
| ordinary_uncached_input_tokens | 13,907.500 / 13,625.500 / 139,075.000 | 13,920.900 / 12,888.500 / 139,209.000 |
| end_to_end_wall_seconds | 26.478 / 25.334 / 264.778 | 24.203 / 23.128 / 242.035 |
| total_observed_local_cpu_seconds | 7.537 / 6.450 / 75.370 | 5.769 / 5.569 / 57.690 |
| process_tree_peak_rss_bytes | 267,495,424.000 / 286,154,752.000 / unavailable | 258,041,856.000 / 255,768,576.000 / unavailable |
| mcp_calls | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |
| observed_file_read_commands | 1.300 / 1.000 / 13.000 | 0.900 / 1.000 / 9.000 |
| observed_repeated_read_commands | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |
| test_count | 9.600 / 9.000 / 96.000 | 9.200 / 8.500 / 92.000 |

| Estimated cost component (total USD) | A | B |
|---|---:|---:|
| uncached_input | 0.278150 | 0.278418 |
| cached_input | 0.033408 | 0.033229 |
| cache_write_input | 0.000000 | 0.000000 |
| output | 0.080710 | 0.071690 |

| Descriptive stratum | A USD / success | B USD / success | Saving % |
|---|---:|---:|---:|
| selection_stratum: caller_context_supplied | 0.034912 | 0.023298 | 33.27 |
| selection_stratum: explicit_focus | 0.040305 | 0.042093 | -4.43 |
| task_kind: integration | 0.045866 | 0.057829 | -26.08 |
| task_kind: single-source | 0.034745 | 0.026356 | 24.14 |
| task_kind: supplied-context | 0.034912 | 0.023298 | 33.27 |
| language: python | 0.038694 | 0.035403 | 8.50 |
| language: typescript | 0.039760 | 0.041264 | -3.78 |

| Task | B − A estimated USD | Saving % |
|---|---:|---:|
| py-cost-inventory-aggregate-stock | -0.002319 | 11.09 |
| py-cost-inventory-pack-ceiling | -0.017212 | 50.36 |
| py-cost-inventory-reorder-inclusive | 0.001526 | -2.61 |
| py-cost-reports-csv-quoted-cell | 0.000488 | -1.31 |
| py-cost-reports-weighted-mean | 0.001065 | -2.48 |
| ts-cost-geometry-edge-touch | -0.013378 | 34.74 |
| ts-cost-geometry-normalized-bounds | 0.023409 | -57.01 |
| ts-cost-ledger-memo-empty-only | -0.006017 | 16.88 |
| ts-cost-ledger-receipt-quantity | 0.021854 | -53.09 |
| ts-cost-ledger-signed-cents | -0.018347 | 43.25 |

Paired cost outcomes: `{"A_cheaper": 5, "B_cheaper": 5, "equal": 0, "unavailable": 0}`.

Failed/unknown attempts: 0.

- All USD values are published API-price equivalents, not measured billing or subscription charges.
- Native-reported cache writes may default upstream omissions to zero; show conservative write sensitivity, not certainty about provider cache creation.
- No point estimate is invented when writes are absent, usage is incomplete, or short-context pricing cannot be established.
- Every attempted row supplied in report.runs contributes to the numerator; any unknown supplied attempt makes the whole-arm total and cost per success unavailable. Callers must include every attempt; this parser cannot discover omitted retries or supplementary ledgers.
- Reasoning output is included in output, and cached reads/writes are included in total input; none are counted twice.
- Ten fresh tasks, one balanced trial per arm, synthetic small repositories, and uncontrolled backend/OS caches limit generalization; the range is not statistical uncertainty.
- Local CPU/RSS/time overhead is reported but has no attributable dollar rate and is not included as fabricated spending. Peak RSS totals have no physical interpretation.
- Requested default service tier is frozen; realized provider tier/routing and actual per-request model calls are unavailable from this stream.

Full pricing citations, source hashes, every run, paired deltas, missing values and failures are retained in the companion JSON.

- Pricing source: https://developers.openai.com/api/docs/pricing (retrieved 2026-10-18T16:24:05.775122+00:00; SHA-256 `59379c0a6cb2bfaa7c696098e4073d7d95fa5da1f08b7b69bf4b2d61cfc6d059`).
- Pricing source: https://developers.openai.com/api/docs/models/gpt-6.1-sol (retrieved 2026-10-18T16:24:43.518218+00:00; SHA-256 `9c43eeb7cc81f9b2bc1e992f1cdf5ba2a724a02171bf52ef1a6d052fcd30ae31`).
- Pricing source: https://developers.openai.com/api/docs/guides/prompt-caching (retrieved 2026-10-18T16:24:43.514846+00:00; SHA-256 `777b3210fbc81cc3bbc604a483f930a55f13fbedba5ae5c8c960ca45e45d5dca`).
