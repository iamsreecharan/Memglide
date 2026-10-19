# Automatic source discovery: preregistered comparison (automatic-1)

This protocol defines a **future**, approval-gated native comparison. Plan and
offline commands make **zero model requests**. An offline source-selection result
cannot establish coding success, token savings, billed savings or native latency.
Historical reports and original failures remain unchanged.

The question is whether opt-in, deterministic task-to-source discovery plus a
conditional context gate improves total task performance over both bare Codex
and the existing caller-known-path source-only engine. No architecture is assumed
universally optimal. Optional warm memory stays disabled in every treatment.

## Arms and common information

| Arm | Information provided to preparation | Native prompt |
|---|---|---|
| A | No Memglide preparation | Original natural-language task |
| B | Approved project plus private author-known complete-source paths | Original task plus complete source when the existing source-only preparer accepts it |
| C | Approved project plus the same natural-language task; **no target paths** | Original task plus automatically selected complete source only when the new gate accepts it |

The shared public prompt contains natural-language requirements and the same
test-preservation instructions. It does not contain evaluator-known production
or support paths, target identifiers, reference edits, hidden cases or curated
findings. Symbol names in ordinary issue descriptions are allowed. Private
`known_paths` belong only to B's preparation and subsequent evaluator diagnostics;
they never enter C's selection API. No task identifier is added to the native
prompt. Repository tests remain normally readable in all arms.

C's discovery query is exactly the public natural-language task, passed as the
optional `task_query` substring of that shared native prompt. Preparation still
receives and preserves the full shared prompt and workflow instructions. The
production adapter requires this query to occur verbatim in the actual task
prompt; private paths, grader metadata and reference text are not query inputs.
This explicit client query boundary separates user requirements from common
workflow text before held-out evaluation; it does not parse benchmark prefixes
or tune selection against expected files.

All configurations use the same explicit model (`gpt-6.1-sol`), low reasoning,
requested Standard/default service, native Codex CLI 0.159.2, structured final
summary schema, native sandbox and tools. Configured MCP, apps and web search are
disabled equally. The production Python preparation APIs perform **zero auxiliary
model calls**; this is not a live MCP-treatment experiment. Experimental symbol
excerpts are excluded from the initial formal treatment: source delivery is
complete-file fidelity, not an inferred dependency-completeness claim.

## Corpus and held-out boundary

The intended study contains 12 newly authored tasks across four pinned public
upstream repositories: six Python and six TypeScript tasks. Each starts from a
disclosed upstream snapshot with one intentional defect. Source snapshots,
licenses, upstream commits, exclusions and size are recorded by the corpus.
These are controlled mutation tasks, not upstream issue reproductions or proof
of performance in large unfamiliar production repositories. Full versus partial
snapshot coverage must be disclosed accurately.

The discovery implementer uses separate development fixtures and does not tune
ranking or thresholds after observing these task outcomes. Task authors lock
private expected scope and behavioral checks before the first offline evaluation.
Correct upstream source is a reference oracle and never enters the indexed buggy
worktree. Hidden assertions and mutation/reference metadata remain outside source
roots. Baseline-fail, reference-pass and partial/incorrect-change negative controls
validate independent graders before requests. Gold information may not select or
repair C's output. Offline misses are retained; changes motivated by held-out
outcomes require a new future cohort, not reclassification of these observations.

The external grader checks behavior independently of a model's final response.
Pre-existing tracked tests, fixtures, build configuration and Git metadata are
protected according to the corpus contract; source edits outside designated
implementation scope are checked independently. Existing tests remain byte-for-
byte unchanged. Legitimate added tests belong in new files. Protecting source
does not mean executing it during indexing: only the explicitly invoked test
grader executes the task repository. Host isolation is procedural, not a secure
boundary against a deliberately malicious agent. Audit native command logs and
patches for forbidden external oracle access.

## Freeze, isolation and order

`plan` materializes a separate canonical Git baseline per task. The preregistration
seals application Python, benchmark helpers, corpus/fixtures/grading, task text,
private B scopes, protocol, package locks, pricing assumptions, settings, public
prompt hashes, task Git commits/trees and repository identity. A changed file or
Git HEAD invalidates formal dispatch. All original assignments and their order
are fixed before model requests. The SHA-256 sidecar detects accidental edits;
it is not a cryptographic third-party timestamp or adversarial authorization.

12 tasks × three arms × two repeats gives **72 original assignments**. Repeat one
cycles all six arm permutations twice after seeded task/order shuffling. Repeat
two reverses each task's first arm order. Every pair's precedence is exactly
balanced over the two repeats. Per-language order counts are reported rather
than assumed balanced. Each task/arm/repeat uses a fresh isolated worktree,
approval/index database and native state; no source or memories carry between
runs. Same-task starting commits, prompts and grading are identical.

B and C both pay their actual cold repository approval/index cost. C additionally
pays its production live-source refresh, automatic ranking, gate and verification.
Task wall time includes preparation and native execution. Fixture creation,
worktree creation, independent treatment reconstruction and external grading are
excluded and reported separately. Shared imports/harness startup are excluded;
this measures production Python API preparation, not cold preload CLI startup.
Preparation CPU and child-process resources have separate scopes; no host-dollar
rate is invented. Full secure source validation is never replaced by mtime trust.

