"""One separately accounted native access check; never copy credential values."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks import estimate_cost, run_cost, run_daily  # noqa: E402

output = ROOT / '.local/router-v4/native-preflight'
output.mkdir()
repo = output / 'repository'
repo.mkdir()
subprocess.run(['git', 'init', '-q', '--initial-branch=benchmark', str(repo)], check=True)
(repo / 'README.md').write_text('Native transport readiness only. No coding task or grading data.\n')
schema = output / 'schema.json'
schema.write_text(json.dumps({'type': 'object', 'properties': {'ready': {'type': 'boolean'}},
                              'required': ['ready'], 'additionalProperties': False}))
artifacts = output / 'attempt'
artifacts.mkdir()
executable = shutil.which('codex')
if not executable:
    raise RuntimeError('Native executable unavailable')
command = run_cost.codex_command(executable, repo, schema, output / 'final.json', 'gpt-6.1-sol', 'low')
prompt = 'Return exactly the schema-compliant result with ready true. Do not use tools or inspect files.'
(output / 'start.json').write_text(json.dumps({'kind': 'separate_native_access_check',
    'attempted': True, 'planned_native_requests': 1, 'timeout_seconds': 45,
    'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
    'model': 'gpt-6.1-sol', 'effort': 'low', 'requested_service_tier': 'default',
    'actual_billed_charges': None}, indent=2)+'\n')
result = run_daily.execute_codex(command, prompt, repo, artifacts, 45, os.environ.copy())
usage = estimate_cost.parse_native_usage((artifacts / 'events.jsonl').read_text())
price = estimate_cost.price_usage(usage, json.loads((ROOT / 'benchmarks/cost-pricing.json').read_text()))
final = json.loads((output / 'final.json').read_text()) if (output / 'final.json').exists() else None
receipt = {'kind': 'separate_native_access_check', 'result': result, 'usage': usage,
    'historical_tariff_estimate': price, 'tariff_scope': 'Oct18 historical provenance; no fresh verification yet',
    'final': final, 'ready': result['exit_code'] == 0 and not result['timed_out'] and final == {'ready': True},
    'actual_billed_charges': None}
(output / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({'ready': receipt['ready'], 'exit_code': result['exit_code'],
    'timed_out': result['timed_out'], 'wall_seconds': result['wall_time_seconds'],
    'observed_usage': usage, 'historical_tariff_estimate': price}))
