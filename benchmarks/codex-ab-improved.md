# Memglide Codex A/B benchmark

No verified A/B coding pairs completed; performance and savings are undetermined.

A = standard Codex. B = same Codex settings with Memglide. Success is determined by the external grader. Missing measurements are `unavailable`, not zero.

## Protocol and environment

```json
{
  "blockers": [
    "Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl"
  ],
  "cgroup_v2_limits": {
    "cpu.max": "400000 100000",
    "memory.max": "34359738368",
    "memory.swap.max": "max",
    "pids.max": "max"
  },
  "codex_version": "codex-cli 0.159.2",
  "cpu_affinity_count": 5,
  "finished_at": "2026-10-16T17:10:32.881029+00:00",
  "host_python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]",
  "logical_cpu_count": 5,
  "measurement_sha256": {
    "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
    "benchmarks/reporting.py": "fe5469cdf9985d609299b1b7c74f0296dc9289d902a677b924ecb55bb5ba5842",
    "benchmarks/run.py": "9f0bd71cb66bb1ce1240e8b813b8636b0aa7be9b3c7e66093c5079d2a2118b9d",
    "benchmarks/tasks.json": "5a921674ff669ebe09af08c06b9bb95ea597ff051ddcddb3312ce9508affe185",
    "benchmarks/telemetry.py": "0cf7a4fae8973f9cb771129e71c11c2b3e0d03106cdc5a41eed6698f32460fe7"
  },
  "memglide_source_after": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-16T17:10:32.905837+00:00",
    "git_head": "39e8df30565783a686270f8a6f422e56e41e3776",
    "measurement_files": {
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state",
    "source_dirty_entries": [
      " M src/memglide/api/app.py",
      " M src/memglide/cli.py",
      " M src/memglide/core/context.py",
      " M src/memglide/core/indexer.py",
      " M src/memglide/integrations/codex.py",
      " M src/memglide/integrations/mcp_server.py",
      " M src/memglide/memory/engine.py",
      "?? src/memglide/core/query.py"
    ],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "b789245d01bbc0d93771137889b5971e0980864c971b612dd87e84ab430d6ac2",
      "src/memglide/cli.py": "0a4cc01bafe7e2d2c43171984fa05c01cafeeba113a432d5f62706560a1d3989",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/context.py": "d94123bf425545944c25d13c96eae30810e5cd5ba013657fdf7b86cc42f5b30d",
      "src/memglide/core/indexer.py": "d71181f44519883c93dafab1df7b0ce5587c61d0e242b52a4187e6e15df60f7f",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "781f44a138491a23c1283feb54f0ff6ab83b20264bc658d9776f4518b9b85567",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "99e3d527187cfc457b4c574a1127a1c6fb738db6b4d4e9a7f8a42c56d5879d76",
      "src/memglide/integrations/mcp_server.py": "80f1ed60fcfd7951ced1f7b957c46661c71fe8eac3cb8bd1eb62c5b75c99dff8",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "524a42285ebed31bb14d7b2948847fd1f83b88f1cfc1eb695a650bb4400e598f",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "f346d2c4162346eab3c4e8abb16c18a9bd0dee2b8bc2599a489312a72162dbd2",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "b8b866bca23b40ec567d73a9c650d9189d8c179ce267bd2a05d0273181723932"
    },
    "source_tree_sha256": "b0fd2cc1f3997d1a0d19ab97addaaef00abe2e859a1cacf570162b6fc231df94"
  },
  "memglide_source_before": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-16T17:10:29.246558+00:00",
    "git_head": "39e8df30565783a686270f8a6f422e56e41e3776",
    "measurement_files": {
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state",
    "source_dirty_entries": [
      " M src/memglide/api/app.py",
      " M src/memglide/cli.py",
      " M src/memglide/core/context.py",
      " M src/memglide/core/indexer.py",
      " M src/memglide/integrations/codex.py",
      " M src/memglide/integrations/mcp_server.py",
      " M src/memglide/memory/engine.py",
      "?? src/memglide/core/query.py"
    ],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "b789245d01bbc0d93771137889b5971e0980864c971b612dd87e84ab430d6ac2",
      "src/memglide/cli.py": "0a4cc01bafe7e2d2c43171984fa05c01cafeeba113a432d5f62706560a1d3989",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/context.py": "d94123bf425545944c25d13c96eae30810e5cd5ba013657fdf7b86cc42f5b30d",
      "src/memglide/core/indexer.py": "d71181f44519883c93dafab1df7b0ce5587c61d0e242b52a4187e6e15df60f7f",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "781f44a138491a23c1283feb54f0ff6ab83b20264bc658d9776f4518b9b85567",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "99e3d527187cfc457b4c574a1127a1c6fb738db6b4d4e9a7f8a42c56d5879d76",
      "src/memglide/integrations/mcp_server.py": "80f1ed60fcfd7951ced1f7b957c46661c71fe8eac3cb8bd1eb62c5b75c99dff8",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "524a42285ebed31bb14d7b2948847fd1f83b88f1cfc1eb695a650bb4400e598f",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "f346d2c4162346eab3c4e8abb16c18a9bd0dee2b8bc2599a489312a72162dbd2",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "b8b866bca23b40ec567d73a9c650d9189d8c179ce267bd2a05d0273181723932"
    },
    "source_tree_sha256": "b0fd2cc1f3997d1a0d19ab97addaaef00abe2e859a1cacf570162b6fc231df94"
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
  "output_directory": "/workspace/Memglide/.local/benchmarks/improved-ab-final",
  "platform": "linux",
  "preflight_runs": [
    {
      "artifacts": "/workspace/Memglide/.local/benchmarks/improved-ab-final/preflight",
      "exit_code": 1,
      "overhead": {
        "cpu_seconds": 1.66,
        "memglide_cpu_seconds": null,
        "memglide_peak_rss_bytes": null,
        "method": "/proc sampling; CPU observed lower bound, RSS shared pages can be counted multiple times; short-lived processes may be missed",
        "observed_memglide_processes": 0,
        "observed_processes": 2,
        "process_tree_peak_rss_bytes": 83898368,
        "samples": 47,
        "sampling_interval_seconds": 0.05,
        "scope": "Local Codex process tree only; remote model CPU and memory unavailable"
      },
      "scope": "Readiness request, excluded from task comparisons; usage retained separately",
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": 0,
        "commands": [],
        "completed_turns": 0,
        "errors": [
          {
            "message": "Your access token could not be refreshed because you have since logged out or signed in to another account. Please sign in again.",
            "type": "error"
          },
          {
            "error": {
              "message": "Your access token could not be refreshed because you have since logged out or signed in to another account. Please sign in again."
            },
            "type": "turn.failed"
          }
        ],
        "event_count": 4,
        "failed_turns": 1,
        "file_read_method": "Heuristic command-intent proxy from successful command_execution items containing literal cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, scripts, directory searches, MCP reads, and internal reads are excluded. A repeated command names a path recognized in an earlier command. This is not an I/O trace, an actual read count, or a guaranteed lower bound on filesystem reads.",
        "file_reads_complete": false,
        "mcp_call_count": 0,
        "mcp_calls": [],
        "mcp_count_scope": "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound",
        "mcp_counts_complete": false,
        "memglide_get_context_success_unknown_count": 0,
        "memglide_mcp_call_count": 0,
        "memglide_successful_get_context_count": 0,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": null,
          "input_tokens": null,
          "output_tokens": null
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
          "cached_input_tokens": null,
          "input_tokens": null,
          "output_tokens": null
        },
        "usage_coverage_complete": false,
        "usage_scope": "Complete parsed stream only; partial observed turn usage is stored separately",
        "usage_unavailable_reasons": {
          "cached_input_tokens": "Total usage unavailable: event stream is empty, truncated, contains unparsed lines, or includes a failed turn whose usage may be unreported",
          "input_tokens": "Total usage unavailable: event stream is empty, truncated, contains unparsed lines, or includes a failed turn whose usage may be unreported",
          "output_tokens": "Total usage unavailable: event stream is empty, truncated, contains unparsed lines, or includes a failed turn whose usage may be unreported"
        }
      },
      "timed_out": false,
      "wall_time_seconds": 3.2654911860008724
    }
  ],
  "random_seed": 20261016,
  "reasoning_effort": "low",
  "repeats": 2,
  "repetitions": 2,
  "repositories": {
    "python": {
      "commit": "85568ed610998b0a253770b5d2e85dec8c6be75a",
      "path": "/workspace/Memglide/.local/benchmarks/improved-ab-final/repositories/python"
    },
    "typescript": {
      "commit": "0de302a024de06e8a9b28de14e87ee557f57e42f",
      "path": "/workspace/Memglide/.local/benchmarks/improved-ab-final/repositories/typescript"
    }
  },
  "resource_scope": "Local execution host; model inference resources are not exposed",
  "source_unchanged_during_experiment": true,
  "started_at": "2026-10-16T17:10:28.916987+00:00",
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
| Planned runs | 48 | 48 |
| Attempted runs | 0 | 0 |
| Not run | 48 | 48 |
| Graded runs | 0 | 0 |
| Successful runs | 0 | 0 |
| Failed grades | 0 | 0 |
| Ungraded attempts | 0 | 0 |
| Task completion rate | unavailable | unavailable |
| Invalid treatment runs | 0 | 0 |
| Unknown treatment runs | 0 | 0 |
| Actual provider cost per success (USD) | unavailable | unavailable |
| Computed pricing cost per success (USD) | unavailable | unavailable |

Cost per success includes all attempted-run costs, including failures. It is unavailable when any attempted-run cost is missing or no task succeeds.

## Measurements

Means/medians include observed values only. Coverage columns show observed n / missing among attempted runs / missing among all planned runs. Totals are withheld when coverage is incomplete and for non-additive metrics.

| Metric | A mean | A median | A n / attempted missing / planned missing | A total | B mean | B median | B n / attempted missing / planned missing | B total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| input_tokens | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| cached_input_tokens | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| output_tokens | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| model_calls | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| mcp_calls | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| memglide_mcp_calls | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| observed_mcp_calls | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| observed_memglide_mcp_calls | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| wall_time_seconds | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| end_to_end_wall_seconds | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| setup_wall_seconds | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| setup_cpu_seconds | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| repeated_file_reads | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| observed_file_read_commands | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| observed_repeated_read_commands | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| actual_cost_usd | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| computed_cost_usd | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| process_tree_peak_rss_bytes | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| cpu_seconds | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| memglide_cpu_seconds | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| context_freshness | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| retrieval_completeness | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 / 0 / 48 | unavailable | unavailable | unavailable | 0 / 0 / 48 | unavailable |

## Individual runs

| Task | Config | Repeat | Order | Status | Grader success | MCP calls | Memglide calls | Treatment valid | Input | Cached | Output | Seconds | Errors |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| ts-selective-retry | B | 1 | 1 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-selective-retry | A | 1 | 2 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-lru-eviction | B | 1 | 3 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-lru-eviction | A | 1 | 4 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-selective-retry | B | 1 | 5 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-selective-retry | A | 1 | 6 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-boolean-config | B | 1 | 7 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-boolean-config | A | 1 | 8 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-billing-rounding | B | 1 | 9 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-billing-rounding | A | 1 | 10 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | A | 1 | 11 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | B | 1 | 12 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-and-search | B | 1 | 13 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-and-search | A | 1 | 14 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | B | 1 | 15 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | A | 1 | 16 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | B | 1 | 17 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | A | 1 | 18 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | A | 1 | 19 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | B | 1 | 20 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | A | 1 | 21 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | B | 1 | 22 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | A | 1 | 23 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | B | 1 | 24 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-boolean-config | B | 1 | 25 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-boolean-config | A | 1 | 26 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | A | 1 | 27 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | B | 1 | 28 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-idempotent-events | B | 1 | 29 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-idempotent-events | A | 1 | 30 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | A | 1 | 31 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | B | 1 | 32 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-storage-containment | A | 1 | 33 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-storage-containment | B | 1 | 34 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | B | 1 | 35 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | A | 1 | 36 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-and-search | A | 1 | 37 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-and-search | B | 1 | 38 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | A | 1 | 39 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | B | 1 | 40 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | B | 1 | 41 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | A | 1 | 42 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | B | 1 | 43 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | A | 1 | 44 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-storage-containment | B | 1 | 45 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-storage-containment | A | 1 | 46 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-scope-authorization | A | 1 | 47 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-scope-authorization | B | 1 | 48 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-selective-retry | A | 2 | 49 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-selective-retry | B | 2 | 50 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-lru-eviction | A | 2 | 51 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-lru-eviction | B | 2 | 52 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-selective-retry | A | 2 | 53 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-selective-retry | B | 2 | 54 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-boolean-config | A | 2 | 55 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-boolean-config | B | 2 | 56 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-billing-rounding | A | 2 | 57 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-billing-rounding | B | 2 | 58 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | B | 2 | 59 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | A | 2 | 60 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-and-search | A | 2 | 61 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-and-search | B | 2 | 62 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | A | 2 | 63 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | B | 2 | 64 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | A | 2 | 65 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | B | 2 | 66 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | B | 2 | 67 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | A | 2 | 68 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | B | 2 | 69 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | A | 2 | 70 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | B | 2 | 71 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | A | 2 | 72 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-boolean-config | A | 2 | 73 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-boolean-config | B | 2 | 74 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | B | 2 | 75 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | A | 2 | 76 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-idempotent-events | A | 2 | 77 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-idempotent-events | B | 2 | 78 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | B | 2 | 79 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | A | 2 | 80 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-storage-containment | B | 2 | 81 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-storage-containment | A | 2 | 82 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | A | 2 | 83 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | B | 2 | 84 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-and-search | B | 2 | 85 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-and-search | A | 2 | 86 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | B | 2 | 87 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | A | 2 | 88 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | A | 2 | 89 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | B | 2 | 90 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | A | 2 | 91 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | B | 2 | 92 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-storage-containment | A | 2 | 93 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| ts-storage-containment | B | 2 | 94 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-scope-authorization | B | 2 | 95 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |
| py-scope-authorization | A | 2 | 96 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl |

### Per-run costs, reads, and local overhead

CPU values are sampled process CPU seconds (an observed lower bound); RSS values are sampled peaks in bytes. Short-lived processes may be missed. RSS may count shared pages more than once. Process-tree measurements include Codex and its observed children. Memglide-specific measurements cover only processes identified by the runner. Actual read counts are unavailable; command-intent proxy metrics appear separately.

| Task / configuration / repeat | Model calls | Repeated reads | Actual USD | Computed USD | Tree peak RSS | Tree CPU sec | Memglide peak RSS | Memglide CPU sec | Freshness | Completeness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ts-selective-retry / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-selective-retry / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-lru-eviction / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-lru-eviction / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-selective-retry / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-selective-retry / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-boolean-config / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-boolean-config / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-billing-rounding / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-billing-rounding / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-transitive-dependencies / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-transitive-dependencies / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-and-search / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-and-search / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-cursor-pagination / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-cursor-pagination / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-idempotent-events / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-idempotent-events / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-ttl-boundary / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-ttl-boundary / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-optimistic-revision / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-optimistic-revision / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-boolean-config / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-boolean-config / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-transitive-dependencies / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-transitive-dependencies / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-idempotent-events / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-idempotent-events / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-optimistic-revision / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-optimistic-revision / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-storage-containment / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-storage-containment / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-cursor-pagination / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-cursor-pagination / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-and-search / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-and-search / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-billing-rounding / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-billing-rounding / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-lru-eviction / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-lru-eviction / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-storage-containment / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-storage-containment / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-scope-authorization / A / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-scope-authorization / B / 1 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-selective-retry / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-selective-retry / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-lru-eviction / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-lru-eviction / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-selective-retry / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-selective-retry / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-boolean-config / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-boolean-config / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-billing-rounding / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-billing-rounding / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-transitive-dependencies / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-transitive-dependencies / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-and-search / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-and-search / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-cursor-pagination / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-cursor-pagination / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-ttl-boundary / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-idempotent-events / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-idempotent-events / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-ttl-boundary / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-ttl-boundary / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-optimistic-revision / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-optimistic-revision / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-boolean-config / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-boolean-config / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-transitive-dependencies / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-transitive-dependencies / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-idempotent-events / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-idempotent-events / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-optimistic-revision / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-optimistic-revision / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-storage-containment / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-storage-containment / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-cursor-pagination / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-cursor-pagination / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-and-search / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-and-search / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-billing-rounding / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-billing-rounding / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-lru-eviction / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-lru-eviction / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-scope-authorization / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-storage-containment / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ts-storage-containment / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-scope-authorization / B / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| py-scope-authorization / A / 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |

### MCP invocation evidence

Calls are deduplicated by CLI item ID across started/updated/completed events. A call that starts and fails is still an observed invocation. Enabled server configuration alone does not establish invocation.

No MCP invocations are present in the available raw event streams.

## Paired differences

Verified attempted A/B pairs: **0**. Differences are B minus A. Failed tasks remain in paired observations.

| Metric | Mean difference | Median difference | Pairs with measurements | Missing |
| --- | ---: | ---: | ---: | ---: |
| input_tokens | unavailable | unavailable | 0 | 0 |
| cached_input_tokens | unavailable | unavailable | 0 | 0 |
| output_tokens | unavailable | unavailable | 0 | 0 |
| model_calls | unavailable | unavailable | 0 | 0 |
| mcp_calls | unavailable | unavailable | 0 | 0 |
| memglide_mcp_calls | unavailable | unavailable | 0 | 0 |
| observed_mcp_calls | unavailable | unavailable | 0 | 0 |
| observed_memglide_mcp_calls | unavailable | unavailable | 0 | 0 |
| wall_time_seconds | unavailable | unavailable | 0 | 0 |
| end_to_end_wall_seconds | unavailable | unavailable | 0 | 0 |
| setup_wall_seconds | unavailable | unavailable | 0 | 0 |
| setup_cpu_seconds | unavailable | unavailable | 0 | 0 |
| repeated_file_reads | unavailable | unavailable | 0 | 0 |
| observed_file_read_commands | unavailable | unavailable | 0 | 0 |
| observed_repeated_read_commands | unavailable | unavailable | 0 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 | 0 |
| computed_cost_usd | unavailable | unavailable | 0 | 0 |
| process_tree_peak_rss_bytes | unavailable | unavailable | 0 | 0 |
| cpu_seconds | unavailable | unavailable | 0 | 0 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 | 0 |
| memglide_cpu_seconds | unavailable | unavailable | 0 | 0 |
| context_freshness | unavailable | unavailable | 0 | 0 |
| retrieval_completeness | unavailable | unavailable | 0 | 0 |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 | 0 |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 | 0 |

Excluded pairs (still retained in the individual and overall results):

- ts-selective-retry repeat 1: Both configurations must be attempted with verified treatment
- py-lru-eviction repeat 1: Both configurations must be attempted with verified treatment
- py-selective-retry repeat 1: Both configurations must be attempted with verified treatment
- ts-boolean-config repeat 1: Both configurations must be attempted with verified treatment
- py-billing-rounding repeat 1: Both configurations must be attempted with verified treatment
- py-transitive-dependencies repeat 1: Both configurations must be attempted with verified treatment
- ts-and-search repeat 1: Both configurations must be attempted with verified treatment
- py-cursor-pagination repeat 1: Both configurations must be attempted with verified treatment
- py-ttl-boundary repeat 1: Both configurations must be attempted with verified treatment
- ts-idempotent-events repeat 1: Both configurations must be attempted with verified treatment
- ts-ttl-boundary repeat 1: Both configurations must be attempted with verified treatment
- ts-optimistic-revision repeat 1: Both configurations must be attempted with verified treatment
- py-boolean-config repeat 1: Both configurations must be attempted with verified treatment
- ts-transitive-dependencies repeat 1: Both configurations must be attempted with verified treatment
- py-idempotent-events repeat 1: Both configurations must be attempted with verified treatment
- py-optimistic-revision repeat 1: Both configurations must be attempted with verified treatment
- py-storage-containment repeat 1: Both configurations must be attempted with verified treatment
- ts-cursor-pagination repeat 1: Both configurations must be attempted with verified treatment
- py-and-search repeat 1: Both configurations must be attempted with verified treatment
- ts-billing-rounding repeat 1: Both configurations must be attempted with verified treatment
- ts-lru-eviction repeat 1: Both configurations must be attempted with verified treatment
- ts-scope-authorization repeat 1: Both configurations must be attempted with verified treatment
- ts-storage-containment repeat 1: Both configurations must be attempted with verified treatment
- py-scope-authorization repeat 1: Both configurations must be attempted with verified treatment
- ts-selective-retry repeat 2: Both configurations must be attempted with verified treatment
- py-lru-eviction repeat 2: Both configurations must be attempted with verified treatment
- py-selective-retry repeat 2: Both configurations must be attempted with verified treatment
- ts-boolean-config repeat 2: Both configurations must be attempted with verified treatment
- py-billing-rounding repeat 2: Both configurations must be attempted with verified treatment
- py-transitive-dependencies repeat 2: Both configurations must be attempted with verified treatment
- ts-and-search repeat 2: Both configurations must be attempted with verified treatment
- py-cursor-pagination repeat 2: Both configurations must be attempted with verified treatment
- py-ttl-boundary repeat 2: Both configurations must be attempted with verified treatment
- ts-idempotent-events repeat 2: Both configurations must be attempted with verified treatment
- ts-ttl-boundary repeat 2: Both configurations must be attempted with verified treatment
- ts-optimistic-revision repeat 2: Both configurations must be attempted with verified treatment
- py-boolean-config repeat 2: Both configurations must be attempted with verified treatment
- ts-transitive-dependencies repeat 2: Both configurations must be attempted with verified treatment
- py-idempotent-events repeat 2: Both configurations must be attempted with verified treatment
- py-optimistic-revision repeat 2: Both configurations must be attempted with verified treatment
- py-storage-containment repeat 2: Both configurations must be attempted with verified treatment
- ts-cursor-pagination repeat 2: Both configurations must be attempted with verified treatment
- py-and-search repeat 2: Both configurations must be attempted with verified treatment
- ts-billing-rounding repeat 2: Both configurations must be attempted with verified treatment
- ts-lru-eviction repeat 2: Both configurations must be attempted with verified treatment
- ts-scope-authorization repeat 2: Both configurations must be attempted with verified treatment
- ts-storage-containment repeat 2: Both configurations must be attempted with verified treatment
- py-scope-authorization repeat 2: Both configurations must be attempted with verified treatment

## Failures and treatment fidelity

- ts-selective-retry / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-selective-retry / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-lru-eviction / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-lru-eviction / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-selective-retry / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-selective-retry / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-boolean-config / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-boolean-config / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-billing-rounding / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-billing-rounding / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-and-search / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-and-search / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-cursor-pagination / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-cursor-pagination / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-ttl-boundary / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-ttl-boundary / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-idempotent-events / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-idempotent-events / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-boolean-config / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-boolean-config / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-idempotent-events / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-idempotent-events / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-optimistic-revision / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-optimistic-revision / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-storage-containment / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-storage-containment / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-and-search / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-and-search / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-billing-rounding / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-billing-rounding / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-lru-eviction / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-lru-eviction / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-scope-authorization / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-scope-authorization / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-storage-containment / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-storage-containment / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-scope-authorization / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-scope-authorization / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-selective-retry / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-selective-retry / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-lru-eviction / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-lru-eviction / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-selective-retry / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-selective-retry / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-boolean-config / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-boolean-config / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-billing-rounding / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-billing-rounding / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-and-search / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-and-search / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-cursor-pagination / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-cursor-pagination / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-ttl-boundary / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-ttl-boundary / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-idempotent-events / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-idempotent-events / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-boolean-config / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-boolean-config / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-idempotent-events / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-idempotent-events / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-optimistic-revision / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-optimistic-revision / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-storage-containment / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-storage-containment / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-and-search / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-and-search / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-billing-rounding / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-billing-rounding / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-lru-eviction / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-lru-eviction / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-scope-authorization / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-scope-authorization / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-storage-containment / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- ts-storage-containment / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-scope-authorization / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl
- py-scope-authorization / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/improved-ab-final/preflight/stderr.log and events.jsonl

## Evidence and limitations

- No savings claim follows from a shorter response or fewer returned context characters.
- Completed Codex turns are not the number of underlying model/API calls.
- Absent provider invoiced cost is null. Computed list-price cost, if supplied, is separate.
- Metric averages and medians use observed values; n and missing counts accompany them.
- Failed and ungraded attempts remain in completion-rate and cost-per-success accounting.
- Actual repeated filesystem reads are unavailable. Observed read-command fields are heuristics for command intent, not actual I/O measurements or guaranteed I/O lower bounds.
- MCP invocation is checked from tool events, independent of model self-report.
- B treatment fidelity requires a completed, error-free Memglide get_context result; failed calls and calls to other tools do not verify retrieval treatment.
- MCP total counts are withheld for incomplete event streams; observed counts are lower bounds.
- Retrieval completeness and freshness require separate ground-truth observations; null is unknown.
- Independent target-path/symbol coverage probes are labelled proxies; they do not measure semantic completeness or establish what source context the coding model used.
- Sampled process CPU is an observed lower bound; sampled RSS peaks may miss short-lived processes and count shared pages repeatedly. Remote inference resources are unavailable.
- A/B prompt caching cannot generally be reset at the provider; run order and observed cached tokens matter.
- Synthetic fixture tasks do not establish performance on arbitrary production repositories.

Full per-run grader output, raw-event paths, process measurements, unavailable reasons, and task definitions are retained in the accompanying JSON report.
