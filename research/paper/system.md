# Architecture and evidence boundaries

Memglide prepares repository context and records the source and policy used to
prepare it. Its central design choice is conservative selection from current
local files. Lexical evidence, static syntax and bounded dependency expansion
produce a small source bundle without an embedding model or auxiliary
language-model request. The coding agent interprets the task, edits the
repository and checks its work. Memglide changes context preparation rather
than model weights.

The implementation has two entry paths. Interactive clients reach a common
service through a command-line interface, loopback HTTP API or MCP STDIO
server. The service combines repository indexing, context retrieval, a SQLite
database and explicit session memory; a dashboard uses the HTTP API. The native
launcher, `memglide-codex`, calls the source-preparation libraries directly
before executing Codex. The latest comparison evaluates this path with the
opt-in `commands-first` candidate at commit `3c3f82b`, together with the measured
setup planner described below. Figure 1 distinguishes this path from the
interactive services. Interactive retrieval, the dashboard and session-memory
reuse require separate evaluation.

Repository registration resolves the Git root and records project state. The
SQLite FTS5 index stores searchable source, file hashes and metadata, symbol
locations and signatures, and conservative dependency edges. Python structure
comes from the standard AST; JavaScript and TypeScript use an isolated
Tree-sitter worker. Incremental refresh checks current files before using
indexed evidence. Dynamic imports, generated code and runtime dispatch can
leave static dependencies unresolved, limiting what the selected context
represents.

The interactive context engine combines identifier and path matches,
normalized terms, FTS5 evidence and graph expansion. Session memory stores
caller-submitted observations, decisions, errors and fixes with provenance,
timestamps and source versions. Sessions have inactivity and absolute expiry
limits. Returned context passports identify source hashes, memory versions and
omissions. These features provide versioned context within an active session;
the experiment does not measure cross-session reuse. The native prelaunch
selector follows a separate deterministic algorithm and does not automatically
inject session observations.

Prelaunch selection first checks whether preparation is enabled, context has
already been supplied, and an approved project and eligible task are
available. Explicit off/context-supplied modes and requests failing these initial
approval or task gates preserve the original task. The v4 policy
then securely refreshes the index and screens production files. Known tests,
examples and demonstration directories are excluded from production
competition. Potentially relevant unsupported files, partial indexing or an
overfull candidate frontier cause source-selection abstention. Under
`commands-first`, a completed content-selection abstention may still be eligible
for verified command assistance. Source activation and command activation are
recorded separately; reading source successfully does not establish that the
task received useful context.

Remaining supported candidates are parsed into runtime or declaration syntax
units. Normalized query terms receive candidate-set frequency weights
$w(t)=\log(1+(N+0.5)/(\mathrm{df}(t)+0.5))$. Here $N$ is the number of files
passed to syntax ranking, and $\mathrm{df}(t)$ counts those files with term $t$ in
the clean body or header of any eligible-role syntax unit. A file counts once
even if several units match; this frequency is computed on the bounded
candidate set, rather than the entire repository. A unit is sufficient if it has an
explicit current anchor, or at least two distinct clean body/header matches
including one body match. Explicit and sufficient evidence receive large
priority terms in ranking. The remaining score combines body, header, path and
documentation weights with coefficients 3, 2, 0.25 and 0.05. This score orders
evidence; it is not a calibrated confidence. An independently competitive file
causes abstention unless the leader has the required body-evidence dominance.

After accepting an anchor, Memglide reads the complete file and at most three
resolved direct production helpers. It checks their current hashes and
selection evidence before rendering the task. “Full source” refers to these
selected files, not repository-wide or transitive dependency coverage. Final
handoff revalidates inspected competitors, selected source, approval and ignore
policy. A changed proof prevents reuse of the prepared context. Source,
comments and strings remain project data for the coding agent to interpret.

Each phase has its own bounds. Default indexing permits 20,000 files and
100 MiB of eligible source, with a 512,000-byte per-file read limit. The v4 task
limit is 4,000 UTF-8 bytes and 64 normalized non-generic terms, each at most 128
characters. Coarse screening permits 100 files and 2 MiB; syntax analysis permits
24 files and a separate 2 MiB. The syntax worker has a five-second timeout,
200,000-node limit and 1,000,000-byte output limit. Added context defaults to
12,000 UTF-8 bytes, with an additional `ceil(bytes/3)` planning limit of 4,000.
This proxy is not a provider token measurement. Repeated freshness checks mean
that phase byte limits are not whole-workflow I/O or memory bounds.

