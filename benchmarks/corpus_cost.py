"""Fresh cost-comparison coding tasks and independent, external behavioral oracles.

All task source scopes are disclosed in the common prompts. Two tasks also
include their complete relevant source. Reference fixes and hidden assertions
never enter an agent worktree; that separation is procedural, not a sandbox.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any

from benchmarks.corpus import _command

CORPUS_VERSION = "cost-1.0.0"
REPOSITORIES = {
    "inventory-python-cost": ("python", "inventory"),
    "reports-python-cost": ("python", "reports"),
    "ledger-typescript-cost": ("typescript", "ledger"),
    "geometry-typescript-cost": ("typescript", "geometry"),
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
    smoke: str,
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
            raise ValueError(f"nonunique domain reference edit: {slug}: {old!r}")
        reference = reference.replace(old, new)
    adapter_baseline = _clean(adapter) if adapter is not None else None
    adapter_reference = adapter_baseline
    for old, new in (adapter_replacements or {}).items():
        if adapter_reference is None or adapter_reference.count(old) != 1:
            raise ValueError(f"nonunique adapter reference edit: {slug}: {old!r}")
        adapter_reference = adapter_reference.replace(old, new)
    SPECS.append(
        {
            "repository": repository,
            "slug": slug,
            "function": function,
            "request": request,
            "baseline": baseline,
            "reference": reference,
            "adapter_baseline": adapter_baseline,
            "adapter_reference": adapter_reference,
            "supplied": supplied,
            "smoke": smoke,
            "cases": _clean(cases),
        }
    )


_add(
    "inventory-python-cost",
    "aggregate-stock",
    "aggregate_stock",
    "Fix aggregate_stock(rows): sum quantities for repeated SKU strings, preserving the first-seen SKU order. Each row is a (sku, quantity) pair with integer quantities, including negative adjustments and zero. Return a fresh dict, do not alter rows, and return {} for no rows.",
    '''
    def aggregate_stock(rows):
        """Combine a sequence of inventory movements into ordered SKU balances.

        Zero and negative movements are valid adjustments. SKU strings are
        literal, case-sensitive identifiers owned by the caller.
        """
        balances = {}
        for sku, quantity in rows:
            balances[sku] = quantity
        return balances
    ''',
    {"balances[sku] = quantity": "balances[sku] = balances.get(sku, 0) + quantity"},
    'self.assertEqual(core.aggregate_stock([("A",2),("B",3)]),{"A":2,"B":3})',
    """
    def test_repeated_skus_and_first_seen_order(self):
        rows=[("A",2),("B",4),("A",-1),("C",0),("B",3)]
        result=core.aggregate_stock(rows)
        self.assertEqual(result,{"A":1,"B":7,"C":0})
        self.assertEqual(list(result),["A","B","C"])
    def test_empty_case_sensitive_and_unchanged(self):
        rows=[("a",2),("A",1),("a",0)]
        self.assertEqual(core.aggregate_stock(rows),{"a":2,"A":1})
        self.assertEqual(rows,[("a",2),("A",1),("a",0)])
        self.assertEqual(core.aggregate_stock([]),{})
    """,
)
SPECS[-1]["extra_smokes"] = ["self.assertEqual(core.aggregate_stock([]),{})"]

_add(
    "inventory-python-cost",
    "reorder-inclusive",
    "reorder_needed",
    "Repair reorder_needed and reorder_skus. A product needs reorder when its integer stock is less than OR EQUAL to its threshold. reorder_skus receives ordered (sku,stock,threshold) rows and must return every matching SKU in input order, preserving case and duplicates. The adapter must not sort or deduplicate its results. Do not modify inputs.",
    '''
    def reorder_needed(stock, threshold):
        """Return whether an inventory balance has reached its reorder point.

        Negative stock and negative thresholds remain ordinary integers;
        callers choose policy values before invoking this comparison.
        """
        return stock < threshold
    ''',
    {"stock < threshold": "stock <= threshold"},
    'self.assertEqual(api.reorder_skus([("A",1,2),("B",4,2)]),["A"])',
    """
    def test_inclusive_boundary_and_public_order(self):
        self.assertTrue(core.reorder_needed(3,3))
        self.assertEqual(api.reorder_skus([("z",1,2),("A",2,2),("z",0,4)]),["z","A","z"])
    def test_negatives_empty_and_unchanged(self):
        rows=[("b",-2,-1),("a",2,1),("b",-1,-1)]
        self.assertEqual(api.reorder_skus(rows),["b","b"])
        self.assertEqual(rows,[("b",-2,-1),("a",2,1),("b",-1,-1)])
        self.assertEqual(api.reorder_skus([]),[])
        self.assertFalse(core.reorder_needed(2,1))
    """,
    adapter='''
    from .reorder_inclusive import reorder_needed

    def reorder_skus(rows):
        """Produce the display list for a reorder worksheet."""
        return sorted(set(sku for sku, stock, threshold in rows if reorder_needed(stock, threshold)))
    ''',
    adapter_replacements={
        "sorted(set(sku for sku, stock, threshold in rows if reorder_needed(stock, threshold)))": "[sku for sku, stock, threshold in rows if reorder_needed(stock, threshold)]"
    },
)
SPECS[-1]["extra_smokes"] = ["self.assertFalse(core.reorder_needed(8,2))"]

_add(
    "inventory-python-cost",
    "pack-ceiling",
    "packs_required",
    "Fix packs_required(units,pack_size): return the smallest number of full packs covering a nonnegative integer unit count, rounding upward. pack_size must be a positive integer. Reject booleans and all noninteger arguments with ValueError, and reject negative units or nonpositive pack_size. Zero units requires zero packs.",
    '''
    def packs_required(units, pack_size):
        """Convert a requested unit count into a whole number of shipping packs."""
        if type(units) is not int or type(pack_size) is not int:
            raise ValueError("integer arguments required")
        if units < 0 or pack_size <= 0:
            raise ValueError("invalid packing quantities")
        return units // pack_size
    ''',
    {"return units // pack_size": "return (units + pack_size - 1) // pack_size"},
    "self.assertEqual(core.packs_required(12,6),2)",
    """
    def test_round_up_and_large_exact_integer(self):
        for units,size,expected in ((1,6,1),(7,6,2),(0,3,0),(12,6,2),(10**30+1,10,10**29+1)):
            self.assertEqual(core.packs_required(units,size),expected)
    def test_invalid_arguments(self):
        for units,size in ((-1,2),(1,0),(1,-1),(True,2),(2,False),(2.0,2),(2,"2")):
            with self.assertRaises(ValueError): core.packs_required(units,size)
    """,
    supplied=True,
)
SPECS[-1]["extra_smokes"] = ["self.assertEqual(core.packs_required(0,4),0)"]

_add(
    "reports-python-cost",
    "csv-quoted-cell",
    "csv_cell",
    "Fix csv_cell(value) for string values: if it contains comma, double quote, CR or LF, wrap it in double quotes and double each existing double quote. Otherwise return it unchanged. Preserve all whitespace and Unicode, including leading/trailing spaces. Empty string returns ''.",
    '''
    def csv_cell(value):
        """Encode one string cell for a comma-delimited export.

        Callers assemble delimiters and row endings separately, so this
        helper must preserve every character of the supplied value.
        """
        if any(char in value for char in (",", '"', "\\r", "\\n")):
            return '"' + value + '"'
        return value
    ''',
    {"return '\"' + value + '\"'": "return '\"' + value.replace('\"', '\"\"') + '\"'"},
    'self.assertEqual(core.csv_cell("hello"),"hello")',
    '''
    def test_quotes_commas_and_linebreaks(self):
        for value,expected in [('a"b','"a""b"'),('"','""""'),('a,b','"a,b"'),('a\\nb','"a\\nb"'),('a\\rb','"a\\rb"')]:
            self.assertEqual(core.csv_cell(value),expected)
    def test_plain_empty_and_unicode(self):
        for value in (""," plain ","東京","tab\\tvalue"):
            self.assertEqual(core.csv_cell(value),value)
        self.assertEqual(core.csv_cell('É,"x"'),'"É,""x"""')
    ''',
)
SPECS[-1]["extra_smokes"] = [
    'self.assertEqual(core.csv_cell(""),"")',
    'self.assertEqual(core.csv_cell("a,b"),\'"a,b"\')',
]

_add(
    "reports-python-cost",
    "weighted-mean",
    "weighted_mean",
    "Repair weighted_mean and report_mean. Inputs are equally sized sequences of finite numeric values and nonnegative finite weights. Reject mismatched lengths, empty inputs, negative weights and zero total weight with ValueError. Compute sum(value*weight)/sum(weight), including fractional weights. report_mean must return that float unchanged, rather than round it to an integer. Do not mutate sequences.",
    '''
    import math

    def weighted_mean(values, weights):
        """Calculate an explicitly weighted numeric report statistic."""
        if len(values) != len(weights) or not values:
            raise ValueError("nonempty matching inputs required")
        if any(not math.isfinite(v) for v in values) or any(not math.isfinite(w) or w < 0 for w in weights):
            raise ValueError("finite values and nonnegative weights required")
        total = sum(weights)
        if total == 0:
            raise ValueError("positive total weight required")
        return sum(value * weight for value, weight in zip(values, weights)) / len(weights)
    ''',
    {"/ len(weights)": "/ total"},
    "self.assertEqual(api.report_mean([2,4],[1,1]),3)",
    """
    def test_weight_denominator_and_no_public_rounding(self):
        self.assertAlmostEqual(core.weighted_mean([10,20],[1,3]),17.5)
        self.assertAlmostEqual(api.report_mean([1,2],[0.25,0.75]),1.75)
        self.assertEqual(api.report_mean([2,100],[2,0]),2)
    def test_invalid_inputs_and_preservation(self):
        for values,weights in (([],[]),([1],[1,2]),([1],[-1]),([1],[0]),([float("inf")],[1]),([1],[float("nan")])):
            with self.assertRaises(ValueError): api.report_mean(values,weights)
        values=[2,4];weights=[1,2];api.report_mean(values,weights)
        self.assertEqual(values,[2,4]);self.assertEqual(weights,[1,2])
    """,
    adapter='''
    from .weighted_mean import weighted_mean

    def report_mean(values, weights):
        """Expose the statistic for a report renderer to format later."""
        return round(weighted_mean(values, weights))
    ''',
    adapter_replacements={
        "round(weighted_mean(values, weights))": "weighted_mean(values, weights)"
    },
)
SPECS[-1]["extra_smokes"] = [
    "self.assertEqual(core.weighted_mean([7],[1]),7)",
    "self.assertEqual(api.report_mean([0],[1]),0)",
]

_add(
    "ledger-typescript-cost",
    "signed-cents",
    "formatCents",
    "Fix formatCents(cents) for safe integer cents: return signed decimal money with exactly two fractional digits and no grouping, e.g. -5 -> '-0.05', 105 -> '1.05', 0 -> '0.00'. Reject non-safe-integers with RangeError. Compute from integer cents so rounding and negative remainder do not corrupt the fraction.",
    """
    export function formatCents(cents: number): string {
      // Keep this helper independent of locale and of floating currency input.
      if (!Number.isSafeInteger(cents)) throw new RangeError("integer cents required");
      const sign = cents < 0 ? "-" : "";
      const absolute = Math.abs(cents);
      const whole = Math.floor(absolute / 100);
      const fraction = String(absolute % 100);
      return sign + whole + "." + fraction;
    }
    """,
    {"String(absolute % 100)": 'String(absolute % 100).padStart(2,"0")'},
    'assert.equal(core.formatCents(1234),"12.34")',
    """
    test("small fractions and signs",()=>{
      for(const [value,expected] of [[0,"0.00"],[5,"0.05"],[-5,"-0.05"],[105,"1.05"],[-100,"-1.00"],[100,"1.00"]])assert.equal(core.formatCents(value),expected);
    });
    test("safe-integer validation and boundary",()=>{
      for(const value of [0.1,NaN,Infinity,Number.MAX_SAFE_INTEGER+1])assert.throws(()=>core.formatCents(value),RangeError);
      assert.equal(core.formatCents(Number.MAX_SAFE_INTEGER),"90071992547409.91");
    });
    """,
)
SPECS[-1]["extra_smokes"] = ['assert.equal(core.formatCents(-1234),"-12.34")']

_add(
    "ledger-typescript-cost",
    "receipt-quantity",
    "lineTotal",
    "Repair lineTotal and receiptTotal. A line has unitCents and quantity, both nonnegative safe integers. lineTotal must multiply them and reject invalid or unsafe products with RangeError. receiptTotal must sum every line total, including repeated lines, and reject unsafe cumulative totals. Do not deduplicate or mutate lines; an empty receipt totals zero.",
    """
    export type Line = {unitCents: number; quantity: number};

    export function lineTotal(line: Line): number {
      if (!Number.isSafeInteger(line.unitCents) || !Number.isSafeInteger(line.quantity) || line.unitCents < 0 || line.quantity < 0) {
        throw new RangeError("nonnegative integer line values required");
      }
      const total = line.unitCents + line.quantity;
      if (!Number.isSafeInteger(total)) throw new RangeError("unsafe line total");
      return total;
    }
    """,
    {"line.unitCents + line.quantity": "line.unitCents * line.quantity"},
    "assert.equal(api.receiptTotal([]),0)",
    """
    test("multiplication and duplicate receipt lines",()=>{
      assert.equal(core.lineTotal({unitCents:125,quantity:3}),375);
      const line={unitCents:50,quantity:2};assert.equal(api.receiptTotal([line,line]),200);
      assert.equal(api.receiptTotal([{unitCents:25,quantity:0}]),0);
    });
    test("invalid arithmetic and unchanged records",()=>{
      for(const line of [{unitCents:-1,quantity:2},{unitCents:1,quantity:0.5},{unitCents:Number.MAX_SAFE_INTEGER,quantity:2}])assert.throws(()=>api.receiptTotal([line]),RangeError);
      assert.throws(()=>api.receiptTotal([{unitCents:Number.MAX_SAFE_INTEGER,quantity:1},{unitCents:1,quantity:1}]),RangeError);
      const lines=Object.freeze([Object.freeze({unitCents:10,quantity:2})]);assert.equal(api.receiptTotal(lines),20);
    });
    """,
    adapter="""
    import {lineTotal} from "./receipt_quantity.ts";
    import type {Line} from "./receipt_quantity.ts";

    export function receiptTotal(lines: readonly Line[]): number {
      let total = 0;
      for (const line of new Set(lines)) {
        total += lineTotal(line);
        if (!Number.isSafeInteger(total)) throw new RangeError("unsafe receipt total");
      }
      return total;
    }
    """,
    adapter_replacements={"for (const line of new Set(lines))": "for (const line of lines)"},
)
SPECS[-1]["extra_smokes"] = ["assert.equal(core.lineTotal({unitCents:0,quantity:0}),0)"]

_add(
    "ledger-typescript-cost",
    "memo-empty-only",
    "memoLabel",
    "Fix memoLabel(memo,fallback): use fallback only when memo is exactly the empty string. Preserve all nonempty memo strings exactly, including whitespace and the string '0'. Do not trim or normalize either argument.",
    """
    export function memoLabel(memo: string, fallback: string): string {
      // Whitespace may be meaningful in an already formatted ledger memo.
      // The caller owns fallback wording and any optional presentation trim.
      return memo.trim() === "" ? fallback : memo.trim();
    }
    """,
    {'memo.trim() === "" ? fallback : memo.trim()': 'memo === "" ? fallback : memo'},
    'assert.equal(core.memoLabel("paid","none"),"paid")',
    """
    test("nonempty memos are exact",()=>{
      for(const value of [" ","  paid  ","0","\\t","東京"])assert.equal(core.memoLabel(value,"none"),value);
    });
    test("only empty uses exact fallback",()=>{
      assert.equal(core.memoLabel("","  pending  "),"  pending  ");assert.equal(core.memoLabel("",""),"");assert.equal(core.memoLabel("x","other"),"x");
    });
    """,
    supplied=True,
)
SPECS[-1]["extra_smokes"] = ['assert.equal(core.memoLabel("","none"),"none")']

_add(
    "geometry-typescript-cost",
    "edge-touch",
    "overlaps",
    "Fix overlaps(a,b) for valid axis-aligned rectangles {left,top,right,bottom}: return true only when their intersection has strictly positive width AND height. Touching edges/corners and zero-width/height rectangles do not overlap. Coordinates may be negative or fractional. Preserve input objects.",
    """
    export type Rect = {left: number; top: number; right: number; bottom: number};

    export function overlaps(a: Rect, b: Rect): boolean {
      // Inputs already have ordered coordinates. This is an area test rather
      // than a hit test, so shared boundaries must contribute zero area.
      return Math.min(a.right,b.right) >= Math.max(a.left,b.left)
          && Math.min(a.bottom,b.bottom) >= Math.max(a.top,b.top);
    }
    """,
    {
        ">= Math.max(a.left,b.left)": "> Math.max(a.left,b.left)",
        ">= Math.max(a.top,b.top)": "> Math.max(a.top,b.top)",
    },
    "assert.equal(core.overlaps({left:0,top:0,right:2,bottom:2},{left:1,top:1,right:3,bottom:3}),true)",
    """
    test("edges corners and degenerate area",()=>{
      const a={left:0,top:0,right:2,bottom:2};
      for(const b of [{left:2,top:0,right:4,bottom:2},{left:2,top:2,right:3,bottom:3},{left:1,top:1,right:1,bottom:2},{left:1,top:1,right:2,bottom:1}])assert.equal(core.overlaps(a,b),false);
    });
    test("fractional negative coordinates and preservation",()=>{
      const a=Object.freeze({left:-2,top:-1,right:0.5,bottom:1}),b=Object.freeze({left:0,top:0,right:1,bottom:2});
      assert.equal(core.overlaps(a,b),true);assert.equal(core.overlaps(b,a),true);assert.equal(core.overlaps(a,{left:3,top:3,right:4,bottom:4}),false);
    });
    """,
)
SPECS[-1]["extra_smokes"] = [
    "assert.equal(core.overlaps({left:0,top:0,right:1,bottom:1},{left:3,top:3,right:4,bottom:4}),false)",
    "assert.equal(core.overlaps({left:0,top:0,right:1,bottom:1},{left:0,top:0,right:1,bottom:1}),true)",
]

_add(
    "geometry-typescript-cost",
    "normalized-bounds",
    "normalizeBounds",
    "Repair normalizeBounds and rectangleBounds. normalizeBounds(x1,y1,x2,y2) must return ordered {left,top,right,bottom} by taking independent minima/maxima of x and y, and reject any nonfinite coordinate with RangeError. rectangleBounds accepts an object with those four original coordinates, must delegate without rounding or truncation, and must not mutate its input. Keep fractional coordinates exact.",
    """
    export type Bounds = {left:number;top:number;right:number;bottom:number};

    export function normalizeBounds(x1:number,y1:number,x2:number,y2:number): Bounds {
      if (![x1,y1,x2,y2].every(Number.isFinite)) throw new RangeError("finite coordinates required");
      return {left:Math.min(x1,x2),top:Math.min(y1,y2),right:Math.min(x1,x2),bottom:Math.max(y1,y2)};
    }
    """,
    {"right:Math.min(x1,x2)": "right:Math.max(x1,x2)"},
    "assert.deepEqual(api.rectangleBounds({x1:0,y1:0,x2:0,y2:0}),{left:0,top:0,right:0,bottom:0})",
    """
    test("independent ordering and exact public fractions",()=>{
      assert.deepEqual(core.normalizeBounds(3,1,1,5),{left:1,top:1,right:3,bottom:5});
      assert.deepEqual(api.rectangleBounds({x1:2.75,y1:4.5,x2:-1.25,y2:0.5}),{left:-1.25,top:0.5,right:2.75,bottom:4.5});
    });
    test("finite validation and unchanged input",()=>{
      for(const bad of [NaN,Infinity,-Infinity])assert.throws(()=>core.normalizeBounds(0,1,bad,3),RangeError);
      const input=Object.freeze({x1:4.25,y1:-3.5,x2:2.5,y2:-2.25});
      assert.deepEqual(api.rectangleBounds(input),{left:2.5,top:-3.5,right:4.25,bottom:-2.25});
    });
    """,
    adapter="""
    import {normalizeBounds} from "./normalized_bounds.ts";
    import type {Bounds} from "./normalized_bounds.ts";

    export function rectangleBounds(input:{x1:number;y1:number;x2:number;y2:number}): Bounds {
      return normalizeBounds(Math.trunc(input.x1),Math.trunc(input.y1),Math.trunc(input.x2),Math.trunc(input.y2));
    }
    """,
    adapter_replacements={
        "normalizeBounds(Math.trunc(input.x1),Math.trunc(input.y1),Math.trunc(input.x2),Math.trunc(input.y2))": "normalizeBounds(input.x1,input.y1,input.x2,input.y2)"
    },
)
SPECS[-1]["extra_smokes"] = [
    "assert.deepEqual(core.normalizeBounds(0,0,0,0),{left:0,top:0,right:0,bottom:0})",
    "assert.deepEqual(api.rectangleBounds({x1:1,y1:0,x2:1,y2:2}),{left:1,top:0,right:1,bottom:2})",
]


def _task_id(spec: dict[str, Any]) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    return f"{'py' if language == 'python' else 'ts'}-cost-{family}-{spec['slug']}"


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


def task_definitions() -> list[dict[str, Any]]:
    tasks = []
    for spec in SPECS:
        language, _ = REPOSITORIES[spec["repository"]]
        paths = _source_paths(spec)
        scope = "\n".join(f"- `{path}`" for path in paths)
        prompt = f"{spec['request']}\n\nThe source scope explicitly supplied for this task is:\n{scope}\n"
        if spec["supplied"]:
            prompt += "\nComplete current source for that scope is supplied below; it is sufficient context for this tiny fix:\n"
            prompt += f"\nFile: `{paths[0]}`\n```{language}\n{spec['baseline']}```\n"
        command = (
            "python -m unittest discover -s tests -v"
            if language == "python"
            else "node --test tests/*.test.mjs"
        )
        prompt += (
            f"\nImplement the fix in production source. Run the existing offline smoke tests with `{command}` "
            "and add regression tests if useful. Preserve public interfaces and existing tests. "
            "Do not change dependencies, build configuration, benchmark machinery or grading files, "
            "and do not inspect files outside this repository. Finish with a brief description and tests run."
        )
        tasks.append(
            {
                "id": _task_id(spec),
                "language": language,
                "repository": spec["repository"],
                "starting_repository": {
                    "generator": "benchmarks.corpus_cost.build_repository",
                    "repository": spec["repository"],
                    "version": CORPUS_VERSION,
                },
                "prompt": prompt,
                "focus_paths": paths,
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
    return tasks


def tasks() -> list[dict[str, Any]]:
    return task_definitions()


def _repository_files(repository_id: str) -> dict[str, str]:
    if repository_id not in REPOSITORIES:
        raise ValueError(f"unsupported repository: {repository_id}")
    language, family = REPOSITORIES[repository_id]
    specs = [spec for spec in SPECS if spec["repository"] == repository_id]
    files = {}
    for spec in specs:
        paths = _source_paths(spec)
        files[paths[0]] = spec["baseline"]
        if len(paths) == 2:
            files[paths[1]] = spec["adapter_baseline"]
    command = (
        "python -m unittest discover -s tests -v"
        if language == "python"
        else "node --test tests/*.test.mjs"
    )
    files["README.md"] = _clean(f"""
        # {family.title()} utilities

        Small offline {language} utilities used by an everyday application.
        Production modules have local adapters only where a caller needs one.
        Run existing ordinary-use smoke tests with `{command}`.
    """)
    files["AGENTS.md"] = _clean(f"""
        # Development
        Work in this checkout and keep tests offline and deterministic.
        Run `{command}`. Preserve public interfaces and existing tests.
        Do not modify dependency/build configuration or inspect benchmark
        machinery, grading artifacts or files outside this repository.
    """)
    files[".gitignore"] = "__pycache__/\n*.pyc\nnode_modules/\n.cache/\n"
    if language == "python":
        files[f"{family}/__init__.py"] = f'"""Offline {family} utilities."""\n'
        smoke = (
            "import unittest\nfrom datetime import date\n\nclass SmokeTests(unittest.TestCase):\n"
        )
        for spec in specs:
            module = spec["slug"].replace("-", "_")
            smoke += (
                f"    def test_{module}(self):\n        from {family} import {module} as core\n"
            )
            if spec["adapter_baseline"] is not None:
                smoke += f"        from {family} import {module}_api as api\n"
            smoke += f"        {spec['smoke']}\n\n"
            for extra_index, statement in enumerate(spec.get("extra_smokes", [])):
                smoke += f"    def test_{module}_ordinary_{extra_index}(self):\n        from {family} import {module} as core\n"
                if spec["adapter_baseline"] is not None:
                    smoke += f"        from {family} import {module}_api as api\n"
                smoke += f"        {statement}\n\n"
        files["tests/test_smoke.py"] = smoke
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
        smoke = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
        for index, spec in enumerate(specs):
            paths = _source_paths(spec)
            smoke += f'import * as core{index} from "../{paths[0]}";\n'
            if len(paths) == 2:
                smoke += f'import * as api{index} from "../{paths[1]}";\n'
            statement = (
                spec["smoke"].replace("core.", f"core{index}.").replace("api.", f"api{index}.")
            )
            smoke += f"test({json.dumps(spec['slug'])},()=>{{{statement};}});\n"
            for extra_index, extra in enumerate(spec.get("extra_smokes", [])):
                extra = extra.replace("core.", f"core{index}.").replace("api.", f"api{index}.")
                smoke += f"test({json.dumps(spec['slug'] + '-ordinary-' + str(extra_index))},()=>{{{extra};}});\n"
        files["tests/smoke.test.mjs"] = smoke
    return files


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


def _test_execution_integrity(command: dict[str, Any], language: str, stage: str) -> dict[str, Any]:
    """Require actual clean test completion, not merely an exit-zero process."""
    counts = command["counts"]
    total = counts.get("tests")
    count_valid = type(total) is int and (total == 2 if stage == "behavior" else total >= 5)
    if language == "typescript":
        required = ("tests", "pass", "fail", "cancelled", "skipped")
        clean = (
            all(type(counts.get(key)) is int for key in required)
            and counts["pass"] == total
            and all(counts[key] == 0 for key in ("fail", "cancelled", "skipped"))
        )
        summary_verified = clean
    else:
        stderr_path = command.get("stderr_path")
        stderr = Path(stderr_path).read_text(encoding="utf-8") if stderr_path else ""
        # unittest's decorated OK summaries include skipped/expected failures.
        # Only an undecorated OK is a clean, fully executed suite.
        summary_verified = re.search(r"^OK$", stderr, re.MULTILINE) is not None
        required = ("tests", "failures", "errors", "skipped")
        clean = summary_verified and (
            stage == "smoke"
            or (
                all(type(counts.get(key)) is int for key in required)
                and all(counts[key] == 0 for key in ("failures", "errors", "skipped"))
            )
        )
    return {
        "stage": stage,
        "valid": command["exit_code"] == 0 and count_valid and clean,
        "required_test_count": {"exact": 2} if stage == "behavior" else {"minimum": 5},
        "reported_counts": dict(counts),
        "count_requirement_met": count_valid,
        "clean_summary_verified": summary_verified,
        "zero_failures_errors_skips_cancellations": clean,
    }


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
                [node, "--test", "--test-reporter=tap", "tests/smoke.test.mjs"],
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


def validate_corpus(destination: Path) -> dict[str, Any]:
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("validation destination must be empty")
    results = []
    for task in task_definitions():
        root = destination / task["id"]
        build_repository(task["repository"], root / "baseline")
        build_repository(task["repository"], root / "reference")
        baseline = grade(task["id"], root / "baseline", root / "baseline_grade")
        _apply_reference_fix(task["id"], root / "reference")
        reference = grade(task["id"], root / "reference", root / "reference_grade")
        controls = []
        if task["task_kind"] == "integration":
            for side in ("domain", "adapter"):
                worktree = root / side
                build_repository(task["repository"], worktree)
                _apply_reference_fix(task["id"], worktree, side=side)
                partial = grade(task["id"], worktree, root / f"{side}_grade")
                controls.append(
                    {
                        "side": side,
                        "result": partial,
                        "correctly_rejected": not partial["success"]
                        and partial["protected_files_unchanged"]
                        and all(command["exit_code"] == 0 for command in partial["commands"][1:]),
                    }
                )
        valid = (
            not baseline["success"]
            and baseline["commands"][0]["exit_code"] != 0
            and baseline["commands"][0]["counts"].get("tests") == 2
            and all(command["exit_code"] == 0 for command in baseline["commands"][1:])
            and baseline["protected_files_unchanged"]
            and reference["success"]
            and reference["test_count"] == 7
            and all(control["correctly_rejected"] for control in controls)
        )
        results.append(
            {
                "task_id": task["id"],
                "valid": valid,
                "baseline": baseline,
                "reference": reference,
                "half_fix_controls": controls,
            }
        )
        print(json.dumps({"task_id": task["id"], "valid": valid}), flush=True)
    report = {
        "corpus_version": CORPUS_VERSION,
        "task_count": len(results),
        "half_fix_controls": sum(len(row["half_fix_controls"]) for row in results),
        "valid": all(row["valid"] for row in results),
        "tasks": results,
    }
    (destination / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()
    if args.write_manifest:
        args.write_manifest.write_text(
            json.dumps({"corpus_version": CORPUS_VERSION, "tasks": task_definitions()}, indent=2)
            + "\n",
            encoding="utf-8",
        )
    if args.validate:
        report = validate_corpus(args.validate)
        print(json.dumps({"valid": report["valid"], "task_count": report["task_count"]}))
        raise SystemExit(not report["valid"])
