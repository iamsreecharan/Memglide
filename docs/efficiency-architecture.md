# Efficient source delivery and reliable retrieval

The latest architecture changes target observed work left after source delivery:
native Codex still inspected existing tests in all eight focused tasks of the
previous cost comparison. Source delivery removed recognized production-source
read commands, but did not establish cost savings. The
[140-run trace diagnosis](https://github.com/iamsreecharan/Memglide/blob/8acc8af/benchmarks/efficiency-diagnosis.md) preserves each
cohort separately; the [research ledger](https://github.com/iamsreecharan/Memglide/blob/8acc8af/benchmarks/efficiency-research.md)
records primary sources, exact reading scopes and uncertainty.

The implementation keeps the cheap source-only path and adds explicit supporting
files as an optional experiment. It also fixes retrieval lifecycle and
invalidation defects without replacing live freshness checks with caches.
Implementation correctness and measured model efficiency are separate claims.

## Complete evidence, selected locally

The launcher accepts up to eight `--focus` paths and four `--support` paths for
already known tests, configuration or other relevant source. Both use the same
approved project and indexed eligibility, current ignore policy, secure complete
file reads, secret checks and final policy/source-hash rechecks. The combined
bundle must fit the existing 12,000-byte default addition cap. An unsafe,
unavailable, unindexed, changed or oversized requested file discards the entire
addition; the original task then remains available to normal native discovery.

```sh
memglide-codex --db /absolute/path/state.db --project PROJECT_ID \
  --focus src/totals.py --support tests/test_totals.py \
  "Fix totals, add regression coverage, and run python -m pytest tests/test_totals.py." \
  -- --model YOUR_MODEL --json
```

The test command belongs to the original task. Preparation does not discover or
execute tests, interpret shell commands, import repository code, summarize files
or call a model to select evidence. Repository contents remain untrusted source
data. There is no automatic test expansion or instruction telling Codex to skip
other required evidence or validation.

Support files do not replace the focus requirement. Off, caller-context supplied,
missing focus and missing project still return the original task using only the
standard library and without opening state. Empty support preserves previous
prompt bytes and report schemas. Explicit support requests use report version 3
and private focus/support classifications, including on a bypass; source-only
legacy and compact reports retain versions 1 and 2. The
[launcher guide](preload.md) describes full argument and transport behavior.

## Preserve native context honestly

Compact JSON removes redundant model-visible metadata and keeps complete source.
It does not create a separate provider message: source and changing task are one
native user message. Current provider documentation describes eligible message
endings as cache breakpoints. A common leading substring alone does not establish
a reusable endpoint, and the inspected installed CLI has no arbitrary
multiple-message or explicit-breakpoint prompt option.

Native manual continuation remains supported. `--context-supplied` is a caller
assertion that needed evidence is actually available, not an automatic receipt
based on an old source hash. Compaction can remove context, and source can change.
No session-ID override, stale source cache, padding or automatic history omission
is introduced. Resumed or multi-turn traces need verified usage scope before
cost estimation; unverified possibly cumulative usage is rejected rather than
summed as though it were incremental.

## Retrieval correctness without unnecessary reads

The full retrieval and memory API remains separate from preload. Its current
changes address defects found during the broader review:

- Passport invalidation compares exact selected source references, verified
  source hashes and selected-memory dependencies. A path mentioned only in a
  query or warning, or contained inside another filename, no longer falsely
  invalidates unrelated evidence. Selected changed evidence still becomes stale.
- Retrieval, its passport, event and session activity update commit under the
  active-session write gate. A session that ends or expires during preparation
  cannot receive a late committed retrieval or TTL extension. A failure rolls
  back the unit of work.
- Context assembly filters stored memory metadata for relevance before doing
  live source freshness reads. Eligible claims retain the same freshness checks;
  public memory recall behavior remains independent. This avoids validating
  irrelevant source evidence without treating cached state as current source.

A local regression fixture reduced source-reader calls from 55 to 15, with 1,200
checked old/new context outputs matching. Those are component observations, not
model tokens, dollar savings or a claim of universally faster retrieval.

## Promotion requires a matched comparison

Source-only remains the default. The optional support workflow must earn
promotion on fresh tasks, rather than being tuned to the prior eight cases.
The [three-arm protocol](../benchmarks/workflow-protocol.md) declares ten fresh
Python/TypeScript tasks, three arms and two repeats: 60 native assignments.
A is bare Codex, B is source-only Memglide and C adds complete supporting files.
All arms receive the same task, source/support path hints and test-command argv.
Two provided-context controls must bypass unchanged in both Memglide arms.

The predeclared promotion gate requires C's focused-task estimated cost and full
time, both mean and median, to be no worse than both A and B overall and in each
repeat, while retaining task success, complete retrieval and freshness. A gate
failure keeps support experimental and optional. All attempts, failures,
outliers and controls must remain visible; provided-context controls cannot prove
that retrieval saves money. This document states the design and gate, not an A/B
outcome.

Actual billing remains unavailable without attributable charges. API
price-equivalent estimates use observed categories and cited rates, keep failures
in cost per successful task, and disclose cache-write uncertainty. Cached input
is already included in total input, and reasoning is already included in output.
Unavailable model-call counts, filesystem reads and server resources stay
unknown. Neither a smaller envelope nor fewer read-command mentions alone proves
lower cost.
