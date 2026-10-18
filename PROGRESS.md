# Memglide V1 verification record

The latest [cost assessment](benchmarks/cost-assessment.md) and
[20 original runs](benchmarks/codex-cost-ab.json) compare **bare Codex against
current compact-prefix Memglide** on ten fresh tasks: five Python, five
TypeScript, four small purpose-built repositories, one repeat, five A-first
and five B-first pairs. Both configurations passed 10/10. Runtime, corpus,
official pricing and model/settings were frozen at `c7be678` before execution;
the application source hash stayed unchanged. There were no formal failures,
retries, interruptions, supplemental attempts or resumes.

At the [verified official standard API rates](benchmarks/cost-pricing-research.md)
for `gpt-6.1-sol`, estimated model totals are **$0.392268 for Codex and $0.3833368
for Memglide**, or **$0.0392268 and $0.03833368 per successful task**. This is
2.28% lower overall, but it does **not** establish retrieval cost savings:
the eight source-prepared pairs cost **4.43% more** with Memglide. The two
byte-identical supplied-context controls cost 33.27% less and drive the aggregate
decrease. Five pairs favor each arm. Single-repeat execution and uncontrolled
provider caches limit causal interpretation.

All 20 native streams report zero cache-write tokens. The pinned CLI defaults
an omitted upstream field to zero, so reported zero is not independent proof
of provider cache-write billing. A conservative write-attribution scenario
allows estimated savings between **−15.47% and +16.99%** under the same standard
tariff; this is not a confidence interval. Actual billing, account discounts,
realized routing, local hosting dollars and actual cost per success remain
unavailable. Cached reads/writes are exclusive parts of total input, and
reasoning is already included in output. No category is charged twice.

The independent run audit passed **4,307 assertions**, including native framing,
exact frozen behavioral oracles, complete source delivery, protected tests,
paired settings, log seals and all aggregate metrics. Independent Decimal
arithmetic checks verify the separately derived price-equivalent assessment.
[113 new benchmark/accounting tests passed](benchmarks/cost-validation.md),
with initial helper-test and broad imported-module typing failures preserved.
The earlier 988 application/tooling cases passed at the same unchanged runtime
source; a combined enlarged full-suite rerun is not claimed. The
[downloadable report](benchmarks/memglide-cost-ab-report.zip) preserves pricing,
every formal run, validation history and independent audits.

The earlier [cache-format assessment](benchmarks/cache-refinement-assessment.md)
and [40 individual runs](benchmarks/codex-cache-formats.json) compare **legacy
Memglide against compact-prefix Memglide**, using 20 fresh Python/TypeScript
tasks and one counterbalanced repeat. Neither arm is bare Codex. Implementation
was frozen at `94998bb`; source stayed unchanged throughout execution. Both
arms passed 20/20, with no formal failures, retries, interruptions or resumes.

The new format canonically orders full source before the exact original task,
removes model-visible hash/range metadata, and retains private source validation.
Across the 16 preloads per arm, it delivered the same 24 complete files with a
31.0% smaller added envelope. The conditional gate makes no auxiliary model call.
Existing approval, ignore-policy, complete-source budgets and freshness checks
remain enforced. The launcher defaults to compact-prefix when explicitly used;
the Python API and historical runner retain legacy compatibility.

Full execution time fell 11.2% and output fell 6.1%, but **uncached input rose
3.9%**. Overall input fell 2.0%; that decrease comes from four identical-prompt
controls, while the 16 source-prepared pairs used 0.63% more input and 1.53% more
uncached input. One pair contributes 59.5% of the net time reduction. Provider
cache conditions remain uncontrolled. Cost and cost per successful task remain
null; cache benefits and money savings are unproven. Different tasks and arm
definitions prevent interpreting the earlier +27.1% and current +3.9% uncached
figures as a controlled iteration gain.

[988 distinct tests passed](benchmarks/cache-refinement-validation.md): 961
Python, 24 frontend and three production Chromium cases, plus static, packaging
and installed-package checks. Before formal execution, recovery handling was
fixed to preserve unknown index overhead as null, and read-command attribution
was corrected without changing historical usage, time or grading outcomes.
The post-run independent audit passed 5,138 assertions. Its initial 40 failures
were an auditor argument-order mismatch; the initial audit, corrected auditor
and explanation are retained alongside all original evidence. The
[research review](benchmarks/cache-refinement-research.md) distinguishes pinned
source inspections from inaccessible articles and papers. The
[downloadable report bundle](benchmarks/memglide-cache-refinement-report.zip)
preserves the new experiment and its limitations.

