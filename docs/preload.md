# Optional focused context before Codex starts

`memglide-codex` prepares complete, explicitly selected source files locally and
then replaces its own process with one installed `codex exec` process. It never
asks a model whether to retrieve, starts no Memglide MCP server, and performs no
repository scan or indexing during preparation. This is an experimental option;
lower tokens, lower cost, and lower latency require measured comparison.

Approve and index the repository once using the existing CLI. Keep the returned
project ID:

```sh
memglide --db /absolute/path/memglide.db project add /absolute/path/repository
```

Use the launcher from the coding repository, supplying a registered project and
the source paths you already know are relevant:

```sh
memglide-codex --db /absolute/path/memglide.db --project PROJECT_ID \
  --focus src/calculation.py \
  --preparation-report /absolute/path/preparation.json \
  "Fix the rounding behavior and update its regression coverage." \
  -- --model YOUR_MODEL --json --output-schema /absolute/path/schema.json
```

When the relevant existing tests or configuration are already known, optionally
include their complete files with `--support`:

```sh
memglide-codex --db /absolute/path/memglide.db --project PROJECT_ID \
  --focus src/calculation.py --support tests/test_calculation.py \
  "Fix rounding, update regression coverage, and run python -m pytest tests/test_calculation.py." \
  -- --model YOUR_MODEL --json
```

Up to eight focus and four support paths are accepted. Support files must pass
the same approval, indexing, current ignore-policy, secure-read and source-hash
checks as focus files. They share the existing total context cap; an unavailable
or oversized support file discards the entire addition. Support never discovers
tests, selects or executes a test command, or replaces the focus requirement.
Keep the intended validation in the ordinary task; native Codex decides which
commands to run. Source-only remains the default. The support option is an
experiment to reduce subsequent investigation, not an established saving. See
the [efficiency architecture](efficiency-architecture.md).

The equivalent module invocation is
`python -I -m memglide.integrations.codex_preload`. All native `codex exec`
options go after the first `--`; they are forwarded in their original order,
without changing sandbox permissions, approval policy, model settings, or MCP
configuration. `--codex-executable /absolute/path/codex` selects a particular
installed executable; otherwise the launcher searches `PATH`. Executables in the
current Git repository, including symlinks resolving into it, are rejected to
avoid local command shadowing.

The launcher defaults to `--context-format compact-prefix`: one canonical JSON
source envelope comes **before** the task, followed by exactly `\n\nTask:\n` and
the original task text. The envelope contains a short untrusted-source notice
and sorted, unique source paths with complete file content. SHA-256 values and
line ranges remain in private validation metadata; they are checked locally
without repeating them in the model-visible source envelope. JSON escaping
preserves the decoded source exactly.

Use `--context-format legacy` to reproduce the earlier layout: original task
first, followed by the longer explanation and source JSON including hashes and
line ranges. The Python `prepare_prompt` API still defaults to `legacy` for
compatibility; API callers must explicitly request `context_format="compact-prefix"`.
The existing ordinary-task benchmark runner explicitly selects `legacy`, so its
completed 80-run report is historical evidence for that layout, not a measurement
of the new default.

Putting stable source before a changed task preserves common prompt bytes and
removes avoidable envelope text. It does not establish a cache boundary: both
remain inside one changing native user message. The newer provider guide
describes eligible message-ending breakpoints, while the inspected installed
Codex CLI exposes no arbitrary multiple-message or explicit-breakpoint input.
Native request construction and backend state remain outside this wrapper's
control. See the [efficiency research](../benchmarks/efficiency-research.md) for
the current scoped findings and the [earlier cache research](../benchmarks/cache-refinement-research.md)
for the preserved diagnosis. Neither layout proves a token or cost saving.

