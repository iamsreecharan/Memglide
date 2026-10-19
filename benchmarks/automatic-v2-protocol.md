# Fresh selective-source protocol (automatic-2)

This is a new cohort and policy comparison. The v1 automatic-selection policy,
protocol, source snapshots and negative offline outcomes remain preserved. The
new policy was developed on separate development fixtures. Neither its implementer
nor this runner reads fresh task prompts or expected scopes until the policy and
this protocol are frozen. A favorable result is not assumed.
One compatibility-only edit explicitly pins the old runner's C preparation to
`selection_policy="v1"` after the API gains its new default; historical protocol,
report bytes and original revision remain preserved. This prevents future v1
reproduction from silently selecting v2.

## Question and configurations

The formal comparison remains **A bare Codex, B existing complete-source preload
with evaluator-known paths, C opt-in selective v2 automatic source**. C receives
only the public natural-language task and approved repository. No target paths,
reference bytes, test answers or task identifier enter its API. Its `task_query`
is an exact public-task substring of the shared native prompt; full workflow and
task text are otherwise preserved. B alone receives the private `known_paths`.
No task memory, auxiliary inference, embedding service or live MCP is enabled.
Experimental excerpts remain outside the initial formal treatment: delivered
files must be complete, current source under the existing security policy.

An additional **V1 previous automatic-policy arm is offline only**, using explicit
`selection_policy="v1"`; C explicitly requests `"v2"`. Production defaults do not
implicitly choose the comparator. This separates a new automatic-policy effect
from the caller-known-path benchmark. Historical reports are not rewritten or
pooled with the fresh observations.

The fresh corpus contains 12 independently authored tasks, six Python and six
TypeScript, across four unfamiliar pinned upstream projects. Corpus provenance
records exact commits, full/partial tracked-tree coverage, exclusions, bytes and
licenses. Each task deliberately introduces a documented defect into upstream
source. These are controlled mutation tasks, not upstream issue reproductions,
production prevalence estimates or proof of superior architecture everywhere.
Baselines, reference restorations and partial/wrong fixes are independently
graded before model requests. Hidden tests/reference metadata stay outside agent
and indexed worktrees. No repository install/build hooks are run by indexing.

All arms share the same path-free issue requirements, test-preservation wording,
model (`gpt-6.1-sol`), low reasoning, requested default/Standard service, native
Codex CLI 0.159.2, supported JSONL output/final summary schema and sandbox options.
Configured MCP, apps and web search are disabled. Pre-existing tracked tests,
fixtures, build configuration and Git metadata remain protected; legitimate new
tests use new files. Independent external behavior and integrity checks determine
strict success, never a model's summary. Host filesystem separation is procedural,
not a sandbox against a deliberately malicious agent; review commands for forbidden
oracle access.

The same pinned installed TypeScript compiler is prepended to PATH for every
native arm. Its complete installed package files, package version, executable
binding, Node version/binary hash and the frontend package manifest/lock are
frozen before dispatch. The common trusted workflow states that the compiler
and Node built-in test/assert are available for focused checks, and forbids
installing repository development dependencies or running package lifecycle/build
scripts. This takes precedence over ordinary upstream AGENTS/CLAUDE instructions.
Those upstream instruction files stay byte-for-byte in full snapshots and may
supply repository-map information equally to all native arms; they contain no
author's hidden grades or reference fixes. Upstream complete development suites
are not installed or claimed to pass. Focused native tests and independent
external behavioral grading have their own explicit scopes.
For the installed TypeScript native compiler, all installed optional
`@typescript/typescript-*` platform package files, including the executed native
compiler binary, are hashed as well as the Node wrapper. Large binary hashing is
streamed and remains outside timed product preparation.

## Freeze and order

The preregistration seals application Python, all benchmark Python helpers, both
v1/v2 corpus fixtures, task definitions, protocol, grader, package locks, pricing,
model/native settings, Git HEAD, exact common-prompt hashes and canonical task Git
commits/trees. It records every assignment before requests and rejects source,
task, order or Git drift. Artifact hashes detect accidental alteration; they are
not a third-party cryptographic timestamp or proof of authorization.

