# Evaluation design

## Task panel and conditions

The v7 experiment started with 36 author-designed feature tasks in 36 pinned
public repositories: 18 Python projects and 18 JavaScript/TypeScript projects.
Tasks were selected for executable upstream checks, not sampled from historical
issues. Several repositories share maintainers or development conventions.
The model's prior familiarity with their source is unknown. AI agents assisted
with task writing, feature oracles, reference implementations, deliberately
incorrect controls and review. Separate authoring roles and control outcomes
provide checks on the evaluation; they are not independent human replication.
Public task inputs, dependency profiles, commands and original protected-file
hashes were fixed before collection. Each task had baseline, reference and
incorrect-implementation controls. Private tests remain finite specifications,
and the wording ambiguity discussed in the results limits one task's rubric.

The comparison uses the installed candidate whose source bytes are preserved
at commit `3c3f82b`. Arm A invokes its explicit off/pass-through mode. Arm M
uses the commands-first policy: bounded v4 source discovery can preload source;
when source discovery abstains but the production workflow is eligible, a
verified public-command card can be supplied without source. Otherwise the
original task passes through. All assigned tasks remain in the comparison,
including abstentions. Source, command-only and pass-through decisions are
policy outcomes, not separate randomized arms.

M indexes the project and checks actual production eligibility before creating
the command provider. Full public baseline verification and binding are skipped
only when no eligible card would attach. Eligible source or command-only paths
still require fresh verification, cleanup, manifest binding and validation by
the installed launcher. This demand-driven setup policy was fixed before the
28-task primary cohort began. Product source did not change during that
cohort; later repairs concerned the harness, source-role metadata and telemetry
interpretation. The experiment measures the combined installed policy, not the
isolated effect of a source excerpt or command card.

## Allocation and the fixed primary cohort

The original schedule contained two arms and two repeats per task, or 144
unique assignments. Seed 20261101 determined a sequential, balanced first-repeat
schedule with 18 A–M and 18 M–A task orders. Repeat two reversed the full
first-repeat task/arm sequence. Every coding session used a fresh project copy,
local native state and thread.

The first 15 assignments exposed eight tasks before an infrastructure stop.
Assignment 0016, on an already exposed task, then failed locally before the
native bridge because its copied executable lacked execute permission. Its
recorded usage remains unknown. Before any of the remaining tasks had a model
session, the primary cohort was defined as the 28 tasks outside that exposure
prefix: 15 Python and 13 JavaScript/TypeScript projects. Each contributes both
arms twice, giving 112 sessions and 28 analysis clusters. This membership rule
used exposure, not observed savings, speed or grading outcomes.

The same 112 primary assignments occupy slots 0017–0128. The final 16 slots are
the remaining second-repeat sessions on the eight exposed tasks; these are
auxiliary descriptive evidence. The completed 128-record comparison pool
therefore spans 36 tasks with unequal repeat coverage. Statistical inference
uses the 28 complete task clusters; the other 16 records are descriptive.
No primary task was removed because retrieval abstained, coding failed or a
measurement appeared unfavorable. The primary cohort retains 13 A–M and 15 M–A
first-repeat orders.

## Collection, amendments and isolation

All coding sessions requested `gpt-6.1-sol`, low reasoning effort and the default
service tier through Codex CLI 0.159.2. This fixes the requested alias, not a
provider backend or model-weight snapshot. Both arms received the same task and
common developer contract, response schema, tools and network-disabled
workspace-write configuration. Project-document injection was disabled in both.
Actual prompt bytes and native arguments were checked against installed
zero-model handoff receipts. These are coding-agent `codex exec` sessions;
local sandbox processes used for controls or grading do not themselves make
additional coding-model requests. Neither process counts nor agent commands
identify the provider's internal inference count.

Collection required several versioned amendments. After 25 primary
measurements, a broad protected-file rule incorrectly classified published
production files as tests or build material. A baseline-only audit of all 36
repositories certified five exact production code/type paths. It used original
package metadata and public module documentation, not candidate patches,
private grades or resource contrasts. The correction was applied uniformly to
all 128 records while preserving the original raw flags. Feature assertions
and reference cases were unchanged. Ordinary edits to owned protected tests,
documentation or configuration still imply strict coding failure; unsafe
paths, Git/shared-dependency changes and evidence corruption remain hard
integrity failures.

After 52 measurements, the usage parser stopped on an intermediate reconnect
warning even though its turn completed. The pinned CLI source distinguishes
retry notifications from fatal failures but renders both through the same
JSONL error shape. A separate, source-verified adapter accepts only the narrow
retry constructions within one fresh, completed thread/turn, with matching
full token counters, telemetry, process identity and final-output evidence.
It recomputes every pooled record and preserves the original parser verdict
and events. Arbitrary errors or unfinished turns remain invalid. The resulting
estimand is native-reported completed-thread usage, not proof that every
underlying provider attempt is accounted for in an invoice.

