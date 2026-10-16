# Memglide V1

Architecture: shared Python service layer over transactional SQLite WAL storage; local parser/indexer; deterministic search/context engine; expiring session memory; FastAPI, Typer, official MCP v2 STDIO transports; React dashboard served by FastAPI. Repository roots are explicitly registered. Source hashes are checked at retrieval. FTS5 stores searchable source once; file metadata does not duplicate full source.

Milestones, in dependency order:
1. Foundation, storage, security and pinned tooling.
2. Incremental repository indexing and parsing.
3. Search and conservative dependency resolution.
4. Persistent index and expiring task memory.
5. Deterministic selection and token budgets.
6. Context Passports and progressive expansion.
7. Filesystem monitoring and invalidation.
8. Official MCP v2 and Codex integration.
9. Typed HTTP API and shared-service CLI.
10. Connected React dashboard.
11. Integration/security/browser checks and fixes.
12. Wheel, reproducible installation, operational documentation.

Implementation is parallel within cohesive modules; integration and validation follow the dependency sequence. See PROGRESS.md for observed outcomes rather than inferred completion.
