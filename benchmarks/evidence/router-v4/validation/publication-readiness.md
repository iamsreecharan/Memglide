# Published configuration and attached-worker readiness

The new configuration is published, but this attached worker still reports the original version and enforced network policy. Native access remains blocked; the benchmark is not ready to dispatch.

| Observation | Published configuration | Attached worker |
| --- | --- | --- |
| Version | `5c33fc12-3c6c-4925-af68-8f84d833fb3a~cecfgver_6ad67f9a7158819e95747debdfba49d2` | `5c33fc12-3c6c-4925-af68-8f84d833fb3a~cecfgver_6ad1ae6997f4819e9b4e9b0a8bb20912` |
| Draft | `null` (reader returned published configuration) | Revision `1` |
| Custom OpenAI hosts | `auth.openai.com`, `chatgpt.com`, `developers.openai.com` | None; all three absent from current effective policy |
| Verification | Read-only configuration tool | Current/enforced runtime tool plus actual `/etc/codex/network-policy.json` |

The local policy SHA-256 is `30f2ede0cbbeec2304389d374bab11bf356191d6899a460ad332815774b844e2`. Both supported runtime metadata and the worker file exclude the required hosts. Running/connected status does not establish model access. This is an observed publication-versus-worker mismatch; no claim is made that publication failed or that the current worker migrated.

Two separate native CLI access checks are preserved:

| Attempt | Wall time | Outcome | Completed turns | Usage and charge |
| --- | ---: | --- | ---: | --- |
| Original | 45.008s | Timeout; proxy HTTP CONNECT 403 | 0 | Unknown |
| After publication | 45.016s | Timeout; proxy HTTP CONNECT 403 | 0 | Unknown |

Both stderr files contain `HTTP CONNECT failed with status 403`; neither contains a 401. This diagnoses the observed proxy layer and does not verify credentials. Each incomplete JSONL stream lacks completed-turn usage. There were **two CLI invocations**, not two known model/API calls. Their internal reconnect messages cannot supply a model-call count. Estimated and actual total spending remain `null`, never $0.

Original receipts and logs remain unchanged:

- [First receipt](native-preflight/receipt.json), [stderr](native-preflight/attempt/stderr.log), [events](native-preflight/attempt/events.jsonl).
- [Post-publication receipt](native-preflight-after-publish/receipt.json), [stderr](native-preflight-after-publish/attempt/stderr.log), [events](native-preflight-after-publish/attempt/events.jsonl).

The existing pricing scenario is still explicitly historical and unrefreshed. Its source retrieval date is `2026-10-18T16:24:05.775122+00:00`. The current research JSON has `fresh_current_pricing_verified:false`; the research text, native protocol, runner interpretation and both receipts label current applicability or charges unknown. No pricing request was retried for this diagnosis.

Start a **new cloud task using the published environment/configuration**. Preserve the reviewed checkout and evidence if they are newer than the published snapshot. In that task, first verify the published source version and all three hosts in current enforced policy. Revalidate source/runtime seals before one bounded, separately recorded native eligibility check. New-task restoration, authentication and model access have not been verified here.

The onboarding contract says “publishing a version does not migrate unrelated running tasks”; the product owns publication/reconnection. If a new task still reports the old version, provide these exact version IDs and policy evidence through the platform support path. Editing the local policy file or changing proxy/TLS behavior cannot apply a published configuration.

Keep all 72 formal slots UNRUN until a successful current eligibility check. Retain both failed access checks and any later checks separately. These preflights support no coding correctness, latency, token, cost-benefit or savings result.

Only this diagnostics pair was written. Production code, runners, pricing, frozen reports and original receipts were not changed. No model request, pricing retry, credential-file read, environment-value dump, draft mutation or proxy/TLS bypass was performed during this diagnosis. Full selected metadata, source hashes and receipt hashes are in [publication-readiness.json](publication-readiness.json).
