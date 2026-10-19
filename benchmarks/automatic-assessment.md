# Automatic source preparation: implementation and evaluation assessment

**Implementation verified; the first held-out offline result is negative and automatic promotion is rejected. The new native model comparison has NOT RUN.** There is no new measured token, end-to-end latency, strict coding-success or model-cost improvement to report. Existing historical reports and failures remain unchanged.

Memglide now has an opt-in path from a natural-language coding task to a bounded bundle of verified complete production files. It reuses the existing local index and source-only delivery path, adds conservative abstention, and makes no auxiliary model call. This is an incremental extension of Memglide, not a replacement model or a claim to outperform every retrieval architecture.

## What changed and what remains uncertain

| Area | Implemented change | Benefit established or expected | Regression risk / unproven result |
| --- | --- | --- | --- |
| Automatic discovery | `prepare_task_prompt` and explicit `memglide-codex --discover` accept a task without caller target paths. Reuse existing symbols, path/signature evidence, project-local lexical weights, FTS5 BM25 and resolved relationships. | Removes the API requirement for manually selected source paths; deterministic private explanations. Development and clean installed-wheel checks pass, but held-out delivery is 0/12 below. | Relevant source can be missed, especially for synonyms, broad work or weak identifiers. There is no measured agent-efficiency gain yet. |
| Conditional gate | `SKIP`, `FOCUSED_SOURCE`, or `FULL_SOURCE` under added-byte and planning-token limits, evidence thresholds, ambiguity rules and bounded helper expansion. | Unsupported, ambiguous, saturated, unsafe or over-budget discovery preserves the exact original task. No selector LLM. | Heuristics are not calibrated probabilities or a prediction of saved cost. An abstention after ranking still pays discovery cost. |
| Duplicate context | Group candidates by file without summing declaration counts; suppress a complete body explicitly present in the actual task only after current-source checks. | Avoids selecting the same file repeatedly or adding exactly supplied source again. | Literal nonduplication does not establish semantic novelty. Old receipts and thread IDs do not prove source remains in the model context. |
| Source fidelity and safety | Reuse complete-file preparation, current repository approval, ignores, secret exclusions, safe paths, source hashes and policy/version rechecks. Reject missing/replaced databases through an existing-state write facade. | Existing source boundaries remain the authority; no intentional truncation of required selected bodies. Full regression and installed-package checks pass below; nine offline source preloads match complete frozen source exactly. | Snapshot freshness can change after return. Static dependency coverage is bounded and does not prove task completeness. |
| Local overhead | Bound metadata query/row/value/VM/time work; preserve complete secure repository refresh. | Observed mean cold setup plus preparation was 1.048 s for automatic C versus 0.728 s for known-path B; descriptive, fixed-order offline measurement. | Refresh scans, parsers, Git subprocesses and database waits can dominate; the metadata deadline is not an end-to-end deadline. Extra preparation can make easy tasks slower. |
| Python excerpts | Separate disabled-by-default explicit experimental API, with restricted declarations and local syntactic closure. | Offers a conservative experiment for reducing added source bytes. | Incomplete-file evidence; no semantic completeness or agent-cost benefit is established. Excluded from automatic preload and the first formal treatment. |
| Warm memory | Existing implementation preserved; no memory lookup or automatic injection in the new adapter. | Avoids reintroducing the historically worse warm treatment by default. | Whether one carefully chosen memory can outperform source-only remains unproven. |
| Observability | Private decisions/reasons, selected versions, phase timings, byte/token estimates, saturation and unresolved static edges. Strict version-4 launcher receipt validation. | Makes local preparation decisions and costs reviewable. | Provider/model telemetry and actual charges cannot be inferred from these receipts. |

`FULL_SOURCE` means complete selected anchor and bounded direct resolved production helpers, **never the entire repository or proof that all relevant dependencies are included**. The ordinary agent retains normal exploration tools. The original explicit-path API, source-only path and launcher defaults remain available; the new automatic feature is opt-in.

See [usage and scope](../docs/automatic-source.md), [separate excerpt experiment](../docs/source-excerpts.md), [implementation plan](automatic-implementation-plan.md) and [primary-source research](auto-source-research.md).

## Historical comparison: useful evidence, bounded scope

The [80-completed-assignment report](warm-80-analysis.md) preserves 80 strict successes, one user-interrupted original and 135 unrun assignments from the stopped 216-assignment study. The fair descriptive subset is the first 72 matched runs: 24 tasks per configuration, eight complete three-task sequences per arm.

