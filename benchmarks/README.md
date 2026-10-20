# Benchmarks

This directory contains the experiment runners and their fixed inputs. Start
with the [research overview](../research/README.md) for the paper, latest
comparison, uncertainty and downloadable evidence.

The runners measure task outcomes and observed agent usage. Context-size
estimates, local retrieval speed and successful MCP transport checks do not
establish model-token savings or a coding benefit.

## Directory contents

| Files | Purpose |
| --- | --- |
| `run*.py`, corpus builders, analysis and packaging helpers | Historical and current experiment implementations. |
| `tasks*.json`, grading, provenance, control and holdout manifests | Fixed experiment inputs; keep their bytes and identifiers intact. |
| `automatic*-fixtures/` | Pinned upstream source/test fixtures with their own licenses. They are required for reproduction and corpus checks. |
| `*protocol*.md` and `refinement_protocol.json` | Prespecified designs, including older superseded experiments. |
| `cost-pricing.json` | Fixed accounting inputs, not a live provider-price feed. |
| Seven retained historical reports | Inputs to budget estimation and frozen-manifest regression tests. |
| [Evidence archive index](evidence/README.md) | Access to generated outputs removed from the active source listing. |

The seven retained reports are `warm-80-analysis.json`,
`codex-workflow-ab.json`/`.md`, `workflow-assessment.json`/`.md` and
`workflow-contract-issue.json`/`.md`. Their presence is a test dependency, not an
indication that they describe the latest result.

## Local verification

From the repository root, install the pinned Python and frontend dependencies:

```sh
uv sync --frozen
npm --prefix frontend ci
uv run pytest tests/test_benchmark_*.py tests/test_corpus_*.py
```

Put `frontend/node_modules/.bin` on `PATH` when a corpus check needs `tsc`, as CI
does. These tests verify harness behavior and controls. Fake CLI streams and
reference solutions are fixtures, not live model observations.

## Native experiments

Native runs need Codex installed and authenticated, working access to its
configured model provider, and available account usage. A successful login
status alone does not verify a working model request. Runners can execute code
and consume account usage; inspect the chosen protocol and options first.

Use a fresh output directory under `.local/` for each experiment. Preserve
failed readiness requests, timeouts, missing usage and all planned run slots.
Do not overwrite a frozen result, discard failed arms, or change the scoring to
obtain a desired finding. A provider failure is distinct from a task failure.

The [router coding protocol](router-coding-protocol.md) and
[automatic v4 protocol](automatic-v4-protocol.md) belong to earlier studies;
they do not describe the latest paper comparison. Use the complete paper
capsule for its exact installed-system protocol and reproduction instructions.
Historical defaults may require reports from the
[pre-cleanup archive](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks).

## Evidence retention

Generated reports, copied run repositories, logs and duplicate ZIP/PDF bundles
are excluded from new source commits. Their old bytes remain in Git history;
the paper and final evidence are published separately. See the
[archive index](evidence/README.md) for recovery links and scope. Keep credentials,
authentication state and local databases out of research artifacts.
