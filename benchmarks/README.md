# Codex A/B benchmark

This benchmark tests task outcomes and observed Codex usage. It does not infer
token savings from Memglide's estimated context size or claim that MCP transport
tests establish a coding benefit.

## Read the evidence

- `improvements.md` / `improvements.json`: current retrieval fixes, online
  research, tested strategies, exact memory-version acknowledgements, latest
  verification totals and retained performance/ranking regressions.
- `codex-ab-improved.md` / `codex-ab-improved.json`: latest actual Codex attempt
  and every planned run. Authentication still fails before coding.
- `component-comparison-final.md` / `component-comparison-final.json`: paired
  original/final SDK probes, including individual observations and regressions.
- `search-frequency-performance.md` / `.json`: paired local large-index search
  measurements and exact result equivalence; no model calls or cost telemetry.

- `validation.md` / `validation.json`: existing application suites, including
  security, real STDIO MCP, frontend components and production browser workflows.
- `report.md` / `report.json`: the planned A/B experiment, every run slot,
  infrastructure failures, measurements, averages, medians and paired results.
- `component-probe.md` / `component-probe.json`: independent MCP retrieval and
  freshness diagnostics. These are not Codex runs or evidence of A/B savings.
- `tasks.json`: all 24 prompts and declared reference paths/symbols.
- `corpus.py`: offline repository generators, held-out behavioral oracles and
  reference fixes used to verify the graders.

Read a report's status and missing-data explanations before interpreting totals.
The original `report`, `validation`, `assessment` and `component-probe` artifacts
describe the V1 baseline; they are retained rather than rewritten with new results.
An unrun task has no observed success rate, token usage or cost. A network failure
before coding is an infrastructure observation, not evidence that an arm failed
to solve a task.

## Run

From the repository root, use the existing frozen development environment:

```sh
UV_CACHE_DIR="$PWD/.cache/uv" uv sync --frozen
npm_config_cache="$PWD/.cache/npm" npm --prefix frontend ci
UV_CACHE_DIR="$PWD/.cache/uv" uv run python -m benchmarks.run \
  --model gpt-6.1-sol --effort low --repeats 2 --timeout 180
```

Codex must be installed and authenticated, with network access to its configured
model provider. This command makes real model requests and can consume account
usage. The default experiment has **96 planned runs**: 24 tasks × 2 arms × 2
repetitions. `--limit 1 --repeats 1` is a two-run smoke experiment, not the full
benchmark. A timeout is an experimental budget; retain and report timeouts.

Use a fresh `--output /absolute/path` for each experiment. The default writes to
the ignored `.local/benchmarks/<UTC timestamp>/`. Existing output directories are
rejected to preserve evidence. A failed readiness request stops coding runs and
records every remaining slot as `not_run`; it does not issue 96 identical failed
requests. Retry after fixing the recorded prerequisite. Do not use
`--skip-preflight` to conceal an infrastructure failure.

The retained experiment's latest readiness request failed with HTTP 401 and a
Codex token-refresh/sign-in error. A successful `codex login status` alone did
not establish working provider authorization. Refresh the environment's Codex
authentication, or select an existing valid authenticated state with
`--codex-home`; do not put a token in chat or checked-in files. Earlier diagnostic
attempts also encountered a read-only state directory and a proxy HTTP 403.
Those failures are retained separately from the final reproducible preflight.

The managed environment can provide authentication in a read-only `CODEX_HOME`.
The runner creates fresh writable state for each invocation and references only
the existing `auth.json` binding by symlink. It does not copy credential values or
edit user configuration. `--codex-home` can select an existing authenticated
directory if needed. Never put credentials in benchmark artifacts.

Run offline harness verification separately from the live experiment:

```sh
UV_CACHE_DIR="$PWD/.cache/uv" uv run pytest tests/test_benchmark_*.py
UV_CACHE_DIR="$PWD/.cache/uv" uv run python -m benchmarks.probe \
  --artifacts "$PWD/.local/benchmarks/component-$(date -u +%Y%m%dT%H%M%SZ)" \
  --output "$PWD/.local/benchmarks/component-report-$(date -u +%Y%m%dT%H%M%SZ)"
```

