# Memglide refinement measurements

These component measurements establish no live Codex coding, token or cost benefit. Every original observation and failure is retained in the JSON report or its checksummed inputs. p95 uses the nearest rank of the observed finite sample; it is not a confidence bound.

SDK request pairing valid: **True**.

- Startup includes Python/SDK initialization and list_tools; host caches were not flushed.
- The first natural retrieval is not a repeated warm-query measurement.
- Workflow includes startup, seven calls, controlled edit and shutdown; it is not retrieval latency.
- Declared-target precision excludes other potentially useful context; it is a narrow selectivity proxy.
- Complete method and dependency recall were not measured by these historical SDK probes.
- Sampled local CPU is an observed lower bound; shared RSS pages may be counted repeatedly.
- Single sequential task observations do not establish a causal timing improvement or statistical significance.

## SDK component baseline

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| index_wall_seconds | 24 / 0 | 0.34207 | 0.33422 | 0.604571 | 0.119852 | 0.930722 |
| startup_initialize_list_tools_wall_seconds | 24 / 0 | 3.53502 | 3.18713 | 5.02274 | 2.03219 | 7.63411 |
| first_natural_retrieval_wall_seconds | 24 / 0 | 1.06938 | 0.862465 | 2.53876 | 0.534912 | 2.85348 |
| seven_call_workflow_wall_seconds | 24 / 0 | 8.24654 | 7.90832 | 13.1501 | 4.63256 | 15.7963 |
| returned_file_count | 24 / 0 | 14.0833 | 14 | 15 | 12 | 15 |
| returned_item_count | 24 / 0 | 14.4167 | 14 | 16 | 12 | 17 |
| declared_target_file_precision | 24 / 0 | 0.071131 | 0.0714286 | 0.0714286 | 0.0666667 | 0.0833333 |
| target_file_recall | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| exact_symbol_identity_recall | 24 / 0 | 0.166667 | 0 | 1 | 0 | 1 |
| declaration_visible_fraction | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| natural_evidence_hashes_current | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| old_passport_detected_edit | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| updated_target_hash_matches | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| updated_edit_marker_visible | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| sampled_server_cpu_seconds | 24 / 0 | 7.80375 | 7.205 | 12.36 | 4.4 | 16.24 |
| sampled_server_peak_rss_bytes | 24 / 0 | 84048384 | 8.28088e+07 | 89575424 | 74043392 | 148570112 |

## SDK component candidate

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| index_wall_seconds | 24 / 0 | 0.195766 | 0.196493 | 0.277468 | 0.101943 | 0.279796 |
| startup_initialize_list_tools_wall_seconds | 24 / 0 | 1.84024 | 1.82137 | 2.35742 | 1.30161 | 2.50303 |
| first_natural_retrieval_wall_seconds | 24 / 0 | 0.423709 | 0.395301 | 0.598591 | 0.230188 | 1.197 |
| seven_call_workflow_wall_seconds | 24 / 0 | 3.66701 | 3.60564 | 4.42331 | 2.64471 | 5.26732 |
| returned_file_count | 24 / 0 | 8.66667 | 8 | 13 | 4 | 14 |
| returned_item_count | 24 / 0 | 9.41667 | 9 | 16 | 4 | 16 |
| declared_target_file_precision | 24 / 0 | 0.132695 | 0.125 | 0.25 | 0.0714286 | 0.25 |
| target_file_recall | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| exact_symbol_identity_recall | 24 / 0 | 0.166667 | 0 | 1 | 0 | 1 |
| declaration_visible_fraction | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| natural_evidence_hashes_current | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| old_passport_detected_edit | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| updated_target_hash_matches | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| updated_edit_marker_visible | 24 / 0 | 1 | 1 | 1 | 1 | 1 |
| sampled_server_cpu_seconds | 24 / 0 | 3.36125 | 3.31 | 4.1 | 2.36 | 4.43 |
| sampled_server_peak_rss_bytes | 24 / 0 | 8.37948e+07 | 8.40929e+07 | 89870336 | 74014720 | 145670144 |

