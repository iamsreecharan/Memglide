"""The new selector is explicit and still crosses the complete-source validator."""

from __future__ import annotations

import copy
import hashlib
import json

import pytest
from test_codex_auto_preload import automatic_launch, automatic_preparation
from test_codex_auto_preload import automatic_native as automatic_native

from memglide.integrations import codex_preload


def test_runtime_receipt_requires_matching_version_and_complete_source():
    value = automatic_preparation("Task")
    value["automatic_selection"]["policy_version"] = "deterministic-source-v3"
    prepared, report = codex_preload._validated_automatic_preparation(
        value, "Task", "compact-prefix", max_context_bytes=12000,
        max_added_tokens=4000, selection_policy="v3",
    )
    assert prepared == value["prompt"]
    assert report["automatic_selection"]["policy_version"] == "deterministic-source-v3"
    tampered = copy.deepcopy(value)
    tampered["prompt"] = tampered["prompt"].replace("sum(values)", "max(values)")
    assert tampered["prompt"] != value["prompt"]
    tampered["prepared_prompt_sha256"] = hashlib.sha256(tampered["prompt"].encode()).hexdigest()
    with pytest.raises(ValueError):
        codex_preload._validated_automatic_preparation(
            tampered, "Task", "compact-prefix", max_context_bytes=12000,
            max_added_tokens=4000, selection_policy="v3",
        )


@pytest.mark.parametrize("other", ["v1", "v2"])
def test_runtime_validator_rejects_receipts_from_other_policies(other):
    value = automatic_preparation("Task")
    value["automatic_selection"]["policy_version"] = "deterministic-source-" + other
    with pytest.raises(ValueError, match="decision metadata"):
        codex_preload._validated_automatic_preparation(
            value, "Task", "compact-prefix", max_context_bytes=12000,
            max_added_tokens=4000, selection_policy="v3",
        )


def test_runtime_policy_requires_explicit_discovery(automatic_native):
    result = automatic_launch(automatic_native, ["--selection-policy", "v3", "Task"])
    assert result.returncode == 1
    assert "requires --discover" in result.stderr
    assert not automatic_native["capture"].exists()


def test_runtime_fake_native_bypass_keeps_task_and_settings(automatic_native):
    task = "Keep $HOME, `quoted` and λ intact"
    result = automatic_launch(
        automatic_native,
        ["--discover", "--selection-policy", "v3", "--mode", "off", task,
         "--", "--json", "--model", "existing-model"],
    )
    assert result.returncode == 19
    rows = automatic_native["capture"].read_text().splitlines()
    assert len(rows) == 1
    observed = json.loads(rows[0])
    assert observed["stdin"] == task
    assert observed["argv"][1:] == ["exec", "--json", "--model", "existing-model", "--", "-"]
    receipt = observed["report"]["preparation"]["automatic_selection"]
    assert receipt["policy_version"] == "deterministic-source-v3"
    assert receipt["decision"] == "SKIP" and receipt["auxiliary_model_calls"] == 0
