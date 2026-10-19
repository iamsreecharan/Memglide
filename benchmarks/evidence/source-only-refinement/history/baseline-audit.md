# Source-only historical baseline audit

The existing source-only preparer already implements the architecture behind both favorable point estimates. Its historical SHA-256 is `9ae8595b4b5f97993dcf177d78d090db5f1e0f6fdb8ce2e2da5e3d766d69afac`; current bytes match both frozen cohorts: **True**. No whole-checkout rollback is needed.

| Evidence | Frozen revision | Strict scope | Source-only B versus A |
|---|---|---|---|
| Warm partial matched subset | `58ba0545187dbfb5270df246109bb81295718063` | 24 tasks per arm; 24/24 passed, one repeat; eight complete sequences chosen after stopping | 9.055% lower API-equivalent cost; 6.892% shorter mean instrumented time |
| Fresh source/support confirmation | `85ebff2229efd62be2e3c0e179c3c8eae0f0cade` | Eight focused tasks, two repeats; 16/16 passed per arm | 10.19% lower API-equivalent cost; 3.18% longer mean full time, median also longer |

Both used `gpt-6.1-sol`, low reasoning, requested Standard/default service and Codex 0.159.2. All native configurations disabled MCP, apps and web search and used fresh native state. Both supplied explicit source paths equally in the common task. B delivered complete current caller-selected files with compact-prefix JSON and no memory, automatic ranking or selector model.

Warm B called the production Python API from a persistent-per-sequence approved root with initial index and per-stage refresh; its time includes independent treatment auditing and excludes shared startup. Confirmation B used the actual compact-prefix launcher with cold approval/index, so its timing includes launcher startup. These are different workflows/corpora and must not be pooled or interpreted as successive architecture gains.

Across all ten confirmation tasks, including two supplied-context controls, B cost $0.0292192 per success versus A $0.0299606 (about 2.47% lower), with mean time 21.196 s versus 20.970 s. The 10.19% figure belongs only to the eight source-focused tasks; it is not an all-task saving.

The warm matched cost per strict success was $0.044824 for A and $0.040765 for B. Focused confirmation costs were $0.0312153 and $0.028035. Actual billing remains unavailable. Possible cache-write attribution permits B/A savings from -7.10% to +23.00% in warm and -3.54% to +22.49% in confirmation. These are scenarios, not confidence intervals. Input minus cached reads fell 10.81% and 13.49%, respectively, but actual write attribution and underlying model-call counts remain unknown.

The warm sample was stopped after 80 completed assignments; one interruption and 135 unrun assignments remain. Its post-hoc first-72 subset has five TypeScript and three Python sequences, not the full balanced two-repeat study. Confirmation is complete but small and synthetic; supplied-context controls remain separate. Its earlier 60 protected-test failures remain failures and their spend stays visible.

Preserve the approved-root read-only known-path route, complete live source, canonical compact prefix, private hashes, exact fallback and all security/freshness checks. Do not restore automatic memory/support/MCP overhead or remove current security corrections. The real launcher preserves user MCP registrations; the original benchmark's zero-MCP profile must be explicitly selected for reproduction rather than silently changing user setup.

The proposed refinement is narrower: reuse compiled ignore specifications within one request while still reading current policy/source and returning exactly the same normal prompt bytes. Compare local compile work, reader calls, CPU and preparation time before/after, with fidelity and security controls. No paid model benchmark is needed: identical model-visible prompts/settings cannot attribute token/cost differences to this local cache. Local gains must not be called new model savings.

This audit made zero model requests, authored no tasks, ran no heavy tests and edited no source. Detailed exact settings, counts, component paths and caveats are in `baseline-audit.json`.