## SDK component paired_candidate_minus_baseline

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| index_wall_seconds | 24 / 0 | -0.146304 | -0.136648 | 0.034751 | -0.669029 | 0.0427858 |
| startup_initialize_list_tools_wall_seconds | 24 / 0 | -1.69478 | -1.45143 | -0.333973 | -6.10183 | 0.00619063 |
| first_natural_retrieval_wall_seconds | 24 / 0 | -0.645675 | -0.45756 | -0.0251486 | -2.39933 | 0.515204 |
| seven_call_workflow_wall_seconds | 24 / 0 | -4.57953 | -4.00081 | -0.868145 | -13.1284 | -0.0170339 |
| returned_file_count | 24 / 0 | -5.41667 | -6 | -1 | -10 | 0 |
| returned_item_count | 24 / 0 | -5 | -5 | -1 | -11 | 0 |
| declared_target_file_precision | 24 / 0 | 0.0615639 | 0.0535714 | 0.178571 | 0 | 0.178571 |
| target_file_recall | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| exact_symbol_identity_recall | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| declaration_visible_fraction | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| natural_evidence_hashes_current | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| old_passport_detected_edit | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| updated_target_hash_matches | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| updated_edit_marker_visible | 24 / 0 | 0 | 0 | 0 | 0 | 0 |
| sampled_server_cpu_seconds | 24 / 0 | -4.4425 | -3.765 | -1.11 | -13.81 | -0.55 |
| sampled_server_peak_rss_bytes | 24 / 0 | -253611 | 55296 | 4608000 | -72716288 | 71626752 |

## SDK observations and failures

| Arm | Task | Status | Error |
|---|---|---|---|
| baseline | py-ttl-boundary | passed | unavailable |
| baseline | py-lru-eviction | passed | unavailable |
| baseline | py-cursor-pagination | passed | unavailable |
| baseline | py-optimistic-revision | passed | unavailable |
| baseline | py-scope-authorization | passed | unavailable |
| baseline | py-storage-containment | passed | unavailable |
| baseline | py-transitive-dependencies | passed | unavailable |
| baseline | py-selective-retry | passed | unavailable |
| baseline | py-boolean-config | passed | unavailable |
| baseline | py-and-search | passed | unavailable |
| baseline | py-billing-rounding | passed | unavailable |
| baseline | py-idempotent-events | passed | unavailable |
| baseline | ts-ttl-boundary | passed | unavailable |
| baseline | ts-lru-eviction | passed | unavailable |
| baseline | ts-cursor-pagination | passed | unavailable |
| baseline | ts-optimistic-revision | passed | unavailable |
| baseline | ts-scope-authorization | passed | unavailable |
| baseline | ts-storage-containment | passed | unavailable |
| baseline | ts-transitive-dependencies | passed | unavailable |
| baseline | ts-selective-retry | passed | unavailable |
| baseline | ts-boolean-config | passed | unavailable |
| baseline | ts-and-search | passed | unavailable |
| baseline | ts-billing-rounding | passed | unavailable |
| baseline | ts-idempotent-events | passed | unavailable |
| candidate | py-ttl-boundary | passed | unavailable |
| candidate | py-lru-eviction | passed | unavailable |
| candidate | py-cursor-pagination | passed | unavailable |
| candidate | py-optimistic-revision | passed | unavailable |
| candidate | py-scope-authorization | passed | unavailable |
| candidate | py-storage-containment | passed | unavailable |
| candidate | py-transitive-dependencies | passed | unavailable |
| candidate | py-selective-retry | passed | unavailable |
| candidate | py-boolean-config | passed | unavailable |
| candidate | py-and-search | passed | unavailable |
| candidate | py-billing-rounding | passed | unavailable |
| candidate | py-idempotent-events | passed | unavailable |
| candidate | ts-ttl-boundary | passed | unavailable |
| candidate | ts-lru-eviction | passed | unavailable |
| candidate | ts-cursor-pagination | passed | unavailable |
| candidate | ts-optimistic-revision | passed | unavailable |
| candidate | ts-scope-authorization | passed | unavailable |
| candidate | ts-storage-containment | passed | unavailable |
| candidate | ts-transitive-dependencies | passed | unavailable |
| candidate | ts-selective-retry | passed | unavailable |
| candidate | ts-boolean-config | passed | unavailable |
| candidate | ts-and-search | passed | unavailable |
| candidate | ts-billing-rounding | passed | unavailable |
| candidate | ts-idempotent-events | passed | unavailable |

