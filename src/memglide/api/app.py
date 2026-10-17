"""Loopback dashboard API. All behavior is delegated to shared application services."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from memglide.storage.database import DomainError

logger = logging.getLogger(__name__)


class Record(BaseModel):
    """Preserve service metadata while documenting common response fields."""

    model_config = ConfigDict(extra="allow")


class Project(Record):
    id: str
    path: str
    name: str


class Session(Record):
    id: str
    project_id: str
    task: str


class Memory(Record):
    id: str
    session_id: str
    category: str
    content: str
    provenance: str


class Health(Record):
    status: str
    local_only: bool


class Settings(BaseModel):
    session_ttl_minutes: int
    max_session_hours: int
    context_token_budget: int
    ignored_directories: list[str]
    max_file_size: int
    watch_enabled: bool
    event_logging: bool
    theme: Literal["dark", "light", "system"]
    retrieval_weights: dict[str, float] = Field(default_factory=dict)


class SettingsUpdate(BaseModel):
    # Keep transport validation aligned with the shared service. Coercion would
    # turn true into a one-minute TTL or a boolean into a numeric search weight.
    model_config = ConfigDict(extra="forbid", strict=True)
    session_ttl_minutes: int | None = Field(None, ge=1, le=480)
    max_session_hours: int | None = Field(None, ge=1, le=168)
    context_token_budget: int | None = Field(None, ge=256, le=100000)
    ignored_directories: list[str] | None = None
    max_file_size: int | None = Field(None, ge=1024, le=5000000)
    watch_enabled: bool | None = None
    event_logging: bool | None = None
    theme: Literal["dark", "light", "system"] | None = None
    retrieval_weights: dict[str, float] | None = None


class ProjectCreate(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class Reindex(BaseModel):
    full: bool = False


class SessionCreate(BaseModel):
    project_id: str
    task: str = Field("", max_length=20000)


class MemoryCreate(BaseModel):
    category: str
    content: str = Field(min_length=1, max_length=100000)
    provenance: str = Field(min_length=1, max_length=20000)
    sources: list[dict[str, Any]] | None = None


class MemoryUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=100000)
    provenance: str | None = Field(None, min_length=1, max_length=20000)


class Search(BaseModel):
    project_id: str
    query: str = Field(min_length=1, max_length=20000)
    limit: int = Field(20, ge=1, le=100)


class ContextRequest(BaseModel):
    session_id: str
    query: str = Field(min_length=1, max_length=20000)
    level: int = Field(1, ge=1, le=3)
    budget: int | None = Field(None, ge=256, le=100000)
    known_memory_ids: list[str] | None = Field(None, max_length=1000)
    known_memory_versions: dict[str, str] | None = Field(None, max_length=1000)


class ExpandRequest(BaseModel):
    session_id: str
    level: int | None = Field(None, ge=1, le=3)
    budget: int | None = Field(None, ge=256, le=100000)
    known_memory_ids: list[str] | None = Field(None, max_length=1000)
    known_memory_versions: dict[str, str] | None = Field(None, max_length=1000)


class ContextResult(Record):
    retrieval_id: str
    session_id: str
    project_id: str
    query: str
    level: int
    budget: int
    estimated_tokens: int
    items: list[dict[str, Any]]
    passport: dict[str, Any]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


def _error(message: str, status: int, code: str = "request_error") -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


def _loopback_host(host: str) -> bool:
    try:
        parsed = urlsplit("//" + host)
        return (
            parsed.hostname in {"localhost", "127.0.0.1", "::1"}
            and parsed.username is None
            and parsed.password is None
            and parsed.path == ""
            and parsed.query == ""
            and parsed.fragment == ""
            and (parsed.port is None or 1 <= parsed.port <= 65535)
        )
    except ValueError:
        return False


def create_app(service: Any = None) -> FastAPI:
    """Create an app; explicit service injection keeps tests and embedded use isolated."""
    if service is None:
        from memglide.service import Service

        service = Service(watch=True)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            service.close()

    app = FastAPI(
        title="Memglide local API",
        version="0.1.0",
        lifespan=lifespan,
        responses={
            400: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            410: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
        },
    )
    app.state.service = service

    @app.middleware("http")
    async def browser_protection(request: Request, call_next: Any):
        host = request.headers.get("host", "")
        if not _loopback_host(host):
            return _error("Only loopback Host headers are accepted", 403, "forbidden_host")
        origin = request.headers.get("origin")
        if origin is not None:
            expected = f"{request.url.scheme}://{host}"
            if origin.rstrip("/") != expected:
                return _error("Cross-origin requests are not allowed", 403, "forbidden_origin")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("x-memglide-request") != "1":
                return _error(
                    "State changes require X-Memglide-Request: 1", 403, "missing_request_header"
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(DomainError)
    async def domain_error(_: Request, error: DomainError):
        return _error(str(error), error.status, "domain_error")

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, error: StarletteHTTPException):
        return _error(str(error.detail), error.status_code, "http_error")

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_: Request, error: RequestValidationError):
        # Pydantic error input can contain submitted source or secrets; do not echo it.
        details = [
            {"location": list(e["loc"]), "message": e["msg"], "type": e["type"]}
            for e in error.errors()
        ]
        return JSONResponse(
            {
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request",
                    "details": details,
                }
            },
            status_code=422,
        )

    @app.exception_handler(Exception)
    async def unexpected_error(_: Request, error: Exception):
        logger.error("Unhandled local API error: %s", type(error).__name__)
        return _error("Internal error; consult local service diagnostics", 500, "internal_error")

    @app.get("/api/health", response_model=Health)
    def health():
        return {"status": "ok", "local_only": True, "version": "0.1.0"}

    @app.get("/api/overview", response_model=Record)
    def overview():
        return service.overview()

    @app.get("/api/projects", response_model=list[Project])
    def projects():
        return service.indexer.list_projects()

    @app.post("/api/projects", response_model=Project, status_code=201)
    def add_project(body: ProjectCreate):
        return service.indexer.add_project(body.path)

    @app.get("/api/projects/{project_id}", response_model=Project)
    def project(project_id: str):
        matches = [p for p in service.indexer.list_projects() if p["id"] == project_id]
        if not matches:
            raise DomainError("Unknown or unregistered project", 404)
        return matches[0]

    @app.delete("/api/projects/{project_id}", response_model=Record)
    def remove_project(project_id: str):
        result = service.indexer.remove_project(project_id)
        return result or {"removed": True, "project_id": project_id}

    @app.post("/api/projects/{project_id}/reindex", response_model=Record)
    def reindex(project_id: str, body: Reindex):
        return service.indexer.reindex(project_id, full=body.full)

    @app.get("/api/sessions", response_model=list[Session])
    def sessions(project_id: str | None = None):
        if project_id is not None:
            service.db.project(project_id)
        return service.memory.list_sessions(project_id)

    @app.post("/api/sessions", response_model=Session, status_code=201)
    def start_session(body: SessionCreate):
        return service.memory.start_session(body.project_id, body.task)

    @app.get("/api/sessions/{session_id}", response_model=Session)
    def session_status(session_id: str):
        return service.memory.status(session_id)

    @app.delete("/api/sessions/{session_id}", response_model=Record)
    def end_session(session_id: str):
        return service.memory.end_session(session_id)

    @app.post("/api/sessions/{session_id}/clear", response_model=Record)
    def clear_session(session_id: str):
        return service.memory.clear_session(session_id)

    @app.get("/api/sessions/{session_id}/memories", response_model=list[Memory])
    def memories(session_id: str, query: str = "", category: str | None = None):
        return service.memory.recall_memory(session_id, query, category)

    @app.post("/api/sessions/{session_id}/memories", response_model=Memory, status_code=201)
    def save_memory(session_id: str, body: MemoryCreate):
        return service.memory.save_memory(
            session_id, body.category, body.content, body.provenance, body.sources
        )

    @app.patch("/api/sessions/{session_id}/memories/{memory_id}", response_model=Memory)
    def update_memory(session_id: str, memory_id: str, body: MemoryUpdate):
        return service.memory.update_memory(session_id, memory_id, body.content, body.provenance)

    @app.delete("/api/sessions/{session_id}/memories/{memory_id}", response_model=Record)
    def delete_memory(session_id: str, memory_id: str):
        return service.memory.delete_memory(session_id, memory_id)

    @app.post("/api/sessions/{session_id}/memories/{memory_id}/invalidate", response_model=Memory)
    def invalidate_memory(session_id: str, memory_id: str):
        return service.memory.invalidate_memory(session_id, memory_id)

    @app.post("/api/search", response_model=list[Record])
    def search(body: Search):
        return service.indexer.search(body.project_id, body.query, body.limit)

    @app.post("/api/context", response_model=ContextResult)
    def context(body: ContextRequest):
        return service.context.get_context(
            body.session_id,
            body.query,
            body.level,
            body.budget,
            known_memory_ids=body.known_memory_ids,
            known_memory_versions=body.known_memory_versions,
        )

    @app.post("/api/context/{retrieval_id}/expand", response_model=ContextResult)
    def expand(retrieval_id: str, body: ExpandRequest):
        return service.context.expand_context(
            body.session_id,
            retrieval_id,
            body.level,
            body.budget,
            known_memory_ids=body.known_memory_ids,
            known_memory_versions=body.known_memory_versions,
        )

    @app.get("/api/context/{retrieval_id}/passport", response_model=Record)
    def passport(retrieval_id: str, session_id: str):
        return service.context.get_passport(session_id, retrieval_id)

    @app.get("/api/events", response_model=list[Record])
    def events(
        project_id: str | None = None, session_id: str | None = None, event_type: str | None = None
    ):
        return service.events(project_id=project_id, session_id=session_id, event_type=event_type)

    @app.get("/api/settings", response_model=Settings)
    def settings():
        return service.settings()

    @app.put("/api/settings", response_model=Settings)
    def update_settings(body: SettingsUpdate):
        return service.update_settings(body.model_dump(exclude_unset=True, exclude_none=True))

    @app.get("/api/diagnostics", response_model=Record)
    def diagnostics():
        return service.diagnostics()

    @app.post("/api/cleanup", response_model=Record)
    def cleanup():
        return service.cleanup()

    bundled = Path(__file__).resolve().parents[1] / "web"
    development = Path(__file__).resolve().parents[3] / "frontend" / "dist"
    web_root = bundled if (bundled / "index.html").is_file() else development

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            return _error("Unknown API route", 404, "not_found")
        candidate = (web_root / path).resolve()
        if not candidate.is_relative_to(web_root.resolve()) or any(
            p.startswith(".") for p in Path(path).parts
        ):
            return _error("Unknown resource", 404, "not_found")
        if candidate.is_file():
            return FileResponse(candidate)
        if "." not in Path(path).name and (web_root / "index.html").is_file():
            return FileResponse(web_root / "index.html")
        return _error(
            "Dashboard assets unavailable; build frontend with npm run build", 404, "not_found"
        )

    return app
