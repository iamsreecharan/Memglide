# Ordinary-task candidate validation

**817 distinct automated cases passed**: 790 Python, 24 frontend and 3 production Chromium cases. All final cases passed; none were skipped, failed or errored. Exact per-file counts and SHA-256 case identities are in [JSON](daily-validation.json); raw parameter names are not duplicated here; public raw JUnit evidence retains literal synthetic fixtures verified against the frozen security tests.

## Final verification

The final whole Python suite reported 271.066 seconds. The frontend suite reported 14.385 seconds; production browser execution reported 51.923 seconds. These are suite-reported durations, not invented whole-command timings.

Ruff checks, Ruff formatting and mypy passed. The frontend build succeeded, and every bundled asset matched the fresh build byte-for-byte. The final wheel/sdist audit passed with no forbidden state or symlink entries. Clean installed-wheel API/CLI/source-freshness/loopback production asset checks passed. Installed preload verification observed one trusted fake native exec with the expected exit status and private stdin metadata; it made no model or network requests.

The installed preload receipt contains 12 functional assertions. They are not counted as additional pytest cases. Earlier full Python validation (757 cases) and focused reruns overlap the final suite and are not added.

## Per-file Python and frontend counts

| File | Cases | Passed | Failed/error/skipped |
| --- | ---: | ---: | ---: |
| tests/test_agent_codex_registration.py | 2 | 2 | 0 |
| tests/test_agent_context.py | 16 | 16 | 0 |
| tests/test_agent_mcp.py | 4 | 4 | 0 |
| tests/test_benchmark_comparison.py | 14 | 14 | 0 |
| tests/test_benchmark_corpus.py | 30 | 30 | 0 |
| tests/test_benchmark_corpus_daily.py | 53 | 53 | 0 |
| tests/test_benchmark_corpus_v2.py | 82 | 82 | 0 |
| tests/test_benchmark_daily_runner.py | 63 | 63 | 0 |
| tests/test_benchmark_probe.py | 6 | 6 | 0 |
| tests/test_benchmark_runner.py | 13 | 13 | 0 |
| tests/test_benchmark_runner_v2.py | 30 | 30 | 0 |
| tests/test_benchmark_telemetry.py | 20 | 20 | 0 |
| tests/test_codex_preload.py | 17 | 17 | 0 |
| tests/test_compact_quality_evaluation.py | 6 | 6 | 0 |
| tests/test_context_audit_v2.py | 42 | 42 | 0 |
| tests/test_context_budgeting.py | 8 | 8 | 0 |
| tests/test_context_diagnostics.py | 2 | 2 | 0 |
| tests/test_context_efficiency_v2.py | 17 | 17 | 0 |
| tests/test_context_focus.py | 23 | 23 | 0 |
| tests/test_context_performance.py | 6 | 6 | 0 |
| tests/test_context_request_scope.py | 12 | 12 | 0 |
| tests/test_functional_lifecycle.py | 22 | 22 | 0 |
| tests/test_indexer_context_candidates.py | 6 | 6 | 0 |
| tests/test_indexing.py | 25 | 25 | 0 |
| tests/test_live_context_analysis.py | 13 | 13 | 0 |
| tests/test_mcp_import_isolation.py | 1 | 1 | 0 |
| tests/test_memory_acknowledgement.py | 1 | 1 | 0 |
| tests/test_memory_context.py | 20 | 20 | 0 |
| tests/test_memory_versions.py | 20 | 20 | 0 |
| tests/test_preload.py | 61 | 61 | 0 |
| tests/test_query_focus.py | 4 | 4 | 0 |
| tests/test_refinement_reporting.py | 10 | 10 | 0 |
| tests/test_refinement_retrieval.py | 26 | 26 | 0 |
| tests/test_retrieval_experiment.py | 9 | 9 | 0 |
| tests/test_retrieval_holdout.py | 4 | 4 | 0 |
| tests/test_search_relevance.py | 23 | 23 | 0 |
| tests/test_security_storage.py | 69 | 69 | 0 |
| tests/test_transports.py | 9 | 9 | 0 |
| tests/test_workflow.py | 1 | 1 | 0 |
| tests/api.test.ts | 2 | 2 | 0 |
| tests/ui.test.tsx | 4 | 4 | 0 |
| tests/workflows.test.tsx | 18 | 18 | 0 |

## Retained failures and fixes

The initial unsupported `uv build --locked` command exited **2**. Its log and receipt remain preserved; a supported corrected build succeeded, followed by a final rebuild after benchmark-only integrity changes. Frontend/build/browser whole-command durations were not recorded and remain null with an explicit reason.

Independent review found that corrupt stored policy/root data and a huge JSON integer could escape the intended fallback; the final implementation validates these values and bounds SQLite work. The original exception reproductions and the independent successful fallback receipt are preserved.

Review also demonstrated a false pass when a production module exited zero before tests ran. The grader now requires actual test execution, expected counts and no skipped/error/failing outcomes; separate negative regression cases exercise both languages. Runner integrity checks added after the initial suite are included in the final whole-suite receipt. These are pre-formal development findings, not hidden or discarded live benchmark failures.

## Source and privacy scope

The current source identity covers 24 runtime Python files and 19 compiled assets. Per-file SHA-256 and aggregate algorithms are in JSON. Package audit confirms archive/source equality at its build boundary; later report/evidence additions are not retroactively claimed to exist in an earlier archive.

The raw Playwright report includes confidential configuration/environment, so it remains private. An allowlisted browser receipt preserves all test titles, statuses, durations, retries, counts and diagnostic-presence counts. Arbitrary diagnostic bodies and configuration are omitted for confidentiality, not to conceal failed outcomes. Original raw SHA-256 and byte length remain in provenance.

These checks establish application and tooling mechanics. They do not establish token savings, paid model behavior or actual cost per success. The native A/B comparison has a separate report; no benchmark outcome is invented here.
