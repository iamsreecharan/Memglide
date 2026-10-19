# Source-router V2: evidence-gate research and security review

**Final scoped architecture/security review: previously identified blockers are resolved in the reviewed patch.** Six small independent helper controls pass; full regression, installed-package checks and formal outcomes belong to the coordinator's separate validation/report.

This review supports a smaller correction to the opt-in source router: evaluate bounded **current source evidence** instead of comparing every task word with declaration metadata or interpreting a mixed retrieval score as confidence. The initial automatic cohort remains unchanged negative evidence. This document does not claim that V2 improves coding correctness, model tokens, latency or billing; the new policy requires its own frozen held-out evaluation.

The reviewer has not inspected the new V2 held-out corpus or task definitions. Policy development and security review use production code, separate development cases and primary sources. No model request or authentication probe was made for this review. Automatic memory injection remains disabled.

## Why this is a plausible correction

The prior policy uses lexical/path/FTS ranking to find candidates but gates them using declaration/path words divided by all normalized task words. That asks structured names to match requirements prose. A useful file can contain the necessary implementation while its declaration metadata lacks acceptance-language terms. A raw ratio between two mixed ranking scores has a separate problem: fixed bonuses and saturating transforms are not calibrated probabilities, and near-equal scores do not establish equal task evidence.

The V2 proposal retains existing candidate ranking and safety boundaries. It derives informative task terms from project-local document frequency, considers bounded live source bodies and compares explicit evidence overlap between independent candidates. Terms absent from the index are not silently treated as proof that a source lacks relevance; they are also not proof that task requirements were satisfied. Distinct lexical terms and project rarity are relevance features, not independence assumptions or semantic utility estimates.

### Relevant primary sources

The [existing research ledger](auto-source-research.json) records exact source responses and reading scopes. Reused evidence includes:

- [SQLite FTS5 BM25 source](https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5_aux.c), selected `fts5Bm25GetData` and `fts5Bm25Function`: frequency saturation, document-length normalization, IDF floor and negative score convention. These motivate respecting scoring semantics; they do not calibrate a hand-weighted composite score.
- [Repoformer](https://arxiv.org/pdf/2403.10059), selected mechanism and Appendix C: selective injection can be useful, but trial retrieval still pays retrieval cost. Its trained selector and serving speedups cannot be transferred to a deterministic wrapper.
- [RepoCoder](https://aclanthology.org/2023.emnlp-main.151.pdf), main text and selected sparse/dense and iteration analyses: sparse evidence can be useful without a new model service, but these completion results do not establish modern agent efficacy or complete dependency discovery.
- [Official OpenAI latency guidance](https://developers.openai.com/api/docs/guides/latency-optimization), previously verified seven-principles sections: input processing, output generation and sequential request roundtrips have different costs. Smaller source bundles are not sufficient evidence of lower full-task latency.

No upstream percentage gain is attributed to Memglide. This is not an assertion that a novel globally optimal retrieval architecture has been discovered.

## Proposed policy and mandatory review conditions

The reviewed implementation uses at most 24 candidate files and 2 MiB of whole-body evidence, project-local document frequencies plus bounded verified candidate-code frequencies, separate metadata and code-like lexical evidence, and abstention for conflicting independent candidates. Normalized query terms, body work and returned matches are bounded. Exact code/constants must be frozen separately before new held-out outcomes are observed. The initial findings and their resolutions appear below.

| Boundary | Required property | Why it matters |
| --- | --- | --- |
| Candidate evidence budget | Bound candidate count, cumulative source bytes, lexical work and SQL work. If a required comparison cannot be completed, abstain explicitly. | Silently ignoring an uninspected candidate can hide ambiguity; a smaller inspection prefix is not a complete candidate comparison. |
| Live body reads | Apply current approval, ancestor ignores, safe paths, symlink rejection, sensitive-source and size policy before reading bodies. Compare secure current hashes with the indexing version. | Ranking metadata is not authority to read or expose excluded or changed source. |
| Policy/source races | Recheck policy and versions for every body whose evidence affected the winning/ambiguity decision, including losing candidates when relevant. | A changed losing file can alter the decision without updating the index generation. Checking only delivered bodies does not establish current evidence for the selection decision. |
| Lexical classification | Use the existing pinned grammars in an isolated worker for JS/TS/TSX and explicit tokenizer error handling for Python. Treat identifier syntax as lexical evidence. | JS/TS regexes, templates and JSX, Python f-strings, shell heredocs and SQL quotes complicate comment/string removal. A lexical token is not proof of executed code or semantic behavior. |
| Evidence and ambiguity | Explain distinct informative matches and any metadata support privately. Do not call thresholds calibrated confidence or guarantee task coverage. | Rare terms can still be irrelevant, and comment/documentation prose can be informative without being executable. |
| Delivery | Preserve the exact selected complete-file preparer, bounded helper expansion, source fidelity and all-or-nothing fallback. | Better lexical routing does not justify clipping required bodies or weakening freshness. |
| Versioned receipt | Make the policy version explicit and strictly validate any new diagnostics, source versions and resource counts. Preserve the V1 report/reproduction path. | Historical and new policy evidence must remain distinguishable. |
| Memory | No new automatic memory branch. | Source hashes do not prove a prior rule's semantic truth, novelty or usefulness. |

The cumulative metadata deadline is not an end-to-end deadline. Full secure repository refresh, current-body hashing, path-policy work, parsers/Git and database waits remain actual preparation work. These costs must be included even when V2 eventually chooses `SKIP`.

## Fresh tariff verification

On 19 October 2026, both [official API pricing](https://developers.openai.com/api/docs/pricing) and the [GPT-6.1 Sol model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol) returned HTTP 200 through the inherited proxy with HTTPS certificate verification. This review read the exact Standard flagship row, matching GPT-6.1 Sol pricing/threshold text and tier multipliers; it did not review every model or every linked document.

| Standard API-price equivalent, USD per 1 million tokens | Ordinary input | Cache read | Cache write | Output |
| --- | ---: | ---: | ---: | ---: |
| At most 272,000 input tokens per model request | 2.00 | 0.10 | 2.50 | 10.00 |
| More than 272,000 input tokens per model request | 4.00 | 0.20 | 5.00 | 15.00 |

The model page states that more than 272K input tokens reprices the **full request** at twice input/cache rates and 1.5 times output rates. Aggregate native-turn input is not automatically one request. Fast is 2× Standard, Batch/Flex 0.5× and Ultrafast 6×. These values match the existing frozen `benchmarks/cost-pricing.json`; that historical tariff file was not edited. Use it with the fresh verification receipt if the formal model/settings remain the same.

Fresh response hashes: pricing `3a0aa16e462a04343f817237b02491b3e4d9126b22c9a54cee8cafd0e9df3c3f` (600,758 bytes); model page `d444d7a0bbf5de241564a76df1a849bc2d4195bf988f2577a996ac21af1d3510` (454,270 bytes). The JSON ledger records retrieval times, URLs, reading scopes and equality with frozen numerical assumptions.

Published API prices do not establish ChatGPT/Codex account charges, discounts, actual service tier, endpoint uplifts or server cache-write attribution. Native login status and installed CLI version do not establish backend acceptance; no model-auth probe occurred here. Actual billing remains unavailable.

## Validation and promotion status

Final V2 patch review: **completed within the stated scope**, with six independent synthetic helper controls passing and no additional blocking finding. New held-out offline/native outcomes: **not reviewed or claimed by this document**. Preserve V1 negative results and make V2 a separate preregistered cohort. Do not change policy constants after new held-out results to rescue that cohort. No additional model call should be used to select or validate context.

The user has authorized the proposed 72-assignment study under an estimated $18.59 API-equivalent planning allowance, subject to the coordinator's offline health checks and frozen protocol. This is not a guaranteed maximum or hard cap. This reviewer does not initiate native requests or change execution approval. A model result, failure, interruption or fallback remains part of the appropriate complete report.

## Initial patch review: blocking lexical-work defect found

The first V2 patch retained current-source/policy guards, bounded the whole candidate pool rather than silently inspecting a prefix, and rechecked losing candidate bodies before delivery. It preserved V1 reproduction and the selected complete-file source path. Review nevertheless found a blocking defect in the new JS/TS regex lexer, before any new held-out corpus inspection or formal requests.

An unmatched block-comment pattern retried scanning the remaining body at subsequent `/*` positions. A small read-only helper probe on synthetic `/*x\n` repetition took approximately 0.089 seconds for 4 kB and 0.356 seconds for 8 kB on the shared host; these individual unreplicated timings illustrate a scaling defect, not normal product latency. The helper also returned `invoice` and `subtotal` as code-like terms from unterminated block comments, quotes and template strings. Closed comment/string controls excluded those terms correctly.

The implementation agent was asked to replace the regex with linear finite-state scanning and conservative incomplete-syntax handling, plus regression controls. That initial patch was blocked pending correction; it was corrected before the final scoped review below. No source code was edited by this reviewer, no held-out data was inspected, and no model request was made. Literal, template, regex and JSX edge cases remain lexical limitations rather than executable-semantics claims.

The official [RE2 project README](https://raw.githubusercontent.com/google/re2/main/README.md), selected introductory guarantee/tradeoff sections, provides a useful primary engineering reference for this defect: it treats linear input-time matching, configurable memory budgets and graceful exhaustion as explicit goals, while rejecting any claim of being fastest under all circumstances. This supports fixing algorithmic work bounds, not adding RE2 as a new Memglide dependency or transferring its implementation guarantee to a custom lexer. The verified 11,420-byte response hashes to `53b525040a3d69727f9244c3021a54d283d00a09ec955c24dc54c490fda86fa6`; an initial guessed README path returned 404 and remains in the ledger. At that review step the ledger contained four fresh requests (three successful, one failed) plus four reused verified sources; subsequent documentation checks are also retained below.

### Linear fix and supported-version follow-ups

The revised patch replaces the backtracking block/literal pattern with finite-state scanning and a shared lexical deadline. The reviewer's 160 kB repeated unclosed-comment control now declines promptly (one observed call: approximately 0.00017 seconds). This resolves the identified quadratic rescan mechanism; the single observation is not a comparative product benchmark. Complete candidate bodies and losing-candidate policies/hashes still receive the existing source guards. Evidence sufficiency now requires informative support in both metadata and code-like channels, rather than allowing any common code token to provide that support.

Two follow-ups were reported before release. First, Python 3.11 is supported, but the review host is Python 3.12.14. The official [CPython 3.11 documentation source](https://raw.githubusercontent.com/python/cpython/3.11/Doc/library/tokenize.rst) explicitly says unclosed single-quoted strings yield `ERRORTOKEN` followed by tokenization of their contents, rather than raising `TokenError`. A NAME-only token filter must reject that error marker explicitly; observing a TokenError on Python 3.12 is insufficient. The selected 10,798-byte response hashes to `f099254f0079a8f503c95c73cbd16a3e01bff5be5bda22126823caef84516e83`. The documentation-host request was denied with CONNECT 403 and retained; the official CPython GitHub source was fetched normally.

Second, the finite lexer masks a common assigned regex literal but still treats pattern words after `if (...)` or `typeof` as code-like identifiers. These constructs need conservative handling or narrower documented classification claims and regression cases. A lexical classifier must never be described as semantic execution analysis. These follow-ups were raised before final review and resolved by the changes documented below. The final ledger records six fresh requests (four successful, two retained failures), plus four reused verified sources.

### Prefer the existing pinned grammar over maintaining a custom JS parser

The coordinator and implementation agent chose to replace the remaining JS-family heuristic scanner with the pinned Tree-sitter JavaScript/TypeScript/TSX grammars already used by Memglide. This should classify regex literals, template substitutions and JSX structurally rather than expanding ad hoc slash-context rules. Identifier syntax remains lexical evidence, not execution or semantic completeness.

Preserve the existing production parser's fault-isolation principle: native parsing occurs in a trusted worker with bounded input, output, parse time, node traversal and total wall time. Do not import indexed repository modules or resolve worker imports through the target repository, environment paths or its working directory. Malformed/missing syntax, worker faults or incomplete candidate output must decline the whole evidence operation. Startup, parsing and child CPU are costs; parent-only CPU does not include that child work. The replacement has now received the final scoped review documented below.

Finally, interpret the formal baselines accurately. B receives author-known paths without charging human discovery time; it is a strong oracle-path baseline. If C ultimately delivers identical source prompts, it adds local preparation work, and random native timing/cost differences alone cannot establish a better selection policy. Path-free usability, benefits over bare Codex and cost superiority over oracle B are separate claims. Record identical-prompt controls and do not invent saved manual discovery time.

## Final reviewed implementation and independent controls

The custom JS lexer is removed. `syntax_identifiers.py` starts as a trusted absolute application script under Python `-I`; its only added import path is derived from its own application installation, never an indexed root, current target directory or `PYTHONPATH`. The worker uses the already pinned Tree-sitter grammars, masks literal/comment/regex/JSX text nodes, and retains identifier nodes inside actual template/JSX expressions. It rejects malformed or missing syntax and returns only normalized query-term matches. It does not import or execute repository code.

The reviewed boundaries are 24 files/2 MiB raw source, 13 MiB escaped worker input, at most 64 query terms of 128 characters, 200 ms native parse per file within a three-second worker batch budget, 200,000 iteratively visited/pending nodes, and a five-second caller timeout. Response schema, version, exact file keys, duplicate JSON keys, duplicate/unknown matches and a 256 kB stdout limit are checked. Worker crashes, timeouts, invalid output and incomplete evidence decline the whole operation. These are practical work bounds, not an end-to-end wall-time or RSS guarantee. Python tokenization rejects nonwhitespace `ERRORTOKEN` explicitly, covering the documented Python 3.11 behavior.

The evidence gate requires informative support in both metadata and code-like channels, or an explicit code anchor. It compares distinct informative evidence sets for independent candidates, not raw score ratios; resolved direct helpers remain bounded. Every inspected candidate's live source version and ancestor ignore policy is rechecked after complete-file preparation, including losing candidates. Settings/index/policy/source changes decline the entire addition. No memory is injected.

An independent read-only probe used only small reviewer-owned source constants: regex literals after `if (...)` and `typeof` were excluded; template and JSX expression identifiers were retained while literal text was excluded; a simulated Python 3.11 error-token stream declined; malformed native syntax declined. **Six controls passed.** These checks made zero model requests, read no new held-out corpus/task data and do not count as native coding successes. The local receipt `.local/router-v2-research/final-helper-review.json` preserves reviewed source hashes, individual observations and explicit scope. Its individual worker startup observations are not a product latency benchmark. A later equivalent change moved native timeout configuration from a deprecated setter into the parser constructor; review confirmed the same numerical bounds.

No additional blocking architecture/security issue was identified in the reviewed automatic adapter, evidence helper and syntax worker. The shared query-normalization resource fix and explicit V1 runner pin were also reviewed below. Full application tests, installed validation, source freeze and any held-out/model comparison remain coordinator verification work. Path-free coverage, lower successful-task cost, lower end-to-end latency and actual billed savings remain unproven by this review.

### Shared normalization bound and V1 reproduction pin

The final read-only review also covered `core/query.py`: the old greedy acronym/CamelCase suffix capture is replaced by fixed-width lookaround boundaries at the same ASCII transitions. Acronym plural handling, case folding, stopwords, singularization and token order remain unchanged. Each boundary test examines a fixed-width neighborhood rather than retrying a long uppercase suffix, addressing source-controlled large identifier work upstream of V2. The accompanying tests preserve manual expected outputs for acronym/CamelCase/underscore/digit/Unicode examples and contain a process-timeout control for 500,000-character uppercase identifiers. This is a resource-regression guard, not a measured product speedup. No new blocking issue was identified in this additional code review.

The old `benchmarks/run_automatic.py` now passes `selection_policy="v1"` explicitly, so changing the opt-in automatic API's default policy to V2 does not silently reinterpret that runner as a new treatment. Original V1 reports and frozen artifacts remain historical evidence. Source manifests still identify exact code, and an old frozen plan is not interchangeable with a new source version merely because its policy name matches.

**Final review disposition: PASS within the stated architecture/security review scope; no additional blocker identified.** This does not approve unobserved efficacy, billing, production readiness or all possible inputs. The reviewer did not inspect the new held-out tasks/corpus, modify application code or make a model/authentication request.
