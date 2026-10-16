# Retrieval improvements and verification

Measured component retrieval now returns the declared target file in **24/24**
natural task-prompt queries, compared with **16/24** in the preserved V1 probe.
Expected declarations are visible in **24/24**, compared with **15/24**. These
are useful, narrow retrieval improvements. They do not establish better coding
outcomes, lower model token use, or lower cost than regular Codex.

The first improved component probe also became slower: mean seven-call workflow
time rose from **5.1211 s to 10.0638 s**, and mean sampled server CPU rose from
**4.8046 s to 9.4808 s**. Those observations remain retained. Subsequent scale
tests identified and addressed a document-frequency counting bottleneck; final
measurements must be read separately from the earlier result.

Final status: application and component verification passed. The live Codex
comparison remains blocked by unusable authentication; all 96 coding slots are
unrun. Model usage, cost and coding-success benefits remain unavailable.

## Evidence and scope

| Evidence | What it measures |
| --- | --- |
| [Preserved V1 assessment](assessment.md), [Markdown](report.md), [JSON](report.json) | Original application verification and 96 planned Codex coding runs, blocked before coding by authentication |
| [Original SDK probe](component-probe.md), [JSON](component-probe.json) | Original 24-task retrieval/freshness observations; 168 real SDK calls |
| [First improved SDK probe](component-probe-improved.md), [JSON](component-probe-improved.json) | Combined retrieval changes before the final frequency-count optimization; 168 real SDK calls |
| [Intermediate comparison](component-comparison.md), [JSON](component-comparison.json) | All 24 original/intermediate pairs and all 95 observed regression measurements |
| [Final component comparison](component-comparison-final.md), [JSON](component-comparison-final.json) | All 24 original/final pairs, source manifests and all 116 numerical regression observations |
| [Research](retrieval-research.md) | Primary online sources actually fetched, source hashes and the resulting experimental hypotheses |
| [Initial strategy experiment](retrieval-strategies-initial.md), [JSON](retrieval-strategies-initial.json) | First locked development/holdout evaluation: 240 query/policy observations |
| [Strategy validation rerun](retrieval-strategies.md), [JSON](retrieval-strategies.json) | Another 240 observations after a regular-plural bug fix; explicitly reused validation |
| [Rejected score calibration](retrieval-calibration.md), [JSON](retrieval-calibration.json) | Additional 48 development-only observations, including the rejected candidate |
| [Frequency performance](search-frequency-performance.md), [JSON](search-frequency-performance.json) | Controlled local search measurements, exact candidate/score comparisons and retained slower cases |
| [Final frequency equivalence](frequency-equivalence-final.json) | Candidate/rank/score comparisons on 48 previously evaluated development/validation queries |
| [Latest Codex A/B attempt](codex-ab-improved.md), [JSON](codex-ab-improved.json) | Fresh authentication failure and all 96 planned coding-run slots; independent of SDK diagnostics |

The original V1 report, assessment and component-probe files are preserved as
historical evidence. Their original test totals and proposed fixes describe that
version, rather than the final working tree. Repeated executions do not create
additional distinct tests or independent task domains.

## Research and implementation decisions

Seven primary HTTPS sources were fetched and inspected: Lucene BM25, SQLite's
actual FTS5 BM25 implementation, Elasticsearch identifier tokenization and RRF,
LangChain RRF and MMR, and Sentence Transformers' retrieve-and-rerank guide.
[The research record](retrieval-research.md) links the exact URLs and content
hashes. Mutable upstream branch names are identified as such; proxy-denied
commit-resolution requests were not replaced with invented commit hashes.

The sources suggested testable choices, rather than an automatic reason to add
complexity. In particular, SQLite floors nonpositive BM25 IDF to `1e-6` and
returns negative scores. A large fixed bonus can overwhelm differences between
weak full-text matches. Rank fusion can combine differently scaled channels,
and diversity can reduce repeated evidence, but either can also lower relevant
results. No embedding model or cross-encoder was downloaded or evaluated.

