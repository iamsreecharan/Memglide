# Independent MCP component before/after comparison

These real SDK probes are **not live Codex A/B runs**. They establish no token savings, monetary savings, coding success rate, cost per completed task, or semantic context completeness. Those measurements remain unavailable.

Comparison validity: **True**. Observed 24 baseline and 24 candidate tasks; 24 comparable pairs and 0 invalid pairs. Invalid or unavailable pairs have no computed deltas. Both complete input reports, including their original summaries and failures, are embedded in the JSON.

Source provenance:

- baseline: unavailable; git HEAD `unavailable`; source digest `unavailable`.
- candidate: captured_source_state_before_probe; git HEAD `39e8df30565783a686270f8a6f422e56e41e3776`; source digest `26371ec4dd5eca2baee7d3bd2bf470ae32306ee0a85294f5c6fe537f139ce43d`.
- Limitation: baseline source version was not recorded; source attribution is limited.

Protocol and interpretation:

- Exact task ID, language, immutable fixture commit, expected declarations, session prompt and actual retrieval query/level/budget sequence.
- Declared target-file and declaration visibility proxies; not semantic completeness or coding success.
- Single sequential observations, not randomized repeated performance trials. Sampled CPU is an observed lower bound; sampled RSS may double-count shared pages. Every numerical increase in time/CPU/RSS is listed as an observed regression, without claiming statistical significance..
- Source capture and historical reconstruction are distinguished; unknown versions remain unknown.
- Fresh databases per probe; provider cache is irrelevant because no model is invoked. Host filesystem caches are uncontrolled..
- Configured estimated-token budget; not measured or billed model tokens.

All observed values are summarized below; paired deltas use only matching tasks and available measurements. A negative delta favors the candidate for runtime and resources; a positive delta favors the candidate for coverage and freshness. Counts and missing measurements are explicit.

| Metric | Baseline n/missing | Mean | Median | Candidate n/missing | Mean | Median | Paired delta n/missing | Mean delta | Median delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| target_file_coverage | 24/0 | 0.666667 | 1 | 24/0 | 1 | 1 | 24/0 | 0.333333 | 0 |
| expected_symbol_coverage | 24/0 | 0.333333 | 0 | 24/0 | 0.166667 | 0 | 24/0 | -0.166667 | 0 |
| declaration_visible_coverage | 24/0 | 0.625 | 1 | 24/0 | 1 | 1 | 24/0 | 0.375 | 0 |
| natural_hashes_current | 24/0 | 1 | 1 | 24/0 | 1 | 1 | 24/0 | 0 | 0 |
| old_passport_detected_edit | 24/0 | 1 | 1 | 24/0 | 1 | 1 | 24/0 | 0 | 0 |
| updated_target_sha_matches | 24/0 | 1 | 1 | 24/0 | 1 | 1 | 24/0 | 0 | 0 |
| updated_edit_marker_visible | 24/0 | 1 | 1 | 24/0 | 1 | 1 | 24/0 | 0 | 0 |
| updated_evidence_hashes_current | 24/0 | 1 | 1 | 24/0 | 1 | 1 | 24/0 | 0 | 0 |
| index_wall_seconds | 24/0 | 0.275028 | 0.245041 | 24/0 | 0.521893 | 0.303145 | 24/0 | 0.246865 | 0.050814 |
| index_client_cpu_seconds | 24/0 | 0.082913 | 0.0731273 | 24/0 | 0.160558 | 0.0896806 | 24/0 | 0.0776449 | 0.0185464 |
| mcp_transport_wall_seconds | 24/0 | 5.12113 | 5.04976 | 24/0 | 10.0638 | 7.28371 | 24/0 | 4.94267 | 2.62873 |
| natural_retrieval_wall_seconds | 24/0 | 0.77348 | 0.732025 | 24/0 | 1.33691 | 0.861803 | 24/0 | 0.56343 | 0.184074 |
| server_sampled_cpu_seconds | 24/0 | 4.80458 | 4.755 | 24/0 | 9.48083 | 6.655 | 24/0 | 4.67625 | 2.275 |
| server_sampled_peak_rss_bytes | 24/0 | 81954816 | 8.09021e+07 | 24/0 | 8.1161e+07 | 8.00113e+07 | 24/0 | -793771 | -581632 |

