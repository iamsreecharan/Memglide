"""Fresh offline v4 evaluation. No native/model dispatcher or corpus at import.

The pinned v3 module supplies audited Git, source-fidelity and resource helpers;
its policy runner, corpus, reports and original outcomes are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import time
from itertools import combinations, permutations
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "benchmarks/run_automatic_v3.py"
HELPER_SHA256 = "51a81176cf253c6afe19dbc676a80fac113a3df623e37ae9e8a70550244cb907"
if hashlib.sha256(HELPER_PATH.read_bytes()).hexdigest() != HELPER_SHA256:
    raise ValueError("frozen v3 verification helper changed")
_SPEC = importlib.util.spec_from_file_location("_frozen_v3_offline_helpers", HELPER_PATH)
assert _SPEC is not None and _SPEC.loader is not None
base = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = base
_SPEC.loader.exec_module(base)

sha, dump = base.sha, base.dump
new_directory, tree_hashes, safe_relative = base.new_directory, base.tree_hashes, base.safe_relative
verify_delivery, grade_scope = base.verify_delivery, base.grade_scope
resources, difference, stop_process_group = base.resources, base.difference, base.stop_process_group
PROTOCOL = ROOT / "benchmarks/automatic-v4-protocol.md"
TASKS, CONTROLS = ROOT / "benchmarks/tasks_automatic_v4.json", ROOT / "benchmarks/controls_automatic_v4.json"
GRADING, PROVENANCE = ROOT / "benchmarks/automatic-v4-grading.json", ROOT / "benchmarks/automatic-v4-provenance.json"
FIXTURES = ROOT / "benchmarks/automatic-v4-fixtures"
ARMS, REPEATS, SEED = ("B", "V3", "C"), 2, 20261107
SETTINGS: dict[str, Any] = dict(base.SETTINGS)
MAX_LOG_BYTES, TIMEOUT = base.MAX_LOG_BYTES, 90
BYTE_ATTRIBUTES = "* -text -eol -ident -filter -working-tree-encoding\n"


def git_environment() -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull,
                        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ATTR_NOSYSTEM": "1"})
    return environment


def git_bytes(root: Path, *arguments: str, input_data: bytes | None = None) -> bytes:
    options = ("core.fsmonitor=false", "core.hooksPath=" + os.devnull, "commit.gpgsign=false",
               "core.attributesFile=" + os.devnull, "core.autocrlf=false", "core.safecrlf=false")
    command = ["git", *(item for option in options for item in ("-c", option)), "-C", str(root), *arguments]
    return subprocess.run(command, input=input_data, check=True, capture_output=True,
                          env=git_environment(), timeout=30).stdout


def git(root: Path, *arguments: str) -> str:
    return git_bytes(root, *arguments).decode("utf-8", errors="strict").strip()


def initialize_repository(root: Path) -> None:
    git(root, "init", "--initial-branch=benchmark", "--template=")
    attributes = root / ".git" / "info" / "attributes"
    attributes.parent.mkdir(exist_ok=True)
    attributes.write_text(BYTE_ATTRIBUTES)
    git(root, "config", "user.name", "Memglide Offline Evaluation")
    git(root, "config", "user.email", "benchmark@example.invalid")
    git(root, "add", "--force", ".")
    git(root, "commit", "-m", "Frozen upstream source")


def canonical_hashes(root: Path, commit: str) -> dict[str, str]:
    entries: list[tuple[str, str]] = []
    for entry in git_bytes(root, "ls-tree", "-r", "-z", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8", errors="strict")
        if mode not in {"100644", "100755"} or kind != "blob" or not safe_relative(path):
            raise ValueError("canonical repository contains unsafe/nonregular source")
        entries.append((path, object_id))
    data = git_bytes(root, "cat-file", "--batch", input_data="".join(identifier + "\n" for _, identifier in entries).encode())
    result, cursor = {}, 0
    for path, identifier in entries:
        boundary = data.index(b"\n", cursor)
        object_id, kind, size = data[cursor:boundary].decode("ascii").split()
        end = boundary + 1 + int(size)
        if object_id != identifier or kind != "blob" or data[end:end + 1] != b"\n" or int(size) > 512_000:
            raise ValueError("canonical blob batch has invalid bounds/identity")
        result[path] = sha(data[boundary + 1:end])
        cursor = end + 1
    if cursor != len(data):
        raise ValueError("unexpected canonical blob data")
    return result


def verify_repository(root: Path, commit: str, expected: dict[str, str]) -> None:
    attributes = root / ".git" / "info" / "attributes"
    if attributes.is_symlink() or not attributes.is_file() or attributes.read_text() != BYTE_ATTRIBUTES:
        raise ValueError("byte-preserving canonical attributes changed")
    if canonical_hashes(root, commit) != expected:
        raise ValueError("canonical Git blobs differ from retained fixture bytes/path set")


def policy_seal() -> dict[str, Any]:
    paths = sorted((ROOT / "src/memglide").rglob("*.py")) + [Path(__file__), PROTOCOL, HELPER_PATH,
             ROOT / "tests/test_benchmark_automatic_v4.py", ROOT / "pyproject.toml", ROOT / "uv.lock"]
    return {"head": git(ROOT, "rev-parse", "HEAD"), "files": {path.relative_to(ROOT).as_posix(): sha(path.read_bytes()) for path in paths}}


def freeze(output: Path) -> dict[str, Any]:
    output = new_directory(output)
    record = {"version": "automatic-4", "seal": policy_seal(), "settings": SETTINGS, "arms": list(ARMS),
              "seed": SEED, "repeats": REPEATS, **base.runtime_identity(), "corpus_selected_or_inspected": False,
              "scope": "offline source-scope proxies/fidelity/local overhead only; no coding correctness/model economics"}
    dump(output / "policy-freeze.json", record)
    return record


def verify_freeze(record: dict[str, Any]) -> None:
    if (record.get("version") != "automatic-4" or record.get("settings") != SETTINGS or record.get("arms") != list(ARMS)
            or record.get("seed") != SEED or record.get("repeats") != REPEATS or record.get("corpus_selected_or_inspected") is not False
            or record.get("seal") != policy_seal() or any(record.get(key) != value for key, value in base.runtime_identity().items())):
        raise ValueError("v4 policy/runtime/runner/protocol changed after pre-corpus freeze")


def validate_provenance(provenance: dict[str, Any], fixtures: Path, tasks: list[dict[str, Any]]) -> None:
    base.validate_provenance(provenance, fixtures, tasks)
    urls = [metadata["repository_url"].lower().removesuffix("/").removesuffix(".git") for metadata in provenance.values()]
    if len(set(urls)) != len(urls) or any(not re.fullmatch(r"https://github\.com/[a-z0-9_.-]+/[a-z0-9_.-]+", url) for url in urls):
        raise ValueError("repository labels must refer to distinct canonical upstream roots")


def validate_tasks(positives: list[dict[str, Any]], controls: list[dict[str, Any]], grading: dict[str, Any]) -> None:
    if len(positives) != 12 or len(controls) != 4:
        raise ValueError("requires twelve positive coding tasks and four separate controls")
    tasks = positives + controls
    if len({task.get("id") for task in tasks}) != 16 or set(grading) != {task.get("id") for task in tasks}:
        raise ValueError("public/private task identity mismatch")
    positive_repositories = {task.get("repository") for task in positives}
    if len(positive_repositories) < 6 or {task.get("repository") for task in controls} - positive_repositories:
        raise ValueError("requires at least six positive upstream roots; controls use those roots")
    if {language: sum(task.get("language") == language for task in positives) for language in ("python", "typescript")} != {"python": 6, "typescript": 6}:
        raise ValueError("positive tasks require six Python and six TypeScript tasks")
    for task in tasks:
        positive = task in positives
        prefix = "t" if positive else "c"
        if set(task) != {"id", "repository", "language", "prompt"} or not re.fullmatch(prefix + r"\d{2}", task["id"]):
            raise ValueError("neutral public task schema contains target/grade metadata")
        if not re.fullmatch(r"r\d{2}", task["repository"]) or task["language"] not in {"python", "typescript"}:
            raise ValueError("invalid neutral repository/language")
        prompt = task["prompt"]
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode()) > 4000:
            raise ValueError("invalid task text")
        grade = grading[task["id"]]
        allowed = {"kind", "required_paths", "rationale", "task_kind", "scope_limitations"}
        if not isinstance(grade, dict) or set(grade) - allowed:
            raise ValueError("offline scope labels must not contain native reference fixes/tests")
        if grade.get("kind") != ("positive" if positive else "abstention_control") or not grade.get("rationale"):
            raise ValueError("private scope kind/rationale mismatch")
        paths = grade.get("required_paths")
        if not isinstance(paths, list) or len(paths) > 8 or len(set(paths)) != len(paths) or not all(safe_relative(path) for path in paths):
            raise ValueError("invalid existing-source scope")
        if bool(paths) != positive:
            raise ValueError("positive scope must be nonempty; control scope must be empty")
        if any(path in prompt or PurePosixPath(path).name in prompt for path in paths):
            raise ValueError("public task leaks known target paths")


def assignments(positives: list[dict[str, Any]], controls: list[dict[str, Any]], repeats: int = REPEATS) -> list[dict[str, Any]]:
    if type(repeats) is not int or repeats not in {1, 2}:
        raise ValueError("repeats must be one explicit pilot or two formal repeats")
    generator = random.Random(SEED)
    selected, arm_orders = [], {}
    for kind, items in (("positive", positives), ("abstention_control", controls)):
        members, choices = list(items), list(permutations(ARMS))
        generator.shuffle(members)
        generator.shuffle(choices)
        for index, task in enumerate(members):
            selected.append((task, kind))
            arm_orders[task["id"]] = choices[index % len(choices)]
    generator.shuffle(selected)
    result: list[dict[str, Any]] = []
    for repeat in range(1, repeats + 1):
        for task, kind in selected:
            order = arm_orders[task["id"]]
            if repeat == 2:
                order = tuple(reversed(order))
            first = len(result)
            result.extend({"ordinal": first + position + 1, "task_id": task["id"], "kind": kind,
                           "arm": arm, "repeat": repeat} for position, arm in enumerate(order))
    return result


def make_plan(freeze_path: Path, output: Path, *, tasks_path: Path = TASKS, controls_path: Path = CONTROLS,
              grading_path: Path = GRADING, provenance_path: Path = PROVENANCE, fixtures: Path = FIXTURES,
              repeats: int = REPEATS) -> dict[str, Any]:
    frozen = json.loads(freeze_path.read_text())
    verify_freeze(frozen)
    positives, controls, grading = (json.loads(path.read_text()) for path in (tasks_path, controls_path, grading_path))
    validate_tasks(positives, controls, grading)
    tasks = positives + controls
    provenance = json.loads(provenance_path.read_text())
    validate_provenance(provenance, fixtures, tasks)
    hashes = tree_hashes(fixtures)
    output = new_directory(output)
    repositories = {}
    for index, identifier in enumerate(sorted({task["repository"] for task in tasks}), 1):
        root = output / "repositories" / f"repo-{index:04d}"
        root.parent.mkdir(exist_ok=True)
        shutil.copytree(fixtures / identifier, root)
        initialize_repository(root)
        repositories[identifier] = {"path": str(root), "commit": git(root, "rev-parse", "HEAD"), "tree": git(root, "rev-parse", "HEAD^{tree}")}
        verify_repository(root, repositories[identifier]["commit"], provenance[identifier]["retained_file_sha256"])
    for task in tasks:
        if any(not (Path(repositories[task["repository"]]["path"]) / path).is_file() for path in grading[task["id"]]["required_paths"]):
            raise ValueError("declared existing-source target does not exist")
    inputs = {"tasks": tasks_path, "controls": controls_path, "grading": grading_path, "provenance": provenance_path}
    plan = {"version": "automatic-4", "plan_directory": str(output), "policy_freeze": frozen, "positive_tasks": positives, "controls": controls,
            "grading": grading, "provenance": provenance, "repositories": repositories, "repeats": repeats,
            "pilot": repeats != REPEATS, "settings": SETTINGS, "assignments": assignments(positives, controls, repeats),
            "inputs": {key: {"path": str(path.resolve()), "sha256": sha(path.read_bytes())} for key, path in inputs.items()},
            "fixtures": str(fixtures.resolve()), "fixture_hashes": hashes}
    dump(output / "plan.json", plan)
    return plan


def verify_plan(plan: dict[str, Any]) -> None:
    verify_freeze(plan["policy_freeze"])
    loaded = {}
    for key, descriptor in plan["inputs"].items():
        data = Path(descriptor["path"]).read_bytes()
        if sha(data) != descriptor["sha256"]:
            raise ValueError("frozen corpus input changed: " + key)
        loaded[key] = json.loads(data)
    if any(loaded[key] != plan[field] for key, field in (("tasks", "positive_tasks"), ("controls", "controls"), ("grading", "grading"), ("provenance", "provenance"))):
        raise ValueError("plan differs from frozen public/private inputs")
    positives, controls = plan["positive_tasks"], plan["controls"]
    validate_tasks(positives, controls, plan["grading"])
    validate_provenance(plan["provenance"], Path(plan["fixtures"]), positives + controls)
    if tree_hashes(Path(plan["fixtures"])) != plan["fixture_hashes"] or plan["settings"] != SETTINGS or plan["assignments"] != assignments(positives, controls, plan["repeats"]):
        raise ValueError("corpus/order/settings changed after plan")
    identifiers = sorted({task["repository"] for task in positives + controls})
    if set(plan["repositories"]) != set(identifiers):
        raise ValueError("canonical repository identity mismatch")
    for index, identifier in enumerate(identifiers, 1):
        repository = plan["repositories"][identifier]
        root = Path(repository["path"])
        if root != Path(plan["plan_directory"]) / "repositories" / f"repo-{index:04d}" or root.resolve(strict=True) != root:
            raise ValueError("canonical neutral repository mapping changed")
        verify_repository(root, repository["commit"], plan["provenance"][identifier]["retained_file_sha256"])
        if git(root, "rev-parse", "HEAD") != repository["commit"] or git(root, "rev-parse", "HEAD^{tree}") != repository["tree"] or git(root, "status", "--porcelain"):
            raise ValueError("canonical repository changed")


def worker(request_path: Path) -> dict[str, Any]:
    if request_path.stat().st_size > 16_000:
        raise ValueError("worker request exceeded cap")
    config = json.loads(request_path.read_text())
    allowed = {"arm", "prompt", "worktree", "settings"} | ({"known_paths"} if config.get("arm") == "B" else set())
    if set(config) != allowed or config.get("arm") not in ARMS or config.get("settings") != SETTINGS:
        raise ValueError("automatic request contains target/grade metadata or invalid settings")
    root = Path(config["worktree"])
    if root.resolve(strict=True) != root or root.parent != request_path.resolve().parents[2] / "worktrees" or not re.fullmatch(r"work-\d{4}", root.name):
        raise ValueError("invalid neutral isolated worktree")
    if not isinstance(config["prompt"], str) or len(config["prompt"].encode()) > 4000:
        raise ValueError("invalid public task")
    from memglide.core.indexer import Indexer
    from memglide.integrations.auto_preload import prepare_task_prompt
    from memglide.integrations.preload import prepare_prompt
    from memglide.storage.database import Database

    before = resources()
    wall, cpu = time.perf_counter(), time.process_time()
    database = Database(request_path.parent / "state" / "state.db")
    project = Indexer(database).add_project(str(root))["id"]
    setup: dict[str, Any] = {"wall_seconds": time.perf_counter() - wall, "cpu_seconds": time.process_time() - cpu}
    indexed = resources()
    setup["waited_child_cpu_seconds"] = difference(indexed["waited_child_cpu_seconds"], before["waited_child_cpu_seconds"])
    wall, cpu = time.perf_counter(), time.process_time()
    if config["arm"] == "B":
        paths = config["known_paths"]
        preparation = prepare_prompt(config["prompt"], project_id=project, db_path=database.path, focus_paths=paths,
                                     mode="auto" if paths else "off", context_format=SETTINGS["context_format"], max_context_bytes=SETTINGS["max_context_bytes"])
    else:
        preparation = prepare_task_prompt(config["prompt"], project_id=project, db_path=database.path, enabled=True,
                                          selection_policy="v3" if config["arm"] == "V3" else "v4", **SETTINGS)
    timing: dict[str, Any] = {"wall_seconds": time.perf_counter() - wall, "cpu_seconds": time.process_time() - cpu}
    after = resources()
    timing["waited_child_cpu_seconds"] = difference(after["waited_child_cpu_seconds"], indexed["waited_child_cpu_seconds"])
    return {"preparation": preparation, "setup": setup, "timing": timing, "resources": after,
            "source_mutations": git(root, "status", "--porcelain"), "dispatched_model_requests": 0}


def run_child(request: Path, directory: Path) -> dict[str, Any]:
    launched, cleanup_error = time.perf_counter(), None
    try:
        with (directory / "stdout.log").open("wb") as out, (directory / "stderr.log").open("wb") as err:
            process = subprocess.Popen([sys.executable, "-m", "benchmarks.run_automatic_v4", "worker", "--request", str(request)],
                                       cwd=ROOT, stdout=out, stderr=err, env=git_environment(), start_new_session=base.os.name == "posix")
            try:
                process.wait(timeout=TIMEOUT)
            except BaseException:
                try:
                    stop_process_group(process)
                except Exception as exc:
                    cleanup_error = type(exc).__name__ + ": " + str(exc)
                raise
            try:
                stop_process_group(process)
            except Exception as exc:
                cleanup_error = type(exc).__name__ + ": " + str(exc)
        lifetime = time.perf_counter() - launched
        if any((directory / name).stat().st_size > MAX_LOG_BYTES for name in ("stdout.log", "stderr.log")):
            raise ValueError("worker output exceeded validation limit; originals retained")
        observation = json.loads((directory / "stdout.log").read_text())
        if not isinstance(observation, dict):
            raise ValueError("worker output must be an object")
        return {"observation": observation, "returncode": process.returncode, "process_wall_seconds": lifetime,
                "worker_completed": process.returncode == 0 and not observation.get("source_mutations") and cleanup_error is None,
                "cleanup_error": cleanup_error, "halt_after_failure": cleanup_error is not None}
    except (subprocess.SubprocessError, OSError, ValueError, KeyboardInterrupt) as exc:
        return {"observation": None, "worker_completed": False, "process_wall_seconds": time.perf_counter() - launched,
                "error": type(exc).__name__ + ": " + str(exc), "interrupted": isinstance(exc, KeyboardInterrupt),
                "cleanup_error": cleanup_error, "halt_after_failure": cleanup_error is not None}


def _valid(row: dict[str, Any]) -> bool:
    return row.get("worker_completed") is True and row.get("fidelity", {}).get("valid") is True


def _metrics(observation: dict[str, Any], fidelity: dict[str, Any]) -> dict[str, Any]:
    preparation, setup, timing, usage = observation["preparation"], observation["setup"], observation["timing"], observation["resources"]
    return {"setup_plus_preparation_wall_seconds": setup["wall_seconds"] + timing["wall_seconds"],
            "preparation_wall_seconds": timing["wall_seconds"], "preparation_cpu_seconds": timing["cpu_seconds"],
            "setup_cpu_seconds": setup["cpu_seconds"], "setup_waited_child_cpu_seconds": setup["waited_child_cpu_seconds"],
            "preparation_waited_child_cpu_seconds": timing["waited_child_cpu_seconds"], "context_bytes": preparation["context_bytes"],
            "selected_source_bytes": fidelity["selected_source_bytes"], "self_peak_rss_bytes": usage["self_peak_rss_bytes"],
            "max_waited_child_rss_bytes": usage["max_waited_child_rss_bytes"]}


def summarize(rows: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    positives, controls, repeats = plan["positive_tasks"], plan["controls"], plan["repeats"]
    tasks, grading = positives + controls, plan["grading"]
    indexed = {(row["task_id"], row["repeat"], row["arm"]): row for row in rows}
    result: dict[str, Any] = {"arms": {}, "paired_effects": {}, "default_promotion": False}
    numeric = ("setup_plus_preparation_wall_seconds", "preparation_wall_seconds", "preparation_cpu_seconds", "setup_cpu_seconds",
               "setup_waited_child_cpu_seconds", "preparation_waited_child_cpu_seconds", "context_bytes", "selected_source_bytes", "self_peak_rss_bytes", "max_waited_child_rss_bytes")
    for arm in ARMS:
        members = [row for row in rows if row["arm"] == arm]
        record: dict[str, Any] = {"planned": len(tasks) * repeats, "observed": len(members), "worker_errors": sum(row.get("worker_completed") is not True for row in members),
                                  "fidelity_passes": sum(_valid(row) for row in members), "evaluator_errors": sum(bool(row.get("error")) and row.get("worker_completed") is True for row in members)}
        for kind, selected, field in (("positive", positives, "declared_scope_complete"), ("abstention_control", controls, "expected_bypass")):
            relevant = [row for row in members if grading[row["task_id"]]["kind"] == kind]
            values: dict[str, Any] = {}
            for metric in numeric + ("process_wall_seconds",):
                observed = [row.get(metric) if metric == "process_wall_seconds" else row.get("metrics", {}).get(metric) for row in relevant]
                measurements = [float(value) for value in observed if isinstance(value, (int, float)) and not isinstance(value, bool)]
                values[metric] = {"observed": len(measurements), "missing_of_planned": len(selected) * repeats - len(measurements),
                                  "mean": statistics.mean(measurements) if measurements else None, "median": statistics.median(measurements) if measurements else None}
            consistent = [task["id"] for task in selected if all(_valid(row := indexed.get((task["id"], repeat, arm), {})) and row.get("scope_grade", {}).get(field) is True for repeat in range(1, repeats + 1))]
            record[kind] = {"planned": len(selected) * repeats, "observed": len(relevant),
                            "scope_or_control_passes": sum(_valid(row) and row.get("scope_grade", {}).get(field) is True for row in relevant),
                            "consistent_tasks_all_repeats": consistent, "metrics": values}
        result["arms"][arm] = record
    for baseline in ("B", "V3"):
        for kind, selected in (("positive", positives), ("abstention_control", controls)):
            for metric in ("setup_plus_preparation_wall_seconds", "preparation_wall_seconds", "preparation_cpu_seconds", "context_bytes", "self_peak_rss_bytes"):
                clusters: dict[str, list[tuple[float, float]]] = {}
                task_effects, missing = [], []
                for task in selected:
                    pairs = []
                    for repeat in range(1, repeats + 1):
                        first, second = (indexed.get((task["id"], repeat, arm), {}) for arm in (baseline, "C"))
                        candidates = [row.get("metrics", {}).get(metric) for row in (first, second)]
                        if _valid(first) and _valid(second) and all(type(value) in {int, float} for value in candidates):
                            pairs.append((float(candidates[0]), float(candidates[1])))
                    if len(pairs) == repeats:
                        clusters.setdefault(task["repository"], []).extend(pairs)
                        task_effects.append({"task_id": task["id"], "pairs": len(pairs), "mean_delta": statistics.mean(right - left for left, right in pairs), "median_delta": statistics.median(right - left for left, right in pairs)})
                    else:
                        missing.append({"task_id": task["id"], "observed_valid_metric_pairs": len(pairs), "planned_pairs": repeats})
                effect = base.clustered_effect(clusters, seed=SEED)
                effect["repository_clusters"] = effect.pop("task_clusters")
                effect.update({"interval_unit": "repository cluster retaining all tasks/repeats", "per_task_effects": task_effects,
                               "missing_or_invalid_task_pairs": missing, "planned_tasks": len(selected)})
                result["paired_effects"]["C_minus_" + baseline + ":" + kind + ":" + metric] = effect
    expected = {(task["id"], repeat, arm) for task in tasks for repeat in range(1, repeats + 1) for arm in ARMS}
    actual = set(indexed)
    result.update({"unrun_assignments": len(expected - actual), "duplicate_assignments": len(rows) - len(actual),
                   "integrity_complete": actual == expected and len(rows) == len(expected) and all(_valid(row) for row in rows)})
    result["actual_order_counts"] = {str(repeat): {arm: {str(position): sum(row["repeat"] == repeat and row["arm"] == arm and (row["ordinal"] - 1) % 3 + 1 == position for row in rows) for position in range(1, 4)} for arm in ARMS} for repeat in range(1, repeats + 1)}
    result["actual_pair_precedence"] = {}
    for kind, selected in (("positive", positives), ("abstention_control", controls)):
        result["actual_pair_precedence"][kind] = {}
        for repeat in range(1, repeats + 1):
            counts = {}
            for first_arm, second_arm in combinations(ARMS, 2):
                order_pairs = [(indexed.get((task["id"], repeat, first_arm)), indexed.get((task["id"], repeat, second_arm))) for task in selected]
                complete = [(left["ordinal"], right["ordinal"]) for left, right in order_pairs if left is not None and right is not None]
                counts[first_arm + "_vs_" + second_arm] = {first_arm + "_first": sum(left < right for left, right in complete),
                                                         second_arm + "_first": sum(right < left for left, right in complete), "missing": len(selected) - len(complete)}
            result["actual_pair_precedence"][kind][str(repeat)] = counts
    result["strata_counts"] = {field: {value: {arm: {"planned": sum(task[field] == value for task in tasks) * repeats,
                                                     "observed": sum(row["arm"] == arm and next(task for task in tasks if task["id"] == row["task_id"])[field] == value for row in rows)} for arm in ARMS} for value in sorted({task[field] for task in tasks})} for field in ("language", "repository")}
    return result


def evaluate(plan_path: Path, output: Path) -> dict[str, Any]:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    verify_plan(plan)
    if plan.get("plan_directory") is not None and plan_path.resolve().parent != Path(plan["plan_directory"]):
        raise ValueError("plan location differs from frozen canonical repository mapping")
    output = new_directory(output)
    (output / "plan-input.json").write_bytes(plan_bytes)
    (output / "worktrees").mkdir()
    (output / "runs").mkdir()
    tasks = {task["id"]: task for task in plan["positive_tasks"] + plan["controls"]}
    rows, interrupted = [], False
    for assignment in plan["assignments"]:
        task = tasks[assignment["task_id"]]
        repository = plan["repositories"][task["repository"]]
        ordinal = assignment["ordinal"]
        worktree, artifacts = output / "worktrees" / f"work-{ordinal:04d}", output / "runs" / f"run-{ordinal:04d}"
        artifacts.mkdir()
        row = {**assignment, "worker_completed": False}
        try:
            git(Path(repository["path"]), "worktree", "add", "--detach", str(worktree), repository["commit"])
            request = {"arm": assignment["arm"], "prompt": task["prompt"], "worktree": str(worktree), "settings": SETTINGS}
            if assignment["arm"] == "B":
                request["known_paths"] = plan["grading"][task["id"]]["required_paths"]
            dump(artifacts / "request.json", request)
            row.update(run_child(artifacts / "request.json", artifacts))
            if row["worker_completed"]:
                row["fidelity"] = verify_delivery(row["observation"]["preparation"], task["prompt"], repository)
                row["scope_grade"] = grade_scope(row["fidelity"], plan["grading"][task["id"]])
                row["metrics"] = _metrics(row["observation"], row["fidelity"])
        except Exception as exc:
            row.update({"error": type(exc).__name__ + ": " + str(exc), "fidelity": {"valid": False}})
        except KeyboardInterrupt:
            row.update({"worker_completed": False, "interrupted": True, "error": "KeyboardInterrupt"})
        rows.append(row)
        dump(artifacts / "result.json", row)
        if row.get("interrupted") or row.get("halt_after_failure"):
            interrupted = bool(row.get("interrupted"))
            break
    try:
        verify_plan(plan)
        if plan_path.read_bytes() != plan_bytes:
            raise ValueError("plan file changed during cohort")
        unchanged, seal_error = True, None
    except Exception as exc:
        unchanged, seal_error = False, type(exc).__name__ + ": " + str(exc)
    summary = summarize(rows, plan)
    summary["integrity_complete"] = summary["integrity_complete"] and unchanged
    report = {"version": "automatic-4", "plan_sha256": sha(plan_bytes), "rows": rows, "summary": summary,
              "seal_unchanged": unchanged, "seal_error": seal_error, "interrupted": interrupted,
              "dispatched_model_requests": 0, "coding_task_success": None, "total_coding_task_time": None,
              "model_input_tokens": None, "cached_model_input_tokens": None, "model_output_tokens": None,
              "estimated_model_cost": None, "actual_billed_charges": None,
              "limits": "Offline author-scope proxies/local overhead only. Complete files do not prove semantic completeness or code correctness. Lower bytes from bypasses are not savings. SELF/child peaks never summed; OS caches/load uncontrolled."}
    dump(output / "report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "plan", "run", "worker"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args(argv)
    if args.command == "worker":
        if args.request is None:
            parser.error("worker requires --request")
        data = json.dumps(worker(args.request), sort_keys=True)
        if len(data.encode()) > MAX_LOG_BYTES:
            raise ValueError("worker output exceeded serialization cap")
        print(data)
        return 0
    if args.output is None:
        parser.error("requires --output NEW_DIRECTORY")
    if args.command == "freeze":
        freeze(args.output)
    elif args.command == "plan":
        if args.freeze is None:
            parser.error("plan requires --freeze POLICY_FREEZE_JSON")
        make_plan(args.freeze, args.output)
    else:
        if args.plan is None:
            parser.error("run requires --plan PLAN_JSON")
        return int(not evaluate(args.plan, args.output)["summary"]["integrity_complete"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
