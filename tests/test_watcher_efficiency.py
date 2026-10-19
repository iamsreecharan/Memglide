"""Watcher bookkeeping stays cheap without relying on notifications for freshness."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from watchdog.events import FileModifiedEvent, FileMovedEvent

from memglide.core.watcher import RepositoryWatcher
from memglide.storage.database import Database


class Clock:
    def __init__(self) -> None:
        self.now = 100.0

    def monotonic(self) -> float:
        return self.now


class Ticks:
    def __init__(self, clock: Clock, count: int, before: Any = None) -> None:
        self.clock = clock
        self.remaining = count
        self.before = before

    def wait(self, seconds: float) -> bool:
        if not self.remaining:
            return True
        self.remaining -= 1
        self.clock.now = round(self.clock.now + seconds, 3)
        if self.before is not None:
            self.before(self.clock.now)
        return False

    def is_set(self) -> bool:
        return False


def run_ticks(
    monkeypatch: pytest.MonkeyPatch, *, ticks: int = 60, before: Any = None
) -> tuple[RepositoryWatcher, list[float], list[float]]:
    clock = Clock()
    watcher = RepositoryWatcher(Mock(), Mock(), debounce=0.1, poll_interval=5)
    calls: list[float] = []
    controls: list[float] = []
    monkeypatch.setattr("memglide.core.watcher.time.monotonic", clock.monotonic)

    def state() -> tuple[bool, dict[str, dict[str, str]]]:
        controls.append(clock.now)
        return True, {"p": {"id": "p", "path": "/repo"}}

    def tick(now: float) -> None:
        if before is not None:
            before(watcher, now)

    watcher._stop = Ticks(clock, ticks, tick)  # type: ignore[assignment]
    monkeypatch.setattr(watcher, "_watch_state", state)
    watcher.indexer.reindex.side_effect = lambda _: calls.append(clock.now)
    watcher._run()
    return watcher, calls, controls


def test_idle_control_reads_are_bounded_and_full_audits_continue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, calls, controls = run_ticks(monkeypatch)
    assert calls == pytest.approx([100.2, 105.2, 110.2])
    assert len(controls) == 12  # one small state read per second, not 60 full reports


def test_event_scan_satisfies_periodic_audit_without_duplicate_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def event(watcher: RepositoryWatcher, now: float) -> None:
        if now == 104.6:
            watcher._pending["p"] = now

    _, calls, _ = run_ticks(monkeypatch, before=event)
    assert calls == pytest.approx([100.2, 104.8, 109.8])


def test_failed_scan_is_retried_at_poll_interval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = Clock()
    watcher = RepositoryWatcher(Mock(), Mock(), poll_interval=5)
    monkeypatch.setattr("memglide.core.watcher.time.monotonic", clock.monotonic)
    monkeypatch.setattr(watcher, "_watch_state", lambda: (True, {"p": {"path": "/repo"}}))
    watcher._stop = Ticks(clock, 30)  # type: ignore[assignment]
    watcher.indexer.reindex.side_effect = OSError("fixture unavailable")
    watcher._run()
    assert watcher.indexer.reindex.call_count == 2


def test_watch_state_omits_large_reports_and_uses_one_connection(tmp_path: Path) -> None:
    db = Database(tmp_path / "state.db")
    db.execute(
        "INSERT INTO projects(id,path,name,created_at,index_stats) VALUES(?,?,?,?,?)",
        ("p", str(tmp_path), "fixture", 0, "not parsed as a report"),
    )
    watcher = RepositoryWatcher(db, Mock())
    enabled, projects = watcher._watch_state()
    assert enabled
    assert projects == {"p": {"id": "p", "path": str(tmp_path)}}
    db.execute("UPDATE settings SET value='false' WHERE key='watch_enabled'")
    assert watcher._watch_state()[0] is False


def test_slow_scan_does_not_turn_periodic_audits_into_a_busy_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = Clock()
    watcher = RepositoryWatcher(Mock(), Mock(), poll_interval=5)
    monkeypatch.setattr("memglide.core.watcher.time.monotonic", clock.monotonic)
    monkeypatch.setattr(watcher, "_watch_state", lambda: (True, {"p": {"path": "/repo"}}))
    watcher._stop = Ticks(clock, 10)  # type: ignore[assignment]

    def slow_scan(_: str) -> None:
        clock.now += 6

    watcher.indexer.reindex.side_effect = slow_scan
    watcher._run()
    assert watcher.indexer.reindex.call_count == 1


@pytest.mark.parametrize(
    ("source", "destination", "queued"),
    [
        ("node_modules/a.py", "src/a.py", True),
        ("src/a.py", "node_modules/a.py", True),
        ("node_modules/a.py", "node_modules/b.py", False),
        ("/outside/a.py", "src/a.py", True),
    ],
)
def test_moves_check_both_endpoints(source: str, destination: str, queued: bool) -> None:
    root = Path("/repo")
    watcher = RepositoryWatcher(Mock(), Mock())
    watcher._handler("p", root).on_any_event(
        FileMovedEvent(str(root / source), str(root / destination))
    )
    assert bool(watcher._pending) is queued


def test_ignored_and_read_notifications_do_not_queue() -> None:
    watcher = RepositoryWatcher(Mock(), Mock())
    handler = watcher._handler("p", Path("/repo"))
    handler.on_any_event(FileModifiedEvent("/repo/.env"))
    handler.on_any_event(FileModifiedEvent("/repo/node_modules/a.py"))
    handler.on_any_event(FileModifiedEvent("/repo/.git/objects/file"))
    assert not watcher._pending
    handler.on_any_event(FileModifiedEvent("/repo/.git/HEAD"))
    assert "p" in watcher._pending


def test_timed_out_stop_does_not_allow_a_duplicate_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    watcher = RepositoryWatcher(Mock(), Mock())
    thread = Mock()
    thread.is_alive.return_value = True
    watcher._thread = thread
    watcher._scheduled = {"p": object()}
    observer = Mock()
    watcher._observer = observer
    factory = Mock()
    monkeypatch.setattr("memglide.core.watcher.Observer", factory)
    watcher.stop()
    assert watcher._thread is thread
    assert watcher._stop.is_set()
    watcher.start()
    factory.assert_not_called()
    assert watcher._stop.is_set()
    # Once the old worker actually exits, a later start uses fresh schedules.
    thread.is_alive.return_value = False
    replacement = Mock()
    monkeypatch.setattr("memglide.core.watcher.threading.Thread", lambda **_: replacement)
    watcher.start()
    assert not watcher._stop.is_set()
    assert watcher._scheduled == {}
    replacement.start.assert_called_once()
