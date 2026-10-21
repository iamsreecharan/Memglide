# Memglide: completed Codex comparison

128 sessions were collected and graded; 124 passed the frozen strict checks (62/64 in each arm). The main comparison uses 112 sessions: 28 tasks, two repetitions, and two methods. The remaining 16 sessions are descriptive because those tasks were previously exposed.

| Main-comparison metric | Codex | Codex + Memglide | Observed change |
|---|---:|---:|---:|
| API-equivalent USD per session | 0.16094230 | 0.15316045 | -4.84% |
| Full workflow seconds per session | 59.59018 | 60.28628 | +1.17% (slower) |
| Strict correctness | 54/56 | 54/56 | Equal observed counts |
| Input tokens, total | 7,341,887 | 6,681,908 | -8.99% |

Cost is computed from measured token counters at fixed prices of $5 per million uncached input tokens, $0.20 per million cached input tokens, and $15 per million output tokens. These are API-equivalent estimates, not actual subscription invoices. The primary cost totals were $9.0127690 and $8.5769854, a $0.4357836 equivalent difference over 56 sessions per method.

The paired task-level cost difference (Memglide minus Codex) is $-0.00778185 per session, with a nominal 95% confidence interval [$-0.02524202, +$0.00967832] and one-sided p=0.184279. The full-workflow difference is +0.69610 seconds, interval [-3.02400, +4.41620] seconds, p=0.647984. Neither superiority test passes; joint cost-and-latency superiority is not established.

The native Codex phase averaged 59.37133 seconds versus 57.31269 seconds. Its observed 2.05863-second decrease was offset by 2.75473 seconds of additional workflow overhead. Memglide indexing, verification, and launcher preparation are therefore concrete targets for future optimization; native-only timing is not the end-to-end result.

All four strict failures concern task u21 in both methods and both repetitions. All passed 111 public tests and 26/30 private checks. Four private checks expected TypeError for invalid safeInteger flags, while implementations returned false; the public request said reject without specifying an exception. The frozen strict grades remain unchanged.

Infrastructure corrections addressed launcher deployment, required schema presence, production-file classification, and source-verified recoverable transport warnings. Original artifacts and failed attempts are preserved. The final panel has complete token-price and workflow measurements. This is an amended fixed-panel analysis with nominal intervals, not a new fully prospective confirmation. The candidate, task set, endpoints, and stopping decisions were not changed to obtain a favorable result.

The independent audit matched all 128 record/grade provenance bindings and all primary task-paired calculations exactly. No additional model calls were used for grading or analysis.

Source analysis SHA-256: `fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26`.
