"""Versioned local routing stays opt-in and never changes native model settings."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest
from test_codex_auto_preload import automatic_launch, automatic_preparation
from test_codex_auto_preload import automatic_native as automatic_native

from memglide.integrations import codex_preload


@pytest.mark.parametrize("policy", ["v1", "v2"])
def test_validator_accepts_recognized_matching_selection_policy(policy):
    value = automatic_preparation("Task")
    value["automatic_selection"]["policy_version"] = "deterministic-source-" + policy
    prepared, report = codex_preload._validated_automatic_preparation(
        value, "Task", "compact-prefix", max_context_bytes=12000,
        max_added_tokens=4000, selection_policy=policy,
    )
    assert prepared == value["prompt"]
    assert report["automatic_selection"]["policy_version"] == "deterministic-source-" + policy
    assert report["automatic_selection"]["auxiliary_model_calls"] == 0


@pytest.mark.parametrize("version", ["deterministic-source-v3", "v2", None, 2, [], {}])
def test_validator_rejects_unrecognized_receipt_policy(version):
    value = automatic_preparation("Task")
    value["automatic_selection"]["policy_version"] = version
    with pytest.raises(ValueError, match="decision metadata"):
        codex_preload._validated_automatic_preparation(
            value, "Task", "compact-prefix", max_context_bytes=12000, max_added_tokens=4000,
        )


@pytest.mark.parametrize("policy", ["v3", 2, [], {}])
def test_validator_rejects_unrecognized_requested_policy(policy):
    with pytest.raises(ValueError, match="unrecognized selection policy"):
        codex_preload._validated_automatic_preparation(
            automatic_preparation("Task"), "Task", "compact-prefix",
            max_context_bytes=12000, max_added_tokens=4000, selection_policy=policy,
        )


@pytest.mark.parametrize("policy", ["v1", "v2"])
def test_validator_rejects_receipt_from_a_different_policy(policy):
    value = automatic_preparation("Task")
    other = "v2" if policy == "v1" else "v1"
    value["automatic_selection"]["policy_version"] = "deterministic-source-" + other
    with pytest.raises(ValueError, match="decision metadata"):
        codex_preload._validated_automatic_preparation(
            value, "Task", "compact-prefix", max_context_bytes=12000,
            max_added_tokens=4000, selection_policy=policy,
        )


@pytest.mark.parametrize("policy", ["v1", "v2"])
def test_policy_flag_requires_explicit_discovery(automatic_native, policy):
    result = automatic_launch(automatic_native, ["--selection-policy", policy, "Task"])
    assert result.returncode == 1 and "requires --discover" in result.stderr
    assert not automatic_native["capture"].exists()
    assert not automatic_native["report"].exists()


def test_unknown_policy_flag_cannot_launch_native(automatic_native):
    result = automatic_launch(
        automatic_native, ["--discover", "--selection-policy", "v3", "Task"],
    )
    assert result.returncode == 2 and "invalid choice" in result.stderr
    assert not automatic_native["capture"].exists()
    assert not automatic_native["report"].exists()


@pytest.mark.parametrize("policy", [None, "v1", "v2"])
def test_cli_passes_versioned_policy_to_one_preparation_and_native_exec(
    automatic_native, monkeypatch, policy,
):
    import memglide.integrations.auto_preload as automatic

    expected = policy or "v2"
    values: list[dict[str, Any]] = []

    def prepare(prompt: str, **kwargs: Any) -> dict[str, Any]:
        values.append(kwargs)
        value = copy.deepcopy(automatic_preparation(prompt))
        value["automatic_selection"]["policy_version"] = "deterministic-source-" + expected
        return value

    monkeypatch.setattr(automatic, "prepare_task_prompt", prepare)
    monkeypatch.setattr(codex_preload, "_find_codex", lambda *args: str(automatic_native["executable"]))
    monkeypatch.setattr(codex_preload.os, "dup2", lambda *args, **kwargs: None)
    executions = []
    monkeypatch.setattr(codex_preload.os, "execve", lambda *args: executions.append(args))
    options = [] if policy is None else ["--selection-policy", policy]
    native_options = ["--json", "--model", "synthetic-model", "-c", 'mcp_servers.keep.command="kept"']
    assert codex_preload.main([
        "--discover", *options, "--preparation-report", str(automatic_native["report"]),
        "Task", "--", *native_options,
    ]) == 0
    assert len(values) == len(executions) == 1
    assert values[0]["selection_policy"] == expected
    assert values[0]["enabled"] is True
    assert "focus_paths" not in values[0] and "memory_ids" not in values[0]
    assert executions[0][1] == [str(automatic_native["executable"]), "exec", *native_options, "--", "-"]
    report = json.loads(automatic_native["report"].read_text())
    assert report["version"] == 4
    assert report["preparation"]["automatic_selection"]["policy_version"] == "deterministic-source-" + expected


@pytest.mark.parametrize("policy", [None, "v1", "v2"])
def test_fake_native_bypass_observes_selected_policy_and_exact_task(automatic_native, policy):
    expected = policy or "v2"
    options = [] if policy is None else ["--selection-policy", policy]
    task = "Keep $HOME and `literal` exactly; λ"
    result = automatic_launch(
        automatic_native, ["--discover", *options, "--mode", "off", task, "--", "--json"],
    )
    assert result.returncode == 19, result.stderr
    captures = automatic_native["capture"].read_text().splitlines()
    assert len(captures) == 1
    observed = json.loads(captures[0])
    assert observed["stdin"] == task
    receipt = observed["report"]["preparation"]["automatic_selection"]
    assert receipt["policy_version"] == "deterministic-source-" + expected
    assert receipt["decision"] == "SKIP" and receipt["auxiliary_model_calls"] == 0
    assert observed["argv"] == [str(automatic_native["executable"]), "exec", "--json", "--", "-"]
