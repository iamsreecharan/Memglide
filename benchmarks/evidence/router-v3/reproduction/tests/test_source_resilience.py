"""Real process restart, rollback and concurrent source observations stay safe."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from contextlib import closing

import pytest

from memglide.integrations.preload import TASK_SEPARATOR, prepare_prompt
from memglide.service import Service

TASK = "Inspect the current computation."
VERSIONS = {
    value: f"def compute(value):\n    return value + {value}\n" for value in (1, 2, 3)
}


@pytest.fixture
def approved_source(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    for path, source in {
        "compute.py": VERSIONS[1],
        "removed.py": "def removed():\n    return 1\n",
        "ignored.py": "def ignored():\n    return 1\n",
    }.items():
        (root / path).write_text(source)
    database = tmp_path / "state" / "memglide.sqlite"
    service = Service(database)
    try:
        project_id = service.indexer.add_project(str(root))["id"]
    finally:
        service.close()
    return root, database, project_id


def child(program, *arguments, **kwargs):
    return subprocess.Popen(
        [sys.executable, "-I", "-c", program, *map(str, arguments)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs,
    )


def wait_for(path, process, timeout=12):
    deadline = time.monotonic() + timeout
    while not path.exists():
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=3)
            pytest.fail(f"Child exited before readiness: {process.returncode}: {stdout} {stderr}")
        if time.monotonic() >= deadline:
            pytest.fail("Child did not reach the bounded process barrier")
        time.sleep(0.01)


def stop(process):
    if process.poll() is None:
        process.kill()
    return process.communicate(timeout=5)


def snapshot(database):
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as connection:
        return {
            "files": connection.execute("SELECT path,hash FROM files ORDER BY path").fetchall(),
            "search": connection.execute("SELECT path,content FROM file_search ORDER BY path").fetchall(),
            "symbols": connection.execute("SELECT path,name,start_line,end_line FROM symbols ORDER BY path,name").fetchall(),
        }


def assert_complete(preparation, source):
    assert preparation["mode"] == "preloaded", preparation["reason"]
    envelope = json.loads(preparation["prompt"].removesuffix(TASK_SEPARATOR + TASK))
    assert envelope["memglide_sources"] == [{"path": "compute.py", "content": source}]
    assert preparation["files"] == [{
        "path": "compute.py", "sha256": hashlib.sha256(source.encode()).hexdigest(),
        "start_line": 1, "end_line": len(source.splitlines()),
    }]


def test_killed_reindex_transaction_recovers_old_index_then_current_source(approved_source, tmp_path):
    root, database, project_id = approved_source
    before = snapshot(database)
    (root / "compute.py").write_text(VERSIONS[2])
    (root / "added.py").write_text("def added():\n    return 2\n")
    barrier = tmp_path / "inside-write.json"
    # SQLite tracing pauses a real reindex after its deletes and before an
    # insert. No index writes or transaction outcomes are substituted by the test.
    program = """
import contextlib,json,sys,time
from pathlib import Path
from memglide.service import Service
service=Service(sys.argv[1]); original=service.db.connect
@contextlib.contextmanager
def observed_connection():
    with original() as connection:
        def trace(statement):
            if statement.lstrip().upper().startswith('INSERT INTO FILES'):
                Path(sys.argv[3]).write_text(json.dumps({'in_transaction':connection.in_transaction,
                                                        'changes':connection.total_changes}))
                while True: time.sleep(.05)
        connection.set_trace_callback(trace)
        yield connection
service.db.connect=observed_connection
service.indexer.reindex(sys.argv[2])
raise AssertionError('The parent should terminate the active write transaction')
"""
    process = child(program, database, project_id, barrier)
    try:
        wait_for(barrier, process)
        observed = json.loads(barrier.read_text())
        assert observed["in_transaction"] is True and observed["changes"] > 0
        assert snapshot(database) == before  # A separate WAL reader sees committed state.
    finally:
        stop(process)
    assert process.returncode != 0
    reopened = Service(database)
    try:
        assert reopened.db.project(project_id)["path"] == str(root)
        assert reopened.db.one("PRAGMA integrity_check")["integrity_check"] == "ok"
        assert reopened.db.rows("PRAGMA foreign_key_check") == []
        assert snapshot(database) == before
        # The persisted index may be old, but known-path preparation must read
        # the live body rather than treating indexed content as current source.
        assert_complete(prepare_prompt(
            TASK, db_path=database, project_id=project_id,
            focus_paths=["compute.py"], context_format="compact-prefix",
        ), VERSIONS[2])
        reopened.indexer.reindex(project_id)
        hits = reopened.indexer.search(project_id, "compute")
        assert hits and all(hit["hash"] == hashlib.sha256(VERSIONS[2].encode()).hexdigest() for hit in hits)
        assert reopened.db.one("SELECT count(*) AS n FROM files")["n"] == 4
        assert reopened.db.one("SELECT count(*) AS n FROM file_search")["n"] == 4
        with reopened.db.connect() as connection:
            connection.execute("INSERT INTO file_search(file_search) VALUES('integrity-check')")
    finally:
        reopened.close()


def test_fresh_process_preload_handles_changed_deleted_and_newly_ignored_indexed_sources(
    approved_source,
):
    root, database, project_id = approved_source
    previous = (root / "compute.py").stat()
    (root / "compute.py").write_text(VERSIONS[2])
    os.utime(root / "compute.py", ns=(previous.st_atime_ns, previous.st_mtime_ns))
    (root / "removed.py").unlink()
    (root / ".gitignore").write_text("ignored.py\n")
    program = """