## Seen development trials

Previously evaluated development tasks used for tuning; not held-out evidence. Every supplied earlier and rejected trial is retained.

### Retained development trial 1

Previously evaluated Atlas development tasks, frozen rankers and common current context packer. No model calls or timing comparisons. Legacy is eligible; no unseen results used for ranking selection.

| Strategy | First-file hit@1 | Reciprocal rank | Declared files | Declaration visible | Context files | JSON bytes |
|---|---:|---:|---:|---:|---:|---:|
| refined | 0.5 | 0.75 | 1 | 1 | 13.25 | 22540.5 |
| previous | 0.25 | 0.459722 | 1 | 1 | 14.0833 | 23294.4 |
| legacy | 0.333333 | 0.545288 | 1 | 1 | 14.7083 | 23674.5 |
### Retained development trial 2

Previously evaluated Atlas development tasks, frozen rankers and common current context packer. No model calls or timing comparisons. Legacy is eligible; no unseen results used for ranking selection.

| Strategy | First-file hit@1 | Reciprocal rank | Declared files | Declaration visible | Context files | JSON bytes |
|---|---:|---:|---:|---:|---:|---:|
| refined | 0.5 | 0.75 | 1 | 1 | 13.25 | 22520.5 |
| previous | 0.25 | 0.459722 | 1 | 1 | 14.0833 | 23283.9 |
| legacy | 0.333333 | 0.545288 | 1 | 1 | 14.7083 | 23672 |
### Retained development trial 3

Previously evaluated Atlas development tasks, frozen rankers and common current context packer. No model calls or timing comparisons. Legacy is eligible; no unseen results used for ranking selection.

| Strategy | First-file hit@1 | Reciprocal rank | Declared files | Declaration visible | Context files | JSON bytes |
|---|---:|---:|---:|---:|---:|---:|
| refined | 0.5 | 0.75 | 1 | 1 | 8.66667 | 17758.9 |
| previous | 0.25 | 0.459722 | 1 | 1 | 10.7083 | 20496.5 |
| legacy | 0.333333 | 0.545288 | 1 | 1 | 9.625 | 20025.1 |

## Fresh retrieval evaluation

Evaluation status: **valid**. Source and harness attestations are retained in the JSON; invalid evaluations establish no comparative benefit.

- Complete-body and dependency recall cover the explicitly declared fixture expectations only.
- Returned JSON bytes and estimated planning tokens are not measured or billed model tokens.
- Missing metrics remain missing, including failed observations; failure counts must accompany conditional means.
- Multiple repeats of the same query are correlated; pooled p95 is descriptive only.
- Primary-file rank is undefined on misses; inspect top-1 and reciprocal rank, which retain miss penalties.

### Strategy: legacy