Formal: 12 tasks × A/B/C × two repeats = **72 original native assignments**.
Offline: the same tasks × B/C/V1 × two repeats = **72 independent preparations**.
Both plans cycle the six arm permutations twice in repeat one, after seeded
shuffling. Repeat two reverses each task's first order. Every pair's precedence
is balanced across the complete two-repeat design. Per-language order counts are
reported rather than assumed. Dynamic smaller task/repeat invocations remain
explicit pilots and never become a completed 72-assignment study.

Agent-visible directory names contain no task identifier, arm or language label.
Canonical repositories are enumerated as `repositories/repo-0001`; offline and
native worktrees use assignment order only, such as `worktrees/work-0001`.
This also keeps canonical repository names in Git worktree pointers neutral.
Private artifact records retain original task/run identifiers for auditing;
those identifiers are never added to the prompt or working-directory name.

Every observation has a fresh worktree, database/approval/index and, for native
runs, isolated Codex state. Same-task commits and tasks match across arms. B and
C pay actual cold approval/index time; C additionally pays its full live refresh,
ranking, gate and current-source preparation. Time includes preparation and native
execution; fixture/worktree creation, external grading and independent treatment
reconstruction are excluded. Shared module imports occur before timed observations.
This measures production Python APIs, not cold launcher startup. Provider/OS
caches are uncontrolled, sequential runs share the machine and concurrent host
activity is disclosed. Balanced order is not proof of identical cache conditions.

## Fixed technical eligibility, before fresh labels

Before any fresh query is executed or expected scope inspected, freeze this gate:

1. C must preload on **at least 50% of unique tasks**.
2. Among tasks where B can preload the complete known source, C must supply the
   complete author-declared scope on **at least 75% of those tasks**.
3. A task qualifies for either fraction only when the requirement holds in **both
   requested repetitions** (or all repetitions of an explicitly smaller pilot).
4. Every delivered complete-source or exact-passthrough treatment must verify,
   all planned offline observations must be present and no harness errors qualify.

B-preparable scope is an evaluator-only diagnostic, consulted **after** C selection.
The gate filters no individual formal tasks: if it passes, all preregistered native
assignments remain planned, including future C abstentions. If it fails, stop with
the complete negative offline report; do not spend the model allowance. All-SKIP
cannot pass. This is minimum technical eligibility, **not predicted savings,
correctness proof or default promotion**. Expected paths are a target-scope proxy,
not proof that all semantically relevant dependencies were selected. Never tune
thresholds against these held-out outcomes; a changed policy needs new tasks.

## Authorization, budget and durable execution

The user explicitly authorized continuation after the previously disclosed
**USD 18.59 estimated 72-assignment API-equivalent planning allowance**, stating
“no need for approval you have all access.” Record that actual user authorization
in `--authorization-reference`; do not ask for it again. No request is initiated
by importing this module, generating a plan, showing help or running offline.
The root operator dispatches native work only after policy/corpus/protocol freeze,
corpus validation, regression checks and technical eligibility.

The allowance uses the maximum possible-write estimate among 80 historical
completed assignments, ×3 per run, ×72. It is **not actual billing, a guaranteed
maximum, a confidence bound or a hard spending cap**. Codex exec exposes no hard
total-turn token cap here; unfamiliar tasks can exceed planning spend. Actual
subscription invoices, discounts and per-request charges remain unavailable.
Pricing/model changes require a fresh reviewed plan. No credentials are printed,
copied into artifacts or checked in; existing auth bindings are referenced only.

Execute requires the matching sealed offline report and recomputes its gate, an
explicit estimated allowance and actual authorization reference. Before each
new original, stop if observed possible-write upper estimates plus one next-run
planning allowance exceed the authorized estimate. Stop on unknown whole-attempt
cost, confirmed shared authentication/quota/network blocker, code drift or user
interruption. An in-flight request can exceed its allowance. Raw streams, immutable
starts/results and a hash-chained ledger preserve originals. Native child identity
and durable grant precede dispatch. No automatic retries, replacement runs or
resume are supported; hard-process-death artifacts remain partial, require orphan
cleanup and cannot be silently converted into successes.

## Measurements and claims

