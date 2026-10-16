"""Transport-independent application facade and operational lifecycle."""

from __future__ import annotations

import json
import math
import platform
import shutil
import sqlite3
import threading
from pathlib import Path
from typing import Any

from memglide.core.context import ContextEngine
from memglide.core.indexer import Indexer
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import DEFAULT_SETTINGS, Database, DomainError


class Service:
    def __init__(self, db_path: str | Path | None = None, watch: bool = False):
        self.db = Database(db_path)
        self.indexer = Indexer(self.db)
        self.memory = MemoryEngine(self.db)
        self.context = ContextEngine(self.db, self.indexer, self.memory)
        self._stop = threading.Event()
        self._maintenance: threading.Thread | None = None
        self._watcher: Any = None
        self.memory.cleanup()
        if watch:
            from memglide.core.watcher import RepositoryWatcher

            self._watcher = RepositoryWatcher(self.db, self.indexer)
            self._watcher.start()
            self._maintenance = threading.Thread(target=self._maintain, daemon=True)
            self._maintenance.start()

    def _maintain(self) -> None:
        while not self._stop.wait(15):
            try:
                self.memory.cleanup()
            except sqlite3.Error:
                # Another local operation may temporarily hold a transaction; retry next tick.
                continue

    def close(self) -> None:
        self._stop.set()
        if self._watcher is not None:
            self._watcher.stop()
        if self._maintenance is not None:
            self._maintenance.join(timeout=2)

    def settings(self) -> dict[str, Any]:
        return self.db.settings()

    def update_settings(self, values: dict[str, Any]) -> dict[str, Any]:
        unknown = set(values) - set(DEFAULT_SETTINGS)
        if unknown:
            raise DomainError("Unknown settings: " + ", ".join(sorted(unknown)))
        ranges = {
            "session_ttl_minutes": (1, 480),
            "max_session_hours": (1, 168),
            "context_token_budget": (256, 100000),
            "max_file_size": (1024, 5000000),
        }
        values = dict(values)
        for key, value in values.items():
            if key in ranges:
                low, high = ranges[key]
                if type(value) is not int or not low <= value <= high:
                    raise DomainError(f"{key} must be an integer between {low} and {high}")
            elif key in {"watch_enabled", "event_logging"}:
                if not isinstance(value, bool):
                    raise DomainError(f"{key} must be true or false")
            elif key == "theme" and (
                not isinstance(value, str) or value not in {"dark", "light", "system"}
            ):
                raise DomainError("Theme must be dark, light, or system")
            elif key == "retrieval_weights":
                supported = DEFAULT_SETTINGS["retrieval_weights"]
                if (
                    not isinstance(value, dict)
                    or set(value) - set(supported)
                    or not all(
                        type(v) in {int, float} and math.isfinite(v) and 0 <= v <= 10000
                        for v in value.values()
                    )
                ):
                    raise DomainError(
                        "Retrieval weights must use known names and finite numbers between 0 and 10000"
                    )
                values[key] = {**self.settings()[key], **value}
            elif key == "ignored_directories":
                if (
                    not isinstance(value, list)
                    or len(value) > 100
                    or not all(
                        isinstance(v, str)
                        and 0 < len(v) <= 200
                        and "/" not in v
                        and "\\" not in v
                        and v not in {".", ".."}
                        for v in value
                    )
                ):
                    raise DomainError(
                        "Ignored directories must be a list of simple directory names"
                    )
        with self.db.connect() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO settings VALUES(?,?)",
                [(k, json.dumps(v)) for k, v in values.items()],
            )
        return self.settings()

    def events(
        self,
        project_id: str | None = None,
        session_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        self.memory.cleanup()
        where, params = [], []
        if project_id:
            self.db.project(project_id)
            where.append("project_id=?")
            params.append(project_id)
        if session_id:
            self.memory.status(session_id, project_id=project_id)
            where.append("session_id=?")
            params.append(session_id)
        if event_type:
            where.append("type=?")
            params.append(event_type)
        sql = (
            "SELECT * FROM events"
            + (" WHERE " + " AND ".join(where) if where else "")
            + " ORDER BY created_at DESC LIMIT 500"
        )
        events = self.db.rows(sql, tuple(params))
        for event in events:
            event["detail"] = json.loads(event["detail"])
        return events

    def overview(self) -> dict[str, Any]:
        self.memory.cleanup()
        counts = {
            name: (self.db.one(f"SELECT count(*) AS count FROM {name}") or {"count": 0})["count"]
            for name in ("projects", "files", "symbols", "memories", "retrievals")
        }
        counts["sessions"] = len([s for s in self.memory.list_sessions() if not s.get("ended_at")])
        counts["database_bytes"] = sum(
            p.stat().st_size
            for p in self.db.path.parent.glob(self.db.path.name + "*")
            if p.is_file()
        )
        projects = self.indexer.list_projects()
        warnings = []
        for project in projects:
            errors = project.get("index_stats", {}).get("errors", [])
            if errors:
                warnings.append(
                    f"{project['name']}: {len(errors)} indexing error(s); inspect Projects"
                )
        return {
            "status": "ok",
            "service": "Memglide",
            "version": "0.1.0",
            "mcp": {
                "status": "not_observable",
                "detail": "STDIO clients connect independently; a Codex connection cannot be inferred from HTTP service status.",
            },
            "counts": counts,
            "projects": projects,
            "sessions": self.memory.list_sessions(),
            "recent_retrievals": self.db.rows(
                "SELECT id,session_id,project_id,query,level,budget,estimated_tokens,created_at FROM retrievals ORDER BY created_at DESC LIMIT 20"
            ),
            "recent_events": self.events()[:20],
            "warnings": warnings,
            "settings": self.settings(),
        }

    def diagnostics(self) -> dict[str, Any]:
        from importlib.metadata import version

        with self.db.connect() as conn:
            integrity = conn.execute("PRAGMA quick_check").fetchone()[0]
            fts = conn.execute("SELECT count(*) FROM file_search").fetchone()[0]
        return {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "database": str(self.db.path),
            "database_integrity": integrity,
            "fts5": True,
            "searchable_files": fts,
            "git_available": shutil.which("git") is not None,
            "codex_available": shutil.which("codex") is not None,
            "mcp_sdk": version("mcp"),
            "telemetry": False,
            "frontend_built": (Path(__file__).parent / "web" / "index.html").exists()
            or (Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html").exists(),
        }

    def cleanup(self) -> dict[str, Any]:
        return self.memory.cleanup()
