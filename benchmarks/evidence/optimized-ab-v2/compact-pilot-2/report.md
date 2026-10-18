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
  "experiment_version": 2,
  "finished_at": "2026-10-17T23:00:53.851835+00:00",
  "frozen_manifest": {
    "common_instructions_sha256": "9bf1ac8fd96ab9457aeeb20fa4e2b18d9b066660358d97d58a29d64450c6a55e",
    "files": {
      "benchmarks/compare_components.py": "c9c0b463068a7fc679e4387566daeefc82b556b789c0de98b568880b13aea89e",
      "benchmarks/context_audit_v2.py": "d473d241237364b08f228e3f6ea7092d414bcb2ce9b347c9918a967ee95a3a4a",
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
      "benchmarks/reporting.py": "3e1d1c86cf0d091db7d7e04576110687e267de025397e6ef87c9a0d319577c8e",
      "benchmarks/run.py": "ccf8d44ca7ea8286a8a9241b030eaa76ca339ec15032aeb95cb4e256ef500a26",
      "benchmarks/run_v2.py": "eaa1d36af3796bf54de4137fd406af2fa3233421855e49628644e9572a358c69",
      "benchmarks/tasks.json": "5a921674ff669ebe09af08c06b9bb95ea597ff051ddcddb3312ce9508affe185",
      "benchmarks/telemetry.py": "21a6fa239c25ab1fb417aa7042f3f4e8412ef941172d1dfc42ec0d5895c6cc52",
      "pyproject.toml": "fef0be39ee002efcd53f7388f821ab9a8199f74fc23f4854c70743c8641d1ab4",
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "11729dc77f84f912d2b0e2998ce885b45e28c7c0330925dc48f1af15dc1a5fb4",
      "src/memglide/cli.py": "ebdc8c3e647af25afca6ab2a53c372fea7c6578541770ad4b3e8540aad04a691",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/agent_context.py": "3969dc826768da0718608e869aa8cdb8c2d7d2da62cf4b3cae77e8f65c2f7fb9",
      "src/memglide/core/context.py": "7b0c94938cfaeaff843d9c013c91d885747cecf73626317b3ca5acc607c4ac53",
      "src/memglide/core/indexer.py": "8b84cd28858dd16c36b4ddf25edb62391721e6874fa0deb68dd48dd01bb50621",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "1d3f015454fd096ced74f6239ada586ba77490738cf62697e676157fe843152c",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "aa810dd1f7e1bfa30b4f20a2b49515a93282ff68ca931c914126ee6549e644d5",
      "src/memglide/integrations/mcp_server.py": "b5398c1480e0074ceb22519624834c34f79b71d63e652ed3d499a91d07523831",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "82ff4f79c32dd2281026057098c9cffb872038640fa5ac387b1bd1ab6a5ab1d1",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "6dd6f33a5adc3863ff68d6125296c84c32170085c9c20eb53c8809f02a4c2a7b",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "38a483c6e05758a8f7df743ce7965a0fe20b6ea5f13c4921788b61efa971f58e",
      "uv.lock": "89bcc0d7a1c76ece1b91aaaa39ab108f819d1268d8d27bc60890abad124306f0"
    },
    "git_head": "e6e10a8f588c9236c7303a83780219d027a1c702",
    "prompt_sha256": {
      "py-ttl-boundary": "66a47d4518c1a8b312d24900d8a81bab95f895916ec2adf41246a99dff37100a"
    },
    "settings": {
      "codex_executable": "/opt/codex/bin/codex",
      "codex_home_binding_directory": "/workspace/Memglide/.local/codex-device-login-NlwVLVWg",
      "codex_version": "codex-cli 0.159.2",
      "corpus": "legacy",
      "effort": "low",
      "limit": 1,
      "model": "gpt-6.1-sol",
      "repeats": 1,
      "require_verification": false,
      "seed": 20261017,
      "skip_preflight": false,
      "timeout": 180.0
    }
  },
  "last_checkpoint_at": "2026-10-17T23:00:53.839321+00:00",
  "logical_cpu_count": 5,
  "memglide_source_after": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-17T23:00:53.867792+00:00",
    "git_head": "e6e10a8f588c9236c7303a83780219d027a1c702",
    "measurement_files": {
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state",
    "source_dirty_entries": [
      " M src/memglide/cli.py",
      " M src/memglide/core/context.py",
      " M src/memglide/core/indexer.py",
      " M src/memglide/integrations/codex.py",
      " M src/memglide/integrations/mcp_server.py",
      "?? src/memglide/core/agent_context.py"
    ],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "11729dc77f84f912d2b0e2998ce885b45e28c7c0330925dc48f1af15dc1a5fb4",
      "src/memglide/cli.py": "ebdc8c3e647af25afca6ab2a53c372fea7c6578541770ad4b3e8540aad04a691",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/agent_context.py": "3969dc826768da0718608e869aa8cdb8c2d7d2da62cf4b3cae77e8f65c2f7fb9",
      "src/memglide/core/context.py": "7b0c94938cfaeaff843d9c013c91d885747cecf73626317b3ca5acc607c4ac53",
      "src/memglide/core/indexer.py": "8b84cd28858dd16c36b4ddf25edb62391721e6874fa0deb68dd48dd01bb50621",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "1d3f015454fd096ced74f6239ada586ba77490738cf62697e676157fe843152c",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "aa810dd1f7e1bfa30b4f20a2b49515a93282ff68ca931c914126ee6549e644d5",
      "src/memglide/integrations/mcp_server.py": "b5398c1480e0074ceb22519624834c34f79b71d63e652ed3d499a91d07523831",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "82ff4f79c32dd2281026057098c9cffb872038640fa5ac387b1bd1ab6a5ab1d1",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "6dd6f33a5adc3863ff68d6125296c84c32170085c9c20eb53c8809f02a4c2a7b",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "38a483c6e05758a8f7df743ce7965a0fe20b6ea5f13c4921788b61efa971f58e"
    },
    "source_tree_sha256": "5e867d309e0a24a3e52f15a1e40b837dc7a228074380a4aaa3b1419b989856f3"
  },
  "memglide_source_before": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-17T23:00:08.409063+00:00",
    "git_head": "e6e10a8f588c9236c7303a83780219d027a1c702",
    "measurement_files": {
      "benchmarks/corpus.py": "691e5c1f0122c8c9be685e9949e2a64a1e544fcc36ab35a92461a2b44953197c",
      "benchmarks/probe.py": "54a1520c39b9385904328445a253e6d1831cecb043165612afba1bdb377701d0"
    },
    "scope": "On-disk public Python source at capture time, not a proof of earlier runtime state",
    "source_dirty_entries": [
      " M src/memglide/cli.py",
      " M src/memglide/core/context.py",
      " M src/memglide/core/indexer.py",
      " M src/memglide/integrations/codex.py",
      " M src/memglide/integrations/mcp_server.py",
      "?? src/memglide/core/agent_context.py"
    ],
    "source_files": {
      "src/memglide/__init__.py": "2892ab3612d318a128ceb8996e9d91ce6a2d8ec71bde7a055c9551579c2d0896",
      "src/memglide/__main__.py": "04d6a5692ef6d9a9c21343ce931fd8cb1da94f71f85770a8f08e4cab87a78637",
      "src/memglide/api/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/api/app.py": "11729dc77f84f912d2b0e2998ce885b45e28c7c0330925dc48f1af15dc1a5fb4",
      "src/memglide/cli.py": "ebdc8c3e647af25afca6ab2a53c372fea7c6578541770ad4b3e8540aad04a691",
      "src/memglide/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/core/agent_context.py": "3969dc826768da0718608e869aa8cdb8c2d7d2da62cf4b3cae77e8f65c2f7fb9",
      "src/memglide/core/context.py": "7b0c94938cfaeaff843d9c013c91d885747cecf73626317b3ca5acc607c4ac53",
      "src/memglide/core/indexer.py": "8b84cd28858dd16c36b4ddf25edb62391721e6874fa0deb68dd48dd01bb50621",
      "src/memglide/core/parsing.py": "75984e1fec6e56e889bbeb0d344c16b9a1b9b793aabae8fd34fcec7a241012b4",
      "src/memglide/core/query.py": "1d3f015454fd096ced74f6239ada586ba77490738cf62697e676157fe843152c",
      "src/memglide/core/watcher.py": "c851302b1d47c45b7742fa8fed69b500ade914e03f3cc6a33a985badd64f1511",
      "src/memglide/integrations/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/integrations/codex.py": "aa810dd1f7e1bfa30b4f20a2b49515a93282ff68ca931c914126ee6549e644d5",
      "src/memglide/integrations/mcp_server.py": "b5398c1480e0074ceb22519624834c34f79b71d63e652ed3d499a91d07523831",
      "src/memglide/memory/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/memory/engine.py": "82ff4f79c32dd2281026057098c9cffb872038640fa5ac387b1bd1ab6a5ab1d1",
      "src/memglide/security/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/security/paths.py": "3b75ec6217650eaecad4344cf614e4d73e2e7c5b5a1b98cd8a51272c733fcd38",
      "src/memglide/service.py": "6dd6f33a5adc3863ff68d6125296c84c32170085c9c20eb53c8809f02a4c2a7b",
      "src/memglide/storage/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "src/memglide/storage/database.py": "38a483c6e05758a8f7df743ce7965a0fe20b6ea5f13c4921788b61efa971f58e"
    },
    "source_tree_sha256": "5e867d309e0a24a3e52f15a1e40b837dc7a228074380a4aaa3b1419b989856f3"
  },
  "methodology": {
    "caching": "Counterbalanced paired order reverses on repeat 2; fresh local state. Provider/OS caches cannot be reset; cached tokens are observed separately",
    "context_audit": "Independent source-file hash snapshot after Codex exit and before grader/build mutations; a point observation, not call-time freshness or semantic completeness. Own-edit mismatches do not fail coding grades. Audit time is recorded separately outside Codex timing",
    "cost": "No invoice/cost or underlying model-call telemetry is estimated",
    "durability": "Atomic fsynced checkpoints and immutable hash-chained attempt log; interrupted originals retained; distinct supplemental retries excluded from original comparison",
    "isolation": "Fresh worktree from each task's frozen repository commit, process/session/database per arm",
    "prompt": "Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.\nIf Memglide MCP tools are available, use fetch_context once with your task query before editing. Reuse complete returned source instead of reading it again unless additional evidence is needed. Use verify_context only if you are uncertain whether another process changed the source or need to validate older context before using it again. Your own edits make earlier context stale; a final verification is not required. Otherwise use ordinary source tools. Do not claim token or cost savings.\n",
    "repositories": "Development pilot on the earlier two-fixture corpus; excluded from the fresh 40-task experiment",
    "settings": "Same model, effort, schema, workspace-write sandbox, global approval never and common prompt; only scoped MCP availability differs",
    "timing": "CLI wall time plus B's required fresh index equals end-to-end time; external graders/readiness excluded",
    "treatment": "B requires actual compact source retrieval. Verification is optional and on demand; invocation evidence does not establish chronology relative to final edits. A has no configured MCP servers"
  },
  "model": "gpt-6.1-sol",
  "output_directory": "/workspace/Memglide/.local/optimization-v2/compact-pilot-2",
  "preflight_complete": true,
  "preflight_runs": [
    {
      "artifacts": "/workspace/Memglide/.local/optimization-v2/compact-pilot-2/preflight",
      "exit_code": 0,
      "overhead": {
        "cpu_seconds": 2.4099999999999997,
        "memglide_cpu_seconds": null,
        "memglide_peak_rss_bytes": null,
        "method": "/proc sampling; CPU observed lower bound, RSS shared pages can be counted multiple times; short-lived processes may be missed",
        "observed_memglide_processes": 0,
        "observed_processes": 7,
        "process_tree_peak_rss_bytes": 104206336,
        "samples": 80,
        "sampling_interval_seconds": 0.05,
        "scope": "Local Codex process tree only; remote model CPU and memory unavailable"
      },
      "scope": "Readiness only; excluded from task comparison",
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
        "memglide_successful_fetch_context_count": 0,
        "memglide_successful_get_context_count": 0,
        "memglide_successful_verify_context_count": 0,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": 8960,
          "input_tokens": 10955,
          "output_tokens": 36
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
          "cached_input_tokens": 8960,
          "input_tokens": 10955,
          "output_tokens": 36
        },
        "usage_coverage_complete": true,
        "usage_scope": "Complete parsed stream only; partial observed turn usage is stored separately",
        "usage_unavailable_reasons": {}
      },
      "timed_out": false,
      "wall_time_seconds": 4.909132968999984
    }
  ],
  "preflight_started_at": "2026-10-17T23:00:08.731138+00:00",
  "random_seed": 20261017,
  "reasoning_effort": "low",
  "repeats": 1,
  "repetitions": 1,
  "repositories": {
    "atlas-python-v1": {
      "commit": "28df2f323ab1b5807e880b0cbb2e2f5e10669edd",
      "path": "/workspace/Memglide/.local/optimization-v2/compact-pilot-2/repositories/atlas-python-v1",
      "tree": "b186ecdf768189c8aa2d7f2d0ef94cdc21647e3f"
    }
  },
  "resource_scope": "Local execution host; model inference resources are not exposed",
  "resume_count": 0,
  "source_unchanged_during_experiment": true,
  "started_at": "2026-10-17T23:00:08.394923+00:00",
  "supplemental_attempt_count": 0,
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
| input_tokens | 48601 | 48601 | 1 / 0 / 0 | 48601 | 71063 | 71063 | 1 / 0 / 0 | 71063 |
| cached_input_tokens | 43648 | 43648 | 1 / 0 / 0 | 43648 | 42112 | 42112 | 1 / 0 / 0 | 42112 |
| output_tokens | 934 | 934 | 1 / 0 / 0 | 934 | 995 | 995 | 1 / 0 / 0 | 995 |
| model_calls | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 1 | 1 | 1 / 0 / 0 | 1 |
| memglide_mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 1 | 1 | 1 / 0 / 0 | 1 |
| observed_mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 1 | 1 | 1 / 0 / 0 | 1 |
| observed_memglide_mcp_calls | 0 | 0 | 1 / 0 / 0 | 0 | 1 | 1 | 1 / 0 / 0 | 1 |
| wall_time_seconds | 17.2723 | 17.2723 | 1 / 0 / 0 | 17.2723 | 22.0038 | 22.0038 | 1 / 0 / 0 | 22.0038 |
| end_to_end_wall_seconds | 17.2723 | 17.2723 | 1 / 0 / 0 | 17.2723 | 22.1067 | 22.1067 | 1 / 0 / 0 | 22.1067 |
| setup_wall_seconds | unavailable | unavailable | 0 / 1 / 1 | unavailable | 0.102863 | 0.102863 | 1 / 0 / 0 | 0.102863 |
| setup_cpu_seconds | unavailable | unavailable | 0 / 1 / 1 | unavailable | 0.0542549 | 0.0542549 | 1 / 0 / 0 | 0.0542549 |
| repeated_file_reads | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| observed_file_read_commands | 1 | 1 | 1 / 0 / 0 | 1 | 1 | 1 | 1 / 0 / 0 | 1 |
| observed_repeated_read_commands | 0 | 0 | 1 / 0 / 0 | 0 | 0 | 0 | 1 / 0 / 0 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| computed_cost_usd | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| process_tree_peak_rss_bytes | 190730240 | 190730240 | 1 / 0 / 0 | unavailable | 271118336 | 271118336 | 1 / 0 / 0 | unavailable |
| cpu_seconds | 2.92 | 2.92 | 1 / 0 / 0 | 2.92 | 4.69 | 4.69 | 1 / 0 / 0 | 4.69 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 / 1 / 1 | unavailable | 72273920 | 72273920 | 1 / 0 / 0 | unavailable |
| memglide_cpu_seconds | unavailable | unavailable | 0 / 1 / 1 | unavailable | 1.76 | 1.76 | 1 / 0 / 0 | 1.76 |
| context_freshness | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| retrieval_completeness | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 / 1 / 1 | unavailable | unavailable | unavailable | 0 / 1 / 1 | unavailable |

