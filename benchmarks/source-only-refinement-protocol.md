# Source-only request-local policy refinement: frozen local protocol

This preregistration compares the exact trusted source-only preparer at Git
`391d86e` with the current preparer after a request-local compiled-ignore cache.
The baseline file is `src/memglide/integrations/preload.py`, SHA256
`9ae8595b4b5f97993dcf177d78d090db5f1e0f6fdb8ce2e2da5e3d766d69afac`.
The runner rejects another baseline blob. This is a component comparison of
source preparation, not a rerun of earlier coding-agent cohorts.

The experiment calls `prepare_prompt` directly with explicit known source paths,
`context_format="compact-prefix"`, a 12,000-byte envelope cap, and the same public
task. This is the source-only compact architecture used by the earlier positive
agent cohorts. Default legacy API compatibility belongs to application regression
tests; it is not mixed into this timing cohort. There is no automatic selection,
memory, MCP server, model, native agent, authentication, network, indexing,
Tree-sitter, repository test execution, or source clipping in this experiment.

## Freeze and fixtures

Before any worker is started, save the resolved baseline commit, exact baseline
and candidate source snapshots/hashes, runner/test/protocol hashes, all current
application Python hashes, Git HEAD, Python version, fixed settings, and every
assignment in a manifest. Verify that seal immediately before dispatch and after
all workers. A seal failure invalidates the comparison while preserving outcomes.
Workers verify their snapshot before importing it and after calls. Production
code must not be edited during timing. Git extraction executes trusted project
code only; synthetic fixture source is never executed. Both arms share the same
sealed current application dependencies; this is not a historical whole-app run.

Three synthetic development fixtures are defined in the runner, independently of
all held-out coding tasks:

1. `noignore`: one small complete source file, no policy files.
2. `typical`: four nested complete source files, three short policy files.
3. `dense`: the exact same four source paths and bytes as `typical`, one root
   `.gitignore` containing exactly 8,192 bytes of harmless, nonmatching patterns.

Every observation gets a fresh directory, source fixture, and minimal SQLite
approval state. SQLite contains only the tables/columns needed by the preparer's
existing read-only approval/policy lookup. Setup does not construct an index or
parse source. It must not be described as a real repository cold-index benchmark.
Approved paths, complete prompt bytes, private source SHA256/ranges, and every
stable preparation-result field must equal an independently constructed canonical
payload. Baseline and candidate must agree exactly. This is controlled fidelity
validation, not independent coding-task correctness or completeness grading.

## Assignments and independent units

There are **12 paired repetitions × three fixtures × two arms = 72 performance
workers**. The fixed seed is `20261019`. Within each fixture, exactly six pairs
run baseline first and six candidate first; pair order is seeded and shuffled.
Every worker is a fresh Python interpreter and database. No automatic retries or
replacement observations are allowed. Smaller `--repeats` invocations are labeled
pilots; repetition bounds are 1–12. A worker has a 30-second timeout and a 1 MiB
stdout cap, and cannot dispatch a model. Output directories must be new and
canonical; existing output is never overwritten.

A performance worker imports only the frozen preparer module, initializes its
fixture/approval database, and calls the API once, including its first lazy
dependency imports. It then calls the same API five more times. Each call retains
its raw observed wall time, own-process CPU, waited-child CPU when available, and
stable full result. Setup and subprocess lifetime are reported separately.
Subprocess lifetime includes interpreter startup, setup, preparation, independent
verification and serialization; it is not pure launcher or API latency.

Five inner warm calls form **one worker mean**, not five independent trials.
Primary comparisons pair first-call wall/CPU and worker mean warm-call wall/CPU
by fixture/repetition. Other resource and setup metrics remain descriptive.
Report every worker, failure, mean and median paired effect, and within-worker
warm-call variation. Bootstrap 95% percentile intervals resample the 12 paired
worker units, with a fixed seed and 2,000 draws, for both mean and median paired
deltas. Each arm's own mean and median are also reported. These are small-sample local
intervals, not a guarantee against host/cache bias or evidence of generalization.
Incomplete/invalid pairs remain in denominators and are explicitly counted; any
missing worker or failed invariant prevents a complete-valid comparison.

## Separate instrumentation and resources

**Six additional diagnostic workers**—one per fixture/arm—repeat the first plus
five warm calls with secure-source-read and policy-compilation counters installed.
They do not enter performance summaries: **72 PERF + six DIAGNOSTIC = 78 workers**.
Their first calls are fresh-process diagnostic calls, not measurements of cold
import latency. Count policy/source API read attempts, successful reads, and read
bytes separately for every phase. These are read-call observations, not actual
filesystem or storage I/O. Source and policy verification reads must be preserved.
Policy compilation counts are explanatory measurements, never additive timing.

The diagnostic workers also check explicit disabled/context-supplied/no-focus and
over-budget fallbacks. Every fallback must retain the exact original task, empty
source list, and zero context; its stable result must match the baseline. Existing
application security/race tests provide broader coverage. No timing from these
controls or instrumented calls is pooled with performance observations.

Linux `resource.getrusage(RUSAGE_SELF).ru_maxrss * 1024` is reported as the observed
whole worker's peak RSS, including interpreter/imports/setup and preparation,
sampled before independent verification. It is not incremental API memory.
Own-process CPU excludes children; waited-child CPU is separately reported where
available. Peak waited-child RSS means the maximum waited child over the process
lifetime, not simultaneous summed RSS. Never add SELF and child peaks. Unsupported
platform measurements are null; no platform-dependent unit guess is allowed.
Allocation instrumentation is omitted to keep timing uninfluenced.

## Interpretation and reporting

Retain raw stdout/stderr, timeout output, partial call errors, all original
assignments, code seals and canonical result hashes. Report cold and warm effects
separately; never combine them into agent latency. Fewer compilations or smaller
local CPU work alone do not establish end-to-end model savings. Model input,
cached input/write, output, actual model calls, task success, API-equivalent model
cost and billed charges are unavailable/null. The runner itself dispatches zero
models. Historical reports remain unchanged. Negative results, noisy/no-effect
controls, fallback mismatches and regressions must remain visible.