The implemented changes are:

- **Consistent query analysis.** Search and context ranking share acronym,
  camelCase and snake_case splitting, stop-word handling and modest regular
  plural normalization. Exact paths and explicit code identifiers remain strong
  signals. Ordinary prose nouns such as “repository” no longer receive the same
  explicit-symbol boost as a code reference. Caller intent remains independent
  of configurable score weights. Existing FTS identifiers receive a versioned
  refresh without reparsing unchanged source or replacing its provenance.
- **Corpus-aware lexical evidence.** Project document frequency gives specific
  terms more influence, and BM25 evidence retains score discrimination. For long
  queries, only the 32 most informative terms enter the BM25 candidate shortlist;
  all analyzed terms remain available to identifier and field scoring. This
  bound can change candidate recall on long queries, so it is an explicit
  tradeoff rather than a guarantee that every term receives full-text ranking.
- **Source capacity before optional graph detail.** The context builder fits
  direct source evidence before optional relationship expansion and counts all
  serialized copies of graph metadata against a separate allowance. Bounded
  relationship previews retain stable identities, omission counts and recovery
  guidance. Partial evidence remains visible in passports. The frontend labels
  shortened relationship references as previews, and full relationships remain
  available through dependency inspection.
- **Exact memory acknowledgements.** Returned memories expose a content-based
  version incorporating category, content, provenance and stored source hashes.
  Passports snapshot selected versions. Editing a claim invalidates its previous
  passport even if source hashes and the clock are unchanged. Compaction requires
  an explicit matching `known_memory_versions` acknowledgement; IDs alone remain
  accepted but return full content. This prevents one client's newer read from
  silently acknowledging content another client has never received. HTTP, MCP,
  CLI and expansion requests use the same rule.
- **Isolated installed-server imports.** New Codex registrations launch the
  installed Python environment with `-I -m memglide.cli`, preventing an indexed
  repository package or `PYTHONPATH` from replacing the server during startup.
  Existing registrations are preserved and require deliberate replacement to
  adopt this command. The server still treats indexed source and stored memories
  as data, and indexing does not execute fixture modules.
- **Exact frequency-count optimization.** Single-project ASCII terms use exact
  FTS vocabulary document counts where equivalent. Variant unions and Unicode
  use an exact MATCH fallback. Multi-project counts use a project-scoped row-ID
  membership table, avoiding repeated extraction of stored FTS payloads. Optional
  vocabulary-module absence falls back to exact matching. Counts remain scoped
  to the requested project and are read within a consistent snapshot.

Memory-version acknowledgements change a client-visible behavior: a bare known
memory ID can no longer suppress content. Clients seeking compaction should
retain the returned version and send it with their next context or expansion
request. See [usage](../docs/usage.md) and [MCP integration](../docs/mcp.md).

## Strategy comparison and rejected alternatives

Five policies were compared on the same current index/context implementation:
frozen legacy search, IDF lexical, weighted file-only FTS5 BM25, RRF with
`k=60`, and RRF followed by token-Jaccard MMR with relevance weight `0.85`.
The frozen legacy policy loads trusted committed search code; it does not
reconstruct the entire previous application. Every policy uses the improved
context packer, so this experiment cannot isolate the packer's contribution.

The development set contains 24 unchanged Atlas coding prompts: twelve intents
mirrored across Python and TypeScript. The Orion set contains 24 independently
authored operational queries, again twelve mirrored intents, with a file-level
primary-positive label. The holdout file was locked before first measurement
with SHA-256
`7c4d343fccc6e1b06badc702c2480d8c0151573be9f1fde2281e8a1e9073ba20`.
No model was called by these experiments, and indexed fixture code was not
executed.

The recorded selection rule used development results only: require all queries
valid; maximize returned target-file coverage, then first-result accuracy, then
reciprocal rank; prefer a simpler policy on exact ties. **Legacy was explicitly
a comparator and excluded from selection of a new candidate.** The selected IDF
policy is therefore the best of the tested new candidates under that rule, not
the best policy on every reported metric.

