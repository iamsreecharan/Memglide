# Memory and repository research for ordinary coding tasks

Recorded 2026-10-18T02:03:11.253157+00:00. Covers user resources 3, 4, 5, 6 and 8. This report separates verified source behavior, engineering hypotheses and future evaluation requirements.

## Access and review scope

Full scientific papers were not retrieved: arxiv.org, aclanthology.org and static.scale.com requests received explicit proxy 403 tunnel denials. No proxy/TLS bypass was attempted. A separate environment configuration draft requires publication; until applied, no retry is treated as permission.

Review scope is per source: full READMEs/project page/small source files and targeted methods in large implementations. This is not a claim to have read entire repositories or the inaccessible papers.

All GitHub citations below use resolved commit URLs and include the fetched-byte SHA-256, UTC time and status in [daily-memory-research.json](daily-memory-research.json). Raw sources and failed attempts are preserved under ignored `.local/daily-v1/research-memory`; they are reference data, never instructions to execute.

Fetch log: 62 attempts; 50 HTTP 200, 5 HTTP 404, 7 transport/policy failures. Full scientific papers read: **0/5**; the README/code/project-page reviews below must not be presented as full-paper reviews.

## What each resource actually supports

### LongMemEval-V2: memory evaluation, not a coding benchmark

LongMemEval-V2 evaluates bounded evidence for fixed-reader question answering over web/enterprise trajectories; it does not grade repository patches. Backend query receives question/image plus opaque invocation identity, not gold metadata.

**Application:** Keep hidden coding graders and gold patches outside the retrieval input; borrow state/workflow/gotcha/premise categories for later cross-session tests.

**Limit:** Its reported accuracy and memory-query latency are not coding completion rates or whole coding-task costs.

