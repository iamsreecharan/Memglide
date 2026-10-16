"""Memglide's local development and agent integration command line."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Callable

import typer
from rich.console import Console

from memglide.storage.database import DomainError

app = typer.Typer(
    help="Memglide — remember what matters, retrieve what is needed, verify what is missing.",
    no_args_is_help=True,
)
project_app = typer.Typer(
    help="Register and index approved local repositories.", no_args_is_help=True
)
session_app = typer.Typer(help="Manage temporary task sessions.", no_args_is_help=True)
memory_app = typer.Typer(help="Inspect or immediately delete task memory.", no_args_is_help=True)
setup_app = typer.Typer(help="Configure supported coding-agent integrations.", no_args_is_help=True)
app.add_typer(project_app, name="project")
app.add_typer(session_app, name="session")
app.add_typer(memory_app, name="memory")
app.add_typer(setup_app, name="setup")
console = Console()
errors = Console(stderr=True)


@app.callback()
def main(
    ctx: typer.Context,
    db: Path | None = typer.Option(None, "--db", help="Override the local SQLite database path."),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = str(db) if db else None


def _invoke(ctx: typer.Context, operation: Callable[[Any], Any]) -> None:
    from memglide.service import Service

    service = None
    try:
        service = Service(db_path=ctx.obj.get("db_path"))
        result = operation(service)
        console.print_json(json.dumps(result, ensure_ascii=False, default=str))
    except (DomainError, OSError, sqlite3.Error) as error:
        errors.print(f"Error: {error}", markup=False)
        raise typer.Exit(1) from None
    finally:
        if service is not None:
            service.close()


@project_app.command("add")
def project_add(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ..., help="Existing local repository directory to approve and index."
    ),
) -> None:
    """Approve a repository and build its local index without executing source code."""
    _invoke(ctx, lambda s: s.indexer.add_project(str(path)))


@project_app.command("list")
def project_list(ctx: typer.Context) -> None:
    """List registered projects and index statistics."""
    _invoke(ctx, lambda s: s.indexer.list_projects())


@project_app.command("remove")
def project_remove(ctx: typer.Context, project_id: str) -> None:
    """Remove a registration, its index, and associated sessions; keep source files."""
    _invoke(ctx, lambda s: s.indexer.remove_project(project_id))


@project_app.command("reindex")
def project_reindex(
    ctx: typer.Context,
    project_id: str,
    full: bool = typer.Option(
        False, "--full", help="Reparse every eligible file rather than only changed files."
    ),
) -> None:
    """Refresh an approved repository index."""
    _invoke(ctx, lambda s: s.indexer.reindex(project_id, full=full))


@session_app.command("start")
def session_start(
    ctx: typer.Context,
    project_id: str,
    task: str = typer.Option("", "--task", help="Task description for this session."),
) -> None:
    """Start an expiring task session for an approved project."""
    _invoke(ctx, lambda s: s.memory.start_session(project_id, task))


@session_app.command("list")
def session_list(
    ctx: typer.Context,
    project: str | None = typer.Option(None, "--project", help="Filter by registered project ID."),
) -> None:
    """List sessions without extending their inactivity timer."""

    def operation(s: Any) -> Any:
        if project:
            s.db.project(project)
        return s.memory.list_sessions(project)

    _invoke(ctx, operation)


@session_app.command("status")
def session_status(ctx: typer.Context, session_id: str) -> None:
    """Show session status, memory counts, and expiration."""
    _invoke(ctx, lambda s: s.memory.status(session_id))


@session_app.command("clear")
def session_clear(ctx: typer.Context, session_id: str) -> None:
    """Immediately delete a session and all its temporary task data."""
    _invoke(ctx, lambda s: s.memory.clear_session(session_id))


@memory_app.command("list")
def memory_list(
    ctx: typer.Context, session_id: str, category: str | None = typer.Option(None, "--category")
) -> None:
    """List session memories, including provenance and source validity."""
    _invoke(ctx, lambda s: s.memory.recall_memory(session_id, category=category))


@memory_app.command("search")
def memory_search(
    ctx: typer.Context,
    session_id: str,
    query: str,
    category: str | None = typer.Option(None, "--category"),
) -> None:
    """Search a session's explicitly recorded memory."""
    _invoke(ctx, lambda s: s.memory.recall_memory(session_id, query, category))


