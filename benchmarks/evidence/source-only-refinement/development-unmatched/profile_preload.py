"""Small synthetic development-only known-path profile; no model requests."""
import contextlib
import hashlib
import importlib
import json
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import pathspec
from memglide.integrations import preload
from memglide.security import paths as security
from memglide.storage.database import Database


def fixture(base, name, policy):
    root = base / name
    root.mkdir()
    sources = {"src/app/calculate.py": "def calculate(values):\n    return sum(values)\n"}
    if name != "no_ignore_one_source":
        sources.update({
            "src/app/sub/clamp.py": "def clamp(value):\n    return max(0, value)\n",
            "src/app/sub/format.py": "def format_result(value):\n    return str(value)\n",
            "src/shared/types.py": "class Result:\n    pass\n",
        })
    db = Database(base / (name + ".sqlite"))
    db.execute("INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
               (name, str(root), name, time.time()))
    for index, (relative, source) in enumerate(sources.items()):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
        db.execute("INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)", (
            str(index), name, relative, hashlib.sha256(source.encode()).hexdigest(),
            "python", len(source.encode()), path.stat().st_mtime, 1, None, time.time(),
        ))
    for relative, content in policy.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return {"project_id": name, "db_path": db.path, "focus_paths": list(sources),
            "context_format": "compact-prefix"}, sources


def observation(options, expected):
    counts = Counter()
    times = Counter()
    originals = {
        "selection": preload._selection, "eligible": preload._eligible,
        "secure_read": security.read_source, "safe_path": security.safe_path,
        "compile": pathspec.GitIgnoreSpec.from_lines,
        "match": pathspec.GitIgnoreSpec.check_file,
        "connect": sqlite3.connect,
    }

    def measured(name, function):
        def call(*args, **kwargs):
            counts[name] += 1
            started = time.perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                times[name] += time.perf_counter() - started
        return call

    def connect(*args, **kwargs):
        counts["sqlite_connections"] += 1
        connection = originals["connect"](*args, **kwargs)
        connection.set_trace_callback(lambda _: counts.update(["sqlite_statements"]))
        return connection

    def secure_read(root, relative, limit):
        label = "policy_secure_reads" if relative.endswith((".gitignore", ".memglideignore")) else "source_secure_reads"
        return measured(label, originals["secure_read"])(root, relative, limit)

    with contextlib.ExitStack() as stack:
        for target, name, value in (
            (preload, "_selection", measured("selection", originals["selection"])),
            (preload, "_eligible", measured("eligible", originals["eligible"])),
            (security, "read_source", secure_read),
            (security, "safe_path", measured("safe_path", originals["safe_path"])),
            (pathspec.GitIgnoreSpec, "from_lines", staticmethod(measured("ignore_compilations", originals["compile"]))),
            (pathspec.GitIgnoreSpec, "check_file", measured("ignore_match_calls", originals["match"])),
            (sqlite3, "connect", connect),
        ):
            stack.enter_context(patch.object(target, name, value))
        prepared = preload.prepare_prompt("Inspect and correct calculation.", **options)
    assert prepared["mode"] == "preloaded", prepared["reason"]
    envelope = json.loads(prepared["prompt"].removesuffix(preload.TASK_SEPARATOR + "Inspect and correct calculation."))
    assert {row["path"]: row["content"] for row in envelope["memglide_sources"]} == expected
    samples = []
    for _ in range(10):
        started = time.perf_counter()
        repeated = preload.prepare_prompt("Inspect and correct calculation.", **options)
        samples.append(time.perf_counter() - started)
        assert repeated["prompt"] == prepared["prompt"] and repeated["files"] == prepared["files"]
    return {"instrumented_counts": dict(counts), "instrumented_inclusive_seconds": dict(times),
            "uninstrumented_10_warm_api_wall_seconds": {"values": samples, "mean": statistics.mean(samples), "median": statistics.median(samples)},
            "prepared_prompt_sha256": prepared["prepared_prompt_sha256"], "context_bytes": prepared["context_bytes"]}


def imports(module):
    samples = []
    program = "import importlib,json,sys,time;t=time.perf_counter();importlib.import_module(sys.argv[1]);print(json.dumps({'import_seconds':time.perf_counter()-t}))"
    for _ in range(3):
        started = time.perf_counter()
        completed = subprocess.run([sys.executable, "-I", "-c", program, module], check=True, capture_output=True, text=True, timeout=10)
        samples.append({**json.loads(completed.stdout), "process_wall_seconds": time.perf_counter() - started})
    return samples


def main():
    destination = Path(sys.argv[1])
    assert not destination.exists()
    dense = "".join(f"discarded_{index:04d}.tmp\n" for index in range(431))
    dense += "#" * (8191 - len(dense)) + "\n"
    assert len(dense.encode()) == 8192
    cases = {
        "no_ignore_one_source": {},
        "typical_nested_four_sources": {
            ".gitignore": ".cache/\n.venv/\nnode_modules/\n*.log\n*.tmp\ncoverage/\n",
            "src/.gitignore": "generated/\n*.min.js\n.cache/\n",
            "src/app/.memglideignore": "private/\n*.secret\n",
        },
        "dense_8k_four_sources": {".gitignore": dense},
    }
    result = {"scope": "Synthetic development probe; current warm OS caches, no native agents or held-out tasks. Instrumented timers are inclusive and must not be added. Imports use fresh processes but uncontrolled OS caches.",
              "model_requests": 0, "cases": {}, "fresh_process_imports": {}}
    with tempfile.TemporaryDirectory(prefix="known-path-profile-", dir=destination.parent) as temporary:
        for name, policy in cases.items():
            options, sources = fixture(Path(temporary).resolve(), name, policy)
            preload.prepare_prompt("Warm local dependencies.", **options)
            result["cases"][name] = {"source_files": len(sources), "policy_files": len(policy), "policy_bytes": sum(len(value.encode()) for value in policy.values()), **observation(options, sources)}
    for module in ("memglide.integrations.preload", "memglide.integrations.codex_preload", "memglide.security.paths"):
        result["fresh_process_imports"][module] = imports(module)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
