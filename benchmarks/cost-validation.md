# Ten-task cost-study validation

**113 distinct new checks passed:** 35 corpus checks, 27 runner checks and 51 cost-accounting checks. Zero final failures, errors or skips. These tests made no model requests; the live 20-run comparison is separate. Initial and final reruns overlap and are not added.

Corpus validation verified all ten baseline failures and correct-reference passes, eight partial-fix failures, protected-test integrity and legitimate added-regression handling. The initial suite had one copied test-helper import failure (34 passed, one failed). The helper was corrected without changing behavioral-oracle or reference-fix semantics; initial output and an AST equality receipt are retained.

Runner checks cover direct standard-Codex input, compact-prefix delivery from independent frozen Git bytes, balanced order, durable starts, actual orphan recovery, shared authentication/source stops and preservation of all original assignments. A broad imported-module type check initially reported 33 errors. The new runner's missing list annotation was fixed before freezing; the other 32 errors concern unchanged historical benchmark modules. Focused runner type checking passed. The failed broad log is retained; no broad benchmark mypy pass is claimed.

Accounting checks cover separate cache-read/write pricing, reasoning as a subset of output, strict native event framing, unknown costs, failed-attempt numerators, unique successful-task denominators, input reconciliation, threshold uncertainty, write sensitivity, component/stratum arithmetic and no-overwrite CLI behavior. Its Ruff and formatting checks passed, with exact receipts preserved.

The application runtime remains at source hash `e777cbd53a1ca6228e5c3403ebb5cc3547834a00edac1d1f20210342740aeee4`. The earlier 988 application/tooling cases passed at this same application hash; the combined enlarged suite was not rerun for this tooling-only change.

Runtime runner, corpus and official pricing were frozen at `c7be678ab52aa5dab1f2a03317e53f2f6b0e5168` before formal requests. The accounting module is separate postprocessing completed afterward; native task execution never imports it. Passing checks establish mechanics, not actual billing or performance savings. Exact counts, source hashes and preserved failure paths are in [JSON](cost-validation.json).

After the native experiment finished, a scoped Ruff and formatting check passed on all six newly authored benchmark/accounting modules and tests. This did not alter any source or rerun model tasks. Receipts are retained under `final-static/`.
