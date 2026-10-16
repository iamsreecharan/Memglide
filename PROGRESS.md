# Memglide V1 verification record

V1 is implemented and passes the local Linux acceptance workflow. All twelve implementation milestones are complete for the tested platform. Native Windows/macOS execution and a live Codex model session remain unverified; these are not claimed below.

## Implemented milestones

1. Installable Python foundation, pinned uv/npm dependencies and durable project instructions.
2. Transactional SQLite schema/migration, WAL, FTS5, foreign keys and concurrent local access.
3. Python AST / Tree-sitter JS, TS and TSX indexing; stable symbols; conservative imports/calls; deterministic configurable ranking.
4. Source-aware session memory, provenance, atomic deduplication, bounded inactivity/absolute expiration and deletion.
5. Budgeted context selection, overlap deduplication, explicit known-memory references and bounded search excerpts with full-source fallback.
6. Context Passports, three retrieval levels, dependencies/tests, source versions, gaps and progressive expansion.
7. Incremental filesystem/Git updates, Watchdog debounce/poll fallback, stale memory/passport invalidation and changed-file history.
8. Official MCP SDK 2.3.0 MCPServer with fourteen STDIO tools and safe supported Codex CLI registration.
9. Shared-service CLI and typed FastAPI endpoints with loopback/Host/origin/request-header protections and no-store responses.
10. Seven connected React screens, dark/light/system themes, project/session controls, memory CRUD, context/passport exploration, timeline and settings.
11. Backend, transport, security, component and production-browser integration checks, with discovered defects fixed.
12. Bundled frontend wheel and source distribution, clean installation/reconstruction, installation/security/architecture/MCP/troubleshooting docs and separate V2 plan.

## Executed checks

| Check | Observed result |
| --- | --- |
| Backend suite, source checkout | **126 passed**, no skipped/failed tests; two upstream Typer/Click deprecation warnings |
| Frontend Vitest / React Testing Library | **15 passed** across three files |
| Production Playwright, real FastAPI | **2 passed** in 42.6 seconds; all seven routes at 1440/1024/768 px, no uncaught exceptions or horizontal overflow |
| Ruff format/check | Passed |
| mypy | Passed over 20 Python source files |
| TypeScript and Vite production build | Passed |
| uv frozen dependency installation / lock check | Passed |
| Official MCP STDIO client | Initialized, discovered and invoked all fourteen tools; isolation and ended-session error paths verified |
| Actual Codex CLI configuration | Supported add/get tested in an isolated project-local configuration, existing registration preserved; user configuration unchanged |
| Clean wheel installation | Installed into an isolated environment; imports resolve to installed site-packages, with Tree-sitter 0.25.2 |
| Installed wheel behavior | CLI doctor, fixture registration, eight search hits, seven context items, loopback health, compiled JS/CSS and SPA route all passed |
| Source distribution reconstruction | Required source/tests/locks/ignore/build files present; no caches/node_modules; frozen uv install, clean npm install, TypeScript/Vite build, **15 frontend tests and all 126 backend tests passed** |
| Saved cloud startup command | Actual checkout service started; health/project checks and source-aware `safe_path` context retrieval passed within its budget; validation session cleared |

The normal fixture workflow exercised registration/indexing → session start → search/retrieve/expand → save/edit memory → source edit → stale evidence → updated retrieval → expiry/cascading cleanup. Source code remains intact. New/deleted/renamed files, branch switches, project/session isolation, path/symlink races, ignored secrets, database concurrency and parser failure containment have dedicated coverage. The small ordinary-search comparison reports retrieval behavior only, with no billed-token or cost-saving claim.

## Real-source and failure findings

- Memglide indexed its own repository: 86 files and 324 symbols at the recorded run. A focused retrieval returned 7,512 estimated tokens within an 8,000 budget and correctly produced a Partial passport.
- One valid TSX bare-ampersand grammar warning is reported explicitly by the pinned grammar. Partial structure and text remain available; source syntax is not assumed invalid. Static analysis and secret detection remain heuristic.
- Tree-sitter 0.26.0 crashed in 11/15 isolated trials on real TSX components; the official 0.25.2 release passed 15/15. The pin and lockfile were corrected. Changed JS-family files now use bounded isolated parser batches; native crashes/timeouts/recursion produce visible text-search fallbacks rather than killing the service. Regression coverage parses real frontend components.
- Production browsers caught and verified fixes for ignored-file object rendering, modal keyboard focus, busy controls, ended-session deletion and direct-passport URL/session initialization races.
- In the restricted cloud shell, npm's default user cache was unwritable. A clean install succeeded with a project-local cache and unchanged artifact-integrity/TLS checks. Reusable setup sets both uv and npm cache locations under .cache.

## Environment and distribution

Observed platform: Linux, Python 3.12.14, uv 0.12.23, Node 24.19.0, npm 11.9.0 and Git 2.52.0. No paid service or credential is required by Memglide.

Local artifacts: `dist/memglide-0.1.0-py3-none-any.whl` and `dist/memglide-0.1.0.tar.gz`. Production assets are bundled under generated `src/memglide/web`. Desktop/tablet browser screenshots are in ignored `frontend/test-results/`.

Reusable `install_script` and `start_skill` were saved to the cloud environment draft, including project-local caches, production frontend bundling, restart commands and functional readiness checks. Saving does not publish a snapshot or prove fresh-task restoration. Review/save the draft and publish through environment settings when you want to reuse that snapshot; publication and a new cloud-task restore have not been tested here.

Implementation and validation ran locally. The user subsequently authorized publishing this repository to GitHub. No deployment or package publication was performed. See docs/limitations.md for the supported trust model, static graph and tokenizer limits, filesystem requirements and unverified platform/Codex behavior. Repository changes remain available for user review.
