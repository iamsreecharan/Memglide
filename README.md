# Memglide

Memglide helps coding agents find current repository source and keep explicit
findings during a task. It indexes approved Git repositories in SQLite, retrieves
source with version checks, and reports missing or unresolved evidence in a
Context Passport.

Use it through the CLI, a local dashboard/API, or an MCP client. An optional
Codex launcher can prepare selected source before the agent starts. Source
selection uses Python AST, Tree-sitter and text search, without an embedding
service or an extra model call. The connected coding agent has its own
authentication, data handling and billing.

## Install from source

You need Git, Python 3.11+, [uv](https://docs.astral.sh/uv/), and npm with
Node.js 24.x (24.15+) or 22.x (22.22.2+). Node/npm builds the dashboard; a built
Python wheel can run without them.

```sh
git clone https://github.com/iamsreecharan/Memglide.git
cd Memglide
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run python scripts/bundle_frontend.py
uv run memglide doctor
```

The build bundles the production dashboard into the Python package. See
[installation and packaging](docs/installation.md) for PowerShell, WSL, local
wheels and a separate development-state directory.

## Try it on a repository

Register a Git repository you approve for source access:

```sh
uv run memglide project add /absolute/path/to/your/repository
uv run memglide project list
```

Use the returned project ID, then the session ID returned by `session start`:

```sh
uv run memglide session start PROJECT_ID --task "Investigate authentication"
uv run memglide search PROJECT_ID authenticate_user
uv run memglide context SESSION_ID authenticate_user --level 2 --budget 4000
uv run memglide serve
```

Open the dashboard at [127.0.0.1:8765](http://127.0.0.1:8765). The HTTP API's
interactive reference is at [127.0.0.1:8765/docs](http://127.0.0.1:8765/docs).
CLI and MCP operations also work without a dashboard process.

State defaults to `~/.memglide`. Set `MEMGLIDE_HOME` to an absolute directory to
use another location, and use the same setting when starting Memglide or Codex.
Sessions expire after 60 minutes of inactivity, with an eight-hour maximum by
default. Removing a project deletes its index and task records, keeping source
files intact. The [usage guide](docs/usage.md) covers the workflow in more detail.

## Connect an agent

### MCP with Codex

With Codex installed and authenticated, register Memglide's local STDIO server:

```sh
uv run memglide setup codex
codex mcp get memglide --json
```

Restart Codex and call `list_projects` with the default profile to check the
connection. Setup preserves an existing `memglide` registration. `doctor` checks local setup and
observed configuration; it cannot confirm another process's live connection.
See [MCP configuration](docs/mcp.md) for other clients, explicit database paths
and the optional two-tool project-bound profile.

### Source before a Codex task

For a known file, replace the path and task below with your own:

```sh
uv run memglide-codex --project PROJECT_ID --focus src/calculation.py \
  "Fix rounding for fractional prices." -- --json
```

To try automatic discovery, select the experimental v4 policy explicitly:

```sh
uv run memglide-codex --discover --selection-policy v4 \
  --context-format compact-prefix --project PROJECT_ID \
  "Fix rounding for fractional prices." -- --json
```

The launcher supplies bounded complete selected files or forwards the original
task to Codex when selection is insufficient. Native Codex options go after
`--`. Automatic memory injection is disabled. Read the
[focused launcher](docs/preload.md), [v4 policy](docs/bounded-source-routing.md)
and [verified command-context](docs/verified-command-context.md) guides before
using the optional command/count preset.

## Trust and limits

Indexing reads approved source without running it. Explicit command verification
runs project checks and needs the same care and execution isolation as running
those checks yourself. Repository text and saved findings remain untrusted data.

Source hashes show which bytes were checked, not that the selected context is
complete or the code is correct. Static dependencies and sensitive-content
filtering can miss cases. Context budgets are planning estimates, not billing
meters. Local storage does not make inference local: an agent may send returned
source to its model provider. The HTTP service accepts loopback hosts only.
See [known limitations](docs/limitations.md) and [security](SECURITY.md).

## Research

The latest comparison completed 128 real Codex sessions. Its primary panel
contains 28 author-designed tasks, two methods and two repeats: 112 sessions.
Codex and Codex + Memglide each passed 54/56 strict assessments. Memglide's
observed fixed-price API equivalent was **4.84% lower** ($0.16094 to $0.15316
per session); complete workflow time was **1.17% slower** (59.59 to 60.29 s).
Both nominal 95% intervals include zero, so neither superiority test passes.
These are token-price estimates, not invoices. The paper explains the amended
protocol, finite grading and cache limitations.

- [Revised paper and supplement](research/paper/README.md)
- [Results tables, task catalog and offline statistical reproduction](research/results/router-v7-20261021/README.md)
- [Paper, supplement and results ZIP](https://github.com/iamsreecharan/Memglide/raw/refs/heads/main/downloads/memglide-research-20261020/Memglide-paper-and-supplement.zip)
- [Complete research ZIP](https://github.com/iamsreecharan/Memglide/raw/refs/heads/main/downloads/memglide-research-20261020/Memglide-complete-research.zip)
- [Download contents and checksums](downloads/memglide-research-20261020/README.md)

The replacement complete ZIP includes the revised paper, all current numeric
results and reproduction code, evaluated source, and the previous v6 capsule
under a historical label. The dated download path is retained for compatibility;
its current contents are the v7 revision. The manuscript discloses AI assistance
and remains a preprint for author review.

## Development and documentation

Run the checks after installing dependencies:

```sh
uv run pytest
uv run ruff check .
uv run mypy src
npm --prefix frontend run build
npm --prefix frontend test -- --run
uv run python scripts/bundle_frontend.py
```

[Contributing](CONTRIBUTING.md) covers browser tests and packaging.
The [documentation index](docs/README.md) separates current guides from earlier
design notes and experiments. Memglide is licensed under [MIT](LICENSE);
third-party research fixtures retain their own notices.
