"""Explicit, source-aware task memory with bounded lifetimes.

Reading session status never extends its life. Only explicitly submitted memories
and retrievals count as activity. Source text is authoritative over stored claims.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator

from memglide.security.paths import SECRET_PATTERN, UNQUOTED_SECRET, read_source
from memglide.storage.database import Database, DomainError, new_id

CATEGORIES = frozenset(
    {
        "observation",
        "decision",
        "error",
        "failed_attempt",
        "verified_fix",
        "open_issue",
        "checkpoint",
    }
)


class MemoryEngine:
    def __init__(self, db: Database):
        self.db = db

    def start_session(self, project_id: str, task: str = "") -> dict[str, Any]:
        self.db.project(project_id)
        if len(task.encode("utf-8")) > 16000:
            raise DomainError("Task description is too large")
        self.cleanup()
        settings = self.db.settings()
        now = time.time()
        absolute = now + float(settings["max_session_hours"]) * 3600
        expiry = min(absolute, now + float(settings["session_ttl_minutes"]) * 60)
        session_id = new_id()
        self.db.execute(
            "INSERT INTO sessions VALUES(?,?,?,?,?,?,?,NULL)",
            (session_id, project_id, task, now, now, expiry, absolute),
        )
        self.db.event(project_id, session_id, "session_started", {"task": task})
        return self.status(session_id)

    def list_sessions(self, project_id: str | None = None) -> list[dict[str, Any]]:
        self.cleanup()
        if project_id is not None:
            self.db.project(project_id)
        sql = "SELECT * FROM sessions"
        args: tuple[Any, ...] = ()
        if project_id is not None:
            sql += " WHERE project_id=?"
            args = (project_id,)
        return [
            self._session_view(s) for s in self.db.rows(sql + " ORDER BY created_at DESC,id", args)
        ]

    @staticmethod
    def _session_view(session: dict[str, Any]) -> dict[str, Any]:
        now = time.time()
        expiry = min(session["expires_at"], session["absolute_expires_at"])
        return {
            **session,
            "active": session["ended_at"] is None and now < expiry,
            "expires_in_seconds": max(0, int(expiry - now)),
        }

    def status(self, session_id: str, project_id: str | None = None) -> dict[str, Any]:
        session = self.history_status(session_id, project_id)
        if session["ended_at"] is not None:
            raise DomainError("Session has ended; start a new session", 410)
        return session

    def history_status(self, session_id: str, project_id: str | None = None) -> dict[str, Any]:
        """Inspect retained lifecycle metadata, including ended sessions, without activity.

        History never permits further work or revives an expired session. Project
        ownership is checked before expiration cleanup to avoid disclosing another
        project's session lifecycle.
        """
        while True:
            session = self.db.one("SELECT * FROM sessions WHERE id=?", (session_id,))
            if session is None or (project_id is not None and project_id != session["project_id"]):
                raise DomainError("Unknown session for this project", 404)
            now = time.time()
            if now < min(session["expires_at"], session["absolute_expires_at"]):
                return self._session_view(session)
            # A useful request may have renewed the session after this read. Check
            # its current deadline again in the DELETE so a stale status snapshot
            # cannot erase a newly renewed session and its associated evidence.
            with self.db.connect() as conn:
                deleted = conn.execute(
                    "DELETE FROM sessions WHERE id=? AND (expires_at<=? OR absolute_expires_at<=?)",
                    (session_id, now, now),
                ).rowcount
            if deleted:
                raise DomainError("Session expired; start a new session", 410)
            # Another request renewed or cleared the row. Inspect its current
            # lifecycle and ownership instead of reporting the obsolete snapshot.

    def touch(self, session_id: str) -> None:
        """Refresh explicit useful activity, always capped by the absolute limit."""
        self.status(session_id)
        with self._active_write(session_id):
            pass

    @contextmanager
    def _active_write(
        self, session_id: str, *, refresh: bool = True
    ) -> Iterator[tuple[sqlite3.Connection, dict[str, Any], Callable[[str, dict[str, Any]], None]]]:
        """Check lifecycle and commit a mutation under the same SQLite write lock.

        Source capture and input validation happen first. A session can end or
        expire during that work; rechecking after BEGIN IMMEDIATE prevents a late
        mutation or TTL refresh from slipping past that transition.
        """
        settings = self.db.settings()
        with self.db.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
            if row is None:
                raise DomainError("Unknown session for this project", 404)
            session = dict(row)
            now = time.time()
            if now >= min(session["expires_at"], session["absolute_expires_at"]):
                raise DomainError("Session expired; start a new session", 410)
            if session["ended_at"] is not None:
                raise DomainError("Session has ended; start a new session", 410)

            def event(kind: str, detail: dict[str, Any]) -> None:
                if settings["event_logging"]:
                    conn.execute(
                        "INSERT INTO events VALUES(?,?,?,?,?,?)",
                        (
                            new_id(),
                            session["project_id"],
                            session_id,
                            kind,
                            json.dumps(detail),
                            time.time(),
                        ),
                    )

            yield conn, session, event
            if refresh:
                ttl = float(settings["session_ttl_minutes"]) * 60
                conn.execute(
                    "UPDATE sessions SET last_activity=?,expires_at=MIN(absolute_expires_at,?) WHERE id=?",
                    (now, now + ttl, session_id),
                )

    def end_session(self, session_id: str) -> dict[str, Any]:
        self.status(session_id)
        with self._active_write(session_id, refresh=False) as (conn, session, event):
            now = time.time()
            conn.execute("UPDATE sessions SET ended_at=? WHERE id=?", (now, session_id))
            event("session_ended", {})
        return self._session_view({**session, "ended_at": now})

    def clear_session(self, session_id: str) -> dict[str, Any]:
        # Deletion also works for expired or ended sessions, without reviving them.
        session = self.db.one("SELECT * FROM sessions WHERE id=?", (session_id,))
        if session is None:
            raise DomainError("Unknown session", 404)
        self.db.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        return {"session_id": session_id, "cleared": True}

    def cleanup(self) -> dict[str, Any]:
        now = time.time()
        with self.db.connect() as conn:
            count = conn.execute(
                "DELETE FROM sessions WHERE expires_at<=? OR absolute_expires_at<=?",
                (now, now),
            ).rowcount
        return {"deleted_sessions": count, "cleaned_at": now}

    @staticmethod
    def _validate_content(content: str, provenance: str) -> None:
        if not content.strip() or not provenance.strip():
            raise DomainError("Memory content and provenance are required")
        if len(content.encode("utf-8")) > 32000 or len(provenance.encode("utf-8")) > 4000:
            raise DomainError("Memory or provenance exceeds the size limit")
        if any(
            pattern.search(value)
            for pattern in (SECRET_PATTERN, UNQUOTED_SECRET)
            for value in (content, provenance)
        ):
            raise DomainError("Memory containing detected credentials is excluded")

    @staticmethod
    def _fingerprint(category: str, content: str, sources: list[dict[str, Any]]) -> str:
        payload = [
            category,
            " ".join(content.split()),
            sorted((s["path"], s["hash"]) for s in sources),
        ]
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()

    @staticmethod
    def version(memory: dict[str, Any]) -> str:
        """Identify an exact submitted claim independently of clocks and deduplication.

        A memory's ID survives edits, and its deduplication fingerprint deliberately
        normalizes whitespace and omits provenance. Neither identifies the evidence
        a caller actually received. Ignore live source-check fields here: the stored
        source hashes identify the claim's references, while freshness is validated
        separately against current files.
        """
        payload = {
            "category": memory["category"],
            "content": memory["content"],
            "provenance": memory["provenance"],
            "sources": sorted(
                (source["path"], source["hash"]) for source in memory.get("sources", [])
            ),
        }
        return hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def _capture_sources(
        self, project_id: str, sources: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        project = self.db.project(project_id)
        captured: dict[str, dict[str, str]] = {}
        if len(sources) > 100:
            raise DomainError("A memory may reference at most 100 sources")
        for source in sources:
            path = source.get("path")
            if not isinstance(path, str):
                raise DomainError("Each memory source needs a relative path")
            try:
                _, current_hash = read_source(
                    project["path"], path, self.db.settings()["max_file_size"]
                )
            except OSError as exc:
                raise DomainError("Memory source is missing or inaccessible") from exc
            if source.get("hash") is not None and source["hash"] != current_hash:
                raise DomainError(
                    "Memory source changed; inspect current source before saving", 409
                )
            captured[path] = {"path": path, "hash": current_hash}
        return [captured[path] for path in sorted(captured)]

    def save_memory(
        self,
        session_id: str,
        category: str,
        content: str,
        provenance: str,
        sources: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        session = self.status(session_id)
        if category not in CATEGORIES:
            raise DomainError("Unknown memory category; use " + ", ".join(sorted(CATEGORIES)))
        self._validate_content(content, provenance)
        captured = self._capture_sources(session["project_id"], sources or [])
        fingerprint = self._fingerprint(category, content, captured)
        now = time.time()
        memory_id = new_id()
        with self._active_write(session_id) as (conn, session, event):
            inserted = conn.execute(
                "INSERT OR IGNORE INTO memories VALUES(?,?,?,?,?,?,?,?,?)",
                (memory_id, session_id, category, content, provenance, now, now, 0, fingerprint),
            ).rowcount
            existing = not inserted
            if inserted:
                conn.executemany(
                    "INSERT INTO memory_sources VALUES(?,?,?)",
                    [(memory_id, s["path"], s["hash"]) for s in captured],
                )
            else:
                memory_id = conn.execute(
                    "SELECT id FROM memories WHERE session_id=? AND fingerprint=?",
                    (session_id, fingerprint),
                ).fetchone()["id"]
            if not existing:
                event("memory_saved", {"memory_id": memory_id, "category": category})
        memory = self._get_memory(session_id, memory_id)
        return {**self._memory_view(memory, session["project_id"]), "deduplicated": bool(existing)}

    def _get_memory(
        self, session_id: str, memory_id: str, conn: sqlite3.Connection | None = None
    ) -> dict[str, Any]:
        query = "SELECT * FROM memories WHERE id=? AND session_id=?"
        params = (memory_id, session_id)
        if conn is None:
            memory = self.db.one(query, params)
        else:
            row = conn.execute(query, params).fetchone()
            memory = dict(row) if row is not None else None
        if memory is None:
            raise DomainError("Unknown memory for this session", 404)
        return memory

    def _memory_view(self, memory: dict[str, Any], project_id: str) -> dict[str, Any]:
        sources = self.db.rows(
            "SELECT path,hash FROM memory_sources WHERE memory_id=? ORDER BY path", (memory["id"],)
        )
        root = self.db.project(project_id)["path"]
        stale = bool(memory["stale"])
        for source in sources:
            try:
                _, source["current_hash"] = read_source(
                    root, source["path"], self.db.settings()["max_file_size"]
                )
                source["current"] = source["hash"] == source["current_hash"]
            except (OSError, DomainError):
                source["current"] = False
            stale = stale or not source["current"]
        if stale and not memory["stale"]:
            self.db.execute("UPDATE memories SET stale=1 WHERE id=?", (memory["id"],))
        result = {k: v for k, v in memory.items() if k != "fingerprint"}
        view = {
            **result,
            "stale": stale,
            "sources": sources,
            "freshness": "Stale" if stale else ("Current" if sources else "Requires inspection"),
        }
        view["version"] = self.version(view)
        return view

    def get_memory_snapshot(self, session_id: str, memory_id: str) -> dict[str, Any]:
        """Read one owned, current memory snapshot without extending session TTL."""
        session = self.status(session_id)
        memory = self._get_memory(session_id, memory_id)
        return self._memory_view(memory, session["project_id"])

    def recall_memory(
        self, session_id: str, query: str = "", category: str | None = None
    ) -> list[dict[str, Any]]:
        session = self.status(session_id)
        if category is not None and category not in CATEGORIES:
            raise DomainError("Unknown memory category")
        sql = "SELECT * FROM memories WHERE session_id=?"
        params: tuple[Any, ...] = (session_id,)
        if category is not None:
            sql += " AND category=?"
            params += (category,)
        memories = self.db.rows(sql + " ORDER BY updated_at DESC,id", params)
        tokens = query.casefold().split()
        memories = [
            m
            for m in memories
            if all(t in (m["content"] + " " + m["provenance"]).casefold() for t in tokens)
        ]
        result = [self._memory_view(m, session["project_id"]) for m in memories]
        self.touch(session_id)
        return result

    def update_memory(
        self, session_id: str, memory_id: str, content: str, provenance: str | None = None
    ) -> dict[str, Any]:
        self.status(session_id)
        memory = self._get_memory(session_id, memory_id)
        self._validate_content(content, memory["provenance"] if provenance is None else provenance)
        try:
            with self._active_write(session_id) as (conn, session, event):
                memory = self._get_memory(session_id, memory_id, conn)
                # Omitting provenance preserves the revision current at commit,
                # including a correction another client committed meanwhile.
                current_provenance = memory["provenance"] if provenance is None else provenance
                sources = [
                    dict(row)
                    for row in conn.execute(
                        "SELECT path,hash FROM memory_sources WHERE memory_id=?", (memory_id,)
                    )
                ]
                fingerprint = self._fingerprint(memory["category"], content, sources)
                conn.execute(
                    "UPDATE memories SET content=?,provenance=?,updated_at=?,fingerprint=? WHERE id=?",
                    (content, current_provenance, time.time(), fingerprint, memory_id),
                )
                event("memory_updated", {"memory_id": memory_id})
        except sqlite3.IntegrityError as exc:
            raise DomainError("An identical memory already exists in this session", 409) from exc
        return self._memory_view(self._get_memory(session_id, memory_id), session["project_id"])

    def invalidate_memory(self, session_id: str, memory_id: str) -> dict[str, Any]:
        self.status(session_id)
        with self._active_write(session_id) as (conn, session, event):
            self._get_memory(session_id, memory_id, conn)
            conn.execute(
                "UPDATE memories SET stale=1,updated_at=? WHERE id=?", (time.time(), memory_id)
            )
            event("memory_invalidated", {"memory_id": memory_id})
        return self._memory_view(self._get_memory(session_id, memory_id), session["project_id"])

    def delete_memory(self, session_id: str, memory_id: str) -> dict[str, Any]:
        self.status(session_id)
        with self._active_write(session_id, refresh=False) as (conn, session, event):
            self._get_memory(session_id, memory_id, conn)
            conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            event("memory_deleted", {"memory_id": memory_id})
        return {"memory_id": memory_id, "deleted": True}
