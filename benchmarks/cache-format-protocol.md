# Fresh-task comparison: Memglide legacy (A) versus compact-prefix (B)

The primary question is whether a smaller, stable source prefix improves the
cached/uncached token and latency tradeoff relative to the original Memglide
layout. **Neither configuration is standard Codex.** The preserved earlier
80-run standard-Codex/Memglide experiment remains a separate experiment.

## Cohort and assignments

Twenty fresh tasks are authored after both source formats are fixed: ten Python,
ten TypeScript, four purpose-built repositories with five tasks each. Eight tasks
name one source file, eight name two interacting sources, and four already supply
their complete relevant source. The caller-visible focus paths appear in the same
common task prompt for both arms. Hidden oracle fields never choose sources.

One repeat yields forty original assignments and twenty matched pairs. Tasks are
seed-shuffled, with alternating pair order: exactly ten pairs run A first and ten
run B first. Independent graders validate baseline failures, reference fixes,
protected smoke tests and partial-fix negative controls before native execution.
No actual model requests, outcome-driven source selection or byte-budget tuning
use these fresh cases before the frozen comparison.

Explicit `--corpus daily` is available solely for development/fake-native tests on
the earlier tasks. Such reports are labelled reused development evidence, never
fresh confirmation. The primary defaults to `--corpus cache` and `tasks_cache.json`.

## Matched configurations and deliberate difference

- **A = Memglide legacy:** the original task precedes complete source JSON with
  per-file path, hash and line ranges, plus the original explanation.
- **B = Memglide compact-prefix:** sorted complete source path/content JSON and a
  concise untrusted-data notice precede the exact original task. Hashes and ranges
  remain in private preparation metadata rather than model-visible context.
- Both use the same native Codex executable/version, `gpt-6.1-sol`, effort `low`,
  supported JSON events and structured final schema, workspace-write sandbox,
  global approval `never`, disabled apps/web search and an empty MCP map.
- Both receive fresh isolated worktrees at matched repository commits, writable
  native state and production-approved cold indexes/databases. Both skip approval,
  indexing and retrieval on the four caller-context-supplied tasks, forwarding the
  exact common prompt. Source context is capped at the same 12,000 added UTF-8 bytes.
- Authentication references the same existing binding by symlink. Credential
  values are never read, printed or copied. There is no auxiliary model decision,
  MCP server, watcher or implicit paid readiness request.

Both formats preserve complete source and source-security checks. The experiment
changes source layout, source ordering and model-visible metadata together; it does
not isolate these components causally. Common task-prompt hashes and commits match;
actual model-prompt hashes intentionally differ on source-preload tasks. An
independent renderer rebuilds each exact native prompt from frozen Git bytes and
compares hashes/byte lengths with the launcher's private-stdin record. Assigned
scoped tasks require actual complete-source preparation; a fallback remains an
original invalid-treatment observation, never an omitted case.

## Measurement and interpretation

Record every original run, native input/cached/uncached/output tokens, wall time,
command proxies, local CPU/RSS, grade, native execution validity and delivery
fidelity. Full execution time includes **both arms'** required cold approval/index,
launcher and native process, excluding worktree creation and external grading.
Native timing uses an observed monotonic handoff boundary and includes report-write
and exec handoff. Parent index CPU is separate; parent index RSS is not sampled.

Fresh local state cannot reset OS or provider caches. Observe cached input rather
than treating cache conditions as controlled or cached tokens as free. Cached
input is part of total input. The primary aggregate includes all original attempts
and failures; supplied-context/source-preload strata are descriptive.

Successful completion requires a valid completed native invocation, thread/turn
framing, final `summary`/`tests_run` schema, passing external behavior grade, and
valid format delivery. Behavior-grade passes on failed executions are counted
separately. Actual billing, exact underlying model calls and actual filesystem
reads remain null when unavailable. Read-command proxies are not actual file I/O.
Cost per successful task cannot be reported as a measured dollar value without
complete applicable cost data, including failed attempts.

Source hashes attest delivered starting bytes, not semantic understanding or
freshness after Codex's edits. Small synthetic tasks and one repeat do not establish
production-scale, cross-session, statistical or monetary benefits. A reduction in
payload bytes does not prove token, cache, latency or cost improvement. Each fresh
task has a distinct focus set and one repeat; the experiment does not directly test
cross-task prefix reuse over unchanged identical source files. Do not compare this
new cohort directly with the old standard-Codex arm as a matched test.

## Freeze, failure preservation and execution

Before any primary request, freeze the fresh corpus/manifest, all runtime Python,
all shared runner/telemetry/grading helpers (including transitive corpus helpers),
new runner, common prompts, settings, CLI identity and Git HEAD. Root alone launches
native requests after the complete validations and freeze commit.

```sh
uv run python -m benchmarks.run_cache_formats \
  --corpus cache --tasks benchmarks/tasks_cache.json \
  --output NEW_DIRECTORY --repeats 1 --seed 20261018 --timeout 180 \
  --codex-home EXISTING_AUTH_DIRECTORY --model gpt-6.1-sol --effort low
```

Format-aware immutable starts mark setup wall/CPU as unknown for both focused
formats until durably measured, while caller-context bypasses record known zero
setup. Both starts carry explicitly unknown treatment/native validity; interruption
cannot turn missing A setup into a zero-overhead observation.

Atomic fsynced checkpoints, immutable starts/results, a hash-chained attempt log
and the existing child identity/parent launch-grant protocol precede requests.
Resume validates frozen source/settings, saved plan and terminal state projections
against sealed records, stops exact orphan process identities, retains interrupted
originals with unknown complete usage/outcomes, then continues only pending slots.
No original is retried or overwritten. Shared auth/quota/network or source-guard
failures leave remaining slots explicitly unrun. Finished resume is read-only.
