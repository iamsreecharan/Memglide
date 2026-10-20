# Documentation

Start with installation and usage. Integration guides describe the supported
commands; versioned design notes retain earlier experiments and their limits.

## Getting started

| Guide | What it covers |
| --- | --- |
| [Installation](installation.md) | Dependencies, platform setup, dashboard build and local wheels. |
| [Usage](usage.md) | Project approval, sessions, source search and context retrieval. |
| [Troubleshooting](troubleshooting.md) | Diagnostics, state paths and integration problems. |
| [Known limitations](limitations.md) | Source coverage, freshness, estimates and memory boundaries. |
| [Security](../SECURITY.md) | Local service, untrusted source and reporting vulnerabilities. |

## Integrations

| Guide | What it covers |
| --- | --- |
| [MCP and Codex](mcp.md) | STDIO setup, tools, connection checks and the compact project-bound profile. |
| [Focused Codex launcher](preload.md) | Complete source from caller-selected paths before a native task. |
| [Bounded source routing v4](bounded-source-routing.md) | Explicit automatic discovery, limits and abstention. |
| [Verified command context](verified-command-context.md) | Authorized public checks, pinned receipts and the optional command/count card. |
| [Memory preparation](memory-preload.md) | Explicit source-backed findings from a still-active session. |

Automatic discovery policies and command context are opt-in. The latest
installed-system results are in the [research overview](../research/README.md).
Some guides retain the evaluation status at the time they were written; their
older measurements or pending-study wording do not replace the latest study.

## Architecture and implementation notes

- [Architecture and storage](architecture.md): service paths, indexing and local state.
- [Focused preparation architecture](daily-architecture.md): known-path source delivery.
- [Source-only refinement](source-only-refinement.md): profile settings and bounded local preparation.
- [Source delivery and workflow design](efficiency-architecture.md): the earlier workflow intervention.
- [Local efficiency design](product-efficiency-architecture.md): component work and proposed product boundaries.
- [Design decisions](decisions.md): recorded implementation choices.

The native prelaunch path and interactive MCP/API path have different behavior.
Read each guide's scope before applying its measurements to another path.

## Earlier designs and experiments

These notes explain versioned policies and proposals. Their version labels are
not a recommendation to enable a policy or a claim of improved coding results.

- [Automatic source preparation v1](automatic-source.md)
- [Task-aware routing v2](task-aware-router.md)
- [Runtime-aware routing v3](runtime-aware-routing.md)
- [Experimental Python excerpts](source-excerpts.md)
- [V2 evaluation proposal — plan only](v2.md)

## Research and project history

- [Research overview, paper and evidence](../research/README.md)
- [Original implementation plan](archive/IMPLEMENTATION_PLAN.md)
- [Historical progress and validation log](archive/PROGRESS.md)
- [Contribution workflow](../CONTRIBUTING.md)

Historical reports preserve failed attempts, superseded designs and their
original source versions. They are context for the project, not installation
instructions or new independent evaluations.
