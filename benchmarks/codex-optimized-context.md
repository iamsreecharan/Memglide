# Optimized native Codex context audit

This companion audit retains 160 original assignments across 40 tasks. It examines actual MCP response evidence and the independent source-version snapshots captured after coding and before grading. Coding correctness, model usage, latency and cost are reported in the main A/B report.

## Original assignments

| Observation | A: standard Codex | B: compact Memglide |
|---|---:|---:|
| Assigned runs | 80 | 80 |
| Attempted runs | 80 | 80 |
| Observed Memglide calls | 0 | 80 |
| Available / observed fetch responses | 0 / 0 | 80 / 80 |
| Verify calls | 0 | 0 |
| Calls with errors | 0 | 0 |

## Returned context

- Canonical response bytes: mean 9846.5625, median 10080.0; 80 observed, 0 unavailable.
- Returned snippet UTF-8 bytes: mean 6664.825, median 6891.0; 80 observed, 0 unavailable.
- Unique source files per fetch: mean 11.825, median 12.0; 80 observed, 0 unavailable.
- Declared target-file coverage per fetch: mean 1.0, median 1.0; 80 observed, 0 unavailable.
- Declared target-file union coverage per B run: mean 1.0, median 1.0; 80 observed, 0 unavailable.

Independent baseline body checks found 160 complete and 0 incomplete bodies among 160 eligible body observations. 0 other body observations were ineligible or unknown because a returned source version could not be matched to the starting source. These observations cover declared task symbols only; they do not establish semantic completeness.

Server assertions were status {'Partial': 80}, source freshness {'Current': 80}, and truncation {'True': 77, 'False': 3}. A complete pair of declared bodies can coexist with truncation or missing broader evidence. The average fetch contained 11.825 distinct paths for two declared target files; other returned paths may contain relevant tests, helpers or supporting configuration.

## Independent source observations

Post-execution comparisons: {'match': 793, 'mismatch': 112, 'unknown': 41}; 946 file observations in 80 original B runs. Mismatches can be caused by the model's intended edits. Matching later hashes do not prove historical call-time freshness.

Of 112 mismatches checked against exported change metadata, 112 named files in both the run's tracked-change patch and Git status. This verifies correspondence with the run's edits without reconstructing exact historical mutation times.

Unknown source comparisons by path: {'tsconfig.json': 15, 'package.json': 15, 'README.md': 8, 'AGENTS.md': 3}. These files were excluded by the snapshot helper's explicit source-file suffix policy, which avoids opening config, state, database or credential files. Their versions remain unmeasured by this independent snapshot.

0 fetches completed before the first observable command start; 80 occurred after or interleaved with commands; 0 had unknown ordering. Command ordering is a proxy, not a complete filesystem mutation trace.

## Read-command intent overlap

The conservative literal-command parser recognized 91 read-command intents in A and 84 in B. 12 B commands included 14 path mentions also returned by an earlier completed fetch. A returned path may contain only a snippet, and a subsequent read may obtain additional or changed code. These overlaps do not establish redundant reads or actual filesystem I/O.

| B run | Paths named after an earlier fetch returned the same path |
|---|---|
| ts2-stream-decimal-money-parser-r1-B | package.json, tests/smoke.test.mjs |
| py2-ledger-csv-bank-import-r1-B | AGENTS.md |
| ts2-stream-fragmented-ndjson-r1-B | package.json |
| ts2-config-casefold-header-collection-r1-B | package.json |
| ts2-config-utf8-feature-cohorts-r1-B | package.json |
| ts2-config-safe-local-redirects-r1-B | package.json |
| py2-ledger-signed-tax-rounding-r1-B | ledger/api.py |
| ts2-config-semantic-version-precedence-r2-B | package.json |
| ts2-stream-decimal-money-parser-r2-B | package.json, tests/smoke.test.mjs |
| py2-ledger-csv-bank-import-r2-B | ledger/csv_bank_import.py |
| py2-workflow-interval-coalescing-r2-B | tests/test_smoke.py |
| py2-ledger-signed-tax-rounding-r2-B | tests/test_smoke.py |

