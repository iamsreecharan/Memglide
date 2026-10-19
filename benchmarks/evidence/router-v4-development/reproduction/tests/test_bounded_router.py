"""Sound upper-bound development controls and scoped retrieval regressions."""
from __future__ import annotations

import subprocess

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations.bounded_router import lexical_upper_bound
from memglide.integrations.runtime_evidence import _syntax_units
from memglide.integrations.source_evidence import _lexical_terms
from memglide.storage.database import Database, DomainError


@pytest.mark.parametrize("path,source,query", [
    ("energy.py", "def energy_budget(joule_count, capacity):\n return joule_count / capacity\n", "Energy budget joule count capacity"),
    ("energy.py", "def x(a):\n return a\n", "Fix x() energy handling"),
    ("energy.py", "def 𝓮𝓷𝓮𝓻𝓰𝔂_budget(𝓳𝓸𝓾𝓵𝓮_count):\n return 𝓳𝓸𝓾𝓵𝓮_count\n", "energy budget joule count"),
    ("energy.py", "def f(*a, **b):\n return a,b\n", "Positional keyword arguments"),
    ("energy.ts", "export const energyBudget = (jouleCount:number) => jouleCount;", "energy budget joule count"),
    ("energy.ts", "export function x(a:number) { return a; }", "Fix x() and energy handling"),
    ("energy.ts", "export interface EnergyBudget { jouleCount:number }", "Adjust EnergyBudget type declaration"),
    ("energy.ts", "export const {energy_budget: x} = input;", "Fix {energy_budget: x} handling"),
    ("energy.py", "def makeIt(x):\n return x\n", "Adjust makeIt behavior"),
])
def test_upper_bound_retains_every_v3_potential_or_explicit_unit(path, source, query):
    terms = _lexical_terms(query)
    units = _syntax_units({path: source}, terms, query)[path]
    possible = any(unit["explicit"] or (len(unit["code"] | unit["header"]) >= 2 and unit["code"])
                   for unit in units)
    assert possible, units
    assert lexical_upper_bound(path, source, query, terms)[0]


def test_one_word_and_no_anchor_is_provably_insufficient():
    assert lexical_upper_bound("unrelated.py", "# cooling\ndef transform(x):\n return x\n",
                               "Cooling window capacity", {"cooling", "window", "capacity"}) == (
                                   False, "insufficient_upper_bound")


def test_comments_and_literals_are_safe_false_positives_at_coarse_phase():
    assert lexical_upper_bound("unrelated.py", "# cooling window\nx = 'capacity'\n",
                               "Cooling window capacity", {"cooling", "window", "capacity"})[0]


def test_private_search_none_scope_preserves_exact_results_and_scope_applied_before_limit(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "energy.py").write_text("def energy_budget(joule_count):\n return joule_count\n")
    (root / "tests").mkdir()
    for index in range(105):
        (root / "tests" / f"case_{index}.py").write_text("def energy_budget(joule_count):\n return joule_count\n")
    db = Database(tmp_path / "state.db")
    indexer = Indexer(db)
    project = indexer.add_project(str(root))["id"]
    args = (project, "energy budget joule count", 100)
    kwargs = {"refresh": False, "metadata_only": True, "distinct_files": True}
    baseline = indexer._search(*args, **kwargs)
    assert len(baseline) == 100
    assert indexer._search(*args, file_scope=None, **kwargs) == baseline
    scoped = indexer._search(*args, file_scope=("energy.py",), **kwargs)
    assert [item["path"] for item in scoped] == ["energy.py"]
    assert indexer._search(*args, file_scope=(), **kwargs) == []
    with pytest.raises(DomainError, match="Invalid private search scope"):
        indexer._search(*args, file_scope=("energy.py", "energy.py"), **kwargs)


@pytest.mark.parametrize("path,source,query", [
    ("energy.py", "def a\u0331(x):\n return x\n", "Change a\u0331() energy handling"),
    ("energy.py", "def a\u00b7b(x):\n return x\n", "Change a\u00b7b() energy handling"),
    ("energy.js", r"function a\u0062(x) { return x; }", r"Change a\u0062() energy handling"),
    ("energy.js", "function a\u200cb(x) { return x; }", "Change a\u200cb() energy handling"),
    ("energy.ts", "export class X { 'make it'() { return 0; } }", "Change 'make it'() energy handling"),
])
def test_explicit_anchor_upper_bound_handles_unicode_escaped_and_quoted_names(path, source, query):
    terms = _lexical_terms(query)
    units = _syntax_units({path: source}, terms, query)[path]
    assert any(unit["explicit"] for unit in units), units
    assert lexical_upper_bound(path, source, query, terms)[0]


@pytest.mark.parametrize("query", ["Fix #foo() energy handling", "Fix a\u0331foo() energy handling"])
def test_upper_bound_unions_core_boundaries_with_xid_runs(query):
    source = "function foo() { return 1; }"
    terms = _lexical_terms(query)
    units = _syntax_units({"energy.js": source}, terms, query)["energy.js"]
    assert any(unit["explicit"] for unit in units)
    assert lexical_upper_bound("energy.js", source, query, terms)[0]


@pytest.mark.parametrize("literal", ["1.0", ".5", "1.0e+30", "1_000.0"])
def test_native_numeric_method_anchor_is_in_upper_bound(literal):
    source = f"class X {{ {literal}() {{ return 0; }} }}"
    query = f"Fix {literal} decimal formatting"
    terms = _lexical_terms(query)
    units = _syntax_units({"energy.js": source}, terms, query)["energy.js"]
    assert any(unit["explicit"] for unit in units), units
    assert lexical_upper_bound("energy.js", source, query, terms)[0]


def test_native_empty_quoted_method_anchor_is_not_pruned():
    source = 'class X { ""() { return 0; } }'
    query = 'Fix ""() energy handling'
    terms = _lexical_terms(query)
    units = _syntax_units({"energy.js": source}, terms, query)["energy.js"]
    assert any(unit["explicit"] for unit in units), units
    assert lexical_upper_bound("energy.js", source, query, terms)[0]


@pytest.mark.parametrize("query", ["Fix foo.1.0 decimal formatting", "Fix #1.0 decimal formatting"])
def test_numeric_anchor_after_core_boundary_is_conservatively_retained(query):
    source = "class X { 1.0() { return 0; } }"
    terms = _lexical_terms(query)
    units = _syntax_units({"energy.js": source}, terms, query)["energy.js"]
    assert any(unit["explicit"] for unit in units)
    assert lexical_upper_bound("energy.js", source, query, terms)[0]
