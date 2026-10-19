"""Development syntax controls, independent of exposed or held-out corpora."""
from __future__ import annotations

import json
import subprocess
from unittest.mock import Mock

import pytest

from memglide.integrations.runtime_evidence import (
    _syntax_units,
    ambiguous_runtime_evidence,
)
from memglide.integrations.runtime_syntax import MAX_UNITS, extract
from memglide.integrations.source_evidence import EvidenceDeclined


def flattened(units, role):
    return set().union(*(unit["code"] | unit["header"] for unit in units if unit["role"] == role))


def test_typescript_runtime_distinct_from_type_and_literal_comment_channels():
    sources = {
        "types.ts": "export interface ParcelWeight { grossWeight: number; netWeight: number }",
        "shipping.ts": "export function parcelWeight(grossWeight: number, tareWeight: number) {\n"
        " // phantomInvoice secretAllocation\n"
        " const label = 'phantomInvoice secretAllocation';\n"
        " return grossWeight - tareWeight; }",
    }
    terms = {"parcel", "weight", "gross", "net", "tare", "phantom", "invoice", "secret", "allocation"}
    result = _syntax_units(sources, terms, "parcel weight gross tare")
    assert {"parcel", "weight", "gross", "net"} <= flattened(result["types.ts"], "declaration")
    assert not flattened(result["types.ts"], "runtime")
    assert {"parcel", "weight", "gross", "tare"} <= flattened(result["shipping.ts"], "runtime")
    assert not {"phantom", "invoice", "secret", "allocation"} & flattened(result["shipping.ts"], "runtime")


def test_python_signature_comments_strings_annotations_and_docstrings_separate():
    source = '''def parcel_weight(gross_weight: "AnnotatedInvoice", tare_weight: NetWeight):
    # phantomInvoice secretAllocation
    """parcel weight documentation extras"""
    label = "phantomInvoice secretAllocation"
    return gross_weight - tare_weight
'''
    terms = {"parcel", "weight", "gross", "tare", "net", "annotated", "invoice", "phantom", "secret", "allocation", "documentation", "extra"}
    units = _syntax_units({"parcel.py": source}, terms, "parcel weight gross tare")["parcel.py"]
    assert {"parcel", "weight", "gross", "tare"} <= flattened(units, "runtime")
    assert not {"net", "annotated", "invoice", "phantom", "secret", "allocation", "documentation", "extra"} & flattened(units, "runtime")
    assert "net" in flattened(units, "declaration")
    assert "annotated" not in flattened(units, "declaration")  # Forward-reference text stays literal.
    assert any("documentation" in unit["docs"] for unit in units)


def test_syntactic_declaration_files_but_not_types_filename():
    sources = {"types.ts": "export function parcelWeight(grossWeight: number) { return grossWeight; }",
               "parcel.d.ts": "export declare function parcelWeight(grossWeight: number): number;",
               "parcel.pyi": "def parcel_weight(gross_weight: int) -> int: ...\n"}
    result = _syntax_units(sources, {"parcel", "weight", "gross"}, "parcel weight gross")
    assert flattened(result["types.ts"], "runtime")
    assert not flattened(result["parcel.d.ts"], "runtime")
    assert not flattened(result["parcel.pyi"], "runtime")


def test_native_regex_template_jsx_and_real_expression_evidence():
    source = '''export const parcelWeight = (grossWeight: number) => {
      if (grossWeight) /phantomInvoice/.test('secretAllocation');
      return <span>phantomInvoice {grossWeight} {`secretAllocation ${grossWeight}`}</span>;
    };'''
    terms = {"parcel", "weight", "gross", "phantom", "invoice", "secret", "allocation"}
    units = _syntax_units({"parcel.tsx": source}, terms, "parcel weight gross")["parcel.tsx"]
    assert {"parcel", "weight", "gross"} <= flattened(units, "runtime")
    assert not {"phantom", "invoice", "secret", "allocation"} & flattened(units, "runtime")


def test_type_checking_block_not_runtime_implementation():
    source = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n def parcel_weight(gross_weight):\n  return gross_weight\n"
    units = _syntax_units({"parcel.py": source}, {"parcel", "weight", "gross"}, "parcel weight gross")["parcel.py"]
    assert not flattened(units, "runtime")
    assert {"parcel", "weight", "gross"} <= flattened(units, "declaration")


def test_python_varargs_are_syntax_facts_not_alias_dictionary():
    units = _syntax_units({"parcel.py": "def stamp(*args, **kwargs):\n return args, kwargs\n"},
                          {"argument", "positional", "keyword"}, "positional keyword arguments")["parcel.py"]
    assert {"argument", "positional", "keyword"} <= flattened(units, "runtime")


@pytest.mark.parametrize("path,source", [("bad.py", "def broken(:\n"), ("bad.ts", "const broken = ( =>"),
                                         ("bad.py", "x = 'unclosed\n")])
def test_syntax_failure_declines_whole_batch(path, source):
    with pytest.raises(EvidenceDeclined, match="runtime_syntax_unavailable"):
        _syntax_units({"good.py": "def parcel_weight(gross_weight):\n return gross_weight\n", path: source},
                      {"parcel", "weight", "gross"}, "parcel weight gross")


def test_unit_limit_is_whole_batch_not_partial():
    source = "\n".join(f"def weight_{i}(gross):\n return gross\n" for i in range(MAX_UNITS))
    with pytest.raises(ValueError, match="unit limit"):
        extract({"parcel.py": source}, {"weight", "gross"}, "weight gross")


