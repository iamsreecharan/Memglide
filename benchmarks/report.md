# Memglide V1 verification and benchmark assessment

## Finding

**Tested application behavior works. A benefit over regular Codex has not been
established.** All 143 existing application tests passed. The final Python suite
also passed all 60 new benchmark checks: 186 Python tests plus 15 frontend and
two production browser tests, **203 distinct checks in total**. No application
fixes were needed. Ruff, mypy, TypeScript, Vite, frozen installs and package builds
passed. Repeated executions of a test are not counted as additional checks.

The reproducible A/B experiment has 24 tasks, two configurations and two
repetitions, for **96 planned coding runs**. The formal `codex exec` preflight
failed with HTTP 401 and: “Your access token could not be refreshed ... Please
sign in again.” It exited 1 after 2.257 measured seconds. **All 96 coding runs
remain `not_run`; no verified A/B pair exists.** This is an authentication
blocker, not 96 failed coding tasks. Token usage, model calls, task success,
actual cost and cost per successful task remain unavailable. No token or money
savings claim is supported.

Earlier diagnostic invocations failed on read-only Codex state, then proxy HTTP
403. Those failures are retained in [evidence](evidence/README.md). Fresh writable
per-invocation state referencing the existing authentication binding solved
startup. The latest request reached the provider but could not authenticate.
The earlier `chatgpt.com` network addition was saved to the cloud draft; that
does not establish an applied or published policy. Refresh Codex authentication,
review/save the network draft as needed, and run the documented experiment with
a fresh output directory. Do not supply credential values in chat or reports.

## Independent MCP measurements

The official MCP SDK executed **168 actual tool calls** across 24 isolated
worktrees and fresh databases. These were SDK component probes, not Codex B
invocations. All 24 transport/hash/freshness checks passed: returned evidence
hashes matched disk, a controlled comment edit made the previous passport stale,
and subsequent retrieval returned the updated hash and full-source edit marker.
This demonstrates tested source freshness; it does not establish coding success.

Natural whole-task queries at level 2 with an 8,000 estimated-token budget
returned the declared fix file in **16/24 cases (66.7%)**. Eight misses remain in
the report. Exact target-symbol identity matched in 8/24, and its declaration was
visible in a snippet in 15/24. Whole-file/class evidence can contain useful code
without matching a symbol identity. Conversely, a file hit or declaration does
not establish a complete method body or all necessary context. A model could
formulate a better query than these full-prompt probes; misses are not measured
coding failures.

Across the seven-call probe workflows, mean wall time was 5.1211 s (median
5.0498 s), excluding initial registration/indexing, whose mean was 0.2750 s.
Mean sampled server CPU was 4.8046 s and mean sampled peak summed RSS was
81,954,816 bytes. These include fresh server startup, multiple queries, controlled
edit and shutdown. They are not the cost of one query or incremental A/B
overhead. CPU is an observed sampled lower bound; short-lived processes can be
missed and shared RSS pages counted more than once. Full individual observations
and distributions are in the component report and accompanying JSON.

## Why natural retrieval missed the target

All eight targets existed in the candidate pool. They were omitted during
ranking/budget selection, with Partial passports and omitted-candidate warnings.
No indexing errors were reported for these queries.

| Task | Best target file/function candidate rank | Target symbol rank |
| --- | ---: | ---: |
| py-scope-authorization | 4 | 17 |
| py-storage-containment | 4 | 21 |
| py-transitive-dependencies | 9 | 35 |
| ts-scope-authorization | 7 | 19 |
| ts-storage-containment | 8 | 22 |
| ts-transitive-dependencies | 12 | 25 |
| ts-boolean-config | 9 | 20 |
| ts-and-search | 3 (function); 5 (file) | 3 |

