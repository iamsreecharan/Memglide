# Memglide V1 validation

All 143 existing application tests passed on the current Linux checkout at commit `39e8df30565783a686270f8a6f422e56e41e3776`. No application fixes were needed. These results validate tested application behavior; they do not establish token, cost, or coding-task benefits over Codex.

| Check | Result | Recorded duration |
| --- | --- | --- |
| Backend unit, integration, security, HTTP, CLI, real MCP | 126 passed; 0 failed/skipped | 54.26 s |
| Frontend components/API/workflows | 15 passed in 3 files | 14.62 s |
| Production Chromium browser workflows | 2 passed | 59.3 s including server startup/build |
| Ruff | Passed | Not separately recorded |
| mypy | Passed, 20 source files | Not separately recorded |
| TypeScript + production Vite | Passed | Vite phase reported 1.69 s |
| Frozen dependency installs | Passed, 56 Python packages checked / 134 npm packages installed | Not separately recorded |
| Bundle + wheel/source build | Passed | Not separately recorded |

Backend counts by module: context diagnostics 2, indexing 25, memory/context 20, security/storage 69, transports 9, end-to-end service workflow 1. Parameterized cases are counted individually. Security/storage is part of the 126 backend tests, not an additional count.

The MCP test launches the actual server over STDIO with the official SDK, initializes it, discovers all 14 tools, requires structured output schemas, calls every tool and validates structured content. It also verifies rejected foreign-project/session and ended-session requests. This verifies Memglide's transport independently of the live Codex invocation evidence in the A/B benchmark.

The production browser suite builds and bundles the dashboard, starts the actual FastAPI backend on loopback port 18765 with isolated Git fixtures/database, and checks the repository/session/memory/retrieval/passport workflow, all seven routes, errors and empty states, and 1440/1024/768 pixel layouts. Its two cases took 31.7 s and 13.9 s; suite duration also includes setup.

Exact commands (run from `/workspace/Memglide`):

```sh
export UV_CACHE_DIR=/workspace/Memglide/.cache/uv
export npm_config_cache=/workspace/Memglide/.cache/npm
export MEMGLIDE_HOME=/workspace/Memglide/.local/validation/home
uv sync --frozen
npm --prefix frontend ci
uv run pytest -ra --junitxml=.local/validation/pytest.xml
uv run ruff check .
uv run mypy src
npm --prefix frontend test -- --run
npm --prefix frontend run build
MEMGLIDE_E2E_PORT=18765 npm --prefix frontend run e2e
uv run python scripts/bundle_frontend.py
uv build
```

Python Python 3.12.14, Node v24.19.0, npm 11.9.0, uv uv 0.12.23 (x86_64-unknown-linux-gnu), and Chromium 154.0.8037.57 built on Debian GNU/Linux 13 (trixie) were used.

One initial install command omitted the local uv cache variable and failed before installation because the default home cache is read-only. Retrying with the project cache succeeded. No tests failed. Pytest emitted two upstream Typer/Click deprecation warnings; Playwright emitted a color-environment warning. uv build warned that the cache sits inside the source tree; inspecting the resulting 109-member source archive found no `.cache`, `node_modules`, `.local`, or `.venv` directories. The wheel contains 19 production frontend files.

No tracked application files changed during validation. Generated state, logs, bundled assets and package artifacts use existing ignored paths. Detailed per-test durations, original command output, tool versions and MCP tool names are preserved in [validation.json](validation.json). Native Windows/macOS and live Codex model behavior are outside these application-test results.