Public-command assistance requires explicit verification. The caller declares
atomic argument lists and allowed
environment updates. A verifier records a fresh bounded public-text tree,
fingerprints declared executable files, runs the checks, and records exit
status, positive behavioral-test counts and log hashes. It checks the tree,
policy and tools again before writing a canonical receipt outside the project.
The caller retains the trusted receipt hash. Because public tests may execute
repository code, verification is a separate authorized action; context
preparation does not itself run those commands. Public-tree binding is limited
to 20,000 directory entries, depth 12 and 16 MiB of eligible text; individual
reads also obey the project's source-size limit. A receipt is at most 4 MiB,
with at most 16 declared commands and bounded arguments. Declared executable
fingerprints use a separate 256 MiB per-tool limit. These limits describe
different inputs and are not a combined workflow resource budget.

The evaluated candidate separates source selection from command delivery.
Its three final modes are:

- `preloaded`: complete selected source is delivered; a current verified
  command card may accompany it.
- `commands_only`: a card is delivered without selected source. The receipt
  retains the source-decline reason and selection proof, and its source list is
  empty.
- `passthrough`: neither source nor a command card is delivered, and the original
  task bytes are preserved.

Command-only eligibility is limited to explicit content-selection declines,
including ambiguity, weak or missing production evidence, an unsupported
competitor and bounded candidate, dependency or context limits. It requires a
completed v4 decision with a refreshed index and no selected files. Explicit
caller skip gates, an over-limit query, missing approval and freshness or policy
failures do not authorize a command card. This exception changes which verified
facts can be delivered; it does not relax the v4 source-selection threshold or
substitute guessed source.

The launcher loads the receipt against the caller's trusted hash and rechecks
its public-tree, approval, policy and tool bindings. The card gives atomic
commands, allowed environment settings and observed baseline results. Its
`commands-first` instruction says that the listed checks passed on the current
starting tree, asks the agent to use that baseline without repeating it before
editing, and requires the listed checks after changes with their full results.
This is an instruction backed by observed baseline facts, not evidence that the
agent obeyed it or that the future implementation passes.

Unavailable or stale optional facts, or a card that exceeds the unchanged
whole-context caps, leave the underlying source preparation available. For a
command-only candidate, this means returning to the original task when no card
can be delivered. Invalid explicitly pinned receipt input is rejected on an
active workflow path. Before native execution, the launcher repeats source
selection, validates the complete source or source-decline proof, reconstructs
the rendered payload exactly, checks its hashes and rechecks the provider's
current bindings. Even an empty source list does not exempt the eligible public
tree or executable tools from this final freshness check.

The evaluated setup orchestration adds a demand-driven planner before optional
provider creation. After indexing, it invokes the installed v4 preparation and
validation functions, then applies the same command-only eligibility predicate.
If neither complete source nor command-only assistance is eligible, setup skips
public-command execution and supplies no provider to the ordinary launcher.
Eligible routes still require the full fresh binding, public checks, cleanup and
current-manifest validation. A typed initial binding unavailability can omit the
optional provider; failed checks and later integrity failures remain errors.
The launcher subsequently repeats routing and final validation. The planner's
observation is not a reusable receipt. This optimization belongs to the measured
setup workflow; the shipping launcher still consumes an explicitly verified
provider rather than silently running repository tests. Planning, indexing and
verification time are included in the workflow measurement.

The trust boundary separates local preparation from an external coding model.
Selected source is sent to Codex; local-first describes where the index and
state reside. Secure readers enforce containment, reject symlink traversal and
read bounded regular UTF-8 files. Known sensitive filenames and content
patterns are filtered heuristically. Hashes establish equality at checked
reads, not semantic safety, permanent freshness or universal secret detection.
A command receipt covers eligible public text and declared executable bytes,
not every transitive dependency, binary resource or undeclared environment
setting. Sensitive or unreadable eligible text can make the provider
unavailable; the system then makes no verified-command claim. Command-runner
time and output limits also differ from operating-system isolation.

These boundaries motivate separate evaluation of activation, functional
success, preparation time, native execution time and token-tariff equivalents.
The source-and-command workflow incurs planning, verification and freshness costs.
Finite public and hidden checks do not establish universal correctness,
semantic quality of new tests or general coding superiority. Natural
abstentions, functional failures and unavailable telemetry remain in the record.
The measured native path provides no evidence of benefits for the implemented
memory, interactive API or dashboard features.
