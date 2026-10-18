# Uncached-input diagnosis of the completed 80 runs

The extra uncached input is mathematically a loss of observed cached input, not an increase in total input: **-57,138 total input - (-149,760 cached input) = +92,622 uncached input**. This arithmetic does not identify why the provider returned fewer cache hits.

Repeat 1 gave B **75.20% more uncached input**; repeat 2 gave B **11.42% less**, even though prepared-prompt hashes matched between repeats for all 20 tasks. In the eight caller-context-supplied controls, A and B received the same task bytes, yet B still used 3.72% more uncached input. Provider cache keys, routing, retention and per-inference usage are unavailable, so source size or task metadata cannot reliably predict a cache win.

The stored read-command proxy totals (A47/B33) mostly retain necessary tests, repository rules and package inspection. All three B focused-source path mentions in that proxy come from `git diff` operands after a newline, incorrectly attached to a preceding `cat` command. Two concern a preloaded source pair; one concerns a supplied-context control. There is no supported evidence here of an accidental focused-source reread causing the uncached regression. Actual filesystem I/O remains unavailable.

Across 32 preloaded runs, the added context was **33,648 UTF-8 bytes**: **16,536 source bytes**, **8,000 explanation bytes**, and **9,112 other envelope/metadata/JSON-escaping bytes**. This supports removing redundant envelope text while retaining every source byte. It does not convert bytes into actual model tokens or cost.

A versioned compact prefix is a reasonable deterministic refinement: keep a concise untrusted-source warning, source paths and complete content before the unchanged task; retain full source hashes/ranges in the private forwarding report; preserve secure reads, freshness checks, explicit scope and unchanged bypass. Canonical ordering stabilizes equivalent file sets. Preserve explicit append-v1 compatibility for prior APIs/runners.

The prefix hypothesis is untested by the existing A/B cohort: its 20 tasks use 20 distinct focus sets. A larger common prefix in an offline same-files/different-tasks example is a byte-layout result, not evidence of provider cache hits. New layout performance and billed cost remain unmeasured. Never skip source or suppress correctness checks based on a guessed cache benefit; keep caller-context and explicit off controls.

The JSON companion retains repeat/order strata, exact payload accounting, proxy-error commands and limitations. The original benchmark and evidence remain unchanged.
