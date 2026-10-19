"""V4 bounded production retrieval and conservative lexical upper bounds.

This opt-in phase is not a semantic relevance oracle. It may discard a candidate
only when its entire verified body cannot supply v3's clean-term/anchor evidence.
Literal/comment matches are retained as false positives. All inspected versions,
including rejected and unsupported competitors, are guarded until delivery.
"""
from __future__ import annotations

import re
import time
import unicodedata
from pathlib import PurePosixPath
from typing import Any, Iterator

from memglide.integrations.source_evidence import (
    MAX_EVIDENCE_BYTES,
    EvidenceDeclined,
    _lexical_terms,
)

MAX_COARSE_FILES = 100
_SCOPE = "supported-production-lexical-upper-bound-v1"


def empty_diagnostics() -> dict[str, Any]:
    return {"version": 1, "scope": _SCOPE, "supported_production_files": 0,
            "unsupported_production_files": 0, "coarse_files_checked": 0,
            "coarse_bytes": 0, "potential_supported_files": 0, "weak_supported_files": 0,
            "potential_unsupported_files": 0, "weak_unsupported_files": 0,
            "nonproduction_parse_errors_accepted": 0, "coarse_wall_seconds": 0.0,
            "scope_complete": False, "frontier": [], "frontier_omitted": 0}


