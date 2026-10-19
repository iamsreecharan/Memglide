# Research supporting the v4 coding comparison

Fresh primary-source research supports bounded lexical discovery followed by current-source syntax checks. It does **not** establish a coding, latency, or cost improvement. Those outcomes require the matched native Codex runs and independent grading recorded separately. No model request was made for this research.

The machine-readable [research record](router-v4-research.json) contains retrieval dates, byte hashes, failed requests, selected reading scopes, historical-price provenance, and methodological limits. Full downloaded bytes and fetch scripts are retained under the ignored `.local/router-v4/research/` directory. Downloading a file does not mean its complete contents were reviewed. No complete research paper was read or used to claim an expected percentage improvement.

## Discovery and incomplete information

The current official [SQLite FTS5 API comments](https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5.h) describe phrase matches and row/column/token statistics. The [BM25 implementation](https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5_aux.c) uses phrase frequency, document length, corpus frequency, an IDF floor, and a negative return sign. These are lexical ranking mechanisms; they do not prove semantic ownership, correct edits, complete dependencies, or calibrated confidence. BM25 statistics are calculated over the FTS table, even when an outer query restricts returned rows.

The [Tree-sitter parsing documentation](https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/docs/src/using-parsers/2-basic-parsing.md) supplies source ranges, node kinds, named children, and field names. Its [query documentation](https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/docs/src/using-parsers/queries/1-syntax.md) explains `ERROR` and zero-width `MISSING` nodes. A recovered tree can still contain errors. The [public API comments](https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/lib/include/tree_sitter/api.h) document `ts_node_has_error`, `ts_node_is_missing`, and cancellation. Current upstream APIs may differ from the installed binding and grammar versions; this research does not establish their interchangeability.

The following are engineering conclusions from these mechanisms and the inspected repository, not claims made by the documentation:

1. Apply production eligibility and project scope before each lexical candidate cap. Filtering a mixed pool after `LIMIT` allows documentation, fixtures, or tests to crowd out production candidates. Broad source text remains useful for discovering malformed files that lack extracted symbols; comments and literals may propose a candidate but cannot establish runtime relevance.
2. Separate scan/index integrity from per-file structural parse status. An unrelated parse error or unsupported source language need not invalidate a complete lexical scan. A scan stopped by a resource limit, unreadable source that could hide a competitor, or uncertain inventory must remain explicitly incomplete.
3. Parse only the bounded plausible task candidates, with current source hashes and existing path/approval/ignore/secret guards. Revalidate losing competitors as well as selected files before delivery. Files outside the task's lexical candidate set must not become global structural prerequisites.
4. Preserve unparseable or unsupported plausible candidates as unknown competitors. Silently removing one can create false confidence in the remaining winner. Abstain when an unknown candidate could change the decision; excluding it requires a demonstrably sound bound compatible with the actual decision rule. A rank threshold alone supplies no such proof.
5. Observe candidate overflow using an additional row or equivalent complete enumeration, and distinguish a full bounded set from an exhausted or truncated search. A top-k return proves neither absence of additional competitors nor global semantic recall. A discovery policy covering only selected query terms must disclose that scope.
6. Report dependency coverage at the actual scope of the extracted graph. Resolved direct edges can justify named helpers; missing/unresolved edges, dynamic dispatch, imports, unsupported files, or parser errors prevent a claim of complete dependency closure. If complete required context cannot be established within the delivery contract and budget, use the original-task fallback.

