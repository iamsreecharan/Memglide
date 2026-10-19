# Independent v4 heldout and native coding corpus: design only

Status: framework proposed before policy/runner freeze. No upstream repository,
commit, change request, expected target, test, or reference patch has been chosen
or authored. This document is ignored and is not a policy tuning input. The
author has not inspected the v4 implementation, dev tasks, old frozen tasks, or
their fixes. Actual corpus authoring begins only after the root supplies the
frozen policy and runner commit hashes.

## Freeze and independence boundary

Record the policy commit, runner commit, clean-tree state, configuration digest,
model/effort configuration, and the creation time of the post-freeze corpus.
Neither policy nor runner may change after task selection. Any necessary repair
creates a new experiment/version and invalidates claims of an untouched holdout
for earlier exposed tasks. Preserve failed runs and exclusion reasons.

Preferred design: use separate post-freeze selection and native coding sets.
Selection tasks measure the existing routing/output contract without allowing
their labels, outputs, or grader feedback to influence the policy. Independently
authored native coding tasks then measure actual code changes. If budget or
authoring limits require reuse, call this sequential exposure explicitly:
selection results preceded coding, and native coding remains an independent
behavior grade but not a fresh selection holdout. Never describe reused tasks as
fully unseen end-to-end evidence.

## Corpus shape and sampling

Offline selection set: 12 positive requests plus 4 separately reported abstention
controls. Distinct native coding set: 12 positive requests, exactly 6 Python and
6 TypeScript tasks across at least 6 unrelated upstream roots, at most 3 tasks
per root. Prefer the same upstream roots with independently chosen behaviors;
record shared-repository exposure while keeping all task labels and hidden
behavior graders private. Use different upstream maintainers/projects rather
than forks or sibling packages from one monorepo. Native controls are optional
additional evidence, not part of the current 12-task coding minimum.

Choose upstream repositories and exact archive snapshots after freeze. Preserve
the upstream URL, immutable commit, archive URL, archive SHA-256, source-license
identifier, extraction manifest, and acquisition timestamp. Avoid current
HEAD-only references. Prefer small libraries or a coherent maintained subset
that can run with Python standard library or an already available Node runtime,
without fetching dependencies or executing install/lifecycle scripts. A subset
must retain the relevant original modules and provenance; record exclusions and
never relabel a synthetic implementation as an upstream repository.

Select bounded, representative code changes across multiple behavior families:
boundary handling, value normalization, collection behavior, parsing or
serialization, and public option handling. These are allocation categories,
not selected tasks. Aim for one or two production files and a small reviewable
patch, while allowing discovery of neighboring definitions. Reject candidates
whose specification is ambiguous, whose grader depends on timing or networking,
whose baseline behavior already satisfies the request, or whose intended fix is
merely a spelling edit. Do not deliberately optimize tasks for one router mode.

Controls should include both behavior already satisfied by the pinned source
and relevant requests whose correct result is no code change. They must be
plausible requests with explicit acceptance criteria, rather than impossible
requests or prompts that instruct the model to abstain. Grade unauthorized or
unnecessary production edits separately from a correct no-op outcome.

## Private task package

Each opaque task ID has three components with separate filesystem roots:

1. Indexed source root: upstream original source plus a minimal neutral harness
   entry point if required. No hidden tests, expected path lists, reference
   patches, answer-bearing names, or author notes live here. The source directory
   and task ID use opaque names; prompts can name public APIs where the change
   naturally requires it, but cannot name files, directories, glob patterns,
   line numbers, search hits, or exact target-path strings for A/C.
2. Private authority root outside every indexed root: the canonical request,
   selected source-scope labels, reference patch, protected-file manifest,
   expected behaviors, behavioral grader, and baseline/reference results. Never
   make this root available to the coding agent or repository search/indexing.
3. Per-run output root: arm, repeat, ordering, timestamps, hashes, tool/model
   events, patch, grader output, and accounting. Never feed another arm's output
   to the coding agent.

Keep the source snapshots mechanically faithful. If portability requires a
fixture or shim, commit it to the source fixture before the task is constructed
and apply it identically for all arms. Record this preparation separately from
the requested change. Avoid naming fixtures or tests after the expected fix.

## Independent behavior grader

Use external Python `unittest`/standard-library subprocess checks or Node
standard-library assertions. TypeScript candidates need an existing usable
runtime/compiler or a deliberately small source-compatible subset; verify that
the harness executes the production code the agent changes. Do not silently
grade a prebuilt JavaScript artifact that ignores a TypeScript edit. Do not
execute untrusted package-manager installation or lifecycle hooks. Source under
test is executed only during controlled coding tests with an explicit command,
time/resource bound, temporary working directory, sanitized non-secret
environment, and no network requirement.

Behavior assertions derive from the written request and independently reviewed
expected semantics. Include the main requested behavior, boundary cases,
regression cases for neighboring existing behavior, and at least one check that
distinguishes a superficial constant/output hack from the intended behavior.
Avoid assertions that merely duplicate the reference implementation. A valid
alternative implementation must pass. Task source-scope labels cannot decide
behavior correctness.

