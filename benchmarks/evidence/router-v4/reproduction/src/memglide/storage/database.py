"""SQLite schema and small transactional storage primitives shared by all transports."""

from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterator

DEFAULT_SETTINGS: dict[str, Any] = {
    "session_ttl_minutes": 60,
    "max_session_hours": 8,
    "context_token_budget": 4000,
    "ignored_directories": [],
    "max_file_size": 512000,
    "watch_enabled": True,
    "event_logging": True,
    "theme": "dark",
    "retrieval_weights": {
        "exact_symbol": 120.0,
        "identifier": 35.0,
        "symbol_path": 45.0,
        "signature": 8.0,
        "file_path": 70.0,
        "path_terms": 30.0,
        "full_text": 10.0,
        "task_overlap": 0.3,
    },
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, path TEXT UNIQUE NOT NULL, name TEXT NOT NULL, branch TEXT, git_state TEXT NOT NULL DEFAULT '{}', indexed_at REAL, index_stats TEXT NOT NULL DEFAULT '{}', created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, path TEXT NOT NULL, hash TEXT NOT NULL, language TEXT NOT NULL, size INTEGER NOT NULL, mtime REAL NOT NULL, structural INTEGER NOT NULL DEFAULT 0, parse_error TEXT, indexed_at REAL NOT NULL, UNIQUE(project_id,path));
CREATE TABLE IF NOT EXISTS symbols(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, file_id TEXT NOT NULL REFERENCES files(id) ON DELETE CASCADE, path TEXT NOT NULL, name TEXT NOT NULL, qualified_name TEXT NOT NULL, kind TEXT NOT NULL, signature TEXT NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, exported INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS symbols_names ON symbols(project_id,name);
CREATE INDEX IF NOT EXISTS symbol_files ON symbols(file_id);
CREATE TABLE IF NOT EXISTS dependencies(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, source_file TEXT NOT NULL, source_symbol TEXT, target_file TEXT, target_symbol TEXT, kind TEXT NOT NULL, reference TEXT NOT NULL, resolved INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS dependency_sources ON dependencies(project_id,source_file);
CREATE INDEX IF NOT EXISTS dependency_targets ON dependencies(project_id,target_file);
CREATE VIRTUAL TABLE IF NOT EXISTS file_search USING fts5(project_id UNINDEXED,path,identifiers,content,tokenize='unicode61');
CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, task TEXT NOT NULL, created_at REAL NOT NULL, last_activity REAL NOT NULL, expires_at REAL NOT NULL, absolute_expires_at REAL NOT NULL, ended_at REAL);
CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS session_projects ON sessions(project_id,created_at DESC,id);
CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, category TEXT NOT NULL, content TEXT NOT NULL, provenance TEXT NOT NULL, created_at REAL NOT NULL, updated_at REAL NOT NULL, stale INTEGER NOT NULL DEFAULT 0, fingerprint TEXT NOT NULL, UNIQUE(session_id,fingerprint));
CREATE TABLE IF NOT EXISTS memory_sources(memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE, path TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(memory_id,path));
CREATE INDEX IF NOT EXISTS memory_source_paths ON memory_sources(path,memory_id);
CREATE TABLE IF NOT EXISTS retrievals(id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, query TEXT NOT NULL, level INTEGER NOT NULL, budget INTEGER NOT NULL, estimated_tokens INTEGER NOT NULL, created_at REAL NOT NULL, result_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS retrieval_sessions ON retrievals(session_id);
CREATE INDEX IF NOT EXISTS retrieval_projects ON retrievals(project_id);
CREATE INDEX IF NOT EXISTS retrieval_created ON retrievals(created_at);
CREATE TABLE IF NOT EXISTS passports(retrieval_id TEXT PRIMARY KEY REFERENCES retrievals(id) ON DELETE CASCADE, session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS passport_sessions ON passports(session_id);
CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE, type TEXT NOT NULL, detail TEXT NOT NULL, created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS event_sessions ON events(session_id,created_at);
CREATE INDEX IF NOT EXISTS event_projects ON events(project_id,created_at);
CREATE INDEX IF NOT EXISTS event_created ON events(created_at);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""


class DomainError(ValueError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def new_id() -> str:
    return uuid.uuid4().hex


class Database:
    def __init__(self, path: str | Path | None = None):
        self._request_settings: ContextVar[dict[str, Any] | None] = ContextVar(
            "memglide_request_settings", default=None
        )
        home = Path(os.environ.get("MEMGLIDE_HOME", Path.home() / ".memglide"))
        self.path = Path(path) if path is not None else home / "memglide.db"
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)
            conn.execute("INSERT OR IGNORE INTO schema_migrations VALUES(1,?)", (time.time(),))
            conn.executemany(
                "INSERT OR IGNORE INTO settings VALUES(?,?)",
                [(k, json.dumps(v)) for k, v in DEFAULT_SETTINGS.items()],
            )
        self.path.chmod(0o600)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql, params)]

    def one(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self.rows(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        with self.connect() as conn:
            conn.execute(sql, params)

    def settings(self) -> dict[str, Any]:
        snapshot = self._request_settings.get()
        if snapshot is not None:
            return deepcopy(snapshot)
        return {row["key"]: json.loads(row["value"]) for row in self.rows("SELECT * FROM settings")}

    @contextmanager
    def settings_snapshot(self) -> Iterator[dict[str, Any]]:
        """Use one read-only settings view for a synchronous application request.

        Context-local state keeps concurrent requests independent. Nested work
        shares the outer view; exiting the request always discards it, including
        on errors. Defensive copies prevent caller changes from altering the view.
        """
        existing = self._request_settings.get()
        if existing is not None:
            yield deepcopy(existing)
            return
        snapshot = self.settings()
        token = self._request_settings.set(snapshot)
        try:
            yield deepcopy(snapshot)
        finally:
            self._request_settings.reset(token)

    def event(
        self,
        project_id: str,
        session_id: str | None,
        kind: str,
        detail: dict[str, Any] | None = None,
    ) -> None:
        if self.settings()["event_logging"]:
            self.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?)",
                (new_id(), project_id, session_id, kind, json.dumps(detail or {}), time.time()),
            )

    def project(self, project_id: str) -> dict[str, Any]:
        project = self.one("SELECT * FROM projects WHERE id=?", (project_id,))
        if not project:
            raise DomainError("Unknown or unregistered project", 404)
        return project