Sources: [M01](#m01), [M02](#m02), [M03](#m03), [M04](#m04), [M07](#m07).

AgentRunbook-R generates structured queries with a controller model and can repair/rerank using further calls. AgentRunbook-C invokes a coding agent to gather evidence. The harness separately times query and post-query hook, after trajectory insertion.

**Application:** Do not add a model-based retrieve-or-skip classifier or second agent to the ordinary-task path; include memory build, retrieval, validation and writeback costs in evaluation.

**Limit:** This is an architecture/cost observation, not measured Memglide savings.

Sources: [M04](#m04), [M05](#m05), [M06](#m06).

### Mem0: separate the 2025 paper, current OSS and managed platform

Current Mem0 README describes an April 2026 managed algorithm with proprietary optimizations, distinct from the 2025 paper. OSS infer=True performs one extraction LLM call plus embedding/retrieval/entity work. infer=False skips extraction but still embeds raw messages. OSS rejects platform-only timestamp/reference_date parameters.

**Application:** Use deterministic, explicit local note writes and lexical matching for the initial low-cost mode; do not add extraction/embedding/entity services merely to copy competitor architecture.

**Limit:** No Mem0 published benchmark number establishes a Memglide improvement; current OSS code is not assumed identical to the 2025 paper.

Sources: [M08](#m08), [M09](#m09).

### Letta/MemGPT: versioned memory without assuming free reflection

Letta main redirects active work to letta-code; the former V1 server is archived. Active MemFS uses Git-tracked memory, bounded core/file/depth constraints and trusted policy for protected content. Reflection is an additional configurable worker mechanism.

**Application:** Borrow small inspectable versioned project notes, bounded context and strict project/agent isolation. Keep any future background reflection opt-in and meter its costs.

**Limit:** MemGPT original full paper was inaccessible; no claim of full-paper review or verification of all Letta runtime behavior.

Sources: [M11](#m11), [M12](#m12), [M13](#m13), [M14](#m14), [M15](#m15), [M16](#m16).

### RepoCoder: use cheap retrieval, do not automatically add generation loops

RepoCoder is iterative repository-level code completion: retrieve windows, generate, then use the prediction for another retrieval/generation round. Released example uses 20-line windows, bag-of-words/Jaccard retrieval and bounded prompt packing. It does not demonstrate complete AST-body retrieval.

**Application:** Borrow cheap local lexical/identifier selection and initial context packing, but make further expansion evidence-driven rather than automatically paying for another generation round. Preserve complete required bodies and explicit omission markers.

**Limit:** Completion exact-match/edit-similarity findings do not prove speed/cost benefits for modern multi-tool Codex; the author README says its function-level execution library was not released.

Sources: [M17](#m17), [M18](#m18), [M19](#m19), [M20](#m20), [M21](#m21).

### SWE-bench Pro: the linked snapshot and current canonical protocol differ

The user-linked SWE-bench Pro README describes the legacy v1 pipeline; the canonical repository adds V2 with 642 tasks/11 repositories, offline agent phase, sanitized history, protected verifier and captured patch replay in fresh sandboxes.

**Application:** Pin commits/toolchains, hide test oracles, require baseline-fail/reference-pass sanity checks, capture agent diffs and replay independently, retain infrastructure retries separately.

**Limit:** A custom fresh 20-task Memglide benchmark must not be called SWE-bench Pro or inherit its published scores; the upstream release gate is a reported result, not rerun here.

Sources: [M22](#m22), [M23](#m23), [M24](#m24), [M25](#m25).

## Recommended architecture and why

This is a testable architecture, not a promise that every task can become faster or cheaper. The no-op path matters: when there is no validated useful evidence, returning ordinary Codex behavior is preferable to forcing memory work.

1. **Build a zero-auxiliary-model deterministic preloader and a cheap no-op path.** MCP startup/tool selection/context gathering must replace existing Codex work, not add a compulsory loop. Verification: Guard tests prohibit network/model clients in gate; report model requests=0 for preprocessing; measure skip CPU/time and equivalent whole-task benchmark.

2. **Pack a small number of complete direct implementations with hard byte/token limits and explicit omissions.** Large default context can increase all subsequent model input; blind token cuts lose required bodies. Verification: Development-only body/dependency coverage tests; independent outcome grading; compare extra ordinary discovery calls.

3. **Use explicit bounded project notes with provenance; no default LLM extraction, entity graph or dream worker.** Mem0/Letta machinery adds real work; ordinary-task benefit must pay for memory creation and future readback. Verification: Note create/read/conflict/expiry/hash/project-isolation tests; whole-sequence cost including writes; plain Markdown decision-log comparator.

4. **Use a locked fresh matched comparison and keep the previous unfavorable benchmark intact.** The new mode must demonstrate benefits with unchanged model/settings and independent graders. Verification: Freeze source/protocol before live tasks; no tuning held-out20; publish every run, unsuccessful attempt and cache caveat.

The gate cannot know whether Codex privately “understands enough.” It can inspect explicit supplied files/snippets, validated context previously delivered, exact paths/identifiers and available project notes. Unknown or ambiguous cases should preserve ordinary discovery, with a measured false-skip rate. A preloaded bundle still consumes model tokens; the benefit must come from eliminated discovery and avoided redundant context.

Treat current source and project decisions differently. Implementation facts should be grounded in current source bytes. Decisions/gotchas need provenance, dates, scope, validation and explicit supersession/conflict metadata. A fresh file hash does not prove that an old decision remains correct. TTL expiry is a reason to revalidate, not a correctness guarantee.

Keep decision and memory creation local and explicit initially. Mem0 `infer=False` still invokes embeddings; copying it would not meet a no-extra-model-services path. Do not introduce embeddings, entity graphs, LLM extraction, controllers, reflections or background daemons unless a measured workload justifies their full cost.

Measure all preprocessing, retrieval, validation, memory writes and execution. LongMemEval-V2 query latency excludes its earlier history insertion and separately records post-query work; Memglide needs full task and whole-sequence totals. A later cross-session study should include a plain Markdown decision log as a comparator, matched later starting commits and stale/conflicting history probes.

For the requested 20-task comparison: use fresh tasks, fixed model/settings/source/protocol, matched repositories and prompts, independent hidden grading, original failures retained, and separate cold/warm local caches. Provider cached-input counts are observations, not proof of identical server cache state. Actual billing remains unavailable unless an authoritative usage/pricing source supplies it.

## Claim register

- **MC01 (verified_source_fact):** LongMemEval-V2 evaluates bounded evidence for fixed-reader question answering over web/enterprise trajectories; it does not grade repository patches. Backend query receives question/image plus opaque invocation identity, not gold metadata. Sources: M01, M02, M03, M04, M07.

- **MC02 (verified_source_fact):** AgentRunbook-R generates structured queries with a controller model and can repair/rerank using further calls. AgentRunbook-C invokes a coding agent to gather evidence. The harness separately times query and post-query hook, after trajectory insertion. Sources: M04, M05, M06.

- **MC03 (verified_source_fact):** Current Mem0 README describes an April 2026 managed algorithm with proprietary optimizations, distinct from the 2025 paper. OSS infer=True performs one extraction LLM call plus embedding/retrieval/entity work. infer=False skips extraction but still embeds raw messages. OSS rejects platform-only timestamp/reference_date parameters. Sources: M08, M09.

- **MC04 (verified_source_fact):** Letta main redirects active work to letta-code; the former V1 server is archived. Active MemFS uses Git-tracked memory, bounded core/file/depth constraints and trusted policy for protected content. Reflection is an additional configurable worker mechanism. Sources: M11, M12, M13, M14, M15, M16.

- **MC05 (verified_source_fact):** RepoCoder is iterative repository-level code completion: retrieve windows, generate, then use the prediction for another retrieval/generation round. Released example uses 20-line windows, bag-of-words/Jaccard retrieval and bounded prompt packing. It does not demonstrate complete AST-body retrieval. Sources: M17, M18, M19, M20, M21.

- **MC06 (verified_source_fact):** The user-linked SWE-bench Pro README describes the legacy v1 pipeline; the canonical repository adds V2 with 642 tasks/11 repositories, offline agent phase, sanitized history, protected verifier and captured patch replay in fresh sandboxes. Sources: M22, M23, M24, M25.

- **MC07 (engineering_hypothesis):** A deterministic task preloader can remove an agent-requested MCP discovery roundtrip and decline unhelpful retrieval without auxiliary model calls. Sources: M03, M08, M12, M18, M24.

- **MC08 (engineering_hypothesis):** Project-scoped memories should retain decision provenance and temporal validity independently of current source snippets. Sources: M08, M09, M13, M14.

- **MC09 (evaluation_requirement):** Ordinary same-day task efficiency requires full lifecycle and success-aware measurement, not payload size or a retrieval-only latency score. Sources: M04, M07, M24, M25.

## Source ledger

<a id="m01"></a>

**M01 — LongMemEval-V2 official README**. full README. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/LongMemEval-V2/2cc8c540bdb87fe6761629b585e727e1c4704520/README.md). HTTP 200; SHA-256 `399cc61c9540e587017fccdde28b29b62ed66326425f16f08b5fe0457a593abd`; fetched 2026-10-18T02:00:29.271767+00:00.

<a id="m02"></a>

**M02 — LongMemEval-V2 author project page**. full readable project page, not the paper. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/xiaowu0162.github.io/cf5dfbca96fa6d73e4d9a42012acca14bfedc28d/longmemeval-v2/index.html). HTTP 200; SHA-256 `e28f0a57ce1d15df91a29027baf5ed4a39f8918ae569eaedc388fca027234011`; fetched 2026-10-18T02:01:12.560594+00:00.

<a id="m03"></a>

**M03 — LongMemEval-V2 memory backend interface**. full source file. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/LongMemEval-V2/2cc8c540bdb87fe6761629b585e727e1c4704520/memory_modules/memory.py). HTTP 200; SHA-256 `607ca21320067df2abc3583b80debeb819781e90955776bdea4313a8b93a0586`; fetched 2026-10-18T02:00:29.274103+00:00.

<a id="m04"></a>

**M04 — LongMemEval-V2 evaluator**. targeted source: build_prompt_row, per-question insertion, aggregate metrics. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/LongMemEval-V2/2cc8c540bdb87fe6761629b585e727e1c4704520/evaluation/harness.py). HTTP 200; SHA-256 `93fe5855a74ad46d7e8b489cebac24de38a9b30ba7ec1de2dd8708bd4aeebdb6`; fetched 2026-10-18T02:00:29.280344+00:00.

<a id="m05"></a>

**M05 — LongMemEval-V2 AgentRunbook-R**. targeted source: query, query generation/repair, retrieval/rerank routing. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/LongMemEval-V2/2cc8c540bdb87fe6761629b585e727e1c4704520/memory_modules/agentrunbook_r.py). HTTP 200; SHA-256 `7e96c0f386224bf13ad2a694f35bc6546738bf3b99de09c89fcc3a85509fb8f8`; fetched 2026-10-18T02:00:29.275967+00:00.

<a id="m06"></a>

**M06 — LongMemEval-V2 AgentRunbook-C**. source: file workspace, summary rendering, Codex subprocess query lifecycle. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/LongMemEval-V2/2cc8c540bdb87fe6761629b585e727e1c4704520/memory_modules/agentrunbook_c.py). HTTP 200; SHA-256 `18b30338c847f246734d116d6830967894867598b7b0b73c71070db3ad5dcea3`; fetched 2026-10-18T02:00:29.277513+00:00.

