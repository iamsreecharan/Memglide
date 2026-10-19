"""Separate post-hoc syntax diagnostic; never executes the inspected source."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'benchmarks/automatic-v3-fixtures/r04/test/index.spec.ts'
OUTPUT = ROOT/'.local/router-v4/exposed-parser-diagnostic.json'

if '--child' in sys.argv:
    import tree_sitter
    import tree_sitter_typescript
    data=sys.stdin.buffer.read(100001)
    if len(data)>100000:raise ValueError('Bounded historical source required')
    parser=tree_sitter.Parser(tree_sitter.Language(tree_sitter_typescript.language_typescript()),timeout_micros=200000)
    tree=parser.parse(data)
    if tree is None:raise ValueError('Parser timed out')
    stack=[tree.root_node];visited=0;found=[]
    while stack:
        node=stack.pop();visited+=1
        if visited+len(stack)>100000:raise ValueError('Node diagnostic limit')
        if node.type=='ERROR' or node.is_missing:
            found.append({'type':node.type,'missing':node.is_missing,'start_byte':node.start_byte,'end_byte':node.end_byte,
                          'start_line_1based':node.start_point.row+1,'start_column_0based':node.start_point.column,
                          'end_line_1based':node.end_point.row+1,'end_column_0based':node.end_point.column,
                          'excerpt_utf8':data[node.start_byte:min(node.end_byte,node.start_byte+200)].decode(errors='replace')})
            if len(found)>20:raise ValueError('Error-node diagnostic limit')
        stack.extend(reversed(node.named_children))
    print(json.dumps({'has_error':tree.root_node.has_error,'visited_nodes':visited,'error_nodes':found}))
else:
    if OUTPUT.exists():raise SystemExit('Keep previous diagnostic')
    data=SOURCE.read_bytes();digest=hashlib.sha256(data).hexdigest()
    if digest!='d6866560f3cf277841f014e85fd08cfaf671f51c24fbf5013943fda34ae07e2d':raise ValueError('Historical frozen source mismatch')
    run=subprocess.run([sys.executable,'-I',str(Path(__file__).resolve()),'--child'],input=data,capture_output=True,timeout=2,
                       cwd=Path(__file__).resolve().parent)
    if run.returncode or len(run.stdout)>16000:raise ValueError('Bounded child diagnostic failed: '+run.stderr.decode()[:200])
    result={'scope':'New separate post-hoc native grammar diagnostic on exposed v3 source, not original benchmark telemetry or a discovery rerun.',
            'source_path':str(SOURCE.relative_to(ROOT)),'source_sha256':digest,'source_bytes':len(data),
            'tree_sitter_version':importlib.metadata.version('tree-sitter'),
            'tree_sitter_typescript_version':importlib.metadata.version('tree-sitter-typescript'),
            'limits':{'source_bytes':100000,'native_parse_timeout_micros':200000,'parent_timeout_seconds':2,'traversed_nodes':100000,'reported_error_nodes':20},
            'source_executed':False,'selection_calls':0,'model_calls':0,'diagnostic':json.loads(run.stdout)}
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
