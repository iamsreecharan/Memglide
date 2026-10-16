# Additional development-only BM25 score check

After the initial five-strategy experiment, a second check compared the current
IDF lexical score with a simpler bounded BM25 contribution. All 48 query/policy
observations are retained in [JSON](retrieval-calibration.json).

Only the unchanged 24 Atlas development prompts were used. Both policies used
the same current index/context code, fixture source, level 2 and budget 8000.
The rule was recorded before measurement: retain source coverage, then compare
target-file first-result accuracy and reciprocal rank; ties keep the current
implementation. The earlier Orion holdout was not used in this calibration.

| Policy | Context target-file coverage | Primary source visible | Target file first | Mean reciprocal rank |
| --- | ---: | ---: | ---: | ---: |
| Current IDF lexical | 24/24 | 24/24 | 6/24 | 0.459722 |
| Bounded BM25 contribution | 24/24 | 24/24 | 5/24 | 0.465278 |

The bounded contribution was **rejected** because first-result accuracy fell.
Production retains the IDF lexical policy used in the initial locked experiment.
No tuning was applied after inspecting its holdout results.

The frozen legacy ranker remains stronger on the development first-result
metric: 8/24, versus 6/24 for IDF lexical. On the initial independent holdout,
legacy scored 22/24 and IDF lexical 24/24. This is a tradeoff, not a universal
ranking improvement. The new source-first context packer returned all declared
target files for all five policies; the full original-versus-improved MCP probes
separately evaluate that implementation change. Neither experiment measures
model tokens, billed cost or successful coding tasks.
