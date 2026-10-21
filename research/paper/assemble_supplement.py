"""Assemble the v7 supplement from the public task catalog; no model calls."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results" / "router-v7-20261021"

INTRO = r'''---
title: "Memglide: Cost and Latency Evaluation — Supplementary Material"
abstract: |
  This supplement documents the amended fixed-panel comparison of pass-through
  Codex and Memglide: 28 primary tasks, two methods and two repetitions, or
  112 sessions. It separates 16 auxiliary sessions on eight exposed tasks,
  retains the study amendments and strict failures, and reproduces the public
  task prompts and repository commitments. All monetary values are measured
  token-price equivalents, not account invoices.
---

# Scope and cohort accounting

The main paper reports 112 primary sessions, not the earlier 72-session,
three-arm study. The original v7 allocation covered 36 tasks and 144 unique
assignments. Its first 15 model sessions exposed eight tasks; assignment 0016
failed before the native bridge. The 28 other tasks form the fixed primary
panel, with both methods repeated twice. The remaining two sessions per
exposed task contribute 16 descriptive records. The final 128-record pool
therefore covers 36 tasks with unequal repeat coverage and is not pooled
with earlier model outcomes.

The primary panel comprises 15 Python and 13 JavaScript/TypeScript tasks.
These author-designed features on small public libraries are a purposive panel,
not a random sample of maintenance issues or evidence that the model never saw
the repositories in training. Public readiness and task-informed engineering
preceded collection. Unlike SWE-bench, the panel does not consist of real
GitHub issue-to-patch tasks [@jimenez2024swebench]. The term primary does not imply a fully prospective
confirmation after the later amendments.

# Candidate and treatment

The evaluated implementation is commit `3c3f82b68778f6fb156394594bef3d6ec7118023`.
A uses its installed off/pass-through path. M uses bounded v4 discovery with
the opt-in commands-first workflow. Among the 28 primary tasks, six receive
source plus command context, nine receive commands only, and thirteen pass
through. With two repetitions, these correspond to 12, 18 and 26 M sessions.
Every primary task remains in the analysis. The modes are policy outcomes,
not randomized component arms, and cannot identify separate source or command
effects. There is no auxiliary model call or model-weight training.

Both methods request the `gpt-6.1-sol` alias, low reasoning effort and default
service tier through Codex CLI 0.159.2. The CLI version does not identify a
frozen provider backend snapshot. A fresh local project, thread and run state
are used for each coding session. Provider prefix caches, OS page caches,
provider load and backend changes are uncontrolled.

# Amendments and preserved failures

After 25 primary measurements, a baseline production-role audit corrected five
paths that an overly broad rule had treated as protected test/build material:
`u10:src/click/testing.py`, `u32:lib/defu.cjs`, `u32:lib/defu.d.cts`,
`u34:lib/index.cjs` and `u35:utils.d.ts`. The audit used baseline source and
public metadata across all 36 tasks. It did not inspect candidate patches,
feature-grade outcomes or resource contrasts to choose exceptions. The trigger
was an observed stop, so this is not a pre-outcome protocol correction.
Original raw flags remain intact, and the same exact-path rule is applied to
all pooled records. Feature-oracle assertions were not relaxed.

After 52 measurements, a strict parser stopped on a reconnect warning despite
a completed turn. Source inspection of CLI commit
`ff6aec96948b70d94983af2641a6b67c94faeff5` established a narrow recoverable retry
grammar. The adapter requires one fresh completed thread/turn, complete matching
native counters, valid identity, exit status and final capture. It applies to
all records and preserves raw events and prior verdicts. Arbitrary errors and
unfinished turns remain invalid. Completed-thread cumulative usage does not
establish the provider's request count or independently billed retry charges.

An additional slot-0069 launcher attempt failed because a local schema file was
missing. Source evidence places that exit before model-turn creation. Its raw
usage remains null; a separate operational ledger records the source-proven
zero model-generation requests. The canonical assignment ran after deployment
repair. A descriptive sensitivity adds the entire 2.637254565-second startup
duration to that M session, increasing the observed workflow slowdown to
approximately 1.25%. Diagnosis and repair labor are excluded and unmeasured.

Original stopped protocol decisions remain stopped. No measured coding trial
was retried, discarded or repaired to change its score, and no additional
repetitions were scheduled to obtain significance. Product source and the
fixed primary cohort were unchanged during primary collection. These
amendments nevertheless require nominal, model-based interpretation rather
than a retrospective prospective-confirmation claim.

# Measurement, grading and interpretation

Full-workflow timing begins after common source copying and Git-baseline
construction but before registration, indexing, eligibility planning and
verification; it ends after native process cleanup. Fresh eligible public
verification, preparation and generated-file cleanup count toward M's time.
Environment acquisition, source copying, private grading, packaging and
operator diagnosis are excluded. Native execution alone is not full-workflow
latency or isolated provider inference time.

The fixed API-equivalent accounting convention is

\[
C=(5(I-K)+0.20K+15O)/10^6,
\]

where I is total reported input tokens, K is cached input tokens and O is output
tokens, including the reported output category used in the native counters.
Reasoning output is not charged again. This convention measures resources
using a common tariff, not a provider invoice or a current-price guarantee.
Per-record tokens are cumulative across the coding agent's model steps.

Private grader/reference/control plaintext was sequestered during collection
and restored and verified after native closure. Candidate source was
reconstructed for grading without reusing model-created caches. Strict success
requires execution/treatment integrity, intact protections and passing original
public and private feature checks. All 128 comparison records have valid
measurements and grading; 124 strictly pass, 62/64 in each method. The primary
counts are 54/56 per method. Equality of observed counts does not establish
quality equivalence, noninferiority or correctness beyond finite checks.

All four strict failures are u21, in both methods and both repetitions. Each
passes 111 original public tests and 26/30 private feature checks. The private
oracle expects TypeError for `safeInteger` values null, 1, 'yes' and an object;
the implementations return false. The exact public instruction says “reject
nonboolean safeInteger values” without explicitly requiring an exception.
This task–oracle ambiguity limits interpretation. All four frozen failures
are retained without a post hoc rescore.

For each primary task, both repetitions are averaged within each method before
forming M-minus-A differences. The primary analysis uses 28 paired task means
and 27 degrees of freedom. Joint superiority requires both one-sided tests at
alpha 0.025, both corresponding 95% interval upper limits below zero, complete
integrity and at least as many observed strict successes with M. Neither
resource test passes. A 10,000-replicate task-cluster bootstrap, seed 20261102,
is a descriptive sensitivity and cannot replace the primary decision rule.
Omitting the whole task affected by the recovered retry is also descriptive.

The mean API equivalents are $0.16094230 and $0.15316045 per session; the
observed reduction is 4.83518%. The paired difference is -$0.00778185 with nominal
95% interval [-$0.02524202, $0.00967832] and one-sided p=0.184279. Full-workflow
means are 59.59018 and 60.28628 seconds; the difference is +0.69610 seconds,
interval [-3.02400, 4.41620], p=0.647984. Neither reliable savings nor faster
completion is established by this panel.

# Public artifact and reproduction boundaries

The portable results directory contains primary and auxiliary numeric rows,
paired task means, public task provenance, protocol information, hashes and a
standalone reproduction script. Its README gives the exact command and pinned
SciPy/NumPy versions. Recomputing statistics and figures requires no native
coding-model request. Every public export has its own hash; sanitizing runtime
paths does not preserve an original private artifact's byte identity.

The original final analysis commitment is
`fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26`.
The independent automated audit matched the original 128 source/grade bindings
and all 28 paired task calculations. This is a computational crosscheck, not
independent human replication. The new public numeric export does not include
complete native transcripts or private graders; it supports arithmetic
reproduction rather than complete public replay of the evaluation.

The complete ZIP retains the prior v6 capsule under `historical-v6/` with its
old files and checksums. That older capsule describes the separate 12-task,
72-session three-arm study and its development history, including the
30-round exploratory search. Its protocols, arms and exact/Holm tests must not
be substituted for the present paired-t analysis. Installed dependencies,
authentication and the provider backend are not packaged as an execution image.

# Public task inventory

The following prompts are reproduced from the frozen public input catalog.
Commit identifiers pin public source; obtaining and installing the separately
declared tools is required for a new native replication. Public commands and
environment templates are in `public-task-catalog.json`; the inventory below
reports their expected behavioral-test counts, not counts of all feature
requirements. Exposed tasks appear for complete accounting, not as additional
primary independent clusters. No code in a task prompt is an instruction to
the reader or to this document's build process.
'''


def main() -> None:
    catalog = json.loads((RESULTS / "public-task-catalog.json").read_text())
    tasks = catalog["tasks"]
    assert len(tasks) == 36
    assert sum(task["primary"] for task in tasks) == 28
    pieces = [INTRO]
    for task in tasks:
        cohort = "Primary (four sessions)" if task["primary"] else "Exposed auxiliary (two remaining sessions)"
        repo = task["repository"]
        pieces.append(f"\n## {task['task_id']}: {repo.rstrip('/').split('/')[-1]}\n\n")
        pieces.append(f"Repository: <{repo}>. Language: {task['language']}. {cohort}.\n\n")
        pieces.append(f"Pinned upstream commit: `{task['commit']}`.\n\n")
        pieces.append("Exact feature prompt:\n\n> " + task["prompt"].replace("\n", "\n> ") + "\n\n")
        for command in task["commands"]:
            pieces.append(
                f"- Public check `{command['name']}`: kind `{command['kind']}`, "
                f"expected test count {command.get('expected_tests', 'not supplied')}, "
                f"timeout {command.get('timeout_seconds', 'not supplied')} seconds.\n"
            )
    (HERE / "supplement.md").write_text("".join(pieces))
    print("Assembled v7 supplement: 36 public task contracts, 28 primary; no model calls.")


if __name__ == "__main__":
    main()
