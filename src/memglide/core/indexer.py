"""Incremental repository index, deterministic source search and conservative graph edges."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import subprocess
import threading
import time
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

import pathspec

from memglide.core.parsing import import_parts, parse_sources
from memglide.core.query import (
    INDEX_VERSION,
    explicit_identifier,
    explicit_path,
    preferred_source_role,
    search_focus,
    source_role,
    term_variants,
    tokens,
)
from memglide.security.paths import DEFAULT_IGNORED, read_source, secret_path
from memglide.storage.database import Database, DomainError, new_id

MAX_INDEXED_FILES = 20_000
MAX_INDEX_BYTES = 100 * 1024 * 1024
FTS_QUERY_BATCH_SIZE = 64
MAX_FTS_RANK_TERMS = 32
# Bump when static graph resolution semantics change. Persisting this separately
# from the lexical index lets older databases refresh once without rebuilding an
# identical graph on every synchronous search or watcher poll.
GRAPH_RESOLUTION_VERSION = 1


def _identifier(*parts: str) -> str:
    return hashlib.sha256("\x00".join(parts).encode()).hexdigest()[:32]


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            [
                "git",
                "-c",
                "core.fsmonitor=false",
                "-c",
                f"core.hooksPath={os.devnull}",
                "-c",
                "submodule.recurse=false",
                "-C",
                str(root),
                *args,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.rstrip("\n")
    except (OSError, subprocess.SubprocessError) as exc:
        raise DomainError("Git repository metadata could not be read") from exc


def _tokens(text: str) -> list[str]:
    return tokens(text)


class Indexer:
    def __init__(self, db: Database):
        self.db = db
        self._lock = threading.RLock()

    @staticmethod
    def _document_frequencies(
        conn: Any, project_id: str, expressions: dict[str, str]
    ) -> dict[str, int]:
        """Use exact FTS vocabulary counts without repeatedly loading source payloads.

        A vocabulary row counts documents globally. It is project-correct only
        when all indexed files belong to this project. Multiple matching surface
        forms still require a union count, not a sum that double-counts documents.
        Non-ASCII terms use MATCH's own unicode61 normalization as before.
        """
        frequencies: dict[str, int] = {}
        if not expressions:
            return frequencies
        if not conn.execute(
            "SELECT 1 FROM files WHERE project_id=? LIMIT 1", (project_id,)
        ).fetchone():
            return dict.fromkeys(expressions, 0)
        vocabulary: dict[str, int] | None = None
        single_project = not conn.execute(
            "SELECT 1 FROM files WHERE project_id<>? LIMIT 1", (project_id,)
        ).fetchone()
        if single_project:
            try:
                conn.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS temp.memglide_term_stats "
                    "USING fts5vocab(main,file_search,row)"
                )
                vocabulary_forms = sorted(
                    {form for word in expressions for form in term_variants(word) if form.isascii()}
                )
                vocabulary = {}
                for offset in range(0, len(vocabulary_forms), 500):
                    batch = vocabulary_forms[offset : offset + 500]
                    placeholders = ",".join("?" for _ in batch)
                    for row in conn.execute(
                        f"SELECT term,doc FROM temp.memglide_term_stats WHERE term IN ({placeholders})",
                        batch,
                    ):
                        vocabulary[row["term"]] = row["doc"]
            except sqlite3.OperationalError as error:
                if "no such module: fts5vocab" not in str(error):
                    raise
        scope_prepared = False
        for word, expression in expressions.items():
            forms = term_variants(word)
            if vocabulary is not None and all(form.isascii() for form in forms):
                counts = [vocabulary[form] for form in forms if form in vocabulary]
                if len(counts) <= 1:
                    frequencies[word] = counts[0] if counts else 0
                    continue
            if single_project:
                frequencies[word] = conn.execute(
                    "SELECT count(*) FROM file_search WHERE file_search MATCH ?", (expression,)
                ).fetchone()[0]
            else:
                if not scope_prepared:
                    conn.execute(
                        "CREATE TEMP TABLE IF NOT EXISTS memglide_project_docs(doc INTEGER PRIMARY KEY)"
                    )
                    conn.execute("DELETE FROM temp.memglide_project_docs")
                    conn.execute(
                        "INSERT INTO temp.memglide_project_docs SELECT rowid FROM file_search WHERE project_id=?",
                        (project_id,),
                    )
                    scope_prepared = True
                # Read the project's document IDs once. Per-term membership
                # checks then use integers, without loading UNINDEXED project_id
                # and its source payload for every matching posting.
                frequencies[word] = conn.execute(
                    "SELECT count(*) FROM file_search CROSS JOIN temp.memglide_project_docs p "
                    "ON p.doc=file_search.rowid WHERE file_search MATCH ?",
                    (expression,),
                ).fetchone()[0]
        return frequencies

    @staticmethod
    def _project_output(project: dict[str, Any]) -> dict[str, Any]:
        return {
            **project,
            "git_state": json.loads(project["git_state"]),
            "index_stats": json.loads(project["index_stats"]),
        }

    def add_project(self, path: str) -> dict[str, Any]:
        if not path.strip():
            raise DomainError("A Git repository root path is required")
        try:
            given = Path(path).expanduser().absolute()
            root = given.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise DomainError("Repository path does not exist") from exc
        if not root.is_dir():
            raise DomainError("Repository root must be a directory")
        # The exact Git root is the explicit allowlist boundary, never its parent or a child.
        top = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
        if top != root:
            raise DomainError(
                "Register the canonical Git repository root, rather than a subdirectory"
            )
        if given != root:
            # Reject symlink-based registrations while allowing harmless spelling normalization.
            current = Path(given.anchor)
            for part in given.parts[1:]:
                current /= part
                if current.is_symlink():
                    raise DomainError("Register a canonical repository path without symlinks")
        with self._lock:
            existing = self.db.one("SELECT * FROM projects WHERE path=?", (str(root),))
            if existing:
                self.reindex(existing["id"])
                return self._project_output(self.db.project(existing["id"]))
            project_id = new_id()
            self.db.execute(
                "INSERT INTO projects(id,path,name,created_at) VALUES(?,?,?,?)",
                (project_id, str(root), root.name, time.time()),
            )
            self.reindex(project_id)
            self.db.event(project_id, None, "project_registered", {"name": root.name})
            return self._project_output(self.db.project(project_id))

    def list_projects(self) -> list[dict[str, Any]]:
        return [
            self._project_output(p)
            for p in self.db.rows("SELECT * FROM projects ORDER BY created_at,id")
        ]

    def remove_project(self, project_id: str) -> dict[str, Any]:
        self.db.project(project_id)
        with self._lock, self.db.connect() as conn:
            conn.execute("DELETE FROM file_search WHERE project_id=?", (project_id,))
            conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
        return {"project_id": project_id, "removed": True, "source_deleted": False}

    def _scan(
        self,
        root: Path,
        settings: dict[str, Any],
        *,
        known_hashes: dict[str, str] | None = None,
    ) -> tuple[dict[str, tuple[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        """Securely read every eligible source, retaining only needed bodies.

        Existing hashes never avoid a read or establish freshness themselves.
        They only allow an unchanged body to be released after live validation
        and byte accounting. Default callers still receive complete source.
        """
        sources: dict[str, tuple[str, str]] = {}
        ignored: list[dict[str, str]] = []
        errors: list[dict[str, str]] = []
        specs: dict[str, list[tuple[str, pathspec.GitIgnoreSpec]]] = {}
        configured = settings["ignored_directories"]
        extra = {str(p).strip("/") for p in configured if str(p).strip("/")}
        total_bytes = 0
        resource_exhausted = False

        def excluded(
            relative: str, is_dir: bool, rules: list[tuple[str, pathspec.GitIgnoreSpec]]
        ) -> str | None:
            parts = PurePosixPath(relative).parts
            if any(part in DEFAULT_IGNORED for part in parts):
                return "default ignored directory"
            if secret_path(relative):
                return "secret path"
            if any(
                relative == entry or relative.startswith(entry + "/") or entry in parts
                for entry in extra
            ):
                return "configured ignored directory"
            matched = False
            for base, spec in rules:
                local = relative[len(base) + 1 :] if base else relative
                result = spec.check_file(local + ("/" if is_dir else ""))
                if result.include is not None:
                    matched = bool(result.include)
            return "ignore rule" if matched else None

        def onerror(exc: OSError) -> None:
            errors.append(
                {
                    "path": str(Path(exc.filename or root).relative_to(root)),
                    "error": "Directory could not be read",
                }
            )

        for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
            dirs.sort()
            parent = Path(directory)
            base = parent.relative_to(root).as_posix()
            if base == ".":
                base = ""
            parent_base = str(PurePosixPath(base).parent)
            if parent_base == ".":
                parent_base = ""
            rules = list(specs.get(parent_base, [])) if base else []
            for name in (".gitignore", ".memglideignore"):
                config = parent / name
                if (
                    config.is_file()
                    and not config.is_symlink()
                    and config.stat().st_size <= settings["max_file_size"]
                ):
                    try:
                        config_source, _ = read_source(
                            root, config.relative_to(root).as_posix(), settings["max_file_size"]
                        )
                        rules.append(
                            (base, pathspec.GitIgnoreSpec.from_lines(config_source.splitlines()))
                        )
                    except (OSError, UnicodeError, ValueError):
                        errors.append(
                            {
                                "path": config.relative_to(root).as_posix(),
                                "error": "Ignore rules could not be read",
                            }
                        )
            specs[base] = rules
            for name in sorted(dirs):
                relative = (parent / name).relative_to(root).as_posix()
                reason = (
                    "symlink" if (parent / name).is_symlink() else excluded(relative, True, rules)
                )
                if reason:
                    dirs.remove(name)
                    if len(ignored) < 1000:
                        ignored.append({"path": relative + "/", "reason": reason})
            for name in sorted(files):
                path = parent / name
                relative = path.relative_to(root).as_posix()
                reason = "symlink" if path.is_symlink() else excluded(relative, False, rules)
                if reason:
                    if len(ignored) < 1000:
                        ignored.append({"path": relative, "reason": reason})
                    continue
                if resource_exhausted or len(sources) >= MAX_INDEXED_FILES:
                    if not resource_exhausted:
                        errors.append(
                            {
                                "path": relative,
                                "error": f"Index resource limit reached ({MAX_INDEXED_FILES} files / {MAX_INDEX_BYTES} bytes); index is partial. Narrow ignored directories or register a smaller repository.",
                            }
                        )
                        resource_exhausted = True
                    if len(ignored) < 1000:
                        ignored.append({"path": relative, "reason": "index resource limit"})
                    continue
                try:
                    pair = read_source(root, relative, settings["max_file_size"])
                    size = len(pair[0].encode("utf-8"))
                    if total_bytes + size > MAX_INDEX_BYTES:
                        errors.append(
                            {
                                "path": relative,
                                "error": f"Index resource limit reached ({MAX_INDEX_BYTES} bytes); index is partial. Narrow ignored directories or register a smaller repository.",
                            }
                        )
                        resource_exhausted = True
                        if len(ignored) < 1000:
                            ignored.append({"path": relative, "reason": "index resource limit"})
                        continue
                    total_bytes += size
                    sources[relative] = (
                        ("", pair[1])
                        if known_hashes is not None and known_hashes.get(relative) == pair[1]
                        else pair
                    )
                except DomainError as exc:
                    if len(ignored) < 1000:
                        ignored.append({"path": relative, "reason": str(exc)})
                except (OSError, RuntimeError):
                    errors.append({"path": relative, "error": "Source could not be read"})
        return sources, ignored, errors

    def reindex(self, project_id: str, full: bool = False) -> dict[str, Any]:
        with self._lock:
            project = self.db.project(project_id)
            root = Path(project["path"])
            try:
                if not root.is_dir() or root.resolve(strict=True) != root:
                    raise DomainError("Registered repository is unavailable or no longer canonical")
            except (OSError, RuntimeError, ValueError) as exc:
                raise DomainError(
                    "Registered repository is unavailable or no longer canonical"
                ) from exc
            settings = self.db.settings()
            existing = {
                row["path"]: row
                for row in self.db.rows("SELECT * FROM files WHERE project_id=?", (project_id,))
            }
            sources, ignored, errors = self._scan(
                root,
                settings,
                known_hashes=None if full else {path: row["hash"] for path, row in existing.items()},
            )
            changed = {
                p: pair
                for p, pair in sources.items()
                if full or p not in existing or existing[p]["hash"] != pair[1]
            }
            removed = set(existing) - set(sources)
            previous_stats = json.loads(project["index_stats"])
            refresh_search = previous_stats.get("search_index_version") != INDEX_VERSION
            refresh_graph = (
                bool(changed or removed)
                or full
                or previous_stats.get("graph_resolution_version") != GRAPH_RESOLUTION_VERSION
            )
            parsed = parse_sources({path: content for path, (content, _) in changed.items()})
            for path, result in parsed.items():
                if result.error:
                    errors.append({"path": path, "error": result.error})
            errors.extend(
                {"path": path, "error": row["parse_error"]}
                for path, row in existing.items()
                if path in sources and path not in changed and row["parse_error"]
            )
            branch = (
                _git(root, "rev-parse", "--abbrev-ref", "HEAD")
                if self._has_head(root)
                else "unborn"
            )
            status = _git(
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=normal",
                "--ignore-submodules=all",
            )
            git_state = {
                "branch": branch,
                "dirty": bool(status),
                "changes": status.splitlines(),
                "head": _git(root, "rev-parse", "HEAD") if self._has_head(root) else None,
            }
            now = time.time()
            with self.db.connect() as conn:
                for path in sorted(removed | set(changed)):
                    conn.execute(
                        "DELETE FROM dependencies WHERE project_id=? AND source_file=?",
                        (project_id, path),
                    )
                    conn.execute(
                        "DELETE FROM file_search WHERE project_id=? AND path=?", (project_id, path)
                    )
                    conn.execute(
                        "DELETE FROM files WHERE project_id=? AND path=?", (project_id, path)
                    )
                for path, (content, digest) in sorted(changed.items()):
                    info = parsed[path]
                    file_id = _identifier(project_id, path)
                    conn.execute(
                        "INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (
                            file_id,
                            project_id,
                            path,
                            digest,
                            info.language,
                            len(content.encode()),
                            (root / path).stat().st_mtime,
                            int(info.structural),
                            info.error,
                            now,
                        ),
                    )
                    # Source text has one durable copy in FTS; symbols only keep signatures/locations.
                    conn.execute(
                        "INSERT INTO file_search(project_id,path,identifiers,content) VALUES(?,?,?,?)",
                        (
                            project_id,
                            path,
                            " ".join(
                                f"{s['name']} {s['qualified_name']} {' '.join(_tokens(s['name']))}"
                                for s in info.symbols
                            ),
                            content,
                        ),
                    )
                    seen: Counter[str] = Counter()
                    by_qualified: dict[str, str] = {}
                    for symbol in info.symbols:
                        key = symbol["qualified_name"] + ":" + symbol["kind"]
                        ordinal = seen[key]
                        seen[key] += 1
                        sid = _identifier(project_id, path, key, str(ordinal))
                        by_qualified[symbol["qualified_name"]] = sid
                        conn.execute(
                            "INSERT INTO symbols VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                            (
                                sid,
                                project_id,
                                file_id,
                                path,
                                symbol["name"],
                                symbol["qualified_name"],
                                symbol["kind"],
                                symbol["signature"],
                                symbol["start_line"],
                                symbol["end_line"],
                                symbol["exported"],
                            ),
                        )
                    for ordinal, edge in enumerate(info.dependencies):
                        source_sid = by_qualified.get(edge["source_symbol"])
                        conn.execute(
                            "INSERT INTO dependencies VALUES(?,?,?,?,?,?,?,?,?)",
                            (
                                _identifier(project_id, path, str(ordinal), edge["reference"]),
                                project_id,
                                path,
                                source_sid,
                                None,
                                None,
                                edge["kind"],
                                edge["reference"],
                                0,
                            ),
                        )
                # Upgrade only lexical fields for unchanged source. Symbol identities,
                # hashes, source versions and parse timestamps retain their provenance.
                if refresh_search:
                    identifiers: dict[str, list[str]] = {}
                    for symbol in conn.execute(
                        "SELECT path,name,qualified_name FROM symbols WHERE project_id=? ORDER BY path,start_line,id",
                        (project_id,),
                    ):
                        identifiers.setdefault(symbol["path"], []).append(
                            f"{symbol['name']} {symbol['qualified_name']} "
                            + " ".join(_tokens(symbol["name"]))
                        )
                    for path in sorted(set(sources) - set(changed)):
                        conn.execute(
                            "UPDATE file_search SET identifiers=? WHERE project_id=? AND path=?",
                            (" ".join(identifiers.get(path, [])), project_id, path),
                        )
                # A complete live scan still establishes the source set and
                # hashes above. If none changed, persisted symbols and edges are
                # identical; rewriting all graph targets would add only work.
                # A version mismatch refreshes legacy state and future resolver
                # migrations even when the source bytes are unchanged.
                if refresh_graph:
                    self._resolve(conn, project_id)
                modified = {
                    p for p in changed if p in existing and sources[p][1] != existing[p]["hash"]
                } | removed
                added = set(changed) - set(existing) if project["indexed_at"] is not None else set()
                if modified:
                    self._invalidate(conn, project_id, modified)
                file_count = conn.execute(
                    "SELECT COUNT(*) FROM files WHERE project_id=?", (project_id,)
                ).fetchone()[0]
                symbol_count = conn.execute(
                    "SELECT COUNT(*) FROM symbols WHERE project_id=?", (project_id,)
                ).fetchone()[0]
                languages = {
                    r[0]: r[1]
                    for r in conn.execute(
                        "SELECT language,COUNT(*) FROM files WHERE project_id=? GROUP BY language ORDER BY language",
                        (project_id,),
                    )
                }
                stats = {
                    "project_id": project_id,
                    "indexed": len(changed),
                    "unchanged": len(sources) - len(changed),
                    "deleted": len(removed),
                    "file_count": file_count,
                    "symbol_count": symbol_count,
                    "search_index_version": INDEX_VERSION,
                    "graph_resolution_version": GRAPH_RESOLUTION_VERSION,
                    "search_index_refreshed": (
                        len(sources) - len(changed) if refresh_search else 0
                    ),
                    "languages": languages,
                    "ignored": len(ignored),
                    "ignored_files": ignored,
                    "errors": errors[:200],
                    "partial": any("resource limit" in e["error"] for e in errors),
                    "limits": {"max_files": MAX_INDEXED_FILES, "max_total_bytes": MAX_INDEX_BYTES},
                    "branch": branch,
                    "git_state": git_state,
                }
                conn.execute(
                    "UPDATE projects SET branch=?,git_state=?,indexed_at=?,index_stats=? WHERE id=?",
                    (branch, json.dumps(git_state), now, json.dumps(stats), project_id),
                )
            if changed or removed or full or project["indexed_at"] is None:
                self.db.event(
                    project_id,
                    None,
                    "repository_indexed",
                    {
                        "indexed": len(changed),
                        "deleted": len(removed),
                        "file_count": file_count,
                        "errors": len(errors),
                    },
                )
                for path in sorted(modified | added):
                    self.db.event(
                        project_id,
                        None,
                        "file_changed",
                        {"path": path, "deleted": path in removed, "added": path in added},
                    )
                if modified:
                    self.db.event(
                        project_id, None, "context_invalidated", {"paths": sorted(modified)}
                    )
            return stats

    @staticmethod
    def _has_head(root: Path) -> bool:
        try:
            _git(root, "rev-parse", "--verify", "HEAD")
            return True
        except DomainError:
            return False

    @staticmethod
    def _invalidate(conn: Any, project_id: str, paths: set[str]) -> None:
        affected_memories: dict[str, set[str]] = {}
        for path in paths:
            for row in conn.execute(
                "SELECT ms.memory_id FROM memory_sources ms JOIN memories m ON m.id=ms.memory_id JOIN sessions s ON s.id=m.session_id WHERE s.project_id=? AND ms.path=?",
                (project_id, path),
            ):
                affected_memories.setdefault(row["memory_id"], set()).add(path)
            conn.execute(
                "UPDATE memories SET stale=1 WHERE id IN (SELECT ms.memory_id FROM memory_sources ms JOIN memories m ON m.id=ms.memory_id JOIN sessions s ON s.id=m.session_id WHERE s.project_id=? AND ms.path=?)",
                (project_id, path),
            )
        for row in conn.execute(
            "SELECT p.retrieval_id,p.data FROM passports p JOIN retrievals r ON r.id=p.retrieval_id WHERE r.project_id=?",
            (project_id,),
        ):
            data = json.loads(row["data"])
            # A path mentioned in a query, warning, dependency, or another
            # filename is not selected source evidence. Compare the exact
            # references, including retained legacy passport representations.
            referenced = {
                file if isinstance(file, str) else file["path"]
                for file in data.get("selected_files", [])
            }
            referenced.update(data.get("verified_source_hashes", {}))
            referenced.update(symbol["path"] for symbol in data.get("selected_symbols", []))
            for memory_id in data.get("selected_memory_ids", []):
                referenced.update(affected_memories.get(memory_id, set()))
            affected = sorted(paths & referenced)
            if affected:
                data["status"] = "Stale"
                data["source_freshness"] = "Stale"
                data["stale_files"] = sorted(set(data.get("stale_files", [])) | set(affected))
                data["missing_context"] = list(
                    dict.fromkeys(
                        [
                            *data.get("missing_context", []),
                            *(f"Source changed: {p}" for p in affected),
                        ]
                    )
                )
                conn.execute(
                    "UPDATE passports SET data=? WHERE retrieval_id=?",
                    (json.dumps(data), row["retrieval_id"]),
                )

    @staticmethod
    def _resolve(conn: Any, project_id: str) -> None:
        files = {
            row["path"]: dict(row)
            for row in conn.execute("SELECT * FROM files WHERE project_id=?", (project_id,))
        }
        symbols = [
            dict(row)
            for row in conn.execute("SELECT * FROM symbols WHERE project_id=?", (project_id,))
        ]
        by_path: dict[str, list[dict[str, Any]]] = {}
        by_id = {s["id"]: s for s in symbols}
        for symbol in symbols:
            by_path.setdefault(symbol["path"], []).append(symbol)
        edges = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM dependencies WHERE project_id=? ORDER BY id", (project_id,)
            )
        ]
        # Imports are scoped. Ambiguous or external modules intentionally remain unresolved.
        bindings: dict[tuple[str, str | None, str], tuple[str | None, str | None]] = {}

        def module_file(source: str, module: str, lang: str) -> str | None:
            candidates: list[str] = []
            if lang == "python":
                level = len(module) - len(module.lstrip("."))
                suffix = module.lstrip(".").replace(".", "/")
                if level:
                    base = PurePosixPath(source).parent
                    for _ in range(level - 1):
                        if str(base) == ".":
                            return None
                        base = base.parent
                    stem = str(base / suffix) if suffix else str(base)
                    stems = [stem.removeprefix("./")]
                else:
                    stems = [suffix, "src/" + suffix]
                for stem in stems:
                    candidates.extend([stem + ".py", stem + "/__init__.py", stem + ".pyi"])
            else:
                if not module.startswith("."):
                    return None
                stem_parts: list[str] = list(PurePosixPath(source).parent.parts)
                for part in PurePosixPath(module).parts:
                    if part == "..":
                        if not stem_parts:
                            return None
                        stem_parts.pop()
                    elif part != ".":
                        stem_parts.append(part)
                stem = "/".join(stem_parts)
                candidates.append(stem)
                bare = (
                    str(PurePosixPath(stem).with_suffix(""))
                    if PurePosixPath(stem).suffix in {".js", ".jsx", ".mjs"}
                    else stem
                )
                candidates.extend(
                    bare + suffix
                    for suffix in (
                        ".ts",
                        ".tsx",
                        ".js",
                        ".jsx",
                        ".mjs",
                        ".mts",
                        "/index.ts",
                        "/index.tsx",
                        "/index.js",
                    )
                )
            hits = sorted({p for p in candidates if p in files})
            # Prefer an exact extension explicitly imported by JS rather than guessing.
            if lang != "python" and candidates[0] in files:
                return candidates[0]
            return hits[0] if len(hits) == 1 else None

        def named(path: str | None, name: str | None, exported: bool = False) -> str | None:
            if not path or not name or name == "*":
                return None
            options = [
                s
                for s in by_path.get(path, [])
                if s["name"] == name
                and "." not in s["qualified_name"]
                and (not exported or s["exported"])
            ]
            if name == "default":
                options = [
                    s
                    for s in by_path.get(path, [])
                    if s["exported"] and "." not in s["qualified_name"]
                ]
                # A sole exported declaration is not proof that it is the default export.
                # Tree-sitter marks default declarations in signature using their original parent.
                options = [s for s in options if s["signature"].startswith("default ")]
            return options[0]["id"] if len(options) == 1 else None

        for edge in edges:
            if edge["kind"] not in {"import", "export"}:
                continue
            parts = import_parts(files[edge["source_file"]]["language"], edge["reference"])
            if not parts:
                continue
            module, name, alias = parts
            lang = files[edge["source_file"]]["language"]
            target = module_file(edge["source_file"], module, lang)
            target_symbol = named(target, name, exported=lang != "python")
            if target_symbol is None and lang == "python" and name and name != "*":
                submodule = module_file(
                    edge["source_file"], module + ("" if module.endswith(".") else ".") + name, lang
                )
                if submodule:
                    target = submodule
            if alias:
                binding_target = target
                if (
                    lang == "python"
                    and name is None
                    and "." in module
                    and " as " not in edge["reference"]
                ):
                    binding_target = module_file(edge["source_file"], module.split(".")[0], lang)
                binding_key = (edge["source_file"], edge["source_symbol"], alias)
                binding_value = (binding_target, target_symbol)
                if binding_key in bindings and bindings[binding_key] != binding_value:
                    bindings[binding_key] = (None, None)
                else:
                    bindings[binding_key] = binding_value
            resolved = bool(
                target
                and (
                    name is None
                    or name == "*"
                    or target_symbol
                    or (lang == "python" and PurePosixPath(target).stem == name)
                )
            )
            conn.execute(
                "UPDATE dependencies SET target_file=?,target_symbol=?,resolved=? WHERE id=?",
                (target, target_symbol, int(resolved), edge["id"]),
            )
        for edge in edges:
            if not edge["kind"].startswith("call"):
                continue
            target = None
            target_symbol = None
            reference = edge["reference"]
            if edge["kind"] == "call" and re.fullmatch(
                r"[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?", reference
            ):
                first, _, attr = reference.partition(".")
                binding = bindings.get(
                    (edge["source_file"], edge["source_symbol"], first)
                ) or bindings.get((edge["source_file"], None, first))
                if binding:
                    target, target_symbol = binding
                    if attr and target_symbol is None:
                        target_symbol = named(
                            target,
                            attr,
                            exported=files[edge["source_file"]]["language"] != "python",
                        )
                elif not attr:
                    current = by_id.get(edge["source_symbol"], {}).get("qualified_name", "")
                    scope = current.split(".")
                    while scope:
                        qualified = ".".join([*scope, first])
                        hits = [
                            s
                            for s in by_path.get(edge["source_file"], [])
                            if s["qualified_name"] == qualified
                            and not (
                                files[edge["source_file"]]["language"] == "python"
                                and s["kind"] == "method"
                            )
                        ]
                        if len(hits) == 1:
                            target_symbol = hits[0]["id"]
                            break
                        scope.pop()
                    if target_symbol is None:
                        target_symbol = named(edge["source_file"], first)
                    if target_symbol:
                        target = edge["source_file"]
            conn.execute(
                "UPDATE dependencies SET target_file=?,target_symbol=?,resolved=? WHERE id=?",
                (target, target_symbol, int(target_symbol is not None), edge["id"]),
            )

    def _candidate(
        self,
        project: dict[str, Any],
        row: dict[str, Any],
        score: float,
        reason: str,
        *,
        snippet_limit: int | None = None,
    ) -> dict[str, Any] | None:
        try:
            content, digest = read_source(
                project["path"], row["path"], self.db.settings()["max_file_size"]
            )
        except (DomainError, OSError):
            return None
        if digest != row["hash"]:
            return None  # Never serialize obsolete line ranges after a concurrent source edit.
        start = row.get("start_line", 1)
        end = row.get("end_line", len(content.splitlines()) or 1)
        snippet = "\n".join(content.splitlines()[start - 1 : end])
        truncated = snippet_limit is not None and len(snippet) > snippet_limit
        if truncated:
            snippet = snippet[:snippet_limit]
            reason += "; search excerpt truncated; use get_symbol with full_source_reference for complete evidence"
        name = row.get("name", PurePosixPath(row["path"]).name)
        return {
            **row,
            "symbol": row.get("qualified_name", name),
            "name": name,
            "signature": row.get("signature", ""),
            "kind": row.get("kind", "file"),
            "start_line": start,
            "end_line": end,
            "score": round(score, 4),
            "reason": reason,
            "snippet": snippet,
            "snippet_start_line": start,
            "snippet_end_line": start + max(len(snippet.splitlines()) - 1, 0),
            "snippet_truncated": truncated,
            "full_source_available": True,
            "full_source_reference": row["id"] if "file_id" in row else row["path"],
            "current": True,
            "freshness": "Current",
            "structural": bool(row["structural"]),
        }

    def search(
        self, project_id: str, query: str, limit: int = 20, *, refresh: bool = True
    ) -> list[dict[str, Any]]:
        return self._search(project_id, query, limit, refresh=refresh, metadata_only=False)

    def _search_context_candidates(
        self, project_id: str, query: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Internal index metadata; ContextEngine must verify selected source bytes.

        Search ranking needs indexed declarations, not repeated source snippets.
        This still refreshes the index and never labels metadata Current.
        """
        return self._search(project_id, query, limit, refresh=True, metadata_only=True)

    @staticmethod
    def _context_candidate(row: dict[str, Any], score: float, reason: str) -> dict[str, Any]:
        name = row.get("name", PurePosixPath(row["path"]).name)
        return {
            **row,
            "symbol": row.get("qualified_name", name),
            "name": name,
            "signature": row.get("signature", ""),
            "kind": row.get("kind", "file"),
            "start_line": row.get("start_line", 1),
            "end_line": row.get("end_line"),
            "score": round(score, 4),
            "reason": reason,
            "structural": bool(row["structural"]),
        }

    def _search(
        self,
        project_id: str,
        query: str,
        limit: int,
        *,
        refresh: bool,
        metadata_only: bool,
        distinct_files: bool = False,
        file_scope: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        self.db.project(project_id)
        if not query.strip():
            return []
        if not 1 <= limit <= 100:
            raise DomainError("Search limit must be between 1 and 100")
        if len(query) > 4000:
            raise DomainError("Search query is too long")
        if refresh:
            self.reindex(project_id)
        project = self.db.project(project_id)
        if file_scope is not None and (
            not isinstance(file_scope, tuple) or len(file_scope) > MAX_INDEXED_FILES
            or any(not isinstance(path, str) or not path or len(path) > 4096 for path in file_scope)
            or len(set(file_scope)) != len(file_scope)
        ):
            raise DomainError("Invalid private search scope")
        if file_scope == ():
            return []

        def scope(column: str) -> tuple[str, tuple[str, ...]]:
            if file_scope is None:
                return "", ()
            return " AND " + column + " IN (" + ",".join("?" for _ in file_scope) + ")", file_scope

        weights = self.db.settings().get(
            "retrieval_weights",
            {
                "exact_symbol": 120.0,
                "identifier": 35.0,
                "symbol_path": 45.0,
                "signature": 8.0,
                "file_path": 70.0,
                "path_terms": 30.0,
                "full_text": 10.0,
            },
        )
        focus = search_focus(query)
        words = set(_tokens(focus))
        preferred_role = preferred_source_role(query)
        exact = query.strip().lower()
        # Use document frequency from this project, rather than allowing a common
        # class noun to outweigh several rarer task terms. FTS is parameterized and
        # the tokenizer never passes query operators through to SQLite.
        expressions = {
            word: "(" + " OR ".join(f'"{form}"' for form in term_variants(word)) + ")"
            for word in sorted(words)
        }
        term_weights: dict[str, float] = {}
        with self.db.connect() as conn:
            conn.execute("BEGIN")
            document_count = conn.execute(
                "SELECT count(*) FROM files WHERE project_id=?", (project_id,)
            ).fetchone()[0]
            for word, frequency in self._document_frequencies(
                conn, project_id, expressions
            ).items():
                if frequency:
                    term_weights[word] = math.log1p(
                        (document_count - frequency + 0.5) / (frequency + 0.5)
                    )
        total_weight = sum(term_weights.values()) or 1.0

        def overlap(value: str) -> float:
            return sum(term_weights.get(word, 0) for word in words & set(_tokens(value))) / (
                total_weight
            )

        candidates: list[tuple[float, str, dict[str, Any]]] = []
        requested_scores: dict[str, float] = {}

        def role_score(
            path: str, score: float, reasons: list[str], requested: bool = False
        ) -> float:
            role = source_role(path)
            if preferred_role in {"tests", "documentation"} and role == preferred_role and score:
                reasons.append("matches the requested source role")
                return score + weights["path_terms"]
            if (
                not preferred_role
                or role == preferred_role
                or requested
                or explicit_path(query, path)
            ):
                return score
            factor = 0.65 if role == "tests" else 0.45
            reasons.append("secondary source role for the requested task")
            return score * factor

        symbol_scope, scope_params = scope("s.path")
        rows = self.db.rows(
            "SELECT s.*,f.hash,f.language,f.structural FROM symbols s JOIN files f ON f.id=s.file_id WHERE s.project_id=?"
            + symbol_scope + " ORDER BY s.path,s.start_line,s.id",
            (project_id, *scope_params),
        )
        for row in rows:
            score = 0.0
            reasons = []
            requested = False
            if exact in {row["name"].lower(), row["qualified_name"].lower(), row["id"]}:
                score += weights["exact_symbol"]
                reasons.append("exact symbol match")
                requested = True
            elif explicit_identifier(query, row["name"], row["qualified_name"]):
                score += weights["exact_symbol"] * 0.625
                reasons.append("explicit symbol in query")
                requested = True
            identifier_overlap = overlap(row["name"])
            if identifier_overlap:
                score += weights["identifier"] * identifier_overlap
                reasons.append("matching identifier")
            if explicit_path(query, row["path"]):
                score += weights["symbol_path"]
                reasons.append("matching path")
            signature_overlap = overlap(row["signature"])
            if signature_overlap:
                score += weights["signature"] * signature_overlap
                reasons.append("matching signature")
            score = role_score(row["path"], score, reasons, requested)
            if score:
                candidates.append((score, "; ".join(reasons), row))
            if requested:
                requested_scores[row["id"]] = score
        if re.search(r"\b(call(?:s|ers)?|depend(?:s|ents|encies)?)\b", query.lower()):
            matched_ids = set(requested_scores)
            if matched_ids:
                graph_scope, graph_params = scope("source_file")
                graph = self.db.rows(
                    "SELECT * FROM dependencies WHERE project_id=? AND resolved=1"
                    + graph_scope + " ORDER BY source_file,id",
                    (project_id, *graph_params),
                )
                caller_ids = {
                    edge["source_symbol"]
                    for edge in graph
                    if edge["target_symbol"] in matched_ids and edge["source_symbol"]
                }
                caller_score = max(requested_scores.values()) + weights["exact_symbol"] / 12
                for row in rows:
                    if row["id"] in caller_ids and caller_score > 0:
                        candidates.append(
                            (
                                caller_score,
                                "resolved caller of requested symbol",
                                row,
                            )
                        )
        fts_rows: dict[str, float] = {}
        if words:
            # Every term participates in the identifier/path field scores. Bound
            # expensive BM25 candidate generation to informative terms selected
            # by project document frequency, rather than prompt position.
            ranked_terms = sorted(term_weights, key=lambda word: (-term_weights[word], word))
            parts = [expressions[word] for word in ranked_terms[:MAX_FTS_RANK_TERMS]]
            for offset in range(0, len(parts), FTS_QUERY_BATCH_SIZE):
                fts = " OR ".join(parts[offset : offset + FTS_QUERY_BATCH_SIZE])
                fts_scope, fts_params = scope("path")
                for row in self.db.rows(
                    "SELECT path,bm25(file_search,0.0,3.0,2.0,1.0) AS rank FROM file_search WHERE file_search MATCH ? AND project_id=?"
                    + fts_scope + " ORDER BY rank,path LIMIT 100",
                    (fts, project_id, *fts_params),
                ):
                    fts_rows[row["path"]] = fts_rows.get(row["path"], 0) - row["rank"]
        file_clause, file_params = scope("path")
        for row in self.db.rows(
            "SELECT * FROM files WHERE project_id=?" + file_clause + " ORDER BY path",
            (project_id, *file_params),
        ):
            score = 0.0
            reasons = []
            if explicit_path(query, row["path"]):
                score += weights["file_path"]
                reasons.append("matching file path")
            path_overlap = overlap(row["path"])
            if path_overlap:
                score += weights["path_terms"] * path_overlap
                reasons.append("matching path terms")
            if row["path"] in fts_rows:
                relevance = fts_rows[row["path"]]
                score += weights["full_text"] * (1 + 4 * relevance / (1 + relevance))
                reasons.append("full-text BM25 match")
            score = role_score(row["path"], score, reasons)
            if score:
                candidates.append((score, "; ".join(reasons), row))
        candidates.sort(
            key=lambda item: (
                -item[0],
                item[2]["path"],
                item[2].get("start_line", 0),
                item[2]["id"],
            )
        )
        file_evidence: dict[str, set[str]] = {}
        if distinct_files:
            # Group evidence without summing symbol scores: a large file must
            # not rank higher merely because it declares more symbols. Retain
            # independent lexical support if a file/BM25 row wins over a symbol.
            for _, _, row in candidates:
                value = " ".join(str(row.get(key, "")) for key in ("path", "name", "signature"))
                file_evidence.setdefault(row["path"], set()).update(words & set(_tokens(value)))
        output = []
        returned: set[str] = set()
        returned_paths: set[str] = set()
        for score, reason, row in candidates:
            if row["id"] in returned or (distinct_files and row["path"] in returned_paths):
                continue
            candidate = (
                self._context_candidate(row, score, reason)
                if metadata_only
                else self._candidate(project, row, score, reason, snippet_limit=1600)
            )
            if candidate:
                if distinct_files:
                    candidate["ranking_evidence_terms"] = sorted(file_evidence[row["path"]])
                output.append(candidate)
                returned.add(row["id"])
                returned_paths.add(row["path"])
            if len(output) == limit:
                break
        return output

    def get_symbol(self, project_id: str, symbol: str, *, refresh: bool = True) -> dict[str, Any]:
        return self._get_symbol(project_id, symbol, refresh=refresh, metadata_only=False)

    def _get_context_candidate(self, project_id: str, symbol: str) -> dict[str, Any]:
        """Resolve indexed metadata without emitting unverified source evidence."""
        return self._get_symbol(project_id, symbol, refresh=False, metadata_only=True)

    def _get_symbol(
        self, project_id: str, symbol: str, *, refresh: bool, metadata_only: bool
    ) -> dict[str, Any]:
        project = self.db.project(project_id)
        if refresh:
            self.reindex(project_id)
        rows = self.db.rows(
            "SELECT s.*,f.hash,f.language,f.structural FROM symbols s JOIN files f ON f.id=s.file_id WHERE s.project_id=? AND (s.id=? OR s.qualified_name=? OR s.name=? OR s.path||':'||s.qualified_name=?) ORDER BY s.path,s.start_line",
            (project_id, symbol, symbol, symbol, symbol),
        )
        if not rows:
            row = self.db.one(
                "SELECT * FROM files WHERE project_id=? AND path=?", (project_id, symbol)
            )
            if row:
                rows = [row]
        if not rows:
            raise DomainError("Symbol or indexed file was not found", 404)
        exact_ids = [r for r in rows if r["id"] == symbol]
        if exact_ids:
            rows = exact_ids
        if len(rows) > 1:
            raise DomainError("Symbol is ambiguous; use its ID or path:qualified_name", 409)
        if metadata_only:
            return self._context_candidate(rows[0], 120, "explicit source reference")
        candidate = self._candidate(project, rows[0], 120, "explicit source reference")
        if not candidate:
            raise DomainError(
                "Source changed during retrieval; retry against its current version", 409
            )
        return candidate

    def dependencies(
        self, project_id: str, symbol_or_path: str, direction: str = "both", *, refresh: bool = True
    ) -> list[dict[str, Any]]:
        return self._dependencies(
            project_id, symbol_or_path, direction, refresh=refresh, metadata_only=False
        )

    def _context_dependencies(
        self, project_id: str, symbol_or_path: str, direction: str = "both"
    ) -> list[dict[str, Any]]:
        return self._dependencies(
            project_id, symbol_or_path, direction, refresh=False, metadata_only=True
        )

    def _dependencies(
        self,
        project_id: str,
        symbol_or_path: str,
        direction: str,
        *,
        refresh: bool,
        metadata_only: bool,
    ) -> list[dict[str, Any]]:
        self.db.project(project_id)
        if direction not in {"both", "in", "out", "incoming", "outgoing", "callers", "callees"}:
            raise DomainError("Dependency direction must be both, incoming or outgoing")
        if refresh:
            self.reindex(project_id)
        file = self.db.one(
            "SELECT path FROM files WHERE project_id=? AND path=?", (project_id, symbol_or_path)
        )
        symbol = None
        if not file:
            symbol = self._get_symbol(
                project_id, symbol_or_path, refresh=False, metadata_only=metadata_only
            )
        target_reference = file["path"] if file else (symbol or {})["id"]
        clauses = []
        params: list[Any] = [project_id]
        if direction in {"both", "out", "outgoing", "callees"}:
            clauses.append("source_file=?" if file else "source_symbol=?")
            params.append(target_reference)
        if direction in {"both", "in", "incoming", "callers"}:
            clauses.append("target_file=?" if file else "target_symbol=?")
            params.append(target_reference)
        rows = self.db.rows(
            "SELECT * FROM dependencies WHERE project_id=? AND ("
            + " OR ".join(clauses)
            + ") ORDER BY source_file,kind,reference,id",
            tuple(params),
        )
        return [
            {
                **row,
                "resolved": bool(row["resolved"]),
                "confidence": "verified static relationship"
                if row["resolved"]
                else "unresolved reference",
            }
            for row in rows
        ]
