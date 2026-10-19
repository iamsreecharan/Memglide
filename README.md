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

For the source-only configuration used in the earlier favorable cost estimates,
follow the [focused source-only profile](docs/source-only-refinement.md): complete
known source files, compact prefixes, `gpt-6.1-sol` at low reasoning and no
automatic memory or discovery. Those 9–10% figures describe specific subsets;
actual billing savings remain unproven. The guide explains native configuration
and the new bounded local preparation refinement.

The [refinement assessment](benchmarks/source-only-refinement-assessment.md)
confirms half as many repeated policy compilations with identical source and
freshness checks. Its local timing results are mixed: no reliable overall mean
speedup or additional model-cost saving was demonstrated.

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

The opt-in [bounded v4 router](docs/bounded-source-routing.md) adds production-scoped
discovery and a conservative current-source screen. Its [fresh held-out assessment](benchmarks/router-v4-assessment.md)
found no inclusion improvement: v4 and v3 delivered zero of twelve positive
scopes, while known paths delivered three, consistently over two repeats. V4
added local preparation overhead and remains experimental; no new Codex savings
are established. See [cloud benchmark access](docs/cloud-benchmark-access.md) to
open a worker using the published network configuration.

An experimental [automatic source router](docs/task-aware-router.md) accepts a
natural-language task without target paths:

```sh
uv run memglide-codex --discover --project PROJECT_ID \
  'Correct invoice subtotal rounding for fractional prices.' -- --json
```

It reuses local ranking and static dependencies, supplies bounded complete files,
and returns the original task when evidence or safe delivery is insufficient.
There is no auxiliary selection model call. The feature is opt-in; automatic
warm-memory injection stays disabled. [Research](benchmarks/auto-source-research.md),
the [implementation audit](benchmarks/automatic-implementation-plan.md) and the
[approval-gated A/B/C protocol](benchmarks/automatic-protocol.md) distinguish
source-selection coverage from unmeasured coding-agent efficiency. Conservative
[Python excerpts](docs/source-excerpts.md) are a separate experiment, excluded
from normal source delivery and the initial formal treatment.

The original v1 [held-out offline assessment](benchmarks/automatic-assessment.md) is
negative: automatic preparation delivered source on **0/12 tasks**, compared with
**9/12** for known-path preparation, and added local overhead. It remains opt-in
and unpromoted. [1,907 automated cases passed](benchmarks/automatic-validation.md)
at that revision; its proposed paid comparison was not run. The
[initial v1 policy guide](docs/automatic-source.md) remains available.

The newer [task-aware v2 assessment](benchmarks/router-v2-assessment.md) is also
negative: 72 fresh offline preparations covered 12 tasks with two repeats.
Known-path B delivered the target source in 24/24 observations; automatic v2
delivered it in 0/24 and had 72.54% longer mean local preparation than B.
Its two preloads contained a type-only file instead of the runtime target.
The fixed eligibility gate failed, so all 72 planned native assignments remain
unrun. Discovery preserves its v1 default; v2 requires explicit
`--selection-policy v2` and is not promoted. Neither automatic policy has proven
cost or speed benefits over Codex. Complete known-path delivery and optional
memory remain available. [Final verification](benchmarks/router-v2-final-validation.md)
records 2,040 distinct Python cases across completed runs, 24 frontend cases,
three browser cases and 14 separate installed-wheel smoke checks passing.

An explicit [runtime-aware v3 policy](docs/runtime-aware-routing.md) separates
current implementation evidence from type declarations, annotations and prose.
Use `--discover --selection-policy v3` to try it; known-path delivery, earlier
policies and explicit memory remain available. The [fresh assessment](benchmarks/router-v3-assessment.md)
reports source selection and local overhead separately from coding success and
model cost. V3 is experimental and does not change the discovery default.

## Local efficiency and warm-memory evaluation

The [latest local-efficiency assessment](benchmarks/saas-efficiency-assessment.md)
records less graph/SQLite work, lower unchanged-scan Python allocation and leaner
watcher/dashboard bookkeeping. Complete live source reads and freshness checks
remain enforced. These component measurements do not establish new model-token,
billed-cost or native-task speed savings. See the
[product architecture](docs/product-efficiency-architecture.md) and
[primary-source research](benchmarks/saas-efficiency-research.md).

