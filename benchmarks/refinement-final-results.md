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
| index_wall_seconds | 24 / 0 | 0.174267 | 0.17522 | 0.27392 | 0.0850695 | 0.298298 |
| startup_initialize_list_tools_wall_seconds | 24 / 0 | 1.68701 | 1.68764 | 2.33505 | 1.18683 | 2.34961 |
| first_natural_retrieval_wall_seconds | 24 / 0 | 0.341943 | 0.32365 | 0.478081 | 0.255043 | 0.595903 |
| seven_call_workflow_wall_seconds | 24 / 0 | 3.29651 | 3.1267 | 4.51441 | 2.57947 | 4.91242 |
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
| sampled_server_cpu_seconds | 24 / 0 | 3.05667 | 2.89 | 4.08 | 2.39 | 4.49 |
| sampled_server_peak_rss_bytes | 24 / 0 | 80957952 | 8.12216e+07 | 87810048 | 74002432 | 89899008 |

## SDK component paired_candidate_minus_baseline

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| index_wall_seconds | 24 / 0 | -0.167803 | -0.140211 | -0.0164255 | -0.737544 | -0.0126145 |
| startup_initialize_list_tools_wall_seconds | 24 / 0 | -1.84801 | -1.42158 | -0.576315 | -6.14453 | -0.555176 |
| first_natural_retrieval_wall_seconds | 24 / 0 | -0.727442 | -0.524521 | -0.239445 | -2.25757 | -0.202484 |
| seven_call_workflow_wall_seconds | 24 / 0 | -4.95003 | -4.59829 | -1.87838 | -12.8714 | -1.62823 |
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
| sampled_server_cpu_seconds | 24 / 0 | -4.74708 | -4.35 | -1.89 | -13.5 | -1.57 |
| sampled_server_peak_rss_bytes | 24 / 0 | -3090432 | -266240 | 2494464 | -73879552 | 6852608 |

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

## Previously evaluated retrieval validation

Evaluation status: **valid**. Source and harness attestations are retained in the JSON; invalid evaluations establish no comparative benefit.

This is reused validation after an earlier evaluation, not independent unseen evidence. Reuse reason: Reused Meridian validation after initial misses triggered a narrow safety fix: unknown inspection intent bypasses the new source cap and qualified path anchors do not broaden to matching basenames. First fresh results are preserved; this replay is not a new holdout..

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
| search_wall_seconds | 48 / 0 | 0.210099 | 0.203689 | 0.267596 | 0.161247 | 0.333298 |
| search_process_cpu_seconds | 48 / 0 | 0.209218 | 0.203337 | 0.267238 | 0.160691 | 0.333259 |
| context_wall_seconds | 48 / 0 | 0.199248 | 0.189596 | 0.287439 | 0.140146 | 0.313013 |
| context_process_cpu_seconds | 48 / 0 | 0.183699 | 0.174661 | 0.269349 | 0.125695 | 0.297512 |
| search_plus_context_wall_seconds | 48 / 0 | 0.409347 | 0.398752 | 0.535132 | 0.316848 | 0.620737 |
| context_output_json_bytes | 48 / 0 | 22702 | 22809.5 | 23042 | 22262 | 23111 |
| context_estimated_planning_tokens | 48 / 0 | 7895.88 | 7891 | 7991 | 7786 | 7999 |
| context_returned_file_count | 48 / 0 | 20.3333 | 22 | 23 | 15 | 23 |
| context_returned_item_count | 48 / 0 | 20.3333 | 22 | 23 | 15 | 23 |
| context_declared_file_precision | 48 / 0 | 0.0711278 | 0.0454545 | 0.176471 | 0 | 0.2 |
| required_file_recall | 48 / 0 | 0.375 | 0.333333 | 0.666667 | 0 | 0.666667 |
| primary_complete_body_coverage | 48 / 0 | 0.791667 | 1 | 1 | 0 | 1 |
| required_dependency_complete_body_recall | 48 / 0 | 0.166667 | 0 | 0.5 | 0 | 0.5 |
| all_required_bodies_present | 48 / 0 | 0 | 0 | 0 | 0 | 0 |