Preserve individual original rows, failures, strict grades, source version hashes,
gate/skip reasons, ranked candidates, context bytes/token estimates, preparation
times and retrieval/refresh overhead. Independent reconstruction compares every
delivered complete file against canonical Git bytes; passthrough must preserve the
exact original task. Freshness means a verified preparation-time snapshot, not a
promise that the native agent never subsequently edits or re-reads source.

Native measurements, when available: input, cached reads/writes and output;
input-minus-cache-read counts; preparation-plus-native time; command/read/repeated-
command proxies; sampled child CPU/RSS; parent CPU; strict correctness. Selection
uses zero auxiliary model calls. Underlying provider inference counts and actual
filesystem read counts remain null. RSS is sampled native-tree RSS, excludes parent
preparation peak and can double-count shared pages. Parent CPU includes preparation,
sampler and independent audit work and excludes child CPU; do not present their
sum as an exact resource total. Remote model resources are unavailable.
Both offline and formal observations separately record the OS
`getrusage(RUSAGE_CHILDREN)` user+system CPU difference from just before repository
approval/index setup through context preparation, before treatment reconstruction
and native execution. This observes synchronous waited Git/parser workers where
supported; it excludes still-running/unwaited children and later audit/native/
grading work. Unsupported counters stay null. It is not combined with sampled
native CPU or used to infer preparation peak RSS.

Cached input is part of total input and reasoning part of output. Whole-attempt
unknown usage stays unknown. Reported zero cache writes can reflect an upstream
decoder default. Dollars are separately labelled frozen API-price equivalents;
report possible-write scenarios, never call them actual charges or statistical
confidence intervals. Cost per strict successful task includes all attempted
failure costs; unknown attempted spend or zero successes makes the complete ratio
unavailable. Interrupted and unrun rows stay visible, without treating unrun work
as coding failure. Known subtotals are not complete campaign totals.

Report arm totals/means/medians, individual repeats and paired B/A, C/A and C/B
effects. Preserve missing/excluded metric pairs explicitly without dropping those
attempts from primary accounting. For mean and median paired differences, use
2,000 seeded bootstrap draws of **task clusters**, retaining both repeats together,
with 95% percentile intervals. These describe a small controlled corpus, not all
repositories. Offline preparation intervals are local component evidence, not
native latency estimates. Default promotion remains false until strict correctness
and security are preserved and a complete approved native comparison plus fresh
replication supports both cost-per-success and latency benefits over A and B.

The primary report always retains every assignment. Additional descriptive
strata separate C's pre-request source-preloaded versus passthrough decisions;
unknown decisions remain explicit. Controls require equal, non-null observed
actual-prompt SHA-256 values for the same task/repeat in A/C or B/C. Identical
prompts can still produce different native usage and time through stochasticity
and uncontrolled provider caches; those differences do not demonstrate improved
selection. Keep control and source-delivered effects separate rather than using
control variation to claim retrieval savings. Stratum costs retain failures and
unknown spend under the same accounting rules as the primary report.

B is an oracle-path baseline: its author-known paths have no measured human
discovery cost. C's automatic discovery is additional local work. If B/C deliver
identical source prompts, a native point difference is not evidence that C found
better context. Automation capability, local overhead and model efficiency are
separate outcomes; no unmeasured manual investigation time is credited to C.

## Commands

Local-only, zero model requests:

```sh
uv run python -m benchmarks.run_automatic_v2 plan --output .local/automatic-v2-plan
uv run python -m benchmarks.run_automatic_v2 offline \
  --plan .local/automatic-v2-plan --output .local/automatic-v2-offline
```

After the already authorized prerequisites and eligible offline report:

```sh
uv run python -m benchmarks.run_automatic_v2 execute \
  --plan .local/automatic-v2-plan --output .local/automatic-v2-formal \
  --offline-report .local/automatic-v2-offline/report.json \
  --approved-estimated-budget-usd 18.59 \
  --authorization-reference 'User authorization after the disclosed 18.59 USD estimate: no need for approval you have all access'
```

All output directories must be fresh. After any subsequent code or Git change,
regenerate preregistration and matching offline evidence before dispatch.