Status counts: `{"ok": 48}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| primary_file_rank | 48 / 0 | 16.625 | 8 | 55 | 1 | 56 |
| primary_file_hit_at_1 | 48 / 0 | 0.0833333 | 0 | 1 | 0 | 1 |
| primary_file_reciprocal_rank | 48 / 0 | 0.232434 | 0.125 | 1 | 0.0178571 | 1 |
| search_wall_seconds | 48 / 0 | 0.233742 | 0.206831 | 0.389947 | 0.140237 | 0.634054 |
| search_process_cpu_seconds | 48 / 0 | 0.232694 | 0.206546 | 0.389753 | 0.139998 | 0.633723 |
| context_wall_seconds | 48 / 0 | 0.149329 | 0.104676 | 0.310742 | 0.0522562 | 0.429346 |
| context_process_cpu_seconds | 48 / 0 | 0.132482 | 0.0885684 | 0.288157 | 0.0398793 | 0.395959 |
| search_plus_context_wall_seconds | 48 / 0 | 0.38307 | 0.331973 | 0.731263 | 0.210931 | 1.04119 |
| context_output_json_bytes | 48 / 0 | 16551 | 18589 | 23042 | 6993 | 23111 |
| context_estimated_planning_tokens | 48 / 0 | 5746.29 | 6479.5 | 7943 | 2448 | 7981 |
| context_returned_file_count | 48 / 0 | 10.625 | 11 | 17 | 4 | 18 |
| context_returned_item_count | 48 / 0 | 11.8333 | 14 | 17 | 4 | 18 |
| context_declared_file_precision | 48 / 0 | 0.224163 | 0.188235 | 0.5 | 0 | 0.5 |
| required_file_recall | 48 / 0 | 0.680556 | 0.666667 | 1 | 0 | 1 |
| primary_complete_body_coverage | 48 / 0 | 0.791667 | 1 | 1 | 0 | 1 |
| required_dependency_complete_body_recall | 48 / 0 | 0.625 | 0.5 | 1 | 0 | 1 |
| all_required_bodies_present | 48 / 0 | 0.458333 | 0 | 1 | 0 | 1 |

### Strategy: previous

Status counts: `{"ok": 48}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| primary_file_rank | 48 / 0 | 5.75 | 6 | 12 | 1 | 12 |
| primary_file_hit_at_1 | 48 / 0 | 0.333333 | 0 | 1 | 0 | 1 |
| primary_file_reciprocal_rank | 48 / 0 | 0.423001 | 0.166667 | 1 | 0.0833333 | 1 |
| search_wall_seconds | 48 / 0 | 0.242547 | 0.215307 | 0.40654 | 0.140364 | 0.414239 |
| search_process_cpu_seconds | 48 / 0 | 0.241448 | 0.213738 | 0.406019 | 0.140045 | 0.414395 |
| context_wall_seconds | 48 / 0 | 0.207264 | 0.213285 | 0.406569 | 0.0440691 | 0.532401 |
| context_process_cpu_seconds | 48 / 0 | 0.188877 | 0.197958 | 0.382124 | 0.0313445 | 0.502858 |
| search_plus_context_wall_seconds | 48 / 0 | 0.44981 | 0.436878 | 0.727213 | 0.196568 | 0.946641 |
| context_output_json_bytes | 48 / 0 | 17568.8 | 22831 | 23140 | 6586 | 23198 |
| context_estimated_planning_tokens | 48 / 0 | 6070.29 | 7891.5 | 8000 | 2281 | 8000 |
| context_returned_file_count | 48 / 0 | 10.25 | 10 | 17 | 4 | 18 |
| context_returned_item_count | 48 / 0 | 12.9167 | 17 | 18 | 4 | 18 |
| context_declared_file_precision | 48 / 0 | 0.140448 | 0.117647 | 0.4 | 0 | 0.4 |
| required_file_recall | 48 / 0 | 0.527778 | 0.666667 | 1 | 0 | 1 |
| primary_complete_body_coverage | 48 / 0 | 0.666667 | 1 | 1 | 0 | 1 |
| required_dependency_complete_body_recall | 48 / 0 | 0.416667 | 0.25 | 1 | 0 | 1 |
| all_required_bodies_present | 48 / 0 | 0.333333 | 0 | 1 | 0 | 1 |

### Strategy: refined

