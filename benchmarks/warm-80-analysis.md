# Memglide: results after 80 completed coding assignments

**Source-only context has the better point result in the matched partial sample. Optional memory did not beat it.** All 80 completed assignments passed strict grading. The user requested a stop after 80 results; an already-started 81st assignment was interrupted and is retained, with 135 assignments unrun. This is a partial first-repeat study, not a completed 216-assignment benchmark or a basis for default promotion.

All dollar figures are **API list-price equivalents calculated from observed native usage**, not actual charges or subscription savings. The interrupted attempt has unknown whole-attempt usage and cost, so complete campaign cost and campaign cost per success remain unavailable.

[Detailed JSON with all 216 planned rows](warm-80-analysis.json) · [Unchanged generated report](warm-v2-initial-report.json) · [Final integrity audit](warm-v2-final-integrity-audit.json) · [Frozen protocol](warm-protocol.md)

## What was tested

- A: native Codex with bare tools and no Memglide source/memory context.
- B: the same model/settings with complete focused production source supplied by Memglide; no saved memory.
- C: identical focused source plus bounded, current source quotations actually produced by that arm’s earlier tasks. C retains one still-active Memglide session across fresh native Codex processes. This does not test reuse across new, ended or expired Memglide sessions.

The frozen design contains 12 three-task sequences, six Python and six TypeScript repositories, three arms and two repeats. Each task starts from the same canonical commit across arms; earlier agent patches never carry forward. All arms receive the same task, hints, test command and paid structured findings requirement. Independent behavior, test-preservation and treatment checks determine strict success. Model: `gpt-6.1-sol`, low reasoning, requested Standard tier. Native processes/state and arm/sequence databases are isolated. Provider and operating-system cache conditions remain uncontrolled.

## All observed attempts, including the interruption

| Arm | Strictly completed | User-interrupted | Unrun | Known completed point subtotal | All-attempt cost / strict success |
|---|---:|---:|---:|---:|---:|
| A | 27 | 0 | 45 | $1.1889952 | $0.0440369 |
| B | 27 | 0 | 45 | $1.0809684 | $0.0400359 |
| C | 26 | 1 | 45 | $1.1587256 | Unavailable |

The known subtotal for the 80 completed assignments is **$3.4286892**. It excludes an unknown amount for the interrupted 81st attempt and is not the complete campaign total. A/B have 27 completed tasks each; C has 26. Do not compare those unequal three-arm task mixtures as though they were a matched experiment.

The interrupted original is `warm-py-warm-pagination-s3-r1-C`. Its execution outcome, treatment completion and whole-attempt usage remain unknown; any partial native observations remain in the raw evidence. The interruption followed the user’s stop request. It is not evidence that C was unable to solve the task. None of the 80 completed solutions failed grading. Unrun rows are not model failures. The earlier authentication-blocked cohort is retained separately and is not pooled into these timings.

## Fair three-arm comparison: first 72 assignments

The following subset contains the first eight complete three-arm sequences in the frozen order: **24 unique coding tasks, eight repositories, 24 assignments per arm**, with five TypeScript and three Python sequences. Each arm passed all 24 tasks and all eight full sequences. This subset was selected **after the user stopped the run**, because all three arms completed it; it is a post-hoc descriptive analysis. It has one repeat and does not represent the full balanced language/corpus/two-repeat design.

| Arm | Estimated USD / successful task | Median task USD | Estimated USD / successful sequence | Mean full task seconds | Median full task seconds |
|---|---:|---:|---:|---:|---:|
| A | $0.044824 | $0.039290 | $0.134471 | 27.097 | 26.386 |
| B | $0.040765 | $0.040265 | $0.122295 | 25.230 | 25.169 |
| C | $0.045798 | $0.042522 | $0.137393 | 26.086 | 24.480 |

| Arm | Mean full sequence seconds | Median full sequence seconds | Mean native task seconds |
|---|---:|---:|---:|
| A | 81.291 | 80.367 | 27.011 |
| B | 75.689 | 75.861 | 24.923 |
| C | 78.259 | 78.303 | 25.492 |

