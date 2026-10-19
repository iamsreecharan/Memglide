# Memglide efficiency: research and a practical product architecture

This review favors a **local context engine with an optional SaaS control plane**. Keep current source selection, freshness checks and repository data near the developer. Remove avoidable local database and bookkeeping work before introducing another network service or model call. This is an architecture recommendation and scoped source review, not a claim that Memglide is production-ready or cheaper than Codex.

The [research ledger](saas-efficiency-research.json) identifies six newly checked primary sources, response hashes, exact reading scopes and one failed URL. Downloads used the inherited HTTPS proxy and TLS verification. This review made **zero model requests**, inspected no authentication material and changed no network policy.

## What is worth preserving

The existing native confirmation study found source-only preparation had a lower **point API-price-equivalent cost** on focused tasks, with slightly longer mean completion time. Adding complete support tests reduced recognized read commands but increased total commands, ordinary input, output and mean time relative to source-only. These observations support keeping source-only as the default and support material explicit. They do not prove actual subscription or billed-dollar savings; see [the frozen assessment](efficiency-assessment.md).

Preserve deterministic passthrough for off, supplied-context, missing-focus and missing-project cases. Preserve complete selected source, bounded output, approval and current ignore-policy checks, secure current file reads and honest missing-evidence warnings. The existing agent MCP profile already consolidates context into a small tool surface; adding another planner or discovery service needs evidence that it removes more work than it adds.

## Findings that add to the earlier review

### 1. Native file notifications and polling have different roles

Microsoft's [VS Code base watcher](https://github.com/microsoft/vscode/blob/main/src/vs/platform/files/node/watcher/baseWatcher.ts) tracks individual failed/suspended watch requests. It first tries an existing recursive watcher and falls back to polling the suspended path when needed. Its update path also batches watcher changes. This is a useful example of containing bookkeeping and failure recovery to affected requests.

Memglide currently debounces native events but also performs a full reconciliation every five seconds. That reconciliation securely reads/hashes eligible source, so it remains a substantial potential I/O cost. **The selected changes in this round retain the five-second reconciliation and existing source-freshness behavior** while reducing repeated watcher bookkeeping and fixing shutdown races. Moving to native-only or less frequent reconciliation would change missed-event recovery latency; it requires explicit overflow, notification-loss, rename, ignore-change, mount and observer-failure tests first. An unchanged mtime is not sufficient proof that source content is unchanged.

### 2. Avoid repeated graph resolution when its input is unchanged

The application rebuilds graph targets after indexing. A repository scan with no added, modified or removed eligible files does not introduce a new graph input. Conditional graph resolution can therefore remove repeated SQL work while retaining full source reconciliation and current readback. Search-index migrations, explicit full rebuilds and actual file-set/content changes must still take their required paths. Equivalence tests and the local performance report, rather than the general research sources, establish whether this specific implementation is safe and useful.

### 3. FTS column equality is not a B-tree lookup

SQLite's [FTS5 query-planning implementation](https://github.com/sqlite/sqlite/blob/master/ext/fts5/fts5_main.c#L538) recognizes MATCH constraints and rowid equality/ranges. Ordinary equality on stored FTS columns does not gain a relational composite-index lookup. This matters because Memglide performs FTS updates/deletes using project/path predicates.

A local SQLite 3.53.1 `EXPLAIN QUERY PLAN` probe confirmed a project/path predicate used `VIRTUAL TABLE INDEX 0:`, whereas explicit rowid equality used `VIRTUAL TABLE INDEX 0:=`. This verifies plan selection, **not elapsed-time savings**. SQLite's planner cost constants are internal estimates and must not be presented as a runtime speedup.

An indexed relational mapping from `(project_id, path)` to FTS rowid is a promising **next candidate, not implemented in this round**. It needs migration/backfill, insert/delete/update atomicity, project-removal, restart, orphan/duplicate detection and multi-project isolation tests, plus measured update/search performance. Do not write directly to FTS shadow tables. Additive indexes on ordinary relational query and foreign-key access paths are a smaller change that can be evaluated independently.

### 4. WAL and a timeout do not remove all database concurrency risks

SQLite's [WAL blocking-lock document](https://github.com/sqlite/sqlite/blob/master/doc/wal-lock.md) explains that POSIX blocking-lock behavior requires a suitable SQLite build and timeout configuration. Read-to-write upgrades and timeout expiry can still return `SQLITE_BUSY`. Memglide already uses WAL and a busy timeout; increasing timeouts alone is not a throughput fix.

