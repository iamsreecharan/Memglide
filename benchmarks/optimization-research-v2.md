# Optimization research for the second live A/B comparison

Accessed **October 17, 2026 (America/New_York)**. This is a focused review of primary papers’ author repositories, provider cookbooks, official protocol specifications and client source. It is not an exhaustive literature search or a claim to have read every book. Two requested chapters of Stanford’s *Introduction to Information Retrieval* were blocked by the cloud proxy; no recommendations below are attributed to unread chapters. The [machine-readable research record](optimization-research-v2.json) includes exact URLs, access times, short verified excerpts, hashes, failed fetches and candidate experiments.

The preserved [first authenticated comparison](live-ab-assessment.md) measured **2.751× input tokens and 1.465× Codex-plus-index time** for Memglide across 47 verified pairs, with no observed correctness advantage. Those are historical observations. The sources below motivate improvements but do not establish that any candidate will reverse that outcome.

## Decisions to test first

1. Combine project resolution, session creation and initial retrieval in one operation. Expose a small, stable agent tool profile with focused expansion. This targets sequential interaction overhead; it is a hypothesis until native usage and timing improve.
2. Return unique useful source with short path/range/version and completeness/freshness markers. Remove repeated debug/graph metadata and duplicate spans while preserving necessary definitions and explicit expansion.
3. Prefer exact identifiers/paths and complete direct definitions plus bounded helpers. Do not add a large embedding model or reranker merely because it is fashionable: quality, CPU, memory and latency must all be measured.
4. Independently test edits, renames, deletions and content changes with restored timestamps. Keep real freshness evidence visible to the model and distinguish it from server labels.
5. Freeze the new 40-task corpus, application and protocol before live evaluation. Preserve failed runs and report actual usage, success and missing costs honestly.

## What the sources actually support

