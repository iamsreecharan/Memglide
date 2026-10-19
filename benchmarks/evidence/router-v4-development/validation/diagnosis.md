# Five v3 source-selection misses: independent diagnosis

This is a new post-study diagnosis. The original frozen v3 application, 96-run
report, tasks, grades, raw results and negative outcomes are unchanged. Its
report SHA-256 is
`e1e9ba4c55ab7c30ac1f847f92d98dd1fef085f69ed046f140fdef3a4a414c25`.
No new selector, index refresh or model request was made for this diagnosis.
The two parser diagnostics below are explicitly separate new observations.

| Miss | What the original observations establish | What remains unknown | Smallest safe repair candidate |
| --- | --- | --- | --- |
| **t01: byte-size formatting** | Both C repeats returned `runtime_language_unavailable` with six production candidates; B delivered the complete formatter and translation helper. The frozen guard rejects the entire batch if any candidate has an unsupported suffix. Stored index rows show only two unsupported production paths, both translation shell scripts. | Exact candidate identities/order were not recorded. At least one unsupported file triggered the guard, but neither which script nor its individual lexical strength is observed. The target's later runtime ranking was never tested. | Give the new policy a declared supported-language frontier. Classify coarse current evidence before AST inspection; discard unsupported competitors only when a sound necessary-condition check proves they cannot satisfy the policy. Possible or explicit unsupported evidence must still decline, with a frontier reason. |
| **t04: task-list rewriting** | Both repeats returned `candidate_limit_reached`, with the saturation flag true and zero production candidates recorded. The frozen code applies its 100-file return cap before production filtering. | The original 100 path identities and the test/doc/production mix are unavailable. A later 24-file evidence cap was not reached, so it is incorrect to label this an AST-cap failure. | Apply the new policy's supported-production scope before candidate/FTS output caps. Keep a bounded separately observed unsupported frontier; do not let excluded tests/docs consume the source selector's entire shortlist. Reaching the scoped cap must still abstain. |
| **t05: mathematics parsing** | Both repeats returned `evidence_candidate_limit` with 38 production candidates. The existing evidence validator accepts at most 24 and declines before source attestation. | Individual candidates and which could supply sufficient syntax evidence were not preserved. A 38-file pool does not prove 38 plausible implementations. No useful retained subset is established by the old run. | Add a separate bounded, current-source coarse stage for at most 100 files/2 MiB. Remove only candidates provably incapable of the exact later sufficiency/explicit-anchor rule. Keep the AST cap at 24; if more potentially sufficient candidates remain, decline. Guard every inspected coarse loser as well as every AST candidate. |
| **t10: filename extraction** | Both repeats returned `incomplete_index` before candidate generation; B delivered complete `src/utils.ts`. Stored project errors identify only nonproduction `test/index.spec.ts`, while `partial=false`. | The original receipt did not store error-node locations or establish semantic invalidity. It did not evaluate production filename ranking. | Permit only typed, complete, same-hash parse diagnostics for files outside the new selector's declared production scope. Preserve their warning and block unknown, truncated, scan/read, ignore-policy or relevant production structural failures. Do not broadly treat `partial=false` as a healthy index. |
| **t11: Windows drive normalization** | The same preselection index guard blocked both repeats; B delivered complete `src/_internal.ts`. This is a separate positive task and target, despite sharing the blocker with t10. | It is unknown from the original run whether the target would outrank unrelated modules after passing the index-health guard. | Use the same narrowly verified nonproduction parse-only exception, then apply the unchanged complete-source and current-hash checks. The exception alone is not proof of successful retrieval. |

## A more precise parser explanation, kept separate

`exposed-parser-diagnostic.json` parses only the already exposed, byte-frozen
14,009-byte test file in an isolated child with the installed Tree-sitter
0.25.2/TypeScript grammar 0.23.2. It reports `ERROR` spans at lines 106 and 404,
around `\undefined` and `\unc-path` in `String.raw` tagged templates.

`minimal-parser-controls.json` records two reviewer-owned syntax controls.
Node v24.19.0 `--check` accepts ``const path = String.raw`.\undefined`;`` but the
pinned grammar reports an error; both reject the corresponding untagged invalid
escape. These compile/parse checks execute neither program. They support a
specific pinned-grammar limitation on this tagged-template form, rather than a
claim that the upstream tests are invalid TypeScript. They do not modify or
replace any original benchmark observation and do not justify suppressing
arbitrary syntax errors or upgrading a grammar without regression checks.

## Independent review of the proposed v4 plan

The three proposed changes address the observed **stage boundaries** rather than
weakening the runtime ranker's threshold. Preserve source-only, v1/v2/v3 and all
defaults; make v4 explicit. Keep full source fidelity, the 24-file AST cap,
cumulative 2 MiB evidence, parser/node/time/output limits, bounded direct helpers
and all-or-nothing original-task fallback. A new 100-file coarse stage really can
read more files than v3; disclose and measure it rather than claiming the old
24-file total-read ceiling is unchanged.

The key proof obligation is that the coarse screen has **no false negatives
relative to the later syntactic rule**, not that it finds semantic relevance.
Comments, literals and irrelevant tokens may create false-positive survivors.
Names in clean headers, short or quoted/call/qualified explicit anchors,
Python AST NFKC-normalized identifiers, and synthesized syntax facts such as
varargs' `positional`/`keyword`/`argument` terms must not be screened out. A single
indexed winning declaration cannot stand for every actual current declaration.
Uncertain classification retains the candidate or declines; it never certifies
that an uninspected competitor is irrelevant.

`stats.errors` currently mixes parse errors with scan, read, ignore and resource
errors, stores at most 200 entries, and sets `partial` only from resource errors.
Therefore a safe parse-only exception needs positive typed/provenance evidence
and complete error accounting. Every exception must match the current same-hash
file's stored parse diagnostic outside the declared source scope. Unknown,
truncated or potentially relevant errors remain fail-closed. An unread ignore
file can change eligibility even when its own path is not production source.

## Required development/security controls

- Production-scoped generation with over 100 matching tests/docs, plus genuine
  supported-production saturation; old public search/test/doc workflows stay
  unchanged.
- A 25–100-file coarse pool with provably weak distractors, and an over-24 pool
  of genuinely potentially sufficient/ambiguous files that must still decline.
- Necessary-condition preservation against independent syntax examples: Unicode
  normalization, short/cased/quoted/call/qualified anchors, varargs facts,
  declaration-only tasks, comments/strings, mixed-language competitors and exact
  unsupported references. Do not use target labels as screen inputs.
- Typed nonproduction parse warnings may be bypassed; production parse failures,
  unknown/truncated errors, unread policies, read/scan faults and partial resource
  indexes must decline. Source/policy changes invalidate earlier exceptions.
- Changed, deleted, ignored, oversized, sensitive and symlinked **coarse losers**
  must invalidate the decision when they affected its candidate comparison.
  Keep approvals, policies and index/settings identities current at release.
- Cumulative bytes/file/row/node/time caps across phases, isolated trusted parser
  imports, bounded replies, exact complete-source ABI and exact fallback. More
  source reads and unsupported frontiers need truthful private diagnostics.

These repairs may expose further ranking or ambiguity misses. That is a valid
negative result. Do not rerun the exposed 96 observations and call them a fresh
holdout, retune on future labels, increase caps until a desired task succeeds,
remove competing files or weaken freshness. Develop general regressions, freeze
the revised policy, and only then author a new independent unfamiliar corpus.
Retain all original and new failures. If new inclusion **and** complete local
overhead justify it, a separately frozen, independently graded native comparison
can test successful-task cost; these diagnostics establish no Codex savings.
