# Engineering decisions

- SQLite WAL with foreign keys, short per-operation connections and busy timeout supports multiple local transports; no daemon or cloud database required.
- FTS5 contains searchable source text once; current snippets are read from validated paths and verified against indexed SHA-256. Source files remain authoritative.
- Python AST and Tree-sitter JS/TS/TSX parse without execution. Relationships are conservatively resolved; ambiguous calls remain unresolved.
- Deterministic budgets estimate tokens conservatively by UTF-8 bytes; output includes metadata and warnings. Estimates are not billing measurements.
- An explicit project registration approves a canonical local Git root; all later operations require registered project/session identifiers.
- MCP 2.3.0 stable is available; installed APIs must be inspected before transport implementation.

- Real-source self-indexing exposed a native Tree-sitter 0.26.0 regression: 11 of 15 isolated trials on five production TSX files crashed. The same parser/grammars with the official 0.25.2 release passed 15/15. Pin 0.25.2 rather than suppressing TSX analysis. Indexing isolates changed JavaScript-family files in bounded parser batches so native failures can become explicit text-only indexing errors without terminating the API/MCP process.
- Browser source/memory responses are not persisted in web storage. API responses and dashboard fetches use no-store. Active passports are revalidated without refreshing session inactivity.
