"""Fresh known-file tasks for source-only versus source-and-test workflow evaluation.

Common prompts disclose source, supporting tests and exact offline test argv in
all arms. Held-out behavior remains outside worktrees; this is procedural
separation, not a security sandbox or a production-scale repository benchmark.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any

from benchmarks.corpus import _command
from benchmarks.corpus_cost import _test_execution_integrity

CORPUS_VERSION = "workflow-2.0.0"
REPOSITORIES = {
    "codec-python-workflow-v2": ("python", "codec"),
    "similarity-python-workflow-v2": ("python", "similarity"),
    "contracts-typescript-workflow-v2": ("typescript", "contracts"),
    "coordinates-typescript-workflow-v2": ("typescript", "coordinates"),
}
SPECS: list[dict[str, Any]] = []


def _clean(source: str) -> str:
    return textwrap.dedent(source).strip("\n") + "\n"


def _add(
    repository: str,
    slug: str,
    function: str,
    request: str,
    source: str,
    replacements: dict[str, str],
    smokes: list[str],
    cases: str,
    *,
    adapter: str | None = None,
    adapter_replacements: dict[str, str] | None = None,
    supplied: bool = False,
) -> None:
    baseline = _clean(source)
    reference = baseline
    for old, new in replacements.items():
        if reference.count(old) != 1:
            raise ValueError(f"nonunique domain reference edit: {slug}")
        reference = reference.replace(old, new)
    adapter_baseline = _clean(adapter) if adapter is not None else None
    adapter_reference = adapter_baseline
    for old, new in (adapter_replacements or {}).items():
        if adapter_reference is None or adapter_reference.count(old) != 1:
            raise ValueError(f"nonunique adapter reference edit: {slug}")
        adapter_reference = adapter_reference.replace(old, new)
    if len(smokes) != 5:
        raise ValueError("each task needs five protected ordinary-use tests")
    SPECS.append(
        dict(
            repository=repository,
            slug=slug,
            function=function,
            request=request,
            baseline=baseline,
            reference=reference,
            adapter_baseline=adapter_baseline,
            adapter_reference=adapter_reference,
            supplied=supplied,
            smokes=smokes,
            cases=_clean(cases),
        )
    )


_add(
    "codec-python-workflow-v2",
    "glob-literal-escape",
    "escape_glob",
    "Repair escape_glob(text) so a literal filename matches itself with fnmatch.fnmatchcase. Escape each original star as [*], question mark as [?], and opening square bracket as [[]. Preserve closing brackets, backslashes, Unicode and every other character. Escapes must be based on original characters, never reprocessed.",
    """
    def escape_glob(text):
        return text.replace("*", "[*]").replace("?", "[?]").replace("[", "[[]")
    """,
    {
        'return text.replace("*", "[*]").replace("?", "[?]").replace("[", "[[]")': 'return "".join({"*": "[*]", "?": "[?]", "[": "[[]"}.get(char, char) for char in text)'
    },
    [
        'self.assertEqual(core.escape_glob("abc"),"abc")',
        'self.assertEqual(core.escape_glob(""),"")',
        'self.assertEqual(core.escape_glob("]"),"]")',
        'self.assertEqual(core.escape_glob("a-b.txt"),"a-b.txt")',
        'self.assertEqual(core.escape_glob("café"),"café")',
    ],
    """
    def test_original_metacharacters_once(self):
        self.assertEqual(core.escape_glob("a*?[b]"),"a[*][?][[]b]")
        self.assertEqual(core.escape_glob("[?*"),"[[][?][*]")
    def test_literal_matching_and_preservation(self):
        import fnmatch
        for name in ["*", "?", "[abc]", "a*b?.txt", "雪[?]", "a\\\\b"]:
            self.assertTrue(fnmatch.fnmatchcase(name,core.escape_glob(name)))
        self.assertFalse(fnmatch.fnmatchcase("axb",core.escape_glob("a*b")))
    """,
)
_add(
    "codec-python-workflow-v2",
    "unsigned-varint-batch",
    "encode_unsigned",
    "Repair encode_unsigned(value) for nonnegative Python integers: produce unsigned base-128 varint bytes, least-significant seven-bit groups first; every nonfinal group has bit 0x80 set and zero is one zero byte. encode_values(values) must concatenate encodings in caller order without sorting or mutating the input. Integers may exceed 64 bits.",
    """
    def encode_unsigned(value):
        result = bytearray()
        while value > 128:
            result.append((value & 127) | 128)
            value >>= 7
        result.append(value)
        return bytes(result)
    """,
    {"while value > 128:": "while value >= 128:"},
    [
        'self.assertEqual(core.encode_unsigned(0),b"\\x00")',
        'self.assertEqual(core.encode_unsigned(1),b"\\x01")',
        'self.assertEqual(core.encode_unsigned(127),b"\\x7f")',
        'self.assertEqual(api.encode_values([]),b"")',
        'self.assertEqual(api.encode_values([1,2]),b"\\x01\\x02")',
    ],
    """
    def test_continuation_boundaries_and_large_values(self):
        self.assertEqual(core.encode_unsigned(128),b"\\x80\\x01")
        self.assertEqual(core.encode_unsigned(16384),b"\\x80\\x80\\x01")
        self.assertEqual(core.encode_unsigned(1 << 70),b"\\x80"*10+b"\\x01")
    def test_batch_order_and_nonmutation(self):
        values=[128,1,0,16384]; before=list(values)
        self.assertEqual(api.encode_values(values),b"\\x80\\x01\\x01\\x00\\x80\\x80\\x01")
        self.assertEqual(values,before)
    """,
    adapter="""
    from .unsigned_varint_batch import encode_unsigned
    def encode_values(values):
        return b"".join(encode_unsigned(value) for value in sorted(values))
    """,
    adapter_replacements={"for value in sorted(values)": "for value in values"},
)
_add(
    "codec-python-workflow-v2",
    "roman-subtractive",
    "roman_numeral",
    "Repair roman_numeral(value) for integers 1 through 3999 using canonical uppercase Roman numerals, including subtractive pairs IV, IX, XL, XC, CD and CM. Do not change the public function signature.",
    """
    def roman_numeral(value):
        symbols=((1000,"M"),(500,"D"),(100,"C"),(50,"L"),(10,"X"),(5,"V"),(1,"I"))
        parts=[]
        for amount,symbol in symbols:
            count,value=divmod(value,amount)
            parts.append(symbol*count)
        return "".join(parts)
    """,
    {
        'symbols=((1000,"M"),(500,"D"),(100,"C"),(50,"L"),(10,"X"),(5,"V"),(1,"I"))': 'symbols=((1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I"))'
    },
    [
        'self.assertEqual(core.roman_numeral(1),"I")',
        'self.assertEqual(core.roman_numeral(3),"III")',
        'self.assertEqual(core.roman_numeral(5),"V")',
        'self.assertEqual(core.roman_numeral(10),"X")',
        'self.assertEqual(core.roman_numeral(2023),"MMXXIII")',
    ],
    """
    def test_subtractive_pairs(self):
        for value,expected in [(4,"IV"),(9,"IX"),(40,"XL"),(90,"XC"),(400,"CD"),(900,"CM")]:
            self.assertEqual(core.roman_numeral(value),expected)
    def test_combinations_and_upper_limit(self):
        self.assertEqual(core.roman_numeral(1994),"MCMXCIV")
        self.assertEqual(core.roman_numeral(3999),"MMMCMXCIX")
        self.assertEqual(core.roman_numeral(944),"CMXLIV")
    """,
    supplied=True,
)
_add(
    "similarity-python-workflow-v2",
    "bit-hamming-distance",
    "hamming_distance",
    "Repair hamming_distance(left,right) for equal-length nonempty strings containing only ASCII zero and one: count positions with different bits, preserving leading zeros. Inputs may be arbitrarily long. Do not compute numeric distance between the encoded integers.",
    """
    def hamming_distance(left,right):
        return abs(int(left,2)-int(right,2))
    """,
    {"return abs(int(left,2)-int(right,2))": "return sum(a != b for a,b in zip(left,right))"},
    [
        'self.assertEqual(core.hamming_distance("0","0"),0)',
        'self.assertEqual(core.hamming_distance("1","0"),1)',
        'self.assertEqual(core.hamming_distance("11","10"),1)',
        'self.assertEqual(core.hamming_distance("00","01"),1)',
        'self.assertEqual(core.hamming_distance("111","111"),0)',
    ],
    """
    def test_position_count_not_numeric_distance(self):
        self.assertEqual(core.hamming_distance("1000","0111"),4)
        self.assertEqual(core.hamming_distance("1010","0101"),4)
    def test_leading_zeros_and_long_values(self):
        self.assertEqual(core.hamming_distance("0001","1001"),1)
        self.assertEqual(core.hamming_distance("10"*100,"01"*100),200)
        self.assertEqual(core.hamming_distance("0"*200,"0"*199+"1"),1)
    """,
)
_add(
    "similarity-python-workflow-v2",
    "jaccard-stable-selection",
    "jaccard_score",
    "Repair jaccard_score(left,right) for lists of hashable strings: intersection size divided by union size of DISTINCT values; two empty sets have score 1. most_similar(candidates,reference) returns the index of the candidate with largest score, choosing the earliest index on a tie, or None for no candidates. Do not mutate inputs.",
    """
    def jaccard_score(left,right):
        union=set(left)|set(right)
        if not union:
            return 1.0
        return len(set(left)&set(right))/(len(left)+len(right)-len(set(left)&set(right)))
    """,
    {
        "return len(set(left)&set(right))/(len(left)+len(right)-len(set(left)&set(right)))": "return len(set(left)&set(right))/len(union)"
    },
    [
        "self.assertEqual(core.jaccard_score([],[]),1.0)",
        'self.assertEqual(core.jaccard_score(["a"],["a"]),1.0)',
        'self.assertEqual(core.jaccard_score(["a"],["b"]),0.0)',
        "self.assertIsNone(api.most_similar([],[]))",
        'self.assertEqual(api.most_similar([["a"]],["a"]),0)',
    ],
    """
    def test_distinct_set_denominator(self):
        self.assertEqual(core.jaccard_score(["a","a"],["a","b","b"]),0.5)
        self.assertEqual(core.jaccard_score(["x","x"],["x","x"]),1.0)
    def test_earliest_tie_and_nonmutation(self):
        candidates=[["a"],["a"],["b"]]; before=[list(row) for row in candidates]
        self.assertEqual(api.most_similar(candidates,["a"]),0)
        self.assertEqual(api.most_similar([["a","a"],["a","b"]],["a"]),0)
        self.assertEqual(candidates,before)
    """,
    adapter="""
    from .jaccard_stable_selection import jaccard_score
    def most_similar(candidates,reference):
        best=None
        best_score=-1.0
        for index,candidate in enumerate(candidates):
            score=jaccard_score(candidate,reference)
            if score >= best_score:
                best,best_score=index,score
        return best
    """,
    adapter_replacements={"if score >= best_score:": "if score > best_score:"},
)
_add(
    "contracts-typescript-workflow-v2",
    "luhn-checksum",
    "luhnCheck",
    "Repair luhnCheck(value): accept nonempty ASCII digit strings whose Luhn checksum is divisible by ten. Moving left from the rightmost digit, double every second digit and subtract nine if that doubled digit exceeds nine. Reject empty strings and any nondigit; preserve leading zeros. Do not parse the whole string as a number.",
    """
    export function luhnCheck(value: string): boolean {
      if (!/^[0-9]+$/.test(value)) return false;
      return [...value].reduce((sum,digit)=>sum+Number(digit),0)%10===0;
    }
    """,
    {
        "return [...value].reduce((sum,digit)=>sum+Number(digit),0)%10===0;": "let total=0;\n  for (let i=value.length-1, offset=0;i>=0;i--,offset++) {\n    let digit=Number(value[i]);\n    if (offset%2===1) {digit*=2;if(digit>9)digit-=9;}\n    total+=digit;\n  }\n  return total%10===0;"
    },
    [
        'assert.equal(core.luhnCheck("0"),true)',
        'assert.equal(core.luhnCheck("00"),true)',
        'assert.equal(core.luhnCheck("11"),false)',
        'assert.equal(core.luhnCheck(""),false)',
        'assert.equal(core.luhnCheck(" 0"),false)',
    ],
    """
    test("alternating doubling and reduction",()=>{
      assert.equal(core.luhnCheck("4111111111111111"),true);
      assert.equal(core.luhnCheck("4111111111111112"),false);
      assert.equal(core.luhnCheck("18"),true);
    });
    test("leading zeros parity and strict syntax",()=>{
      assert.equal(core.luhnCheck("0018"),true);assert.equal(core.luhnCheck("00018"),true);
      assert.equal(core.luhnCheck("79927398713"),true);assert.equal(core.luhnCheck("18x"),false);
      assert.equal(core.luhnCheck("１８"),false);
    });
    """,
)
_add(
    "contracts-typescript-workflow-v2",
    "natural-stable-sort",
    "compareNatural",
    "Repair compareNatural(left,right): split strings into maximal ASCII digit and nondigit runs. Compare pairs of digit runs by exact integer value, ignoring leading zeros; otherwise compare runs by JavaScript case-sensitive lexical order. The first different run decides; if all paired runs tie, fewer runs sorts first; otherwise return zero. sortedNatural(values) returns a stable naturally sorted NEW array and never mutates values. Numeric runs may exceed safe integers.",
    """
    export function compareNatural(left: string,right: string): number {
      return left < right ? -1 : left > right ? 1 : 0;
    }
    """,
    {
        "return left < right ? -1 : left > right ? 1 : 0;": "const a=left.match(/[0-9]+|[^0-9]+/g) ?? [];\n  const b=right.match(/[0-9]+|[^0-9]+/g) ?? [];\n  for (let i=0;i<Math.min(a.length,b.length);i++) {\n    if (/^[0-9]+$/.test(a[i]) && /^[0-9]+$/.test(b[i])) {\n      const x=BigInt(a[i]),y=BigInt(b[i]);if(x!==y)return x<y?-1:1;\n    } else if (a[i]!==b[i]) return a[i]<b[i]?-1:1;\n  }\n  return a.length<b.length?-1:a.length>b.length?1:0;"
    },
    [
        'assert.equal(core.compareNatural("a","b"),-1)',
        'assert.equal(core.compareNatural("same","same"),0)',
        'assert.equal(core.compareNatural("z","a"),1)',
        "assert.deepEqual(api.sortedNatural([]),[])",
        'assert.deepEqual(api.sortedNatural(["a","b"]),["a","b"])',
    ],
    """
    test("numeric runs use exact integer values",()=>{
      assert.equal(core.compareNatural("item2","item10"),-1);
      assert.equal(core.compareNatural("x0002","x2"),0);
      assert.equal(core.compareNatural("x9007199254740993","x9007199254740992"),1);
    });
    test("sorting is stable and does not mutate",()=>{
      const values=["x10","x2","x02","x1"];const before=[...values];
      assert.deepEqual(api.sortedNatural(values),["x1","x2","x02","x10"]);
      assert.deepEqual(values,before);assert.equal(core.compareNatural("a","a1"),-1);
    });
    """,
    adapter="""
    import {compareNatural} from "./natural_stable_sort.ts";
    export function sortedNatural(values: string[]): string[] {
      return values.sort(compareNatural);
    }
    """,
    adapter_replacements={
        "return values.sort(compareNatural);": "return [...values].sort(compareNatural);"
    },
)
_add(
    "contracts-typescript-workflow-v2",
    "unicode-common-prefix",
    "commonPrefix",
    "Repair commonPrefix(values) to return the longest prefix shared by every string, measured at complete Unicode code point boundaries. An empty array returns an empty string. Preserve case and Unicode exactly and do not mutate the array. A shared high surrogate alone is not a complete common code point.",
    """
    export function commonPrefix(values: string[]): string {
      return values[0] ?? "";
    }
    """,
    {
        'return values[0] ?? "";': 'const points=Array.from(values[0] ?? "");\n  while(points.length && !values.every(value=>value.startsWith(points.join("")))) points.pop();\n  return points.join("");'
    },
    [
        'assert.equal(core.commonPrefix([]),"")',
        'assert.equal(core.commonPrefix(["abc"]),"abc")',
        'assert.equal(core.commonPrefix(["same","same"]),"same")',
        'assert.equal(core.commonPrefix(["",""]),"")',
        'assert.equal(core.commonPrefix(["雪","雪山"]),"雪")',
    ],
    """
    test("longest prefix across every string",()=>{
      assert.equal(core.commonPrefix(["flower","flow","flight"]),"fl");
      assert.equal(core.commonPrefix(["abc","abc",""]),"");
      assert.equal(core.commonPrefix(["Alpha","alpha"]),"");
    });
    test("complete code points and unchanged input",()=>{
      const values=["🙂alpha","🙂beta"];const before=[...values];
      assert.equal(core.commonPrefix(values),"🙂");assert.deepEqual(values,before);
      assert.equal(core.commonPrefix(["😀a","😁b"]),"");
    });
    """,
    supplied=True,
)
_add(
    "coordinates-typescript-workflow-v2",
    "manhattan-symmetric",
    "manhattanDistance",
    "Repair manhattanDistance(a,b) for two finite number coordinate tuples: return abs(a.x-b.x)+abs(a.y-b.y). It must be symmetric, handle negative coordinates and fractional differences, and leave both tuples unchanged.",
    """
    export function manhattanDistance(a: [number,number],b: [number,number]): number {
      return (b[0]-a[0])+(b[1]-a[1]);
    }
    """,
    {"return (b[0]-a[0])+(b[1]-a[1]);": "return Math.abs(b[0]-a[0])+Math.abs(b[1]-a[1]);"},
    [
        "assert.equal(core.manhattanDistance([0,0],[0,0]),0)",
        "assert.equal(core.manhattanDistance([0,0],[1,0]),1)",
        "assert.equal(core.manhattanDistance([0,0],[0,1]),1)",
        "assert.equal(core.manhattanDistance([1,2],[3,4]),4)",
        "assert.equal(core.manhattanDistance([-3,-2],[-1,-1]),3)",
    ],
    """
    test("symmetric absolute differences",()=>{
      assert.equal(core.manhattanDistance([3,4],[1,2]),4);
      assert.equal(core.manhattanDistance([5,-2],[-1,3]),11);
    });
    test("fractions and unchanged tuples",()=>{
      const a=[-1.5,2.25],b=[0.5,-0.75];
      assert.equal(core.manhattanDistance(a,b),5);assert.equal(core.manhattanDistance(b,a),5);
      assert.deepEqual(a,[-1.5,2.25]);assert.deepEqual(b,[0.5,-0.75]);
    });
    """,
)
_add(
    "coordinates-typescript-workflow-v2",
    "bounded-cardinal-neighbors",
    "gridNeighbors",
    "Repair gridNeighbors(x,y,width,height) for valid integer coordinates inside a positive rectangular grid. Return only in-bounds cardinal neighbors, in left, right, up, down order. reachableNeighbors accepts the same arguments plus blocked, a readonly Set of exact 'x,y' keys, and removes blocked neighbors while preserving order. Never mutate blocked.",
    """
    export function gridNeighbors(x:number,y:number,width:number,height:number): [number,number][] {
      return [[x-1,y],[x+1,y],[x,y-1],[x,y+1]];
    }
    """,
    {
        "return [[x-1,y],[x+1,y],[x,y-1],[x,y+1]];": "const candidates:[number,number][]=[[x-1,y],[x+1,y],[x,y-1],[x,y+1]];\n  return candidates.filter(([a,b])=>a>=0 && a<width && b>=0 && b<height);"
    },
    [
        "assert.deepEqual(core.gridNeighbors(1,1,3,3),[[0,1],[2,1],[1,0],[1,2]])",
        "assert.equal(core.gridNeighbors(2,2,5,5).length,4)",
        "assert.deepEqual(api.reachableNeighbors(1,1,3,3,new Set()),[[0,1],[2,1],[1,0],[1,2]])",
        'assert.equal(api.reachableNeighbors(2,2,5,5,new Set(["0,0"])).length,4)',
        "assert.deepEqual(core.gridNeighbors(3,2,7,5),[[2,2],[4,2],[3,1],[3,3]])",
    ],
    """
    test("grid edges and singleton dimensions",()=>{
      assert.deepEqual(core.gridNeighbors(0,0,2,2),[[1,0],[0,1]]);
      assert.deepEqual(core.gridNeighbors(0,0,1,1),[]);
      assert.deepEqual(core.gridNeighbors(0,1,1,3),[[0,0],[0,2]]);
    });
    test("blocked neighbors order and set preservation",()=>{
      const blocked=new Set(["0,1","1,0"]);const before=[...blocked];
      assert.deepEqual(api.reachableNeighbors(1,1,3,3,blocked),[[2,1],[1,2]]);
      assert.deepEqual([...blocked],before);assert.deepEqual(api.reachableNeighbors(0,0,2,2,new Set(["1,0"])),[[0,1]]);
    });
    """,
    adapter="""
    import {gridNeighbors} from "./bounded_cardinal_neighbors.ts";
    export function reachableNeighbors(x:number,y:number,width:number,height:number,blocked:ReadonlySet<string>): [number,number][] {
      return gridNeighbors(x,y,width,height);
    }
    """,
    adapter_replacements={
        "return gridNeighbors(x,y,width,height);": "return gridNeighbors(x,y,width,height).filter(([a,b])=>!blocked.has(`${a},${b}`));"
    },
)


def _task_id(spec: dict[str, Any]) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    return f"{'py' if language == 'python' else 'ts'}-workflow2-{family}-{spec['slug']}"


def _spec(task_id: str) -> dict[str, Any]:
    for spec in SPECS:
        if _task_id(spec) == task_id:
            return spec
    raise ValueError(f"unknown task: {task_id}")


def _source_paths(spec: dict[str, Any]) -> list[str]:
    language, family = REPOSITORIES[spec["repository"]]
    directory, suffix = (family, "py") if language == "python" else ("src", "ts")
    module = spec["slug"].replace("-", "_")
    paths = [f"{directory}/{module}.{suffix}"]
    if spec["adapter_baseline"] is not None:
        paths.append(f"{directory}/{module}_api.{suffix}")
    return paths


def build_repository(repository_id: str, destination: Path) -> None:
    files = _repository_files(repository_id)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("destination must be empty")
    for relative, content in files.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _oracle(spec: dict[str, Any], worktree: Path) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    paths = _source_paths(spec)
    if language == "python":
        module = spec["slug"].replace("-", "_")
        source = "import json, unittest\nfrom datetime import date, datetime\n"
        source += f"from {family} import {module} as core\n"
        if len(paths) == 2:
            source += f"from {family} import {module}_api as api\n"
        source += "\nclass BehaviorTests(unittest.TestCase):\n" + textwrap.indent(
            spec["cases"], "    "
        )
        source += _clean("""
            if __name__ == "__main__":
                suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
                result = unittest.TextTestRunner(verbosity=2).run(suite)
                print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
                raise SystemExit(not result.wasSuccessful())
        """)
        return source
    source = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
    source += f"import * as core from {json.dumps((worktree / paths[0]).resolve().as_uri())};\n"
    if len(paths) == 2:
        source += f"import * as api from {json.dumps((worktree / paths[1]).resolve().as_uri())};\n"
    return source + spec["cases"]


def grade(task_id: str, worktree: Path, artifacts: Path) -> dict[str, Any]:
    spec = _spec(task_id)
    language, family = REPOSITORIES[spec["repository"]]
    worktree, artifacts = Path(worktree).resolve(), Path(artifacts).resolve()
    if artifacts == worktree or worktree in artifacts.parents:
        raise ValueError("grading artifacts must be outside the agent worktree")
    artifacts.mkdir(parents=True, exist_ok=True)
    protected = []
    source_prefix = family + "/" if language == "python" else "src/"
    for relative, content in _repository_files(spec["repository"]).items():
        if relative.startswith(source_prefix):
            continue
        path = worktree / relative
        actual = path.read_bytes() if path.is_file() and not path.is_symlink() else b""
        expected = content.encode("utf-8")
        protected.append(
            {
                "file": relative,
                "unchanged": actual == expected,
                "expected_sha256": hashlib.sha256(expected).hexdigest(),
                "actual_sha256": hashlib.sha256(actual).hexdigest(),
            }
        )
    environment = dict(os.environ)
    commands = []
    if language == "python":
        environment.update(PYTHONPATH=str(worktree), PYTHONDONTWRITEBYTECODE="1")
        oracle = artifacts / "held_out.py"
        oracle.write_text(_oracle(spec, worktree), encoding="utf-8")
        commands.append(
            _command([sys.executable, str(oracle)], worktree, artifacts / "behavior", environment)
        )
        commands.append(
            _command(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                worktree,
                artifacts / "smoke",
                environment,
            )
        )
    else:
        node = shutil.which("node")
        if node is None:
            raise RuntimeError("Node with native TypeScript support is required")
        oracle = artifacts / "held_out.test.mjs"
        oracle.write_text(_oracle(spec, worktree), encoding="utf-8")
        commands.append(
            _command(
                [node, "--test", "--test-reporter=tap", str(oracle)],
                worktree,
                artifacts / "behavior",
                environment,
            )
        )
        commands.append(
            _command(
                [node, "--test", "--test-reporter=tap"],
                worktree,
                artifacts / "smoke",
                environment,
            )
        )
        local = Path(__file__).resolve().parents[1] / "frontend/node_modules/typescript/bin/tsc"
        compiler = os.environ.get("MEMGLIDE_BENCHMARK_TSC") or (
            str(local) if local.is_file() else shutil.which("tsc")
        )
        if compiler is None:
            commands.append(
                {
                    "command": ["tsc", "--project", "tsconfig.json"],
                    "exit_code": None,
                    "counts": {},
                    "unavailable_reason": "TypeScript compiler not installed",
                }
            )
        else:
            commands.append(
                _command(
                    [node, compiler, "--project", "tsconfig.json"],
                    worktree,
                    artifacts / "typecheck",
                    environment,
                )
            )
    execution_checks = [
        _test_execution_integrity(commands[0], language, "behavior"),
        _test_execution_integrity(commands[1], language, "smoke"),
    ]
    # A different test file can exit early while Node still runs its siblings.
    # Require every frozen ordinary test, not merely the legacy five-test floor.
    required_smokes = 5 * sum(row["repository"] == spec["repository"] for row in SPECS)
    smoke_total = commands[1]["counts"].get("tests")
    smoke_count_valid = type(smoke_total) is int and smoke_total >= required_smokes
    execution_checks[1]["required_test_count"] = {"minimum": required_smokes}
    execution_checks[1]["count_requirement_met"] = smoke_count_valid
    execution_checks[1]["valid"] = execution_checks[1]["valid"] and smoke_count_valid
    execution_complete = all(item["valid"] for item in execution_checks)
    tamper_free = all(item["unchanged"] for item in protected)
    passed = tamper_free and execution_complete and all(item["exit_code"] == 0 for item in commands)
    result = {
        "task_id": task_id,
        "repository": spec["repository"],
        "corpus_version": CORPUS_VERSION,
        "passed": passed,
        "success": passed,
        "exit_code": 0 if passed else 1,
        "commands": commands,
        "test_count": sum(item["counts"].get("tests", 0) for item in commands),
        "protected_files_unchanged": tamper_free,
        "protected_files": protected,
        "test_execution_complete": execution_complete,
        "test_execution_integrity": execution_checks,
        "grading_separation": "held-out files outside worktree; not cryptographically hidden",
    }
    (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _apply_reference_fix(task_id: str, destination: Path, *, side: str = "both") -> None:
    spec = _spec(task_id)
    paths = _source_paths(spec)
    if side not in ("both", "domain", "adapter"):
        raise ValueError("unsupported reference side")
    if side != "adapter":
        (destination / paths[0]).write_text(spec["reference"], encoding="utf-8")
    if side != "domain" and len(paths) == 2:
        (destination / paths[1]).write_text(spec["adapter_reference"], encoding="utf-8")


def _support_path(spec: dict[str, Any]) -> str:
    module = spec["slug"].replace("-", "_")
    return (
        f"tests/test_{module}.py"
        if REPOSITORIES[spec["repository"]][0] == "python"
        else f"tests/{module}.test.mjs"
    )


def _test_argv(language: str) -> list[str]:
    return (
        ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
        if language == "python"
        else ["node", "--test"]
    )


def _support_content(spec: dict[str, Any]) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    paths = _source_paths(spec)
    if language == "python":
        module = spec["slug"].replace("-", "_")
        source = f"import unittest\nfrom {family} import {module} as core\n"
        if len(paths) == 2:
            source += f"from {family} import {module}_api as api\n"
        source += "\nclass OrdinaryTests(unittest.TestCase):\n"
        for index, statement in enumerate(spec["smokes"]):
            source += f"    def test_ordinary_{index}(self):\n        {statement}\n\n"
        return source
    source = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
    source += f'import * as core from "../{paths[0]}";\n'
    if len(paths) == 2:
        source += f'import * as api from "../{paths[1]}";\n'
    for index, statement in enumerate(spec["smokes"]):
        source += f'test("ordinary-{index}",()=>{{{statement};}});\n'
    return source


def _repository_files(repository_id: str) -> dict[str, str]:
    if repository_id not in REPOSITORIES:
        raise ValueError(f"unsupported repository: {repository_id}")
    language, family = REPOSITORIES[repository_id]
    specs = [spec for spec in SPECS if spec["repository"] == repository_id]
    command = " ".join(_test_argv(language))
    files = {
        "README.md": f"# {family.title()} utilities\n\nOffline {language} helpers. Run `{command}`.\n",
        "AGENTS.md": f"# Development\nWork in this checkout; keep tests offline and deterministic.\nRun `{command}`. Preserve public interfaces. All existing tracked test files are READ-ONLY: keep their bytes identical.\nAdd regression tests ONLY in NEW test files; never append to, rewrite, rename, or delete existing tests.\nDo not modify dependency/build configuration or inspect benchmark machinery,\ngrading artifacts or files outside this repository.\n",
        ".gitignore": "__pycache__/\n*.pyc\nnode_modules/\n.cache/\n",
    }
    if language == "python":
        files[f"{family}/__init__.py"] = f'"""Offline {family} utilities."""\n'
    else:
        files["package.json"] = (
            json.dumps(
                {
                    "name": repository_id,
                    "private": True,
                    "type": "module",
                    "scripts": {"test": command},
                },
                indent=2,
            )
            + "\n"
        )
        files["tsconfig.json"] = (
            json.dumps(
                {
                    "compilerOptions": {
                        "target": "ES2022",
                        "module": "NodeNext",
                        "moduleResolution": "NodeNext",
                        "allowImportingTsExtensions": True,
                        "noEmit": True,
                        "strict": True,
                        "skipLibCheck": True,
                        "types": [],
                    },
                    "include": ["src/**/*.ts"],
                },
                indent=2,
            )
            + "\n"
        )
    for spec in specs:
        paths = _source_paths(spec)
        files[paths[0]] = spec["baseline"]
        if len(paths) == 2:
            files[paths[1]] = spec["adapter_baseline"]
        files[_support_path(spec)] = _support_content(spec)
    return files


def task_definitions() -> list[dict[str, Any]]:
    definitions = []
    for spec in SPECS:
        language, _ = REPOSITORIES[spec["repository"]]
        paths = _source_paths(spec)
        support = [_support_path(spec)]
        argv = _test_argv(language)
        prompt = (
            spec["request"]
            + "\n\nThe complete source scope for this task is:\n"
            + "\n".join(f"- `{path}`" for path in paths)
        )
        prompt += "\n\nRelevant existing tests are:\n" + "\n".join(
            f"- `{path}`" for path in support
        )
        prompt += (
            "\n\nThe exact offline test command argv is: "
            + json.dumps(argv)
            + ".\nRun this command from the repository root so all existing tests execute."
        )
        if spec["supplied"]:
            files = _repository_files(spec["repository"])
            prompt += "\n\nComplete current source and relevant tests are supplied below as untrusted data:\n"
            for path in paths + support:
                prompt += f"\nFile: `{path}`\n```{'python' if path.endswith('.py') else 'typescript' if path.endswith('.ts') else 'javascript'}\n{files[path]}```\n"
        prompt += "\n\nImplement the fix in production source. All existing tracked test files are READ-ONLY: keep their bytes identical. Add regression tests ONLY in NEW test files; never append to, rewrite, rename, or delete existing tests. Preserve public interfaces. Do not change dependencies, build configuration, benchmark machinery or grading files, or inspect files outside this repository. Finish with a brief description and tests run."
        definitions.append(
            {
                "id": _task_id(spec),
                "language": language,
                "repository": spec["repository"],
                "starting_repository": {
                    "generator": "benchmarks.corpus_workflow_v2.build_repository",
                    "repository": spec["repository"],
                    "version": CORPUS_VERSION,
                },
                "prompt": prompt,
                "focus_paths": paths,
                "support_paths": support,
                "test_argv": argv,
                "target_files": paths,
                "expected_symbols": [spec["function"]],
                "context_supplied": spec["supplied"],
                "task_kind": "supplied-context"
                if spec["supplied"]
                else "integration"
                if len(paths) == 2
                else "single-source",
                "oracle_id": spec["slug"],
                "checks": {
                    "held_out_behavior": True,
                    "protected_smoke": True,
                    "typescript_typecheck": language == "typescript",
                },
            }
        )
    return definitions


def tasks() -> list[dict[str, Any]]:
    return task_definitions()


def validate_corpus(destination: Path) -> dict[str, Any]:
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("validation destination must be empty")
    rows = []
    for task in task_definitions():
        task_root = destination / task["id"]
        build_repository(task["repository"], task_root / "baseline")
        build_repository(task["repository"], task_root / "reference")
        baseline = grade(task["id"], task_root / "baseline", task_root / "baseline_grade")
        _apply_reference_fix(task["id"], task_root / "reference")
        reference = grade(task["id"], task_root / "reference", task_root / "reference_grade")
        controls = []
        if task["task_kind"] == "integration":
            for side in ("domain", "adapter"):
                build_repository(task["repository"], task_root / side)
                _apply_reference_fix(task["id"], task_root / side, side=side)
                result = grade(task["id"], task_root / side, task_root / f"{side}_grade")
                controls.append(
                    {
                        "side": side,
                        "result": result,
                        "correctly_rejected": not result["success"]
                        and result["protected_files_unchanged"]
                        and result["commands"][0]["counts"].get("tests") == 2
                        and all(command["exit_code"] == 0 for command in result["commands"][1:]),
                    }
                )
        expected_smokes = 5 * sum(spec["repository"] == task["repository"] for spec in SPECS)
        valid = (
            not baseline["success"]
            and baseline["commands"][0]["exit_code"] != 0
            and baseline["commands"][0]["counts"].get("tests") == 2
            and all(command["exit_code"] == 0 for command in baseline["commands"][1:])
            and baseline["protected_files_unchanged"]
            and reference["success"]
            and reference["test_count"] == expected_smokes + 2
            and all(control["correctly_rejected"] for control in controls)
        )
        rows.append(
            {
                "task_id": task["id"],
                "valid": valid,
                "expected_smoke_tests": expected_smokes,
                "baseline": baseline,
                "reference": reference,
                "half_fix_controls": controls,
            }
        )
        print(json.dumps({"task_id": task["id"], "valid": valid}), flush=True)
    result = {
        "corpus_version": CORPUS_VERSION,
        "task_count": len(rows),
        "half_fix_controls": sum(len(row["half_fix_controls"]) for row in rows),
        "valid": all(row["valid"] for row in rows),
        "tasks": rows,
    }
    (destination / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()
    if args.write_manifest:
        args.write_manifest.write_text(
            json.dumps({"corpus_version": CORPUS_VERSION, "tasks": task_definitions()}, indent=2)
            + "\n"
        )
    if args.validate:
        result = validate_corpus(args.validate)
        raise SystemExit(not result["valid"])
