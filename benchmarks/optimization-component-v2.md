# Context efficiency refinement: component measurements

The final development-fixture measurement reduced mean Python CPU and wall time in all three cases. Natural-query median wall time increased slightly; this is not a universal latency improvement. The source-superset fix intentionally changed 10/15 responses, and all 30 final requests succeeded. Actual model tokens, costs and Codex task benefits are not measured here.

The changes avoid repeated source snippets during candidate ranking, use bounded request-only verified snapshots, securely verify retained sources again, and allow a complete parent body to replace contained smaller spans only when the complete response fits its budget. Public source tools retain their secure-read behavior.

## Final coordinated measurement

| Case | Before mean / median wall (s) | After mean / median wall (s) | Mean wall change | Mean Python CPU before → after (s) | UTF-8 response bytes before → after |
| --- | ---: | ---: | ---: | ---: | ---: |
| natural | 0.2568 / 0.1891 | 0.2240 / 0.1922 | -12.8% | 0.2168 → 0.1600 | 16943 → 17225 |
| small_budget | 0.2553 / 0.2194 | 0.1762 / 0.1574 | -31.0% | 0.2010 → 0.1338 | 5049 → 5331 |
| full_source | 0.2679 / 0.2780 | 0.2185 / 0.2617 | -18.4% | 0.2259 → 0.1753 | 22216 → 22216 |

Five repeats per case. 15/15 pairs were comparable; 5/15 retained the entire same JSON after normalizing only actual session/retrieval IDs. Natural and small-budget selection changed intentionally; full-source responses stayed identical. A larger parent body supplies additional imports/source, so response bytes increase in those two cases.

A separate natural-query profile counted **84 → 33 secure `read_source` invocations** and **102 → 82 database `rows` invocations**. Function counts are not filesystem I/O measurements or model calls. Source checks moved from unreturned candidate excerpts to selected-source verification; the final source recheck detects edits, same-size restored-mtime changes, deletion and symlink swaps.

The root and quality agents coordinated a pause in local CPU work for this final pass. The shared cloud host and OS caches remain uncontrolled. Case/arm order is counterbalanced; SQLite starts from matched clones, while each arm reuses a session across requests. Local Python CPU excludes Git child processes. Five observations make nearest-rank p95 the observed maximum, not a reliable tail estimate.

## Every development stage is retained

| Stage | Observations | Equivalent pairs | Natural mean wall before → after (s) | Conditions |
| --- | ---: | ---: | ---: | --- |
| unchanged-control | 6 | 3/3 | 0.2112 → 0.2136 | Unchanged code control; exploratory shared host; one repeat. |
| snapshot-only | 18 | 9/9 | 0.1999 → 0.2104 | Request-only snapshots plus final source validation; shared host; three repeats; no metadata path yet. |
| metadata-pilot | 6 | 3/3 | 0.5785 → 0.3581 | Metadata-only internal candidate path; exploratory one-repeat pilot. |
| metadata-test-overlap | 18 | 9/9 | 0.3198 → 0.2259 | Metadata-only path; three repeats overlapped a local regression-test process. Confounded exploratory timing. |
| metadata-browser-overlap | 30 | 15/15 | 0.1638 → 0.1371 | Metadata-only path; five repeats. Despite the private directory name, production Chromium was running; this is NOT a quiet measurement. |
| final-coordinated | 30 | 5/15 | 0.2568 → 0.2240 | Metadata-only path plus transactional source-superset selection; five repeats. Root and quality agents coordinated a pause in local CPU work; cloud-host background variation and caches remain uncontrolled. |

The first snapshot-only stage had mixed timings and established no broad speed improvement. The metadata-only stages retained exact output in all pairs, with test/browser overlap explicitly disclosed. An initial diagnostic-harness import failed before producing observations; its error and fix are recorded in JSON. No measurement was discarded or selected as a replacement for an unfavorable result.

## Validation and reproduction

114 focused context/indexer/retrieval tests passed after the selector fix; the earlier 248-test batch included security/storage. New tests cover complete parent replacement, several contained spans, insufficient-budget rollback, nested/equal/partial overlap, and mutations during packing. Both source modules pass mypy; owned source/tests/harness pass Ruff. The complete suite is reported separately by the main verification.

The [independent old-24 development quality study](compact-quality-v2.md) measures primary/helper/caller body coverage. It is separate from this timing study and from the held-out live Codex A/B.

```bash
UV_CACHE_DIR="$PWD/.cache/uv" uv run python -m benchmarks.context_efficiency_v2 \
  --baseline e6e10a8f588c9236c7303a83780219d027a1c702 \
  --output .local/context-efficiency-v2-reproduction --repeats 5 --allow-response-changes
```

The baseline commit is trusted local application code imported by the harness; indexed fixture code is never executed. Both source arms are frozen before timing. Existing output directories are refused. Intentional response changes remain recorded; failed/missing requests cannot validate the comparison.

[Detailed JSON, individual-run evidence links and SHA-256 manifest](optimization-component-v2.json). Raw before/after JSON, profiler output, exact executed harnesses and matching source snapshots are retained under [component evidence](evidence/context-efficiency-v2).

Actual model usage, billed cost, cost per successful coding task, model/MCP calls, exact filesystem reads and RSS are unavailable in this component study; they are not inferred from planning estimates or payload size.
