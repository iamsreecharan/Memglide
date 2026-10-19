"""Reproduce local graph-work and retained-source-memory component measurements.

Graph: uv run python benchmarks/saas_graph_efficiency.py --component graph
Scan:  uv run python benchmarks/saas_graph_efficiency.py --component scan

No native agent or model is invoked. Graph baseline emulates exactly the prior
unconditional resolver branch, holding current secure scanning common. The old
Git source is read only to verify that branch and unchanged resolver semantics.
"""
from __future__ import annotations

import argparse
import ast
import gc
import hashlib
import inspect
import json
import resource
import statistics
import subprocess
import textwrap
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable
from unittest.mock import patch

import memglide.core.indexer as module
from memglide.core.indexer import Indexer
from memglide.storage.database import Database

BASELINE_REF = "6de6f150aaa90fba14e49439723a8139c03217eb"
APP_PATH = "src/memglide/core/indexer.py"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _prior_source(root: Path, reference: str) -> tuple[str, bytes]:
    revision = subprocess.run(
        ["git", "rev-parse", "--verify", "--end-of-options", reference + "^{commit}"],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()
    source = subprocess.run(
        ["git", "cat-file", "blob", f"{revision}:{APP_PATH}"],
        cwd=root, check=True, capture_output=True,
    ).stdout
    return revision, source


def _baseline_reindex(old_source: bytes) -> tuple[Callable[..., Any], str]:
    old_class = next(
        node for node in ast.parse(old_source).body if isinstance(node, ast.ClassDef)
        and node.name == "Indexer"
    )
    old_resolve = next(node for node in old_class.body if isinstance(node, ast.FunctionDef)
                       and node.name == "_resolve")
    current_resolve = ast.parse(textwrap.dedent(inspect.getsource(Indexer._resolve))).body[0]
    assert ast.dump(old_resolve, include_attributes=False) == ast.dump(
        current_resolve, include_attributes=False
    ), "Resolver semantics changed: review and version this comparison before running"
    old_reindex = next(node for node in old_class.body if isinstance(node, ast.FunctionDef)
                       and node.name == "reindex")
    old_calls = [node for node in ast.walk(old_reindex) if isinstance(node, ast.Expr)
                 and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Attribute)
                 and node.value.func.attr == "_resolve"]
    assert len(old_calls) == 1, "Expected exactly one old direct resolver call"
    source = textwrap.dedent(inspect.getsource(Indexer.reindex))

    class UnconditionalResolver(ast.NodeTransformer):
        replacements = 0

        def visit_If(self, node: ast.If) -> Any:
            self.generic_visit(node)
            if isinstance(node.test, ast.Name) and node.test.id == "refresh_graph":
                assert len(node.body) == 1 and not node.orelse
                assert ast.dump(node.body[0], include_attributes=False) == ast.dump(
                    old_calls[0], include_attributes=False
                )
                node.test = ast.Constant(value=True)
                self.replacements += 1
            return node

    transform = UnconditionalResolver()
    tree = ast.fix_missing_locations(transform.visit(ast.parse(source)))
    assert transform.replacements == 1, "Expected exactly one graph conditional"
    namespace = dict(module.__dict__)
    exec(compile(tree, "<trusted-current-indexer-unconditional-graph-branch>", "exec"), namespace)
    return namespace["reindex"], _sha(source.encode())


def _graph(db: Database, project: str) -> list[dict[str, Any]]:
    return db.rows("SELECT * FROM dependencies WHERE project_id=? ORDER BY id", (project,))


