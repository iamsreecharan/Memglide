"""Read documented C API contracts for cancellation, work bounds, and syntax errors."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_sources import ROOT, fetch

SOURCES = [
    ("sqlite-public-api-docs", "https://raw.githubusercontent.com/sqlite/sqlite/master/src/sqlite.h.in"),
    ("tree-sitter-public-api-docs", "https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/lib/include/tree_sitter/api.h"),
]

if __name__ == "__main__":
    ledger = ROOT / "bounds-fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
