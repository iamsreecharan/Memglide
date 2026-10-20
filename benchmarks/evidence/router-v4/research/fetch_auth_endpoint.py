"""Inspect public CLI source for refresh destinations; never inspect runtime auth."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_sources import ROOT, PIN, fetch

SOURCES = [
    ("codex-workspace-cargo", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/Cargo.toml"),
    ("codex-login-lib", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/login/src/lib.rs"),
    ("codex-login-auth", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/login/src/auth.rs"),
    ("codex-login-server", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/login/src/server.rs"),
]

if __name__ == "__main__":
    ledger = ROOT / "auth-endpoint-fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
