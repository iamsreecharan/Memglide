# Router v2 engineering validation

Final validation passed: **True**. No model request is made by this collector.

| Verification | Observed result |
|---|---|
| Completed full Python run | 2033 passed; 0 failed; 0 errors; 0 skipped |
| Later runner-only run | 43 passed; 0 failed; 0 errors |
| Distinct full + later-runner identities | 2039; 37 overlapping cases counted once; 6 additional cases |
| Frontend unit cases | 24/24 passed |
| Production browser cases | 3 expected passes; 0 unexpected; 0 flaky |
| Installed-package smoke checks, separate | 14/14 passed |
| Fresh corpus controls, separate | 12/12 baseline failures; 12/12 reference passes; 12/12 partial-fix failures |

The distinct Python count is a union of completed receipts, not a claim that one enlarged full suite ran once. Targeted reruns, smoke checks and corpus controls are not summed into it.

## Retained initial failures

- `.local/auto-router-v2-core.xml`: 2 failed, 0 errors; original XML retained.
- `.local/automatic-validation/router-v2-launcher-compat-initial.xml`: 1 failed, 0 errors; original XML retained.
- `.local/automatic-validation/router-v2-analysis.xml`: 0 failed, 1 errors; original XML retained.
- `.local/automatic-validation/profile-router-v2-unit.xml`: 0 failed, 1 errors; original XML retained.
- `.local/automatic-v2-corpus-tests.xml`: 1 failed, 0 errors; original XML retained.

## Retained frontend attempts

- `.local/router-v2-validation/frontend-unit-initial.json`: 23 passed, 1 failed, 0 pending/skipped; original JSON retained and not added to final frontend count.
- `.local/router-v2-validation/frontend-memory-focused.json`: 1 passed, 0 failed, 17 pending/skipped; original JSON retained and not added to final frontend count.

## Evidence

[Machine-readable validation](router-v2-validation.json) records every copied receipt's source, artifact path, SHA-256 and byte count. Raw receipts live under `evidence/router-v2/validation/`.

- This collector only reads explicit engineering receipts and copies an allowlist. It executes no tests, indexed code, login, discovery query or model request.
- Overlapping targeted reruns and initial failures are preserved but not added to primary test counts.
- The full-run plus later-runner union is distinct from running the enlarged full suite once.
- Installed smoke, corpus controls, component measurements and unit/browser cases have separate denominators.
- No auth, credential, native-state, indexed repository, worktree, database or dependency directory is copied.
- Historical v1 reports and older corpus-v2 experiments are neither modified nor pooled here.