Status counts: `{"ok": 48}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| primary_file_rank | 48 / 0 | 5.75 | 6 | 12 | 1 | 12 |
| primary_file_hit_at_1 | 48 / 0 | 0.333333 | 0 | 1 | 0 | 1 |
| primary_file_reciprocal_rank | 48 / 0 | 0.423001 | 0.166667 | 1 | 0.0833333 | 1 |
| search_wall_seconds | 48 / 0 | 0.249259 | 0.230224 | 0.402458 | 0.149733 | 0.472681 |
| search_process_cpu_seconds | 48 / 0 | 0.24777 | 0.22998 | 0.391913 | 0.148715 | 0.472642 |
| context_wall_seconds | 48 / 0 | 0.185706 | 0.188525 | 0.317093 | 0.0476919 | 0.413796 |
| context_process_cpu_seconds | 48 / 0 | 0.168115 | 0.175242 | 0.302736 | 0.0357539 | 0.385145 |
| search_plus_context_wall_seconds | 48 / 0 | 0.434965 | 0.424715 | 0.703952 | 0.200888 | 0.78976 |
| context_output_json_bytes | 48 / 0 | 17568.8 | 22831 | 23140 | 6586 | 23198 |
| context_estimated_planning_tokens | 48 / 0 | 6070.29 | 7891.5 | 8000 | 2281 | 8000 |
| context_returned_file_count | 48 / 0 | 10.25 | 10 | 17 | 4 | 18 |
| context_returned_item_count | 48 / 0 | 12.9167 | 17 | 18 | 4 | 18 |
| context_declared_file_precision | 48 / 0 | 0.140448 | 0.117647 | 0.4 | 0 | 0.4 |
| required_file_recall | 48 / 0 | 0.527778 | 0.666667 | 1 | 0 | 1 |
| primary_complete_body_coverage | 48 / 0 | 0.666667 | 1 | 1 | 0 | 1 |
| required_dependency_complete_body_recall | 48 / 0 | 0.416667 | 0.25 | 1 | 0 | 1 |
| all_required_bodies_present | 48 / 0 | 0.333333 | 0 | 1 | 0 | 1 |

| Strategy | Query | Repeat | Status | Required files | Complete primary body | Complete declared dependencies | Returned files | Errors |
|---|---|---:|---|---:|---:|---:|---:|---|
| refined | meridian-python-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| legacy | meridian-python-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-media-extend | 1 | ok | 1 | 1 | 0 | 10 | [] |
| legacy | meridian-python-media-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| refined | meridian-python-media-extend | 1 | ok | 1 | 1 | 0 | 10 | [] |
| legacy | meridian-python-media-revoke | 1 | ok | 1 | 1 | 1 | 12 | [] |
| refined | meridian-python-media-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-python-media-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| legacy | meridian-python-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-appointments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-python-appointments-extend | 1 | ok | 1 | 1 | 1 | 6 | [] |
| refined | meridian-python-appointments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-python-appointments-revoke | 1 | ok | 1 | 1 | 1 | 6 | [] |
| refined | meridian-python-appointments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-python-appointments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| legacy | meridian-python-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-specimens-extend | 1 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-python-specimens-extend | 1 | ok | 0 | 0 | 0 | 10 | [] |
| refined | meridian-python-specimens-extend | 1 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-python-specimens-revoke | 1 | ok | 1 | 1 | 1 | 12 | [] |
| refined | meridian-python-specimens-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-python-specimens-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| legacy | meridian-python-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-deployments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-python-deployments-extend | 1 | ok | 1 | 1 | 1 | 8 | [] |
| refined | meridian-python-deployments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-python-deployments-revoke | 1 | ok | 1 | 1 | 1 | 6 | [] |
| refined | meridian-python-deployments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-python-deployments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-python-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| refined | meridian-python-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| refined | meridian-python-media-extend | 2 | ok | 1 | 1 | 0 | 10 | [] |
| legacy | meridian-python-media-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| previous | meridian-python-media-extend | 2 | ok | 1 | 1 | 0 | 10 | [] |
| previous | meridian-python-media-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-media-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-python-media-revoke | 2 | ok | 1 | 1 | 1 | 12 | [] |
| legacy | meridian-python-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-appointments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-python-appointments-extend | 2 | ok | 1 | 1 | 1 | 6 | [] |
| previous | meridian-python-appointments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| previous | meridian-python-appointments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-appointments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-python-appointments-revoke | 2 | ok | 1 | 1 | 1 | 6 | [] |
| legacy | meridian-python-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-specimens-extend | 2 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-python-specimens-extend | 2 | ok | 0 | 0 | 0 | 10 | [] |
| previous | meridian-python-specimens-extend | 2 | ok | 0.333333 | 1 | 0 | 10 | [] |
| previous | meridian-python-specimens-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-specimens-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-python-specimens-revoke | 2 | ok | 1 | 1 | 1 | 12 | [] |
| legacy | meridian-python-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-deployments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-python-deployments-extend | 2 | ok | 1 | 1 | 1 | 8 | [] |
| previous | meridian-python-deployments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| previous | meridian-python-deployments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-python-deployments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-python-deployments-revoke | 2 | ok | 1 | 1 | 1 | 6 | [] |
| refined | meridian-typescript-media-release | 1 | ok | 1 | 1 | 1 | 15 | [] |
| previous | meridian-typescript-media-release | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-typescript-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 15 | [] |
| previous | meridian-typescript-media-extend | 1 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-typescript-media-extend | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-media-extend | 1 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-typescript-media-revoke | 1 | ok | 1 | 1 | 1 | 12 | [] |
| refined | meridian-typescript-media-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-media-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-appointments-release | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-typescript-appointments-release | 1 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-typescript-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-typescript-appointments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-typescript-appointments-extend | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-appointments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-typescript-appointments-revoke | 1 | ok | 1 | 1 | 1 | 6 | [] |
| refined | meridian-typescript-appointments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-appointments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-specimens-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| previous | meridian-typescript-specimens-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| legacy | meridian-typescript-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-specimens-extend | 1 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-typescript-specimens-extend | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-specimens-extend | 1 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-typescript-specimens-revoke | 1 | ok | 1 | 1 | 1 | 12 | [] |
| refined | meridian-typescript-specimens-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-specimens-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-deployments-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| previous | meridian-typescript-deployments-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| legacy | meridian-typescript-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-deployments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-typescript-deployments-extend | 1 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-deployments-extend | 1 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-typescript-deployments-revoke | 1 | ok | 1 | 1 | 1 | 6 | [] |
| refined | meridian-typescript-deployments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-deployments-revoke | 1 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-typescript-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 15 | [] |
| previous | meridian-typescript-media-release | 2 | ok | 1 | 1 | 1 | 15 | [] |
| refined | meridian-typescript-media-release | 2 | ok | 1 | 1 | 1 | 15 | [] |
| refined | meridian-typescript-media-extend | 2 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-typescript-media-extend | 2 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-media-extend | 2 | ok | 0.333333 | 1 | 0 | 10 | [] |
| previous | meridian-typescript-media-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-media-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-typescript-media-revoke | 2 | ok | 1 | 1 | 1 | 12 | [] |
| legacy | meridian-typescript-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-typescript-appointments-release | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-appointments-release | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-appointments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-typescript-appointments-extend | 2 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-appointments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| previous | meridian-typescript-appointments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-appointments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-typescript-appointments-revoke | 2 | ok | 1 | 1 | 1 | 6 | [] |
| legacy | meridian-typescript-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-specimens-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-specimens-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-specimens-extend | 2 | ok | 0.333333 | 1 | 0 | 10 | [] |
| legacy | meridian-typescript-specimens-extend | 2 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-specimens-extend | 2 | ok | 0.333333 | 1 | 0 | 10 | [] |
| previous | meridian-typescript-specimens-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-specimens-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-typescript-specimens-revoke | 2 | ok | 1 | 1 | 1 | 12 | [] |
| legacy | meridian-typescript-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-deployments-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-deployments-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-deployments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| legacy | meridian-typescript-deployments-extend | 2 | ok | 0 | 0 | 0 | 4 | [] |
| previous | meridian-typescript-deployments-extend | 2 | ok | 1 | 1 | 1 | 10 | [] |
| previous | meridian-typescript-deployments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| refined | meridian-typescript-deployments-revoke | 2 | ok | 0 | 0 | 0 | 4 | [] |
| legacy | meridian-typescript-deployments-revoke | 2 | ok | 1 | 1 | 1 | 6 | [] |

## Direct application timings: baseline

- Direct application timings exclude cold MCP startup and remote model calls.
- Run conditions and equivalence attestations are retained in the supplied report.
- Before/after means alone do not establish comparability; inspect request and source provenance.

### Case: full_source

Status counts: `{"ok": 3}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 3 / 0 | 0.613578 | 0.523255 | 0.956211 | 0.361269 | 0.956211 |
| cpu_seconds | 3 / 0 | 0.570396 | 0.482104 | 0.899205 | 0.329878 | 0.899205 |

