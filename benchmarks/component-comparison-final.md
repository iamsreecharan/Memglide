# Independent MCP component before/after comparison

These real SDK probes are **not live Codex A/B runs**. They establish no token savings, monetary savings, coding success rate, cost per completed task, or semantic context completeness. Those measurements remain unavailable.

Comparison validity: **True**. Observed 24 baseline and 24 candidate tasks; 24 comparable pairs and 0 invalid pairs. Invalid or unavailable pairs have no computed deltas. Both complete input reports, including their original summaries and failures, are embedded in the JSON.

Source provenance:

- baseline: unavailable; git HEAD `unavailable`; source digest `unavailable`.
- candidate: captured_source_state_before_probe; git HEAD `39e8df30565783a686270f8a6f422e56e41e3776`; source digest `b0fd2cc1f3997d1a0d19ab97addaaef00abe2e859a1cacf570162b6fc231df94`.
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
| index_wall_seconds | 24/0 | 0.275028 | 0.245041 | 24/0 | 0.34207 | 0.33422 | 24/0 | 0.0670417 | 0.0380824 |
| index_client_cpu_seconds | 24/0 | 0.082913 | 0.0731273 | 24/0 | 0.101573 | 0.103681 | 24/0 | 0.0186596 | 0.0159462 |
| mcp_transport_wall_seconds | 24/0 | 5.12113 | 5.04976 | 24/0 | 8.24654 | 7.90832 | 24/0 | 3.12541 | 2.81016 |
| natural_retrieval_wall_seconds | 24/0 | 0.77348 | 0.732025 | 24/0 | 1.06938 | 0.862465 | 24/0 | 0.295905 | 0.221956 |
| server_sampled_cpu_seconds | 24/0 | 4.80458 | 4.755 | 24/0 | 7.80375 | 7.205 | 24/0 | 2.99917 | 2.625 |
| server_sampled_peak_rss_bytes | 24/0 | 81954816 | 8.09021e+07 | 24/0 | 84048384 | 8.28088e+07 | 24/0 | 2093568 | -610304 |

Every task and any retained failure:

| Task | Comparable | Baseline / candidate status | File coverage before / after | Declaration visible before / after | Natural hashes before / after | Regression metrics |
|---|---|---|---|---|---|---|
| py-and-search | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-billing-rounding | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-boolean-config | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-cursor-pagination | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, mcp_transport_wall_seconds, server_sampled_cpu_seconds |
| py-idempotent-events | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | mcp_transport_wall_seconds, server_sampled_cpu_seconds |
| py-lru-eviction | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-optimistic-revision | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-scope-authorization | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-selective-retry | True | passed / passed | 1 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-storage-containment | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| py-transitive-dependencies | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| py-ttl-boundary | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, server_sampled_cpu_seconds |
| ts-and-search | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-billing-rounding | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-boolean-config | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| ts-cursor-pagination | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-idempotent-events | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |
| ts-lru-eviction | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | expected_symbol_coverage, index_client_cpu_seconds, mcp_transport_wall_seconds, server_sampled_cpu_seconds |
| ts-optimistic-revision | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-scope-authorization | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-selective-retry | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-storage-containment | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-transitive-dependencies | True | passed / passed | 0 / 1 | 0 / 1 | 1 / 1 | index_wall_seconds, index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds |
| ts-ttl-boundary | True | passed / passed | 1 / 1 | 1 / 1 | 1 / 1 | index_client_cpu_seconds, mcp_transport_wall_seconds, natural_retrieval_wall_seconds, server_sampled_cpu_seconds, server_sampled_peak_rss_bytes |

All 116 observed regressions (including every runtime/resource increase):

