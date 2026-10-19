"""Cheap profile-harness checks; no live index/profile/model process is launched."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from memglide.integrations.preload import TASK_SEPARATOR

_SPEC = importlib.util.spec_from_file_location(
    "profile_router_v2", Path(__file__).resolve().parents[1] / "benchmarks/profile_router_v2.py"
)
assert _SPEC is not None and _SPEC.loader is not None
probe = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(probe)


def test_balanced_order_each_size_and_repeat_unique() -> None:
    rows = probe.plan(3, [8, 100])
    assert len(rows) == 18
    assert len({(row["repeat"], row["files"], row["arm"]) for row in rows}) == 18
    for size in (8, 100):
        subset = [row for row in rows if row["files"] == size]
        assert Counter(row["arm"] for row in subset) == {"B": 3, "V1": 3, "C": 3}
        assert all(Counter(row["arm"] for row in subset[position::3]) == {"B": 1, "V1": 1, "C": 1} for position in range(3))


@pytest.mark.parametrize("repeats,sizes", [(0, [8]), (7, [8]), (True, [8]), (3, []), (3, [8, 8]), (3, [1]), (3, [101]), (3, [8, 9, 10])])
def test_assignment_caps(repeats: int, sizes: list[int]) -> None:
    with pytest.raises(ValueError):
        probe.plan(repeats, sizes)


def test_canonical_new_directory_never_overwrites_or_follows_symlink(tmp_path: Path) -> None:
    output = probe._new_directory(tmp_path / "new")
    (output / "keep").write_text("original")
    with pytest.raises(FileExistsError):
        probe._new_directory(output)
    link = tmp_path / "link"
    link.symlink_to(output, target_is_directory=True)
    with pytest.raises(ValueError):
        probe._new_directory(link / "nested")
    assert (output / "keep").read_text() == "original"
    assert not (output / "nested").exists()


def test_development_fixture_is_bounded_deterministic_path_free_task(tmp_path: Path) -> None:
    sources = probe.fixture(tmp_path, 8, 128)
    assert len(sources) == 8 and all(len(source.encode()) == 128 for source in sources.values())
    assert all((tmp_path / path).read_text() == source for path, source in sources.items())
    assert probe.TARGET in sources and ".py" not in probe.TASK
    assert not any("invoice" in source or "shipping" in source for source in sources.values())
    with pytest.raises(ValueError):
        probe.fixture(tmp_path, 101, 128)
    with pytest.raises(ValueError):
        probe.fixture(tmp_path, 8, 17_000)


def response(source: str) -> dict[str, Any]:
    return {
        "mode": "preloaded",
        "files": [{"path": probe.TARGET, "sha256": hashlib.sha256(source.encode()).hexdigest()}],
        "prompt": json.dumps({"memglide_sources": [{"path": probe.TARGET, "content": source}]}) + TASK_SEPARATOR + probe.TASK,
    }


def test_independent_full_content_and_hash_validation() -> None:
    source = "def orbital_phase(period, elapsed):\n    return elapsed % period\n"
    valid = response(source)
    assert probe.fidelity(valid, {probe.TARGET: source}) == {"exact_treatment_fidelity": True, "expected_target_delivered": True}
    valid["files"][0]["sha256"] = "0" * 64
    assert not probe.fidelity(valid, {probe.TARGET: source})["exact_treatment_fidelity"]
    assert not probe.fidelity(response(source), {probe.TARGET: source + "# changed\n"})["exact_treatment_fidelity"]


def test_fallback_is_faithful_but_does_not_silently_count_as_selection() -> None:
    fallback = {"mode": "passthrough", "files": [], "prompt": probe.TASK}
    assert probe.fidelity(fallback, {}) == {"exact_treatment_fidelity": True, "expected_target_delivered": False}
    fallback["prompt"] = "different task"
    assert not probe.fidelity(fallback, {})["exact_treatment_fidelity"]


def test_non_linux_rss_is_unavailable_not_guess_scaled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(probe.sys, "platform", "darwin")
    assert probe.peak_rss()["bytes"] is None
    assert probe.child_usage() == {"cpu_seconds": None, "peak_rss_bytes": None}
    assert probe._cpu_difference({"cpu_seconds": None}, {"cpu_seconds": None}) is None


def test_worker_failure_remains_in_summary_denominator() -> None:
    rows = [{"files": 8, "arm": "B", "observation": None, "error": "failure"}]
    summaries = probe.summarize(rows)
    bare = next(row for row in summaries if row["arm"] == "B")
    assert bare["attempts"] == 1 and bare["observed"] == 0 and bare["failed_workers"] == 1
    assert bare["peak_python_self_rss_bytes"] is None
    assert "not" in probe.SCOPE.lower()
