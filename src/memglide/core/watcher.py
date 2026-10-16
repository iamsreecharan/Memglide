"""Debounced local filesystem watching with a polling fallback and clean shutdown."""

from __future__ import annotations

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

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        if self.running:
            return
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
        self._stop.set()
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=3)
        if self._thread:
            self._thread.join(timeout=5)
        self._thread = None
        self._scheduled.clear()

    def _handler(self, project_id: str, root: Path) -> FileSystemEventHandler:
        owner = self

        class Handler(FileSystemEventHandler):
            def on_any_event(self, event: FileSystemEvent) -> None:
                if event.event_type in {"opened", "closed", "closed_no_write"}:
                    return
                try:
                    relative = Path(str(event.src_path)).relative_to(root).as_posix()
                except ValueError:
                    return
                parts = Path(relative).parts
                if secret_path(relative) or any(p in DEFAULT_IGNORED - {".git"} for p in parts):
                    return
                if ".git" in parts and not any(part in {"HEAD", "refs", "index"} for part in parts):
                    return
                with owner._lock:
                    owner._pending[project_id] = time.monotonic()

        return Handler()

    def _run(self) -> None:
        last_poll = 0.0
        while not self._stop.wait(0.2):
            try:
                enabled = self.db.settings()["watch_enabled"]
                projects = {p["id"]: p for p in self.indexer.list_projects()}
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
                if now - last_poll >= self.poll_interval:
                    due.update(projects)
                    last_poll = now
                for project_id in sorted(due & set(projects)):
                    if self._stop.is_set():
                        break
                    try:
                        self.indexer.reindex(project_id)
                    except Exception:
                        logger.exception("Background repository indexing failed")
            except Exception:
                logger.exception("Repository watcher iteration failed")