## Individual runs

| Task | Config | Repeat | Order | Status | Grader success | MCP calls | Memglide calls | Treatment valid | Input | Cached | Output | Seconds | Errors |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| py-ttl-boundary | B | 1 | 1 | completed | yes | 1 | 1 | yes | 71063 | 42112 | 995 | 22.0038 |  |
| py-ttl-boundary | A | 1 | 2 | completed | yes | 0 | 0 | yes | 48601 | 43648 | 934 | 17.2723 |  |

### Per-run costs, reads, and local overhead

CPU values are sampled process CPU seconds (an observed lower bound); RSS values are sampled peaks in bytes. Short-lived processes may be missed. RSS may count shared pages more than once. Process-tree measurements include Codex and its observed children. Memglide-specific measurements cover only processes identified by the runner. Actual read counts are unavailable; command-intent proxy metrics appear separately.

| Task / configuration / repeat | Model calls | Repeated reads | Actual USD | Computed USD | Tree peak RSS | Tree CPU sec | Memglide peak RSS | Memglide CPU sec | Freshness | Completeness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| py-ttl-boundary / B / 1 | unavailable | unavailable | unavailable | unavailable | 271118336 | 4.69 | 72273920 | 1.76 | unavailable | unavailable |
| py-ttl-boundary / A / 1 | unavailable | unavailable | unavailable | unavailable | 190730240 | 2.92 | unavailable | unavailable | unavailable | unavailable |

