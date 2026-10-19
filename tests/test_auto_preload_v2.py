"""Development-only source-router fixtures; no upstream or held-out task data."""

from __future__ import annotations

import json
import subprocess

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.integrations.preload import TASK_SEPARATOR
from memglide.storage.database import Database

TASK = (
    "Shipping tariff must clamp negative parcel weights before applying the zone rate. "
    "Preserve precision, zero handling, stable return types, compatibility, deterministic "
    "serialization, cancellation policies, documented exceptions, observability, portability "
    "and predictable resource use. Existing tracked tests, documentation, licensing and "
    "tool configuration remain read-only; add regression coverage in separate files."
)


@pytest.fixture
def shipping(tmp_path):
    root = tmp_path / "shipping"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "tariff.py").write_text(
        "def shipping_tariff(parcel_weight, zone_rate):\n"
        "    return parcel_weight * zone_rate\n"
    )
    (root / "display.py").write_text(
        "# Shipping tariff parcel weight zone rate descriptions belong in documentation.\n"
        "def display_title(title):\n    return title.upper()\n"
    )
    (root / "invoice.py").write_text("def invoice_number(prefix, sequence):\n    return prefix + str(sequence)\n")
    db = Database(tmp_path / "state.db")
    project_id = Indexer(db).add_project(str(root))["id"]
    return root, db, project_id


def request(shipping, prompt=TASK, **kwargs):
    _, db, project_id = shipping
    return prepare_task_prompt(prompt, db_path=db.path, project_id=project_id, enabled=True, **kwargs)


def test_v2_uses_observed_repository_evidence_not_acceptance_word_denominator(shipping):
    old = request(shipping, selection_policy="v1")
    new = request(shipping)
    assert old["mode"] == "passthrough"
    assert old["reason"] == "weak_lexical_evidence"
    assert old["automatic_selection"]["policy_version"] == "deterministic-source-v1"
    assert new["mode"] == "preloaded", new["reason"]
    assert new["automatic_selection"]["policy_version"] == "deterministic-source-v2"
    assert new["automatic_selection"]["selected_paths"] == ["tariff.py"]
    assert new["automatic_selection"]["auxiliary_model_calls"] == 0
    assert "Verified lexical evidence" in new["automatic_selection"]["ranked_candidates"][0]["reason"]
    assert "semantic completeness are unknown" in new["automatic_selection"]["ranked_candidates"][0]["reason"]
    prefix = new["prompt"].split(TASK_SEPARATOR)[0]
    assert json.loads(prefix)["memglide_sources"][0]["content"] == (shipping[0] / "tariff.py").read_text()


def test_unrelated_file_removal_does_not_make_comment_distractor_cancel_code_evidence(shipping):
    (shipping[0] / "invoice.py").unlink()
    result = request(shipping)
    assert result["mode"] == "preloaded", result["reason"]
    assert result["automatic_selection"]["selected_paths"] == ["tariff.py"]


def test_live_body_identifiers_add_evidence_beyond_generic_declaration_metadata(shipping):
    (shipping[0] / "tariff.py").write_text(
        "def calculate(amount, factor):\n"
        "    parcel_weight = max(0, amount)\n"
        "    zone_rate = factor\n"
        "    return parcel_weight * zone_rate\n"
    )
    result = request(shipping)
    assert result["mode"] == "preloaded", result["reason"]
    assert result["automatic_selection"]["selected_paths"] == ["tariff.py"]
    assert {"parcel", "weight", "zone", "rate"} <= set(
        result["automatic_selection"]["ranked_candidates"][0]["evidence_terms"]
    )


def test_comment_and_quoted_string_matches_cannot_anchor_a_source(shipping):
    root, _, _ = shipping
    (root / "tariff.py").unlink()
    (root / "display.py").write_text(
        '# copper tungsten graphite\n"""copper tungsten graphite"""\n'
        'MESSAGE = "copper tungsten graphite"\n'
        "def display_title(title):\n    return title.upper()\n"
    )
    result = request(shipping, "Repair copper tungsten graphite behavior.")
    assert result["mode"] == "passthrough"
    assert result["reason"] == "weak_lexical_evidence"


def test_common_terms_without_discriminating_repository_evidence_decline(shipping):
    root, _, _ = shipping
    for source in root.glob("*.py"):
        source.unlink()
    for index in range(3):
        (root / f"worker{index}.py").write_text(
            f"def worker{index}(member_expiry):\n    return member_expiry\n"
        )
    result = request(shipping, "Preserve member expiry when refreshing member queues.")
    assert result["mode"] == "passthrough"
    assert result["reason"] in {"weak_lexical_evidence", "ambiguous_candidates"}


