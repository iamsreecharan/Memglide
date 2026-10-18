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
  "finished_at": "2026-10-18T00:27:14.607106+00:00",
  "frozen_manifest": {
    "common_instructions_sha256": "9bf1ac8fd96ab9457aeeb20fa4e2b18d9b066660358d97d58a29d64450c6a55e",
    "files": {
      "benchmarks/compare_components.py": "c9c0b463068a7fc679e4387566daeefc82b556b789c0de98b568880b13aea89e",
      "benchmarks/context_audit_v2.py": "d473d241237364b08f228e3f6ea7092d414bcb2ce9b347c9918a967ee95a3a4a",
      "benchmarks/corpus_v2.py": "9f6976324ad19989a9ac68336648bc508baea542f697bef5dde15c0bf00ea5ba",
      "benchmarks/reporting.py": "3e1d1c86cf0d091db7d7e04576110687e267de025397e6ef87c9a0d319577c8e",
      "benchmarks/run.py": "ccf8d44ca7ea8286a8a9241b030eaa76ca339ec15032aeb95cb4e256ef500a26",
      "benchmarks/run_v2.py": "eaa1d36af3796bf54de4137fd406af2fa3233421855e49628644e9572a358c69",
      "benchmarks/tasks_v2.json": "d3e9e789eaf333e7b44b5d7e4f0b98b36aa20d6454519f047cdd2d501c613f83",
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
    "git_head": "62e07cc98855b4cdde255395372e5d78b3a7e2a1",
    "prompt_sha256": {
      "py2-ledger-atomic-transfer": "956bbe39f5ca3979293fe1a1e4dccde985d77fa58acd26012a2c7a20aa6ae54f",
      "py2-ledger-audit-hash-chain": "0efa3e5aa0ae8e03e74fd1244674edfb91b28e5144a5c1b29be09883d31c53c9",
      "py2-ledger-csv-bank-import": "8b625df00f32ca8c8fafefea9360048cdbe937b61b572a012c344539c9d46546",
      "py2-ledger-currency-netting": "eb9c9a4cf23376802e8461d8837d18106be3a4d32239af26d30763f895925717",
      "py2-ledger-invoice-line-discounts": "ea7561222d28daf9f4811289190d6717a03fcd34aa94bbe6257abc35cf28c101",
      "py2-ledger-nested-redaction": "73ed4eeffce31addf0e38010bc40f427f84030580a917732a4d9f1bf2c3324e1",
      "py2-ledger-reconciliation-version-merge": "24240375e25a3a1ff861acf251af597fcf0ed08b553e20aab206f28a1931250d",
      "py2-ledger-signed-tax-rounding": "366a25266ad628bdde4940640bacaf0504c6996e032dc4822b1faf6f761ab88e",
      "py2-ledger-statement-timezones": "6d1e04c26532829bd992451e787f5d39aace30c31926af8aeab21914ac75bbcb",
      "py2-ledger-weighted-allocation": "79c56678fb8842a3ab75662ff399bff9797770f85cf976b409256c57d39f5857",
      "py2-workflow-atomic-pointer-updates": "97b6cc741da3818be659daab08307484e8803676763c747470c5a4f319277f45",
      "py2-workflow-bounded-async-execution": "27463af33d27aa8056805bd9a4b1b71955397b70d33c1f7bb3e82c25d1ece8cc",
      "py2-workflow-capped-backoff": "85fe3f89a50c4d4c6c20fb031ceae3a7bf867cf45f04f4c3af1ae011996205a1",
      "py2-workflow-deep-settings-overlay": "67433aac3d87151087d676fbf761bc3711208041035352e369e51b6175c9b7e9",
      "py2-workflow-deterministic-build-order": "249adfcc52574f4f9fc3e8b30077bd767c9ba1671d58bcf5d8ec3c2cf79f9bd3",
      "py2-workflow-incremental-utf8-lines": "164a609fa4073999a8060023538163bfe6b98b543a86d1f7a27d7feafd7f8161",
      "py2-workflow-interval-coalescing": "2e32e79ad8812fcabc3c6dad7c344d1b540eb93f558df44b8268a244abfb40a1",
      "py2-workflow-ready-job-order": "8f11b45ec76724707883cbf2ed6f8f6164255bee581a7744b02813ba4d88191a",
      "py2-workflow-strict-template-expansion": "786afc153d36a4dae2ea603f179e59430044ec1ec5c2e67e17b1d6b5a859606b",
      "py2-workflow-utf8-batch-budget": "976decc945ce2295ca5b76cffe90152ad4c83deb7e2f653ee067654e00be8476",
      "ts2-config-casefold-header-collection": "eabc294ba35581588f8967090d4d3c45156a897232dd1c7eeb9d7adbda7c79d0",
      "ts2-config-complete-form-errors": "1a687496c5dd21180d892408479a984f8e538936f47690c9f1b7f7296a3f7f7d",
      "ts2-config-quoted-env-values": "e14c0f82b6a734f03a4e7783661e0d0ec5b426fcd11fa6688b3025c3d2d2c7d2",
      "ts2-config-repeated-query-values": "8b22fb365976cd12f9cfcd5ae76522de55558d44d71775641a892ab4c65c3e48",
      "ts2-config-safe-local-redirects": "d80c7b69240993489f781581dec08e064cefa7308cd4da75c29b8949aa1b911b",
      "ts2-config-semantic-version-precedence": "ebcefb6e9428a09ffa1c657a34c8c4cfcc443b2d6cf8396c19c3d0a5fc458aa5",
      "ts2-config-specific-route-matching": "efcf60cd5517f72622e8f155daab8c8c7c5893b5bc4d22b2ba06335a11f89a43",
      "ts2-config-strict-pointer-lookup": "1ce91b5eace7c2c2f3336f3bfabbbe27cc113473a05c2d06d729e4542ccd7fdd",
      "ts2-config-unicode-ascii-slugs": "b86a433a94c64aa030d0992d0b2acf144d5253f4175b071ca3d24e73ccc82c0e",
      "ts2-config-utf8-feature-cohorts": "b43d69da1540360076aa7ebd9747b5f0e3b9c068121ca3a07642075d39f94ef8",
      "ts2-stream-abort-aware-delay-plan": "2afb9062f797e68cc386b7338ec733a955e936c4596ea8d742c42d76865456dd",
      "ts2-stream-bounded-run-length-decode": "3047b443e9bcbe8759f6dafe03c671f6d637b8da99e04546d896e468b6436556",
      "ts2-stream-decimal-money-parser": "6481ff03b13fcc70e003bbad17fb187e9b55084596e9ab76c23407d3aab1d534",
      "ts2-stream-escaped-record-codec": "0c72f2c796a2981a9087d09cbd59a274468dca5a130e7ea46da34f5bb860765e",
      "ts2-stream-event-time-rolling-counts": "a3a99eeb8bdeae8edd2864a2327d2aa089528f4ee99fbcfd8da30780dc6d9409",
      "ts2-stream-fragmented-ndjson": "99642116d57b9b82d8ca8825d4c6eedf6cc1903acdae09161c680ee15d3b75b0",
      "ts2-stream-half-open-window-join": "b2bdcc0483e28ff7692a2900f38075a21774e88aaa87ccd7fbaabdc2400901e1",
      "ts2-stream-keyed-upsert-order": "ead296910e484a36c0571eddf054ff7c56cc798fe505fc7b7388d92ade5ea2fd",
      "ts2-stream-simultaneous-text-edits": "c155cab773cf14552b304d160af6270e6f5d19b884307887c8e603846ec80700",
      "ts2-stream-transactional-accumulator": "948102b633cdf8735bb2ee4a6cd086f841af50327717ca2587e7b018b0947d1b"
    },
    "settings": {
      "codex_executable": "/opt/codex/bin/codex",
      "codex_home_binding_directory": "/workspace/Memglide/.local/codex-device-login-NlwVLVWg",
      "codex_version": "codex-cli 0.159.2",
      "corpus": "v2",
      "effort": "low",
      "limit": null,
      "model": "gpt-6.1-sol",
      "repeats": 2,
      "require_verification": false,
      "seed": 20261017,
      "skip_preflight": false,
      "timeout": 180.0
    }
  },
  "last_checkpoint_at": "2026-10-18T00:27:14.369019+00:00",
  "logical_cpu_count": 5,
  "memglide_source_after": {
    "attestation": "captured_source_state_before_probe",
    "captured_at": "2026-10-18T00:27:14.664292+00:00",
    "git_head": "62e07cc98855b4cdde255395372e5d78b3a7e2a1",
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
    "captured_at": "2026-10-17T23:04:44.207910+00:00",
    "git_head": "62e07cc98855b4cdde255395372e5d78b3a7e2a1",
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
    "repositories": "Four new multi-module fixtures; ten tasks per fixture; independent external graders",
    "settings": "Same model, effort, schema, workspace-write sandbox, global approval never and common prompt; only scoped MCP availability differs",
    "timing": "CLI wall time plus B's required fresh index equals end-to-end time; external graders/readiness excluded",
    "treatment": "B requires actual compact source retrieval. Verification is optional and on demand; invocation evidence does not establish chronology relative to final edits. A has no configured MCP servers"
  },
  "model": "gpt-6.1-sol",
  "output_directory": "/workspace/Memglide/.local/optimization-v2/formal-40-v1",
  "preflight_complete": true,
  "preflight_runs": [
    {
      "artifacts": "/workspace/Memglide/.local/optimization-v2/formal-40-v1/preflight",
      "exit_code": 0,
      "overhead": {
        "cpu_seconds": 1.83,
        "memglide_cpu_seconds": null,
        "memglide_peak_rss_bytes": null,
        "method": "/proc sampling; CPU observed lower bound, RSS shared pages can be counted multiple times; short-lived processes may be missed",
        "observed_memglide_processes": 0,
        "observed_processes": 7,
        "process_tree_peak_rss_bytes": 99434496,
        "samples": 89,
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
          "cached_input_tokens": 0,
          "input_tokens": 10963,
          "output_tokens": 40
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
          "input_tokens": 10963,
          "output_tokens": 40
        },
        "usage_coverage_complete": true,
        "usage_scope": "Complete parsed stream only; partial observed turn usage is stored separately",
        "usage_unavailable_reasons": {}
      },
      "timed_out": false,
      "wall_time_seconds": 5.698476261999986
    }
  ],
  "preflight_started_at": "2026-10-17T23:04:44.827925+00:00",
  "random_seed": 20261017,
  "reasoning_effort": "low",
  "repeats": 2,
  "repetitions": 2,
  "repositories": {
    "config-typescript-v2": {
      "commit": "6ac686c6379e81c78d272edbaae6ae074cc58888",
      "path": "/workspace/Memglide/.local/optimization-v2/formal-40-v1/repositories/config-typescript-v2",
      "tree": "f41f03000cc91bc312ee653d62432ee6fe78b65b"
    },
    "ledger-python-v2": {
      "commit": "2b78ee8ee850842d3a9c9f16277d94b17980bd7b",
      "path": "/workspace/Memglide/.local/optimization-v2/formal-40-v1/repositories/ledger-python-v2",
      "tree": "6d8e5aec93118e00cc1cd69139ae68963dcde364"
    },
    "stream-typescript-v2": {
      "commit": "0dcda6fd2717033c7655f549f92b7951a416ef23",
      "path": "/workspace/Memglide/.local/optimization-v2/formal-40-v1/repositories/stream-typescript-v2",
      "tree": "dbec169db4812e60dad1f7dde6efdf2cb598122c"
    },
    "workflow-python-v2": {
      "commit": "7d21ae7cda0fdf1ae3f4327620af377faa66d72a",
      "path": "/workspace/Memglide/.local/optimization-v2/formal-40-v1/repositories/workflow-python-v2",
      "tree": "61bc046e65fe6735d3d26bd542e7d6a624972bec"
    }
  },
  "resource_scope": "Local execution host; model inference resources are not exposed",
  "resume_count": 0,
  "source_unchanged_during_experiment": true,
  "started_at": "2026-10-17T23:04:44.191664+00:00",
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
| Planned runs | 80 | 80 |
| Attempted runs | 80 | 80 |
| Not run | 0 | 0 |
| Graded runs | 80 | 80 |
| Successful runs | 80 | 80 |
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
| input_tokens | 62881.3 | 64608.5 | 80 / 0 / 0 | 5030508 | 83520.2 | 89638 | 80 / 0 / 0 | 6681616 |
| cached_input_tokens | 50595.2 | 49408 | 80 / 0 / 0 | 4047616 | 70968 | 71296 | 80 / 0 / 0 | 5677440 |
| output_tokens | 1422.53 | 1346.5 | 80 / 0 / 0 | 113802 | 1498.01 | 1415.5 | 80 / 0 / 0 | 119841 |
| model_calls | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| mcp_calls | 0 | 0 | 80 / 0 / 0 | 0 | 1 | 1 | 80 / 0 / 0 | 80 |
| memglide_mcp_calls | 0 | 0 | 80 / 0 / 0 | 0 | 1 | 1 | 80 / 0 / 0 | 80 |
| observed_mcp_calls | 0 | 0 | 80 / 0 / 0 | 0 | 1 | 1 | 80 / 0 / 0 | 80 |
| observed_memglide_mcp_calls | 0 | 0 | 80 / 0 / 0 | 0 | 1 | 1 | 80 / 0 / 0 | 80 |
| wall_time_seconds | 27.2964 | 26.2554 | 80 / 0 / 0 | 2183.71 | 31.9703 | 30.5637 | 80 / 0 / 0 | 2557.63 |
| end_to_end_wall_seconds | 27.2964 | 26.2554 | 80 / 0 / 0 | 2183.71 | 32.1779 | 30.8408 | 80 / 0 / 0 | 2574.23 |
| setup_wall_seconds | unavailable | unavailable | 0 / 80 / 80 | unavailable | 0.207526 | 0.19404 | 80 / 0 / 0 | 16.6021 |
| setup_cpu_seconds | unavailable | unavailable | 0 / 80 / 80 | unavailable | 0.0700109 | 0.0565159 | 80 / 0 / 0 | 5.60087 |
| repeated_file_reads | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| observed_file_read_commands | 1.1375 | 1 | 80 / 0 / 0 | 91 | 1.05 | 1 | 80 / 0 / 0 | 84 |
| observed_repeated_read_commands | 0 | 0 | 80 / 0 / 0 | 0 | 0 | 0 | 80 / 0 / 0 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| computed_cost_usd | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| process_tree_peak_rss_bytes | 2.82614e+08 | 2.76167e+08 | 80 / 0 / 0 | unavailable | 3.69267e+08 | 3.52244e+08 | 80 / 0 / 0 | unavailable |
| cpu_seconds | 5.35425 | 4.925 | 80 / 0 / 0 | 428.34 | 7.73862 | 7.235 | 80 / 0 / 0 | 619.09 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 / 80 / 80 | unavailable | 7.21893e+07 | 7.21756e+07 | 80 / 0 / 0 | unavailable |
| memglide_cpu_seconds | unavailable | unavailable | 0 / 80 / 80 | unavailable | 1.97875 | 1.905 | 80 / 0 / 0 | 158.3 |
| context_freshness | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| retrieval_completeness | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 / 80 / 80 | unavailable | unavailable | unavailable | 0 / 80 / 80 | unavailable |

