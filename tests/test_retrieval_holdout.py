"""Independent retrieval contracts outside the measured Atlas coding corpus."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

import pytest

from memglide.service import Service


@pytest.fixture
def telemetry_projects(tmp_path: Path) -> Any:
    service = Service(tmp_path / "state/memglide.db")
    canary = tmp_path / "indexed_code_was_executed"
    projects = []
    for name, marker in (("nautilus", "selected_project"), ("other", "foreign_project")):
        root = tmp_path / name
        (root / "telemetry").mkdir(parents=True)
        (root / "telemetry/envelope.py").write_text(
            "from pathlib import Path\n"
            f"Path({str(canary)!r}).write_text('unsafe execution')\n\n"
            "def verify_envelope_digest(envelope):\n"
            '    """Verify the telemetry envelope digest without changing the payload."""\n'
            f"    return {marker!r}, envelope\n"
        )
        (root / "telemetry/schedule.py").write_text(
            "def acknowledgement_deadline(sent_at, timeout):\n    return sent_at + timeout\n"
        )
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        project = service.indexer.add_project(str(root))
        session = service.memory.start_session(project["id"], "Review telemetry correctness.")
        projects.append((project, session, root))
    try:
        yield service, projects, canary
    finally:
        service.close()


def test_exact_qualified_symbol_preserves_project_boundary_and_never_executes_source(
    telemetry_projects: Any,
) -> None:
    service, projects, canary = telemetry_projects
    for position, (_, session, root) in enumerate(projects):
        result = service.context.get_context(
            session["id"], "verify_envelope_digest", level=2, budget=8000
        )
        selected = [item for item in result["items"] if item["path"] == "telemetry/envelope.py"]
        assert selected
        expected = "selected_project" if position == 0 else "foreign_project"
        other = "foreign_project" if position == 0 else "selected_project"
        assert any(expected in item["snippet"] for item in selected)
        assert all(other not in item["snippet"] for item in result["items"])
        assert all(
            item["hash"] == hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
            for item in result["items"]
        )
        assert not canary.exists()


def test_exact_path_retrieval_selects_source_from_its_approved_root(
    telemetry_projects: Any,
) -> None:
    service, projects, _ = telemetry_projects
    _, session, root = projects[0]
    result = service.context.get_context(
        session["id"], "telemetry/schedule.py", level=3, budget=8000
    )
    assert result["items"]
    assert result["items"][0]["path"] == "telemetry/schedule.py"
    assert "return sent_at + timeout" in result["items"][0]["snippet"]
    assert all(root in (root / item["path"]).resolve().parents for item in result["items"])


@pytest.mark.parametrize("query", ["zephyrlattice qxzprism", '") OR secret_id:* --'])
def test_no_match_and_fts_punctuation_return_no_invented_evidence(
    telemetry_projects: Any, query: str
) -> None:
    service, projects, canary = telemetry_projects
    result = service.context.get_context(projects[0][1]["id"], query, level=2, budget=8000)
    assert result["items"] == []
    assert result["passport"]["status"] == "Partial"
    assert result["warnings"]
    assert not canary.exists()
