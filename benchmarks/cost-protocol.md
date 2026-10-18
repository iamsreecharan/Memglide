# Ten-task Codex / Memglide cost study

This is a prospective comparison of standard Codex (A) against the current
compact-prefix Memglide launcher (B). It does not reuse the earlier format
comparison's legacy-Memglide arm as a Codex baseline. The primary design has
ten fresh tasks, five Python and five TypeScript, run once in each arm: twenty
native executions and ten matched pairs. Tasks are purpose-built small fixes;
they do not represent large production repositories or cross-session memory.

## Freeze and order

Before starting requests, freeze the application source, Git HEAD, corpus,
task JSON, runner and transitive execution/grading helpers, dependency lock,
native executable/version, model, reasoning effort, standard service tier,
timeouts and seed. The durable frozen manifest contains exact hashes and task
prompt hashes. Compare it before and after every attempt; stop the experiment
on source drift. Each task uses the same initial repository commit and tree
in both arms, fresh isolated worktrees, identical common task prompts,
supported final-response schema, native sandbox/settings and test tools.

Shuffle task order using the fixed seed, then alternate A-first and B-first
pairs. For ten tasks this gives exactly five A/B and five B/A pairs. Retain
the full planned assignments, immutable start/results, launch identities and
grants, chained durable log, native JSONL, stderr, final structured output,
grader logs and patches. No automatic retries, cherry-picking, discarded
failures or early stopping based on performance. Shared authentication/runtime
blockers stop future requests and leave those assignments visible as not run.

## Treatment and cache conditions

A invokes native `codex exec` directly and supplies the exact common prompt
on stdin. It creates no Memglide project, database, preparation report, MCP
configuration or source augmentation. B invokes the production
`memglide.integrations.codex_preload` launcher with explicit
`--context-format compact-prefix --mode auto --max-context-bytes 12000`.
Both arms receive identical task-disclosed focus paths. B's deterministic
caller-context condition skips source delivery for the two tasks whose common
prompt already contains complete source. The other eight B assignments use
actual cold production project approval/indexing, then full bounded focused
source. This selection uses no auxiliary model call.

Fresh local native state and worktrees are used for every run. Existing
authentication is referenced by the established isolated-state helper without
reading, printing or copying credential values. All native MCP server maps
are empty. The intervention is pre-execution conditional source delivery;
the benchmark does not claim MCP retrieval was invoked. Cold B indexing is
included in elapsed/local CPU measurements, A has known zero indexing, and
both arms' native launch options match. OS and provider cache state cannot
be controlled; counterbalancing and observed cache usage are reported rather
than claiming equivalent cache hits.

Both arms request `service_tier="default"` using native `-c` configuration.
This is supported by the exact Codex 0.159.2 source tag
`ff6aec96948b70d94983af2641a6b67c94faeff5`:
[`Config.service_tier`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/config/mod.rs#L624)
and
[`SERVICE_TIER_DEFAULT_REQUEST_VALUE`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/config_types.rs#L533).
This freezes the requested routing; actual attributable billing and backend
routing remain unavailable unless the native events independently expose them.

## Independent validity and completion

A's recorded command must equal its native command, and recorded stdin must
equal the exact common task prompt. B's preparation report version 2 must
match the assigned format and forwarded native options. Reconstruct B's
canonical compact-prefix JSON independently from full frozen Git blobs,
sorted source paths, the exact notice and task separator; verify every source
hash and full-file range, added byte budget, actual forwarded stdin hash/size
and common prompt identity. Supplied-context bypass must be byte-identical.
Both arms require a complete supported native event stream beginning with
`thread.started` / `turn.started`, successful exit, terminal usage and a valid
final output schema. Confirm complete MCP call counts are zero.

An external behavioral grader evaluates each attempt independently from the
model's final claims. Existing tests and Git metadata are protected. Completion
requires all of: successful native execution, verified treatment delivery,
passing independent behavior grade and completed status. Report failures and
behavior-only passes separately. An interrupted original remains an attempted
unknown outcome, with partial evidence retained and complete usage/cost null;
a completed-looking JSONL tail does not establish completed execution. Cold B
indexing remains unknown after interruption when not durably measured, not zero.

## Measurements and price-equivalent assessment

The primary report records supported native input, cached input and output
usage; uncached input equals input minus cached input. It also records elapsed
time including B setup, observed child-process and indexing CPU, sampled child
RSS, MCP calls, command-read proxies and tests/completion. Actual model calls,
actual filesystem reads and attributable monetary charges remain null when
not exposed. RSS excludes the parent indexer, can double-count shared pages
and can miss brief children; CPU is an observed local lower bound.

Raw primary `actual_cost_usd` and `computed_cost_usd` fields stay null. A
separate Markdown/JSON assessment may calculate a **price-equivalent estimate**
using cited applicable model rates and native usage, including any separately
reported cache-write tokens or reasoning/output accounting. It must explain
whether the native output field already includes reasoning, whether cache
writes are a subset of input, and the applicable context/service-tier pricing
assumptions; do not double-count tokens or treat absent usage as zero. Preserve
raw usage fields even where shared legacy metrics omit them. ChatGPT account
subscription usage does not establish an actual API bill.

Compute per-run estimates, per-arm totals/means/medians, all-failure-inclusive
cost per successful task and the relative A/B difference. Cost per success is
the sum of costs for **every attempted original**, including failed/unknown
attempts, divided by strictly validated successful completions; missing cost
for any attempted original makes the complete total and complete cost per
success unavailable. Clearly distinguish any known lower bound. Also report
individual pairs, wins/losses, order, provided-source controls and descriptive
strata. Small single-repeat results and uncontrolled provider caches cannot
prove broad savings; do not conceal unfavorable token, latency or cost results.

## Launcher

Root starts the formal run only after corpus controls, local fake-native runner
tests and an independent auditor preflight pass, using a new ignored output:

```sh
.venv/bin/python -m benchmarks.run_cost \
  --output .local/cost-v1/formal-10-v1 \
  --model gpt-6.1-sol --effort low --repeats 1 --seed 20261018
```

Use `--codex-home` only to point to an existing authorized authentication
binding directory, without reading its credentials. A completed experiment
can be validated with explicit `--resume`; it must retain its original sealed
report and make no replacement requests. Partial studies are retained with
their actual failures and unrun assignments.
