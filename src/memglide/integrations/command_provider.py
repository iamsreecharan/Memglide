"""Explicit public-check verification and pinned, current provider receipts.

Verification executes only explicitly supplied commands. Loading and checking a
receipt never executes code. A repository JSON file is not a trust anchor: the
caller must pin the receipt's hash obtained from its own verification action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import stat
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_BINDING_BYTES = 16 * 1024 * 1024
MAX_RECEIPT_BYTES = 4 * 1024 * 1024
MAX_TOOL_BYTES = 256 * 1024 * 1024
EXCLUDED_PARTS = {".memglide-check", ".pytest_cache", "__pycache__"}
TEXT_SUFFIXES = {
    ".py",
    ".pyi",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".cjs",
    ".mjs",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".yaml",
    ".yml",
    ".txt",
    ".md",
    ".lock",
    ".xml",
}


class ProviderUnavailable(ValueError):
    """No current verified provider is available; do not claim verified facts."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


@contextmanager
def _parent_descriptor(path: Path, *, create: bool = False):
    """Walk canonical absolute directory components without following links.

    Fail closed on platforms without descriptor-relative no-follow traversal;
    a portable API must not silently weaken the file-integrity guarantee.
    """
    if not path.is_absolute() or ".." in path.parts or not path.name:
        raise ProviderUnavailable("A canonical absolute provider path is required")
    if not all(hasattr(os, flag) for flag in ("O_NOFOLLOW", "O_NONBLOCK", "O_DIRECTORY")):
        raise ProviderUnavailable("Secure descriptor-relative provider files are unavailable")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    directory = None
    try:
        directory = os.open(path.anchor, flags)
        for part in path.parts[1:-1]:
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=directory)
                except FileExistsError:
                    pass
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        yield directory
    except (OSError, NotImplementedError) as exc:
        raise ProviderUnavailable("Provider paths must have regular nonsymlink ancestors") from exc
    finally:
        if directory is not None:
            os.close(directory)


def _fingerprint(info: os.stat_result) -> tuple:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


@contextmanager
def _regular_stream(path: Path, limit: int):
    path = path.absolute()
    with _parent_descriptor(path) as parent:
        descriptor = None
        try:
            descriptor = os.open(
                path.name,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent,
            )
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise ProviderUnavailable(
                    "Provider input must be a bounded regular nonsymlink file"
                )
            with os.fdopen(descriptor, "rb") as stream:
                descriptor = None
                yield stream
                if _fingerprint(os.fstat(stream.fileno())) != _fingerprint(before):
                    raise ProviderUnavailable("Provider input changed during its bounded read")
        except (OSError, NotImplementedError) as exc:
            raise ProviderUnavailable(
                "Provider input must be a bounded regular nonsymlink file"
            ) from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)


def _regular_bytes(path: Path, limit: int) -> bytes:
    with _regular_stream(path, limit) as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ProviderUnavailable("Provider receipt exceeded its bound")
    return raw