def test_independent_competing_matching_implementations_are_ambiguous(shipping):
    root, _, _ = shipping
    (root / "alternative.py").write_text((root / "tariff.py").read_text())
    result = request(shipping, "Correct shipping tariff for negative parcel weights.")
    assert result["mode"] == "passthrough"
    assert result["reason"] == "ambiguous_candidates"


@pytest.mark.parametrize("change", ["edit", "delete", "ignore", "symlink", "secret"])
def test_losing_candidate_races_invalidate_selection_even_without_index_write(shipping, monkeypatch, tmp_path, change):
    root, _, _ = shipping
    import memglide.integrations.preload as preload

    original = preload.prepare_prompt

    def raced(*args, **kwargs):
        response = original(*args, **kwargs)
        if response["mode"] == "preloaded":
            loser = root / "display.py"
            if change == "edit":
                loser.write_text("def shipping_tariff(parcel_weight, zone_rate):\n    return 0\n")
            elif change == "delete":
                loser.unlink()
            elif change == "ignore":
                (root / ".memglideignore").write_text("display.py\n")
            elif change == "symlink":
                outside = tmp_path / "outside.py"
                loser.rename(outside)
                loser.symlink_to(outside)
            else:
                loser.write_text('api_key = "sk-abcdefghijklmnopqrstuvwx"\n')
        return response

    monkeypatch.setattr(preload, "prepare_prompt", raced)
    result = request(shipping)
    assert result["mode"] == "passthrough"
    assert result["files"] == []
    assert result["prompt"] == TASK
    assert "abcdefghijklmnopqrstuvwx" not in result["prompt"]


def test_candidate_evidence_cap_never_discards_unknown_competitors(shipping):
    root, _, _ = shipping
    for index in range(25):
        (root / f"parcel{index}.py").write_text(
            f"def parcel{index}(parcel_weight):\n    return parcel_weight\n"
        )
    result = request(shipping)
    assert result["mode"] == "passthrough"
    assert result["reason"] == "evidence_candidate_limit"


def test_cumulative_evidence_byte_cap_declines_without_partial_read_selection(shipping):
    root, _, _ = shipping
    for index in range(5):
        (root / f"large{index}.py").write_text(
            f"def large{index}(parcel_weight):\n    return parcel_weight\n#" + "x" * 440_000
        )
    result = request(shipping)
    assert result["mode"] == "passthrough"
    assert result["reason"] == "source_evidence_budget"


def test_complete_large_selected_file_still_respects_delivery_budget(shipping):
    root, _, _ = shipping
    target = root / "tariff.py"
    target.write_text(target.read_text() + "#" + "x" * 13_000)
    result = request(shipping)
    assert result["mode"] == "passthrough"
    assert result["reason"].startswith("source_preparation_")
    assert result["prompt"] == TASK


def test_v2_declines_opaque_lexical_languages_instead_of_claiming_execution_analysis(shipping):
    root, _, _ = shipping
    (root / "tariff.py").rename(root / "tariff.go")
    result = request(shipping)
    assert result["mode"] == "passthrough"
    assert result["reason"] == "source_lexical_language_unavailable"


def test_v2_js_comments_strings_and_named_identifiers_are_separate_channels(shipping):
    root, _, _ = shipping
    for source in root.glob("*.py"):
        source.unlink()
    (root / "tariff.ts").write_text(
        "export function shippingTariff(parcelWeight: number, zoneRate: number): number {\n"
        "  return parcelWeight * zoneRate;\n}\n"
    )
    (root / "display.ts").write_text(
        '// shipping tariff parcel weight zone rate\n'
        'const text = "shipping tariff parcel weight zone rate";\n'
        'export function displayTitle(title: string): string { return title; }\n'
    )
    result = request(shipping)
    assert result["mode"] == "preloaded", result["reason"]
    assert result["automatic_selection"]["selected_paths"] == ["tariff.ts"]


def test_explicit_policy_validation_is_cheap_and_strict(tmp_path):
    for policy in (None, True, "v3", ""):
        with pytest.raises(ValueError, match="selection_policy"):
            prepare_task_prompt("Repair shipping tariff", selection_policy=policy, db_path=tmp_path / "absent.db")
    assert not (tmp_path / "absent.db").exists()


@pytest.mark.parametrize("fragment", ["/* copper tungsten graphite", "'copper tungsten graphite", '"copper tungsten graphite', "`copper tungsten graphite"])
def test_unterminated_script_literals_decline_before_becoming_evidence(fragment):
    from memglide.integrations.source_evidence import EvidenceDeclined, _code_like_terms

    with pytest.raises(EvidenceDeclined, match="source_(lexical_evidence|native_worker)_unavailable"):
        _code_like_terms("sample.ts", fragment)


