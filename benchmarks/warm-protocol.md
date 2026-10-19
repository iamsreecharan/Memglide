# Bounded warm-memory benchmark protocol (warm-1)

This protocol is frozen before the first native request. The primary study is 12
fresh sequences of three related coding tasks, six Python and six TypeScript,
three configurations, two repeats: **216 original assignments**. A smaller
`--limit-sequences` invocation is a pilot and must not be described as the full
study. Importing the runner never makes a model request.

## Capability boundary

Memglide's ordinary memories belong to one bounded session. They do not become
project-global memories when that session ends or expires. C therefore retains
**one still-active Memglide session** while starting a fresh native Codex process
for each task. Default expiration settings remain unchanged (60-minute idle TTL,
eight-hour absolute cap); capture of a real quotation is ordinary write activity,
while preparation does not extend TTL. Session ending, expiration or wrong
ownership cannot create or silently replace a warm session. This experiment
measures active-session memory across fresh agent processes, not persistence
across ended Memglide sessions.

## Configurations and identity

- **A:** native Codex, no Memglide source or memory context.
- **B:** production `prepare_prompt` Python API, compact complete caller-selected
  source, no saved memory. Source-only production defaults remain unchanged.
- **C:** identical B source plus optional bounded `prepare_memory_prompt` context
  selected only from quotations that this arm actually emitted in earlier stages.

The same `gpt-6.1-sol`, low reasoning, explicit `service_tier="default"`, supported
native `codex exec --json --ephemeral --output-schema` interface, task, source/test
path hints, test argv and final response schema apply to all arms. There are zero
configured MCP servers and apps are disabled. Preparation/capture call production
Python services; these are not model-visible MCP invocations or an evaluation of
the Codex preload CLI launcher's startup time. Imports and the long-lived Python
benchmark harness are shared setup and excluded from per-stage time. B/C pay their
measured application setup, preparation and capture work explicitly.

Each sequence/arm/repeat has a separate stable worktree, database and approval.
Each stage's native process has separate ephemeral native state; an existing
credential binding may be referenced by path/symlink, never read or copied. B/C
retain the same approved root/index within their sequence. C alone retains a
memory session; repeat two and different sequences never share memories.

## Canonical transitions and independent grading

All 36 stage snapshots and their Git commits/trees are materialized and frozen
before requests. Stage two includes the task author's canonical stage-one fix;
stage three includes both prior canonical fixes. Every arm begins a stage with
exactly the same declared commit/tree. Earlier model patches and new test files
are archived before the next canonical reset and never become the next baseline.
No repair or baseline selection depends on whether an earlier model run passed.

The external grader checks behavior and protects preexisting tracked files other
than the designated implementation source. Existing tests must stay byte-for-byte
unchanged; optional regressions belong in new files. Native completion/schema,
source delivery, memory delivery, repository protection and external behavior
are distinct checks. Strict completion requires all of them. Failed attempts,
unknown usage, stale controls, absent findings and fallback are retained.

**Memory capture never consults a grading outcome.** The same paid structured
final response in every arm is `{summary: string, findings: [{path, quote}]}`,
with at most three exact contiguous quotations of at most 500 characters. Empty
findings are allowed. A is bare tooling within this matched paid-findings workflow,
not an unconstrained ordinary summary-only Codex prompt. Findings output is charged
in every arm; extraction is not free. C captures only native-schema-valid quotations matching a
currently readable, eligible indexed production source or repository policy
document, excluding protected tests and AGENTS.md, with the current source hash. It saves the exact quotation, not a
model paraphrase or summary. Provenance links the prior native run and final
output hash. This establishes textual support, not semantic truth. Quotes may be
retained even when the independent behavioral grade fails; no grader, reference
implementation or curated gold finding is inserted into memory.

At most six actual earlier captured distinct IDs exist before stage three.
The runner calls the ordinary live production memory snapshot API for each,
records every candidate's freshness, and selects the four most recently observed
Current IDs. Only explicit Stale is an expected exclusion; missing, malformed or
unexpected source-free candidate states are faults. Stale claims are excluded before whole-bundle preparation, so one
old production quotation cannot suppress an unrelated current policy quotation.
This uses no canonical-Git/grading oracle, relevance model, embedding call,
automatic discovery or auxiliary inference. Every validation read is charged. Memory JSON is capped at 3,000 added bytes and source-plus-memory additions
share a 12,000-byte cap. Whole-bundle current-source and lifecycle validation must
succeed. Source changes and genuine absence may yield an expected original-source
prompt fallback; no_current_memory explicitly records an empty Current subset. Stale-memory fallback is reported, never rerun or omitted.
Session errors, unknown/corrupted memory or delivery mismatch are invalid
assignments, rather than successful memory use. One sequence changes the active
policy source before stage three to exercise stale-evidence rejection.