Omit the positional prompt, or use `-`, to read its UTF-8 text from stdin. With a
positional prompt, that argument is the entire task input; additional piped stdin
is not appended. Prepared text is delivered through a private temporary file on
native Codex stdin, using its supported `-` prompt form. Source text is not put
in process arguments, and large context does not depend on pipe-buffer or
per-argument limits. Codex still receives the source as model context.

`--mode auto` is the default. It prepares only when the caller explicitly names
an existing approved project and indexed source paths. `--mode off`,
`--context-supplied`, missing focus paths, or a missing project ID forward the
task unchanged without opening Memglide state or importing its services, MCP
SDK, or parser. The `--context-supplied` flag is a caller assertion, not a test of
what Codex understands. Omitting useful context can still increase later reads
or reduce correctness, so those decisions need evaluation.

`--mode preload` explicitly requests the same scoped preparation. Unsafe,
excluded, unindexed, changed, unavailable, or oversized files cause a complete
fallback to the original task, with an explicit reason in the report and a
stderr diagnostic for this mode. Files are never silently clipped or partially
selected. Invalid arguments or malformed preparation metadata stop the launch
with a nonzero exit status. The default 12,000-byte limit covers the entire added
notice/explanation, JSON envelope and format separator;
`--max-context-bytes` accepts 1 through 256,000.
Source and applicable ignore-policy hashes are checked again before delivery,
but files may still change afterward; normal Codex reads remain available.

The optional report is atomically written with private permissions before
native execution. It records the decision/reason, original and prepared prompt
hashes, source paths/hashes/line ranges, added context bytes, preparation wall
time and CPU time, actual executable/argv, and delivered stdin hash/byte count.
Compact-prefix reports also record `context_format="compact-prefix"` and
`prompt_layout="source_prefix"` (or `unchanged` for a bypass), using report
version 2. Legacy forwarding reports retain their version 1 shape.
Explicit `--support` requests use version 3 in either format and record separate
private `focus_paths` and `support_paths`, including for a bypass. Leaving support
empty preserves the existing source-only prompt bytes and report shape.
It does not duplicate source text or capture authentication/configuration
values. `native_exec_boundary_monotonic_seconds` is sampled before the report
write and exec handoff, so a runner's derived native interval also includes
that small handoff cost. Preparation timings alone omit Python startup and
native execution; compare complete end-to-end runs as well. The report records
preparation, not successful model execution or task completion.

Use this launcher as an alternative to the Memglide MCP integration for the
same work. Existing native configuration is intentionally preserved: if your
Codex configuration already registers Memglide MCP, Codex can still start it.
Manage that choice explicitly in your normal Codex profile/configuration; the
launcher does not silently disable any registration. Native Codex inherits the
existing authentication, proxy, CA trust, and environment without copying or
printing credential contents.

Both formats securely read current source and recheck policy/source hashes;
neither reuses stale file contents, pads requests to trigger caching, invents a
cache parameter, changes session IDs or makes a model call to decide retrieval.
The compact format is a versioned layout refinement. The
[20-pair measured comparison](../benchmarks/cache-refinement-assessment.md)
found lower full execution time but higher uncached input. The overall input
decrease came from identical-prompt controls, so it does not establish a token
or cache benefit from the layout. Cost savings remain unproven.

For related work in an existing native thread, preserve Codex's own history
instead of starting a fresh thread just to resend unchanged evidence. The
installed CLI supports `codex exec resume SESSION_ID -`; the launcher forwards
that native subcommand too:

```sh
memglide-codex --context-supplied "Continue the related task." \
  -- resume SESSION_ID --json
```

Use `--context-supplied` only when the existing context actually contains the
needed evidence; it is an explicit assertion, not a freshness check. Changed or
missing files still need normal reads or a fresh approved bundle. Resuming keeps
native session handling intact, but does not guarantee cache hits or lower cost.

Resumed-session cost accounting needs separately verified cumulative or per-turn
usage. The estimator rejects resumed or multi-turn traces whose usage scope is
not verified; summing possibly cumulative totals can double-count cost.