<a id="m07"></a>

**M07 — LongMemEval-V2 leaderboard protocol**. full README. [Pinned source](https://raw.githubusercontent.com/xiaowu0162/LongMemEval-V2/2cc8c540bdb87fe6761629b585e727e1c4704520/leaderboard/README.md). HTTP 200; SHA-256 `7c703e2c138b23949eefe1a89aa981d6d4ba9340b0060b5ca0a0225c780f257f`; fetched 2026-10-18T02:00:29.284897+00:00.

<a id="m08"></a>

**M08 — Mem0 official README**. full README. [Pinned source](https://raw.githubusercontent.com/mem0ai/mem0/0724291bd864cf807e88ee8981c8226644e8fb42/README.md). HTTP 200; SHA-256 `f72db3426438dbdf6879a2b50583fbee8e7e2dde5d01308c6295bcd09fd3db86`; fetched 2026-10-18T02:00:29.760168+00:00.

<a id="m09"></a>

**M09 — Mem0 OSS Memory implementation**. targeted source: initialization, add, extraction, embedding, dedup, scoped search/expiration. [Pinned source](https://raw.githubusercontent.com/mem0ai/mem0/0724291bd864cf807e88ee8981c8226644e8fb42/mem0/memory/main.py). HTTP 200; SHA-256 `f329ca4a17af1fbefb32ac10d4cc7ae7ddbdb7435a87eb74c30915cff98b8b7c`; fetched 2026-10-18T01:59:52.275830+00:00.

<a id="m10"></a>

**M10 — Mem0 memory-benchmarks README**. full README. [Pinned source](https://raw.githubusercontent.com/mem0ai/memory-benchmarks/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/README.md). HTTP 200; SHA-256 `ed4ee055be417ca6896aab00b2ad62d4b3c67205ed32f496544803492faffae2`; fetched 2026-10-18T02:01:13.017736+00:00.

<a id="m11"></a>

**M11 — Letta current repository redirect**. full README. [Pinned source](https://raw.githubusercontent.com/letta-ai/letta/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a/README.md). HTTP 200; SHA-256 `1d624e8fd383c1198c8d42da87b055d591a5760e19607692eb46bbbfe2a58f03`; fetched 2026-10-18T02:00:29.806287+00:00.

<a id="m12"></a>

**M12 — Letta Code active harness**. full README. [Pinned source](https://raw.githubusercontent.com/letta-ai/letta-code/7be3c81f9cfce481994fe4484d59a5bf17cdb48a/README.md). HTTP 200; SHA-256 `61811b022086eeb9d0bdab91cce960f193e9b1bec544c36f64cf6a1f5eb9382c`; fetched 2026-10-18T02:00:29.819434+00:00.

<a id="m13"></a>

**M13 — Letta Code memory constraints**. full source file. [Pinned source](https://raw.githubusercontent.com/letta-ai/letta-code/7be3c81f9cfce481994fe4484d59a5bf17cdb48a/src/memory-constraints.ts). HTTP 200; SHA-256 `8a1dd24323b4c89315a9daa0a5f33802235b18088f53021a1626247e317f5da7`; fetched 2026-10-18T02:01:12.566776+00:00.

<a id="m14"></a>

**M14 — Letta Code memory frontmatter policy**. full source file. [Pinned source](https://raw.githubusercontent.com/letta-ai/letta-code/7be3c81f9cfce481994fe4484d59a5bf17cdb48a/src/memory-frontmatter.ts). HTTP 200; SHA-256 `01010a6e79bb34b08345433ff352e5c52e2eed26051fe8960ed8470de082327c`; fetched 2026-10-18T02:01:12.572971+00:00.

<a id="m15"></a>

**M15 — Letta Code memory process confinement wrapper**. full source file; downstream sandbox implementation not reviewed. [Pinned source](https://raw.githubusercontent.com/letta-ai/letta-code/7be3c81f9cfce481994fe4484d59a5bf17cdb48a/src/memory-confinement.ts). HTTP 200; SHA-256 `86ee70df3a9b8f6c4bc0e8bd03e0f5a8ba37a6aad40a0710f7bd64de7d1ae780`; fetched 2026-10-18T02:01:12.571130+00:00.

<a id="m16"></a>

**M16 — Letta Code reflection configuration**. full source file. [Pinned source](https://raw.githubusercontent.com/letta-ai/letta-code/7be3c81f9cfce481994fe4484d59a5bf17cdb48a/src/reflection-settings.ts). HTTP 200; SHA-256 `54bb6d37d25a29e442e797a77b9016dd016bc20ab71403f62d79692c9d9c49bc`; fetched 2026-10-18T02:01:12.993685+00:00.

<a id="m17"></a>

**M17 — RepoCoder author README**. full README. [Pinned source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/README.md). HTTP 200; SHA-256 `d19d72d5407c3d7081a9f5393dca53503f3b8dc5a36be4ee0ec9d8ee4f34cd1b`; fetched 2026-10-18T02:00:30.427174+00:00.

<a id="m18"></a>

**M18 — RepoCoder retrieval/generation pipeline**. full source file. [Pinned source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/run_pipeline.py). HTTP 200; SHA-256 `b08804b7d4de453ee1d0cdc8333c0658608df3b67a4a298bf447421f08da7bf6`; fetched 2026-10-18T02:00:30.428189+00:00.

<a id="m19"></a>

**M19 — RepoCoder window construction**. full source file. [Pinned source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/make_window.py). HTTP 200; SHA-256 `45b01cfe027a887c0f3da521076a384b1577a1189ff7940842d706bb90c47603`; fetched 2026-10-18T02:00:30.504260+00:00.

<a id="m20"></a>

**M20 — RepoCoder retrieval scoring**. full source file. [Pinned source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/search_code.py). HTTP 200; SHA-256 `977bc3469390b030dc2f47cd8a9b4449c9142308e58afe2b90d0fecad7359ba3`; fetched 2026-10-18T02:00:30.607804+00:00.

<a id="m21"></a>

**M21 — RepoCoder prompt construction**. full source file. [Pinned source](https://raw.githubusercontent.com/microsoft/CodeT/35f54d60b152cc31d134b788e702878ad613d9f7/RepoCoder/build_prompt.py). HTTP 200; SHA-256 `1907f0b26ba4fbd02b1b43cf88c0478b8ee9cad7e6fe15e5c769a8863c10039b`; fetched 2026-10-18T02:00:30.652817+00:00.

<a id="m22"></a>

**M22 — User-linked SWE-bench Pro repository snapshot**. full README. [Pinned source](https://raw.githubusercontent.com/EvanXiaa/swepro/64ab94d68861a98ae0203be1e29e9428b93bd5e9/README.md). HTTP 200; SHA-256 `8a07de16a7a25dd6ad0001ed61e0c61d9ec3093287f12405ca216cd6aa4ab20b`; fetched 2026-10-18T02:00:30.115346+00:00.

<a id="m23"></a>

**M23 — SWE-bench Pro canonical repository README**. full README. [Pinned source](https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/66f92766bba642462d4bbe5479e83f91f9211862/README.md). HTTP 200; SHA-256 `9b5058fbc2f806a47a2de6db9a89c5805b8c7d89319cd7d4f9b328c091d1f983`; fetched 2026-10-18T02:00:30.156671+00:00.

<a id="m24"></a>

**M24 — SWE-bench Pro V2 protocol**. full README. [Pinned source](https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/66f92766bba642462d4bbe5479e83f91f9211862/v2/README.md). HTTP 200; SHA-256 `dde4168fed17ca1ea00b26a93aca78dad43c7b3f981b93a2872428259428231f`; fetched 2026-10-18T02:01:12.562890+00:00.

<a id="m25"></a>

**M25 — SWE-bench Pro V2 published release gate**. full gate record, not independently rerun. [Pinned source](https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/66f92766bba642462d4bbe5479e83f91f9211862/v2/GATE.md). HTTP 200; SHA-256 `7c30b8d6aef5ea7413831ac5618220f8c01ff15439bc6732a25ceaeb2c401e71`; fetched 2026-10-18T02:01:12.564231+00:00.

<a id="m26"></a>

**M26 — SWE-bench Pro legacy v1 evaluator**. targeted source; canonical README marks this as v1, not V2. [Pinned source](https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/66f92766bba642462d4bbe5479e83f91f9211862/swe_bench_pro_eval.py). HTTP 200; SHA-256 `bb5d4c5486be296e464e695df3747064aaa3bb197394bc6d39980634afec2034`; fetched 2026-10-18T02:00:30.216106+00:00.

## Remaining limits

- Some discovery URLs returned 404, including an incorrect initial RepoCoder CodeBERT path and guessed GitHub PDF mirror; all attempts are retained in the source log. Canonical RepoCoder author source was then verified at microsoft/CodeT.

- Published competitor/benchmark statistics remain attributed claims; no Memglide token, latency, accuracy or cost improvement is inferred from them.

- Current source snapshots can differ from the architecture in older papers. The report distinguishes current Mem0/Letta implementations from their original papers.

- No fresh live 20-task corpus, gold patches or hidden grading assertions were read or tuned during this research. No model API requests or external account creation were performed.
