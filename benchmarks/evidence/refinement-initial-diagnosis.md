# Initial fresh retrieval diagnosis

Read-only analysis of the preserved first Meridian evaluation. The subsequent replay is reused validation; the original result remains evidence for its recorded source revision.

The experiment has **24 unique task IDs**, twelve mirrored language intents, three policies and two repeats: **144 observations**, not 144 independent tasks. The counts below use repeat one. All-body acceptance means the primary body and two declared helper bodies are present; it does not mean a coding task succeeded.

| Policy | Complete primary / 24 | Complete dependency bodies / 48 | All required bodies / 24 | Declared file precision |
|---|---:|---:|---:|---:|
| refined | 16 | 20 | 8 | 14.04% |
| previous | 16 | 20 | 8 | 14.04% |
| legacy | 19 | 30 | 11 | 22.42% |

## Supported causes

1. Refined and previous quality is identical here because every inspection prompt has no preferred source role and unchanged lexical focus token set; the new ranking heuristics do not activate.
2. All eight refined revoke primary-body misses already have a covering search candidate within the first forty. Four documentation pages survive focus selection while the primary source and required helpers do not.
3. Refined has twenty-eight missing dependency bodies: twenty-six required files absent and two present with a different or partial body. Every missing dependency has a covering candidate within the first forty. Sixteen tasks show budget omissions and sixteen show focus omissions.
4. All eight exact-path extend contexts include three service files from other domains. Code inspection of the initial selector found basename identifier anchoring in addition to qualified path anchoring, consistent with excess cross-domain expansion.
5. Release prompts say the rule it calls; the initial broad-query calls heuristic bypasses four-file focus. These eight contexts average 16.75 files and all have budget omissions.
6. All forty-eight declared direct dependencies have the correct resolved graph edge. These observations support selection, anchoring and packing as the failures; they do not support unresolved graph edges as the main cause.

## Proposed next checks

- Guard narrowed context selection when implementation intent is unknown, preserving source recall before claiming selectivity gains.
- Treat a qualified path as a specific module anchor rather than preserving every matching basename.
- Distinguish a request for direct helper evidence from a broad search for all callers.
- Prioritize complete source plus resolved direct helper bundles ahead of optional overlapping documentation and unrelated modules, then validate on a newly authored independent corpus.

## Limits

- Procedural visible synthetic holdout, not production representativeness; twelve mirrored language intents are correlated.
- Counterfactual causes are inferred from retained candidates, exact source evidence, omission warnings and initial code inspection; no isolated causal ablation was run for this diagnosis.
- Direct dependency judgments cover only two declared helpers per task; neither exact body inclusion nor all-body acceptance proves semantic coding-task completeness.
- Any replay after these misses is reused validation. Initial evidence remains valid for its frozen source but does not attest a later source revision.
- No model calls, actual token/cost measurement or coding-task success is supplied by these local retrieval observations.

## Preserved evidence

- `benchmarks/refinement-retrieval.json` SHA-256 `4a7286e6276fe2509fc6a79e8b35399beb2d02717079a95881341101bbd2c432`
- `benchmarks/refinement-retrieval.md` SHA-256 `f86997c4e1a03b815d9fe198ac6a9fd97c44f9a3666637fc75d0f8a83f75b0ac`

Initial source tree: `c966edd662ca7d9d20c9f48d3bdaabfd35427c809c4e8f6fb917d00617c5dc99`. Full per-label misses and forty-eight resolved-edge witnesses are in the adjacent JSON.
