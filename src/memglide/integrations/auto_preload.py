"""Opt-in deterministic task discovery, complete-source delivery, and abstention.

No memory or model call participates in selection. The existing explicit source
preparer remains responsible for source delivery. Ranking scores and byte-based
token estimates are heuristics, never probabilities or avoided-work measurements.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import time
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

MAX_ADDED_TOKENS = 85_334
_MAX_FILES = 20_000
_MAX_SYMBOLS = 100_000
_MAX_DEPENDENCIES = 200_000
_MAX_ROWS_BYTES = 16 * 1024 * 1024
_MAX_CANDIDATES = 100
_MAX_HELPERS = 3
_PRODUCTION_SUFFIXES = frozenset(
    ".py .pyi .js .mjs .cjs .jsx .ts .tsx .go .rs .java .c .h .cc .cpp .hpp "
    ".cs .rb .php .swift .kt .kts .scala .vue .svelte .sh .sql".split()
)
_NONPRODUCTION_PARTS = frozenset(
    "test tests __tests__ spec specs fixture fixtures __fixtures__ docs documentation "
    "examples example benchmarks benchmark vendor third_party generated".split()
)
_GENERIC = frozenset(
    "improve optimize optimisation optimization performance faster efficient efficiency "
    "code source repository repo project codebase behavior behaviour change update "
    "correct bug error issue problem support handle add remove return value result "
    "make better work works working test tests check checks run fix please ensure "
    "function functions file files handled everything all anything something "
    "the their then there these they this those our you your will would could "
    "should have has had are was were been being not now just again done "
    "into its does can from with when that for and".split()
)
TOKEN_ESTIMATE_METHOD = (
    "ceil(UTF-8 added context bytes / 3); planning proxy, not measured usage"
)
_COVERAGE = "bounded direct resolved production targets; not global completeness"


class _Decline(ValueError):
    pass


def _production(path: str) -> bool:
    source = PurePosixPath(path)
    return (
        source.suffix.casefold() in _PRODUCTION_SUFFIXES
        and not set(part.casefold() for part in source.parts) & _NONPRODUCTION_PARTS
        and not source.name.casefold().startswith("test_")
        and not source.name.casefold().endswith("_test.py")
        and ".test." not in source.name.casefold()
        and ".spec." not in source.name.casefold()
        and source.name.casefold() not in {"conftest.py", "setup.py"}
    )


class _ReadIndex:
    """Read-only ranker facade; cumulative query, VM, row and payload bounds.

    TEMP vocabulary tables used by the production ranker are connection-local.
    No durable database creation, migration or source body reads occur here.
    """

    def __init__(self, path: Path):
        self.path = path
        self.deadline = time.perf_counter() + 2.0
        self.steps = 0
        self.row_bytes = 0
        self.row_count = 0

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, timeout=0.1)
        conn.row_factory = sqlite3.Row
        conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 512_000)

        def progress() -> int:
            self.steps += 1000
            return int(self.steps > 2_000_000 or time.perf_counter() > self.deadline)

        conn.set_progress_handler(progress, 1000)
        try:
            yield conn
        finally:
            conn.close()

    def rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        result = []
        with self.connect() as conn:
            for row in conn.execute(sql, params):
                value = dict(row)
                self.row_count += 1
                self.row_bytes += sum(
                    len(item.encode("utf-8")) for item in value.values() if isinstance(item, str)
                )
                if (
                    self.row_count > 250_000
                    or self.row_bytes > _MAX_ROWS_BYTES
                    or time.perf_counter() > self.deadline
                ):
                    raise _Decline("ranking_resource_limit")
                result.append(value)
        return result

    def one(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self.rows(sql, params)
        return rows[0] if rows else None

    def project(self, project_id: str) -> dict[str, Any]:
        project = self.one("SELECT * FROM projects WHERE id=?", (project_id,))
        if project is None:
            raise _Decline("project_unavailable")
        return project

    def settings(self) -> dict[str, Any]:
        from memglide.storage.database import DEFAULT_SETTINGS

        settings = {key: value for key, value in DEFAULT_SETTINGS.items()}
        for row in self.rows("SELECT key,value FROM settings"):
            settings[row["key"]] = json.loads(row["value"])
        weights = settings["retrieval_weights"]
        defaults = DEFAULT_SETTINGS["retrieval_weights"]
        if (
            not isinstance(weights, dict)
            or set(weights) != set(defaults)
            or any(
                type(value) not in {int, float} or not math.isfinite(value) or not 0 <= value <= 10000
                for value in weights.values()
            )
        ):
            raise _Decline("ranking_policy_unavailable")
        return settings


def _preflight(database: Path, project_id: str) -> None:
    index = _ReadIndex(database)
    index.project(project_id)
    index.settings()
    with index.connect() as conn:
        for table, cap in (
            ("files", _MAX_FILES),
            ("symbols", _MAX_SYMBOLS),
            ("dependencies", _MAX_DEPENDENCIES),
        ):
            count = conn.execute(
                f"SELECT count(*) FROM (SELECT 1 FROM {table} WHERE project_id=? LIMIT ?)",
                (project_id, cap + 1),
            ).fetchone()[0]
            if count > cap:
                raise _Decline("index_resource_limit")
        sizes = conn.execute(
            "SELECT sum(size) AS bytes, sum(CASE WHEN typeof(size)!='integer' OR size<0 "
            "THEN 1 ELSE 0 END) AS invalid FROM files WHERE project_id=?",
            (project_id,),
        ).fetchone()
        if sizes["invalid"] or (sizes["bytes"] or 0) > 100 * 1024 * 1024:
            raise _Decline("index_resource_limit")


def _existing_database(database: Path, identity: tuple[int, int]) -> Any:
    """Reuse index writes without ever creating, migrating or chmod'ing a DB."""
    from memglide.storage.database import Database

    class ExistingDatabase(Database):
        def __init__(self) -> None:
            self.path = database
            self._request_settings = ContextVar("automatic_preparation_settings", default=None)

        @contextmanager
        def connect(self) -> Iterator[sqlite3.Connection]:
            before = database.stat()
            if (before.st_dev, before.st_ino) != identity:
                raise _Decline("database_changed")
            conn = sqlite3.connect(database.as_uri() + "?mode=rw", uri=True, timeout=30)
            try:
                after = database.stat()
                if (after.st_dev, after.st_ino) != identity:
                    raise _Decline("database_changed")
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA busy_timeout=30000")
                with conn:
                    yield conn
            finally:
                conn.close()

    return ExistingDatabase()


