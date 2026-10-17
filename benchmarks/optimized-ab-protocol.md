# Frozen protocol for the optimized 40-task comparison

This protocol is recorded before running the fresh task corpus through Codex.
Research, component tests and old-task development pilots are separate evidence.
The earlier reports and failed attempts remain unchanged.

## Question and configurations

Does the optimized Memglide integration improve coding-task success or resource
use compared with standard Codex under the same settings?

- A: native Codex with an empty MCP-server map.
- B: the same native Codex with only the project-bound Memglide agent profile.
  Its two tools are `fetch_context` and `verify_context`. Project discovery,
  session creation and initial retrieval are combined server-side. Source is
  refreshed synchronously; this profile runs without background file watching.
- Both receive identical prompts, model `gpt-6.1-sol`, `low` effort, structured
  final-output schema, workspace sandbox and timeout. The shared prompt uses the
  retrieval tool only when available. Verification is on demand when reusing
  older context whose freshness is uncertain. Task completion alone does not
  require an extra model/tool round trip, and intentional edits do not mandate
  another retrieval. The retained first development pilot used mandatory final
  verification; `--require-verification` keeps that separate ablation available.
- B's scoped tool permissions authorize exactly those two operations on that
  run's synthetic repository/database. Global approvals and sandbox protections
  are retained. MCP startup must complete its connection handshake.
- The selected context default is 4000 planning tokens. Smaller development
  budgets omitted complete implementations; response bytes are not model tokens.

The default fourteen-tool interface remains compatible. The compact interface
uses one native JSON text payload, with no duplicated structured-content copy.
This prevents protocol duplication; any actual model-token effect must be
measured rather than inferred from serialized sizes.

## Tasks and independence

`tasks_v2.json` contains forty unique maintenance tasks: twenty Python and twenty
TypeScript, distributed across four synthetic repositories. Sixteen tasks have
independent domain and public-API defects. Hidden behavioral checks exercise both
layers, visible smoke tests must remain passing, and TypeScript must compile.
Every baseline must fail its requested behavior and every reference solution must
pass before formal evaluation. Reference validation is not a model result.

The new tasks are excluded from retrieval tuning and development model pilots.
They remain synthetic, share repository families, and do not establish performance
on arbitrary production repositories or persistent memory across related tasks.

Two repetitions yield **160 planned original attempts** and eighty A/B pairs.
Each task reverses its first-arm order on the second repetition. The fixed seed
is `20261017`. Every attempt uses an isolated detached worktree at the recorded
per-repository starting commit. B receives a fresh index, database and private
session. No evaluation answer is seeded into memory.

## Freeze and execution

Before the formal run, application changes, corpus, graders, harness and tests
must pass review and required checks. Commit the source and capture all runtime,
measurement, task and prompt hashes in the experiment's frozen manifest. Model
settings and native CLI version must remain fixed. Resume refuses a changed
manifest. No tuning or application edits are permitted during the comparison.

Use native `codex exec --json` and its supported output schema. Start the runner
detached from the interactive execution session and preserve its progress log.
Only lightweight progress inspection runs alongside formal measurements; all
builds and tests finish first.

Save metadata before requests and atomically checkpoint each attempted result.
An immutable hash-chained attempt log records starts and completions. An
interrupted original attempt remains interrupted, with unobserved timing, usage
and overhead unknown. Resume continues only pending assignments. Any explicit
retry is supplemental, uses new artifact paths and never replaces the original.
An authentication, provider-quota or confirmed shared network blocker is retained
and leaves unattempted assignments visible rather than fabricating results.

## Outcomes and measurements

- External behavioral grading establishes task success, independently of the
  model's final summary. Report all-attempt completion rates, graded-only rates,
  statuses and every individual failure. Preserve tests, Git metadata and grader
  integrity checks.
- B requires an observed successful source-bearing `fetch_context`, decoded from
  native tool results. Optional `verify_context` calls and failures remain visible.
  Structural-only placeholders are not implementations. The explicit strict
  ablation additionally requires successful verification; the policy is frozen
  per run. Invocation fidelity alone does not establish that verification followed
  the final edit or independently prove source freshness.
- Report total input, cached input and output tokens from native completed-turn
  usage. Cached input is a subset of total input. Missing or interrupted usage
  remains unknown; known subtotals are not full totals.
- Actual provider charges, cost per successful task and underlying model/API-call
  counts remain null unless reliable telemetry exposes them. Cost per success
  must include costs from all attempts, including failures. Planning tokens and
  list-price examples are not actual billed costs.
- Report native MCP calls and failures. File-read command counts are intent
  proxies; exact repeated filesystem reads are unavailable without an independent
  I/O trace.
- Report Codex process time and necessary B indexing separately and together.
  This excludes worktree preparation, external grading and report generation.
  OS and provider caches cannot be reset; retain cached usage and order strata.
- Sample local Codex/MCP process-tree CPU and RSS, preserving missing values and
  sample limitations. Memglide is a subset of total process resources. Indexing
  has separately measured wall/process CPU; its parent RSS peak is not measured.
- Analyze actual returned paths, declarations and body coverage where independent
  ground truth is available. Clearly separate server freshness assertions,
  independent mutation/hash probes and live measurements that remain unavailable.
  Capture returned versus securely observed source hashes after native Codex
  exits and before grading, outside model timing. These are post-execution
  observations; expected differences from edits are not coding failures and do
  not reconstruct the exact file state at an earlier tool-call instant.

Publish Markdown and JSON with all individual attempts, totals or explicitly
partial subtotals, means, medians, coverage counts and matched comparisons.
Descriptive p95 values use the nearest-rank method. Include language, repetition
and arm-order strata. Matched resource deltas require equal starting commits and
prompt hashes plus verified intended treatment; unconditional results retain
every failure and invalid treatment. Do not exclude poor results or present
correlated repetitions as independent tasks.

If B performs worse, state that outcome, distinguish observed causes from
hypotheses, and propose changes without revising the frozen experiment to erase
failures. A combined optimization experiment does not isolate the causal effect
of each individual mechanism.