| Policy | Development target first | Development MRR | Initial Orion target first | Initial Orion MRR | Target-file coverage with common improved context |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen legacy | 8/24 | 0.5453 | 22/24 | 0.9583 | 24/24 on each split |
| IDF lexical | 6/24 | 0.4597 | 24/24 | 1.0000 | 24/24 on each split |
| BM25 files | 1/24 | 0.3479 | 24/24 | 1.0000 | 24/24 on each split |
| RRF | 4/24 | 0.4049 | 24/24 | 1.0000 | 24/24 on each split |
| RRF + MMR | 4/24 | 0.4160 | 24/24 | 1.0000 | 24/24 on each split |

All policies also exposed a nonempty snippet for each primary target in this
small experiment. That does not prove that the complete relevant method, every
dependency or all information needed for coding was present. Other returned
files can also be relevant; a single declared positive is not an exhaustive
relevance judgment. **Legacy performed better on development first-result
accuracy and MRR.** IDF improved the initial Orion first-result count by two.
The result is a ranking tradeoff, not a universal ranking improvement. RRF/MMR
added complexity and measured local search time without winning the declared
development selection criteria, so they were not adopted.

After the initial evaluation, an independently discovered regular-plural bug was
fixed and all five policies were rerun. Results above remained unchanged. Orion
had already been evaluated by then: the final strategy report correctly labels
it **previously seen validation**, not a fresh holdout. The initial results and
selection lock remain retained. The second 240 observations do not double the
number of independent queries.

A separate development-only check tested replacing the current BM25 score
contribution with a simpler bounded contribution. Both candidates returned the
target files in 24/24 contexts. The alternative raised mean reciprocal rank
from `0.459722` to `0.465278` but lowered first-result accuracy from **6/24 to
5/24**. It was rejected under the recorded priority order. All 48 observations
remain in the calibration JSON; the previously evaluated Orion queries were not
used to choose this adjustment.

## Full MCP component results, including regressions

The original and first improved probes each made seven actual official-SDK tool
calls per task, with 24 fresh databases and isolated task worktrees. The natural
query was the unchanged full coding prompt, level 2, budget 8,000 estimated
planning tokens. A later exact-file level-3 query and controlled comment edit
tested freshness separately; they do not repair a natural-query miss.

| Measure | Preserved V1 | First improved version | Final optimized version |
| --- | ---: | ---: | ---: |
| Declared target file returned | 16/24 | 24/24 | 24/24 |
| Exact target-symbol identity returned | 8/24 | 4/24 | 4/24 |
| Expected declaration visible in a snippet | 15/24 | 24/24 | 24/24 |
| Natural evidence hashes current | 24/24 | 24/24 | 24/24 |
| Old passport detected controlled edit | 24/24 | 24/24 | 24/24 |
| Updated target hash and edit marker visible | 24/24 | 24/24 | 24/24 |
| Workflow wall seconds, mean / median | 5.1211 / 5.0498 | 10.0638 / 7.2837 | 8.2465 / 7.9083 |
| Natural retrieval wall seconds, mean / median | 0.7735 / 0.7320 | 1.3369 / 0.8618 | 1.0694 / 0.8625 |
| Initial index wall seconds, mean / median | 0.2750 / 0.2450 | 0.5219 / 0.3031 | 0.3421 / 0.3342 |
| Sampled server CPU seconds, mean / median | 4.8046 / 4.7550 | 9.4808 / 6.6550 | 7.8038 / 7.2050 |
| Sampled peak server RSS bytes, mean / median | 81,954,816 / 80,902,144 | 81,161,045 / 80,011,264 | 84,048,384 / 82,808,832 |

