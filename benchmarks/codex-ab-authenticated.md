# Memglide Codex A/B benchmark

Observed results are descriptive. Assess task success, full cost coverage, treatment fidelity, sample size, cache order, and task representativeness before claiming savings.

A = standard Codex. B = same Codex settings with Memglide. Success is determined by the external grader. Missing measurements are `unavailable`, not zero.

## Protocol and environment

```json
{
  "codex_version": "codex-cli 0.159.2",
  "finished_at": "2026-10-17T22:16:41.322938+00:00",
  "measurement_sha256": {
    "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
    "benchmarks/reporting.py": "723fcd5529dc7b3b52d4fdddec4692a9399faa0e864a6b7fcde26f824136f0fc",
    "benchmarks/run.py": "ccf8d44ca7ea8286a8a9241b030eaa76ca339ec15032aeb95cb4e256ef500a26",
    "benchmarks/tasks.json": "5a921674ff669ebe09af08c06b9bb95ea597ff051ddcddb3312ce9508affe185",
    "benchmarks/telemetry.py": "0cf7a4fae8973f9cb771129e71c11c2b3e0d03106cdc5a41eed6698f32460fe7"
  },
  "memglide_source_after": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-17T22:16:41.349239+00:00",
    "git_head": "12ade2381b25412fff41a3348aadf34a8c824715",
    "measurement_files": {
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state",
    "source_dirty_entries": [],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "11729dc77f84f912d2b0e2998ce885b45e28c7c0330925dc48f1af15dc1a5fb4",
      "src/memglide/cli.py": "0a4cc01bafe7e2d2c43171984fa05c01cafeeba113a432d5f62706560a1d3989",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/context.py": "fab6d35379a7e865e433289a1bf64fb23832d306369df9e9a348c2da460d20b3",
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
    "source_tree_sha256": "20cc181bc45cecacc6e96f40e4a470112dd1581212eac7acece46c44f7270454"
  },
  "memglide_source_before": {
    "attestation": "Prelaunch manifest retained the commit and aggregate source hash; original in-memory detailed metadata was lost on disconnect",
    "git_head": "12ade2381b25412fff41a3348aadf34a8c824715",
    "source_tree_sha256": "20cc181bc45cecacc6e96f40e4a470112dd1581212eac7acece46c44f7270454"
  },
  "methodology": {
    "caching": "Counterbalanced ordering across repeats. Provider and OS caches not flushable; cached tokens recorded. Execution interruption adds a disclosed pause before order91.",
    "cost": "Provider billed cost/model-call counts unavailable; remain null",
    "failed_runs": "Original interruption retained in96 planned rows; no silent retries or replacement",
    "isolation": "Fresh detached worktrees from unchanged per-language seed commit; new state/index per B run",
    "prompt": "Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.\nIf memglide MCP tools are available, use list_projects, start_session and get_context before editing, inspect the source evidence you need, and revalidate the Context Passport after edits. Otherwise use ordinary source tools. Do not claim token or cost savings.\n",
    "repositories": "Two synthetic multi-module Python/TypeScript fixtures, 24 IDs representing12 mirrored intents; external hidden oracles",
    "settings": "Same model/effort/schema/sandbox/instructions, only B required scoped Memglide MCP configuration differs",
    "timing": "Codex process plus B fresh-index timing; excludes grader and worktree preparation. Run90 timing unavailable after interruption."
  },
  "model": "gpt-6.1-sol",
  "output_directory": "/workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1",
  "preflight_runs": [
    {
      "artifacts": "/workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/preflight",
      "exit_code": null,
      "scope": "Original readiness call, excluded from task comparisons. Reparsed raw usage; original process timing/exit metadata lost on disconnect.",
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": 0,
        "commands": [],
        "completed_turns": 1,
        "errors": [],
        "event_count": 4,
        "failed_turns": 0,
        "file_read_method": "Heuristic command-intent proxy from successful command_execution items containing literal cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, scripts, directory searches, MCP reads, and internal reads are excluded. A repeated command names a path recognized in an earlier command. This is not an I/O trace, an actual read count, or a guaranteed lower bound on filesystem reads.",
        "file_reads_complete": false,
        "mcp_call_count": 0,
        "mcp_calls": [],
        "mcp_count_scope": "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound",
        "mcp_counts_complete": true,
        "memglide_get_context_success_unknown_count": 0,
        "memglide_mcp_call_count": 0,
        "memglide_successful_get_context_count": 0,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": 0,
          "input_tokens": 10945,
          "output_tokens": 42
        },
        "observed_file_read_commands": 0,
        "observed_read_command_paths": [],
        "observed_repeated_read_commands": 0,
        "parse_errors": [],
        "repeated_file_reads": null,
        "repeated_file_reads_unavailable_reason": "Codex JSONL does not expose a filesystem I/O trace; command text cannot establish actual reads",
        "repeated_read_command_paths": {},
        "source": "codex exec --json; turn.completed usage and item lifecycle events",
        "stream_terminal": true,
        "usage": {
          "cached_input_tokens": 0,
          "input_tokens": 10945,
          "output_tokens": 42
        },
        "usage_coverage_complete": true,
        "usage_scope": "Complete parsed stream only; partial observed turn usage is stored separately",
        "usage_unavailable_reasons": {}
      },
      "wall_time_seconds": null
    }
  ],
  "random_seed": 20261016,
  "reasoning_effort": "low",
  "recovery": {
    "continuation_orders": [
      91,
      92,
      93,
      94,
      95,
      96
    ],
    "interrupted_run_id": "ts-lru-eviction-r2-B",
    "last_completed_order": 96,
    "metadata_limitations": "Original metadata was only written after all runs; its in-memory start timestamp and host snapshot were lost. Current host metadata below is a recovery-time observation. No reconstructed timestamp, timing, exit code or CPU value is presented as a measurement.",
    "observed_at": "2026-10-17T22:13:50.421115+00:00",
    "original_checkpoint_sha256": "e31733b9ec85cefa8a09e4f5b5fb005158657eb7e84b8ce0f4b790fc091bf873",
    "original_completed_checkpoint_count": 89,
    "policy": "No original run is replaced. Original run90 remains an interrupted attempt in the main96. Continue remaining six original assignments using unchanged run_task and existing commits/schema/settings. Any later retry is separate supplemental evidence.",
    "recovery_host": {
      "cgroup_v2_limits": {
        "cpu.max": "400000 100000",
        "memory.max": "34359738368",
        "memory.swap.max": "max",
        "pids.max": "max"
      },
      "cpu_affinity_count": 5,
      "logical_cpu_count": 5,
      "resource_scope": "Local execution host; model inference resources are not exposed",
      "tool_versions": {
        "git": "git version 2.52.0",
        "node": "v24.19.0",
        "npm": "11.9.0",
        "python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]"
      }
    }
  },
  "repeats": 2,
  "repetitions": 2,
  "repositories": {
    "python": {
      "commit": "b59bc4bd500f08bd043860ae105db5612434b3d7",
      "path": "/workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/repositories/python"
    },
    "typescript": {
      "commit": "064e2cb7a6f8ede292c7d4fcd2c9829757c2c97a",
      "path": "/workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/repositories/typescript"
    }
  },
  "source_snapshot_scope": "Prelaunch recorded aggregate matches recovery/end snapshot. This is not continuous runtime attestation.",
  "source_unchanged_during_experiment": true,
  "started_at": null
}
```

