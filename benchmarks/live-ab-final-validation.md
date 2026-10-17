# Final validation after authenticated A/B

**418 distinct checks passed:** 391 Python, 24 frontend and three production-browser tests. Python tests include the complete configured unit, integration, security/storage, real MCP/CLI and benchmark-tooling suites. No tests were skipped in the successful Python run.

Frozen uv installation/lock checks, Ruff format/check, mypy, frontend installation/typecheck/build and bundling passed. All 21 application Python files and 19 bundled assets remain unchanged. Full commands, counts and hashes are in [the validation JSON](live-ab-final-validation.json); frontend details are in [its separate record](live-ab-final-frontend-validation.json).

The first final Python invocation had 385 passes and 6 failures because it overlapped npm ci replacing the shared TypeScript compiler. The retained logs show missing executables, ETXTBSY and missing type declarations. Once installation finished, the complete suite passed 391/391 in 72.12 seconds with no source change. All model measurements had already finished before this validation race. Both failed and successful validation logs/XML and all six fixture compiler logs are retained under [evidence](evidence/live-ab-final-backend/).

Two upstream Typer/Click deprecation warnings remain. Previous packaging validation applies to the unchanged application runtime; no new package or Windows/macOS verification is claimed. Independent benchmark audit assertions and repeated per-run grader executions are not added to the 418-check count.

Raw recorded grader/recovery Python files are excluded from Ruff to preserve their exact bytes; all 70 implementation and test files still pass lint and format checks. The initial evidence lint findings and final checks are retained. Credential-pattern matches in the two test XML files exactly match existing synthetic security-test literals; no unknown credential patterns were found.
