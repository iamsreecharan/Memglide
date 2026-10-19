# SaaS efficiency: local scan component probe

These are local component measurements. No Codex/model request was made; model tokens, model latency, actual charges and cost savings are unknown.

## Method

Current _scan with default complete-source retention

Both arms use the same live secure source reader. Graph comparison holds the current scanner common; scan comparison holds the scanner code common and changes only retention of bodies already verified unchanged.

The graph baseline is an explicit old-branch emulation, not a benchmark of the entire historical application. Its resolver semantics and exact call are checked against the pinned prior Git source. OS caches are uncontrolled. Results describe this synthetic fixture, not SaaS throughput.

Prior source: `6de6f150aaa90fba14e49439723a8139c03217eb` / `src/memglide/core/indexer.py`; SHA256 `7c49242c79ee0b1f3aa1cc03c066f863de1727c91c3be7768c61201ace5d99c6`.

Current source SHA256 `ab97faacfccd032e8dfae73ee526ad0952f877b646bb8c061466b14e270cf5ad`.

Fixture: `{"alternating_order": true, "files": 40, "os_cache_controlled": false, "repeats_per_arm": 10, "secure_full_scan_both_arms": true, "source_bytes": 20971520, "tracemalloc_enabled_both_arms": true}`.

## Measurements

| Metric | Baseline mean | Candidate mean | Change |
|---|---:|---:|---:|
| wall_seconds | 3.974534 | 3.666382 | -7.75% |
| process_cpu_seconds | 3.765276 | 3.499755 | -7.05% |
| tracemalloc_peak_bytes | 21525591.200000 | 1601118.800000 | -92.56% |
| retained_source_bytes | 20971520.000000 | 0.000000 | -100.00% |
| secure_source_reads | 40.000000 | 40.000000 | +0.00% |

Full individual samples, medians and totals are retained in the adjacent JSON.
Graph outputs and source hashes must match across every measured run; an assertion failure stops publication. Counts of secure reads stay unchanged.

`process_cpu_seconds` excludes child processes; graph JSON reports child CPU separately. `tracemalloc_peak_bytes` measures Python allocations during instrumented scanning, not total process RSS or server memory. Instrumented scan timing should not be treated as uninstrumented application latency.

## Reproduce

```sh
uv run python benchmarks/saas_graph_efficiency.py --component scan
```

## Run limitations

Host load and operating-system caches were uncontrolled. The graph and scan probes briefly overlapped; preserve each cohort separately and do not pool their timings. These point observations do not establish model savings or SaaS throughput.
