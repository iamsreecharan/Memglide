"""Read stored offline outcomes/SQLite metadata and static frozen code only.

No selector/ranker/search API, FTS MATCH query, parser, source execution, model,
index refresh, mutation, or benchmark rerun occurs here.
"""
import ast
import hashlib
import json
import sqlite3
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/Memglide')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def constant(relative, name):
    for node in ast.parse((ROOT / relative).read_text()).body:
        if not isinstance(node, ast.Assign) or not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        value = node.value
        if isinstance(value, ast.Constant):
            return value.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == 'frozenset':
            inner = value.args[0]
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == 'split' and isinstance(inner.func.value, ast.Constant):
                return set(inner.func.value.value.split())
            return set(ast.literal_eval(inner))
    raise ValueError('static constant not found: ' + name)

suffixes = constant('src/memglide/integrations/auto_preload.py', '_PRODUCTION_SUFFIXES')
nonproduction = constant('src/memglide/integrations/auto_preload.py', '_NONPRODUCTION_PARTS')
supported = constant('src/memglide/integrations/runtime_syntax.py', 'LANGUAGES')

def production(path):
    value = PurePosixPath(path)
    name = value.name.casefold()
    return (value.suffix.casefold() in suffixes and not {part.casefold() for part in value.parts} & nonproduction
            and not name.startswith('test_') and not name.endswith('_test.py') and '.test.' not in name
            and '.spec.' not in name and name not in {'conftest.py', 'setup.py'})

report_path = ROOT / '.local/router-v3-offline/report.json'
report = json.loads(report_path.read_text())
missed = {'t01','t04','t05','t10','t11'}
observations = []
for row in report['rows']:
    if row['arm'] != 'C' or row['task_id'] not in missed:
        continue
    directory = ROOT / '.local/router-v3-offline/runs' / ('run-' + str(row['ordinal']).zfill(4))
    db_path = directory / 'state/state.db'
    with sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA query_only=ON')
        stats = json.loads(connection.execute('SELECT index_stats FROM projects').fetchone()[0])
        files = [dict(value) for value in connection.execute('SELECT path,language,size,parse_error,structural,hash FROM files ORDER BY path')]
    auto = row['observation']['preparation']['automatic_selection']
    unsupported = [item for item in files if production(item['path']) and PurePosixPath(item['path']).suffix.casefold() not in supported]
    errors = [{'path':item['path'],'language':item['language'],'parse_error':item['parse_error'],
               'static_production_path':production(item['path']),'sha256':item['hash']} for item in files if item['parse_error']]
    observations.append({'task_id':row['task_id'],'repeat':row['repeat'],'ordinal':row['ordinal'],
                         'reason':auto['reason'],'candidate_files_considered':auto.get('candidate_files_considered'),
                         'candidate_generation_limit_reached':auto.get('candidate_generation_limit_reached'),
                         'ranked_candidate_metadata_recorded':auto.get('ranked_candidates',[]),
                         'index_stats':{key:stats.get(key) for key in ('file_count','symbol_count','languages','partial','errors','ignored')},
                         'indexed_parse_errors':errors,'indexed_static_production_file_count':sum(production(item['path']) for item in files),
                         'indexed_unsupported_production_paths':unsupported,
                         'database_artifact':str(db_path.relative_to(ROOT))})

sources=['src/memglide/integrations/auto_preload.py','src/memglide/integrations/runtime_evidence.py','src/memglide/integrations/runtime_syntax.py','src/memglide/integrations/source_evidence.py']
freeze=json.loads((ROOT/'.local/router-v3-policy-freeze/policy-freeze.json').read_text())
preload=ROOT/'src/memglide/integrations/preload.py'
result={'scope':'Read-only post-hoc stored outcomes/index metadata/static code. No selectors, searches, parsing workers, models or reruns.',
        'cohort_report_sha256':sha(report_path.read_bytes()),'frozen_head':freeze['seal']['head'],
        'limits':{'candidate_generation_cap':constant(sources[0],'_MAX_CANDIDATES'),'evidence_file_cap':constant(sources[3],'MAX_EVIDENCE_FILES'),
                  'runtime_supported_suffixes':sorted(supported)},
        'known_path_preparer_sha256':sha(preload.read_bytes()),'known_path_preparer_matches_frozen':sha(preload.read_bytes())==freeze['seal']['files']['src/memglide/integrations/preload.py'],
        'static_source_sha256':{path:sha((ROOT/path).read_bytes()) for path in sources},'observations':observations,
        'findings':[
            {'tasks':['t10','t11'],'observed_cause':'Stored index errors report Tree-sitter syntax errors in test/index.spec.ts. The whole-project stats.errors guard returns incomplete_index before candidate generation. This is a nonproduction test path under the frozen production-path predicate. No claim is made that the upstream test is invalid TypeScript; parser diagnostics have no stored error-node location.'},
            {'tasks':['t04'],'observed_cause':'Receipt records candidate_generation_limit_reached=true. Static code declines when metadata search returns exactly100 before filtering production paths. Exact100 candidate paths are not preserved, so no nonproduction share is inferred.'},
            {'tasks':['t05'],'observed_cause':'Receipt records38 production candidates; shared evidence validator cap is24. Guard declines before source attestation. Individual candidate paths are not preserved.'},
            {'tasks':['t01'],'observed_cause':'Receipt records6 production candidates and runtime_language_unavailable. Static guard requires every candidate suffix to be in the8 supported Python/JS/TS suffixes. The only indexed production-suffix paths outside that set are scripts/update-translations.sh and scripts/generate-translation-binaries.sh (.sh, indexed text). At least one must have entered the unrecorded batch for this guard; exact offending candidate membership/order is not observed and no ranking reconstruction is performed.'}
        ],'selector_or_model_calls':0}
output=ROOT/'.local/router-v3/posthoc-diagnostics.json'
output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({'output':str(output),'observations':len(observations),'known_path_preparer_matches_frozen':result['known_path_preparer_matches_frozen'],'selector_or_model_calls':0}))
