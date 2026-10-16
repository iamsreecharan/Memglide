"""A real, source-only fixture workflow through the shared application services."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

from memglide.service import Service
from memglide.storage.database import DomainError


@pytest.fixture
def authentication_repository(tmp_path: Path) -> Path:
    source = Path(__file__).resolve().parents[1] / "examples" / "auth_repository"
    target = tmp_path / "authentication"
    shutil.copytree(source, target)
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    # These files exercise exclusion without requiring any real credentials.
    (target / ".env").write_text("EXAMPLE_ONLY=not-a-credential\n")
    (target / "scratch").mkdir()
    (target / "scratch" / "ignored.py").write_text("def ignored_function(): pass\n")
    return target


def test_authentication_workflow_current_stale_updated_and_expired(
    authentication_repository: Path,
    tmp_path: Path,
) -> None:
    repository = authentication_repository
    service = Service(tmp_path / "state" / "memglide.db")
    try:
        project = service.indexer.add_project(str(repository))
        project_id = project["id"]
        indexed = service.db.rows("SELECT path FROM files WHERE project_id=?", (project_id,))
        paths = {row["path"] for row in indexed}
        assert {"api/auth.py", "api/main.py", "web/src/AuthPanel.tsx"} <= paths
        assert ".env" not in paths
        assert "scratch/ignored.py" not in paths

        symbols = service.db.rows("SELECT name FROM symbols WHERE project_id=?", (project_id,))
        assert {"authenticate_user", "verify_token", "AuthPanel"} <= {s["name"] for s in symbols}
        session = service.memory.start_session(project_id, "Investigate authenticate_user")
        session_id = session["id"]
        status = service.memory.status(session_id)
        assert status["expires_at"] == session["expires_at"]

        hits = service.indexer.search(project_id, "authenticate_user")
        assert any(hit["path"] == "api/auth.py" for hit in hits)
        discovery = service.context.get_context(
            session_id, "authenticate_user", level=1, budget=12000
        )
        assert discovery["items"]
        assert all(not item["snippet"] for item in discovery["items"])
        assert discovery["passport"]["recommended_next_retrievals"]

        focused = service.context.expand_context(
            session_id, discovery["retrieval_id"], level=2, budget=12000
        )
        assert focused["estimated_tokens"] <= focused["budget"]
        auth_items = [item for item in focused["items"] if item["path"] == "api/auth.py"]
        assert auth_items and any("def authenticate_user" in item["snippet"] for item in auth_items)
        old_hash = hashlib.sha256((repository / "api/auth.py").read_bytes()).hexdigest()
        assert all(item["hash"] == old_hash for item in auth_items)
        assert focused["passport"]["related_tests"]
        assert focused["passport"]["unresolved_dependencies"]

        memory = service.memory.save_memory(
            session_id,
            "observation",
            "authenticate_user delegates signature verification to verify_token.",
            "workflow test: inspected api/auth.py",
            [{"path": "api/auth.py", "hash": old_hash}],
        )
        assert memory["freshness"] == "Current"
        assert memory["provenance"].startswith("workflow test:")
        assert memory["sources"][0]["hash"] == old_hash

        # Edit only the copied source. No fixture module is imported or executed.
        auth_path = repository / "api/auth.py"
        auth_path.write_text(
            auth_path.read_text().replace(
                'scheme.lower() != "bearer"', 'scheme.lower() != "bearer-v2"'
            )
        )
        stale = service.context.get_passport(session_id, focused["retrieval_id"])
        assert stale["source_freshness"] == "Stale"
        assert "api/auth.py" in stale["stale_files"]
        recalled = service.memory.recall_memory(session_id, "authenticate_user")
        assert recalled[0]["stale"] is True

        service.indexer.reindex(project_id)
        updated = service.context.get_context(
            session_id, "authenticate_user", level=2, budget=12000
        )
        updated_auth = [item for item in updated["items"] if item["path"] == "api/auth.py"]
        assert updated_auth and all(item["hash"] != old_hash for item in updated_auth)
        assert any('"bearer-v2"' in item["snippet"] for item in updated_auth)
        assert not any(item["id"] == memory["id"] for item in updated["memories"])

        # Simulate the inactivity deadline elapsing, then exercise production cleanup.
        service.db.execute("UPDATE sessions SET expires_at=0 WHERE id=?", (session_id,))
        assert service.cleanup()["deleted_sessions"] == 1
        for table in ("sessions", "memories", "memory_sources", "retrievals", "passports"):
            assert service.db.one(f"SELECT count(*) AS total FROM {table}")["total"] == 0
        with pytest.raises(DomainError, match="Unknown session"):
            service.memory.status(session_id)
        assert service.indexer.list_projects()[0]["id"] == project_id
        assert auth_path.is_file()
        assert service.db.one("SELECT count(*) AS total FROM files")["total"] > 0
    finally:
        service.close()