## Overall results (all runs)

| Measure | A | B |
| --- | ---: | ---: |
| Planned runs | 48 | 48 |
| Attempted runs | 48 | 48 |
| Not run | 0 | 0 |
| Graded runs | 48 | 47 |
| Successful runs | 48 | 47 |
| Failed grades | 0 | 0 |
| Ungraded attempts | 0 | 1 |
| Task completion rate | 1 | 0.979167 |
| Invalid treatment runs | 0 | 0 |
| Unknown treatment runs | 0 | 1 |
| Actual provider cost per success (USD) | unavailable | unavailable |
| Computed pricing cost per success (USD) | unavailable | unavailable |

Cost per success includes all attempted-run costs, including failures. It is unavailable when any attempted-run cost is missing or no task succeeds.

## Measurements

Means/medians include observed values only. Coverage columns show observed n / missing among attempted runs / missing among all planned runs. Totals are withheld when coverage is incomplete and for non-additive metrics.

| Metric | A mean | A median | A n / attempted missing / planned missing | A total | B mean | B median | B n / attempted missing / planned missing | B total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| input_tokens | 54826.3 | 48864.5 | 48 / 0 / 0 | 2631663 | 150409 | 143169 | 47 / 1 / 1 | unavailable |
| cached_input_tokens | 41144 | 36224 | 48 / 0 / 0 | 1974912 | 121344 | 113152 | 47 / 1 / 1 | unavailable |
| output_tokens | 1032.81 | 987 | 48 / 0 / 0 | 49575 | 1439.53 | 1415 | 47 / 1 / 1 | unavailable |
| model_calls | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| mcp_calls | 0 | 0 | 48 / 0 / 0 | 0 | 5.48936 | 6 | 47 / 1 / 1 | unavailable |
| memglide_mcp_calls | 0 | 0 | 48 / 0 / 0 | 0 | 5.48936 | 6 | 47 / 1 / 1 | unavailable |
| observed_mcp_calls | 0 | 0 | 48 / 0 / 0 | 0 | 5.41667 | 6 | 48 / 0 / 0 | 260 |
| observed_memglide_mcp_calls | 0 | 0 | 48 / 0 / 0 | 0 | 5.41667 | 6 | 48 / 0 / 0 | 260 |
| wall_time_seconds | 24.0047 | 23.0707 | 48 / 0 / 0 | 1152.23 | 34.65 | 33.9061 | 47 / 1 / 1 | unavailable |
| end_to_end_wall_seconds | 24.0047 | 23.0707 | 48 / 0 / 0 | 1152.23 | 34.8426 | 33.9937 | 47 / 1 / 1 | unavailable |
| setup_wall_seconds | unavailable | unavailable | 0 / 48 / 48 | unavailable | 0.192554 | 0.184793 | 47 / 1 / 1 | unavailable |
| setup_cpu_seconds | unavailable | unavailable | 0 / 48 / 48 | unavailable | 0.0604689 | 0.0545734 | 47 / 1 / 1 | unavailable |
| repeated_file_reads | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| observed_file_read_commands | 1.29167 | 1 | 48 / 0 / 0 | 62 | 1.5 | 1 | 48 / 0 / 0 | 72 |
| observed_repeated_read_commands | 0.0416667 | 0 | 48 / 0 / 0 | 2 | 0.0416667 | 0 | 48 / 0 / 0 | 2 |
| actual_cost_usd | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| computed_cost_usd | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| process_tree_peak_rss_bytes | 255105024 | 2.75333e+08 | 48 / 0 / 0 | unavailable | 3.78435e+08 | 362872832 | 47 / 1 / 1 | unavailable |
| cpu_seconds | 5.2325 | 3.99 | 48 / 0 / 0 | 251.16 | 9.93936 | 8.25 | 47 / 1 / 1 | unavailable |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 / 48 / 48 | unavailable | 8.27505e+07 | 76337152 | 47 / 1 / 1 | unavailable |
| memglide_cpu_seconds | unavailable | unavailable | 0 / 48 / 48 | unavailable | 4.00255 | 3.43 | 47 / 1 / 1 | unavailable |
| context_freshness | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| retrieval_completeness | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 / 48 / 48 | unavailable | unavailable | unavailable | 0 / 48 / 48 | unavailable |

## Individual runs

