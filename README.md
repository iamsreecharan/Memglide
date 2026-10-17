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

## Verify and develop

```sh
uv run pytest
uv run ruff check .
uv run mypy src
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for browser tests and packaging. [PROGRESS.md](PROGRESS.md) records observed validation and outstanding limitations; source-file presence alone is not a completion claim.

The [Codex A/B benchmark](benchmarks/README.md) provides 24 Python/TypeScript tasks,
isolated runs, independent grading and conservative telemetry. The retained
[Markdown report](benchmarks/report.md) and [JSON report](benchmarks/report.json)
record the original authentication-blocked live experiment. The
[retrieval improvement assessment](benchmarks/improvements.md) and
[JSON evidence index](benchmarks/improvements.json) cover the subsequent fixes,
strategy comparisons, performance measurements and retained regressions.
Declared-target coverage in independent MCP probes improved from 16/24 to 24/24.
The [current refinement assessment](benchmarks/refinements.md) records subsequent
performance, lifecycle and dashboard fixes, including failed retrieval cases and
reused validation after correcting selection defects. The
[latest Codex attempt](benchmarks/codex-ab-refined.md) remains blocked by invalid
authentication. No Codex coding, token or cost benefit has been established.

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
