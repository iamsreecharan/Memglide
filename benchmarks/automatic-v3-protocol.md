# Independent offline automatic-source policy evaluation (automatic-3)

This is an **offline source-selection evaluation only**. It cannot dispatch a
native coding agent or model. It does not grade coding correctness, infer avoided
investigation, estimate model tokens/cost, or establish billed savings. Previous
protocols, source snapshots, reports, failures and raw outcomes remain unchanged.

## Freeze before corpus authoring

Freeze production policy v3, the current v1/v2 compatibility paths, this protocol,
the generic runner and its tests **before selecting or inspecting fresh upstream
repositories or writing tasks/targets**. `freeze` records current application
Python hashes, runner/protocol/test hashes, locks, Git HEAD, API settings and
Python/dependency versions. The corpus author is separate from the policy author.
Python, SQLite, pathspec, Tree-sitter and both grammar-package versions are checked
again with the source seal. Provenance is a separately hashed JSON input; its
retained-file hashes and license paths must match every repository snapshot.
Only after the root operator confirms this freeze may the corpus author select
four previously unused upstream repositories and inspect their source. No held-out
query or expected target is used to tune policy. A policy change after results
requires new tasks, not replacement of unfavorable original observations.

Record four exact upstream commit SHAs, HTTPS archive URLs, archive SHA256,
per-file SHA256s, license files and complete/partial tracked-tree coverage.
Preserve ordinary source, tests, configuration, documentation and instruction
files byte-for-byte where retained. Explicit exclusions for symlinks, binary,
oversized or unsafe archive entries must be recorded. Never install or execute
upstream packages, build scripts, tests, hooks or source while indexing/evaluating.
Repository snapshots and author targets remain outside application source.

## Public tasks and private grading

The fresh cohort has **12 tasks across four repositories**: two positive tasks
and one abstention control per repository. Prefer two Python and two JavaScript/
TypeScript repositories with several production modules. This is a small,
deliberately authored corpus, not representative production prevalence.

Public `tasks_automatic_v3.json` contains neutral IDs, repository IDs, language
and natural-language requests. It contains no target paths, source snippets,
reference fixes, hidden tests, target-scope hashes, or arm-dependent instructions.
Targets live separately in `automatic-v3-grading.json`, outside indexed roots.
Positive requests describe real source behavior; author-declared required paths
are a **scope proxy**, not proof of all semantic dependencies. Abstention controls
are deliberately underspecified or request capabilities absent from the retained
repository; their declared expected action is safe bypass, not an objective proof
that no imaginable relevant source exists. Explain each control's rationale.

No defect mutation or reference fix is needed: only source inclusion is graded.
Check that positive targets exist as complete eligible production files and
that public task text does not disclose their paths. Freeze public tasks, private
targets, provenance, every retained upstream byte, source code, settings, order,
and canonical Git commits/trees before issuing any held-out query. Automatic
requests contain only the public prompt, registered project and fixed API
settings; no target path, task identifier, repository semantic label or grader
data enters discovery. B alone receives target paths. Private targets are read
by the evaluator after preparation, never by an automatic worker.

## Arms, order and isolated observations

- **B**: existing `prepare_prompt`, complete caller-known paths for positives;
  untouched original prompt for abstention controls.
- **V1**: `prepare_task_prompt(selection_policy="v1")`.
- **V2**: `prepare_task_prompt(selection_policy="v2")`.
- **C**: `prepare_task_prompt(selection_policy="v3")`.

All preloads use `compact-prefix`, 12,000 added UTF-8 bytes and, for automatic
arms, the 4,000 estimated-token cap. All source files must be complete and live
verified. No memory, excerpts, embeddings, network service or auxiliary LLM is
used. These are current frozen compatibility policies, not historical whole-app
reproductions. Do not silently change an arm's settings or supply target hints.

Twelve tasks × four arms × **two repeats = 96 original workers**. Seed is
`20261031`. A seeded task shuffle cycles 12 distinct four-arm permutations;
repeat two reverses each task's order, balancing pairwise precedence overall.
Report actual position/order counts and language strata rather than assuming
perfect position balance. Smaller explicit pilot counts remain labeled pilots.
Every original has a fresh Python process, neutral isolated Git worktree,
database, approval/index and complete preparation attempt. Canonical repository
and worktree names are ordinal only, with no task/arm/language hints. The same
commit/tree and prompt are used for every same-task arm/repeat. No retries,
replacement observations or automatic resume are supported. Preserve every
assignment, stderr/stdout, timeout, code drift, API error and incomplete result.
Timeout or interruption requests cleanup of the worker's own process session,
including inherited Git/parser descendants; cleanup failure halts further work.
An interrupted cohort writes its partial report with planned unrun assignments.
The 2 MiB log limit is post-exit validation, not a guaranteed live disk cap;
normal worker JSON is also bounded before printing. Original logs are retained.