A subsequent slot-0069 CLI startup failed on a missing local output-schema file.
Pinned source established that this exit precedes model-turn creation. That
extra process remains a separate operational failure with its original null
usage; only its separate ledger records source-proven zero generation requests
and zero model-generation tariff. The canonical model assignment proceeded
after deployment repair. A declared sensitivity charges the full failed
startup duration to that M assignment. Operator diagnosis and repair time was
not measured. Overall accounting retains 144 unique master assignments, 145
allocation attempts, 143 coding-model turns and 144 native CLI processes. These
counts exclude separate development and connectivity probes.

The final pool combines the first 52 measurements with the remaining 76 canonical
sessions. There were no retries of measured coding trials, replacement tasks,
additional outcome-driven repeats or significance-based stopping. Original
stopped states and protocol decisions remain unchanged and cannot acquire a
retrospective confirmatory pass. Because 25 measurements preceded the
source-role correction and 52 preceded the parser amendment, the final study
is an **amended fixed-panel evaluation**. Its local hashes and analysis freezes
are audit commitments, not a public preregistration or a fully prospective
confirmation.

Private grader, reference and control plaintext was absent during model
collection. Authenticated AES-GCM ciphertext and per-file commitments could
remain locally, while keys were held outside the model executor. A historical
key-loss incident required reconstruction against original hash commitments
before the primary cohort began; later versioning changed source-protection
metadata and deployment paths, not feature assertions. The final private bundle
was restored and byte-verified after collection closed. This is a documented
plaintext-sequestration procedure, not proof of complete operating-system
isolation.

## Timing and strict assessment

Timing begins after identical public-source copying and Git-baseline creation,
before registration, indexing, eligibility planning or verification. It ends
after native process-group cleanup. All M preparation, fresh eligible public
checks, generated-file cleanup and installed-launcher work are included.
Grading, environment acquisition, source/Git copying and evidence packaging are
excluded. Setup has a 90-second allowance; native execution has a separate
600-second allowance from the recorded bridge handoff. Native wall time is a
local process measurement, not isolated remote inference latency.

Environment profiles and developer instructions were shared. Projects and
run-local caches were fresh; OS page caches, provider prefix caches and backend
load were uncontrolled. Allocation order was retained across amendments, but
interruptions and clock-time effects cannot be removed by reversing order.

After closure, each final source tree was reconstructed without reusing
model-generated caches. Public and private checks ran with candidate source
read-only, network disabled and bounded artifact write roots. Raw hashes,
source-role adjudication, native adjudication and version 3 grading metadata
are bound to every result. Strict success requires valid execution and usage,
correct treatment, intact hard protections, valid unchanged-source grading and
passing original public plus feature checks. A valid public coding failure can
conclude strict failure without running private tests. Failures retain their
observed cost and time; unknown values are never filled with zero. All 128
pooled records must satisfy integrity and grading prerequisites before the
primary inference is eligible.

## Accounting and analysis

For each task and arm, the two repeats are averaged first. The analysis uses the
28 paired task differences M minus A for two primary endpoints: uniform
API-equivalent dollars and full workflow seconds. The dollar convention is
[(input minus cached input) × 5 + cached input × 0.20 + output × 15] / 1,000,000.
These are native-reported cumulative token counters under a fixed historical
tariff, not current prices, subscription charges or actual billing.

Each endpoint receives a paired Student t test with 27 degrees of freedom,
one-sided alternative M minus A below zero and alpha 0.025, together with a
pointwise 95% two-sided t interval. The joint efficiency claim requires both
tests to pass, both upper interval endpoints below zero, complete primary
metrics, all 128 integrity/grade gates and M's strict-success count at least A's
among 56 sessions per arm. This intersection-union rule tests a single claim
of simultaneous cost and speed superiority; one favorable endpoint cannot
replace the other. Equal observed pass counts are a quality-count guard, not
a noninferiority or equivalence test.

Intervals and tests are nominal model-based summaries. Their finite-sample
calibration assumes independent, normally distributed task differences;
repeats do not increase the independent cluster count above 28. Pointwise
10,000-resample task-bootstrap intervals, distribution/influence diagnostics,
workflow components and jointly successful timing are secondary. A further
secondary summary omits the entire four-session task cluster containing any
certified retry warning, symmetrically across arms and repeats. It cannot
change the primary decision. Soft known-tariff allowances and admission
reserves controlled further dispatch, not actual account charges. The old
0016 unknown usage prevents a complete 144-assignment cost claim even though
all 112 primary and all 128 pooled comparison records have complete uniform
accounting. The [public result package](https://github.com/iamsreecharan/Memglide/blob/main/research/results/router-v7-20261021/README.md)
contains the portable export and reproduction instructions.
