# Memglide Codex A/B benchmark

Observed results are descriptive. Assess task success, full cost coverage, treatment fidelity, sample size, cache order, and task representativeness before claiming savings.

A = standard Codex. B = same Codex settings with Memglide. Success is determined by the external grader. Missing measurements are `unavailable`, not zero.

## Protocol and environment

```json
{
  "cgroup_v2_limits": {
    "cpu.max": "400000 100000",
    "memory.max": "34359738368",
    "memory.swap.max": "max",
    "pids.max": "max"
  },
  "codex_version": "codex-cli 0.159.2",
  "cpu_affinity_count": 5,
  "finished_at": "2026-10-17T21:23:33.297542+00:00",
  "host_python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]",
  "logical_cpu_count": 5,
  "measurement_sha256": {
    "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
    "benchmarks/reporting.py": "723fcd5529dc7b3b52d4fdddec4692a9399faa0e864a6b7fcde26f824136f0fc",
    "benchmarks/run.py": "ccf8d44ca7ea8286a8a9241b030eaa76ca339ec15032aeb95cb4e256ef500a26",
    "benchmarks/tasks.json": "5a921674ff669ebe09af08c06b9bb95ea597ff051ddcddb3312ce9508affe185",
    "benchmarks/telemetry.py": "0cf7a4fae8973f9cb771129e71c11c2b3e0d03106cdc5a41eed6698f32460fe7"
  },
  "memglide_source_after": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-17T21:23:33.313985+00:00",
    "git_head": "6556ef2fda9509f1b2c6a6d4b1be922cf9727c09",
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
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-17T21:22:33.466167+00:00",
    "git_head": "6556ef2fda9509f1b2c6a6d4b1be922cf9727c09",
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
  "methodology": {
    "caching": "Fresh process/session/index per run; counterbalanced arm order. OS and provider caches are not flushable; cached input is recorded when exposed",
    "cost": "Actual cost and model-call count remain null unless provider telemetry exposes them; no token-price estimate is actual cost",
    "failed_runs": "All planned rows and attempted failures retained; common preflight blockers stop pointless repeats",
    "isolation": "Fresh detached Git worktree from the same per-language seed commit for every run",
    "overhead": "Linux /proc samples local child processes; remote model resources unavailable",
    "prompt": "Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.\nIf memglide MCP tools are available, use list_projects, start_session and get_context before editing, inspect the source evidence you need, and revalidate the Context Passport after edits. Otherwise use ordinary source tools. Do not claim token or cost savings.\n",
    "repositories": "Two synthetic multi-module Python/TypeScript maintenance fixtures; external hidden oracles",
    "settings": "Same model, effort, output schema, sandbox and tool instructions; only Memglide MCP availability differs",
    "timing": "wall_time_seconds measures Codex process; B index timing is separate and included in end_to_end_wall_seconds. Independent readiness probes are excluded"
  },
  "model": "gpt-6.1-sol",
  "output_directory": "/workspace/Memglide/.local/benchmarks/device-auth-smoke-v3",
  "platform": "linux",
  "preflight_runs": [
    {
      "artifacts": "/workspace/Memglide/.local/benchmarks/device-auth-smoke-v3/preflight",
      "exit_code": 0,
      "overhead": {
        "cpu_seconds": 1.51,
        "memglide_cpu_seconds": null,
        "memglide_peak_rss_bytes": null,
        "method": "/proc sampling; CPU observed lower bound, RSS shared pages can be counted multiple times; short-lived processes may be missed",
        "observed_memglide_processes": 0,
        "observed_processes": 2,
        "process_tree_peak_rss_bytes": 102502400,
        "samples": 81,
        "sampling_interval_seconds": 0.05,
        "scope": "Local Codex process tree only; remote model CPU and memory unavailable"
      },
      "scope": "Readiness request, excluded from task comparisons; usage retained separately",
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
          "output_tokens": 43
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
          "output_tokens": 43
        },
        "usage_coverage_complete": true,
        "usage_scope": "Complete parsed stream only; partial observed turn usage is stored separately",
        "usage_unavailable_reasons": {}
      },
      "timed_out": false,
      "wall_time_seconds": 4.346457829000428
    }
  ],
  "random_seed": 20261016,
  "reasoning_effort": "low",
  "repeats": 1,
  "repetitions": 1,
  "repositories": {
    "python": {
      "commit": "04352134a24fd3400abfc1a14ef65cfb00ffc9d7",
      "path": "/workspace/Memglide/.local/benchmarks/device-auth-smoke-v3/repositories/python"
    }
  },
  "resource_scope": "Local execution host; model inference resources are not exposed",
  "source_unchanged_during_experiment": true,
  "started_at": "2026-10-17T21:22:32.888409+00:00",
  "tool_versions": {
    "git": "git version 2.52.0",
    "node": "v24.19.0",
    "npm": "11.9.0",
    "python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]"
  }
}
```