def parse_error_guard(reader: Any, project_id: str, stats: dict[str, Any]) -> dict[str, str]:
    """Allow only exhaustively recorded, known nonproduction syntax diagnostics.

    Scan/read/policy/resource failures are never exempted. A 200-entry report may
    be truncated, so it is rejected. Matching file rows alone do not establish
    current bytes: the coarse phase and final delivery both attest their hashes.
    """
    from memglide.integrations.auto_preload import _production

    errors = stats.get("errors")
    if stats.get("partial") or not isinstance(errors, list) or len(errors) >= 200:
        raise EvidenceDeclined("incomplete_index")
    rows = reader.rows("SELECT path,hash,parse_error FROM files WHERE project_id=? "
                       "AND parse_error IS NOT NULL ORDER BY path", (project_id,))
    if len(rows) != len(errors):
        raise EvidenceDeclined("incomplete_index")
    reported = set()
    for item in errors:
        if (not isinstance(item, dict) or set(item) != {"path", "error"}
            or not isinstance(item["path"], str) or not isinstance(item["error"], str)):
            raise EvidenceDeclined("incomplete_index")
        reported.add((item["path"], item["error"]))
    if len(reported) != len(errors):
        raise EvidenceDeclined("incomplete_index")
    result = {}
    for row in rows:
        message = row["parse_error"]
        if (_production(row["path"]) or (row["path"], message) not in reported
            or not isinstance(message, str)
            or not (message.startswith("Python parse error: ") or message ==
                    "Tree-sitter found syntax errors; partial structural results require inspection")
            or not isinstance(row["hash"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["hash"])):
            raise EvidenceDeclined("incomplete_index")
        result[row["path"]] = row["hash"]
    return result


def _identifier_runs(text: str) -> Iterator[str]:
    """Identifier superset, including XID combining marks and JS joiners."""
    start: int | None = None
    for index, char in enumerate(text):
        included = (char.isalnum() or char in "_$#" or (not char.isascii() and (
            unicodedata.category(char) in {"Mn", "Mc", "Pc", "Cf"}
            or ("a" + char).isidentifier())))
        if included and start is None:
            start = index
        elif not included and start is not None:
            yield text[start:index]
            start = None
    if start is not None:
        yield text[start:]


def lexical_upper_bound(path: str, body: str, query: str, terms: set[str]) -> tuple[bool, str]:
    """Overapproximate v3 syntax matches, including normalization and syntax facts.

    Python AST NFKC-normalizes names. Native pattern names may contain syntax,
    so a query containing an array/object pattern is conservatively retained.
    Raw comments/literals are intentionally included; they cannot create a false
    negative here, and the later syntax worker cannot accept them as clean code.
    """
    from memglide.core.query import explicit_identifier, explicit_path

    normalized = unicodedata.normalize("NFKC", body)
    matches = _lexical_terms(body, terms) | _lexical_terms(normalized, terms)
    if PurePosixPath(path).suffix.casefold() in {".py", ".pyi"} and "*" in body:
        matches.update(_lexical_terms("positional keyword argument", terms))
    if (explicit_path(query, path) or any(char in query for char in "[{")
        or "\\" in query and "\\" in body):
        return True, "possible_explicit_anchor"
    # Native numeric property names may be explicitly matched after a core
    # boundary within a longer dotted query token (foo.1.0 or #1.0). Do not
    # require a maximal query token to equal that numeric name.
    if "." in body and re.search(r"\d[\d_]*\.|\.[\d_]*\d", query):
        return True, "possible_explicit_anchor"
    if len(matches) >= 2:
        return True, "two_term_upper_bound"
    # Query-bounded names avoid retaining or classifying every source token.
    # A source name may be shorter than the task filter (e.g. x()). Substring
    # checks intentionally overapproximate identifier boundaries in source.
    quoted = re.findall(r"([\"\'`])([^\r\n]{0,4000}?)\1", query)
    if any((value or quote * 2) in body or (value or quote * 2) in normalized
           for quote, value in quoted):
        return True, "possible_explicit_anchor"
    for name in (set(_identifier_runs(query)) | set(re.findall(r"[\w$]+", query))
                 | set(re.findall(r"[\w$#.]+", query))):
        if explicit_identifier(query, name, name) and (name in body or name in normalized):
            return True, "possible_explicit_anchor"
    return False, "insufficient_upper_bound"


def discover_scoped_candidates(
    reader: Any, project_id: str, query: str, terms: set[str], selection: dict[str, Any],
    parse_guard: dict[str, str], diagnostics: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    """Filter before retrieval caps, then attest every bounded coarse competitor.

    Coarse body rows (production plus exempt syntax-error controls) share a
    100-file/2MiB cap. Only at most24 potential supported files reach v3 AST
    inspection. Unsupported potential competitors cause abstention. The returned
    boolean records candidate-generation saturation without concealing it.
    """
    from memglide.core.indexer import Indexer
    from memglide.integrations.auto_preload import _production
    from memglide.integrations.preload import _eligible
    from memglide.integrations.runtime_syntax import LANGUAGES
    from memglide.security.paths import read_source

    started = time.perf_counter()
    try:
        rows = reader.rows("SELECT path,hash,size FROM files WHERE project_id=? ORDER BY path", (project_id,))
        files = {row["path"]: row for row in rows}
        supported = tuple(path for path in files if _production(path) and
                          PurePosixPath(path).suffix.casefold() in LANGUAGES)
        unsupported = tuple(path for path in files if _production(path) and
                            PurePosixPath(path).suffix.casefold() not in LANGUAGES)
        diagnostics["supported_production_files"] = len(supported)
        diagnostics["unsupported_production_files"] = len(unsupported)
        candidates = Indexer(reader)._search(  # type: ignore[arg-type]
            project_id, query, MAX_COARSE_FILES, refresh=False, metadata_only=True,
            distinct_files=True, file_scope=supported)
        if len(candidates) == MAX_COARSE_FILES:
            return candidates, {}, True
        originals = {item["path"]: item for item in candidates}
        production_paths = tuple(sorted({*originals, *unsupported}))
        paths = tuple(sorted({*production_paths, *parse_guard}))
        if len(paths) > MAX_COARSE_FILES:
            raise EvidenceDeclined("coarse_candidate_limit")
        if (any(path not in files or type(files[path]["size"]) is not int or files[path]["size"] < 0
                for path in paths)
            or sum(files[path]["size"] for path in paths) > MAX_EVIDENCE_BYTES):
            raise EvidenceDeclined("coarse_source_budget")
        policy = _eligible(selection, paths)
        versions = {}
        potential = []
        deadline = time.perf_counter() + 2.0
        # Exempt parser diagnostics must first prove their exact source version.
        for path in (*sorted(parse_guard), *production_paths):
            if time.perf_counter() > deadline:
                raise EvidenceDeclined("coarse_time_limit")
            body, digest = read_source(selection["root"], path,
                                       min(selection["max_size"], MAX_EVIDENCE_BYTES - diagnostics["coarse_bytes"]))
            diagnostics["coarse_bytes"] += len(body.encode("utf-8"))
            if digest != files[path]["hash"] or (path in parse_guard and digest != parse_guard[path]):
                raise EvidenceDeclined("ranking_source_changed")
            versions[path] = digest
            if path in parse_guard:
                diagnostics["nonproduction_parse_errors_accepted"] += 1
                continue
            possible, reason = lexical_upper_bound(path, body, query, terms)
            if time.perf_counter() > deadline:
                raise EvidenceDeclined("coarse_time_limit")
            is_supported = path in originals
            key = ("potential_" if possible else "weak_") + ("supported_files" if is_supported else "unsupported_files")
            diagnostics[key] += 1
            diagnostics["coarse_files_checked"] += 1
            if len(diagnostics["frontier"]) < 4:
                diagnostics["frontier"].append({"path": path, "sha256": digest, "classification":
                    ("potential_supported" if is_supported else "potential_unsupported") if possible else
                    "lexically_impossible", "reason": reason})
            else:
                diagnostics["frontier_omitted"] += 1
            if possible and is_supported:
                potential.append(originals[path])
        diagnostics["scope_complete"] = True
        guard = {"versions": versions, "policy": policy, "paths": paths, "selection": selection}
        if diagnostics["potential_unsupported_files"]:
            raise EvidenceDeclined("unsupported_competitor")
        if len(potential) > 24:
            raise EvidenceDeclined("evidence_candidate_limit")
        return potential, guard, False
    finally:
        diagnostics["coarse_wall_seconds"] = time.perf_counter() - started