Delivered source prompts are reconstructed independently from frozen Git bytes.
Delivered memory is reconstructed from the actual earlier native final output,
its captured quote hash, provenance and the current canonical source hash.
Stage-one B/C prompt hashes must be equal: neither arm then has prior memory.

## Ordering and immutable observations

All six arm orders occur once per language in each repeat (twice overall).
Repeat two reverses each sequence's order, yielding four occurrences of each
permutation overall and balanced pairwise precedence. The three dependent stages
of an arm run consecutively. Provider routing/cache and operating-system caches
remain uncontrolled; no affinity/session/cache-header manipulation is used.

The shared durable native executor creates a child identity and immutable launch
grant before native execution. Start/result records and a hash-chained ledger
retain each original once. Resume verifies the frozen source, fixture identity
and immutable records; interrupted originals stay interrupted and are not
reissued. There are no automatic retries. A confirmed shared authentication,
quota, model or network blocker stops further requests and marks remaining
assignments unrun, preventing repeated HTTP 401 attempts. A warm-local guard
also stops on an explicit unsupported/invalid response schema error or explicit
HTTP 429 rate limit when native execution failed before any completed turn; it
does not reinterpret ordinary coding/test failures as shared blockers.

## Measurements, denominators and decision

Retain each run's supported raw native events, stderr, final output, exact prompt,
command, grant, result, patch and external grader artifacts. Report input,
cached input and output tokens, observed local CPU/RSS, full/native seconds,
read-command/repeated-read proxies, native MCP calls, tests, strict completion,
quote capture/retrieval/fallback, source freshness and complete source delivery.
Actual provider inference calls, filesystem read counts, server resources and
billed cost remain unavailable rather than fabricated.

Instrumented full execution time includes initial database/approval/index and C
session creation, matched stage reindex, source/memory preparation, native
execution, source quote verification/save, C capture index refresh and end-session
cleanup. It also includes independent benchmark treatment audits: frozen-Git
source reconstruction and C prior-final/source-envelope verification. These audits
are included in parent CPU as well as instrumented full wall time. This is not
pure product latency. Native wall time is reported separately. Fixture
construction/canonical reset, external grading, shared product API imports and
the long-lived harness startup are excluded. Parent CPU plus sampled native child
CPU is a local lower bound. Child RSS excludes parent work and can double-count
shared pages. No hosting-dollar rate is invented.

Use the existing conservative usage parser and pinned cited pricing for a
separately labelled API list-price-equivalent estimate. Cached input is a subset
of total input; cache writes and reasoning are not charged twice. Unknown usage
prevents a complete cost total. Native zero cache writes do not prove actual
upstream zero; preserve possible-write sensitivity bounds. Actual billed cost is
null. Cost per successful task includes every original attempt's cost, including
failures. **Cost per successful sequence includes all three stages and all failed
sequence costs**, divided only by sequences where every stage strictly succeeds.
Zero successes or an unknown numerator yields unavailable, never zero.

Primary comparison: C versus B for full-sequence cost per strict successful
sequence and instrumented full-sequence mean/median time (including independent
treatment audit work), with C versus A also reported. Native wall time is separate. Show
cold stage one separately from stages two/three, individual observations,
per-repeat results, all failures and all fallback reasons. Primary intent-to-treat
results include no-memory and stale fallback observations; memory-used subsets
are descriptive only. No default promotion is justified unless C has at least B's
strict success rate and no worse cost per successful sequence and mean/median
instrumented full time overall and in both repeats. This finite-corpus rule is not statistical
proof or a production guarantee. If evidence is mixed, keep optional memory
explicit and report the tradeoffs rather than claiming a universal win.

## Invocation

After unit/fake-native validation and application/corpus freeze:

```sh
uv run python -m benchmarks.run_warm \
  --output .local/warm-v1 --model gpt-6.1-sol --effort low \
  --codex /absolute/path/to/codex --codex-home /existing/native/home \
  --repeats 2 --timeout 180
```

Fresh output is required. Explicit `--resume` only reconciles durable observations;
it never replaces an original. No request occurs until this command executes.