Keep transactions bounded, avoid unnecessary writes and preserve atomic publication. Do not assume that every deployed Python SQLite build supports the optional blocking-lock implementation described in this source. No new SQLite compile option, shared cross-thread connection or global connection pool is justified by this review alone.

### 5. A faster scanner must preserve Memglide's own policy

The official [ripgrep guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md) documents ignore precedence, hidden/binary filtering and not following symlinks by default. It also explains that an explicitly named file can behave differently from a recursively discovered file.

Using ripgrep or Git's tracked-file list as an index manifest would therefore change semantics unless reconciled with Memglide's untracked-file handling, nested `.memglideignore`, configured exclusions, secret policy, symlink rejection and size/resource limits. Keep the secure reader as the authority. A replacement scanner is a separately tested candidate, not a drop-in speed fix.

### 6. MCP resources can support product UX, but add a read step

The official MCP [tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/tools.mdx) and [resources](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/resources.mdx) specifications distinguish model-controlled tools from application-driven resources. Resource links and optional update subscriptions can let a host present evidence for selection without embedding every body immediately. The host still decides whether and how to fetch/include that content.

For Memglide's existing one-call focused retrieval, replacing complete evidence with links can add an interaction and leave required context unread. Keep the current complete bounded response as the default. An IDE evidence picker with explicit resource reads is a reasonable future product option when the host supports it. Preserve URI validation, authorization and current-source checks; subscription notifications are not proof that no source change was missed.

## Keep the local data plane small

Use the existing local service and SQLite database as the data plane: explicit repository approval, secure indexing, lexical/symbol retrieval, current-source validation, bounded evidence delivery and provenance-bearing memory. CLI, MCP and the loopback HTTP API should continue sharing those services and access rules. Repository code and stored text remain untrusted data.

An optional SaaS control plane can later manage accounts, organizations, entitlements, release channels and explicit policy configuration. Source bodies, local paths and memory contents should not be uploaded merely to enable these features. Any diagnostics export should be explicit, bounded and reviewed for sensitive content. Remote access, tenant isolation, authentication, TLS, billing and operational recovery are separate engineering work; the current local efficiency changes do not establish those guarantees.

The critical request path should remain usable locally without a round trip to a control-plane server. This reduces a source of service dependency and latency, but no quantitative reliability or timing improvement has been measured for a hosted architecture here.

## Why extra models and vector services stay optional

An LLM selector adds a paid inference and network latency before the coding task. External embeddings add generation cost, an index lifecycle, privacy decisions and freshness coordination. A graph service or reflection worker adds process and operational overhead. None is warranted by the current small same-day fixture results. Lexical/symbol retrieval is already a strong deterministic fit for explicit identifiers and paths; ambiguity and large cross-session work remain appropriate held-out research workloads.

This is not a claim that embeddings can never help. Add them behind an explicit option only after comparing end-to-end successful-task cost, relevance/completeness, freshness, latency and local/remote resource use against the existing path. Include extraction, embedding, indexing and failed-attempt costs. A semantic score alone does not demonstrate a product benefit.

## Token and cache conclusions remain bounded

The earlier [efficiency research](efficiency-research.md) and its pinned Codex 0.159.2 source inspection remain applicable. A stable prefix inside one changing native user message does not prove a reusable cache boundary. The inspected CLI does not expose arbitrary multi-message/cache-breakpoint control. Native continuation preserves history but can incur billable prior input; unobserved compaction makes an unchanged file hash plus a thread ID insufficient proof that source remains in context.

Do not move source into privileged instructions, manipulate hidden cache headers, automatically omit source based on a receipt, or price bytes as measured tokens. Keep actual billing unknown where unavailable, report observed native token categories separately and preserve the cache-write accounting caveat. Removing local SQL work can be measured as local work; it is not evidence of model token or dollar savings.

## Evaluation and promotion

The selected engineering work is deliberately narrow: conditional unchanged graph resolution, ordinary relational indexes, less repeated watcher bookkeeping and a shutdown-race fix. Validate correctness and source freshness first, then measure unchanged, one-file-change, rename/delete, multi-project and concurrent request workloads. Record actual SQL counts, secure source reads, CPU/wall time and memory where observable, keeping warm/cold conditions explicit.

Any later source-selection or delivery change requires fresh independently graded native A/B tasks with matched settings and all failures retained. Preserve source-only as the default until an alternative passes correctness, completeness and freshness checks and demonstrates acceptable cost-per-success and latency. No universal best architecture, faster model or cash-saving claim follows from this review.