### Case: natural

Status counts: `{"ok": 3}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 3 / 0 | 0.439672 | 0.338565 | 0.652112 | 0.328339 | 0.652112 |
| cpu_seconds | 3 / 0 | 0.400456 | 0.305001 | 0.60184 | 0.294525 | 0.60184 |

### Case: small_budget

Status counts: `{"ok": 3}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 3 / 0 | 0.514328 | 0.547666 | 0.667605 | 0.327713 | 0.667605 |
| cpu_seconds | 3 / 0 | 0.469139 | 0.509271 | 0.617749 | 0.280396 | 0.617749 |

| Pair | Status | Wall seconds | CPU seconds | Error |
|---|---|---:|---:|---|
| natural:1 | ok | 0.652112 | 0.60184 | unavailable |
| small_budget:1 | ok | 0.547666 | 0.509271 | unavailable |
| full_source:1 | ok | 0.523255 | 0.482104 | unavailable |
| full_source:2 | ok | 0.956211 | 0.899205 | unavailable |
| small_budget:2 | ok | 0.667605 | 0.617749 | unavailable |
| natural:2 | ok | 0.338565 | 0.305001 | unavailable |
| natural:3 | ok | 0.328339 | 0.294525 | unavailable |
| small_budget:3 | ok | 0.327713 | 0.280396 | unavailable |
| full_source:3 | ok | 0.361269 | 0.329878 | unavailable |

