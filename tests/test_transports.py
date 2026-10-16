"""Exercise HTTP, CLI, actual SDK STDIO, and isolated actual Codex registration."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from typer.testing import CliRunner

from memglide.api.app import create_app
from memglide.cli import app
from memglide.service import Service

HEADER = {"X-Memglide-Request": "1"}


@pytest.fixture
def application(tmp_path: Path):
    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "auth.py").write_text(
        'def authenticate_user(token: str) -> bool:\n    """Verify a user token."""\n    return token == "valid"\n'
    )
    (repo / "app.py").write_text(
        "from auth import authenticate_user\n\ndef login(token):\n    return authenticate_user(token)\n"
    )
    service = Service(tmp_path / "state" / "memglide.db")
    project = service.indexer.add_project(str(repo))
    session = service.memory.start_session(project["id"], "Verify authentication")
    yield service, repo, project, session
    service.close()


def test_http_complete_route_workflow(application: Any):
    service, repo, project, session = application
    sid, pid = session["id"], project["id"]
    with TestClient(create_app(service), base_url="http://127.0.0.1:7432") as client:
        health = client.get("/api/health")
        assert health.json()["status"] == "ok"
        assert health.headers["cache-control"] == "no-store"
        assert health.headers["x-content-type-options"] == "nosniff"
        assert client.get("/api/projects").json()[0]["id"] == pid
        assert client.get(f"/api/projects/{pid}").json()["path"] == str(repo)
        assert client.get("/api/overview").json()["counts"]["projects"] == 1
        assert client.get("/api/sessions", params={"project_id": pid}).json()[0]["id"] == sid
        assert client.get(f"/api/sessions/{sid}").json()["active"]
        response = client.post(
            "/api/search", json={"project_id": pid, "query": "authenticate_user"}, headers=HEADER
        )
        assert response.status_code == 200, response.text
        assert response.json()
        created = client.post(
            f"/api/sessions/{sid}/memories",
            json={
                "category": "observation",
                "content": "Authentication validates a token",
                "provenance": "inspected auth.py",
                "sources": [{"path": "auth.py"}],
            },
            headers=HEADER,
        )
        assert created.status_code == 201, created.text
        mid = created.json()["id"]
        known_context = client.post(
            "/api/context",
            json={
                "session_id": sid,
                "query": "Authentication",
                "budget": 8000,
                "known_memory_ids": [mid],
            },
            headers=HEADER,
        )
        assert known_context.status_code == 200, known_context.text
        known_memory = next(m for m in known_context.json()["memories"] if m["id"] == mid)
        assert known_memory["content_omitted"] and "content" not in known_memory
        assert (
            client.get(f"/api/sessions/{sid}/memories", params={"query": "validates"}).json()[0][
                "id"
            ]
            == mid
        )
        assert (
            client.patch(
                f"/api/sessions/{sid}/memories/{mid}",
                json={"content": "Authentication verifies an exact token"},
                headers=HEADER,
            ).status_code
            == 200
        )
        assert client.post(f"/api/sessions/{sid}/memories/{mid}/invalidate", headers=HEADER).json()[
            "stale"
        ]
        context = client.post(
            "/api/context",
            json={"session_id": sid, "query": "authenticate_user", "budget": 2000},
            headers=HEADER,
        )
        assert context.status_code == 200, context.text
        rid = context.json()["retrieval_id"]
        passport = client.get(f"/api/context/{rid}/passport", params={"session_id": sid})
        assert passport.status_code == 200, passport.text
        expanded = client.post(
            f"/api/context/{rid}/expand", json={"session_id": sid, "level": 2}, headers=HEADER
        )
        assert expanded.status_code == 200, expanded.text
        assert expanded.json()["level"] == 2
        assert client.get("/api/events", params={"session_id": sid}).json()
        assert (
            client.put(
                "/api/settings",
                json={"context_token_budget": 3072, "theme": "light"},
                headers=HEADER,
            ).json()["context_token_budget"]
            == 3072
        )
        assert client.get("/api/settings").json()["theme"] == "light"
        weights = client.put(
            "/api/settings", json={"retrieval_weights": {"exact_symbol": 125.0}}, headers=HEADER
        )
        assert weights.status_code == 200, weights.text
        assert weights.json()["retrieval_weights"]["exact_symbol"] == 125.0
        assert client.get("/api/settings").json()["retrieval_weights"]["exact_symbol"] == 125.0
        assert client.get("/api/diagnostics").json()["database_integrity"] == "ok"
        assert (
            client.post(
                f"/api/projects/{pid}/reindex", json={"full": True}, headers=HEADER
            ).status_code
            == 200
        )
        assert (
            client.delete(f"/api/sessions/{sid}/memories/{mid}", headers=HEADER).status_code == 200
        )
        assert client.get(f"/api/sessions/{sid}/memories").json() == []
        assert client.post(f"/api/sessions/{sid}/clear", headers=HEADER).status_code == 200
        assert client.get(f"/api/sessions/{sid}").status_code == 404
        started = client.post(
            "/api/sessions", json={"project_id": pid, "task": "Delete test"}, headers=HEADER
        )
        assert started.status_code == 201
        assert (
            client.delete(f"/api/sessions/{started.json()['id']}", headers=HEADER).status_code
            == 200
        )
        assert client.post("/api/cleanup", headers=HEADER).status_code == 200
        assert client.delete(f"/api/projects/{pid}", headers=HEADER).status_code == 200
        assert (repo / "auth.py").is_file()
        assert client.get("/api/projects").json() == []


def test_http_security_validation_and_isolation(application: Any):
    service, _, project, session = application
    with TestClient(create_app(service), base_url="http://localhost:7432") as client:
        assert client.get("/api/health", headers={"host": "attacker.example"}).status_code == 403
        assert (
            client.get("/api/health", headers={"host": "localhost.attacker.example"}).status_code
            == 403
        )
        assert (
            client.get("/api/health", headers={"host": "localhost@attacker.example"}).status_code
            == 403
        )
        assert (
            client.get("/api/health", headers={"origin": "https://evil.example"}).status_code == 403
        )
        assert client.post("/api/cleanup").status_code == 403
        assert (
            client.post(
                "/api/cleanup", headers={**HEADER, "origin": "http://localhost:7432"}
            ).status_code
            == 200
        )
        response = client.post(
            "/api/context",
            json={"session_id": session["id"], "query": "auth", "level": 9},
            headers=HEADER,
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"
        assert "input" not in json.dumps(response.json())
        assert client.get("/api/projects/unregistered").status_code == 404
        assert client.get("/api/unknown").status_code == 404
        wrong_method = client.patch("/api/health", headers=HEADER)
        assert wrong_method.status_code == 405
        assert wrong_method.json()["error"]["code"] == "http_error"
        assert (
            client.post(
                "/api/sessions", json={"project_id": "unregistered"}, headers=HEADER
            ).status_code
            == 404
        )
        context = client.post(
            "/api/context",
            json={"session_id": session["id"], "query": "authenticate_user"},
            headers=HEADER,
        ).json()
        other = client.post(
            "/api/sessions", json={"project_id": project["id"]}, headers=HEADER
        ).json()
        assert (
            client.get(
                f"/api/context/{context['retrieval_id']}/passport",
                params={"session_id": other["id"]},
            ).status_code
            == 404
        )
        schema = client.get("/openapi.json").json()
        assert "ProjectCreate" in schema["components"]["schemas"]
        assert "ContextResult" in schema["components"]["schemas"]


def test_cli_commands_and_friendly_errors(application: Any):
    service, _, project, session = application
    runner = CliRunner()
    prefix = ["--db", str(service.db.path)]
    for command in ([], ["project"], ["session"], ["memory"], ["setup"]):
        assert runner.invoke(app, [*command, "--help"]).exit_code == 0
    for command in (
        ["project", "list"],
        ["session", "list"],
        ["session", "status", session["id"]],
        ["memory", "list", session["id"]],
        ["search", project["id"], "authenticate_user"],
        ["context", session["id"], "authenticate_user", "--level", "2"],
        ["cleanup"],
    ):
        response = runner.invoke(app, [*prefix, *command])
        assert response.exit_code == 0, response.output
        json.loads(response.output)
    missing = runner.invoke(app, [*prefix, "session", "status", "unknown"])
    assert missing.exit_code == 1
    assert "Unknown session" in missing.output
    forbidden = runner.invoke(app, [*prefix, "serve", "--host", "0.0.0.0"])
    assert forbidden.exit_code == 1
    assert "loopback" in forbidden.output


@pytest.mark.asyncio
async def test_actual_mcp_stdio_client_discovers_and_calls_every_tool(application: Any):
    service, _, project, _ = application
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "memglide.cli", "--db", str(service.db.path), "mcp"],
        env={
            "MEMGLIDE_HOME": str(service.db.path.parent),
            "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
        },
    )
    expected = {
        "list_projects",
        "start_session",
        "get_session_status",
        "search_code",
        "get_symbol",
        "get_dependencies",
        "get_context",
        "expand_context",
        "get_context_passport",
        "save_memory",
        "recall_memory",
        "update_memory",
        "invalidate_memory",
        "end_session",
    }
    async with stdio_client(params) as (read, write), ClientSession(read, write) as client:
        initialized = await client.initialize()
        assert initialized.server_info.name == "Memglide"
        discovered = await client.list_tools()
        assert {tool.name for tool in discovered.tools} == expected
        assert all(tool.output_schema for tool in discovered.tools)
        called: set[str] = set()

        async def invoke(name: str, **arguments: Any) -> dict[str, Any]:
            result = await client.call_tool(name, arguments)
            assert not result.is_error, (name, result)
            assert result.structured_content is not None, name
            called.add(name)
            return result.structured_content

        projects = await invoke("list_projects")
        assert projects["projects"][0]["id"] == project["id"]
        session = await invoke("start_session", project_id=project["id"], task="Actual STDIO test")
        sid = session["id"]
        assert (await invoke("get_session_status", session_id=sid))["active"]
        assert (await invoke("search_code", project_id=project["id"], query="authenticate_user"))[
            "results"
        ]
        assert (await invoke("get_symbol", project_id=project["id"], symbol="authenticate_user"))[
            "name"
        ]
        await invoke(
            "get_dependencies", project_id=project["id"], symbol_or_path="authenticate_user"
        )
        context = await invoke(
            "get_context", session_id=sid, query="authenticate_user", budget=2000
        )
        await invoke(
            "expand_context", session_id=sid, retrieval_id=context["retrieval_id"], level=2
        )
        await invoke("get_context_passport", session_id=sid, retrieval_id=context["retrieval_id"])
        memory = await invoke(
            "save_memory",
            session_id=sid,
            category="observation",
            content="Token verification is in auth.py",
            provenance="actual MCP transport test",
            sources=[{"path": "auth.py"}],
        )
        assert (await invoke("recall_memory", session_id=sid, query="verification"))["memories"]
        known_context = await invoke(
            "get_context",
            session_id=sid,
            query="Token verification",
            budget=8000,
            known_memory_ids=[memory["id"]],
        )
        known_memory = next(m for m in known_context["memories"] if m["id"] == memory["id"])
        assert known_memory["content_omitted"] and "content" not in known_memory
        await invoke(
            "update_memory",
            session_id=sid,
            memory_id=memory["id"],
            content="Token verification compares against a valid token",
        )
        await invoke("invalidate_memory", session_id=sid, memory_id=memory["id"])
        rejected = await client.call_tool(
            "get_session_status", {"session_id": sid, "project_id": "unregistered"}
        )
        assert rejected.is_error
        assert "Unknown session" in str(rejected.content)
        await invoke("end_session", session_id=sid)
        expired = await client.call_tool("get_session_status", {"session_id": sid})
        assert expired.is_error
        assert "ended" in str(expired.content)
        assert called == expected


def test_actual_codex_supported_registration_preserves_existing():
    if shutil.which("codex") is None:
        pytest.skip("Codex CLI is not installed")
    # Pass Codex's documented configuration selector only to isolated subprocesses.
    runtime = Path(__file__).resolve().parents[1] / ".runtime"
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-test-", dir=runtime) as directory:
        codex_test_env = {**os.environ, "CODEX_HOME": directory}
        command = [sys.executable, "-m", "memglide.cli", "setup", "codex"]
        first = subprocess.run(
            command, env=codex_test_env, capture_output=True, text=True, timeout=45
        )
        assert first.returncode == 0, first.stderr
        result = json.loads(first.stdout)
        assert result["changed"] and result["registered"]
        assert result["connection"] == "not_observable"
        before = (Path(directory) / "config.toml").read_bytes()
        second = subprocess.run(
            command, env=codex_test_env, capture_output=True, text=True, timeout=45
        )
        assert second.returncode == 0, second.stderr
        assert not json.loads(second.stdout)["changed"]
        assert (Path(directory) / "config.toml").read_bytes() == before
        assert "args" not in result and "env" not in result


@pytest.mark.parametrize(
    "returncode,output", [(1, ""), (0, "invalid JSON"), (0, '{"wrong":"shape"}')]
)
def test_codex_unreadable_configuration_never_triggers_add(
    monkeypatch: pytest.MonkeyPatch, returncode: int, output: str
):
    from memglide.integrations import codex
    from memglide.storage.database import DomainError

    commands: list[list[str]] = []
    monkeypatch.setattr(codex.shutil, "which", lambda _: "/test/codex")

    def run(command: list[str], **_: Any):
        commands.append(command)
        return subprocess.CompletedProcess(command, returncode, stdout=output, stderr="")

    monkeypatch.setattr(codex.subprocess, "run", run)
    with pytest.raises(DomainError, match="Cannot safely inspect"):
        codex.setup_codex()
    assert len(commands) == 1
    assert commands[0][1:] == ["mcp", "list", "--json"]


def test_codex_diagnostics_do_not_expose_configured_arguments_or_environment(
    monkeypatch: pytest.MonkeyPatch,
):
    from memglide.integrations import codex

    marker = "sensitive-test-value-never-returned"
    configuration = [
        {
            "name": "memglide",
            "transport": {
                "type": "stdio",
                "command": "/approved/bin/python",
                "args": [marker],
                "env": {"API_TOKEN": marker},
            },
        }
    ]
    monkeypatch.setattr(codex.shutil, "which", lambda _: "/test/codex")
    monkeypatch.setattr(
        codex.subprocess,
        "run",
        lambda command, **_: subprocess.CompletedProcess(
            command, 0, stdout=json.dumps(configuration), stderr=""
        ),
    )
    status = codex.registration_status()
    assert status["registered"]
    assert status["command"] == "python"
    assert marker not in json.dumps(status)
