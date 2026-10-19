"""Bounded verified lexical evidence for the opt-in deterministic source router.

This ranks observed text, not program semantics. Code-like identifier scanning
removes comments and quoted strings but is deliberately not called execution or
dependency analysis. Static declarations and graph edges remain index evidence.
"""

from __future__ import annotations

import io
import json
import math
import re
import subprocess
import sys
import time
import tokenize
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

MAX_EVIDENCE_FILES = 24
MAX_EVIDENCE_BYTES = 2 * 1024 * 1024
_LEXICAL_LANGUAGES = frozenset({".py", ".pyi", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"})
_IDENTIFIER_BOUNDARIES = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])|(?<=[a-z0-9])(?=[A-Z])")
_WORDS = re.compile(r"[^\W_]+")


class EvidenceDeclined(ValueError):
    """Insufficient or unverified evidence; never a partial-candidate success."""


def _lexical_terms(value: str, query_terms: set[str] | None = None) -> set[str]:
    """Shared plural rules with fixed-width identifier splitting for large text.

    Applying the legacy greedy acronym-splitting regex to an entire adversarial
    uppercase source token can require repeated suffix scans. Fixed-width
    boundaries avoid that extra work without retaining all source terms.
    """
    from memglide.core.query import _STOP_WORDS, _singular

    value = re.sub(r"\b([A-Z]{2,})s\b", r"\1", value)
    value = _IDENTIFIER_BOUNDARIES.sub(" ", value)
    matched = set()
    for word in _WORDS.finditer(value.casefold()):
        raw = word.group()
        if raw in _STOP_WORDS:
            continue
        token = _singular(raw)
        if query_terms is None or token in query_terms:
            matched.add(token)
    return matched


def _native_identifier_terms(sources: dict[str, str], terms: set[str]) -> dict[str, set[str]]:
    """One isolated trusted syntax batch; startup and child work are not free."""
    from memglide.integrations import syntax_identifiers

    if not 1 <= len(sources) <= MAX_EVIDENCE_FILES or len(terms) > 64 or any(
        not isinstance(term, str) or not term or len(term) > 128 for term in terms
    ):
        raise EvidenceDeclined("source_native_input_limit")
    if sum(len(source.encode("utf-8")) for source in sources.values()) > MAX_EVIDENCE_BYTES:
        raise EvidenceDeclined("source_evidence_budget")
    payload = json.dumps({"sources": sources, "terms": sorted(terms)}, ensure_ascii=False)
    if len(payload.encode("utf-8")) > syntax_identifiers.MAX_PAYLOAD_BYTES:
        raise EvidenceDeclined("source_native_input_limit")
    try:
        completed = subprocess.run(
            [sys.executable, "-I", str(Path(syntax_identifiers.__file__).resolve()), "--worker"],
            input=payload, text=True, capture_output=True, timeout=5,
            cwd=Path(syntax_identifiers.__file__).resolve().parent,
        )
        if completed.returncode or len(completed.stdout.encode("utf-8")) > 256_000:
            raise EvidenceDeclined("source_native_worker_unavailable")

        def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate key")
                result[key] = value
            return result

        response = json.loads(completed.stdout, object_pairs_hook=unique)
        if (
            not isinstance(response, dict) or set(response) != {"version", "files"}
            or type(response["version"]) is not int or response["version"] != 1
            or not isinstance(response["files"], dict) or set(response["files"]) != set(sources)
            or any(
                not isinstance(matches, list) or len(matches) > len(terms)
                or any(not isinstance(term, str) or term not in terms for term in matches)
                or len(set(matches)) != len(matches)
                for matches in response["files"].values()
            )
        ):
            raise ValueError("Invalid syntax evidence")
        return {path: set(matches) for path, matches in response["files"].items()}
    except EvidenceDeclined:
        raise
    except (subprocess.SubprocessError, OSError, ValueError, TypeError, RecursionError) as exc:
        raise EvidenceDeclined("source_lexical_evidence_unavailable") from exc


