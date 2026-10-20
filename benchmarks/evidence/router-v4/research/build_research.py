"""Assemble reviewed source receipts and conditional cost-method research."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[2]
PIN = "ff6aec96948b70d94983af2641a6b67c94faeff5"
SCOPES = {
    "sqlite-fts5-bm25": "Selected fts5Bm25GetData and fts5Bm25Function, lines 625-775: corpus statistics, phrase frequency, length normalization, IDF floor and negative return sign.",
    "sqlite-fts5-api": "Selected public API documentation comments lines 35-170: row/column/token statistics, phrase instances and xQueryPhrase behavior.",
    "sqlite-fts5-parser": "Selected grammar lines 1-175: AND/OR/NOT, column filters, phrase/NEAR rules, syntax-error handling. Not a complete query-language review.",
    "sqlite-public-api-docs": "Query Progress Callbacks documentation lines 3709-3748 only: approximate VM instruction cadence, interruption and prepare/step applicability. The rest of the large header was not reviewed.",
    "tree-sitter-query-syntax": "Full short query syntax page: node patterns, fields, ERROR, MISSING and supertypes.",
    "tree-sitter-basic-parsing": "Full short basic parsing page: input, source positions, named/anonymous nodes, traversal and field names.",
    "tree-sitter-readme": "Full short README: concrete syntax tree and robustness goals, links. No measured performance claims adopted.",
    "tree-sitter-public-api-docs": "Selected parse/cancellation documentation lines 285-345 and node missing/error documentation lines 568-607 only. Current upstream API is not proof of installed binding support.",
    "codex-jsonl-events": "Selected Usage, TurnCompletedEvent and TurnFailedEvent definitions, lines 35-90.",
    "codex-jsonl-processor": "Selected initialization, usage_from_last_total, token-usage notification and completed/failed turn branches, lines 85-128 and 493-565.",
    "codex-response-usage": "Selected ResponseCompletedUsage/InputTokensDetails definitions and mapping lines 110-155; cache-write/reasoning parsing test lines 799-823.",
    "codex-protocol-usage": "Selected TokenUsage, TokenUsageRecord, TokenUsageInfo, append aggregation and display/add_assign methods, lines 2240-2365 and 2421-2505.",
    "codex-config-types": "Selected ServiceTier and explicit default Standard-routing sentinel definitions lines 525-556.",
    "codex-config": "Selected service-tier override preservation lines 3940-3978; endpoint/config path text searched while locating backend defaults. No full-file review.",
    "codex-openai-models": "Selected model/catalog tier metadata and service_tier_for_request implementation lines 980-1015. No complete catalog/model review.",
    "codex-readme": "Selected README ChatGPT-plan/API authentication distinction; no authentication commands executed.",
    "openai-openapi-readme": "Full repository README: API specification publication and SDK/documentation links. It does not supply applicable model prices.",
    "openai-python-response-usage": "Full short current usage schema: cache-write/cached input and reasoning output breakdown.",
    "openai-cookbook-readme": "Full short README: repository role and documentation pointers only. No pricing verified and no examples executed.",
    "codex-client": "Imports searched to locate the model-provider-info crate. No full-file review or endpoint/billing claim based on this file.",
    "codex-model-provider-info-crate": "Selected CHATGPT_CODEX_BASE_URL constant line 77, provider metadata lines 134-152 and to_api_provider lines 420-438: auth-mode backend default and configured override.",
    "codex-model-provider-crate": "Full short module/re-export list while locating endpoint defaults; no further provider behavior inferred.",
    "codex-workspace-cargo": "Selected codex-login workspace crate path while locating public auth source; no dependency/security review.",
    "codex-login-lib": "Full short module/re-export list to identify auth module location. No runtime credential inspection.",
    "codex-login-server": "Selected DEFAULT_ISSUER constant line 76 and token endpoint construction lines 710-730 and 1015-1045. These establish source defaults only; no login executed.",
    "codex-login-auth-module": "Full short module/re-export list to locate manager implementation.",
    "codex-login-auth-manager": "Selected refresh endpoint/time-window constants lines 203-214, request_chatgpt_token_refresh lines 1625-1648, endpoint override lines 1726-1728, auth refresh trigger lines 2390-2405, refresh_token early behavior lines 2848-2870, should_refresh_proactively lines 3004-3025 and refresh/persist call lines 3090-3110. No auth files or environment override values inspected.",
    "codex-login-auth-access-token": "Full short source used while locating token refresh; no runtime token or credential values read.",
}

ledgers = sorted(ROOT.glob("*fetch-ledger.json"))
sources = []
for ledger in ledgers:
    for receipt in json.loads(ledger.read_text()):
        row = dict(receipt)
        row["local_ledger"] = str(ledger.relative_to(REPOSITORY))
        row["local_snapshot"] = (
            str((ROOT / row["snapshot"]).relative_to(REPOSITORY))
            if "snapshot" in row else None
        )
        row["reading_scope"] = SCOPES.get(
            row["name"],
            "No document content reviewed: request failed, path returned 404, or response exceeded the bounded download cap."
        )
        sources.append(row)

historical = json.loads((REPOSITORY / "benchmarks/cost-pricing.json").read_text())
ARCHIVES = {
    "platform-pricing": historical["provenance"][0],
    "gpt-6-1-sol": historical["provenance"][1],
    "prompt-caching": historical["provenance"][2],
}
archive_checks = []
for name, provenance in ARCHIVES.items():
    path = REPOSITORY / ".local/cost-v1/research" / (name + ".source")
    body = path.read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    assert digest == provenance["body_sha256"], name
    archive_checks.append({
        "name": name, "historical_url": provenance["url"],
        "original_retrieved_at_utc": provenance["retrieved_at_utc"],
        "local_archive": str(path.relative_to(REPOSITORY)),
        "bytes": len(body), "sha256": digest,
        "matches_historical_receipt": True,
        "fresh_network_retrieval": False,
        "reading_scope_this_round": {
            "platform-pricing": "Selected historical Standard flagship table, extracted text lines 709-755.",
            "gpt-6-1-sol": "Selected historical model identity, four token rates, >272K full-request condition and tier multipliers, extracted text lines 703-728.",
            "prompt-caching": "Selected historical non-additive pricing sentence, extracted text lines 745-756; ordinary-input partition excerpt located by text search. Not the full caching guide.",
        }[name],
    })

tag_command = ["git", "ls-remote", "https://github.com/openai/codex.git", "refs/tags/rust-v0.159.2", "refs/tags/rust-v0.159.2^{}"]
tag = subprocess.run(tag_command, check=True, capture_output=True, text=True, timeout=40)
assert PIN + "\trefs/tags/rust-v0.159.2^{}" in tag.stdout
tag_receipt = {
    "command": tag_command, "exit_code": tag.returncode,
    "observed_at_utc": datetime.now(timezone.utc).isoformat(),
    "stdout": tag.stdout,
    "stdout_sha256": hashlib.sha256(tag.stdout.encode()).hexdigest(),
    "authentication_values_read": False,
}
(ROOT / "installed-tag-resolution.json").write_text(json.dumps(tag_receipt, indent=2, sort_keys=True) + "\n")

result = {
    "schema_version": 1,
    "research_date_utc": datetime.now(timezone.utc).isoformat(),
    "purpose": "Primary-source mechanisms and honest measurement/cost assumptions for a separate matched bare-Codex versus Memglide coding experiment.",
    "scope_limits": {
        "no_model_requests_dispatched_by_research": True,
        "no_authentication_tests_by_research": True,
        "no_credential_values_read_or_changed": True,
        "indexed_or_downloaded_source_code_executed": False,
        "research_fetch_scripts_executed": True,
        "production_or_test_files_changed_by_research": False,
        "tests_executed_by_research": 0,
        "fresh_evaluation_corpus_contents_read_by_research": False,
        "full_research_papers_read_this_round": [],
        "native_coding_outcomes_established_by_research": False,
        "billing_data_obtained": False,
    },
    "network": {
        "mode": "restricted", "policy_state": "enforced", "observations_current": True,
        "vpn_configured": False, "inherited_proxy_preserved": True,
        "tls_verification": True, "policy_changed_by_research": False,
        "per_response_cap_bytes": 2 * 1024 * 1024,
        "runtime_status_observed": "connected/running; no configured capabilities, secrets, runtime variables or outbound identities reported",
        "official_pricing_host_currently_allowed": False,
        "successful_destination": "raw.githubusercontent.com; read-only public Git tag lookup via github.com",
    },
    "requests": len(sources),
    "successful_responses": sum(row["success"] for row in sources),
    "failed_or_unretained_responses": sum(not row["success"] for row in sources),
    "sources": sources,
    "source_provenance_limits": [
        "Mutable branch documents are identified by downloaded byte hashes and dates; their branch commit was not resolved.",
        "Installed CLI version and official annotated release tag were checked; no binary reproducibility or exact local executable hash equivalence is claimed.",
        "Selected API documentation comments and implementation sections were read; no claim of complete source review.",
        "Direct sqlite.org FTS5 HTML was inaccessible. SQLite FTS5 public API comments, query grammar and BM25 source were freshly read from the official sqlite/sqlite repository.",
        "Public OpenAPI YAML response exceeded the 2MiB cap and was not retained or reviewed; no current price claim follows.",
    ],
    "discovery_engineering_conclusions": {
        "status": "Design conclusions and caveats, not measured efficacy or externally proved semantic completeness.",
        "production_scope": "Filter project and production eligibility before every discovery cap; do not filter only after mixed-pool top-k.",
        "parse_errors": "Separate complete lexical inventory from per-file parse status. Unrelated syntax errors/unsupported files outside plausible task candidates need not block. Candidate errors remain unknown evidence.",
        "broad_lexical_origin": "Retain raw-text discovery for files without extracted symbols; comments/literals may propose candidates but cannot prove runtime relevance.",
        "unknown_competitors": "Never silently discard an unparseable/unsupported plausible competitor; abstain unless an independently sound decision-compatible upper bound excludes it.",
        "overflow": "Use a sentinel row/equivalent complete bounded enumeration; disclose truncation and missing query-term coverage. Top-k is not proof of absent competitors or semantic recall.",
        "freshness": "Revalidate winner and losing competitor current hashes plus policy before delivery.",
        "dependency_graph": "State extracted resolved-direct production coverage only; incomplete/unresolved/dynamic graph is not complete closure. Required-context uncertainty within an all-or-nothing delivery contract must preserve fallback.",
        "resource_limits": "Result LIMIT alone is insufficient: combine SQL VM/progress limits with time, rows/bytes, parser/process bounds; do not claim hard RSS or end-to-end lock/filesystem deadlines without evidence.",
        "bm25_caveat": "Lexical ranking with corpus-length/frequency effects, IDF floor and negative score sign; not semantic correctness or confidence. Outer result filtering does not restrict FTS table statistics.",
        "tree_sitter_caveat": "Recovered syntax tree may contain ERROR or MISSING nodes; syntax fields/ranges do not prove execution/type erasure or dependency completeness. Current upstream API may differ from installed versions.",
    },
    "codex_usage": {
        "installed_version": "codex-cli 0.159.2", "official_source_commit": PIN,
        "tag_resolution": str((ROOT / "installed-tag-resolution.json").relative_to(REPOSITORY)),
        "native_fields": ["input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens"],
        "accounting": "C and W are within I; R is within O. Validate nonnegative integral counts and C+W<=I; do not double count subsets.",
        "cache_write_omission": "Pinned SSE parser defaults missing cache_write_tokens to zero; native zero is not proof of explicit upstream zero.",
        "cumulative_usage": "exec JSONL processor copies last ThreadTokenUsage.total, which is cumulative. Use fresh sessions per attempt; do not sum cumulative updates/resumed-thread totals.",
        "absent_usage": "Processor returns default zero Usage when no thread usage update was received. Failed turns emit error without completed-turn usage; absent usage is unknown, not zero spending.",
        "model_request_count": None,
        "model_request_count_reason": "exec JSONL usage has no per-request count. Protocol defines best-effort per-completed-response records but their presence in exec JSONL is not established. Tool-command count cannot substitute.",
        "supported_standard_routing_override": "-c 'service_tier=\"default\"'",
        "routing_scope": "Client sentinel prevents catalog defaults and is omitted from outbound tier field; server-confirmed tier/tariff remains unknown.",
        "default_backend": {
            "base_url": "https://chatgpt.com/backend-api/codex",
            "source": f"https://github.com/openai/codex/blob/{PIN}/codex-rs/model-provider-info/src/lib.rs#L77",
            "selection_scope": "to_api_provider lines 420-438 selects Codex base for Chatgpt, ChatgptAuthTokens, Headers, AgentIdentity and PersonalAccessToken; API-key mode defaults to https://api.openai.com/v1. Configured provider base_url can override.",
            "runtime_auth_or_connectivity_verified": False,
        },
        "default_chatgpt_oauth_refresh": {
            "url": "https://auth.openai.com/oauth/token",
            "source": f"https://github.com/openai/codex/blob/{PIN}/codex-rs/login/src/auth/manager.rs#L212",
            "refresh_call_scope": "request_chatgpt_token_refresh lines 1625-1648 uses endpoint; explicit environment override possible in lines 1726-1728.",
            "proactive_scope": "Managed Chatgpt auth only: token expiry within5min, or fallback last_refresh older8days; other auth modes differ.",
            "runtime_binding_or_expiry_inspected": False,
            "runtime_refresh_needed_or_working": None,
        },
    },
    "pricing": {
        "fresh_current_pricing_verified": False,
        "status": "Fresh official pricing/model/caching fetches blocked by inherited proxy CONNECT403; public official GitHub fallbacks verified usage contracts but no current applicable tariff.",
        "actual_billing_usd": None,
        "historical_source_file": "benchmarks/cost-pricing.json",
        "historical_model": historical["model"], "historical_service_tier": historical["service_tier"],
        "historical_retrieved_at_utc": historical["retrieved_at_utc"],
        "historical_archive_checks": archive_checks,
        "estimate_label": "Conditional API list-price-equivalent estimate using historically verified Oct18 rates; current applicability and actual CLI account billing unverified.",
        "historical_per_million_usd": historical["per_million_usd"],
        "historical_long_context_per_million_usd": historical["long_context_per_million_usd"],
        "historical_context_threshold_tokens": historical["context_threshold_tokens"],
        "historical_context_threshold_comparison": ">",
        "context_scope": "Per model request, full-request rates. Aggregate above threshold cannot locate qualifying calls. Aggregate below threshold bounds included completed calls only; missing request usage remains unknown.",
        "historical_tier_scenarios_relative_to_standard": historical["tier_scenarios_relative_to_standard"],
        "historical_conditional_uplifts": historical["conditional_uplifts"],
        "short_formula": "((I-C-W)*2 + C*0.10 + W*2.50 + O*10) / 1000000",
        "write_sensitivity": "Native-reported W point scenario; separate hypothetical W=I-C upper write scenario under same historical tariff and complete usage. No actual-billing bound.",
        "cost_per_success": "All arm attempt costs including failures / independently successful tasks; zero successes undefined. Missing failure/request usage prevents complete cost.",
        "savings_formula": "100*(1-Memglide_cost_per_success/bare_Codex_cost_per_success)",
        "write_uncertainty_savings_interval": "[1-B_upper/A_lower, 1-B_lower/A_upper] with positive cost-per-success denominators",
        "unmeasured_costs": ["Actual account tariff and charges", "Server-confirmed tier and endpoint classification", "Missing request/failed-attempt usage", "Local compute/hosting", "Separately charged tools/external services"],
    },
    "matched_experiment_requirements": [
        "Same task, source baseline, model, reasoning, requested tier, budgets and independent grading in both arms.",
        "Fresh sessions per attempt; counterbalance order and preserve failures/timeouts and development attempts separately.",
        "Actual automatic Memglide preparation and unchanged coding task; report preload/abstention and preparation costs.",
        "Actual independently graded behavior; process exit and syntax validity alone do not establish correctness.",
        "End-to-end wall latency includes preparation and failures; token outputs retain categories and availability.",
        "Conditional historical-price API equivalent reported separately from actual billing and complete spend availability.",
        "No transfer of prior cohort/paper improvements; conclusions limited to recorded tasks and conditions.",
    ],
}
destination = REPOSITORY / "benchmarks/router-v4-research.json"
destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"output": str(destination), "requests": len(sources), "successful_responses": result["successful_responses"], "historical_hash_checks": len(archive_checks), "fresh_prices_verified": False}, indent=2))
