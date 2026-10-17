"""Internal index metadata avoids excerpts; source evidence is verified by packing."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

import memglide.core.indexer as indexer_module
from memglide.core.context import ContextEngine, estimate_tokens
from memglide.core.indexer import Indexer
from memglide.memory.engine import MemoryEngine
from memglide.storage.database import Database, DomainError


@pytest.fixture
def repository(tmp_path: Path) -> tuple[Path, Indexer, ContextEngine, str, str]:
    root = tmp_path / "repository"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "auth.py").write_text(
        "from helpers import allowed\n\ndef authenticate(value):\n    return allowed(value)\n"
    )
    (root / "helpers.py").write_text("def allowed(value):\n    return value == 'accepted'\n")
    db = Database(tmp_path / "state/db.sqlite")
    indexer = Indexer(db)
    project = indexer.add_project(str(root))["id"]
    memory = MemoryEngine(db)
    session = memory.start_session(project, "Repair authenticate correctness")["id"]
    return root, indexer, ContextEngine(db, indexer, memory), project, session


def test_internal_candidates_have_no_excerpt_or_current_assertion_and_do_not_read_source(
    repository: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, indexer, _, project, _ = repository
    # Index refresh is still mandatory in normal context search. Isolate the
    # candidate-construction stage after a completed refresh for this assertion.
    refreshes = []
    monkeypatch.setattr(indexer, "reindex", lambda pid: refreshes.append(pid))

    def unexpected_read(*_: Any, **__: Any) -> Any:
        raise AssertionError("Metadata resolution should not create source excerpts")

    monkeypatch.setattr(indexer_module, "read_source", unexpected_read)
    candidates = indexer._search_context_candidates(project, "authenticate", limit=40)
    assert refreshes == [project]
    assert candidates
    for candidate in candidates:
        assert "snippet" not in candidate
        assert "freshness" not in candidate
        assert "current" not in candidate
        assert len(candidate["hash"]) == 64
    selected = next(candidate for candidate in candidates if candidate["kind"] == "function")
    assert indexer._get_context_candidate(project, selected["id"])["path"] == "auth.py"
    edges = indexer._context_dependencies(project, selected["id"])
    assert any(edge["reference"] == "allowed" and edge["resolved"] for edge in edges)


def test_default_public_search_and_symbol_still_securely_read_complete_current_source(
    repository: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, indexer, _, project, _ = repository
    original = indexer_module.read_source
    reads = []

    def read(project_root: str, path: str, max_size: int) -> tuple[str, str]:
        reads.append(path)
        return original(project_root, path, max_size)

    monkeypatch.setattr(indexer_module, "read_source", read)
    found = indexer.search(project, "authenticate", refresh=False)
    assert reads
    selected = next(candidate for candidate in found if candidate["kind"] == "function")
    assert selected["current"] is True and selected["freshness"] == "Current"
    assert "return allowed(value)" in selected["snippet"]
    complete = indexer.get_symbol(project, selected["id"], refresh=False)
    assert complete["snippet"] == "def authenticate(value):\n    return allowed(value)"
    (root / "auth.py").write_text("def authenticate(value):\n    return False\n")
    assert not indexer.search(project, "authenticate", refresh=False)
    with pytest.raises(DomainError, match="Source changed"):
        indexer.get_symbol(project, selected["id"], refresh=False)


@pytest.mark.parametrize("change", ["edit", "delete", "symlink"])
def test_unverified_metadata_never_bypasses_source_policy_when_context_is_packed(
    repository: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, change: str
) -> None:
    root, indexer, context, _, session = repository
    # Retain intentionally obsolete index rows to exercise the validation
    # boundary, rather than letting the normal refresh remove them first.
    monkeypatch.setattr(indexer, "reindex", lambda _: None)
    source = root / "auth.py"
    if change == "edit":
        source.write_text("def authenticate(value):\n    return 'changed'\n")
    else:
        source.unlink()
        if change == "symlink":
            outside = tmp_path / "outside.py"
            outside.write_text("OUTSIDE MUST NEVER BE READ\n")
            source.symlink_to(outside)
    result = context.get_context(session, "authenticate", level=2, budget=4000)
    assert "auth.py" not in {item["path"] for item in result["items"]}
    assert "auth.py" not in result["passport"]["verified_source_hashes"]
    assert result["passport"]["status"] == "Partial"
    assert any(
        "Source changed or is unavailable: auth.py" in warning for warning in result["warnings"]
    )
    assert all("OUTSIDE" not in item["snippet"] for item in result["items"])
    assert estimate_tokens(result) == result["estimated_tokens"] <= 4000


def test_metadata_selection_still_returns_complete_direct_helper_bodies(repository: Any) -> None:
    _, _, context, _, session = repository
    result = context.get_context(session, "authenticate", level=2, budget=4000)
    snippets = {item["path"]: item["snippet"] for item in result["items"]}
    assert "def authenticate(value):\n    return allowed(value)\n" in snippets["auth.py"]
    assert "def allowed(value):\n    return value == 'accepted'\n" in snippets["helpers.py"]
    assert set(result["passport"]["verified_source_hashes"]) == {"auth.py", "helpers.py"}
    assert result["passport"]["source_freshness"] == "Current"