Exact symbol identity became worse on five task pairs even though declarations
became visible in every context. Whole-file or class evidence can contain the
needed declaration while carrying a different symbol identity. This explains
the disagreement between proxies; the decrease remains reported rather than
being removed or relabeled a success.

The intermediate comparison retains **95 numerical regression observations**,
including each increase in measured index time, workflow time, natural query
time, CPU or RSS and each drop in symbol identity. A numerical increase in one
sequential observation is not a statistically established regression. Both the
improvement and regression tables retain every task and measurement.

Workflow timing includes server startup, seven SDK operations, controlled edit
and shutdown, excluding the separately measured initial registration/index.
These values are not the cost of one query or incremental overhead versus
regular Codex. CPU and RSS are sampled every 50 ms: short-lived processes may be
missed, CPU is an observed lower bound, and summed RSS may count shared pages
more than once. Host activity and filesystem caches are uncontrolled. There is
one workflow observation per task/version, rather than randomized repeated
performance trials.

Request/fixture pairing is attested from retained SDK arguments: task ID,
language, immutable starting commit, expected targets, session prompt and the
query/level/budget sequence must match. Candidate source manifests were captured
around its probes; the original V1 probe did not record an exact runtime source
manifest. Original source attribution remains **unknown**, despite the retained
Git commit and files, and the comparison does not invent a historical runtime
attestation. The final candidate source digest is `b0fd2cc1f3997d1a0d19ab97addaaef00abe2e859a1cacf570162b6fc231df94`, captured before and after its 24 probes with no source changes. Its final probe retained 168 real SDK tool calls.

## Large-index performance investigation

Long-query stress tests exposed a cost that the tiny task fixtures could not
show. A synthetic index with 20,000 real text files and a 650-term query was used
for paired search measurements. It exercises search over a prepared FTS index,
rather than complete parsing, project registration, watcher rescans or model
execution. Results do not describe all application scaling costs.

The first controlled check bounded only BM25 ranking terms. For a long query
whose terms occur commonly in the index, retaining all terms took **80.2699 s
and 87.0338 s** in two repetitions; retaining 32 informative terms took
**59.1202 s and 60.5877 s**. Execution order reversed for the second repetition.
All four observations remain retained. The shortlist helped this case but left
it near a minute, so it did not resolve the problem.

Inspection found that project-scoped document-frequency queries repeatedly
loaded FTS payloads. The final optimization changes counting rather than score
formulas. Exact vocabulary counts or exact project-row membership avoid those
payload reads where equivalent, with a tokenizer-aware fallback where required.

The final paired count comparison retained the same 20,000-file / 78 MB fixture,
650-term queries and 32-term BM25 shortlist. Two repeats reversed implementation
order. Mean / median long-common-query wall time changed from **67.7045 /
67.7045 s** to **4.0437 / 4.0437 s**; individual optimized observations were
**1.7406 s** and **6.3469 s**, showing substantial variability. Mean process CPU
changed from **67.4406 s** to **3.9679 s**. Short-common-query mean wall time
changed from **3.8486 s** to **1.1846 s**, while absent-term queries were close:
**2.3018 s** versus **2.2417 s**. All 12 observations and CPU distributions are in
[the frequency report](search-frequency-performance.md) and its
[JSON](search-frequency-performance.json). All six paired candidate lists,
including paths, symbols, scores, reasons and hashes, were identical. This
isolates the count implementation on a synthetic index; two repeats with shared
caches do not establish a production latency distribution or a coding benefit.
The earlier shortlist-only failures remain in
[search-shortlist-performance.json](search-shortlist-performance.json).

All **48** previously evaluated development/validation queries also retained
exact candidate ordering, scores, reasons and line ranges after optimization:
[final equivalence JSON](frequency-equivalence-final.json). The source manifest
was unchanged during both comparisons. Passing these inputs is neither a new
holdout nor proof of equivalence for every query. Separate tests cover project
scope, variant unions, Unicode, long queries with a rare late term and an
unavailable optional vocabulary module.

## Correctness, security and integration verification

