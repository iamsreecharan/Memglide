"""Project-bound agent context without discovery/session/metadata round trips.

The full context engine remains the authority for selection and source validation.
This adapter only owns a private session and removes repeated transport metadata;
it does not claim semantic completeness or account for model tokens.
"""

from __future__ import annotations

import threading
from typing import Any

from memglide.core.context import estimate_tokens
from memglide.storage.database import DomainError


class AgentContext:
    """A single approved project and private, expiring task session per server."""

    def __init__(self, service: Any, project_id: str):
        if not project_id:
            raise DomainError("The agent profile requires an explicitly registered project ID")
        service.db.project(project_id)
        self.service = service
        self.project_id = project_id
        self._session_id: str | None = None
        self._retrievals: set[str] = set()
        self._latest: str | None = None
        self._lock = threading.RLock()

    def _session(self, query: str) -> str:
        if self._session_id is not None:
            try:
                self.service.memory.status(self._session_id, project_id=self.project_id)
                return self._session_id
            except DomainError as error:
                if error.status not in {404, 410}:
                    raise
                # A new explicit retrieval can start fresh; old retrieval IDs
                # never move into the replacement session.
                self._retrievals.clear()
                self._latest = None
                self._session_id = None
        session = self.service.memory.start_session(self.project_id, query)
        self._session_id = str(session["id"])
        return self._session_id

    @staticmethod
    def _warnings(values: list[str]) -> list[str]:
        # Keep every gap while directing this two-tool client to operations it
        # actually has. These are engine-authored notices, not source snippets.
        return list(
            dict.fromkeys(
                value.replace(
                    "get_dependencies returns full references.",
                    "Inspect imports and callers with normal source tools for full references.",
                ).replace(
                    "Query an exact symbol/path or use level 3 for broader source evidence.",
                    "Fetch an exact symbol/path or inspect normal source files for broader evidence.",
                )
                for value in values
            )
        )

    @staticmethod
    def _compact(response: dict[str, Any]) -> dict[str, Any]:
        passport = response["passport"]
        result: dict[str, Any] = {
            "operation": "get_context",
            "retrieval_id": response["retrieval_id"],
            "items": [
                {key: item[key] for key in ("path", "symbol", "start_line", "end_line", "snippet")}
                for item in response["items"]
            ],
            "source_hashes": passport["verified_source_hashes"],
            "status": passport["status"],
            "source_freshness": passport["source_freshness"],
            "truncated": response["truncated"],
            "warnings": AgentContext._warnings(response["warnings"]),
        }
        if passport.get("related_tests"):
            result["related_tests"] = passport["related_tests"]
        if response.get("memories"):
            # Usually empty: the compact profile exposes no memory mutation.
            # Preserve evidence if another local client explicitly adds a claim.
            result["memories"] = response["memories"]
        if response.get("session_events"):
            result["session_events"] = response["session_events"]
            result["session_event_scope"] = response["session_event_scope"]
        return result

    def fetch(self, query: str, budget: int = 4000) -> dict[str, Any]:
        if not isinstance(query, str) or not query.strip():
            raise DomainError("Provide a non-empty task, exact symbol, or relative source path")
        if len(query.encode("utf-8")) > 4000:
            raise DomainError("Context query is too large")
        if type(budget) is not int or not 256 <= budget <= 100000:
            raise DomainError("Context token budget must be between 256 and 100000")
        with self._lock:
            session_id = self._session(query)
            response = self.service.context.get_context(session_id, query, level=2, budget=budget)
            result = self._compact(response)
            # Metadata removal must never create a larger response. This is a
            # planning byte estimate, not billed usage or a tokenizer result.
            if estimate_tokens(result) > budget:
                raise DomainError("Compact context exceeds its planning budget; retry", 409)
            self._latest = str(response["retrieval_id"])
            self._retrievals.add(self._latest)
            return result

    def verify(self, retrieval_id: str = "") -> dict[str, Any]:
        with self._lock:
            retrieval_id = retrieval_id or self._latest or ""
            if self._session_id is None or not retrieval_id or retrieval_id not in self._retrievals:
                raise DomainError(
                    "Fetch context first; only this server's retrievals can be verified", 404
                )
            self.service.memory.status(self._session_id, project_id=self.project_id)
            passport = self.service.context.get_passport(self._session_id, retrieval_id)
            return {
                "operation": "get_context_passport",
                "retrieval_id": retrieval_id,
                "status": passport["status"],
                "source_freshness": passport["source_freshness"],
                "stale_files": passport.get("stale_files", []),
                "stale_memory_ids": passport.get("stale_memory_ids", []),
                "warnings": self._warnings(passport.get("missing_context", [])),
            }

    def close(self) -> None:
        with self._lock:
            if self._session_id is not None:
                try:
                    self.service.memory.end_session(self._session_id)
                except DomainError:
                    # Expiration, explicit ending or project removal already
                    # prevents further work; cleanup must still close services.
                    pass
                self._session_id = None
            self._retrievals.clear()
            self._latest = None
