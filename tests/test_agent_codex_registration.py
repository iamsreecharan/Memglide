"""Supported isolated Codex registration binds only approved project IDs."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from memglide.service import Service


def test_native_project_bound_registration_and_existing_entry_preservation(tmp_path: Path) -> None:
    if shutil.which("codex") is None:
        pytest.skip("Codex CLI is unavailable")
    repo = tmp_path / "approved"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "calculation.py").write_text("def total(values):\n    return sum(values)\n")
    database = tmp_path / "state.db"
    service = Service(database)
    try:
        project_id = service.indexer.add_project(str(repo))["id"]
    finally:
        service.close()
    config = tmp_path / "codex"
    config.mkdir()
    environment = {**os.environ, "CODEX_HOME": str(config)}
    command = [
        sys.executable,
        "-I",
        "-m",
        "memglide.cli",
        "--db",
        str(database),
        "setup",
        "codex",
        "--project",
        project_id,
    ]
    result = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed["changed"] and observed["registered"] and observed["profile"] == "agent"
    native = subprocess.run(
        ["codex", "mcp", "get", "memglide", "--json"],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    arguments = json.loads(native.stdout)["transport"]["args"]
    assert arguments == [
        "-I",
        "-m",
        "memglide.cli",
        "--db",
        str(database),
        "mcp",
        "--profile",
        "agent",
        "--project",
        project_id,
    ]
    before = (config / "config.toml").read_bytes()
    repeated = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=45)
    assert repeated.returncode == 0, repeated.stderr
    assert json.loads(repeated.stdout)["changed"] is False
    assert (config / "config.toml").read_bytes() == before


def test_unknown_project_cannot_register_an_agent_server(tmp_path: Path) -> None:
    config = tmp_path / "codex"
    config.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-m",
            "memglide.cli",
            "--db",
            str(tmp_path / "state.db"),
            "setup",
            "codex",
            "--project",
            "unapproved-project",
        ],
        env={**os.environ, "CODEX_HOME": str(config)},
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert "unregistered project" in result.stderr
    assert not (config / "config.toml").exists()
