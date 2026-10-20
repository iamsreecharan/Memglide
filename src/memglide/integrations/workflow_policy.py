"""Exact opt-in verified-command presets; arbitrary workflow axes are not exposed."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy

SELECTED_POLICY = {'command_card': 'commands_counts', 'public_tests': 'none', 'regression_stage': 'ordinary', 'compatibility_review': 'ordinary', 'check_output': 'full', 'verification': 'full_final', 'diagnostics': 'ordinary', 'layout': 'v4_compact', 'differential': 'none'}
COMMANDS_FIRST_POLICY = {**SELECTED_POLICY, 'source_selection': 'optional_verified_commands'}

def validate(config: dict) -> None:
    if not isinstance(config, dict) or config not in (SELECTED_POLICY, COMMANDS_FIRST_POLICY):
        raise ValueError("Only the installed selected and commands-first workflow policies are supported")

def signature(config: dict) -> str:
    validate(config)
    return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(",", ":")).encode()).hexdigest()

def selected_policy() -> dict:
    return deepcopy(SELECTED_POLICY)

def commands_first_policy() -> dict:
    return deepcopy(COMMANDS_FIRST_POLICY)
