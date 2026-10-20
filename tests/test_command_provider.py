"""Provider provenance and stale-input guards, using synthetic public checks."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations import command_provider as providers
from memglide.storage.database import Database


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "feature.py").write_text("def feature(value):\n    return value\n")
    (root / "test_feature.py").write_text("from feature import feature\ndef test_feature():\n    assert feature(1) == 1\n")
    database = Database(tmp_path / "state.db")
    project_id = Indexer(database).add_project(str(root))["id"]
    return root, database, project_id


def verify(project, tmp_path, **kwargs):
    return providers.verify_public_commands([{"name": "public tests", "kind": "tests",
        "argv": [sys.executable, "-c", "print('1 passed')"]}], project_id=project[2],
        db_path=project[1].path, receipt_path=tmp_path / "provider.json", **kwargs)


def test_hash_pin_required_and_canonical_receipt_cannot_be_replaced(project, tmp_path):
    verified = verify(project, tmp_path)
    path = tmp_path / "provider.json"
    with pytest.raises(providers.ProviderUnavailable, match="trusted hash"):
        providers.load_verified_provider(path, "0" * 64)
    loaded = providers.load_verified_provider(path, verified.trusted_sha256)
    manifest = loaded.current_manifest(project[2], project[1].path, ("feature.py",))
    assert manifest["commands"][0]["baseline"]["tests"] == 1
    value = json.loads(path.read_bytes())
    value["commands"][0]["baseline"]["tests"] = 100
    path.write_bytes(providers.canonical(value) + b"\n")
    with pytest.raises(providers.ProviderUnavailable, match="trusted hash"):
        providers.load_verified_provider(path, verified.trusted_sha256)


def test_direct_mutation_of_pinned_provider_is_detected(project, tmp_path):
    verified = verify(project, tmp_path)
    verified.receipt["commands"][0]["argv"][-1] = "print('99 passed')"
    with pytest.raises(providers.ProviderUnavailable, match="pinning"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))


@pytest.mark.parametrize("relative", ["feature.py", "test_feature.py"])
def test_changed_bound_source_or_test_is_stale(project, tmp_path, relative):
    verified = verify(project, tmp_path)
    (project[0] / relative).write_text("# changed input\n")
    with pytest.raises(providers.ProviderUnavailable, match="stale"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))


def test_explicit_tool_file_change_is_stale(project, tmp_path):
    tool = tmp_path / "explicit-tool.cfg"
    tool.write_text("version 1")
    verified = verify(project, tmp_path, tool_files=(str(tool),))
    tool.write_text("version 2")
    with pytest.raises(providers.ProviderUnavailable, match="tool binding"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))


def test_policy_change_cannot_reuse_verification(project, tmp_path):
    verified = verify(project, tmp_path)
    (project[0] / ".gitignore").write_text("# new ignore policy\n")
    with pytest.raises(providers.ProviderUnavailable, match="stale"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))


def test_nonverification_manifest_is_never_accepted_as_provider(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_bytes(providers.canonical({"commands": [{"argv": ["true"], "baseline": {"exit_code": 0}}]}) + b"\n")
    with pytest.raises(providers.ProviderUnavailable, match="Unsupported"):
        providers.load_verified_provider(path, hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.mark.parametrize("code", ["pass", "print('0 passed')", "print('1 failed')", "raise SystemExit(5)"])
def test_failed_or_zero_evidence_verification_never_writes_receipt(project, tmp_path, code):
    target = tmp_path / "bad.json"
    with pytest.raises(providers.ProviderUnavailable, match="did not pass"):
        providers.verify_public_commands([{"name": "bad", "argv": [sys.executable, "-c", code]}],
            project_id=project[2], db_path=project[1].path, receipt_path=target)
    assert not target.exists()


def test_checks_changing_bound_files_are_rejected(project, tmp_path):
    target = tmp_path / "bad.json"
    with pytest.raises(providers.ProviderUnavailable, match="changed bound"):
        providers.verify_public_commands([{"name": "mutating", "argv": [sys.executable, "-c",
            "from pathlib import Path;Path('feature.py').write_text('# modified');print('1 passed')"]}],
            project_id=project[2], db_path=project[1].path, receipt_path=target)
    assert not target.exists()


def test_verifier_requires_external_receipt_and_atomic_commands(project):
    with pytest.raises(ValueError, match="outside"):
        providers.verify_public_commands([{"argv": [sys.executable, "-c", "print('1 passed')"]}],
            project_id=project[2], db_path=project[1].path, receipt_path=project[0] / "forged.json")
    with pytest.raises(ValueError, match="shell"):
        providers.verify_public_commands([{"argv": ["bash", "-c", "false; true"]}],
            project_id=project[2], db_path=project[1].path, receipt_path=project[0] / "forged.json")


def test_receipt_symlink_and_noncanonical_json_rejected(project, tmp_path):
    verified = verify(project, tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(tmp_path / "provider.json")
    with pytest.raises(providers.ProviderUnavailable, match="nonsymlink"):
        providers.load_verified_provider(link, verified.trusted_sha256)
    path = tmp_path / "provider.json"
    path.write_text(json.dumps(verified.receipt, indent=2))
    with pytest.raises(providers.ProviderUnavailable, match="canonical"):
        providers.load_verified_provider(path, hashlib.sha256(path.read_bytes()).hexdigest())


def test_receipt_fifo_and_tool_fifo_fail_without_blocking(tmp_path):
    fifo = tmp_path / "named-pipe"
    os.mkfifo(fifo)
    started = time.monotonic()
    with pytest.raises(providers.ProviderUnavailable, match="regular"):
        providers.load_verified_provider(fifo, "0" * 64)
    with pytest.raises(providers.ProviderUnavailable, match="regular"):
        providers._tool(str(fifo))
    assert time.monotonic() - started < 1


def test_receipt_symlink_ancestor_never_reads_or_writes(project, tmp_path):
    verified = verify(project, tmp_path)
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(providers.ProviderUnavailable, match="ancestors"):
        providers.load_verified_provider(alias / "provider.json", verified.trusted_sha256)
    with pytest.raises(providers.ProviderUnavailable, match="ancestors"):
        providers._write_receipt(alias / "no-write.json", b"{}\n", project[0])
    assert not (tmp_path / "no-write.json").exists()


def test_external_looking_symlink_cannot_route_receipt_writer_into_project(project, tmp_path):
    alias = tmp_path / "external-looking"
    alias.symlink_to(project[0], target_is_directory=True)
    with pytest.raises(ValueError, match="outside"):
        providers._write_receipt(alias / "forged.json", b"{}\n", project[0])
    assert not (project[0] / "forged.json").exists()


def test_receipt_write_is_exclusive_and_private(project, tmp_path):
    path = tmp_path / "fresh-parent/receipt.json"
    providers._write_receipt(path, b"{}\n", project[0])
    assert path.read_bytes() == b"{}\n"
    assert path.stat().st_mode & 0o077 == 0
    with pytest.raises(providers.ProviderUnavailable):
        providers._write_receipt(path, b"replacement", project[0])
    assert path.read_bytes() == b"{}\n"


@pytest.mark.parametrize("relative,body", [
    ("pytest.ini", "[pytest]\naddopts=-q\n"),
    ("test_new.py", "def test_new():\n    assert True\n"),
])
def test_new_unindexed_test_or_config_invalidates_provider(project, tmp_path, relative, body):
    verified = verify(project, tmp_path)
    (project[0] / relative).write_text(body)
    with pytest.raises(providers.ProviderUnavailable, match="stale"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))


@pytest.mark.parametrize("selector", ["./check", "{root}/check"])
def test_relative_executable_and_environment_are_normalized_identically(project, tmp_path, selector):
    script = project[0] / "check"
    script.write_text("#!" + sys.executable + "\nimport os\nfrom pathlib import Path\n"
        "assert os.environ['PYTHONPATH'] == str(Path.cwd())\nprint('1 passed')\n")
    script.chmod(0o700)
    verified = providers.verify_public_commands([{"name": "explicit root command", "argv": [selector],
        "env_updates": {"PYTHONPATH": "{root}"}}], project_id=project[2], db_path=project[1].path,
        receipt_path=tmp_path / "provider.json")
    manifest = verified.current_manifest(project[2], project[1].path, ("feature.py",))
    command = manifest["commands"][0]
    assert command["argv"] == [str(script)]
    assert command["env_updates"] == {"PYTHONPATH": str(project[0])}


def test_directory_probe_ignore_pattern_cannot_hide_new_python_test(project, tmp_path):
    (project[0] / ".gitignore").write_text("*.txt\n")
    tests = project[0] / "tests"
    tests.mkdir()
    verified = verify(project, tmp_path)
    (tests / "test_new.py").write_text("def test_new():\n    assert True\n")
    with pytest.raises(providers.ProviderUnavailable, match="stale"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))


def test_eligible_added_symlink_is_unavailable_without_following_target(project, tmp_path):
    verified = verify(project, tmp_path)
    external = tmp_path / "private.py"
    external.write_text("# no target reading required\n")
    (project[0] / "test_new.py").symlink_to(external)
    with pytest.raises(providers.ProviderUnavailable, match="nonsymlink"):
        verified.current_manifest(project[2], project[1].path, ("feature.py",))




def test_explicit_cli_returns_the_real_receipt_trust_pin(project, tmp_path, capsys):
    specification = tmp_path / "commands.json"
    specification.write_text(json.dumps([{"name": "explicit public tests",
        "argv": [sys.executable, "-c", "print('2 passed')"], "kind": "tests"}]))
    target = tmp_path / "cli-provider.json"
    assert providers.main(["verify", "--project", project[2], "--db", str(project[1].path),
        "--commands-json", str(specification), "--receipt", str(target)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["trusted_sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
    assert output["readiness"]["passed_behavioral_tests"] == 2


@pytest.mark.parametrize("invalid", [
    {"env_updates": {"SSL_CERT_FILE": "/untrusted"}},
    {"env_updates": {"PYTHONPATH": 3}},
    {"timeout_seconds": float("nan")},
    {"timeout_seconds": 301},
    {"expected_tests": 0},
])
def test_invalid_command_settings_fail_before_execution(project, tmp_path, monkeypatch, invalid):
    from memglide.integrations import public_check

    monkeypatch.setattr(public_check, "run_check", lambda *args, **kwargs: pytest.fail("invalid command executed"))
    with pytest.raises(ValueError):
        providers.verify_public_commands([{"argv": [sys.executable, "-c", "print('1 passed')"], **invalid}],
            project_id=project[2], db_path=project[1].path, receipt_path=tmp_path / "bad.json")


def test_missing_registered_tool_raises_optional_provider_unavailable(tmp_path):
    with pytest.raises(providers.ProviderUnavailable, match='unavailable'):
        providers._tool(str(tmp_path / 'missing-executable'))