## Direct application timings: candidate

- Direct application timings exclude cold MCP startup and remote model calls.
- Run conditions and equivalence attestations are retained in the supplied report.
- Before/after means alone do not establish comparability; inspect request and source provenance.

### Case: full_source

Status counts: `{"ok": 3}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 3 / 0 | 0.39511 | 0.334799 | 0.560474 | 0.290057 | 0.560474 |
| cpu_seconds | 3 / 0 | 0.347903 | 0.297496 | 0.507351 | 0.238861 | 0.507351 |

### Case: natural

Status counts: `{"ok": 3}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 3 / 0 | 0.342313 | 0.358398 | 0.443161 | 0.22538 | 0.443161 |
| cpu_seconds | 3 / 0 | 0.302521 | 0.315464 | 0.403957 | 0.188142 | 0.403957 |

### Case: small_budget

Status counts: `{"ok": 3}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 3 / 0 | 0.415823 | 0.414881 | 0.564137 | 0.268452 | 0.564137 |
| cpu_seconds | 3 / 0 | 0.36345 | 0.361131 | 0.511482 | 0.217736 | 0.511482 |

| Pair | Status | Wall seconds | CPU seconds | Error |
|---|---|---:|---:|---|
| natural:1 | ok | 0.358398 | 0.315464 | unavailable |
| small_budget:1 | ok | 0.414881 | 0.361131 | unavailable |
| full_source:1 | ok | 0.334799 | 0.297496 | unavailable |
| full_source:2 | ok | 0.560474 | 0.507351 | unavailable |
| small_budget:2 | ok | 0.564137 | 0.511482 | unavailable |
| natural:2 | ok | 0.443161 | 0.403957 | unavailable |
| natural:3 | ok | 0.22538 | 0.188142 | unavailable |
| small_budget:3 | ok | 0.268452 | 0.217736 | unavailable |
| full_source:3 | ok | 0.290057 | 0.238861 | unavailable |

## Direct timing pairs with equal outputs

Valid pairs: 9; comparison valid: True.

Direct calls; excludes cold MCP startup and model use. Same-process cache conditions are declared in the supplied protocol.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| wall_seconds | 9 / 0 | -0.138111 | -0.103468 | 0.104596 | -0.395738 | 0.104596 |
| cpu_seconds | 9 / 0 | -0.142039 | -0.106383 | 0.0989551 | -0.391854 | 0.0989551 |

Observed direct timing increases are retained without claiming statistical significance:

- natural:2: wall_seconds increased 0.104596.
- natural:2: cpu_seconds increased 0.0989551.
- natural: wall_seconds median increased from 0.338565 to 0.358398.
- natural: cpu_seconds median increased from 0.305001 to 0.315464.

All SDK regression observations, invalid pairing reasons, complete fresh retrieval observations, direct timing runs and source provenance are retained in the JSON. Declared body recall does not establish semantic completeness. Costs per successful coding task remain unavailable until model usage/cost and external coding grades are actually measured.
