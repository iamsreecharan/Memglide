# Data dictionary

Each CSV row is one scheduled native session. `configuration` is `A` (installed
launcher with Memglide off) or `M` (commands-first Memglide candidate). `repeat`
is 1 or 2; `order` and `run_id` preserve the original schedule. `primary=True`
marks the fixed 112-session cohort. `measurement_epoch` labels the collection
epoch without rewriting earlier measurements. Repository URLs and task IDs are
public; the catalog also supplies the original upstream commit for all 36 tasks.

CSV Boolean values are `True` and `False`. A blank is unknown/not available;
it must never be interpreted as zero or a failed test. Integer token counts are
native reported counts. Seconds and USD equivalents retain round-trip numeric
precision from the frozen JSON.

The CLI may decode an upstream-omitted cache-write count as zero. A reported zero
does not prove that the provider supplied zero; the fixed primary tariff does
not make a separate cache-write inference.

| Fields | Meaning |
|---|---|
| `strict_success` | Frozen strict conjunction of public checks and private feature rubric, subject to integrity. |
| `public_success`, `private_success` | Recorded outcomes; this export invents no unexecuted check result. |
| `grade_valid`, `grade_infrastructure_valid` | The deferred grade and its execution/provenance passed the frozen validity rules. |
| `native_valid`, `native_identity_valid`, `native_transport_valid` | Effective version-pinned native completion and independent identity validity. These do not assert coding correctness. |
| `usage_complete` | Complete supported native-reported counters under the source-certified interpretation; no invoice-completeness claim. |
| `evidence_preservation_valid`, `source_policy_valid`, `source_protection_valid` | Complete bounded capture and effective baseline source/protection adjudication. |
| `source_unchanged` | Native source was unchanged by external grading. It does not mean the model left the original source unchanged. |
| `grading_source_reconstructed`, `reconstructed_source_unchanged`, `reconstructed_source_matches_native` | Genuine cache-free grading reconstruction retained the exact attested final source map. |
| `model_generated_caches_reused` | Whether grading reused model cache bytes; false throughout this panel. |
| `uniform_long_usd` | Effective completed-turn token counts priced under the fixed uniform tariff in the README. |
| `original_native_valid`, `original_uniform_long_usd` | Original parser verdict/cost, preserved separately. A blank original cost remains unknown even when the certified effective cost is available. |
| `workflow_wall_seconds`, `native_wall_seconds` | Main measured workflow and nested native component, with boundaries defined in the README. |
| `index_wall_seconds`, `verification_wall_seconds`, `cleanup_wall_seconds` | Memglide setup-worker components. Cleanup here concerns setup cleanup; it is not the complete final process-cleanup duration. |
| `installed_launcher_preparation_wall_seconds` | Installed launcher start through actual native bridge boundary; part of the workflow, not an additional disjoint total. |
| `input_tokens`, `cached_input_tokens`, `output_tokens` | Total reported input, cached-read subset and output. Cached input must not be added to total input. |
| `cache_write_input_tokens`, `reasoning_output_tokens` | Reported cache-write subset of input and reasoning subset of output. These are not extra independent tokens. |
| `reported_public_behavioral_tests` | Public grader's reported behavioral count; framework units can differ, including whole-file legacy checks. |
| `reported_private_contract_checks` | Reported private contract-check slots, not a universal count of independent assertions. |
| `recovered_transport_warning_count` | Number of retained retry notifications accepted only with the pinned successful terminal lifecycle. |
| `original_protection_violation_count` | Original protection flags, before the baseline-only production-file correction. |
| `authorized_production_correction_count` | Exact source-policy certificates applied; no task was removed. |
| `coding_policy_violation_count` | Owned regular protected-source edit violations; such a violation is a coding failure, not automatic infrastructure invalidity. |
| `*_sha256` | Content commitments to original raw records, native/source adjudications, policy and grading deployment. They are identifiers, not paths. |

The paired table contains `cost_A`, `cost_M`, `workflow_A`, `workflow_M`, and
their M-minus-A `*_delta` values. Each arm value is the mean of its two session
repetitions. `A_both_pass` and `M_both_pass` mean both strict repetitions passed;
the task-level quality matrix uses these indicators.

## Public task command placeholders

The command arrays/environment updates preserve the frozen declaration and
replace machine selectors with these labels:

| Placeholder | Meaning |
|---|---|
| `{root}` | Supplied task checkout. |
| `{python}`, `{node}` | Pinned runtime interpreter. |
| `{runtime_v5}` | Shared pinned evaluation interpreters/tooling. |
| `{runtime_v6}` | Shared public runtime extensions and tooling. |
| `{runtime_cohort_a}`, `{runtime_cohort_b}`, `{runtime_cohort_c}` | Public task-cohort dependency and adapter roots. |
| `{repository_root}` | Product/source checkout root for any remaining declared public tool. |

`/dev/null`, where present, is the standard Unix null device used by the original
test command. It is not an executor-root selector. Toolchain dependencies and
public fixtures are not embedded in this compact statistical pack.
