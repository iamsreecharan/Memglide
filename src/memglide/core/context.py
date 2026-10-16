"""Deterministic progressive context selection and source-version passports."""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from pathlib import PurePosixPath
from typing import Any

from memglide.core.query import tokens
from memglide.memory.engine import MemoryEngine
from memglide.security.paths import read_source
from memglide.storage.database import Database, DomainError, new_id


def estimate_tokens(value: Any) -> int:
    """A conservative planning estimate; not a tokenizer or usage measurement."""
    return math.ceil(len(json.dumps(value, ensure_ascii=False).encode("utf-8")) / 3)


class ContextEngine:
    def __init__(self, db: Database, indexer: Any, memory: MemoryEngine):
        self.db = db
        self.indexer = indexer
        self.memory = memory

    @staticmethod
    def _dependency_key(dep: dict[str, Any]) -> tuple[str, ...]:
        return tuple(
            str(dep.get(key, ""))
            for key in (
                "source_file",
                "source_symbol",
                "target_file",
                "target_symbol",
                "kind",
                "reference",
            )
        )

    @staticmethod
    def _dependency_view(dep: dict[str, Any]) -> dict[str, Any]:
        return {
            key: dep.get(key)
            for key in (
                "source_file",
                "source_symbol",
                "target_file",
                "target_symbol",
                "kind",
                "reference",
                "resolved",
            )
        }

    @staticmethod
    def _words(value: str) -> set[str]:
        return set(tokens(value))

    @classmethod
    def _query_intent(cls, query: str) -> str | None:
        """Small explicit query rules, never inferred or generated summaries."""
        # Intent rules use the original inflections, unlike relevance matching.
        words = set(re.findall(r"[a-z0-9_]+", query.casefold()))
        if words & {"session", "task"} and words & {"changed", "changes", "change", "modified"}:
            return "session_changes"
        if words & {"try", "tried", "attempt", "attempts", "attempted", "failures"} and words & {
            "we",
            "already",
            "previous",
            "previously",
            "before",
            "session",
            "error",
            "fix",
        }:
            return "prior_attempts"
        return None

    def _session_changes(self, session: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
        rows = self.db.rows(
            "SELECT id,type,created_at,detail FROM events WHERE project_id=? AND type='file_changed' "
            "AND created_at>=? ORDER BY created_at DESC,id DESC LIMIT 101",
            (session["project_id"], session["created_at"]),
        )
        events = []
        warnings = []
        if len(rows) > 100:
            warnings.append(
                "Only the 100 most recent recorded file changes are candidates; inspect the session timeline for earlier events."
            )
        for row in rows[:100]:
            detail = json.loads(row["detail"])
            path = detail.get("path")
            if not isinstance(path, str):
                continue
            events.append(
                {
                    "id": row["id"],
                    "type": row["type"],
                    "created_at": row["created_at"],
                    "path": path,
                    "deleted": bool(detail.get("deleted")),
                }
            )
        if not self.db.settings()["event_logging"]:
            warnings.append(
                "Event logging is disabled; recorded session change history may be incomplete."
            )
        if not events:
            warnings.append(
                "No recorded project file-change events were observed since this session started; this does not establish that no edits occurred."
            )
        return events, warnings

    def _rank(
        self, candidates: list[dict[str, Any]], query: str, task: str
    ) -> list[dict[str, Any]]:
        task_words = self._words(task)
        task_weight = self.db.settings()["retrieval_weights"]["task_overlap"]
        for candidate in candidates:
            text = " ".join(
                str(candidate.get(k, "")) for k in ("path", "name", "symbol", "signature")
            )
            name = str(candidate.get("symbol") or candidate.get("name") or "")
            candidate["score"] = (
                float(candidate.get("score", 0))
                + (
                    1000
                    if query.casefold()
                    in {name.casefold(), str(candidate.get("qualified_name", "")).casefold()}
                    else 0
                )
                + len(task_words & self._words(text)) * task_weight
            )
        return sorted(
            candidates,
            key=lambda c: (
                -c["score"],
                c.get("path", ""),
                c.get("start_line", 0),
                c.get("symbol", ""),
            ),
        )

    def _source_item(
        self, project: dict[str, Any], candidate: dict[str, Any], level: int
    ) -> dict[str, Any]:
        path = str(candidate["path"])
        text, current_hash = read_source(project["path"], path, self.db.settings()["max_file_size"])
        expected = candidate.get("hash")
        if expected and expected != current_hash:
            raise DomainError("Indexed source changed; reindex " + path, 409)
        lines = text.splitlines(keepends=True)
        start = max(1, int(candidate.get("start_line") or 1))
        end = max(start, min(len(lines), int(candidate.get("end_line") or len(lines))))
        if level == 3:
            start, end = 1, max(1, len(lines))
        snippet = "" if level == 1 else "".join(lines[start - 1 : end])
        return {
            "path": path,
            "symbol": candidate.get("symbol")
            or candidate.get("qualified_name")
            or candidate.get("name"),
            "signature": candidate.get("signature", ""),
            "start_line": start,
            "end_line": end,
            "hash": current_hash,
            "language": candidate.get("language", "text"),
            "kind": candidate.get("kind", "file"),
            "structural": bool(candidate.get("structural", False)),
            "parse_error": candidate.get("parse_error"),
            "score": candidate.get("score", 0),
            "reason": candidate.get("reason", "Related dependency"),
            "snippet": snippet,
            "freshness": "Current",
            "full_source": level == 3,
        }

    def _candidate_dependencies(
        self, project_id: str, candidates: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        found: dict[tuple[str, ...], dict[str, Any]] = {}
        for candidate in candidates[:10]:
            key = candidate.get("id") or candidate.get("symbol") or candidate["path"]
            try:
                deps = self.indexer.dependencies(project_id, key, direction="both", refresh=False)
            except DomainError:
                deps = self.indexer.dependencies(
                    project_id, candidate["path"], direction="both", refresh=False
                )
            for dep in deps:
                found[self._dependency_key(dep)] = self._dependency_view(dep)
        return [found[key] for key in sorted(found)]

    def _related_tests(self, project_id: str, candidates: list[dict[str, Any]]) -> list[str]:
        stems = {PurePosixPath(c["path"]).stem for c in candidates[:10]}
        tests = []
        for row in self.db.rows(
            "SELECT path FROM files WHERE project_id=? ORDER BY path", (project_id,)
        ):
            path = row["path"]
            name = PurePosixPath(path).name
            is_test = (
                name.startswith("test_")
                or name.endswith("_test.py")
                or ".test." in name
                or ".spec." in name
                or "tests" in PurePosixPath(path).parts
            )
            if is_test and any(stem in name for stem in stems):
                tests.append(path)
        return tests

    def _expand_candidates(
        self,
        project_id: str,
        candidates: list[dict[str, Any]],
        dependencies: list[dict[str, Any]],
        tests: list[str],
        level: int,
    ) -> list[dict[str, Any]]:
        if level == 1:
            return candidates
        keys: list[str] = []
        # Expansion is bounded separately from the graph's reported omissions.
        # Direct search results stay first; optional neighbors never displace them.
        for dep in dependencies[:100]:
            if dep.get("resolved") and dep.get("target_file"):
                keys.append(dep.get("target_symbol") or dep["target_file"])
            if level == 3 and dep.get("source_file"):
                keys.append(dep.get("source_symbol") or dep["source_file"])
        if level == 3:
            keys.extend(tests[:20])
        seen = {(c["path"], c.get("start_line", 0), c.get("end_line", 0)) for c in candidates}
        for key in dict.fromkeys(keys):
            try:
                related = self.indexer.get_symbol(project_id, key, refresh=False)
            except DomainError:
                continue
            identity = (related["path"], related.get("start_line", 0), related.get("end_line", 0))
            if identity in seen:
                continue
            seen.add(identity)
            related = {
                **related,
                "score": 0,
                "reason": "Related test"
                if related["path"] in tests
                else "Resolved dependency of a selected candidate",
            }
            candidates.append(related)
        return candidates

    def _select_memories(
        self, session_id: str, query: str, task: str, intent: str | None = None
    ) -> list[dict[str, Any]]:
        terms = self._words(query + " " + task)
        memories = self.memory.recall_memory(session_id)
        ranked = []
        for memory in memories:
            history_match = intent == "prior_attempts" and memory["category"] in {
                "failed_attempt",
                "error",
                "verified_fix",
            }
            # A stale claim never becomes evidence merely because it matches a query.
            if memory["stale"] and not history_match:
                continue
            overlap = len(terms & self._words(memory["content"]))
            if not overlap and terms and not history_match:
                continue
            weight = (
                overlap
                + (3 if memory["freshness"] == "Current" else 0)
                + (100 if history_match else 0)
            )
            weight += 1 if memory["category"] == "verified_fix" else 0
            ranked.append((weight, memory))
        ranked.sort(key=lambda pair: (-pair[0], -pair[1]["updated_at"], pair[1]["id"]))
        return [
            {
                key: value
                for key, value in memory.items()
                if key not in {"session_id", "deduplicated"}
            }
            for _, memory in ranked[:10]
        ]

    @staticmethod
    def _refresh_estimate(response: dict[str, Any]) -> None:
        # Include the number itself, the envelope, and the complete embedded passport.
        for _ in range(5):
            total = estimate_tokens(response)
            if total == response["estimated_tokens"]:
                return
            response["estimated_tokens"] = total
            response["passport"]["estimated_tokens_returned"] = total

    @classmethod
    def _dependency_preview(cls, dependency: dict[str, Any]) -> dict[str, Any]:
        """Bound repeated graph text without changing the full dependency endpoint."""
        full = cls._dependency_view(dependency)
        preview = dict(full)
        shortened = []
        for field in ("reference", "source_symbol", "target_symbol"):
            value = preview.get(field)
            if isinstance(value, str) and len(value) > 160:
                preview[field] = value[:157] + "..."
                shortened.append(field)
        if shortened:
            preview["preview_truncated_fields"] = shortened
            preview["reference_length"] = len(str(full.get("reference") or ""))
        # Hash the complete relationship, so previews remain identifiable when
        # two large expressions have the same prefix. This is not a source hash.
        preview["id"] = hashlib.sha256(
            json.dumps(full, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:20]
        return preview

    @staticmethod
    def _graph_estimate(
        dependencies: list[dict[str, Any]],
        tests: list[str],
        summary: dict[str, Any],
        warnings: list[str],
        next_tests: list[str],
    ) -> int:
        """Count every serialized copy, including the legacy passport arrays.

        The projection conservatively includes its own containers and all graph
        warnings/recommendations. Object arrays remain compatible with existing
        consumers; deduplication in Python would not deduplicate serialized JSON.
        """
        return estimate_tokens(
            {
                "dependencies": dependencies,
                "warnings": warnings,
                "passport": {
                    "dependencies": dependencies,
                    "unresolved_dependencies": [
                        dependency for dependency in dependencies if not dependency.get("resolved")
                    ],
                    "related_tests": tests,
                    "dependency_summary": summary,
                    "missing_context": warnings,
                    "recommended_next_retrievals": next_tests,
                },
            }
        )

    def _build_passport(
        self,
        response: dict[str, Any],
        all_deps: list[dict[str, Any]],
        related_tests: list[str],
        missing: list[str],
        *,
        include_graph: bool = False,
    ) -> None:
        items = response["items"]
        source_hashes = {item["path"]: item["hash"] for item in items}
        for memory in response["memories"]:
            for source in memory["sources"]:
                if source.get("current"):
                    source_hashes[source["path"]] = source["hash"]
        paths = set(source_hashes)
        relevant = [
            dependency
            for dependency in all_deps
            if dependency["source_file"] in paths or dependency.get("target_file") in paths
        ]
        if any(memory.get("freshness") != "Current" for memory in response["memories"]):
            missing = [
                *missing,
                "Selected session claims lack verified source references; inspect their provenance before relying on them.",
            ]
        if response["level"] == 1 and items:
            missing = [
                *missing,
                "Discovery does not include implementations; expand to level 2 before modifying code.",
            ]
        if any(not memory["sources"] for memory in response["memories"]):
            missing = [
                *missing,
                "Some submitted memories have no source references and require independent verification.",
            ]
        base_next = []
        if response["level"] < 3:
            base_next.append(
                f"expand_context({response['retrieval_id']}, level={response['level'] + 1})"
            )
        if response["truncated"]:
            base_next.append("Repeat with a larger budget or a more specific symbol query.")
        if not items:
            base_next.append("Reindex the project and query an exact symbol or relative file path.")
        passport = {
            "retrieval_id": response["retrieval_id"],
            "session_id": response["session_id"],
            "query": response["query"],
            "level": response["level"],
            "selected_files": [
                {"path": path, "hash": source_hashes[path]} for path in sorted(paths)
            ],
            "selected_symbols": [
                {
                    "path": i["path"],
                    "symbol": i["symbol"],
                    "start_line": i["start_line"],
                    "end_line": i["end_line"],
                }
                for i in items
            ],
            "verified_source_hashes": source_hashes,
            "selected_memory_ids": [memory["id"] for memory in response["memories"]],
            "selected_memory_versions": {
                memory["id"]: memory["version"] for memory in response["memories"]
            },
            "source_freshness": "Current",
            "evidence_quality": "Structural discovery"
            if response["level"] == 1
            else "Current source evidence; task sufficiency requires inspection",
            "token_budget": response["budget"],
            "estimated_tokens_returned": response["estimated_tokens"],
        }
        response["passport"] = passport
        if "session_events" in response:
            passport["session_event_ids"] = [event["id"] for event in response["session_events"]]
            passport["session_event_scope"] = response["session_event_scope"]

        # Keep optional graph metadata below an independent limit, and fit it
        # only after sources. The floor accommodates the omission notice itself
        # at small budgets; the complete response must still fit the user budget.
        graph_budget = min(1200, max(256, response["budget"] // 5))
        unresolved_count = sum(not dependency.get("resolved") for dependency in relevant)

        def apply_graph(deps: list[dict[str, Any]], tests: list[str]) -> int:
            omitted = len(relevant) - len(deps)
            shortened = sum(bool(dep.get("preview_truncated_fields")) for dep in deps)
            omitted_tests = len(related_tests) - len(tests)
            graph_warnings = []
            if omitted or omitted_tests or shortened:
                graph_warnings.append(
                    "Dependency/test graph is partial; get_dependencies returns full references."
                )
            if unresolved_count and not omitted:
                graph_warnings.append(
                    "Some static references could not be resolved; inspect their imports and callers."
                )
            next_tests = ["Inspect test " + path for path in tests[:3] if path not in paths]
            summary: dict[str, Any] = {
                "scope": "First 10 search candidates; selected files only",
                "total_references": len(relevant),
                "returned_references": len(deps),
                "omitted_references": omitted,
                "unresolved_references": unresolved_count,
                "truncated_previews": shortened,
                "omitted_related_tests": omitted_tests,
                "graph_token_budget": graph_budget,
                "estimated_graph_tokens": 0,
            }
            for _ in range(5):
                graph_tokens = self._graph_estimate(
                    deps, tests, summary, graph_warnings, next_tests
                )
                if graph_tokens == summary["estimated_graph_tokens"]:
                    break
                summary["estimated_graph_tokens"] = graph_tokens
            response["dependencies"] = deps
            response["warnings"] = list(dict.fromkeys([*missing, *graph_warnings]))
            passport.update(
                {
                    "dependencies": deps,
                    "unresolved_dependencies": [d for d in deps if not d.get("resolved")],
                    "related_tests": tests,
                    "dependency_summary": summary,
                    "missing_context": response["warnings"],
                    "recommended_next_retrievals": [*base_next, *next_tests],
                    "status": "Partial"
                    if response["warnings"] or response["truncated"]
                    else "Current",
                }
            )
            if any(memory["freshness"] == "Stale" for memory in response["memories"]):
                passport["status"] = "Stale"
                passport["source_freshness"] = "Stale"
            self._refresh_estimate(response)
            return int(summary["estimated_graph_tokens"])

        selected: list[dict[str, Any]] = []
        selected_tests: list[str] = []
        empty_graph_tokens = apply_graph(selected, selected_tests)
        if not include_graph:
            return
        # A generous caller budget must not cause a small source answer to grow
        # into mostly graph metadata. Above the small compatibility allowance,
        # bound graph cost to half the answer's non-graph evidence/envelope.
        non_graph_tokens = max(0, response["estimated_tokens"] - empty_graph_tokens)
        graph_budget = min(graph_budget, max(512, non_graph_tokens // 2))
        apply_graph(selected, selected_tests)
        # Evaluate only a bounded preview window. Counts still cover every
        # discovered relationship, so this limit never hides omitted edges.
        for dependency in relevant[:100]:
            preview = self._dependency_preview(dependency)
            trial = [*selected, preview]
            cost = apply_graph(trial, selected_tests)
            if cost <= graph_budget and response["estimated_tokens"] <= response["budget"]:
                selected = trial
            else:
                apply_graph(selected, selected_tests)
        for path in related_tests[:100]:
            trial_tests = [*selected_tests, path]
            cost = apply_graph(selected, trial_tests)
            if cost <= graph_budget and response["estimated_tokens"] <= response["budget"]:
                selected_tests = trial_tests
            else:
                apply_graph(selected, selected_tests)
        apply_graph(selected, selected_tests)

    def get_context(
        self,
        session_id: str,
        query: str,
        level: int = 1,
        budget: int | None = None,
        known_memory_ids: list[str] | None = None,
        known_memory_versions: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        session = self.memory.status(session_id)
        if level not in (1, 2, 3):
            raise DomainError("Context level must be 1, 2, or 3")
        budget = int(self.db.settings()["context_token_budget"] if budget is None else budget)
        if not 256 <= budget <= 100000:
            raise DomainError("Context token budget must be between 256 and 100000")
        if len(query.encode("utf-8")) > 4000:
            raise DomainError("Context query is too large")
        if known_memory_ids is not None and (
            len(known_memory_ids) > 1000
            or any(not isinstance(value, str) or len(value) > 128 for value in known_memory_ids)
        ):
            raise DomainError("known_memory_ids must contain at most 1000 memory identifiers")
        if known_memory_versions is not None and (
            not isinstance(known_memory_versions, dict)
            or len(known_memory_versions) > 1000
            or any(
                not isinstance(memory_id, str)
                or not memory_id
                or len(memory_id) > 128
                or not isinstance(version, str)
                or re.fullmatch(r"[0-9a-f]{64}", version) is None
                for memory_id, version in known_memory_versions.items()
            )
        ):
            raise DomainError(
                "known_memory_versions must map at most 1000 memory identifiers to 64-character lowercase SHA-256 versions"
            )
        project_id = session["project_id"]
        project = self.db.project(project_id)
        query = query.strip() or session["task"].strip()
        if not query:
            raise DomainError("Provide a context query or start the session with a task")
        intent = self._query_intent(query)
        candidates = self._rank(
            self.indexer.search(project_id, query, limit=40), query, session["task"]
        )
        session_events: list[dict[str, Any]] = []
        history_warnings: list[str] = []
        if intent == "session_changes":
            session_events, history_warnings = self._session_changes(session)
            candidates = []
            for path in dict.fromkeys(event["path"] for event in session_events):
                try:
                    candidate = self.indexer.get_symbol(project_id, path, refresh=False)
                except DomainError:
                    history_warnings.append(
                        "Recorded changed source is deleted, excluded, or unavailable: " + path
                    )
                    continue
                candidates.append(
                    {
                        **candidate,
                        "reason": "Current source for recorded project activity observed since session start",
                        "score": 100,
                    }
                )
        dependencies = self._candidate_dependencies(project_id, candidates)
        tests = self._related_tests(project_id, candidates)
        candidates = self._expand_candidates(project_id, candidates, dependencies, tests, level)
        memories = self._select_memories(session_id, query, session["task"], intent)
        # Legacy known IDs remain accepted, but cannot identify which version
        # this particular client has seen when several clients share a session.
        acknowledged_versions = known_memory_versions or {}
        memories = [
            {
                **{
                    key: memory[key]
                    for key in ("id", "category", "updated_at", "freshness", "sources", "version")
                },
                "content_omitted": True,
            }
            if acknowledged_versions.get(memory["id"]) == memory["version"]
            else memory
            for memory in memories
        ]
        response: dict[str, Any] = {
            "retrieval_id": new_id(),
            "session_id": session_id,
            "project_id": project_id,
            "query": query,
            "level": level,
            "budget": budget,
            "estimated_tokens": 0,
            "token_estimate_method": "ceil(UTF-8 JSON bytes / 3); includes metadata; estimate, not measured usage",
            "items": [],
            "memories": [],
            "dependencies": [],
            "warnings": [],
            "truncated": False,
            "passport": {},
        }
        if intent == "session_changes":
            response["session_events"] = []
            response["session_event_scope"] = (
                "Project activity observed since session start; events do not identify the actor or attribute edits to this session. Only recorded changes are shown."
            )
        missing: list[str] = history_warnings
        stats = json.loads(self.db.project(project_id)["index_stats"])
        if stats.get("partial"):
            missing.append(
                "The repository index is partial because a resource limit was reached; narrow ignored directories or register a smaller repository and reindex."
            )
        if stats.get("errors"):
            missing.append(
                f"Indexing reported {len(stats['errors'])} error(s); inspect the project indexing report for missing evidence."
            )
        if any(c.get("parse_error") for c in candidates):
            missing.append(
                "Some matching source could not be structurally parsed; inspect full source and parser support before relying on symbol relationships."
            )
        if not candidates:
            missing.append("No indexed source matched this query.")
        if intent == "prior_attempts" and not memories:
            missing.append(
                "No matching submitted attempts, errors, or verified fixes exist in this session; unsubmitted agent activity is unavailable."
            )
        for event in session_events:
            response["session_events"].append(event)
            self._build_passport(response, dependencies, tests, missing)
            if response["estimated_tokens"] > budget:
                response["session_events"].pop()
                response["truncated"] = True
                missing.append(
                    "Some recorded file-change events could not fit; increase the budget or inspect the session timeline."
                )
                break
        included: list[tuple[str, int, int]] = []
        omitted = 0
        for candidate in candidates:
            try:
                item = self._source_item(project, candidate, level)
            except (OSError, DomainError):
                missing.append(
                    "Source changed or is unavailable: "
                    + candidate["path"]
                    + "; reindex and retry."
                )
                continue
            identity = (item["path"], item["start_line"], item["end_line"])
            if any(
                path == identity[0]
                and (
                    level == 1
                    and identity == (path, start, end)
                    or level > 1
                    and max(start, identity[1]) <= min(end, identity[2])
                )
                for path, start, end in included
            ):
                continue
            response["items"].append(item)
            self._build_passport(response, dependencies, tests, missing)
            while (
                response["estimated_tokens"] > budget
                and len(response.get("session_events", [])) > 1
            ):
                response["session_events"].pop()
                response["truncated"] = True
                missing = list(
                    dict.fromkeys(
                        [
                            *missing,
                            "Some recorded file-change events could not fit with current source evidence; inspect the session timeline.",
                        ]
                    )
                )
                self._build_passport(response, dependencies, tests, missing)
            if response["estimated_tokens"] > budget:
                response["items"].pop()
                # Keep a structural reference if an implementation cannot fit.
                if level > 1:
                    discovery = self._source_item(project, candidate, 1)
                    discovery["reason"] += "; implementation omitted by token budget"
                    response["items"].append(discovery)
                    response["truncated"] = True
                    self._build_passport(response, dependencies, tests, missing)
                    if response["estimated_tokens"] <= budget:
                        included.append(
                            (discovery["path"], discovery["start_line"], discovery["end_line"])
                        )
                        omitted += 1
                        continue
                    response["items"].pop()
                omitted += 1
            else:
                included.append(identity)
        if omitted:
            response["truncated"] = True
            missing.append(f"Budget omitted {omitted} candidate implementation(s) or references.")
        for memory in memories:
            response["memories"].append(memory)
            self._build_passport(response, dependencies, tests, missing)
            if response["estimated_tokens"] > budget:
                response["memories"].pop()
                response["truncated"] = True
        self._build_passport(response, dependencies, tests, missing)
        # Final warnings and passport metadata also consume budget. Remove whole
        # evidence units instead of silently cutting source in the middle.
        while response["estimated_tokens"] > budget and (
            response["memories"] or response["items"] or response.get("session_events")
        ):
            units = response["memories"] or response["items"] or response["session_events"]
            units.pop()
            response["truncated"] = True
            missing = list(
                dict.fromkeys(
                    [
                        *missing,
                        "Some evidence could not fit with its metadata; increase the budget.",
                    ]
                )
            )
            self._build_passport(response, dependencies, tests, missing)
        if response["estimated_tokens"] > budget:
            raise DomainError(
                f"Budget is too small for retrieval metadata; use at least {response['estimated_tokens']} estimated tokens"
            )
        self._build_passport(response, dependencies, tests, missing, include_graph=True)
        self.memory.touch(session_id)
        created = time.time()
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO retrievals VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    response["retrieval_id"],
                    session_id,
                    project_id,
                    query,
                    level,
                    budget,
                    response["estimated_tokens"],
                    created,
                    json.dumps(response, ensure_ascii=False),
                ),
            )
            conn.execute(
                "INSERT INTO passports VALUES(?,?,?)",
                (
                    response["retrieval_id"],
                    session_id,
                    json.dumps(response["passport"], ensure_ascii=False),
                ),
            )
        self.db.event(
            project_id,
            session_id,
            "context_retrieved",
            {
                "retrieval_id": response["retrieval_id"],
                "level": level,
                "estimated_tokens": response["estimated_tokens"],
                "files": len(response["passport"]["selected_files"]),
            },
        )
        return response

    def expand_context(
        self,
        session_id: str,
        retrieval_id: str,
        level: int | None = None,
        budget: int | None = None,
        known_memory_ids: list[str] | None = None,
        known_memory_versions: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        self.memory.status(session_id)
        previous = self.db.one(
            "SELECT * FROM retrievals WHERE id=? AND session_id=?", (retrieval_id, session_id)
        )
        if previous is None:
            raise DomainError("Unknown retrieval for this session", 404)
        next_level = min(3, previous["level"] + 1) if level is None else level
        if next_level < previous["level"]:
            raise DomainError("Expansion level cannot be below the previous retrieval level")
        return self.get_context(
            session_id,
            previous["query"],
            next_level,
            previous["budget"] if budget is None else budget,
            known_memory_ids,
            known_memory_versions,
        )

    def get_passport(self, session_id: str, retrieval_id: str) -> dict[str, Any]:
        session = self.memory.status(session_id)
        row = self.db.one(
            "SELECT data FROM passports WHERE retrieval_id=? AND session_id=?",
            (retrieval_id, session_id),
        )
        if row is None:
            raise DomainError("Unknown Context Passport for this session", 404)
        passport = json.loads(row["data"])
        project = self.db.project(session["project_id"])
        stale_files = []
        stale_memories = []
        for file in passport["selected_files"]:
            try:
                _, current_hash = read_source(
                    project["path"], file["path"], self.db.settings()["max_file_size"]
                )
                if current_hash != file["hash"]:
                    stale_files.append(file["path"])
            except (OSError, DomainError):
                stale_files.append(file["path"])
        for memory_id in passport.get("selected_memory_ids", []):
            try:
                memory = self.memory.get_memory_snapshot(session_id, memory_id)
            except DomainError:
                stale_memories.append(memory_id)
                continue
            version = passport.get("selected_memory_versions", {}).get(memory_id)
            if memory["stale"] or version != memory["version"]:
                stale_memories.append(memory_id)
        if stale_files or stale_memories:
            passport["status"] = "Stale"
            passport["source_freshness"] = "Stale"
            passport["stale_files"] = stale_files
            passport["stale_memory_ids"] = stale_memories
            passport["verified_source_hashes"] = {
                path: digest
                for path, digest in passport["verified_source_hashes"].items()
                if path not in stale_files
            }
            warning = "Selected source or memory changed or disappeared; retrieve current evidence."
            passport["missing_context"] = list(
                dict.fromkeys([*passport["missing_context"], warning])
            )
            passport["recommended_next_retrievals"] = list(
                dict.fromkeys(
                    [
                        "Reindex project "
                        + session["project_id"]
                        + " and repeat query: "
                        + passport["query"],
                        *passport["recommended_next_retrievals"],
                    ]
                )
            )
            self.db.execute(
                "UPDATE passports SET data=? WHERE retrieval_id=?",
                (json.dumps(passport, ensure_ascii=False), retrieval_id),
            )
        return passport
