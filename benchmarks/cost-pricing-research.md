# Pricing research for the 10-task Codex/Memglide comparison

Official documentation retrieved on **2026-10-18** publishes prices for the exact model used in the experiment, **`gpt-6.1-sol`**. No model alias or surrogate-model price is necessary. The result can be an **API list-price-equivalent estimate** using measured token usage. It is not an actual ChatGPT subscription charge or a provider invoice.

The machine-readable rates are in [cost-pricing.json](cost-pricing.json). [cost-pricing-research.json](cost-pricing-research.json) preserves retrieval times, response hashes, reading scope, failed access attempts, source citations, formulas and limitations. Ignored research files retain the fetched official page/source bytes; the public report contains short excerpts and paraphrases.

## Verified rates

The [official API pricing page](https://developers.openai.com/api/docs/pricing) and [exact model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol) agree on these **USD prices per million tokens**:

| Input/output category | Standard, at most 272,000 input tokens per request | Standard, more than 272,000 input tokens per request |
| --- | ---: | ---: |
| Ordinary uncached input | $2.00 | $4.00 |
| Cached input reads | $0.10 | $0.20 |
| Cache writes | $2.50 | $5.00 |
| Output, including reasoning | $10.00 | $15.00 |

The model page applies the long-context rates to the **full request** once input exceeds 272,000 tokens. A Codex turn may make several model requests; its aggregate input is not one model request. An aggregate below this threshold establishes that each included request is also below it. An aggregate above the threshold requires per-request context usage to determine which requests qualify.

Fast rates are twice Standard; Ultrafast rates are six times Standard; Batch and Flex rates are half Standard. These are pricing scenarios, not proof of the tariff actually applied to a ChatGPT-authenticated CLI session. The API pricing page also describes conditional 10% uplifts for regional processing/data residency and FedRAMP endpoints. The benchmark must not silently apply or exclude an account-specific surcharge as an actual observed charge.

## Correct token accounting

The [official prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) states: “Cache-write pricing is not an additive fee”. Input must be partitioned into ordinary input, cache reads and cache writes. Counting all non-cached tokens at the ordinary rate and then adding the full cache-write rate would overcharge cache writes.

For measured total input `I`, cached input `C`, cache-write input `W` and output `O`, the Standard short-context estimate is:

```text
ordinary input = I - C - W

API price-equivalent USD =
  [(I - C - W) × 2.00 + C × 0.10 + W × 2.50 + O × 10.00]
  / 1,000,000
```

Validate nonnegative integral counts and `C + W <= I`. Cached tokens and cache writes are already within total input. Reasoning tokens are already within output: do not add them again. The pinned Codex wire-parser test uses input 100, output 10, reasoning 5 and total 110, corroborating that relationship.

## What the installed CLI exposes

The installed command reports `codex-cli 0.159.2`. Its official `rust-v0.159.2` source is pinned to commit [`ff6aec96948b70d94983af2641a6b67c94faeff5`](https://github.com/openai/codex/tree/ff6aec96948b70d94983af2641a6b67c94faeff5).

Relevant selected source sections were inspected:

- [`exec/src/exec_events.rs`, lines 59–73](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/exec/src/exec_events.rs#L59): JSONL usage includes total input, cached input, cache-write input, output and reasoning output. These fields must be retained from the native event, even if a previous benchmark parser ignored some of them.
- [`exec/src/event_processor_with_jsonl_output.rs`, lines 118–128](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/exec/src/event_processor_with_jsonl_output.rs#L118): JSONL copies accumulated usage, without an actual dollar charge.
- [`codex-api/src/sse/responses.rs`, lines 128–150](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/codex-api/src/sse/responses.rs#L128): the wire parser maps `input_tokens_details.cache_write_tokens` to `cache_write_input_tokens`, but defaults an omitted cache-write field to zero.
- [`codex-api/src/sse/responses.rs`, lines 799–823](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/codex-api/src/sse/responses.rs#L799): the usage parsing example checks cache-write and reasoning categories.

Consequently, a native-reported cache-write count of zero cannot distinguish an explicit upstream zero from an upstream omission. Retain zero exactly as reported in the primary estimate and disclose the uncertainty; do not relabel the count as independently verified provider billing.

For the same Standard short-context tariff, an additional **hypothetical sensitivity** can treat every non-cached input token as a cache write:

```text
possible-write upper scenario USD =
  [(I - C) × 2.50 + C × 0.10 + O × 10.00] / 1,000,000
```

This is not observed usage. It bounds the extra cache-write premium under that tariff if some zero/defaulted write counts were omitted upstream. It does not bound unknown account tariffs, missing usage from failed requests, external service fees or hosting costs. If A and B have different unknown write behavior, a conservative savings interval uses `1 - B_upper/A_lower` through `1 - B_lower/A_upper`, after each arm's cost is divided by its successful task count.

## Requesting the same Standard routing

Both arms can use the supported config override:

```text
-c 'service_tier="default"'
```

This is supported by the installed version's source, rather than an invented pricing flag:

- [`protocol/src/config_types.rs`, lines 533–537](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/config_types.rs#L533) defines `default` as the explicit Standard-routing sentinel, preventing model catalog defaults from being applied.
- [`core/src/config/mod.rs`, lines 3957–3968](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/core/src/config/mod.rs#L3957) preserves that explicit choice.
- [`protocol/src/openai_models.rs`, lines 1000–1004](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/codex-rs/protocol/src/openai_models.rs#L1000) intentionally omits the sentinel from the outbound tier field.

This verifies the client's supported routing configuration. It does not expose the server's final tier or subscription billing tariff, so Standard list-price equivalence must still be labelled as an estimate.

## Actual spending versus price equivalence

The [pinned official Codex README](https://github.com/openai/codex/blob/ff6aec96948b70d94983af2641a6b67c94faeff5/README.md#using-codex-with-your-chatgpt-plan) describes ChatGPT-plan sign-in separately from API-key setup. Token use under a subscription is not automatically the same thing as a per-task API charge.

The [official Organization Costs API documentation](https://developers.openai.com/api/docs/api-reference/usage/costs) describes time-bucketed monetary values, with optional grouping by project, API key and line item; its request example uses an Admin API key. This public schema is evidence that billing data can be obtained in an appropriately authorized API organization. It does not provide an invoice or charge for these benchmark runs. No billing API calls, credential reads or login changes were made during pricing research.

Keep actual billed dollars `null` unless attributable billing data is available. Report the estimated API price equivalent separately. Do not convert subscription quota or credits into dollar charges without an applicable, verified tariff.

For a fair result:

```text
cost per successful task =
  estimated costs of ALL attempts, including failures
  / number of independently successful tasks

savings % =
  100 × (1 - Memglide cost per success / bare-Codex cost per success)
```

If no task succeeds, cost per success is undefined. If failed attempts lack complete usage, report incomplete cost rather than assuming those attempts cost zero. Local CPU, memory, hosting and separately charged services also remain outside a token-only estimate unless their applicable prices and usage are measured.

## Access and evidence limits

Official API pricing, model and prompt-caching documentation were reachable with TLS verification and the inherited proxy. The marketing pricing URL, Codex pricing/models routes and ChatGPT Help article failed with proxy 403. Some guessed API/source paths returned 404 and were retained as failed attempts. No network policy or authentication was changed to fetch the documents.

Reading scope is explicit in the JSON: pricing/model/caching sections, selected billing schema sections, the full short README/auth redirect, and cited native source functions were reviewed. Fetching a complete HTML or source file does not imply every line was read. No unpublished model mapping, actual money savings conclusion or claim of complete account billing access follows from this research.
