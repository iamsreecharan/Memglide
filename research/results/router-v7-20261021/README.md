# Memglide v7: publication data and statistical reproduction

The completed comparison has 128 graded sessions. The primary analysis uses
112 sessions from 28 tasks, two repetitions per arm. Codex alone and Codex with
Memglide each passed 54/56 primary strict checks. Memglide's observed uniform
token-price equivalent was 4.84% lower, while its full measured workflow was
1.17% slower. Neither paired superiority test passed. Joint cost and latency
superiority is **not established**.

This is the amended fixed-panel result. It does not replace the original closed
study's decision with a claim of prospective confirmation. The task membership,
two endpoints, repetitions and primary quality rule were retained through the
documented deployment, source-policy and transport-accounting corrections.

## Reproduce the statistics

Use Python 3.12 with the pinned numerical libraries:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py
```

If the dependencies are already available, run `python reproduce.py` directly.
The script reads only this directory, verifies the published checksums, checks
all 128 per-run tariffs and validity fields, rebuilds the exact primary subset,
and recomputes paired means, Student t tests, confidence intervals, task-level
bootstrap sensitivities, quality counts and the joint decision. It makes no
network request or model call. `reproduction-results.json` records the successful
reference run with SciPy 1.17.0 and NumPy 2.3.5. The bootstrap uses 10,000 task
resamples, seed 20261102; it is descriptive and cannot change the primary rule.

For a dependency-free integrity check, run `sha256sum -c SHA256SUMS` from this
directory. The manifest verifies the payload plus `checksums.json`; the checksum
files exclude their own bytes to avoid a circular commitment.

## Files and scope

| File | Contents |
|---|---|
| `report.md` | Readable results and their interpretation. |
| `analysis-summary.json` | Portable, allowlisted summary preserving the primary statistics and arm totals. |
| `summary.json` | Byte-identical compatibility alias for the figure generator. |
| `primary-112-runs.csv` | All 112 primary measurements and attested quality/integrity fields. |
| `all-128-runs.csv` | All 128 measured and graded rows in the amended panel; includes the 16 descriptive exposed-task rows. |
| `paired-28-tasks.csv` | The two-repeat arm means and differences for each primary task. |
| `public-task-catalog.json` | All 36 frozen public task IDs, repositories, commits, prompts and command templates; primary/exposure labels are explicit. |
| `protocol-excerpt.json` | Portable excerpt of the sealed design and decision rules. |
| `data-dictionary.md` | Units, validity definitions, unknowns and command placeholders. |
| `source-commitments.json` | Original source-analysis/protocol/task/grade-seal hash commitments. |
| `reproduce.py`, `requirements.txt` | Standalone statistical reproduction. |
| `export_from_frozen.py` | Auditable export logic, requiring the separately preserved original frozen inputs. |
| `verification.json` | Export checks, successful reproduction and source-to-table comparison counts. |
| `checksums.json`, `SHA256SUMS` | Per-file SHA-256 and size inventory. |

The complete-pool CSV is the exact sequence of original schedule orders 17–144.
Its 128 rows contain 62/64 strict passes in each arm. The primary CSV is an exact
112-row subset identified by the fixed 28 task IDs. The remaining 16 rows are
descriptive because their eight task IDs had prior exposure. The earlier 15
historical runs and failed pre-bridge assignment 0016 are outside this CSV pool;
their quality is not invented or pooled into the primary result. A separately
certified schema-startup failure did not reach a model request and is retained
in the historical operational ledger rather than duplicated as a model trial.

## Measurement and interpretation

For each primary task, average the two repetitions within each arm, then compute
Memglide minus Codex. The paired t tests use 28 task differences and 27 degrees
of freedom, with a one-sided alternative below zero. The joint rule requires
both p-values at most 0.025, both nominal 95% two-sided interval upper endpoints
below zero, complete integrity and no lower observed Memglide strict-pass count.
The intervals are nominal model-based intervals for this amended, purposively
selected panel. Equal observed correctness counts do not establish equivalence
or noninferiority.

The uniform tariff is
`((input_tokens - cached_input_tokens)*5 + cached_input_tokens*0.20 + output_tokens*15)/1000000`.
It prices native-reported completed-turn counters under a fixed convention.
It is not an invoice, a subscription charge, an account-credit estimate or proof
that every unsuccessful provider request cost zero. Original unknown parser
verdicts remain visible in the CSV; certified effective values are separate.

`workflow_wall_seconds` starts after common source-copy/environment preparation
and includes Memglide indexing, route planning, eligible public verification,
installed launcher preparation, native Codex execution and process cleanup.
It excludes shared source copying, harness hashing/capture, deferred grading,
analysis and operator repair time. `native_wall_seconds` is a nested component,
not the full workflow. Do not add the overlapping component columns together.

All four frozen strict failures concern u21, in both arms and both repetitions.
The public request's word “reject” did not specify whether invalid safeInteger
flags must raise or return false. The private rubric required TypeError. The
published grades remain unchanged; no favorable relabeling is applied.

## What this pack reproduces

The files reproduce the published statistics from attested compact records.
The original analysis SHA-256 is
`fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26`.
That hash names the separately preserved original analysis, **not** either
sanitized summary in this pack; each export has its own published checksum.

Full native transcripts, credentials/auth selectors, private grader code or keys,
and absolute execution-root paths are omitted. Regrading or launching the public
task commands requires the separately preserved fixtures, pinned tooling and
evaluation controls. The task catalog uses documented placeholders instead of
machine-specific locations; it is not presented as a turnkey native rerun.

No new model calls, task selection, source patches or grade changes were made to
produce this publication export.
