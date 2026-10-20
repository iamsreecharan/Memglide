"""A separate receipt ledger for targeted official-source follow-ups."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_sources import ROOT, PIN, fetch

SOURCES = [
    ("sqlite-fts5-parser", "https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5parse.y"),
    ("sqlite-official-docs-unavailable", "https://sqlite.org/fts5.html"),
    ("codex-manager", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/src/models_manager/manager.rs"),
    ("codex-models-subdir", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/src/models_manager/models.json"),
    ("codex-models-manager-data", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/models_manager/models.json"),
    ("codex-models-protocol-data", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/protocol/src/models.json"),
    ("openai-cookbook-readme", "https://raw.githubusercontent.com/openai/openai-cookbook/main/README.md"),
    ("openai-openapi", "https://raw.githubusercontent.com/openai/openai-openapi/main/openapi.yaml"),
]

if __name__ == "__main__":
    ledger = ROOT / "followup-fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
