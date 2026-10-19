# Efficiency changes: engineering validation

The full application regression run passed **1,367 cases**: 1,340 Python, 24 frontend and 3 production Chromium. Another **76 new confirmation-benchmark cases passed** (41 corpus, 35 runner), for **1,443 distinct verified cases**, with no final failures or skips. Application source stayed unchanged. All 1,416 current Python cases collect cleanly; an enlarged full-suite rerun is not claimed. Two upstream Click deprecation warnings remain. Overlapping targeted reruns are not added to this count.

Frozen implementation: `93acf63e1583bd66239b22dc53c2aaf196e3a35a`; application SHA256: `43032dcabab006ec346b77d2032da9b7016adfea2ff013cf414d25f67f61f176`.

## Changes verified

- Exact selected-source and memory-dependency invalidation replaces substring matches in unrelated passport text.
- Retrieval, passport, lifecycle check, event and activity refresh publish atomically under the active-session gate.
- Memory relevance prefilter avoids irrelevant live source reads while retaining all eligible freshness checks and ranking.
- Optional complete caller-selected support uses existing secure bounded all-or-nothing preload; no automatic discovery, model selector or command execution.
- Unverified cumulative/resumed native usage is rejected instead of charged as new incremental usage.
- Unique pytest temporary directories prevent concurrent invocations deleting each other fixtures.
- Live benchmark typing passes combined application/harness checking without suppressions.

The measured local fixture reduced secure source-reader invocations **55→15**, with selected evidence unchanged. Separately, 1,200 synthetic old/new selection cases matched; their freshness views were precomputed. Neither result measures model tokens or dollars.

## Complete integration and package checks

Ruff and whitespace checks pass. Combined mypy passes all 24 application and 34 live benchmark modules. A clean installed wheel passed real loopback CLI/API/SPA and default/agent MCP checks, legacy v1/compact v2/support v3 behavior, current-source validation and security bypasses. 11,851 archive checks verified 24 application files and 19 frontend assets. 12 preload and 31 support/MCP functional checks are separate from pytest. No model requests were made for these engineering checks.

## Failures retained

- `corpus-tests.xml`: 32 cases, 4 failures, 0 errors. Three shared-basetemp fixture deletions and one incomplete-test-coverage assertion; fixed isolation and strengthened the new grader.
- `corpus-tests-final.xml`: 36 cases, 2 failures, 0 errors. Two Node 24 reporter-shape assertions were corrected before freeze; full behavior checks retained.
- `launcher.xml`: 48 cases, 1 failure, 0 errors. New regression-test assertions were initially placed in the wrong test; corrected test placement.
- `runner-tests-initial.xml`: 33 cases, 0 failures, 1 error. Concurrent shared-basetemp deletion removed a SQLite fixture; unique temporary directories fix the cause.
- `independent-review-cost.xml`: 38 cases, 1 failure, 0 errors. Markdown omitted the actual third configuration label; renderer fixed and all-arm unknown-cost gate strengthened.

The old-method negative control intentionally failed 13 of 23 cases; the current methods passed all 23. An initial installed smoke used an unsupported memory category and correctly failed; its log and original script remain. Initial type-check failures are retained with corrected source transitions. An earlier 90-case partial full run was interrupted before final collection; it is not counted as a completed suite.

All 11,501 historical report/configuration/evidence/archive files remain byte-identical to 448f705. Source helpers have explicit authorized fixes; historical reports and results were not rewritten.

These checks demonstrate the listed observed defects are fixed within their coverage. They do not prove every repository or task is cheaper or faster. Fresh native comparisons, all failures and list-price-equivalent cost-per-success accounting belong to the separate workflow reports. Actual billing remains unavailable.

Exact XML counts, scopes, source identities, preserved-failure descriptions and supporting receipt paths are in [the JSON validation](efficiency-validation.json).

## Confirmation contract and new benchmark validation

The initial native study retained 60 strict failures despite all external tests passing: agents changed protected existing test files while adding regressions. [The issue record](workflow-contract-issue.md) preserves those outcomes and costs. The fresh confirmation corpus makes the unchanged byte-protection policy explicit and requires regressions in new files. Its tests reject appended existing tests even when behavior passes, accept legitimate new files, and check all ten baseline failures, reference fixes and eight half-fix negative controls.

Before native confirmation, two oracle tests failed because one JavaScript hidden file contained a TypeScript annotation; the annotation was removed, and the original failure evidence remains. The first runner protection fixture used the wrong Git repository form; it was corrected to an actual worktree, preserving the initial failure. Final 41 corpus and 35 runner cases pass. Combined mypy now passes 60 application/benchmark modules and Ruff format checks 120 files. These checks do not change the original native-study outcomes.
