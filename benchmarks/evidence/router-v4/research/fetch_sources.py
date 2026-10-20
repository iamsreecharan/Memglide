"""Fetch only public primary-source documentation; retain bounded bytes and receipts."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 2 * 1024 * 1024
PIN = "ff6aec96948b70d94983af2641a6b67c94faeff5"
SOURCES = [
    ("openai-current-pricing", "https://developers.openai.com/api/docs/pricing"),
    ("openai-current-model", "https://developers.openai.com/api/docs/models/gpt-6.1-sol"),
    ("openai-current-caching", "https://developers.openai.com/api/docs/guides/prompt-caching"),
    ("sqlite-fts5-doc", "https://raw.githubusercontent.com/sqlite/docsrc/master/pages/fts5.in"),
    ("sqlite-fts5-bm25", "https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5_aux.c"),
    ("sqlite-fts5-api", "https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5.h"),
    ("tree-sitter-query-syntax", "https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/docs/src/using-parsers/queries/1-syntax.md"),
    ("tree-sitter-basic-parsing", "https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/docs/src/using-parsers/2-basic-parsing.md"),
    ("tree-sitter-readme", "https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/README.md"),
    ("codex-jsonl-events", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/exec/src/exec_events.rs"),
    ("codex-jsonl-processor", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/exec/src/event_processor_with_jsonl_output.rs"),
    ("codex-response-usage", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/codex-api/src/sse/responses.rs"),
    ("codex-protocol-usage", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/protocol/src/protocol.rs"),
    ("codex-config-types", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/protocol/src/config_types.rs"),
    ("codex-config", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/src/config/mod.rs"),
    ("codex-openai-models", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/protocol/src/openai_models.rs"),
    ("codex-catalog", f"https://raw.githubusercontent.com/openai/codex/{PIN}/codex-rs/core/models.json"),
    ("codex-current-catalog", "https://raw.githubusercontent.com/openai/codex/main/codex-rs/core/models.json"),
    ("codex-readme", f"https://raw.githubusercontent.com/openai/codex/{PIN}/README.md"),
    ("openai-openapi-readme", "https://raw.githubusercontent.com/openai/openai-openapi/master/README.md"),
    ("openai-python-response-usage", "https://raw.githubusercontent.com/openai/openai-python/main/src/openai/types/responses/response_usage.py"),
    ("openai-docs-pricing", "https://raw.githubusercontent.com/openai/openai-docs/main/api/docs/pricing.md"),
]


def fetch(row: tuple[str, str]) -> dict:
    name, url = row
    receipt = {
        "name": name, "url": url,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "maximum_bytes": MAX_BYTES,
        "transport": "Inherited HTTPS proxy and CA trust; default TLS verification; no auth/policy changes.",
    }
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Memglide-public-primary-source-review/4"})
        try:
            response = urllib.request.urlopen(request, timeout=25)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read(MAX_BYTES + 1)
            receipt.update(status=response.code, final_url=response.url,
                           content_type=response.headers.get("Content-Type"),
                           etag=response.headers.get("ETag"))
        if len(body) > MAX_BYTES:
            raise ValueError("Response exceeds bounded download cap; body not retained")
        destination = ROOT / (name + ".txt")
        destination.write_bytes(body)
        receipt.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                       snapshot=destination.name, success=receipt["status"] == 200)
    except Exception as error:
        receipt.update(success=False, error=type(error).__name__ + ": " + str(error))
    return receipt


if __name__ == "__main__":
    ledger = ROOT / "fetch-ledger.json"
    if ledger.exists():
        raise SystemExit("Existing receipts must not be overwritten")
    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    ledger.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: row.get(k) for k in ("name", "status", "bytes", "success", "error")} for row in receipts], indent=2))