Every task and any retained failure:

| Task | Comparable | Baseline / candidate status | File coverage before / after | Declaration visible before / after | Natural hashes before / after | Regression metrics |
|---|---|---|---|---|---|---|
| py-and-search | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_client_cpu_seconds |
| py-billing-rounding | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-boolean-config | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-cursor-pagination | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-idempotent-events | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | none observed |
| py-lru-eviction | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-optimistic-revision | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-scope-authorization | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-selective-retry | True | passed / passed | 1 / 1 | 0 / 1 | 1 / 1 | none observed |
| py-storage-containment | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds |
| py-transitive-dependencies | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-ttl-boundary | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-and-search | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| ts-billing-rounding | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-boolean-config | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| ts-cursor-pagination | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-idempotent-events | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| ts-lru-eviction | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage |
| ts-optimistic-revision | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| ts-scope-authorization | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-selective-retry | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-storage-containment | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, server_sampled_cpu_seconds |
| ts-transitive-dependencies | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-ttl-boundary | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_client_cpu_seconds, server_sampled_peak_rss_bytes |

All 95 observed regressions (including every runtime/resource increase):

| Task | Metric | Baseline | Candidate | Candidate minus baseline |
|---|---|---:|---:|---:|
| py-and-search | expected_symbol_coverage | 1 | 0 | -1 |
| py-and-search | index_client_cpu_seconds | 0.0851665 | 0.0935248 | 0.00835828 |
| py-billing-rounding | index_client_cpu_seconds | 0.0704919 | 0.0899598 | 0.0194679 |
| py-billing-rounding | mcp_transport_wall_seconds | 5.10989 | 5.87139 | 0.761504 |
| py-billing-rounding | natural_retrieval_wall_seconds | 0.850484 | 0.867725 | 0.0172415 |
| py-billing-rounding | server_sampled_cpu_seconds | 4.84 | 5.45 | 0.61 |
| py-boolean-config | index_wall_seconds | 0.188606 | 0.243913 | 0.0553069 |
| py-boolean-config | index_client_cpu_seconds | 0.0929982 | 0.148056 | 0.0550579 |
| py-boolean-config | natural_retrieval_wall_seconds | 0.835889 | 0.855881 | 0.0199922 |
| py-boolean-config | server_sampled_cpu_seconds | 4.95 | 5.01 | 0.06 |
| py-cursor-pagination | expected_symbol_coverage | 1 | 0 | -1 |
| py-cursor-pagination | index_wall_seconds | 0.134232 | 0.2063 | 0.0720679 |
| py-cursor-pagination | index_client_cpu_seconds | 0.0731581 | 0.0954766 | 0.0223185 |
| py-cursor-pagination | mcp_transport_wall_seconds | 4.43039 | 7.79096 | 3.36057 |
| py-cursor-pagination | natural_retrieval_wall_seconds | 0.750083 | 1.20459 | 0.454508 |
| py-cursor-pagination | server_sampled_cpu_seconds | 4.31 | 7.43 | 3.12 |
| py-lru-eviction | expected_symbol_coverage | 1 | 0 | -1 |
| py-lru-eviction | index_wall_seconds | 0.130518 | 0.515362 | 0.384843 |
| py-lru-eviction | index_client_cpu_seconds | 0.0730964 | 0.436146 | 0.363049 |
| py-lru-eviction | mcp_transport_wall_seconds | 4.33373 | 22.3552 | 18.0214 |
| py-lru-eviction | natural_retrieval_wall_seconds | 0.587975 | 2.34792 | 1.75994 |
| py-lru-eviction | server_sampled_cpu_seconds | 4.14 | 21.48 | 17.34 |
| py-optimistic-revision | index_wall_seconds | 0.115317 | 0.181592 | 0.0662747 |
| py-optimistic-revision | index_client_cpu_seconds | 0.0620273 | 0.0902204 | 0.0281931 |
| py-optimistic-revision | mcp_transport_wall_seconds | 4.47404 | 8.04194 | 3.56789 |
| py-optimistic-revision | natural_retrieval_wall_seconds | 0.653932 | 0.870959 | 0.217027 |
| py-optimistic-revision | server_sampled_cpu_seconds | 4.34 | 7.52 | 3.18 |
| py-optimistic-revision | server_sampled_peak_rss_bytes | 74919936 | 75218944 | 299008 |
| py-scope-authorization | index_wall_seconds | 0.180434 | 0.189753 | 0.00931934 |
| py-scope-authorization | mcp_transport_wall_seconds | 4.4768 | 6.22971 | 1.75292 |
| py-scope-authorization | natural_retrieval_wall_seconds | 0.455082 | 0.765171 | 0.310088 |
| py-scope-authorization | server_sampled_cpu_seconds | 4.2 | 5.85 | 1.65 |
| py-storage-containment | index_wall_seconds | 0.137034 | 0.138374 | 0.0013401 |
| py-transitive-dependencies | mcp_transport_wall_seconds | 4.60543 | 5.0794 | 0.473978 |
| py-transitive-dependencies | natural_retrieval_wall_seconds | 0.714454 | 0.813629 | 0.0991754 |
| py-transitive-dependencies | server_sampled_cpu_seconds | 4.35 | 4.9 | 0.55 |
| py-ttl-boundary | index_wall_seconds | 0.140488 | 0.40978 | 0.269292 |
| py-ttl-boundary | index_client_cpu_seconds | 0.068897 | 0.182184 | 0.113287 |
| py-ttl-boundary | mcp_transport_wall_seconds | 5.13742 | 15.0628 | 9.92537 |
| py-ttl-boundary | natural_retrieval_wall_seconds | 0.686612 | 0.751563 | 0.0649505 |
| py-ttl-boundary | server_sampled_cpu_seconds | 4.81 | 14.92 | 10.11 |
| ts-and-search | index_wall_seconds | 0.251644 | 0.440067 | 0.188424 |
| ts-and-search | index_client_cpu_seconds | 0.0553851 | 0.0720365 | 0.0166514 |
| ts-and-search | mcp_transport_wall_seconds | 4.7134 | 5.90051 | 1.18712 |
| ts-and-search | natural_retrieval_wall_seconds | 0.589366 | 0.919601 | 0.330235 |
| ts-and-search | server_sampled_cpu_seconds | 4.43 | 5.48 | 1.05 |
| ts-and-search | server_sampled_peak_rss_bytes | 88207360 | 89477120 | 1269760 |
| ts-billing-rounding | index_wall_seconds | 0.302094 | 0.371952 | 0.069858 |
| ts-billing-rounding | index_client_cpu_seconds | 0.0805072 | 0.13081 | 0.0503029 |
| ts-billing-rounding | mcp_transport_wall_seconds | 5.08196 | 17.22 | 12.138 |
| ts-billing-rounding | natural_retrieval_wall_seconds | 0.656348 | 1.27723 | 0.620886 |
| ts-billing-rounding | server_sampled_cpu_seconds | 4.77 | 15.19 | 10.42 |
| ts-boolean-config | index_wall_seconds | 0.292566 | 0.338887 | 0.046321 |
| ts-boolean-config | index_client_cpu_seconds | 0.0630404 | 0.0883975 | 0.0253571 |
| ts-boolean-config | mcp_transport_wall_seconds | 5.01756 | 15.267 | 10.2495 |
| ts-boolean-config | natural_retrieval_wall_seconds | 0.877696 | 3.69151 | 2.81381 |
| ts-boolean-config | server_sampled_cpu_seconds | 4.74 | 14.14 | 9.4 |
| ts-boolean-config | server_sampled_peak_rss_bytes | 88096768 | 89137152 | 1040384 |
| ts-cursor-pagination | expected_symbol_coverage | 1 | 0 | -1 |
| ts-cursor-pagination | mcp_transport_wall_seconds | 4.67532 | 7.32992 | 2.65461 |
| ts-cursor-pagination | natural_retrieval_wall_seconds | 0.604009 | 0.75513 | 0.151121 |
| ts-cursor-pagination | server_sampled_cpu_seconds | 4.36 | 6.95 | 2.59 |
| ts-idempotent-events | index_wall_seconds | 0.241443 | 2.02456 | 1.78311 |
| ts-idempotent-events | index_client_cpu_seconds | 0.0606062 | 0.584641 | 0.524035 |
| ts-idempotent-events | mcp_transport_wall_seconds | 4.13021 | 22.0509 | 17.9207 |
| ts-idempotent-events | natural_retrieval_wall_seconds | 0.623589 | 1.58538 | 0.961795 |
| ts-idempotent-events | server_sampled_cpu_seconds | 3.87 | 20.82 | 16.95 |
| ts-idempotent-events | server_sampled_peak_rss_bytes | 88383488 | 89452544 | 1069056 |
| ts-lru-eviction | expected_symbol_coverage | 1 | 0 | -1 |
| ts-optimistic-revision | index_wall_seconds | 0.315491 | 0.483926 | 0.168435 |
| ts-optimistic-revision | index_client_cpu_seconds | 0.0693487 | 0.0782685 | 0.00891987 |
| ts-optimistic-revision | mcp_transport_wall_seconds | 4.71458 | 9.58265 | 4.86807 |
| ts-optimistic-revision | natural_retrieval_wall_seconds | 0.606762 | 1.42466 | 0.817897 |
| ts-optimistic-revision | server_sampled_cpu_seconds | 4.4 | 8.96 | 4.56 |
| ts-optimistic-revision | server_sampled_peak_rss_bytes | 87769088 | 89600000 | 1830912 |
| ts-scope-authorization | index_wall_seconds | 0.34584 | 0.666424 | 0.320583 |
| ts-scope-authorization | index_client_cpu_seconds | 0.0723903 | 0.166926 | 0.0945355 |
| ts-scope-authorization | mcp_transport_wall_seconds | 6.10612 | 30.3517 | 24.2456 |
| ts-scope-authorization | natural_retrieval_wall_seconds | 1.01466 | 6.28328 | 5.26863 |
| ts-scope-authorization | server_sampled_cpu_seconds | 5.65 | 28.97 | 23.32 |
| ts-selective-retry | index_client_cpu_seconds | 0.0610443 | 0.0786693 | 0.017625 |
| ts-selective-retry | mcp_transport_wall_seconds | 4.61453 | 7.96184 | 3.34732 |
| ts-selective-retry | natural_retrieval_wall_seconds | 0.708164 | 1.8999 | 1.19174 |
| ts-selective-retry | server_sampled_cpu_seconds | 4.24 | 7.52 | 3.28 |
| ts-storage-containment | index_wall_seconds | 0.411405 | 3.16771 | 2.7563 |
| ts-storage-containment | index_client_cpu_seconds | 0.0833092 | 0.835078 | 0.751769 |
| ts-storage-containment | mcp_transport_wall_seconds | 7.33709 | 14.4355 | 7.09837 |
| ts-storage-containment | server_sampled_cpu_seconds | 6.78 | 13.77 | 6.99 |
| ts-transitive-dependencies | index_wall_seconds | 0.285429 | 1.0836 | 0.798176 |
| ts-transitive-dependencies | index_client_cpu_seconds | 0.0686743 | 0.0908758 | 0.0222015 |
| ts-transitive-dependencies | mcp_transport_wall_seconds | 4.63464 | 7.23749 | 2.60285 |
| ts-transitive-dependencies | natural_retrieval_wall_seconds | 0.609253 | 1.01761 | 0.408358 |
| ts-transitive-dependencies | server_sampled_cpu_seconds | 4.4 | 6.36 | 1.96 |
| ts-ttl-boundary | index_client_cpu_seconds | 0.071964 | 0.0778356 | 0.00587166 |
| ts-ttl-boundary | server_sampled_peak_rss_bytes | 85266432 | 89645056 | 4378624 |

Full per-task settings, source hash manifests, min/max distributions, measurements, deltas, invalid-pair reasons, input reports and all failures are retained in the companion JSON. Faster component queries do not establish faster or cheaper completed coding tasks.
