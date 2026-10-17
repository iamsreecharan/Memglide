"""Exercise the bound compact profile over real MCP STDIO, not only adapters."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from test_agent_context import build_agent_service

from memglide.integrations.mcp_server import create_server
from memglide.storage.database import DomainError


@pytest.mark.parametrize(
    "arguments",
    [
        {"profile": "agent"},
        {"profile": "arbitrary"},
        {"profile": "default", "project_id": "anything"},
    ],
)
def test_profile_requires_explicit_supported_project_binding(arguments: Any) -> None:
    with pytest.raises(DomainError):
        create_server(**arguments)


@pytest.mark.asyncio
async def test_actual_agent_stdio_has_two_tools_and_verifies_post_edit_sources(
    tmp_path: Path,
) -> None:
    service, root, project_id = build_agent_service(tmp_path)
    try:
        params = StdioServerParameters(
            command=sys.executable,
            args=[
                "-I",
                "-m",
                "memglide.cli",
                "--db",
                str(service.db.path),
                "mcp",
                "--profile",
                "agent",
                "--project",
                project_id,
            ],
            env={**os.environ, "MEMGLIDE_HOME": str(service.db.path.parent)},
        )
        async with stdio_client(params) as (read, write), ClientSession(read, write) as client:
            await client.initialize()
            tools = (await client.list_tools()).tools
            assert {tool.name for tool in tools} == {"fetch_context", "verify_context"}
            # A native JSON text result advertises no structured-output schema;
            # the SDK must not demand an absent structuredContent duplicate.
            assert all(tool.output_schema is None for tool in tools)
            fetch_schema = next(tool.input_schema for tool in tools if tool.name == "fetch_context")
            assert fetch_schema["required"] == ["query"]
            assert fetch_schema["properties"]["budget"]["default"] == 4000
            verify_schema = next(
                tool.input_schema for tool in tools if tool.name == "verify_context"
            )
            assert not verify_schema.get("required")
            rejected = await client.call_tool("fetch_context", {})
            assert rejected.is_error
            assert service.memory.list_sessions() == []
            unknown = await client.call_tool("verify_context", {})
            assert unknown.is_error
            assert "Fetch context first" in str(unknown.content)

            actual = await client.call_tool("fetch_context", {"query": "Fix add_item"})
            assert not actual.is_error, actual
            assert actual.structured_content is None
            assert len(actual.content) == 1 and actual.content[0].type == "text"
            context = json.loads(actual.content[0].text)
            assert context["operation"] == "get_context"
            assert any("def add_item" in item["snippet"] for item in context["items"])
            assert context["source_hashes"]["inventory.py"]
            assert len(service.memory.list_sessions(project_id)) == 1

            verified = await client.call_tool("verify_context", {})
            assert not verified.is_error
            assert verified.structured_content is None
            assert len(verified.content) == 1 and verified.content[0].type == "text"
            assert json.loads(verified.content[0].text)["source_freshness"] == "Current"
            source = root / "inventory.py"
            source.write_text(source.read_text().replace("+ count", "+ count * 2"))
            stale = await client.call_tool("verify_context", {})
            assert not stale.is_error
            assert stale.structured_content is None
            assert len(stale.content) == 1 and stale.content[0].type == "text"
            stale_payload = json.loads(stale.content[0].text)
            assert stale_payload["stale_files"] == ["inventory.py"]
            assert stale_payload["source_freshness"] == "Stale"
            assert "passport" not in context and "session_id" not in context
            assert "complete" not in json.dumps(context)
    finally:
        service.close()

    # Closing the actual transport ends its private session rather than leaving
    # active sessions behind until the expiration sweep.
    assert not any(row["active"] for row in service.memory.list_sessions(project_id))