SQL `LIMIT` bounds returned rows, not all work needed to find and sort them. The official [SQLite progress-handler contract](https://raw.githubusercontent.com/sqlite/sqlite/master/src/sqlite.h.in) describes callbacks at an approximate number of virtual-machine instructions and interruption on nonzero return. Combine query/VM limits with wall deadlines and bounded rows/bytes. Parsing requires its own input, node, time, and process bounds. These mechanisms do not, by themselves, establish a hard end-to-end deadline, an RSS ceiling, or cancellation of database lock waits and filesystem operations.

## Installed Codex usage and routing

The installed CLI reports **`codex-cli 0.159.2`**. A fresh read-only tag lookup resolves `rust-v0.159.2` to official commit [`ff6aec96948b70d94983af2641a6b67c94faeff5`](https://github.com/openai/codex/tree/ff6aec96948b70d94983af2641a6b67c94faeff5). Selected matching source establishes:

- [`exec_events.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/exec/src/exec_events.rs#L59) exposes input `I`, cached input `C`, cache-write input `W`, output `O`, and reasoning output `R` in JSONL usage.
- [`responses.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/codex-api/src/sse/responses.rs#L128) maps the upstream usage fields and defaults an omitted cache-write field to zero. Its parsing test uses `I=100`, `C=40`, `W=60`, `O=10`, `R=5`, total `110`: cached/write tokens are within input and reasoning is within output. A zero write count does not prove an explicit upstream zero.
- [`event_processor_with_jsonl_output.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/exec/src/event_processor_with_jsonl_output.rs#L118) copies the last thread usage **total**. Fresh sessions per attempt prevent earlier thread use from contaminating a task's total. Summing repeated cumulative updates or resumed-thread totals double-counts usage. If no usage update was received, the function returns default zero usage; zeros alone do not establish complete accounting. Failed turns emit an error without the completed-turn usage payload.
- [`protocol.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/protocol.rs#L2262) defines a best-effort per-completed-response usage record, but this does not mean the exec JSONL stream emits it. Tool-command count is not model-request count. Missing per-request counts remain unavailable.
- [`config_types.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/config_types.rs#L533), [`config/mod.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/config/mod.rs#L3957), and [`openai_models.rs`](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/openai_models.rs#L1000) support `-c 'service_tier="default"'` as the explicit Standard-routing sentinel. The sentinel prevents catalog defaults and is omitted from the outbound tier field. It does not prove the server's final tariff or an actual dollar charge.

The freshly fetched official [Python SDK usage schema](https://raw.githubusercontent.com/openai/openai-python/main/src/openai/types/responses/response_usage.py) independently documents cached and cache-write input detail and reasoning output detail. No backend request, authentication test, credential read, or login change was used to verify these source contracts.

The installed version's [provider source](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/model-provider-info/src/lib.rs#L77) defines the default Codex backend as `https://chatgpt.com/backend-api/codex`. Lines 420–438 select this default for ChatGPT/token/header/agent-identity/personal-access-token authentication; API-key mode falls back to `https://api.openai.com/v1`, and a configured provider base URL can override it. This is source evidence for the network destination, not proof of the session's authentication or backend readiness.

The pinned [authentication manager](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/login/src/auth/manager.rs#L212) defines the default ChatGPT OAuth refresh endpoint as `https://auth.openai.com/oauth/token`; lines 1625–1648 use it for refresh. Managed ChatGPT auth can refresh proactively when token expiry is within five minutes, or when its fallback refresh age exceeds eight days (lines 3004–3025). External/header/agent authentication modes differ, and a configured endpoint override is possible. No credential contents or expiry were inspected: source support for `auth.openai.com` does not establish that this session needs a refresh or that its authentication works.

## Pricing status and conditional estimates

**Fresh pricing verification is blocked.** Requests to the official API pricing page, exact model page, and caching guide failed through the inherited proxy with `Tunnel connection failed: 403 Forbidden`. The network policy was not changed. Public official GitHub source/schema fallbacks retrieved usage contracts, but did not establish a current applicable tariff. Guessed documentation/catalog paths that returned 404 and an oversized OpenAPI response are retained as failed attempts.

The existing [pricing file](cost-pricing.json) has official-page receipts from **2026-10-18**. The three archived source bodies remain present and their SHA-256 values were rechecked against those receipts in this research. Selected archived pricing/model/caching sections were reread. These are **historical, currently unrefreshed API list prices**, not newly verified rates and not a subscription invoice:

| USD per million tokens | Historical Standard, input at most 272,000 per request | Historical Standard, input over 272,000 per request |
| --- | ---: | ---: |
| Ordinary input | 2.00 | 4.00 |
| Cached input reads | 0.10 | 0.20 |
| Cache writes | 2.50 | 5.00 |
| Output, including reasoning | 10.00 | 15.00 |

Under that historical short-context scenario:

```text
ordinary input = I - C - W
estimated API-equivalent USD = ((I-C-W)*2 + C*0.10 + W*2.50 + O*10) / 1_000_000
```

Validate nonnegative integral counts and `C+W<=I`; do not add `R` to `O`. Native-reported `W` supplies the point scenario. A separate hypothetical maximum-write scenario sets `W=I-C`; it bounds only the cache-write premium under the same historical tariff, with complete input/output accounting. It does not bound actual account charges or missing requests. If writes are uncertain in both arms, report the cost-per-success savings interval using `1-B_upper/A_lower` through `1-B_lower/A_upper` where denominators are positive.

The archived model page applies the >272,000 condition to **each model request**, repricing its full input/output. A fresh-thread aggregate below the threshold establishes that each included completed request is below it; an aggregate above it cannot identify which calls qualify. Without per-request usage, show a conditional all-short/all-long scenario or mark the applicable context regime unknown. Do not reprice a multi-request aggregate as one request.

The historical pages also describe Fast at 2x Standard, Ultrafast at 6x, Batch/Flex at 0.5x, and conditional 10% endpoint uplifts. These are historical sensitivity assumptions. They do not establish which rate this CLI account pays. Keep attributable actual billed dollars `null` without billing evidence.

## What the native experiment must measure

Use the same task, starting source, model, reasoning setting, routing request, budgets, and grading criteria in both arms. The Memglide arm performs its real automatic preparation before the same coding request; record preload/abstention and all setup overhead. Keep development attempts and historical cohorts separate from frozen evaluation tasks. Grade actual behavior with independent checks; process completion and valid syntax are insufficient correctness criteria.

Report independently successful tasks and the paired correctness outcomes, end-to-end wall time including preparation/failures/timeouts, native token categories and availability, and conditional API-equivalent cost. Count all attempts and failures in each arm's cost numerator:

```text
cost per successful task = all attempt costs / independently successful tasks
savings % = 100 * (1 - Memglide cost per success / bare Codex cost per success)
```

With zero successes, cost per success is undefined. Missing failed-attempt usage makes complete cost unavailable; it is not zero spending. A common tariff multiplier can cancel in a ratio only when it actually applies identically to both arms. Cache behavior, context pricing, missing usage, or different billing classifications can prevent that simplification. Local compute/hosting and external service fees remain outside a token-only estimate unless measured and priced separately. Small matched samples support conclusions only about their recorded tasks and conditions.
