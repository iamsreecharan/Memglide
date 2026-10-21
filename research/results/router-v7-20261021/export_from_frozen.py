"""Export the publication tables from committed analysis and public task metadata."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ANALYSIS_SHA256 = "fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26"
HERE = Path(__file__).parent
METRICS = (
    "uniform_long_usd",
    "workflow_wall_seconds",
    "native_wall_seconds",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "index_wall_seconds",
    "verification_wall_seconds",
    "installed_launcher_preparation_wall_seconds",
    "cleanup_wall_seconds",
)
FIRST_FIELDS = (
    "run_id",
    "task_id",
    "configuration",
    "repeat",
    "strict_success",
    "public_success",
    "private_success",
    "grade_valid",
    "usage_complete",
    *METRICS,
)


def load(path):
    return json.loads(path.read_text())


def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Only regular public source files may be exported")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def write_csv(name, rows):
    with (HERE / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def portable(value, executor_root):
    """Replace execution-root selectors, preserving declared argv/env structure."""
    if isinstance(value, list):
        return [portable(item, executor_root) for item in value]
    if isinstance(value, dict):
        return {key: portable(item, executor_root) for key, item in value.items()}
    if not isinstance(value, str):
        return value
    if value.startswith("/opt/") and value.endswith("/node/bin/node"):
        return "{node}"
    replacements = [(executor_root + "/.venv/bin/python", "{python}")]
    replacements += [
        (
            executor_root + f"/.local/router-v7-development/authoring/cohort-{c}/",
            "{runtime_cohort_" + c + "}/",
        )
        for c in "abc"
    ]
    replacements += [
        (executor_root + "/.local/router-v5-search/tooling/", "{runtime_v5}/"),
        (executor_root + "/.local/router-v6-paper/", "{runtime_v6}/"),
        (executor_root + "/", "{repository_root}/"),
    ]
    for source, target in replacements:
        value = value.replace(source, target)
    if any(marker in value for marker in ("/workspace/", "/opt/codex/", "/tmp/", "/home/")):
        raise ValueError("Unmapped absolute executor path in public catalog")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--public-tasks", type=Path, required=True)
    parser.add_argument("--author-tasks", type=Path, action="append", required=True)
    parser.add_argument("--results-summary", type=Path, required=True)
    parser.add_argument(
        "--executor-root",
        help="Original repository prefix in command templates, if inputs were relocated",
    )
    args = parser.parse_args()
    if sha(args.analysis) != ANALYSIS_SHA256:
        raise ValueError("Source analysis does not match the committed result")
    source, protocol, tasks = load(args.analysis), load(args.protocol), load(args.public_tasks)
    reference = load(args.results_summary)
    primary = source["all_scheduled_rows"]
    primary_ids = {row["run_id"] for row in primary}
    rows = source["all_original144_scheduled_rows"][16:]
    if (
        len(rows) != 128
        or len(primary) != 112
        or [row["order"] for row in rows] != list(range(17, 145))
        or len(primary_ids) != 112
    ):
        raise ValueError("Frozen primary/master row cardinality or order changed")
    indexed = {row["run_id"]: row for row in rows}
    for row in primary:
        other = indexed[row["run_id"]]
        if row["metrics"] != other["metrics"] or row["strict_success"] != other["strict_success"]:
            raise ValueError("Primary and complete-pool records disagree")

    def compact(row):
        metrics = row["metrics"]
        result = {key: row[key] for key in FIRST_FIELDS if key not in METRICS}
        result.update({key: metrics[key] for key in METRICS})
        result.update(
            order=row["order"],
            repository=row["repository"],
            language=row["language"],
            primary=row["run_id"] in primary_ids,
            measurement_epoch=row["measurement_epoch"],
            native_valid=row["native_valid"],
            native_identity_valid=row["native_identity_valid"],
            evidence_preservation_valid=row["evidence_preservation_valid"],
            source_policy_valid=row["source_policy_adjudication_valid"],
            native_transport_valid=row["native_transport_adjudication_valid"],
            source_unchanged=row["source_unchanged"],
            source_protection_valid=not row["grading_protected_file_violations"],
            grade_infrastructure_valid=row["grade_infrastructure_valid"],
            grading_source_reconstructed=row["grading_source_reconstructed"],
            reconstructed_source_unchanged=row["reconstructed_source_unchanged"],
            reconstructed_source_matches_native=row["reconstructed_source_matches_native"],
            model_generated_caches_reused=row["model_generated_caches_reused"],
            cache_write_input_tokens=metrics["cache_write_input_tokens"],
            reasoning_output_tokens=metrics["reasoning_output_tokens"],
            reported_public_behavioral_tests=row["reported_public_behavioral_tests"],
            reported_private_contract_checks=row["reported_private_contract_checks"],
            original_native_valid=row["original_native_execution_validity"]["valid"],
            original_uniform_long_usd=row["original_uniform_long_usd"],
            recovered_transport_warning_count=len(
                row["native_transport_adjudication"]["recoverable_transport_events"]
            ),
            original_protection_violation_count=len(row["original_protected_file_violations"]),
            authorized_production_correction_count=len(row["authorized_production_corrections"]),
            coding_policy_violation_count=len(row["coding_policy_violations"]),
            raw_result_sha256=row["native_transport_adjudication"]["raw_result_sha256"],
            native_adjudication_sha256=row["native_adjudication_sha256"],
            source_policy_adjudication_sha256=row["source_policy_adjudication_sha256"],
            source_policy_manifest_sha256=row["source_policy_manifest_sha256"],
            grading_manifest_sha256=row["grading_manifest_sha256"],
        )
        if type(result["strict_success"]) is not bool or not all(
            result[key] is True
            for key in (
                "native_valid",
                "native_identity_valid",
                "usage_complete",
                "grade_valid",
                "source_policy_valid",
                "native_transport_valid",
                "evidence_preservation_valid",
                "source_protection_valid",
            )
        ):
            raise ValueError("Cannot export an unattested row as a complete measurement")
        return result

    exported = [compact(row) for row in rows]
    write_csv("all-128-runs.csv", exported)
    write_csv("primary-112-runs.csv", [row for row in exported if row["primary"]])
    paired = []
    time_map = {
        row["task_id"]: row
        for row in source["primary"]["workflow_wall_seconds"]["paired_task_values"]
    }
    quality = {row["task_id"]: row for row in source["quality"]["task_matrix"]}
    for row in source["primary"]["uniform_long_usd"]["paired_task_values"]:
        time, outcome = time_map[row["task_id"]], quality[row["task_id"]]
        paired.append(
            {
                "task_id": row["task_id"],
                "cost_A": row["A"],
                "cost_M": row["M"],
                "cost_delta": row["delta"],
                "workflow_A": time["A"],
                "workflow_M": time["M"],
                "workflow_delta": time["delta"],
                "A_both_pass": outcome["A_both_pass"],
                "M_both_pass": outcome["M_both_pass"],
            }
        )
    write_csv("paired-28-tasks.csv", paired)
    summary = {
        key: source[key]
        for key in (
            "primary",
            "arms",
            "quality",
            "joint_decision",
            "analysis_design_status",
            "cohort_selection",
            "grading_version_scope",
            "scope",
            "analysis_environment",
            "attempt_accounting",
            "pooled_all128_descriptive",
            "transport_warning_summary",
        )
    }
    summary.update(
        version="portable-v7-publication-summary-1",
        source_analysis_sha256=ANALYSIS_SHA256,
        original_analysis_sha256_is_not_this_export_sha256=True,
        product_commit=reference["product_commit"],
        arm_labels=reference["arm_labels"],
        primary_design=reference["primary_design"],
        cost_definition=reference["cost_definition"],
        failure_review=reference["failure_review"],
        primary_task_ids=source["epochs"]["primary_task_ids"],
        exposed_task_ids=source["epochs"]["exposed_task_ids"],
    )
    write_json("analysis-summary.json", summary)
    write_json("summary.json", summary)
    protocol_keys = (
        "version",
        "model",
        "effort",
        "tier",
        "arms",
        "task_clusters",
        "primary_task_clusters",
        "repeats_per_arm",
        "assignment_seed",
        "primary_estimands",
        "primary_analysis",
        "uniform_tariff",
        "quality_guard",
        "failures",
        "secondary_diagnostics",
        "missingness",
        "grading",
    )
    excerpt = {key: protocol[key] for key in protocol_keys if key in protocol}
    write_json(
        "protocol-excerpt.json",
        {
            "version": "portable-protocol-excerpt-1",
            "original_protocol_sha256": sha(args.protocol),
            "source_fields": excerpt,
        },
    )
    authored = {}
    for path in args.author_tasks:
        for row in load(path):
            authored[row["id"]] = row
    catalog = []
    for task in tasks:
        author = authored[task["id"]]
        if (
            author["repository"].rstrip("/") != task["repository"].rstrip("/")
            or author["prompt"] != task["prompt"]
        ):
            raise ValueError("Authored public task provenance disagrees with the frozen task")
        catalog.append(
            {
                "task_id": task["id"],
                "repository": task["repository"],
                "commit": author.get("commit"),
                "language": task["language"],
                "primary": task["id"] in summary["primary_task_ids"],
                "previously_exposed_task": task["id"] in summary["exposed_task_ids"],
                "prompt": task["prompt"],
                "commands": portable(
                    task["commands"],
                    args.executor_root or str(args.public_tasks.resolve().parents[2]),
                ),
            }
        )
    write_json(
        "public-task-catalog.json",
        {
            "version": "portable-public-tasks-1",
            "tasks": catalog,
            "command_scope": "Faithful frozen argv/env templates; runtime placeholders require the separately pinned evaluation tooling. This pack reproduces statistics without executing these commands.",
        },
    )
    commitments = {
        "original_analysis_sha256": ANALYSIS_SHA256,
        "original_protocol_sha256": sha(args.protocol),
        "original_public_tasks_sha256": sha(args.public_tasks),
        "original_public_author_task_manifests_sha256": {
            f"cohort_{i + 1}": sha(path) for i, path in enumerate(args.author_tasks)
        },
        "original_compact_summary_sha256": sha(args.results_summary),
        "analysis_code_sha256": {
            Path(name).name: digest for name, digest in source["analysis_code_sha256"].items()
        },
        "seal_sha256": source["seal_sha256"],
        "export_rule": "Explicit scalar/table allowlists. No credentials, private graders, full transcripts, native auth selectors or executor-root paths.",
    }
    write_json("source-commitments.json", commitments)
    print(
        json.dumps(
            {
                "primary_rows": 112,
                "complete_pool_rows": 128,
                "paired_tasks": 28,
                "public_tasks": len(catalog),
            }
        )
    )


if __name__ == "__main__":
    main()
