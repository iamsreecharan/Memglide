# Authentication indexing fixture

A small FastAPI-shaped Python application and React/TypeScript client used to exercise cross-file imports, authentication searches, tests, and unresolved relationships. Memglide parses these files without importing or running them. This is an indexing fixture, not a deployable authentication service.

`api/auth.py` verifies an HMAC-signed opaque value using a key supplied by its caller. It contains no credentials. `api/main.py` deliberately references an unavailable optional audit package. `web/src/AuthPanel.tsx` deliberately imports an unavailable feature flag module. A Context Passport should report unresolved relationships rather than inventing implementations.

Copy this directory to a temporary location and run `git init` there before registering it as a project. See [the workflow guide](../../docs/usage.md). The fixture tests are source evidence for retrieval; Memglide's own test suite indexes them without executing the fixture application.
