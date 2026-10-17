"""Task-behavior ranking and explicit evidence-role regressions."""

from __future__ import annotations

import subprocess
from pathlib import Path

from memglide.core.indexer import Indexer
from memglide.core.query import preferred_source_role, search_focus
from memglide.storage.database import Database


def test_workflow_prose_does_not_replace_behavior_or_explicit_references() -> None:
    query = (
        "In this Python shipping project, Fix delivery watermarks. "
        "Duplicate submissions must not advance the watermark.\n\n"
        "Implement the change in the production source. "
        "Use existing smoke tests and add regression tests. "
        "Do not change dependency or build configuration. "
        "Finish with a brief description and the tests you ran."
    )
    focus = search_focus(query)
    assert "Duplicate submissions must not advance" in focus
    assert "delivery watermarks" in focus
    assert "shipping project" not in focus and "smoke tests" not in focus
    assert preferred_source_role(query) == "implementation"
    explicit = query + "\nRun tests/test_watermarks.py to verify `advance_watermark`."
    assert "tests/test_watermarks.py" in search_focus(explicit)
    assert "advance_watermark" in search_focus(explicit)


def test_workflow_requests_and_code_blocks_remain_retrievable() -> None:
    query = "Write regression tests for delivery watermarks."
    assert search_focus(query) == query
    assert preferred_source_role(query) == "tests"
    assert preferred_source_role("Update documentation for delivery watermarks") == "documentation"
    query = "Fix this function:\n```python\ndef advance_watermark():\n    pass\n```"
    assert search_focus(query) == query
    assert preferred_source_role("Explain delivery watermarks") is None


def test_acceptance_details_survive_test_instruction_filtering() -> None:
    for clause in (
        "Add tests for jitter floors and cancellation deadlines.",
        "Write tests that cancellation deadlines preserve the jitter floor.",
        "Run tests to verify cancellation deadlines and jitter floors.",
    ):
        focus = search_focus("Fix backoff scheduling. " + clause)
        assert "jitter" in focus and "cancellation deadlines" in focus
    standalone = "Add tests for jitter floors and cancellation deadlines."
    assert search_focus(standalone) == standalone
    assert preferred_source_role(standalone) == "tests"


def test_task_role_ranking_keeps_explicit_docs_and_tests_accessible(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    sources = {
        "delivery.py": (
            "def advance_watermark(sequence):\n"
            "    '''Validate delivery watermarks and duplicate submissions.'''\n"
            "    return sequence\n"
        ),
        "README.md": "Delivery watermarks validate duplicate submissions.\n",
        "tests/test_delivery.py": (
            "# Delivery watermarks validate duplicate submissions.\n"
            "def test_delivery():\n    pass\n"
        ),
    }
    for path, text in sources.items():
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text)
    indexer = Indexer(Database(tmp_path / "state/memglide.db"))
    project = indexer.add_project(str(root))["id"]
    assert (
        indexer.search(project, "Fix delivery watermarks duplicate submissions")[0]["path"]
        == "delivery.py"
    )
    assert (
        indexer.search(project, "Update documentation for delivery watermarks")[0]["path"]
        == "README.md"
    )
    assert (
        indexer.search(project, "Write tests for delivery watermarks")[0]["path"]
        == "tests/test_delivery.py"
    )
    assert indexer.search(project, "Fix README.md delivery watermarks")[0]["path"] == "README.md"
    assert (
        indexer.search(project, "Fix tests/test_delivery.py watermarks")[0]["path"]
        == "tests/test_delivery.py"
    )
