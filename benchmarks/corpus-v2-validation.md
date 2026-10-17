# Fresh 40-task corpus validation

This corpus contains **40 coding tasks**, twenty Python and twenty TypeScript,
across four new synthetic repositories. It does not rename the earlier Atlas
corpus or mirror every problem between languages. Every task starts with a real
behavioral defect, passes its unchanged visible smoke tests, and is solvable
without dependency downloads or network services.

| Repository | Tasks | Examples |
| --- | ---: | --- |
| `ledger-python-v2` | 10 | Atomic transfers, exact signed tax and per-unit discounts, timezone statements, quoted CSV import, reconciliation, audit hash chains |
| `workflow-python-v2` | 10 | Bounded async execution and cancellation, atomic pointer updates, deterministic dependency ordering, UTF-8 batching and streaming decoding |
| `stream-typescript-v2` | 10 | Fragmented NDJSON, event-time windows, transactional counters, simultaneous text edits, exact decimal parsing, escaped record decoding |
| `config-typescript-v2` | 10 | Redirect origin security, strict semantic versions, quoted environment values, repeated query parameters, route specificity, Unicode rollout hashing |

The public API and domain function are both graded. **Sixteen tasks contain
independent defects in both modules**: separate validation checks prove that a
domain-only fix and an adapter-only fix each still fail the behavioral oracle.
Tests exercise failure atomicity, error propagation, integer boundaries,
Unicode byte boundaries, deterministic ties, and defensive copies where relevant.

Validation passed **82 pytest tests**:

- Forty baseline/reference pairs: each baseline fails external behavioral
  grading (two cases) while all ten original smoke cases and TypeScript compilation pass; the
  corresponding reference passes both behavioral cases and all ten smoke cases.
- Thirty-two partial-fix checks independently require both halves of the sixteen
  coordinated changes.
- Four deterministic-generation checks and four protected-test tampering checks.
- Manifest and oracle-location validation.

There are eighty defined hidden cases and forty defined smoke cases. The ten
smoke cases for a repository repeat across its tasks; repeated execution does
not create additional distinct tests. These validation runs use reference code,
not Codex, and are excluded from actual A/B model outcomes.

Grading files stay outside model worktrees. Generated repositories contain only
production source, their visible smoke tests, README, AGENTS and build metadata;
there are no reference solutions, grading answers or task manifests inside them.
The separation is procedural, not a security boundary against host filesystem
access. The grader checks original non-source files byte for byte and runs fixed
commands rather than trusting repository-defined scripts.

Before freezing, an independent review hardened original ASCII currency checks,
strict JavaScript end-of-input handling, timezone input validation and final
unterminated CR preservation. A partial-fix validation caught a missing public
API assertion for falsy template values; the assertion was added before the
final passing suite. The first CLI draft also had a syntax error. Those draft
logs remain under validation history; they are not model runs.

No model pilot, retrieval ranking experiment or optimization selection used this
fresh corpus during development. The prior Atlas tasks are the development set.
These forty tasks are synthetic offline coding work, so results do not establish
performance on arbitrary production repositories or long-lived memory workflows.

Machine-readable validation and frozen source hashes are in
[corpus-v2-validation.json](corpus-v2-validation.json). Individual baseline and
reference grades, exact oracles, raw stdout/stderr and pytest history are under
[evidence/corpus-v2-validation](evidence/corpus-v2-validation/manifest.json).
