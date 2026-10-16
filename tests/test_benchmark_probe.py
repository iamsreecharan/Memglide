"""Checks for narrow component metrics, including honest unavailable values."""

import sys
from pathlib import Path

# Benchmark tooling is intentionally not part of the installed application wheel.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmarks.corpus import task_definitions  # noqa: E402
from benchmarks.probe import component_checks, coverage_proxy, verify_hashes  # noqa: E402


def _context(items):
    return {"items": items, "passport": {"status": "Partial"}, "warnings": [], "truncated": False}


def test_exact_symbol_requires_its_declared_file():
    task = task_definitions()[0]
    result = coverage_proxy(
        task,
        _context(
            [
                {"path": "atlas/other.py", "symbol": "TTLCache.get", "snippet": "def get(): pass"},
            ]
        ),
    )
    assert result["target_file_coverage_fraction"] == 0
    assert result["expected_symbol_coverage_fraction"] == 0
    assert result["expected_declaration_visible_fraction"] == 0


def test_whole_file_evidence_is_distinct_from_exact_symbol_identity():
    task = task_definitions()[0]
    result = coverage_proxy(
        task,
        _context(
            [
                {
                    "path": "atlas/cache.py",
                    "symbol": "cache.py",
                    "snippet": "class TTLCache:\n    def get(self, key):\n        return None\n",
                },
            ]
        ),
    )
    assert result["target_file_coverage_fraction"] == 1
    assert result["expected_symbol_coverage_fraction"] == 0
    assert result["expected_declaration_visible_fraction"] == 1


def test_typescript_generic_declaration_is_visible():
    task = next(item for item in task_definitions() if item["id"] == "ts-selective-retry")
    result = coverage_proxy(
        task,
        _context(
            [
                {
                    "path": "src/retry.ts",
                    "symbol": "retry.ts",
                    "snippet": "export function runWithRetry<T>(operation: () => T): T { return operation(); }",
                },
            ]
        ),
    )
    assert result["expected_declaration_visible_fraction"] == 1


def test_hash_check_uses_actual_disk_and_detects_mutation(tmp_path):
    import hashlib

    target = tmp_path / "source.py"
    target.write_text("first\n")
    context = _context(
        [
            {
                "path": "source.py",
                "symbol": "source.py",
                "hash": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        ]
    )
    assert verify_hashes(context, tmp_path)["all_hashes_current"]
    target.write_text("second\n")
    assert not verify_hashes(context, tmp_path)["all_hashes_current"]


def test_empty_or_escaped_evidence_never_establishes_freshness(tmp_path):
    assert not verify_hashes(_context([]), tmp_path)["all_hashes_current"]
    parent = tmp_path.parent / "outside.py"
    parent.write_text("outside\n")
    assert not verify_hashes(_context([{"path": "../outside.py", "hash": "ignored"}]), tmp_path)[
        "all_hashes_current"
    ]


def test_successful_transport_does_not_imply_successful_freshness_checks():
    checks = component_checks({"transport_status": "passed"})
    assert checks
    assert not any(checks.values())
