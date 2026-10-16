# Exact document-frequency performance check

Local synthetic search measurements. No coding tasks, token usage or cost measured.

20,000 files, 78 MB, shared caches, two repeats with reversed policy order. Both policies use the same 32-term BM25 shortlist. The retained prior implementation reads the unindexed project_id payload for each matching posting; the optimized implementation uses equivalent vocabulary counts or project-scoped row IDs.

| Query | Prior mean / median seconds | Optimized mean / median seconds |
|---|---:|---:|
| short_common | 3.8486 / 3.8486 | 1.1846 / 1.1846 |
| long_absent | 2.3018 / 2.3018 | 2.2417 / 2.2417 |
| long_common | 67.7045 / 67.7045 | 4.0437 / 4.0437 |

All six paired candidate lists (paths, symbols, scores, reasons and source hashes) identical: True. Source unchanged during measurement: True.

Individual runs, CPU measurements, source hashes and fixture digest are retained in [JSON](search-frequency-performance.json). Two repeats do not establish a stable production latency distribution. Earlier all-terms-versus-shortlist slow observations are retained separately; these results must not replace them.
