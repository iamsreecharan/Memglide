# Versioned daily read-command diagnostics

Offline lexical correction of original 80-run read-command proxies; no new coding/model runs.

The preserved primary report recorded **47 A / 33 B** recognized read-command items. This offline diagnostic reproduces those original values with the frozen parser, then applies the newline correction to the same raw events. Actual filesystem read counts remain unavailable.

| Metric | A original | A corrected | B original | B corrected |
|---|---:|---:|---:|---:|
| observed_file_read_commands | 47 | 47 | 33 | 33 |
| observed_repeated_read_commands | 0 | 0 | 0 | 0 |
| recognized_path_mentions | 118 | 118 | 78 | 69 |
| declared_focus_path_mentions | 48 | 48 | 3 | 0 |
| test_path_mentions | 33 | 33 | 33 | 33 |
| other_path_mentions | 37 | 37 | 42 | 36 |

Unquoted newlines previously disappeared during shell tokenization. For example, `cat tests/test_module.py` followed by `git diff -- src/module.py` on the next line could make `git`, `diff` and the changed source path look like additional `cat` operands. The corrected parser keeps those commands separate.

## Individual original runs

| Run | Read-command items old/new | Path mentions old/new | Declared-focus mentions old/new | Changed commands |
|---|---:|---:|---:|---:|
| py-daily-catalog-relative-indentation-r1-A | 2/2 | 3/3 | 1/1 | 0 |
| py-daily-catalog-relative-indentation-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-inventory-chunk-without-empty-tail-r1-A | 1/1 | 4/4 | 1/1 | 0 |
| ts-daily-inventory-chunk-without-empty-tail-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| py-daily-catalog-strict-column-projection-r1-A | 1/1 | 4/4 | 2/2 | 0 |
| py-daily-catalog-strict-column-projection-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-editor-html-text-escaping-r1-B | 1/1 | 3/3 | 0/0 | 0 |
| ts-daily-editor-html-text-escaping-r1-A | 1/1 | 3/3 | 1/1 | 0 |
| py-daily-catalog-tag-normalization-r1-A | 1/1 | 4/4 | 2/2 | 0 |
| py-daily-catalog-tag-normalization-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-inventory-zero-count-plural-r1-A | 0/0 | 0/0 | 0/0 | 0 |
| ts-daily-inventory-zero-count-plural-r1-B | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-rectangular-transpose-r1-A | 2/2 | 3/3 | 1/1 | 0 |
| py-daily-desk-rectangular-transpose-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-editor-literal-replace-all-r1-A | 3/3 | 4/4 | 2/2 | 0 |
| ts-daily-editor-literal-replace-all-r1-B | 1/1 | 5/3 | 0/0 | 1 |
| ts-daily-inventory-signed-code-padding-r1-A | 1/1 | 5/5 | 2/2 | 0 |
| ts-daily-inventory-signed-code-padding-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-inventory-equal-length-zip-r1-A | 1/1 | 4/4 | 2/2 | 0 |
| ts-daily-inventory-equal-length-zip-r1-B | 1/1 | 3/3 | 0/0 | 0 |
| py-daily-desk-label-ellipsis-r1-A | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-label-ellipsis-r1-B | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-catalog-saturday-weekend-r1-B | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-catalog-saturday-weekend-r1-A | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-elapsed-clock-r1-A | 2/2 | 3/3 | 1/1 | 0 |
| py-daily-desk-elapsed-clock-r1-B | 1/1 | 1/1 | 0/0 | 0 |
| ts-daily-inventory-numeric-median-r1-B | 1/1 | 3/3 | 0/0 | 0 |
| ts-daily-inventory-numeric-median-r1-A | 1/1 | 4/4 | 1/1 | 0 |
| ts-daily-editor-whitespace-word-spans-r1-A | 2/2 | 4/4 | 2/2 | 0 |
| ts-daily-editor-whitespace-word-spans-r1-B | 1/1 | 3/3 | 0/0 | 0 |
| py-daily-desk-export-line-endings-r1-A | 2/2 | 4/4 | 2/2 | 0 |
| py-daily-desk-export-line-endings-r1-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-editor-inclusive-clamp-r1-A | 1/1 | 1/1 | 0/0 | 0 |
| ts-daily-editor-inclusive-clamp-r1-B | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-calendar-month-shift-r1-B | 1/1 | 5/1 | 2/0 | 1 |
| py-daily-desk-calendar-month-shift-r1-A | 1/1 | 4/4 | 2/2 | 0 |
| ts-daily-editor-crlf-line-position-r1-A | 1/1 | 4/4 | 1/1 | 0 |
| ts-daily-editor-crlf-line-position-r1-B | 1/1 | 3/3 | 0/0 | 0 |
| py-daily-catalog-single-pass-partition-r1-B | 1/1 | 1/1 | 0/0 | 0 |
| py-daily-catalog-single-pass-partition-r1-A | 1/1 | 3/3 | 1/1 | 0 |
| py-daily-catalog-relative-indentation-r2-B | 1/1 | 2/2 | 0/0 | 0 |
| py-daily-catalog-relative-indentation-r2-A | 2/2 | 3/3 | 1/1 | 0 |
| ts-daily-inventory-chunk-without-empty-tail-r2-B | 1/1 | 1/1 | 0/0 | 0 |
| ts-daily-inventory-chunk-without-empty-tail-r2-A | 1/1 | 3/3 | 1/1 | 0 |
| py-daily-catalog-strict-column-projection-r2-B | 1/1 | 1/1 | 0/0 | 0 |
| py-daily-catalog-strict-column-projection-r2-A | 1/1 | 4/4 | 2/2 | 0 |
| ts-daily-editor-html-text-escaping-r2-A | 2/2 | 3/3 | 1/1 | 0 |
| ts-daily-editor-html-text-escaping-r2-B | 1/1 | 3/3 | 0/0 | 0 |
| py-daily-catalog-tag-normalization-r2-B | 1/1 | 2/2 | 0/0 | 0 |
| py-daily-catalog-tag-normalization-r2-A | 1/1 | 4/4 | 2/2 | 0 |
| ts-daily-inventory-zero-count-plural-r2-B | 1/1 | 4/1 | 1/0 | 1 |
| ts-daily-inventory-zero-count-plural-r2-A | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-rectangular-transpose-r2-B | 1/1 | 2/2 | 0/0 | 0 |
| py-daily-desk-rectangular-transpose-r2-A | 2/2 | 3/3 | 1/1 | 0 |
| ts-daily-editor-literal-replace-all-r2-B | 1/1 | 3/3 | 0/0 | 0 |
| ts-daily-editor-literal-replace-all-r2-A | 2/2 | 3/3 | 2/2 | 0 |
| ts-daily-inventory-signed-code-padding-r2-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-inventory-signed-code-padding-r2-A | 1/1 | 4/4 | 2/2 | 0 |
| ts-daily-inventory-equal-length-zip-r2-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-inventory-equal-length-zip-r2-A | 1/1 | 4/4 | 2/2 | 0 |
| py-daily-desk-label-ellipsis-r2-B | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-label-ellipsis-r2-A | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-catalog-saturday-weekend-r2-A | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-catalog-saturday-weekend-r2-B | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-elapsed-clock-r2-B | 1/1 | 1/1 | 0/0 | 0 |
| py-daily-desk-elapsed-clock-r2-A | 2/2 | 3/3 | 1/1 | 0 |
| ts-daily-inventory-numeric-median-r2-A | 1/1 | 4/4 | 1/1 | 0 |
| ts-daily-inventory-numeric-median-r2-B | 1/1 | 3/3 | 0/0 | 0 |
| ts-daily-editor-whitespace-word-spans-r2-B | 1/1 | 3/3 | 0/0 | 0 |
| ts-daily-editor-whitespace-word-spans-r2-A | 1/1 | 5/5 | 2/2 | 0 |
| py-daily-desk-export-line-endings-r2-B | 1/1 | 1/1 | 0/0 | 0 |
| py-daily-desk-export-line-endings-r2-A | 2/2 | 4/4 | 2/2 | 0 |
| ts-daily-editor-inclusive-clamp-r2-B | 0/0 | 0/0 | 0/0 | 0 |
| ts-daily-editor-inclusive-clamp-r2-A | 0/0 | 0/0 | 0/0 | 0 |
| py-daily-desk-calendar-month-shift-r2-A | 2/2 | 4/4 | 2/2 | 0 |
| py-daily-desk-calendar-month-shift-r2-B | 1/1 | 2/2 | 0/0 | 0 |
| ts-daily-editor-crlf-line-position-r2-B | 1/1 | 3/3 | 0/0 | 0 |
| ts-daily-editor-crlf-line-position-r2-A | 1/1 | 3/3 | 1/1 | 0 |
| py-daily-catalog-single-pass-partition-r2-A | 1/1 | 3/3 | 1/1 | 0 |
| py-daily-catalog-single-pass-partition-r2-B | 1/1 | 2/2 | 0/0 | 0 |