The preserved V1 assessment recorded 186 Python checks, 15 frontend checks and
two production-browser workflows: **203 distinct checks**. That is historical
evidence and should not be used as the final count for this change set.

| Final verification | Result |
| --- | --- |
| Complete Python suite, including unit, integration, storage, security, official SDK MCP and benchmark harness checks | 266 passed, no failures/errors/skips |
| Frontend component suite | 16 passed, no failures/errors/skips |
| Production Chromium workflows | 2 passed, no failed/flaky/skipped tests |
| Ruff and mypy | Ruff format/check passed; mypy passed over 21 source files |
| TypeScript/Vite production build and bundled frontend | TypeScript/Vite build and frontend bundling passed |
| Wheel/sdist build and artifact-content audit | Wheel/sdist build and content audit passed; isolated installed-wheel smoke passed |
| Distinct checks across Python, frontend and browser suites | 284 distinct checks; repeated runs are not counted again |

The initial final frontend execution had one timeout awaiting a passport heading.
Cold lazy-route loading was suspected, not proven. The test now explicitly
synchronizes the sessions request and passport response while retaining its
unresolved-session assertions and releasing the request gate in `finally`.
No product source change or arbitrary timeout increase was required. The initial
failed execution is retained in [JUnit evidence](evidence/final-frontend-initial-failure.xml);
the final full frontend and production browser suites passed. See
[final verification details](validation-improved.md) and [JSON](validation-improved.json).

Additional cases exercise generic-name collisions, explicit identifiers and
paths, caller queries with zero scoring weights, regular plural forms, stale
normalized indexes, graph-heavy contexts and relationship previews. Memory cases
cover same-clock claim edits, ID-only requests, matching/stale acknowledgements,
multi-client reads, malformed version maps and CLI transport behavior. Import
isolation is checked with a hostile working-directory package and `PYTHONPATH`
canary. Independent retrieval cases cover project ownership, source hashes and
malformed/no-match queries without executing indexed canaries. These cases
verify their stated behaviors; passing tests does not establish absence of all
security or product defects.

## Codex A/B status and unavailable measurements

The live benchmark plan remains 24 coding tasks × two configurations × two
repetitions: **96 planned coding runs**. A uses ordinary Codex; B uses the same
model, settings, structured response schema and prompt with Memglide available.
Fresh worktrees share identical per-language starting commits. Each B run starts
with a fresh index/database and no diagnostic retrieval warm-up. Arm order
reverses for the second repetition, and initialization is separately measured
and included in end-to-end time. Hosted apps/web search and user configuration
are excluded equally from both arms.

The preserved attempt failed its real readiness request with HTTP 401 and a
Codex token-refresh/sign-in error. All 96 original coding slots remain `not_run`,
not 96 failed coding tasks. Earlier read-only state and proxy failures are also
retained. A local “Logged in” status did not establish usable provider
authorization. Writable per-invocation state references the existing
authentication binding without copying credential values into reports.

The fresh attempt at **2026-10-16 17:10 UTC** failed its readiness request in
**3.2655 s** with HTTP 401 and: “Your access token could not be refreshed because
you have since logged out or signed in to another account. Please sign in
again.” Codex exited 1; it completed no model turn. All **96 coding slots are
`not_run`**: zero attempted, completed or graded coding tasks and zero verified
B treatments. No coding success rate, token total, cost per successful task or
A/B benefit is available. See [the new A/B report](codex-ab-improved.md),
[JSON](codex-ab-improved.json) and
[retained preflight events](evidence/codex-improved-preflight/events.jsonl).
Its application source manifest remained unchanged during the attempt.

Refresh the environment's Codex sign-in, or select an existing valid authenticated
state with `--codex-home`, then rerun `python -m benchmarks.run` with the same
model/settings. Do not put a token in chat or checked-in files. This external
authentication prerequisite cannot be repaired by changing retrieval code.