Before admitting any positive task, the grader must fail the original pinned
snapshot for the intended behavioral reason and pass the reference patch. Save
both complete outcomes and the failing assertion. For controls, the original
must pass; a no-op reference must pass. Add harness self-checks for nonzero test
execution, current task/commit identity, timeout propagation, and failed import
or subprocess exit status. An infrastructure error is not a task failure or
success. Reject or repair broken tasks before the evaluated arms run, then
record the final task-package digest.

Grade a run from a fresh read-only copy of its final patch applied to the frozen
source. Verify the exact initial commit and tree hashes, original source file
hashes, Git metadata integrity, and a protected-file manifest before and after
the run. Reject edits to the hidden grader, harness assertions, expected output,
tests designated as protected, manifests/lockfiles outside task scope, Git
metadata, and source provenance. Detect file deletion, renamed/symlinked files,
mode changes, untracked generated artifacts, and an agent returning only a
verbal answer without its required patch. Keep policy/tamper status separate
from behavior pass/fail; do not hide a failed behavior grade behind scope labels.

## Native A/B/C protocol

Use the root's frozen definitions of A/B/C verbatim. B is explicitly privileged:
it receives the correct source file paths as a known-path oracle. A and C get
the exact same path-free change request and ordinary source-discovery
capabilities permitted by their frozen mode. Do not provide A/C target paths
through prompt prose, environment names, test commands, filenames, traceback
snippets, repository aliases, or paths in a task manifest. Public API names and
ordinary upstream repository structure remain legitimate source context.

Provide all arms the same public sanity-test command, if a candidate has one.
The hidden behavioral grader remains external and unavailable during coding;
its invocation is an observer action after the run. If no public sanity command
is useful, say that plainly and allow agents to run their own bounded checks.
Do not expose a private grader path as an apparently available coding tool.
Record public check availability as a task attribute.

Each arm starts from the same pinned source commit and byte-identical task
prompt except B's disclosed oracle addition. Use fresh native sessions, distinct
source roots, a cleared session/conversation state, and a documented equal cache
condition. Use the same model, effort, tool configuration, time/token budget,
observer instrumentation, and coding/test permissions across arms. Preserve
which startup/index warmups are charged and their duration. Prevent index,
conversation, filesystem, and test-result leakage between repetitions or arms.

Run two independent repetitions of all 12 coding tasks: 72 native sessions. Balance the
six A/B/C permutations across tasks and reverse or re-randomize them for the
second repetition using a committed random seed. If execution is concurrent,
record concurrency and ensure no arm shares writable source/cache state; do not
compare one serial arm with another heavily contended arm. Capture wall-clock
and work time using the same observer boundaries for every session.

## Separate measurements and claims

Report source-scope quality and actual coding correctness in distinct columns.
Source-scope labels are private independently authored evidence: for each task,
state the required discovery/production file set and justified optional neighbor
set. Report coverage and excess scope without counting an alternative valid
implementation as behavior failure. Keep selection completion, valid output,
abstention, scope grade, executable patch, hidden behavior pass, protected-file
status, and infrastructure status distinct.

The paired coding result is task-level pass on both repetitions, one of two,
or neither, alongside individual run results. Aggregate by task and repository
as well as session so correlated repeats do not masquerade as 96 independent
tasks. Report paired A/C and B/C correctness differences, per-task and overall
wall time, observed model input/output/reasoning tokens, router/search overhead,
and API-equivalent cost from a dated explicit rate table. Native subscription
billing is unknown; never claim actual savings from output length alone.

Always publish the 12-task native and separate 16-task selection denominators,
exclusions, missing runs, timeouts, selection controls, and baseline/reference
admission checks. A small 6-repository sample
can support an observed tradeoff on these bounded tasks; it does not establish
general production superiority or a universal correctness-equivalence claim.

## Practical budget envelope for root

At 12 tasks × 3 arms × 2 repetitions, there are 72 native sessions. A $20 total
API-equivalent ceiling permits an average of $0.2778 per native session before
selection and shared overhead. A provisional $3 reserve leaves $0.2361 per
native session; root must increase the reserve if the 96 separate offline
selection sessions and router/search/setup/reference costs exceed $3.
Root should translate that ceiling through the chosen model's actual rates,
including cached/uncached input, output/reasoning, tool calls, and any minimum
charges. This is planning arithmetic, not a billing guarantee.

Keep native work bounded with small dependency-free snapshots, compact requests,
short public smoke checks, a fixed reasonable per-session context/output budget,
and explicit timeout accounting. Stop at the precommitted global spend cap;
report incomplete coverage instead of silently dropping expensive failures or
shrinking an arm's budget. A 2-task-per-repository distribution over 6 projects meets the coding minimum
and is easy to pair; using more projects increases diversity. Choose only after
freeze and preserve the precommitted language and task counts.

Authoring can proceed incrementally after freeze: admit and hash the entire
corpus before observing any evaluated arm, then execute the full matched
schedule. Use baseline/reference grader validation to reject bad candidates,
never evaluated-arm performance. Root owns model dispatch and spending policy.
