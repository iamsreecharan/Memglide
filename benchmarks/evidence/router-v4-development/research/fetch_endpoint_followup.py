"""Follow crate paths identified in the pinned client's imports."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_sources import ROOT, PIN, fetch

SOURCES = [
    ("codex-model-provider-info-crate", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/model-provider-info/src/lib.rs"),
    ("codex-model-provider-crate", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/model-provider/src/lib.rs"),
    ("codex-login-default-client", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/login/src/default_client.rs"),
]

if __name__ == "__main__":
    ledger = ROOT / "endpoint-followup-fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
