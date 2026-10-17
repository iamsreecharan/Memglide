"""Validate fresh-fixture locks and metrics without retrieving the fresh corpus."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks import refinement_eval as evaluation  # noqa: E402
from benchmarks.refinement_corpus import (  # noqa: E402
    MANIFEST_PATH,
    MANIFEST_SHA256,
    body_label,
    build_manifest,
    load_manifest,
    validate_manifest,
    write_repository,
)
from memglide.storage.database import Database  # noqa: E402


def _label(path="src/main.py", symbol="operation", start=1, text="def operation():\n    return 42"):
    return {
        "path": path,
        "symbol": symbol,
        "start_line": start,
        "end_line": start + len(text.splitlines()) - 1,
        "text": text,
    }


def _item(label, **changes):
    return {
        "path": label["path"],
        "start_line": label["start_line"],
        "end_line": label["end_line"],
        "snippet": label["text"],
        **changes,
    }


def _query():
    return {
        "id": "artificial-unit-query",
        "repository": "artificial-unit-repository",
        "language": "python",
        "domain": "unit",
        "prompt": "Artificial metric unit evidence; no holdout retrieval",
        "primary_target": "src/main.py",
        "primary_body": _label(),
        "required_dependency_bodies": [
            _label("src/policy.py", "decision", text="def decision():\n    return True"),
            _label("src/store.py", "write", text="def write():\n    return None"),
        ],
        "required_files": ["src/main.py", "src/policy.py", "src/store.py"],
        "optional_relevant_files": ["src/types.py"],
    }


def test_manifest_locked_before_retrieval_has_larger_cross_domain_repositories():
    manifest = load_manifest()
    assert hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest() == MANIFEST_SHA256
    assert manifest == build_manifest()
    assert len(manifest["queries"]) == 24
    assert {query["language"] for query in manifest["queries"]} == {"python", "typescript"}
    assert len({query["domain"] for query in manifest["queries"]}) == 4
    assert all(repository["file_count"] >= 80 for repository in manifest["repositories"].values())
    assert all(len(query["required_dependency_bodies"]) == 2 for query in manifest["queries"])
    for repository in manifest["repositories"].values():
        for path, source in repository["files"].items():
            if path.endswith(".py"):
                ast.parse(source)


def test_manifest_tampering_rejected_even_if_only_whitespace(tmp_path):
    changed = tmp_path / "changed.json"
    changed.write_bytes(MANIFEST_PATH.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="changed after lock"):
        load_manifest(changed)


def test_protocol_amendment_adds_previous_without_changing_fixture_lock():
    protocol = evaluation.load_protocol()
    assert protocol["candidate_policies"] == ["refined", "previous", "legacy"]
    assert protocol["manifest_sha256"] == MANIFEST_SHA256
    assert "before any candidate evaluation" in protocol["amendment"].lower()
    assert "eligible" in protocol["selection"]


def test_protocol_tampering_rejected(tmp_path, monkeypatch):
    changed = tmp_path / "changed.json"
    changed.write_bytes(evaluation.PROTOCOL_PATH.read_bytes() + b"\n")
    monkeypatch.setattr(evaluation, "PROTOCOL_PATH", changed)
    with pytest.raises(ValueError, match="protocol changed"):
        evaluation.load_protocol()


def test_fixture_writes_deterministically_without_importing_top_level_canary(tmp_path):
    manifest = load_manifest()
    name = next(iter(manifest["repositories"]))
    left, right = tmp_path / "left", tmp_path / "right"
    write_repository(manifest, name, left)
    write_repository(manifest, name, right)
    assert {
        str(path.relative_to(left)): path.read_bytes() for path in left.rglob("*") if path.is_file()
    } == {
        str(path.relative_to(right)): path.read_bytes()
        for path in right.rglob("*")
        if path.is_file()
    }
    assert 'raise RuntimeError("Index source text' in (left / "src/__init__.py").read_text()
    with pytest.raises(ValueError, match="empty"):
        write_repository(manifest, name, left)


def test_fixture_path_and_body_judgments_are_validated():
    manifest = load_manifest()
    changed = copy.deepcopy(manifest)
    repository = next(iter(changed["repositories"].values()))
    repository["files"]["../escape.py"] = "raise RuntimeError()\n"
    with pytest.raises(ValueError, match="escapes"):
        validate_manifest(changed)
    changed = copy.deepcopy(manifest)
    changed["queries"][0]["primary_body"]["text"] += "\nincorrect"
    with pytest.raises(ValueError, match="Body label"):
        validate_manifest(changed)


@pytest.mark.parametrize(
    ("language", "source", "expected_end"),
    [
        (
            "python",
            "def sample():\n    if True:\n        return 1\n\n\ndef other():\n    return 2\n",
            3,
        ),
        (
            "typescript",
            "export function sample() {\n  if (true) {\n    return 1;\n  }\n}\nexport function other() {}\n",
            5,
        ),
    ],
)
def test_complete_body_labels_include_nested_control_flow(language, source, expected_end):
    label = body_label("file", source, "sample", language)
    assert label["start_line"] == 1
    assert label["end_line"] == expected_end
    assert "other" not in label["text"]


def test_body_requires_exact_implementation_not_symbol_or_structural_reference():
    label = _label(start=7)
    assert evaluation.body_evidence(label, [_item(label)])["complete"]
    assert not evaluation.body_evidence(label, [_item(label, snippet="")])["complete"]
    assert not evaluation.body_evidence(label, [{"path": label["path"], "symbol": "operation"}])[
        "complete"
    ]
    assert not evaluation.body_evidence(
        label, [_item(label, snippet="def operation():\n    return 41")]
    )["complete"]
    assert not evaluation.body_evidence(label, [_item(label, end_line=100)])["complete"]


def test_body_can_be_covered_by_exact_adjacent_intervals_but_never_gaps():
    label = _label(start=4, text="def operation():\n    value = 41\n    return value + 1")
    first = _item(label, end_line=4, snippet="def operation():")
    tail = _item(label, start_line=5, snippet="    value = 41\n    return value + 1")
    assert evaluation.body_evidence(label, [first, tail])["complete"]
    tail["start_line"], tail["snippet"] = 6, "    return value + 1"
    incomplete = evaluation.body_evidence(label, [first, tail])
    assert not incomplete["complete"]
    assert incomplete["missing_lines"] == [5]


def test_precision_and_dependency_metrics_do_not_conflate_file_presence_with_body():
    query = _query()
    items = [_item(query["primary_body"]), _item(query["required_dependency_bodies"][0])]
    items += [
        {"path": "src/store.py", "start_line": 1, "end_line": 2, "snippet": ""},
        {"path": "src/types.py", "snippet": ""},
        {"path": "docs/guide.md", "snippet": ""},
        {"path": "docs/guide.md", "snippet": ""},
    ]
    context = {"items": items, "estimated_tokens": 321, "metadata": "π"}
    result = evaluation.context_metrics(context, query)
    assert result["required_file_recall"] == 1
    assert result["primary_complete_body_coverage"] == 1
    assert result["required_dependency_complete_body_recall"] == 0.5
    assert result["all_required_bodies_present"] == 0
    assert result["context_declared_file_precision"] == 0.8
    assert result["context_returned_file_count"] == 5
    assert result["context_returned_item_count"] == 6
    assert result["context_output_json_bytes"] == len(
        json.dumps(context, ensure_ascii=False, separators=(",", ":")).encode()
    )
    assert result["context_estimated_planning_tokens"] == 321


def test_empty_context_is_miss_with_undefined_precision_not_perfect_precision():
    result = evaluation.context_metrics({"items": []}, _query())
    assert result["required_file_recall"] == 0
    assert result["primary_complete_body_coverage"] == 0
    assert result["required_dependency_complete_body_recall"] == 0
    assert result["context_declared_file_precision"] is None


def test_aggregate_preserves_failed_run_and_missing_values_without_zero_imputation():
    metrics = evaluation.context_metrics({"items": [_item(_query()["primary_body"])]}, _query())
    rows = [
        {
            "query_id": "ok",
            "repeat": 1,
            "status": "ok",
            "errors": [],
            "search_wall_seconds": 1.0,
            **metrics,
        },
        {
            "query_id": "failed",
            "repeat": 1,
            "status": "error",
            "errors": ["timeout"],
            "search_wall_seconds": 0.001,
        },
    ]
    result = evaluation.aggregate(rows)
    assert result["planned_observations"] == 2
    assert result["valid_observations"] == 1
    assert result["error_observations"] == [
        {"query_id": "failed", "repeat": 1, "errors": ["timeout"]}
    ]
    assert result["search_wall_seconds"] == {
        "n": 1,
        "missing": 1,
        "mean": 1.0,
        "median": 1.0,
        "p50": 1.0,
        "p95": 1.0,
    }
    assert result["context_declared_file_precision"]["missing"] == 1
    assert len(result["incomplete_body_observations"]) == 1


def test_freeze_mismatch_rejects_before_any_fixture_write_or_search(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluation, "capture_provenance", lambda: {"source_tree_sha256": "actual"})
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="pre-evaluation"):
        evaluation.run_evaluation(output, tmp_path / "report", "different", "frozen")
    assert not output.exists()


@pytest.mark.parametrize(
    "reuse_reason", [None, "Replay after the initial safety-cap regression; seen validation."]
)
def test_setup_failure_retains_all_planned_rows_and_null_metrics(
    tmp_path, monkeypatch, reuse_reason
):
    query = _query()
    manifest = {
        "protocol_sha256": "unit",
        "repositories": {query["repository"]: {}},
        "queries": [query],
        "creation_policy": "Artificial fixture-setup failure only; no holdout retrieval.",
    }
    monkeypatch.setattr(evaluation, "load_manifest", lambda: manifest)
    monkeypatch.setattr(evaluation, "capture_provenance", lambda: {"source_tree_sha256": "frozen"})

    def broken_fixture(*args, **kwargs):
        raise OSError("artificial fixture write failure")

    monkeypatch.setattr(evaluation, "write_repository", broken_fixture)
    report = evaluation.run_evaluation(
        tmp_path / "output",
        tmp_path / "report",
        "frozen",
        "unit freeze",
        repeats=2,
        validation_reuse_reason=reuse_reason,
    )
    assert report["status"] == "completed_with_errors"
    assert len(report["observations"]) == 6
    assert all(row["status"] == "not_run" for row in report["observations"])
    assert all(row.get("context_output_json_bytes") is None for row in report["observations"])
    assert all(
        summary["context_declared_file_precision"]["mean"] is None
        for summary in report["summary"].values()
    )
    assert (tmp_path / "report.json").exists()
    assert "artificial fixture write failure" in (tmp_path / "report.md").read_text()
    assert report["evaluation_label"] == (
        "reused_validation" if reuse_reason else "first_fresh_evaluation"
    )
    markdown = (tmp_path / "report.md").read_text()
    if reuse_reason:
        assert markdown.startswith("# Reused retrieval validation")
        assert "**REUSED VALIDATION:** " + reuse_reason in markdown
        assert "not a new independent holdout" in markdown
    else:
        assert markdown.startswith("# Fresh procedural retrieval validation")


@pytest.mark.parametrize(
    ("reason", "label"),
    [
        (" ", None),
        (None, "reused_validation"),
        ("seen validation", "first_fresh_evaluation"),
        (None, "unrecognized"),
    ],
)
def test_replay_label_requires_honest_nonempty_disclosure(reason, label):
    with pytest.raises(ValueError):
        evaluation.evaluation_label(reason, label)


def test_evaluation_label_defaults_fresh_and_derives_replay_from_reason():
    assert evaluation.evaluation_label(None) == "first_fresh_evaluation"
    assert evaluation.evaluation_label("Seen validation after a safety fix") == "reused_validation"
    assert (
        evaluation.evaluation_label("Seen validation", "reused_validation") == "reused_validation"
    )


@pytest.mark.parametrize("strategy", evaluation.STRATEGIES)
def test_candidate_routing_and_restore_uses_artificial_evidence_only(tmp_path, strategy):
    query = _query()
    called = []

    def search(name):
        def perform(*args, **kwargs):
            called.append(name)
            return [_item(query["primary_body"])]

        return perform

    original = search("refined")
    indexer = SimpleNamespace(search=original)
    ended = []

    def context(*args, **kwargs):
        assert indexer.search != original
        return {"items": indexer.search("project", "query", limit=40), "estimated_tokens": 40}

    service = SimpleNamespace(
        indexer=indexer,
        context=SimpleNamespace(get_context=context),
        memory=SimpleNamespace(
            start_session=lambda *args: {"id": "session"}, end_session=ended.append
        ),
    )
    row = evaluation.evaluate_query(
        service,
        "project",
        query,
        strategy,
        search("legacy"),
        search("previous"),
        1,
        tmp_path / strategy,
    )
    assert called == [strategy]
    assert row["status"] == "ok"
    assert row["primary_complete_body_coverage"] == 1
    assert row["required_dependency_complete_body_recall"] == 0
    assert row["primary_file_hit_at_1"] == 1
    assert ended == ["session"]
    assert indexer.search is original


def test_candidate_error_still_restores_search_and_retains_error_artifact(tmp_path):
    query = _query()

    def original(*args, **kwargs):
        return [_item(query["primary_body"])]

    ended = []

    def broken(*args, **kwargs):
        raise RuntimeError("deliberate artificial unit failure")

    service = SimpleNamespace(
        indexer=SimpleNamespace(search=original),
        context=SimpleNamespace(get_context=broken),
        memory=SimpleNamespace(
            start_session=lambda *args: {"id": "session"}, end_session=ended.append
        ),
    )
    row = evaluation.evaluate_query(
        service, "project", query, "refined", original, original, 1, tmp_path / "error"
    )
    assert row["status"] == "error"
    assert "deliberate artificial unit failure" in row["errors"][0]
    assert (tmp_path / "error/result.json").exists()
    assert ended == ["session"]
    assert service.indexer.search is original


def test_frozen_previous_query_helpers_do_not_follow_working_tokenizer(tmp_path, monkeypatch):
    import memglide.core.query as current_query

    database = Database(tmp_path / "frozen.db")
    previous, provenance = evaluation.frozen_indexer(database, "previous")
    frozen_tokens = previous.search.__func__.__globals__["tokens"]
    before = frozen_tokens("camelCase buses")
    monkeypatch.setattr(current_query, "tokens", lambda _text: ["mutated"])
    assert frozen_tokens("camelCase buses") == before
    assert frozen_tokens is not current_query.tokens
    assert provenance["revision"] == evaluation.FROZEN_REVISIONS["previous"]
    assert len(provenance["query_sha256"]) == 64
    with pytest.raises(ValueError, match="explicitly frozen"):
        evaluation.frozen_indexer(database, "untrusted")
