# Preserved source-only refinement evidence

The frozen implementation is Git `971c400e8dc1fe1f0ea8c5cf91c36fbf77d8a7d9`.
The comparison baseline is `391d86e64e53cf79d99824e1b5a63e4d70f0ae1b`.
Later documentation commits do not change the measured implementation. The
[assessment](../../source-only-refinement-assessment.md) includes every result,
negative timing observations and unavailable model telemetry.

- `profile/` contains all 78 original worker requests, results, stdout/stderr,
  the manifest and source snapshots. No worker was replaced or omitted.
- `validation/` records the complete Python, frontend, browser, installed-wheel,
  static/build and independent security results. Targeted reruns overlap the
  full Python suite and are not additional distinct tests.
- `audit/` contains the independent read-only reconstruction and its exact script.
- `history/` identifies the earlier source-only implementation and distinct
  historical native cohorts. Their reports and original outcomes remain unchanged.
- `development-unmatched/` retains confounded development probes; these do not
  enter the balanced comparison.
- `reproduction/` freezes the runner, protocol, tests, dependency locks and
  initial report collector as used. The guide is its pre-results version.

The ledger records exact copied bytes and original project-relative locations.
It intentionally excludes credentials, native-agent state, databases, fixture
repositories, installed environments, build binaries and dependency directories.

For a new local comparison, use the frozen implementation with the locked
runtime and follow `reproduction/benchmarks/source-only-refinement-protocol.md`.
Use a fresh output path; a new run is a distinct cohort, never a replacement
for these original observations. No native model calls are dispatched.

The archival scripts expect their original paths below the repository root.
To reconstruct the independent audit, restore `profile/` receipts under
`.local/source-only-refinement-balanced/` and `audit/audit_profile.py` under
`.local/source-only-refinement/` in an isolated copy of the frozen revision.
Run the script there; it checks the original HEAD and file seals and rebuilds
all statistics without running workers. Later HEADs intentionally fail that seal.
The initial collector similarly expects its original local receipt locations,
including `.local/known-path-audit/`. It refuses existing destinations.

The final assessment adds reviewed interpretation, independent-audit links and
scope corrections to the initial collector output; the archived collector is
preserved rather than retroactively edited to claim byte-identical regeneration.
Primary statistics can be reconstructed independently from the raw receipts.
