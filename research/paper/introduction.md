# Introduction

Coding agents must find the source and test commands needed for a change.
Providing that information in advance may reduce their work, but preparation
also costs time and adds to the prompt. The relevant question is whether the
complete workflow improves after selection, verification, prompt length, failed
attempts and preservation of existing behavior are counted. A compact source
bundle or shorter serialized response cannot settle that question.

Memglide is a local repository-context system with a native coding-agent
launcher. The launcher uses lexical and static syntax evidence to select
current source and delivers complete selected files within fixed limits. Its
opt-in `commands-first` workflow can supply verified public test commands and
observed baseline counts even when source selection abstains. Source selection
and command assistance therefore have separate activation conditions: an
ambiguous source target need not make current, verified commands unusable.
Preparation uses no auxiliary language model or embedding service. The external
coding model interprets the task, edits the code and runs checks.

Earlier experiments revealed gaps between a working context system and an
efficiency claim. Interactive MCP retrieval could increase tokens and elapsed
time. An automatic selector could abstain on most tasks, producing apparent
agent differences without evidence of a preload effect. A development-only
compiler configuration could change a score in a separate compatibility
diagnostic. A provider failure could leave token usage unknown. These findings
motivated a comparison of the installed system with explicit records of
activation, source protection, timing and missing data.

Development included a 30-round search over prompt and verification approaches
on three tasks and subsequent native comparisons. We retain those experiments
as exploratory evidence. The latest comparison evaluates pass-through Codex
against the installed `commands-first` candidate, with demand-driven public
verification. The primary cohort contains 28 tasks, each run twice per
condition, for 112 sessions. A further 16 sessions on previously exposed tasks
remain in the 128-session amended analysis. Private grading occurs after native
collection closes; reference implementations, oracles and revealing plaintext
logs are sequestered during collection.

The tasks are feature additions to small public libraries, designed with AI
assistance.
SWE-bench, by comparison, evaluates patches for real GitHub issues
[@jimenez2024swebench]. The primary cohort was fixed before its native sessions,
but collection required subsequent corrections to evaluation infrastructure.
These included identifying published production files that an edit-protection
rule had misclassified, and distinguishing completed-turn transport retries
from fatal failures. Original records, failures and amendments remain in the
evidence. The analysis is an amended fixed-panel comparison with nominal
inference, rather than an untouched prospective confirmation. Its purposive
task selection also limits generalization to other coding workloads.

On the 28-task primary cohort, Memglide's mean uniform API-price equivalent was
4.84% lower, while mean measured workflow time was 1.17% higher. Both conditions
passed the strict finite correctness checks in 54 of 56 sessions. The resource
intervals include zero, and the specified joint cost-and-time superiority
criterion was not met. The lower tariff point estimate does not establish
reliable savings; the timing result does not support a speedup. The tariff is
computed from native-reported tokens under a fixed rate schedule, not from
provider invoices.

We ask three questions. First, when does the installed policy deliver source,
verified commands, both or neither? Second, how do the conditions compare
under finite feature, original public-check and source-integrity requirements?
Third, how do native token-tariff equivalents and workflow time change when
fresh indexing and public baseline verification are included?

The contributions are an implementation that separates bounded source selection
from verified command assistance; an evaluation method that records activation,
functional outcomes, timing and telemetry provenance; and a development-to-
evaluation record that retains unsuccessful approaches and collection repairs.
The study evaluates context and workflow preparation around an existing model.
It does not train model weights, measure memory-reuse benefits or establish a
benchmark-leading coding agent.