The earlier [focused-launcher assessment](benchmarks/daily-ab-assessment.md) and
[80 individual runs](benchmarks/codex-ab-daily.json) cover 20 fresh known-file
utility tasks, ten Python and ten TypeScript, with two repeats per configuration.
Implementation and protocol were frozen at `6f4b6f6` before formal execution;
no development model pilot was run. Source stayed
unchanged throughout the 2026-10-18 UTC experiment. A and B each passed 40/40,
with 40 verified pairs, no failed or retried formal runs, and no resumes.

The new opt-in launcher makes its preparation decision locally without an
auxiliary model or mandatory MCP request. B delivered 32 complete focused bundles
and correctly bypassed eight supplied-context cases. Both native configurations
had zero MCP calls. B's mean total input fell 2.9%, output fell 6.2%, and full
execution time including cold indexing fell 4.8%; **uncached input rose 27.1%**.
Median paired total input rose 182.5 tokens. Cached input is already part of total
input. Actual billing and cost per successful task remain null. These results
do not establish a money saving, general production-repository benefit,
cross-session memory benefit or equivalently reset provider caches.

The [final validation](benchmarks/daily-validation.md) passed **817 distinct
cases: 790 Python, 24 frontend and three production Chromium tests**, plus
static/build/package/installed-wheel checks. Independent review fixed corrupt
policy fallback, an early-exit grading loophole, completion denominators,
native structured-output/event integrity and resumed-state verification before
the formal experiment. Initial repros and failures remain preserved. The
post-run independent audit passed 9,884 assertions and reconstructed prepared
stdin from frozen source. Audit assertions and overlapping reruns are not added
to the test total.

The [architecture](docs/daily-architecture.md),
[engineering research](benchmarks/daily-engineering-research.md) and
[memory/repository research](benchmarks/daily-memory-research.md) distinguish
read official alternate implementations from inaccessible original articles and
full papers. The [report bundle](benchmarks/memglide-daily-ab-report.zip) preserves
the protocol, all formal attempts, validation and the research access logs.
Earlier experiments below remain historical and used different treatments and
corpora; their percentages are not a controlled comparison with this iteration.

The earlier [optimized assessment](benchmarks/optimized-ab-assessment.md),
[160 individual runs](benchmarks/codex-ab-optimized.json) and
[live context audit](benchmarks/codex-optimized-context.md) cover 40 fresh tasks
across four purpose-built Python/TypeScript repositories, both configurations
and two repeats. The frozen implementation is commit `62e07cc`; its source stayed
unchanged throughout the 2026-10-17/18 UTC experiment. A and B each passed 80/80;
all B runs made an actual MCP source-retrieval call. There were no failed,
interrupted, supplemental or retried formal attempts. Across 80 verified pairs,
B used 32.8% more total input tokens and took 17.9% longer including fresh indexing.
Uncached input rose 2.2%, output rose 5.3%, and sampled CPU/RSS also increased.
This corpus establishes no success or efficiency advantage. Billed cost and cost
per successful task remain unavailable, rather than estimated as actual charges.

The [candidate validation record](benchmarks/optimization-validation-v2.md)
reports **623 distinct passing checks: 596 Python, 24 frontend and three production
Chromium tests**, plus static/build/package/installed-wheel checks. Those totals
include benchmark-tooling tests and do not add repeated executions or audit
assertions. The new opt-in two-tool agent profile removes its background watcher
and mandatory final verification round trip. Metadata-only candidate selection,
bounded request-local source snapshots and whole-source overlap promotion reduce
repeated retrieval work while retaining source checks. The
[component report](benchmarks/optimization-component-v2.md) retains timing
regressions, and [quality evidence](benchmarks/compact-quality-v2.md) explains why
smaller budgets were rejected. The [research record](benchmarks/optimization-research-v2.md)
cites inspected sources and distinguishes findings from untested proposals.
The [report bundle](benchmarks/memglide-ab-optimized-report.zip) contains raw
formal evidence, both unfavorable development pilots and the independent audit.

