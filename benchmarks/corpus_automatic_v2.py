"""Fresh independent held-out tasks from four new pinned public repositories.

Only task construction introduces synthetic defects. The complete frozen
upstream snapshots retain their exact source/license bytes. Expected paths,
reference edits and author-controlled behavioral graders are evaluator data;
none enters a task repository or automatic-selection request. No repository
build script or package install is used. This is procedural grading isolation,
not a security sandbox against malicious benchmark participants.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from benchmarks.corpus import _command
from benchmarks.corpus_automatic import _tree_hash
from benchmarks.corpus_cost import _test_execution_integrity

CORPUS_VERSION = "automatic-2.0.0"
FIXTURES = Path(__file__).with_name("automatic-v2-fixtures")
MANIFEST = Path(__file__).with_name("tasks_automatic_v2.json")

SPECS: list[dict[str, Any]] = [
    {
        "id": "blinker-bound-receiver-identity",
        "repository": "blinker",
        "language": "python",
        "path": "src/blinker/_utilities.py",
        "original": "return id(obj.__func__), id(obj.__self__)",
        "bug": "return id(obj)",
        "partial": 'return (id(obj.__func__), id(obj.__self__)) if obj.__func__.__name__ == "receive" else id(obj)',
        "request": "Repeated access to the same bound receiver method gets different identity keys, breaking signal disconnect and deduplication. Make the receiver identifier stable across bound-method objects while distinguishing methods and receiver instances.",
        "behavior": [
            "class Receiver:\n            def receive(self): pass\n        target=Receiver(); first=target.receive; second=target.receive\n        self.assertIsNot(first,second); self.assertEqual(util.make_id(first),util.make_id(second)); self.assertNotEqual(util.make_id(first),util.make_id(Receiver().receive))",
            "class Receiver:\n            def receive(self): pass\n            def other(self): pass\n        target=Receiver(); first=target.other; second=target.other\n        self.assertEqual(util.make_id(first),util.make_id(second)); self.assertNotEqual(util.make_id(first),util.make_id(target.receive))",
        ],
    },
    {
        "id": "blinker-value-sender-identity",
        "repository": "blinker",
        "language": "python",
        "path": "src/blinker/_utilities.py",
        "original": "if isinstance(obj, (str, int)):",
        "bug": "if isinstance(obj, int):",
        "partial": "if isinstance(obj, int) or isinstance(obj, str) and len(obj) < 5:",
        "request": "Equal string senders created as distinct objects no longer share signal identity. Restore value-based identifiers for strings and integers of any length, while keeping ordinary mutable sender objects distinguished by identity.",
        "behavior": [
            'left="".join(["a","bc"]); right="".join(["ab","c"]); self.assertEqual(left,right); self.assertIsNot(left,right); self.assertEqual(util.make_id(left),util.make_id(right)); self.assertEqual(util.make_id(10**30),util.make_id(int("1"+"0"*30)))',
            'left="long sender value "+"x"*50; right="".join(["long sender ","value ","x"*50]); self.assertEqual(left,right); self.assertIsNot(left,right); self.assertEqual(util.make_id(left),util.make_id(right)); self.assertNotEqual(util.make_id([]),util.make_id({})); first=[]; second=[]; self.assertNotEqual(util.make_id(first),util.make_id(second))',
        ],
    },
    {
        "id": "blinker-bound-weak-references",
        "repository": "blinker",
        "language": "python",
        "path": "src/blinker/_utilities.py",
        "original": "return WeakMethod(obj, callback)  # type: ignore[arg-type, return-value]",
        "bug": "return ref(obj, callback)",
        "partial": 'return WeakMethod(obj, callback) if getattr(obj.__self__, "marker", None) == "first" else ref(obj, callback)',
        "request": "Weakly connected bound receivers disappear even while their owning instance remains alive. Keep a usable weak reference to bound methods without retaining the owner, and preserve the cleanup callback when the owner is collected.",
        "behavior": [
            'class Receiver:\n            marker="first"\n            def receive(self): return 7\n        target=Receiver(); reference=util.make_ref(target.receive); gc.collect(); self.assertIsNotNone(reference()); self.assertEqual(reference()(),7)',
            'class Receiver:\n            marker="other"\n            def receive(self): return 9\n        target=Receiver(); callbacks=[]; reference=util.make_ref(target.receive,lambda item:callbacks.append(item)); gc.collect(); self.assertIsNotNone(reference()); self.assertEqual(reference()(),9); del target; gc.collect(); self.assertIsNone(reference()); self.assertEqual(callbacks,[reference])',
        ],
    },
    {
        "id": "cachetools-keyword-order",
        "repository": "cachetools",
        "language": "python",
        "path": "src/cachetools/keys.py",
        "original": "return _HashedTuple(args + _kwmark + tuple(sorted(kwargs.items())))",
        "bug": "return _HashedTuple(args + _kwmark + tuple(kwargs.items()))",
        "partial": "return _HashedTuple(args + _kwmark + tuple(sorted(kwargs.items()) if len(kwargs) <= 2 else kwargs.items()))",
        "request": "Memoization misses when callers reorder otherwise identical keyword arguments. Cache-key construction must ignore keyword insertion order while preserving positional argument order and the separation between positional and keyword arguments.",
        "behavior": [
            "self.assertEqual(keys.hashkey(4,a=1,b=2),keys.hashkey(4,b=2,a=1)); self.assertEqual(hash(keys.hashkey(a=1,b=2)),hash(keys.hashkey(b=2,a=1))); self.assertNotEqual(keys.hashkey(1,2),keys.hashkey(2,1))",
            "self.assertEqual(keys.hashkey(a=1,b=2,c=3),keys.hashkey(c=3,a=1,b=2)); self.assertNotEqual(keys.hashkey(1),keys.hashkey(a=1)); self.assertEqual(keys.hashkey(),())",
        ],
    },
    {
        "id": "cachetools-positional-type-tags",
        "repository": "cachetools",
        "language": "python",
        "path": "src/cachetools/keys.py",
        "original": "key += tuple(type(v) for v in args)",
        "bug": "key += ()",
        "partial": "key += tuple(type(v) for v in args) if len(args) == 1 else ()",
        "request": "Typed memoization conflates equal-valued positional arguments of different types. Include type distinctions for every positional argument, including booleans and mixed multi-argument calls, without losing keyword type distinctions or order-insensitive keyword handling.",
        "behavior": [
            "self.assertNotEqual(keys.typedkey(1),keys.typedkey(1.0)); self.assertNotEqual(keys.typedkey(True),keys.typedkey(1)); self.assertEqual(keys.typedkey(1),keys.typedkey(1))",
            "self.assertNotEqual(keys.typedkey(1,2),keys.typedkey(1.0,2)); self.assertNotEqual(keys.typedkey(1,2.0),keys.typedkey(1,2)); self.assertNotEqual(keys.typedkey(x=1),keys.typedkey(x=1.0)); self.assertEqual(keys.typedkey(a=1,b=2.0),keys.typedkey(b=2.0,a=1))",
        ],
    },
    {
        "id": "cachetools-method-receiver-exclusion",
        "repository": "cachetools",
        "language": "python",
        "path": "src/cachetools/keys.py",
        "original": "return typedkey(*args, **kwargs)",
        "bug": "return typedkey(self, *args, **kwargs)",
        "partial": "return typedkey(type(self), *args, **kwargs)",
        "request": "Typed method-cache keys incorrectly include the receiver. Exclude the instance entirely, even for unhashable receivers and receivers of different classes; retain type distinctions for the actual method arguments.",
        "behavior": [
            "first=[]; second=[]; left=keys.typedmethodkey(first,1,flag=True); right=keys.typedmethodkey(second,1,flag=True); self.assertEqual(left,right); hash(left); self.assertNotEqual(left,keys.typedmethodkey(first,1.0,flag=True))",
            'self.assertEqual(keys.typedmethodkey([],4),keys.typedmethodkey({},4)); self.assertEqual(keys.typedmethodkey(object(),a=1,b="x"),keys.typedmethodkey(None,b="x",a=1)); self.assertNotEqual(keys.typedmethodkey(None,a=1),keys.typedmethodkey(None,a=1.0))',
        ],
    },
    {
        "id": "defu-array-precedence",
        "repository": "defu",
        "language": "typescript",
        "path": "src/defu.ts",
        "original": "object[key] = [...value, ...object[key]];",
        "bug": "object[key] = [...object[key], ...value];",
        "partial": "object[key] = namespace ? [...object[key], ...value] : [...value, ...object[key]];",
        "request": "Merging default configurations reverses array precedence. User-provided array entries must precede default entries at every nesting depth and across multiple layers, without modifying any input arrays or objects.",
        "behavior": [
            "const source={items:['user']}; const defaults={items:['default']}; const result=core.defu(source,defaults); assert.deepEqual(result.items,['user','default']); assert.deepEqual(source,{items:['user']}); assert.deepEqual(defaults,{items:['default']});",
            "const source={nested:{items:['user']}}; const defaults={nested:{items:['default']}}; assert.deepEqual(core.defu(source,defaults,{nested:{items:['last']}}),{nested:{items:['user','default','last']}}); assert.deepEqual(source,{nested:{items:['user']}});",
        ],
    },
    {
        "id": "defu-nullish-fallback",
        "repository": "defu",
        "language": "typescript",
        "path": "src/defu.ts",
        "original": "if (value === null || value === undefined) {",
        "bug": "if (value === undefined) {",
        "partial": 'if (value === undefined || value === null && namespace === "") {',
        "request": "Explicit null values incorrectly erase configuration defaults. Treat null and undefined as missing at every nesting level, while preserving intentional false, zero and empty-string overrides and keeping input configurations unchanged.",
        "behavior": [
            "assert.deepEqual(core.defu({a:null,b:undefined,c:false,d:0,e:''},{a:1,b:2,c:true,d:3,e:'default'}),{a:1,b:2,c:false,d:0,e:''});",
            "const user={nested:{a:null,b:false}}; assert.deepEqual(core.defu(user,{nested:{a:3,b:true,c:4}}),{nested:{a:3,b:false,c:4}}); assert.deepEqual(user,{nested:{a:null,b:false}});",
        ],
    },
    {
        "id": "defu-class-instance-boundaries",
        "repository": "defu",
        "language": "typescript",
        "path": "src/_utils.ts",
        "original": "prototype !== null &&\n    prototype !== Object.prototype &&\n    Object.getPrototypeOf(prototype) !== null",
        "bug": "false",
        "partial": 'prototype !== null && prototype !== Object.prototype && typeof (value as any).kind === "string"',
        "request": "Configuration merging now recursively traverses class instances as though they were plain objects. Preserve class instances as atomic values, continue merging ordinary and null-prototype mappings, and keep iterable objects excluded from plain-object handling.",
        "behavior": [
            "class Box{constructor(){this.kind='box';this.value=4}} const item=new Box(); assert.equal(util.isPlainObject(item),false); assert.equal(core.defu({item},{item:{fallback:true}}).item,item); assert.equal(util.isPlainObject({a:1}),true);",
            "class Value{constructor(){this.value=2}} const item=new Value(); assert.equal(util.isPlainObject(item),false); assert.equal(core.defu({item},{item:{fallback:3}}).item,item); assert.equal(util.isPlainObject(Object.create(null)),true); assert.equal(util.isPlainObject({[Symbol.iterator]:function*(){}}),false);",
        ],
    },
    {
        "id": "hookable-nested-hook-names",
        "repository": "hookable",
        "language": "typescript",
        "path": "src/utils.ts",
        "original": "const name = parentName ? `${parentName}:${key}` : key;",
        "bug": "const name = parentName ? `${parentName}.${key}` : key;",
        "partial": 'const name = parentName ? `${parentName}${parentName.includes(":") ? "." : ":"}${key}` : key;',
        "request": "Nested hook configurations no longer register under their documented colon-separated names. Flatten every nesting level consistently, preserve callback identity, and ensure public hook registration and invocation use the same flattened names.",
        "behavior": [
            "const handler=()=>3; const flat=core.flatHooks({build:{before:handler}}); assert.deepEqual(Object.keys(flat),['build:before']); assert.equal(flat['build:before'],handler);",
            "const seen=[]; const hooks=core.createHooks(); hooks.addHooks({build:{client:{done:v=>seen.push(v)}}}); await hooks.callHook('build:client:done',7); assert.deepEqual(seen,[7]); assert.deepEqual(Object.keys(core.flatHooks({a:{b:{c:()=>{}}}})),['a:b:c']);",
        ],
    },
    {
        "id": "hookable-serial-awaiting",
        "repository": "hookable",
        "language": "typescript",
        "path": "src/utils.ts",
        "original": "return tasks.reduce((promise, task) => promise.then(() => function_(task)), Promise.resolve());",
        "bug": "return Promise.all(tasks.map(function_));",
        "partial": "return tasks.length === 2 ? tasks.reduce((promise, task) => promise.then(() => function_(task)), Promise.resolve()) : Promise.all(tasks.map(function_));",
        "request": "Serial hook composition starts asynchronous callbacks concurrently. Await each callback before starting the next and stop on rejection, preserving callback order and correct behavior for empty task lists.",
        "behavior": [
            "const seen=[]; await util.serial([1,2],async value=>{seen.push('start'+value); await new Promise(resolve=>setTimeout(resolve,2)); seen.push('end'+value)}); assert.deepEqual(seen,['start1','end1','start2','end2']);",
            "const seen=[]; await util.serial([1,2,3],async value=>{seen.push(value); await Promise.resolve()}); assert.deepEqual(seen,[1,2,3]); const stopped=[]; await assert.rejects(util.serial([1,2,3],async value=>{stopped.push(value); if(value===2)throw new Error('expected'); await Promise.resolve()}),/expected/); assert.deepEqual(stopped,[1,2]); await util.serial([],()=>{throw new Error('never')});",
        ],
    },
    {
        "id": "hookable-observer-snapshots",
        "repository": "hookable",
        "language": "typescript",
        "path": "src/utils.ts",
        "original": "for (const callback of [...callbacks]) {",
        "bug": "for (const callback of callbacks) {",
        "partial": 'for (const callback of (arg0 === "first" ? [...callbacks] : callbacks)) {',
        "request": "Removing an observer during notification skips another observer already scheduled for that event. Deliver each notification from a stable callback-list snapshot, pass through the original event object, and apply removals only to later notifications.",
        "behavior": [
            "const seen=[]; const second=value=>seen.push('b:'+value); const callbacks=[value=>{seen.push('a:'+value); callbacks.splice(callbacks.indexOf(second),1)},second]; util.callEachWith(callbacks,'first'); assert.deepEqual(seen,['a:first','b:first']);",
            "const event={name:'tick'}; const seen=[]; const second=value=>{assert.equal(value,event);seen.push('b')}; const callbacks=[value=>{assert.equal(value,event);seen.push('a');const index=callbacks.indexOf(second);if(index>=0)callbacks.splice(index,1)},second]; util.callEachWith(callbacks,event); util.callEachWith(callbacks,event); assert.deepEqual(seen,['a','b','a']);",
        ],
    },
]


def _spec(task_id: str) -> dict[str, Any]:
    for spec in SPECS:
        if spec["id"] == task_id:
            return spec
    raise ValueError(f"unknown automatic-v2 task: {task_id}")


def load_tasks() -> list[dict[str, Any]]:
    """Issue-only prompts; known paths are evaluator labels, never C input."""
    return [
        {
            "id": spec["id"],
            "repository": spec["repository"],
            "language": spec["language"],
            "prompt": spec["request"],
            "known_paths": [spec["path"]],
            "focus_paths": [spec["path"]],
            "defect_origin": "author-created mutation of pinned upstream production code",
            "grading": "two external behavioral groups plus six external regression groups; no claim of full upstream-suite execution",
            "corpus_version": CORPUS_VERSION,
        }
        for spec in SPECS
    ]


def _source_bytes(spec: dict[str, Any], variant: str) -> bytes:
    original_bytes = (FIXTURES / spec["repository"] / spec["path"]).read_bytes()
    original = original_bytes.decode("utf-8")
    if original.count(spec["original"]) != 1:
        raise ValueError(f"upstream edit not unique: {spec['id']}")
    return (
        original_bytes
        if variant == "reference"
        else original.replace(spec["original"], spec[variant]).encode()
    )


def build_task_repo(task_id: str, root: Path) -> dict[str, Any]:
    spec = _spec(task_id)
    root = Path(root)
    if root.is_symlink():
        raise ValueError("task destination must not be a symlink")
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("task destination must be empty")
    shutil.copytree(FIXTURES / spec["repository"], root, dirs_exist_ok=True)
    (root / spec["path"]).write_bytes(_source_bytes(spec, "bug"))
    return {
        "task_id": task_id,
        "repository": spec["repository"],
        "source_tree_sha256": _tree_hash(root),
        "corpus_version": CORPUS_VERSION,
    }


def apply_reference_fix(root: Path, task_id: str) -> None:
    spec = _spec(task_id)
    (Path(root) / spec["path"]).write_bytes(_source_bytes(spec, "reference"))


def _protection(spec: dict[str, Any], root: Path) -> dict[str, Any]:
    initial = FIXTURES / spec["repository"]
    protected, unexpected, original_names = [], [], set()
    for original in sorted(initial.rglob("*")):
        if not original.is_file():
            continue
        name = original.relative_to(initial).as_posix()
        original_names.add(name)
        if name.startswith("src/"):
            continue
        actual = root / name
        safe = actual.is_file() and not actual.is_symlink()
        protected.append(
            {"file": name, "unchanged": safe and actual.read_bytes() == original.read_bytes()}
        )
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            unexpected.append(relative.as_posix())
            continue
        if path.is_dir() or relative.as_posix() in original_names:
            continue
        bytecode = "__pycache__" in relative.parts and path.suffix == ".pyc"
        new_test = relative.parts[0] in {"test", "tests"} and (
            path.name.startswith("test_")
            and path.suffix == ".py"
            or path.name.endswith((".test.ts", ".test.mjs"))
        )
        new_source = relative.parts[0] == "src" and path.suffix in {".py", ".ts"}
        if not (bytecode or new_test or new_source):
            unexpected.append(relative.as_posix())
    return {
        "protected_files": protected,
        "protected_files_unchanged": all(row["unchanged"] for row in protected),
        "unexpected_files": sorted(set(unexpected)),
        "new_files_valid": not unexpected,
    }


def _python_imports(repository: str) -> str:
    if repository == "blinker":
        return "import gc,weakref\nfrom blinker import Signal, signal, ANY\nfrom blinker import _utilities as util\n"
    return "from cachetools import keys, LRUCache, TTLCache, cached\n"


def _smokes(repository: str) -> list[str]:
    if repository == "blinker":
        return [
            'self.assertIs(util.Symbol("example"),util.Symbol("example"))',
            'self.assertIs(signal("named"),signal("named"))',
            's=Signal(); receiver=lambda sender,value: value+1; s.connect(receiver,weak=False); self.assertEqual(s.send("sender",value=3),[(receiver,4)])',
            's=Signal(); seen=[]; receiver=lambda sender:seen.append(sender); s.connect(receiver,sender="one",weak=False); s.send("two"); s.send("one"); self.assertEqual(seen,["one"])',
            "s=Signal(); receiver=lambda sender:4; s.connect(receiver,weak=False)\n        with s.muted():\n            self.assertEqual(s.send(None),[])\n        self.assertEqual(s.send(None),[(receiver,4)])",
            "def receiver(): return 3\n        reference=util.make_ref(receiver); self.assertIs(reference(),receiver)",
        ]
    if repository == "cachetools":
        return [
            "self.assertEqual(keys.hashkey(1,2),(1,2))",
            "self.assertEqual(keys.methodkey([],4),keys.hashkey(4))",
            "self.assertNotEqual(keys.typedkey(x=1),keys.typedkey(x=1.0))",
            'cache=LRUCache(maxsize=2); cache["a"]=1; cache["b"]=2; self.assertEqual(cache["a"],1); cache["c"]=3; self.assertNotIn("b",cache)',
            'clock=[0]; cache=TTLCache(maxsize=2,ttl=3,timer=lambda:clock[0]); cache["a"]=1; clock[0]=4; self.assertNotIn("a",cache)',
            "calls=[]\n        @cached(cache={})\n        def double(value): calls.append(value); return value*2\n        self.assertEqual(double(3),6); self.assertEqual(double(3),6); self.assertEqual(calls,[3])",
        ]
    if repository == "defu":
        return [
            "assert.deepEqual(core.defu({a:1},{a:2,b:3}),{a:1,b:3});",
            "assert.deepEqual(core.defu({nested:{a:1}},{nested:{b:2}}),{nested:{a:1,b:2}});",
            "assert.deepEqual(core.defu({a:false,b:0,c:''},{a:true,b:2,c:'x'}),{a:false,b:0,c:''});",
            "assert.equal(util.isPlainObject(null),false); assert.equal(util.isPlainObject([]),false);",
            "assert.deepEqual(core.defuFn({a:value=>value+2},{a:3}),{a:5});",
            "assert.deepEqual(core.defuArrayFn({a:items=>items.slice(1)},{a:[1,2,3]}),{a:[2,3]});",
        ]
    return [
        "const hooks=core.createHooks(); const seen=[]; hooks.hook('tick',value=>seen.push(value)); await hooks.callHook('tick',3); assert.deepEqual(seen,[3]);",
        "const hooks=core.createHooks(); let count=0; hooks.hookOnce('tick',()=>count++); await hooks.callHook('tick'); await hooks.callHook('tick'); assert.equal(count,1);",
        "const hooks=core.createHooks(); let count=0; const remove=hooks.hook('tick',()=>count++); remove(); await hooks.callHook('tick'); assert.equal(count,0);",
        "assert.deepEqual(Object.keys(core.flatHooks({simple:()=>{}})),['simple']);",
        "const hooks=core.createHooks(); const seen=[]; hooks.beforeEach(event=>seen.push('before:'+event.name)); hooks.afterEach(event=>seen.push('after:'+event.name)); await hooks.callHook('tick'); assert.deepEqual(seen,['before:tick','after:tick']);",
        "const hooks=core.createHooks(); hooks.hook('tick',()=>{throw new Error('expected')}); await assert.rejects(Promise.resolve(hooks.callHook('tick')),/expected/);",
    ]


def _oracle(spec: dict[str, Any], statements: list[str], stage: str, compiled: Path) -> str:
    if spec["language"] == "python":
        source = "import json,unittest\n" + _python_imports(spec["repository"])
        source += "\nclass ExternalChecks(unittest.TestCase):\n"
        for index, statement in enumerate(statements):
            source += f"    def test_{stage}_{index}(self):\n        {statement}\n\n"
        source += 'if __name__ == "__main__":\n    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExternalChecks))\n    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))\n    raise SystemExit(not result.wasSuccessful())\n'
        return source
    source = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
    if spec["repository"] == "defu":
        source += 'import {createRequire} from "node:module";\nconst require=createRequire(import.meta.url);\n'
        source += f"const core=require({json.dumps(str(compiled / 'defu.js'))});\nconst util=require({json.dumps(str(compiled / '_utils.js'))});\n"
    else:
        source += f"const core=await import({json.dumps((compiled / 'index.js').as_uri())});\nconst util=await import({json.dumps((compiled / 'utils.js').as_uri())});\n"
    for index, statement in enumerate(statements):
        source += f"test({json.dumps(stage + '-' + str(index))},async()=>{{{statement}}});\n"
    return source


def grade_task(root: Path, task_id: str, *, artifact_dir: Path) -> dict[str, Any]:
    spec = _spec(task_id)
    if Path(root).is_symlink() or Path(artifact_dir).is_symlink():
        raise ValueError("repository and artifact roots must not be symlinks")
    root, artifacts = Path(root).resolve(), Path(artifact_dir).resolve()
    if root == artifacts or root in artifacts.parents:
        raise ValueError("grading artifacts must stay outside the agent worktree")
    artifacts.mkdir(parents=True, exist_ok=True)
    protection = _protection(spec, root)
    result: dict[str, Any] = {
        "task_id": task_id,
        "repository": spec["repository"],
        "success": False,
        "passed": False,
        "exit_code": 1,
        "commands": [],
        "test_count": 0,
        "test_execution_integrity": [],
        "execution_did_not_mutate_tree_or_git": None,
        "corpus_version": CORPUS_VERSION,
        "scope": "author-controlled external behavior and regression checks; not full upstream suites",
        **protection,
    }
    if not protection["protected_files_unchanged"] or not protection["new_files_valid"]:
        result["bypass_reason"] = (
            "protected file tampering or unsafe/unexpected repository entry; no code executed"
        )
        (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    before_git, before_tree = _tree_hash(root, git_only=True), _tree_hash(root)
    commands = []
    environment = dict(os.environ)
    environment.update(PYTHONPATH=str(root / "src"), PYTHONDONTWRITEBYTECODE="1")
    compiled = artifacts / "compiled"
    compiled.mkdir(exist_ok=True)
    if spec["language"] == "typescript":
        node = shutil.which("node")
        compiler = Path(__file__).resolve().parents[1] / "frontend/node_modules/typescript/bin/tsc"
        if not node or not compiler.is_file():
            raise RuntimeError(
                "existing local Node/TypeScript compiler required; no installation performed"
            )
        command = [
            node,
            str(compiler),
            "--ignoreConfig",
            "--module",
            "node16",
            "--target",
            "es2022",
            "--moduleResolution",
            "node16",
            "--rewriteRelativeImportExtensions",
            "--skipLibCheck",
            "--noEmitOnError",
            "--outDir",
            str(compiled),
        ]
        command += [str(path) for path in sorted((root / "src").glob("*.ts"))]
        commands.append(_command(command, root, artifacts / "typecheck", environment))
        package_type = "module" if spec["repository"] == "hookable" else "commonjs"
        (compiled / "package.json").write_text(json.dumps({"type": package_type}) + "\n")
    for stage, statements in (
        ("behavior", spec["behavior"]),
        ("smoke", _smokes(spec["repository"])),
    ):
        oracle = artifacts / (stage + (".py" if spec["language"] == "python" else ".test.mjs"))
        oracle.write_text(_oracle(spec, statements, stage, compiled))
        command = (
            [sys.executable, str(oracle)]
            if spec["language"] == "python"
            else [str(shutil.which("node")), "--test", "--test-reporter=tap", str(oracle)]
        )
        commands.append(_command(command, root, artifacts / stage, environment))
    checks = [
        _test_execution_integrity(command, spec["language"], stage)
        for stage, command in zip(("behavior", "smoke"), commands[-2:])
    ]
    execution_safe = before_git == _tree_hash(root, git_only=True) and before_tree == _tree_hash(
        root
    )
    success = (
        execution_safe
        and all(check["valid"] for check in checks)
        and all(command["exit_code"] == 0 for command in commands)
    )
    result.update(
        success=success,
        passed=success,
        exit_code=0 if success else 1,
        commands=commands,
        test_count=sum(command["counts"].get("tests", 0) for command in commands),
        test_execution_integrity=checks,
        execution_did_not_mutate_tree_or_git=execution_safe,
    )
    (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def validate_corpus(destination: Path) -> dict[str, Any]:
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    receipts = []
    for spec in SPECS:
        task_id = spec["id"]
        root = destination / task_id / "repository"
        build_task_repo(task_id, root)
        baseline = grade_task(root, task_id, artifact_dir=destination / task_id / "baseline")
        apply_reference_fix(root, task_id)
        reference = grade_task(root, task_id, artifact_dir=destination / task_id / "reference")
        (root / spec["path"]).write_bytes(_source_bytes(spec, "partial"))
        partial = grade_task(root, task_id, artifact_dir=destination / task_id / "partial")
        receipts.append(
            {
                "task_id": task_id,
                "baseline_failed": not baseline["success"],
                "reference_passed": reference["success"],
                "partial_failed": not partial["success"],
                "baseline": baseline,
                "reference": reference,
                "partial": partial,
            }
        )
    result = {
        "corpus_version": CORPUS_VERSION,
        "tasks": receipts,
        "valid": all(
            row["baseline_failed"] and row["reference_passed"] and row["partial_failed"]
            for row in receipts
        ),
        "model_requests": 0,
    }
    (destination / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def fixture_paths() -> list[Path]:
    return [path for path in sorted(FIXTURES.rglob("*")) if path.is_file()]


def frozen_files() -> list[Path]:
    return [Path(__file__), MANIFEST, *fixture_paths()]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", type=Path)
    arguments = parser.parse_args()
    if arguments.validate:
        result = validate_corpus(arguments.validate)
        print(
            json.dumps(
                {"valid": result["valid"], "tasks": len(result["tasks"]), "model_requests": 0}
            )
        )
        raise SystemExit(0 if result["valid"] else 1)
    print(json.dumps(load_tasks(), indent=2))


if __name__ == "__main__":
    main()
