"""Locate the installed CLI's public endpoint defaults without authentication."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_sources import ROOT, PIN, fetch

SOURCES = [
    ("codex-model-provider-info", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/src/model_provider_info.rs"),
    ("codex-default-client", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/src/default_client.rs"),
    ("codex-client", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/src/client.rs"),
]

if __name__ == "__main__":
    ledger = ROOT / "endpoint-fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