## Individual runs

| Task | Config | Repeat | Order | Status | Grader success | MCP calls | Memglide calls | Treatment valid | Input | Cached | Output | Seconds | Errors |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| ts2-config-strict-pointer-lookup | A | 1 | 1 | completed | yes | 0 | 0 | yes | 65770 | 59008 | 1512 | 27.8286 |  |
| ts2-config-strict-pointer-lookup | B | 1 | 2 | completed | yes | 1 | 1 | yes | 93909 | 84480 | 1451 | 28.8446 |  |
| ts2-config-semantic-version-precedence | B | 1 | 3 | completed | yes | 1 | 1 | yes | 119793 | 97664 | 3809 | 58.4876 |  |
| ts2-config-semantic-version-precedence | A | 1 | 4 | completed | yes | 0 | 0 | yes | 66997 | 60032 | 1966 | 34.2283 |  |
| py2-ledger-reconciliation-version-merge | B | 1 | 5 | completed | yes | 1 | 1 | yes | 73010 | 56064 | 1009 | 23.9877 |  |
| py2-ledger-reconciliation-version-merge | A | 1 | 6 | completed | yes | 0 | 0 | yes | 49978 | 44032 | 1251 | 22.8465 |  |
| py2-ledger-currency-netting | B | 1 | 7 | completed | yes | 1 | 1 | yes | 91077 | 72448 | 1530 | 32.1651 |  |
| py2-ledger-currency-netting | A | 1 | 8 | completed | yes | 0 | 0 | yes | 50442 | 35200 | 1481 | 24.3648 |  |
| py2-workflow-utf8-batch-budget | B | 1 | 9 | completed | yes | 1 | 1 | yes | 74812 | 56832 | 1104 | 23.8461 |  |
| py2-workflow-utf8-batch-budget | A | 1 | 10 | completed | yes | 0 | 0 | yes | 50258 | 44416 | 1102 | 22.355 |  |
| ts2-config-complete-form-errors | B | 1 | 11 | completed | yes | 1 | 1 | yes | 93384 | 74240 | 1352 | 35.8665 |  |
| ts2-config-complete-form-errors | A | 1 | 12 | completed | yes | 0 | 0 | yes | 64988 | 58752 | 1328 | 26.5096 |  |
| py2-ledger-statement-timezones | B | 1 | 13 | completed | yes | 1 | 1 | yes | 92417 | 82560 | 1723 | 37.6893 |  |
| py2-ledger-statement-timezones | A | 1 | 14 | completed | yes | 0 | 0 | yes | 80884 | 63744 | 2011 | 30.9677 |  |
| ts2-stream-bounded-run-length-decode | B | 1 | 15 | completed | yes | 1 | 1 | yes | 92660 | 83584 | 1352 | 30.2495 |  |
| ts2-stream-bounded-run-length-decode | A | 1 | 16 | completed | yes | 0 | 0 | yes | 65619 | 59008 | 1485 | 27.819 |  |
| ts2-stream-simultaneous-text-edits | B | 1 | 17 | completed | yes | 1 | 1 | yes | 76779 | 67584 | 1606 | 31.325 |  |
| ts2-stream-simultaneous-text-edits | A | 1 | 18 | completed | yes | 0 | 0 | yes | 66477 | 50688 | 1777 | 30.8749 |  |
| ts2-config-specific-route-matching | A | 1 | 19 | completed | yes | 0 | 0 | yes | 79777 | 63872 | 1580 | 30.8152 |  |
| ts2-config-specific-route-matching | B | 1 | 20 | completed | yes | 1 | 1 | yes | 93902 | 84224 | 1650 | 35.3584 |  |
| py2-workflow-incremental-utf8-lines | A | 1 | 21 | completed | yes | 0 | 0 | yes | 64087 | 49280 | 1149 | 22.0032 |  |
| py2-workflow-incremental-utf8-lines | B | 1 | 22 | completed | yes | 1 | 1 | yes | 73217 | 64768 | 1545 | 34.536 |  |
| ts2-config-repeated-query-values | A | 1 | 23 | completed | yes | 0 | 0 | yes | 65209 | 58624 | 1174 | 23.4619 |  |
| ts2-config-repeated-query-values | B | 1 | 24 | completed | yes | 1 | 1 | yes | 59612 | 42240 | 1413 | 30.0832 |  |
| ts2-stream-transactional-accumulator | B | 1 | 25 | completed | yes | 1 | 1 | yes | 93344 | 83456 | 2128 | 41.5915 |  |
| ts2-stream-transactional-accumulator | A | 1 | 26 | completed | yes | 0 | 0 | yes | 66436 | 50432 | 1833 | 33.8136 |  |
| ts2-stream-keyed-upsert-order | B | 1 | 27 | completed | yes | 1 | 1 | yes | 74458 | 57344 | 1396 | 27.9862 |  |
| ts2-stream-keyed-upsert-order | A | 1 | 28 | completed | yes | 0 | 0 | yes | 50643 | 35584 | 1302 | 26.2671 |  |
| ts2-stream-decimal-money-parser | B | 1 | 29 | completed | yes | 1 | 1 | yes | 59844 | 50816 | 1257 | 25.8178 |  |
| ts2-stream-decimal-money-parser | A | 1 | 30 | completed | yes | 0 | 0 | yes | 65249 | 58880 | 1380 | 28.1335 |  |
| py2-ledger-weighted-allocation | A | 1 | 31 | completed | yes | 0 | 0 | yes | 64951 | 57472 | 1542 | 30.6226 |  |
| py2-ledger-weighted-allocation | B | 1 | 32 | completed | yes | 1 | 1 | yes | 92251 | 83328 | 1344 | 36.365 |  |
| py2-ledger-csv-bank-import | B | 1 | 33 | completed | yes | 1 | 1 | yes | 78331 | 68352 | 1965 | 39.1419 |  |
| py2-ledger-csv-bank-import | A | 1 | 34 | completed | yes | 0 | 0 | yes | 79762 | 72192 | 2068 | 35.0879 |  |
| py2-workflow-deep-settings-overlay | B | 1 | 35 | completed | yes | 1 | 1 | yes | 90083 | 71680 | 1562 | 36.4514 |  |
| py2-workflow-deep-settings-overlay | A | 1 | 36 | completed | yes | 0 | 0 | yes | 50058 | 35200 | 1294 | 40.34 |  |
| py2-workflow-ready-job-order | B | 1 | 37 | completed | yes | 1 | 1 | yes | 57728 | 41216 | 1427 | 32.2269 |  |
| py2-workflow-ready-job-order | A | 1 | 38 | completed | yes | 0 | 0 | yes | 50241 | 32896 | 1553 | 28.8269 |  |
| py2-ledger-invoice-line-discounts | A | 1 | 39 | completed | yes | 0 | 0 | yes | 63925 | 35200 | 1058 | 23.9687 |  |
| py2-ledger-invoice-line-discounts | B | 1 | 40 | completed | yes | 1 | 1 | yes | 75915 | 67328 | 1260 | 31.9015 |  |
| ts2-config-unicode-ascii-slugs | B | 1 | 41 | completed | yes | 1 | 1 | yes | 76814 | 58368 | 990 | 25.0532 |  |
| ts2-config-unicode-ascii-slugs | A | 1 | 42 | completed | yes | 0 | 0 | yes | 64005 | 38016 | 881 | 20.4331 |  |
| ts2-stream-event-time-rolling-counts | B | 1 | 43 | completed | yes | 1 | 1 | yes | 92848 | 73984 | 1434 | 36.1234 |  |
| ts2-stream-event-time-rolling-counts | A | 1 | 44 | completed | yes | 0 | 0 | yes | 65451 | 59008 | 1385 | 29.5826 |  |
| ts2-stream-fragmented-ndjson | B | 1 | 45 | completed | yes | 1 | 1 | yes | 76203 | 57856 | 1247 | 28.3925 |  |
| ts2-stream-fragmented-ndjson | A | 1 | 46 | completed | yes | 0 | 0 | yes | 64292 | 49280 | 1109 | 22.6859 |  |
| py2-ledger-nested-redaction | A | 1 | 47 | completed | yes | 0 | 0 | yes | 49846 | 44032 | 1269 | 23.548 |  |
| py2-ledger-nested-redaction | B | 1 | 48 | completed | yes | 1 | 1 | yes | 90790 | 72448 | 1498 | 29.1836 |  |
| py2-ledger-atomic-transfer | A | 1 | 49 | completed | yes | 0 | 0 | yes | 50336 | 44160 | 1556 | 24.1667 |  |
| py2-ledger-atomic-transfer | B | 1 | 50 | completed | yes | 1 | 1 | yes | 76445 | 67200 | 1680 | 42.3521 |  |
| py2-workflow-bounded-async-execution | B | 1 | 51 | completed | yes | 1 | 1 | yes | 107896 | 98560 | 1981 | 39.2259 |  |
| py2-workflow-bounded-async-execution | A | 1 | 52 | completed | yes | 0 | 0 | yes | 79647 | 72064 | 2165 | 35.9678 |  |
| ts2-config-casefold-header-collection | A | 1 | 53 | completed | yes | 0 | 0 | yes | 79535 | 63872 | 1633 | 33.1353 |  |
| ts2-config-casefold-header-collection | B | 1 | 54 | completed | yes | 1 | 1 | yes | 78488 | 68736 | 1801 | 38.0019 |  |
| py2-workflow-capped-backoff | B | 1 | 55 | completed | yes | 1 | 1 | yes | 72186 | 64000 | 1381 | 27.9093 |  |
| py2-workflow-capped-backoff | A | 1 | 56 | completed | yes | 0 | 0 | yes | 49822 | 44032 | 1235 | 23.6926 |  |
| py2-workflow-deterministic-build-order | B | 1 | 57 | completed | yes | 1 | 1 | yes | 72611 | 65664 | 1303 | 25.607 |  |
| py2-workflow-deterministic-build-order | A | 1 | 58 | completed | yes | 0 | 0 | yes | 49773 | 36352 | 1203 | 22.9995 |  |
| ts2-stream-escaped-record-codec | B | 1 | 59 | completed | yes | 1 | 1 | yes | 92330 | 83584 | 1241 | 24.5773 |  |
| ts2-stream-escaped-record-codec | A | 1 | 60 | completed | yes | 0 | 0 | yes | 64151 | 49280 | 1036 | 23.141 |  |
| py2-workflow-strict-template-expansion | B | 1 | 61 | completed | yes | 1 | 1 | yes | 72443 | 55936 | 1305 | 26.1056 |  |
| py2-workflow-strict-template-expansion | A | 1 | 62 | completed | yes | 0 | 0 | yes | 50179 | 35200 | 1163 | 20.393 |  |
| ts2-config-utf8-feature-cohorts | A | 1 | 63 | completed | yes | 0 | 0 | yes | 79565 | 58368 | 1322 | 26.7491 |  |
| ts2-config-utf8-feature-cohorts | B | 1 | 64 | completed | yes | 1 | 1 | yes | 59724 | 41216 | 1206 | 25.9722 |  |
| ts2-stream-half-open-window-join | A | 1 | 65 | completed | yes | 0 | 0 | yes | 64410 | 48896 | 1220 | 25.6945 |  |
| ts2-stream-half-open-window-join | B | 1 | 66 | completed | yes | 1 | 1 | yes | 92838 | 73984 | 1344 | 28.1316 |  |
| ts2-config-quoted-env-values | A | 1 | 67 | completed | yes | 0 | 0 | yes | 79683 | 64000 | 1501 | 32.1963 |  |
| ts2-config-quoted-env-values | B | 1 | 68 | completed | yes | 1 | 1 | yes | 93859 | 85888 | 1546 | 31.5199 |  |
| ts2-config-safe-local-redirects | B | 1 | 69 | completed | yes | 1 | 1 | yes | 59580 | 50688 | 1270 | 24.6956 |  |
| ts2-config-safe-local-redirects | A | 1 | 70 | completed | yes | 0 | 0 | yes | 64975 | 47232 | 1452 | 28.9273 |  |
| py2-ledger-audit-hash-chain | A | 1 | 71 | completed | yes | 0 | 0 | yes | 49494 | 31488 | 1239 | 21.3697 |  |
| py2-ledger-audit-hash-chain | B | 1 | 72 | completed | yes | 1 | 1 | yes | 75449 | 67968 | 1214 | 27.0273 |  |
| py2-workflow-interval-coalescing | B | 1 | 73 | completed | yes | 1 | 1 | yes | 57600 | 49664 | 1082 | 23.6183 |  |
| py2-workflow-interval-coalescing | A | 1 | 74 | completed | yes | 0 | 0 | yes | 50034 | 36480 | 1332 | 22.7493 |  |
| ts2-stream-abort-aware-delay-plan | A | 1 | 75 | completed | yes | 0 | 0 | yes | 65394 | 51200 | 1378 | 23.7062 |  |
| ts2-stream-abort-aware-delay-plan | B | 1 | 76 | completed | yes | 1 | 1 | yes | 75861 | 68096 | 1258 | 42.9461 |  |
| py2-ledger-signed-tax-rounding | B | 1 | 77 | completed | yes | 1 | 1 | yes | 74546 | 57216 | 1277 | 26.446 |  |
| py2-ledger-signed-tax-rounding | A | 1 | 78 | completed | yes | 0 | 0 | yes | 64188 | 46464 | 1131 | 22.06 |  |
| py2-workflow-atomic-pointer-updates | A | 1 | 79 | completed | yes | 0 | 0 | yes | 65877 | 50048 | 1763 | 29.4803 |  |
| py2-workflow-atomic-pointer-updates | B | 1 | 80 | completed | yes | 1 | 1 | yes | 92478 | 73600 | 1975 | 37.9592 |  |
| ts2-config-strict-pointer-lookup | B | 2 | 81 | completed | yes | 1 | 1 | yes | 94971 | 75648 | 1417 | 38.9095 |  |
| ts2-config-strict-pointer-lookup | A | 2 | 82 | completed | yes | 0 | 0 | yes | 65652 | 50048 | 1443 | 25.935 |  |
| ts2-config-semantic-version-precedence | A | 2 | 83 | completed | yes | 0 | 0 | yes | 66836 | 59904 | 1884 | 34.8794 |  |
| ts2-config-semantic-version-precedence | B | 2 | 84 | completed | yes | 1 | 1 | yes | 77889 | 58880 | 1816 | 29.5866 |  |
| py2-ledger-reconciliation-version-merge | A | 2 | 85 | completed | yes | 0 | 0 | yes | 50067 | 44160 | 1156 | 20.3367 |  |
| py2-ledger-reconciliation-version-merge | B | 2 | 86 | completed | yes | 1 | 1 | yes | 73375 | 65024 | 1234 | 34.9474 |  |
| py2-ledger-currency-netting | A | 2 | 87 | completed | yes | 0 | 0 | yes | 50238 | 36608 | 1401 | 32.0869 |  |
| py2-ledger-currency-netting | B | 2 | 88 | completed | yes | 1 | 1 | yes | 73593 | 66432 | 1503 | 28.9289 |  |
| py2-workflow-utf8-batch-budget | A | 2 | 89 | completed | yes | 0 | 0 | yes | 64489 | 59392 | 1146 | 25.0777 |  |
| py2-workflow-utf8-batch-budget | B | 2 | 90 | completed | yes | 1 | 1 | yes | 91090 | 83584 | 1194 | 27.4512 |  |
| ts2-config-complete-form-errors | A | 2 | 91 | completed | yes | 0 | 0 | yes | 64632 | 36224 | 1374 | 25.6214 |  |
| ts2-config-complete-form-errors | B | 2 | 92 | completed | yes | 1 | 1 | yes | 77054 | 67712 | 1472 | 33.0815 |  |
| py2-ledger-statement-timezones | A | 2 | 93 | completed | yes | 0 | 0 | yes | 85852 | 76416 | 2149 | 35.2907 |  |
| py2-ledger-statement-timezones | B | 2 | 94 | completed | yes | 1 | 1 | yes | 114788 | 93696 | 2358 | 39.8797 |  |
| ts2-stream-bounded-run-length-decode | A | 2 | 95 | completed | yes | 0 | 0 | yes | 65383 | 49920 | 1348 | 25.2442 |  |
| ts2-stream-bounded-run-length-decode | B | 2 | 96 | completed | yes | 1 | 1 | yes | 92953 | 83968 | 1443 | 34.602 |  |
| ts2-stream-simultaneous-text-edits | A | 2 | 97 | completed | yes | 0 | 0 | yes | 66089 | 50176 | 1578 | 29.9595 |  |
| ts2-stream-simultaneous-text-edits | B | 2 | 98 | completed | yes | 1 | 1 | yes | 92651 | 84992 | 1718 | 30.2536 |  |
| ts2-config-specific-route-matching | B | 2 | 99 | completed | yes | 1 | 1 | yes | 93523 | 84224 | 1629 | 30.9337 |  |
| ts2-config-specific-route-matching | A | 2 | 100 | completed | yes | 0 | 0 | yes | 65671 | 59008 | 1515 | 28.2758 |  |
| py2-workflow-incremental-utf8-lines | B | 2 | 101 | completed | yes | 1 | 1 | yes | 89512 | 81152 | 1561 | 32.5475 |  |
| py2-workflow-incremental-utf8-lines | A | 2 | 102 | completed | yes | 0 | 0 | yes | 50121 | 41856 | 1261 | 25.0346 |  |
| ts2-config-repeated-query-values | B | 2 | 103 | completed | yes | 1 | 1 | yes | 93381 | 85248 | 1185 | 26.7968 |  |
| ts2-config-repeated-query-values | A | 2 | 104 | completed | yes | 0 | 0 | yes | 64936 | 49664 | 1174 | 22.6471 |  |
| ts2-stream-transactional-accumulator | A | 2 | 105 | completed | yes | 0 | 0 | yes | 65496 | 58880 | 1530 | 31.2103 |  |
| ts2-stream-transactional-accumulator | B | 2 | 106 | completed | yes | 1 | 1 | yes | 93268 | 83456 | 2242 | 45.7959 |  |
| ts2-stream-keyed-upsert-order | A | 2 | 107 | completed | yes | 0 | 0 | yes | 79408 | 73728 | 1266 | 26.4254 |  |
| ts2-stream-keyed-upsert-order | B | 2 | 108 | completed | yes | 1 | 1 | yes | 92798 | 83712 | 1417 | 26.8839 |  |
| ts2-stream-decimal-money-parser | A | 2 | 109 | completed | yes | 0 | 0 | yes | 65402 | 58880 | 1606 | 32.508 |  |
| ts2-stream-decimal-money-parser | B | 2 | 110 | completed | yes | 1 | 1 | yes | 77896 | 68608 | 1310 | 36.235 |  |
| py2-ledger-weighted-allocation | B | 2 | 111 | completed | yes | 1 | 1 | yes | 90827 | 73728 | 1385 | 28.7092 |  |
| py2-ledger-weighted-allocation | A | 2 | 112 | completed | yes | 0 | 0 | yes | 64534 | 49280 | 1345 | 27.6695 |  |
| py2-ledger-csv-bank-import | A | 2 | 113 | completed | yes | 0 | 0 | yes | 64511 | 57600 | 1867 | 35.2517 |  |
| py2-ledger-csv-bank-import | B | 2 | 114 | completed | yes | 1 | 1 | yes | 131857 | 120704 | 2321 | 45.532 |  |
| py2-workflow-deep-settings-overlay | A | 2 | 115 | completed | yes | 0 | 0 | yes | 64204 | 45696 | 1468 | 25.9137 |  |
| py2-workflow-deep-settings-overlay | B | 2 | 116 | completed | yes | 1 | 1 | yes | 89764 | 81280 | 1422 | 31.2011 |  |
| py2-workflow-ready-job-order | A | 2 | 117 | completed | yes | 0 | 0 | yes | 49819 | 44032 | 1187 | 22.388 |  |
| py2-workflow-ready-job-order | B | 2 | 118 | completed | yes | 1 | 1 | yes | 91443 | 72832 | 1476 | 29.4601 |  |
| py2-ledger-invoice-line-discounts | B | 2 | 119 | completed | yes | 1 | 1 | yes | 91251 | 82432 | 1380 | 31.8637 |  |
| py2-ledger-invoice-line-discounts | A | 2 | 120 | completed | yes | 0 | 0 | yes | 64736 | 58496 | 1261 | 25.8095 |  |
| ts2-config-unicode-ascii-slugs | A | 2 | 121 | completed | yes | 0 | 0 | yes | 64079 | 45184 | 869 | 21.1501 |  |
| ts2-config-unicode-ascii-slugs | B | 2 | 122 | completed | yes | 1 | 1 | yes | 76634 | 58112 | 1043 | 26.6765 |  |
| ts2-stream-event-time-rolling-counts | A | 2 | 123 | completed | yes | 0 | 0 | yes | 64934 | 49792 | 1314 | 26.419 |  |
| ts2-stream-event-time-rolling-counts | B | 2 | 124 | completed | yes | 1 | 1 | yes | 93182 | 74240 | 1463 | 31.0384 |  |
| ts2-stream-fragmented-ndjson | A | 2 | 125 | completed | yes | 0 | 0 | yes | 64619 | 38400 | 1104 | 23.7314 |  |
| ts2-stream-fragmented-ndjson | B | 2 | 126 | completed | yes | 1 | 1 | yes | 76112 | 58880 | 1071 | 28.7296 |  |
| py2-ledger-nested-redaction | B | 2 | 127 | completed | yes | 1 | 1 | yes | 90960 | 83456 | 1414 | 27.814 |  |
| py2-ledger-nested-redaction | A | 2 | 128 | completed | yes | 0 | 0 | yes | 50158 | 44032 | 1476 | 27.7216 |  |
| py2-ledger-atomic-transfer | B | 2 | 129 | completed | yes | 1 | 1 | yes | 76084 | 66816 | 1679 | 31.7136 |  |
| py2-ledger-atomic-transfer | A | 2 | 130 | completed | yes | 0 | 0 | yes | 65128 | 45952 | 1658 | 37.9384 |  |
| py2-workflow-bounded-async-execution | A | 2 | 131 | completed | yes | 0 | 0 | yes | 78765 | 62848 | 1944 | 31.1209 |  |
| py2-workflow-bounded-async-execution | B | 2 | 132 | completed | yes | 1 | 1 | yes | 107342 | 98048 | 1890 | 35.7225 |  |
| ts2-config-casefold-header-collection | B | 2 | 133 | completed | yes | 1 | 1 | yes | 77549 | 58112 | 1849 | 38.91 |  |
| ts2-config-casefold-header-collection | A | 2 | 134 | completed | yes | 0 | 0 | yes | 95038 | 80384 | 2196 | 39.3768 |  |
| py2-workflow-capped-backoff | A | 2 | 135 | completed | yes | 0 | 0 | yes | 50397 | 44288 | 1283 | 26.2436 |  |
| py2-workflow-capped-backoff | B | 2 | 136 | completed | yes | 1 | 1 | yes | 71804 | 63872 | 1279 | 29.1197 |  |
| py2-workflow-deterministic-build-order | A | 2 | 137 | completed | yes | 0 | 0 | yes | 50134 | 35072 | 1461 | 27.8662 |  |
| py2-workflow-deterministic-build-order | B | 2 | 138 | completed | yes | 1 | 1 | yes | 90451 | 81792 | 1535 | 30.7221 |  |
| ts2-stream-escaped-record-codec | A | 2 | 139 | completed | yes | 0 | 0 | yes | 64598 | 49536 | 1108 | 28.6722 |  |
| ts2-stream-escaped-record-codec | B | 2 | 140 | completed | yes | 1 | 1 | yes | 91353 | 82688 | 1153 | 27.5522 |  |
| py2-workflow-strict-template-expansion | A | 2 | 141 | completed | yes | 0 | 0 | yes | 50041 | 41728 | 1169 | 24.6485 |  |
| py2-workflow-strict-template-expansion | B | 2 | 142 | completed | yes | 1 | 1 | yes | 72284 | 55808 | 1181 | 27.454 |  |
| ts2-config-utf8-feature-cohorts | B | 2 | 143 | completed | yes | 1 | 1 | yes | 94400 | 84608 | 1294 | 27.3934 |  |
| ts2-config-utf8-feature-cohorts | A | 2 | 144 | completed | yes | 0 | 0 | yes | 64015 | 37760 | 1033 | 22.4959 |  |
| ts2-stream-half-open-window-join | B | 2 | 145 | completed | yes | 1 | 1 | yes | 59020 | 40576 | 1396 | 26.2043 |  |
| ts2-stream-half-open-window-join | A | 2 | 146 | completed | yes | 0 | 0 | yes | 50469 | 35584 | 1156 | 24.0228 |  |
| ts2-config-quoted-env-values | B | 2 | 147 | completed | yes | 1 | 1 | yes | 95169 | 85632 | 1649 | 39.2697 |  |
| ts2-config-quoted-env-values | A | 2 | 148 | completed | yes | 0 | 0 | yes | 82507 | 74752 | 2636 | 39.2767 |  |
| ts2-config-safe-local-redirects | A | 2 | 149 | completed | yes | 0 | 0 | yes | 64781 | 58624 | 1353 | 23.9438 |  |
| ts2-config-safe-local-redirects | B | 2 | 150 | completed | yes | 1 | 1 | yes | 59394 | 50560 | 1324 | 28.2097 |  |
| py2-ledger-audit-hash-chain | B | 2 | 151 | completed | yes | 1 | 1 | yes | 74836 | 66176 | 1318 | 30.4053 |  |
| py2-ledger-audit-hash-chain | A | 2 | 152 | completed | yes | 0 | 0 | yes | 50132 | 44160 | 1107 | 22.4592 |  |
| py2-workflow-interval-coalescing | A | 2 | 153 | completed | yes | 0 | 0 | yes | 50198 | 44160 | 1229 | 22.8202 |  |
| py2-workflow-interval-coalescing | B | 2 | 154 | completed | yes | 1 | 1 | yes | 58818 | 50176 | 1269 | 27.4277 |  |
| ts2-stream-abort-aware-delay-plan | B | 2 | 155 | completed | yes | 1 | 1 | yes | 93445 | 74496 | 1438 | 31.6033 |  |
| ts2-stream-abort-aware-delay-plan | A | 2 | 156 | completed | yes | 0 | 0 | yes | 64512 | 58368 | 1104 | 22.1773 |  |
| py2-ledger-signed-tax-rounding | A | 2 | 157 | completed | yes | 0 | 0 | yes | 50058 | 44160 | 1266 | 21.9753 |  |
| py2-ledger-signed-tax-rounding | B | 2 | 158 | completed | yes | 1 | 1 | yes | 59200 | 50304 | 1322 | 25.6305 |  |
| py2-workflow-atomic-pointer-updates | B | 2 | 159 | completed | yes | 1 | 1 | yes | 92180 | 70912 | 1875 | 37.6629 |  |
| py2-workflow-atomic-pointer-updates | A | 2 | 160 | completed | yes | 0 | 0 | yes | 65461 | 58880 | 1558 | 28.275 |  |

