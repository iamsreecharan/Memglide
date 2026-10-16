# Engineering decisions

- SQLite WAL with foreign keys, short per-operation connections and busy timeout supports multiple local transports; no daemon or cloud database required.
- FTS5 contains searchable source text once; current snippets are read from validated paths and verified against indexed SHA-256. Source files remain authoritative.
- Python AST and Tree-sitter JS/TS/TSX parse without execution. Relationships are conservatively resolved; ambiguous calls remain unresolved.
- Deterministic budgets estimate tokens conservatively by UTF-8 bytes; output includes metadata and warnings. Estimates are not billing measurements.
- An explicit project registration approves a canonical local Git root; all later operations require registered project/session identifiers.
- MCP 2.3.0 stable is available; installed APIs must be inspected before transport implementation.

- Real-source self-indexing exposed a native Tree-sitter 0.26.0 regression: 11 of 15 isolated trials on five production TSX files crashed. The same parser/grammars with the official 0.25.2 release passed 15/15. Pin 0.25.2 rather than suppressing TSX analysis. Indexing isolates changed JavaScript-family files in bounded parser batches so native failures can become explicit text-only indexing errors without terminating the API/MCP process.
- Browser source/memory responses are not persisted in web storage. API responses and dashboard fetches use no-store. Active passports are revalidated without refreshing session inactivity.

- Benchmark usage comes only from supported Codex JSONL events; final structured
  model summaries are not telemetry or grading. Missing billing/API-call/read
  instrumentation remains null. Read-command intent and declared-target
  retrieval coverage are separate proxies, with explicit limitations.
- The cold-start experiment uses fresh B indexes without prior memories or
  diagnostic retrievals. It counts initialization and retains failed runs;
  counterbalanced order limits provider-cache confounding without claiming caches
  can be reset. A separate longitudinal experiment would be needed to assess
  reuse of prior task memories.
- Preserve the V1 baseline and the measured eight natural-query retrieval misses.
  Diagnose and propose ranking/metadata improvements before claiming benefit;
  any later implementation must be evaluated as a separate version with the
  original results retained.
- Source distributions include benchmark tooling because their included tests
  import it. Codex authentication state, databases, caches and live-run worktrees
  stay outside the distribution and Git under ignored `.local` paths.
- Keep the online retrieval research and every measured policy. IDF lexical won
  among the new candidates; legacy remained better on development top-one ranking.
  RRF, MMR and a later score calibration did not justify replacing the simpler
  candidate. Reused Orion validation is disclosed. The combined patch improves
  declared-source coverage, without an individual-mechanism causal claim.
- Fit current direct source before optional graph detail, count all serialized
  graph copies, and expose bounded previews with omission/recovery information.
  This preserves budgets without hiding incomplete relationship evidence.
- Memory IDs identify records, not claim revisions. Compaction requires the exact
  returned content version, and passports snapshot versions independently of clocks
  and source hashes. One reader cannot acknowledge another reader's newer claim.
- Exact FTS vocabulary counts and project-row membership remove repeated payload
  extraction while retaining MATCH union/Unicode behavior. Keep the slower scale
  observations and verify ranked candidates, scores and hashes remain identical.
- New Codex registrations use isolated Python imports so repository packages and
  PYTHONPATH cannot replace the installed MCP server. Existing entries remain
  preserved; supported Codex commands are required to replace them deliberately.
- Preserve the authentication-blocked A/B slots as unrun, with unavailable costs,
  success rates and token totals. An SDK retrieval improvement cannot establish
  savings or task-completion benefits versus Codex.