def _code_like_terms(
    path: str, body: str, query_terms: set[str] | None = None, *, deadline: float | None = None
) -> set[str]:
    deadline = time.perf_counter() + 2.0 if deadline is None else deadline
    names: Iterator[str]
    if PurePosixPath(path).suffix.casefold() in {".py", ".pyi"}:
        def python_names() -> Iterator[str]:
            for index, item in enumerate(tokenize.generate_tokens(io.StringIO(body).readline)):
                if index % 1024 == 0 and time.perf_counter() > deadline:
                    raise EvidenceDeclined("source_evidence_time_limit")
                # Python 3.11 emits ERRORTOKEN for unclosed single quotes;
                # later supported versions may raise TokenError instead.
                if item.type == tokenize.ERRORTOKEN and not item.string.isspace():
                    raise EvidenceDeclined("source_lexical_evidence_unavailable")
                if item.type == tokenize.NAME:
                    yield item.string

        names = python_names()
    else:
        terms = _lexical_terms(body) if query_terms is None else query_terms
        return _native_identifier_terms({path: body}, terms)[path]
    observed: set[str] = set()
    try:
        for index, name in enumerate(names):
            if index % 1024 == 0 and time.perf_counter() > deadline:
                raise EvidenceDeclined("source_evidence_time_limit")
            observed.update(_lexical_terms(name, query_terms))
    except (tokenize.TokenError, IndentationError, SyntaxError, RecursionError) as exc:
        raise EvidenceDeclined("source_lexical_evidence_unavailable") from exc
    if time.perf_counter() > deadline:
        raise EvidenceDeclined("source_evidence_time_limit")
    return observed