- **B versus A:** 9.055% lower point estimated cost per success, 6.892% shorter mean full time and 5.606% shorter median full-sequence time. This is a favorable descriptive source-only result, with the limitations above.
- **C versus B:** 12.346% higher point estimated cost per success, 3.396% longer mean full time and 3.219% longer median full-sequence time. C’s median individual-task time was 2.739% shorter; the median sum of three tasks was longer. Those are different statistics, not a contradiction.
- **C versus A:** 2.173% higher point estimated cost per success, with 3.730% shorter mean full time. Memory does not show a joint cheaper-and-faster win in this sample.

Full timing is **instrumented**: it includes application setup, current-source checks, memory work, cleanup and independent treatment audits. Shared imports/harness startup, canonical resets and external grading are excluded. It is not isolated product latency. Native task time is shown separately.

## Tokens and the point cost difference

Cached input is already included in total input. Input minus cached input is shown separately; unknown cache-write attribution prevents treating that entire partition as verified ordinary-input billing. Output already includes reasoning.

| Arm | Total input | Cached input | Input − cached | Output | Point estimated total USD |
|---|---:|---:|---:|---:|---:|
| A | 1,439,744 | 1,050,112 | 389,632 | 19,149 | $1.0757652 |
| B | 1,339,767 | 992,256 | 347,511 | 18,411 | $0.9783576 |
| C | 1,400,892 | 995,328 | 405,564 | 18,848 | $1.0991408 |

At the pinned Standard rates, ordinary input is $2, cached input $0.10, cache-write input $2.50 and output $10 per million tokens. The point estimate uses the native-reported categories. Native-reported zero cache writes may be an upstream default; it does not establish zero billed writes. No bytes-to-token conversion is used.

| Matched C minus B point charge | USD |
|---|---:|
| Ordinary input under the native-reported write point | $0.1161060 |
| Cached input | $0.0003072 |
| Reported cache writes | $0.0000000 |
| Output | $0.0043700 |
| Total | $0.1207832 |

**96.13% of C’s extra point-estimated charge versus B comes from the uncached-input charge**, with a smaller output increase. This is an arithmetic decomposition of the observed categories, not proof of why the provider produced those traces. Extra memory context, repeated interactions and cache variability are plausible contributors; underlying inference-call counts and server cache state are unavailable.

Possible independent cache-write attribution gives these **saving ranges**, where positive means the candidate costs less:

| Candidate versus baseline | Point saving | Possible-write saving range |
|---|---:|---:|
| B versus A | +9.055% | -7.10% to +23.00% |
| C versus B | -12.346% | -33.07% to +4.60% |
| C versus A | -2.173% | -21.02% to +13.49% |

These are sensitivity scenarios, not confidence intervals or actual invoices. They permit a different price ranking. Actual billed-dollar savings remain unproven.

## Follow-up tasks and the cold control

| Stratum | Arm | Tasks | Point estimated subtotal USD | Mean full task seconds | Median full task seconds |
|---|---|---:|---:|---:|---:|
| Cold stage 1 | A | 8 | $0.3433152 | 27.463 | 27.246 |
| Cold stage 1 | B | 8 | $0.3389960 | 25.157 | 24.119 |
| Cold stage 1 | C | 8 | $0.3189840 | 27.346 | 27.979 |
| Follow-up stages 2–3 | A | 16 | $0.7324500 | 26.914 | 25.704 |
| Follow-up stages 2–3 | B | 16 | $0.6393616 | 25.266 | 25.169 |
| Follow-up stages 2–3 | C | 16 | $0.7801568 | 25.456 | 24.055 |

In the 16 follow-up tasks per arm, C cost 22.021% more by the point estimate than B. Input minus cached input rose from 225,644 to 295,694 tokens; output rose from 12,168 to 12,450. Mean full task time rose 0.755%, while median task time fell 4.427%. This mix does not establish a reliable memory improvement.

Cold stage-one B/C source prompts were byte-identical and had no prior memory. Their costs and times still differed: B cost $0.3389960 and C $0.3189840, while mean full times were 25.157 and 27.346 seconds. Thus every observed difference cannot be attributed to memory. Provider/cache variation, native execution and the small sample remain material.

## Memory behavior and resource observations

