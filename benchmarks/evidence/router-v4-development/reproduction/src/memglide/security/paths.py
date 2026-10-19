"""Source access policy: no traversal, symlinks, secret files or executable evaluation."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path, PurePosixPath

from memglide.storage.database import DomainError

DEFAULT_IGNORED = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".cache",
    "__pycache__",
    ".memglide",
    ".local",
    "coverage",
    ".pytest_cache",
    ".pytest_tmp",
    ".mypy_cache",
    ".ruff_cache",
}
SECRET_NAMES = {
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "credentials",
    ".npmrc",
    ".pypirc",
    ".netrc",
    ".git-credentials",
    ".envrc",
    "secrets.toml",
    "credentials.json",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
}
SECRET_PATTERN = re.compile(
    r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bsk-[A-Za-z0-9_-]{20,}\b|(?i:(?:password|passwd|api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[\"'][^\"'\n]{8,}[\"'])"
)
UNQUOTED_SECRET = re.compile(
    r"(?im)^\s*(?:export\s+)?(?:password|passwd|api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[A-Za-z0-9_./+~-]{12,}\s*(?:#.*)?$"
)


def secret_path(path: str) -> bool:
    p = PurePosixPath(path)
    return (
        any(part in {".ssh", ".aws", ".gnupg", ".kube", ".azure", ".docker"} for part in p.parts)
        or any(part == ".env" or part.startswith(".env.") for part in p.parts)
        or p.name in SECRET_NAMES
        or p.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".keystore"}
    )


def safe_path(root: str | Path, relative: str, *, must_exist: bool = True) -> Path:
    try:
        base = Path(root).resolve(strict=True)
    except (OSError, ValueError) as exc:
        raise DomainError("Registered project root is unavailable") from exc
    if Path(root).absolute() != base:
        raise DomainError(
            "Registered project root must remain canonical and cannot be replaced by a symlink"
        )
    if (
        not relative
        or not PurePosixPath(relative).parts
        or "\x00" in relative
        or "\\" in relative
        or Path(relative).is_absolute()
        or ".." in PurePosixPath(relative).parts
    ):
        raise DomainError("Source path must be relative and remain inside its registered project")
    candidate = base / relative
    current = base
    for part in PurePosixPath(relative).parts:
        current /= part
        if current.is_symlink():
            raise DomainError("Symlink source access is not permitted")
    resolved = candidate.resolve(strict=must_exist)
    if not resolved.is_relative_to(base):
        raise DomainError("Source path escapes its registered project")
    if secret_path(relative):
        raise DomainError("Secret-file access is not permitted")
    return resolved


def read_source(root: str | Path, relative: str, max_size: int = 512000) -> tuple[str, str]:
    path = safe_path(root, relative)
    descriptors: list[int] = []
    try:
        if os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW"):
            # Resolve each component from an already opened directory. Validation and
            # opening cannot be separated by an attacker swapping in a symlink.
            directory = os.open(Path(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.append(directory)
            parts = PurePosixPath(relative).parts
            for part in parts[:-1]:
                directory = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
                )
                descriptors.append(directory)
            file_fd = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
            )
        else:
            # Portable fallback verifies the opened file identity before returning data.
            # Reparse-point/symlink changes are rejected even when open itself followed one.
            file_fd = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
        descriptors.append(file_fd)
        opened = os.fstat(file_fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > max_size:
            raise DomainError("Source is not a regular file within the configured size limit")
        with os.fdopen(os.dup(file_fd), "rb") as stream:
            data = stream.read(max_size + 1)
        checked = safe_path(root, relative).stat(follow_symlinks=False)
        if (opened.st_dev, opened.st_ino) != (checked.st_dev, checked.st_ino):
            raise DomainError("Source changed during secure read; retry indexing")
    except (OSError, ValueError) as exc:
        if isinstance(exc, DomainError):
            raise
        raise DomainError("Source is unavailable or changed during secure read") from exc
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
    if len(data) > max_size or b"\x00" in data:
        raise DomainError("Binary or oversized source is excluded")
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DomainError("Non-UTF-8 source is excluded") from exc
    if SECRET_PATTERN.search(content) or UNQUOTED_SECRET.search(content):
        raise DomainError("Source containing detected credentials is excluded")
    return content, hashlib.sha256(data).hexdigest()
