# Memglide V1 verification and benchmark assessment

## Finding

**Tested application behavior works. A benefit over regular Codex has not been
established.** All 143 existing application tests passed. The final Python suite
also passed all 60 new benchmark checks: 186 Python tests plus 15 frontend and
two production browser tests, **203 distinct checks in total**. No application
fixes were needed. Ruff, mypy, TypeScript, Vite, frozen installs and package builds
passed. Repeated executions of a test are not counted as additional checks.

The reproducible A/B experiment has 24 tasks, two configurations and two
repetitions, for **96 planned coding runs**. The formal `codex exec` preflight
failed with HTTP 401 and: “Your access token could not be refreshed ... Please
sign in again.” It exited 1 after 2.257 measured seconds. **All 96 coding runs
remain `not_run`; no verified A/B pair exists.** This is an authentication
blocker, not 96 failed coding tasks. Token usage, model calls, task success,
actual cost and cost per successful task remain unavailable. No token or money
savings claim is supported.

Earlier diagnostic invocations failed on read-only Codex state, then proxy HTTP
403. Those failures are retained in [evidence](evidence/README.md). Fresh writable
per-invocation state referencing the existing authentication binding solved
startup. The latest request reached the provider but could not authenticate.
The earlier `chatgpt.com` network addition was saved to the cloud draft; that
does not establish an applied or published policy. Refresh Codex authentication,
review/save the network draft as needed, and run the documented experiment with
a fresh output directory. Do not supply credential values in chat or reports.

## Independent MCP measurements

The official MCP SDK executed **168 actual tool calls** across 24 isolated
worktrees and fresh databases. These were SDK component probes, not Codex B
invocations. All 24 transport/hash/freshness checks passed: returned evidence
hashes matched disk, a controlled comment edit made the previous passport stale,
and subsequent retrieval returned the updated hash and full-source edit marker.
This demonstrates tested source freshness; it does not establish coding success.

Natural whole-task queries at level 2 with an 8,000 estimated-token budget
returned the declared fix file in **16/24 cases (66.7%)**. Eight misses remain in
the report. Exact target-symbol identity matched in 8/24, and its declaration was
visible in a snippet in 15/24. Whole-file/class evidence can contain useful code
without matching a symbol identity. Conversely, a file hit or declaration does
not establish a complete method body or all necessary context. A model could
formulate a better query than these full-prompt probes; misses are not measured
coding failures.

Across the seven-call probe workflows, mean wall time was 5.1211 s (median
5.0498 s), excluding initial registration/indexing, whose mean was 0.2750 s.
Mean sampled server CPU was 4.8046 s and mean sampled peak summed RSS was
81,954,816 bytes. These include fresh server startup, multiple queries, controlled
edit and shutdown. They are not the cost of one query or incremental A/B
overhead. CPU is an observed sampled lower bound; short-lived processes can be
missed and shared RSS pages counted more than once. Full individual observations
and distributions are in the component report and accompanying JSON.

## Why natural retrieval missed the target

All eight targets existed in the candidate pool. They were omitted during
ranking/budget selection, with Partial passports and omitted-candidate warnings.
No indexing errors were reported for these queries.

| Task | Best target file/function candidate rank | Target symbol rank |
| --- | ---: | ---: |
| py-scope-authorization | 4 | 17 |
| py-storage-containment | 4 | 21 |
| py-transitive-dependencies | 9 | 35 |
| ts-scope-authorization | 7 | 19 |
| ts-storage-containment | 8 | 22 |
| ts-transitive-dependencies | 12 | 25 |
| ts-boolean-config | 9 | 20 |
| ts-and-search | 3 (function); 5 (file) | 3 |

The code gives a 75-point explicit-symbol boost to generic words such as
`Repository` and TypeScript `Document`, which occur in prompt boilerplate
“document-service repository” ([indexer.py](../src/memglide/core/indexer.py#L783)).
Selected broad classes therefore outrank small task-specific helpers. Search
ORs prompt terms, including generic instructions; tokenization has no stemming
and the context tokenizer handles identifiers differently from search.

Dependency metadata is repeated in the response, passport dependencies and
unresolved-dependency fields ([context.py](../src/memglide/core/context.py#L312)).
For `py-scope-authorization`, the retained natural response serialized to 23,695
UTF-8 JSON bytes: 3,456 raw snippet-text bytes and 12,643 serialized bytes across those dependency
blocks. Its estimate was 7,899/8,000 and 15 candidates were omitted. For
`ts-and-search`, 15,823 of 23,611 serialized bytes were dependency blocks (about
67%); raw snippet text used 2,260 bytes, the estimate was 7,871/8,000 and 21 candidates
were omitted. **These are serialized-byte counts and Memglide budget estimates,
not measured model tokens.** Greedy fitting skips candidates that add too much
source and graph metadata, and final pruning can remove more. This explains why
even a third-ranked target could disappear.

Rank analysis replayed the original fixture source in an in-memory copy of the
retained index after the controlled comment edit. It did not change persisted
data or rerun/tune the queries. Raw SDK responses are under
`.local/component-probe/runs/<task>/call-03-get_context.json`.

## Proposed improvements and further evaluation

1. Represent each dependency once, use compact identifiers/reference spans, and
   give graph metadata a separate budget. Reserve source capacity for direct
   matches before optional graph expansion and documentation.
2. Distinguish explicit code identifiers from ordinary prose when applying
   symbol boosts. Share identifier tokenization and handle common inflections.
   Evaluate concise task queries separately from full-prompt queries.
3. Validate changes against these eight misses and additional held-out tasks at
   fixed budgets. Retain this V1 result and report the changed version separately.
4. Extend the controlled synthetic corpus with independent production
   repositories and larger cross-file changes. The two translated fixture
   repositories and twelve task families are correlated and limit generalization.
5. Add a separate longitudinal cohort for prior-memory reuse with matched task
   histories, counting warm-up cost. Fresh B databases currently test retrieval
   and initialization, not reuse of earlier saved task memories.
6. Obtain provider usage/billing evidence for actual model-call count and cost,
   and use explicit filesystem tracing if exact repeated reads are required.
   Until then, these fields stay null; read-command intent remains a proxy.

These are proposed fixes and follow-up experiments. Their benefits have not been
measured. The current data cannot determine whether Memglide makes Codex coding
cheaper, faster, more reliable or worse overall.

