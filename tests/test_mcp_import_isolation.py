"""MCP startup must not import a package supplied by the indexed repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from memglide.service import Service


async def test_isolated_mcp_startup_ignores_hostile_cwd_and_pythonpath(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    package = repository / "memglide"
    package.mkdir(parents=True)
    canary = tmp_path / "untrusted_package_executed"
    (package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(canary)!r}).write_text('executed')\n"
        "raise RuntimeError('Untrusted repository package imported')\n"
    )
    (repository / "example.py").write_text("def approved_symbol():\n    return 1\n")
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    service = Service(tmp_path / "state" / "memglide.db")
    try:
        project = service.indexer.add_project(str(repository))
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-I", "-m", "memglide.cli", "--db", str(service.db.path), "mcp"],
            cwd=str(repository),
            env={"PYTHONPATH": str(repository)},
        )
        async with stdio_client(parameters) as (read, write), ClientSession(read, write) as client:
            await client.initialize()
            response = await client.call_tool("list_projects", {})
            assert not response.is_error and response.structured_content is not None
            assert response.structured_content["projects"][0]["id"] == project["id"]
            assert not canary.exists()
    finally:
        service.close()