Unit-test fake CLI streams and reference fixes are verification fixtures. They
must never be merged into live benchmark results.

## Experimental protocol

A uses Codex without an MCP server. B uses the same executable, explicit model,
reasoning effort, sandbox, structured response schema and prompt, with only the
Memglide MCP server added. Both ignore user configuration and rules and disable
hosted apps and web search. The shared prompt conditionally instructs use of
Memglide when available. This tests enabled, instructed use rather than voluntary
tool adoption.

Each run starts in a fresh detached Git worktree at its language repository's
recorded immutable commit. The run order is seeded, and each task's arm order
reverses on its second repetition. Python, TypeScript and test tools are shared
installed versions, without per-run dependency downloads. Each B run has a fresh
index/database and no previous task memory. Necessary B initialization is
reported separately and included in end-to-end timing. Independent diagnostic
queries must not warm the model's treatment database.

Provider prompt caches and the host filesystem cache cannot be reset reliably.
Order balancing and observed cached input tokens help describe this limitation;
they do not prove identical cache hits. There is no simultaneous competition
between live runs. Local process resource measurements remain subject to other
host activity.

The tasks cover twelve maintenance families in both Python and TypeScript: TTL
boundaries, LRU eviction, cursor pagination, optimistic revisions, authorization
scope, path containment, graph closure, retry policy, feature flags, search
conjunction, integer billing and idempotency. They use two small, synthetic,
multi-module document-service repositories. They are controlled correctness
tasks, not a representative sample of all production work. The translated task
families are correlated; 24 task IDs do not imply 24 independent domains.

Every baseline is required to fail its held-out behavioral oracle while passing
its smoke tests and, for TypeScript, strict compilation. Each reference fix must
pass the oracle and smoke checks. Model self-reported completion is ignored.
Existing tests, build configuration and Git metadata are protected; changes and
grader logs are retained. Hidden oracles live outside the worktree. Isolation is
procedural, not cryptographic: the host filesystem can expose benchmark tooling,
so prompts prohibit inspecting it and command logs/diffs must be audited.

## Measurement limits

- Tokens come only from supported `codex exec --json` completed-turn usage.
  Incomplete or malformed streams do not become complete totals. The final
  `--output-schema` response contains a summary, not authoritative telemetry.
- MCP events establish actual observed invocation, including failures. A valid B
  treatment additionally needs successful context retrieval; merely configuring
  a server does not establish use. Event streams and call status are retained.
- Codex's JSONL does not expose underlying model/API request count or provider
  invoiced cost. Those fields stay null. ChatGPT subscription usage is not a
  per-request API invoice. Any separately supplied verified price calculation
  must remain distinct from actual billed cost.
- Cost per successful task includes costs of unsuccessful attempts in its
  numerator. It is undefined when costs are missing or no task succeeds.
- Literal read commands provide only a limited command-intent proxy. They cannot
  establish exact repeated file reads, identical byte ranges or filesystem cache
  hits. Exact repeated reads stay null; the separate command proxy is not a
  guaranteed lower bound on actual I/O. Missing complete tracing is disclosed,
  not estimated as measured fact.
- `/proc` sampling measures local observed process CPU and summed RSS. Short-lived
  children may escape sampling; shared RSS pages can be counted more than once.
  Sampled CPU is a lower bound and sampled peak RSS is not exact peak private
  memory. Remote model CPU/memory are unavailable.
- Context coverage is the fraction of declared oracle target files/symbols
  returned by an independent query. It is a proxy, not proof of all semantically
  necessary context. Source hashes and controlled edits can test freshness.
  These diagnostics cannot establish what the model attended to or understood.

Fresh databases test context retrieval and its initialization overhead. This
experiment does not test benefits from reusing previously saved task memories.
A separate longitudinal experiment with matched prior task histories would be
needed for that claim; its warm-up cost must also be counted.

All attempted runs, invalid treatments, failed grades, timeouts, missing metrics
and excluded pairs remain visible. Comparisons must consider success and cost
coverage before making any savings claim.
