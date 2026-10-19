# Source-only profile and local preparation refinement

Use the existing focused source launcher when the relevant files are known:

```sh
uv run memglide-codex --project PROJECT_ID --focus src/calculation.py \
  'Fix the rounding behavior and run the relevant tests.' -- \
  --model gpt-6.1-sol -c 'model_reasoning_effort="low"' \
  -c 'service_tier="default"' --json
```

The favorable historical studies used that model at low reasoning, requested
Standard/default service, complete known production source, the compact-prefix
format, no automatically selected support files, no task memory and zero
configured MCP servers. The launcher preserves native configuration; it does
not silently disable an existing MCP registration. To omit the standard
`memglide` MCP registration for one preload invocation, explicitly add
`-c 'mcp_servers.memglide.enabled=false'` after `--`. Other registered servers
and native preferences still apply. This is not an exact reproduction of the
isolated benchmark unless all its settings match.

Approve and index the repository once with the normal project workflow. Focused
preparation checks the existing approved index and current files; it does not
rebuild the repository index, start a selector model, or start its own MCP
server. Leave `--discover` off for this profile. Memory and `--support` remain
explicit options. If files are unknown, ordinary Codex investigation remains
available. Use `--context-supplied` when the needed source is already supplied;
that is a caller assertion, not an automatic check of hidden model context.

## What the earlier percentages mean

The source preparer at the start of this refinement was byte-for-byte identical
to both favorable study revisions. A whole-checkout rollback was unnecessary
and would discard later safety fixes.

- The partial warm-study matched subset reported 9.055% lower API-equivalent
  cost per strict success and 6.892% shorter mean instrumented time for source
  only versus bare Codex: 24 tasks per arm, one repeat, selected after stopping.
- The separate confirmation reported 10.19% lower focused-task cost and 3.18%
  longer mean full time: eight focused tasks, two repeats. Across all ten tasks,
  including supplied-context controls, cost was about 2.47% lower and mean time
  was slightly longer.

These are distinct small studies. Cache-write uncertainty can reverse the
estimated ranking. Actual billed savings and general performance remain
unproven. See the unchanged [warm analysis](../benchmarks/warm-80-analysis.md)
and [confirmation](../benchmarks/efficiency-assessment.md).

## The narrow new change

Focused preparation still makes two independent approval/eligibility checks,
two secure observations of each source, and fresh ignore-policy reads on both
passes. Previously it compiled identical ignore rules twice. It now keeps
derived compiled rules within the current request and reuses them only after
securely reading identical current policy content and its hash.

The cache retains at most 64 specifications and 64,000 bytes of policy content.
The byte limit covers retained UTF-8 policy text. Dictionary/tuple/hash-string
bookkeeping and compiled-pattern allocations are additional.
An uncached specification is compiled normally when retention would exceed a
bound. Current per-pass policy byte limits, ancestor order, negations, matching,
missing-file checks and symlink/secret exclusions remain enforced. Nothing
persists across requests. A changed policy or source still causes complete
fallback under the existing checks; timestamps are not freshness evidence.

This change preserves normal complete-source prompt bytes, source versions,
native settings and report fields. It targets local preparation CPU/time; it
does not itself remove model-visible tokens or establish additional model cost
savings. The [component protocol](../benchmarks/source-only-refinement-protocol.md)
compares the historical preparer and the refined implementation with separate
first-call, warm-call, whole-worker and diagnostic measurements.