The code gives a 75-point explicit-symbol boost to generic words such as
`Repository` and TypeScript `Document`, which occur in prompt boilerplate
“document-service repository” ([indexer.py](../src/memglide/core/indexer.py#L783)).
Selected broad classes therefore outrank small task-specific helpers. Search
ORs prompt terms, including generic instructions; tokenization has no stemming
and the context tokenizer handles identifiers differently from search.

Dependency metadata is repeated in the response, passport dependencies and
unresolved-dependency fields ([context.py](../src/memglide/core/context.py#L312)).
For `py-scope-authorization`, the retained natural response serialized to 23,695
UTF-8 JSON bytes: 3,456 raw snippet-text bytes and 12,643 serialized bytes across those dependency
blocks. Its estimate was 7,899/8,000 and 15 candidates were omitted. For
`ts-and-search`, 15,823 of 23,611 serialized bytes were dependency blocks (about
67%); raw snippet text used 2,260 bytes, the estimate was 7,871/8,000 and 21 candidates
were omitted. **These are serialized-byte counts and Memglide budget estimates,
not measured model tokens.** Greedy fitting skips candidates that add too much
source and graph metadata, and final pruning can remove more. This explains why
even a third-ranked target could disappear.

Rank analysis replayed the original fixture source in an in-memory copy of the
retained index after the controlled comment edit. It did not change persisted
data or rerun/tune the queries. Raw SDK responses are under
`.local/component-probe/runs/<task>/call-03-get_context.json`.

## Proposed improvements and further evaluation

1. Represent each dependency once, use compact identifiers/reference spans, and
   give graph metadata a separate budget. Reserve source capacity for direct
   matches before optional graph expansion and documentation.
2. Distinguish explicit code identifiers from ordinary prose when applying
   symbol boosts. Share identifier tokenization and handle common inflections.
   Evaluate concise task queries separately from full-prompt queries.
3. Validate changes against these eight misses and additional held-out tasks at
   fixed budgets. Retain this V1 result and report the changed version separately.
4. Extend the controlled synthetic corpus with independent production
   repositories and larger cross-file changes. The two translated fixture
   repositories and twelve task families are correlated and limit generalization.
5. Add a separate longitudinal cohort for prior-memory reuse with matched task
   histories, counting warm-up cost. Fresh B databases currently test retrieval
   and initialization, not reuse of earlier saved task memories.
6. Obtain provider usage/billing evidence for actual model-call count and cost,
   and use explicit filesystem tracing if exact repeated reads are required.
   Until then, these fields stay null; read-command intent remains a proxy.

These are proposed fixes and follow-up experiments. Their benefits have not been
measured. The current data cannot determine whether Memglide makes Codex coding
cheaper, faster, more reliable or worse overall.


## Detailed A/B experiment

No verified A/B coding pairs completed; performance and savings are undetermined.

A = standard Codex. B = same Codex settings with Memglide. Success is determined by the external grader. Missing measurements are `unavailable`, not zero.

## Protocol and environment

```json
{
  "blockers": [
    "Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl"
  ],
  "cgroup_v2_limits": {
    "cpu.max": "400000 100000",
    "memory.max": "34359738368",
    "memory.swap.max": "max",
    "pids.max": "max"
  },
  "codex_version": "codex-cli 0.159.2",
  "cpu_affinity_count": 5,
  "evidence_scope": "No completed live coding run. Component SDK invocations are not Codex B invocation evidence.",
  "finished_at": "2026-10-16T07:58:08.358248+00:00",
  "host_python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]",
  "logical_cpu_count": 5,
  "methodology": {
    "caching": "Fresh process/session/index per run; counterbalanced arm order. OS and provider caches are not flushable; cached input is recorded when exposed",
    "cost": "Actual cost and model-call count remain null unless provider telemetry exposes them; no token-price estimate is actual cost",
    "failed_runs": "All planned rows and attempted failures retained; common preflight blockers stop pointless repeats",
    "isolation": "Fresh detached Git worktree from the same per-language seed commit for every run",
    "memory_history": "Fresh databases test retrieval/index initialization; longitudinal prior-memory reuse is not measured.",
    "overhead": "Linux /proc samples local child processes; remote model resources unavailable",
    "prompt": "Implement the requested change in this repository. Inspect the current source and run relevant tests. Preserve existing tests and Git metadata; do not commit. Do not access files outside this repository except installed development tools. The final structured response is only a summary, not a grading result.\nIf memglide MCP tools are available, use list_projects, start_session and get_context before editing, inspect the source evidence you need, and revalidate the Context Passport after edits. Otherwise use ordinary source tools. Do not claim token or cost savings.\n",
    "repositories": "Two synthetic multi-module Python/TypeScript maintenance fixtures; external hidden oracles",
    "settings": "Same model, effort, output schema, sandbox and tool instructions; only Memglide MCP availability differs",
    "timing": "wall_time_seconds measures Codex process; B index timing is separate and included in end_to_end_wall_seconds. Independent readiness probes are excluded"
  },
  "model": "gpt-6.1-sol",
  "network_draft": {
    "added_domain": "chatgpt.com",
    "latest_observed_provider_response": "HTTP 401 authentication rejection",
    "publication": "not performed by agent",
    "runtime_application": "not established by draft save",
    "status": "saved"
  },
  "output_directory": "/workspace/Memglide/.local/benchmarks/ab-full-20261016",
  "platform": "linux",
  "preflight_runs": [
    {
      "artifacts": "/workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight",
      "exit_code": 1,
      "overhead": {
        "cpu_seconds": 1.46,
        "memglide_cpu_seconds": null,
        "memglide_peak_rss_bytes": null,
        "method": "/proc sampling; CPU observed lower bound, RSS shared pages can be counted multiple times; short-lived processes may be missed",
        "observed_memglide_processes": 0,
        "observed_processes": 2,
        "process_tree_peak_rss_bytes": 84066304,
        "samples": 37,
        "sampling_interval_seconds": 0.05,
        "scope": "Local Codex process tree only; remote model CPU and memory unavailable"
      },
      "retained_events": "benchmarks/evidence/formal-preflight.events.jsonl",
      "retained_stderr": "benchmarks/evidence/formal-preflight.stderr.log",
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
      "wall_time_seconds": 2.2568011739986105
    }
  ],
  "prior_diagnostic_invocations": [
    {
      "actual_cost_usd": null,
      "codex_exit_code": null,
      "diagnosis": "runtime_state_readonly",
      "events": "benchmarks/evidence/initial-readonly.events.jsonl",
      "id": "initial-readonly",
      "scope": "Setup diagnosis, excluded from coding task comparisons",
      "status": "diagnostic_failed",
      "stderr": "benchmarks/evidence/initial-readonly.stderr.log",
      "supervision": null,
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": null,
        "commands": [],
        "completed_turns": 0,
        "errors": [],
        "event_count": 0,
        "failed_turns": 0,
        "file_read_method": "Heuristic command-intent proxy from successful command_execution items containing literal cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, scripts, directory searches, MCP reads, and internal reads are excluded. A repeated command names a path recognized in an earlier command. This is not an I/O trace, an actual read count, or a guaranteed lower bound on filesystem reads.",
        "file_reads_complete": false,
        "mcp_call_count": null,
        "mcp_calls": [],
        "mcp_count_scope": "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound",
        "mcp_counts_complete": false,
        "memglide_get_context_success_unknown_count": null,
        "memglide_mcp_call_count": null,
        "memglide_successful_get_context_count": null,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": null,
          "input_tokens": null,
          "output_tokens": null
        },
        "observed_file_read_commands": null,
        "observed_read_command_paths": [],
        "observed_repeated_read_commands": null,
        "parse_errors": [],
        "repeated_file_reads": null,
        "repeated_file_reads_unavailable_reason": "Codex JSONL does not expose a filesystem I/O trace; command text cannot establish actual reads",
        "repeated_read_command_paths": {},
        "source": "codex exec --json; turn.completed usage and item lifecycle events",
        "stream_terminal": false,
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
      "wall_time_seconds": null
    },
    {
      "actual_cost_usd": null,
      "codex_exit_code": null,
      "diagnosis": "runtime_state_readonly",
      "events": "benchmarks/evidence/state-overrides-2.events.jsonl",
      "id": "state-overrides-2",
      "scope": "Setup diagnosis, excluded from coding task comparisons",
      "status": "diagnostic_failed",
      "stderr": "benchmarks/evidence/state-overrides-2.stderr.log",
      "supervision": null,
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": null,
        "commands": [],
        "completed_turns": 0,
        "errors": [],
        "event_count": 0,
        "failed_turns": 0,
        "file_read_method": "Heuristic command-intent proxy from successful command_execution items containing literal cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, scripts, directory searches, MCP reads, and internal reads are excluded. A repeated command names a path recognized in an earlier command. This is not an I/O trace, an actual read count, or a guaranteed lower bound on filesystem reads.",
        "file_reads_complete": false,
        "mcp_call_count": null,
        "mcp_calls": [],
        "mcp_count_scope": "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound",
        "mcp_counts_complete": false,
        "memglide_get_context_success_unknown_count": null,
        "memglide_mcp_call_count": null,
        "memglide_successful_get_context_count": null,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": null,
          "input_tokens": null,
          "output_tokens": null
        },
        "observed_file_read_commands": null,
        "observed_read_command_paths": [],
        "observed_repeated_read_commands": null,
        "parse_errors": [],
        "repeated_file_reads": null,
        "repeated_file_reads_unavailable_reason": "Codex JSONL does not expose a filesystem I/O trace; command text cannot establish actual reads",
        "repeated_read_command_paths": {},
        "source": "codex exec --json; turn.completed usage and item lifecycle events",
        "stream_terminal": false,
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
      "wall_time_seconds": null
    },
    {
      "actual_cost_usd": null,
      "codex_exit_code": null,
      "diagnosis": "runtime_state_readonly",
      "events": "benchmarks/evidence/state-overrides-3.events.jsonl",
      "id": "state-overrides-3",
      "scope": "Setup diagnosis, excluded from coding task comparisons",
      "status": "diagnostic_failed",
      "stderr": "benchmarks/evidence/state-overrides-3.stderr.log",
      "supervision": null,
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": null,
        "commands": [],
        "completed_turns": 0,
        "errors": [],
        "event_count": 0,
        "failed_turns": 0,
        "file_read_method": "Heuristic command-intent proxy from successful command_execution items containing literal cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, scripts, directory searches, MCP reads, and internal reads are excluded. A repeated command names a path recognized in an earlier command. This is not an I/O trace, an actual read count, or a guaranteed lower bound on filesystem reads.",
        "file_reads_complete": false,
        "mcp_call_count": null,
        "mcp_calls": [],
        "mcp_count_scope": "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound",
        "mcp_counts_complete": false,
        "memglide_get_context_success_unknown_count": null,
        "memglide_mcp_call_count": null,
        "memglide_successful_get_context_count": null,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": null,
          "input_tokens": null,
          "output_tokens": null
        },
        "observed_file_read_commands": null,
        "observed_read_command_paths": [],
        "observed_repeated_read_commands": null,
        "parse_errors": [],
        "repeated_file_reads": null,
        "repeated_file_reads_unavailable_reason": "Codex JSONL does not expose a filesystem I/O trace; command text cannot establish actual reads",
        "repeated_read_command_paths": {},
        "source": "codex exec --json; turn.completed usage and item lifecycle events",
        "stream_terminal": false,
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
      "wall_time_seconds": null
    },
    {
      "actual_cost_usd": null,
      "codex_exit_code": null,
      "diagnosis": "runtime_state_readonly",
      "events": "benchmarks/evidence/state-trace.events.jsonl",
      "id": "state-trace",
      "scope": "Setup diagnosis, excluded from coding task comparisons",
      "status": "diagnostic_failed",
      "stderr": "benchmarks/evidence/state-trace.stderr.log",
      "supervision": null,
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": null,
        "commands": [],
        "completed_turns": 0,
        "errors": [],
        "event_count": 0,
        "failed_turns": 0,
        "file_read_method": "Heuristic command-intent proxy from successful command_execution items containing literal cat, sed -n, head, tail, or rg commands with explicit file-like paths. Shell expansion, scripts, directory searches, MCP reads, and internal reads are excluded. A repeated command names a path recognized in an earlier command. This is not an I/O trace, an actual read count, or a guaranteed lower bound on filesystem reads.",
        "file_reads_complete": false,
        "mcp_call_count": null,
        "mcp_calls": [],
        "mcp_count_scope": "Observed unique invocation items; total only for complete parsed streams, otherwise a lower bound",
        "mcp_counts_complete": false,
        "memglide_get_context_success_unknown_count": null,
        "memglide_mcp_call_count": null,
        "memglide_successful_get_context_count": null,
        "model_calls": null,
        "model_calls_unavailable_reason": "Codex exec JSONL exposes completed turns, not underlying provider/API model calls",
        "observed_completed_turn_usage": {
          "cached_input_tokens": null,
          "input_tokens": null,
          "output_tokens": null
        },
        "observed_file_read_commands": null,
        "observed_read_command_paths": [],
        "observed_repeated_read_commands": null,
        "parse_errors": [],
        "repeated_file_reads": null,
        "repeated_file_reads_unavailable_reason": "Codex JSONL does not expose a filesystem I/O trace; command text cannot establish actual reads",
        "repeated_read_command_paths": {},
        "source": "codex exec --json; turn.completed usage and item lifecycle events",
        "stream_terminal": false,
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
      "wall_time_seconds": null
    },
    {
      "actual_cost_usd": null,
      "codex_exit_code": null,
      "diagnosis": "proxy_HTTP_CONNECT_403",
      "events": "benchmarks/evidence/proxy-denial.events.jsonl",
      "id": "proxy-denial",
      "scope": "Setup diagnosis, excluded from coding task comparisons",
      "status": "diagnostic_failed",
      "stderr": "benchmarks/evidence/proxy-denial.stderr.log",
      "supervision": "Stopped by a configured 50-second supervisor timeout; actual elapsed time was not recorded",
      "telemetry": {
        "actual_cost_unavailable_reason": "Codex exec JSONL does not emit provider invoiced cost",
        "actual_cost_usd": null,
        "command_count": 0,
        "commands": [],
        "completed_turns": 0,
        "errors": [
          {
            "message": "Reconnecting... 2/5 (stream disconnected before completion: URL error: Proxy connection failed: HTTP CONNECT failed with status 403)",
            "type": "error"
          },
          {
            "message": "Reconnecting... 3/5 (stream disconnected before completion: URL error: Proxy connection failed: HTTP CONNECT failed with status 403)",
            "type": "error"
          },
          {
            "message": "Reconnecting... 4/5 (stream disconnected before completion: URL error: Proxy connection failed: HTTP CONNECT failed with status 403)",
            "type": "error"
          },
          {
            "message": "Reconnecting... 5/5 (stream disconnected before completion: URL error: Proxy connection failed: HTTP CONNECT failed with status 403)",
            "type": "error"
          },
          {
            "message": "Reconnecting... waiting for network (Connection failed: error sending request)",
            "type": "error"
          },
          {
            "message": "Reconnecting... waiting for network (Connection failed: error sending request)",
            "type": "error"
          },
          {
            "message": "Reconnecting... waiting for network (Connection failed: error sending request)",
            "type": "error"
          }
        ],
        "event_count": 10,
        "failed_turns": 0,
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
        "stream_terminal": false,
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
      "wall_time_seconds": null
    }
  ],
  "random_seed": 20261016,
  "reasoning_effort": "low",
  "repeats": 2,
  "repetitions": 2,
  "repositories": {
    "python": {
      "commit": "3b0bea8141bd0d774e301ea8eadde19b264c3c82",
      "path": "/workspace/Memglide/.local/benchmarks/ab-full-20261016/repositories/python"
    },
    "typescript": {
      "commit": "99211bc8d48a86400fb8d1d794523b51e4b88c59",
      "path": "/workspace/Memglide/.local/benchmarks/ab-full-20261016/repositories/typescript"
    }
  },
  "resource_scope": "Local execution host; model inference resources are not exposed",
  "started_at": "2026-10-16T07:58:05.678800+00:00",
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
| ts-selective-retry | B | 1 | 1 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-selective-retry | A | 1 | 2 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-lru-eviction | B | 1 | 3 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-lru-eviction | A | 1 | 4 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-selective-retry | B | 1 | 5 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-selective-retry | A | 1 | 6 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-boolean-config | B | 1 | 7 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-boolean-config | A | 1 | 8 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-billing-rounding | B | 1 | 9 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-billing-rounding | A | 1 | 10 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | A | 1 | 11 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | B | 1 | 12 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-and-search | B | 1 | 13 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-and-search | A | 1 | 14 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | B | 1 | 15 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | A | 1 | 16 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | B | 1 | 17 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | A | 1 | 18 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | A | 1 | 19 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | B | 1 | 20 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | A | 1 | 21 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | B | 1 | 22 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | A | 1 | 23 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | B | 1 | 24 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-boolean-config | B | 1 | 25 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-boolean-config | A | 1 | 26 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | A | 1 | 27 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | B | 1 | 28 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-idempotent-events | B | 1 | 29 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-idempotent-events | A | 1 | 30 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | A | 1 | 31 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | B | 1 | 32 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-storage-containment | A | 1 | 33 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-storage-containment | B | 1 | 34 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | B | 1 | 35 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | A | 1 | 36 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-and-search | A | 1 | 37 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-and-search | B | 1 | 38 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | A | 1 | 39 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | B | 1 | 40 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | B | 1 | 41 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | A | 1 | 42 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | B | 1 | 43 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | A | 1 | 44 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-storage-containment | B | 1 | 45 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-storage-containment | A | 1 | 46 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-scope-authorization | A | 1 | 47 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-scope-authorization | B | 1 | 48 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-selective-retry | A | 2 | 49 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-selective-retry | B | 2 | 50 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-lru-eviction | A | 2 | 51 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-lru-eviction | B | 2 | 52 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-selective-retry | A | 2 | 53 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-selective-retry | B | 2 | 54 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-boolean-config | A | 2 | 55 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-boolean-config | B | 2 | 56 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-billing-rounding | A | 2 | 57 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-billing-rounding | B | 2 | 58 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | B | 2 | 59 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-transitive-dependencies | A | 2 | 60 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-and-search | A | 2 | 61 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-and-search | B | 2 | 62 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | A | 2 | 63 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-cursor-pagination | B | 2 | 64 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | A | 2 | 65 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-ttl-boundary | B | 2 | 66 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | B | 2 | 67 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-idempotent-events | A | 2 | 68 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | B | 2 | 69 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-ttl-boundary | A | 2 | 70 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | B | 2 | 71 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-optimistic-revision | A | 2 | 72 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-boolean-config | A | 2 | 73 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-boolean-config | B | 2 | 74 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | B | 2 | 75 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-transitive-dependencies | A | 2 | 76 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-idempotent-events | A | 2 | 77 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-idempotent-events | B | 2 | 78 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | B | 2 | 79 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-optimistic-revision | A | 2 | 80 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-storage-containment | B | 2 | 81 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-storage-containment | A | 2 | 82 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | A | 2 | 83 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-cursor-pagination | B | 2 | 84 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-and-search | B | 2 | 85 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-and-search | A | 2 | 86 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | B | 2 | 87 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-billing-rounding | A | 2 | 88 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | A | 2 | 89 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-lru-eviction | B | 2 | 90 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | A | 2 | 91 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-scope-authorization | B | 2 | 92 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-storage-containment | A | 2 | 93 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| ts-storage-containment | B | 2 | 94 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-scope-authorization | B | 2 | 95 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |
| py-scope-authorization | A | 2 | 96 | not_run | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl |

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

- ts-selective-retry / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-selective-retry / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-lru-eviction / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-lru-eviction / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-selective-retry / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-selective-retry / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-boolean-config / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-boolean-config / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-billing-rounding / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-billing-rounding / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-and-search / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-and-search / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-cursor-pagination / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-cursor-pagination / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-ttl-boundary / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-ttl-boundary / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-idempotent-events / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-idempotent-events / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-boolean-config / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-boolean-config / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-idempotent-events / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-idempotent-events / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-optimistic-revision / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-optimistic-revision / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-storage-containment / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-storage-containment / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-and-search / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-and-search / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-billing-rounding / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-billing-rounding / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-lru-eviction / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-lru-eviction / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-scope-authorization / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-scope-authorization / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-storage-containment / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-storage-containment / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-scope-authorization / A / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-scope-authorization / B / repeat 1: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-selective-retry / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-selective-retry / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-lru-eviction / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-lru-eviction / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-selective-retry / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-selective-retry / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-boolean-config / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-boolean-config / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-billing-rounding / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-billing-rounding / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-transitive-dependencies / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-and-search / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-and-search / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-cursor-pagination / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-cursor-pagination / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-ttl-boundary / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-ttl-boundary / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-idempotent-events / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-idempotent-events / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-ttl-boundary / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-optimistic-revision / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-boolean-config / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-boolean-config / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-transitive-dependencies / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-idempotent-events / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-idempotent-events / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-optimistic-revision / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-optimistic-revision / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-storage-containment / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-storage-containment / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-cursor-pagination / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-and-search / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-and-search / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-billing-rounding / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-billing-rounding / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-lru-eviction / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-lru-eviction / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-scope-authorization / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-scope-authorization / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-storage-containment / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- ts-storage-containment / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-scope-authorization / B / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl
- py-scope-authorization / A / repeat 2: status not_run; grader success unavailable; No observable MCP event stream; treatment fidelity is unknown. Codex preflight failed (authentication); inspect /workspace/Memglide/.local/benchmarks/ab-full-20261016/preflight/stderr.log and events.jsonl

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

## Detailed MCP component measurements

These measurements use the official MCP SDK against real STDIO subprocesses. They are independent component checks, **not Codex model runs, A/B results, or evidence of token/cost savings**.

Executed 24 isolated task worktrees with fresh databases: 24 transport probes passed, 0 failed; 24 freshness/hash checks passed, 0 failed; 168 actual SDK tool calls.

Natural task-prompt retrieval uses level 2 and an 8,000 estimated-token budget. Target-file and symbol coverage compare returned evidence with one declared fix location per task. This is a narrow coverage proxy; passing it does not prove context completeness or successful coding. The returned budget estimate is not billed token usage.

Mean target-file coverage: 0.6666666666666666; mean exact target-symbol identity coverage: 0.3333333333333333; mean expected declaration visibility in source snippets: 0.625. Whole-file/class evidence can contain a declaration while failing an exact symbol-identity match; declaration visibility does not establish a complete method body. All returned natural-retrieval evidence hashes matched disk in 24/24 task probes.

**Natural task-prompt retrieval missed the declared target file in 8/24 queries:** `py-scope-authorization`, `py-storage-containment`, `py-transitive-dependencies`, `ts-scope-authorization`, `ts-storage-containment`, `ts-transitive-dependencies`, `ts-boolean-config`, `ts-and-search`. These misses remain in every coverage statistic; the later exact-file query does not repair the natural-query score.

A separate exact-file level-3 retrieval selected a controlled comment edit. The old passport detected staleness in 24/24 probes; updated target hashes matched in 24/24, and updated full-source snippets contained the marker in 24/24.

| Metric | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|
| index_wall_seconds | 0.2750 | 0.2450 | 0.1153 | 1.0383 |
| mcp_transport_wall_seconds | 5.1211 | 5.0498 | 4.1302 | 7.3371 |
| mcp_server_sampled_cpu_seconds | 4.8046 | 4.7550 | 3.8700 | 6.7800 |
| mcp_server_sampled_peak_rss_bytes | 81954816.0000 | 80902144.0000 | 74858496.0000 | 90370048.0000 |

Server CPU and RSS are sampled locally every 50 ms. CPU is an observed lower bound; short-lived processes can be missed, shared RSS pages may be counted more than once. Timings include startup, SDK operations, controlled edit and shutdown. Index registration is measured separately in the probe process. These tiny synthetic libraries do not establish production scaling behavior.

| Task | Transport/hash checks | File coverage | Exact symbol coverage | Declaration visible | Old passport stale | Updated hash | Edit marker | MCP calls |
|---|---|---:|---:|---:|---|---|---|---:|
| py-ttl-boundary | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| py-lru-eviction | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-cursor-pagination | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-optimistic-revision | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-scope-authorization | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-storage-containment | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-transitive-dependencies | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-selective-retry | passed | 1.0 | 0.0 | 0.0 | True | True | True | 7 |
| py-boolean-config | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| py-and-search | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| py-billing-rounding | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| py-idempotent-events | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| ts-ttl-boundary | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| ts-lru-eviction | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-cursor-pagination | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-optimistic-revision | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-scope-authorization | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-storage-containment | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-transitive-dependencies | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-selective-retry | passed | 1.0 | 1.0 | 1.0 | True | True | True | 7 |
| ts-boolean-config | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-and-search | passed | 0.0 | 0.0 | 0.0 | True | True | True | 7 |
| ts-billing-rounding | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |
| ts-idempotent-events | passed | 1.0 | 0.0 | 1.0 | True | True | True | 7 |

Raw SDK arguments/responses and server logs are retained under the reported artifact root. Every failure is included. Model input/cached/output tokens, model calls, billed cost and coding success are unavailable in this component probe and remain null. A full passport status can remain Partial when source hashes are current, because unresolved static dependencies are reported separately from freshness.

## Detailed application validation

All 143 existing application tests passed on the current Linux checkout at commit `39e8df30565783a686270f8a6f422e56e41e3776`. No application fixes were needed. These results validate tested application behavior; they do not establish token, cost, or coding-task benefits over Codex.

| Check | Result | Recorded duration |
| --- | --- | --- |
| Backend unit, integration, security, HTTP, CLI, real MCP | 126 passed; 0 failed/skipped | 54.26 s |
| Frontend components/API/workflows | 15 passed in 3 files | 14.62 s |
| Production Chromium browser workflows | 2 passed | 59.3 s including server startup/build |
| Ruff | Passed | Not separately recorded |
| mypy | Passed, 20 source files | Not separately recorded |
| TypeScript + production Vite | Passed | Vite phase reported 1.69 s |
| Frozen dependency installs | Passed, 56 Python packages checked / 134 npm packages installed | Not separately recorded |
| Bundle + wheel/source build | Passed | Not separately recorded |

Backend counts by module: context diagnostics 2, indexing 25, memory/context 20, security/storage 69, transports 9, end-to-end service workflow 1. Parameterized cases are counted individually. Security/storage is part of the 126 backend tests, not an additional count.

The MCP test launches the actual server over STDIO with the official SDK, initializes it, discovers all 14 tools, requires structured output schemas, calls every tool and validates structured content. It also verifies rejected foreign-project/session and ended-session requests. This verifies Memglide's transport independently of the live Codex invocation evidence in the A/B benchmark.

The production browser suite builds and bundles the dashboard, starts the actual FastAPI backend on loopback port 18765 with isolated Git fixtures/database, and checks the repository/session/memory/retrieval/passport workflow, all seven routes, errors and empty states, and 1440/1024/768 pixel layouts. Its two cases took 31.7 s and 13.9 s; suite duration also includes setup.

Exact commands (run from `/workspace/Memglide`):

```sh
export UV_CACHE_DIR=/workspace/Memglide/.cache/uv
export npm_config_cache=/workspace/Memglide/.cache/npm
export MEMGLIDE_HOME=/workspace/Memglide/.local/validation/home
uv sync --frozen
npm --prefix frontend ci
uv run pytest -ra --junitxml=.local/validation/pytest.xml
uv run ruff check .
uv run mypy src
npm --prefix frontend test -- --run
npm --prefix frontend run build
MEMGLIDE_E2E_PORT=18765 npm --prefix frontend run e2e
uv run python scripts/bundle_frontend.py
uv build
```

Python Python 3.12.14, Node v24.19.0, npm 11.9.0, uv uv 0.12.23 (x86_64-unknown-linux-gnu), and Chromium 154.0.8037.57 built on Debian GNU/Linux 13 (trixie) were used.

One initial install command omitted the local uv cache variable and failed before installation because the default home cache is read-only. Retrying with the project cache succeeded. No tests failed. Pytest emitted two upstream Typer/Click deprecation warnings; Playwright emitted a color-environment warning. uv build warned that the cache sits inside the source tree; inspecting the resulting 109-member source archive found no `.cache`, `node_modules`, `.local`, or `.venv` directories. The wheel contains 19 production frontend files.

No tracked application files changed during validation. Generated state, logs, bundled assets and package artifacts use existing ignored paths. Detailed per-test durations, original command output, tool versions and MCP tool names are preserved in [validation.json](validation.json). Native Windows/macOS and live Codex model behavior are outside these application-test results.
