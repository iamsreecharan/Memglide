# Workflow and source-search smoke comparison

Register only repositories you approve for source access. Supply the canonical Git repository root; subdirectories are rejected. Check the returned canonical path before relying on its index.

```sh
uv run memglide project add /absolute/path/to/approved/repository
uv run memglide session start PROJECT_ID --task "Investigate authenticate_user"
uv run memglide search PROJECT_ID authenticate_user
uv run memglide context SESSION_ID authenticate_user --level 1 --budget 4000
uv run memglide context SESSION_ID authenticate_user --level 2 --budget 8000
uv run memglide passport SESSION_ID RETRIEVAL_ID
```

Copy `PROJECT_ID`, `SESSION_ID`, and `RETRIEVAL_ID` from the JSON returned by the relevant commands. A passport can be **Partial** even when every included file is current: there may be unresolved imports, omitted source, or undiscovered runtime behavior. Read its warnings before editing. Level 1 contains structural discovery and should be expanded before relying on an implementation.

Search returns short excerpts capped at 1,600 characters per hit. `start_line`/`end_line` describe the complete symbol or file; `snippet_start_line`/`snippet_end_line` identify the excerpt, and `snippet_truncated` signals omitted text. Use its `full_source_reference` with MCP `get_symbol` to request the current full implementation/file explicitly, or retrieve level 2/3 context under a suitable budget. A search excerpt alone is not the whole source.

Use the dashboard Context Explorer or MCP `expand_context` to deepen an existing retrieval. Level 3 supplies broader source where it fits. If the result is truncated, increase the budget or query a specific symbol/path. Metadata consumes the budget as well as snippets; very small budgets can be rejected because even the evidence envelope cannot fit. All token counts are estimates, not tokenizer or billing measurements.

The application JSON budget includes snippets, memories, warnings, and passport metadata. It excludes HTTP/MCP transport framing and any additional context the client supplies to its model. For explicitly acknowledged memories, repeat `--known-memory-id MEMORY_ID` on the CLI, or pass `known_memory_ids` to HTTP/MCP context and expansion requests. Matching selected memories then return IDs, update timestamps, freshness, and source references with `content_omitted: true`. Only declare memories your client already holds; inspect update timestamps and recall again when needed. Omission is explicit client input rather than hidden per-process state.

Session-history queries also work through context retrieval:

```sh
uv run memglide context SESSION_ID "What changed in this session?" --budget 8000
uv run memglide context SESSION_ID "What did we already try to fix this error?" --budget 8000
```

Change queries show recorded project activity observed since the session began, with current source when available; they cannot identify who edited a file or assign a concurrent edit to one session. Attempt queries select explicitly submitted failed attempts, errors, and fixes. They can include stale records as explicitly flagged history, which must not be treated as current source facts. Unrecorded agent activity is unavailable, and disabling event logging limits change evidence. Passport warnings state these limits.

## Explicit task memory

Create or edit memories in the dashboard or use MCP `save_memory`/`update_memory`. Categories are `observation`, `decision`, `error`, `failed_attempt`, `verified_fix`, `open_issue`, and `checkpoint`. Always describe where the finding came from. A source reference accepts a project-relative `path` and optional `hash`; the server captures and verifies the current SHA-256.

For example, with the HTTP service running, replace `SESSION_ID` before invoking:

```sh
curl -X POST http://127.0.0.1:8765/api/sessions/SESSION_ID/memories \
  -H 'Content-Type: application/json' \
  -H 'X-Memglide-Request: 1' \
  --data '{"category":"observation","content":"authenticate_user delegates signature verification to verify_token.","provenance":"Inspected api/auth.py during authentication task","sources":[{"path":"api/auth.py"}]}'
```

On Windows use the dashboard, an HTTP client, or `Invoke-RestMethod` with the same JSON and request header. `curl` quoting above is for POSIX shells. The API is documented at `http://127.0.0.1:8765/docs`; state-changing requests need `X-Memglide-Request: 1`, and browser requests must use the exact same origin as the service.

```sh
uv run memglide memory list SESSION_ID
uv run memglide memory search SESSION_ID "signature verification"
uv run memglide memory clear SESSION_ID
uv run memglide session clear SESSION_ID
uv run memglide cleanup
```

Memory clear removes that session's memories. Session clear immediately removes all its task records. Cleanup removes expired sessions. Ending a session stops further work while its history remains until expiration or manual clearing. None of these commands removes source code or a persistent repository index.

## Freshness after an edit

After modifying an indexed file, inspect the previous passport: changed/missing sources become stale. Source-linked memories are also marked stale when their references are validated. Ordinary context selection excludes stale memories; an explicit prior-attempt query may return them as flagged historical records. Update the index and retrieve again:

```sh
uv run memglide project reindex PROJECT_ID
uv run memglide context SESSION_ID authenticate_user --level 2 --budget 8000
```

The dashboard and MCP service monitor registered roots while running. Manual reindex is useful after offline changes, branch switches, or watcher failures. A full reindex is available with `project reindex PROJECT_ID --full`.

## Reproducible fixture comparison

The fixture includes a FastAPI-shaped application, HMAC authentication helper, React/TSX client, cross-file imports, test sources, and intentionally unavailable imports. Never deploy it as an authentication service. Copy it to an ignored local directory and initialize an independent Git root:

```sh
mkdir -p .local
cp -R examples/auth_repository .local/auth-fixture
git -C .local/auth-fixture init
uv run python examples/smoke_compare.py "$PWD/.local/auth-fixture" authenticate_user
```

PowerShell equivalent:

```powershell
New-Item -ItemType Directory -Force .local | Out-Null
Copy-Item -Recurse examples/auth_repository .local/auth-fixture
git -C .local/auth-fixture init
uv run python examples/smoke_compare.py (Join-Path (Get-Location) ".local/auth-fixture") authenticate_user
```

Install [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) to run this optional comparison. The script prints ordinary fixed-string match locations, Memglide's ranked references, selected paths, estimated response size, and passport warnings. It creates temporary SQLite state under this checkout's `.local` and removes that state on exit. The baseline may include files that Memglide excludes, so the script reports paths and line numbers without printing raw baseline source.

This checks that retrieval returns useful, traceable source evidence alongside ordinary repository search. It does not measure coding-task success, complete agent context, model token use, or cost. The automated `tests/test_workflow.py` exercises registration, indexing, retrieval/expansion, source-aware memory, file modification, stale evidence, reindexing, and expiration cleanup through the shared service.
