"""Bounded primary-source downloads over the inherited verified HTTPS proxy."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 2 * 1024 * 1024
SOURCES = [
    ('repoformer-readme', 'https://raw.githubusercontent.com/amazon-science/Repoformer/main/README.md'),
    ('repocoder-readme', 'https://raw.githubusercontent.com/microsoft/CodeT/main/RepoCoder/README.md'),
    ('sqlite-fts5-bm25', 'https://raw.githubusercontent.com/sqlite/sqlite/master/ext/fts5/fts5_aux.c'),
    ('typescript-38-type-imports', 'https://raw.githubusercontent.com/microsoft/TypeScript-Website/v2/packages/documentation/copy/en/release-notes/TypeScript%203.8.md'),
    ('tree-sitter-query-syntax', 'https://raw.githubusercontent.com/tree-sitter/tree-sitter/master/docs/src/using-parsers/queries/1-syntax.md'),
    ('tree-sitter-typescript-node-types', 'https://raw.githubusercontent.com/tree-sitter/tree-sitter-typescript/master/typescript/src/node-types.json'),
    ('tree-sitter-python-node-types', 'https://raw.githubusercontent.com/tree-sitter/tree-sitter-python/master/src/node-types.json'),
    ('cpython-312-ast', 'https://raw.githubusercontent.com/python/cpython/3.12/Doc/library/ast.rst'),
    ('codex-exec-doc', 'https://raw.githubusercontent.com/openai/codex/main/docs/exec.md'),
    ('codex-exec-cli', 'https://raw.githubusercontent.com/openai/codex/main/codex-rs/exec/src/cli.rs'),
    ('codex-exec-json', 'https://raw.githubusercontent.com/openai/codex/main/codex-rs/exec/src/event_processor_with_json_output.rs'),
]


def fetch(row):
    name, url = row
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt = {'name': name, 'url': url, 'fetched_at_utc': started, 'maximum_bytes': MAX_BYTES,
               'transport': 'Inherited HTTPS proxy; default HTTPS certificate verification; no auth or policy changes.'}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Memglide-local-primary-source-review/1'})
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read(MAX_BYTES + 1)
            receipt.update({'status': response.status, 'final_url': response.url,
                            'content_type': response.headers.get('Content-Type'),
                            'etag': response.headers.get('ETag')})
        if len(data) > MAX_BYTES:
            raise ValueError('Source exceeded bounded download cap; not retained')
        text = data.decode('utf-8')
        path = ROOT / (name + '.txt')
        path.write_text(text, encoding='utf-8')
        receipt.update({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                        'snapshot': str(path.relative_to(ROOT)), 'success': True})
    except urllib.error.HTTPError as exc:
        receipt.update({'status': exc.code, 'success': False, 'error': str(exc)})
    except Exception as exc:
        receipt.update({'status': None, 'success': False, 'error': type(exc).__name__ + ': ' + str(exc)})
    return receipt


if __name__ == '__main__':
    if (ROOT / 'fetch-ledger.json').exists():
        raise SystemExit('Existing research receipts must not be overwritten')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(fetch, SOURCES))
    (ROOT / 'fetch-ledger.json').write_text(json.dumps(receipts, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipts, indent=2, sort_keys=True))