In that historical subset, **known-path source-only Memglide** had approximately **9.055% lower estimated API-price-equivalent cost** and **6.892% shorter mean instrumented full task/sequence time** than bare Codex, with equal strict correctness. Warm memory was approximately **12.35% costlier and 3.40% slower** than source-only. These percentages apply to the frozen prior implementation, small task repositories and matched subset; one observed repeat and uncontrolled provider/OS caches limit interpretation.

Those results do not establish actual billed savings, automatic discovery quality or generalization to this implementation. In particular, the prior source-only baseline received caller-selected paths. There is no defensible new C-versus-B or C-versus-Codex efficiency percentage before the preregistered comparison runs.

## Research and architecture rationale

The [research ledger](auto-source-research.json) records 15 fetches, 12 successful primary-source responses, three retained failures, downloaded-byte hashes and exact reading scopes. Repoformer supports investigating selective retrieval, but its trained selector cannot be reproduced by this deterministic wrapper; its Appendix C warns that trial retrieval followed by rejection still pays retrieval overhead. RepoCoder found sparse retrieval competitive with its dense alternative on its completion setup and documented unstable later iterations and latency limitations. Aider offers local graph-ranking and budget-selection examples. Anthropic's context/tool guidance favors useful bounded context and realistic held-out evaluation.