| Requested measure | Interpretation and current evidence limit |
| --- | --- |
| Input, cached input and output tokens | Only supported `codex exec --json` completed-turn usage establishes these; incomplete streams have unavailable totals |
| Actual model cost | Provider invoiced cost is unavailable from this CLI stream; subscription use is not a per-request invoice |
| Model calls | Completed turns do not reveal underlying provider/model request count; keep unavailable |
| MCP calls and treatment | Actual SDK calls establish component transport only; B requires its own observed successful `get_context` result from Codex tool events |
| Execution time | Component/search timings are measured locally; coding-task timing requires actual Codex runs |
| Repeated file reads | Exact I/O tracing is unavailable; literal command-intent proxies remain separately labeled and are not guaranteed I/O lower bounds |
| Automated tests and successful task completion | External graders, rather than model self-report, determine coding success; offline baseline/reference validation is separate |
| Freshness and retrieval completeness | Current hashes and controlled edits test freshness; declared-file/declaration coverage is a narrow proxy, not semantic completeness or model attention |
| Memory and CPU | Local sampled process measurements have coverage/shared-page limits; remote model resources are unavailable |
| Cost per successfully completed task | Requires all attempted-run costs, including failures, divided by successful runs; missing costs or no successful tasks make it undefined |

No unavailable value is estimated and presented as an actual measurement.
Provider prompt caches and host filesystem caches cannot be reliably reset;
counterbalancing and observed cached tokens describe, but do not eliminate, that
limitation. All failed runs, invalid treatments, timeouts, missing metrics and
excluded pairs remain visible in the live report. Unauthenticated readiness
failures do not establish either coding configuration's success rate.

## What the results support and what remains

The available evidence supports improved declared-source coverage for this
combined implementation and tested preservation of hash-based freshness. It
also shows real ranking tradeoffs and an intermediate latency/CPU regression.
The current experiments do not isolate the contribution of source packing,
normalization, lexical scoring or graph bounds; an individual-mechanism ablation
would be needed for causal attribution. The strategy comparison's shared
improved packer explains why it should not be mistaken for an old/full-new
service comparison.

The final SDK workflow mean remained slower than V1: **8.2465 s versus
5.1211 s**; sampled server CPU averaged **7.8038 s versus 4.8046 s**, and mean
sampled peak RSS was **84,048,384 versus 81,954,816 bytes**. All 24 workflows
were numerically slower and the final comparison retains **116 regression
observations** across its metrics. The final workflow mean is lower than the
intermediate 10.0638 s observation, but those sequential runs do not isolate a
causal effect or establish statistical significance. The controlled large-index
comparison separately supports a frequency-count speedup on its synthetic inputs.
These performance costs remain material even with improved declared-source
coverage. Repeated settings/database access and source/path validation were
observed in profiling; request-level batching is a proposed follow-up, not a
measured fix or permission to cache stale evidence. No measured component result alone
supports a claim that Memglide saves model tokens or money, reduces cost per
successful coding task, or improves successful task completion over regular
Codex.

Further improvements should be evaluated against these retained tradeoffs:

1. Run authenticated paired Codex tasks and report test success, all attempted
   costs and treatment fidelity before making a productivity or savings claim.
2. Add independently sampled production repositories, larger cross-file changes
   and a fresh, locked validation set. Two small synthetic coding repositories
   and mirrored language intents limit generalization; 24 IDs are not 24
   independent domains.
3. Isolate context packing, query analysis and ranking with ablations. Keep
   legacy as a meaningful comparator rather than assuming every new policy must
   win. Evaluate tighter budgets where first-result quality matters more.
4. Profile remaining local overhead before changing it. Observed hotspots
   include repeated database/settings access and source/path validation. A
   bounded request-level batch could be tested, but unsafe freshness or security
   caching is not justified by the current measurements.
5. Test longitudinal memory reuse with identical prior histories and count its
   warm-up cost. Fresh B indexes measure retrieval and initialization rather
   than benefits from previously saved task memories.