| Task | Config | Repeat | Order | Status | Grader success | MCP calls | Memglide calls | Treatment valid | Input | Cached | Output | Seconds | Errors |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| ts-selective-retry | B | 1 | 1 | completed | yes | 5 | 5 | yes | 165149 | 137088 | 1487 | 35.9061 |  |
| ts-selective-retry | A | 1 | 2 | completed | yes | 0 | 0 | yes | 61974 | 47488 | 1160 | 23.2235 |  |
| py-lru-eviction | B | 1 | 3 | completed | yes | 4 | 4 | yes | 138366 | 109312 | 1839 | 38.4497 |  |
| py-lru-eviction | A | 1 | 4 | completed | yes | 0 | 0 | yes | 48342 | 22912 | 1352 | 24.9983 |  |
| py-selective-retry | B | 1 | 5 | completed | yes | 6 | 6 | yes | 163954 | 117760 | 1404 | 83.0976 |  |
| py-selective-retry | A | 1 | 6 | completed | yes | 0 | 0 | yes | 47723 | 43008 | 946 | 19.3573 |  |
| ts-boolean-config | B | 1 | 7 | completed | yes | 6 | 6 | yes | 164877 | 135936 | 1587 | 34.9054 |  |
| ts-boolean-config | A | 1 | 8 | completed | yes | 0 | 0 | yes | 75435 | 60672 | 1105 | 25.7751 |  |
| py-billing-rounding | B | 1 | 9 | completed | yes | 6 | 6 | yes | 140942 | 110208 | 1503 | 34.0197 |  |
| py-billing-rounding | A | 1 | 10 | completed | yes | 0 | 0 | yes | 61563 | 47232 | 1001 | 27.6853 |  |
| py-transitive-dependencies | A | 1 | 11 | completed | yes | 0 | 0 | yes | 47916 | 34304 | 887 | 47.9706 |  |
| py-transitive-dependencies | B | 1 | 12 | completed | yes | 4 | 4 | yes | 111874 | 92032 | 1229 | 28.4893 |  |
| ts-and-search | B | 1 | 13 | completed | yes | 5 | 5 | yes | 143590 | 112256 | 1384 | 35.8725 |  |
| ts-and-search | A | 1 | 14 | completed | yes | 0 | 0 | yes | 49011 | 34816 | 858 | 17.356 |  |
| py-cursor-pagination | B | 1 | 15 | completed | yes | 6 | 6 | yes | 141943 | 112000 | 1568 | 33.9061 |  |
| py-cursor-pagination | A | 1 | 16 | completed | yes | 0 | 0 | yes | 49059 | 34560 | 1191 | 23.5014 |  |
| py-ttl-boundary | B | 1 | 17 | completed | yes | 6 | 6 | yes | 168798 | 137856 | 1297 | 32.2086 |  |
| py-ttl-boundary | A | 1 | 18 | completed | yes | 0 | 0 | yes | 48342 | 35200 | 880 | 44.7494 |  |
| ts-idempotent-events | A | 1 | 19 | completed | yes | 0 | 0 | yes | 60993 | 46848 | 923 | 20.6816 |  |
| ts-idempotent-events | B | 1 | 20 | completed | yes | 6 | 6 | yes | 143883 | 122752 | 1415 | 32.7172 |  |
| ts-ttl-boundary | A | 1 | 21 | completed | yes | 0 | 0 | yes | 48673 | 34688 | 909 | 21.6 |  |
| ts-ttl-boundary | B | 1 | 22 | completed | yes | 4 | 4 | yes | 112754 | 83328 | 1240 | 31.8394 |  |
| ts-optimistic-revision | A | 1 | 23 | completed | yes | 0 | 0 | yes | 62075 | 47872 | 877 | 19.3581 |  |
| ts-optimistic-revision | B | 1 | 24 | completed | yes | 6 | 6 | yes | 142241 | 112000 | 1272 | 27.0998 |  |
| py-boolean-config | B | 1 | 25 | completed | yes | 6 | 6 | yes | 165456 | 136448 | 1573 | 34.5489 |  |
| py-boolean-config | A | 1 | 26 | completed | yes | 0 | 0 | yes | 75494 | 49408 | 1106 | 42.0345 |  |
| ts-transitive-dependencies | A | 1 | 27 | completed | yes | 0 | 0 | yes | 61920 | 36608 | 1167 | 23.2726 |  |
| ts-transitive-dependencies | B | 1 | 28 | completed | yes | 7 | 7 | yes | 142599 | 111744 | 1545 | 35.6008 |  |
| py-idempotent-events | B | 1 | 29 | completed | yes | 7 | 7 | yes | 170838 | 139904 | 1321 | 29.3166 |  |
| py-idempotent-events | A | 1 | 30 | completed | yes | 0 | 0 | yes | 60179 | 35200 | 918 | 19.9337 |  |
| py-optimistic-revision | A | 1 | 31 | completed | yes | 0 | 0 | yes | 48402 | 34432 | 825 | 17.1951 |  |
| py-optimistic-revision | B | 1 | 32 | completed | yes | 6 | 6 | yes | 168489 | 137472 | 1263 | 30.7192 |  |
| py-storage-containment | A | 1 | 33 | completed | yes | 0 | 0 | yes | 61556 | 35840 | 1273 | 25.1793 |  |
| py-storage-containment | B | 1 | 34 | completed | yes | 6 | 6 | yes | 140513 | 110592 | 1483 | 33.4403 |  |
| ts-cursor-pagination | B | 1 | 35 | completed | yes | 4 | 4 | yes | 140359 | 110336 | 1666 | 33.9861 |  |
| ts-cursor-pagination | A | 1 | 36 | completed | yes | 0 | 0 | yes | 63536 | 48640 | 1335 | 31.4622 |  |
| py-and-search | A | 1 | 37 | completed | yes | 0 | 0 | yes | 48664 | 34688 | 857 | 20.5937 |  |
| py-and-search | B | 1 | 38 | completed | yes | 6 | 6 | yes | 139987 | 110720 | 1449 | 30.844 |  |
| ts-billing-rounding | A | 1 | 39 | completed | yes | 0 | 0 | yes | 48244 | 34560 | 1178 | 27.8334 |  |
| ts-billing-rounding | B | 1 | 40 | completed | yes | 4 | 4 | yes | 135986 | 106752 | 1405 | 35.1705 |  |
| ts-lru-eviction | B | 1 | 41 | completed | yes | 6 | 6 | yes | 143173 | 121728 | 1886 | 37.8804 |  |
| ts-lru-eviction | A | 1 | 42 | completed | yes | 0 | 0 | yes | 61851 | 45312 | 1383 | 24.5229 |  |
| ts-scope-authorization | B | 1 | 43 | completed | yes | 4 | 4 | yes | 138382 | 108416 | 1074 | 27.9677 |  |
| ts-scope-authorization | A | 1 | 44 | completed | yes | 0 | 0 | yes | 48430 | 35456 | 804 | 17.9525 |  |
| ts-storage-containment | B | 1 | 45 | completed | yes | 4 | 4 | yes | 130878 | 102016 | 1434 | 31.041 |  |
| ts-storage-containment | A | 1 | 46 | completed | yes | 0 | 0 | yes | 48843 | 43520 | 1248 | 22.4668 |  |
| py-scope-authorization | A | 1 | 47 | completed | yes | 0 | 0 | yes | 48664 | 34688 | 852 | 17.4855 |  |
| py-scope-authorization | B | 1 | 48 | completed | yes | 4 | 4 | yes | 142330 | 112000 | 1152 | 34.631 |  |
| ts-selective-retry | A | 2 | 49 | completed | yes | 0 | 0 | yes | 47724 | 34176 | 968 | 19.5983 |  |
| ts-selective-retry | B | 2 | 50 | completed | yes | 4 | 4 | yes | 136534 | 119296 | 1233 | 27.9033 |  |
| py-lru-eviction | A | 2 | 51 | completed | yes | 0 | 0 | yes | 48291 | 43136 | 1340 | 23.3815 |  |
| py-lru-eviction | B | 2 | 52 | completed | yes | 6 | 6 | yes | 177092 | 132480 | 1829 | 36.0476 |  |
| py-selective-retry | A | 2 | 53 | completed | yes | 0 | 0 | yes | 47551 | 34048 | 887 | 23.8866 |  |
| py-selective-retry | B | 2 | 54 | completed | yes | 4 | 4 | yes | 136667 | 116736 | 1175 | 28.4823 |  |
| ts-boolean-config | A | 2 | 55 | completed | yes | 0 | 0 | yes | 75795 | 60928 | 1065 | 24.2729 |  |
| ts-boolean-config | B | 2 | 56 | completed | yes | 7 | 7 | yes | 145118 | 113152 | 1649 | 37.6199 |  |
| py-billing-rounding | A | 2 | 57 | completed | yes | 0 | 0 | yes | 48112 | 43136 | 1102 | 23.6396 |  |
| py-billing-rounding | B | 2 | 58 | completed | yes | 6 | 6 | yes | 171357 | 140544 | 1621 | 42.1004 |  |
| py-transitive-dependencies | B | 2 | 59 | completed | yes | 7 | 7 | yes | 163880 | 144640 | 1453 | 33.8393 |  |
| py-transitive-dependencies | A | 2 | 60 | completed | yes | 0 | 0 | yes | 47838 | 34304 | 802 | 15.9743 |  |
| ts-and-search | A | 2 | 61 | completed | yes | 0 | 0 | yes | 62469 | 48128 | 873 | 22.7119 |  |
| ts-and-search | B | 2 | 62 | completed | yes | 6 | 6 | yes | 141231 | 111360 | 1278 | 32.5457 |  |
| py-cursor-pagination | A | 2 | 63 | completed | yes | 0 | 0 | yes | 48991 | 34560 | 1156 | 21.0626 |  |
| py-cursor-pagination | B | 2 | 64 | completed | yes | 6 | 6 | yes | 174811 | 144512 | 1498 | 32.0669 |  |
| py-ttl-boundary | A | 2 | 65 | completed | yes | 0 | 0 | yes | 48265 | 34432 | 861 | 20.2747 |  |
| py-ttl-boundary | B | 2 | 66 | completed | yes | 4 | 4 | yes | 113348 | 83072 | 1232 | 27.0144 |  |
| ts-idempotent-events | B | 2 | 67 | completed | yes | 6 | 6 | yes | 142989 | 122240 | 1431 | 33.9847 |  |
| ts-idempotent-events | A | 2 | 68 | completed | yes | 0 | 0 | yes | 61118 | 46848 | 1008 | 25.4926 |  |
| ts-ttl-boundary | B | 2 | 69 | completed | yes | 6 | 6 | yes | 171276 | 139520 | 1396 | 34.2373 |  |
| ts-ttl-boundary | A | 2 | 70 | completed | yes | 0 | 0 | yes | 48595 | 34560 | 879 | 22.918 |  |
| ts-optimistic-revision | B | 2 | 71 | completed | yes | 7 | 7 | yes | 200871 | 178304 | 1318 | 41.0318 |  |
| ts-optimistic-revision | A | 2 | 72 | completed | yes | 0 | 0 | yes | 48623 | 34688 | 836 | 19.7 |  |
| py-boolean-config | A | 2 | 73 | completed | yes | 0 | 0 | yes | 48426 | 43392 | 1129 | 27.7314 |  |
| py-boolean-config | B | 2 | 74 | completed | yes | 6 | 6 | yes | 171248 | 137984 | 1528 | 49.3798 |  |
| ts-transitive-dependencies | B | 2 | 75 | completed | yes | 7 | 7 | yes | 173591 | 142080 | 1582 | 34.7252 |  |
| ts-transitive-dependencies | A | 2 | 76 | completed | yes | 0 | 0 | yes | 61454 | 56448 | 991 | 20.1963 |  |
| py-idempotent-events | A | 2 | 77 | completed | yes | 0 | 0 | yes | 48116 | 35328 | 942 | 20.9289 |  |
| py-idempotent-events | B | 2 | 78 | completed | yes | 6 | 6 | yes | 169349 | 139392 | 1312 | 30.9518 |  |
| py-optimistic-revision | B | 2 | 79 | completed | yes | 6 | 6 | yes | 143169 | 96896 | 1373 | 30.3203 |  |
| py-optimistic-revision | A | 2 | 80 | completed | yes | 0 | 0 | yes | 48219 | 43392 | 798 | 19.1565 |  |
| py-storage-containment | B | 2 | 81 | completed | yes | 6 | 6 | yes | 142950 | 112512 | 1592 | 34.8579 |  |
| py-storage-containment | A | 2 | 82 | completed | yes | 0 | 0 | yes | 60950 | 46464 | 1125 | 23.8051 |  |
| ts-cursor-pagination | A | 2 | 83 | completed | yes | 0 | 0 | yes | 63725 | 35584 | 1350 | 27.4901 |  |
| ts-cursor-pagination | B | 2 | 84 | completed | yes | 6 | 6 | yes | 169097 | 150784 | 1877 | 39.1161 |  |
| py-and-search | B | 2 | 85 | completed | yes | 4 | 4 | yes | 139940 | 108928 | 1201 | 28.6992 |  |
| py-and-search | A | 2 | 86 | completed | yes | 0 | 0 | yes | 48223 | 34304 | 983 | 19.8793 |  |
| ts-billing-rounding | B | 2 | 87 | completed | yes | 4 | 4 | yes | 135126 | 106240 | 1304 | 29.8139 |  |
| ts-billing-rounding | A | 2 | 88 | completed | yes | 0 | 0 | yes | 61452 | 47232 | 1220 | 25.6291 |  |
| ts-lru-eviction | A | 2 | 89 | completed | yes | 0 | 0 | yes | 61953 | 56576 | 1406 | 34.6024 |  |
| ts-lru-eviction | B | 2 | 90 | harness_error | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Exec-server transport disconnected; benchmark process no longer present. Original partial evidence retained; no model failure inferred. |
| ts-scope-authorization | A | 2 | 91 | completed | yes | 0 | 0 | yes | 48395 | 35328 | 809 | 19.5478 |  |
| ts-scope-authorization | B | 2 | 92 | completed | yes | 6 | 6 | yes | 170682 | 150016 | 1287 | 32.9008 |  |
| ts-storage-containment | A | 2 | 93 | completed | yes | 0 | 0 | yes | 48886 | 43648 | 1157 | 25.8441 |  |
| ts-storage-containment | B | 2 | 94 | completed | yes | 6 | 6 | yes | 144154 | 113152 | 1673 | 36.4258 |  |
| py-scope-authorization | B | 2 | 95 | completed | yes | 4 | 4 | yes | 137379 | 108672 | 1340 | 30.8282 |  |
| py-scope-authorization | A | 2 | 96 | completed | yes | 0 | 0 | yes | 61603 | 56320 | 853 | 18.312 |  |

