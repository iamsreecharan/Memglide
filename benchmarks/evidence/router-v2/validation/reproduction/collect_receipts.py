"""Collect explicit engineering receipts only; never execute tests or a model.

Run only after all required final receipts exist. Source/application/benchmark
Python is not changed. Existing published artifacts are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local"
DESTINATION = ROOT / "benchmarks/evidence/router-v2/validation"
PRIMARY_DEFAULTS = {
    "full_python": LOCAL / "router-v2-validation/full-python.xml",
    "runner_python": LOCAL / "router-v2-validation/runner-final.xml",
    "frontend_unit": LOCAL / "router-v2-validation/frontend-unit.json",
    "frontend_browser": LOCAL / "router-v2-validation/frontend-browser.json",
    "installed_smoke": LOCAL / "router-v2-validation/installed-smoke-final.json",
}
# Exact paths only. Never recurse into .local, runtime state or indexed trees.
OPTIONAL_RECEIPTS = (
    ("initial", ".local/router-v2-validation/full-python-initial.xml"),
    ("initial", ".local/router-v2-validation/runner-initial.xml"),
    ("frontend-attempts", ".local/router-v2-validation/frontend-unit-initial.json"),
    ("frontend-attempts", ".local/router-v2-validation/frontend-memory-focused.json"),
    ("targeted", ".local/auto-router-v2-core.xml"),
    ("targeted", ".local/auto-router-v2-core-final.xml"),
    ("targeted", ".local/auto-router-v2-only-final.xml"),
    ("targeted", ".local/automatic-validation/router-v2-cli-unit.xml"),
    ("targeted", ".local/automatic-validation/router-v2-cli-final.xml"),
    ("targeted", ".local/automatic-validation/router-v2-launcher-compat-initial.xml"),
    ("targeted", ".local/automatic-validation/router-v2-launcher-compat-final.xml"),
    ("targeted", ".local/automatic-validation/router-v2-analysis.xml"),
    ("targeted", ".local/automatic-validation/router-v2-analysis-final.xml"),
    ("targeted", ".local/automatic-validation/router-v2-analysis-final2.xml"),
    ("targeted", ".local/automatic-validation/profile-router-v2-unit.xml"),
    ("targeted", ".local/automatic-validation/profile-router-v2-unit-final.xml"),
    ("targeted", ".local/automatic-validation/profile-router-v2-unit-final-2.xml"),
    ("targeted", ".local/automatic-v2-corpus-tests.xml"),
    ("targeted", ".local/automatic-v2-corpus-tests-final.xml"),
    ("targeted", ".local/router-v2-validation/query-and-v1-compat.xml"),
    ("component-profile", ".local/router-v2-profile/report.json"),
    ("build-static", ".local/router-v2-validation/build-static.json"),
)
REQUIRED_CONTROLS = (
    ("controls", ".local/automatic-v2-corpus-validation-v1/validation.json"),
    ("freeze", ".local/automatic-v2-corpus-author-freeze.json"),
    ("freeze", ".local/router-v2-validation/policy-freeze.json"),
    ("freeze", ".local/router-v2-validation/policy-freeze-final.json"),
)
FORBIDDEN_COMPONENTS = {
    "auth", "auth.json", "credentials", "credentials.json", "codex-state",
    "repositories", "worktrees", ".git", "node_modules", "installed-env",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_bytes(path: Path) -> bytes:
    path = path.absolute()
    if not path.is_relative_to(LOCAL):
        raise ValueError(f"Receipt must be inside the repository .local directory: {path}")
    relative = path.relative_to(LOCAL)
    if any(part.lower() in FORBIDDEN_COMPONENTS for part in relative.parts):
        raise ValueError("Runtime/auth/indexed source paths cannot be copied")
    for candidate in (path, *path.parents):
        if candidate == ROOT:
            break
        if candidate.is_symlink():
            raise ValueError(f"Receipt symlink refused: {path}")
    if not path.is_file() or path.suffix not in {".xml", ".json"}:
        raise ValueError(f"Expected an explicit regular XML/JSON receipt: {path}")
    if path.stat().st_size > 32_000_000:
        raise ValueError(f"Oversized receipt refused: {path}")
    return path.read_bytes()


def xml_cases(content: bytes) -> tuple[dict[str, Any], dict[str, str]]:
    root = ET.fromstring(content)
    cases = {}
    failures = []
    total_seconds = 0.0
    for case in root.iter("testcase"):
        identifier = (case.get("classname") or case.get("file") or "") + "::" + case.get("name", "")
        if identifier in cases:
            raise ValueError(f"Duplicate test identity in receipt: {identifier}")
        if case.find("failure") is not None:
            status = "failed"
        elif case.find("error") is not None:
            status = "error"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        cases[identifier] = status
        if status in {"failed", "error"}:
            failures.append({"case": identifier, "status": status})
        total_seconds += float(case.get("time", "0"))
    counts = Counter(cases.values())
    return {
        "testcases": len(cases),
        "passed": counts["passed"], "failed": counts["failed"],
        "errors": counts["error"], "skipped": counts["skipped"],
        "sum_case_seconds": total_seconds,
        "failures": failures,
        "case_identity_sha256": digest(json.dumps(sorted(cases), separators=(",", ":")).encode()),
    }, cases


def vitest_summary(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "tests": data["numTotalTests"], "passed": data["numPassedTests"],
        "failed": data["numFailedTests"], "pending": data.get("numPendingTests", 0),
        "todo": data.get("numTodoTests", 0), "success": data["success"] is True,
    }


def browser_summary(data: dict[str, Any]) -> dict[str, Any]:
    stats = data["stats"]
    return {
        "expected_passes": stats["expected"], "unexpected": stats["unexpected"],
        "skipped": stats["skipped"], "flaky": stats["flaky"],
        "top_level_errors": len(data.get("errors", [])),
        "duration_milliseconds": stats["duration"],
        "success": stats["unexpected"] == 0 and stats["flaky"] == 0 and not data.get("errors"),
        "scope": "Production browser cases, distinct from frontend unit cases",
    }


def collect(arguments: argparse.Namespace) -> dict[str, Any]:
    paths = {name: getattr(arguments, name) for name in PRIMARY_DEFAULTS}
    for path in paths.values():
        source_bytes(path)  # Verify every required final file before publishing anything.
    for _, name in REQUIRED_CONTROLS:
        source_bytes(ROOT / name)
    output_json = ROOT / "benchmarks/router-v2-validation.json"
    output_markdown = ROOT / "benchmarks/router-v2-validation.md"
    if output_json.exists() or output_markdown.exists() or DESTINATION.exists():
        raise ValueError("Fresh validation output is required; old published evidence will not be overwritten")

    copies = []

    def retain(group: str, label: str, path: Path) -> bytes:
        content = source_bytes(path)
        destination = DESTINATION / group / (label + path.suffix)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(content)
        copies.append({
            "source": path.relative_to(ROOT).as_posix(),
            "artifact": destination.relative_to(ROOT).as_posix(),
            "bytes": len(content), "sha256": digest(content),
        })
        return content

    primary = {name: retain("final", name, path) for name, path in paths.items()}
    full_summary, full_cases = xml_cases(primary["full_python"])
    runner_summary, runner_cases = xml_cases(primary["runner_python"])
    combined = {**full_cases, **runner_cases}
    final_counts = Counter(combined.values())
    added = sorted(set(runner_cases) - set(full_cases))
    overlap = set(full_cases) & set(runner_cases)
    changed_outcomes = [
        {"case": identity, "full_run": full_cases[identity], "later_runner_run": runner_cases[identity]}
        for identity in sorted(overlap) if full_cases[identity] != runner_cases[identity]
    ]
    python_summary = {
        "full_run": full_summary,
        "later_runner_run": runner_summary,
        "overlapping_cases_not_added_twice": len(overlap),
        "additional_runner_cases": len(added),
        "additional_runner_case_ids": added,
        "changed_outcomes_retained": changed_outcomes,
        "distinct_verified_case_ids": len(combined),
        "final_case_status_counts": dict(final_counts),
        "distinct_identity_sha256": digest(json.dumps(sorted(combined), separators=(",", ":")).encode()),
        "interpretation": "Union of the completed full Python run and later runner-only cases. This is not a claim that one enlarged full suite ran once.",
    }

    targeted = []
    initial_failed_xml = []
    outside_union = set()
    components = []
    frontend_attempts = []
    absent_optional = []
    for group, name in OPTIONAL_RECEIPTS:
        path = ROOT / name
        if not path.exists():
            absent_optional.append(name)
            continue
        content = retain(group, path.stem, path)
        if path.suffix == ".xml":
            summary, cases = xml_cases(content)
            observation = {"source": name, **summary, "overlap_with_primary_union": len(set(cases) & set(combined)), "not_added_to_primary_count": True}
            targeted.append(observation)
            outside_union.update(set(cases) - set(combined))
            if summary["failed"] or summary["errors"]:
                initial_failed_xml.append(observation)
        else:
            value = json.loads(content)
            if group == "frontend-attempts":
                failed_assertions = [
                    {"name": item.get("fullName", item.get("title")), "status": item.get("status")}
                    for suite in value.get("testResults", [])
                    for item in suite.get("assertionResults", [])
                    if item.get("status") == "failed"
                ]
                frontend_attempts.append({"source": name, **vitest_summary(value), "failed_assertions": failed_assertions, "not_added_to_final_frontend_count": True})
            else:
                components.append({"source": name, "scope": value.get("scope"), "model_calls": value.get("model_calls"), "not_a_unit_or_native_model_test": True})

    controls = {}
    for group, name in REQUIRED_CONTROLS:
        path = ROOT / name
        content = retain(group, path.parent.name.lstrip(".") + "-" + path.stem, path)
        value = json.loads(content)
        if group == "controls":
            if not str(value.get("corpus_version", "")).startswith("automatic-2"):
                raise ValueError("Only the fresh automatic-v2 corpus control receipt is accepted")
            tasks = value["tasks"]
            controls = {
                "corpus_version": value["corpus_version"], "tasks": len(tasks),
                "baseline_failed": sum(task.get("baseline_failed") is True for task in tasks),
                "reference_passed": sum(task.get("reference_passed") is True for task in tasks),
                "partial_failed": sum(task.get("partial_failed") is True for task in tasks),
                "valid": value.get("valid") is True,
                "model_requests": value.get("model_requests"),
                "scope": "External corpus validity controls, separate from application/unit counts; upstream full suites were not run.",
            }

    frontend = vitest_summary(json.loads(primary["frontend_unit"]))
    browser = browser_summary(json.loads(primary["frontend_browser"]))
    smoke_raw = json.loads(primary["installed_smoke"])
    checks = smoke_raw.get("checks", {})
    if not isinstance(checks, dict) or any(type(value) is not bool for value in checks.values()):
        raise ValueError("Installed smoke receipt needs an explicit Boolean check map")
    smoke = {
        "checks": checks, "check_count": len(checks),
        "expected_check_count": arguments.expected_installed_checks,
        "all_passed": smoke_raw.get("all_passed") is True and all(checks.values()),
        "model_requests": smoke_raw.get("model_requests"),
        "not_added_to_unit_counts": True,
        "scope": "Installed-package CLI/API/MCP/launcher checks; distinct smoke checks, not unit cases",
    }
    final_success = (
        full_summary["failed"] == full_summary["errors"] == 0
        and full_summary["testcases"] > 0 and runner_summary["testcases"] > 0
        and runner_summary["failed"] == runner_summary["errors"] == 0
        and not final_counts["failed"] and not final_counts["error"]
        and frontend["success"] and frontend["tests"] > 0
        and frontend["passed"] == frontend["tests"]
        and browser["success"] and browser["expected_passes"] > 0
        and browser["skipped"] == 0 and smoke["all_passed"]
        and smoke["check_count"] == arguments.expected_installed_checks
        and controls["valid"]
    )
    report = {
        "version": "router-v2-engineering-validation-1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation_passed": final_success,
        "python": python_summary, "frontend_unit": frontend,
        "production_browser": browser, "installed_package_smoke": smoke,
        "targeted_python_runs_not_summed": targeted,
        "retained_initial_xml_failures": initial_failed_xml,
        "retained_frontend_attempts_not_summed": frontend_attempts,
        "targeted_case_ids_outside_primary_union": sorted(outside_union),
        "fresh_corpus_controls": controls,
        "component_profile_receipts": components,
        "optional_receipts_absent": absent_optional,
        "raw_receipts": copies,
        "model_requests_by_this_collector": 0,
        "limits": [
            "This collector only reads explicit engineering receipts and copies an allowlist. It executes no tests, indexed code, login, discovery query or model request.",
            "Overlapping targeted reruns and initial failures are preserved but not added to primary test counts.",
            "The full-run plus later-runner union is distinct from running the enlarged full suite once.",
            "Installed smoke, corpus controls, component measurements and unit/browser cases have separate denominators.",
            "No auth, credential, native-state, indexed repository, worktree, database or dependency directory is copied.",
            "Historical v1 reports and older corpus-v2 experiments are neither modified nor pooled here.",
        ],
    }
    with output_json.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    markdown = [
        "# Router v2 engineering validation", "",
        f"Final validation passed: **{final_success}**. No model request is made by this collector.", "",
        "| Verification | Observed result |", "|---|---|",
        f"| Completed full Python run | {full_summary['passed']} passed; {full_summary['failed']} failed; {full_summary['errors']} errors; {full_summary['skipped']} skipped |",
        f"| Later runner-only run | {runner_summary['passed']} passed; {runner_summary['failed']} failed; {runner_summary['errors']} errors |",
        f"| Distinct full + later-runner identities | {len(combined)}; {len(overlap)} overlapping cases counted once; {len(added)} additional cases |",
        f"| Frontend unit cases | {frontend['passed']}/{frontend['tests']} passed |",
        f"| Production browser cases | {browser['expected_passes']} expected passes; {browser['unexpected']} unexpected; {browser['flaky']} flaky |",
        f"| Installed-package smoke checks, separate | {sum(checks.values())}/{len(checks)} passed |",
        f"| Fresh corpus controls, separate | {controls['baseline_failed']}/{controls['tasks']} baseline failures; {controls['reference_passed']}/{controls['tasks']} reference passes; {controls['partial_failed']}/{controls['tasks']} partial-fix failures |", "",
        "The distinct Python count is a union of completed receipts, not a claim that one enlarged full suite ran once. Targeted reruns, smoke checks and corpus controls are not summed into it.", "",
        "## Retained initial failures", "",
    ]
    markdown.extend(
        f"- `{item['source']}`: {item['failed']} failed, {item['errors']} errors; original XML retained."
        for item in initial_failed_xml
    )
    if not initial_failed_xml:
        markdown.append("No failed XML is present in this explicit receipt allowlist.")
    markdown.extend(["", "## Retained frontend attempts", ""])
    markdown.extend(
        f"- `{item['source']}`: {item['passed']} passed, {item['failed']} failed, {item['pending']} pending/skipped; original JSON retained and not added to final frontend count."
        for item in frontend_attempts
    )
    if not frontend_attempts:
        markdown.append("No separate initial/focused frontend receipt is present.")
    markdown.extend(["", "## Evidence", "", "[Machine-readable validation](router-v2-validation.json) records every copied receipt's source, artifact path, SHA-256 and byte count. Raw receipts live under `evidence/router-v2/validation/`.", ""])
    markdown.extend("- " + value for value in report["limits"])
    with output_markdown.open("x") as stream:
        stream.write("\n".join(markdown) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in PRIMARY_DEFAULTS.items():
        parser.add_argument("--" + name.replace("_", "-"), dest=name, type=Path, default=default)
    parser.add_argument("--expected-installed-checks", type=int, default=14)
    args = parser.parse_args()
    report = collect(args)
    print(json.dumps({"validation_passed": report["validation_passed"], "python_distinct": report["python"]["distinct_verified_case_ids"], "raw_receipts": len(report["raw_receipts"])}))
    return 0 if report["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
