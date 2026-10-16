from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from memglide.core.indexer import Indexer
from memglide.core.parsing import ParsedFile, parse_source, parse_sources
from memglide.core.watcher import RepositoryWatcher
from memglide.storage.database import Database, DomainError


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, text=True, capture_output=True
    ).stdout.strip()


@pytest.fixture
def repository(tmp_path: Path) -> tuple[Path, Indexer, Database]:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q")
    (root / "auth.py").write_text(
        'def verify_jwt(token: str) -> bool:\n    return token == "valid"\n'
    )
    (root / "app.py").write_text(
        "from auth import verify_jwt as verify\n\ndef authenticate_user(token):\n    return verify(token)\n"
    )
    db = Database(tmp_path / "state" / "memglide.db")
    return root, Indexer(db), db


def test_python_ast_definitions_and_shadowing() -> None:
    parsed = parse_source(
        "app.py",
        """__all__ = ['Auth']
class Auth:
    def verify(self, token: str) -> bool:
        return verify_jwt(token)
def helper(verify_jwt):
    return verify_jwt('sample')
""",
    )
    assert parsed.structural and not parsed.error
    symbols = {s["qualified_name"]: s for s in parsed.symbols}
    assert symbols["Auth"]["exported"]
    assert symbols["Auth.verify"]["kind"] == "method"
    assert symbols["Auth.verify"]["signature"] == "def verify(self, token: str) -> bool:"
    assert not symbols["helper"]["exported"]
    assert parsed.dependencies[-1]["kind"] == "call_unresolved"


@pytest.mark.parametrize("extension", ["ts", "tsx", "js"])
def test_tree_sitter_symbols_imports_exports(extension: str) -> None:
    annotation = ": string" if extension != "js" else ""
    source = f"""import {{ verify as verifyJwt }} from './auth';
export function authenticate(token{annotation}) {{ return verifyJwt(token); }}
export class Auth {{ verify(token{annotation}) {{ return authenticate(token); }} }}
export const helper = (value{annotation}) => value;
"""
    if extension == "tsx":
        source += "export const Panel = () => <section>Authentication</section>;\n"
    parsed = parse_source(f"app.{extension}", source)
    assert parsed.structural and parsed.error is None
    names = {s["qualified_name"]: s for s in parsed.symbols}
    assert {"authenticate", "Auth", "Auth.verify", "helper"} <= names.keys()
    assert names["authenticate"]["exported"]
    assert names["helper"]["exported"]
    assert any(
        d["reference"] == "verifyJwt" and d["source_symbol"] == "authenticate"
        for d in parsed.dependencies
    )


def test_registration_requires_explicit_canonical_git_root(
    repository: tuple[Path, Indexer, Database], tmp_path: Path
) -> None:
    root, indexer, _ = repository
    with pytest.raises(DomainError, match="Git repository"):
        indexer.add_project(str(tmp_path))
    (root / "sub").mkdir()
    with pytest.raises(DomainError, match="root"):
        indexer.add_project(str(root / "sub"))
    project = indexer.add_project(str(root))
    assert indexer.add_project(str(root))["id"] == project["id"]
    assert len(indexer.list_projects()) == 1
    assert project["index_stats"]["file_count"] == 2
    indexer.remove_project(project["id"])
    assert not indexer.list_projects()
    assert (root / "auth.py").is_file()
    with pytest.raises(DomainError, match="unregistered"):
        indexer.search(project["id"], "verify_jwt")