The original V1 results below are historical. The earlier authenticated Codex
comparison is in [benchmarks/live-ab-assessment.md](benchmarks/live-ab-assessment.md)
and [its JSON analysis](benchmarks/live-ab-assessment.json), with
[all 96 primary runs](benchmarks/codex-ab-authenticated.json) and
[actual MCP context observations](benchmarks/codex-live-context.md).
A passed 48/48; B passed 47/48, with one exec-server interruption left ungraded.
The separate successful retry does not replace that interruption. Across 47
verified pairs B used 2.75 times the input tokens and took 46.5% longer including
fresh indexing. Billed cost and cost per successful task remain unavailable;
this experiment does not establish a benefit. Original authentication failures
and startup pilots remain preserved as historical evidence.

The [final validation record](benchmarks/live-ab-final-validation.md) reports
418 distinct passing checks: 391 Python, 24 frontend and three production-browser
tests. It also retains the initial six compiler-install race failures and their
successful full rerun. Application source and bundled frontend assets stayed
unchanged throughout the authenticated experiment and final verification.

Earlier refinement results are in
[benchmarks/refinements.md](benchmarks/refinements.md) and its
[JSON evidence index](benchmarks/refinements.json). Earlier retrieval, memory-version
and MCP import-isolation fixes, the current verification totals, all strategy
tradeoffs and earlier authentication-blocked Codex attempts are recorded in
[benchmarks/improvements.md](benchmarks/improvements.md) and its
[JSON evidence index](benchmarks/improvements.json). Original reports remain
unchanged; component retrieval gains do not establish Codex savings.

V1 is implemented and passes the local Linux acceptance workflow. All twelve implementation milestones are complete for the tested platform. Authenticated Codex execution is now verified by the comparison above. Native Windows/macOS execution remains unverified.

## Implemented milestones

1. Installable Python foundation, pinned uv/npm dependencies and durable project instructions.
2. Transactional SQLite schema/migration, WAL, FTS5, foreign keys and concurrent local access.
3. Python AST / Tree-sitter JS, TS and TSX indexing; stable symbols; conservative imports/calls; deterministic configurable ranking.
4. Source-aware session memory, provenance, atomic deduplication, bounded inactivity/absolute expiration and deletion.
5. Budgeted context selection, overlap deduplication, explicit known-memory references and bounded search excerpts with full-source fallback.
6. Context Passports, three retrieval levels, dependencies/tests, source versions, gaps and progressive expansion.
7. Incremental filesystem/Git updates, Watchdog debounce/poll fallback, stale memory/passport invalidation and changed-file history.
8. Official MCP SDK 2.3.0 MCPServer with fourteen STDIO tools and safe supported Codex CLI registration.
9. Shared-service CLI and typed FastAPI endpoints with loopback/Host/origin/request-header protections and no-store responses.
10. Seven connected React screens, dark/light/system themes, project/session controls, memory CRUD, context/passport exploration, timeline and settings.
11. Backend, transport, security, component and production-browser integration checks, with discovered defects fixed.
12. Bundled frontend wheel and source distribution, clean installation/reconstruction, installation/security/architecture/MCP/troubleshooting docs and separate V2 plan.

## Executed checks

| Check | Observed result |
| --- | --- |
| Backend suite, source checkout | **126 passed**, no skipped/failed tests; two upstream Typer/Click deprecation warnings |
| Frontend Vitest / React Testing Library | **15 passed** across three files |
| Production Playwright, real FastAPI | **2 passed** in 42.6 seconds; all seven routes at 1440/1024/768 px, no uncaught exceptions or horizontal overflow |
| Ruff format/check | Passed |
| mypy | Passed over 20 Python source files |
| TypeScript and Vite production build | Passed |
| uv frozen dependency installation / lock check | Passed |
| Official MCP STDIO client | Initialized, discovered and invoked all fourteen tools; isolation and ended-session error paths verified |
| Actual Codex CLI configuration | Supported add/get tested in an isolated project-local configuration, existing registration preserved; user configuration unchanged |
| Clean wheel installation | Installed into an isolated environment; imports resolve to installed site-packages, with Tree-sitter 0.25.2 |
| Installed wheel behavior | CLI doctor, fixture registration, eight search hits, seven context items, loopback health, compiled JS/CSS and SPA route all passed |
| Source distribution reconstruction | Required source/tests/locks/ignore/build files present; no caches/node_modules; frozen uv install, clean npm install, TypeScript/Vite build, **15 frontend tests and all 126 backend tests passed** |
| Saved cloud startup command | Actual checkout service started; health/project checks and source-aware `safe_path` context retrieval passed within its budget; validation session cleared |