### Per-run costs, reads, and local overhead

CPU values are sampled process CPU seconds (an observed lower bound); RSS values are sampled peaks in bytes. Short-lived processes may be missed. RSS may count shared pages more than once. Process-tree measurements include Codex and its observed children. Memglide-specific measurements cover only processes identified by the runner. Actual read counts are unavailable; command-intent proxy metrics appear separately.

| Task / configuration / repeat | Model calls | Repeated reads | Actual USD | Computed USD | Tree peak RSS | Tree CPU sec | Memglide peak RSS | Memglide CPU sec | Freshness | Completeness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ts-selective-retry / B / 1 | unavailable | unavailable | unavailable | unavailable | 414691328 | 10.36 | 84119552 | 4.61 | unavailable | unavailable |
| ts-selective-retry / A / 1 | unavailable | unavailable | unavailable | unavailable | 309186560 | 5.15 | unavailable | unavailable | unavailable | unavailable |
| py-lru-eviction / B / 1 | unavailable | unavailable | unavailable | unavailable | 347205632 | 8.07 | 74915840 | 3.49 | unavailable | unavailable |
| py-lru-eviction / A / 1 | unavailable | unavailable | unavailable | unavailable | 196513792 | 4.15 | unavailable | unavailable | unavailable | unavailable |
| py-selective-retry / B / 1 | unavailable | unavailable | unavailable | unavailable | 348151808 | 51.42 | 75505664 | 11.08 | unavailable | unavailable |
| py-selective-retry / A / 1 | unavailable | unavailable | unavailable | unavailable | 206557184 | 3.43 | unavailable | unavailable | unavailable | unavailable |
| ts-boolean-config / B / 1 | unavailable | unavailable | unavailable | unavailable | 419422208 | 9.73 | 89989120 | 3.92 | unavailable | unavailable |
| ts-boolean-config / A / 1 | unavailable | unavailable | unavailable | unavailable | 319725568 | 4.59 | unavailable | unavailable | unavailable | unavailable |
| py-billing-rounding / B / 1 | unavailable | unavailable | unavailable | unavailable | 353439744 | 7.24 | 75636736 | 2.99 | unavailable | unavailable |
| py-billing-rounding / A / 1 | unavailable | unavailable | unavailable | unavailable | 184172544 | 6.63 | unavailable | unavailable | unavailable | unavailable |
| py-transitive-dependencies / A / 1 | unavailable | unavailable | unavailable | unavailable | 152354816 | 21.42 | unavailable | unavailable | unavailable | unavailable |
| py-transitive-dependencies / B / 1 | unavailable | unavailable | unavailable | unavailable | 348147712 | 7.92 | 74838016 | 3.6 | unavailable | unavailable |
| ts-and-search / B / 1 | unavailable | unavailable | unavailable | unavailable | 414793728 | 8.27 | 89767936 | 3.19 | unavailable | unavailable |
| ts-and-search / A / 1 | unavailable | unavailable | unavailable | unavailable | 292261888 | 3.54 | unavailable | unavailable | unavailable | unavailable |
| py-cursor-pagination / B / 1 | unavailable | unavailable | unavailable | unavailable | 265187328 | 6 | 76066816 | 3.09 | unavailable | unavailable |
| py-cursor-pagination / A / 1 | unavailable | unavailable | unavailable | unavailable | 240488448 | 3.59 | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / B / 1 | unavailable | unavailable | unavailable | unavailable | 334282752 | 13.76 | 74772480 | 7.22 | unavailable | unavailable |
| py-ttl-boundary / A / 1 | unavailable | unavailable | unavailable | unavailable | 163508224 | 24.13 | unavailable | unavailable | unavailable | unavailable |
| ts-idempotent-events / A / 1 | unavailable | unavailable | unavailable | unavailable | 313667584 | 3.97 | unavailable | unavailable | unavailable | unavailable |
| ts-idempotent-events / B / 1 | unavailable | unavailable | unavailable | unavailable | 426401792 | 8.43 | 87691264 | 3.29 | unavailable | unavailable |
| ts-ttl-boundary / A / 1 | unavailable | unavailable | unavailable | unavailable | 327110656 | 4.07 | unavailable | unavailable | unavailable | unavailable |
| ts-ttl-boundary / B / 1 | unavailable | unavailable | unavailable | unavailable | 423030784 | 7.35 | 86396928 | 2.74 | unavailable | unavailable |
| ts-optimistic-revision / A / 1 | unavailable | unavailable | unavailable | unavailable | 308994048 | 3.54 | unavailable | unavailable | unavailable | unavailable |
| ts-optimistic-revision / B / 1 | unavailable | unavailable | unavailable | unavailable | 393613312 | 7.73 | 85352448 | 2.78 | unavailable | unavailable |
| py-boolean-config / B / 1 | unavailable | unavailable | unavailable | unavailable | 336306176 | 7.38 | 74936320 | 2.85 | unavailable | unavailable |
| py-boolean-config / A / 1 | unavailable | unavailable | unavailable | unavailable | 191057920 | 19.62 | unavailable | unavailable | unavailable | unavailable |
| ts-transitive-dependencies / A / 1 | unavailable | unavailable | unavailable | unavailable | 328335360 | 4.4 | unavailable | unavailable | unavailable | unavailable |
| ts-transitive-dependencies / B / 1 | unavailable | unavailable | unavailable | unavailable | 421367808 | 9.56 | 90116096 | 4.21 | unavailable | unavailable |
| py-idempotent-events / B / 1 | unavailable | unavailable | unavailable | unavailable | 358264832 | 7.38 | 75292672 | 3.23 | unavailable | unavailable |
| py-idempotent-events / A / 1 | unavailable | unavailable | unavailable | unavailable | 196268032 | 2.67 | unavailable | unavailable | unavailable | unavailable |
| py-optimistic-revision / A / 1 | unavailable | unavailable | unavailable | unavailable | 186486784 | 2.47 | unavailable | unavailable | unavailable | unavailable |
| py-optimistic-revision / B / 1 | unavailable | unavailable | unavailable | unavailable | 359284736 | 7.14 | 75636736 | 2.98 | unavailable | unavailable |
| py-storage-containment / A / 1 | unavailable | unavailable | unavailable | unavailable | 264900608 | 3.98 | unavailable | unavailable | unavailable | unavailable |
| py-storage-containment / B / 1 | unavailable | unavailable | unavailable | unavailable | 341508096 | 8.52 | 75300864 | 3.32 | unavailable | unavailable |
| ts-cursor-pagination / B / 1 | unavailable | unavailable | unavailable | unavailable | 425926656 | 11 | 87986176 | 4.7 | unavailable | unavailable |
| ts-cursor-pagination / A / 1 | unavailable | unavailable | unavailable | unavailable | 344051712 | 5.25 | unavailable | unavailable | unavailable | unavailable |
| py-and-search / A / 1 | unavailable | unavailable | unavailable | unavailable | 186585088 | 2.57 | unavailable | unavailable | unavailable | unavailable |
| py-and-search / B / 1 | unavailable | unavailable | unavailable | unavailable | 346619904 | 7.21 | 75206656 | 3.1 | unavailable | unavailable |
| ts-billing-rounding / A / 1 | unavailable | unavailable | unavailable | unavailable | 302080000 | 4.47 | unavailable | unavailable | unavailable | unavailable |
| ts-billing-rounding / B / 1 | unavailable | unavailable | unavailable | unavailable | 420401152 | 7.98 | 85475328 | 2.53 | unavailable | unavailable |
| ts-lru-eviction / B / 1 | unavailable | unavailable | unavailable | unavailable | 362872832 | 8.55 | 85716992 | 3.88 | unavailable | unavailable |
| ts-lru-eviction / A / 1 | unavailable | unavailable | unavailable | unavailable | 313954304 | 4.24 | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / B / 1 | unavailable | unavailable | unavailable | unavailable | 400936960 | 8.98 | 87355392 | 3.71 | unavailable | unavailable |
| ts-scope-authorization / A / 1 | unavailable | unavailable | unavailable | unavailable | 305065984 | 3.26 | unavailable | unavailable | unavailable | unavailable |
| ts-storage-containment / B / 1 | unavailable | unavailable | unavailable | unavailable | 431583232 | 7.91 | 90173440 | 3.53 | unavailable | unavailable |
| ts-storage-containment / A / 1 | unavailable | unavailable | unavailable | unavailable | 317317120 | 3.65 | unavailable | unavailable | unavailable | unavailable |
| py-scope-authorization / A / 1 | unavailable | unavailable | unavailable | unavailable | 185798656 | 2.66 | unavailable | unavailable | unavailable | unavailable |
| py-scope-authorization / B / 1 | unavailable | unavailable | unavailable | unavailable | 352337920 | 7.25 | 74477568 | 3.23 | unavailable | unavailable |
| ts-selective-retry / A / 2 | unavailable | unavailable | unavailable | unavailable | 304893952 | 3.38 | unavailable | unavailable | unavailable | unavailable |
| ts-selective-retry / B / 2 | unavailable | unavailable | unavailable | unavailable | 404021248 | 8.42 | 86716416 | 3.15 | unavailable | unavailable |
| py-lru-eviction / A / 2 | unavailable | unavailable | unavailable | unavailable | 181125120 | 2.94 | unavailable | unavailable | unavailable | unavailable |
| py-lru-eviction / B / 2 | unavailable | unavailable | unavailable | unavailable | 349347840 | 8.47 | 75010048 | 3.79 | unavailable | unavailable |
| py-selective-retry / A / 2 | unavailable | unavailable | unavailable | unavailable | 200343552 | 2.83 | unavailable | unavailable | unavailable | unavailable |
| py-selective-retry / B / 2 | unavailable | unavailable | unavailable | unavailable | 288026624 | 7.68 | 75792384 | 3.07 | unavailable | unavailable |
| ts-boolean-config / A / 2 | unavailable | unavailable | unavailable | unavailable | 318566400 | 4.28 | unavailable | unavailable | unavailable | unavailable |
| ts-boolean-config / B / 2 | unavailable | unavailable | unavailable | unavailable | 467230720 | 11.54 | 87560192 | 5.04 | unavailable | unavailable |
| py-billing-rounding / A / 2 | unavailable | unavailable | unavailable | unavailable | 189681664 | 4.31 | unavailable | unavailable | unavailable | unavailable |
| py-billing-rounding / B / 2 | unavailable | unavailable | unavailable | unavailable | 340348928 | 7.48 | 75472896 | 3.23 | unavailable | unavailable |
| py-transitive-dependencies / B / 2 | unavailable | unavailable | unavailable | unavailable | 355639296 | 7.34 | 75177984 | 3.01 | unavailable | unavailable |
| py-transitive-dependencies / A / 2 | unavailable | unavailable | unavailable | unavailable | 178388992 | 2.57 | unavailable | unavailable | unavailable | unavailable |
| ts-and-search / A / 2 | unavailable | unavailable | unavailable | unavailable | 307187712 | 6.13 | unavailable | unavailable | unavailable | unavailable |
| ts-and-search / B / 2 | unavailable | unavailable | unavailable | unavailable | 390328320 | 10.27 | 87031808 | 5.48 | unavailable | unavailable |
| py-cursor-pagination / A / 2 | unavailable | unavailable | unavailable | unavailable | 192454656 | 2.65 | unavailable | unavailable | unavailable | unavailable |
| py-cursor-pagination / B / 2 | unavailable | unavailable | unavailable | unavailable | 341667840 | 7.16 | 75980800 | 3.1 | unavailable | unavailable |
| py-ttl-boundary / A / 2 | unavailable | unavailable | unavailable | unavailable | 180850688 | 4.21 | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / B / 2 | unavailable | unavailable | unavailable | unavailable | 344625152 | 7.53 | 74883072 | 3.14 | unavailable | unavailable |
| ts-idempotent-events / B / 2 | unavailable | unavailable | unavailable | unavailable | 412282880 | 9.74 | 89903104 | 4.28 | unavailable | unavailable |
| ts-idempotent-events / A / 2 | unavailable | unavailable | unavailable | unavailable | 321867776 | 4.78 | unavailable | unavailable | unavailable | unavailable |
| ts-ttl-boundary / B / 2 | unavailable | unavailable | unavailable | unavailable | 432533504 | 9.34 | 88350720 | 3.64 | unavailable | unavailable |
| ts-ttl-boundary / A / 2 | unavailable | unavailable | unavailable | unavailable | 303280128 | 4 | unavailable | unavailable | unavailable | unavailable |
| ts-optimistic-revision / B / 2 | unavailable | unavailable | unavailable | unavailable | 432910336 | 14.27 | 145850368 | 5.75 | unavailable | unavailable |
| ts-optimistic-revision / A / 2 | unavailable | unavailable | unavailable | unavailable | 294682624 | 3.98 | unavailable | unavailable | unavailable | unavailable |
| py-boolean-config / A / 2 | unavailable | unavailable | unavailable | unavailable | 261222400 | 4.9 | unavailable | unavailable | unavailable | unavailable |
| py-boolean-config / B / 2 | unavailable | unavailable | unavailable | unavailable | 379236352 | 24.99 | 75440128 | 11.47 | unavailable | unavailable |
| ts-transitive-dependencies / B / 2 | unavailable | unavailable | unavailable | unavailable | 431927296 | 10.04 | 89903104 | 3.89 | unavailable | unavailable |
| ts-transitive-dependencies / A / 2 | unavailable | unavailable | unavailable | unavailable | 317771776 | 3.91 | unavailable | unavailable | unavailable | unavailable |
| py-idempotent-events / A / 2 | unavailable | unavailable | unavailable | unavailable | 192954368 | 2.75 | unavailable | unavailable | unavailable | unavailable |
| py-idempotent-events / B / 2 | unavailable | unavailable | unavailable | unavailable | 349970432 | 7.98 | 74780672 | 3.4 | unavailable | unavailable |
| py-optimistic-revision / B / 2 | unavailable | unavailable | unavailable | unavailable | 355196928 | 8.25 | 76337152 | 3.55 | unavailable | unavailable |
| py-optimistic-revision / A / 2 | unavailable | unavailable | unavailable | unavailable | 189984768 | 2.53 | unavailable | unavailable | unavailable | unavailable |
| py-storage-containment / B / 2 | unavailable | unavailable | unavailable | unavailable | 342405120 | 7.55 | 76103680 | 3.43 | unavailable | unavailable |
| py-storage-containment / A / 2 | unavailable | unavailable | unavailable | unavailable | 268640256 | 4.21 | unavailable | unavailable | unavailable | unavailable |
| ts-cursor-pagination / A / 2 | unavailable | unavailable | unavailable | unavailable | 320233472 | 5.17 | unavailable | unavailable | unavailable | unavailable |
| ts-cursor-pagination / B / 2 | unavailable | unavailable | unavailable | unavailable | 412725248 | 10.18 | 90095616 | 4.72 | unavailable | unavailable |
| py-and-search / B / 2 | unavailable | unavailable | unavailable | unavailable | 347103232 | 7.4 | 75030528 | 3.21 | unavailable | unavailable |
| py-and-search / A / 2 | unavailable | unavailable | unavailable | unavailable | 196698112 | 2.57 | unavailable | unavailable | unavailable | unavailable |
| ts-billing-rounding / B / 2 | unavailable | unavailable | unavailable | unavailable | 395894784 | 7.55 | 85569536 | 2.93 | unavailable | unavailable |
| ts-billing-rounding / A / 2 | unavailable | unavailable | unavailable | unavailable | 309690368 | 4.98 | unavailable | unavailable | unavailable | unavailable |
| ts-lru-eviction / A / 2 | unavailable | unavailable | unavailable | unavailable | 282025984 | 14.54 | unavailable | unavailable | unavailable | unavailable |
| ts-lru-eviction / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / A / 2 | unavailable | unavailable | unavailable | unavailable | 318730240 | 3.62 | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / B / 2 | unavailable | unavailable | unavailable | unavailable | 435630080 | 7.98 | 89944064 | 3.57 | unavailable | unavailable |
| ts-storage-containment / A / 2 | unavailable | unavailable | unavailable | unavailable | 290627584 | 5.53 | unavailable | unavailable | unavailable | unavailable |
| ts-storage-containment / B / 2 | unavailable | unavailable | unavailable | unavailable | 403734528 | 11.46 | 89837568 | 4.97 | unavailable | unavailable |
| py-scope-authorization / B / 2 | unavailable | unavailable | unavailable | unavailable | 327897088 | 9.39 | 75776000 | 3.03 | unavailable | unavailable |
| py-scope-authorization / A / 2 | unavailable | unavailable | unavailable | unavailable | 186695680 | 2.94 | unavailable | unavailable | unavailable | unavailable |

