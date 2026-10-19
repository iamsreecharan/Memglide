# Automatic-source implementation plan and repository audit

The audit preceded application edits. Baseline: commit
`7206b8e7f76599d742d69a9a2e218b9bfb1f54ac`. The user-facing plan was announced before
implementation; this artifact records its concrete extension points.

Already working: Indexer natural-language normalization, project DF/BM25, exact
symbol/path and signature ranking, conservative graph relationships, deterministic
explanations; ContextEngine focused/dependency expansion and range deduplication;
source-only secure complete-file delivery and read-only approval/ignore checks;
cheap off/context-supplied bypasses; private source receipts and native launcher;
optional expiring memory, API/CLI/MCP and dashboard. The recent favorable native
point result supplied known paths and does not prove automatic discovery.

Missing integration: an opt-in path-free task-to-preload adapter with explicit
abstention, file-level deduplication, cost-proxy bounds and no memory/session side
effects. ContextEngine is not reused for launch preparation because it also
manages sessions, memories and retrieval history. Existing source fidelity and
all explicit-path behavior must remain unchanged.

1. Reuse existing ranking and secure complete-file preparation behind a new
   `prepare_task_prompt` adapter; extend private ranking with file-unique limiting
   without changing default search ordering.
2. Implement deterministic SKIP/FOCUSED_SOURCE/FULL_SOURCE decisions, budgeted
   helper expansion, current-source/version/policy checks and private phase
   observability. Do not add an auxiliary selector model or auto-inject memory.
3. Add `--discover` as an explicit launcher route with strict receipts. Keep
   complete source as the normal format. Add conservative Python excerpts as a
   separately labeled experiment, never as an automatic replacement.
4. Test generic/ambiguous tasks, path-free discovery, stale/added/deleted sources,
   policy/race/security/resource failures and exact fallback behavior. Run existing
   application and transport checks. Validate real upstream mutation graders
   before considering any model study.
5. Freeze an independent A/B/C plan on fresh pinned upstream repositories, with
   public path-free tasks, private B scopes, balanced two-repeat execution,
   protected tests, usage/accounting and paired uncertainty. Run offline first;
   do not dispatch native models without new approval and an estimated budget.
6. Report both successes and declines, local overhead and scope-coverage proxies,
   and leave unmeasured native correctness/tokens/prices/billing unavailable.

Research supports selective sparse retrieval, meaningful source budgets and
abstention, not a globally superior architecture. Full secure refresh has real
cost; metadata-query limits are not an end-to-end latency guarantee. Historical
native reports and raw outcomes remain preserved.
