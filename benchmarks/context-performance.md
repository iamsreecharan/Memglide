# Context request performance refinement

The isolated context/database optimization reduced mean request time in all three measured cases while preserving the complete response in all 9 pairs. This is a small local component result, not evidence of Codex token or monetary savings.

The measured changes load settings once per request with defensive copies and automatic scope reset; calculate the exact existing JSON planning estimate with one full serialization; and avoid full-response serialization for graph trials rejected by the graph allowance. All secure source reads remain.

## Paired results

| Case | Before mean/median/p95(s) | After mean/median/p95(s) | Mean CPU before→after(s) | Exact output pairs |
| --- | --- | --- | --- | --- |
| natural | 0.4397/0.3386/0.6521 | 0.3423/0.3584/0.4432 | 0.4005→0.3025 |3/3|
| small_budget | 0.5143/0.5477/0.6676 | 0.4158/0.4149/0.5641 | 0.4691→0.3634 |3/3|
| full_source | 0.6136/0.5233/0.9562 | 0.3951/0.3348/0.5605 | 0.5704→0.3479 |3/3|

All18requests succeeded; no observed wall/CPU pair regressions were discarded. Three observations per case make p95 the observed maximum, not a reliable tail-latency estimate.

| Diagnostic natural request | Before | After |
| --- | ---: | ---: |
| Actual settings SELECT calls |75|1|
| Database rows() calls |191|117|
| Secure read_source calls |86|86|
| Full-response estimate refresh calls |148|22|
| Passport builds |15|15|

Counts come from separate untimed query instrumentation/profiles. Function calls are not filesystem I/O counts. The settings() function itself is still called 76 times after the change;75 read the request snapshot rather than querying SQLite.

## Individual observations

| Case | Repeat | Before wall/CPU(s) | After wall/CPU(s) | Planning estimate before/after | Equal response |
| --- | ---: | --- | --- | --- | --- |
| natural | 1 | 0.652112/0.601840 | 0.358398/0.315464 | 7197/7197 | True |
| small_budget | 1 | 0.547666/0.509271 | 0.414881/0.361131 | 1792/1792 | True |
| full_source | 1 | 0.523255/0.482104 | 0.334799/0.297496 | 7406/7406 | True |
| full_source | 2 | 0.956211/0.899205 | 0.560474/0.507351 | 7406/7406 | True |
| small_budget | 2 | 0.667605/0.617749 | 0.564137/0.511482 | 1792/1792 | True |
| natural | 2 | 0.338565/0.305001 | 0.443161/0.403957 | 7197/7197 | True |
| natural | 3 | 0.328339/0.294525 | 0.225380/0.188142 | 7197/7197 | True |
| small_budget | 3 | 0.327713/0.280396 | 0.268452/0.217736 | 1792/1792 | True |
| full_source | 3 | 0.361269/0.329878 | 0.290057/0.238861 | 7406/7406 | True |

## Protocol and evidence

Baseline:`b51a26234656c647f12da3ad63d8bc1fe9380c58`. Both arms use frozen baseline indexer/memory modules, the same immutable TypeScript fixture, identical prompts/levels/budgets and a fresh SQLite clone/session per arm. Each arm reuses its session for 9 requests. Arm order reverses on repeat 2; case order reverses on repeat 2. The first natural query is the first context retrieval; later requests share a warm process. No OS caches were flushed and no MCP/server startup is measured.

Only the actual 32-character session/retrieval IDs are normalized, including embedded `expand_context` references. All 9 pairs otherwise have equal complete JSON, including source/hash/ranking, graph, omission warnings and estimated budgets.

[JSON report](context-performance.json) contains all 18 observations, means/medians/p95, pair checks, source/fixture hashes, diagnostics and limitations. Full raw results are retained in [before](evidence/context-performance-before.json) and [after](evidence/context-performance-after.json). The exact executed [measurement harness](evidence/context-performance-measured-harness.txt) is preserved separately from the cleaned standalone reproduction harness.

Reproduce in an otherwise idle workspace:

```bash
UV_CACHE_DIR="$PWD/.cache/uv" uv run python -m benchmarks.context_performance \
  --baseline b51a26234656c647f12da3ad63d8bc1fe9380c58 \
  --output .local/context-performance-reproduction --repeats 3
```

The standalone reproduction harness was smoke-tested with one repeat and all 3 pairs matched. Those validation timings are excluded from the performance result above. Its baseline is trusted local repository code imported by the harness; indexed fixture code is never executed.

## Validation and limits

41 focused request/budget/memory tests passed; 6 pair-integrity tests passed; Ruff and focused mypy passed. Tests cover concurrent source edits, next-request size-policy/settings visibility, nested/thread/database settings isolation, mutation-resistant snapshots, exception cleanup and exact UTF-8 estimates across digit boundaries. An initial test import setup error is retained in the raw log and was corrected.

This result covers one small synthetic repository. It does not establish broad latency, production usefulness or savings; full current SDK timing and unseen-repository retrieval results must be assessed separately. Baseline artifacts from earlier experiments remain unchanged.

## Historical measurement stage

These timings predate the final focused primary-file selector and ranking refinements. Exact measured candidate source is retained in [context.py snapshot](evidence/context-performance-measured-context.txt) and [database.py snapshot](evidence/context-performance-measured-database.txt); their SHA-256 digests match the raw after report. Running the standalone harness against the final checkout can legitimately return different evidence and report failed equivalence. Reproducing this historical stage requires the measured source snapshots. No timings or previously recorded source hashes were changed.
