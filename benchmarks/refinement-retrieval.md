# Fresh procedural retrieval validation

24 locked retrieval tasks across Python/TypeScript, four domains and two 85+ file synthetic repositories, with ambiguous identifiers and docs/tests/read-model overlap. Exact source bodies and two declared direct dependency implementations are judged independently of declaration visibility.

No model calls, coding-task outcomes, billed tokens or costs are measured here. Context bytes are measured; planning tokens remain an engine estimate.

All candidates share the current context packer. Previous means frozen shipped b51a262 ranking and legacy means frozen 39e8df3 ranking, not either complete former service. The holdout validates a previously frozen choice; it does not select or tune the default.

Report status: valid

| Policy | Valid/planned | File hit@1 | Complete primary body | Declared dependency body recall | All required bodies | Declared file precision | Mean files | Mean JSON bytes | Packing p50/p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| refined | 48/48 | 33.3% | 66.7% | 41.7% | 33.3% | 14.0% | 10.25 | 17568.75 | 188.53/317.09 |
| previous | 48/48 | 33.3% | 66.7% | 41.7% | 33.3% | 14.0% | 10.25 | 17568.75 | 213.28/406.57 |
| legacy | 48/48 | 8.3% | 79.2% | 62.5% | 45.8% | 22.4% | 10.62 | 16551.04 | 104.68/310.74 |

## Every individual observation

