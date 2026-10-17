# Optimized candidate validation

**623 distinct checks passed:** 596 Python, 24 frontend and three production-browser tests. The Python total includes 69 security/storage cases, 82 fresh-corpus checks, actual default fourteen-tool and compact two-tool MCP transports, CLI registration, source-race regressions and durable-runner checks. No Python tests failed or skipped. See [the JSON record](optimization-validation-v2.json) for exact evidence hashes, counts, candidate source identity and retained intermediate failures.

Frozen dependency installation, Ruff on 85 authored files, mypy on 22 source files, frontend typecheck/build and bundling passed. The final wheel/source archive audit passed: 22 Python runtime files and 19 frontend assets match, with zero forbidden state/symlink entries. An isolated wheel installation passed CLI/storage/retrieval/freshness/HTTP/SPA probes and actual compact MCP retrieval, same-size/restored-timestamp staleness, refresh and foreign-retrieval rejection.

Earlier setup/test-assertion, temporary-fixture lint and early-archive snapshot failures are preserved and explained in JSON; none is relabeled as a passing initial check. Two upstream Typer/Click deprecation warnings remain. No native Windows/macOS claim or model savings conclusion follows from these tests. Source archive scope is the tested prebenchmark snapshot.
