"""Experimental current-syntax source ranking with conservative abstention.

No model calls or semantic correctness claims. Unlike whole-file lexical bags,
only one bounded syntax unit supplies sufficient body/header evidence. Comments,
quoted literals and indexed signature strings cannot establish relevance.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from memglide.integrations.source_evidence import (
    MAX_EVIDENCE_BYTES,
    MAX_EVIDENCE_FILES,
    EvidenceDeclined,
    _lexical_terms,
)

# Static-typing intent is deliberately narrower than a bare word such as "type".
_STATIC_INTENT = re.compile(
    r"\b(?:typescript compiler|static typ(?:e|ing)|"
    r"type[- ](?:check(?:ing)?|infer(?:ence)?|annotation|declaration|definition)|"
    r"declaration file|generic (?:type|constraint)|interface declaration|"
    r"(?:mypy|pyright|tsc) (?:reports?|rejects?|fails?|errors?|diagnostics?)|"
    r"(?:mypy|pyright|tsc) (?:type )?(?:errors?|failures?))\b", re.IGNORECASE)


def _syntax_units(sources: dict[str, str], terms: set[str], query: str) -> dict[str, list[dict[str, Any]]]:
    from memglide.integrations import runtime_syntax

    if (not 1 <= len(sources) <= MAX_EVIDENCE_FILES or len(terms) > 64
        or any(not isinstance(term, str) or not term or len(term) > 128 for term in terms)
        or len(query) > 4000
        or sum(len(source.encode("utf-8")) for source in sources.values()) > MAX_EVIDENCE_BYTES):
        raise EvidenceDeclined("runtime_evidence_input_limit")
    payload = json.dumps({"sources": sources, "terms": sorted(terms), "query": query}, ensure_ascii=False)
    if len(payload.encode("utf-8")) > runtime_syntax.MAX_PAYLOAD_BYTES:
        raise EvidenceDeclined("runtime_evidence_input_limit")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate key")
            result[key] = value
        return result

    try:
        worker = Path(runtime_syntax.__file__).resolve()
        result = subprocess.run([sys.executable, "-I", str(worker), "--worker"],
                                input=payload, text=True, capture_output=True, timeout=5,
                                cwd=worker.parent)
        if result.returncode or len(result.stdout.encode("utf-8")) > runtime_syntax.MAX_OUTPUT_BYTES:
            raise EvidenceDeclined("runtime_syntax_unavailable")
        response = json.loads(result.stdout, object_pairs_hook=unique)
        if (not isinstance(response, dict) or set(response) != {"version", "files"}
            or type(response["version"]) is not int or response["version"] != 1
            or not isinstance(response["files"], dict) or set(response["files"]) != set(sources)):
            raise ValueError("Invalid runtime syntax response")
        for units in response["files"].values():
            if not isinstance(units, list) or not 1 <= len(units) <= 8:
                raise ValueError("Invalid syntax units")
            for unit in units:
                if (not isinstance(unit, dict)
                    or set(unit) != {"role", "code", "header", "docs", "explicit"}
                    or unit["role"] not in {"runtime", "declaration"}
                    or type(unit["explicit"]) is not bool):
                    raise ValueError("Invalid syntax unit")
                for key in ("code", "header", "docs"):
                    matches = unit[key]
                    if (not isinstance(matches, list) or len(matches) > len(terms)
                        or any(not isinstance(term, str) or term not in terms for term in matches)
                        or len(set(matches)) != len(matches)):
                        raise ValueError("Invalid syntax matched terms")
                    unit[key] = set(matches)
        return response["files"]
    except EvidenceDeclined:
        raise
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, RecursionError) as exc:
        raise EvidenceDeclined("runtime_syntax_unavailable") from exc


def rank_runtime_sources(
    reader: Any, project_id: str, query: str, candidates: list[dict[str, Any]],
    terms: set[str], selection: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Read/parse every candidate or decline; all competitors remain guarded.

    Sufficient evidence is an explicit current eligible anchor, or two distinct
    matched clean body/header terms in one syntax unit, including one body term.
    Candidate-frequency weights only order evidence; they are not probabilities.
    Type/declaration units lead only for explicit static-type intent or an
    exclusive current declaration anchor. Complete source delivery is external.
    """
    from memglide.core.query import explicit_path
    from memglide.integrations import runtime_syntax
    from memglide.integrations.preload import _eligible
    from memglide.security.paths import read_source

    if not candidates or len(candidates) > MAX_EVIDENCE_FILES:
        raise EvidenceDeclined("evidence_candidate_limit")
    paths = tuple(sorted(item["path"] for item in candidates))
    if len(set(paths)) != len(paths):
        raise EvidenceDeclined("runtime_duplicate_candidates")
    if any(PurePosixPath(path).suffix.casefold() not in runtime_syntax.LANGUAGES for path in paths):
        raise EvidenceDeclined("runtime_language_unavailable")
    policy = _eligible(selection, paths)
    placeholders = ",".join("?" for _ in paths)
    rows = reader.rows(f"SELECT path,hash,size FROM files WHERE project_id=? AND path IN ({placeholders})",
                       (project_id, *paths))
    files = {row["path"]: row for row in rows}
    if set(files) != set(paths):
        raise EvidenceDeclined("ranking_source_unavailable")
    if (any(type(row["size"]) is not int or row["size"] < 0 for row in rows)
        or sum(row["size"] for row in rows) > MAX_EVIDENCE_BYTES):
        raise EvidenceDeclined("source_evidence_budget")
    sources = {}
    versions = {}
    used = 0
    for item in candidates:
        path = item["path"]
        body, digest = read_source(selection["root"], path,
                                   min(selection["max_size"], MAX_EVIDENCE_BYTES - used))
        used += len(body.encode("utf-8"))
        if used > MAX_EVIDENCE_BYTES:
            raise EvidenceDeclined("source_evidence_budget")
        if digest != item["hash"] or digest != files[path]["hash"]:
            raise EvidenceDeclined("ranking_source_changed")
        sources[path], versions[path] = body, digest
    observed = _syntax_units(sources, terms, query)
    sources.clear()
    static_intent = bool(_STATIC_INTENT.search(query))
    eligible: dict[str, list[dict[str, Any]]] = {}
    for path, units in observed.items():
        explicit_declaration = any(unit["explicit"] and unit["role"] == "declaration" for unit in units)
        explicit_runtime = any(unit["explicit"] and unit["role"] == "runtime" for unit in units)
        declaration_anchor = explicit_declaration and not explicit_runtime
        declaration_file = path.casefold().endswith((".pyi", ".d.ts"))
        role = "declaration" if (static_intent or declaration_anchor or (
            declaration_file and explicit_path(query, path))) else "runtime"
        eligible[path] = [unit for unit in units if unit["role"] == role]
        if not eligible[path]:
            eligible[path] = [{"role": role, "code": set(), "header": set(), "docs": set(),
                               "explicit": False}]
    frequency = {term: sum(any(term in unit["code"] | unit["header"] for unit in units)
                           for units in eligible.values()) for term in terms}
    weights = {term: math.log1p((len(paths) + 0.5) / (frequency[term] + 0.5)) for term in terms}
    evidence: dict[str, dict[str, Any]] = {}
    ranked: list[dict[str, Any]] = []
    for path, units in eligible.items():
        path_terms = _lexical_terms(path, terms)
        path_anchor = explicit_path(query, path)

        def measure(unit: dict[str, Any]) -> tuple[float, bool, bool]:
            code, header = unit["code"], unit["header"]
            explicit = unit["explicit"] or path_anchor
            sufficient = explicit or len(code | header) >= 2 and bool(code)
            score = (10_000.0 * explicit + 100.0 * sufficient
                     + 3 * sum(weights[term] for term in code)
                     + 2 * sum(weights[term] for term in header)
                     + 0.25 * sum(weights[term] for term in path_terms)
                     + 0.05 * sum(weights[term] for term in unit["docs"]))
            return score, sufficient, explicit

        unit = max(units, key=lambda item: (measure(item)[0], len(item["code"]), len(item["header"])))
        score, sufficient, explicit = measure(unit)
        code, header = unit["code"], unit["header"]
        evidence[path] = {"informative": code | header, "code": code, "metadata": header,
                          "sufficient": sufficient, "explicit": explicit, "role": unit["role"]}
        ranked.append({"path": path, "score": round(score, 6),
                       "reason": (f"Verified {unit['role']} syntax unit: {len(code)} body/role term(s), "
                                  f"{len(header)} clean header term(s); candidate-specificity weights. "
                                  "Comments, literals and indexed signatures cannot justify selection; "
                                  "syntax roles are heuristic, not execution or requirement completeness."),
                       "evidence_terms": sorted(code | header | path_terms), "explicit_anchor": explicit})
    ranked.sort(key=lambda item: (-item["score"], item["path"]))
    originals = {item["path"]: item for item in candidates}
    return ([{**originals[item["path"]], "score": item["score"]} for item in ranked], ranked,
            {"evidence": evidence, "versions": versions, "policy": policy,
             "paths": paths, "selection": selection})


def ambiguous_runtime_evidence(top: dict[str, Any], competitors: list[dict[str, Any]]) -> bool:
    """Require strictly stronger body evidence; ties and tradeoffs abstain.

    A strictly greater count alone is insufficient when its useful header count
    decreases. This is deterministic evidence dominance, not calibrated confidence.
    """
    for other in competitors:
        if top["explicit"]:
            if other["explicit"]:
                return True
            continue
        if not other["sufficient"]:
            continue
        if top["code"] == other["code"]:
            return True
        if not (len(top["code"]) > len(other["code"])
                and len(top["code"] | top["metadata"]) >= len(other["code"] | other["metadata"])):
            return True
    return False
