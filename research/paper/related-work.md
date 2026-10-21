# Related work

Repository context has been studied as both a retrieval problem and part of
code generation. RepoCoder combines a similarity retriever with a pretrained
code model in an iterative retrieval–generation pipeline
[@zhang-etal-2023-repocoder]. RepoBench evaluates retrieval, completion and a
combined pipeline, including cross-file dependencies [@liu2023repobench].
These settings separate the evidence a retriever returns from the result of
using it. Memglide evaluates functional patches with preserved public
regressions on small feature tasks, rather than code-completion similarity.

Context length alone gives an incomplete account of useful input. Liu et al.
varied the position of relevant information in multi-document question
answering and key–value retrieval. Performance often declined when relevant
information appeared in the middle of long contexts
[@liu-etal-2024-lost]. LLMLingua compresses prompts through a coarse-to-fine
method with token-level compression and model alignment
[@jiang-etal-2023-llmlingua]. Memglide uses lexical evidence and static syntax
analysis to construct bounded bundles of selected complete files. Preparation
makes no auxiliary model call and can abstain when selection or freshness
checks fail. The present study includes no performance comparison with these
approaches.

Agent design provides a second point of reference. SWE-agent studies an
agent–computer interface for automated software engineering
[@yang2024sweagent]. Agentless separates localization, repair and patch
validation [@agentless]. Memglide runs before the installed coding agent,
supplying source and optional verified-command context while leaving
investigation and editing to the agent. SWE-bench evaluates issue-to-patch
behavior on real GitHub issues [@jimenez2024swebench]. The present panel uses
author-designed extensions to public repositories. Its results describe an
installed-system comparison within that panel; they supply neither a SWE-bench
score nor a direct performance comparison with these systems.