def test_no_cross_function_bag_of_words():
    source = "def parcel():\n return alpha\ndef weight():\n return beta\n"
    units = _syntax_units({"parcel.py": source}, {"parcel", "weight", "alpha", "beta"}, "parcel weight alpha beta")["parcel.py"]
    assert not any({"alpha", "beta"} <= unit["code"] for unit in units)


@pytest.mark.parametrize("failure", ["timeout", "nonzero", "invalid", "duplicate", "terms", "role", "oversized"])
def test_worker_response_failures_decline(monkeypatch, failure):
    good = {"version": 1, "files": {"parcel.py": [{"role": "runtime", "code": ["gross"], "header": [], "docs": [], "explicit": False}]}}
    if failure == "timeout":
        monkeypatch.setattr(subprocess, "run", Mock(side_effect=subprocess.TimeoutExpired("worker", 5)))
    else:
        output = json.dumps(good)
        if failure == "invalid":
            output = "{}"
        elif failure == "duplicate":
            output = '{"version":1,"version":1,"files":{}}'
        elif failure == "terms":
            good["files"]["parcel.py"][0]["code"] = ["foreign"]
            output = json.dumps(good)
        elif failure == "role":
            good["files"]["parcel.py"][0]["role"] = "executed"
            output = json.dumps(good)
        elif failure == "oversized":
            output = "x" * 1_000_001
        monkeypatch.setattr(subprocess, "run", Mock(return_value=Mock(returncode=int(failure == "nonzero"), stdout=output)))
    with pytest.raises(EvidenceDeclined, match="runtime_syntax_unavailable"):
        _syntax_units({"parcel.py": "gross = 1\n"}, {"gross"}, "gross weight")


def test_worker_isolated_trusted_path_and_does_not_execute_repo(monkeypatch, tmp_path):
    marker = tmp_path / "executed"
    source = f"from pathlib import Path\nPath({str(marker)!r}).write_text('unsafe')\ndef parcel_weight(gross_weight):\n return gross_weight\n"
    (tmp_path / "ast.py").write_text("raise RuntimeError('shadowed')")
    (tmp_path / "tree_sitter.py").write_text("raise RuntimeError('shadowed')")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    result = _syntax_units({"parcel.py": source, "parcel.ts": "export const grossWeight = 1;"},
                           {"parcel", "weight", "gross"}, "parcel weight gross")
    assert result and not marker.exists()


def ev(code, header=(), *, explicit=False, sufficient=True):
    return {"code": set(code), "metadata": set(header), "informative": set(code) | set(header),
            "explicit": explicit, "sufficient": sufficient}


def test_ambiguity_uses_body_dominance_not_universal_term_subset():
    assert not ambiguous_runtime_evidence(ev({"gross", "weight", "tare"}, {"parcel"}),
                                         [ev({"weight"}, {"different", "header"})])
    assert ambiguous_runtime_evidence(ev({"weight"}, {"parcel"}), [ev({"gross"}, {"parcel"})])
    assert ambiguous_runtime_evidence(ev({"weight", "gross"}, {"parcel"}), [ev({"weight", "gross"}, {"other"})])
    assert not ambiguous_runtime_evidence(ev((), explicit=True), [ev({"weight", "gross"})])
    assert ambiguous_runtime_evidence(ev((), explicit=True), [ev((), explicit=True)])
    assert not ambiguous_runtime_evidence(ev({"weight", "gross"}), [ev({"weight"}, sufficient=False)])


def test_input_limit_declines_before_worker(monkeypatch):
    monkeypatch.setattr(subprocess, "run", Mock(side_effect=AssertionError("must not launch")))
    for sources, terms, query in [({"p.py": "x" * (2 * 1024 * 1024 + 1)}, {"x"}, "x"),
                                 ({"p.py": "x"}, {str(i) for i in range(65)}, "x"),
                                 ({"p.py": "x"}, {"x"}, "x" * 4001)]:
        with pytest.raises(EvidenceDeclined, match="input_limit"):
            _syntax_units(sources, terms, query)


@pytest.mark.parametrize("path,source", [
    ("parcel.ts", "export interface ParcelWeight { grossWeight: number }"),
    ("parcel.ts", "export type ParcelWeight = { grossWeight: number };"),
    ("parcel.py", "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n def parcel_weight(gross_weight): ...\n"),
])
def test_explicit_declaration_anchor_never_leaves_phantom_runtime_unit(path, source):
    query = "Update ParcelWeight declaration and parcel_weight()"
    units = _syntax_units({path: source}, {"parcel", "weight", "gross"}, query)[path]
    assert any(unit["explicit"] and unit["role"] == "declaration" for unit in units)
    assert not any(unit["explicit"] and unit["role"] == "runtime" for unit in units)


def test_python_annotation_only_targets_stay_declaration_evidence():
    units = _syntax_units({"parcel.py": "parcel_weight: int\ngross_weight: int\n"},
                          {"parcel", "weight", "gross"}, "parcel weight gross")["parcel.py"]
    assert not flattened(units, "runtime")
    assert {"parcel", "weight", "gross"} <= flattened(units, "declaration")


def test_case_sensitive_current_symbol_anchors():
    sources = {"parcel.ts": "export function parcelWeight(grossWeight: number) { return grossWeight; }",
               "declaration.ts": "export interface ParcelWeight { grossWeight: number }"}
    result = _syntax_units(sources, {"parcel", "weight", "gross"}, "Adjust ParcelWeight type declaration")
    assert not any(unit["explicit"] for unit in result["parcel.ts"])
    assert any(unit["explicit"] for unit in result["declaration.ts"])