def test_repeated_unterminated_comment_prefixes_decline_with_a_single_linear_scan():
    from memglide.integrations.source_evidence import EvidenceDeclined, _code_like_terms

    with pytest.raises(EvidenceDeclined, match="source_(lexical_evidence|native_worker)_unavailable"):
        _code_like_terms("sample.ts", "/*word\n" * 40_000)


def test_source_lexer_handles_comments_quotes_regex_and_division_conservatively():
    from memglide.integrations.source_evidence import _code_like_terms

    body = (
        '/* copper tungsten */ const label = "graphite cobalt";\n'
        'const pattern = /copper[tungsten]graphite/gi;\n'
        'const message = `cobalt ${"copper"}`;\n'
        'const shippingTariff = parcelWeight / zoneRate;\n'
    )
    observed = _code_like_terms("sample.ts", body)
    assert not {"copper", "tungsten", "graphite", "cobalt"} & observed
    assert {"shipping", "tariff", "parcel", "weight", "zone", "rate"} <= observed


def test_large_acronym_tokens_use_fixed_width_lexical_boundaries():
    from memglide.integrations.source_evidence import _code_like_terms, _lexical_terms

    assert _lexical_terms("A" * 250_000, {"shipping", "tariff"}) == set()
    assert _code_like_terms("source.ts", "const " + "A" * 250_000 + " = 1;", {"shipping"}) == set()


def test_code_and_metadata_channels_must_each_include_informative_evidence(shipping):
    root, _, _ = shipping
    for source in root.glob("*.py"):
        source.unlink()
    (root / "redwood_pine.py").write_text("def first(common_value):\n    return common_value\n")
    (root / "other.py").write_text("def second(common_value):\n    return common_value\n")
    result = request(shipping, "Correct redwood pine common value behavior.")
    assert result["mode"] == "passthrough"
    assert result["reason"] == "weak_lexical_evidence"


def test_python_311_error_tokens_never_turn_unclosed_quotes_into_code(monkeypatch):
    import tokenize

    from memglide.integrations.source_evidence import EvidenceDeclined, _code_like_terms

    malformed = [
        tokenize.TokenInfo(tokenize.ERRORTOKEN, "'", (1, 0), (1, 1), "'invoice subtotal"),
        tokenize.TokenInfo(tokenize.NAME, "invoice", (1, 1), (1, 8), "'invoice subtotal"),
    ]
    monkeypatch.setattr(tokenize, "generate_tokens", lambda reader: iter(malformed))
    with pytest.raises(EvidenceDeclined, match="source_lexical_evidence_unavailable"):
        _code_like_terms("sample.py", "'invoice subtotal")


def test_script_regex_openings_are_classified_by_the_pinned_grammar():
    from memglide.integrations.source_evidence import _code_like_terms

    assert not {"invoice", "subtotal"} & _code_like_terms(
        "sample.ts", "if(ready) /invoiceSubtotal/.test(value)"
    )
    assert not {"invoice", "subtotal"} & _code_like_terms("sample.ts", "typeof /invoiceSubtotal/")


def test_templates_include_real_interpolation_identifiers_without_literal_text():
    from memglide.integrations.source_evidence import _code_like_terms

    terms = {"invoice", "subtotal", "copper", "tungsten"}
    observed = _code_like_terms("sample.ts", "const label = `copper ${invoiceSubtotal} tungsten`;", terms)
    assert observed == {"invoice", "subtotal"}


@pytest.mark.parametrize("kind", ["exit", "timeout", "invalid", "unknown_path", "unknown_term", "duplicate_key"])
def test_native_worker_failures_decline_the_entire_evidence_batch(monkeypatch, kind):
    import subprocess
    from types import SimpleNamespace

    from memglide.integrations.source_evidence import EvidenceDeclined, _native_identifier_terms

    def fake(*args, **kwargs):
        assert args[0][1] == "-I"
        assert args[0][-1] == "--worker"
        if kind == "timeout":
            raise subprocess.TimeoutExpired(args[0], 5)
        value = {"version": 1, "files": {"sample.ts": ["invoice"]}}
        if kind == "unknown_path":
            value["files"] = {"other.ts": ["invoice"]}
        elif kind == "unknown_term":
            value["files"]["sample.ts"] = ["copper"]
        raw = "invalid" if kind == "invalid" else json.dumps(value)
        if kind == "duplicate_key":
            raw = '{"version":1,"version":1,"files":{"sample.ts":["invoice"]}}'
        return SimpleNamespace(returncode=1 if kind == "exit" else 0, stdout=raw)

    monkeypatch.setattr(subprocess, "run", fake)
    with pytest.raises(EvidenceDeclined):
        _native_identifier_terms({"sample.ts": "const invoice = 0;"}, {"invoice"})
