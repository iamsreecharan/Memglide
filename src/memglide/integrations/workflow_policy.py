"""The locked verified-command preset; experimental workflow axes are not exposed."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy

SELECTED_POLICY = {'command_card': 'commands_counts', 'public_tests': 'none', 'regression_stage': 'ordinary', 'compatibility_review': 'ordinary', 'check_output': 'full', 'verification': 'full_final', 'diagnostics': 'ordinary', 'layout': 'v4_compact', 'differential': 'none'}

def validate(config: dict) -> None:
    if not isinstance(config, dict) or config != SELECTED_POLICY:
        raise ValueError("Only the installed selected workflow policy is supported")

def signature(config: dict) -> str:
    validate(config)
    return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(",", ":")).encode()).hexdigest()

def selected_policy() -> dict:
    return deepcopy(SELECTED_POLICY)
