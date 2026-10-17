# Live Codex MCP context responses

Source experiment: `/workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1`.

- Declared target-file / exact-symbol / visible-declaration matches are narrow proxies; they do not establish complete method bodies or semantic retrieval completeness.
- Passport status and source_freshness are server assertions, not independently verified source versions at the instant of a live tool call.
- Server estimated_tokens values are planning estimates, not measured model tokens, invoiced usage, or money saved.
- Snippet bytes count returned item strings, including duplicates; canonical response JSON bytes do not measure transport encoding, model context size, or billed tokens.
- Missing/failed/unparsed tool results remain unavailable. A run with no context call is retained and does not receive invented zero-byte or freshness measurements.


The primary experiment retains all **96 planned runs**. All 48 A runs have no Memglide context by design. **47 of 48 B runs** returned context; the interrupted `ts-lru-eviction-r2-B` run has no context measurement. The separate supplemental retry is excluded.

There were **158 observed context-related calls**: 78 `get_context`, 76 `get_context_passport`, and four `expand_context`. Of these, 156 returned usable JSON results; two expansion calls failed because the model omitted the required `session_id`. These failures remain in the JSON with the native validation result. They occurred in `py-selective-retry-r1-B` and `py-lru-eviction-r2-B`.

All **47 measured B runs** retrieved their declared target file and exposed its expected declaration in at least one context response. Across the **80 valid context responses**, target-file coverage was 80/80 and declaration visibility was 78/80. The two responses without declarations were level 1 discovery responses with no source snippets. These are declared metadata proxies, not complete-body or semantic-completeness measurements.

Server assertions were **109 Partial / 47 Stale** for passport status, and **109 Current / 47 Stale** for source freshness. Counts are response observations, including repeated passport/retrieval observations. Independent freshness at each live call and complete method-body coverage remain unavailable.

| Per valid context response (80 observations) | Mean | Median | p95 (nearest rank) |
| --- | ---: | ---: | ---: |
| Returned files | 5.58 | 6.50 | 9 |
| Returned items | 6.30 | 7.00 | 10 |
| Snippet UTF-8 bytes | 3085.30 | 3528.00 | 4617 |
| Canonical response JSON bytes | 9581.65 | 11609.50 | 11999 |
| Server planning-token estimate; not billing | 3194.20 | 3870.00 | 4000 |

| Run | Arm | Context responses | Unavailable tool results | Target-file union | Declaration union |
| --- | --- | ---: | ---: | ---: | ---: |
| ts-selective-retry-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-selective-retry-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-lru-eviction-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| py-lru-eviction-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-selective-retry-r1-B | B | 2 | 1 | 1.0 | 1.0 |
| py-selective-retry-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-boolean-config-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-boolean-config-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-billing-rounding-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-billing-rounding-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-transitive-dependencies-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-transitive-dependencies-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-and-search-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-and-search-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-cursor-pagination-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-cursor-pagination-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-ttl-boundary-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-ttl-boundary-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-idempotent-events-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-idempotent-events-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-ttl-boundary-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-ttl-boundary-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-optimistic-revision-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-optimistic-revision-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-boolean-config-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-boolean-config-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-transitive-dependencies-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-transitive-dependencies-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-idempotent-events-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-idempotent-events-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-optimistic-revision-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-optimistic-revision-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| py-storage-containment-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-storage-containment-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-cursor-pagination-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-cursor-pagination-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-and-search-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-and-search-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-billing-rounding-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-billing-rounding-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-lru-eviction-r1-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-lru-eviction-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-scope-authorization-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-scope-authorization-r1-A | A | 0 | 0 | unavailable | unavailable |
| ts-storage-containment-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-storage-containment-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-scope-authorization-r1-A | A | 0 | 0 | unavailable | unavailable |
| py-scope-authorization-r1-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-selective-retry-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-selective-retry-r2-B | B | 1 | 0 | 1.0 | 1.0 |
| py-lru-eviction-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-lru-eviction-r2-B | B | 2 | 1 | 1.0 | 1.0 |
| py-selective-retry-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-selective-retry-r2-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-boolean-config-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-boolean-config-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-billing-rounding-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-billing-rounding-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-transitive-dependencies-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-transitive-dependencies-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-and-search-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-and-search-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-cursor-pagination-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-cursor-pagination-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-ttl-boundary-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-ttl-boundary-r2-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-idempotent-events-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-idempotent-events-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-ttl-boundary-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-ttl-boundary-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-optimistic-revision-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-optimistic-revision-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-boolean-config-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-boolean-config-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-transitive-dependencies-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-transitive-dependencies-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-idempotent-events-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-idempotent-events-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-optimistic-revision-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-optimistic-revision-r2-A | A | 0 | 0 | unavailable | unavailable |
| py-storage-containment-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-storage-containment-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-cursor-pagination-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-cursor-pagination-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-and-search-r2-B | B | 1 | 0 | 1.0 | 1.0 |
| py-and-search-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-billing-rounding-r2-B | B | 1 | 0 | 1.0 | 1.0 |
| ts-billing-rounding-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-lru-eviction-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-lru-eviction-r2-B | B | 0 | 0 | unavailable | unavailable |
| ts-scope-authorization-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-scope-authorization-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| ts-storage-containment-r2-A | A | 0 | 0 | unavailable | unavailable |
| ts-storage-containment-r2-B | B | 2 | 0 | 1.0 | 1.0 |
| py-scope-authorization-r2-B | B | 1 | 0 | 1.0 | 1.0 |
| py-scope-authorization-r2-A | A | 0 | 0 | unavailable | unavailable |

Full per-call arguments, response sizes, passport assertions, and failures are in the companion JSON.