## Every original run

| Run | Arm | Status | Fetch available / observed | Target-file union coverage | Post-exit match / mismatch / unknown |
|---|---|---|---:|---:|---|
| ts2-config-strict-pointer-lookup-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-strict-pointer-lookup-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 2 |
| ts2-config-semantic-version-precedence-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-config-semantic-version-precedence-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-reconciliation-version-merge-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-reconciliation-version-merge-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-currency-netting-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-ledger-currency-netting-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-utf8-batch-budget-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 0 |
| py2-workflow-utf8-batch-budget-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-complete-form-errors-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| ts2-config-complete-form-errors-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-statement-timezones-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-statement-timezones-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-bounded-run-length-decode-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-stream-bounded-run-length-decode-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-simultaneous-text-edits-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-stream-simultaneous-text-edits-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-specific-route-matching-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-specific-route-matching-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-workflow-incremental-utf8-lines-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-incremental-utf8-lines-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-config-repeated-query-values-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-repeated-query-values-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| ts2-stream-transactional-accumulator-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| ts2-stream-transactional-accumulator-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-keyed-upsert-order-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| ts2-stream-keyed-upsert-order-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-decimal-money-parser-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 1 |
| ts2-stream-decimal-money-parser-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-weighted-allocation-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-weighted-allocation-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| py2-ledger-csv-bank-import-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 2 / 2 |
| py2-ledger-csv-bank-import-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-deep-settings-overlay-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-deep-settings-overlay-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-ready-job-order-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 0 |
| py2-workflow-ready-job-order-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-invoice-line-discounts-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-invoice-line-discounts-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| ts2-config-unicode-ascii-slugs-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-config-unicode-ascii-slugs-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-event-time-rolling-counts-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-stream-event-time-rolling-counts-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-fragmented-ndjson-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 2 |
| ts2-stream-fragmented-ndjson-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-nested-redaction-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-nested-redaction-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-atomic-transfer-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-atomic-transfer-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 2 / 2 |
| py2-workflow-bounded-async-execution-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-workflow-bounded-async-execution-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-casefold-header-collection-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-casefold-header-collection-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| py2-workflow-capped-backoff-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-capped-backoff-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-deterministic-build-order-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-deterministic-build-order-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-escaped-record-codec-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-stream-escaped-record-codec-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-strict-template-expansion-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-workflow-strict-template-expansion-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-utf8-feature-cohorts-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-utf8-feature-cohorts-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-stream-half-open-window-join-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-half-open-window-join-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-config-quoted-env-values-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-quoted-env-values-r1-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-config-safe-local-redirects-r1-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| ts2-config-safe-local-redirects-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-audit-hash-chain-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-audit-hash-chain-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 1 |
| py2-workflow-interval-coalescing-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 1 |
| py2-workflow-interval-coalescing-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-abort-aware-delay-plan-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-abort-aware-delay-plan-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 1 |
| py2-ledger-signed-tax-rounding-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| py2-ledger-signed-tax-rounding-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-atomic-pointer-updates-r1-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-atomic-pointer-updates-r1-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| ts2-config-strict-pointer-lookup-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 2 |
| ts2-config-strict-pointer-lookup-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-semantic-version-precedence-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-semantic-version-precedence-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| py2-ledger-reconciliation-version-merge-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-reconciliation-version-merge-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-currency-netting-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-currency-netting-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-workflow-utf8-batch-budget-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-utf8-batch-budget-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 0 |
| ts2-config-complete-form-errors-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-complete-form-errors-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-ledger-statement-timezones-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-statement-timezones-r2-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 1 |
| ts2-stream-bounded-run-length-decode-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-bounded-run-length-decode-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-stream-simultaneous-text-edits-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-simultaneous-text-edits-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-config-specific-route-matching-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| ts2-config-specific-route-matching-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-incremental-utf8-lines-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-incremental-utf8-lines-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-repeated-query-values-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| ts2-config-repeated-query-values-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-transactional-accumulator-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-transactional-accumulator-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| ts2-stream-keyed-upsert-order-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-keyed-upsert-order-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| ts2-stream-decimal-money-parser-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-decimal-money-parser-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 1 |
| py2-ledger-weighted-allocation-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-weighted-allocation-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-csv-bank-import-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-csv-bank-import-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 1 |
| py2-workflow-deep-settings-overlay-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-deep-settings-overlay-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-ready-job-order-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-ready-job-order-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 2 / 0 |
| py2-ledger-invoice-line-discounts-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-invoice-line-discounts-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-unicode-ascii-slugs-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-unicode-ascii-slugs-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-stream-event-time-rolling-counts-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-event-time-rolling-counts-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-stream-fragmented-ndjson-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-fragmented-ndjson-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 1 |
| py2-ledger-nested-redaction-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-ledger-nested-redaction-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-atomic-transfer-r2-B | B | completed | 1 / 1 | 1.0 | 11 / 2 / 2 |
| py2-ledger-atomic-transfer-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-bounded-async-execution-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-bounded-async-execution-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| ts2-config-casefold-header-collection-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| ts2-config-casefold-header-collection-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-capped-backoff-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-capped-backoff-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-deterministic-build-order-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-deterministic-build-order-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-stream-escaped-record-codec-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-escaped-record-codec-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| py2-workflow-strict-template-expansion-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-strict-template-expansion-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| ts2-config-utf8-feature-cohorts-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-config-utf8-feature-cohorts-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-stream-half-open-window-join-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 1 |
| ts2-stream-half-open-window-join-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-quoted-env-values-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 0 |
| ts2-config-quoted-env-values-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-safe-local-redirects-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| ts2-config-safe-local-redirects-r2-B | B | completed | 1 / 1 | 1.0 | 9 / 2 / 0 |
| py2-ledger-audit-hash-chain-r2-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| py2-ledger-audit-hash-chain-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-interval-coalescing-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-workflow-interval-coalescing-r2-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 1 |
| ts2-stream-abort-aware-delay-plan-r2-B | B | completed | 1 / 1 | 1.0 | 10 / 1 / 2 |
| ts2-stream-abort-aware-delay-plan-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-signed-tax-rounding-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |
| py2-ledger-signed-tax-rounding-r2-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| py2-workflow-atomic-pointer-updates-r2-B | B | completed | 1 / 1 | 1.0 | 11 / 1 / 0 |
| py2-workflow-atomic-pointer-updates-r2-A | A | completed | 0 / 0 | Unavailable | Unavailable / not applicable |

