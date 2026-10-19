# Memglide: local efficiency and product architecture assessment

The best-supported direction is a small **local context engine with an optional SaaS control plane**. This round reduces repeated local indexing, database and dashboard work without adding a selector model, remote vector service or extra retrieval round trip. The measured improvements are local component results. They do not establish a lower model bill, faster native coding tasks or hosted production readiness.

The [architecture](../docs/product-efficiency-architecture.md) describes the implemented changes and remaining product work. The [JSON assessment](saas-efficiency-assessment.json) retains source-report references, exact numbers, research scopes and explicit unknowns.

## What changed

- **Graph resolution:** an unchanged live-validated source set reuses graph targets. Actual additions, edits, deletions, explicit full rebuilds and resolver-version migrations still resolve the graph.
- **Scan memory:** unchanged file bodies are released after the same secure read, hash and byte accounting. Changed/new files retain full bodies. Complete live reads, source policy and index limits remain authoritative.
- **Watcher:** scheduling reads small fields rather than full project reports; event-driven scans satisfy periodic reconciliation; slow scans cannot create continuous audit loops. Shutdown retains a still-running worker so restart cannot create duplicates. Moves check both endpoints.
- **Dashboard:** reuse one session list and fetch the 20 event rows displayed rather than fetching 500 and discarding 480. The compared response remains equal.
- **Database:** nine additive indexes remove measured history sorts and foreign-key child scans. Upgrades preserve stored records and existing isolation.

Foreground refreshes retain their existing full live scans. Background reconciliation remains configured at five seconds, plus debounced events and polling fallback. The interval follows completed attempts; scan time and contention can extend start-to-start lag. This is not a five-second freshness guarantee. The four changes do not change source-preload formats or native event-stream processing, and source-only remains the default.

## New local measurements

| Probe and population | Before | After | Interpretation |
| --- | ---: | ---: | --- |
| Graph: unchanged 600-file repository, 10 runs/arm; mean wall time | 0.715832 s | 0.631705 s | 11.75% lower component point mean |
| Same graph probe; mean process CPU | 0.609627 s | 0.529591 s | 13.13% lower; child CPU recorded separately |
| Same graph probe; graph-row updates per refresh | 1,198 | 0 | Same graph outputs and source hashes |
| Same graph probe; secure source reads per refresh | 600 | 600 | Live source validation preserved |
| Scan: unchanged 40-file / 20 MiB fixture, 10 runs/arm; mean peak Python allocations | 21,525,591 B | 1,601,119 B | 92.56% lower `tracemalloc` peak; not RSS |
| Same instrumented scan probe; mean wall time | 3.974534 s | 3.666382 s | 7.75% lower instrumented component point mean |
| Same scan probe; mean retained unchanged source bodies | 20,971,520 B | 0 B | Bodies released after validation; hashes retained |
| Same scan probe; secure source reads per refresh | 40 | 40 | Source hashes equal in every measured run |
| Scheduler: 60 virtual ticks / 12 logical seconds, 25 projects; DB connections | 120 | 12 | Scheduling bookkeeping only |
| Same scheduler fixture; decoded JSON bytes | 68,877,900 B | 48 B | Full reports no longer decoded for scheduling |
| Same scheduler fixture; no-op scan calls | 75 | 75 | Identical project-scan sequence |
| Dashboard fixture; event rows fetched | 500 | 20 | Equal compared response |
| Same dashboard fixture; cleanup / session-list calls | 4 / 2 | 2 / 1 | Less repeated work |

The [graph](saas-graph-efficiency.md) baseline emulates only the former unconditional resolver branch inside current trusted reindex code; it is not the entire old application. Both graph arms share the current scanner. The [scan](saas-scan-efficiency.md) comparison holds scanner code common and changes retention of bodies already verified unchanged. Graph and scan timing runs briefly overlapped; host load and OS caches were uncontrolled. Keep their percentages separate. `tracemalloc` covers Python allocation peaks, not full process, native or remote memory. Child CPU is not included in process CPU.

The [scheduler observations](saas-scheduler-efficiency.json) compare actual pinned prior watcher/service source with current code, using current database/imported helpers common to both. Virtual waits and repository scans are not performed. Recorded compute time concerns this bookkeeping fixture, not 12 seconds of live daemon behavior or model latency.

The [initial graph cohort](saas-graph-efficiency-initial.json) is also retained: mean wall time 0.233646 → 0.213604 seconds, 8.58% lower. Its earlier source/measurement context differs; it is not pooled with the later 11.75% observation or used to choose a preferred timing result. All individual runs, means, medians and applicable totals remain in their original JSON reports.

## Database work and its tradeoff

The [database probe](saas-database-efficiency.md) ran three complete attempts on identical synthetic data: 100 projects, 5,000 rows in each main child table and 10,000 events. The old-schema simulation drops only the nine new indexes, then restores those definitions on the same fixture. The table shows SQLite VM instructions, **not milliseconds or model tokens**.

| Query or operation | Before instructions | After instructions |
| --- | ---: | ---: |
| Recent 500 global events | 152,509 | 5,508 |
| Project event history | 31,912 | 1,216 |
| Recent 20 retrievals | 85,149 | 268 |
| Project session list | 16,312 | 863 |
| Source invalidation lookup | 15,820 | 1,024 |
| Delete file with symbol cascade | 35,067 | 80 |
| Delete session with dependent-record cascades | 70,310 | 368 |
| Append one event | 44 | 55 |

