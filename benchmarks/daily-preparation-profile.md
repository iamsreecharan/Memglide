# Local preparation component profile

Measured `2026-10-18T02:08:58.534224+00:00` to `2026-10-18T02:08:58.751276+00:00`. The [JSON report](daily-preparation-profile.json) contains every one of the **1,520 observations**, separate setup times, fixture/source hashes and measurement boundaries.

This measures the already imported `prepare_prompt` function on an independent trusted two-file Git fixture. **It excludes Python process startup, the native launcher, Codex execution, model usage and full task cost.** It cannot establish token or cost savings, nor a whole-task speed improvement.

## Measured warm-process API overhead

Times are milliseconds; p95 uses nearest rank. All outliers remain in the raw JSON.

| Path | Calls | Wall mean | Wall median | Wall p95 | Wall maximum | CPU median | Added bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| off | 500 | 0.043166 | 0.017626 | 0.149240 | 0.969599 | 0.017229 | 0 |
| context_supplied | 500 | 0.054100 | 0.017691 | 0.148447 | 2.217083 | 0.017265 | 0 |
| no_focus | 500 | 0.013062 | 0.003814 | 0.009717 | 2.014815 | 0.003418 | 0 |
| scoped_preload | 20 | 7.744729 | 7.377205 | 10.676856 | 17.257012 | 7.007787 | 649 |

`off` and `context_supplied` still validate two explicit focus paths; `no_focus` has no paths to validate. That difference contributes to their different function timings. Each bypass returned the exact original task and no source. Every scoped call returned both complete files and matching independently computed hashes. The addition was 649 UTF-8 bytes including explanation, paths, hashes, line ranges and JSON; bytes are not model tokens.

The 500 calls per bypass were interleaved using a seeded shuffle. The 20 scoped calls followed them. This is one warm-process component sample, not a cold/warm A/B. Fixture setup imported the production service before measuring scoped preparation, so heavy setup dependencies and filesystem state were already warm. Internal function timing fields are retained alongside the outer `perf_counter_ns` / `process_time_ns` measurements. No failed or slow observation was discarded.

## Setup measured separately

The fixture used an actual Git repository plus production database initialization, project approval and initial indexing. No benchmark task, gold patch or hidden assertion from the fresh 20-task evaluation was read.

| Setup stage | Wall milliseconds | Current-process CPU milliseconds |
| --- | ---: | ---: |
| trusted_git_fixture_initialization | 11.504195 | 1.004408 |
| preparation_module_import | 9.137067 | 9.139279 |
| production_service_import_for_fixture_setup | 70.204464 | 69.900433 |
| production_database_and_service_initialization | 37.700984 | 13.555827 |
| production_approval_and_initial_index | 198.513693 | 35.330845 |

Setup subprocess CPU is outside `process_time_ns`; these CPU figures are for the current Python process. Approval/indexing belongs in a full cold task measurement whenever incurred and cannot be subtracted just because it is reported separately here. The tiny fixture is 97 source bytes across `totals.py` and `types.ts`; it is not representative of a large repository.

## What this establishes

The gate is implemented without a model classifier, and inspection plus existing guarded preparation/launcher tests establish that it does not invoke model clients, network requests or an MCP process. The component script made **zero model, native Codex and MCP requests**. This is not general operating-system syscall telemetry, and one native exec must not later be mislabeled as one underlying model call.

The measurements show low function overhead for these explicit skip cases and millisecond-level source preparation for this small warm fixture. They do not show whether an added source bundle saves enough native searches, reads or interactions to compensate for its input tokens. Only the frozen native comparison can answer that.

Runner/corpus tests were briefly paused and root frontend work had finished during the short collection window. The host remained shared: unrelated activity, scheduling and OS caches were not controlled. No provider cache claims can be made because no provider request was issued. The JSON records process/platform versions and full min/mean/median/p95/max distributions for wall and CPU.

## Measured implementation identity

- `src/memglide/integrations/preload.py`: SHA-256 `e1bf1bc2bddff34d1ce68872ba762599b1426d140724a8c60fd26bcb8ff8d805`
- `src/memglide/integrations/codex_preload.py`: SHA-256 `4bef2eff9163d5aebf419d309ec89bbcdea1e8427c57cf9d4a6cdf3fc8a8cb66`

Profiler SHA-256: `41f6f6441d3c5fd5096aef2099a83e1c56f09fc4160b29e215b98b6ada8f31d1`. The collection script, original raw capture and trusted fixture remain in ignored `.local/daily-v1/preparation-profile`; the public JSON preserves all observed timings. Source hashes were unchanged across collection. Timing code did not modify application or evaluation source.