The optional [memory preparation API](docs/memory-preload.md) supplies explicitly
selected, current source-backed findings from one still-active Memglide session
to a fresh agent process. It does not transfer memory into a new Memglide session
or restore ended/expired sessions. Source-only launcher defaults are unchanged.
The [warm-memory study](benchmarks/warm-80-analysis.md) stopped at the user's
request after **80 completed assignments, all passing**; an already-started 81st
was interrupted and retained. On the descriptive matched first 72 runs, source-only
B had 9.05% lower API-price-equivalent cost and 6.89% lower mean instrumented time
than A. Warm C was 12.35% costlier and 3.40% slower than B. This is a partial,
one-repeat study; actual billed savings remain unknown. The [final audit](benchmarks/warm-v2-final-integrity-audit.md)
passed with incomplete coverage. [Download v2 evidence](benchmarks/memglide-warm-v2-evidence.zip).
The [earlier authentication failure](benchmarks/warm-study-assessment.md) remains
preserved separately.

## Verify and develop

```sh
uv run pytest
uv run ruff check .
uv run mypy src
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for browser tests and packaging. [PROGRESS.md](PROGRESS.md) records observed validation and outstanding limitations; source-file presence alone is not a completion claim.

The latest [efficiency report](benchmarks/efficiency-assessment.md) preserves **120 native assignments in two separately frozen studies**. The original 60 remain strict protected-test failures; a fresh explicit-contract confirmation records A 20/20, B 20/20, C 20/20. The [validation](benchmarks/efficiency-validation.md) records **1,443 verified automated cases** and unchanged application source. In the confirmation's focused tasks, C versus bare Codex has 2.41% lower estimated cost per success and 12.63% higher mean full time. The frozen promotion gate is **False**; support stays explicit and optional. API-price equivalents are estimates, actual charges are unavailable, and the report includes every failed attempt's spend. [Download the complete evidence](benchmarks/memglide-efficiency-report.zip).

Source-only B is the best focused-task point estimate in this confirmation: **10.19% lower estimated cost per successful task** than A, but **3.18% longer mean full time**. Its median time is also longer. This is not a joint cost-and-speed win. Under independent possible cache-write attribution, its focused saving range is **-3.54% to 22.49%**; these are scenarios, not confidence intervals or actual billing.

The preceding [cost study](benchmarks/cost-assessment.md) compares **bare Codex with
compact-prefix Memglide on ten fresh paired tasks: 20 runs, all successful**.
At [verified standard API rates](benchmarks/cost-pricing-research.md), estimated
cost per successful task was **$0.03923 for Codex and $0.03833 for Memglide**,
2.3% lower overall. However, the eight tasks that received source bundles cost
**4.4% more** with Memglide; two identical-prompt bypass controls drove the
overall decrease. Five pairs favored each arm. These results establish no
retrieval cost saving. Actual charges are unavailable; cache-write uncertainty
allows outcomes in either direction under the same tariff. The
[complete JSON](benchmarks/cost-assessment.json) and
[downloadable evidence bundle](benchmarks/memglide-cost-ab-report.zip) retain
all runs, pricing assumptions, independent checks and failures from validation.

The earlier [source-format assessment](benchmarks/cache-refinement-assessment.md)
and [individual results](benchmarks/codex-cache-formats.json) cover **20 fresh
Python/TypeScript tasks, 40 native runs** comparing legacy Memglide with
compact-prefix Memglide. Both passed 20/20. Compact formatting delivered the same
complete source with a 31.0% smaller added envelope. Mean full execution time
fell 11.2%, but **uncached input rose 3.9%**. The aggregate 2.0% input decrease
came from identical-prompt controls; input rose 0.63% in the 16 pairs that
received source. One pair accounts for 59.5% of the net time reduction.
These small, single-repeat results establish neither a cache benefit nor a
money saving. This comparison has no bare-Codex arm and must stay separate from
the earlier comparisons below. [988 distinct tests passed](benchmarks/cache-refinement-validation.md).
The [downloadable report bundle](benchmarks/memglide-cache-refinement-report.zip)
includes every run, independent audits, research limits and validation evidence.

The earlier [focused-launcher assessment](benchmarks/daily-ab-assessment.md) and
[individual results](benchmarks/codex-ab-daily.json) cover **20 fresh tasks,
two configurations and two repeats: 80 native Codex runs**. Both configurations
passed 40/40. Memglide used 2.9% less total input and 6.2% less output, and took
4.8% less time including cold indexing, but used **27.1% more uncached input**.
Median paired total input increased slightly. These small, known-file utility
tasks do not establish a general efficiency gain or money saving; actual cost
and cost per successful task remain unavailable. The experiment used upfront
source delivery with zero MCP calls in both arms, rather than the earlier MCP
treatment. [817 distinct checks passed](benchmarks/daily-validation.md), and an
independent audit verified all 80 outcomes. The [downloadable report bundle](benchmarks/memglide-daily-ab-report.zip)
includes reports, research access limits, validation and raw evidence.

The earlier [optimized MCP A/B assessment](benchmarks/optimized-ab-assessment.md) and
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
