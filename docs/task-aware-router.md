# Task-aware source routing, version 2

The opt-in launcher can discover source from a coding task without caller-selected
paths. Version 2 compares verified body identifiers, declarations, paths and
repository-local term frequencies. It does not predict model savings, infer hidden
agent context or automatically add memory. Existing explicit source preparation
and normal MCP/API workflows remain available.

```sh
uv run memglide-codex --discover --selection-policy v2 --project PROJECT_ID \
  --preparation-report /private/preparation.json \
  'Correct rounding of fractional invoice subtotals.' -- --json
```

`--discover` is required for `--selection-policy`; its default is v2. Python callers
use `prepare_task_prompt(..., enabled=True, selection_policy="v2")`. The overall
API remains disabled by default. `selection_policy="v1"` and the matching launcher
flag reproduce the previous automatic policy. The historical runner explicitly
pins v1; previous reports, tasks and original revisions remain preserved.

## What the gate checks

The previous gate compared declaration matches with every natural-language task
term and used a ratio of saturated ranking scores for ambiguity. On its first
held-out cohort it delivered nothing on 12 tasks. Version 2 changes the evidence
model rather than lowering that threshold:

- Retain the existing FTS/symbol/path candidate generator and secure full refresh.
- Inspect every eligible candidate or decline: at most 24 files and 2 MiB total.
  A saturated generation pool, unsupported language or incomplete inspection
  cannot silently become a confident choice.
- Separate verified code identifiers from comments and literal text. Python uses
  bounded token streaming; JavaScript/TypeScript/TSX uses pinned Tree-sitter
  grammars in one isolated trusted worker batch. No repository code is executed.
- Combine project document frequency and observed candidate identifier frequency.
  Terms absent from repository evidence do not dilute a metadata denominator.
  Both code and metadata channels contribute to non-explicit selections.
- Compare distinct evidence and independent competitors rather than treating a
  raw ranking-score margin as calibrated confidence. Ambiguous evidence declines.
- Prepare the complete anchor and bounded direct production helpers through the
  existing source-only delivery API. Required bodies are never clipped to fit.

These are deterministic lexical heuristics. They do not prove semantic relevance,
rule usefulness or dependency completeness. Ordinary agent tools and tests remain
available after preloading or fallback. `FULL_SOURCE` means the complete selected
bundle, not the entire repository.

## Safety and measured work

Approval, ignores, secret exclusions, symlink/safe-path rules, complete-file size
budgets and indexed/current hashes remain authoritative. Every inspected body,
including a losing candidate, is checked again with its policy before source is
released. Missing state, partial indexes, stale source, races, worker faults,
unsupported syntax and insufficient evidence return the original task exactly.

The syntax worker ignores indexed working directories and `PYTHONPATH`, imports
the trusted application and installed grammars, and emits only bounded matched
query terms. Its limits include 24 files/2 MiB source, 13 MiB serialized input,
200,000 nodes, 200 ms native parse per file, a three-second internal batch budget
and a five-second parent timeout. Syntax errors and missing nodes decline the
whole selection. These limits do not make the complete preparation path a hard
latency guarantee: full scanning, Git and database waits retain their own costs.

Worker startup, body inspection, secure refresh and verification are real local
work, including when selection declines. Private receipts distinguish v1/v2,
decisions, evidence, current selected versions, added bytes/token proxies and
phase/overall timings. Parent CPU excludes parser/Git children; the benchmark
records waited-child CPU separately. No missing resource counter is assumed zero.

The shared identifier normalizer now uses fixed-width acronym/camel boundaries,
preserving ordinary token semantics while avoiding repeated suffix scans on long
uppercase source identifiers. A process-bounded large-identifier regression covers
that resource failure independently of the routing policy.

## Memory and evaluation

Automatic warm-memory injection stays disabled. Fresh source hashes do not prove
a saved rule is true, absent from the supplied source, or useful to the task.
Existing explicit memory features are preserved. Experimental excerpts remain a
separate incomplete-file API, excluded from this source-routing treatment.

[Research and security review](../benchmarks/router-v2-research.md) records the
mechanisms, resolved defects and current pricing verification. The
[fresh protocol](../benchmarks/automatic-v2-protocol.md) freezes independent tasks,
grading and settings before offline B/C/V1 selection and any A/B/C model study.
Known-path B is an oracle baseline with unmeasured human path-discovery cost.
Identical-prompt controls must be reported separately; their stochastic/cache
variation cannot establish improved source selection. API-price equivalents
remain estimates, distinct from actual billing.