The normal fixture workflow exercised registration/indexing → session start → search/retrieve/expand → save/edit memory → source edit → stale evidence → updated retrieval → expiry/cascading cleanup. Source code remains intact. New/deleted/renamed files, branch switches, project/session isolation, path/symlink races, ignored secrets, database concurrency and parser failure containment have dedicated coverage. The small ordinary-search comparison reports retrieval behavior only, with no billed-token or cost-saving claim.

## Real-source and failure findings

- Memglide indexed its own repository: 86 files and 324 symbols at the recorded run. A focused retrieval returned 7,512 estimated tokens within an 8,000 budget and correctly produced a Partial passport.
- One valid TSX bare-ampersand grammar warning is reported explicitly by the pinned grammar. Partial structure and text remain available; source syntax is not assumed invalid. Static analysis and secret detection remain heuristic.
- Tree-sitter 0.26.0 crashed in 11/15 isolated trials on real TSX components; the official 0.25.2 release passed 15/15. The pin and lockfile were corrected. Changed JS-family files now use bounded isolated parser batches; native crashes/timeouts/recursion produce visible text-search fallbacks rather than killing the service. Regression coverage parses real frontend components.
- Production browsers caught and verified fixes for ignored-file object rendering, modal keyboard focus, busy controls, ended-session deletion and direct-passport URL/session initialization races.
- In the restricted cloud shell, npm's default user cache was unwritable. A clean install succeeded with a project-local cache and unchanged artifact-integrity/TLS checks. Reusable setup sets both uv and npm cache locations under .cache.

## Environment and distribution

Observed platform: Linux, Python 3.12.14, uv 0.12.23, Node 24.19.0, npm 11.9.0 and Git 2.52.0. No paid service or credential is required by Memglide.

Local artifacts: `dist/memglide-0.1.0-py3-none-any.whl` and `dist/memglide-0.1.0.tar.gz`. Production assets are bundled under generated `src/memglide/web`. Desktop/tablet browser screenshots are in ignored `frontend/test-results/`.

Reusable `install_script` and `start_skill` were saved to the cloud environment draft, including project-local caches, production frontend bundling, restart commands and functional readiness checks. Saving does not publish a snapshot or prove fresh-task restoration. Review/save the draft and publish through environment settings when you want to reuse that snapshot; publication and a new cloud-task restore have not been tested here.

Implementation and validation ran locally. The user subsequently authorized publishing this repository to GitHub. No deployment or package publication was performed. See docs/limitations.md for the supported trust model, static graph and tokenizer limits, filesystem requirements and unverified platform/Codex behavior. Repository changes remain available for user review.

## Independent verification and Codex benchmark (2026-10-16)

The existing application suites were rerun: 126 backend tests (including 69
security/storage cases and all 14 tools through the real STDIO MCP client),
15 frontend tests and two production Chromium workflows passed. No application
fixes were required. Frozen installation, Ruff, mypy, TypeScript, Vite and package
builds passed. Detailed commands and evidence are in
[benchmarks/validation.md](benchmarks/validation.md).

The new benchmark has 24 maintenance tasks, split evenly between Python and
TypeScript. Every task's baseline fails its held-out behavior check, and every
reference fix passes. Its default plan has 96 coding runs: two configurations
and two repetitions per task. It uses identical per-language starting commits,
prompts and model settings, separate worktrees, fresh B databases, balanced arm
order, external grading and supported Codex JSONL/structured output. Necessary B
indexing is counted separately and in end-to-end timing. Diagnostics do not warm
the model database. All planned rows, failures and unavailable measurements are
retained.

The final full Python suite passed **186 tests**, including 60 new benchmark
checks; frontend/browser counts above are additional. Earlier diagnostic
invocations exposed read-only Codex state and a proxy HTTP 403. Writable isolated
state with an authentication symlink resolved startup. The formal readiness
request then reached the provider but failed with HTTP 401 and a token-refresh
error requiring sign-in again. Therefore **none of the 96 coding runs executed**.
Usage, cost per successful task and A/B benefits remain unknown. See
[benchmarks/report.md](benchmarks/report.md) and its JSON companion; configured
MCP availability is not counted as actual Codex invocation.