@memory_app.command("clear")
def memory_clear(ctx: typer.Context, session_id: str) -> None:
    """Delete all memories in a session while keeping the session."""

    def operation(s: Any) -> Any:
        memories = s.memory.recall_memory(session_id)
        for memory in memories:
            s.memory.delete_memory(session_id, memory["id"])
        return {"deleted_memories": len(memories), "session_id": session_id}

    _invoke(ctx, operation)


@app.command("search")
def search(
    ctx: typer.Context, project_id: str, query: str, limit: int = typer.Option(20, min=1, max=100)
) -> None:
    """Search current source evidence in an approved project."""
    _invoke(ctx, lambda s: s.indexer.search(project_id, query, limit))


@app.command("context")
def context(
    ctx: typer.Context,
    session_id: str,
    query: str,
    level: int = typer.Option(1, min=1, max=3),
    budget: int | None = typer.Option(None, min=256, max=100000),
    known_memory_id: list[str] | None = typer.Option(
        None,
        "--known-memory-id",
        help="Legacy memory ID hint; exact versions are required to omit content safely.",
    ),
    known_memory_version: list[str] | None = typer.Option(
        None,
        "--known-memory-version",
        help="Repeat MEMORY_ID=VERSION for exact memory revisions the caller retains.",
    ),
) -> None:
    """Retrieve discovery (1), focused (2), or expanded (3) context and passport."""
    versions: dict[str, str] = {}
    for value in known_memory_version or []:
        memory_id, separator, version = value.partition("=")
        if not separator or not memory_id or not version:
            raise typer.BadParameter("Use MEMORY_ID=VERSION for --known-memory-version")
        if memory_id in versions and versions[memory_id] != version:
            raise typer.BadParameter("Conflicting versions for the same memory ID")
        versions[memory_id] = version
    _invoke(
        ctx,
        lambda s: s.context.get_context(
            session_id,
            query,
            level,
            budget,
            known_memory_ids=known_memory_id,
            known_memory_versions=versions or None,
        ),
    )


@app.command("passport")
def passport(ctx: typer.Context, session_id: str, retrieval_id: str) -> None:
    """Validate source versions and inspect gaps in a previous retrieval."""
    _invoke(ctx, lambda s: s.context.get_passport(session_id, retrieval_id))


@app.command("mcp")
def mcp(ctx: typer.Context) -> None:
    """Run the official MCP v2 STDIO server; diagnostics use stderr."""
    from memglide.integrations.mcp_server import run_server

    run_server(ctx.obj.get("db_path"))


@setup_app.command("codex")
def setup_codex_command(ctx: typer.Context) -> None:
    """Register the STDIO server with Codex, preserving an existing registration."""
    from memglide.integrations.codex import setup_codex

    try:
        console.print_json(json.dumps(setup_codex(ctx.obj.get("db_path"))))
    except (DomainError, OSError) as error:
        errors.print(f"Error: {error}", markup=False)
        raise typer.Exit(1) from None


@app.command("doctor")
def doctor(ctx: typer.Context) -> None:
    """Check storage, FTS5, SDK, frontend, and observed Codex configuration."""
    from memglide.integrations.codex import registration_status

    _invoke(ctx, lambda s: {**s.diagnostics(), "codex": registration_status()})


@app.command("serve")
def serve(
    ctx: typer.Context,
    port: int = typer.Option(8765, min=1, max=65535),
    host: str = typer.Option("127.0.0.1", help="Loopback host only: 127.0.0.1, localhost, or ::1."),
) -> None:
    """Start the loopback dashboard and API, with automatic indexing and expiration."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        errors.print("Error: Memglide serves only on loopback hosts.")
        raise typer.Exit(1)
    import uvicorn

    from memglide.api.app import create_app
    from memglide.service import Service

    uvicorn.run(
        create_app(Service(db_path=ctx.obj.get("db_path"), watch=True)),
        host=host,
        port=port,
        log_level="info",
    )


@app.command("cleanup")
def cleanup(ctx: typer.Context) -> None:
    """Delete expired sessions and their associated temporary task records."""
    _invoke(ctx, lambda s: s.cleanup())


if __name__ == "__main__":
    app()
