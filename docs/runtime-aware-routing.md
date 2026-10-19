# Runtime-aware routing and local release verification

Memglide remains a local Python service with SQLite FTS5, Python AST and pinned
Tree-sitter grammars. It has not trained or replaced the coding model. The CLI,
MCP server and loopback API share the application service layer; the optional
source launcher prepares context before handing control to the native agent.

The established [known-path profile](source-only-refinement.md) remains the
practical choice when the relevant files are known. Complete source, approval,
ignores, secret checks, safe paths, current hashes and exact original-task
fallback remain authoritative. Memory stays explicit. This work does not change
native model/settings or silently disable existing MCP registrations.

## Opt-in runtime-aware selection

```sh
uv run memglide-codex --discover --selection-policy v3 --project PROJECT_ID \
  --preparation-report /private/preparation.json \
  'Correct the retry delay when the attempt count is negative.' -- --json
```

The local pipeline is **secure index refresh → existing lexical shortlist →
current syntax-origin evidence → bounded complete-file bundle → final current
source/policy verification → original task or prepared task**. No selector model,
embedding service or memory injection participates. `--discover` stays explicit;
its compatibility default remains v1. Version 2 and version 3 require their
respective policy flags.

The new policy separates implementation identifiers from type/declaration
evidence rather than combining every matching word. Type tasks still need
declaration evidence, mixed files can serve both roles, and Python annotations
are not assumed to be erased at runtime. Comments, literal strings and stale
index signatures cannot independently justify a selection. Syntactic roles are
relevance heuristics, not a proof of behavior or semantic completeness.

Every candidate must be inspected within the existing source and candidate
bounds, including competitors not ultimately delivered. Parsing runs as data
in a bounded isolated trusted worker; repository modules are never imported or
executed. Full selected files and the existing bounded direct production
dependencies are preserved. Insufficient evidence, ambiguity, resource failure,
unsafe files or changed observations lead to exact task passthrough.

Syntax inspection and subsequent relationship queries have separate bounded
budgets. The latter gets a fresh SQL budget only after rechecking settings and
index identity. Final current-source and losing-competitor checks still run.
V3 SQLite failures report safe phase/category names such as
`retrieval_query_budget` or `index_refresh_database_locked`; exception details,
SQL and private paths are not added to the receipt. Older receipt behavior is
preserved. No hard whole-operation latency guarantee follows from these phase
limits: index scanning, Git and database waits have their own costs.

## What the checks can establish

The [research](../benchmarks/router-v3-research.md) explains the mechanism and
its limits. The [frozen offline protocol](../benchmarks/automatic-v3-protocol.md)
separates known-path delivery, original automatic policies and the new policy.
Its public path-free tasks and private target scopes remain separate; no hidden
test, reference fix or expected target enters automatic discovery. Source
inclusion is a declared-scope proxy, not coding correctness or measured avoided
investigation. Model token usage, whole-task cost and billing require native
outcomes and cannot be inferred from source size.

Release verification includes the full Python regression suite, lint/typing,
production frontend and browser tests, a clean installed wheel, actual API and
default/agent MCP clients, parser import-isolation checks and exact native
handoff using a controlled fake executable. Additional process tests exercise
reindex interruption and SQLite/FTS recovery, concurrent service instances,
fresh processes with changed/deleted/ignored source, and bounded FIFO rejection.
Each check has its own outcome; a test plan is not evidence it passed.

A passing release report supports a tested **local single-user application**
within its recorded platform and load. It does not prove remote tenant
isolation, hosted authentication/TLS, operational service targets, disk-failure
recovery, exhaustive adversarial safety or consistently cheaper coding tasks.
Those require their own implementation and measured deployment evidence.