def rank_verified_sources(
    reader: Any,
    project_id: str,
    query: str,
    candidates: list[dict[str, Any]],
    terms: set[str],
    selection: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Rank every candidate or decline; no omitted competitor is assumed weak.

    Terms absent from indexed and verified code carry no lexical evidence. Their
    absence is not a claim that the behavior is satisfied. Common terms can rank
    candidates, but cannot independently justify preloading. There is no ratio
    between metadata matches and all acceptance-criteria words.
    """
    from memglide.core.indexer import Indexer
    from memglide.core.query import explicit_identifier, explicit_path, term_variants, tokens
    from memglide.integrations.preload import _eligible
    from memglide.security.paths import read_source

    if len(candidates) > MAX_EVIDENCE_FILES:
        raise EvidenceDeclined("evidence_candidate_limit")
    if any(PurePosixPath(item["path"]).suffix.casefold() not in _LEXICAL_LANGUAGES for item in candidates):
        raise EvidenceDeclined("source_lexical_language_unavailable")
    paths = tuple(sorted(item["path"] for item in candidates))
    policy = _eligible(selection, paths)
    placeholders = ",".join("?" for _ in paths)
    file_rows = reader.rows(
        f"SELECT path,hash,size FROM files WHERE project_id=? AND path IN ({placeholders})",
        (project_id, *paths),
    )
    files = {row["path"]: row for row in file_rows}
    if set(files) != set(paths):
        raise EvidenceDeclined("ranking_source_unavailable")
    if any(type(row["size"]) is not int or row["size"] < 0 for row in file_rows):
        raise EvidenceDeclined("source_evidence_budget")
    if sum(row["size"] for row in file_rows) > MAX_EVIDENCE_BYTES:
        raise EvidenceDeclined("source_evidence_budget")
    declarations: dict[str, set[str]] = {path: set() for path in paths}
    explicit_declarations: set[str] = set()
    for row in reader.rows(
        "SELECT path,name,qualified_name,signature FROM symbols WHERE project_id=? "
        f"AND path IN ({placeholders}) ORDER BY path,start_line,id",
        (project_id, *paths),
    ):
        declarations[row["path"]].update(tokens(row["name"] + " " + row["signature"]))
        if explicit_identifier(query, row["name"], row["qualified_name"]):
            explicit_declarations.add(row["path"])
    expressions = {
        term: "(" + " OR ".join(f'"{form}"' for form in term_variants(term)) + ")"
        for term in sorted(terms)
    }
    with reader.connect() as conn:
        document_count = conn.execute(
            "SELECT count(*) FROM files WHERE project_id=?", (project_id,)
        ).fetchone()[0]
        frequencies = Indexer._document_frequencies(conn, project_id, expressions)
    evidence: dict[str, dict[str, Any]] = {}
    observed_features: dict[str, dict[str, Any]] = {}
    native_sources: dict[str, str] = {}
    ranked = []
    versions = {}
    used_bytes = 0
    lexical_deadline = time.perf_counter() + 2.0
    for item in candidates:
        path = item["path"]
        body, digest = read_source(
            selection["root"], path, min(selection["max_size"], MAX_EVIDENCE_BYTES - used_bytes)
        )
        used_bytes += len(body.encode("utf-8"))
        if used_bytes > MAX_EVIDENCE_BYTES:
            raise EvidenceDeclined("source_evidence_budget")
        if digest != files[path]["hash"] or digest != item["hash"]:
            raise EvidenceDeclined("ranking_source_changed")
        versions[path] = digest
        path_terms = terms & set(tokens(path))
        declaration_terms = terms & declarations[path]
        metadata = path_terms | declaration_terms
        code: set[str] = set()
        if PurePosixPath(path).suffix.casefold() in {".py", ".pyi"}:
            code = _code_like_terms(path, body, terms, deadline=lexical_deadline)
        else:
            native_sources[path] = body
        # Whole-source evidence is a separate, weaker channel. Instructions in
        # comments/strings never become instructions or a standalone anchor.
        prose = _lexical_terms(body, terms)
        if time.perf_counter() > lexical_deadline:
            raise EvidenceDeclined("source_evidence_time_limit")
        observed_features[path] = {
            "code": code,
            "metadata": metadata,
            "prose": prose,
            "explicit": explicit_path(query, path) or path in explicit_declarations,
        }
    if native_sources:
        for path, matches in _native_identifier_terms(native_sources, terms).items():
            observed_features[path]["code"] = matches
        native_sources.clear()
    code_frequencies = {
        term: sum(term in features["code"] for features in observed_features.values())
        for term in terms
    }
    # FTS document frequencies include prose and do not split every parameter
    # identifier. Verified code occurrences supply an explicit second channel;
    # a comment-only competitor cannot erase distinguishing live-code evidence.
    weights = {
        term: math.log1p((document_count + 0.5) / (max(frequencies[term], code_frequencies[term]) + 0.5))
        for term in terms if frequencies[term] > 0 or code_frequencies[term] > 0
    }
    informative = {
        term for term in weights if (
            0 < frequencies[term] < document_count
            or 0 < code_frequencies[term] < len(candidates)
            or len(candidates) == 1
        )
    }
    for path, features in observed_features.items():
        code, metadata, prose = features["code"], features["metadata"], features["prose"]
        informative_code = code & informative
        informative_metadata = metadata & informative
        supports = informative_code | informative_metadata
        explicit = features["explicit"]
        sufficient = explicit or (
            len(supports) >= 2 and bool(informative_metadata) and bool(informative_code)
        )
        score = (
            (10_000.0 if explicit else 0.0)
            + 2 * sum(weights.get(term, 0.0) for term in code)
            + sum(weights.get(term, 0.0) for term in metadata)
            + 0.1 * sum(weights.get(term, 0.0) for term in prose)
        )
        evidence[path] = {
            "informative": supports,
            "code": code,
            "metadata": metadata,
            "sufficient": sufficient,
            "explicit": explicit,
        }
        ranked.append({
            "path": path,
            "score": round(score, 6),
            "reason": (
                f"Verified lexical evidence: {len(code)} code-like identifier term(s), "
                f"{len(metadata)} path/declaration term(s), {len(prose)} whole-source term(s); "
                f"{len(supports)} repository/candidate-informative term(s). "
                "Channel agreement is heuristic; unmet requirements and semantic completeness are unknown."
            ),
            "evidence_terms": sorted(code | metadata),
            "explicit_anchor": explicit,
        })
    ranked.sort(key=lambda item: (-item["score"], item["path"]))
    by_path = {item["path"]: item for item in candidates}
    candidates = [{**by_path[item["path"]], "score": item["score"]} for item in ranked]
    return candidates, ranked, {
        "evidence": evidence,
        "versions": versions,
        "policy": policy,
        "paths": paths,
        "selection": selection,
    }


def ambiguous_evidence(top: dict[str, Any], competitors: list[dict[str, Any]]) -> bool:
    """Require positive distinguishing evidence rather than a raw-score ratio."""
    for other in competitors:
        if top["explicit"]:
            if other["explicit"]:
                return True
            continue
        # Repeated same-context modules are ambiguous even when their shared
        # words are too common to count as repository-informative evidence.
        if (
            len(top["code"]) >= 2
            and top["metadata"]
            and top["code"] == other["code"]
            and other["metadata"]
        ):
            return True
        if other["sufficient"] and (
            not other["informative"] < top["informative"]
            or len(top["informative"] - other["informative"]) < 2
        ):
            return True
    return False
