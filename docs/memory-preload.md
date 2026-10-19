# Bounded memory preparation

`prepare_memory_prompt` is an explicit optional Python integration for passing
caller-selected findings to a new native agent process. Existing source preload,
its defaults, bytes and reports are unchanged. No model, embedding service, MCP
server, background worker or automatic memory discovery is involved.

## What survives a fresh process

The caller keeps **one active Memglide session** for related work and starts fresh
Codex processes as needed. Saved memories survive a service/process restart when
the caller supplies that same session ID and existing database. They do not move
into a new Memglide session. Ending the original session blocks memory access;
expiration cleanup deletes its temporary records. Defaults are 60 minutes of
inactivity and an eight-hour absolute lifetime. This preparation operation does
not refresh either deadline, create a database or start a replacement session.

The compact MCP profile owns a separate private session and closes it when its
server closes. This integration does not change that lifecycle or add persistent
project memory.

## API

```python
from memglide.integrations.memory_preload import prepare_memory_prompt

result = prepare_memory_prompt(
    original_prompt,
    db_path=existing_database,
    project_id=approved_project_id,
    session_id=still_active_session_id,
    memory_ids=[previously_saved_memory_id],
    max_context_bytes=3000,
    max_memories=4,
)
prompt_for_new_codex_process = result["prompt"]
```

The caller must explicitly select up to four IDs belonging to that session. An
empty selection returns the exact input without opening the database. Preparation
does not search or source-check unrelated saved memories. At most 16 source
references are accepted across the selected claims. Argument mistakes raise
`ValueError`; unavailable evidence returns the original prompt.

A selected claim needs at least one source reference, no stale marker, and live
source hashes matching the captured hashes. Each source must still be indexed in
the approved project and allowed by current `.gitignore`, `.memglideignore`,
configured directory exclusions and secure source-reading policy. Missing,
changed, secret, symlinked, unindexed or ignored evidence causes the entire
addition to be discarded. The integration checks ownership and active lifecycle,
then repeats version, source and policy checks before returning. It never resets
old hashes to make a stale claim appear current. As with any snapshot, sources and
session state can change after return.

The result prefixes ordinary prompt text with one JSON data envelope. Every
selected claim retains its original complete content, category, provenance and
source hashes. Its notice explicitly treats claims as untrusted data and states
that current hashes do not prove a claim's meaning. Source freshness is not an
independent factual grader: clients should retain auditable prior observations,
validate quoted evidence, and exclude answers or findings obtained from hidden
graders. Stored text never becomes developer/system instructions.

## Budgets and reports

The default 3,000-byte added-context cap includes all JSON, the notice,
provenance, source hashes and separator. The configurable maximum is 12,000
bytes. The claim bundle is complete or absent; preparation never truncates a
claim to fit. This is a byte budget, not measured model token usage or savings.

Reports contain `mode` (`preloaded` or `passthrough`), `reason`,
`scope="active_memglide_session"`, `prompt_layout`, `context_bytes`, original
and prepared prompt SHA-256, selected IDs/versions/categories/source hashes, and
local wall/CPU preparation durations. Reports exclude claim content except in the
returned prompt. No TTL activity, memory event, stale-marker or index update is
written. Read-only SQLite access has bounded row sizes, row counts, VM steps and
per-query time limits. A missing or malformed database fails closed.

Source and memory preparation can be composed explicitly:

```python
source = prepare_prompt(original_prompt, **source_options)
prepared = source["prompt"]
remaining_bytes = 12_000 - source["context_bytes"]
if remaining_bytes > 0:
    memory = prepare_memory_prompt(
        prepared,
        db_path=existing_database,
        project_id=approved_project_id,
        session_id=still_active_session_id,
        memory_ids=selected_ids,
        max_context_bytes=min(3000, remaining_bytes),
    )
    prepared = memory["prompt"]
```

The caller must enforce the combined source-plus-memory budget and retain both
reports. Memory preparation falling back preserves its exact input, which can
already contain a source bundle.

## Benchmark interpretation

A fair initial comparison uses bare Codex, fresh source context without saved
memory, and the same source context with prior verified observations. Each task
gets a fresh native Codex process/profile; the warm arm alone retains one active
Memglide session within a bounded related-task sequence. All arms use identical
predeclared starting commits and graders. Source changes can legitimately make
earlier findings unavailable. Memory capture, source validation and preparation
costs belong in full-sequence measurements. Cold first tasks and warm follow-up
tasks should be reported separately.

This measures bounded memory across fresh native agent processes. It does not
demonstrate memory across ended, expired or newly created Memglide sessions, nor
does it establish cost or latency gains before native measurements support them.