## Limitations

- This is a post-experiment content audit of actual native MCP event results, not a model cost meter.
- Target-file coverage is a declared-file proxy; expected declaration/body coverage is narrowly scoped to the two symbols declared by each synthetic task. Full semantic completeness is unknown.
- Exact body checks use independent Python AST or the narrow TypeScript fixture scanner against immutable starting Git blobs. A check is eligible only when that returned file hash matches the starting blob; post-edit or unknown versions are not treated as missing baseline bodies.
- Source versions recorded after Codex exit and before grading are later observations. A model's intended edits can cause mismatches; neither matches nor mismatches establish source freshness at the instant of retrieval.
- Server status, source_freshness, truncation and warnings are application assertions. Independently verified live call-time freshness remains unavailable.
- Native event ordering establishes only whether a completed retrieval preceded observable command starts. Commands may read or mutate source; the full filesystem history is not measured.
- Snippet and canonical JSON bytes are measured response content, not transport bytes, tokenizer counts, model input tokens, or money saved.
- Missing, interrupted, failed, ambiguous and ineligible observations remain visible and unknown; no unobserved responses are invented as zero-byte or successful retrievals.
- A does not expose Memglide MCP and receives no invented retrieval-quality scores. Repeated runs and related tasks are correlated; this is a small synthetic corpus.

Supplemental attempts retained separately in JSON: 0. They never replace original observations.

Generated at 2026-10-18T00:32:05.354772+00:00. See the companion JSON for every call, eligibility decision, comparison, missing observation and provenance digest.
