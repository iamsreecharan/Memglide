# Reproduce the recorded v4 selection study

Read [the assessment](router-v4-assessment.md) before running anything. V4 failed
its selection gate. Replaying this exposed corpus cannot establish a fresh
held-out improvement, and the prospective native coding study was not executed.

The frozen implementation and both runners are at
`0b8e3586554a5002b6d49ded21d64b923a27a99c`. The later assessment commit adds
corpus/evidence and documentation; it does not retune that implementation.

Use a separate isolated checkout of the recorded implementation commit for a
historical replay. Restore the four public task/control/grading/provenance JSON
files and `automatic-v4-fixtures/r01` through `r06` from the assessment commit.
Keep them byte-identical. Copy the original offline policy seal from
`evidence/router-v4/freeze/offline-policy-freeze.json` to a local replay directory. The
evidence ledger hashes each retained file; do not modify the archived originals.

Install the frozen dependencies and match the Python, SQLite and grammar
versions recorded in the seal. Its verifier rejects a changed implementation,
Git HEAD or runtime. Create new plan/run directories rather than changing the
original absolute-path plan:

```sh
uv sync --frozen
uv run python benchmarks/run_automatic_v4.py plan \
  --freeze /absolute/replay/policy-freeze.json --output /absolute/replay/new-plan
uv run python benchmarks/run_automatic_v4.py run \
  --plan /absolute/replay/new-plan/plan.json --output /absolute/replay/new-run
```

The replay runs 96 local preparations and zero model requests. Keep every new
result and label its host/cache conditions. Different timings are possible;
matching source output does not reproduce model tokens, coding correctness or
charges, which this study did not measure. Creating a new seal after inspecting
this corpus would not turn the replay into a preregistered fresh evaluation.

The public native artifacts contain the actual 72-slot plan, its blocked
snapshot, public requests, hash seals and standard-control count projections.
Private grader/reference bodies and the compiler package remain local and are
not published. That limits public reproduction of native grading. No native
coding outcome is claimed. The n06 punctuation correction, performed after the
offline cohort and before native planning, is separately versioned and disclosed.

For connection setup use [the cloud access guide](../docs/cloud-benchmark-access.md).
Restoring connectivity does not clear v4's failed selection gate or the recorded
native-grader coverage/isolation limits. A new policy needs separate development
cases, a new pre-corpus freeze and independently authored held-out tasks.
