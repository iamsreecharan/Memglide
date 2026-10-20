# Research and evidence

Memglide is a repository-context system around an existing coding agent. The
experiments change source selection and the information supplied to Codex;
they do not train or modify the model's weights.

## Paper and downloads

**Memglide: Auditable, Bounded Repository Context for Coding Agents**

Sree Charan Reddy Kailasam · srcharan014@gmail.com

The manuscript is a research draft for author review, with AI assistance
disclosed. It has not been accepted by a publication or independently replicated.

- [Paper and supplement ZIP](https://github.com/iamsreecharan/Memglide/raw/525f92d5ed63dcffbe0c6164fe951117f854dfdd/downloads/memglide-research-20261020/Memglide-paper-and-supplement.zip)
- [Complete research ZIP, 125,307,729 bytes](https://github.com/iamsreecharan/Memglide/raw/525f92d5ed63dcffbe0c6164fe951117f854dfdd/downloads/memglide-research-20261020/Memglide-complete-research.zip)
- [Download directory and verification notes](https://github.com/iamsreecharan/Memglide/tree/525f92d5ed63dcffbe0c6164fe951117f854dfdd/downloads/memglide-research-20261020)

Complete ZIP SHA-256:

```text
51e030257f7d07cda71f851a3e45fb136ec99a18408bb93bf77823fbae6eda6f
```

The complete ZIP contains the manuscript, supplement, source/build materials,
final evidence capsule, raw observations, grading controls and retained earlier
study archives. The published download was fetched again and its hash checked.
Use the capsule's verification instructions to inspect the evidence. These are
fixed artifacts; a later source checkout is not the frozen study environment.

## What the latest comparison found

The installed-system study used 12 author-designed coding tasks, three
conditions and two repeats: 72 native Codex runs with recorded usage. It used
`gpt-6.1-sol` at low reasoning effort through Codex 0.159.2.

| Condition | Strict task assessments passed | Mean fixed-tariff-equivalent cost | Mean workflow time |
| --- | ---: | ---: | ---: |
| Codex pass-through | 24 / 24 | $0.13255 | 40.56 s |
| Selected source | 24 / 24 | $0.12717 | 39.00 s |
| Selected source + verified commands | 24 / 24 | $0.11440 | 40.03 s |

The command-context condition's observed mean was **13.69% lower** than
pass-through and **10.04% lower** than source alone. Neither prespecified cost
comparison rejected after Holm adjustment; both adjusted p-values were 0.1481.
The study therefore provides a panel-specific estimate, not established savings.
It did not establish a workflow speed advantage. Passing these finite checks
does not establish correctness beyond the tested tasks.

Cost is a common accounting convention applied to recorded uncached input, cached input
and output tokens: $5, $0.20 and $15 per million respectively. It is not an
invoice or a claim about a current provider price. Fresh command verification
is included in the workflow time. Seven tasks activated source preparation;
five abstained and passed the task through. All twelve remain in the analysis.

The supplement reports uncertainty, paired comparisons, controls, exclusions
and study boundaries. A stronger savings claim needs a new, adequately powered
comparison on independent tasks; the existing outcomes should remain unchanged.

## Earlier studies and failures

The project tried interactive MCP, focused source delivery, automatic routing,
cache formats, memory and verified command context. Some attempts failed
connectivity or selection gates. The earlier 30-round development search is
exploratory and is not pooled with the final comparison.

The active source tree keeps runnable harnesses and fixed inputs rather than
thousands of generated run files. Original records remain available:

- [All historical benchmark files at the last pre-cleanup main commit](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks)
- [Historical raw evidence](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks/evidence)
- [Frozen v4 assessment, including failed gates](https://github.com/iamsreecharan/Memglide/blob/8acc8af/benchmarks/router-v4-assessment.md)
- [Historical development and validation log](../docs/archive/PROGRESS.md)
- [Benchmark runners and preserved inputs](../benchmarks/README.md)

The latest complete ZIP preserves the paper study and its included predecessors.
It does **not** replace every old unpacked file: the immutable Git history above
is the recovery source for the older tracked evidence. No history was rewritten.

## Reproduction boundaries

Indexing and local harness tests need no model account. Native comparisons need
an installed, authenticated Codex client, working provider access and available
account usage. They can consume paid usage. Run them in an appropriate execution
sandbox: coding tasks and explicit public-check verification execute project code.

Follow the final capsule's frozen protocol, manifests, tooling requirements and
checksums for that study. Do not substitute the current launcher and call it an
exact reproduction. Historical runners remain for inspection and controlled
reruns; their defaults may refer to archived reports. Recover those files from
the linked commit when reproducing an older study.
