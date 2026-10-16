"""The real CLI must acknowledge a revision, not merely a mutable memory ID."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from memglide.cli import app
from memglide.service import Service


def test_cli_matching_stale_and_id_only_acknowledgements(tmp_path: Path) -> None:
    repo = tmp_path / "repository"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "tokens.py").write_text("def verify_token(value):\n    return bool(value)\n")
    database = tmp_path / "state" / "memory.sqlite"
    service = Service(database)
    try:
        project = service.indexer.add_project(str(repo))
        session = service.memory.start_session(project["id"], "verify_token")
        saved = service.memory.save_memory(
            session["id"],
            "observation",
            "verify_token checks presence",
            "inspected tokens.py",
            [{"path": "tokens.py"}],
        )
        runner = CliRunner()
        arguments = [
            "--db",
            str(database),
            "context",
            session["id"],
            "verify_token",
            "--level",
            "2",
            "--budget",
            "8000",
        ]
        compact = runner.invoke(
            app, [*arguments, "--known-memory-version", f"{saved['id']}={saved['version']}"]
        )
        assert compact.exit_code == 0, compact.output
        assert json.loads(compact.output)["memories"][0]["content_omitted"]
        changed = service.memory.update_memory(
            session["id"],
            saved["id"],
            "verify_token does not validate a signature",
            "reviewed implementation",
        )
        stale = runner.invoke(
            app, [*arguments, "--known-memory-version", f"{saved['id']}={saved['version']}"]
        )
        assert stale.exit_code == 0, stale.output
        current = json.loads(stale.output)["memories"][0]
        assert current["content"] == changed["content"]
        assert current["version"] == changed["version"]
        id_only = runner.invoke(app, [*arguments, "--known-memory-id", saved["id"]])
        assert id_only.exit_code == 0, id_only.output
        assert json.loads(id_only.output)["memories"][0]["content"] == changed["content"]
        malformed = runner.invoke(app, [*arguments, "--known-memory-version", "missing-separator"])
        assert malformed.exit_code == 2
        assert "MEMORY_ID=VERSION" in malformed.output
    finally:
        service.close()
