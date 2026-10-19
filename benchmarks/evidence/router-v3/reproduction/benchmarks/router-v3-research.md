# Runtime-aware source routing: research and release scope

Research date: **19 October 2026**. This review recommends a small correction to
Memglide's **opt-in** automatic source selector: distinguish implementation-body
evidence from declaration/type evidence before choosing a complete source bundle.
It does not establish a new best retrieval architecture, lower coding-agent cost,
or production readiness. No model, authentication probe, test suite, repository
source, or downloaded research code was executed by this review.

The [research ledger](router-v3-research.json) records 17 fresh HTTPS requests:
16 successful responses and one preserved 404. Downloads used the inherited
proxy and certificate verification, with a 2 MiB per-response cap. No network
policy, proxy, certificate trust or credentials were changed. The sources below
are official project code/documentation; exact content hashes identify the
inspected snapshots. Mutable branch URLs are not immutable commit references.

## Begin with the measured failure, not a replacement stack

The existing engine already has local SQLite FTS5, project-local term frequency,
identifier/path/symbol retrieval, AST/Tree-sitter structure, conservative graph
resolution and complete-source delivery with live safety/freshness checks. The
successful historical source-only path uses caller-selected production paths;
it does not prove automatic task-to-file discovery. The latest frozen automatic
v2 offline cohort delivered the declared target in **0/24** observations, while
known-path source preparation delivered it in 24/24. Its two preloads selected
a type-only file rather than the runtime implementation. Preparation was also
slower. That cohort remains negative evidence and is not a tuning holdout now.

Code inspection identifies a plausible mechanism. The v2 syntax worker counts
`type_identifier` and other identifiers anywhere outside opaque comments/literals
in the same `code` set. Type annotations, interfaces and function bodies can
therefore contribute interchangeable lexical evidence. Python tokenization also
does not distinguish an annotation from an implementation name. The evidence
ranker combines indexed symbol names and signatures, then combines code,
metadata and whole-source term matches. These are observed syntactic/lexical
features, not evidence that a particular file implements the requested behavior.

The recent request-local compiled-ignore cache is separate. It halved duplicate
compilations and preserved source/prompt fidelity, but all primary mean timing
intervals included zero, and the unchanged-work control contained a large
apparent gain. Do not carry those local percentages into this selector's claims.

## Primary sources and what they actually support

