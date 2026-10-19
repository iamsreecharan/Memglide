"""Reviewer-owned synthetic v4 controls; no prospective corpus or model requests."""
from __future__ import annotations
import hashlib, json, sys, tempfile, subprocess
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path.cwd() / 'src'))
from memglide.core.indexer import Indexer
from memglide.core.query import tokens
from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.integrations.bounded_router import lexical_upper_bound
from memglide.integrations.runtime_syntax import extract
from memglide.storage.database import Database
import memglide.integrations.preload as preload

out={'scope':'new reviewer-owned synthetic development controls only; not held-out efficacy or model benchmark', 'model_calls':0,'prospective_corpus_reads':0,'soundness':[],'delivery_guards':[]}
for path, body, names in [
 ('pkg/a.py','def a\u0331(value):\n return value\n',['a\u0331']),
 ('pkg/a.py','def a\u00b7b(value):\n return value\n',['a\u00b7b']),
 ('pkg/a.py','def 𝓯𝓸𝓸(value):\n return value\n',['foo']),
 ('pkg/a.js',r'function a\u0062(value) { return value; }',[r'a\u0062']),
 ('pkg/a.ts','class X { #foo() { return 1; } }',['#foo']),
 ('pkg/a.ts',"class X { 'x y'() { return 1; } }",["'x y'"]),
 ('pkg/a.ts','class X { [Symbol.iterator]() { return 1; } }',['[Symbol.iterator]']),
 ('pkg/a.ts','const {foo: x} = source;',['{foo: x}']),
 ('pkg/a.ts','class X { "+"() { return 1; } }',['"+"']),
]:
 for name in names:
  for query in [f'Fix `{name}`',f'Fix {name}()']:
   terms={t for t in tokens(query) if len(t)>2}
   units=extract({path:body},terms,query)[path]
   possible=any(u['explicit'] or len(set(u['code'])|set(u['header']))>=2 and u['code'] for u in units)
   coarse=lexical_upper_bound(path,body,query,terms)
   assert not possible or coarse[0], (path,query,units,coarse)
   out['soundness'].append({'path':path,'source_sha256':hashlib.sha256(body.encode()).hexdigest(),'query':query,'v3_potential':bool(possible),'coarse_possible':coarse[0],'reason':coarse[1]})
for body,query in [
 ('function foo() { return 1; }','Fix #foo() energy handling'),
 ('function foo() { return 1; }','Fix a\u0331foo() energy handling'),
 ('function foo() { return 1; }','Fix a\u200cfoo() energy handling'),
 *[(f'class X {{ {name}() {{ return 0; }} }}',f'Fix {name} decimal formatting') for name in ['1.0','1.','.5','1.0e+30','1_000.0']],
 ('class X { 1.0() { return 0; } }','Fix foo.1.0 decimal formatting'),
 ('class X { 1.0() { return 0; } }','Fix #1.0 decimal formatting'),
 ('class X { ""() { return 0; } }','Fix ""() energy handling'),
]:
 terms={t for t in tokens(query) if len(t)>2}
 units=extract({'pkg/a.js':body},terms,query)['pkg/a.js']
 possible=any(u['explicit'] or len(set(u['code'])|set(u['header']))>=2 and u['code'] for u in units)
 coarse=lexical_upper_bound('pkg/a.js',body,query,terms)
 assert possible and coarse[0], (body,query,units,coarse)
 out['soundness'].append({'path':'pkg/a.js','source_sha256':hashlib.sha256(body.encode()).hexdigest(),'query':query,'v3_potential':bool(possible),'coarse_possible':coarse[0],'reason':coarse[1]})
for target in ['weak_unsupported','nonproduction_parse_warning']:
 for mutation in ['edit','delete','ignore','symlink']:
  with tempfile.TemporaryDirectory(prefix='memglide-review-v4-') as tmp:
   base=Path(tmp);root=base/'repo';root.mkdir();subprocess.run(['git','init','-q',str(root)],check=True)
   (root/'cooling.py').write_text('def cooling_window(flow_rate, capacity):\n return flow_rate / capacity\n')
   if target=='weak_unsupported':
    victim=root/'maintain.sh';victim.write_text("echo 'cooling'\n")
   else:
    (root/'tests').mkdir();victim=root/'tests'/'bad.py';victim.write_text('def invalid(:\n')
   outside=base/'outside.py';outside.write_text('def secret():\n return 99\n')
   db=Database(base/'state.db');pid=Indexer(db).add_project(str(root))['id']
   original=preload.prepare_prompt;changed=False
   def mutate(*args,**kwargs):
    global changed
    prepared=original(*args,**kwargs)
    if kwargs.get('mode')!='off' and not changed:
     changed=True
     if mutation=='edit':victim.write_text('# different\n')
     elif mutation=='delete':victim.unlink()
     elif mutation=='ignore':(root/'.memglideignore').write_text(victim.relative_to(root).as_posix()+'\n')
     else:victim.unlink();victim.symlink_to(outside)
    return prepared
   with patch.object(preload,'prepare_prompt',mutate):
    result=prepare_task_prompt('Cooling window must account for flow rate and capacity.',project_id=pid,db_path=db.path,enabled=True,selection_policy='v4')
   assert changed, result
   assert result['mode']=='passthrough' and not result['files'],result
   assert result['prompt']=='Cooling window must account for flow rate and capacity.',result
   out['delivery_guards'].append({'target':target,'mutation':mutation,'mode':result['mode'],'reason':result['reason'],'original_prompt_preserved':True,'selected_sources_released':0})
out['passed']=True
out['control_counts']={'soundness':len(out['soundness']),'delivery_guards':len(out['delivery_guards'])}
Path('.local/router-v4/reviewer-controls.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'control_counts':out['control_counts']}))