## Integrity and limits

Frozen parser source: `6f4b6f6be83a7ad58ffba5f6c2176a9cc5d36dff`; SHA-256 `21a6fa239c25ab1fb417aa7042f3f4e8412ef941172d1dfc42ec0d5895c6cc52`.

Corrected parser SHA-256: `4e7a19e8c37d1cb47c0306dac2e962648267de23aa5b361c2e8a29d5b258a936`.

All 84 input files were SHA-256 checked before and after; none changed. No commands from the event streams were executed.

- Original report/raw events/results are unchanged; this versioned diagnostic does not replace the primary experiment.
- Read-command counts are heuristic successful command_execution items containing recognized literal read commands. Path mentions are operands inferred from command text, not actual file opens, bytes read, unique files, or guaranteed I/O lower bounds.
- Unquoted newlines now separate shell commands. Quoted newlines remain argument data and are excluded as literal paths; unquoted/double-quoted backslash-newline is treated as a line continuation. Redirection, here-doc, pipe, OR and background operators remain conservative exclusions.
- Only standalone bash/sh/zsh -c/-lc wrappers are recursively unpacked. Mixed outer/wrapper commands are not flattened, preventing a subshell cd from changing the inferred outer directory.
- Declared-focus/test classifications use caller-visible focus paths and lexical path normalization only; no source or grading oracle selects or reads files during these diagnostics.
- Actual filesystem reads and actual repeated filesystem reads remain null. These proxy corrections do not change measured native token usage, execution timing, success, CPU, memory or cost conclusions.
