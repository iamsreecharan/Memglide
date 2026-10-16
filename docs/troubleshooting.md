# Troubleshooting

Run `uv run memglide doctor` from a source checkout, or `memglide doctor` from a wheel installation. It reports database integrity, FTS5, tool availability, MCP SDK version, frontend presence, and observed Codex configuration. It does not certify a live Codex connection.

| Symptom | Action |
| --- | --- |
| `uv sync --frozen` fails | Check Python is 3.11+, inspect the reported package/network/trust error, and preserve the lockfile. Do not disable TLS verification. |
| npm engine or install error | Use Node.js 24.x at 24.15+ or 22.x at 22.22.2+ with npm; rerun `npm --prefix frontend ci`. Keep `package-lock.json` unchanged for a reproducible install. |
| Dashboard assets unavailable | Run `npm --prefix frontend run build`, then `uv run python scripts/bundle_frontend.py`; restart `serve`. |
| Port already in use | Stop the previous local process or use `memglide serve --port 8766`. Open the matching origin. |
| HTTP 403 | Use a loopback hostname, the exact same browser origin, and `X-Memglide-Request: 1` for state changes. Public hostnames/proxies are deliberately rejected. |
| No registered projects in Codex | Ensure CLI and MCP use the same database/`MEMGLIDE_HOME`; register through `project add` and call `list_projects`. |
| Registration exists but Codex cannot start it | Inspect `codex mcp get memglide --json`; verify the configured executable still exists and is usable from Codex. Reinstall after moving a checkout. |
| Codex configuration cannot be read | Diagnose `codex mcp list --json` and local configuration permissions. Memglide preserves unreadable/existing configuration. |
| Session expired/unknown | Start a new session. Polling status does not prevent expiration; expired task data is intentionally temporary. |
| Stale passport or source warning | Reindex the project, inspect changed files, then retrieve again. Do not reuse old source hashes as current evidence. |
| No search hits | Try an exact identifier or relative source path; inspect ignored files and indexing errors in Projects; run `project reindex PROJECT_ID --full`. |
| Unresolved relationship | Inspect its source/import directly. External modules, dynamic calls, and ambiguous references are not invented graph edges. |
| Native parser worker error or timeout | Inspect the file and indexing report; text search remains available. Use the pinned dependencies, narrow oversized/generated inputs, and report a sanitized reproducer. Do not treat missing structural evidence as a verified empty graph. |
| Context cannot fit | Increase `--budget` or use a narrower query. Passport and warning metadata also count; extremely small budgets may be rejected. |
| Ignored or credential-like file absent | This is expected for secret paths/content. Add a sanitized source fixture rather than disabling security checks. |
| Database locked or unexpected I/O error | Keep state on a local disk, avoid external SQLite writers, verify permissions/free space, and retry after a conflicting transaction ends. |
| Watcher did not see changes | Ensure `serve` or MCP is running and watching is enabled; run a manual reindex after offline edits. Retrieval still checks source hashes. |
| Browser tests cannot launch | Install Playwright Chromium and OS prerequisites; consult the exact launcher error. A restricted host may require environment preparation. |

For a clean isolated diagnosis, choose a new absolute `--db` path and register a small fixture repository. This preserves normal user state. Do not print environment variables, credential files, raw private source, or memories when collecting a public bug report.

Removing a project clears its index and associated task records without modifying the source checkout. Clearing a session removes only task data. Do not manually delete a database while other Memglide processes are writing it. Stop all transports before filesystem-level backup or removal; SQLite can use adjacent `-wal` and `-shm` files.

## Restricted cloud cache directories

If dependency installation cannot write the default user cache, use project-local caches instead of changing artifact verification. From the repository root, run `uv --cache-dir .cache/uv sync --frozen` and `npm --cache .cache/npm --prefix frontend ci`. In a POSIX shell, `export UV_CACHE_DIR="$PWD/.cache/uv"` and `export npm_config_cache="$PWD/.cache/npm"` also apply these locations to later commands. These directories are ignored by Git and indexing. The reusable cloud installation script sets both locations and keeps lockfile, checksum and TLS verification enabled.