| Task | Metric | Baseline | Candidate | Candidate minus baseline |
|---|---|---:|---:|---:|
| py-and-search | expected_symbol_coverage | 1 | 0 | -1 |
| py-and-search | index_wall_seconds | 0.1693 | 0.22783 | 0.0585298 |
| py-and-search | index_client_cpu_seconds | 0.0851665 | 0.094462 | 0.00929545 |
| py-and-search | mcp_transport_wall_seconds | 6.73944 | 13.1501 | 6.41071 |
| py-and-search | natural_retrieval_wall_seconds | 1.02281 | 2.53876 | 1.51595 |
| py-and-search | server_sampled_cpu_seconds | 6.16 | 12.36 | 6.2 |
| py-and-search | server_sampled_peak_rss_bytes | 74948608 | 75051008 | 102400 |
| py-billing-rounding | index_wall_seconds | 0.158139 | 0.313196 | 0.155057 |
| py-billing-rounding | index_client_cpu_seconds | 0.0704919 | 0.155369 | 0.0848776 |
| py-billing-rounding | mcp_transport_wall_seconds | 5.10989 | 6.12072 | 1.01083 |
| py-billing-rounding | server_sampled_cpu_seconds | 4.84 | 5.84 | 1 |
| py-billing-rounding | server_sampled_peak_rss_bytes | 75214848 | 148570112 | 73355264 |
| py-boolean-config | index_wall_seconds | 0.188606 | 0.258235 | 0.0696289 |
| py-boolean-config | index_client_cpu_seconds | 0.0929982 | 0.134122 | 0.0411238 |
| py-boolean-config | mcp_transport_wall_seconds | 5.25648 | 8.15264 | 2.89616 |
| py-boolean-config | server_sampled_cpu_seconds | 4.95 | 7.53 | 2.58 |
| py-boolean-config | server_sampled_peak_rss_bytes | 75317248 | 75390976 | 73728 |
| py-cursor-pagination | expected_symbol_coverage | 1 | 0 | -1 |
| py-cursor-pagination | mcp_transport_wall_seconds | 4.43039 | 4.63256 | 0.202167 |
| py-cursor-pagination | server_sampled_cpu_seconds | 4.31 | 4.4 | 0.09 |
| py-idempotent-events | mcp_transport_wall_seconds | 5.63372 | 8.75533 | 3.12161 |
| py-idempotent-events | server_sampled_cpu_seconds | 5.22 | 8.37 | 3.15 |
| py-lru-eviction | expected_symbol_coverage | 1 | 0 | -1 |
| py-lru-eviction | index_wall_seconds | 0.130518 | 0.194135 | 0.0636162 |
| py-lru-eviction | index_client_cpu_seconds | 0.0730964 | 0.112721 | 0.0396244 |
| py-lru-eviction | mcp_transport_wall_seconds | 4.33373 | 4.9041 | 0.570373 |
| py-lru-eviction | natural_retrieval_wall_seconds | 0.587975 | 0.813572 | 0.225597 |
| py-lru-eviction | server_sampled_cpu_seconds | 4.14 | 4.71 | 0.57 |
| py-optimistic-revision | index_wall_seconds | 0.115317 | 0.147359 | 0.0320421 |
| py-optimistic-revision | index_client_cpu_seconds | 0.0620273 | 0.0736454 | 0.0116181 |
| py-optimistic-revision | mcp_transport_wall_seconds | 4.47404 | 5.28435 | 0.810306 |
| py-optimistic-revision | natural_retrieval_wall_seconds | 0.653932 | 0.681794 | 0.0278621 |
| py-optimistic-revision | server_sampled_cpu_seconds | 4.34 | 4.98 | 0.64 |
| py-optimistic-revision | server_sampled_peak_rss_bytes | 74919936 | 74973184 | 53248 |
| py-scope-authorization | mcp_transport_wall_seconds | 4.4768 | 5.66002 | 1.18322 |
| py-scope-authorization | natural_retrieval_wall_seconds | 0.455082 | 0.815402 | 0.36032 |
| py-scope-authorization | server_sampled_cpu_seconds | 4.2 | 5.45 | 1.25 |
| py-selective-retry | index_wall_seconds | 0.175888 | 0.215976 | 0.0400885 |
| py-selective-retry | mcp_transport_wall_seconds | 5.21614 | 10.3943 | 5.17813 |
| py-selective-retry | natural_retrieval_wall_seconds | 0.780232 | 1.69394 | 0.913706 |
| py-selective-retry | server_sampled_cpu_seconds | 4.82 | 9.47 | 4.65 |
| py-selective-retry | server_sampled_peak_rss_bytes | 74907648 | 74969088 | 61440 |
| py-storage-containment | index_wall_seconds | 0.137034 | 0.165031 | 0.027997 |
| py-storage-containment | index_client_cpu_seconds | 0.0732403 | 0.0803136 | 0.00707335 |
| py-storage-containment | mcp_transport_wall_seconds | 5.51049 | 15.7963 | 10.2859 |
| py-storage-containment | natural_retrieval_wall_seconds | 0.749596 | 1.35583 | 0.606232 |
| py-storage-containment | server_sampled_cpu_seconds | 5.22 | 16.24 | 11.02 |
| py-storage-containment | server_sampled_peak_rss_bytes | 75431936 | 75788288 | 356352 |
| py-transitive-dependencies | index_wall_seconds | 0.189013 | 0.205081 | 0.0160681 |
| py-transitive-dependencies | mcp_transport_wall_seconds | 4.60543 | 6.96285 | 2.35743 |
| py-transitive-dependencies | natural_retrieval_wall_seconds | 0.714454 | 1.13581 | 0.421352 |
| py-transitive-dependencies | server_sampled_cpu_seconds | 4.35 | 6.59 | 2.24 |
| py-ttl-boundary | index_wall_seconds | 0.140488 | 0.168904 | 0.028416 |
| py-ttl-boundary | index_client_cpu_seconds | 0.068897 | 0.0858022 | 0.0169051 |
| py-ttl-boundary | mcp_transport_wall_seconds | 5.13742 | 6.5649 | 1.42748 |
| py-ttl-boundary | server_sampled_cpu_seconds | 4.81 | 6.23 | 1.42 |
| ts-and-search | index_wall_seconds | 0.251644 | 0.576544 | 0.3249 |
| ts-and-search | index_client_cpu_seconds | 0.0553851 | 0.147314 | 0.0919294 |
| ts-and-search | mcp_transport_wall_seconds | 4.7134 | 10.5614 | 5.848 |
| ts-and-search | natural_retrieval_wall_seconds | 0.589366 | 0.639235 | 0.0498695 |
| ts-and-search | server_sampled_cpu_seconds | 4.43 | 10.18 | 5.75 |
| ts-billing-rounding | index_wall_seconds | 0.302094 | 0.355245 | 0.053151 |
| ts-billing-rounding | index_client_cpu_seconds | 0.0805072 | 0.0973209 | 0.0168137 |
| ts-billing-rounding | mcp_transport_wall_seconds | 5.08196 | 6.59399 | 1.51203 |
| ts-billing-rounding | natural_retrieval_wall_seconds | 0.656348 | 0.991737 | 0.335389 |
| ts-billing-rounding | server_sampled_cpu_seconds | 4.77 | 6.25 | 1.48 |
| ts-boolean-config | index_wall_seconds | 0.292566 | 0.476885 | 0.184319 |
| ts-boolean-config | index_client_cpu_seconds | 0.0630404 | 0.103337 | 0.0402965 |
| ts-boolean-config | mcp_transport_wall_seconds | 5.01756 | 8.81468 | 3.79711 |
| ts-boolean-config | server_sampled_cpu_seconds | 4.74 | 8.36 | 3.62 |
| ts-boolean-config | server_sampled_peak_rss_bytes | 88096768 | 89395200 | 1298432 |
| ts-cursor-pagination | expected_symbol_coverage | 1 | 0 | -1 |
| ts-cursor-pagination | index_client_cpu_seconds | 0.0817547 | 0.104025 | 0.0222708 |
| ts-cursor-pagination | mcp_transport_wall_seconds | 4.67532 | 8.28906 | 3.61374 |
| ts-cursor-pagination | natural_retrieval_wall_seconds | 0.604009 | 0.969766 | 0.365757 |
| ts-cursor-pagination | server_sampled_cpu_seconds | 4.36 | 7.82 | 3.46 |
| ts-idempotent-events | index_wall_seconds | 0.241443 | 0.497625 | 0.256182 |
| ts-idempotent-events | index_client_cpu_seconds | 0.0606062 | 0.0728788 | 0.0122726 |
| ts-idempotent-events | mcp_transport_wall_seconds | 4.13021 | 7.664 | 3.53379 |
| ts-idempotent-events | natural_retrieval_wall_seconds | 0.623589 | 0.955619 | 0.33203 |
| ts-idempotent-events | server_sampled_cpu_seconds | 3.87 | 6.88 | 3.01 |
| ts-idempotent-events | server_sampled_peak_rss_bytes | 88383488 | 89575424 | 1191936 |
| ts-lru-eviction | expected_symbol_coverage | 1 | 0 | -1 |
| ts-lru-eviction | index_client_cpu_seconds | 0.0920858 | 0.107164 | 0.0150787 |
| ts-lru-eviction | mcp_transport_wall_seconds | 5.40035 | 6.62785 | 1.2275 |
| ts-lru-eviction | server_sampled_cpu_seconds | 5.06 | 6.31 | 1.25 |
| ts-optimistic-revision | index_wall_seconds | 0.315491 | 0.930722 | 0.615231 |
| ts-optimistic-revision | index_client_cpu_seconds | 0.0693487 | 0.146139 | 0.0767902 |
| ts-optimistic-revision | mcp_transport_wall_seconds | 4.71458 | 6.13276 | 1.41818 |
| ts-optimistic-revision | natural_retrieval_wall_seconds | 0.606762 | 0.861067 | 0.254305 |
| ts-optimistic-revision | server_sampled_cpu_seconds | 4.4 | 5.69 | 1.29 |
| ts-scope-authorization | index_wall_seconds | 0.34584 | 0.381917 | 0.0360763 |
| ts-scope-authorization | index_client_cpu_seconds | 0.0723903 | 0.114006 | 0.0416157 |
| ts-scope-authorization | mcp_transport_wall_seconds | 6.10612 | 11.2975 | 5.19137 |
| ts-scope-authorization | natural_retrieval_wall_seconds | 1.01466 | 2.85348 | 1.83882 |
| ts-scope-authorization | server_sampled_cpu_seconds | 5.65 | 9.95 | 4.3 |
| ts-selective-retry | index_wall_seconds | 0.334389 | 0.424261 | 0.0898722 |
| ts-selective-retry | index_client_cpu_seconds | 0.0610443 | 0.0732786 | 0.0122343 |
| ts-selective-retry | mcp_transport_wall_seconds | 4.61453 | 7.25499 | 2.64047 |
| ts-selective-retry | natural_retrieval_wall_seconds | 0.708164 | 1.06059 | 0.352428 |
| ts-selective-retry | server_sampled_cpu_seconds | 4.24 | 6.73 | 2.49 |
| ts-storage-containment | index_wall_seconds | 0.411405 | 0.426002 | 0.0145969 |
| ts-storage-containment | index_client_cpu_seconds | 0.0833092 | 0.0891495 | 0.00584037 |
| ts-storage-containment | mcp_transport_wall_seconds | 7.33709 | 11.0975 | 3.76038 |
| ts-storage-containment | natural_retrieval_wall_seconds | 1.46602 | 1.53003 | 0.0640103 |
| ts-storage-containment | server_sampled_cpu_seconds | 6.78 | 10.51 | 3.73 |
| ts-transitive-dependencies | index_wall_seconds | 0.285429 | 0.604571 | 0.319142 |
| ts-transitive-dependencies | index_client_cpu_seconds | 0.0686743 | 0.120609 | 0.0519352 |
| ts-transitive-dependencies | mcp_transport_wall_seconds | 4.63464 | 8.92347 | 4.28883 |
| ts-transitive-dependencies | natural_retrieval_wall_seconds | 0.609253 | 0.784593 | 0.17534 |
| ts-transitive-dependencies | server_sampled_cpu_seconds | 4.4 | 8.52 | 4.12 |
| ts-ttl-boundary | index_client_cpu_seconds | 0.071964 | 0.108422 | 0.0364584 |
| ts-ttl-boundary | mcp_transport_wall_seconds | 5.55735 | 8.28151 | 2.72416 |
| ts-ttl-boundary | natural_retrieval_wall_seconds | 0.810265 | 1.02858 | 0.218315 |
| ts-ttl-boundary | server_sampled_cpu_seconds | 5.25 | 7.92 | 2.67 |
| ts-ttl-boundary | server_sampled_peak_rss_bytes | 85266432 | 87232512 | 1966080 |

Full per-task settings, source hash manifests, min/max distributions, measurements, deltas, invalid-pair reasons, input reports and all failures are retained in the companion JSON. Faster component queries do not establish faster or cheaper completed coding tasks.
