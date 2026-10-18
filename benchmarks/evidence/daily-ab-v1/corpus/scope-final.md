# Known-file utility-edit microbenchmark

This is a focused microbenchmark of known-file utility edits, not a representative production-repository evaluation. No model requests were used to create or revise the tasks.

- 20 fresh tasks: 10 Python, 10 TypeScript; four repositories with five tasks each.
- Eight single-source tasks, eight two-source integration tasks, four supplied-source tasks.
- Each relevant path is explicitly supplied in the identical common prompt. Four prompts also contain the complete relevant source.
- External behavioral assertions run outside the agent worktree. Existing smoke files, README, AGENTS, ignore/config files are fingerprinted; TypeScript source is strictly typechecked.
- Twenty baseline versions fail the held-out behavior; twenty references pass all seven test methods plus applicable typechecks. Sixteen half-fix controls require both domain and adapter fixes.

Scope source sizes are 148–1372 bytes (mean 466.1, median 340.5). Four integration cases contain real typed application records and batch callers, tested for immutable inputs and preserved data contracts.

## Limits

- Four purpose-built small repositories, not representative production repositories.
- Every relevant production path is already explicitly disclosed to both configurations.
- Complete relevant source is included in the four supplied-context task prompts.
- Four nonsupplied integration tasks include typed application records and real public batch callers; this adds actual contract/caller complexity, not production repository scale.
- One independent utility bug or pair of coupled utility/adapter bugs per task.
- Does not evaluate unfamiliar large-repository discovery, longitudinal decisions, or cross-session memory.
- Reference fixes and grading assertions are procedurally separated, not cryptographically hidden from a host-capable agent.

## Individual source scope sizes

| Task | Kind | Source bytes |
|---|---|---:|
| py-daily-desk-elapsed-clock | single-source | 343 |
| py-daily-desk-rectangular-transpose | single-source | 160 |
| py-daily-desk-calendar-month-shift | integration | 1268 |
| py-daily-desk-export-line-endings | integration | 569 |
| py-daily-desk-label-ellipsis | supplied-context | 338 |
| py-daily-catalog-relative-indentation | single-source | 148 |
| py-daily-catalog-single-pass-partition | single-source | 211 |
| py-daily-catalog-tag-normalization | integration | 1372 |
| py-daily-catalog-strict-column-projection | integration | 397 |
| py-daily-catalog-saturday-weekend | supplied-context | 243 |
| ts-daily-editor-crlf-line-position | single-source | 378 |
| ts-daily-editor-html-text-escaping | single-source | 197 |
| ts-daily-editor-literal-replace-all | integration | 992 |
| ts-daily-editor-whitespace-word-spans | integration | 494 |
| ts-daily-editor-inclusive-clamp | supplied-context | 253 |
| ts-daily-inventory-numeric-median | single-source | 252 |
| ts-daily-inventory-chunk-without-empty-tail | single-source | 314 |
| ts-daily-inventory-signed-code-padding | integration | 397 |
| ts-daily-inventory-equal-length-zip | integration | 776 |
| ts-daily-inventory-zero-count-plural | supplied-context | 220 |

## Preserved drafting evidence

The initial draft and complete initial validation remain under `.local/daily-v1/corpus-initial-draft` and `corpus-validation-1`. Independent review added four genuine application call chains and fixed the median gold implementation for subnormal floats. The revised corpus passed a separate complete validation at `corpus-validation-2`. No task was selected or rewritten based on an A/B outcome.

Final validation: **46 pytest checks passed in43.61seconds**, Ruff passed. Both preserved CLI validation stages checked20 baseline/reference pairs and16 half-fix negative controls. These are corpus/tooling checks, not live Codex results.

A subsequent independent grading-integrity review reproduced two early-exit false passes in the original grader. Both identical exploit worktrees are now rejected. Seven new real-subprocess regressions passed in4.61seconds, including skipped/todo/expected-failure rejection and acceptance of additional passing regressions. Task prompts, fixture source and solutions remain unchanged. The root agent is coordinating the complete updated53-check rerun. Before/after evidence is preserved in `.local/daily-v1/review`.
