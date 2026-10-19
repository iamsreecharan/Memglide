# Open a worker with the published network configuration

Open [Codex](https://chatgpt.com/codex), start a **new cloud task**, and choose the
published Memglide environment for `iamsreecharan/Memglide` on `main`.

The latest configuration is published with `chatgpt.com`, `auth.openai.com`, and
`developers.openai.com`. The worker that prepared the v4 report still enforced
the earlier configuration. Its two bounded access checks failed at proxy HTTP
CONNECT 403; neither completed a model turn. Login status alone did not establish
usable authentication, and usage and charges remain unknown.

Suggested message for the new task:

> Read PROGRESS.md and benchmarks/router-v4-assessment.md. Verify that this worker
> uses the published Memglide environment and that the three required domains are
> present in its current enforced network policy. Check Codex login status without
> reading or printing credential files. If the network prerequisites are active,
> perform one bounded, separately recorded structured-output connectivity check.
> Preserve all previous evidence. Do not launch the v4 coding cohort: its fresh
> source-selection improvement gate failed. Any new candidate needs separate
> development tasks and a new frozen held-out evaluation.

Publishing a configuration does not migrate an unrelated running worker. If the
new task still has the older configuration, use the platform support path with
the version IDs and policy evidence in the assessment. The local network-policy
file is descriptive; editing it cannot grant access. Preserve the inherited
proxy and TLS verification.

Source-selection fidelity, source inclusion, coding correctness and model cost
are different measurements. The published report keeps them separate; a new
connection check does not turn the failed v4 selection experiment into evidence
of savings.