def prepare_task_prompt(
    prompt: str,
    *,
    project_id: str | None = None,
    db_path: str | Path | None = None,
    enabled: bool = False,
    context_supplied: bool = False,
    mode: str = "auto",
    max_context_bytes: int = 12_000,
    context_format: str = "compact-prefix",
    max_added_tokens: int = 4_000,
    provided_sources: dict[str, str] | None = None,
    task_query: str | None = None,
) -> dict[str, Any]:
    """Discover from a task with no supplied paths, or return the exact original.

    FULL_SOURCE means an anchor plus its complete bounded direct production
    dependency bundle; it never means the whole repository. FOCUSED_SOURCE is a
    complete anchor without eligible direct production helpers. Static coverage
    does not establish semantic completeness. A full secure index refresh is
    included in preparation time. ``provided_sources`` may only name complete
    bodies actually present, together with their paths, in this very prompt.
    A wrapper may supply ``task_query`` to separate the actual task from its
    workflow text; it must be an exact, bounded substring of the delivered prompt.
    """
    from memglide.integrations.preload import prepare_prompt

    started = time.perf_counter()
    cpu_started = time.process_time()
    # Reuse strict argument validation without touching state or heavy imports.
    base = prepare_prompt(
        prompt,
        project_id=project_id,
        db_path=db_path,
        mode="off",
        context_supplied=context_supplied,
        max_context_bytes=max_context_bytes,
        context_format=context_format,
    )
    if type(enabled) is not bool:
        raise ValueError("enabled must be a boolean")
    if not isinstance(mode, str) or mode not in {"auto", "off", "preload"}:
        raise ValueError("mode must be auto, off, or preload")
    if type(max_added_tokens) is not int or not 1 <= max_added_tokens <= MAX_ADDED_TOKENS:
        raise ValueError(f"max_added_tokens must be between 1 and {MAX_ADDED_TOKENS}")
    if provided_sources is not None and (
        not isinstance(provided_sources, dict)
        or len(provided_sources) > 8
        or any(
            not isinstance(path, str)
            or not path
            or len(path) > 4096
            or not isinstance(body, str)
            or not body
            or len(body.encode("utf-8")) > 256_000
            for path, body in provided_sources.items()
        )
    ):
        raise ValueError("provided_sources must map at most eight paths to complete source bodies")
    if task_query is not None and (
        not isinstance(task_query, str)
        or not task_query.strip()
        or len(task_query.encode("utf-8")) > 4000
        or task_query not in prompt
    ):
        raise ValueError("task_query must be an exact nonempty prompt substring within 4000 bytes")
    query = prompt if task_query is None else task_query
    receipt: dict[str, Any] = {
        "version": 1,
        "policy_version": "deterministic-source-v1",
        "decision": "SKIP",
        "reason": "disabled",
        "selected_paths": [],
        "source_versions": {},
        "ranked_candidates": [],
        "estimated_added_tokens": 0,
        "token_estimate_method": TOKEN_ESTIMATE_METHOD,
        "discovery_wall_seconds": 0.0,
        "discovery_cpu_seconds": 0.0,
        "index_refresh_wall_seconds": 0.0,
        "retrieval_wall_seconds": 0.0,
        "source_preparation_wall_seconds": 0.0,
        "auxiliary_model_calls": 0,
        "provided_source_paths": [],
        "static_dependency_coverage": _COVERAGE,
        "candidate_files_considered": 0,
        "omitted_candidate_files": 0,
        "dependency_paths_considered": 0,
        "unresolved_dependency_count": 0,
        "candidate_generation_limit_reached": False,
        "index_refreshed": False,
    }
    phase = "preflight"
    phase_started = started

    def finish(reason: str, value: dict[str, Any] | None = None) -> dict[str, Any]:
        if phase in {"index_refresh", "retrieval", "source_preparation"}:
            receipt[phase + "_wall_seconds"] = time.perf_counter() - phase_started
        response = dict(base if value is None else value)
        response["reason"] = reason
        receipt["reason"] = reason
        response["preparation_wall_seconds"] = time.perf_counter() - started
        response["preparation_cpu_seconds"] = time.process_time() - cpu_started
        receipt["discovery_wall_seconds"] = response["preparation_wall_seconds"]
        receipt["discovery_cpu_seconds"] = response["preparation_cpu_seconds"]
        response["automatic_selection"] = receipt
        return response

    if not enabled or mode == "off":
        return finish("disabled")
    if context_supplied:
        return finish("context_supplied")
    if project_id is None:
        return finish("no_approved_project")
    if len(query.encode("utf-8")) > 4_000:
        return finish("task_query_limit")
    # This first gate is intentionally stdlib-only, before any DB/index work.
    import re

    lexical = {
        word.casefold()
        for word in re.findall(r"[^\W_]+", query)
        if len(word) > 2 and word.casefold() not in _GENERIC
    }
    lexical -= {"the", "and", "for", "with", "that", "this", "should", "when", "from"}
    if not lexical:
        return finish("insufficient_task_evidence")
    from memglide.core.indexer import Indexer
    from memglide.core.query import explicit_identifier, explicit_path, search_focus, tokens
    from memglide.integrations.preload import _eligible, _selection, _Unavailable
    from memglide.security.paths import read_source
    from memglide.storage.database import DomainError

    try:
        home = Path(os.environ.get("MEMGLIDE_HOME", Path.home() / ".memglide"))
        database = (Path(db_path) if db_path is not None else home / "memglide.db").absolute()
        database_stat = database.stat()
        database_identity = (database_stat.st_dev, database_stat.st_ino)
        initial_selection = _selection(database, project_id, ())
        _preflight(database, project_id)
        refreshed_at = time.perf_counter()
        phase, phase_started = "index_refresh", refreshed_at
        # Only an existing approved database is opened for normal indexing.
        db = _existing_database(database, database_identity)
        stats = Indexer(db).reindex(project_id)
        receipt["index_refresh_wall_seconds"] = time.perf_counter() - refreshed_at
        receipt["index_refreshed"] = True
        phase = "verification"
        if stats.get("partial") or stats.get("errors"):
            return finish("incomplete_index")
        if _selection(database, project_id, ()) != initial_selection:
            return finish("policy_changed")
        ranked_at = time.perf_counter()
        phase, phase_started = "retrieval", ranked_at
        reader = _ReadIndex(database)
        project_version = reader.project(project_id)
        ranking_settings = reader.settings()
        candidates = Indexer(reader)._search(  # type: ignore[arg-type]
            project_id,
            query,
            _MAX_CANDIDATES,
            refresh=False,
            metadata_only=True,
            distinct_files=True,
        )
        receipt["candidate_generation_limit_reached"] = len(candidates) == _MAX_CANDIDATES
        if receipt["candidate_generation_limit_reached"]:
            return finish("candidate_limit_reached")
        candidates = [item for item in candidates if _production(item["path"])]
        receipt["candidate_files_considered"] = len(candidates)
        terms = {
            term for term in tokens(search_focus(query)) if term not in _GENERIC and len(term) > 2
        }
        if not terms or len(terms) > 64 or any(len(term) > 128 for term in terms):
            return finish("insufficient_task_evidence")
        ranked = []
        for item in candidates:
            evidence = set(
                tokens(" ".join(str(item.get(key, "")) for key in ("path", "name", "signature")))
            )
            evidence.update(item.get("ranking_evidence_terms", ()))
            explicit = explicit_path(query, item["path"]) or explicit_identifier(
                query,
                item.get("name", ""),
                item.get("qualified_name") or item.get("name", ""),
            )
            matched = sorted(terms & evidence)
            ranked.append(
                {
                    "path": item["path"],
                    "score": item["score"],
                    "reason": item["reason"],
                    "evidence_terms": matched,
                    "explicit_anchor": explicit,
                }
            )
        receipt["ranked_candidates"] = ranked[:12]
        receipt["omitted_candidate_files"] = max(0, len(candidates) - 12)
        if not ranked:
            return finish("no_production_match")
        top = ranked[0]
        if not top["explicit_anchor"] and (
            len(top["evidence_terms"]) < 2
            or len(top["evidence_terms"]) / len(terms) < 0.30
        ):
            return finish("weak_lexical_evidence")
        anchor = candidates[0]
        edges = reader.rows(
            "SELECT * FROM dependencies WHERE project_id=? AND source_file=? "
            "ORDER BY target_file,id LIMIT 1001",
            (project_id, anchor["path"]),
        )
        if len(edges) > 1000:
            return finish("dependency_resource_limit")
        receipt["unresolved_dependency_count"] = sum(not edge["resolved"] for edge in edges)
        helpers = sorted(
            {
                edge["target_file"]
                for edge in edges
                if edge["resolved"]
                and edge["target_file"] is not None
                and edge["target_file"] != anchor["path"]
                and _production(edge["target_file"])
            }
        )
        receipt["dependency_paths_considered"] = len(helpers)
        if len(helpers) > _MAX_HELPERS:
            return finish("dependency_bundle_limit")
        # A close second independent module is ambiguity, not confidence.
        independent = [item for item in ranked[1:] if item["path"] not in helpers]
        if independent and independent[0]["score"] >= top["score"] * 0.82:
            return finish("ambiguous_candidates")
        paths = sorted({anchor["path"], *helpers})
        versions = {}
        for path in paths:
            row = reader.one(
                "SELECT hash FROM files WHERE project_id=? AND path=?", (project_id, path)
            )
            if row is None:
                return finish("ranking_source_unavailable")
            versions[path] = row["hash"]
        selection = _selection(database, project_id, tuple(paths))
        if selection != initial_selection:
            return finish("policy_changed")
        policy = _eligible(selection, tuple(paths))
        for path in paths:
            _, digest = read_source(selection["root"], path, selection["max_size"])
            if digest != versions[path]:
                return finish("ranking_source_changed")
        provided = provided_sources or {}
        for path, body in provided.items():
            if path not in paths or path not in prompt or body not in prompt:
                return finish("provided_source_unverified")
            if hashlib.sha256(body.encode("utf-8")).hexdigest() != versions[path]:
                return finish("provided_source_changed")
        receipt["provided_source_paths"] = sorted(provided)
        deliver = [path for path in paths if path not in provided]
        receipt["retrieval_wall_seconds"] = time.perf_counter() - ranked_at
        phase = "verification"
        response = base
        if deliver:
            prepared_at = time.perf_counter()
            phase, phase_started = "source_preparation", prepared_at
            response = prepare_prompt(
                prompt,
                project_id=project_id,
                db_path=database,
                focus_paths=deliver,
                max_context_bytes=min(max_context_bytes, max_added_tokens * 3),
                context_format=context_format,
            )
            receipt["source_preparation_wall_seconds"] = time.perf_counter() - prepared_at
            phase = "verification"
            if response["mode"] != "preloaded":
                return finish("source_preparation_" + response["reason"])
        # Preserve ranking versions and the original entire closure, including
        # complete bodies that the caller supplied in this actual prompt.
        if _selection(database, project_id, tuple(paths)) != selection:
            return finish("policy_changed")
        if _eligible(selection, tuple(paths)) != policy:
            return finish("policy_changed")
        final_reader = _ReadIndex(database)
        final_project = final_reader.project(project_id)
        if final_reader.settings() != ranking_settings:
            return finish("ranking_policy_changed")
        if any(
            final_project.get(key) != project_version.get(key)
            for key in ("path", "indexed_at", "index_stats")
        ):
            return finish("index_changed")
        for path in paths:
            _, digest = read_source(selection["root"], path, selection["max_size"])
            if digest != versions[path]:
                return finish("ranking_source_changed")
        if not deliver:
            return finish("source_already_provided")
        if any(item["sha256"] != versions[item["path"]] for item in response["files"]):
            return finish("ranking_source_changed")
        receipt["decision"] = "FULL_SOURCE" if helpers else "FOCUSED_SOURCE"
        receipt["selected_paths"] = [item["path"] for item in response["files"]]
        receipt["source_versions"] = {
            item["path"]: item["sha256"] for item in response["files"]
        }
        receipt["estimated_added_tokens"] = math.ceil(response["context_bytes"] / 3)
        return finish("automatic_verified_source", response)
    except _Decline as exc:
        return finish(str(exc))
    except _Unavailable as exc:
        return finish(str(exc))
    except (DomainError, sqlite3.Error, OSError, RuntimeError, ValueError, TypeError, RecursionError):
        return finish("discovery_unavailable")
