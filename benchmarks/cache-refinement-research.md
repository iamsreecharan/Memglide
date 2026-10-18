# Cache-aware source layout: evidence and limits

The compact source-prefix refinement removes avoidable model-visible metadata and moves reusable source before changing task text. **It does not establish a reduction in actual model tokens, uncached input, latency or money.** The completed [80-run ordinary-task report](codex-ab-daily.md) used the legacy layout and remains unchanged.

This review uses the official OpenAI prompt-caching notebook already read in full, newly downloaded pinned native Codex source, and an independent analysis of the preserved 80-run evidence. Research examples were not executed and made no model requests. The [JSON record](cache-refinement-research.json) includes the download access logs, immutable URLs, byte counts, hashes, exact review scopes and the distinction between facts and hypotheses.

## What the completed runs tell us

The independent uncached-input diagnosis found:

- B used **57,138 fewer total input tokens**, but received **149,760 fewer cached input tokens**. Because cached input is included in total input, the uncached difference is `-57,138 - (-149,760) = +92,622` tokens.
- B's uncached input was **75.20% higher in repeat 1** and **11.42% lower in repeat 2**. All 20 tasks had the same B prepared-prompt hash across repeats.
- In the eight caller-context controls, A and B received identical task bytes, yet B still had **3.72% more uncached input**.
- The stored read-command proxy mistakenly associated three `git diff` operands with a preceding `cat` command. It does not support a claim that accidental rereading of preloaded source caused the uncached regression. Actual filesystem reads remain unavailable.
- Across 32 preloaded runs, the addition contained **33,648 UTF-8 bytes**: 16,536 raw source bytes, 8,000 explanation bytes and 9,112 other envelope/metadata/escaping bytes. This identifies removable overhead, not a measured token conversion. Some path/JSON/notice overhead is still necessary.

These observations show variability in measured cache reuse and a real legacy envelope overhead. They do not identify the backend cache key, routing decision, retention interval or per-inference cause. The diagnosis is retained at `.local/daily-v1/review/uncached-diagnostic-v1.md/json`; its source-report hash is verified in the machine-readable review. No failed run is removed and the original result is not recalculated using a more favorable repeat.

## What the native client actually implements

