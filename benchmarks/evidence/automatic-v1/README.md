# Automatic-source v1 retained evidence

This directory retains the first frozen offline probe, final validation receipts,
available initial failures and post-hoc diagnostics. No native model study ran.
Source delivery was 9/12 for known-path B and 0/12 for automatic C. Automatic
promotion was rejected. See [the assessment](../../automatic-assessment.md).

`offline-preregistration.json` records the source hashes and then-current Git HEAD
used for this historical offline probe. Its sidecar hashes the exact JSON bytes.
It is **not approved for native execution**. Committing this implementation changes
Git HEAD and invalidates that historical plan for dispatch; generate a new plan
from the final committed checkout before any newly approved future experiment.
Do not spend on this unsuccessful router configuration without further offline
evidence and explicit budget approval.

`offline-report.json` contains every B/C preparation, selected versions, original
private evaluator labels, timings, byte counts and declines. Labels were consulted
only after C preparation. No reference fixes, grader answers or target paths were
provided to C. Post-hoc ranks are diagnostics, not successful deliveries.

Host-local fixture/worktree paths in receipts are provenance, not portable runtime
configuration. Databases, worktrees, `.git` directories, credentials and native
state are excluded. `installed_smoke.py` uses a private fake executable and real
local MCP/API clients; it does not contact a model.

The artifact ledger hashes original copied evidence. This README is explanatory
documentation; root assessment/validation JSON summarize the same observations.
