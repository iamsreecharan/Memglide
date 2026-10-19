# Offline router-v3 evidence

The ledger hashes an explicit allowlist. Files are exact original evidence except
this generated guide. Logs and JSON retain original absolute paths. There are no
databases, worktrees, Git internals, environments, credentials or binary packages.
Historical evidence was not replaced. Model/coding outcomes are not measured.

Reproduction requires the application commit in freeze/policy-freeze.json and
`uv sync --frozen` in that checkout. Restore corpus/tasks.json to
benchmarks/tasks_automatic_v3.json, corpus/grading.json to
benchmarks/automatic-v3-grading.json, corpus/provenance.json to
benchmarks/automatic-v3-provenance.json and corpus/fixtures/ to
benchmarks/automatic-v3-fixtures/. Keep the archived originals unchanged.

Follow reproduction/benchmarks/automatic-v3-protocol.md, using new freeze, plan
and output directories. A new plan must reconstruct canonical Git roots and
fresh worktrees at current absolute paths; copying the old plan is insufficient.
Do not execute upstream repository source, hooks, builds, tests or packages.

Archived local helpers are evidence, not installed entry points. Restore the
collector to .local/router-v3/build_report.py in the checkout before invoking it.
Other audit/smoke helpers may also depend on their documented .local locations
or original absolute inputs. Adapt a new copy for reproduction and retain the
original bytes; do not expect helpers to work directly inside this archive.
Timestamps, absolute paths and timings are not expected to be byte-identical in
a new run. Compare verified source bytes and declared outcomes instead.

The post-study test-only corpus schema compatibility repair is archived as
reproduction/tests/test_benchmark_corpus_warm.py. It retains the freshness check
while accepting the declared list manifest. Use that validator for the final
mixed-schema full-suite verification; it is outside the unchanged frozen
production, runner and corpus seals. Original before-corpus/failed receipts are
preserved separately from the final complete-tree verification on both runtimes.

The collector only reads completed observations; it cannot start a model study.
Supply its independent formal-audit path and new evidence/report output paths.
The ledger deliberately excludes itself and the standalone assessment files to
avoid circular hashes. Post-hoc diagnostics, if present, remain separately
labeled and do not revise original outcomes or establish causal attribution.
