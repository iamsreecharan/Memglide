# Memglide: revised paper and results

**Memglide: Measuring the Cost and Latency of Bounded Repository Context for Coding Agents**

Sree Charan Reddy Kailasam · srcharan014@gmail.com

- [Revised paper](memglide-paper.pdf) · [editable manuscript](manuscript.md)
- [Revised supplement](memglide-supplement.pdf) · [supplement source](supplement.md)
- [Results, task catalog and offline reproduction](../results/router-v7-20261021/README.md)
- [Editorial status](publication-and-editorial-notes.md) · [typesetting](typesetting.md)
- [Supplied prior draft](history/author-supplied-prior-draft.pdf)

The main comparison contains 28 author-designed feature tasks, two methods and
two repeats: 112 real Codex sessions. Another 16 sessions on eight previously
exposed tasks remain descriptive. All 128 have valid measurements and grades;
124 pass the frozen strict checks (62/64 in each method).

| Main metric | Codex | Codex + Memglide | Observed change |
| --- | ---: | ---: | ---: |
| Fixed-price API equivalent/run | $0.16094 | $0.15316 | 4.84% lower |
| Complete workflow/run | 59.59 s | 60.29 s | 1.17% slower |
| Strict correctness | 54/56 | 54/56 | Same observed count |

Cost is measured tokens valued at fixed prices, not an account invoice. The
nominal 95% cost and time intervals both cross zero; neither superiority test
passes. Equal correctness counts do not establish equivalence. This is an
amended fixed-panel analysis after infrastructure/source-policy corrections,
not a fully prospective confirmation. The manuscript preserves these limits.

## Recompute and rebuild

The portable results README gives the exact offline statistics command and
pinned numerical dependencies. It needs no Codex authentication or model call.
With those dependencies, Matplotlib, Pandoc and the documented TeX packages:

```sh
python research/paper/assemble.py
python research/paper/assemble_supplement.py
python research/paper/create_figures.py
python research/paper/build.py
```

Section Markdown files are the editable manuscript sources. The assembler
writes `manuscript.md`; the build script generates TeX/PDF and a local receipt.
Only curated publication inputs and outputs are committed; build caches and
experiment authentication are excluded. The complete research ZIP includes
the current paper, supplement, portable results, source and the previous v6
capsule under `historical-v6/`, where its older scope remains explicit.

This is an AI-assisted preprint for author review. It has not been submitted,
accepted or independently replicated by a human research team.
