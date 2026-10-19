# Native plan and blocked snapshot commands

Run only after the independent corpus author provides the final artifact-digest
receipt. These commands do not enter the frozen runner's execution branch and do
not dispatch native coding assignments, prepare source, or run behavior graders.

From `/workspace/Memglide`, create the real pending 72-slot native plan:

```bash
.venv/bin/python -I -c 'import runpy,sys;root=sys.argv[1];sys.path[:0]=[root,root+"/src"];sys.argv=["benchmarks.run_router_coding",*sys.argv[2:]];runpy.run_module("benchmarks.run_router_coding",run_name="__main__")' \
  /workspace/Memglide \
  --tasks /workspace/Memglide/.local/router-v4/native-tasks.json \
  --grading /workspace/Memglide/.local/router-v4/native-authority/grading.json \
  --grader-root /workspace/Memglide/.local/router-v4/native-authority \
  --fixtures /workspace/Memglide/benchmarks/automatic-v4-fixtures \
  --provenance /workspace/Memglide/benchmarks/automatic-v4-provenance.json \
  --pricing /workspace/Memglide/benchmarks/cost-pricing.json \
  --policy-freeze /workspace/Memglide/.local/router-v4/native-policy-freeze.json \
  --output /workspace/Memglide/.local/router-v4-native-plan \
  --repeats 2 --seed 20261019 --timeout 180 \
  --max-attempts 72 --max-estimated-usd 20 \
  --attempt-reserve-usd 0.25 --max-wall-seconds 18000
```

After the two failed access checks are retained in the independently prepared
`publication-readiness.json`, create the explicitly labelled UNRUN snapshot:

```bash
.venv/bin/python -I .local/router-v4/record_blocked_native_plan.py \
  --plan /workspace/Memglide/.local/router-v4-native-plan \
  --preflight /workspace/Memglide/.local/router-v4/publication-readiness.json \
  --policy-freeze /workspace/Memglide/.local/router-v4/native-policy-freeze.json \
  --output /workspace/Memglide/.local/router-v4-native-blocked
```

The snapshot output is separate from the untouched pending plan and states that
all 72 assignments remain unrun. Its metadata retains both access checks and
unknown spending. The collector should use
`--native-report .local/router-v4-native-blocked/report.json`, archive both
preflight directories and `publication-readiness.json`, and withhold the entire
native authority root unless the cohort has been explicitly retired.

Required author artifacts are twelve public `nNN` tasks with six Python/six
TypeScript tasks over at least six distinct pinned roots, matching private grades,
all retained fixture/license hashes and provenance, plus the final digest receipt.
Before any future eligible native dispatch, each private task must bind
`task_digest` to canonical public-task JSON, `fixture_hashes` to its complete
retained root, and baseline-fail/reference-pass receipts to positive executed-check
counts and the frozen grader script SHA256. The grader script and literal data
paths must stay inside the dedicated private authority root; the interpreter must
be the frozen Python or Node executable. No private oracle bodies enter native
worktrees or public evidence while the cohort remains prospective.
