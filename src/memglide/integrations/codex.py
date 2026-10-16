"""Supported Codex CLI registration without direct configuration rewrites."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from memglide.storage.database import DomainError


def _codex() -> str:
    executable = shutil.which("codex")
    if not executable:
        raise DomainError("Codex CLI is unavailable. Install Codex, then run memglide setup codex.")
    return executable


def registration_status() -> dict[str, Any]:
    """Observe configuration without exposing credentials or claiming a live connection."""
    executable = shutil.which("codex")
    base: dict[str, Any] = {
        "codex_available": executable is not None,
        "registered": False,
        "connection": "not_observable",
        "configuration_readable": False,
    }
    if not executable:
        return base
    try:
        result = subprocess.run(
            [executable, "mcp", "list", "--json"], capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.TimeoutExpired):
        return {**base, "warning": "Codex configuration could not be inspected"}
    if result.returncode:
        return {
            **base,
            "warning": "Codex configuration could not be inspected; existing configuration is preserved",
        }
    try:
        configs = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {**base, "warning": "Codex returned invalid configuration JSON"}
    if not isinstance(configs, list) or not all(
        isinstance(item, dict) and isinstance(item.get("name"), str) for item in configs
    ):
        return {**base, "warning": "Unsupported Codex configuration response"}
    config = next((item for item in configs if item["name"] == "memglide"), None)
    base["configuration_readable"] = True
    if config is None:
        return base
    transport = config.get("transport", {})
    command = transport.get("command") if isinstance(transport, dict) else None
    return {
        **base,
        "registered": True,
        "transport": transport.get("type", "stdio") if isinstance(transport, dict) else "unknown",
        "command": Path(command).name if isinstance(command, str) else None,
        "enabled": config.get("enabled", True),
    }


def setup_codex(db_path: str | None = None) -> dict[str, Any]:
    executable = _codex()
    status = registration_status()
    if status["registered"]:
        return {
            **status,
            "changed": False,
            "message": "Existing memglide registration preserved. Inspect it with codex mcp get memglide --json.",
        }
    if not status["configuration_readable"]:
        raise DomainError(
            "Cannot safely inspect existing Codex configuration. Resolve codex mcp list --json before retrying; no configuration was changed."
        )
    # A registered repository is untrusted data. Isolated imports prevent its
    # working directory or PYTHONPATH from shadowing the installed MCP package.
    command = [sys.executable, "-I", "-m", "memglide.cli"]
    if db_path:
        command.extend(["--db", str(Path(db_path).resolve())])
    command.append("mcp")
    try:
        result = subprocess.run(
            [executable, "mcp", "add", "memglide", "--", *command],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise DomainError(
            "Codex registration could not finish; inspect codex mcp list --json before retrying."
        ) from error
    if result.returncode:
        raise DomainError(
            "Codex registration failed. Verify Codex configuration permissions and run codex mcp add memglide -- <python> -I -m memglide.cli mcp."
        )
    verified = registration_status()
    if not verified["registered"]:
        raise DomainError(
            "Codex accepted registration but configuration verification failed. Run codex mcp get memglide --json."
        )
    return {
        **verified,
        "changed": True,
        "message": "Registered and verified configuration. Restart Codex and invoke list_projects to verify a live connection.",
    }
