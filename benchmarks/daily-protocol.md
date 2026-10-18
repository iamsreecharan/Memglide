# Ordinary-task upfront-context experiment: preregistered protocol

This experiment asks whether deterministic, conditional context preparation helps
on **ordinary same-day coding tasks**, rather than requiring an MCP retrieval for
every task. It does not assume an improvement or replace the preserved 40-task
MCP experiment. Research conclusions and prior development pilots are not scored
as fresh experimental observations.

## Frozen primary design

- Twenty new tasks: ten Python and ten TypeScript, four purpose-built repositories
  with five tasks each. Eight tasks have one explicitly named source file, eight
  need two named source files, and four already include complete relevant source
  in their task prompt. These remain small synthetic repositories; this experiment
  does not establish benefits on large production repositories or long-term memory.
- Two configurations and two repeats: **80 original assignments, 40 matched pairs**.
  A is native Codex without Memglide. B uses `codex_preload` in automatic mode,
  with a 12,000-byte source-context cap, before starting the same native Codex.
- Same `gpt-6.1-sol`, reasoning effort `low`, native CLI, workspace-write sandbox,
  global approval `never`, supported JSON event stream and structured final-output
  schema. The native CLI version and resolved executable are captured before launch.
  Both configurations disable apps/web search and configure an empty MCP map.
- The caller explicitly names the source scope. `focus_paths` are enumerated in
  the common task prompt **for both configurations**. Hidden grading fields such
  as expected symbols and target files never choose B's source bundle.
- B's deterministic policy skips retrieval when the caller says context is already
  supplied, or no explicit focus is available. No auxiliary model request or
  model-visible decision tool is used. Scope-known tasks receive bounded complete
  files; bypasses and conservative fallback decisions stay in the primary results.
- B's forwarded prompt intentionally contains extra source on preload runs. The
  common task-prompt SHA is matched within pairs; the actual model-prompt SHA is
  separately recorded. Actual model prompts are **not claimed identical**. Supplied
  context bypasses must forward the common task prompt byte-for-byte.
- Configurations use fresh worktrees at identical frozen repository commits,
  fresh writable native state and fresh Memglide databases. Actual existing auth
  is referenced by a symlink; credential contents are never read, copied or printed.
  The four context-supplied tasks skip project/index setup as well as retrieval.
- B's cold production project approval/initial index cost is counted on scoped
  tasks. Preparation never fabricates approval rows and never starts a watcher.
  This cold-start design is conservative for an already approved same-day project;
  it does not measure index reuse or cross-session memory.
- Task order is shuffled with the captured fixed seed. A/B order within each task
  reverses on repeat two. Fresh local state does not reset OS or provider caches;
  provider cached-input tokens are reported separately, with no perfect cache-equivalence
  claim and no assumption that cached input is free.

## Delivery evidence and independent grading

B's launcher records preparation mode/reason, common and prepared prompt hashes,
full-file path/hash/ranges, source bytes, preparation wall/process CPU, executable,
native argument array and private-stdin SHA/size before one `execve` of native
Codex. Source bodies are not exposed in argv or duplicated in the report. The
frozen launcher has direct fake-native transport tests proving exact stdin forwarding;
these records attest the launcher handoff, not that a model attended to every byte.

The runner compares delivered file hashes independently against frozen Git source
blobs. Both native event streams must complete with zero MCP calls. A legitimate
B bypass is a valid treatment and remains in intent-to-treat aggregates. Source
hashes establish the pre-execution source snapshot, not semantic completeness or
freshness after Codex's own edits. No MCP invocation is claimed for upfront delivery.

The external corpus grader decides success using behavior tests and smoke tests;
agent final summaries are not grades. Successful completion additionally requires
native exit status zero without a timeout, a complete parsed error-free terminal
JSON event stream beginning with a nonempty `thread.started` identity then
`turn.started`, an independently validated final artifact matching the requested
`summary`/`tests_run` schema, and valid treatment evidence. Behavior-test passes on
failed/invalid/timed-out native executions are counted separately as
`behavior_grade_pass_count`; they do not inflate completion rates or the cost-per-success
denominator. Original repository tests and Git metadata are protected. The runner records any protected-file violation and fails that
external grade. All failed, timed-out, invalid-treatment, interrupted and unrun
assignments remain visible. Failed tasks are never retried into their original slots.

## Measurements and missing data

Report JSON and Markdown include every original run, success counts, execution
statuses, per-arm means/medians/nearest-rank p95, totals and measurement coverage,
matched-pair deltas/ratios and descriptive supplied-context/focused strata.

- Actual native input, cached-input and output usage comes only from supported
  `codex exec --json` usage events. Cached input is part of total input. Uncached
  input is calculated only when both measured values are present.
- Full execution wall time includes B's production project approval/index, launcher
  preparation and native execution. It excludes fixture/worktree creation,
  independent grading and report generation. Native wall time is separately
  available only when an actual monotonic launcher boundary exists; that interval
  includes report-writing/`execve` handoff and ends at observed native child exit.
  A lacks an instrumented native boundary and its separate native interval is null.
- Local child-process-tree CPU and simultaneous RSS are sampled using the existing
  Linux `/proc` sampler. CPU is an observed lower bound; RSS can double-count shared
  pages and misses parent-indexer memory. Parent approval/index process CPU is
  measured separately and added to child CPU without adding launcher CPU twice.
- Native MCP totals should be zero in both arms. Underlying model-call counts and
  actual filesystem reads are unavailable. Observable read-command and repeat-command
  proxies are labelled separately and never presented as actual filesystem reads.
- Actual billing and an applicable verified price schedule are unavailable, so
  actual and price-equivalent cost remain null. Cost per successful task is null
  when any attempted cost is unavailable; if costs become available, its numerator
  includes failed attempts too. No token or money saving is claimed in advance.

## Durability and freeze

`python -m benchmarks.run_daily --output NEW_DIRECTORY --tasks
benchmarks/tasks_daily.json --repeats 2 --seed 20261018 --timeout 180 --model
gpt-6.1-sol --effort low --codex-home EXISTING_AUTH_DIRECTORY` starts the experiment.
There is no implicit paid readiness request. Root may run a separately labelled
old-task development pilot before freezing; it does not enter the primary 20 tasks.

Before model execution the runner freezes source-file hashes, corpus/manifest,
common prompts, Git HEAD, native version/executable, authentication binding path
and settings. Source/settings/commit changes stop the experiment. Do not edit
frozen source, tasks or Git HEAD while it is running.

Atomic fsynced checkpoints, immutable per-attempt starts/results and a hash-chained
attempt log retain each assignment. A child durably records its private process
identity and waits for the parent-written launch grant before starting the launcher
or native process. If the parent dies first, no delayed wrapper can make a hidden
late paid request. Resume stops the exact orphan identity and preserves interrupted
original outcomes and complete usage as unknown; only still-pending slots continue.
Resume also verifies the saved plan against the frozen computed assignments,
checks immutable start/result hashes and artifact paths, and refuses terminal
state projections that disagree with sealed results. Legitimate stale pending/running
crash projections recover from their original immutable records. There are no
automatic supplemental retries in this primary runner. A confirmed
shared authentication/quota/network blocker leaves remaining slots unrun with the
reason disclosed. A finished resume is read-only; no output directory is overwritten.

Selection strata are descriptive. The primary result is the entire frozen set,
including bypasses and failures; a favorable subgroup never replaces it. Two
repeats do not establish statistical certainty, generality or monetary benefit.
