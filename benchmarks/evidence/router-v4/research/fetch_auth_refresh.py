"""Follow the installed auth module's public refresh implementation."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_sources import ROOT, PIN, fetch

SOURCES = [
    ("codex-login-auth-module", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/login/src/auth/mod.rs"),
    ("codex-login-auth-refresh", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/login/src/auth/refresh.rs"),
]

if __name__ == "__main__":
    ledger = ROOT / "auth-refresh-fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