All three formal attempts report those counts, unchanged full-data fingerprints, equal returned row multisets, successful integrity checks and no foreign-key violations. Mutations roll back between probes. A separate exploratory observation is retained: its first recent-events count was 152,775 rather than 152,509; other pairs matched. It is not pooled into the formal repetitions.

The nine indexes occupy **839,680 bytes**, growing this fixture's database from 3,686,400 to 4,526,080 bytes. Event insertion requires additional index writes, as its higher VM count shows. This is one insert shape, not a measured throughput percentage. Initial index creation takes a database write lock. Query plans and each index's size are available in the [raw JSON](saas-database-efficiency.json).

## Research that informed the decisions

Six newly checked primary sources are recorded with response hashes, reading scope and one failed URL in the [research ledger](saas-efficiency-research.json): SQLite's [WAL locking notes](https://github.com/sqlite/sqlite/blob/master/doc/wal-lock.md), selected [FTS5 query-planning source](https://github.com/sqlite/sqlite/blob/master/ext/fts5/fts5_main.c), selected [ripgrep filtering guidance](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md), the [VS Code base watcher](https://github.com/microsoft/vscode/blob/main/src/vs/platform/files/node/watcher/baseWatcher.ts), and the official MCP [tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/tools.mdx) and [resources](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/resources.mdx) specifications. Upstream branch URLs are mutable; retained response hashes identify the inspected content.

These sources favor bounded work, targeted failure handling, secure scanning and explicit evidence access. They do not supply a Memglide speedup percentage. FTS-rowid mapping, native-only watching, an IDE resource picker and hosted control-plane infrastructure remain separate candidates requiring implementation and tests. None is presented as completed here.

## Native Codex results remain a separate historical cohort

The prior [frozen assessment](efficiency-assessment.md) retains 120 native assignments across two different corpora. The original 60 had zero strict successes because all runs changed protected existing tests. Those failures remain visible; behavior-only passing checks did not replace the strict grader. After clarifying instructions, a fresh 60-assignment study achieved 20/20 strict successes in each of A, B and C.

On that fresh study's **16 focused assignments per arm**, source-only B had a **10.19% lower point API-price-equivalent cost per successful task** than bare A, with **3.18% longer mean full time**. Support-file C was **8.66% more expensive by that estimate and 9.16% slower** than source-only B. C failed 17 of 24 predeclared cost/time checks, so support remains optional. These studies evaluated source preload with zero configured MCP calls; MCP functionality was tested separately.

Those are outcomes on the frozen prior implementation, not outcomes on the new local code. **Actual billed cost and cash savings remain unknown.** Cached-input pricing, cache-write attribution, provider/cache variability and unsuccessful attempts must remain in cost accounting. Local VM work, source bytes or fewer command mentions cannot establish model token or dollar savings.

## Memory evaluation and current verification

The opt-in [memory preparation API](../docs/memory-preload.md) passes **43 regression cases and nine real prerequisite checks**. The [warm-task evaluation](warm-80-analysis.md) completed 80 passing assignments after fresh device authorization and stopped at the user's request. An already-started 81st original was interrupted and retained; 135 planned assignments remain unrun. The descriptive matched first 72 runs contain eight complete sequences (five TypeScript, three Python), 24 unique tasks and one repeat. Source-only B has a 9.05% lower API-price-equivalent cost and 6.89% lower mean instrumented time than A; warm C is 12.35% costlier and 3.40% slower than B. The [final offline audit](warm-v2-final-integrity-audit.md) passes 2,595 checks with 18 unavailable and incomplete coverage. The first failed authentication cohort and initial interrupted-accounting audit failures remain preserved. Actual billing and C's total attempted-cohort cost remain unavailable; this partial study does not justify default memory promotion. The initial memory scope is related native sessions sharing one **still-active Memglide session**. It is not durable memory after that Memglide session ends or expires. Closing a native Codex session and ending a Memglide session are different operations. Preload alone does not bridge either lifecycle.

The warm evaluation must include writing and reading memories, preparation costs and unsuccessful attempts; preserve current-source validation; use fresh matched tasks and controls; and grade independently. Larger unfamiliar repositories and durable cross-session product behavior need separate studies.

Targeted verification completed so far: 11 new database regression cases pass; a relevant security/indexing/memory/lifecycle/request-scope/transport run passes 168 cases; the combined database/watcher run passes 22. Those counts overlap and must not be added as distinct tests. Database/probe files pass Ruff and mypy. **24 frontend tests, three production Chromium cases and clean installed-wheel CLI/API/SPA plus real default/agent MCP checks pass.** The [complete Python regression](saas-efficiency-validation.md) passed **1,626 cases**; two later recovery cases passed separately, for **1,628 distinct verified Python cases**. Runtime application source stayed unchanged. An initial run was stopped after 390 passes and one temporary-artifact-root fixture failure; that test now declares its root explicitly, with two containment regressions, and all 16 comparison cases pass. No artifact-reader security check was weakened. The JSON keeps the initial failure and the final completed regression receipt.

## Product decision

Keep source-only and deterministic bypass as defaults, ship the verified local work reductions, and retain live evidence checks. An optional SaaS control plane can be designed separately without uploading source or adding a network dependency to each request. Explicit event retention, visible quotas, versioned pagination, attributable model telemetry and a successful warm-task comparison remain product priorities. Hosted authentication, tenant isolation, billing and operational recovery must be established before calling this a hosted production-ready SaaS.
