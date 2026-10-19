# Fresh offline v4 source-selection comparison

This runner measures automatic source inclusion, safe bypass, verified complete
delivery and local preparation overhead. It never dispatches a native agent or
model. It does not grade code changes, infer avoided investigation, or report
model-token/cost/billing savings. The v3 code, corpus, protocols, reports and raw
failures remain unchanged and are not pooled with this cohort.

## Freeze and independent authoring

Freeze production v4, the preserved v3 policy branch, this generic runner, its
tests/protocol and trusted transitive v3 verifier before any new repository/task
selection or inspection. The freeze records Git HEAD, application/generic helper
hashes, package locks, API settings, Python/SQLite/grammar versions and fixed order
seed. Native infrastructure has its own freeze; this runner never imports it.

Only after the root confirms both infrastructure freezes may an independent
author select **at least six previously unused, unrelated upstream roots** and
write twelve realistic positive coding tasks, six Python and six TypeScript,
plus four separately labeled abstention controls. Each positive must describe a
concrete requested behavior, fix, extension or refactor. Purely vague review
prompts cannot serve as positive tasks. Public tasks contain no manually supplied
target paths, snippets, reference edits, test answers or grading metadata.

`tasks_automatic_v4.json` holds twelve positive public objects;
`controls_automatic_v4.json` holds four public controls. Each object has only
neutral `id`, neutral `repository`, `language` and natural-language `prompt`.
`automatic-v4-grading.json` separately declares the required **existing source
paths** and author rationale. They are contextual source-scope proxies, not proof
that every semantic dependency is present or that an eventual code edit is
correct. New files that do not exist yet cannot be required preload targets.
Actual native fixes/behavioral graders remain separate artifacts, never read by
automatic workers or this offline grader. Native tasks must be distinct from
these offline tasks even when repositories are shared.

The four controls are declared safe-bypass expectations for underspecified or
unsupported requests. They are normative controls, not proof that no conceivable
source could help. Keep control outcomes separate from positive inclusion, and
explain bypasses caused by unrelated index/availability errors rather than
crediting them as semantic discrimination.

Provenance records pinned upstream commits, HTTPS archive URLs/SHA256, retained
byte hashes, licenses, coverage/exclusions and any parser issues. Do not prune an
unfavorable source file or rewrite a task after a query. Never install or execute
upstream source, tests, hooks or build scripts while preparing/indexing. Freeze
all corpus bytes, public/private metadata, provenance, canonical Git trees and
every assignment before formal evaluation. Any changed policy needs new held-out
tasks; it cannot replace these original outcomes.

Canonical Git setup ignores inherited Git overrides, system/global configuration
and attributes, hooks, fsmonitor and signing. A highest-priority local attributes
policy disables filters, text/EOL/ident and working-tree-encoding conversion.
Templates are disabled. Independently require canonical Git blob hashes and path
sets to match retained fixture bytes per repository, and verify neutral repository
mapping before workers. Worktrees inherit the byte-preserving attributes policy.

## Arms, settings and isolation

- **B**: existing complete-source `prepare_prompt`, private known existing paths
  for positives; exact original task for controls.
- **V3**: preserved `prepare_task_prompt(selection_policy="v3")` behavior.
- **C**: new opt-in `prepare_task_prompt(selection_policy="v4")`.

Every arm receives the identical public task, same snapshot and fixed
`compact-prefix`, 12,000-byte added-context cap. Automatic arms use the 4,000
estimated-token cap. No excerpts, warm memory, embeddings or auxiliary inference
are enabled. Automatic worker requests have a strict allowlist and contain no
target paths, task IDs, semantic repository labels, grades or hidden fixes.
Only B receives known paths. No policy override or target hint is injected into
the task. V3 is a frozen-behavior compatibility arm in the same frozen current
application, not a historical whole-system reproduction.

Twelve positives × three arms × two repeats = **72 main observations**. Four
controls × three arms × two repeats = **24 control observations**, reported
separately: **96 original workers total**. Fixed seed is `20261107`. Within each
stratum a seeded task shuffle cycles all six arm permutations; repeat two
reverses each task's first order. Actual arm positions, language/repository
strata and pair precedence are reported, including any finite control imbalance.

Each observation has a fresh Python worker, neutral isolated Git worktree,
approval database, initial index and one API preparation attempt. Canonical and
worktree names are ordinal, with no target/arm/task hints. No retries,
replacement originals or automatic resume. Preserve failed, interrupted and
unrun assignments. Every exit receives own-session descendant cleanup; unknown
cleanup halts the cohort. The 2 MiB log check is post-exit validation, not a live
disk cap, and original stdout/stderr remain intact. Normal JSON is bounded before
printing. The worker timeout is 90 seconds.

## Verification, measurements and uncertainty

An independent frozen verifier reconstructs every delivered file from canonical
Git bytes, requiring exact whole-file content, SHA256, line ranges, unchanged task
suffix, duplicate-free canonical JSON and correct byte accounting. Exact
passthrough must attach no evidence. A partial/invalid delivery fails integrity;
it is never counted as successful source inclusion. Consult private scope labels
only after the automatic worker returns.

Report positive complete declared-scope inclusion, missing/extra paths, safe
bypasses and controls separately, with planned denominators. Report task-level
consistency across both repeats. All-SKIP earns zero positive inclusion.
Author-scope path recall/precision are proxies, not semantic relevance or coding
success. B has oracle paths with no measured human discovery cost. Matching B's
prompt proves the same supplied source, not lower model cost.

Imports precede application timers. Record approval/index setup and preparation
wall, own CPU and waited-child CPU separately, plus externally observed worker
lifetime. Lifetime includes startup, verification/serialization and cleanup; it
is not pure API or launcher latency. Linux SELF peak RSS includes imports/setup
and preparation; it is not incremental API memory. Waited-child peak RSS is
maximum waited child, not simultaneous summed RSS. Never sum parent/child peaks.
Unsupported counters remain null. Balanced order does not equalize uncontrolled
OS caches or host load.

Per-arm tables include means, medians, missing measurements and failed-attempt
lifetime. Paired C-minus-B and C-minus-V3 metrics retain task/repeat identity.
The primary 95% percentile bootstrap resamples **repository clusters**, retaining
all their tasks and repeats, using 2,000 seeded draws. Report cluster/task/pair
counts and per-task effects. The small corpus and shared source scopes limit
generalization; do not infer statistical superiority from isolated point values.
Intervals are exploratory and unadjusted for multiple comparisons.
Missing/invalid pairs remain explicitly counted and prevent complete-integrity
claims. Keep positive and control timing strata distinct; lower source bytes from
missed tasks do not demonstrate token savings.

Code/runtime/provenance/task/plan-byte seals must match before and after the
cohort. Retain the original plan bytes and hash, immutable per-run requests,
results, stdout/stderr and the complete raw report. No code changes during
timing. Default promotion remains **false**. Coding correctness, total coding
latency, model usage/cache/output and estimated/actual model charges are null.
This runner dispatches zero model requests. A later native comparison requires
its separately estimated maximum budget and frozen plan and is never started by
this program.
