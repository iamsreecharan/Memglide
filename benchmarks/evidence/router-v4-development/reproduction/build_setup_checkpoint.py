"""Archive an explicit development allowlist; no benchmark or model dispatch."""
from __future__ import annotations
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / '.local/router-v4'
OUT = ROOT / 'benchmarks/evidence/router-v4-development'
if OUT.exists():
    raise ValueError('Never overwrite prior evidence')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def counts(name):
    suites = list(ET.parse(LOCAL / name).getroot().iter('testsuite'))
    result = {k: sum(int(s.get(k, '0')) for s in suites) for k in ('tests','failures','errors','skipped')}
    result['passed'] = result['tests'] - result['failures'] - result['errors'] - result['skipped']
    return result

for name in ('full-python.xml', 'python311-full.xml'):
    c = counts(name)
    assert c['passed'] == 2341 and not c['failures'] and not c['errors'] and not c['skipped']

NAMES = '''diagnosis.md diagnosis.json exposed-parser-diagnostic.json minimal-parser-controls.json
implementation-plan.json historical-preservation.json network-readiness.json
development-ledger.json security-review.json offline-runner-review.json native-runner-review.json
query-boundary-control-initial.json numeric-anchor-control-initial.json dotted-boundary-control-initial.json
private-method-control.json reviewer-controls-initial-failure.json reviewer-controls-first-pass.json reviewer-controls.json
reviewer_controls.py diagnose_parser.py
native-runner-review-descendants.json native-runner-review-freeze-bootstrap.json
native-runner-review-accounting.json native-runner-review-processes.json native-runner-review-corrections.json
native-runner-review-reproductions.json native-runner-review-tests.xml native-runner-review-tests-final.xml
owned-tests-initial.log owned-tests-second.log owned-tests-third.log owned-tests-final.log
owned-tests-postreview.log owned-tests-postreview-numeric.log owned-tests-final-reviewed.log owned-tests-final-frozen.log
cli-initial.xml cli-initial.log cli-final.xml cli-final.log cli-complete.xml cli-complete.log
affected-initial-command.xml affected-initial-command.log affected.xml affected.log
production-final.xml production-final.log python311-production.xml python311-production.log
full-python.xml full-python.log python311-full.xml python311-full.log
frontend-install.log frontend-build.log frontend-unit.json frontend-unit.log frontend-browser.raw.log frontend-browser.json
bundle.log wheel-build.log installed-env.log installed-dependencies.log installed-wheel.log
runtime-requirements.txt runtime-export.log installed_smoke.py installed-smoke.json installed-smoke.stdout.log installed-smoke.stderr.log
wheel-source-manifest.json ruff.log mypy.log native_preflight.py native-preflight-output.log
corpus-design.md corpus_prepare.py build_report.py'''.split()
OUT.mkdir(parents=True)
entries = []

def add(path, target):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'Expected original regular evidence: {path}')
    data = path.read_bytes()
    data.decode('utf-8')
    if len(data) > 8_000_000:
        raise ValueError('Evidence cap exceeded')
    destination = OUT / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as f:
        f.write(data)
    entries.append({'path':target,'sha256':digest(data),'bytes':len(data),
                    'source':str(path.relative_to(ROOT))})

for name in NAMES:
    add(LOCAL / name, 'validation/' + name)
for name in ('start.json','receipt.json','schema.json','attempt/events.jsonl',
             'attempt/stderr.log','attempt/command.json','attempt/prompt.txt',
             'attempt/process-identity.json','attempt/launch-grant.json'):
    add(LOCAL / 'native-preflight' / name, 'preflight/' + name)
for p in sorted((ROOT / '.local/router-v4-runner').iterdir()):
    if p.is_file() and p.suffix in {'.json','.xml','.log'}:
        add(p, 'offline-runner/' + p.name)
for p in sorted((LOCAL / 'research').rglob('*')):
    if p.is_file() and not p.is_symlink() and p.suffix in {'.json','.txt','.md','.py'} and '__pycache__' not in p.parts:
        add(p, 'research/' + p.relative_to(LOCAL / 'research').as_posix())
add(Path(__file__).resolve(), 'reproduction/build_setup_checkpoint.py')
sources = sorted((ROOT / 'src/memglide').rglob('*.py'))
sources += [ROOT/p for p in ('benchmarks/run_automatic_v4.py','benchmarks/run_router_coding.py',
    'benchmarks/automatic-v4-protocol.md','benchmarks/router-coding-protocol.md',
    'tests/test_bounded_router.py','tests/test_auto_preload_v4.py','tests/test_codex_router_v4.py',
    'tests/test_benchmark_automatic_v4.py','tests/test_benchmark_router_coding.py','pyproject.toml','uv.lock')]
for p in sources:
    add(p, 'reproduction/' + p.relative_to(ROOT).as_posix())
ledger = {'version':1,'kind':'development checkpoint; no fresh model/selection comparison',
    'files':entries,'excluded':['auth/native state','credentials','databases','Git/worktrees','venvs','wheels/binary archives'],
    'self_and_checkpoint_hashes_excluded':True}