Fresh [official OpenAI latency guidance](https://developers.openai.com/api/docs/guides/latency-optimization) distinguishes output generation and sequential request roundtrips from input processing. Its numerical examples are general heuristics, not predicted Memglide improvements. The new source selector therefore uses classical local computation and must be judged on complete-task outcomes, not added bytes alone. No universal best architecture or transferable upstream speedup is claimed.

## Decision on a memory-aware router

Keep automatic memory injection disabled. Current memory APIs verify ownership/lifecycle, exact claim versions and cited source freshness. The caller-supplied `verified_fix` category and free-text provenance do not prove a rule is true, new or useful. A rule absent verbatim from source can still be a redundant paraphrase.

Context passports merge actual source-item hashes and memory source references into `selected_files`; a passport path is not proof that a complete source body was delivered. Any novelty check must inspect actual delivered bodies/ranges and versions. Current native context retention cannot be proven from an old receipt or thread ID.

The next memory experiment is an offline shadow audit of one candidate, with no injection, covering paraphrase duplicates, unrelated Current claims, misleading categories, changed/ignored source, expired/ended sessions and reference-only passport paths. Any later source-only versus one-memory pilot needs separate preregistration, approval and whole-sequence accounting. This decision preserves existing memory features without claiming an unsupported benefit.

## Verification and offline outcomes

**1,880 Python tests, 24 frontend tests and three production Chromium cases passed: 1,907 distinct automated cases.** This includes existing application/unit/integration/security/API/CLI/MCP coverage and 251 new cases. Targeted runs overlap this total and are not counted again. Ruff passed; mypy passed 29 source files. Two upstream Typer/Click deprecation warnings remain. The production build and frontend bundle passed. A new wheel installed with locked runtime dependencies passed real default/agent MCP clients, loopback API/SPA, CLI doctor, optional-memory preparation and automatic preparation/one fake-native-handoff checks. No actual model was contacted.

[Validation Markdown](automatic-validation.md), [JSON](automatic-validation.json) and [raw evidence](evidence/automatic-v1/artifact-ledger.json) retain initial fixture errors, a conservative bypass, subprocess timeouts and the initial browser failure. Protected existing tests and timeouts were unchanged. Passing these checks establishes behavior within their coverage, not universal security or new native coding success.

**Offline selection: negative.** The frozen first probe used all 12 path-free tasks, one B/C preparation per task. C declined all 12 at `weak_lexical_evidence`, supplied no additional source and preserved the original task exactly. Existing known-path B delivered the evaluator's expected complete source on nine; its three other files were approximately 15.8 kB and could not fit the unchanged 12,000-byte complete-file allowance. No missed or abstained task was removed.

| Offline quantity | Existing known-path B | New automatic C |
| --- | ---: | ---: |
| Preparations | 12 | 12 |
| Delivered complete declared scope (proxy) | 9/12 | 0/12 |
| Mean cold setup + preparation | 0.727844 s | 1.047987 s |
| Median cold setup + preparation | 0.662340 s | 1.052286 s |
| Mean preparation API time, excluding initial approval/index | 0.016691 s | 0.332412 s |
| Mean observed parent CPU, including setup | 0.367692 s | 0.667249 s |
| Mean added UTF-8 bytes across all tasks | 2,823.917 | 0 |
| Median added UTF-8 bytes | 3,235 | 0 |
| Model task correctness/tokens/cost | Unmeasured | Unmeasured |

Cold means fresh project/index state, not cold OS/provider caches or interpreter imports. The offline runner always executes B before C once. Its observed 0.320144 s higher mean C preparation is descriptive, **not a causal full-task latency estimate**. Lower added bytes here mean no evidence delivered, not a token-saving success. Peak preparation RSS, actual filesystem reads and billed charges were not measured. Bare Codex was not run in this offline probe.

All 24 independent treatment checks passed: **nine complete source deliveries** matched the frozen starting Git bytes/hashes, and **15 passthroughs** retained the original task exactly. This proves those treatment bytes, not semantic completeness or agent correctness. [Individual JSON outcomes](evidence/automatic-v1/offline-report.json) preserve every selected version, diagnostic, phase time, byte count and fallback.

| Task | B delivered target scope | C delivered target scope | B cold prep s | C cold prep s | C reason |
| --- | ---: | ---: | ---: | ---: | --- |
| `itsdangerous-base64-padding` | 1 | 0 | 1.327 | 2.298 | weak lexical evidence |
| `itsdangerous-integer-decoding` | 1 | 0 | 1.239 | 1.162 | weak lexical evidence |
| `itsdangerous-compressed-payloads` | 1 | 0 | 0.534 | 1.184 | weak lexical evidence |
| `pyproject-hooks-path-containment` | 0 | 0 | 0.518 | 0.778 | weak lexical evidence |
| `pyproject-hooks-runner-restoration` | 0 | 0 | 0.399 | 0.629 | weak lexical evidence |
| `pyproject-hooks-environment-isolation` | 0 | 0 | 0.400 | 1.053 | weak lexical evidence |
| `mitt-handler-append-order` | 1 | 0 | 0.798 | 0.877 | weak lexical evidence |
| `mitt-absent-handler-removal` | 1 | 0 | 0.640 | 0.609 | weak lexical evidence |
| `mitt-emission-snapshots` | 1 | 0 | 0.428 | 0.542 | weak lexical evidence |
| `ufo-duplicate-query-values` | 1 | 0 | 0.856 | 1.296 | weak lexical evidence |
| `ufo-query-plus-escaping` | 1 | 0 | 0.910 | 1.097 | weak lexical evidence |
| `ufo-path-fragment-boundaries` | 1 | 0 | 0.684 | 1.052 | weak lexical evidence |

### Post-hoc diagnosis, without retuning

The existing ranker put the evaluator's target **first in 8/12 tasks and within the first four in 12/12**. These are post-selection diagnostics, not successful source deliveries. The gate matched only 1–10 declaration/path evidence terms against 31–44 natural-language terms; ratios were 2.7%–23.3%, below its preregistered 30% threshold. The public task's own workflow paragraph contributes 13–16 extra normalized terms. Removing that paragraph alone still leaves objective-only ratios below 30% on every task. The structural problem is asking acceptance-criteria prose to match declaration metadata, despite useful body-level FTS ranking.

Secure refresh averaged 0.257845 s and retrieval 0.058672 s, accounting for about 77.6% and 17.6% respectively of C's 0.332412 s preparation API time. These costs were paid before every abstention. Cheap prequery bypasses work in controlled tests, but did not avoid this postquery overhead.

A downstream **untested hypothesis** is that a raw-score ambiguity ratio is also poorly calibrated: nine multi-candidate tasks have second/first score ratios of 96.9%–100%. The ranker's saturating FTS transform compresses those scores. The helper-exclusion and ambiguity gates were never reached here, so their actual decisions cannot be inferred. Relaxing confidence alone would also not fit B's oversized source into 12 kB.

No source, threshold, task or expected label changed after this first result; no alternative run replaced it. A revised multi-channel policy must be developed separately and tested on a **new held-out cohort**. Do not spend on the planned model comparison yet: C provided no new evidence in this cohort. Automatic discovery stays opt-in and unpromoted; known-path source preparation remains available.

Already observed corpus/grader controls comprise **12 mutated baselines failing, 12 upstream reference versions passing and 12 incomplete/incorrect partial fixes failing**. These validate external behavioral checks and negative controls; they are not model-generated fixes, native successes, a complete upstream suite or evidence of agent performance.

## Reproducible evaluation and corpus limits

The [protocol](automatic-protocol.md) and `python -m benchmarks.run_automatic` runner compare A bare Codex, B existing known-path source-only preparation, and C automatic preparation with no supplied target paths. Plan and offline commands make zero native model requests. The proposed formal study is 12 tasks × three arms × two repeats = **72 original assignments**, with balanced pairwise arm precedence, isolated worktrees/state, identical starts/settings and independent protected grading. Shared workflow text is separated through an explicit public-task query that occurs verbatim in the native prompt; hidden grader information, target labels and reference fixes never enter C selection.

Four pinned full upstream regular-file snapshots supply the tasks: Python `itsdangerous` and `pyproject-hooks`, TypeScript `mitt` and `ufo`. Provenance records respectively 50 files/282,547 bytes, 71/75,966, 13/23,251 and 39/637,695. These are small repositories; the tasks insert one disclosed author-created defect each. They are not upstream issue reproductions, private unfamiliar production workloads or a test of large monorepository scaling. Full tracked regular-file snapshots exclude `.git`; source provenance and licenses are preserved in [the corpus ledger](automatic-fixtures/provenance.json).

Code, task text, reference/grading logic, configuration, locks, pricing assumptions and assignment order must be frozen and checked before formal dispatch. Any code change motivated by held-out misses needs a fresh future cohort. Preserve every failed, skipped, invalid, interrupted and unrun row. The runner records new approval metadata and refuses automatic retries; operator flags are a record of approval, not proof the user gave it.

**Formal native A/B/C: NOT RUN; no new model budget approved.** The generated 72-assignment planning scenario is $18.59 using three times the largest historical possible-cache-write price equivalent per assignment. This is not actual billing, a confidence bound, a guaranteed maximum or a hard spending cap. Recheck published prices and model availability before requesting approval. The user must approve a concrete budget before a large paid comparison. An in-flight request can exceed its allowance.

## Measurement interpretation

| Quantity | Current or future evidence | Interpretation |
| --- | --- | --- |
| Selection/verification time and added UTF-8 bytes | Local preparation receipts; all 24 offline results retained | Direct local observations, including declared measurement scope. |
| Estimated added tokens | `ceil(added UTF-8 bytes / 3)` for automatic source; separately labeled bytes/4 proxy for excerpts | Planning proxy; not model tokens, avoided work or guaranteed savings. |
| Model input/cached-read/cache-write/output | Future supported native JSONL only | Observed where exposed; cached reads are included in input, reasoning in output. Unknown values remain unavailable. |
| Uncached input | Observed total input minus observed cached reads | Distinguish possible cache-write accounting; do not treat missing write telemetry as proven zero. |
| Cost per strict success | Future usage × frozen official prices, including failures | API-price equivalent; complete ratio unavailable if attempted cost is unknown or successes are zero. |
| Actual billed charges | Unavailable | Never substitute list-price equivalents for invoices/subscription charges. |
| File reads, model calls and local resources | Command-text read proxies; underlying inference/filesystem counts unavailable; sampled CPU/RSS with explicit scopes | Do not relabel proxies as actual reads/calls or infer zero overhead from absent measurements. |
| Mean/median paired effects and uncertainty | Future task-clustered paired formal results | Small finite-corpus estimates, not a universal generalization claim. |

## Next experiments and release decision

Reject automatic promotion. Preserve this negative cohort unchanged. First develop repository-aware informative-term weighting and separate body-FTS, symbol/path and graph evidence on development tasks; calibrate abstention against irrelevant/ambiguous controls rather than a raw global score ratio. Evaluate a complete bounded bundle by evidence coverage and byte cost while keeping safety authoritative. Then use fresh held-out tasks and larger repositories before considering model spend. Any excerpt treatment needs its own incomplete-file evaluation.

Investigate trustworthy watcher/index generations and reconciliation for refresh overhead only after overflow, restart, race and ignore-policy controls can preserve current-source guarantees. Keep the secure full refresh as fallback; never substitute mtime alone for freshness. Keep memory shadow-only until a single-rule novelty/usefulness evaluation supports a separately approved pilot.

The source router is an opt-in engineering experiment, not a demonstrated efficiency winner. The known-path historical evidence remains separate; no new comparison with bare Codex, model-token reduction, cost per successful task or actual billed saving has been established.
