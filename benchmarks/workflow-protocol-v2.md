# Fresh confirmation three-arm workflow protocol (v2)

This is a new confirmation study after the original workflow-1 experiment. All 60 original assignments failed strict grading because they edited protected existing test files; external behavior checks passed. The original task wording said to preserve existing tests while permitting regression tests, which was ambiguous about appending additional cases. Those runs remain failed and preserved. They are not overwritten, omitted, or regraded. This study uses ten fresh tasks and an explicit common policy requiring every pre-existing tracked test file to remain byte-for-byte unchanged, including comments and whitespace. Optional regression tests must be placed only in new discovery-compatible test files. The same wording appears in fixture AGENTS.md, task prompts, and every arm's common prompt.

This experiment investigates whether supplying complete caller-selected supporting tests eliminates redundant discovery, without removing complete production source or weakening grading. It does not assume that more context reduces cost.

The frozen manifest also binds all six published workflow-1 primary-report, cost-assessment, and contract-issue Markdown/JSON files. Confirmation metadata records the sealed prior primary JSON SHA-256 `a6586d655fc55b0abaecb3153cb62a1c30ff97e7d03ab279f52caebb47f28596` and prior assessment JSON SHA-256 `3ae65603a11f5a8ad83be14e178916c9147f8d854fa2a0dddf1ee5a0fc5a8b0c`. A mismatch stops the new experiment.

## Treatments and common information

- **A: standard Codex.** Direct native `codex exec` with the exact common prompt; no Memglide database, preparation or configured MCP.
- **B: source-only Memglide.** Production compact-prefix launcher with complete caller-selected production files.
- **C: source plus support.** The same launcher with the same production files and explicit `--support` paths for complete existing test files. No extracted signatures, lossy snippets, hidden test content, model classifier or additional model request.

All arms receive identical task text, explicit production and support paths, and the relevant test command as a JSON argv array. The two supplied-context controls embed both complete production source and supporting tests in that common prompt; B and C must then bypass unchanged. C is an opt-in workflow, not a default assumption that every task needs more source.

Ten fresh tasks cover five Python and five TypeScript changes, with four single-file, four integration and two supplied-context tasks. Each task is repeated twice: 20 task/repeat triplets and **60 original native assignments**. Repeat one shuffles tasks and cycles a shuffled list of six arm permutations. Repeat two reverses each task's first permutation. This balances every pair's precedence exactly 10/10 across the complete study. Six permutation counts cannot be equal over 20 triplets; observed counts are published, without hiding this limitation.

## Isolation and validity

Every assignment gets a fresh worktree at its task repository's frozen commit, isolated native state and, for focused B/C runs, a new Memglide approval/index database. Cold approval/index wall and CPU cost is included. A's setup is known zero; focused interrupted B/C setup remains unknown unless durably observed. Controls have zero approval/index work in all arms. Provider and operating-system caches are uncontrolled. The shared native configuration disables configured MCP, apps and web search, uses the same explicit model/effort and standard (`service_tier="default"`) request, and changes no private session/cache identifiers.

The workflow-2 runner and metadata explicitly identify this as fresh confirmation following the retained failed workflow-1 study. The runner freezes both workflow runners, both corpus modules, the new task JSON and protocol plus transitive helpers and accounting code. It freezes the Git HEAD, application Python source, tasks, corpus and transitive grading/runner code, package lock, native version/settings and published pricing/estimator. It checks this manifest before and after each run, stopping future requests on shared source or authentication blockers. Results and starts are immutable, the event log is chained, native launches require a durable grant, and recovery stops retained orphan process groups. Interrupted originals remain unknown and are not automatically retried.

Independent treatment verification reconstructs each full selected file from the frozen fixture Git commit. It checks exact source hashes and line ranges, canonical compact JSON framing, bounded total context, original task suffix, recorded launcher arguments, forwarded native settings and actual stdin hash/size. Source-only reports use version 2; support reports use version 3 with separate private focus/support classification. Every source-focused assignment must preload its exact complete assigned set; every provided-context assignment must pass through unchanged. MCP calls must be zero, evidenced by a complete native stream.

Independent external behavior checks and protected-test smoke checks grade every completed native execution. Existing tests and Git metadata are protected. Modifying any existing test file, including merely appending a passing regression, fails strict grading; adding a legitimate new regression file is allowed. This rule is unchanged from workflow-1 and is now explicit before execution. Successful completion also requires valid treatment, native event framing, successful process completion and the supported structured final-output schema. A plausible model summary is not a passing grade.

## Measurement and reporting

The primary Markdown/JSON reports preserve all original assignments, individual runs, failures, per-arm totals/means/medians/p95, descriptive selection strata, and separately verified C/A, C/B and B/A pairs. Pair exclusion never removes an attempt from primary per-arm results. Raw supported native JSON retains total input, cached input, cache-write input, output and reasoning usage where available. Cached input is already within total input; reasoning is already within output. Read-command diagnostics remain proxies, not actual filesystem counts.

Actual billing remains null. A separately labelled API list-price-equivalent assessment uses observed usage and cited tariffs, includes failed attempts in cost per successful task, and reports unknown usage as unavailable. A zero cache-write field may reflect an upstream parser default; sensitivity analysis must retain that uncertainty. CPU is a local observed lower bound. Sampled child RSS excludes parent indexing and may miss children or double-count shared pages. No model-server resource measurements are available.

The frozen `workflow-promotion-1` acceptance rule is unchanged. Complete valid matched triplets and successful original assignments are required. On focused tasks, C's estimated model cost and full execution time must each have mean and median no worse than both A and B, overall and separately in each repeat. Supplied-context controls cannot supply the benefit signal. Any failure, missing observation, or regression keeps supporting files explicitly optional; this finite-corpus rule does not establish a general guarantee.

A result can establish an observation on this fresh small-task corpus. It cannot establish general production-repository, cross-session-memory, cache-affinity, global optimality or subscription-billing savings. Positive latency or cost results must be reported alongside failures and regressions.

## Invocation

```bash
uv run python -m benchmarks.run_workflow_v2 \
  --output .local/efficiency-v1/formal-workflow-confirmation-v2 \
  --model gpt-6.1-sol --effort low --repeats 2
```

Importing the runner never starts a model request. Local regression tests use a fake native executable, including a real orphan recovery, and never authenticate to a model.