| Query | Repeat | Policy | Status | Complete primary | Dependency recall | Declared precision | Files | Bytes |
|---|---:|---|---|---:|---:|---:|---:|---:|
| meridian-python-media-release | 1 | refined | ok | 1 | 0.5 | 0.125 | 16 | 23198 |
| meridian-python-media-release | 1 | previous | ok | 1 | 0.5 | 0.125 | 16 | 23198 |
| meridian-python-media-release | 1 | legacy | ok | 1 | 0.5 | 0.125 | 16 | 23042 |
| meridian-python-media-extend | 1 | previous | ok | 1 | 0.0 | 0.3 | 10 | 23129 |
| meridian-python-media-extend | 1 | legacy | ok | 1 | 1.0 | 0.3 | 10 | 17459 |
| meridian-python-media-extend | 1 | refined | ok | 1 | 0.0 | 0.3 | 10 | 23129 |
| meridian-python-media-revoke | 1 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 19719 |
| meridian-python-media-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6774 |
| meridian-python-media-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6774 |
| meridian-python-appointments-release | 1 | refined | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22776 |
| meridian-python-appointments-release | 1 | previous | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22776 |
| meridian-python-appointments-release | 1 | legacy | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22846 |
| meridian-python-appointments-extend | 1 | previous | ok | 1 | 1.0 | 0.3 | 10 | 23127 |
| meridian-python-appointments-extend | 1 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11249 |
| meridian-python-appointments-extend | 1 | refined | ok | 1 | 1.0 | 0.3 | 10 | 23127 |
| meridian-python-appointments-revoke | 1 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11261 |
| meridian-python-appointments-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6587 |
| meridian-python-appointments-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6587 |
| meridian-python-specimens-release | 1 | refined | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 23057 |
| meridian-python-specimens-release | 1 | previous | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 23057 |
| meridian-python-specimens-release | 1 | legacy | ok | 1 | 0.5 | 0.125 | 16 | 22725 |
| meridian-python-specimens-extend | 1 | previous | ok | 1 | 0.0 | 0.1 | 10 | 23140 |
| meridian-python-specimens-extend | 1 | legacy | ok | 0 | 0.0 | 0.0 | 10 | 17316 |
| meridian-python-specimens-extend | 1 | refined | ok | 1 | 0.0 | 0.1 | 10 | 23140 |
| meridian-python-specimens-revoke | 1 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 19723 |
| meridian-python-specimens-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6586 |
| meridian-python-specimens-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6586 |
| meridian-python-deployments-release | 1 | refined | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22850 |
| meridian-python-deployments-release | 1 | previous | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22850 |
| meridian-python-deployments-release | 1 | legacy | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22926 |
| meridian-python-deployments-extend | 1 | previous | ok | 1 | 1.0 | 0.3 | 10 | 23128 |
| meridian-python-deployments-extend | 1 | legacy | ok | 1 | 1.0 | 0.375 | 8 | 14664 |
| meridian-python-deployments-extend | 1 | refined | ok | 1 | 1.0 | 0.3 | 10 | 23128 |
| meridian-python-deployments-revoke | 1 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11248 |
| meridian-python-deployments-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6616 |
| meridian-python-deployments-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6616 |
| meridian-python-media-release | 2 | legacy | ok | 1 | 0.5 | 0.125 | 16 | 23042 |
| meridian-python-media-release | 2 | previous | ok | 1 | 0.5 | 0.125 | 16 | 23198 |
| meridian-python-media-release | 2 | refined | ok | 1 | 0.5 | 0.125 | 16 | 23198 |
| meridian-python-media-extend | 2 | refined | ok | 1 | 0.0 | 0.3 | 10 | 23129 |
| meridian-python-media-extend | 2 | legacy | ok | 1 | 1.0 | 0.3 | 10 | 17459 |
| meridian-python-media-extend | 2 | previous | ok | 1 | 0.0 | 0.3 | 10 | 23129 |
| meridian-python-media-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6774 |
| meridian-python-media-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6774 |
| meridian-python-media-revoke | 2 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 19719 |
| meridian-python-appointments-release | 2 | legacy | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22846 |
| meridian-python-appointments-release | 2 | previous | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22776 |
| meridian-python-appointments-release | 2 | refined | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22776 |
| meridian-python-appointments-extend | 2 | refined | ok | 1 | 1.0 | 0.3 | 10 | 23127 |
| meridian-python-appointments-extend | 2 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11249 |
| meridian-python-appointments-extend | 2 | previous | ok | 1 | 1.0 | 0.3 | 10 | 23127 |
| meridian-python-appointments-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6587 |
| meridian-python-appointments-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6587 |
| meridian-python-appointments-revoke | 2 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11261 |
| meridian-python-specimens-release | 2 | legacy | ok | 1 | 0.5 | 0.125 | 16 | 22725 |
| meridian-python-specimens-release | 2 | previous | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 23057 |
| meridian-python-specimens-release | 2 | refined | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 23057 |
| meridian-python-specimens-extend | 2 | refined | ok | 1 | 0.0 | 0.1 | 10 | 23140 |
| meridian-python-specimens-extend | 2 | legacy | ok | 0 | 0.0 | 0.0 | 10 | 17316 |
| meridian-python-specimens-extend | 2 | previous | ok | 1 | 0.0 | 0.1 | 10 | 23140 |
| meridian-python-specimens-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6586 |
| meridian-python-specimens-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6586 |
| meridian-python-specimens-revoke | 2 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 19723 |
| meridian-python-deployments-release | 2 | legacy | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22926 |
| meridian-python-deployments-release | 2 | previous | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22850 |
| meridian-python-deployments-release | 2 | refined | ok | 1 | 0.5 | 0.11764705882352941 | 17 | 22850 |
| meridian-python-deployments-extend | 2 | refined | ok | 1 | 1.0 | 0.3 | 10 | 23128 |
| meridian-python-deployments-extend | 2 | legacy | ok | 1 | 1.0 | 0.375 | 8 | 14664 |
| meridian-python-deployments-extend | 2 | previous | ok | 1 | 1.0 | 0.3 | 10 | 23128 |
| meridian-python-deployments-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6616 |
| meridian-python-deployments-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6616 |
| meridian-python-deployments-revoke | 2 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11248 |
| meridian-typescript-media-release | 1 | refined | ok | 1 | 1.0 | 0.2 | 15 | 22812 |
| meridian-typescript-media-release | 1 | previous | ok | 1 | 1.0 | 0.2 | 15 | 22812 |
| meridian-typescript-media-release | 1 | legacy | ok | 1 | 0.5 | 0.2 | 15 | 22895 |
| meridian-typescript-media-extend | 1 | previous | ok | 1 | 0.0 | 0.1 | 10 | 23010 |
| meridian-typescript-media-extend | 1 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 6993 |
| meridian-typescript-media-extend | 1 | refined | ok | 1 | 0.0 | 0.1 | 10 | 23010 |
| meridian-typescript-media-revoke | 1 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 20210 |
| meridian-typescript-media-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6809 |
| meridian-typescript-media-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6809 |
| meridian-typescript-appointments-release | 1 | refined | ok | 1 | 1.0 | 0.2222222222222222 | 18 | 23125 |
| meridian-typescript-appointments-release | 1 | previous | ok | 1 | 1.0 | 0.2222222222222222 | 18 | 23125 |
| meridian-typescript-appointments-release | 1 | legacy | ok | 1 | 0.5 | 0.16666666666666666 | 18 | 22827 |
| meridian-typescript-appointments-extend | 1 | previous | ok | 1 | 1.0 | 0.4 | 10 | 23026 |
| meridian-typescript-appointments-extend | 1 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 7161 |
| meridian-typescript-appointments-extend | 1 | refined | ok | 1 | 1.0 | 0.4 | 10 | 23026 |
| meridian-typescript-appointments-revoke | 1 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11233 |
| meridian-typescript-appointments-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6788 |
| meridian-typescript-appointments-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6788 |
| meridian-typescript-specimens-release | 1 | refined | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22804 |
| meridian-typescript-specimens-release | 1 | previous | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22804 |
| meridian-typescript-specimens-release | 1 | legacy | ok | 1 | 0.5 | 0.17647058823529413 | 17 | 22939 |
| meridian-typescript-specimens-extend | 1 | previous | ok | 1 | 0.0 | 0.1 | 10 | 23012 |
| meridian-typescript-specimens-extend | 1 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 7093 |
| meridian-typescript-specimens-extend | 1 | refined | ok | 1 | 0.0 | 0.1 | 10 | 23012 |
| meridian-typescript-specimens-revoke | 1 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 20214 |
| meridian-typescript-specimens-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6813 |
| meridian-typescript-specimens-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6813 |
| meridian-typescript-deployments-release | 1 | refined | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22643 |
| meridian-typescript-deployments-release | 1 | previous | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22643 |
| meridian-typescript-deployments-release | 1 | legacy | ok | 1 | 0.5 | 0.17647058823529413 | 17 | 23111 |
| meridian-typescript-deployments-extend | 1 | previous | ok | 1 | 1.0 | 0.4 | 10 | 23038 |
| meridian-typescript-deployments-extend | 1 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 7151 |
| meridian-typescript-deployments-extend | 1 | refined | ok | 1 | 1.0 | 0.4 | 10 | 23038 |
| meridian-typescript-deployments-revoke | 1 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11220 |
| meridian-typescript-deployments-revoke | 1 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6802 |
| meridian-typescript-deployments-revoke | 1 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6802 |
| meridian-typescript-media-release | 2 | legacy | ok | 1 | 0.5 | 0.2 | 15 | 22895 |
| meridian-typescript-media-release | 2 | previous | ok | 1 | 1.0 | 0.2 | 15 | 22812 |
| meridian-typescript-media-release | 2 | refined | ok | 1 | 1.0 | 0.2 | 15 | 22812 |
| meridian-typescript-media-extend | 2 | refined | ok | 1 | 0.0 | 0.1 | 10 | 23010 |
| meridian-typescript-media-extend | 2 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 6993 |
| meridian-typescript-media-extend | 2 | previous | ok | 1 | 0.0 | 0.1 | 10 | 23010 |
| meridian-typescript-media-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6809 |
| meridian-typescript-media-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6809 |
| meridian-typescript-media-revoke | 2 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 20210 |
| meridian-typescript-appointments-release | 2 | legacy | ok | 1 | 0.5 | 0.16666666666666666 | 18 | 22827 |
| meridian-typescript-appointments-release | 2 | previous | ok | 1 | 1.0 | 0.2222222222222222 | 18 | 23125 |
| meridian-typescript-appointments-release | 2 | refined | ok | 1 | 1.0 | 0.2222222222222222 | 18 | 23125 |
| meridian-typescript-appointments-extend | 2 | refined | ok | 1 | 1.0 | 0.4 | 10 | 23026 |
| meridian-typescript-appointments-extend | 2 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 7161 |
| meridian-typescript-appointments-extend | 2 | previous | ok | 1 | 1.0 | 0.4 | 10 | 23026 |
| meridian-typescript-appointments-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6788 |
| meridian-typescript-appointments-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6788 |
| meridian-typescript-appointments-revoke | 2 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11233 |
| meridian-typescript-specimens-release | 2 | legacy | ok | 1 | 0.5 | 0.17647058823529413 | 17 | 22939 |
| meridian-typescript-specimens-release | 2 | previous | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22804 |
| meridian-typescript-specimens-release | 2 | refined | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22804 |
| meridian-typescript-specimens-extend | 2 | refined | ok | 1 | 0.0 | 0.1 | 10 | 23012 |
| meridian-typescript-specimens-extend | 2 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 7093 |
| meridian-typescript-specimens-extend | 2 | previous | ok | 1 | 0.0 | 0.1 | 10 | 23012 |
| meridian-typescript-specimens-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6813 |
| meridian-typescript-specimens-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6813 |
| meridian-typescript-specimens-revoke | 2 | legacy | ok | 1 | 1.0 | 0.25 | 12 | 20214 |
| meridian-typescript-deployments-release | 2 | legacy | ok | 1 | 0.5 | 0.17647058823529413 | 17 | 23111 |
| meridian-typescript-deployments-release | 2 | previous | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22643 |
| meridian-typescript-deployments-release | 2 | refined | ok | 1 | 1.0 | 0.23529411764705882 | 17 | 22643 |
| meridian-typescript-deployments-extend | 2 | refined | ok | 1 | 1.0 | 0.4 | 10 | 23038 |
| meridian-typescript-deployments-extend | 2 | legacy | ok | 0 | 0.0 | 0.0 | 4 | 7151 |
| meridian-typescript-deployments-extend | 2 | previous | ok | 1 | 1.0 | 0.4 | 10 | 23038 |
| meridian-typescript-deployments-revoke | 2 | previous | ok | 0 | 0.0 | 0.0 | 4 | 6802 |
| meridian-typescript-deployments-revoke | 2 | refined | ok | 0 | 0.0 | 0.0 | 4 | 6802 |
| meridian-typescript-deployments-revoke | 2 | legacy | ok | 1 | 1.0 | 0.5 | 6 | 11220 |