| Inspected primary source and scope | Useful mechanism | Limit and Memglide consequence |
| --- | --- | --- |
| [TypeScript 3.8 release notes](https://raw.githubusercontent.com/microsoft/TypeScript-Website/v2/packages/documentation/copy/en/release-notes/TypeScript%203.8.md), type-only import/export section; [5.0 release notes](https://raw.githubusercontent.com/microsoft/TypeScript-Website/v2/packages/documentation/copy/en/release-notes/TypeScript%205.0.md), `verbatimModuleSyntax` section | Explicit type-only imports/exports are erased; type aliases/interfaces differ from runtime values. A class has both type and runtime roles. | Keep type evidence available for actual type/API work, but do not treat all matching type names as proof of runtime behavior. Do not blanket-exclude classes or infer every ordinary import's runtime effect; compiler settings and mixed declarations matter. |
| [Tree-sitter query syntax](https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/docs/src/using-parsers/queries/1-syntax.md), full short page; [TypeScript node schema](https://raw.githubusercontent.com/tree-sitter/tree-sitter-typescript/master/typescript/src/node-types.json), selected declaration, body, annotation, import and field nodes; [Python node schema](https://raw.githubusercontent.com/tree-sitter/tree-sitter-python/master/src/node-types.json), selected definition, assignment, type and decorator nodes | Named node kinds and child fields distinguish bodies from annotations and declarations. `ERROR` and missing nodes are distinct parse-recovery conditions. | Classify evidence from node/field ancestry using the existing pinned parser. Preserve runtime initializers, computed fields, decorators and expressions inside templates/JSX. Reject incomplete classification rather than counting omitted competitors as weak. Published current grammar schemas motivate the design; the installed pinned grammar is the implementation authority and needs its own tests. |
| [CPython 3.11 AST documentation](https://raw.githubusercontent.com/python/cpython/3.11/Doc/library/ast.rst) and [3.12 AST documentation](https://raw.githubusercontent.com/python/cpython/3.12/Doc/library/ast.rst), selected `Name`, `AnnAssign`, `FunctionDef`, `arguments`, `arg`, parse warnings and version-change sections | AST fields separate function body, annotation, default arguments and decorators. The supported versions differ in type-parameter/type-alias fields. Parsing is not execution or complete validity checking. | Call the new channels **implementation versus declaration/annotation evidence**. Python annotations are not universally erased and can affect runtime behavior. Never import, evaluate or compile repository code to classify it. Retain resource bounds and conservative unsupported-syntax behavior. |
| [SQLite FTS5 BM25 source](https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5_aux.c), `fts5Bm25GetData` and `fts5Bm25Function` | Frequency saturation, document-length normalization, the `1e-6` nonpositive-IDF floor and a negative best-first score. | Reuse existing sparse candidate generation. Raw composite scores, term rarity and channel agreement are heuristics, not calibrated confidence or completeness. Do not add another fusion layer merely to rescale weak evidence. |
| [RepoCoder README](https://raw.githubusercontent.com/microsoft/CodeT/main/RepoCoder/README.md), full text; [search implementation](https://raw.githubusercontent.com/microsoft/CodeT/main/RepoCoder/search_code.py), `SimilarityScore`, shortlist and vectorizer selection; [vector builder](https://raw.githubusercontent.com/microsoft/CodeT/main/RepoCoder/build_vector.py), `BagOfWords` | A sparse one-gram/Jaccard retriever is a real supported path; retrieval and generation are separate stages. The proposed iterative method uses a generated prediction for another retrieval/generation iteration. | Lightweight code lexical evidence is a credible baseline. Do not adopt an additional model iteration under a zero-auxiliary-call objective. This is repository completion research, not evidence of current Codex task savings. The README also discloses unavailable private function-level execution evaluation code. |
| [Repoformer official README](https://raw.githubusercontent.com/amazon-science/Repoformer/main/README.md), full text | It creates selection labels by running with and without retrieval, then trains special-token selective behavior; sparse/Jaccard and other retrievers are supported. | Selective retrieval is a useful hypothesis, but the trained selector and its inference results do not transfer to a deterministic wrapper. A post-retrieval decline still pays local retrieval cost. No new model selector is justified here. |
| [Official Codex exec CLI](https://raw.githubusercontent.com/openai/codex/main/codex-rs/exec/src/cli.rs), JSON/schema/config arguments; [exec library](https://raw.githubusercontent.com/openai/codex/main/codex-rs/exec/src/lib.rs), module declarations, JSON processor and schema loading; [JSONL processor](https://raw.githubusercontent.com/openai/codex/main/codex-rs/exec/src/event_processor_with_jsonl_output.rs), usage mapping and MCP/turn events | `--json` and `--output-schema` are explicit supported interfaces. The current upstream processor exposes input, cached input, cache-write input, output and reasoning counters where supplied, plus MCP items. | Freeze the installed CLI/version/schema before a native evaluation. Current upstream capability does not prove an older installed CLI or historical cohort observed cache writes. Missing usage must remain unavailable; a library default is not proof that real provider usage was zero. Structured final output is not an independent correctness grade or billed invoice. |

The short [Codex exec documentation stub](https://raw.githubusercontent.com/openai/codex/main/docs/exec.md)
only links to the official noninteractive documentation; it provides no additional
interface details. The initial guessed JSON-processor filename returned 404; its
successful replacement was discovered from the official library's module name.
The failed fetch remains in the ledger. No substantive recommendation depends
on that failure or an inaccessible domain.

Earlier [automatic-source research](auto-source-research.md) and
[router-v2 research](router-v2-research.md) retain the original selected RepoCoder
and Repoformer paper-reading scopes. This round freshly checked their official
READMEs/code, not the complete papers. No competitor's published percentage is
transferred to Memglide, and no fresh pricing verification or model outcome is
claimed by these downloads.

## Smallest useful architecture

Keep one local deterministic pipeline: **approved repository → secure refresh →
existing lexical/symbol shortlist → bounded syntax-origin evidence → selective
complete-file bundle → existing final source/policy verification → original
Codex task or source-prefixed task**. Memory remains an explicit separate feature.

1. Preserve source-only known-path behavior, original v1/v2 reproduction and
   current defaults. Add the new policy explicitly rather than promoting it
   before independent evaluation.
2. Keep path, declaration, implementation-body, annotation/type and prose evidence
   distinguishable. A declaration-only competitor cannot establish runtime
   implementation relevance merely through many matching type names. Explicit
   type work must still have a supported route; ambiguous intent should decline.
3. Use syntax and current observed bodies to justify the choice. Generic task
   requirements, literal text, comments or signatures must not become executable
   evidence or privileged instructions. Distinct matched words are correlated
   relevance features, not independent semantic proofs.
4. Keep complete selected files and bounded useful helpers. A type-aware ranking
   does not prove transitive dependency closure. Required source that exceeds a
   budget must cause honest fallback, not silent clipping.
5. Preserve full candidate inspection limits, isolated trusted workers, original
   task passthrough, current hash/approval/ignore/secret/symlink checks and losing-
   competitor revalidation. Report the precise exhausted phase; a safe decline
   is different from successful discovery.
6. Count all refresh, candidate read/parse, verification and delivery work,
   including declined requests. Record parent and waited-child CPU separately.
   Do not add a model, embedding server, vector database or hosted graph service
   without an independent end-to-end benefit that pays for its extra work.

These are engineering hypotheses about evidence quality. They neither solve
synonym mismatch nor make syntax a proof of behavior. If the public task has no
usable lexical/structural connection to implementation, Codex investigation is
the valid fallback. Once correctness is established, profiling can test whether
hash-and-parser-version-keyed **derived** evidence is worth persisting; that is a
separate migration/invalidation design and must not weaken live source reads.

### Frozen implementation contract before fresh evaluation

The implementation owner specifies explicit `v3`, preserving v1/v2 and current
defaults. It classifies all bounded candidates in one trusted isolated worker:
at most 24 files/2 MiB, five-second caller timeout, three-second internal work
deadline and 200,000 traversal nodes. Python AST and the installed pinned
JavaScript/TypeScript/TSX grammars supply syntax-origin evidence. Clean
definition/parameter headers, implementation identifiers and type/annotation
roles remain separate; indexed signature prose does not satisfy the gate.

Selection uses a bounded relevant AST unit rather than joining unrelated
declarations' words throughout a file. The intended sufficiency rule is an
eligible explicit current anchor, or at least two distinct matched body/header
terms with at least one actual term in the requested role's code. Runtime is
the default role; explicit static-type intent or a current declaration anchor
can justify type work. Stub suffixes can be hints; a basename such as `types.ts`
does not prove the file has no implementation. Candidate-frequency weights and
ambiguity comparisons remain explainable heuristics, not semantic probabilities.
The existing helper bundle and final verification are retained.

For reproducibility, the implemented unit score is `10000 × explicit +
100 × sufficient + 3 × weighted_body + 2 × weighted_header +
0.25 × weighted_path + 0.05 × weighted_docs`. Each matched term uses
`log1p((candidate_count + 0.5) / (candidate_presence + 0.5))`; presence is measured
across eligible retained units, not a calibrated probability. Units are retained
by explicit status, code-term count, combined support and doc-term count before
the ranker selects one eligible unit. Non-explicit selection declines when a
sufficient independent competitor has equal body evidence, the top lacks a
strictly larger body-term count, or its total body/header support is smaller.
Evidence sets need not be strict subsets. These constants are frozen engineering
choices requiring fresh evaluation; the cited sources do not establish them.

This is the owner's pre-evaluation contract, not a test result or a statement
that every language construct is classified correctly. Independent review,
syntax/resource controls and a fresh frozen offline cohort must check it.

## What a production verification report can honestly say

The current product is a local single-user context engine: loopback HTTP,
STDIO MCP, CLI, a bundled dashboard and SQLite on a local filesystem. A successful
package/transport/regression run supports a **tested local release candidate
within its recorded platform and load**, not an unconditional production or
hosted-SaaS readiness claim. Existing architecture documentation explicitly leaves
remote authentication, tenant isolation, TLS, billing, recovery and operational
service targets outside this release. Event retention and product quotas also
need separate design; introducing them implicitly could change existing APIs.

| Final report requirement | Evidence needed; otherwise state unproven |
| --- | --- |
| Existing behavior | Full application suite plus API/CLI/MCP/frontend and clean installed-artifact checks; keep targeted reruns separate from the full count. |
| Selection mechanics | Independent runtime/type, mixed declaration, annotation, literal/comment, malformed syntax, ambiguity and no-match controls; no weakened protected tests. |
| Safety and freshness | Current/changed/deleted/ignored/sensitive sources, symlink escapes, ownership/approval races, bounded parser faults and exact original-task fallback. |
| General selection usefulness | Frozen fresh path-free tasks and unfamiliar repositories, labels/reference fixes outside indexed roots, balanced isolated repeats and negative controls; retain misses and incomplete runs. |
| Local efficiency | Cold and warm full preparation wall/own CPU/waited-child CPU and whole-worker RSS with exact scopes; include refresh and rejected retrieval, all outliers and uncertainty. |
| Coding-agent cost and success | Matched native settings and cache conditions, independently protected correctness, observed token availability, cost per strict success, all failed attempts; local source bytes are not observed model tokens. |
| Financial claims | Distinguish observed tokens, estimated API-equivalent tariffs and actual provider/account invoices; no new charge or savings claim without corresponding evidence. |
| Rollout | Failed evaluation means keep the feature explicit. Correct mechanics, good target coverage, cheaper preparation and cheaper successful coding tasks are distinct claims. |

The planned fresh offline profile can evaluate source selection and local work.
It does not run Codex, establish coding success or prove token/cost savings.
Preserve the old negative cohorts and the earlier source-only model estimates
without pooling their different tasks, settings or measurement boundaries.

## Independent pre-freeze code review

Read-only review of the completed v3 integration, syntax worker, evidence ranker
and unchanged complete-source verifier found no new blocking safety/resource
issue within its scope. It checked explicit opt-in behavior, trusted worker
imports, bounded request/result schemas, declaration-only role overrides,
annotation-only assignment targets, generic checker-workflow handling, current
source/approval checks and losing-candidate revalidation. Initial implementation
findings were corrected before freeze; the local review receipt records exact
reviewed source hashes and does not count a read-only review as test execution.

The isolated child bounds faults and caller wait time, but Python `ast.parse`
constructs its tree before iterative node/deadline checks: the 2 MiB input cap
is not a strict AST RSS cap or hard three-second parse interrupt. Full secure
refresh, Git and database write waits also remain outside a whole-request hard
deadline. Retaining only four units per role and heuristic task-role grammar
can miss useful evidence. These limitations do not justify weakening freshness
or presenting retrieval as semantic execution analysis. New held-out outcomes,
full validation and release packaging belong to the coordinator's separate
evidence, not to this review.
