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
  --focus src/calculation.py --focus tests/test_calculation.py \
  --preparation-report /absolute/path/preparation.json \
  "Fix the rounding behavior and update its regression coverage." \
  -- --model YOUR_MODEL --json --output-schema /absolute/path/schema.json
```

The equivalent module invocation is
`python -I -m memglide.integrations.codex_preload`. All native `codex exec`
options go after the first `--`; they are forwarded in their original order,
without changing sandbox permissions, approval policy, model settings, or MCP
configuration. `--codex-executable /absolute/path/codex` selects a particular
installed executable; otherwise the launcher searches `PATH`. Executables in the
current Git repository, including symlinks resolving into it, are rejected to
avoid local command shadowing.

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
explanation and JSON envelope; `--max-context-bytes` accepts 1 through 256,000.
Source and applicable ignore-policy hashes are checked again before delivery,
but files may still change afterward; normal Codex reads remain available.

The optional report is atomically written with private permissions before
native execution. It records the decision/reason, original and prepared prompt
hashes, source paths/hashes/line ranges, added context bytes, preparation wall
time and CPU time, actual executable/argv, and delivered stdin hash/byte count.
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