### Per-run costs, reads, and local overhead

CPU values are sampled process CPU seconds (an observed lower bound); RSS values are sampled peaks in bytes. Short-lived processes may be missed. RSS may count shared pages more than once. Process-tree measurements include Codex and its observed children. Memglide-specific measurements cover only processes identified by the runner. Actual read counts are unavailable; command-intent proxy metrics appear separately.

| Task / configuration / repeat | Model calls | Repeated reads | Actual USD | Computed USD | Tree peak RSS | Tree CPU sec | Memglide peak RSS | Memglide CPU sec | Freshness | Completeness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ts2-config-strict-pointer-lookup / A / 1 | unavailable | unavailable | unavailable | unavailable | 361771008 | 6.16 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-strict-pointer-lookup / B / 1 | unavailable | unavailable | unavailable | unavailable | 415977472 | 7.41 | 72073216 | 2.24 | unavailable | unavailable |
| ts2-config-semantic-version-precedence / B / 1 | unavailable | unavailable | unavailable | unavailable | 366747648 | 6.96 | 72122368 | 1.55 | unavailable | unavailable |
| ts2-config-semantic-version-precedence / A / 1 | unavailable | unavailable | unavailable | unavailable | 277499904 | 4.87 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-reconciliation-version-merge / B / 1 | unavailable | unavailable | unavailable | unavailable | 350142464 | 7.72 | 71958528 | 2.09 | unavailable | unavailable |
| py2-ledger-reconciliation-version-merge / A / 1 | unavailable | unavailable | unavailable | unavailable | 196521984 | 3.81 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-currency-netting / B / 1 | unavailable | unavailable | unavailable | unavailable | 335826944 | 7.48 | 72101888 | 2.28 | unavailable | unavailable |
| py2-ledger-currency-netting / A / 1 | unavailable | unavailable | unavailable | unavailable | 258142208 | 4.91 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-utf8-batch-budget / B / 1 | unavailable | unavailable | unavailable | unavailable | 343453696 | 6.34 | 71794688 | 1.6 | unavailable | unavailable |
| py2-workflow-utf8-batch-budget / A / 1 | unavailable | unavailable | unavailable | unavailable | 194027520 | 3.27 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-complete-form-errors / B / 1 | unavailable | unavailable | unavailable | unavailable | 363536384 | 7.22 | 71987200 | 1.78 | unavailable | unavailable |
| ts2-config-complete-form-errors / A / 1 | unavailable | unavailable | unavailable | unavailable | 307036160 | 4.81 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-statement-timezones / B / 1 | unavailable | unavailable | unavailable | unavailable | 336093184 | 6.3 | 72224768 | 1.58 | unavailable | unavailable |
| py2-ledger-statement-timezones / A / 1 | unavailable | unavailable | unavailable | unavailable | 261341184 | 5.19 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-bounded-run-length-decode / B / 1 | unavailable | unavailable | unavailable | unavailable | 423276544 | 7.31 | 72306688 | 2.17 | unavailable | unavailable |
| ts2-stream-bounded-run-length-decode / A / 1 | unavailable | unavailable | unavailable | unavailable | 344813568 | 5.02 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-simultaneous-text-edits / B / 1 | unavailable | unavailable | unavailable | unavailable | 387715072 | 7.63 | 72388608 | 1.78 | unavailable | unavailable |
| ts2-stream-simultaneous-text-edits / A / 1 | unavailable | unavailable | unavailable | unavailable | 339288064 | 5.47 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-specific-route-matching / A / 1 | unavailable | unavailable | unavailable | unavailable | 358010880 | 6.1 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-specific-route-matching / B / 1 | unavailable | unavailable | unavailable | unavailable | 356421632 | 7.85 | 72589312 | 2.18 | unavailable | unavailable |
| py2-workflow-incremental-utf8-lines / A / 1 | unavailable | unavailable | unavailable | unavailable | 257282048 | 4.53 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-incremental-utf8-lines / B / 1 | unavailable | unavailable | unavailable | unavailable | 336883712 | 7.06 | 72183808 | 1.93 | unavailable | unavailable |
| ts2-config-repeated-query-values / A / 1 | unavailable | unavailable | unavailable | unavailable | 306561024 | 3.93 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-repeated-query-values / B / 1 | unavailable | unavailable | unavailable | unavailable | 436039680 | 7.27 | 72318976 | 1.88 | unavailable | unavailable |
| ts2-stream-transactional-accumulator / B / 1 | unavailable | unavailable | unavailable | unavailable | 391532544 | 7.34 | 72167424 | 2.16 | unavailable | unavailable |
| ts2-stream-transactional-accumulator / A / 1 | unavailable | unavailable | unavailable | unavailable | 348659712 | 4.7 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-keyed-upsert-order / B / 1 | unavailable | unavailable | unavailable | unavailable | 426795008 | 7.96 | 71946240 | 1.67 | unavailable | unavailable |
| ts2-stream-keyed-upsert-order / A / 1 | unavailable | unavailable | unavailable | unavailable | 337788928 | 4.83 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-decimal-money-parser / B / 1 | unavailable | unavailable | unavailable | unavailable | 386097152 | 7.17 | 71970816 | 1.6 | unavailable | unavailable |
| ts2-stream-decimal-money-parser / A / 1 | unavailable | unavailable | unavailable | unavailable | 296329216 | 7.28 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-weighted-allocation / A / 1 | unavailable | unavailable | unavailable | unavailable | 263094272 | 6.79 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-weighted-allocation / B / 1 | unavailable | unavailable | unavailable | unavailable | 337440768 | 14.45 | 71782400 | 2.06 | unavailable | unavailable |
| py2-ledger-csv-bank-import / B / 1 | unavailable | unavailable | unavailable | unavailable | 337883136 | 15.22 | 72146944 | 2.38 | unavailable | unavailable |
| py2-ledger-csv-bank-import / A / 1 | unavailable | unavailable | unavailable | unavailable | 258322432 | 4.98 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-deep-settings-overlay / B / 1 | unavailable | unavailable | unavailable | unavailable | 333066240 | 7.67 | 72372224 | 2.2 | unavailable | unavailable |
| py2-workflow-deep-settings-overlay / A / 1 | unavailable | unavailable | unavailable | unavailable | 177979392 | 19.39 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-ready-job-order / B / 1 | unavailable | unavailable | unavailable | unavailable | 337055744 | 11.31 | 72343552 | 2.08 | unavailable | unavailable |
| py2-workflow-ready-job-order / A / 1 | unavailable | unavailable | unavailable | unavailable | 264822784 | 10.02 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-invoice-line-discounts / A / 1 | unavailable | unavailable | unavailable | unavailable | 262483968 | 4.22 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-invoice-line-discounts / B / 1 | unavailable | unavailable | unavailable | unavailable | 341696512 | 5.88 | 72380416 | 1.57 | unavailable | unavailable |
| ts2-config-unicode-ascii-slugs / B / 1 | unavailable | unavailable | unavailable | unavailable | 381501440 | 7.53 | 72278016 | 2.58 | unavailable | unavailable |
| ts2-config-unicode-ascii-slugs / A / 1 | unavailable | unavailable | unavailable | unavailable | 295157760 | 4.36 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-event-time-rolling-counts / B / 1 | unavailable | unavailable | unavailable | unavailable | 361201664 | 6.87 | 72015872 | 1.55 | unavailable | unavailable |
| ts2-stream-event-time-rolling-counts / A / 1 | unavailable | unavailable | unavailable | unavailable | 343425024 | 5.72 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-fragmented-ndjson / B / 1 | unavailable | unavailable | unavailable | unavailable | 395071488 | 6.12 | 72056832 | 1.78 | unavailable | unavailable |
| ts2-stream-fragmented-ndjson / A / 1 | unavailable | unavailable | unavailable | unavailable | 306159616 | 4.89 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-nested-redaction / A / 1 | unavailable | unavailable | unavailable | unavailable | 267182080 | 4.35 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-nested-redaction / B / 1 | unavailable | unavailable | unavailable | unavailable | 334471168 | 6 | 72028160 | 1.85 | unavailable | unavailable |
| py2-ledger-atomic-transfer / A / 1 | unavailable | unavailable | unavailable | unavailable | 265371648 | 4.34 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-atomic-transfer / B / 1 | unavailable | unavailable | unavailable | unavailable | 351547392 | 13.64 | 72097792 | 1.46 | unavailable | unavailable |
| py2-workflow-bounded-async-execution / B / 1 | unavailable | unavailable | unavailable | unavailable | 349949952 | 6.99 | 72486912 | 1.97 | unavailable | unavailable |
| py2-workflow-bounded-async-execution / A / 1 | unavailable | unavailable | unavailable | unavailable | 274833408 | 5.02 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-casefold-header-collection / A / 1 | unavailable | unavailable | unavailable | unavailable | 340471808 | 6.12 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-casefold-header-collection / B / 1 | unavailable | unavailable | unavailable | unavailable | 435179520 | 7.25 | 72216576 | 1.94 | unavailable | unavailable |
| py2-workflow-capped-backoff / B / 1 | unavailable | unavailable | unavailable | unavailable | 334184448 | 6.24 | 72073216 | 2.27 | unavailable | unavailable |
| py2-workflow-capped-backoff / A / 1 | unavailable | unavailable | unavailable | unavailable | 239464448 | 3.61 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-deterministic-build-order / B / 1 | unavailable | unavailable | unavailable | unavailable | 331816960 | 5.86 | 72118272 | 2.16 | unavailable | unavailable |
| py2-workflow-deterministic-build-order / A / 1 | unavailable | unavailable | unavailable | unavailable | 188960768 | 3.64 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-escaped-record-codec / B / 1 | unavailable | unavailable | unavailable | unavailable | 378966016 | 6.01 | 71970816 | 1.55 | unavailable | unavailable |
| ts2-stream-escaped-record-codec / A / 1 | unavailable | unavailable | unavailable | unavailable | 323883008 | 4.43 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-strict-template-expansion / B / 1 | unavailable | unavailable | unavailable | unavailable | 274903040 | 5.29 | 72269824 | 1.73 | unavailable | unavailable |
| py2-workflow-strict-template-expansion / A / 1 | unavailable | unavailable | unavailable | unavailable | 192647168 | 2.73 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-utf8-feature-cohorts / A / 1 | unavailable | unavailable | unavailable | unavailable | 354299904 | 4.99 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-utf8-feature-cohorts / B / 1 | unavailable | unavailable | unavailable | unavailable | 427626496 | 6.29 | 72331264 | 1.83 | unavailable | unavailable |
| ts2-stream-half-open-window-join / A / 1 | unavailable | unavailable | unavailable | unavailable | 317775872 | 7.82 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-half-open-window-join / B / 1 | unavailable | unavailable | unavailable | unavailable | 440463360 | 6.83 | 72093696 | 2.11 | unavailable | unavailable |
| ts2-config-quoted-env-values / A / 1 | unavailable | unavailable | unavailable | unavailable | 333651968 | 4.56 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-quoted-env-values / B / 1 | unavailable | unavailable | unavailable | unavailable | 409612288 | 6.01 | 72298496 | 1.47 | unavailable | unavailable |
| ts2-config-safe-local-redirects / B / 1 | unavailable | unavailable | unavailable | unavailable | 475611136 | 6.62 | 72359936 | 1.96 | unavailable | unavailable |
| ts2-config-safe-local-redirects / A / 1 | unavailable | unavailable | unavailable | unavailable | 381415424 | 7.49 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-audit-hash-chain / A / 1 | unavailable | unavailable | unavailable | unavailable | 187678720 | 3.1 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-audit-hash-chain / B / 1 | unavailable | unavailable | unavailable | unavailable | 345726976 | 6.31 | 72425472 | 1.88 | unavailable | unavailable |
| py2-workflow-interval-coalescing / B / 1 | unavailable | unavailable | unavailable | unavailable | 268816384 | 5.06 | 72212480 | 2.02 | unavailable | unavailable |
| py2-workflow-interval-coalescing / A / 1 | unavailable | unavailable | unavailable | unavailable | 238895104 | 3.81 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-abort-aware-delay-plan / A / 1 | unavailable | unavailable | unavailable | unavailable | 312987648 | 4.14 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-abort-aware-delay-plan / B / 1 | unavailable | unavailable | unavailable | unavailable | 357879808 | 21.04 | 72355840 | 1.26 | unavailable | unavailable |
| py2-ledger-signed-tax-rounding / B / 1 | unavailable | unavailable | unavailable | unavailable | 339210240 | 6.21 | 72003584 | 1.65 | unavailable | unavailable |
| py2-ledger-signed-tax-rounding / A / 1 | unavailable | unavailable | unavailable | unavailable | 201498624 | 3.36 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-atomic-pointer-updates / A / 1 | unavailable | unavailable | unavailable | unavailable | 269869056 | 4.01 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-atomic-pointer-updates / B / 1 | unavailable | unavailable | unavailable | unavailable | 338587648 | 8.16 | 72048640 | 2.78 | unavailable | unavailable |
| ts2-config-strict-pointer-lookup / B / 2 | unavailable | unavailable | unavailable | unavailable | 404422656 | 11.17 | 72019968 | 2.57 | unavailable | unavailable |
| ts2-config-strict-pointer-lookup / A / 2 | unavailable | unavailable | unavailable | unavailable | 319832064 | 5.66 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-semantic-version-precedence / A / 2 | unavailable | unavailable | unavailable | unavailable | 327122944 | 12.12 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-semantic-version-precedence / B / 2 | unavailable | unavailable | unavailable | unavailable | 416980992 | 6.41 | 71991296 | 1.54 | unavailable | unavailable |
| py2-ledger-reconciliation-version-merge / A / 2 | unavailable | unavailable | unavailable | unavailable | 190705664 | 3.44 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-reconciliation-version-merge / B / 2 | unavailable | unavailable | unavailable | unavailable | 342757376 | 11.55 | 72220672 | 1.72 | unavailable | unavailable |
| py2-ledger-currency-netting / A / 2 | unavailable | unavailable | unavailable | unavailable | 250208256 | 10.89 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-currency-netting / B / 2 | unavailable | unavailable | unavailable | unavailable | 259723264 | 9.77 | 72314880 | 2.17 | unavailable | unavailable |
| py2-workflow-utf8-batch-budget / A / 2 | unavailable | unavailable | unavailable | unavailable | 192897024 | 3.02 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-utf8-batch-budget / B / 2 | unavailable | unavailable | unavailable | unavailable | 333545472 | 5.83 | 72642560 | 1.83 | unavailable | unavailable |
| ts2-config-complete-form-errors / A / 2 | unavailable | unavailable | unavailable | unavailable | 317046784 | 5.06 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-complete-form-errors / B / 2 | unavailable | unavailable | unavailable | unavailable | 378568704 | 8.03 | 72585216 | 1.55 | unavailable | unavailable |
| py2-ledger-statement-timezones / A / 2 | unavailable | unavailable | unavailable | unavailable | 263213056 | 4.99 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-statement-timezones / B / 2 | unavailable | unavailable | unavailable | unavailable | 352940032 | 6.34 | 72036352 | 1.87 | unavailable | unavailable |
| ts2-stream-bounded-run-length-decode / A / 2 | unavailable | unavailable | unavailable | unavailable | 315830272 | 4.68 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-bounded-run-length-decode / B / 2 | unavailable | unavailable | unavailable | unavailable | 392384512 | 9.16 | 72429568 | 1.9 | unavailable | unavailable |
| ts2-stream-simultaneous-text-edits / A / 2 | unavailable | unavailable | unavailable | unavailable | 345690112 | 6.08 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-simultaneous-text-edits / B / 2 | unavailable | unavailable | unavailable | unavailable | 416190464 | 6.53 | 72167424 | 1.55 | unavailable | unavailable |
| ts2-config-specific-route-matching / B / 2 | unavailable | unavailable | unavailable | unavailable | 414769152 | 7.7 | 71974912 | 2.42 | unavailable | unavailable |
| ts2-config-specific-route-matching / A / 2 | unavailable | unavailable | unavailable | unavailable | 309276672 | 5.66 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-incremental-utf8-lines / B / 2 | unavailable | unavailable | unavailable | unavailable | 345722880 | 5.67 | 72560640 | 1.38 | unavailable | unavailable |
| py2-workflow-incremental-utf8-lines / A / 2 | unavailable | unavailable | unavailable | unavailable | 254738432 | 3.97 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-repeated-query-values / B / 2 | unavailable | unavailable | unavailable | unavailable | 398053376 | 5.86 | 72302592 | 1.2 | unavailable | unavailable |
| ts2-config-repeated-query-values / A / 2 | unavailable | unavailable | unavailable | unavailable | 301506560 | 4.46 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-transactional-accumulator / A / 2 | unavailable | unavailable | unavailable | unavailable | 345985024 | 4.59 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-transactional-accumulator / B / 2 | unavailable | unavailable | unavailable | unavailable | 348205056 | 7.81 | 72294400 | 2.32 | unavailable | unavailable |
| ts2-stream-keyed-upsert-order / A / 2 | unavailable | unavailable | unavailable | unavailable | 319045632 | 4.94 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-keyed-upsert-order / B / 2 | unavailable | unavailable | unavailable | unavailable | 430153728 | 5.58 | 72364032 | 1.14 | unavailable | unavailable |
| ts2-stream-decimal-money-parser / A / 2 | unavailable | unavailable | unavailable | unavailable | 347394048 | 5.61 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-decimal-money-parser / B / 2 | unavailable | unavailable | unavailable | unavailable | 427966464 | 7.65 | 72015872 | 1.79 | unavailable | unavailable |
| py2-ledger-weighted-allocation / B / 2 | unavailable | unavailable | unavailable | unavailable | 379052032 | 6.46 | 72015872 | 1.61 | unavailable | unavailable |
| py2-ledger-weighted-allocation / A / 2 | unavailable | unavailable | unavailable | unavailable | 268099584 | 4.39 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-csv-bank-import / A / 2 | unavailable | unavailable | unavailable | unavailable | 258433024 | 4.06 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-csv-bank-import / B / 2 | unavailable | unavailable | unavailable | unavailable | 347848704 | 7.6 | 71888896 | 2.09 | unavailable | unavailable |
| py2-workflow-deep-settings-overlay / A / 2 | unavailable | unavailable | unavailable | unavailable | 264257536 | 5.16 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-deep-settings-overlay / B / 2 | unavailable | unavailable | unavailable | unavailable | 342204416 | 8.05 | 72081408 | 3.38 | unavailable | unavailable |
| py2-workflow-ready-job-order / A / 2 | unavailable | unavailable | unavailable | unavailable | 245178368 | 3.78 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-ready-job-order / B / 2 | unavailable | unavailable | unavailable | unavailable | 338894848 | 5.71 | 72294400 | 1.37 | unavailable | unavailable |
| py2-ledger-invoice-line-discounts / B / 2 | unavailable | unavailable | unavailable | unavailable | 335863808 | 6.77 | 72114176 | 1.8 | unavailable | unavailable |
| py2-ledger-invoice-line-discounts / A / 2 | unavailable | unavailable | unavailable | unavailable | 249176064 | 5.34 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-unicode-ascii-slugs / A / 2 | unavailable | unavailable | unavailable | unavailable | 299577344 | 5.78 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-unicode-ascii-slugs / B / 2 | unavailable | unavailable | unavailable | unavailable | 395890688 | 7.68 | 72286208 | 2.37 | unavailable | unavailable |
| ts2-stream-event-time-rolling-counts / A / 2 | unavailable | unavailable | unavailable | unavailable | 305303552 | 5.15 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-event-time-rolling-counts / B / 2 | unavailable | unavailable | unavailable | unavailable | 401367040 | 6.01 | 72069120 | 1.54 | unavailable | unavailable |
| ts2-stream-fragmented-ndjson / A / 2 | unavailable | unavailable | unavailable | unavailable | 298917888 | 4.54 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-fragmented-ndjson / B / 2 | unavailable | unavailable | unavailable | unavailable | 408739840 | 6.82 | 72495104 | 1.91 | unavailable | unavailable |
| py2-ledger-nested-redaction / B / 2 | unavailable | unavailable | unavailable | unavailable | 342925312 | 6.79 | 71892992 | 1.88 | unavailable | unavailable |
| py2-ledger-nested-redaction / A / 2 | unavailable | unavailable | unavailable | unavailable | 251650048 | 4.6 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-atomic-transfer / B / 2 | unavailable | unavailable | unavailable | unavailable | 341381120 | 5.82 | 72085504 | 1.59 | unavailable | unavailable |
| py2-ledger-atomic-transfer / A / 2 | unavailable | unavailable | unavailable | unavailable | 254029824 | 5.44 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-bounded-async-execution / A / 2 | unavailable | unavailable | unavailable | unavailable | 253816832 | 4.32 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-bounded-async-execution / B / 2 | unavailable | unavailable | unavailable | unavailable | 338018304 | 6.64 | 71921664 | 1.93 | unavailable | unavailable |
| ts2-config-casefold-header-collection / B / 2 | unavailable | unavailable | unavailable | unavailable | 350826496 | 6.39 | 72187904 | 1.45 | unavailable | unavailable |
| ts2-config-casefold-header-collection / A / 2 | unavailable | unavailable | unavailable | unavailable | 333864960 | 6.18 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-capped-backoff / A / 2 | unavailable | unavailable | unavailable | unavailable | 263217152 | 6.36 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-capped-backoff / B / 2 | unavailable | unavailable | unavailable | unavailable | 333791232 | 8.16 | 71950336 | 2.41 | unavailable | unavailable |
| py2-workflow-deterministic-build-order / A / 2 | unavailable | unavailable | unavailable | unavailable | 262086656 | 4.52 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-deterministic-build-order / B / 2 | unavailable | unavailable | unavailable | unavailable | 325419008 | 7.16 | 72167424 | 1.89 | unavailable | unavailable |
| ts2-stream-escaped-record-codec / A / 2 | unavailable | unavailable | unavailable | unavailable | 326512640 | 6.63 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-escaped-record-codec / B / 2 | unavailable | unavailable | unavailable | unavailable | 428601344 | 8.11 | 72454144 | 1.78 | unavailable | unavailable |
| py2-workflow-strict-template-expansion / A / 2 | unavailable | unavailable | unavailable | unavailable | 263000064 | 4.74 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-strict-template-expansion / B / 2 | unavailable | unavailable | unavailable | unavailable | 346460160 | 10.08 | 71880704 | 4.25 | unavailable | unavailable |
| ts2-config-utf8-feature-cohorts / B / 2 | unavailable | unavailable | unavailable | unavailable | 423727104 | 9.21 | 71884800 | 2.48 | unavailable | unavailable |
| ts2-config-utf8-feature-cohorts / A / 2 | unavailable | unavailable | unavailable | unavailable | 327360512 | 5.51 | unavailable | unavailable | unavailable | unavailable |
| ts2-stream-half-open-window-join / B / 2 | unavailable | unavailable | unavailable | unavailable | 412508160 | 7.81 | 72298496 | 2.56 | unavailable | unavailable |
| ts2-stream-half-open-window-join / A / 2 | unavailable | unavailable | unavailable | unavailable | 312303616 | 6.33 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-quoted-env-values / B / 2 | unavailable | unavailable | unavailable | unavailable | 414568448 | 8.51 | 72331264 | 2.62 | unavailable | unavailable |
| ts2-config-quoted-env-values / A / 2 | unavailable | unavailable | unavailable | unavailable | 337829888 | 5.79 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-safe-local-redirects / A / 2 | unavailable | unavailable | unavailable | unavailable | 318730240 | 5.34 | unavailable | unavailable | unavailable | unavailable |
| ts2-config-safe-local-redirects / B / 2 | unavailable | unavailable | unavailable | unavailable | 416890880 | 7.73 | 72388608 | 2.14 | unavailable | unavailable |
| py2-ledger-audit-hash-chain / B / 2 | unavailable | unavailable | unavailable | unavailable | 349270016 | 7.16 | 72507392 | 2.35 | unavailable | unavailable |
| py2-ledger-audit-hash-chain / A / 2 | unavailable | unavailable | unavailable | unavailable | 258854912 | 5.88 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-interval-coalescing / A / 2 | unavailable | unavailable | unavailable | unavailable | 194076672 | 4.6 | unavailable | unavailable | unavailable | unavailable |
| py2-workflow-interval-coalescing / B / 2 | unavailable | unavailable | unavailable | unavailable | 331026432 | 8.47 | 72413184 | 2.45 | unavailable | unavailable |
| ts2-stream-abort-aware-delay-plan / B / 2 | unavailable | unavailable | unavailable | unavailable | 419061760 | 9.64 | 72364032 | 2.18 | unavailable | unavailable |
| ts2-stream-abort-aware-delay-plan / A / 2 | unavailable | unavailable | unavailable | unavailable | 292528128 | 5.54 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-signed-tax-rounding / A / 2 | unavailable | unavailable | unavailable | unavailable | 198029312 | 3.91 | unavailable | unavailable | unavailable | unavailable |
| py2-ledger-signed-tax-rounding / B / 2 | unavailable | unavailable | unavailable | unavailable | 337424384 | 7.49 | 72515584 | 2.56 | unavailable | unavailable |
| py2-workflow-atomic-pointer-updates / B / 2 | unavailable | unavailable | unavailable | unavailable | 341229568 | 9.88 | 71831552 | 2.18 | unavailable | unavailable |
| py2-workflow-atomic-pointer-updates / A / 2 | unavailable | unavailable | unavailable | unavailable | 264351744 | 6.51 | unavailable | unavailable | unavailable | unavailable |