## Failures

No runner errors. Complete-body misses remain visible in every observation and the JSON evidence; an error-free run does not imply sufficient context.

## Limitations

- Authored independently of Atlas/Orion task prompts and frozen before any candidate evaluation. Visible synthetic fixtures with paired language structure are a procedural holdout, not a secret test or a representative sample of production repositories.
- Two language fixtures mirror the same twelve intents, so observations are correlated. Repeats measure variability, not extra independent tasks.
- Complete body means exact fixture lines; declared dependency coverage excludes transitive and language/runtime dependencies and does not prove semantic task sufficiency.
- Declared precision uses explicit fixture-scope positives; documentation or tests can be useful to a real coding task despite falling outside this task's source-implementation judgment.
- Search uses an already indexed immutable fixture with refresh=False. Packing excludes initial ranking and session creation/cleanup. Shared local caches are not flushed; cold startup is not measured.
- Current-process CPU excludes parser workers. No exact physical file-read count, sampled memory overhead, model usage or billed cost is available from this local runner.
- After first evaluation this corpus becomes seen validation. Any subsequent evaluation must disclose reuse, and tuning requires a separately authored fresh holdout.

## Freeze and provenance

```json
{
  "manifest_sha256": "04e0825f818ebafcb037cddad2396e7df12203d5891e588c34afadf3bc10d37c",
  "original_protocol_sha256": "438597dbd230eca58def89e478b542d154da2b49316258182c1fd0f04d84ae51",
  "protocol_sha256": "070daffd810a4bba7016e68a248932b8033ed6e4915325b67f0641df2b5228b2",
  "source_before": {
    "captured_at": "2026-10-17T19:37:48.860988+00:00",
    "attestation": "captured_source_state_before_probe",
    "git_head": "b51a26234656c647f12da3ad63d8bc1fe9380c58",
    "source_dirty_entries": [
      " M src/memglide/api/app.py",
      " M src/memglide/core/context.py",
      " M src/memglide/core/indexer.py",
      " M src/memglide/core/query.py",
      " M src/memglide/memory/engine.py",
      " M src/memglide/service.py",
      " M src/memglide/storage/database.py"
    ],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "11729dc77f84f912d2b0e2998ce885b45e28c7c0330925dc48f1af15dc1a5fb4",
      "src/memglide/cli.py": "0a4cc01bafe7e2d2c43171984fa05c01cafeeba113a432d5f62706560a1d3989",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/context.py": "9151092fa3833fdb40effb04807010f2494a94a2ad39b2f6378e17227c15fd82",
      "src/memglide/core/indexer.py": "3e278aeafd0ba515308df71ac80816b7638d6d636ff3377ed1bd5081b3c2ae32",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "1d3f015454fd096ced74f6239ada586ba77490738cf62697e676157fe843152c",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "99e3d527187cfc457b4c574a1127a1c6fb738db6b4d4e9a7f8a42c56d5879d76",
      "src/memglide/integrations/mcp_server.py": "80f1ed60fcfd7951ced1f7b957c46661c71fe8eac3cb8bd1eb62c5b75c99dff8",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "82ff4f79c32dd2281026057098c9cffb872038640fa5ac387b1bd1ab6a5ab1d1",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "6dd6f33a5adc3863ff68d6125296c84c32170085c9c20eb53c8809f02a4c2a7b",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "38a483c6e05758a8f7df743ce7965a0fe20b6ea5f13c4921788b61efa971f58e"
    },
    "source_tree_sha256": "c966edd662ca7d9d20c9f48d3bdaabfd35427c809c4e8f6fb917d00617c5dc99",
    "measurement_files": {
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0",
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state"
  },
  "source_after": {
    "captured_at": "2026-10-17T19:39:10.213822+00:00",
    "attestation": "captured_source_state_before_probe",
    "git_head": "b51a26234656c647f12da3ad63d8bc1fe9380c58",
    "source_dirty_entries": [
      " M src/memglide/api/app.py",
      " M src/memglide/core/context.py",
      " M src/memglide/core/indexer.py",
      " M src/memglide/core/query.py",
      " M src/memglide/memory/engine.py",
      " M src/memglide/service.py",
      " M src/memglide/storage/database.py"
    ],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "11729dc77f84f912d2b0e2998ce885b45e28c7c0330925dc48f1af15dc1a5fb4",
      "src/memglide/cli.py": "0a4cc01bafe7e2d2c43171984fa05c01cafeeba113a432d5f62706560a1d3989",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/context.py": "9151092fa3833fdb40effb04807010f2494a94a2ad39b2f6378e17227c15fd82",
      "src/memglide/core/indexer.py": "3e278aeafd0ba515308df71ac80816b7638d6d636ff3377ed1bd5081b3c2ae32",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "1d3f015454fd096ced74f6239ada586ba77490738cf62697e676157fe843152c",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "99e3d527187cfc457b4c574a1127a1c6fb738db6b4d4e9a7f8a42c56d5879d76",
      "src/memglide/integrations/mcp_server.py": "80f1ed60fcfd7951ced1f7b957c46661c71fe8eac3cb8bd1eb62c5b75c99dff8",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "82ff4f79c32dd2281026057098c9cffb872038640fa5ac387b1bd1ab6a5ab1d1",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "6dd6f33a5adc3863ff68d6125296c84c32170085c9c20eb53c8809f02a4c2a7b",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "38a483c6e05758a8f7df743ce7965a0fe20b6ea5f13c4921788b61efa971f58e"
    },
    "source_tree_sha256": "c966edd662ca7d9d20c9f48d3bdaabfd35427c809c4e8f6fb917d00617c5dc99",
    "measurement_files": {
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0",
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state"
  },
  "source_unchanged_during_evaluation": true,
  "measurement_files_before": {
    "benchmarks/refinement_corpus.py": "0c0237bd627b417eece59ff43f1b1ed3a16158e332e52d411fede88cedd7cbc2",
    "benchmarks/refinement_holdout.json": "04e0825f818ebafcb037cddad2396e7df12203d5891e588c34afadf3bc10d37c",
    "benchmarks/refinement_protocol.json": "070daffd810a4bba7016e68a248932b8033ed6e4915325b67f0641df2b5228b2",
    "benchmarks/refinement_eval.py": "8e9c6308d7534cdfcc3f787a0d3ca83648f99874a914b08b9b8ddd89311411b9"
  },
  "measurement_files_after": {
    "benchmarks/refinement_corpus.py": "0c0237bd627b417eece59ff43f1b1ed3a16158e332e52d411fede88cedd7cbc2",
    "benchmarks/refinement_holdout.json": "04e0825f818ebafcb037cddad2396e7df12203d5891e588c34afadf3bc10d37c",
    "benchmarks/refinement_protocol.json": "070daffd810a4bba7016e68a248932b8033ed6e4915325b67f0641df2b5228b2",
    "benchmarks/refinement_eval.py": "8e9c6308d7534cdfcc3f787a0d3ca83648f99874a914b08b9b8ddd89311411b9"
  },
  "measurement_unchanged_during_evaluation": true,
  "frozen_ranker_sources": {
    "legacy": {
      "revision": "39e8df30565783a686270f8a6f422e56e41e3776",
      "indexer_sha256": "4f350ffa31207a448b0d5ae16006b32482fa80fb1bdce7030e8454c907adc99f",
      "query_sha256": null
    },
    "previous": {
      "revision": "b51a26234656c647f12da3ad63d8bc1fe9380c58",
      "indexer_sha256": "d71181f44519883c93dafab1df7b0ce5587c61d0e242b52a4187e6e15df60f7f",
      "query_sha256": "781f44a138491a23c1283feb54f0ff6ab83b20264bc658d9776f4518b9b85567"
    }
  },
  "fixtures": {
    "meridian-python-refinement-v1": {
      "commit": "bd76198db55c2afed44953878d1147fef26edccb",
      "file_count": 86,
      "source_utf8_bytes": 48713,
      "index_stats": {
        "project_id": "fef7c9d3c98847f384c825234aae823f",
        "indexed": 86,
        "unchanged": 0,
        "deleted": 0,
        "file_count": 86,
        "symbol_count": 196,
        "search_index_version": 3,
        "search_index_refreshed": 0,
        "languages": {
          "python": 73,
          "text": 13
        },
        "ignored": 1,
        "ignored_files": [
          {
            "path": ".git/",
            "reason": "default ignored directory"
          }
        ],
        "errors": [],
        "partial": false,
        "limits": {
          "max_files": 20000,
          "max_total_bytes": 104857600
        },
        "branch": "master",
        "git_state": {
          "branch": "master",
          "dirty": false,
          "changes": [],
          "head": "bd76198db55c2afed44953878d1147fef26edccb"
        }
      }
    },
    "meridian-typescript-refinement-v1": {
      "commit": "9fa9c1e0e06a978e169c5ea62c7d89922adcc89e",
      "file_count": 85,
      "source_utf8_bytes": 42704,
      "index_stats": {
        "project_id": "15241b64b0684f55bc8b026bd528ec71",
        "indexed": 85,
        "unchanged": 0,
        "deleted": 0,
        "file_count": 85,
        "symbol_count": 196,
        "search_index_version": 3,
        "search_index_refreshed": 0,
        "languages": {
          "text": 13,
          "typescript": 72
        },
        "ignored": 1,
        "ignored_files": [
          {
            "path": ".git/",
            "reason": "default ignored directory"
          }
        ],
        "errors": [],
        "partial": false,
        "limits": {
          "max_files": 20000,
          "max_total_bytes": 104857600
        },
        "branch": "master",
        "git_state": {
          "branch": "master",
          "dirty": false,
          "changes": [],
          "head": "9fa9c1e0e06a978e169c5ea62c7d89922adcc89e"
        }
      }
    }
  },
  "pre_evaluation_lock": {
    "locked_at_utc": "2026-10-17T19:37:48.862527+00:00",
    "manifest_sha256": "04e0825f818ebafcb037cddad2396e7df12203d5891e588c34afadf3bc10d37c",
    "original_protocol_sha256": "438597dbd230eca58def89e478b542d154da2b49316258182c1fd0f04d84ae51",
    "protocol_sha256": "070daffd810a4bba7016e68a248932b8033ed6e4915325b67f0641df2b5228b2",
    "source_tree_sha256": "c966edd662ca7d9d20c9f48d3bdaabfd35427c809c4e8f6fb917d00617c5dc99",
    "freeze_note": "Root froze production ranking and packing before first Meridian evaluation. Selection on seen Atlas only: query focus plus source-role ranking; level 2 maximum four primary files preserving exact anchors and dependency expansion. Development refined hit@1 0.5 / MRR 0.75 versus previous 0.25 / 0.4597 and legacy 0.3333 / 0.5453, with full declared target/declaration coverage. No further tuning permitted from this holdout.",
    "validation_reuse_reason": null,
    "measurement_files_sha256": {
      "benchmarks/refinement_corpus.py": "0c0237bd627b417eece59ff43f1b1ed3a16158e332e52d411fede88cedd7cbc2",
      "benchmarks/refinement_holdout.json": "04e0825f818ebafcb037cddad2396e7df12203d5891e588c34afadf3bc10d37c",
      "benchmarks/refinement_protocol.json": "070daffd810a4bba7016e68a248932b8033ed6e4915325b67f0641df2b5228b2",
      "benchmarks/refinement_eval.py": "8e9c6308d7534cdfcc3f787a0d3ca83648f99874a914b08b9b8ddd89311411b9"
    }
  },
  "raw_artifacts": "/workspace/Memglide/.local/refinement-fresh-v1"
}
```