### MCP invocation evidence

Calls are deduplicated by CLI item ID across started/updated/completed events. A call that starts and fails is still an observed invocation. Enabled server configuration alone does not establish invocation.

- ts-selective-retry / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True)
- py-lru-eviction / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-selective-retry / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.expand_context (status=failed, completed=True); memglide.expand_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-boolean-config / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-billing-rounding / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-transitive-dependencies / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-and-search / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True)
- py-cursor-pagination / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-ttl-boundary / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-idempotent-events / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-ttl-boundary / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-optimistic-revision / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-boolean-config / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-transitive-dependencies / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.end_session (status=completed, completed=True)
- py-idempotent-events / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.end_session (status=completed, completed=True)
- py-optimistic-revision / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-storage-containment / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-cursor-pagination / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-and-search / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-billing-rounding / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-lru-eviction / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-scope-authorization / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-storage-containment / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-scope-authorization / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-selective-retry / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-lru-eviction / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.expand_context (status=failed, completed=True); memglide.expand_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-selective-retry / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-boolean-config / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.end_session (status=completed, completed=True)
- py-billing-rounding / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-transitive-dependencies / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.end_session (status=completed, completed=True)
- ts-and-search / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-cursor-pagination / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-ttl-boundary / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-idempotent-events / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-ttl-boundary / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-optimistic-revision / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.end_session (status=completed, completed=True)
- py-boolean-config / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-transitive-dependencies / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.end_session (status=completed, completed=True)
- py-idempotent-events / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-optimistic-revision / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-storage-containment / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-cursor-pagination / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-and-search / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-billing-rounding / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-lru-eviction / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True)
- ts-scope-authorization / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- ts-storage-containment / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)
- py-scope-authorization / B / repeat 2: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)