### MCP invocation evidence

Calls are deduplicated by CLI item ID across started/updated/completed events. A call that starts and fails is still an observed invocation. Enabled server configuration alone does not establish invocation.

- ts2-config-strict-pointer-lookup / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-semantic-version-precedence / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-reconciliation-version-merge / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-currency-netting / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-utf8-batch-budget / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-complete-form-errors / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-statement-timezones / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-bounded-run-length-decode / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-simultaneous-text-edits / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-specific-route-matching / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-incremental-utf8-lines / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-repeated-query-values / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-transactional-accumulator / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-keyed-upsert-order / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-decimal-money-parser / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-weighted-allocation / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-csv-bank-import / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-deep-settings-overlay / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-ready-job-order / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-invoice-line-discounts / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-unicode-ascii-slugs / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-event-time-rolling-counts / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-fragmented-ndjson / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-nested-redaction / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-atomic-transfer / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-bounded-async-execution / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-casefold-header-collection / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-capped-backoff / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-deterministic-build-order / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-escaped-record-codec / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-strict-template-expansion / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-utf8-feature-cohorts / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-half-open-window-join / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-quoted-env-values / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-safe-local-redirects / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-audit-hash-chain / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-interval-coalescing / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-abort-aware-delay-plan / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-signed-tax-rounding / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-atomic-pointer-updates / B / repeat 1: memglide.fetch_context (status=completed, completed=True)
- ts2-config-strict-pointer-lookup / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-semantic-version-precedence / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-reconciliation-version-merge / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-currency-netting / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-utf8-batch-budget / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-complete-form-errors / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-statement-timezones / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-bounded-run-length-decode / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-simultaneous-text-edits / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-specific-route-matching / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-incremental-utf8-lines / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-repeated-query-values / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-transactional-accumulator / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-keyed-upsert-order / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-decimal-money-parser / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-weighted-allocation / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-csv-bank-import / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-deep-settings-overlay / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-ready-job-order / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-invoice-line-discounts / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-unicode-ascii-slugs / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-event-time-rolling-counts / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-fragmented-ndjson / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-nested-redaction / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-atomic-transfer / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-bounded-async-execution / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-casefold-header-collection / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-capped-backoff / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-deterministic-build-order / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-escaped-record-codec / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-strict-template-expansion / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-utf8-feature-cohorts / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-half-open-window-join / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-quoted-env-values / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-config-safe-local-redirects / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-audit-hash-chain / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-interval-coalescing / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- ts2-stream-abort-aware-delay-plan / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-ledger-signed-tax-rounding / B / repeat 2: memglide.fetch_context (status=completed, completed=True)
- py2-workflow-atomic-pointer-updates / B / repeat 2: memglide.fetch_context (status=completed, completed=True)