### Strategy: previous

Status counts: `{"ok": 48}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| primary_file_rank | 48 / 0 | 5.75 | 6 | 12 | 1 | 12 |
| primary_file_hit_at_1 | 48 / 0 | 0.333333 | 0 | 1 | 0 | 1 |
| primary_file_reciprocal_rank | 48 / 0 | 0.423001 | 0.166667 | 1 | 0.0833333 | 1 |
| search_wall_seconds | 48 / 0 | 0.213894 | 0.210205 | 0.278956 | 0.176494 | 0.32731 |
| search_process_cpu_seconds | 48 / 0 | 0.213104 | 0.209049 | 0.275108 | 0.176364 | 0.326894 |
| context_wall_seconds | 48 / 0 | 0.222251 | 0.212911 | 0.309307 | 0.164469 | 0.372389 |
| context_process_cpu_seconds | 48 / 0 | 0.205503 | 0.188848 | 0.295949 | 0.148708 | 0.353305 |
| search_plus_context_wall_seconds | 48 / 0 | 0.436145 | 0.425295 | 0.544777 | 0.342736 | 0.670852 |
| context_output_json_bytes | 48 / 0 | 22904.1 | 22874.5 | 23198 | 22569 | 23228 |
| context_estimated_planning_tokens | 48 / 0 | 7908.21 | 7896 | 8000 | 7816 | 8000 |
| context_returned_file_count | 48 / 0 | 16.625 | 17 | 18 | 14 | 18 |
| context_returned_item_count | 48 / 0 | 16.625 | 17 | 18 | 14 | 18 |
| context_declared_file_precision | 48 / 0 | 0.18724 | 0.2 | 0.25 | 0.111111 | 0.266667 |
| required_file_recall | 48 / 0 | 0.902778 | 1 | 1 | 0.666667 | 1 |
| primary_complete_body_coverage | 48 / 0 | 1 | 1 | 1 | 1 | 1 |
| required_dependency_complete_body_recall | 48 / 0 | 0.8125 | 1 | 1 | 0.5 | 1 |
| all_required_bodies_present | 48 / 0 | 0.625 | 1 | 1 | 0 | 1 |

### Strategy: refined

Status counts: `{"ok": 48}`.

| Metric | n / missing | Mean | Median | p95 | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| primary_file_rank | 48 / 0 | 5.75 | 6 | 12 | 1 | 12 |
| primary_file_hit_at_1 | 48 / 0 | 0.333333 | 0 | 1 | 0 | 1 |
| primary_file_reciprocal_rank | 48 / 0 | 0.423001 | 0.166667 | 1 | 0.0833333 | 1 |
| search_wall_seconds | 48 / 0 | 0.21919 | 0.208494 | 0.275786 | 0.177969 | 0.427361 |
| search_process_cpu_seconds | 48 / 0 | 0.218409 | 0.208397 | 0.272436 | 0.177615 | 0.427323 |
| context_wall_seconds | 48 / 0 | 0.237847 | 0.220724 | 0.324656 | 0.166857 | 0.764068 |
| context_process_cpu_seconds | 48 / 0 | 0.217131 | 0.20648 | 0.306962 | 0.148056 | 0.597453 |
| search_plus_context_wall_seconds | 48 / 0 | 0.457036 | 0.433751 | 0.580621 | 0.363233 | 1.03276 |
| context_output_json_bytes | 48 / 0 | 22904.1 | 22874.5 | 23198 | 22569 | 23228 |
| context_estimated_planning_tokens | 48 / 0 | 7908.21 | 7896 | 8000 | 7816 | 8000 |
| context_returned_file_count | 48 / 0 | 16.625 | 17 | 18 | 14 | 18 |
| context_returned_item_count | 48 / 0 | 16.625 | 17 | 18 | 14 | 18 |
| context_declared_file_precision | 48 / 0 | 0.18724 | 0.2 | 0.25 | 0.111111 | 0.266667 |
| required_file_recall | 48 / 0 | 0.902778 | 1 | 1 | 0.666667 | 1 |
| primary_complete_body_coverage | 48 / 0 | 1 | 1 | 1 | 1 | 1 |
| required_dependency_complete_body_recall | 48 / 0 | 0.8125 | 1 | 1 | 0.5 | 1 |
| all_required_bodies_present | 48 / 0 | 0.625 | 1 | 1 | 0 | 1 |

| Strategy | Query | Repeat | Status | Required files | Complete primary body | Complete declared dependencies | Returned files | Errors |
|---|---|---:|---|---:|---:|---:|---:|---|
| refined | meridian-python-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| legacy | meridian-python-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-media-extend | 1 | ok | 1 | 1 | 0.5 | 14 | [] |
| legacy | meridian-python-media-extend | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-python-media-extend | 1 | ok | 1 | 1 | 0.5 | 14 | [] |
| legacy | meridian-python-media-revoke | 1 | ok | 0.333333 | 1 | 0 | 21 | [] |
| refined | meridian-python-media-revoke | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-python-media-revoke | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| refined | meridian-python-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| legacy | meridian-python-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-appointments-extend | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-python-appointments-extend | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-python-appointments-extend | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-python-appointments-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-python-appointments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-python-appointments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-python-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| legacy | meridian-python-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-specimens-extend | 1 | ok | 1 | 1 | 0.5 | 14 | [] |
| legacy | meridian-python-specimens-extend | 1 | ok | 0 | 0 | 0 | 22 | [] |
| refined | meridian-python-specimens-extend | 1 | ok | 1 | 1 | 0.5 | 14 | [] |
| legacy | meridian-python-specimens-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-python-specimens-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-python-specimens-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-python-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| legacy | meridian-python-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-deployments-extend | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-python-deployments-extend | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-python-deployments-extend | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-python-deployments-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-python-deployments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-python-deployments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-python-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| refined | meridian-python-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| refined | meridian-python-media-extend | 2 | ok | 1 | 1 | 0.5 | 14 | [] |
| legacy | meridian-python-media-extend | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| previous | meridian-python-media-extend | 2 | ok | 1 | 1 | 0.5 | 14 | [] |
| previous | meridian-python-media-revoke | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| refined | meridian-python-media-revoke | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| legacy | meridian-python-media-revoke | 2 | ok | 0.333333 | 1 | 0 | 21 | [] |
| legacy | meridian-python-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-appointments-extend | 2 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-python-appointments-extend | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| previous | meridian-python-appointments-extend | 2 | ok | 1 | 1 | 1 | 15 | [] |
| previous | meridian-python-appointments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-python-appointments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-python-appointments-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| legacy | meridian-python-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 16 | [] |
| previous | meridian-python-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-specimens-extend | 2 | ok | 1 | 1 | 0.5 | 14 | [] |
| legacy | meridian-python-specimens-extend | 2 | ok | 0 | 0 | 0 | 22 | [] |
| previous | meridian-python-specimens-extend | 2 | ok | 1 | 1 | 0.5 | 14 | [] |
| previous | meridian-python-specimens-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-python-specimens-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-python-specimens-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| legacy | meridian-python-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-python-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| refined | meridian-python-deployments-extend | 2 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-python-deployments-extend | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| previous | meridian-python-deployments-extend | 2 | ok | 1 | 1 | 1 | 15 | [] |
| previous | meridian-python-deployments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-python-deployments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-python-deployments-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-typescript-media-release | 1 | ok | 1 | 1 | 1 | 15 | [] |
| previous | meridian-typescript-media-release | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-typescript-media-release | 1 | ok | 0.666667 | 1 | 0.5 | 15 | [] |
| previous | meridian-typescript-media-extend | 1 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-media-extend | 1 | ok | 0 | 0 | 0 | 23 | [] |
| refined | meridian-typescript-media-extend | 1 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-media-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-typescript-media-revoke | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-typescript-media-revoke | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| refined | meridian-typescript-appointments-release | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-typescript-appointments-release | 1 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-typescript-appointments-release | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-typescript-appointments-extend | 1 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-appointments-extend | 1 | ok | 0 | 0 | 0 | 23 | [] |
| refined | meridian-typescript-appointments-extend | 1 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-appointments-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-typescript-appointments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-typescript-appointments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-specimens-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| previous | meridian-typescript-specimens-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| legacy | meridian-typescript-specimens-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-specimens-extend | 1 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-specimens-extend | 1 | ok | 0 | 0 | 0 | 23 | [] |
| refined | meridian-typescript-specimens-extend | 1 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-specimens-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-typescript-specimens-revoke | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-typescript-specimens-revoke | 1 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| refined | meridian-typescript-deployments-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| previous | meridian-typescript-deployments-release | 1 | ok | 1 | 1 | 1 | 17 | [] |
| legacy | meridian-typescript-deployments-release | 1 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-deployments-extend | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-typescript-deployments-extend | 1 | ok | 0 | 0 | 0 | 23 | [] |
| refined | meridian-typescript-deployments-extend | 1 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-typescript-deployments-revoke | 1 | ok | 0.333333 | 1 | 0 | 22 | [] |
| refined | meridian-typescript-deployments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| previous | meridian-typescript-deployments-revoke | 1 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-typescript-media-release | 2 | ok | 0.666667 | 1 | 0.5 | 15 | [] |
| previous | meridian-typescript-media-release | 2 | ok | 1 | 1 | 1 | 15 | [] |
| refined | meridian-typescript-media-release | 2 | ok | 1 | 1 | 1 | 15 | [] |
| refined | meridian-typescript-media-extend | 2 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-media-extend | 2 | ok | 0 | 0 | 0 | 23 | [] |
| previous | meridian-typescript-media-extend | 2 | ok | 1 | 1 | 1 | 16 | [] |
| previous | meridian-typescript-media-revoke | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| refined | meridian-typescript-media-revoke | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| legacy | meridian-typescript-media-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| legacy | meridian-typescript-appointments-release | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| previous | meridian-typescript-appointments-release | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-appointments-release | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-appointments-extend | 2 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-appointments-extend | 2 | ok | 0 | 0 | 0 | 23 | [] |
| previous | meridian-typescript-appointments-extend | 2 | ok | 1 | 1 | 1 | 16 | [] |
| previous | meridian-typescript-appointments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-appointments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-typescript-appointments-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| legacy | meridian-typescript-specimens-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-specimens-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-specimens-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-specimens-extend | 2 | ok | 1 | 1 | 1 | 16 | [] |
| legacy | meridian-typescript-specimens-extend | 2 | ok | 0 | 0 | 0 | 23 | [] |
| previous | meridian-typescript-specimens-extend | 2 | ok | 1 | 1 | 1 | 16 | [] |
| previous | meridian-typescript-specimens-revoke | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| refined | meridian-typescript-specimens-revoke | 2 | ok | 0.666667 | 1 | 0.5 | 18 | [] |
| legacy | meridian-typescript-specimens-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |
| legacy | meridian-typescript-deployments-release | 2 | ok | 0.666667 | 1 | 0.5 | 17 | [] |
| previous | meridian-typescript-deployments-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-deployments-release | 2 | ok | 1 | 1 | 1 | 17 | [] |
| refined | meridian-typescript-deployments-extend | 2 | ok | 1 | 1 | 1 | 15 | [] |
| legacy | meridian-typescript-deployments-extend | 2 | ok | 0 | 0 | 0 | 23 | [] |
| previous | meridian-typescript-deployments-extend | 2 | ok | 1 | 1 | 1 | 15 | [] |
| previous | meridian-typescript-deployments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| refined | meridian-typescript-deployments-revoke | 2 | ok | 1 | 1 | 1 | 18 | [] |
| legacy | meridian-typescript-deployments-revoke | 2 | ok | 0.333333 | 1 | 0 | 22 | [] |

## Direct timing source scope

Supplied paired timing experiment; this report does not rerun timings or establish identical performance for later source changes.

Timing-candidate context source matches the SDK candidate: **False**. If false, these direct timings describe an earlier implementation; the separately measured SDK timings describe the new candidate.


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

All SDK regression observations, invalid pairing reasons, complete retrieval observations, direct timing runs and source provenance are retained in the JSON. Declared body recall does not establish semantic completeness. Costs per successful coding task remain unavailable until model usage/cost and external coding grades are actually measured.