**Installed version: Codex 0.159.2.** The annotated `rust-v0.159.2` tag resolves to commit `ff6aec96948b70d94983af2641a6b67c94faeff5`. We inspected the complete [`prompt_cache_key` and `responses_session_id` functions](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/client.rs#L575-L597), plus the [request-construction block](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/client.rs#L976-L1005).

The cache-key function first honors an existing internal override. For an internal session with parent-thread metadata, it can derive an affinity value from that source and parent. Otherwise it falls back to the session ID. The second function uses the actual session ID for a non-root agent and otherwise uses the cache-key function. The adjacent upstream comment explicitly states that ChatGPT derives cache affinity from the Responses session-ID header. Request construction places the computed key in the Responses request.

This is client implementation evidence and an upstream explanation of expected server behavior. It does **not** expose the actual keys, chosen branches or server cache contents for our recorded runs. We did not inspect every caller of the internal override or independently observe backend routing. Therefore it would be incorrect to claim that a particular fresh-session key caused the exact measured regression.

The same selected functions in the separately resolved main commit `8c076942cb70fba8e5c4732c23f1faabc4aed484` have the same relevant behavior: [`prompt_cache_key` / `responses_session_id`](https://github.com/openai/codex/blob/8c076942cb70fba8e5c4732c23f1faabc4aed484/codex-rs/core/src/client.rs#L646-L668) and [request construction](https://github.com/openai/codex/blob/8c076942cb70fba8e5c4732c23f1faabc4aed484/codex-rs/core/src/client.rs#L1060-L1094). The complete [`Prompt` structure](https://github.com/openai/codex/blob/8c076942cb70fba8e5c4732c23f1faabc4aed484/codex-rs/core/src/client_common.rs#L21-L42) separately carries conversation items, tool definitions and base instructions. Main is a comparison snapshot, not a claim that the installed binary runs that commit. The large client files were reviewed only in the identified function/block scopes, not in their entirety.

The practical conclusion is limited: **matching source bytes alone cannot guarantee cache sharing across fresh native sessions**. Memglide controls its supplied text; it does not control all native instructions/tools/history, internal affinity branches, provider routing or eviction. A stable user-message source prefix is one eligibility improvement, not control over the entire request prefix or server cache.

## What official caching guidance supports

The full eight Markdown/code cells of OpenAI's pinned [Prompt Caching 101 notebook](https://raw.githubusercontent.com/openai/openai-cookbook/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/Prompt_Caching101.ipynb) were reviewed previously and the stored bytes were verified again here. Cells 1–2 and 7 recommend static content before variable data, identical tool definitions/order and measuring actual cached-token usage. The notebook's examples use older API models; its historical thresholds, discount and latency examples do not establish current ChatGPT-authenticated Codex pricing or performance.

The requested OpenAI web guide was unavailable in the earlier research pass; this notebook is an official alternate, not a claim that the blocked guide was read. Newly attempted `api.github.com` discovery requests also returned `URLError` with no HTTP response status recorded. That host is absent from the configured allowlist. Normal GitHub Git resolution and immutable raw GitHub downloads succeeded; no proxy, TLS or network-policy bypass was used. The exact failed attempts remain in JSON rather than being silently replaced by successful ones.

## The implemented layout refinement

| Choice | Implemented behavior | Why it is useful, and its limit |
| --- | --- | --- |
| Compact source first | Canonical JSON notice and complete path/content pairs precede exactly `\n\nTask:\n` and the original task. | Reusing the same source with a changed task can preserve more leading bytes. It does not establish a cache hit, especially across distinct sessions. |
| Canonical focus ordering | Deduplicate and lexicographically sort explicit focus paths in compact format. | The same file set does not change its prefix merely because the caller reversed arguments. Changed source correctly changes the prefix. |
| Private verification metadata | Full source hashes and line ranges remain in private preparation data; the launcher validates the complete canonical JSON against them. | Removes avoidable model-visible fields without dropping source or weakening local integrity checks. Actual tokenizer impact still requires native usage. |
| Short untrusted-source notice | Retain a concise instruction that content is untrusted and may require newer/additional reads. | Reduces repeated explanation while preserving the trust boundary; a notice does not eliminate prompt injection risk. |
| Preserve current secure reads | Existing approval, indexed eligibility, current ignore policy, byte cap and source/policy rechecks still apply. | Avoids stale contents or a fast-but-incorrect source cache. Preparation and hashing still have local overhead. |
| Explicit compatibility | `memglide-codex` defaults to `compact-prefix`; Python `prepare_prompt` defaults to `legacy`; the old runner explicitly selects legacy. | Avoids silently changing direct API callers or relabeling historical benchmark treatment. The new layout needs its own results. |
| Exact bypass | Off, caller-context supplied, no explicit focus and no project still forward the unchanged task. | No model classifier, MCP process or source cache lookup is added to decide retrieval. False skips and wrapper startup remain measurable costs. |

Compact formatting still delivers every retained file in full. The aggregate default 12,000-byte addition cap includes notice, JSON escaping and separator; if all requested files cannot fit, the function falls back unchanged. The task is not semantically rewritten or summarized. Full metadata is available for local auditing and stdin identity checks without sending it redundantly as source context.

No code invents a Codex cache-key CLI flag, spoofs session IDs, shares A/B sessions, pads prompts, adds an LLM classifier or skips freshness checks to improve a metric. Existing native authentication/configuration is preserved. A later same-session sequence experiment would need matched independent histories; sharing one session between A and B would contaminate the comparison.

## Verification boundaries

The component experiment can establish exact source retention, aggregate byte reduction, canonical same-file prefixes, unchanged original task bytes, fallback behavior and the absence of auxiliary calls. Those are useful engineering checks. A longer common byte prefix is not a measured provider prefix, and serialized bytes are not actual native model tokens.

A native follow-up must record the explicit format/version, model/settings, preparation-plus-execution time, actual total/cached/output usage, independent success and every failed or unavailable attempt. Small repeated development probes should be labeled as probes rather than a fresh held-out 20-task A/B. Old 80-run results must remain attached to the old frozen implementation. Without reliable applicable billing, actual cost and cost per successful task remain null.

This review does not conclude that uncached input is fixed. It identifies a defensible layout improvement and a native-session limitation that the next measurements must respect.