Worker input omits grading targets for automatic arms. Fresh-worker imports
precede timed application setup; measure approval/index and preparation wall,
own CPU and waited-child CPU separately. Their sum is observed local setup plus
preparation, not end-to-end coding latency. Record externally observed worker
lifetime separately; it includes startup and serialization. Worktree creation,
canonical-tree construction, independent grading and report writing are excluded
from application preparation time. Sequential workers share OS caches and host
load; balanced order is not proof of equivalent cache conditions.

## Independent delivery and scope grading

After a worker returns, independently reconstruct delivered source from the
frozen canonical Git tree. Require exact complete file bytes, current SHA256,
whole-file line ranges, bounded source envelope, unchanged task suffix and correct
added-byte accounting. Passthrough must equal the exact original prompt with
empty source metadata and zero added context. An invalid/partial delivery is an
integrity failure, not a useful retrieval. Source/ignore/approval security is
shared across arms and must retain existing application tests.

For positives, report complete required-path inclusion, missing paths, selected
extra paths, byte overhead and bypasses separately. Required-path recall and
selected-path precision are author-scope proxies, not semantic relevance scores.
A safe positive bypass is a selection miss and remains in the denominator. For
negative controls, any preload is an unexpected selection; exact bypass passes
the declared control. B's oracle paths have no measured human discovery cost.
If B and an automatic arm deliver identical source, that proves matching the
declared bundle, not that automation saves model cost or investigation time.

Report task-level consistency across both repeats, per-arm counts, source-byte
fidelity, all individual observations, mean/median local metrics, and paired
differences against B, V1 and V2. Bootstrap 95% percentile intervals resample
**task clusters retaining both repeats**, using 2,000 fixed-seed draws. Separate
positive/negative strata; failed/missing observations remain explicit, and no
all-SKIP policy can pass positive source inclusion. Do not choose only favorable
tasks/repeats. Small controlled intervals do not establish generalization.

## Resources, controls and limitations

On Linux, observed `RUSAGE_SELF.ru_maxrss * 1024` is the whole fresh worker peak,
including imports/setup and preparation, sampled before independent evaluation.
It is not incremental API memory. Waited-child CPU measures synchronous Git/
parser children only; peak waited-child RSS is maximum waited child over the
worker lifetime, not a simultaneous sum. Never add SELF and child peaks.
Unsupported counters are null. Remote resources and actual filesystem reads are
unavailable; retrieval/API counters are explicitly labeled proxies.

Separate small synthetic safety controls cover changed/deleted/ignored files,
symlink escapes and exact fallback. They use no held-out prompts, do not enter
performance summaries and cannot substitute for current integration/security
regressions. No code changes may be made during formal offline timing. The
code/task/provenance seal must match before and after the cohort; drift invalidates
comparison while retaining original outcomes.

Default promotion remains **false**. This evaluation can establish observed
automatic inclusion/abstention, verified source delivery and local overhead on
this corpus only. Native task success, model input/cache/output, total coding
time, model-call counts, API-equivalent cost and actual billed charges remain
null. The runner dispatches zero model requests. Any later paid/native comparison
requires a separately estimated maximum budget and frozen plan; this runner
never starts it.

The generic runner is staged to prevent premature corpus access:

```bash
uv run python -m benchmarks.run_automatic_v3 freeze --output .local/automatic-v3-policy-freeze
# Select/author the independent corpus only after the operator confirms freeze.
uv run python -m benchmarks.run_automatic_v3 controls --output .local/automatic-v3-safety
uv run python -m benchmarks.run_automatic_v3 plan --freeze .local/automatic-v3-policy-freeze/policy-freeze.json --output .local/automatic-v3-plan
uv run python -m benchmarks.run_automatic_v3 run --plan .local/automatic-v3-plan/plan.json --output .local/automatic-v3-offline
```
