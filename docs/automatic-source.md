# Opt-in automatic source preparation

Memglide can connect its existing natural-language index ranking to its complete-file
source preloader. This is an experimental integration, not a new ranking algorithm,
not warm memory, and not a demonstrated reduction in coding-agent cost. Existing
explicit-path preparation, default MCP tools, API behavior and launcher defaults
are preserved.

Approve and index the repository normally, then opt in:

```sh
uv run memglide project add /absolute/path/to/repository
uv run memglide-codex --discover --project PROJECT_ID \
  --max-added-tokens 4000 --max-context-bytes 12000 \
  --preparation-report /private/preparation.json \
  'Correct invoice subtotal rounding for fractional prices.' -- --json
```

The task needs no source paths. `--discover` conflicts with `--focus` and
`--support`. Native Codex settings, environment and existing MCP registrations are
preserved; there is one normal native exec handoff. This documentation does not
authorize a paid benchmark. The launcher itself still runs the agent when invoked.
`--mode off` and `--context-supplied` preserve the original task without index work.

Python clients can prepare without launching an agent:

```python
from memglide.integrations.auto_preload import prepare_task_prompt

result = prepare_task_prompt(
    "Correct invoice subtotal rounding for fractional prices.",
    project_id="approved-project-id",
    db_path="/absolute/path/to/memglide.db",
    enabled=True,
    max_context_bytes=12000,
    max_added_tokens=4000,
)
# result['prompt'] is either the original task or verified complete source + task.
# result['automatic_selection'] is private diagnostic metadata.
```

`enabled=False` is the API default. Clients wrapping a user task in shared workflow
instructions may pass `task_query=the_public_task`. That bounded query must occur
verbatim in the actual prompt. It affects ranking only; the complete original
prompt and its hash remain authoritative. Do not supply private target paths,
reference fixes or hidden grader information as a query.

## Selection policy

The adapter reuses identifier normalization, project document frequencies, FTS5
BM25, symbol/signature/path evidence and conservative static relationships already
implemented by `Indexer`. It groups candidate declarations by file before applying
the file limit, so large files do not win by having many symbols. Ranking scores,
term agreement and score margins are deterministic heuristics, not probabilities.

| Decision | Meaning |
| --- | --- |
| `SKIP` | Return the original task exactly when disabled, context is supplied, evidence is generic/weak/ambiguous, the candidate pool is saturated, state is unavailable, or safe complete delivery exceeds a budget. |
| `FOCUSED_SOURCE` | Deliver a verified complete production anchor file with sufficiently strong task evidence and no eligible resolved direct production helper. |
| `FULL_SOURCE` | Deliver the complete selected anchor plus its bounded resolved direct production-helper bundle. This never means the whole repository or all semantically relevant dependencies. |

The initial gate accepts an explicit code anchor or multiple informative lexical
matches, rejects a close independent alternative, and caps direct helper expansion
at three files. These are preregistered engineering choices, not tuned promises of
accuracy. Exact thresholds and evidence are visible in the implementation and
private receipt. A full 100-file candidate pool causes an explicit abstention;
truncation is not silently presented as complete discovery. Production suffix and
role filters exclude tests, documentation, fixtures and agent/tool instructions
from automatic source injection. The normal agent can still inspect other files.

There is no auxiliary LLM, embedding service, remote vector store, memory lookup,
new session, or agent-visible selection tool chain. Existing memory remains
available separately and is never automatically injected by this adapter.

## Current-source verification and costs

Before opening existing state for refresh, read-only checks validate repository
approval and policy. The indexing facade opens SQLite in `mode=rw`, verifies its
file identity and never creates, migrates or chmods a missing/replaced database.
A full secure refresh then detects added, changed and deleted sources and resolves
the existing index. Partial/error indexes cause abstention. Ranking metadata is
read through bounded query/row/value/VM budgets. Selected source, approval, ignore
policy, ranking settings, index version and all selected source hashes are checked
again at delivery. Symlink escapes, sensitive sources and oversized bodies fail
through the existing source boundaries. No mtime or old receipt proves freshness.

Complete files pass through the existing source-only preparer and canonical
source format. Source bodies are untrusted data, never instructions. Diagnostic
ranking, hashes and graph explanations remain private rather than repeated in the
model-visible source. Overlapping selections are deduplicated; required bodies
are never silently clipped to satisfy a budget.

Optional `provided_sources={relative_path: complete_text}` can suppress a source
only when its path and exact complete body occur in this actual prompt and the
body matches the verified current version. Prior-session hashes alone are not
accepted. This narrow assertion does not observe hidden agent context or survive
unobserved compaction. Supplying the entire context explicitly can use the cheap
`context_supplied=True` bypass instead.

Both added-byte and estimated-token caps apply to the complete source envelope.
The estimate is `ceil(added UTF-8 bytes / 3)`, a planning proxy rather than model
token usage. It is not an estimate of avoided work or guaranteed savings.

The metadata rank reader has a cumulative two-second/VM/row/payload budget. **This
is not a hard end-to-end preparation deadline.** The preceding secure repository
refresh retains existing directory traversal, parser/Git timeouts and database
wait behavior. Large directory trees, cold I/O or contention can make preparation
slow even when the adapter subsequently abstains. Initial index creation and
refresh costs must remain in end-to-end accounting. A postquery `SKIP` is not a
free prequery bypass.

## Evidence and evaluation

The private version-4 launcher receipt includes selection decision and reason,
ranked evidence, selected paths/current versions, phase wall/CPU times, refreshed
index state, byte/token estimates, omitted/saturated candidates and unresolved
static dependency counts. It records zero auxiliary selection model calls by
construction. Provider usage, underlying inference calls, billed charges and
actual file reads are not invented; supported native telemetry is evaluated
separately when actually observed.

[Research](https://github.com/iamsreecharan/Memglide/blob/8acc8af/benchmarks/auto-source-research.md) explains the primary references
and limitations. [Protocol](../benchmarks/automatic-protocol.md) and runner define
A bare Codex, B existing known-path source preload, and C automatic path-free
preload with independent grading. Plan/offline modes make no model requests;
formal execution requires new user approval and an estimated budget.

[Experimental Python excerpts](source-excerpts.md) are a separate disabled-by-default
API. They declare incomplete-file delivery and are excluded from automatic CLI
preloading and the initial formal treatment. Static dependency checks do not prove
that omitted callers or documentation are irrelevant. Complete files remain the
default.
