"""Independent body judgments must reject declarations and missing source lines."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks.compact_quality_evaluation import (  # noqa: E402
    body_preservation,
    independent_hashes,
    labels_for,
    source_label,
)
from benchmarks.corpus import task_definitions  # noqa: E402
from benchmarks.refinement_eval import body_evidence  # noqa: E402


def test_all_old_task_oracles_include_real_implementations() -> None:
    for task in task_definitions():
        labels = labels_for(task)
        for body in [
            labels["primary"],
            *labels["direct_local_helpers"],
            *labels["integration_callers"],
        ]:
            text = body["text"]
            assert "return" in text
            assert body["end_line"] - body["start_line"] + 1 == len(text.splitlines())
            assert body_evidence(body, [{**body, "snippet": text}])["complete"]


def test_complete_body_rejects_declaration_only_and_false_declared_range() -> None:
    label = source_label(
        "source.py", "def example():\n    first = 4\n    return first\n", "example", "python"
    )
    declaration = {**label, "end_line": 1, "snippet": "def example():"}
    assert not body_evidence(label, [declaration])["complete"]
    omitted = {**label, "snippet": "def example():\n    return first"}
    assert not body_evidence(label, [omitted])["complete"]


def test_ts_oracle_keeps_multiline_return_shape_and_one_line_methods() -> None:
    source = "export function page(\n  limit: number,\n): { count: number } {\n  return { count: limit };\n}\nexport function next() { return false; }\n"
    label = source_label("page.ts", source, "page", "typescript")
    assert label["end_line"] == 5
    assert "return { count: limit };" in label["text"]
    assert "next()" not in label["text"]
    method = source_label(
        "service.ts",
        "export class Service {\n  value(): number { return 42; }\n}\n",
        "Service.value",
        "typescript",
    )
    assert method["start_line"] == method["end_line"] == 2


def test_supporting_callers_and_direct_helpers_have_distinct_denominators() -> None:
    labels = [labels_for(task) for task in task_definitions()]
    assert sum(len(label["direct_local_helpers"]) for label in labels) == 2
    assert sum(len(label["integration_callers"]) for label in labels) == 14


def test_absent_source_hashes_are_unavailable_not_verified(tmp_path: Path) -> None:
    assert independent_hashes(tmp_path, {"source_hashes": {}})["all_match"] is None


def test_body_preservation_does_not_hide_swapped_misses_or_failures() -> None:
    def row(task: str, profile: str, complete: bool) -> dict:
        return {
            "task_id": task,
            "repeat": 1,
            "profile": profile,
            "status": "ok",
            "primary_body": {"path": task + ".py", "symbol": "example", "complete": complete},
            "direct_local_helper_bodies": [],
            "integration_caller_bodies": [],
        }

    rows = [
        row("one", "full_4000", True),
        row("two", "full_4000", False),
        row("one", "compact_2000", False),
        row("two", "compact_2000", True),
    ]
    assert not body_preservation(rows, "compact_2000")["all_baseline_complete_bodies_preserved"]
    rows[2] = {"task_id": "one", "repeat": 1, "profile": "compact_2000", "status": "error"}
    assert not body_preservation(rows, "compact_2000")["all_comparable"]
