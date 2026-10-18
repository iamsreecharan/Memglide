# Independent formal A/B audit

**Verdict: PASS.** The independent auditor reproduced 9,480 integrity assertions with zero errors or audit notes. This is the first audit execution; no failed audit or auditor correction was discarded.

Formal experiment: `formal-40-v1`; completed at **2026-10-18T00:27:14.607106+00:00 (UTC)**. Launcher PID 38736 was a zombie before the audit began. A separate process-identity check found no surviving matching native run process.

## Verified evidence

- Exactly 40 unique tasks: 20 Python and 20 TypeScript, ten tasks in each of four new repositories.
- Exactly 160 original assignments: A/B with two counterbalanced repeats per task. All assignments remain in the report.
- A completed and passed independent grading in 80/80 runs; B completed and passed in 80/80. There were zero interrupted originals, supplemental retries, or resumes.
- All 80 A streams contain zero MCP calls. All 80 B streams contain one successful, hash-backed `fetch_context` response; none invoked `verify_context`. Verification is optional in the frozen policy and its absence is valid.
- Frozen commit `62e07cc98855b4cdde255395372e5d78b3a7e2a1`, 22 application Python files, aggregate `5e867d309e0a24a3e52f15a1e40b837dc7a228074380a4aaa3b1419b989856f3`, prompts, initial commits, native Codex settings, immutable results, and protected fixture observations all matched.
- The 322-record attempt hash chain, sealed report digest, original/supplemental projections, external grader commands and external oracle locations matched.
- Native usage was independently reparsed from actual JSONL events; all arm totals, means, medians, and 80 verified pairs matched the report. Cached input never exceeded total input.
- Actual billed cost, cost per success, underlying model-call counts, and actual repeated filesystem reads remain unavailable; none was fabricated.

## Observed comparison

| Metric | A: standard Codex | B: compact Memglide | B versus A |
|---|---:|---:|---:|
| Independent graded success | 80/80 | 80/80 | Equal |
| Total input tokens | 5,030,508 | 6,681,616 | +32.82% |
| Cached input tokens, a subset of input | 4,047,616 | 5,677,440 | +40.27% |
| Derived uncached input tokens | 982,892 | 1,004,176 | +2.17% |
| Output tokens | 113,802 | 119,841 | +5.31% |
| Mean native CLI time | 27.296 s | 31.970 s | +17.12% |
| Mean CLI plus required fresh indexing | 27.296 s | 32.178 s | +17.88% |
| MCP calls | 0 | 80 | One per B run |

Percentages compare arm means or totals over the same 80 assigned runs per arm. Derived uncached input is input minus cached input, not independently emitted billing telemetry. The paired observations and repeats are correlated. These descriptive figures show higher resource use for B in this synthetic cohort; they do not support a token, latency, or billed-cost saving.

## Context limits

Both declared target paths appeared in the returned context union for all 80 B runs. This is a declared-path proxy, not complete function-body or semantic coverage. All 80 responses were server-labelled `Partial` and source `Current`; 77 were marked truncated. Those server labels do not independently prove call-time freshness.

Independent post-execution snapshots are bound to each native stream and labelled `post_codex_pre_grader`. A source mismatch can follow the model own intended edit and is neither a coding failure nor evidence that retrieval was stale at call time.

## Audit artifacts

- Auditor: `audit_formal.py` (standard library only).
- Detailed independent audit: `formal-independent-audit-v1.json`.
- Execution log: `formal-independent-audit-v1.log`.
- Process completion evidence: `formal-process-completion-v1.json`.
- Source report digest: `d1234ce754b9ccd671180c0d5b4d02d97c1b5ac2191415c2648c009857f8300c`.
- Detailed audit SHA-256: `b6a4fd278b076566ef6f6fdc2c8ab20c7631e372ebed9b9c5ae05298e95f2ae7`.

The auditor did not issue model requests, rerun tests, modify application/harness/raw evidence, read credentials or databases, or execute indexed source. The completed benchmark was audited before public documentation edits.
