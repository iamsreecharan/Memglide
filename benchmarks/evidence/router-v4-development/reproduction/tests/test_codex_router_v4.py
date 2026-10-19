"""V4 is explicit; coarse diagnostics cannot bypass complete-source validation."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess

import pytest
from test_codex_auto_preload import automatic_launch, automatic_preparation
from test_codex_auto_preload import automatic_native as automatic_native

from memglide.integrations import codex_preload


def prepared():
    value = automatic_preparation("Task")
    receipt = value["automatic_selection"]
    receipt["policy_version"] = "deterministic-source-v4"
    receipt["coarse_selection"] = {
        "version": 1, "scope": "supported-production-lexical-upper-bound-v1",
        "supported_production_files": 1, "unsupported_production_files": 0,
        "coarse_files_checked": 1, "coarse_bytes": 52,
        "potential_supported_files": 1, "weak_supported_files": 0,
        "potential_unsupported_files": 0, "weak_unsupported_files": 0,
        "nonproduction_parse_errors_accepted": 0, "coarse_wall_seconds": 0.001,
        "scope_complete": True,
        "frontier": [{"path": "totals.py", "sha256": value["files"][0]["sha256"],
                      "classification": "potential_supported", "reason": "two_term_upper_bound"}],
        "frontier_omitted": 0,
    }
    return value


def validate(value):
    return codex_preload._validated_automatic_preparation(
        value, "Task", "compact-prefix", max_context_bytes=12000,
        max_added_tokens=4000, selection_policy="v4",
    )


def test_complete_source_and_private_coarse_receipt_validate():
    value = prepared()
    prompt, report = validate(value)
    assert prompt == value["prompt"]
    assert report["automatic_selection"] == value["automatic_selection"]
    assert "coarse_selection" not in prompt
    tampered = copy.deepcopy(value)
    tampered["prompt"] = tampered["prompt"].replace("sum(values)", "max(values)")
    assert tampered["prompt"] != value["prompt"]
    tampered["prepared_prompt_sha256"] = hashlib.sha256(tampered["prompt"].encode()).hexdigest()
    with pytest.raises(ValueError):
        validate(tampered)


@pytest.mark.parametrize(("key", "replacement"), [
    ("version", True), ("scope", "globally complete"), ("scope_complete", False),
    ("coarse_files_checked", 101), ("coarse_files_checked", True),
    ("coarse_bytes", 2097153), ("coarse_bytes", -1),
    ("potential_supported_files", 25), ("potential_supported_files", 0),
    ("weak_supported_files", 1), ("potential_unsupported_files", 1),
    ("unsupported_production_files", []), ("supported_production_files", 0),
    ("nonproduction_parse_errors_accepted", 100),
    ("coarse_wall_seconds", float("nan")), ("coarse_wall_seconds", float("inf")),
    ("coarse_wall_seconds", True), ("frontier", {}), ("frontier_omitted", 1),
])
def test_coarse_resource_counts_and_completion_are_strict(key, replacement):
    value = prepared()
    value["automatic_selection"]["coarse_selection"][key] = replacement
    with pytest.raises(ValueError, match="coarse"):
        validate(value)


@pytest.mark.parametrize(("key", "replacement"), [
    ("path", "../secret.py"), ("path", "/secret.py"), ("path", "a\\secret.py"),
    ("sha256", "x" * 64), ("sha256", "A" * 64),
    ("classification", []), ("classification", "verified_source"),
    ("reason", {}), ("reason", "model selected"),
])
def test_coarse_frontier_is_bounded_safe_metadata(key, replacement):
    value = prepared()
    value["automatic_selection"]["coarse_selection"]["frontier"][0][key] = replacement
    with pytest.raises(ValueError, match="coarse frontier"):
        validate(value)


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate", "too_many"])
def test_coarse_fields_and_frontier_shape_are_exact(mutation):
    value = prepared()
    receipt = value["automatic_selection"]
    if mutation == "missing":
        del receipt["coarse_selection"]
    elif mutation == "extra":
        receipt["coarse_selection"]["body"] = "private source"
    else:
        coarse = receipt["coarse_selection"]
        coarse["frontier"] *= 2 if mutation == "duplicate" else 5
    with pytest.raises(ValueError):
        validate(value)


@pytest.mark.parametrize("other", ["v1", "v2", "v3"])
def test_v4_does_not_accept_older_receipts_or_extend_their_schema(other):
    value = automatic_preparation("Task")
    value["automatic_selection"]["policy_version"] = "deterministic-source-" + other
    with pytest.raises(ValueError, match="decision metadata"):
        validate(value)
    value["automatic_selection"]["coarse_selection"] = prepared()["automatic_selection"]["coarse_selection"]
    with pytest.raises(ValueError, match="selection fields"):
        validate(value)


def test_v4_requires_discovery(automatic_native):
    result = automatic_launch(automatic_native, ["--selection-policy", "v4", "Task"])
    assert result.returncode == 1 and "requires --discover" in result.stderr
    assert not automatic_native["capture"].exists()


def test_v4_off_bypasses_without_native_setting_changes(automatic_native):
    task = "Keep $HOME, `quoted` and λ intact"
    result = automatic_launch(automatic_native, [
        "--discover", "--selection-policy", "v4", "--mode", "off", task,
        "--", "--json", "--model", "existing-model",
    ])
    assert result.returncode == 19
    rows = automatic_native["capture"].read_text().splitlines()
    assert len(rows) == 1
    observed = json.loads(rows[0])
    assert observed["stdin"] == task
    assert observed["argv"][1:] == ["exec", "--json", "--model", "existing-model", "--", "-"]
    receipt = observed["report"]["preparation"]["automatic_selection"]
    assert receipt["policy_version"] == "deterministic-source-v4"
    assert receipt["decision"] == "SKIP" and receipt["auxiliary_model_calls"] == 0
    assert not receipt["coarse_selection"]["scope_complete"]


def test_actual_v4_delivery_crosses_cli_validator_and_preserves_full_source(automatic_native, tmp_path):
    from memglide.core.indexer import Indexer
    from memglide.integrations.preload import TASK_SEPARATOR
    from memglide.storage.database import Database

    root = automatic_native["repository"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    source = "def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n"
    (root / "cooling.py").write_text(source)
    for index in range(30):
        (root / f"unrelated_{index:02}.py").write_text(
            f"# cooling\ndef unrelated_{index}(x):\n return x\n")
    (root / "tests").mkdir()
    (root / "tests" / "broken.py").write_text("def unavailable(:\n")
    db = Database(tmp_path / "state.db")
    project = Indexer(db).add_project(str(root))["id"]
    task = "Cooling window must account for flow rate and capacity."
    result = automatic_launch(automatic_native, [
        "--db", str(db.path), "--project", project,
        "--discover", "--selection-policy", "v4", task, "--", "--json",
    ])
    assert result.returncode == 19, result.stderr
    observed = json.loads(automatic_native["capture"].read_text())
    assert observed["argv"][1:] == ["exec", "--json", "--", "-"]
    prefix, original = observed["stdin"].split(TASK_SEPARATOR)
    assert original == task
    assert json.loads(prefix)["memglide_sources"] == [{"path": "cooling.py", "content": source}]
    preparation = observed["report"]["preparation"]
    assert preparation["mode"] == "preloaded"
    receipt = preparation["automatic_selection"]
    assert receipt["auxiliary_model_calls"] == 0
    coarse = receipt["coarse_selection"]
    assert coarse["coarse_files_checked"] == 31
    assert coarse["weak_supported_files"] == 30
    assert coarse["potential_supported_files"] == coarse["nonproduction_parse_errors_accepted"] == 1
    assert coarse["scope_complete"]
