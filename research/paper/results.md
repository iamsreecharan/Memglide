# Results

The amended v7 comparison completed all 128 canonical records with valid
effective native telemetry, complete uniform accounting and valid deferred
grading. The primary panel contains 112 sessions on 28 tasks, with 56 sessions
per arm. Each arm passed 54 of 56 strict assessments. The full descriptive pool
passed 124 of 128 assessments, or 62 of 64 per arm. Its eight previously exposed
tasks contribute only their remaining second-repeat sessions; the primary
inference uses the 28 complete task clusters.

\begin{table}[tbp]
\centering
\caption{V7 primary panel: all 112 assigned attempts on 28 tasks. A is installed pass-through; M is the commands-first installed policy. Costs use the fixed uniform token tariff, not billing.}
\label{tab:v7-arm-means}
\begin{tabular}{lrrrr}
\toprule
Arm & Strict pass & Uniform USD & Workflow (s) & Native (s) \\
\midrule
A & 54/56 & 0.1609423 & 59.5902 & 59.3713 \\
M & 54/56 & 0.1531605 & 60.2863 & 57.3127 \\
\bottomrule
\end{tabular}
\end{table}

## Primary cost and latency

The primary uniform equivalents total USD 9.012769 for A and USD 8.5769854 for
M. The observed mean difference is −0.00778185 dollars per attempt, or 4.84%
lower for M. Mean workflow time is 59.5902 seconds for A and 60.2863 seconds for
M: an observed increase of 0.6961 seconds, or 1.17%. These are averages over all
assigned primary attempts, including the four strict-assessment failures.

\begin{table}[tbp]
\centering
\caption{V7 paired task-mean contrasts, M minus A; 28 clusters, 27 degrees of freedom. The joint rule requires both one-sided tests at alpha 0.025 and both upper interval endpoints below zero.}
\label{tab:v7-primary-contrasts}
\begin{tabular}{lrrrr}
\toprule
Endpoint & Mean difference & Change & Pointwise 95\% CI & One-sided $p$ \\
\midrule
Uniform USD & $-0.007782$ & $-4.84\%$ & [$-0.025242$, $+0.009678$] & 0.1843 \\
Workflow seconds & $+0.696101$ & $+1.17\%$ & [$-3.023997$, $+4.416199$] & 0.6480 \\
\bottomrule
\end{tabular}
\end{table}

Neither endpoint meets the declared superiority rule. Both nominal intervals
include zero, and joint cost-and-speed superiority is not established. The
cost estimate favors M, while the workflow point estimate favors A; the data
do not establish either a population cost reduction or a population slowdown.
The bootstrap sensitivity agrees about uncertainty: its cost interval is
[−0.023639, +0.009080] dollars and its workflow interval is [−2.796425, +4.170258]
seconds. It does not replace the primary t analysis.

## Coding outcomes and delivered context

All four strict failures are the two repeats in each arm on task u21
(`is-number`). Original public checks passed in all four cases. The private
feature oracle expected a TypeError for four nonboolean `safeInteger` options;
the submitted implementations returned false instead. The public request said
“reject nonboolean safeInteger values” without specifying an exception. The
frozen rubric therefore contains an ambiguity that limits interpretation of
these failures. Each implementation passed 111 upstream tests and 26 of 30
private checks; only the four TypeError assertions failed. All four remain
strict failures, with their measured costs and times retained. The u21 exception
assertions and these four strict outcomes were not changed or rescored.

M actually preloaded source on 12 primary sessions covering six tasks, supplied
command-only context on 18 sessions covering nine tasks, and passed through on
26 sessions covering thirteen tasks. A passed through on all 56. Captured
handoffs matched the committed treatment receipts. This mixed policy exposure
is part of the primary comparison. It does not identify a causal effect of
source alone, command cards alone or active retrieval alone. Both-repeat strict
success occurred on the same 27 of 28 tasks in each arm. Equal counts and zero
harmful task discordances do not establish quality equivalence; the descriptive
one-sided 97.5% harmful-discordance upper bound remains 12.34%.

## Native time, preparation and robustness

M's observed mean native wall time is 2.0586 seconds shorter than A's. Its total
workflow time nevertheless is longer. Workflow minus native time averages
2.9736 seconds for M and 0.2189 seconds for A. M's measured components include
1.4081 seconds of public verification, 0.2432 seconds of indexing and 0.8178
seconds of installed-launcher preparation per primary assignment; planning,
cleanup and other local work also belong to the workflow clock. This
decomposition describes where time was spent. It does not establish that any
individual preparation component caused a change in agent behavior.

The recorded reconnect warning occurred in A on task u26. Omitting that whole
four-session task cluster, as declared for descriptive robustness, leaves 27
tasks: observed uniform cost is 5.13% lower and workflow time 1.57% higher for M.
Both nominal paired intervals still include zero. The primary retains u26.
Charging the separate failed schema startup's full 2.6373 workflow seconds to
canonical u08-M changes the observed workflow increase to 1.25%, with an
interval of [−2.976951, +4.463340] seconds. Operator repair time was not measured.
Neither sensitivity changes the primary decision. Restricting timing to the
27 tasks passing both repeats in both arms also remains secondary and
outcome-conditioned.

Primary input counters average 131,105 tokens for A and 119,320 for M; output
averages 2,257 and 2,188 tokens. Cached input averages 110,091 and 99,221 tokens.
These are cumulative native counters, not unique source tokens or provider
computation. The alternate native-price/write scenarios remain incomplete for
one primary record in each arm and are not presented as complete comparative
costs. A separately implemented automated audit reproduced the complete pool,
primary estimates, intervals, grading counts and accounting from retained
records. It is an internal consistency check, not external replication.

The reported values come from the frozen assessment with SHA-256
`fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26`.
The portable [analysis summary](https://github.com/iamsreecharan/Memglide/blob/main/research/results/router-v7-20261021/analysis-summary.json)
and [result package](https://github.com/iamsreecharan/Memglide/blob/main/research/results/router-v7-20261021/README.md) are separate public
exports with their own hashes.