## Paired differences

Verified attempted A/B pairs: **47**. Differences are B minus A. Failed tasks remain in paired observations.

| Metric | Mean difference | Median difference | Pairs with measurements | Missing |
| --- | ---: | ---: | ---: | ---: |
| input_tokens | 95734.3 | 90024 | 47 | 0 |
| cached_input_tokens | 80528.3 | 76032 | 47 | 0 |
| output_tokens | 414.66 | 423 | 47 | 0 |
| model_calls | unavailable | unavailable | 0 | 47 |
| mcp_calls | 5.48936 | 6 | 47 | 0 |
| memglide_mcp_calls | 5.48936 | 6 | 47 | 0 |
| observed_mcp_calls | 5.48936 | 6 | 47 | 0 |
| observed_memglide_mcp_calls | 5.48936 | 6 | 47 | 0 |
| wall_time_seconds | 10.8708 | 10.5817 | 47 | 0 |
| end_to_end_wall_seconds | 11.0634 | 10.9586 | 47 | 0 |
| setup_wall_seconds | unavailable | unavailable | 0 | 47 |
| setup_cpu_seconds | unavailable | unavailable | 0 | 47 |
| repeated_file_reads | unavailable | unavailable | 0 | 47 |
| observed_file_read_commands | 0.212766 | 0 | 47 | 0 |
| observed_repeated_read_commands | 0 | 0 | 47 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 | 47 |
| computed_cost_usd | unavailable | unavailable | 0 | 47 |
| process_tree_peak_rss_bytes | 1.23903e+08 | 118321152 | 47 | 0 |
| cpu_seconds | 4.90489 | 4.71 | 47 | 0 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 | 47 |
| memglide_cpu_seconds | unavailable | unavailable | 0 | 47 |
| context_freshness | unavailable | unavailable | 0 | 47 |
| retrieval_completeness | unavailable | unavailable | 0 | 47 |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 | 47 |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 | 47 |

