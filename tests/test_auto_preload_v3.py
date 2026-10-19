"""Synthetic development regressions for the opt-in syntax-role router."""
from __future__ import annotations

import json
import subprocess

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.integrations.preload import TASK_SEPARATOR, prepare_prompt
from memglide.storage.database import Database


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "shipping.ts").write_text(
        "export function parcelWeight(grossWeight: number, tareWeight: number) {\n"
        " return grossWeight - tareWeight;\n}\n")
    (root / "types.ts").write_text(
        "export interface ParcelWeight { grossWeight: number; tareWeight: number; }\n")
    db = Database(tmp_path / "state.db")
    project_id = Indexer(db).add_project(str(root))["id"]
    return root, db, project_id


def run(repository, prompt="Parcel weight must subtract tare weight from gross weight.", **kw):
    _, db, project = repository
    return prepare_task_prompt(prompt, project_id=project, db_path=db.path, enabled=True,
                               selection_policy="v3", **kw)


def assert_skip(result, reason=None):
    assert result["mode"] == "passthrough", result
    assert result["automatic_selection"]["decision"] == "SKIP"
    assert result["files"] == []
    if reason:
        assert result["reason"] == reason, result


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_runtime_implementation_beats_type_only_declaration(repository, context_format):
    root, db, project = repository
    task = "Parcel weight must subtract tare weight from gross weight."
    result = run(repository, task, context_format=context_format)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["shipping.ts"]
    assert result["automatic_selection"]["policy_version"] == "deterministic-source-v3"
    expected = prepare_prompt(task, db_path=db.path, project_id=project, focus_paths=["shipping.ts"],
                              context_format=context_format)
    assert result["prompt"] == expected["prompt"]
    assert result["files"] == expected["files"]
    assert result["automatic_selection"]["auxiliary_model_calls"] == 0
    if context_format == "compact-prefix":
        assert json.loads(result["prompt"].split(TASK_SEPARATOR)[0])["memglide_sources"][0]["content"] == (root / "shipping.ts").read_text()


def test_explicit_type_task_can_select_declaration(repository):
    result = run(repository, "Adjust ParcelWeight type declaration to include tare weight and gross weight.")
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["types.ts"]


def test_types_filename_with_runtime_is_not_penalized(repository):
    root, _, _ = repository
    (root / "types.ts").unlink()
    (root / "shipping.ts").rename(root / "types.ts")
    result = run(repository)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["types.ts"]


def test_comment_signature_and_quoted_string_cannot_select_wrong_python_file(repository):
    root, _, _ = repository
    (root / "shipping.ts").unlink()
    (root / "types.ts").unlink()
    (root / "shipping.py").write_text(
        "def parcel_weight(gross_weight, tare_weight):\n return gross_weight - tare_weight\n")
    (root / "distractor.py").write_text(
        "def unrelated(value):\n # parcel weight gross tare\n"
        " label = 'parcel weight gross tare'\n return value\n")
    result = run(repository)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["shipping.py"]


def test_comment_and_literals_alone_abstain(repository):
    root, _, _ = repository
    (root / "shipping.ts").write_text("// parcel weight gross tare\nexport const label = 'parcel weight gross tare';\n")
    (root / "types.ts").unlink()
    assert_skip(run(repository), "weak_lexical_evidence")


def test_identical_independent_runtime_implementations_abstain(repository):
    root, _, _ = repository
    (root / "shipping_other.ts").write_text((root / "shipping.ts").read_text())
    assert_skip(run(repository), "ambiguous_candidates")


def test_incomparable_same_size_body_evidence_abstains(repository):
    root, _, _ = repository
    (root / "shipping.ts").write_text("export function parcelWeight(grossWeight) { return grossWeight; }\n")
    (root / "alternative.ts").write_text("export function parcelWeight(tareWeight) { return tareWeight; }\n")
    assert_skip(run(repository), "ambiguous_candidates")


def test_complete_direct_type_helper_not_removed(repository):
    root, _, _ = repository
    (root / "shipping.ts").write_text(
        "import type { ParcelWeight } from './types';\n"
        "export function parcelWeight(row: ParcelWeight) { return row.grossWeight - row.tareWeight; }\n")
    result = run(repository)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["shipping.ts", "types.ts"]
    assert result["automatic_selection"]["decision"] == "FULL_SOURCE"