def _summarize(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for arm in ("baseline", "candidate"):
        selected = [row for row in rows if row["arm"] == arm]
        result[arm] = {"runs": len(selected)}
        for field in fields:
            values = [row[field] for row in selected]
            result[arm][field + "_mean"] = statistics.mean(values)
            result[arm][field + "_median"] = statistics.median(values)
            result[arm][field + "_total"] = sum(values)
    result["relative_change_percent"] = {
        field + "_mean": (result["candidate"][field + "_mean"] /
                           result["baseline"][field + "_mean"] - 1) * 100
        for field in fields if result["baseline"][field + "_mean"] != 0
    }
    return result


def graph_probe(directory: Path, files: int, repeats: int, old_source: bytes) -> dict[str, Any]:
    legacy, method_sha = _baseline_reindex(old_source)
    root = directory / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for index in range(files):
        source = (
            f"from module_{index-1} import calculate as prior\n\ndef calculate(value):\n"
            "    return prior(value) + 1\n"
            if index else "def calculate(value):\n    return value + 1\n"
        )
        (root / f"module_{index}.py").write_text(source)
    db = Database(directory / "state.sqlite")
    indexer = Indexer(db)
    project = indexer.add_project(str(root))["id"]
    frozen = _graph(db, project)
    assert len(frozen) == (files - 1) * 2 and all(edge["resolved"] for edge in frozen)
    graph_sha = _sha(json.dumps(frozen, sort_keys=True).encode())
    original_resolve = Indexer._resolve
    original_read = module.read_source
    legacy(indexer, project)
    indexer.reindex(project)
    rows: list[dict[str, Any]] = []
    for repeat in range(repeats):
        order = ("baseline", "candidate") if repeat % 2 == 0 else ("candidate", "baseline")
        for arm in order:
            observed = {"graph_row_updates": 0, "secure_source_reads": 0}

            def read(*args: Any, **kwargs: Any) -> tuple[str, str]:
                observed["secure_source_reads"] += 1
                return original_read(*args, **kwargs)

            def resolve(connection: Any, selected: str) -> None:
                before = connection.total_changes
                original_resolve(connection, selected)
                observed["graph_row_updates"] += connection.total_changes - before

            with patch.object(module, "read_source", read), patch.object(indexer, "_resolve", resolve):
                wall_start = time.perf_counter()
                cpu_start = time.process_time()
                child_start = resource.getrusage(resource.RUSAGE_CHILDREN)
                method = legacy if arm == "baseline" else Indexer.reindex
                stats = method(indexer, project)
                cpu_elapsed = time.process_time() - cpu_start
                child_end = resource.getrusage(resource.RUSAGE_CHILDREN)
                wall_elapsed = time.perf_counter() - wall_start
            assert stats["indexed"] == stats["deleted"] == 0
            assert _graph(db, project) == frozen
            assert observed["secure_source_reads"] == files
            rows.append({"repeat": repeat + 1, "arm": arm, "wall_seconds": wall_elapsed,
                         "process_cpu_seconds": cpu_elapsed,
                         "child_cpu_seconds": child_end.ru_utime + child_end.ru_stime -
                         child_start.ru_utime - child_start.ru_stime,
                         "graph_sha256": graph_sha, **observed})
    return {
        "fixture": {"files": files, "graph_edges": len(frozen), "repeats_per_arm": repeats,
                    "working_tree": "synthetic uncommitted Python repository",
                    "warm_up_both_paths": True, "alternating_order": True,
                    "secure_full_scan_both_arms": True, "os_cache_controlled": False},
        "baseline": "Emulated former unconditional resolver branch in trusted current reindex",
        "ast_transformation": "Exactly one If(Name('refresh_graph')) becomes If(Constant(True)); "
                              "the resolver call and resolver AST must match actual prior Git source",
        "measured_reindex_method_sha256": method_sha,
        "summary": _summarize(rows, ["wall_seconds", "process_cpu_seconds", "child_cpu_seconds",
                                      "graph_row_updates", "secure_source_reads"]),
        "all_graph_outputs_equal": True, "runs": rows,
    }


def scan_probe(directory: Path, repeats: int) -> dict[str, Any]:
    root = directory / "repo"
    root.mkdir()
    # Exactly20MiB, below the100MiB index cap; each file passes a1MiB fixture limit.
    files = 40
    body = "# safe source fixture\n"
    body = (body * (524_288 // len(body) + 1))[:524_288]
    for index in range(files):
        (root / f"module_{index:03}.py").write_text(body)
    known = {path.name: _sha(body.encode()) for path in root.iterdir()}
    db = Database(directory / "state.sqlite")
    indexer = Indexer(db)
    settings = {**db.settings(), "max_file_size": 1_048_576}
    original_read = module.read_source
    rows: list[dict[str, Any]] = []
    for repeat in range(repeats):
        order = ("baseline", "candidate") if repeat % 2 == 0 else ("candidate", "baseline")
        for arm in order:
            observed = {"secure_source_reads": 0}

            def read(*args: Any, **kwargs: Any) -> tuple[str, str]:
                observed["secure_source_reads"] += 1
                return original_read(*args, **kwargs)

            gc.collect()
            tracemalloc.start()
            with patch.object(module, "read_source", read):
                wall_start = time.perf_counter()
                cpu_start = time.process_time()
                sources, ignored, errors = indexer._scan(
                    root, settings, known_hashes=known if arm == "candidate" else None
                )
                cpu_elapsed = time.process_time() - cpu_start
                wall_elapsed = time.perf_counter() - wall_start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            assert not ignored and not errors and len(sources) == files
            assert {path: pair[1] for path, pair in sources.items()} == known
            assert observed["secure_source_reads"] == files
            retained = sum(len(pair[0].encode()) for pair in sources.values())
            assert retained == (files * len(body) if arm == "baseline" else 0)
            rows.append({"repeat": repeat + 1, "arm": arm, "wall_seconds": wall_elapsed,
                         "process_cpu_seconds": cpu_elapsed, "tracemalloc_peak_bytes": peak,
                         "retained_source_bytes": retained,
                         "source_manifest_sha256": _sha(json.dumps(known, sort_keys=True).encode()),
                         **observed})
            del sources
    return {
        "fixture": {"files": files, "source_bytes": files * len(body),
                    "repeats_per_arm": repeats, "alternating_order": True,
                    "secure_full_scan_both_arms": True, "os_cache_controlled": False,
                    "tracemalloc_enabled_both_arms": True},
        "baseline": "Current _scan with default complete-source retention",
        "candidate": "Same scanner with known_hashes: releases live-verified unchanged bodies",
        "summary": _summarize(rows, ["wall_seconds", "process_cpu_seconds", "tracemalloc_peak_bytes",
                                      "retained_source_bytes", "secure_source_reads"]),
        "all_source_hash_outputs_equal": True, "runs": rows,
    }


def _markdown(result: dict[str, Any]) -> str:
    component = result["component"]
    fields = [key.removesuffix("_mean") for key in result["summary"]["baseline"]
              if key.endswith("_mean")]
    lines = [f"# SaaS efficiency: local {component} component probe", "",
             "These are local component measurements. No Codex/model request was made; "
             "model tokens, model latency, actual charges and cost savings are unknown.", "",
             "## Method", "", result["baseline"], "",
             "Both arms use the same live secure source reader. Graph comparison holds "
             "the current scanner common; scan comparison holds the scanner code common "
             "and changes only retention of bodies already verified unchanged.", "",
             "The graph baseline is an explicit old-branch emulation, not a benchmark "
             "of the entire historical application. Its resolver semantics and exact "
             "call are checked against the pinned prior Git source. OS caches are "
             "uncontrolled. Results describe this synthetic fixture, not SaaS throughput.", "",
             f"Prior source: `{result['provenance']['baseline_ref']}` / `{APP_PATH}`; "
             f"SHA256 `{result['provenance']['baseline_source_sha256']}`.", "",
             f"Current source SHA256 `{result['provenance']['candidate_source_sha256']}`.", "",
             "Fixture: `" + json.dumps(result["fixture"], sort_keys=True) + "`.", "",
             "## Measurements", "", "| Metric | Baseline mean | Candidate mean | Change |",
             "|---|---:|---:|---:|"]
    for field in fields:
        before = result["summary"]["baseline"][field + "_mean"]
        after = result["summary"]["candidate"][field + "_mean"]
        change = result["summary"]["relative_change_percent"].get(field + "_mean")
        delta = "unavailable" if change is None else f"{change:+.2f}%"
        lines.append(f"| {field} | {before:.6f} | {after:.6f} | {delta} |")
    lines += ["", "Full individual samples, medians and totals are retained in the adjacent JSON.",
              "Graph outputs and source hashes must match across every measured run; "
              "an assertion failure stops publication. Counts of secure reads stay unchanged.", "",
              "`process_cpu_seconds` excludes child processes; graph JSON reports child CPU "
              "separately. `tracemalloc_peak_bytes` measures Python allocations during "
              "instrumented scanning, not total process RSS or server memory. Instrumented "
              "scan timing should not be treated as uninstrumented application latency.", "",
              "## Reproduce", "", "```sh",
              f"uv run python benchmarks/saas_graph_efficiency.py --component {component}", "```", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=("graph", "scan"), default="graph")
    parser.add_argument("--files", type=int, default=600, help="graph fixture files")
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--baseline-ref", default=BASELINE_REF)
    parser.add_argument("--output-prefix", type=Path)
    arguments = parser.parse_args()
    if not 2 <= arguments.files <= 5000 or not 1 <= arguments.repeats <= 100:
        parser.error("files must be2..5000 and repeats1..100")
    repo = Path(__file__).resolve().parents[1]
    revision, old_source = _prior_source(repo, arguments.baseline_ref)
    current_source = Path(module.__file__).read_bytes()
    with TemporaryDirectory(prefix="memglide-component-probe-") as directory:
        result = (graph_probe(Path(directory), arguments.files, arguments.repeats, old_source)
                  if arguments.component == "graph" else scan_probe(Path(directory), arguments.repeats))
    result.update({
        "version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "component": arguments.component,
        "provenance": {"baseline_ref": revision, "baseline_source_path": APP_PATH,
                       "baseline_source_sha256": _sha(old_source),
                       "candidate_source_path": APP_PATH,
                       "candidate_source_sha256": _sha(current_source),
                       "helper_sha256": _sha(Path(__file__).read_bytes())},
        "model_requests": 0, "model_tokens": None, "model_cost": None,
        "model_latency_seconds": None, "actual_billing": None,
    })
    prefix = arguments.output_prefix or repo / "benchmarks" / f"saas-{arguments.component}-efficiency"
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    prefix.with_suffix(".md").write_text(_markdown(result))
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
