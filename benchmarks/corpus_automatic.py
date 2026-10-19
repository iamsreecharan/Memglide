"""Pinned, complete upstream trees with author-created source-discovery defects.

The twelve tasks are held out from ranker development. All source snapshots are
unaltered upstream bytes; only ``build_task_repo`` inserts a disclosed synthetic
defect. Reference edits and author-controlled graders stay outside agent trees.
This is procedural isolation, not a sandbox against a malicious coding agent.
No upstream build, package install, or repository-defined script is executed.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from benchmarks.corpus import _command
from benchmarks.corpus_cost import _test_execution_integrity

CORPUS_VERSION = "automatic-1.0.0"
FIXTURES = Path(__file__).with_name("automatic-fixtures")
MANIFEST = Path(__file__).with_name("tasks_automatic.json")

# Expected source paths and mutations are evaluator information, never discovery
# input. The public prompt is deliberately stored separately below.
SPECS: list[dict[str, Any]] = [
    {
        "id": "itsdangerous-base64-padding",
        "repository": "itsdangerous",
        "language": "python",
        "path": "src/itsdangerous/encoding.py",
        "original": 'string += b"=" * (-len(string) % 4)',
        "bug": 'string += b""',
        "partial": 'string += b"=" * (-len(string) % 4) if len(string) % 4 == 2 else b""',
        "request": "Repair URL-safe base64 decoding: unpadded text and byte tokens must decode consistently for every valid encoded length. Preserve the existing byte result, padded-input compatibility and malformed-data exception behavior.",
        "behavior": [
            'self.assertEqual(enc.base64_decode("Zg"),b"f"); self.assertEqual(enc.base64_decode(b"Zm8"),b"fo"); self.assertEqual(enc.base64_decode("Zm9v"),b"foo")',
            'self.assertEqual(enc.base64_decode("_w"),b"\\xff"); self.assertEqual(enc.base64_decode("Zg=="),b"f"); self.assertEqual(enc.base64_decode(""),b""); self.assertRaises(BadData,enc.base64_decode,"a")',
        ],
    },
    {
        "id": "itsdangerous-integer-decoding",
        "repository": "itsdangerous",
        "language": "python",
        "path": "src/itsdangerous/encoding.py",
        "original": 'return _bytes_to_int(bytestr.rjust(8, b"\\x00"))[0]',
        "bug": 'return _bytes_to_int(bytestr.ljust(8, b"\\x00"))[0]',
        "partial": 'return _bytes_to_int((bytestr.rjust(8, b"\\x00") if len(bytestr) == 1 else bytestr.ljust(8, b"\\x00")))[0]',
        "request": "Repair compact integer byte decoding. Values encoded in network byte order must survive a round trip, including zero, short encodings and the full unsigned 64-bit range. Preserve the existing integer API and overflow behavior.",
        "behavior": [
            'self.assertEqual(enc.bytes_to_int(b"\\x01"),1); self.assertEqual(enc.bytes_to_int(b"\\x01\\x00"),256); self.assertEqual(enc.bytes_to_int(b""),0)',
            'self.assertEqual(enc.bytes_to_int(b"\\x12\\x34"),0x1234); self.assertEqual(enc.bytes_to_int(enc.int_to_bytes(2**64-1)),2**64-1); self.assertRaises(Exception,enc.bytes_to_int,b"123456789")',
        ],
    },
    {
        "id": "itsdangerous-compressed-payloads",
        "repository": "itsdangerous",
        "language": "python",
        "path": "src/itsdangerous/url_safe.py",
        "original": 'base64d = b"." + base64d',
        "bug": "base64d = base64d",
        "partial": 'base64d = b"." + base64d if isinstance(obj, str) else base64d',
        "request": "Repair URL-safe serialization of compressible payloads. Newly issued compressed tokens must retain the compression marker understood by the loader and round-trip strings as well as structured Unicode data. Keep ordinary small payloads and signed-token verification working.",
        "behavior": [
            's=URLSafeSerializer("test-key"); value="a"*500; payload=s.dump_payload(value); self.assertTrue(payload.startswith(b".")); self.assertEqual(s.load_payload(payload),value)',
            's=URLSafeSerializer("test-key"); value={"東京":["repeat"*90,4]}; payload=s.dump_payload(value); self.assertTrue(payload.startswith(b".")); self.assertEqual(s.loads(s.dumps(value)),value); self.assertEqual(s.loads(s.dumps("x")),"x")',
        ],
    },
    {
        "id": "pyproject-hooks-path-containment",
        "repository": "pyproject-hooks",
        "language": "python",
        "path": "src/pyproject_hooks/_impl.py",
        "original": "if os.path.commonpath([norm_source, norm_requested]) != norm_source:",
        "bug": "if not norm_requested.startswith(norm_source):",
        "partial": 'if requested.startswith(".." ) or not norm_requested.startswith(norm_source):',
        "request": "Repair build-backend path containment validation. Relative backend paths may resolve inside the source tree, including the root, but must not escape into a sibling directory whose name shares the source directory prefix. Reject absolute paths as before and return normalized absolute paths for valid requests.",
        "behavior": [
            'root=os.path.join(tempfile.gettempdir(),"backend-project"); self.assertEqual(impl.norm_and_check(root,"."),os.path.abspath(root)); self.assertRaises(ValueError,impl.norm_and_check,root,"../backend-project-other"); self.assertRaises(ValueError,impl.norm_and_check,root,os.path.abspath("outside"))',
            'root=os.path.join(tempfile.gettempdir(),"backend-project"); self.assertRaises(ValueError,impl.norm_and_check,root,"inside/../../backend-project-other"); self.assertEqual(impl.norm_and_check(root,"a/../backend"),os.path.join(root,"backend")); self.assertEqual(impl.norm_and_check(root,"../backend-project"),root)',
        ],
    },
    {
        "id": "pyproject-hooks-runner-restoration",
        "repository": "pyproject-hooks",
        "language": "python",
        "path": "src/pyproject_hooks/_impl.py",
        "original": "        finally:\n            self._subprocess_runner = prev",
        "bug": "        except Exception:\n            raise\n        else:\n            self._subprocess_runner = prev",
        "partial": "        except RuntimeError:\n            self._subprocess_runner = prev\n            raise\n        else:\n            self._subprocess_runner = prev",
        "request": "Repair temporary build-backend runner overrides: after leaving an override scope, restore the exact prior runner even when the body raises. Nested scopes must restore their respective previous runners, and exceptions must continue to propagate unchanged.",
        "behavior": [
            'first=lambda *a,**k:None; second=lambda *a,**k:None; caller=impl.BuildBackendHookCaller(".","backend",runner=first)\n        with self.assertRaises(RuntimeError):\n            with caller.subprocess_runner(second):\n                self.assertIs(caller._subprocess_runner,second); raise RuntimeError("expected")\n        self.assertIs(caller._subprocess_runner,first)',
            'first=lambda *a,**k:None; second=lambda *a,**k:None; third=lambda *a,**k:None; caller=impl.BuildBackendHookCaller(".","backend",runner=first)\n        with caller.subprocess_runner(second):\n            with self.assertRaises(ValueError):\n                with caller.subprocess_runner(third):\n                    raise ValueError("expected")\n            self.assertIs(caller._subprocess_runner,second)\n        self.assertIs(caller._subprocess_runner,first)',
        ],
    },
    {
        "id": "pyproject-hooks-environment-isolation",
        "repository": "pyproject-hooks",
        "language": "python",
        "path": "src/pyproject_hooks/_impl.py",
        "original": "env = os.environ.copy()",
        "occurrences": 2,
        "bug": "env = os.environ",
        "partial": 'env = os.environ.copy() if cmd[0] == "ordinary" else os.environ',
        "request": "Repair subprocess environment isolation in both ordinary and quiet build-hook runners. Per-call extra environment variables must reach the child invocation without changing the parent process environment. Preserve inherited variables, working directory, failure checking and the quiet runner's output capture.",
        "behavior": [
            'with mock.patch.dict(os.environ,{"MEMGLIDE_CORPUS_PARENT":"kept"},clear=True):\n            with mock.patch.object(impl.subprocess,"run") as run:\n                impl.default_subprocess_runner(["ordinary"],cwd="example",extra_environ={"MEMGLIDE_CORPUS_CHILD":"once"})\n                self.assertEqual(run.call_args.kwargs["env"],{"MEMGLIDE_CORPUS_PARENT":"kept","MEMGLIDE_CORPUS_CHILD":"once"}); self.assertTrue(run.call_args.kwargs["check"])\n            self.assertEqual(dict(os.environ),{"MEMGLIDE_CORPUS_PARENT":"kept"})',
            'with mock.patch.dict(os.environ,{"MEMGLIDE_CORPUS_PARENT":"kept"},clear=True):\n            with mock.patch.object(impl.subprocess,"run") as run:\n                impl.quiet_subprocess_runner(["quiet"],cwd="example",extra_environ={"MEMGLIDE_CORPUS_PARENT":"child"})\n                self.assertEqual(run.call_args.kwargs["env"]["MEMGLIDE_CORPUS_PARENT"],"child"); self.assertEqual(run.call_args.kwargs["stdout"],impl.subprocess.PIPE); self.assertEqual(run.call_args.kwargs["stderr"],impl.subprocess.STDOUT)\n            self.assertEqual(dict(os.environ),{"MEMGLIDE_CORPUS_PARENT":"kept"})',
        ],
    },
    {
        "id": "mitt-handler-append-order",
        "repository": "mitt",
        "language": "typescript",
        "path": "src/index.ts",
        "original": "handlers.push(handler);",
        "bug": "handlers.unshift(handler);",
        "partial": "if (handlers.length === 1) handlers.push(handler); else handlers.unshift(handler);",
        "request": "Repair event-listener registration ordering. Multiple handlers for the same named event must run in registration order; wildcard listeners must preserve their own registration order and run after the named listeners. Keep the caller-provided event map and symbol event support.",
        "behavior": [
            "const emitter=mitt(); const seen=[]; emitter.on('tick',()=>seen.push('first')); emitter.on('tick',()=>seen.push('second')); emitter.emit('tick',1); assert.deepEqual(seen,['first','second']);",
            "const emitter=mitt(); const seen=[]; const key=Symbol('tick'); for(const n of [1,2,3])emitter.on(key,()=>seen.push(n)); for(const n of [4,5,6])emitter.on('*',()=>seen.push(n)); emitter.emit(key,{}); assert.deepEqual(seen,[1,2,3,4,5,6]);",
        ],
    },
    {
        "id": "mitt-absent-handler-removal",
        "repository": "mitt",
        "language": "typescript",
        "path": "src/index.ts",
        "original": "handlers.splice(handlers.indexOf(handler) >>> 0, 1);",
        "bug": "handlers.splice(handlers.indexOf(handler), 1);",
        "partial": 'if (type !== "*") { const index = handlers.indexOf(handler); if(index >= 0) handlers.splice(index, 1); } else handlers.splice(handlers.indexOf(handler),1);',
        "request": "Repair removing an unregistered event handler: it must leave all registered handlers untouched. Cover both named events and wildcard handlers, while keeping removal of a registered handler and removal of all handlers working.",
        "behavior": [
            "const emitter=mitt(); const seen=[]; const a=()=>seen.push('a'); const b=()=>seen.push('b'); emitter.on('x',a); emitter.on('x',b); emitter.off('x',()=>{}); emitter.emit('x'); assert.deepEqual(seen,['a','b']); emitter.off('x',a); seen.length=0; emitter.emit('x'); assert.deepEqual(seen,['b']);",
            "const emitter=mitt(); const seen=[]; emitter.on('*',(t,v)=>seen.push([t,v])); emitter.off('*',()=>{}); emitter.emit('x',3); assert.deepEqual(seen,[['x',3]]); emitter.off('*'); emitter.emit('x',4); assert.equal(seen.length,1);",
        ],
    },
    {
        "id": "mitt-emission-snapshots",
        "repository": "mitt",
        "language": "typescript",
        "path": "src/index.ts",
        "original": ".slice()\n\t\t\t\t\t.map((handler)",
        "occurrences": 2,
        "bug": ".map((handler)",
        "partial": ".map((handler)",
        "partial_occurrences": 1,
        "request": "Repair event emission when listeners unregister other listeners during delivery. Each named-event and wildcard handler list must be delivered from a stable snapshot for that emission; a removal should affect subsequent emissions without skipping a listener already present in the current snapshot.",
        "behavior": [
            "const emitter=mitt(); const seen=[]; const b=()=>seen.push('b'); emitter.on('x',()=>{seen.push('a');emitter.off('x',b)}); emitter.on('x',b); emitter.emit('x'); emitter.emit('x'); assert.deepEqual(seen,['a','b','a']);",
            "const emitter=mitt(); const seen=[]; const b=()=>seen.push('b'); emitter.on('*',()=>{seen.push('a');emitter.off('*',b)}); emitter.on('*',b); emitter.emit('x'); emitter.emit('x'); assert.deepEqual(seen,['a','b','a']);",
        ],
    },
    {
        "id": "ufo-duplicate-query-values",
        "repository": "ufo",
        "language": "typescript",
        "path": "src/query.ts",
        "original": "object[key] = [object[key] as string, value];",
        "bug": "object[key] = value;",
        "partial": 'object[key] = key === "tag" ? [object[key] as string, value] : value;',
        "request": "Repair parsing repeated URL query keys. Preserve every decoded value in encounter order, including empty values and plus-encoded spaces. Single values remain strings, and unsafe prototype-related keys must still be ignored.",
        "behavior": [
            "const value=core.parseQuery('?tag=a&tag=b&tag=c&one=x'); assert.deepEqual(value.tag,['a','b','c']); assert.equal(value.one,'x');",
            "const value=core.parseQuery('q=&q=hello+world&q=%2B&__proto__=x&constructor=y'); assert.deepEqual(value.q,['','hello world','+']); assert.equal(Object.getPrototypeOf(value),null); assert.equal(Object.hasOwn(value,'constructor'),false);",
        ],
    },
    {
        "id": "ufo-query-plus-escaping",
        "repository": "ufo",
        "language": "typescript",
        "path": "src/encoding.ts",
        "original": '.replace(PLUS_RE, "%2B")\n      .replace(ENC_SPACE_RE, "+")',
        "bug": '.replace(ENC_SPACE_RE, "+")\n      .replace(PLUS_RE, "%2B")',
        "partial": '.replace(PLUS_RE, "%2B")\n      .replace(ENC_SPACE_RE, input === "hello world" ? "+" : "%2B")',
        "request": "Repair query-value encoding so spaces use plus notation while literal plus signs remain percent-escaped. Mixed spaces, plus signs, Unicode and reserved delimiters must decode back to their original values without changing path-encoding behavior.",
        "behavior": [
            "assert.equal(core.encodeQueryValue('hello world'),'hello+world'); assert.equal(core.encodeQueryValue('a+b'),'a%2Bb');",
            "for(const value of ['a + b','東京 x+y','&?# =+'])assert.equal(core.decodeQueryValue(core.encodeQueryValue(value)),value); assert.equal(core.encodePath('a b'),'a%20b');",
        ],
    },
    {
        "id": "ufo-path-fragment-boundaries",
        "repository": "ufo",
        "language": "typescript",
        "path": "src/parse.ts",
        "original": "input.match(/([^#?]*)(\\?[^#]*)?(#.*)?/) || []",
        "bug": "input.match(/([^#?]*)(\\?.*)?(#.*)?/) || []",
        "partial": 'input.match(input.startsWith("/one?") ? /([^#?]*)(\\?[^#]*)?(#.*)?/ : /([^#?]*)(\\?.*)?(#.*)?/) || []',
        "request": "Repair splitting URL paths into pathname, query and fragment. A fragment after a query must stay separate, and question marks inside a fragment belong to the fragment. Preserve empty parts and full URL parsing through the same helper.",
        "behavior": [
            "assert.deepEqual(core.parsePath('/one?x=1#two'),{pathname:'/one',search:'?x=1',hash:'#two'}); assert.deepEqual(core.parsePath('/one#two?x=1'),{pathname:'/one',search:'',hash:'#two?x=1'});",
            "assert.deepEqual(core.parsePath('/other?x=#a?b'),{pathname:'/other',search:'?x=',hash:'#a?b'}); const value=core.parseURL('https://example.org/a?x=1#z'); assert.equal(value.search,'?x=1'); assert.equal(value.hash,'#z'); assert.deepEqual(core.parsePath(''),{pathname:'',search:'',hash:''});",
        ],
    },
]


def _spec(task_id: str) -> dict[str, Any]:
    for spec in SPECS:
        if spec["id"] == task_id:
            return spec
    raise ValueError(f"unknown automatic task: {task_id}")


def load_tasks() -> list[dict[str, Any]]:
    """Return prompts and evaluator-only source labels (not discovery hints)."""
    result = []
    for spec in SPECS:
        result.append(
            {
                "id": spec["id"],
                "repository": spec["repository"],
                "language": spec["language"],
                "prompt": spec["request"]
                + "\n\nInvestigate this repository and repair production code without new dependencies. Preserve public APIs. Existing tracked tests, docs, licenses and configuration are read-only; add regression tests in new test files only. Do not inspect files outside this repository or benchmark/grading machinery.",
                "known_paths": [spec["path"]],
                "focus_paths": [spec["path"]],
                "defect_origin": "author-created mutation of pinned upstream production code",
                "grading": "two external behavioral groups plus six external regression groups; upstream dependency-based suites not executed",
                "corpus_version": CORPUS_VERSION,
            }
        )
    return result


def _source_bytes(spec: dict[str, Any], variant: str) -> bytes:
    original = (FIXTURES / spec["repository"] / spec["path"]).read_text()
    count = spec.get("occurrences", 1)
    if original.count(spec["original"]) != count:
        raise ValueError(f"upstream edit not unique: {spec['id']}")
    if variant == "reference":
        return original.encode()
    replacements = spec.get("partial_occurrences", count) if variant == "partial" else count
    return original.replace(spec["original"], spec[variant], replacements).encode()


def build_task_repo(task_id: str, root: Path) -> dict[str, Any]:
    spec = _spec(task_id)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("task destination must be empty")
    source = FIXTURES / spec["repository"]
    shutil.copytree(source, root, dirs_exist_ok=True)
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


def _tree_hash(root: Path, *, git_only: bool = False) -> str:
    directory = root / ".git" if git_only else root
    if git_only and not directory.exists():
        return "absent"
    if directory.is_symlink():
        return "unsafe-symlink"
    if directory.is_file():
        # Worktree .git pointers are protected as bytes; referenced metadata is
        # managed and frozen by the runner rather than traversed here.
        return hashlib.sha256(directory.read_bytes()).hexdigest()
    files = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if not git_only and (relative.parts[0] == ".git" or "__pycache__" in relative.parts):
            continue
        if path.is_symlink():
            files[relative.as_posix()] = "symlink:" + os.readlink(path)
        elif path.is_file():
            files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def _protection(spec: dict[str, Any], root: Path) -> dict[str, Any]:
    initial = FIXTURES / spec["repository"]
    protected, unexpected = [], []
    original_names = set()
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
    if repository == "itsdangerous":
        return "from itsdangerous import encoding as enc\nfrom itsdangerous import URLSafeSerializer, BadData, Signer, BadSignature\n"
    return (
        "import os,tempfile\nfrom unittest import mock\nfrom pyproject_hooks import _impl as impl\n"
    )


def _smokes(repository: str) -> list[str]:
    if repository == "itsdangerous":
        return [
            'self.assertEqual(enc.want_bytes("東京"),"東京".encode())',
            'self.assertEqual(enc.base64_encode(b"foo"),b"Zm9v")',
            'self.assertEqual(enc.base64_decode("Zm9v"),b"foo")',
            'self.assertEqual(enc.int_to_bytes(256),b"\\x01\\x00")',
            's=Signer("key"); self.assertEqual(s.unsign(s.sign("data")),b"data"); self.assertRaises(BadSignature,s.unsign,b"tampered")',
            's=URLSafeSerializer("key"); self.assertEqual(s.loads(s.dumps({"a":1})),{"a":1})',
        ]
    if repository == "pyproject-hooks":
        return [
            'root=tempfile.gettempdir(); self.assertEqual(impl.norm_and_check(root,"."),root)',
            'caller=impl.BuildBackendHookCaller(".","backend"); self.assertEqual(caller.build_backend,"backend")',
            'caller=impl.BuildBackendHookCaller(".","backend",python_executable="custom"); self.assertEqual(caller.python_executable,"custom")',
            'error=impl.HookMissing("wheel"); self.assertEqual(error.hook_name,"wheel")',
            'error=impl.BackendUnavailable("trace","bad","backend",["path"]); self.assertEqual(error.backend_name,"backend"); self.assertIn("trace",str(error))',
            'with tempfile.TemporaryDirectory() as directory:\n            path=os.path.join(directory,"data.json"); impl.write_json({"東京":[1,2]},path); self.assertEqual(impl.read_json(path),{"東京":[1,2]})',
        ]
    if repository == "mitt":
        return [
            "const e=mitt(); assert.equal(e.all.size,0);",
            "const m=new Map(); const e=mitt(m); assert.equal(e.all,m);",
            "const e=mitt(); let got; e.on('x',v=>got=v); e.emit('x',3); assert.equal(got,3);",
            "const e=mitt(); let got; e.on('*',(t,v)=>got=[t,v]); e.emit('x',3); assert.deepEqual(got,['x',3]);",
            "const e=mitt(); const h=()=>{}; e.on('x',h); e.off('x'); assert.equal(e.all.get('x').length,0);",
            "const e=mitt(); const s=Symbol(); let n=0; e.on(s,()=>n++); e.emit(s); assert.equal(n,1);",
        ]
    return [
        "assert.equal(core.encodeQueryValue('plain'),'plain');",
        "assert.equal(core.decodeQueryValue('hello+world'),'hello world');",
        "assert.equal(core.parseQuery('a=1').a,'1');",
        "assert.equal(core.stringifyQuery({a:'x'}),'a=x');",
        "assert.equal(core.parseURL('https://example.org/path').host,'example.org');",
        "assert.equal(core.parsePath('/path').pathname,'/path');",
    ]


def _oracle(spec: dict[str, Any], statements: list[str], stage: str, compiled: Path) -> str:
    if spec["language"] == "python":
        source = "import json,unittest\n" + _python_imports(spec["repository"])
        source += "\nclass ExternalChecks(unittest.TestCase):\n"
        for index, statement in enumerate(statements):
            source += f"    def test_{stage}_{index}(self):\n        {statement}\n\n"
        source += (
            'if __name__ == "__main__":\n'
            "    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExternalChecks))\n"
            '    print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))\n'
            "    raise SystemExit(not result.wasSuccessful())\n"
        )
        return source
    module = compiled / "index.js"
    source = 'import test from "node:test";\nimport assert from "node:assert/strict";\nimport {createRequire} from "node:module";\nconst require=createRequire(import.meta.url);\n'
    source += f"const core=require({json.dumps(str(module))});\n"
    if spec["repository"] == "mitt":
        source += "const mitt=core.default;\n"
    for index, statement in enumerate(statements):
        source += f"test({json.dumps(stage + '-' + str(index))},()=>{{{statement}}});\n"
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
    if not protection["protected_files_unchanged"] or not protection["new_files_valid"]:
        result = {
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
            "bypass_reason": "protected file tampering or unsafe/unexpected repository entry; no code executed",
            **protection,
        }
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
                "existing local Node/TypeScript compiler required; no package installation performed"
            )
        command = [
            node,
            str(compiler),
            "--ignoreConfig",
            "--module",
            "node16",
            "--target",
            "es2020",
            "--moduleResolution",
            "node16",
            "--skipLibCheck",
            "--noEmitOnError",
            "--outDir",
            str(compiled),
        ]
        command += [str(path) for path in sorted((root / "src").glob("*.ts"))]
        commands.append(_command(command, root, artifacts / "typecheck", environment))
        (compiled / "package.json").write_text('{"type":"commonjs"}\n')
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
        protection["protected_files_unchanged"]
        and protection["new_files_valid"]
        and execution_safe
        and all(check["valid"] for check in checks)
        and all(command["exit_code"] == 0 for command in commands)
    )
    result = {
        "task_id": task_id,
        "repository": spec["repository"],
        "success": success,
        "passed": success,
        "exit_code": 0 if success else 1,
        "commands": commands,
        "test_count": sum(command["counts"].get("tests", 0) for command in commands),
        "test_execution_integrity": checks,
        "execution_did_not_mutate_tree_or_git": execution_safe,
        "corpus_version": CORPUS_VERSION,
        "scope": "author-controlled external behavior and regression checks, not full upstream suites",
        **protection,
    }
    (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def validate_corpus(destination: Path) -> dict[str, Any]:
    """Validate labels without models; never provide grade data to discovery."""
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