(OUT / 'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
installed=json.loads((LOCAL/'installed-smoke.json').read_text())
checkpoint = {'version':1,'base_commit':'4758550be8366efa5a9f86735625e67ab71ed6a4',
    'status':'local environment verified; publication required before next stage',
    'tests':{name:counts(name) for name in ('full-python.xml','python311-full.xml')},
    'frontend_unit':{'passed':24,'failed':0},'production_browser':{'passed':3,'unexpected':0,'flaky':0},
    'installed_checks':{'passed':sum(v is True for v in installed['checks'].values()),'total':len(installed['checks'])},
    'count_scope':'Same2341testcases on separate Python runtimes; focused tests overlap full runs and are not pooled.',
    'independent_reviews':{name:json.loads((LOCAL/name).read_text()) for name in ('security-review.json','offline-runner-review.json','native-runner-review.json')},
    'native_access_check':json.loads((LOCAL/'native-preflight/receipt.json').read_text()),
    'connection':json.loads((LOCAL/'network-readiness.json').read_text()),
    'fresh_selection_cohort':'Not authored or run; author remains blinded',
    'fresh_coding_cohort':'Not authored or run; no formal native assignments launched',
    'comparison_with_bare_codex':None,'new_cost_savings':None,'actual_billed_charges':None,
    'known_failure_notes':['Initial affected-test command referenced an absent filename; zero tests ran. Corrected command passed374; original command log/XML retained.',
      'Reviewer/owner synthetic failures and repairs remain in original development ledgers.',
      'One actual native access attempt timed out45s after proxyCONNECT403; no completed usage, unknown spend is not zero.'],
    'source_sha256':{p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sources},
    'archive_files':len(entries),'ledger_sha256':digest((OUT/'ledger.json').read_bytes()),
    'next_stages':['Publish saved network draft','Recheck runtime and existing CLI access without reading credentials',
      'Verify/recreate policy seals before independent task authoring','Author fresh offline and separate coding cohorts; freeze corpus/graders/controls',
      'Run fresh offline comparison; if selection improves run matched nativeA/B/C study','Report correctness,full time,fail-inclusive historical cost per success and all missing values']}
(ROOT/'benchmarks/router-v4-checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
(ROOT/'benchmarks/router-v4-checkpoint.md').write_text('''# V4 development and environment checkpoint

Local setup is verified. Fresh held-out selection and matched coding-agent
comparisons have **not been authored or run**. There is no new measured advantage
over bare Codex, model cost saving or production-readiness certification.

| Surface | Observed result |
| --- | --- |
| Full Python3.12 suite | 2,341 passed; zero failures/errors/skips |
| Full Python3.11 suite | 2,341 passed; zero failures/errors/skips |
| Frontend / production browser | 24 passed /3 passed, no failures or flaky cases |
| Clean installed wheel, API, default/agent MCP, CLI | 21/21 passed |
| Static/build | Ruff,mypy,frozen install,frontend build,bundle,wheel passed |

The Python versions run the same tests; focused checks overlap. Counts are not
pooled. The original v3 study, all799 archived entries, tasks and negative outcomes
are unchanged. See the [individual miss diagnosis](router-v4-diagnosis.md),
[architecture](../docs/bounded-source-routing.md) and [research](router-v4-research.md).

V4 keeps production-scoped lexical retrieval, a bounded conservative current-source
screen and narrowly verified nonproduction parse exceptions explicit. Full source,
unsupported-competitor fallback and current-version/policy checks remain. Earlier
policies, defaults, known-path delivery and optional memory remain intact.

Independent production, offline-runner and native-runner reviews cleared the
recorded hashes after fixing their counterexamples. The native runner's27 fake
controls are harness tests, not model outcomes. Baseline/reference controls for
the future real tasks remain pending. Development failures and the initial
zero-test command error are retained; no protected assertion was weakened.

One separately recorded actual CLI access check reported a ChatGPT login but
timed out after proxy HTTP CONNECT403. No model turn completed. Usage, charges
and any cost-per-success comparison remain unavailable, not zero. The original
attempt and stderr are preserved without credential state.

The saved environment network draft adds chatgpt.com,auth.openai.com and
developers.openai.com. Saving it does not apply or publish it. The platform requires
finishing setup before publication; the next stage resumes after the user publishes.
No proxy or TLS verification was bypassed. After publication recheck access, verify
the code/runtime seals, independently author/freeze the fresh cohorts and run the
offline study before any eligible matched native comparison. Keep v4 opt-in.

The [JSON checkpoint](router-v4-checkpoint.json) records original review receipts,
source hashes, missing metrics and next steps. The [evidence ledger](evidence/router-v4-development/ledger.json)
hashes exact allowlisted text receipts and reproduction sources. Credential/native
state, databases, worktrees, environments and binary packages are excluded.
''' )
print(json.dumps({'archive_files':len(entries),'tests':checkpoint['tests'],'native_comparison_run':False}))