def _write_receipt(path: Path, raw: bytes, root: Path) -> None:
    if path.is_relative_to(root) or path.resolve(strict=False).is_relative_to(root):
        raise ValueError("Verification receipts must be stored outside the untrusted project")
    with _parent_descriptor(path, create=True) as parent:
        descriptor = os.open(
            path.name,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | os.O_NOFOLLOW
            | os.O_NONBLOCK
            | getattr(os, "O_CLOEXEC", 0),
            0o600,
            dir_fd=parent,
        )
        with os.fdopen(descriptor, "wb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ProviderUnavailable("Provider receipt target is not a regular file")
            stream.write(raw)


def _tool(selector: str) -> dict:
    candidate = Path(selector)
    if not candidate.is_absolute():
        found = shutil.which(selector)
        if found is None:
            raise ProviderUnavailable("Declared check executable is unavailable")
        candidate = Path(found).absolute()
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProviderUnavailable("Declared check executable is unavailable") from exc
    digest = hashlib.sha256()
    with _regular_stream(resolved, MAX_TOOL_BYTES) as stream:
        total = 0
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            total += len(chunk)
            if total > MAX_TOOL_BYTES:
                raise ProviderUnavailable("Tool grew beyond its verification bound")
            digest.update(chunk)
    return {"selector": selector, "resolved": str(resolved), "sha256": digest.hexdigest()}


def project_binding(project_id: str, db_path: Path) -> dict:
    """Hash a fresh bounded approved public-text tree and every used policy.

    This covers current eligible source, tests and configuration, including
    unindexed additions. It
    does not claim a complete dependency/environment or external-resource image.
    The caller first obtains the ordinary fresh production preparation.
    """
    from memglide.integrations.preload import _eligible, _selection
    from memglide.security.paths import DEFAULT_IGNORED, read_source, secret_path
    from memglide.storage.database import DomainError

    database = Path(db_path).absolute()
    selection = _selection(database, project_id, ())
    root = Path(selection["root"])
    pending = [(root, 0)]
    paths = []
    entries = 0
    total = 0
    files = {}
    while pending:
        directory, depth = pending.pop()
        if depth > 12:
            raise ProviderUnavailable("Provider public-tree depth exceeds its bound")
        local = []
        with os.scandir(directory) as scan:
            for entry in scan:
                entries += 1
                if entries > 20000:
                    raise ProviderUnavailable("Provider public-tree inventory exceeds entry bound")
                local.append(entry)
        for entry in sorted(local, key=lambda item: item.name):
            relative = Path(entry.path).relative_to(root).as_posix()
            if secret_path(relative) or set(Path(relative).parts) & (
                DEFAULT_IGNORED | EXCLUDED_PARTS
            ):
                continue
            parts = Path(relative).parts
            if any(
                relative == item.strip("/")
                or relative.startswith(item.strip("/") + "/")
                or item.strip("/") in parts
                for item in selection["ignored"]
                if item.strip("/")
            ):
                continue
            is_directory = entry.is_dir(follow_symlinks=False)
            # A synthetic child name can itself match a file ignore pattern;
            # using it to prune a directory would miss eligible new children.
            # Descend conservatively within the fixed entry/depth bounds and
            # check real files against the actual inherited policy instead.
            if is_directory:
                pending.append((Path(entry.path), depth + 1))
                continue
            try:
                _eligible(selection, (relative,))
            except ValueError as exc:
                if str(exc) == "source_excluded":
                    continue
                raise ProviderUnavailable("Provider approval policy is unavailable") from exc
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ProviderUnavailable(
                    "An eligible public input is not a regular nonsymlink file"
                )
            else:
                try:
                    body, digest = read_source(
                        root, relative, min(selection["max_size"], MAX_BINDING_BYTES)
                    )
                except DomainError as exc:
                    if Path(relative).suffix.lower() in TEXT_SUFFIXES or Path(relative).name in {
                        "Makefile",
                        "Dockerfile",
                    }:
                        raise ProviderUnavailable(
                            "An eligible public text input is unavailable"
                        ) from exc
                    # Nontext assets/dependencies are explicitly outside the receipt's scope.
                    continue
                total += len(body.encode())
                if total > MAX_BINDING_BYTES:
                    raise ProviderUnavailable("Provider project binding exceeds total byte bound")
                files[relative] = digest
                paths.append(relative)
    bound_paths = tuple(sorted(paths))
    policy = _eligible(selection, bound_paths)
    if (
        _selection(database, project_id, ()) != selection
        or _eligible(selection, bound_paths) != policy
    ):
        raise ProviderUnavailable("Approval policy changed during provider binding")
    return {
        "root": selection["root"],
        "project_id": project_id,
        "files": files,
        "policy_versions": policy,
        "scope": "fresh bounded eligible public text tree, including unindexed additions; ignored/secret/nontext files and external resources/dependency state not implied",
    }


def _commands(raw: Any) -> list[dict]:
    if not isinstance(raw, list) or not 1 <= len(raw) <= 16:
        raise ValueError("Verification requires one to sixteen explicit commands")
    result = []
    for item in raw:
        argv = item.get("argv") if isinstance(item, dict) else None
        if (
            not isinstance(argv, list)
            or not 1 <= len(argv) <= 128
            or any(
                not isinstance(arg, str) or not arg or "\x00" in arg or len(arg) > 4096
                for arg in argv
            )
        ):
            raise ValueError("Checks require bounded atomic argv lists")
        if Path(argv[0]).name in {"bash", "sh", "zsh", "dash", "fish"}:
            raise ValueError("Compound shell checks cannot attest individual exit status")
        kind = item.get("kind", "tests")
        if kind not in {"tests", "typecheck"}:
            raise ValueError("Unknown public check kind")
        name = item.get("name", "public check")
        if not isinstance(name, str) or not name or len(name) > 120 or "\x00" in name:
            raise ValueError("Check names must be bounded nonempty strings")
        from .public_check import ENVIRONMENT_KEYS

        environment = item.get("env_updates", {})
        if not isinstance(environment, dict) or any(
            key not in ENVIRONMENT_KEYS
            or not isinstance(value, str)
            or len(value) > 4096
            or "\x00" in value
            for key, value in environment.items()
        ):
            raise ValueError("Only bounded nonsecret check environment settings are allowed")
        timeout = item.get("timeout_seconds", 45)
        if (
            type(timeout) not in {int, float}
            or not math.isfinite(timeout)
            or not 0 < timeout <= 300
        ):
            raise ValueError("Explicit verification timeout must be finite and within 300 seconds")
        expected = item.get("expected_tests")
        if expected is not None and (kind != "tests" or type(expected) is not int or expected <= 0):
            raise ValueError("Expected behavioral count must be a positive integer")
        result.append(
            {
                "name": str(item.get("name", "public check")),
                "argv": list(argv),
                "kind": kind,
                "env_updates": dict(environment),
                "timeout_seconds": timeout,
                "expected_tests": expected,
            }
        )
    return result


@dataclass(frozen=True)
class VerifiedPublicCommands:
    """A receipt pinned by the explicit caller, rechecked before any claims."""

    receipt: dict
    trusted_sha256: str

    def current_manifest(
        self, project_id: str, db_path: Path, selected_paths: tuple[str, ...]
    ) -> dict:
        if hashlib.sha256(canonical(self.receipt) + b"\n").hexdigest() != self.trusted_sha256:
            raise ProviderUnavailable("Provider receipt changed after explicit trust pinning")
        current = project_binding(project_id, db_path)
        if current != self.receipt.get("binding"):
            raise ProviderUnavailable(
                "Provider source/test/configuration or policy binding is stale"
            )
        if not set(selected_paths) <= set(current["files"]):
            raise ProviderUnavailable("Provider does not bind every selected production source")
        for tool in self.receipt.get("tools", []):
            if _tool(tool["selector"]) != tool:
                raise ProviderUnavailable("Provider tool binding is stale")
        commands = self.receipt.get("commands")
        if not isinstance(commands, list) or not commands:
            raise ProviderUnavailable("Provider contains no verified public commands")
        try:
            _commands(commands)
        except ValueError as exc:
            raise ProviderUnavailable("Provider command schema is invalid") from exc
        for item in commands:
            baseline = item.get("baseline", {})
            if baseline.get("exit_code") != 0 or baseline.get("verified") is not True:
                raise ProviderUnavailable("Public check lacks explicit successful verification")
            if item["kind"] == "tests" and (
                type(baseline.get("tests")) is not int or baseline["tests"] <= 0
            ):
                raise ProviderUnavailable(
                    "Public behavioral baseline has no executed-test evidence"
                )
        return {
            "commands": commands,
            "readiness": self.receipt["readiness"],
            "python": self.receipt["python"],
            "provider_sha256": self.trusted_sha256,
        }


def load_verified_provider(path: Path, trusted_sha256: str) -> VerifiedPublicCommands:
    """The trusted hash must come from the caller's own verification action."""
    raw = _regular_bytes(Path(path), MAX_RECEIPT_BYTES)
    value = json.loads(raw)
    if (
        not isinstance(value, dict)
        or value.get("version") != "explicit-public-check-verification-1"
    ):
        raise ProviderUnavailable("Unsupported provider receipt")
    if raw != canonical(value) + b"\n":
        raise ProviderUnavailable("Provider receipt is not in its canonical verified format")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != trusted_sha256:
        raise ProviderUnavailable("Provider receipt does not match the caller's trusted hash")
    return VerifiedPublicCommands(value, trusted_sha256)


def verify_public_commands(
    commands: list[dict],
    *,
    project_id: str,
    db_path: Path,
    receipt_path: Path,
    tool_files: tuple[str, ...] = (),
) -> VerifiedPublicCommands:
    """Explicitly execute public checks, bind their inputs and save a receipt.

    This is a separate user-invoked action. Preparation never calls this API.
    Test/imported project code runs only under this explicit authorization.
    """
    from .public_check import run_check

    specifications = _commands(commands)
    binding = project_binding(project_id, db_path)
    root = Path(binding["root"])
    for item in specifications:
        item["argv"] = [arg.replace("{root}", str(root)) for arg in item["argv"]]
        executable = item["argv"][0]
        if not Path(executable).is_absolute() and ("/" in executable or "\\" in executable):
            item["argv"][0] = str((root / executable).absolute())
        item["env_updates"] = {
            key: value.replace("{root}", str(root)) for key, value in item["env_updates"].items()
        }
    target = Path(receipt_path).absolute()
    if target.is_relative_to(root) or target.resolve(strict=False).is_relative_to(root):
        raise ValueError("Verification receipts must be stored outside the untrusted project")
    selectors = sorted({sys.executable, *[item["argv"][0] for item in specifications], *tool_files})
    tools = [_tool(selector) for selector in selectors]
    verified = []
    for item in specifications:
        result = run_check(
            item["argv"],
            root,
            output_mode="structured",
            kind=item["kind"],
            expected_tests=item["expected_tests"],
            timeout_seconds=item["timeout_seconds"],
            env_updates=item["env_updates"],
        )
        if not result["success"]:
            raise ProviderUnavailable("Explicit public check did not pass: " + item["name"])
        verified.append(
            {
                **item,
                "baseline": {
                    "exit_code": 0,
                    "tests": result.get("passed"),
                    "verified": True,
                    "stdout_sha256": result["stdout_sha256"],
                    "stderr_sha256": result["stderr_sha256"],
                    "stdout_log": result["stdout_log"],
                    "stderr_log": result["stderr_log"],
                    "check_receipt_log": result["receipt_log"],
                    "check_receipt_sha256": result["receipt_sha256"],
                },
            }
        )
    if (
        project_binding(project_id, db_path) != binding
        or [_tool(selector) for selector in selectors] != tools
    ):
        raise ProviderUnavailable(
            "Verification changed bound source/test/configuration, policy or tools"
        )
    receipt = {
        "version": "explicit-public-check-verification-1",
        "binding": binding,
        "commands": verified,
        "tools": tools,
        "python": sys.executable,
        "readiness": {
            "verification": "explicit successful public checks",
            "commands": len(verified),
            "passed_behavioral_tests": sum(
                item["baseline"]["tests"] or 0 for item in verified if item["kind"] == "tests"
            ),
            "typechecks": sum(item["kind"] == "typecheck" for item in verified),
        },
    }
    if len(canonical(receipt)) > MAX_RECEIPT_BYTES:
        raise ProviderUnavailable("Provider receipt exceeds serialization bound")
    raw = canonical(receipt) + b"\n"
    _write_receipt(target, raw, root)
    digest = hashlib.sha256(raw).hexdigest()
    return VerifiedPublicCommands(receipt, digest)


def main(argv: list[str] | None = None) -> int:
    """Explicit verification action; never invoked by source preparation."""
    parser = argparse.ArgumentParser(
        description="Explicitly execute declared public checks and pin their current inputs. Run untrusted project tests only in an appropriate isolation environment."
    )
    parser.add_argument("action", choices=("verify",))
    parser.add_argument("--project", required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument(
        "--commands-json",
        type=Path,
        required=True,
        help="explicit bounded JSON list of atomic public check argv specifications",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        required=True,
        help="new private receipt path outside the untrusted project",
    )
    parser.add_argument("--tool-file", action="append", default=[])
    options = parser.parse_args(argv)
    try:
        commands = json.loads(_regular_bytes(options.commands_json, MAX_RECEIPT_BYTES))
        provider = verify_public_commands(
            commands,
            project_id=options.project,
            db_path=options.db,
            receipt_path=options.receipt,
            tool_files=tuple(options.tool_file),
        )
        print(
            json.dumps(
                {
                    "receipt": str(options.receipt.absolute()),
                    "trusted_sha256": provider.trusted_sha256,
                    "readiness": provider.receipt["readiness"],
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print("memglide public-check verification: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