## Paired differences

Verified attempted A/B pairs: **80**. Differences are B minus A. Failed tasks remain in paired observations.

| Metric | Mean difference | Median difference | Pairs with measurements | Missing |
| --- | ---: | ---: | ---: | ---: |
| input_tokens | 20638.8 | 24184.5 | 80 | 0 |
| cached_input_tokens | 20372.8 | 21312 | 80 | 0 |
| output_tokens | 75.4875 | 72 | 80 | 0 |
| model_calls | unavailable | unavailable | 0 | 80 |
| mcp_calls | 1 | 1 | 80 | 0 |
| memglide_mcp_calls | 1 | 1 | 80 | 0 |
| observed_mcp_calls | 1 | 1 | 80 | 0 |
| observed_memglide_mcp_calls | 1 | 1 | 80 | 0 |
| wall_time_seconds | 4.67393 | 4.46462 | 80 | 0 |
| end_to_end_wall_seconds | 4.88146 | 4.66113 | 80 | 0 |
| setup_wall_seconds | unavailable | unavailable | 0 | 80 |
| setup_cpu_seconds | unavailable | unavailable | 0 | 80 |
| repeated_file_reads | unavailable | unavailable | 0 | 80 |
| observed_file_read_commands | -0.0875 | 0 | 80 | 0 |
| observed_repeated_read_commands | 0 | 0 | 80 | 0 |
| actual_cost_usd | unavailable | unavailable | 0 | 80 |
| computed_cost_usd | unavailable | unavailable | 0 | 80 |
| process_tree_peak_rss_bytes | 8.66537e+07 | 8.65157e+07 | 80 | 0 |
| cpu_seconds | 2.38437 | 2.175 | 80 | 0 |
| memglide_peak_rss_bytes | unavailable | unavailable | 0 | 80 |
| memglide_cpu_seconds | unavailable | unavailable | 0 | 80 |
| context_freshness | unavailable | unavailable | 0 | 80 |
| retrieval_completeness | unavailable | unavailable | 0 | 80 |
| probe_target_path_coverage_fraction | unavailable | unavailable | 0 | 80 |
| probe_expected_symbol_coverage_fraction | unavailable | unavailable | 0 | 80 |

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