Across C’s 26 completed assignments, memory was delivered in **16 of the 17 completed follow-up tasks**; nine first tasks had no prior memory and one follow-up had no Current memory. The first-72 subset contains 15 deliveries. Capture produced 28 accepted quotation instances, including deduplicated recaptures; this is not 28 unique memories. All captured sources were current contract documents under `docs/decisions/`.

The changed-policy control excluded **two Stale candidates** at `py-warm-labels` stage three, passed through without memory and still passed the task. This is useful freshness evidence within the controlled fixture. It does not prove semantic completeness or safety for every repository. The offline audit found 24 additional source-reference instances, zero exact path/hash overlap with already supplied focus files and 3,696 delivered quote bytes. Bytes are not tokens. Absence of exact file overlap does not prove that every quote was relevant or eliminated work.

| Matched first-72 local measure | A | B | C |
|---|---:|---:|---:|
| Recognized read-command items, total | 33 | 27 | 35 |
| Repeated read-command items, total | 1 | 0 | 0 |
| Completed command items, total | 108 | 107 | 111 |
| Mean observed local CPU seconds | 23.662 | 20.983 | 22.199 |
| Mean sampled native-tree RSS, MiB | 281.84 | 269.64 | 279.70 |

C did not eliminate investigation work: it had 35 recognized read commands versus B’s 27, and 111 completed command items versus 107. Read-command counters are narrow lexical proxies, not actual file reads or model-call counts. CPU combines measured parent work with sampled native children and includes instrumentation; RSS covers the sampled native process tree, excludes parent preparation memory and can double-count shared pages. Neither isolates Memglide’s CPU/RSS or measures provider resources.

All 80 completed assignments recorded zero native MCP calls, with zero MCP servers configured. They used production Python preparation services in the harness. This evaluates source/memory preloading, not model efficiency through MCP. The interrupted attempt has incomplete runtime telemetry. Actual provider inference-call counts remain unknown.

## Integrity and engineering verification

The final offline integrity audit passed **2,595 checks**, with **18 unavailable checks** and incomplete study coverage. The original audit’s seven flags are retained: its interrupted-attempt handling had treated terminal-looking raw events as verified whole-attempt usage. The report’s original estimator already kept that attempt unknown. The auditor was corrected and regression-tested; no original coding run was retried, replaced or regraded to change its outcome.

The application source remained unchanged during the native cohort. Engineering evidence separately records a complete 1,626-case Python suite, with later recovery/accounting regressions tested separately, 24 frontend cases, three real Chromium cases and clean installed CLI/API/SPA/default-and-agent MCP checks. Overlapping targeted runs are not additional distinct tests, and a full enlarged-suite run is not claimed. See the [validation record](saas-efficiency-validation.md).

## Next approach

1. **Keep source-only as the default.** It has the strongest descriptive point result here while preserving current-source checks. This partial sample does not prove universal savings.
2. **Make memory conditional on likely new, task-relevant evidence.** Use bounded local checks for current versions, topic/path overlap and already supplied evidence. Omit stale, duplicate and clearly unrelated claims without an extra selector-model call. Unknown relevance should retain normal source discovery. The current implementation checks freshness; it does not establish usefulness for the next task.
3. **Reduce the memory envelope and repeated policy fragments.** Evaluate one compact source/provenance reference per document and consolidate overlapping quotations without inventing summaries or losing required evidence. For small contracts, compare a complete bounded current document against several historical quote capsules. Neither fewer bytes nor fewer calls alone proves token or dollar savings.
4. **Require evidence that memory removes work.** Measure ordinary input, output, command/read proxies and full-sequence time. Do not ban necessary source reads, weaken source validation or suppress tests to force a win.
5. **Evaluate the next candidate in a fresh frozen cohort.** Complete both repeats on new held-out related tasks, with comparable cache conditions and independent grading. Include every attempt, setup/capture/readback/cleanup and cost per full successful sequence. Study larger unfamiliar repositories and genuine durable cross-session behavior separately.

These are next candidates, not changes claimed as shipped by this analysis. No new model run was launched for this report. The partial result supports keeping optional memory explicit; the predeclared promotion gate did not pass.

## Individual completed assignments and the interrupted original

All 135 unrun original identities remain in the JSON. Every completed assignment below passed strict grading; the interrupted row remains unknown.

