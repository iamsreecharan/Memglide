"""Debounced local filesystem watching with a polling fallback and clean shutdown."""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from memglide.core.indexer import Indexer
from memglide.security.paths import DEFAULT_IGNORED, secret_path
from memglide.storage.database import Database

logger = logging.getLogger(__name__)


class RepositoryWatcher:
    def __init__(
        self, db: Database, indexer: Indexer, *, debounce: float = 0.4, poll_interval: float = 5.0
    ):
        self.db = db
        self.indexer = indexer
        self.debounce = debounce
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._observer: Any = None
        self._scheduled: dict[str, Any] = {}
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()
        self._lifecycle_lock = threading.Lock()

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        with self._lifecycle_lock:
            if self.running:
                return
            self._scheduled.clear()
            with self._lock:
                self._pending.clear()
            self._stop.clear()
            self._observer = Observer()
            try:
                self._observer.start()
            except OSError:
                logger.warning("Filesystem notifications unavailable; using polling")
                self._observer = None
            self._thread = threading.Thread(target=self._run, name="memglide-watcher", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        with self._lifecycle_lock:
            self._stop.set()
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=3)
            if self._thread:
                self._thread.join(timeout=5)
            # A large scan can outlast the bounded join. Retain its identity and
            # stop event so start() cannot revive it alongside a second worker.
            if not self.running:
                self._thread = None
                self._scheduled.clear()
                with self._lock:
                    self._pending.clear()

    def _handler(self, project_id: str, root: Path) -> FileSystemEventHandler:
        owner = self

        class Handler(FileSystemEventHandler):
            def on_any_event(self, event: FileSystemEvent) -> None:
                if event.event_type in {"opened", "closed", "closed_no_write"}:
                    return
                # Moves can cross an ignored boundary. Either endpoint can make
                # the registered source set change, including moves into root.
                paths = [event.src_path, getattr(event, "dest_path", "")]
                for path in paths:
                    if not path:
                        continue
                    try:
                        relative = Path(str(path)).relative_to(root).as_posix()
                    except ValueError:
                        continue
                    parts = Path(relative).parts
                    if secret_path(relative) or any(p in DEFAULT_IGNORED - {".git"} for p in parts):
                        continue
                    if ".git" in parts and not any(
                        part in {"HEAD", "refs", "index"} for part in parts
                    ):
                        continue
                    with owner._lock:
                        owner._pending[project_id] = time.monotonic()
                    break

        return Handler()

    def _watch_state(self) -> tuple[bool, dict[str, dict[str, str]]]:
        """Read only scheduling fields, without decoding full index reports."""
        with self.db.connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key='watch_enabled'").fetchone()
            enabled = bool(json.loads(row["value"])) if row else False
            projects = {
                row["id"]: dict(row) for row in conn.execute("SELECT id,path FROM projects")
            }
        return enabled, projects

    def _run(self) -> None:
        # Wake promptly for debouncing but refresh small scheduling state at most
        # once a second. Short explicit poll intervals keep their responsiveness.
        control_interval = min(1.0, self.poll_interval)
        next_control = 0.0
        enabled = False
        projects: dict[str, dict[str, str]] = {}
        last_finished: dict[str, float] = {}
        while not self._stop.wait(0.2):
            try:
                now = time.monotonic()
                if now >= next_control:
                    enabled, projects = self._watch_state()
                    next_control = now + control_interval
                    last_finished = {
                        pid: at for pid, at in last_finished.items() if pid in projects
                    }
                    with self._lock:
                        self._pending = {
                            pid: at for pid, at in self._pending.items() if pid in projects
                        }
                if self._observer:
                    for project_id in set(self._scheduled) - (set(projects) if enabled else set()):
                        self._observer.unschedule(self._scheduled.pop(project_id))
                    if enabled:
                        for project_id, project in projects.items():
                            if project_id not in self._scheduled and Path(project["path"]).is_dir():
                                try:
                                    self._scheduled[project_id] = self._observer.schedule(
                                        self._handler(project_id, Path(project["path"])),
                                        project["path"],
                                        recursive=True,
                                    )
                                except OSError:
                                    logger.warning(
                                        "Notifications unavailable for a project; polling remains active"
                                    )
                if not enabled:
                    with self._lock:
                        self._pending.clear()
                    continue
                now = time.monotonic()
                with self._lock:
                    due = {
                        pid
                        for pid, changed in self._pending.items()
                        if now - changed >= self.debounce
                    }
                    for project_id in due:
                        self._pending.pop(project_id, None)
                # Each successful event-driven scan also satisfies the periodic
                # audit. Keep full reconciliation at the existing interval, even
                # if notifications disappear; do not immediately rescan a project
                # that was just refreshed by a debounced event.
                due.update(
                    pid
                    for pid in projects
                    if pid not in last_finished or now - last_finished[pid] >= self.poll_interval
                )
                for project_id in sorted(due & set(projects)):
                    if self._stop.is_set():
                        break
                    try:
                        self.indexer.reindex(project_id)
                    except Exception:
                        logger.exception("Background repository indexing failed")
                    finally:
                        # A slow scan must not trigger continuous audits just
                        # because it took longer than the reconciliation period.
                        # New pending events can still request a prompt refresh.
                        last_finished[project_id] = time.monotonic()
            except Exception:
                logger.exception("Repository watcher iteration failed")