Excluded pairs (still retained in the individual and overall results):

- ts-lru-eviction repeat 2: Both configurations must be attempted with verified treatment

## Failures and treatment fidelity

- ts-lru-eviction / B / repeat 2: status harness_error; grader success unavailable; Successful get_context is unverified: result evidence or stream coverage is incomplete. Exec-server transport disconnected; benchmark process no longer present. Original partial evidence retained; no model failure inferred.

## Evidence and limitations

- No savings claim follows from a shorter response or fewer returned context characters.
- Completed Codex turns are not the number of underlying model/API calls.
- Absent provider invoiced cost is null. Computed list-price cost, if supplied, is separate.
- Metric averages and medians use observed values; n and missing counts accompany them.
- Failed and ungraded attempts remain in completion-rate and cost-per-success accounting.
- Actual repeated filesystem reads are unavailable. Observed read-command fields are heuristics for command intent, not actual I/O measurements or guaranteed I/O lower bounds.
- MCP invocation is checked from tool events, independent of model self-report.
- B treatment fidelity requires a completed, error-free Memglide get_context result; failed calls and calls to other tools do not verify retrieval treatment.
- Paired comparisons require identical recorded starting commits and prompt SHA-256 values. Missing or unequal identities and explicitly changed runtime source exclude paired deltas; all raw attempts, failures and unconditional aggregates remain visible.
- MCP total counts are withheld for incomplete event streams; observed counts are lower bounds.
- Retrieval completeness and freshness require separate ground-truth observations; null is unknown.
- Independent target-path/symbol coverage probes are labelled proxies; they do not measure semantic completeness or establish what source context the coding model used.
- Sampled process CPU is an observed lower bound; sampled RSS peaks may miss short-lived processes and count shared pages repeatedly. Remote inference resources are unavailable.
- A/B prompt caching cannot generally be reset at the provider; run order and observed cached tokens matter.
- Synthetic fixture tasks do not establish performance on arbitrary production repositories.

Full per-run grader output, raw-event paths, process measurements, unavailable reasons, and task definitions are retained in the accompanying JSON report.