| Run | Arm | Input | Cached | Output | Point USD | Full seconds | Memory |
|---|---|---:|---:|---:|---:|---:|---|
| warm-ts-warm-paths-s1-r1-C | C | 75,455 | 61,056 | 839 | $0.0432936 | 32.572 | no_prior_memory |
| warm-ts-warm-paths-s2-r1-C | C | 50,626 | 23,936 | 848 | $0.0642536 | 24.040 | explicit_memories |
| warm-ts-warm-paths-s3-r1-C | C | 65,099 | 37,120 | 707 | $0.0667400 | 22.816 | explicit_memories |
| warm-ts-warm-paths-s1-r1-B | B | 75,128 | 60,800 | 838 | $0.0431160 | 26.511 | no_prior_memory |
| warm-ts-warm-paths-s2-r1-B | B | 49,735 | 35,712 | 840 | $0.0400172 | 28.760 | no_prior_memory |
| warm-ts-warm-paths-s3-r1-B | B | 62,802 | 48,896 | 772 | $0.0404216 | 28.607 | no_prior_memory |
| warm-ts-warm-paths-s1-r1-A | A | 62,150 | 35,968 | 952 | $0.0654808 | 26.301 | no_prior_memory |
| warm-ts-warm-paths-s2-r1-A | A | 89,665 | 61,568 | 966 | $0.0720108 | 30.077 | no_prior_memory |
| warm-ts-warm-paths-s3-r1-A | A | 49,527 | 35,456 | 758 | $0.0392676 | 23.327 | no_prior_memory |
| warm-ts-warm-quota-s1-r1-B | B | 62,339 | 36,992 | 525 | $0.0596432 | 20.203 | no_prior_memory |
| warm-ts-warm-quota-s2-r1-B | B | 49,559 | 35,840 | 665 | $0.0376720 | 21.688 | no_prior_memory |
| warm-ts-warm-quota-s3-r1-B | B | 62,933 | 48,768 | 686 | $0.0400668 | 22.922 | no_prior_memory |
| warm-ts-warm-quota-s1-r1-C | C | 49,377 | 35,712 | 528 | $0.0361812 | 19.073 | no_prior_memory |
| warm-ts-warm-quota-s2-r1-C | C | 63,228 | 36,608 | 655 | $0.0634508 | 24.266 | explicit_memories |
| warm-ts-warm-quota-s3-r1-C | C | 52,033 | 37,632 | 704 | $0.0396052 | 20.777 | explicit_memories |
| warm-ts-warm-quota-s1-r1-A | A | 48,934 | 35,328 | 510 | $0.0358448 | 16.641 | no_prior_memory |
| warm-ts-warm-quota-s2-r1-A | A | 62,461 | 35,456 | 678 | $0.0643356 | 19.699 | no_prior_memory |
| warm-ts-warm-quota-s3-r1-A | A | 62,550 | 36,224 | 672 | $0.0629944 | 32.217 | no_prior_memory |
| warm-ts-warm-routing-s1-r1-A | A | 62,545 | 48,128 | 944 | $0.0430868 | 31.447 | no_prior_memory |
| warm-ts-warm-routing-s2-r1-A | A | 63,362 | 57,856 | 865 | $0.0254476 | 24.786 | no_prior_memory |
| warm-ts-warm-routing-s3-r1-A | A | 62,859 | 36,224 | 767 | $0.0645624 | 33.931 | no_prior_memory |
| warm-ts-warm-routing-s1-r1-C | C | 76,767 | 61,952 | 977 | $0.0455952 | 27.837 | no_prior_memory |
| warm-ts-warm-routing-s2-r1-C | C | 77,946 | 62,976 | 859 | $0.0448276 | 27.151 | explicit_memories |
| warm-ts-warm-routing-s3-r1-C | C | 65,083 | 50,432 | 738 | $0.0417252 | 23.867 | explicit_memories |
| warm-ts-warm-routing-s1-r1-B | B | 49,929 | 23,424 | 939 | $0.0647424 | 25.440 | no_prior_memory |
| warm-ts-warm-routing-s2-r1-B | B | 50,022 | 35,840 | 872 | $0.0406680 | 22.997 | no_prior_memory |
| warm-ts-warm-routing-s3-r1-B | B | 63,112 | 36,480 | 714 | $0.0640520 | 22.552 | no_prior_memory |
| warm-py-warm-labels-s1-r1-C | C | 49,825 | 35,712 | 962 | $0.0414172 | 29.210 | no_prior_memory |
| warm-py-warm-labels-s2-r1-C | C | 64,404 | 59,008 | 734 | $0.0240328 | 25.465 | explicit_memories |
| warm-py-warm-labels-s3-r1-C | C | 49,915 | 32,896 | 744 | $0.0447676 | 21.768 | no_current_memory |
| warm-py-warm-labels-s1-r1-B | B | 49,676 | 35,712 | 861 | $0.0401092 | 22.799 | no_prior_memory |
| warm-py-warm-labels-s2-r1-B | B | 49,642 | 44,672 | 673 | $0.0211372 | 21.222 | no_prior_memory |
| warm-py-warm-labels-s3-r1-B | B | 63,038 | 37,248 | 685 | $0.0621548 | 25.061 | no_prior_memory |
| warm-py-warm-labels-s1-r1-A | A | 62,679 | 54,528 | 978 | $0.0315348 | 35.065 | no_prior_memory |
| warm-py-warm-labels-s2-r1-A | A | 62,802 | 48,640 | 721 | $0.0403980 | 26.470 | no_prior_memory |
| warm-py-warm-labels-s3-r1-A | A | 49,636 | 35,584 | 699 | $0.0386524 | 24.939 | no_prior_memory |
| warm-ts-warm-headers-s1-r1-B | B | 49,591 | 23,424 | 758 | $0.0622564 | 28.417 | no_prior_memory |
| warm-ts-warm-headers-s2-r1-B | B | 63,370 | 49,024 | 915 | $0.0427444 | 28.326 | no_prior_memory |
| warm-ts-warm-headers-s3-r1-B | B | 49,761 | 35,840 | 655 | $0.0379760 | 25.277 | no_prior_memory |
| warm-ts-warm-headers-s1-r1-A | A | 62,162 | 57,088 | 740 | $0.0232568 | 25.586 | no_prior_memory |
| warm-ts-warm-headers-s2-r1-A | A | 63,524 | 35,584 | 1,064 | $0.0700784 | 30.855 | no_prior_memory |
| warm-ts-warm-headers-s3-r1-A | A | 49,695 | 35,712 | 681 | $0.0383472 | 21.384 | no_prior_memory |
| warm-ts-warm-headers-s1-r1-C | C | 61,918 | 35,968 | 681 | $0.0623068 | 25.654 | no_prior_memory |
| warm-ts-warm-headers-s2-r1-C | C | 64,933 | 36,352 | 1,073 | $0.0715272 | 32.145 | explicit_memories |
| warm-ts-warm-headers-s3-r1-C | C | 51,429 | 24,192 | 665 | $0.0635432 | 21.588 | explicit_memories |
| warm-py-warm-retries-s1-r1-B | B | 50,639 | 45,440 | 570 | $0.0206420 | 21.872 | no_prior_memory |
| warm-py-warm-retries-s2-r1-B | B | 49,501 | 35,712 | 672 | $0.0378692 | 22.796 | no_prior_memory |
| warm-py-warm-retries-s3-r1-B | B | 63,933 | 49,280 | 901 | $0.0432440 | 26.702 | no_prior_memory |
| warm-py-warm-retries-s1-r1-C | C | 49,803 | 41,856 | 626 | $0.0263396 | 22.483 | no_prior_memory |
| warm-py-warm-retries-s2-r1-C | C | 50,435 | 36,352 | 682 | $0.0386212 | 21.333 | explicit_memories |
| warm-py-warm-retries-s3-r1-C | C | 65,702 | 59,776 | 914 | $0.0269696 | 33.934 | explicit_memories |
| warm-py-warm-retries-s1-r1-A | A | 62,636 | 48,512 | 589 | $0.0389892 | 28.192 | no_prior_memory |
| warm-py-warm-retries-s2-r1-A | A | 62,526 | 57,472 | 693 | $0.0227852 | 24.499 | no_prior_memory |
| warm-py-warm-retries-s3-r1-A | A | 63,853 | 45,824 | 990 | $0.0505404 | 28.338 | no_prior_memory |
| warm-py-warm-priority-s1-r1-A | A | 62,092 | 48,256 | 612 | $0.0386176 | 24.606 | no_prior_memory |
| warm-py-warm-priority-s2-r1-A | A | 49,536 | 35,584 | 785 | $0.0393124 | 24.399 | no_prior_memory |
| warm-py-warm-priority-s3-r1-A | A | 49,622 | 32,256 | 932 | $0.0472776 | 27.279 | no_prior_memory |
| warm-py-warm-priority-s1-r1-C | C | 49,703 | 35,712 | 760 | $0.0391532 | 28.122 | no_prior_memory |
| warm-py-warm-priority-s2-r1-C | C | 64,153 | 49,792 | 805 | $0.0417512 | 23.682 | explicit_memories |
| warm-py-warm-priority-s3-r1-C | C | 51,817 | 37,120 | 845 | $0.0415560 | 24.069 | explicit_memories |
| warm-py-warm-priority-s1-r1-B | B | 49,564 | 44,672 | 716 | $0.0214112 | 22.136 | no_prior_memory |
| warm-py-warm-priority-s2-r1-B | B | 49,886 | 44,672 | 863 | $0.0235252 | 27.674 | no_prior_memory |
| warm-py-warm-priority-s3-r1-B | B | 49,700 | 44,672 | 823 | $0.0227532 | 30.544 | no_prior_memory |
| warm-ts-warm-clocks-s1-r1-C | C | 49,662 | 44,672 | 1,025 | $0.0246972 | 33.820 | no_prior_memory |
| warm-ts-warm-clocks-s2-r1-C | C | 50,463 | 33,664 | 704 | $0.0440044 | 24.694 | explicit_memories |
| warm-ts-warm-clocks-s3-r1-C | C | 51,116 | 24,832 | 773 | $0.0627812 | 35.708 | explicit_memories |
| warm-ts-warm-clocks-s1-r1-A | A | 63,063 | 36,864 | 1,042 | $0.0665044 | 31.865 | no_prior_memory |
| warm-ts-warm-clocks-s2-r1-A | A | 49,420 | 41,984 | 732 | $0.0263904 | 23.403 | no_prior_memory |
| warm-ts-warm-clocks-s3-r1-A | A | 62,445 | 54,016 | 779 | $0.0300496 | 35.024 | no_prior_memory |
| warm-ts-warm-clocks-s1-r1-B | B | 63,321 | 57,856 | 1,036 | $0.0270756 | 33.880 | no_prior_memory |
| warm-ts-warm-clocks-s2-r1-B | B | 49,557 | 32,384 | 641 | $0.0439944 | 22.239 | no_prior_memory |
| warm-ts-warm-clocks-s3-r1-B | B | 63,029 | 48,896 | 791 | $0.0410656 | 26.884 | no_prior_memory |
| warm-py-warm-pagination-s1-r1-B | B | 49,820 | 32,384 | 763 | $0.0457404 | 26.407 | no_prior_memory |
| warm-py-warm-pagination-s2-r1-B | B | 49,343 | 35,712 | 528 | $0.0361132 | 18.255 | no_prior_memory |
| warm-py-warm-pagination-s3-r1-B | B | 49,557 | 44,672 | 652 | $0.0207572 | 20.635 | no_prior_memory |
| warm-py-warm-pagination-s1-r1-A | A | 49,353 | 35,456 | 672 | $0.0380596 | 21.575 | no_prior_memory |
| warm-py-warm-pagination-s2-r1-A | A | 49,228 | 35,456 | 595 | $0.0370396 | 22.111 | no_prior_memory |
| warm-py-warm-pagination-s3-r1-A | A | 49,287 | 35,328 | 668 | $0.0381308 | 22.986 | no_prior_memory |
| warm-py-warm-pagination-s1-r1-C | C | 49,529 | 44,672 | 683 | $0.0210112 | 27.648 | no_prior_memory |
| warm-py-warm-pagination-s2-r1-C | C | 63,601 | 49,536 | 549 | $0.0385736 | 24.306 | explicit_memories |
| warm-py-warm-pagination-s3-r1-C **interrupted** | C | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
