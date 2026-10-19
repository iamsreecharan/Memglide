"""Record an explicitly unrun snapshot of a real native plan. Never dispatch.

The original pending plan stays untouched and reusable in a fresh ready runtime.
This helper contains no native execution or source preparation call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from benchmarks import run_router_coding as runner  # noqa: E402


def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Input must be a regular retained file")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    digest(path)
    return json.loads(path.read_text(), object_pairs_hook=runner.offline.unique_object)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--preflight", required=True, type=Path)
    parser.add_argument("--policy-freeze", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    plan_root, output = args.plan.resolve(), args.output.resolve()
    if output == plan_root or output.is_relative_to(plan_root):
        raise ValueError("Blocked snapshot needs a separate fresh output directory")
    runner.verify_policy_freeze(args.policy_freeze.resolve())
    source_paths = [plan_root / name for name in ("plan.json", "state.json", "metadata.json")]
    source_hashes = {str(path): digest(path) for path in source_paths}
    plan, state, metadata = [load(path) for path in source_paths]
    preflight = load(args.preflight.resolve())
    if preflight.get("ready") is not False or preflight.get("native_preflight_attempts") != 2:
        raise ValueError("Requires the retained failed two-invocation access receipt")
    if preflight.get("preflight_price_equivalent_upper_usd") is not None:
        raise ValueError("Unknown failed-preflight cost must stay null")
    if len(plan["runs"]) != 72 or len(plan["tasks"]) != 12 or metadata.get("pilot") is not False:
        raise ValueError("Requires the actual formal twelve-task, seventy-two-slot plan")
    if metadata.get("finished_at") or state.get("supplemental") or any(row.get("attempted") for row in state["originals"].values()):
        raise ValueError("Only a wholly unattempted pending original plan may be projected")
    if list((plan_root / "runs").glob("*/attempt-start.json")) or list((plan_root / "runs").glob("*/events.jsonl")):
        raise ValueError("Native attempt artifacts exist; cannot call the plan wholly unrun")
    runner.common.validate_saved_state(plan_root, plan["tasks"], plan["runs"], state)
    blocker = preflight.get("blocker")
    if not isinstance(blocker, str) or not blocker.strip():
        raise ValueError("Blocked access receipt needs an explicit reason")
    rows = [runner.legacy.not_run(row, blocker) for row in plan["runs"]]
    snapshot = {**metadata, "finished_at": runner.legacy.utc_now(), "stop_reason": blocker,
                "preflight_receipt": preflight, "report_only_projection": True,
                "original_pending_plan_directory": str(plan_root),
                "native_assignment_launches": 0,
                "projection_scope": "Actual frozen assignment plan; every slot unrun. No dispatcher, source preparation or grader was called. Original pending state is unchanged."}
    report = runner.build_report(rows, plan["tasks"], snapshot)
    report["record_kind"] = "blocked_native_plan_snapshot"
    report["artifact_provenance"] = {"original_plan_files_sha256": source_hashes,
                                     "preflight_path": str(args.preflight.resolve()),
                                     "preflight_sha256": digest(args.preflight.resolve()),
                                     "report_only_helper_sha256": digest(Path(__file__))}
    output.mkdir(parents=True, exist_ok=False)
    for name in ("plan.json", "final-response-schema.json"):
        shutil.copyfile(plan_root / name, output / name)
    runner.common.atomic_json(output / "state.json", {"originals": {row["run_id"]: row for row in rows}, "supplemental": []}, immutable=True)
    runner.common.atomic_json(output / "metadata.json", snapshot, immutable=True)
    runner.common.atomic_json(output / "execution-preflight.json", preflight, immutable=True)
    runner.common.atomic_json(output / "report.json", report, immutable=True)
    (output / "report.md").write_text("# Native matched coding plan: blocked before dispatch\n\nThe actual twelve-task plan contains 72 original assignments. All 72 are UNRUN; no coding-agent assignment or grader ran. Two separately retained access preflight invocations failed; their model-call counts, complete usage and charges remain unknown.\n\n" + blocker + "\n\nThis is an explicitly labelled report-only snapshot. The original pending plan remains unchanged. No token, cost, speed or coding-quality benefit is measured.\n")
    if source_hashes != {str(path): digest(path) for path in source_paths}:
        raise ValueError("Original plan changed while taking the blocked snapshot")
    print(json.dumps({"report": str(output / "report.json"), "planned": 72, "attempted": 0,
                      "unrun": 72, "preflight_invocations": 2,
                      "actual_billing_usd": None, "original_plan_unchanged": True}))


if __name__ == "__main__":
    main()
