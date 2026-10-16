"""Security regressions and SQLite guarantees shared by all transports."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from memglide.security import paths
from memglide.security.paths import read_source, safe_path, secret_path
from memglide.storage.database import DEFAULT_SETTINGS, Database, DomainError


@pytest.fixture
def database(tmp_path: Path) -> Database:
    return Database(tmp_path / "state" / "memglide.db")


def register(database: Database, path: Path, project_id: str = "project") -> str:
    database.execute(
        "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
        (project_id, str(path), project_id, 1.0),
    )
    return project_id


@pytest.mark.parametrize(
    "relative",
    ["../outside.py", "a/../../outside.py", "/etc/passwd", "a\\b.py", ""],
)
def test_source_rejects_traversal_and_absolute_paths(tmp_path: Path, relative: str) -> None:
    with pytest.raises(DomainError):
        safe_path(tmp_path, relative, must_exist=False)


def test_source_rejects_nul_path_with_domain_error(tmp_path: Path) -> None:
    with pytest.raises(DomainError):
        safe_path(tmp_path, "module\x00.py", must_exist=False)


@pytest.mark.parametrize(
    "relative",
    [
        ".env",
        ".env.production",
        "config/.env.local",
        ".ssh/id_rsa",
        ".aws/config",
        ".gnupg/keyring",
        "config/credentials",
        "credentials.json",
        "secrets.yaml",
        ".npmrc",
        ".pypirc",
        ".netrc",
        ".git-credentials",
        "cert.pem",
        "server.KEY",
        "identity.p12",
        "identity.pfx",
        "signing.keystore",
    ],
)
def test_secret_file_paths_are_denied(tmp_path: Path, relative: str) -> None:
    assert secret_path(relative)
    with pytest.raises(DomainError, match="Secret"):
        safe_path(tmp_path, relative, must_exist=False)


@pytest.mark.parametrize("link_to_directory", [False, True])
def test_symlinks_are_denied_even_when_target_remains_inside_root(
    tmp_path: Path,
    link_to_directory: bool,
) -> None:
    source = tmp_path / "actual"
    source.mkdir()
    (source / "module.py").write_text("answer = 42\n")
    link = tmp_path / "linked"
    link.symlink_to(source if link_to_directory else source / "module.py")
    relative = "linked/module.py" if link_to_directory else "linked"
    with pytest.raises(DomainError, match="Symlink"):
        read_source(tmp_path, relative)


@pytest.mark.parametrize("swap_directory", [False, True])
def test_source_open_cannot_follow_symlink_swapped_after_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    swap_directory: bool,
) -> None:
    root = tmp_path / "root"
    source_dir = root / "source"
    outside = tmp_path / "outside"
    source_dir.mkdir(parents=True)
    outside.mkdir()
    (source_dir / "module.py").write_text("inside = True\n")
    (outside / "module.py").write_text("outside_project_data = True\n")
    original = paths.safe_path

    def swap_after_validation(*args: object, **kwargs: object) -> Path:
        checked = original(*args, **kwargs)  # type: ignore[arg-type]
        if swap_directory:
            source_dir.rename(root / "old_source")
            source_dir.symlink_to(outside, target_is_directory=True)
        else:
            checked.unlink()
            checked.symlink_to(outside / "module.py")
        return checked

    monkeypatch.setattr(paths, "safe_path", swap_after_validation)
    try:
        content, _ = read_source(root, "source/module.py")
    except DomainError:
        return
    assert content == "inside = True\n", "Source open followed a symlink outside its approved root"


@pytest.mark.parametrize(
    "content",
    [
        "-----BEGIN PRIVATE KEY-----\nfixture\n-----END PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----\nfixture\n-----END RSA PRIVATE KEY-----",
        "token = 'ghp_" + "a" * 30 + "'",
        "key = 'AKIA" + "A" * 16 + "'",
        "api_key = 'sk-" + "a" * 24 + "'",
        'password = "fixture-password-value"',
        'access_token: "fixture-access-token"',
    ],
)
def test_detected_credentials_are_excluded(tmp_path: Path, content: str) -> None:
    (tmp_path / "config.py").write_text(content)
    with pytest.raises(DomainError, match="credentials"):
        read_source(tmp_path, "config.py")


@pytest.mark.parametrize("data", [b"binary\x00data", b"invalid\xffutf8", b"x" * 101])
def test_binary_invalid_utf8_and_oversize_sources_are_excluded(tmp_path: Path, data: bytes) -> None:
    (tmp_path / "module.py").write_bytes(data)
    with pytest.raises(DomainError):
        read_source(tmp_path, "module.py", max_size=100)


def test_source_hash_covers_exact_utf8_bytes_and_size_boundary(tmp_path: Path) -> None:
    data = "# π and café\nanswer = 42\n".encode()
    (tmp_path / "module.py").write_bytes(data)
    content, digest = read_source(tmp_path, "module.py", max_size=len(data))
    assert content.encode() == data
    assert digest == hashlib.sha256(data).hexdigest()
    with pytest.raises(DomainError):
        read_source(tmp_path, "module.py", max_size=len(data) - 1)
    with pytest.raises(DomainError):
        read_source(tmp_path, ".")


def test_database_reopening_preserves_data_settings_and_initial_migration(
    database: Database,
    tmp_path: Path,
) -> None:
    register(database, tmp_path)
    database.execute("UPDATE settings SET value=? WHERE key='theme'", (json.dumps("light"),))
    reopened = Database(database.path)
    assert reopened.project("project")["path"] == str(tmp_path)
    assert reopened.settings()["theme"] == "light"
    assert set(reopened.settings()) == set(DEFAULT_SETTINGS)
    assert [row["version"] for row in reopened.rows("SELECT version FROM schema_migrations")] == [1]
    with reopened.connect() as conn:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert conn.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_database_file_and_new_storage_directory_are_private(database: Database) -> None:
    if os.name != "posix":
        pytest.skip("POSIX permission bits")
    assert stat.S_IMODE(database.path.stat().st_mode) == 0o600
    assert stat.S_IMODE(database.path.parent.stat().st_mode) == 0o700


def test_every_connection_enforces_foreign_keys(database: Database) -> None:
    for _ in range(2):
        with pytest.raises(sqlite3.IntegrityError):
            database.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?)",
                ("orphan", "unknown-project", None, "test", "{}", 1.0),
            )
    assert database.rows("SELECT * FROM events") == []


def test_related_writes_roll_back_on_failure(database: Database, tmp_path: Path) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        with database.connect() as conn:
            conn.execute(
                "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
                ("rolled-back", str(tmp_path), "fixture", 1.0),
            )
            conn.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?)",
                ("orphan", "unknown-project", None, "test", "{}", 1.0),
            )
    assert database.one("SELECT id FROM projects WHERE id='rolled-back'") is None


def test_project_deletion_cascades_session_task_data_without_deleting_sources(
    database: Database,
    tmp_path: Path,
) -> None:
    register(database, tmp_path)
    source = tmp_path / "source.py"
    source.write_text("keep_source = True\n")
    with database.connect() as conn:
        conn.execute(
            "INSERT INTO sessions VALUES(?,?,?,?,?,?,?,NULL)",
            ("session", "project", "task", 1.0, 1.0, 2.0, 3.0),
        )
        conn.execute(
            "INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?)",
            ("memory", "session", "observation", "fixture", "test", 1.0, 1.0, 0, "hash"),
        )
        conn.execute("INSERT INTO memory_sources VALUES(?,?,?)", ("memory", "source.py", "hash"))
        conn.execute(
            "INSERT INTO retrievals VALUES(?,?,?,?,?,?,?,?,?)",
            ("retrieval", "session", "project", "query", 1, 1000, 10, 1.0, "{}"),
        )
        conn.execute("INSERT INTO passports VALUES(?,?,?)", ("retrieval", "session", "{}"))
        conn.execute(
            "INSERT INTO events VALUES(?,?,?,?,?,?)",
            ("event", "project", "session", "fixture", "{}", 1.0),
        )
    database.execute("DELETE FROM projects WHERE id=?", ("project",))
    for table in ("sessions", "memories", "memory_sources", "retrievals", "passports", "events"):
        assert database.rows(f"SELECT * FROM {table}") == []
    assert source.read_text() == "keep_source = True\n"


def test_separate_database_instances_can_initialize_and_write_concurrently(
    database: Database,
    tmp_path: Path,
) -> None:
    register(database, tmp_path)

    def write_events(worker: int) -> None:
        instance = Database(database.path)
        for number in range(10):
            instance.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?)",
                (f"{worker}-{number}", "project", None, "test", "{}", 1.0),
            )

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(write_events, range(4)))
    assert database.one("SELECT count(*) AS count FROM events")["count"] == 40
    assert database.one("SELECT count(*) AS count FROM schema_migrations")["count"] == 1
    with database.connect() as conn:
        assert conn.execute("PRAGMA quick_check").fetchone()[0] == "ok"


def test_wal_reader_observes_committed_snapshot_during_pending_write(
    database: Database,
    tmp_path: Path,
) -> None:
    register(database, tmp_path)
    with database.connect() as writer:
        writer.execute("UPDATE projects SET name='pending' WHERE id='project'")
        assert database.project("project")["name"] == "project"
    assert database.project("project")["name"] == "pending"


def test_indexing_does_not_execute_repository_configured_git_fsmonitor(
    database: Database,
    tmp_path: Path,
) -> None:
    from memglide.core.indexer import Indexer

    repo = tmp_path / "untrusted_repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    marker = repo / "hook-was-executed"
    hook = repo / "fsmonitor-hook.sh"
    hook.write_text('#!/bin/sh\n: > "$PWD/hook-was-executed"\nprintf "\\000"\n')
    hook.chmod(0o700)
    subprocess.run(["git", "-C", str(repo), "config", "core.fsmonitor", str(hook)], check=True)
    (repo / "module.py").write_text("answer = 42\n")
    Indexer(database).add_project(str(repo))
    assert not marker.exists(), "Reading Git state executed a repository-controlled fsmonitor hook"


@pytest.fixture
def api_client(database: Database):
    from fastapi.testclient import TestClient

    from memglide.api.app import create_app
    from memglide.service import Service

    service = Service(database.path)
    with TestClient(create_app(service), base_url="http://localhost:4318") as client:
        yield client


@pytest.mark.parametrize("host", ["localhost:4318", "127.0.0.1:4318", "[::1]:4318"])
def test_api_accepts_loopback_hosts(api_client, host: str) -> None:
    response = api_client.get("/api/health", headers={"host": host})
    assert response.status_code == 200
    assert response.json()["local_only"] is True


@pytest.mark.parametrize(
    "host",
    [
        "attacker.example",
        "localhost.attacker.example",
        "127.0.0.1.attacker.example",
        "0.0.0.0:4318",
        "192.168.1.10:4318",
        "localhost:0",
        "localhost:99999",
    ],
)
def test_api_rejects_rebinding_hosts_even_with_forwarded_loopback_host(
    api_client, host: str
) -> None:
    response = api_client.get(
        "/api/health",
        headers={
            "host": host,
            "x-forwarded-host": "localhost:4318",
            "x-forwarded-for": "127.0.0.1",
        },
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_host"


@pytest.mark.parametrize(
    "origin",
    [
        "https://attacker.example",
        "http://localhost:9999",
        "https://localhost:4318",
        "null",
        "http://127.0.0.1:4318",
    ],
)
def test_api_rejects_cross_origin_reads_and_mutations(api_client, origin: str) -> None:
    headers = {"origin": origin, "x-memglide-request": "1"}
    for method, route, data in (
        ("GET", "/api/health", None),
        ("PUT", "/api/settings", {"theme": "light"}),
    ):
        response = api_client.request(method, route, headers=headers, json=data)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden_origin"


def test_api_mutations_require_custom_header_and_same_origin_when_present(api_client) -> None:
    forbidden = api_client.put("/api/settings", json={"theme": "light"})
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "missing_request_header"
    assert api_client.get("/api/settings").json()["theme"] == "dark"
    accepted = api_client.put(
        "/api/settings",
        json={"theme": "light"},
        headers={
            "origin": "http://localhost:4318",
            "x-memglide-request": "1",
        },
    )
    assert accepted.status_code == 200
    assert accepted.json()["theme"] == "light"
    # Non-browser clients have no Origin, but must explicitly opt into state changes.
    native = api_client.put(
        "/api/settings", json={"theme": "dark"}, headers={"x-memglide-request": "1"}
    )
    assert native.status_code == 200


def test_api_validation_errors_never_echo_submitted_sensitive_input(api_client) -> None:
    submitted = "sensitive-fixture-should-not-be-echoed"
    response = api_client.post(
        "/api/sessions",
        headers={"x-memglide-request": "1"},
        json={"project_id": {"secret": submitted}},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert submitted not in response.text


def test_real_service_keeps_same_named_sources_and_symbols_in_their_approved_project(
    database: Database,
    tmp_path: Path,
) -> None:
    from memglide.service import Service

    service = Service(database.path)
    projects = []
    for name in ("alpha", "beta"):
        repo = tmp_path / name
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "auth.py").write_text(f'def verify():\n    return "{name}_evidence"\n')
        projects.append(service.indexer.add_project(str(repo)))
    try:
        alpha, beta = projects
        alpha_results = service.indexer.search(alpha["id"], "verify")
        beta_results = service.indexer.search(beta["id"], "verify")
        assert "alpha_evidence" in json.dumps(alpha_results)
        assert "beta_evidence" not in json.dumps(alpha_results)
        assert "beta_evidence" in json.dumps(beta_results)
        beta_symbol = next(r for r in beta_results if r["kind"] != "file")
        for lookup in (service.indexer.get_symbol, service.indexer.dependencies):
            with pytest.raises(DomainError) as error:
                lookup(alpha["id"], beta_symbol["id"])
            assert error.value.status == 404
        with pytest.raises(DomainError) as error:
            service.indexer.search("unregistered-project", "verify")
        assert error.value.status == 404
    finally:
        service.close()


def test_api_rejects_foreign_project_session_and_retrieval_identifiers(
    api_client,
    tmp_path: Path,
) -> None:
    service = api_client.app.state.service
    sessions = []
    projects = []
    for name in ("alpha", "beta"):
        repo = tmp_path / name
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "auth.py").write_text(f'def verify():\n    return "{name}_evidence"\n')
        project = service.indexer.add_project(str(repo))
        projects.append(project)
        sessions.append(service.memory.start_session(project["id"], "verify"))
    result = service.context.get_context(sessions[0]["id"], "verify", level=2)
    assert "alpha_evidence" in json.dumps(result)
    assert "beta_evidence" not in json.dumps(result)
    retrieval_id = result["retrieval_id"]
    foreign_id = sessions[1]["id"]
    passport = api_client.get(
        f"/api/context/{retrieval_id}/passport", params={"session_id": foreign_id}
    )
    assert passport.status_code == 404
    expanded = api_client.post(
        f"/api/context/{retrieval_id}/expand",
        json={"session_id": foreign_id},
        headers={"x-memglide-request": "1"},
    )
    assert expanded.status_code == 404
    timeline = api_client.get(
        "/api/events",
        params={
            "project_id": projects[0]["id"],
            "session_id": foreign_id,
        },
    )
    assert timeline.status_code == 404


@pytest.mark.parametrize(
    "name,content",
    [
        (".envrc", "export EXAMPLE=example-value"),
        ("config.yaml", "api_key: example-credential-value\n"),
        ("config.yaml", "password: example-password-value\n"),
    ],
)
def test_additional_credential_exclusions(tmp_path, name, content):
    (tmp_path / name).write_text(content)
    with pytest.raises(DomainError):
        read_source(tmp_path, name)