## Overall results (all runs)

| Measure | A | B |
| --- | ---: | ---: |
| Planned runs | 1 | 1 |
| Attempted runs | 1 | 1 |
| Not run | 0 | 0 |
| Graded runs | 1 | 1 |
| Successful runs | 1 | 1 |
| Failed grades | 0 | 0 |
| Ungraded attempts | 0 | 0 |
| Task completion rate | 1 | 1 |
| Invalid treatment runs | 0 | 0 |
| Unknown treatment runs | 0 | 0 |
| Actual provider cost per success (USD) | unavailable | unavailable |
| Computed pricing cost per success (USD) | unavailable | unavailable |

Cost per success includes all attempted-run costs, including failures. It is unavailable when any attempted-run cost is missing or no task succeeds.

## Measurements

Means/medians include observed values only. Coverage columns show observed n / missing among attempted runs / missing among all planned runs. Totals are withheld when coverage is incomplete and for non-additive metrics.

| Metric | A mean | A median | A n / attempted missing / planned missing | A total | B mean | B median | B n / attempted missing / planned missing | B total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| input_tokens | 48343 | 48343 | 1 / 0 / 0 | 48343 | 172380 | 172380 | 1 / 0 / 0 | 172380 |
| cached_input_tokens | 43392 | 43392 | 1 / 0 / 0 | 43392 | 138752 | 138752 | 1 / 0 / 0 | 138752 |
| output_tokens | 892 | 892 | 1 / 0 / 0 | 892 | 1341 | 1341 | 1 / 0 / 0 | 1341 |
| model_calls | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 6 | 6 | 1 / 0 / 0 | 6 |
| memglide_mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 6 | 6 | 1 / 0 / 0 | 6 |
| observed_mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 6 | 6 | 1 / 0 / 0 | 6 |
| observed_memglide_mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 6 | 6 | 1 / 0 / 0 | 6 |
| wall_time_seconds | 20.8202 | 20.8202 | 1 / 0 / 0 | 20.8202 | 33.2882 | 33.2882 | 1 / 0 / 0 | 33.2882 |
| end_to_end_wall_seconds | 20.8202 | 20.8202 | 1 / 0 / 0 | 20.8202 | 33.5494 | 33.5494 | 1 / 0 / 0 | 33.5494 |
| setup_wall_seconds | unavailable | unavailable | 0 / 1 / 1 | unavailable | 0.261196 | 0.261196 | 1 / 0 / 0 | 0.261196 |
| setup_cpu_seconds | unavailable | unavailable | 0 / 1 / 1 | unavailable | 0.122374 | 0.122374 | 1 / 0 / 0 | 0.122374 |
| repeated_file_reads | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| observed_file_read_commands | 1 | 1 | 1 / 0 / 0 | 1 | 1 | 1 | 1 / 0 / 0 | 1 |
| observed_repeated_read_commands | 0 | 0 | 1 / 0 / 0 | 0 | 0 | 0 | 1 / 0 / 0 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| computed_cost_usd | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| process_tree_peak_rss_bytes | 191848448 | 191848448 | 1 / 0 / 0 | unavailable | 395304960 | 395304960 | 1 / 0 / 0 | unavailable |
| cpu_seconds | 4.7 | 4.7 | 1 / 0 / 0 | 4.7 | 9.68 | 9.68 | 1 / 0 / 0 | 9.68 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 / 1 / 1 | unavailable | 75874304 | 75874304 | 1 / 0 / 0 | unavailable |
| memglide_cpu_seconds | unavailable | unavailable | 0 / 1 / 1 | unavailable | 4.49 | 4.49 | 1 / 0 / 0 | 4.49 |
| context_freshness | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| retrieval_completeness | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |

## Individual runs

| Task | Config | Repeat | Order | Status | Grader success | MCP calls | Memglide calls | Treatment valid | Input | Cached | Output | Seconds | Errors |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| py-ttl-boundary | A | 1 | 1 | completed | yes | 0 | 0 | yes | 48343 | 43392 | 892 | 20.8202 |  |
| py-ttl-boundary | B | 1 | 2 | completed | yes | 6 | 6 | yes | 172380 | 138752 | 1341 | 33.2882 |  |

### Per-run costs, reads, and local overhead

CPU values are sampled process CPU seconds (an observed lower bound); RSS values are sampled peaks in bytes. Short-lived processes may be missed. RSS may count shared pages more than once. Process-tree measurements include Codex and its observed children. Memglide-specific measurements cover only processes identified by the runner. Actual read counts are unavailable; command-intent proxy metrics appear separately.

| Task / configuration / repeat | Model calls | Repeated reads | Actual USD | Computed USD | Tree peak RSS | Tree CPU sec | Memglide peak RSS | Memglide CPU sec | Freshness | Completeness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| py-ttl-boundary / A / 1 | unavailable | unavailable | unavailable | unavailable | 191848448 | 4.7 | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / B / 1 | unavailable | unavailable | unavailable | unavailable | 395304960 | 9.68 | 75874304 | 4.49 | unavailable | unavailable |

### MCP invocation evidence

Calls are deduplicated by CLI item ID across started/updated/completed events. A call that starts and fails is still an observed invocation. Enabled server configuration alone does not establish invocation.

- py-ttl-boundary / B / repeat 1: memglide.list_projects (status=completed, completed=True); memglide.start_session (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True); memglide.get_context (status=completed, completed=True); memglide.get_context_passport (status=completed, completed=True)

## Paired differences

Verified attempted A/B pairs: **1**. Differences are B minus A. Failed tasks remain in paired observations.

| Metric | Mean difference | Median difference | Pairs with measurements | Missing |
| --- | ---: | ---: | ---: | ---: |
| input_tokens | 124037 | 124037 | 1 | 0 |
| cached_input_tokens | 95360 | 95360 | 1 | 0 |
| output_tokens | 449 | 449 | 1 | 0 |
| model_calls | unavailable | unavailable | 0 | 1 |
| mcp_calls | 6 | 6 | 1 | 0 |
| memglide_mcp_calls | 6 | 6 | 1 | 0 |
| observed_mcp_calls | 6 | 6 | 1 | 0 |
| observed_memglide_mcp_calls | 6 | 6 | 1 | 0 |
| wall_time_seconds | 12.468 | 12.468 | 1 | 0 |
| end_to_end_wall_seconds | 12.7292 | 12.7292 | 1 | 0 |
| setup_wall_seconds | unavailable | unavailable | 0 | 1 |
| setup_cpu_seconds | unavailable | unavailable | 0 | 1 |
| repeated_file_reads | unavailable | unavailable | 0 | 1 |
| observed_file_read_commands | 0 | 0 | 1 | 0 |
| observed_repeated_read_commands | 0 | 0 | 1 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 | 1 |
| computed_cost_usd | unavailable | unavailable | 0 | 1 |
| process_tree_peak_rss_bytes | 203456512 | 203456512 | 1 | 0 |
| cpu_seconds | 4.98 | 4.98 | 1 | 0 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 | 1 |
| memglide_cpu_seconds | unavailable | unavailable | 0 | 1 |
| context_freshness | unavailable | unavailable | 0 | 1 |
| retrieval_completeness | unavailable | unavailable | 0 | 1 |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 | 1 |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 | 1 |

## Failures and treatment fidelity

Every recorded run passed its external grader and treatment check.

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