| Topic | Verified evidence | Memglide implication and limitation |
| --- | --- | --- |
| C01 [S01](#s01) | OpenAI prompt caching depends on matching prefixes, including identical tool definitions and their ordering. | Use deterministic compact schemas and output ordering. Measure total and cached input separately. Memglide cannot force a Codex provider cache hit. **Limit:** The cookbook discusses the API and earlier model examples; advertised maximum speed/cost reductions are not Memglide measurements or guarantees for ChatGPT-authenticated Codex. |
| C02 [S02](#s02), [S03](#s03), [S21](#s21) | Fewer unnecessary sequential tool interactions and filtering results before model ingestion are established agent-design techniques. | Prototype one server-side bootstrap for project resolution, session creation and initial retrieval; include compact freshness evidence in that result. **Limit:** The Anthropic API feature is not a Codex configuration setting. A wrapper can add complexity and may not reduce underlying model calls or latency; only native usage/timing can establish that. |
| C03 [S04](#s04), [S20](#s20) | Deferred discovery can reduce initial schema exposure; Codex supports an explicit enabled_tools filter. | Offer a stable compact tool profile with bootstrap and focused expansion, while preserving the full compatible profile for integrations. **Limit:** Claude defer_loading and tool_reference are provider-specific and must not be passed to Codex as invented flags. Smaller serialized schema bytes are a proxy, not measured model tokens. |
| C04 [S06](#s06), [S07](#s07), [S08](#s08), [S10](#s10), [S11](#s11) | Repository-level code tasks can require cross-file context, while small retrieval chunks and larger returned parent context serve different purposes. | Use precise identifier/path retrieval, then pack complete direct definitions and bounded direct helpers where possible; expose explicit truncation/omission markers and expansion. **Limit:** The sources do not prove AST chunks or any particular dependency graph algorithm are best. RepoCoder uses line windows and does not guarantee complete functions. Direct-helper completeness is a local hypothesis to test. |
| C05 [S09](#s09) | The Lost-in-the-Middle experiment deliberately varies relevant-passage position among fixed distractors. | Keep the most relevant unique source early; avoid burying it below metadata or large graph expansions. Consider fixed-content ordering ablations. **Limit:** Only author experiment code/instructions were inspected here, not the full paper. No quantitative position effect is imported, and older QA-model findings are not proof about current Codex coding agents. |
| C06 [S05](#s05), [S15](#s15) | Memory, compaction and re-fetchable tool-result clearing address different context problems; memory can become stale and resource subscriptions are optional. | Validate freshness with source identity/hash and mutation tests; keep model-needed markers visible. Test warm memory across related sessions separately from cold retrieval. **Limit:** Memglide cannot edit Codex internal conversation history or activate Claude context-management API features. A server Current label alone is not an independent live-hash check. |
| C07 [S12](#s12), [S22](#s22) | Retrieval quality and final execution-based coding quality require separate evaluation, and high-quality context does not guarantee a gain for every model/task. | Keep reference-file/body coverage, precision and ranking diagnostics separate from hidden behavioral task success, actual usage and elapsed time. **Limit:** No source establishes that Memglide saves tokens, money or time. A larger embedding/reranker stack can cost more CPU, memory and latency than it returns on small tasks. |
| C08 [S13](#s13) | A credible coding grader checks both the requested behavior and preservation of existing passing behavior, including evidence that tests really ran. | Use independent hidden behavioral graders, unchanged smoke checks and compilation; detect protected-file edits and empty/nonexecuted suites. Preserve all failures and interrupted attempts. **Limit:** Passing the selected tests does not prove arbitrary correctness. Local synthetic tasks, repeats and mirrored languages are correlated. |
| C09 [S14](#s14), [S16](#s16), [S17](#s17) | For direct tool output in Codex 0.159.2, text JSON plus non-null structuredContent is not automatically duplicated in the model context: structuredContent is selected and serialized once. | Retain the compatible structured-result contract by default. Do not claim a 50% token saving merely by deleting one SDK envelope representation. **Limit:** MCP events and transport storage can still contain both. Envelope byte size is not model token usage; encrypted content has a different conversion branch. |
| C10 [S18](#s18), [S19](#s19) | Code Mode receives the full result envelope minus _meta, then exposes only emitted runtime content to the model. | Keep freshness/completeness data in visible structured/text fields. Test whether an optional compact result profile or selecting structuredContent avoids repeated payloads. **Limit:** Duplication reaches the model only if the generated JavaScript emits both representations/the whole envelope. Native MCP JSONL alone does not show that choice. Actual CLI usage must validate any token reduction. |

## MCP duplication: a concrete client-source finding

Counting both MCP result representations in JSONL is not enough to infer duplicated model input. In Codex **0.159.2**, [`CallToolResult::as_function_call_output_payload`](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/protocol/src/models.rs#L2302) selects non-null `structuredContent` and serializes it once. Its unit test `preserves_structured_mcp_content` uses text `ignored` and expects only the structured value. The [direct MCP adapter](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core/src/tools/context.rs#L184) adds a timing header and applies its output budget. Deleting the text fallback therefore does **not** automatically halve direct-mode model input.

Code Mode has a different boundary: [`ToolOutput for CallToolResult`](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/tools/src/tool_output.rs#L191) returns the full envelope to generated JavaScript and removes `_meta`. The [runtime adapter](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core/src/tools/code_mode/mod.rs#L261) converts emitted content into model-facing output. Printing the whole envelope could repeat content; selecting `structuredContent` avoids that particular duplication. The MCP event stream alone does not show what the generated JavaScript emitted. An explicit profile/projection needs a native usage pilot, not a claimed percentage from envelope bytes. Keep freshness/completeness fields in visible structured/text content because Code Mode strips `_meta`.

The [MCP specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/tools.mdx#structured-content) recommends returning serialized text alongside structured content for backwards compatibility. Preserve the existing contract unless an explicit supported profile and real client tests justify a change.

## Candidate experiments and rejection criteria

| Candidate | Test and retain only if | Tradeoff |
| --- | --- | --- |
| E01 (priority 1): Bootstrap plus compact tool profile | Resolve project, start/reuse session and retrieve in one server-side operation; retain focused expansion. Verify native B invocation and delivered source, not only process startup. Compare MCP call counts and actual CLI input/cached/output tokens plus elapsed time. Keep same model, effort, prompts and independent graders; declare the integration change. | A combined tool can hide errors or create state unexpectedly; preserve isolation, clear failures and compatibility. |
| E02 (priority 1): Compact unique source payload | Remove repeated graph/debug metadata, duplicate spans and unchanged context while preserving paths, ranges, version/freshness, omissions and complete useful definitions. Compare full-body and direct-helper coverage, precision, explicit truncation and actual structured results. Measure serialized bytes only as bytes; use native usage for model token conclusions. Do not silently omit stale/partial warnings. | Aggressive compression can remove necessary code or make errors harder to diagnose; provide explicit expansion. |
| E03 (priority 1): Freshness and mutation validation | Carry source/index identity in compact results and reject/rebuild stale evidence on edits, renames and deletions. Compare returned source/hash against files in a controlled harness at request time. Test same-size edits and restored mtimes, deletion, rename and project isolation. Keep server assertions separate from independently observed freshness. | Hashing too much on every query raises local overhead; immutable snapshots, scoped checks and cached identities need adversarial tests. |
| E04 (priority 2): Bounded direct-helper packing | Prioritize exact symbol/path and relevant definitions, then a small dependency neighborhood; cap unrelated graph nodes. Use development retrieval fixtures for candidate ablations before freezing the new 40-task evaluation. Report misses, complete-body/helper coverage, byte size and retrieval latency. Do not tune to the final task grader after seeing its results. | Large helper closure wastes context; too narrow a closure misses aliases/callers or behavior across files. |
| E05 (priority 2): Deterministic cache-friendly schemas/results | Stable tool names, schemas and field ordering; append changing task/source state after reusable metadata where the client permits. Record cached input as a subset of total input and derive uncached input explicitly. Counterbalance arm ordering and disclose unresettable provider/OS caches. Do not pad requests to manufacture cache hits. | Dynamic tool discovery can perturb prefix caching; no client-side guarantee of provider cache identity exists. |
| E06 (priority 2): Cold and warm state as separate protocols | Keep fresh-index A/B distinct from future related-task memory reuse. Freeze histories/memory content and split sessions without answer leakage. Include indexing/setup time when incurred. Report state/cache setup and unknown costs, including every failed attempt. | Warm memory may help related tasks but can introduce stale facts and leakage; a cold one-shot benchmark does not measure persistent memory value. |
| E07 (priority 3): Optional Code Mode result projection | Select structuredContent in generated code, or evaluate an explicit transport profile, after inspecting compatibility. Retain default MCP compatibility and structured semantics unless supported client testing justifies change. Pilot on development tasks; compare actual native CLI usage and tool result parsing. Keep the whole-envelope and selected-result hypotheses distinct. | Text-only results can impair typed consumers and yield no direct-mode token saving; native generated code is not fully observable through MCP events. |
| E08 (priority 1): Frozen 40-task live comparison with honest accounting | Use new tasks, isolated identical starting commits, stable prompts/model/settings, native structured usage, balanced order and independent behavioral grading. Freeze source, tasks and protocol before formal execution; do not discard pilot failures or rerun losers into the primary cohort. Report every assigned/attempted run, failures, missing telemetry, paired cohorts, means/medians and sample counts. Report actual cost per success only if complete reliable cost exists; otherwise null, never an estimate labeled actual. | Forty synthetic tasks cannot prove universal superiority; repeats and mirrored task families are not independent samples. |

Use retrieval-development fixtures for deterministic ablations before freezing the fresh task evaluation. The formal A/B comparison tests the selected combined implementation; it cannot identify the isolated causal effect of every mechanism. Keep separate component experiments or matched protocol variants if attribution matters. Do not tune the frozen task prompts/grader after observing formal outcomes.

Warm index reuse and cross-session memory are useful future protocols, but they require matched histories and stale-memory tests. They must be labeled separately from fresh-index single-task evaluation. Adding memories to B with answers from the evaluation corpus would invalidate the comparison.

## Measurement boundaries

- Track native CLI total input, cached input and output independently; cached input is already part of total input. Stable prefixes improve cache eligibility, not guaranteed cache hits or guaranteed savings. Do not pad prompts to inflate cache ratios.
- Serialized bytes and tool-schema size remain size proxies. Completed CLI turns are not full underlying model-call counts; tool events are not exact repeated filesystem reads. Keep unavailable metrics null.
- Use hidden behavioral checks, unchanged smoke tests, compilation and protected-file checks. Confirm tests executed. Report all-attempt success as well as verified matched cohorts, preserving invalid treatments, model mistakes and infrastructure interruptions.
- Include indexing/setup time when incurred, local process CPU/RSS definitions, order/cache controls, individual attempts and denominators. Provider/OS caches may remain uncontrolled even with isolated worktrees.
- Cost per successful task needs reliable costs for **all attempted runs**, including failed ones. Without complete billing or verified applicable pricing, actual cost and actual cost per success remain null. Provider cookbook percentage examples are not measurements for this application.

## Source snapshots

All downloads used standard HTTPS verification and the inherited proxy/CA configuration. No credentials or repository source were uploaded. 43 of 61 source/discovery requests succeeded. 39 raw snapshots were re-fetched by resolved immutable Git commit and matched the original SHA-256; no mismatch was observed. Discovery HTML is not treated as paper evidence. The ignored archive holds originals and short excerpts; public reports include citations and provenance, not copies of books or notebooks.

<a id="s01"></a>
**S01 — OpenAI Prompt Caching 101.** [Verified immutable source](https://raw.githubusercontent.com/openai/openai-cookbook/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/Prompt_Caching101.ipynb). Stable prefixes and identical tool ordering enable cache reuse.

`SHA-256 2f1e5fea7989d37dacf702c2ef4059e12f42b21dbf937d6a4e0eecb19b88ab12` · fetched `2026-10-17T22:37:51.100532+00:00` · commit `5bd6cb40b6b84b69b2032d810610aa85064102df`

<a id="s02"></a>
**S02 — OpenAI GPT-5 prompting guide.** [Verified immutable source](https://raw.githubusercontent.com/openai/openai-cookbook/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/gpt-5/gpt-5_prompting_guide.ipynb). Targeted searches, path deduplication and avoiding repeated queries are recommended; model and effort changes affect behavior.

`SHA-256 020cc2723d0ef16a1cb1451eae655e340e277bedc3c591f416ae24d8b2ae88ec` · fetched `2026-10-17T22:37:51.102090+00:00` · commit `5bd6cb40b6b84b69b2032d810610aa85064102df`

<a id="s03"></a>
**S03 — Anthropic Programmatic Tool Calling cookbook.** [Verified immutable source](https://raw.githubusercontent.com/anthropics/claude-cookbooks/a162e0184e71b60290808a43961a6cbc8060123c/tool_use/programmatic_tool_calling_ptc.ipynb). Programmatic orchestration can filter large results before they enter model context; the example is Claude-specific.

`SHA-256 d0ce8ee18a52465d7f27e649ea7b333fdc7000d6aaa18cc7d52c3d3b907f333d` · fetched `2026-10-17T22:38:55.529865+00:00` · commit `a162e0184e71b60290808a43961a6cbc8060123c`

<a id="s04"></a>
**S04 — Anthropic Tool Search: Alternate Approaches.** [Verified immutable source](https://raw.githubusercontent.com/anthropics/claude-cookbooks/a162e0184e71b60290808a43961a6cbc8060123c/tool_use/tool_search_alternate_approaches.ipynb). Deferred tool loading keeps unused tool definitions out of the initial context and requires client orchestration.

`SHA-256 8aaf534b6204d4c30a13ebf7b7c7ceb408734dc7bacecb8ab520a3671997b153` · fetched `2026-10-17T22:38:55.526972+00:00` · commit `a162e0184e71b60290808a43961a6cbc8060123c`

<a id="s05"></a>
**S05 — Anthropic context engineering tools cookbook.** [Verified immutable source](https://raw.githubusercontent.com/anthropics/claude-cookbooks/a162e0184e71b60290808a43961a6cbc8060123c/tool_use/context_engineering/context_engineering_tools.ipynb). Compaction, tool-result clearing and persistent memory solve different problems and introduce distinct tradeoffs.

`SHA-256 a78f2b21b70cc53e6e8b8e03eaeee02af6bcfc1c5fecd6cbead0b720e2f21c07` · fetched `2026-10-17T22:39:25.335183+00:00` · commit `a162e0184e71b60290808a43961a6cbc8060123c`

<a id="s06"></a>
**S06 — RepoCoder author repository.** [Verified immutable source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/README.md). The framework iterates retrieval and generation for repository-level code completion; its task and models differ from this coding-agent experiment.

`SHA-256 d19d72d5407c3d7081a9f5393dca53503f3b8dc5a36be4ee0ec9d8ee4f34cd1b` · fetched `2026-10-17T22:37:51.612058+00:00` · commit `35f54d60b152cc31d134b788e702878ad613d9f7`

<a id="s07"></a>
**S07 — RepoCoder window construction source.** [Verified immutable source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/make_window.py). Its repository windows are line based and identical context windows are merged; it does not guarantee complete function bodies.

`SHA-256 45b01cfe027a887c0f3da521076a384b1577a1189ff7940842d706bb90c47603` · fetched `2026-10-17T22:38:55.931543+00:00` · commit `35f54d60b152cc31d134b788e702878ad613d9f7`

<a id="s08"></a>
**S08 — LangChain ParentDocumentRetriever, tag 0.3.27.** [Verified immutable source](https://raw.githubusercontent.com/langchain-ai/langchain/bdf1cd383ce36dc18381a3bf3fb0a579337a32b5/libs/langchain/langchain/retrievers/parent_document_retriever.py). It retrieves small chunks and returns larger parent documents to balance retrieval specificity with contextual information.

`SHA-256 18dba80c01e8debc185867b58a9fdd9294170a13f4c017519ccd2b3c929349d2` · fetched `2026-10-17T22:38:56.267679+00:00` · commit `bdf1cd383ce36dc18381a3bf3fb0a579337a32b5`

<a id="s09"></a>
**S09 — Lost in the Middle author experiment generator.** [Verified immutable source](https://raw.githubusercontent.com/nelson-liu/lost-in-the-middle/29b8a6d042ce29abccee3db1a73171a107d7e6af/scripts/make_qa_data_from_retrieval_results.py). The author code explicitly inserts one relevant passage at a controlled position among distractors.

`SHA-256 ffc860687256f8b91f8e5b57aeda16ccde147d0967200b62196507ea133e457b` · fetched `2026-10-17T22:38:55.533822+00:00` · commit `29b8a6d042ce29abccee3db1a73171a107d7e6af`

<a id="s10"></a>
**S10 — RepoBench v1.1 author repository.** [Verified immutable source](https://raw.githubusercontent.com/Leolty/repobench/e0cfd34c9e7cd8f057efd32b9280b9719ae12a91/README.md). It separates cross-file first use, cross-file later use and in-file completion; evaluates exact match, edit similarity and CodeBLEU.

`SHA-256 dcc4550500fbb3ed47d7f73e49694cbb0a55840542d46729056eb38e535be957` · fetched `2026-10-17T22:37:51.619672+00:00` · commit `e0cfd34c9e7cd8f057efd32b9280b9719ae12a91`

<a id="s11"></a>
**S11 — CrossCodeEval author repository.** [Verified immutable source](https://raw.githubusercontent.com/amazon-science/cceval/40c68d2b7ca2a8eae95d901ac80e6a540a84a53d/README.md). Its baseline, retrieval and reference-retrieval settings compare multiple retrievers and explicit cross-file context.

`SHA-256 7fc59eb63a1d26e48de67137cae3f6cf9b1cc64c1932f5884977ac1aa1069e5d` · fetched `2026-10-17T22:37:51.622316+00:00` · commit `40c68d2b7ca2a8eae95d901ac80e6a540a84a53d`

<a id="s12"></a>
**S12 — CodeRAG-Bench author project abstract.** [Verified immutable source](https://raw.githubusercontent.com/code-rag-bench/code-rag-bench.github.io/0857dacd1c06c38a960f8ebeffdec8e4b0f4cf2e/index.html). The abstract says useful context can benefit generation but current retrieval and limited context/RAG abilities constrain gains.

`SHA-256 b65185abbbf1b8fab343f69e2ed0682809a143878d5c8fb0fd4cb3758cd65907` · fetched `2026-10-17T22:38:55.929155+00:00` · commit `0857dacd1c06c38a960f8ebeffdec8e4b0f4cf2e`

<a id="s13"></a>
**S13 — SWE-bench external grading implementation.** [Verified immutable source](https://raw.githubusercontent.com/SWE-bench/SWE-bench/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py). A full resolution requires all fail-to-pass and pass-to-pass tests to pass; harness code checks evidence of actual test execution.

`SHA-256 a095273010175001a6779e365b3b77abb8657c7ac2e4f80b4bc360faa6f09483` · fetched `2026-10-17T22:38:35.367393+00:00` · commit `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`

<a id="s14"></a>
**S14 — MCP 2025-11-25 tools specification.** [Verified immutable source](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/86f6e0c675afea9a8f233e09b6faf566b126086c/docs/specification/2025-11-25/server/tools.mdx). Tools are model controlled; structured results SHOULD also carry serialized JSON as text for backwards compatibility; tool annotations are untrusted hints.

`SHA-256 39e56ad4f3d1ff1cb28ee62283e02947cd97db8aa6190782d629f4562a0f354c` · fetched `2026-10-17T22:38:35.068818+00:00` · commit `86f6e0c675afea9a8f233e09b6faf566b126086c`

<a id="s15"></a>
**S15 — MCP 2025-11-25 resources specification.** [Verified immutable source](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/86f6e0c675afea9a8f233e09b6faf566b126086c/docs/specification/2025-11-25/server/resources.mdx). Resource change subscriptions are optional; a notification is not independent proof of source freshness or necessary-context completeness.

`SHA-256 9c1aa45ee31c1e0f097c5d1f6316e796f0ee2d393fbc960be400e0f77cf82843` · fetched `2026-10-17T22:38:35.077775+00:00` · commit `86f6e0c675afea9a8f233e09b6faf566b126086c`

<a id="s16"></a>
**S16 — Codex 0.159.2 protocol model output conversion.** [Verified immutable source](https://raw.githubusercontent.com/openai/codex/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/models.rs). Direct model output prefers non-null structuredContent over content rather than concatenating both.

`SHA-256 916a595e136f4d7e32ce259f50678ffe818af2ea6a92f54d8628f57bfd4d43e7` · fetched `2026-10-17T22:39:24.934536+00:00` · commit `ff6aec96948b70d94983af2641a6b67c94faeff5`

<a id="s17"></a>
**S17 — Codex 0.159.2 MCP ToolOutput adapter.** [Verified immutable source](https://raw.githubusercontent.com/openai/codex/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/tools/context.rs). Direct output uses that conversion, adds timing information and applies a model-context truncation budget.

`SHA-256 9a9acc6daab2112bd9ca1a07a1e1f2105b20a7f565878157c726ee0d7a3e00cc` · fetched `2026-10-17T22:39:24.932579+00:00` · commit `ff6aec96948b70d94983af2641a6b67c94faeff5`

<a id="s18"></a>
**S18 — Codex 0.159.2 Code Mode raw output conversion.** [Verified immutable source](https://raw.githubusercontent.com/openai/codex/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/tools/src/tool_output.rs). Code Mode receives the full serialized MCP result with only _meta removed; this alone does not show what model-facing JavaScript emits.

`SHA-256 1541422b97b31345461a70721ac7944e22c7fd5cfd427127d8d295e3161e18f5` · fetched `2026-10-17T22:40:04.098804+00:00` · commit `ff6aec96948b70d94983af2641a6b67c94faeff5`

<a id="s19"></a>
**S19 — Codex 0.159.2 Code Mode runtime response.** [Verified immutable source](https://raw.githubusercontent.com/openai/codex/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/tools/code_mode/mod.rs). Only runtime-emitted content items are converted into the Code Mode model-facing tool result.

`SHA-256 e7aae18f4043e9d5964779c0a20f129b9f43dc21873328aa2bcb893035b4cf75` · fetched `2026-10-17T22:39:56.283491+00:00` · commit `ff6aec96948b70d94983af2641a6b67c94faeff5`

<a id="s20"></a>
**S20 — Codex 0.159.2 official configuration schema.** [Verified immutable source](https://raw.githubusercontent.com/openai/codex/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/config.schema.json). The supported schema includes enabled_tools filters, required MCP servers, startup readiness and scoped tool approval settings.

`SHA-256 eda7251b7e46e0b9d0f3d8eef5dab451e11a55d723e2b802e152b7208045836a` · fetched `2026-10-17T22:37:51.105350+00:00` · commit `ff6aec96948b70d94983af2641a6b67c94faeff5`

<a id="s21"></a>
**S21 — Anthropic parallel-tools cookbook.** [Verified immutable source](https://raw.githubusercontent.com/anthropics/anthropic-cookbook/a162e0184e71b60290808a43961a6cbc8060123c/tool_use/parallel_tools.ipynb). The example introduces a batch/meta tool as a workaround for Claude 3.7 Sonnet parallel-calling behavior.

`SHA-256 9be49d93ae4bd5126c242a32bed97f12432a6bb0d242d2ba186453e835b1aef3` · fetched `2026-10-17T22:37:51.603131+00:00` · commit `a162e0184e71b60290808a43961a6cbc8060123c`

<a id="s22"></a>
**S22 — CodeRAG-Bench retrieval and generation implementation guide.** [Verified immutable source](https://raw.githubusercontent.com/code-rag-bench/code-rag-bench/f9e100ca9ed94b8f1983b356ae81966e30210cf4/README.md). Retrieval metrics include NDCG/MRR/recall/precision; execution-based generation evaluation is separate from those metrics.

`SHA-256 ea6653ca198e6b39a31ff5c8d3f945ba44ac10b178d7125d2272d8663c305b9c` · fetched `2026-10-17T22:37:51.957271+00:00` · commit `f9e100ca9ed94b8f1983b356ae81966e30210cf4`

## Unavailable sources and scope limits

The Stanford IR textbook chapter pages, OpenAI platform latency guide and Anthropic engineering pages returned proxy CONNECT 403. Their relevant official GitHub cookbooks/source were used where available; no access controls were bypassed. Several guessed repository file paths returned 404 and were replaced by paths found in upstream directory listings. Every attempt and outcome is retained in JSON.

Full RepoCoder, RepoBench, CrossCodeEval and Lost-in-the-Middle papers were not fetched/read in this pass; the stated claims are limited to the inspected author READMEs, project abstract and implementation/experiment code. No numeric paper result is transferred to Memglide. This research cannot establish a universally “best” retriever; the best candidate for the tested workload must be selected by the ensuing measured comparison.