def test_search_current_source_stable_ids_and_incremental_changes(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, db = repository
    project = indexer.add_project(str(root))
    pid = project["id"]
    result = indexer.search(pid, "verify_jwt")
    assert result[0]["name"] == "verify_jwt"
    assert result[0]["reason"].startswith("exact symbol match")
    assert indexer.search(pid, "verify_jwt") == result
    stable = result[0]["id"]
    before = db.one("SELECT indexed_at FROM files WHERE project_id=? AND path='app.py'", (pid,))
    (root / "auth.py").write_text(
        "\n\ndef verify_jwt(token: str) -> bool:\n    return bool(token)\n"
    )
    stats = indexer.reindex(pid)
    assert stats["indexed"] == 1 and stats["unchanged"] == 1
    assert (
        db.one("SELECT indexed_at FROM files WHERE project_id=? AND path='app.py'", (pid,))
        == before
    )
    current = indexer.get_symbol(pid, stable)
    assert current["id"] == stable and current["start_line"] == 3
    assert "bool(token)" in current["snippet"]
    assert current["hash"] != result[0]["hash"]
    full = indexer.reindex(pid, full=True)
    assert full["indexed"] == 2
    assert indexer.get_symbol(pid, "verify_jwt")["id"] == stable
    (root / "auth.py").rename(root / "tokens.py")
    stats = indexer.reindex(pid)
    assert stats["deleted"] == 1 and stats["indexed"] == 1
    assert indexer.get_symbol(pid, "verify_jwt")["path"] == "tokens.py"
    imports = indexer.dependencies(pid, "app.py")
    assert all(not d["resolved"] for d in imports)


def test_configurable_weights_change_ranking_deterministically(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, db = repository
    pid = indexer.add_project(str(root))["id"]
    assert indexer.search(pid, "verify_jwt")[0]["kind"] == "function"
    weights = {
        "exact_symbol": 120.0,
        "identifier": 35.0,
        "symbol_path": 45.0,
        "signature": 8.0,
        "file_path": 70.0,
        "path_terms": 30.0,
        "full_text": 1000.0,
        "task_overlap": 0.3,
    }
    db.execute(
        "INSERT OR REPLACE INTO settings VALUES('retrieval_weights',?)", (json.dumps(weights),)
    )
    result = indexer.search(pid, "verify_jwt")
    assert result[0]["kind"] == "file"
    assert result == indexer.search(pid, "verify_jwt")


def test_search_excerpts_are_bounded_and_explicit_full_source_remains_available(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    content = "authentication implementation evidence\n" * 2000 + "final evidence marker\n"
    (root / "large.txt").write_text(content)
    pid = indexer.add_project(str(root))["id"]
    match = next(row for row in indexer.search(pid, "authentication") if row["path"] == "large.txt")
    assert len(match["snippet"]) <= 1600
    assert "source" not in match
    assert match["snippet_truncated"] and "truncated" in match["reason"]
    assert match["snippet_start_line"] == 1
    assert match["snippet_end_line"] < match["end_line"]
    assert match["end_line"] == len(content.splitlines())
    assert match["full_source_available"]
    complete = indexer.get_symbol(pid, match["full_source_reference"])
    assert complete["snippet"] == content.rstrip("\n")
    assert not complete["snippet_truncated"] and "source" not in complete
    assert complete["snippet_end_line"] == complete["end_line"]


def test_index_resource_limits_report_partial_index(
    repository: tuple[Path, Indexer, Database], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, indexer, _ = repository
    monkeypatch.setattr("memglide.core.indexer.MAX_INDEXED_FILES", 1)
    project = indexer.add_project(str(root))
    stats = project["index_stats"]
    assert stats["file_count"] == 1
    assert stats["partial"]
    assert "resource limit" in stats["errors"][0]["error"]


def test_reindex_rejects_replaced_root_symlink(
    repository: tuple[Path, Indexer, Database], tmp_path: Path
) -> None:
    root, indexer, _ = repository
    pid = indexer.add_project(str(root))["id"]
    replaced = tmp_path / "moved"
    root.rename(replaced)
    root.symlink_to(replaced, target_is_directory=True)
    with pytest.raises(DomainError, match="canonical"):
        indexer.reindex(pid)


def test_registration_rejects_nul_path(repository: tuple[Path, Indexer, Database]) -> None:
    _, indexer, _ = repository
    with pytest.raises(DomainError, match="path"):
        indexer.add_project("invalid\x00path")


def test_resolved_python_calls_and_imports_not_shadowed(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    (root / "shadow.py").write_text(
        'from auth import verify_jwt\ndef callback(verify_jwt):\n    return verify_jwt("sample")\n'
    )
    pid = indexer.add_project(str(root))["id"]
    incoming = indexer.dependencies(pid, "verify_jwt", "incoming")
    assert any(
        d["kind"] == "call" and d["source_file"] == "app.py" and d["resolved"] for d in incoming
    )
    shadow = indexer.dependencies(pid, "callback", "outgoing")
    assert len(shadow) == 1 and not shadow[0]["resolved"]
    assert indexer.search(pid, "Which functions call verify_jwt?")[0]["name"] == "authenticate_user"


def test_typescript_graph_and_unknown_dynamic_relationships(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    (root / "auth.ts").write_text("export function verifyJwt(token: string) { return !!token; }\n")
    (root / "view.tsx").write_text(
        "import { verifyJwt as verify } from './auth';\nexport function AuthPanel() { verify('sample'); return <div />; }\nexport function dynamic(obj: any) { return obj.verify(); }\n"
    )
    pid = indexer.add_project(str(root))["id"]
    callers = indexer.dependencies(pid, "verifyJwt", "incoming")
    assert any(
        d["source_file"] == "view.tsx" and d["kind"] == "call" and d["resolved"] for d in callers
    )
    unknown = indexer.dependencies(pid, "dynamic", "outgoing")
    assert unknown[0]["reference"] == "obj.verify" and not unknown[0]["resolved"]


def test_ambiguous_or_reassigned_imports_never_invent_calls(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    (root / "other.py").write_text("def verify_jwt(token): return False\n")
    (root / "ambiguous.py").write_text(
        "from auth import verify_jwt\nfrom other import verify_jwt\ndef ambiguous(token): return verify_jwt(token)\n"
    )
    (root / "reassigned.py").write_text(
        "from auth import verify_jwt\nverify_jwt = object()\ndef reassigned(token): return verify_jwt(token)\n"
    )
    package = root / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("# package\n")
    (package / "auth.py").write_text("def verify_jwt(token): return True\n")
    (root / "dotted.py").write_text(
        "import pkg.auth\ndef dotted(token): return pkg.verify_jwt(token)\n"
    )
    pid = indexer.add_project(str(root))["id"]
    for name in ("ambiguous", "reassigned", "dotted"):
        edges = indexer.dependencies(pid, name, "outgoing")
        assert edges and all(not edge["resolved"] for edge in edges)


def test_javascript_named_default_export_resolves_explicitly(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    (root / "default.js").write_text(
        "export default function validate(token) { return !!token; }\n"
    )
    (root / "default_user.js").write_text(
        "import check from './default';\nexport function useDefault(token) { return check(token); }\n"
    )
    pid = indexer.add_project(str(root))["id"]
    edges = indexer.dependencies(pid, "useDefault", "outgoing")
    assert len(edges) == 1 and edges[0]["resolved"]
    assert edges[0]["target_file"] == "default.js"


def test_native_sources_use_one_isolated_batch_and_none_when_unchanged(
    repository: tuple[Path, Indexer, Database],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, indexer, _ = repository
    for number in range(12):
        (root / f"module{number}.ts").write_text(
            f"export function example{number}() {{ return true; }}\n"
        )
    original = subprocess.run
    worker_calls = []

    def spy(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "--worker" in command:
            worker_calls.append(command)
            assert "-I" in command and Path(command[-2]).is_absolute()
        return original(command, **kwargs)  # type: ignore[call-overload,no-any-return]

    monkeypatch.setattr("memglide.core.parsing.subprocess.run", spy)
    pid = indexer.add_project(str(root))["id"]
    assert len(worker_calls) == 1
    assert indexer.get_symbol(pid, "example11")["structural"]
    assert indexer.reindex(pid)["indexed"] == 0
    assert len(worker_calls) == 1


@pytest.mark.parametrize("failure", ["native_exit", "timeout"])
def test_worker_failure_retains_completed_results_and_explicit_text_fallback(
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    completed = (
        json.dumps(
            [
                "a.ts",
                {
                    "language": "typescript",
                    "structural": True,
                    "symbols": [],
                    "dependencies": [],
                    "error": None,
                },
            ]
        )
        + "\n"
    )

    def fail(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, 30, output=completed.encode())
        return subprocess.CompletedProcess(command, -11, stdout=completed, stderr="native failure")

    monkeypatch.setattr("memglide.core.parsing.subprocess.run", fail)
    results = parse_sources({"a.ts": "export {};", "b.ts": "export {};"})
    assert results["a.ts"].structural and results["a.ts"].error is None
    assert not results["b.ts"].structural and not results["b.ts"].symbols
    assert "structural evidence unavailable" in str(results["b.ts"].error)


def test_parser_recursion_failure_falls_back_to_text(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(language: str, source: str) -> ParsedFile:
        raise RecursionError("fixture parser depth limit")

    monkeypatch.setattr("memglide.core.parsing._tree_sitter", fail)
    result = parse_source("deep.ts", "export {};")
    assert not result.structural and not result.symbols
    assert "parser limits" in str(result.error)


def test_real_complex_frontend_tsx_native_regression_and_indexing(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    source_root = Path(__file__).resolve().parents[1] / "frontend" / "src"
    shutil.copytree(source_root, root / "frontend")
    # These actual nested React components reproduced nondeterministic native
    # crashes under tree-sitter 0.26.0; assert the pinned binding in a subprocess.
    program = """from pathlib import Path
from memglide.core.parsing import parse_source
import sys
for _ in range(3):
    for name in ('components/ui.tsx', 'screens/Memory.tsx', 'screens/Passport.tsx', 'screens/Settings.tsx'):
        path = Path(sys.argv[1]) / name
        parsed = parse_source(str(path), path.read_text())
        assert parsed.structural and parsed.symbols and not parsed.error, (name, parsed.error)
"""
    check = subprocess.run(
        [sys.executable, "-X", "faulthandler", "-c", program, str(source_root)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert check.returncode == 0, check.stderr
    project = indexer.add_project(str(root))
    assert project["index_stats"]["languages"]["tsx"] >= 10
    for symbol in ("MemoryScreen", "PassportScreen", "SettingsScreen"):
        candidate = indexer.get_symbol(project["id"], symbol)
        assert candidate["structural"] and "function " + symbol in candidate["snippet"]


def test_ignore_rules_secrets_symlinks_binary_and_file_limits(
    repository: tuple[Path, Indexer, Database], tmp_path: Path
) -> None:
    root, indexer, db = repository
    (root / ".gitignore").write_text("ignored.py\n*.log\n")
    (root / ".memglideignore").write_text("private/\n")
    (root / "ignored.py").write_text("def ignored(): pass\n")
    (root / "private").mkdir()
    (root / "private" / "data.py").write_text("sensitive = True\n")
    (root / "nested").mkdir()
    (root / "nested" / ".gitignore").write_text("local.py\n")
    (root / "nested" / "local.py").write_text("def local(): pass\n")
    (root / ".env.example").write_text("EXAMPLE=value\n")
    (root / "credentials.json").write_text('{"fixture":"value"}')
    (root / "embedded.py").write_text('api_key = "fixture-value-long-enough"\n')
    (root / "binary.dat").write_bytes(b"x\x00x")
    (root / "big.txt").write_text("x" * 600000)
    outside = tmp_path / "outside.py"
    outside.write_text("def outside(): pass\n")
    (root / "link.py").symlink_to(outside)
    (root / "linked_dir").symlink_to(tmp_path, target_is_directory=True)
    project = indexer.add_project(str(root))
    paths = {
        r["path"] for r in db.rows("SELECT path FROM files WHERE project_id=?", (project["id"],))
    }
    assert paths == {"auth.py", "app.py", ".gitignore", ".memglideignore", "nested/.gitignore"}
    reasons = {r["path"]: r["reason"] for r in project["index_stats"]["ignored_files"]}
    assert reasons["link.py"] == "symlink"
    assert reasons["ignored.py"] == "ignore rule"
    assert reasons["nested/local.py"] == "ignore rule"
    assert "credentials" in reasons["embedded.py"]


def test_unsupported_source_and_parse_failures_are_honest(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    (root / "guide.rs").write_text("// authentication implementation guide\nfn auth() {}\n")
    (root / "broken.py").write_text("def invalid(:\n")
    pid = indexer.add_project(str(root))["id"]
    rust = next(r for r in indexer.search(pid, "authentication") if r["path"] == "guide.rs")
    assert rust["language"] == "text" and not rust["structural"]
    stats = indexer.reindex(pid)
    assert any(e["path"] == "broken.py" for e in stats["errors"])


def test_branch_switch_updates_hashes_and_git_state(
    repository: tuple[Path, Indexer, Database],
) -> None:
    root, indexer, _ = repository
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "add", ".")
    git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.test",
        "commit",
        "-qm",
        "initial",
    )
    original_branch = git(root, "branch", "--show-current")
    git(root, "checkout", "-qb", "changed")
    (root / "auth.py").write_text("def verify_jwt(token):\n    return False\n")
    git(root, "add", ".")
    git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.test",
        "commit",
        "-qm",
        "change",
    )
    pid = indexer.add_project(str(root))["id"]
    initial = indexer.get_symbol(pid, "verify_jwt")
    git(root, "checkout", "-q", original_branch)
    stats = indexer.reindex(pid)
    assert stats["branch"] == original_branch and not stats["git_state"]["dirty"]
    assert stats["indexed"] == 1
    assert indexer.get_symbol(pid, "verify_jwt")["hash"] != initial["hash"]


def test_change_invalidates_memory_and_passport(repository: tuple[Path, Indexer, Database]) -> None:
    root, indexer, db = repository
    pid = indexer.add_project(str(root))["id"]
    digest = indexer.get_symbol(pid, "verify_jwt")["hash"]
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO sessions VALUES('s',?,'task',0,0,99999999999,99999999999,NULL)", (pid,)
        )
        conn.execute(
            "INSERT INTO memories VALUES('m','s','observation','found','fixture',0,0,0,'fingerprint')"
        )
        conn.execute("INSERT INTO memory_sources VALUES('m','auth.py',?)", (digest,))
        conn.execute("INSERT INTO retrievals VALUES('r','s',?,'auth',1,4000,10,0,'{}')", (pid,))
        conn.execute(
            "INSERT INTO passports VALUES('r','s',?)",
            (json.dumps({"status": "Current", "selected_files": ["auth.py"]}),),
        )
    (root / "auth.py").unlink()
    indexer.reindex(pid)
    assert db.one("SELECT stale FROM memories WHERE id='m'")["stale"] == 1  # type: ignore[index]
    passport = json.loads(db.one("SELECT data FROM passports WHERE retrieval_id='r'")["data"])  # type: ignore[index]
    assert passport["status"] == "Stale"
    assert passport["stale_files"] == ["auth.py"]


def test_watcher_updates_and_respects_settings(repository: tuple[Path, Indexer, Database]) -> None:
    root, indexer, db = repository
    pid = indexer.add_project(str(root))["id"]
    watcher = RepositoryWatcher(db, indexer, debounce=0.05, poll_interval=0.2)
    watcher.start()
    try:
        (root / "new.py").write_text("def newly_added(): return True\n")
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if db.one("SELECT id FROM symbols WHERE project_id=? AND name='newly_added'", (pid,)):
                break
            time.sleep(0.05)
        assert db.one("SELECT id FROM symbols WHERE project_id=? AND name='newly_added'", (pid,))
        db.execute("UPDATE settings SET value='false' WHERE key='watch_enabled'")
        time.sleep(0.3)
        (root / "not_watched.py").write_text("def not_watched(): pass\n")
        time.sleep(0.5)
        assert not db.one(
            "SELECT id FROM symbols WHERE project_id=? AND name='not_watched'", (pid,)
        )
    finally:
        watcher.stop()
    assert not watcher.running