Independent component probes made 168 actual official-SDK MCP calls across 24
isolated worktrees. Returned evidence hashes were current in all 24 probes, and
all 24 controlled source edits produced stale old passports and refreshed source
hashes/snippets. Natural full task prompts returned the declared fix file in
**16/24** cases. The eight misses are preserved and diagnosed in the report. These
are limited retrieval/freshness diagnostics, not model coding results or savings.

The `chatgpt.com` network addition was saved to the environment draft after the
earlier proxy denial. Saving does not apply or publish it; the latest request's
concrete blocker is unusable Codex authentication. Refresh that authentication
and rerun the documented experiment before making any comparison claim.

## Retrieval fixes and final verification (2026-10-16)

The final source passed **266 Python checks**, **16 frontend checks**, and **two
production Chromium workflows**: **284 distinct checks**, without double-counting
repeated executions. Ruff format/check, mypy (21 source files), the frozen lock,
TypeScript/Vite build, frontend bundling, package content audit and an isolated
installed-wheel retrieval/API smoke check passed. One frontend test timeout was
fixed through explicit request synchronization; the initial failed evidence is
retained, and no product source change or arbitrary timeout increase was needed.

Online research informed five tested policies and a rejected score calibration.
IDF lexical won among new candidates, while legacy ranked development targets
first more often (8/24 versus 6/24). Reused validation is explicitly disclosed.
The combined changes returned declared files and visible declarations in 24/24
fresh official-SDK probes, versus V1's 16/24 and 15/24. Exact symbol identity fell
from 8/24 to 4/24; whole-file/class snippets explain this proxy disagreement.
All 24 hash and controlled-edit checks passed, across 168 real SDK calls.

The final seven-call workflow still averaged 8.2465 seconds versus V1's 5.1211;
all individual measurements and 116 numerical regression observations remain
visible. A separate controlled 20,000-file stress check reduced long-common-query
mean time from 67.7045 to 4.0437 seconds, with identical candidates, scores and
hashes in two reversed-order repeats. All 48 previously evaluated ranking inputs
also retained exact public candidates and scores. No semantic completeness or
universal ranking/performance improvement is claimed.

The latest Codex readiness request (17:10 UTC) still failed HTTP 401 because its
authentication token cannot be refreshed. All 96 coding slots remain unrun,
with unknown success rate, usage, cost and savings. See the detailed
[improvement assessment](benchmarks/improvements.md), [JSON](benchmarks/improvements.json),
[final verification](benchmarks/validation-improved.md), and
[latest A/B report](benchmarks/codex-ab-improved.md). Original V1 reports remain
unchanged. Valid environment Codex sign-in is required to complete that experiment.

## Lifecycle, retrieval and performance refinement (2026-10-17)

The final source passed **376 Python tests, 24 frontend tests and three production
Chromium workflows: 403 distinct checks**, including 69 security/storage cases
and all 14 MCP tools through real STDIO integration. Frozen dependencies, Ruff,
mypy, TypeScript/Vite, the production bundle, package exclusion/source audits and
an isolated installed-wheel retrieval/freshness/API smoke check passed.

Atomic active-session mutations, expiration cleanup, strict settings and delayed
dashboard target selection have regression coverage. Context requests use one
defensive settings snapshot and less repeated serialization. Query focusing keeps
acceptance criteria and explicit references. The first fresh evaluation caught
unsafe documentation-only narrowing and basename anchors; independent failing
regressions drove narrow fixes. Initial results remain unchanged.

On the explicitly **reused** 24-task evaluation, complete primary bodies improved
from 16/24 to 24/24 and declared helper bodies from 20/48 to 39/48. All required
bodies are present in 15/24 tasks; nine remain incomplete. More evidence increased
context bytes and median packing time. Legacy regressed under the new common
packer, and refined ranking itself did not outperform shipped ranking on those
inspection prompts. All observations remain visible.

The final SDK probe passed 24 workflows and 168 actual tool calls, with current
hashes and stale/refreshed controlled-edit checks in every case. Observed whole
workflow mean was 3.2965 seconds versus the historical 8.2465; different host/cache
conditions prevent a causal or model-performance claim. The earlier equal-output
performance experiment is preserved as a separate source stage.

The live Codex readiness request still returned HTTP 401. All 96 coding slots are
unrun; model usage, task completion, billed cost and cost per successful task are
unknown. See [assessment](benchmarks/refinements.md),
[JSON index](benchmarks/refinements.json),
[verification](benchmarks/validation-refined.md) and
[detailed final results](benchmarks/refinement-final-results.md).
