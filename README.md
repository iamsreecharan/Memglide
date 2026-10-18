# Memglide

**Remember what matters. Retrieve what's needed. Verify what's missing.**

Memglide is a local context service for coding agents. It indexes approved Git repositories, stores expiring task memories, retrieves current source under an estimated token budget, and returns a **Context Passport** showing selected evidence, source versions, unresolved relationships, and suggested inspections.

The operating loop is **REMEMBER → SELECT → VERIFY → EXPAND**. Python AST and Tree-sitter supply structural evidence for Python, JavaScript, TypeScript, and TSX. SQLite FTS5 provides deterministic text search for other UTF-8 source. The CLI, local React dashboard, HTTP API, and official MCP STDIO server use one application service layer.

Memglide requires no cloud database, embedding service, LLM API, Redis, or Docker. Repository data stays in local files and SQLite. An external agent you connect can have its own data handling and billing rules.

## Install from this checkout

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), Node.js 24.x at 24.15+ with npm (or 22.x at 22.22.2+), and Git. Use a terminal in the repository root:

```sh
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run python scripts/bundle_frontend.py
uv run memglide doctor
```

These commands build the production dashboard into the Python package. Python-only source development works before bundling; serving the dashboard requires that build. See the [installation guide](docs/installation.md) for Windows/PowerShell, macOS, Linux, WSL, and local wheel installation.

## Run locally

```sh
uv run memglide project add /absolute/path/to/your/git-repository
uv run memglide project list
uv run memglide session start PROJECT_ID --task "Investigate authentication"
uv run memglide search PROJECT_ID authenticate_user
uv run memglide context SESSION_ID authenticate_user --level 2 --budget 4000
uv run memglide serve
```

Use the IDs returned by the previous commands. Open **http://127.0.0.1:8765**. OpenAPI is available at `/docs`. Keep the service on loopback. Registration explicitly approves a local repository for indexing; choose roots carefully.

Sessions expire after 60 minutes of inactivity, capped at eight hours by default. Polling status does not keep a session alive. Expired task records are removed by cleanup; the repository index persists until you remove the project. No deletion operation removes source files.

## Connect Codex

With a working Codex CLI installation:

```sh
uv run memglide setup codex
codex mcp get memglide --json
```

The setup command registers the local STDIO command and refuses to overwrite an existing `memglide` entry. It does not change another server's configuration. See [MCP and Codex](docs/mcp.md) for manual configuration, available tools, verification, and optional agent instructions.

An MCP server controls context returned by its tools. It cannot remove or rewrite Codex conversation history or access hidden model reasoning. A smaller retrieval response does **not** establish a reduction in total billed model tokens.

An optional [project-bound agent profile](docs/mcp.md#optional-project-bound-agent-profile)
offers two tools, compact source responses and on-demand freshness verification.
Register it with `uv run memglide setup codex --project PROJECT_ID` after approving
that repository. Existing Codex registrations are preserved; inspect them before
deliberately switching profiles. The full fourteen-tool interface remains the default.

For tasks with known source paths, the optional [focused Codex launcher](docs/preload.md)
can prepare complete files locally before the first native request:

```sh
uv run memglide-codex --project PROJECT_ID --focus src/calculation.py \
  "Fix the rounding behavior." -- --json
```

It uses an existing approved index, makes no auxiliary model request, and forwards
the original task when preparation is skipped or unsafe. `--context-supplied`
skips state access when the caller already supplied the source. Existing native
settings and MCP registrations are preserved. See the [architecture and research
limits](docs/daily-architecture.md) and [matched experiment protocol](benchmarks/daily-protocol.md);
preparation alone does not establish a token, speed or cost benefit.

## Verify and develop

```sh
uv run pytest
uv run ruff check .
uv run mypy src
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for browser tests and packaging. [PROGRESS.md](PROGRESS.md) records observed validation and outstanding limitations; source-file presence alone is not a completion claim.

The latest [optimized A/B assessment](benchmarks/optimized-ab-assessment.md) and
[individual results](benchmarks/codex-ab-optimized.json) cover **40 fresh coding
tasks, four purpose-built repositories and two repeats: 160 runs** using native
`codex exec`. Both configurations passed 80/80; all 80 Memglide runs actually
retrieved source through MCP. Memglide used **32.8% more total input tokens** and
took **17.9% longer including indexing** on average. Uncached input increased
2.2%, while output increased 5.3%; cached input is included in total input.
There is no demonstrated task-success, token or speed advantage on this corpus.
Billed cost and cost per successful task remain unavailable.

The implementation passed [623 distinct application and tooling checks](benchmarks/optimization-validation-v2.md),
including frontend, production-browser, security and actual MCP integration.
[Research and rejected alternatives](benchmarks/optimization-research-v2.md),
[retrieval component measurements](benchmarks/optimization-component-v2.md),
[body-completeness checks](benchmarks/compact-quality-v2.md) and
[live context observations](benchmarks/codex-optimized-context.md) document the
changes and their limits. Component gains do not establish a Codex efficiency
gain. The [downloadable report bundle](benchmarks/memglide-ab-optimized-report.zip)
includes the reports and raw evidence. Earlier experiments below remain historical.

The [Codex A/B benchmark](benchmarks/README.md) provides 24 Python/TypeScript tasks,
isolated runs, independent grading and conservative telemetry. The retained
[Markdown report](benchmarks/report.md) and [JSON report](benchmarks/report.json)
record the original authentication-blocked live experiment. The
[retrieval improvement assessment](benchmarks/improvements.md) and
[JSON evidence index](benchmarks/improvements.json) cover the subsequent fixes,
strategy comparisons, performance measurements and retained regressions.
Declared-target coverage in independent MCP probes improved from 16/24 to 24/24.
The [earlier refinement assessment](benchmarks/refinements.md) records subsequent
performance, lifecycle and dashboard fixes, including failed retrieval cases and
reused validation after correcting selection defects. The
[earlier Codex attempt](benchmarks/codex-ab-refined.md) retains the original
authentication failure. Device login subsequently enabled a real comparison:
the [authenticated A/B assessment](benchmarks/live-ab-assessment.md),
[individual runs and statistics](benchmarks/codex-ab-authenticated.md) and
[JSON results](benchmarks/codex-ab-authenticated.json) cover 24 tasks, two arms
and two repeats. A passed 48/48; B passed 47/48, with one infrastructure
interruption retained as ungraded. A separate retry passed and remains separate.
Across 47 verified pairs, B used 2.75 times the input tokens and took 46.5% longer
including fresh indexing. This experiment does not support a token, speed or
coding-completion benefit. Billed cost and cost per successful task are unavailable.
[Observed context results](benchmarks/codex-live-context.md) distinguish declared
target coverage from unmeasured semantic completeness and independent freshness.

## Documentation

- [Architecture and storage](docs/architecture.md)
- [Installation and packaging](docs/installation.md)
- [Workflow and retrieval smoke comparison](docs/usage.md)
- [MCP and Codex integration](docs/mcp.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Security policy](SECURITY.md)
- [Known limitations](docs/limitations.md)
- [V2 evaluation plan](docs/v2.md)

The [authentication fixture](examples/auth_repository/) supplies Python/FastAPI and React/TypeScript evidence with intentionally unresolved references for local testing. License: [MIT](LICENSE).
