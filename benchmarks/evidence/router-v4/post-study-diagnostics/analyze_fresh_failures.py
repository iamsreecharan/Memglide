"""Post-study diagnostics only; preserve original observations and frozen code."""
from __future__ import annotations

import ast
import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from memglide.integrations.preload import TASK_SEPARATOR, _COMPACT_NOTICE


def main() -> None:
    out = ROOT / '.local/router-v4/fresh-failure-diagnostics'
    out.mkdir(exist_ok=False)
    path = ROOT / '.local/router-v4-offline/report.json'
    original_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    report = json.loads(path.read_text())
    tasks = json.loads((ROOT / 'benchmarks/tasks_automatic_v4.json').read_text())
    labels = json.loads((ROOT / 'benchmarks/automatic-v4-grading.json').read_text())
    fixture = ROOT / 'benchmarks/automatic-v4-fixtures'
    rows = []
    for task in tasks:
        observations = {arm: [row for row in report['rows'] if row['task_id'] == task['id'] and row['arm'] == arm]
                        for arm in ('B', 'V3', 'C')}
        sources = [{'path': p, 'content': (fixture/task['repository']/p).read_text()}
                   for p in labels[task['id']]['required_paths']]
        framed = json.dumps({'notice': _COMPACT_NOTICE, 'memglide_sources': sources},
                            ensure_ascii=False, separators=(',', ':')) + TASK_SEPARATOR
        auto = observations['C'][0]['observation']['preparation']['automatic_selection']
        rows.append({'task_id': task['id'], 'repository': task['repository'],
                     'declared_sources': [{'path': s['path'], 'raw_bytes':len(s['content'].encode())} for s in sources],
                     'single_declared_bundle_json_bytes':len(framed.encode()), 'context_cap_bytes':12000,
                     'declared_bundle_fits_cap':len(framed.encode()) <= 12000,
                     'observed_reasons':{arm: [r['observation']['preparation']['reason'] for r in entries] for arm,entries in observations.items()},
                     'observed_ranked_paths_C': [c['path'] for c in auto['ranked_candidates']],
                     'observed_coarse_C': auto.get('coarse_selection'),
                     'observed_candidate_files_C':auto['candidate_files_considered']})
    parser_rows = []
    for relative in ('more_itertools/more.py','more_itertools/more.pyi','more_itertools/recipes.py','more_itertools/recipes.pyi'):
        source = (fixture/'r03'/relative).read_text()
        definitions = sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) for n in ast.walk(ast.parse(source)))
        payload = json.dumps({'sources':{relative:source},'terms':['padded'],'query':'padded'})
        worker = ROOT/'src/memglide/integrations/runtime_syntax.py'
        process = subprocess.run([sys.executable,'-I',str(worker),'--worker'],input=payload,text=True,capture_output=True,timeout=5,cwd=worker.parent)
        name = relative.replace('/','-').replace('.','-')
        (out/(name+'.stderr.log')).write_text(process.stderr)
        (out/(name+'.stdout.json')).write_text(process.stdout)
        parser_rows.append({'path':relative,'definition_nodes':definitions,'runtime_and_declaration_units_required':2+2*definitions,
                            'frozen_max_units':256,'returncode':process.returncode,'unit_limit_error':'Runtime syntax unit limit' in process.stderr,
                            'label':'New post-study single-file diagnostic with terms/query padded; original private worker stderr was not retained. Source was parsed, never imported or executed.'})
    counts = {arm:dict(collections.Counter(row['observation']['preparation']['reason'] for row in report['rows'] if row['arm']==arm and row['kind']=='positive')) for arm in ('B','V3','C')}
    data = {'version':1,'kind':'post-study diagnostics, not replacement formal outcomes',
            'original_report_sha256':original_hash,'formal_report_unchanged':True,
            'positive_reason_counts':counts,'tasks':rows,'parser_posthoc':parser_rows,
            'gate':{'passed':False,'reason':'C positive complete-scope inclusion0/24 equals V3 and is below B6/24; C adds local preparation overhead. No native coding assignments justified by the preregistered improvement condition.'},
            'future_hypotheses_not_implemented':['Reject an impossible full-file budget before expensive ranking; preserve normal agent fallback.',
                'Replace coarse all-query-word screening with bounded hierarchical symbol ownership, separately validated on fresh development cases.',
                'Stream query-relevant syntax summaries under explicit complete-competitor bounds rather than failing on every large symbol table.',
                'Investigate independently bounded symbol/dependency bundles as a distinct experimental delivery contract, never silently truncate whole files.'],
            'model_requests':0,'coding_correctness':None,'measured_model_savings':None,'actual_billing':None}
    assert hashlib.sha256(path.read_bytes()).hexdigest()==original_hash
    (out/'diagnosis.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'out':str(out),'formal_report_unchanged':True,'known_bundles_that_fit':sum(x['declared_bundle_fits_cap'] for x in rows),'positive_tasks':len(rows),'parser':parser_rows},indent=2))


if __name__ == '__main__':
    main()