import json,sys
from memglide.service import Service
from memglide.integrations.preload import prepare_prompt
service=Service(sys.argv[1])
try:
    result={'root':service.db.project(sys.argv[2])['path'],'preparations':{}}
    for label,focus,support in [('changed',['compute.py'],[]),('deleted',['removed.py'],[]),
                                ('ignored',['ignored.py'],[]),('whole_bundle',['compute.py'],['ignored.py'])]:
        result['preparations'][label]=prepare_prompt(sys.argv[3],db_path=service.db.path,
            project_id=sys.argv[2],focus_paths=focus,support_paths=support,context_format='compact-prefix')
    print(json.dumps(result))
finally: service.close()
"""
    process = child(program, database, project_id, TASK)
    try:
        stdout, stderr = process.communicate(timeout=15)
    finally:
        if process.poll() is None:
            stop(process)
    assert process.returncode == 0, stderr
    result = json.loads(stdout)
    assert result["root"] == str(root)
    assert_complete(result["preparations"]["changed"], VERSIONS[2])
    for label in ("deleted", "ignored", "whole_bundle"):
        preparation = result["preparations"][label]
        assert preparation["mode"] == "passthrough"
        assert preparation["prompt"] == TASK and preparation["files"] == []
    assert result["preparations"]["ignored"]["reason"] == "source_excluded"
    assert result["preparations"]["whole_bundle"]["reason"] == "source_excluded"


def test_independent_service_processes_never_mix_source_hashes_during_concurrent_edits(
    approved_source, tmp_path,
):
    root, database, project_id = approved_source
    go = tmp_path / "go"
    program = """
import json,sys,time
from pathlib import Path
from memglide.service import Service
from memglide.integrations.preload import prepare_prompt
service=Service(sys.argv[1]); Path(sys.argv[3]).write_text('ready')
try:
    deadline=time.monotonic()+10
    while not Path(sys.argv[4]).exists():
        if time.monotonic()>deadline: raise AssertionError('start barrier expired')
        time.sleep(.005)
    observations=[]
    for _ in range(4):
        hits=service.indexer.search(sys.argv[2],'compute')
        preparation=prepare_prompt(sys.argv[5],db_path=service.db.path,project_id=sys.argv[2],
                                   focus_paths=['compute.py'],context_format='compact-prefix')
        observations.append({'hits':hits,'preparation':preparation})
    print(json.dumps(observations))
finally: service.close()
"""
    processes = [child(program, database, project_id, tmp_path / f"ready-{index}", go, TASK) for index in range(2)]
    try:
        for index, process in enumerate(processes):
            wait_for(tmp_path / f"ready-{index}", process)
        go.write_text("start")
        for index in range(30):
            temporary = root / ".git" / "atomic-replacement"
            temporary.write_text(VERSIONS[2 if index % 2 else 3])
            temporary.replace(root / "compute.py")
            time.sleep(0.003)
        temporary = root / ".git" / "atomic-replacement"
        temporary.write_text(VERSIONS[3])
        temporary.replace(root / "compute.py")
        outputs = [process.communicate(timeout=20) for process in processes]
        by_hash = {hashlib.sha256(source.encode()).hexdigest(): source for source in VERSIONS.values()}
        for process, (stdout, stderr) in zip(processes, outputs, strict=True):
            assert process.returncode == 0, stderr
            observations = json.loads(stdout)
            assert len(observations) == 4
            for observation in observations:
                for hit in observation["hits"]:
                    assert hit["current"] is True
                    assert hit["hash"] in by_hash
                    assert hit["snippet"] == by_hash[hit["hash"]].rstrip("\n")
                preparation = observation["preparation"]
                if preparation["mode"] == "preloaded":
                    assert_complete(preparation, by_hash[preparation["files"][0]["sha256"]])
                else:
                    assert preparation["prompt"] == TASK and preparation["files"] == []
        current = Service(database)
        try:
            hits = current.indexer.search(project_id, "compute")
            assert hits and all(hit["hash"] == hashlib.sha256(VERSIONS[3].encode()).hexdigest() for hit in hits)
            assert current.db.one("PRAGMA integrity_check")["integrity_check"] == "ok"
        finally:
            current.close()
    finally:
        for process in processes:
            if process.poll() is None:
                stop(process)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="POSIX FIFO source exclusion")
def test_indexed_fifo_source_declines_without_waiting_for_a_writer(approved_source):
    root, database, project_id = approved_source
    (root / "compute.py").unlink()
    os.mkfifo(root / "compute.py", 0o600)
    program = """
import json,sys
from memglide.integrations.preload import prepare_prompt
print(json.dumps(prepare_prompt(sys.argv[3],db_path=sys.argv[1],project_id=sys.argv[2],
                              focus_paths=['compute.py'],context_format='compact-prefix')))
"""
    process = child(program, database, project_id, TASK)
    try:
        stdout, stderr = process.communicate(timeout=8)
    finally:
        if process.poll() is None:
            stop(process)
    assert process.returncode == 0, stderr
    preparation = json.loads(stdout)
    assert preparation["mode"] == "passthrough" and preparation["reason"] == "source_unavailable"
    assert preparation["prompt"] == TASK and preparation["files"] == []
