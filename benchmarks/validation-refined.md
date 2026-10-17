# Refinement verification

**403 distinct checks passed:** 376 Python tests, 24 frontend tests and three production Chromium workflows. No final failures, errors or skips. Python includes 69 security/storage cases and real STDIO MCP integration that discovers and invokes all 14 tools. Repeated runs are not counted again.

Frozen uv installation/lock checks, pinned npm installation, Ruff format/check, mypy over 21 source files, strict TypeScript, the Vite production build and frontend bundling passed. All 19 bundled frontend files match the production build. Two upstream Typer/Click deprecation warnings remain.

The wheel and source distribution passed source-byte, frontend, required-file and exclusion audits. No authentication state, caches, databases, node_modules or symlinks were packaged. A fresh Python 3.12.14 environment installed hash-locked dependencies and the wheel; isolated imports from `/tmp`, CLI doctor, source indexing without execution, search/context budgets and hashes, stale/refreshed passports, real loopback API health, compiled assets and SPA routing passed. The final release archives are re-audited after report generation; their checksums stay outside the archives.

Source digest: `20cc181bc45cecacc6e96f40e4a470112dd1581212eac7acece46c44f7270454`. The final SDK and reused retrieval replay have this same source digest. All 50 baseline and eight initial-stage preservation hashes remain unchanged.

[JSON](validation-refined.json) records counts, commands, source manifest, package checks, actual installed-wheel results and initial failed regressions. Raw final JUnit/browser/static logs and pre-fix failures are retained under [evidence](evidence/), including [package audit](evidence/refined-package-audit.json) and [wheel smoke](evidence/refined-wheel-smoke.json).

The local suites establish no model coding, billed-token or cost benefit. The live Codex preflight failed HTTP401; all96 planned coding slots remain unrun. Nine reused retrieval tasks still lack a declared helper body. See the [assessment](refinements.md) for all retained tradeoffs and regressions.
