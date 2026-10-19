#!/usr/bin/env python3
"""Generic offline preparation; no corpus selection or upstream code execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tarfile
import zipfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_path(value: str) -> str:
    p = PurePosixPath(value)
    if not value or p.is_absolute() or ".." in p.parts or "\\" in value:
        raise ValueError(f"unsafe relative path: {value!r}")
    if str(p) != value or value.endswith("/"):
        raise ValueError(f"noncanonical relative path: {value!r}")
    return value


def file_record(path: Path) -> dict[str, object]:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"not a regular file: {path}")
    data = path.read_bytes()
    return {"sha256": digest(data), "size": len(data), "mode": stat.S_IMODE(metadata.st_mode)}


def snapshot(root: Path) -> dict[str, object]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("source root must be an existing nonsymlink directory")
    files = {}
    for path in sorted(root.rglob("*")):
        metadata = path.lstat()
        if stat.S_ISDIR(metadata.st_mode):
            continue
        files[path.relative_to(root).as_posix()] = file_record(path)
    if not files:
        raise ValueError("empty source tree")
    return {"version": 1, "files": files}


def write_json(path: Path, value: object) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def extract(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    if digest(archive.read_bytes()) != args.sha256.lower():
        raise ValueError("archive SHA-256 mismatch")
    prefix = relative_path(args.prefix)
    selected = json.loads(Path(args.members).read_text(encoding="utf-8"))
    if not isinstance(selected, list) or not selected or not all(isinstance(x, str) for x in selected):
        raise ValueError("members must be a nonempty JSON list of relative path strings")
    selected = [relative_path(x) for x in selected]
    if len(set(selected)) != len(selected):
        raise ValueError("duplicate selected member")
    if args.license not in selected:
        raise ValueError("the explicitly designated source license must be selected")
    dest = Path(args.dest)
    if dest.exists():
        raise ValueError("destination must not exist")
    wanted = {prefix + "/" + name: name for name in selected}
    contents: dict[str, bytes] = {}
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as bundle:
            for info in bundle.infolist():
                if info.filename not in wanted:
                    continue
                unix_mode = info.external_attr >> 16
                kind = stat.S_IFMT(unix_mode)
                if info.is_dir() or kind not in (0, stat.S_IFREG):
                    raise ValueError(f"selected member is not regular: {info.filename}")
                if info.file_size > args.max_file_bytes:
                    raise ValueError("selected member exceeds size limit")
                name = wanted[info.filename]
                if name in contents:
                    raise ValueError("duplicate selected archive member")
                contents[name] = bundle.read(info)
    else:
        with tarfile.open(archive, "r:*") as bundle:
            for info in bundle:
                if info.name not in wanted:
                    continue
                if not info.isfile() or info.issym() or info.islnk():
                    raise ValueError(f"selected member is not regular: {info.name}")
                if info.size > args.max_file_bytes:
                    raise ValueError("selected member exceeds size limit")
                name = wanted[info.name]
                if name in contents:
                    raise ValueError("duplicate selected archive member")
                stream = bundle.extractfile(info)
                if stream is None:
                    raise ValueError("selected member has no data")
                contents[name] = stream.read(args.max_file_bytes + 1)
    if set(contents) != set(selected):
        raise ValueError(f"missing selected members: {sorted(set(selected) - set(contents))}")
    if sum(map(len, contents.values())) > args.max_total_bytes:
        raise ValueError("selected archive subset exceeds total size limit")
    for name, data in contents.items():
        if len(data) > args.max_file_bytes or b"\0" in data:
            raise ValueError(f"nontext or oversized selected member: {name}")
        data.decode("utf-8", errors="strict")
    dest.mkdir(parents=True)
    for name, data in contents.items():
        path = dest / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o644)
    print(json.dumps({"success": True, "file_count": len(contents), "source_tree": snapshot(dest)}))


def verify(args: argparse.Namespace) -> None:
    expected = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if expected.get("version") != 1 or not isinstance(expected.get("files"), dict):
        raise ValueError("unsupported snapshot manifest")
    for name in expected["files"]:
        relative_path(name)
    observed = snapshot(Path(args.root))
    missing = sorted(set(expected["files"]) - set(observed["files"]))
    changed = sorted(name for name in set(expected["files"]) & set(observed["files"])
                     if expected["files"][name] != observed["files"][name])
    added = sorted(set(observed["files"]) - set(expected["files"]))
    success = not missing and not changed and (args.allow_added or not added)
    print(json.dumps({"success": success, "missing": missing, "changed": changed, "added": added}))
    if not success:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ex = sub.add_parser("extract", help="extract selected regular UTF-8 files from a pinned archive")
    ex.add_argument("--archive", required=True)
    ex.add_argument("--sha256", required=True)
    ex.add_argument("--prefix", required=True)
    ex.add_argument("--members", required=True, help="JSON list; authored only after freeze")
    ex.add_argument("--license", required=True, help="relative upstream license file in the selected list")
    ex.add_argument("--dest", required=True)
    ex.add_argument("--max-file-bytes", type=int, default=1_000_000)
    ex.add_argument("--max-total-bytes", type=int, default=8_000_000)
    ex.set_defaults(func=extract)
    sn = sub.add_parser("snapshot", help="hash every regular file; reject special files/symlinks")
    sn.add_argument("--root", required=True)
    sn.add_argument("--out", required=True)
    sn.set_defaults(func=lambda a: write_json(Path(a.out), snapshot(Path(a.root))))
    ve = sub.add_parser("verify", help="verify an exact fixture or designated protected-file tree")
    ve.add_argument("--root", required=True)
    ve.add_argument("--manifest", required=True)
    ve.add_argument("--allow-added", action="store_true")
    ve.set_defaults(func=verify)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