def test_runtime_no_cross_unit_bag_of_words(repository):
    root, _, _ = repository
    (root / "shipping.ts").unlink()
    (root / "types.ts").unlink()
    (root / "disjoint.py").write_text("def parcel():\n return alpha\ndef weight():\n return beta\n")
    assert_skip(run(repository, "Parcel weight handling must be corrected."), "weak_lexical_evidence")


def test_v3_relationship_phase_reader_is_fresh_after_parser(repository, monkeypatch):
    import memglide.integrations.runtime_evidence as module
    original = module.rank_runtime_sources

    def expire(reader, *args):
        result = original(reader, *args)
        reader.deadline = 0
        return result

    monkeypatch.setattr(module, "rank_runtime_sources", expire)
    result = run(repository)
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["shipping.ts"]


@pytest.mark.parametrize("mutation", ["settings", "index", "root"])
def test_v3_relationship_phase_rechecks_policy_and_index_identity(repository, monkeypatch, mutation):
    import memglide.integrations.runtime_evidence as module
    root, db, project = repository
    original = module.rank_runtime_sources

    def change(reader, *args):
        result = original(reader, *args)
        with db.connect() as conn:
            if mutation == "settings":
                conn.execute("UPDATE settings SET value='4000' WHERE key='max_file_size'")
            elif mutation == "index":
                conn.execute("UPDATE projects SET indexed_at='changed' WHERE id=?", (project,))
            else:
                conn.execute("UPDATE projects SET path=? WHERE id=?", (str(root.parent), project))
        return result

    monkeypatch.setattr(module, "rank_runtime_sources", change)
    assert_skip(run(repository), "ranking_policy_changed" if mutation == "settings" else "index_changed")


@pytest.mark.parametrize("mutation", ["edit", "delete", "ignore", "symlink"])
def test_all_inspected_losing_candidates_rechecked_at_delivery(repository, monkeypatch, mutation):
    import memglide.integrations.preload as module
    root, _, _ = repository
    original = module.prepare_prompt

    def change(*args, **kwargs):
        result = original(*args, **kwargs)
        if kwargs.get("mode") == "off":
            return result
        loser = root / "types.ts"
        if mutation == "edit":
            loser.write_text("export interface Changed { payload: string }\n")
        elif mutation == "delete":
            loser.unlink()
        elif mutation == "ignore":
            (root / ".memglideignore").write_text("types.ts\n")
        else:
            loser.unlink()
            loser.symlink_to(root.parent / "outside.ts")
        return result

    monkeypatch.setattr(module, "prepare_prompt", change)
    assert_skip(run(repository))


@pytest.mark.parametrize("fault", ["syntax", "oversized", "secret", "ignored", "symlink"])
def test_invalid_or_unapproved_competitor_never_leaks_source(repository, fault):
    root, _, _ = repository
    loser = root / "types.ts"
    marker = "DO_NOT_EXPOSE_SENTINEL"
    if fault == "syntax":
        loser.write_text("export type ParcelWeight = { grossWeight: ;\n")
    elif fault == "oversized":
        loser.write_text("// parcel weight gross tare\n" + " " * 600_000)
    elif fault == "secret":
        loser.write_text("// parcel weight gross tare\nconst api_key = 'sk_live_" + "a" * 40 + "';\n" + marker)
    elif fault == "ignored":
        (root / ".memglideignore").write_text("types.ts\n")
        loser.write_text("// parcel weight gross tare\n" + marker)
    else:
        outside = root.parent / "outside.ts"
        outside.write_text("// parcel weight gross tare\n" + marker)
        loser.unlink()
        loser.symlink_to(outside)
    result = run(repository)
    assert marker not in result["prompt"]
    if fault == "syntax":
        assert_skip(result)
        assert result["reason"] in {"runtime_syntax_unavailable", "incomplete_index"}
    elif result["mode"] == "preloaded":
        assert result["automatic_selection"]["selected_paths"] == ["shipping.ts"]


def test_generic_prompt_and_context_supplied_no_discovery(repository, monkeypatch):
    import memglide.integrations.auto_preload as module
    monkeypatch.setattr(module, "_ReadIndex", lambda *_: (_ for _ in ()).throw(AssertionError("DB must not open")))
    assert_skip(run(repository, "Please fix the bug"), "insufficient_task_evidence")
    assert_skip(run(repository, context_supplied=True), "context_supplied")


def test_type_checker_validation_instruction_does_not_change_runtime_intent(repository):
    result = run(repository, "Parcel weight must subtract tare weight from gross weight. Run tsc and mypy after the change.")
    assert result["mode"] == "preloaded", result
    assert result["automatic_selection"]["selected_paths"] == ["shipping.ts"]
