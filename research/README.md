# Research and evidence

Memglide changes repository context and workflow preparation around an existing
coding agent. It does not train or modify the coding model's weights.

## Revised paper and downloads

**Memglide: Measuring the Cost and Latency of Bounded Repository Context for Coding Agents**

Sree Charan Reddy Kailasam · srcharan014@gmail.com

- [Revised paper and supplement](paper/README.md)
- [Current results, task catalog and offline reproduction](results/router-v7-20261021/README.md)
- [Paper, supplement and current results ZIP](https://github.com/iamsreecharan/Memglide/raw/refs/heads/main/downloads/memglide-research-20261020/Memglide-paper-and-supplement.zip)
- [Complete replacement ZIP](https://github.com/iamsreecharan/Memglide/raw/refs/heads/main/downloads/memglide-research-20261020/Memglide-complete-research.zip)
- [Download manifest and checksums](../downloads/memglide-research-20261020/README.md)

The download path retains its earlier date for compatibility; the current
release replaces those files with the revised paper and v7 results. The complete
ZIP also retains the former v6 capsule under `historical-v6/`. The unchanged
[previous release](https://github.com/iamsreecharan/Memglide/tree/525f92d5ed63dcffbe0c6164fe951117f854dfdd/downloads/memglide-research-20261020)
remains accessible in Git history. No history is rewritten.

## Latest results

The main comparison uses 28 author-designed feature tasks, two methods and
two repetitions: 112 native sessions. Another 16 sessions on eight previously
exposed tasks remain descriptive. All 128 comparison records have valid usage
and grading; 124 strictly pass (62/64 per method).

| Main metric | Codex | Codex + Memglide | Observed change |
| --- | ---: | ---: | ---: |
| Fixed-price API equivalent per run | $0.16094 | $0.15316 | 4.84% lower |
| Complete workflow per run | 59.59 s | 60.29 s | 1.17% slower |
| Strict assessments passed | 54/56 | 54/56 | Same observed count |

Both paired nominal 95% intervals include zero: the cost difference interval is
[-$0.02524, +$0.00968] per run and the workflow interval is [-3.02, +4.42] seconds.
Neither resource-superiority test passes, and equal success counts do not
establish quality equivalence. This is an amended fixed-panel comparison, not
a fully prospective confirmation or proof of general savings.

The requested model alias was `gpt-6.1-sol`, low reasoning effort, through
Codex CLI 0.159.2. Cost uses reported tokens valued at fixed tariffs of $5,
$0.20 and $15 per million uncached input, cached input and output tokens.
It is not an invoice. Preparation, fresh eligible public verification and
cleanup are included in workflow time; grading and operator repair are not.
The paper records infrastructure amendments, uncontrolled caches, all four
strict failures on one ambiguous task and the inference limits.

## Earlier studies

The previous v6 study used twelve tasks, three arms and two repeats (72 sessions).
Its source-and-command arm had a 13.69% lower cost point estimate than
pass-through; neither Holm-adjusted exact comparison passed, and no workflow
speed advantage was established. These older findings and the 30-round
exploratory search are historical evidence, not additional independent
replications of v7. They are retained in the historical capsule and paper history.

Older records removed from the active source tree remain available:

- [Pre-cleanup benchmark history](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks)
- [Historical raw evidence](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks/evidence)
- [Earlier frozen v4 assessment](https://github.com/iamsreecharan/Memglide/blob/8acc8af/benchmarks/router-v4-assessment.md)
- [Development log](../docs/archive/PROGRESS.md)
- [Runnable harnesses and fixed inputs](../benchmarks/README.md)

## Reproduction and publication status

The current portable pack reproduces the reported statistics from exported
measurements with no model account. It is not a complete execution image or a
public release of the new private graders and native transcripts. Exact input
and source commitments, exclusions and reproduction boundaries are explicit.
A fresh native comparison requires separately authenticated Codex access,
appropriate execution isolation, declared dependencies and a new allocation.
Do not reopen sealed trials or substitute today's source for the evaluated
candidate and call it an exact replication.

The named manuscript is AI-assisted and prepared for author review. It has not
been submitted, accepted, peer reviewed or independently replicated by a human
research team. No archive DOI is claimed.