### MCP invocation evidence

Calls are deduplicated by CLI item ID across started/updated/completed events. A call that starts and fails is still an observed invocation. Enabled server configuration alone does not establish invocation.

- py-ttl-boundary / B / repeat 1: memglide.fetch_context (status=completed, completed=True)

## Paired differences

Verified attempted A/B pairs: **1**. Differences are B minus A. Failed tasks remain in paired observations.

| Metric | Mean difference | Median difference | Pairs with measurements | Missing |
| --- | ---: | ---: | ---: | ---: |
| input_tokens | 22462 | 22462 | 1 | 0 |
| cached_input_tokens | -1536 | -1536 | 1 | 0 |
| output_tokens | 61 | 61 | 1 | 0 |
| model_calls | unavailable | unavailable | 0 | 1 |
| mcp_calls | 1 | 1 | 1 | 0 |
| memglide_mcp_calls | 1 | 1 | 1 | 0 |
| observed_mcp_calls | 1 | 1 | 1 | 0 |
| observed_memglide_mcp_calls | 1 | 1 | 1 | 0 |
| wall_time_seconds | 4.73153 | 4.73153 | 1 | 0 |
| end_to_end_wall_seconds | 4.83439 | 4.83439 | 1 | 0 |
| setup_wall_seconds | unavailable | unavailable | 0 | 1 |
| setup_cpu_seconds | unavailable | unavailable | 0 | 1 |
| repeated_file_reads | unavailable | unavailable | 0 | 1 |
| observed_file_read_commands | 0 | 0 | 1 | 0 |
| observed_repeated_read_commands | 0 | 0 | 1 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 | 1 |
| computed_cost_usd | unavailable | unavailable | 0 | 1 |
| process_tree_peak_rss_bytes | 80388096 | 80388096 | 1 | 0 |
| cpu_seconds | 1.77 | 1.77 | 1 | 0 |
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
- Supplemental retries never replace interrupted original assignments or enter the primary A/B aggregates. The compact fetch_context alias counts as retrieval only with observed get_context operation, nonempty source snippets and source hashes. Verification policy is frozen and explicit per run: on demand by default; --require-verification requires both calls for an ablation. Server freshness assertions are not independent semantic completeness measurements.

Full per-run grader output, raw-event paths, process measurements, unavailable reasons, and task definitions are retained in the accompanying JSON report.