The same machine, dependencies and settings are used sequentially. Provider and
OS caches are uncontrolled. No cache-affinity headers, private session identifiers
or cache resets are fabricated. Balanced order and observed cache counters do not
prove comparable cache hits. Record concurrent host activity as a limitation.

The inexpensive offline probe runs B then C once per task. Its phase times and
CPU are descriptive observations, **not** the balanced formal latency comparison
above. Warm OS caches can favor the later preparation; do not infer a causal
speed benefit or confidence interval from that single offline pass.

## Approval and estimated budget

No native requests are authorized by this protocol or by historical permission
to run an older study. Present the generated frozen plan and estimated budget to
the user first. The execute subcommand requires both an explicit
`--approved-estimated-budget-usd` and an `--authorization-reference` documenting
**new user approval**. An operator flag is a record of that approval, not proof
that approval occurred. Do not invoke it in the implementation/evaluation turn.

The planning high scenario uses the maximum possible-write API-price-equivalent
observed among the 80 completed historical warm assignments, multiplied by three
per new assignment. With 72 planned assignments this is **USD 18.59** at the frozen
tariff. This is a conservative planning scenario, **not an invoice, guaranteed
maximum, confidence bound or hard spending cap**. Larger/unfamiliar tasks can
exceed it. Codex exec lacks a hard total-turn token cap here. Reverify published
pricing and model availability before requesting approval; a change needs a new
plan. Actual subscription/account charges remain unavailable.

Before each new original, stop if the sum of observed possible-write upper
estimates plus the next planning allowance exceeds the approved estimate. Stop
when whole-attempt usage is unknown, on a confirmed shared auth/quota/network
blocker, source drift or user interruption. This limits additional dispatch; an
in-flight request can exceed its estimate. No automatic retries, replacement
attempts or resume are supported by this fresh-only runner. A hard process death
leaves starts/raw streams as retained partial evidence; audit and stop surviving
processes before any separately approved new cohort.

## Outcomes, accounting and uncertainty

Primary reporting is intent-to-treat: all planned rows, attempts, abstentions,
invalid treatments, timeouts, failures, interruptions, unknown fields and unrun
assignments remain visible. Declining insufficient/over-budget discovery is a C
outcome, not grounds to discard an otherwise correct task. Successful completion
requires valid supported native completion/schema, independently verified complete
source or exact passthrough, zero observed/configured MCP, protected repository
integrity and independent behavior success. Model self-report does not grade work.

Report observed task time including context preparation; preparation/index time;
source decisions, reasons, versions, selected paths, byte/token estimates; native
input, cache-read/write and output counters when available; command/read proxies;
sampled local CPU/RSS and strict success. Native telemetry is retained as raw
JSONL. Cached input is part of total input and reasoning part of output. Whole-
attempt unknown usage is unavailable, never zero. Underlying model-call counts,
actual filesystem reads, provider resources and billed charges stay null.

Resource scopes remain explicit: native child-process RSS sampling excludes the
preparation process, can miss short-lived children and can double-count shared
pages. Parent CPU is recorded separately and includes instrumentation/audit work;
it is not a clean measure of selector-only CPU. Offline preparation records parent
CPU, excluding Git child CPU, and does not measure peak RSS. Individual results
retain command/read proxies and parent CPU even where the compact arm summary
does not aggregate them. Missing measurements are unavailable, not zero overhead.

Price-equivalent cost uses observed usage and frozen official tariff separately
from actual billing. Unknown cache writes get explicit sensitivity scenarios;
reported zero can be an upstream decoder default. Per-arm cost per successful
task includes **every attempted failure's spend**, divided only by strict successes.
Unknown attempted spend or zero successes makes the complete ratio unavailable.
Unrun tasks do not become zero-cost successes. Costs for incomplete campaigns
are clearly labelled known subtotals rather than complete totals.

For B/A, C/A and C/B, report mean and median paired absolute effects, individual
task/repeat effects and missing pairs. Bootstrap **task clusters**, retaining both
repeats together, with 2,000 seeded draws and a 95% percentile interval for the
mean difference. This interval describes small finite-corpus uncertainty, not a
random sample of all repositories. Correctness must be shown before efficiency;
there is no default promotion from an offline coverage score or a favorable point
estimate. A formal recommendation requires no strict-success/security regression,
credible paired time and cost benefit over both baselines, transparent cache
sensitivity and a separate fresh replication.

## Reproduction

These first two commands are local-only and make zero model requests:

```sh
uv run python -m benchmarks.run_automatic plan --output .local/automatic-plan
uv run python -m benchmarks.run_automatic offline \
  --plan .local/automatic-plan --output .local/automatic-offline
```

Only **after new user approval**, a reviewer can execute the frozen study:

```sh
uv run python -m benchmarks.run_automatic execute \
  --plan .local/automatic-plan --output .local/automatic-formal \
  --approved-estimated-budget-usd APPROVED_AMOUNT \
  --authorization-reference 'Reference to the new explicit user approval'
```

Fresh output directories are mandatory. Running module help, importing the
module, plan generation or offline evaluation never authenticates or calls a
model. Tests use fakes and prohibit accidental native dispatch.
