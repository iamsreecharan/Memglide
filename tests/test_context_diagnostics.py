"""Index failures must stay visible when a text match can still be retrieved."""

import subprocess

from memglide.service import Service


def test_parse_failures_are_evidence_warnings(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    (repo / "auth.py").write_text("def verify_auth(token):\n    return bool(token)\n")
    (repo / "broken.py").write_text("def broken_auth(:\n")
    service = Service(tmp_path / "state" / "memglide.db")
    project = service.indexer.add_project(str(repo))
    session = service.memory.start_session(project["id"], "inspect auth")
    context = service.context.get_context(session["id"], "auth", level=2, budget=16000)
    assert context["items"]
    assert context["passport"]["status"] == "Partial"
    assert any("Indexing reported" in warning for warning in context["warnings"])
    assert any(item["path"] == "broken.py" and item["parse_error"] for item in context["items"])
    service.close()


def test_session_change_query_includes_new_files(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    (repo / "original.py").write_text("def original():\n    return 1\n")
    service = Service(tmp_path / "state" / "memglide.db")
    project = service.indexer.add_project(str(repo))
    session = service.memory.start_session(project["id"], "Review new source")
    (repo / "new_feature.py").write_text("def newly_added():\n    return 2\n")
    service.indexer.reindex(project["id"])
    result = service.context.get_context(
        session["id"], "What changed in this session?", level=2, budget=12000
    )
    assert any(event["path"] == "new_feature.py" for event in result["session_events"])
    assert any(
        item["path"] == "new_feature.py" and "newly_added" in item["snippet"]
        for item in result["items"]
    )
    assert "do not identify the actor" in result["session_event_scope"]
    service.close()
