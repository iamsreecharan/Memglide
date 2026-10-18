# Compact source-prefix component comparison

Local preparation component only; complete source bytes, native forwarded prompt prefix bytes and already imported API time. No Codex/model calls, measured model tokens, actual cache hits, billing or end-to-end speed claims.

| Case | Format | Added bytes | Shared prefix bytes across changed tasks | Median local API ms |
| --- | --- | ---: | ---: | ---: |
| single | legacy | 603 | 0 | 3.839 |
| single | compact-prefix | 362 | 362 | 3.790 |
| two_sources | legacy | 878 | 0 | 4.400 |
| two_sources | compact-prefix | 533 | 533 | 4.514 |

Common-prefix bytes concern the forwarded task only. Codex adds native instructions/history and controls session affinity. These byte measurements do not establish provider cache reuse or a live uncached-token reduction. Source ordering is canonical only in compact-prefix format. No stale source, missing code, cache-threshold padding or model classifier is introduced.
