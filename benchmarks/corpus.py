"""Offline coding benchmark fixtures and independent behavioral grading.

The fixtures intentionally contain one independent defect for each task.  The
grader's assertions live outside task worktrees.  This is procedural separation,
not a security boundary: an agent with host read access could read this file.
Raw logs and protected-file fingerprints are retained to make runs auditable.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

CORPUS_VERSION = "1.0.0"
LANGUAGES = ("python", "typescript")


def _clean(value: str) -> str:
    return textwrap.dedent(value).lstrip("\n")


PYTHON_SOURCES = {
    "atlas/__init__.py": '"""Atlas: a small offline document service."""\n',
    "atlas/cache.py": _clean('''
        from collections import OrderedDict


        class TTLCache:
            """Clock is injected so callers can use deterministic time."""

            def __init__(self, capacity=64):
                self.capacity = capacity
                self.entries = OrderedDict()

            def put(self, key, value, *, now, ttl):
                if self.capacity < 1 or ttl <= 0:
                    return
                self.entries.pop(key, None)
                self.entries[key] = (value, now + ttl)
                while len(self.entries) > self.capacity:
                    self.entries.popitem(last=False)

            def get(self, key, *, now):
                entry = self.entries.get(key)
                if entry is None:
                    return None
                value, expires = entry
                if now > expires:
                    self.entries.pop(key, None)
                    return None
                return value
    '''),
    "atlas/pagination.py": _clean('''
        def page(records, *, cursor=None, limit=20):
            """Stable ascending IDs. Cursor names the last emitted record."""
            if limit < 1 or limit > 100:
                raise ValueError("limit must be between 1 and 100")
            ordered = sorted(records, key=lambda item: item["id"])
            if cursor is not None:
                ordered = [item for item in ordered if item["id"] >= cursor]
            selected = ordered[:limit]
            next_cursor = selected[-1]["id"] if len(ordered) > limit else None
            return {"items": selected, "next_cursor": next_cursor}
    '''),
    "atlas/repository.py": _clean("""
        from copy import deepcopy


        class ConflictError(Exception):
            pass


        class Repository:
            def __init__(self):
                self.records = {}
                self.events = {}

            def create(self, record_id, body):
                record = {"id": record_id, "body": deepcopy(body), "revision": 1}
                self.records[record_id] = record
                return deepcopy(record)

            def update(self, record_id, body, *, expected_revision):
                current = self.records[record_id]
                if expected_revision > current["revision"]:
                    raise ConflictError("revision conflict")
                updated = {"id": record_id, "body": deepcopy(body),
                           "revision": current["revision"] + 1}
                self.records[record_id] = updated
                return deepcopy(updated)

            def put_event(self, key, payload):
                event = {"key": key, "payload": deepcopy(payload),
                         "sequence": len(self.events) + 1}
                self.events[key] = event
                return deepcopy(event)
    """),
    "atlas/security.py": _clean('''
        from pathlib import PurePosixPath


        def can_access(scopes, resource, action):
            required = resource + ":" + action
            return any(scope in required or scope == resource + ":*" for scope in scopes)


        def resolve_under(root, relative):
            """Resolve a POSIX key beneath a storage root; no filesystem I/O."""
            if relative.startswith("/"):
                raise ValueError("absolute keys are not allowed")
            parts = []
            for part in (root.rstrip("/") + "/" + relative).split("/"):
                if part == "..":
                    if parts:
                        parts.pop()
                elif part not in ("", "."):
                    parts.append(part)
            candidate = "/" + "/".join(parts)
            root_path = str(PurePosixPath(root))
            if not candidate.startswith(root_path):
                raise ValueError("key escapes storage root")
            return candidate
    '''),
    "atlas/graph.py": _clean('''
        def dependencies(graph, start):
            """Return all reachable dependencies, excluding start, sorted by ID."""
            return sorted(set(graph.get(start, [])) - {start})
    '''),
    "atlas/retry.py": _clean("""
        class TemporaryError(Exception):
            pass


        def run_with_retry(operation, *, max_attempts=3):
            if max_attempts < 1:
                raise ValueError("max_attempts must be positive")
            for attempt in range(max_attempts):
                try:
                    return operation()
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
    """),
    "atlas/config.py": _clean('''
        def parse_flag(value, *, default=False):
            """Accept bools and case-insensitive true/false, 1/0, yes/no, on/off."""
            if value is None:
                return default
            return bool(value)
    '''),
    "atlas/search.py": _clean('''
        import re


        def tokens(value):
            return set(re.findall(r"[a-z0-9]+", value.lower()))


        def search(records, query):
            """AND token search; most matching tokens first, then ascending ID."""
            wanted = tokens(query)
            if not wanted:
                return []
            scored = []
            for record in records:
                found = tokens(record["title"] + " " + record["body"])
                score = len(wanted & found)
                if score:
                    scored.append((score, record))
            scored.sort(key=lambda item: (-item[0], item[1]["id"]))
            return [record for _, record in scored]
    '''),
    "atlas/billing.py": _clean('''
        def prorated_cents(monthly_cents, active_days, period_days):
            """Nonnegative integer amounts; round half up to a whole cent."""
            if any(type(value) is not int or value < 0
                   for value in (monthly_cents, active_days, period_days)):
                raise ValueError("arguments must be nonnegative integers")
            if period_days == 0 or active_days > period_days:
                raise ValueError("invalid billing period")
            return (monthly_cents * active_days) // period_days
    '''),
    "atlas/service.py": _clean('''
        from .cache import TTLCache
        from .config import parse_flag
        from .graph import dependencies
        from .pagination import page
        from .repository import Repository
        from .search import search
        from .security import can_access, resolve_under


        class DocumentService:
            """Small application boundary used by a future HTTP adapter."""

            def __init__(self, capacity=64):
                self.repository = Repository()
                self.cache = TTLCache(capacity)

            def cached_document(self, document_id, *, now):
                return self.cache.get(document_id, now=now)

            def list_documents(self, *, cursor=None, limit=20):
                return page(list(self.repository.records.values()), cursor=cursor, limit=limit)

            def dependencies_for(self, graph, document_id):
                return dependencies(graph, document_id)

            def search_documents(self, records, query):
                return search(records, query)

            def storage_key(self, root, relative):
                return resolve_under(root, relative)

            def authorized(self, scopes, resource, action):
                return can_access(scopes, resource, action)

            def feature_enabled(self, value):
                return parse_flag(value)
    '''),
}

TYPESCRIPT_SOURCES = {
    "src/cache.ts": _clean("""
        export class TTLCache<T> {
          readonly entries = new Map<string, { value: T; expires: number }>();
          constructor(readonly capacity = 64) {}

          put(key: string, value: T, options: { now: number; ttl: number }): void {
            if (this.capacity < 1 || options.ttl <= 0) return;
            this.entries.delete(key);
            this.entries.set(key, { value, expires: options.now + options.ttl });
            while (this.entries.size > this.capacity) {
              this.entries.delete(this.entries.keys().next().value!);
            }
          }

          get(key: string, options: { now: number }): T | undefined {
            const entry = this.entries.get(key);
            if (!entry) return undefined;
            if (options.now > entry.expires) {
              this.entries.delete(key);
              return undefined;
            }
            return entry.value;
          }
        }
    """).replace(
        "constructor(readonly capacity = 64) {}",
        "readonly capacity: number;\n  constructor(capacity = 64) { this.capacity = capacity; }",
    ),
    "src/pagination.ts": _clean("""
        export type Identified = { id: string };
        export function page<T extends Identified>(
          records: T[], options: { cursor?: string; limit?: number } = {},
        ): { items: T[]; next_cursor: string | null } {
          const limit = options.limit ?? 20;
          if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
            throw new Error("limit must be between 1 and 100");
          }
          let ordered = [...records].sort((a, b) => a.id.localeCompare(b.id));
          if (options.cursor !== undefined) {
            ordered = ordered.filter(item => item.id >= options.cursor!);
          }
          const selected = ordered.slice(0, limit);
          return { items: selected,
            next_cursor: ordered.length > limit ? selected.at(-1)!.id : null };
        }
    """),
    "src/repository.ts": _clean("""
        export type Document = { id: string; body: unknown; revision: number };
        export type Event = { key: string; payload: unknown; sequence: number };
        export class ConflictError extends Error {}

        export class Repository {
          readonly records = new Map<string, Document>();
          readonly events = new Map<string, Event>();

          create(id: string, body: unknown): Document {
            const record = { id, body: structuredClone(body), revision: 1 };
            this.records.set(id, record);
            return structuredClone(record);
          }

          update(id: string, body: unknown, options: { expected_revision: number }): Document {
            const current = this.records.get(id)!;
            if (options.expected_revision > current.revision) {
              throw new ConflictError("revision conflict");
            }
            const updated = { id, body: structuredClone(body), revision: current.revision + 1 };
            this.records.set(id, updated);
            return structuredClone(updated);
          }

          putEvent(key: string, payload: unknown): Event {
            const event = { key, payload: structuredClone(payload), sequence: this.events.size + 1 };
            this.events.set(key, event);
            return structuredClone(event);
          }
        }
    """),
    "src/security.ts": _clean("""
        export function canAccess(scopes: string[], resource: string, action: string): boolean {
          const required = resource + ":" + action;
          return scopes.some(scope => required.includes(scope) || scope === resource + ":*");
        }

        export function resolveUnder(root: string, relative: string): string {
          if (relative.startsWith("/")) throw new Error("absolute keys are not allowed");
          const parts: string[] = [];
          for (const part of (root.replace(/\\/$/, "") + "/" + relative).split("/")) {
            if (part === "..") parts.pop();
            else if (part !== "" && part !== ".") parts.push(part);
          }
          const candidate = "/" + parts.join("/");
          if (!candidate.startsWith(root)) throw new Error("key escapes storage root");
          return candidate;
        }
    """),
    "src/graph.ts": _clean("""
        export function dependencies(graph: Record<string, string[]>, start: string): string[] {
          return [...new Set(graph[start] ?? [])].filter(item => item !== start).sort();
        }
    """),
    "src/retry.ts": _clean("""
        export class TemporaryError extends Error {}

        export function runWithRetry<T>(operation: () => T, maxAttempts = 3): T {
          if (!Number.isInteger(maxAttempts) || maxAttempts < 1) {
            throw new Error("maxAttempts must be positive");
          }
          for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try { return operation(); }
            catch (error) {
              if (attempt === maxAttempts - 1) throw error;
            }
          }
          throw new Error("unreachable");
        }
    """),
    "src/config.ts": _clean("""
        export function parseFlag(value: unknown, defaultValue = false): boolean {
          if (value === undefined || value === null) return defaultValue;
          return Boolean(value);
        }
    """),
    "src/search.ts": _clean("""
        export type SearchDocument = { id: string; title: string; body: string };
        export function tokens(value: string): Set<string> {
          return new Set(value.toLowerCase().match(/[a-z0-9]+/g) ?? []);
        }
        export function search(records: SearchDocument[], query: string): SearchDocument[] {
          const wanted = tokens(query);
          if (!wanted.size) return [];
          return records.map(record => {
            const found = tokens(record.title + " " + record.body);
            const score = [...wanted].filter(word => found.has(word)).length;
            return { record, score };
          }).filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score || a.record.id.localeCompare(b.record.id))
            .map(item => item.record);
        }
    """),
    "src/billing.ts": _clean("""
        export function proratedCents(monthlyCents: number, activeDays: number, periodDays: number): number {
          if (![monthlyCents, activeDays, periodDays].every(value => Number.isSafeInteger(value) && value >= 0)) {
            throw new Error("arguments must be nonnegative safe integers");
          }
          if (periodDays === 0 || activeDays > periodDays) throw new Error("invalid billing period");
          return Math.floor(monthlyCents * activeDays / periodDays);
        }
    """),
    "src/service.ts": _clean("""
        import { TTLCache } from "./cache.ts";
        import { parseFlag } from "./config.ts";
        import { dependencies } from "./graph.ts";
        import { page } from "./pagination.ts";
        import { Repository } from "./repository.ts";
        import { search, type SearchDocument } from "./search.ts";
        import { canAccess, resolveUnder } from "./security.ts";

        export class DocumentService {
          readonly repository = new Repository();
          readonly cache: TTLCache<unknown>;
          constructor(capacity = 64) { this.cache = new TTLCache(capacity); }
          cachedDocument(id: string, now: number): unknown { return this.cache.get(id, { now }); }
          listDocuments(cursor?: string, limit = 20) {
            return page([...this.repository.records.values()], { cursor, limit });
          }
          dependenciesFor(graph: Record<string, string[]>, id: string): string[] {
            return dependencies(graph, id);
          }
          searchDocuments(records: SearchDocument[], query: string): SearchDocument[] {
            return search(records, query);
          }
          storageKey(root: string, relative: string): string { return resolveUnder(root, relative); }
          authorized(scopes: string[], resource: string, action: string): boolean {
            return canAccess(scopes, resource, action);
          }
          featureEnabled(value: unknown): boolean { return parseFlag(value); }
        }
    """),
}

SPECS = [
    (
        "ttl-boundary",
        "cache",
        "TTLCache.get",
        "TTLCache.get",
        "Fix cache expiration at the TTL boundary. A document cached at time 100 with TTL 10 must be unavailable at time 110 and afterwards, and expired entries must be removed. Before the deadline, return its value without changing its expiration; overwriting a key starts the new TTL. Verify the DocumentService cache path as well.",
    ),
    (
        "lru-eviction",
        "cache",
        "TTLCache.get",
        "TTLCache.get",
        "Fix the bounded document cache so it evicts the least recently used live key. A successful get must refresh recency without extending its TTL. Updating a key also makes it most recent, cache misses must not evict anything, and the capacity bound must hold. Preserve the existing API and expiration behavior.",
    ),
    (
        "cursor-pagination",
        "pagination",
        "page",
        "page",
        "Fix cursor pagination so traversing every page emits each document exactly once in ascending ID order. A cursor is the last emitted ID, so the next page contains strictly greater IDs even when that cursor was deleted. Keep the existing limit validation, do not mutate input records, and return a null next_cursor after the final page. Verify DocumentService integration.",
    ),
    (
        "optimistic-revision",
        "repository",
        "Repository.update",
        "Repository.update",
        "Fix optimistic document updates. An update may succeed only when expected_revision exactly equals the current revision. Stale and future revisions must raise ConflictError without modifying the stored document. A successful update increments the revision once and still isolates returned bodies from caller mutation.",
    ),
    (
        "scope-authorization",
        "security",
        "can_access",
        "canAccess",
        "Fix authorization scope matching. Grant access only for the exact resource:action string or the exact resource:* wildcard. Empty scopes, partial action/resource strings, unrelated wildcards, and similar resource prefixes must not grant access. Preserve DocumentService's authorization API.",
    ),
    (
        "storage-containment",
        "security",
        "resolve_under",
        "resolveUnder",
        "Fix POSIX storage-key containment. Normalize . and .. segments and allow a relative key only when its normalized path is the root itself or a descendant separated by /. Reject absolute keys and traversal into a sibling directory whose name begins with the storage root's name (for example root /srv/data and key ../database/secret). Preserve valid nested keys and the storage service API. No filesystem or symlink support is required.",
    ),
    (
        "transitive-dependencies",
        "graph",
        "dependencies",
        "dependencies",
        "Fix dependency discovery to include every transitively reachable document exactly once, in ascending ID order. Exclude the starting document, handle cycles and self-edges without looping, and treat missing graph entries as leaves. Preserve DocumentService integration and leave the caller's graph unchanged.",
    ),
    (
        "selective-retry",
        "retry",
        "run_with_retry",
        "runWithRetry",
        "Fix retry classification: retry only TemporaryError, for at most the configured total number of attempts. Return the first successful result; rethrow the final temporary failure object unchanged. Other exceptions must escape on their first attempt. Preserve validation that at least one attempt is required.",
    ),
    (
        "boolean-config",
        "config",
        "parse_flag",
        "parseFlag",
        "Fix feature flag parsing. Accept boolean values unchanged and strings true/false, 1/0, yes/no, on/off case-insensitively with surrounding whitespace. A missing/null value uses the supplied default. Reject all other values, including numeric values, empty strings, lists/objects and unknown strings. Verify the DocumentService feature flag path.",
    ),
    (
        "and-search",
        "search",
        "search",
        "search",
        "Fix document search so every normalized query token must appear in a record's title or body. Preserve case-insensitive alphanumeric tokenization, empty-query results, ascending ID order for tied results, and input immutability. Partial-token substrings do not count. Verify the DocumentService search path.",
    ),
    (
        "billing-rounding",
        "billing",
        "prorated_cents",
        "proratedCents",
        "Fix prorated billing to round the nonnegative rational cent amount half up rather than truncate. Keep all current integer and period validation, charge exactly the monthly amount for a full period, and return zero for no active days. Avoid binary floating-point rounding errors; TypeScript must support safe-integer inputs whenever the rounded result is safe, even if intermediate products exceed Number.MAX_SAFE_INTEGER.",
    ),
    (
        "idempotent-events",
        "repository",
        "Repository.put_event",
        "Repository.putEvent",
        "Fix the event repository's idempotency contract. The first event stored for a key wins: duplicate submissions return that original event and must not overwrite payload or sequence. Assign consecutive sequence numbers only to new keys. Stored payloads and returned events must remain isolated from caller mutation.",
    ),
]


def task_definitions() -> list[dict[str, Any]]:
    tasks = []
    for language in LANGUAGES:
        prefix, suffix = ("py", ".py") if language == "python" else ("ts", ".ts")
        source_dir = "atlas" if language == "python" else "src"
        for slug, module, py_symbol, ts_symbol, request in SPECS:
            symbol = py_symbol if language == "python" else ts_symbol
            tasks.append(
                {
                    "id": f"{prefix}-{slug}",
                    "language": language,
                    "repository": f"atlas-{language}-v1",
                    "starting_repository": {
                        "generator": "benchmarks.corpus.build_repository",
                        "language": language,
                        "version": CORPUS_VERSION,
                    },
                    "prompt": f"In this {language.title()} Atlas document-service repository, {request}\n\nImplement the change in the production source. Use the existing offline smoke tests and add focused regression tests if useful. Do not inspect or modify benchmark machinery, grading files, or files outside this repository. Do not change the dependency or build configuration. Finish with a brief description and the tests you ran.",
                    "target_files": [f"{source_dir}/{module}{suffix}"],
                    "expected_symbols": [f"{source_dir}.{module}.{symbol}"],
                    "oracle_id": slug,
                    "checks": {
                        "held_out_behavior": True,
                        "smoke": True,
                        "typescript_typecheck": language == "typescript",
                    },
                }
            )
    return tasks


def _repository_files(language: str) -> dict[str, str]:
    if language not in LANGUAGES:
        raise ValueError(f"unsupported language: {language}")
    files = dict(PYTHON_SOURCES if language == "python" else TYPESCRIPT_SOURCES)
    smoke_command = (
        "python -m unittest discover -s tests -v"
        if language == "python"
        else "node --test tests/*.test.mjs"
    )
    files["README.md"] = _clean(f"""
        # Atlas document service ({language})

        An offline library for a document API: caching, persistence, search,
        storage authorization, pagination, dependency graphs, and billing.
        All time is injected. There are no credentials or network services.

        Run visible smoke tests: `{smoke_command}`.
        The service module connects low-level modules to the application API.
        Existing smoke tests exercise happy paths, not every boundary case.
    """)
    files["AGENTS.md"] = _clean(f"""
        # Development

        Use this isolated checkout. Production code is in
        {"atlas/" if language == "python" else "src/"}. Run `{smoke_command}`.
        Tests must remain offline and deterministic. Preserve public interfaces.
        Do not inspect or alter benchmark machinery or grading files outside
        this repository. Implement fixes in source, not by weakening tests.
    """)
    files[".gitignore"] = "__pycache__/\n*.pyc\nnode_modules/\n.cache/\n"
    if language == "python":
        files["tests/test_smoke.py"] = _clean("""
            import unittest
            from atlas.service import DocumentService


            class SmokeTests(unittest.TestCase):
                def test_document_lifecycle(self):
                    service = DocumentService()
                    document = service.repository.create("a", {"title": "Welcome"})
                    self.assertEqual(document["revision"], 1)
                    self.assertEqual(service.list_documents()["items"], [document])
                    service.cache.put("a", document, now=0, ttl=10)
                    self.assertEqual(service.cached_document("a", now=1), document)

                def test_service_helpers(self):
                    service = DocumentService()
                    self.assertTrue(service.authorized(["docs:read"], "docs", "read"))
                    self.assertEqual(service.storage_key("/srv/data", "docs/a"), "/srv/data/docs/a")
                    self.assertEqual(service.dependencies_for({"a": ["b"]}, "a"), ["b"])


            if __name__ == "__main__":
                unittest.main()
        """)
    else:
        files["package.json"] = (
            json.dumps(
                {
                    "name": "atlas-typescript-benchmark",
                    "private": True,
                    "type": "module",
                    "scripts": {"test": "node --test tests/*.test.mjs"},
                },
                indent=2,
            )
            + "\n"
        )
        files["tsconfig.json"] = (
            json.dumps(
                {
                    "compilerOptions": {
                        "target": "ES2022",
                        "module": "NodeNext",
                        "moduleResolution": "NodeNext",
                        "allowImportingTsExtensions": True,
                        "noEmit": True,
                        "strict": True,
                        "skipLibCheck": True,
                        "types": [],
                    },
                    "include": ["src/**/*.ts"],
                },
                indent=2,
            )
            + "\n"
        )
        files["tests/smoke.test.mjs"] = _clean("""
            import test from "node:test";
            import assert from "node:assert/strict";
            import { DocumentService } from "../src/service.ts";

            test("document lifecycle", () => {
              const service = new DocumentService();
              const document = service.repository.create("a", { title: "Welcome" });
              assert.equal(document.revision, 1);
              assert.deepEqual(service.listDocuments().items, [document]);
              service.cache.put("a", document, { now: 0, ttl: 10 });
              assert.deepEqual(service.cachedDocument("a", 1), document);
            });
            test("service helpers", () => {
              const service = new DocumentService();
              assert.equal(service.authorized(["docs:read"], "docs", "read"), true);
              assert.equal(service.storageKey("/srv/data", "docs/a"), "/srv/data/docs/a");
              assert.deepEqual(service.dependenciesFor({ a: ["b"] }, "a"), ["b"]);
            });
        """)
    return files


def build_repository(language: str, destination: Path) -> None:
    """Write a deterministic baseline without Git metadata or external dependencies."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError(f"destination must be empty: {destination}")
    for relative, content in _repository_files(language).items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


PYTHON_CASES = {
    "ttl-boundary": """
        def test_deadline_and_service(self):
            from atlas.service import DocumentService
            service = DocumentService()
            service.cache.put("a", "old", now=100, ttl=10)
            self.assertEqual(service.cached_document("a", now=109.999), "old")
            self.assertIsNone(service.cached_document("a", now=110))
            self.assertNotIn("a", service.cache.entries)

        def test_overwrite_and_zero_ttl(self):
            from atlas.cache import TTLCache
            cache = TTLCache()
            cache.put("a", 1, now=0, ttl=2)
            cache.put("a", 2, now=1, ttl=10)
            self.assertEqual(cache.get("a", now=3), 2)
            self.assertIsNone(cache.get("a", now=11))
            cache.put("zero", 1, now=0, ttl=0)
            self.assertIsNone(cache.get("zero", now=0))
    """,
    "lru-eviction": """
        def test_successful_read_refreshes_recency(self):
            from atlas.cache import TTLCache
            cache = TTLCache(2)
            cache.put("a", 1, now=0, ttl=100)
            cache.put("b", 2, now=0, ttl=100)
            self.assertEqual(cache.get("a", now=1), 1)
            cache.put("c", 3, now=2, ttl=100)
            self.assertIsNone(cache.get("b", now=2))
            self.assertEqual(cache.get("a", now=2), 1)
            self.assertEqual(len(cache.entries), 2)

        def test_updates_misses_and_expiration(self):
            from atlas.cache import TTLCache
            cache = TTLCache(2)
            cache.put("a", 1, now=0, ttl=10)
            cache.put("b", 2, now=0, ttl=100)
            self.assertIsNone(cache.get("missing", now=1))
            cache.put("a", 9, now=1, ttl=10)
            cache.put("c", 3, now=2, ttl=100)
            self.assertIsNone(cache.get("b", now=2))
            self.assertEqual(cache.get("a", now=5), 9)
            self.assertIsNone(cache.get("a", now=12))
    """,
    "cursor-pagination": """
        def test_walk_and_no_mutation(self):
            from atlas.pagination import page
            records = [{"id": key} for key in ["d", "a", "c", "b", "e"]]
            original = deepcopy(records)
            seen, cursor = [], None
            for _ in range(10):
                current = page(records, cursor=cursor, limit=2)
                seen.extend(item["id"] for item in current["items"])
                cursor = current["next_cursor"]
                if cursor is None:
                    break
            self.assertEqual(seen, ["a", "b", "c", "d", "e"])
            self.assertIsNone(cursor)
            self.assertEqual(records, original)

        def test_deleted_cursor_and_service(self):
            from atlas.pagination import page
            from atlas.service import DocumentService
            self.assertEqual(page([{"id": "a"}, {"id": "d"}], cursor="b", limit=1)["items"], [{"id": "d"}])
            service = DocumentService()
            for key in ("b", "a", "c"):
                service.repository.create(key, {})
            self.assertEqual([item["id"] for item in service.list_documents(cursor="b")["items"]], ["c"])
            for limit in (0, -1, 101):
                with self.assertRaises(ValueError):
                    page([], limit=limit)
    """,
    "optimistic-revision": """
        def test_conflicts_are_atomic(self):
            from atlas.repository import Repository, ConflictError
            repository = Repository()
            repository.create("a", {"value": 1})
            repository.update("a", {"value": 2}, expected_revision=1)
            for revision in (1, 0, 99):
                with self.assertRaises(ConflictError):
                    repository.update("a", {"value": 99}, expected_revision=revision)
                self.assertEqual(repository.records["a"], {"id": "a", "body": {"value": 2}, "revision": 2})

        def test_success_and_defensive_copy(self):
            from atlas.repository import Repository
            repository = Repository()
            repository.create("a", {})
            body = {"items": [1]}
            result = repository.update("a", body, expected_revision=1)
            body["items"].append(2)
            result["body"]["items"].append(3)
            self.assertEqual(repository.records["a"]["body"], {"items": [1]})
            self.assertEqual(result["revision"], 2)
    """,
    "scope-authorization": """
        def test_exact_and_resource_wildcard(self):
            from atlas.service import DocumentService
            service = DocumentService()
            for scopes in (["docs:read"], ["docs:*"], ["other:write", "docs:read"]):
                self.assertTrue(service.authorized(scopes, "docs", "read"))

        def test_partial_and_unrelated_scopes_denied(self):
            from atlas.security import can_access
            for scope in ("", "read", "docs", "doc", "docs:rea", "*", "*:read", "doc:*", "docs:write", "archive:read"):
                self.assertFalse(can_access([scope], "docs", "read"), scope)
            self.assertFalse(can_access([], "docs", "read"))
    """,
    "storage-containment": """
        def test_sibling_prefix_and_absolute_denied(self):
            from atlas.security import resolve_under
            for key in ("../database/secret", "../data-backup/key", "../../etc/passwd", "/srv/data/absolute"):
                with self.assertRaises(ValueError, msg=key):
                    resolve_under("/srv/data", key)

        def test_normalization_and_service(self):
            from atlas.service import DocumentService
            service = DocumentService()
            for key, expected in (("", "/srv/data"), (".", "/srv/data"), ("docs/../a/./b", "/srv/data/a/b"), ("docs..txt", "/srv/data/docs..txt")):
                self.assertEqual(service.storage_key("/srv/data", key), expected)
            self.assertEqual(service.storage_key("/srv/data/", "a"), "/srv/data/a")
    """,
    "transitive-dependencies": """
        def test_cycles_diamonds_and_input(self):
            from atlas.service import DocumentService
            graph = {"a": ["c", "b", "a"], "b": ["d"], "c": ["d", "e"], "d": ["a"], "e": ["leaf"]}
            original = deepcopy(graph)
            self.assertEqual(DocumentService().dependencies_for(graph, "a"), ["b", "c", "d", "e", "leaf"])
            self.assertEqual(graph, original)

        def test_missing_and_long_chain(self):
            from atlas.graph import dependencies
            self.assertEqual(dependencies({}, "missing"), [])
            graph = {str(i): [str(i + 1)] for i in range(300)}
            self.assertEqual(dependencies(graph, "0"), sorted(str(i) for i in range(1, 301)))
    """,
    "selective-retry": """
        def test_permanent_error_not_retried(self):
            from atlas.retry import run_with_retry
            calls = []
            error = ValueError("permanent")
            def operation():
                calls.append(1)
                raise error
            with self.assertRaises(ValueError) as caught:
                run_with_retry(operation, max_attempts=5)
            self.assertIs(caught.exception, error)
            self.assertEqual(len(calls), 1)

        def test_temporary_success_exhaustion_and_validation(self):
            from atlas.retry import run_with_retry, TemporaryError
            calls = []
            error = TemporaryError("later")
            def operation():
                calls.append(1)
                if len(calls) < 3:
                    raise error
                return {"ok": True}
            self.assertEqual(run_with_retry(operation, max_attempts=3), {"ok": True})
            self.assertEqual(len(calls), 3)
            calls.clear()
            with self.assertRaises(TemporaryError) as caught:
                run_with_retry(operation, max_attempts=2)
            self.assertIs(caught.exception, error)
            self.assertEqual(len(calls), 2)
            with self.assertRaises(ValueError):
                run_with_retry(lambda: None, max_attempts=0)
    """,
    "boolean-config": """
        def test_supported_values_and_service(self):
            from atlas.config import parse_flag
            from atlas.service import DocumentService
            for value in (True, "true", "  TRUE ", "1", "Yes", "ON"):
                self.assertTrue(DocumentService().feature_enabled(value), repr(value))
            for value in (False, "false", "  FALSE ", "0", "No", "OFF"):
                self.assertFalse(DocumentService().feature_enabled(value), repr(value))
            self.assertTrue(parse_flag(None, default=True))
            self.assertFalse(parse_flag(None))

        def test_invalid_values_rejected(self):
            from atlas.config import parse_flag
            for value in (0, 1, 1.0, "", "truthy", [], {}, ["true"]):
                with self.assertRaises((ValueError, TypeError), msg=repr(value)):
                    parse_flag(value)
    """,
    "and-search": """
        def test_all_tokens_and_no_mutation(self):
            from atlas.service import DocumentService
            records = [{"id": "b", "title": "Cloud", "body": "CACHE docs"}, {"id": "a", "title": "cache cloud", "body": "guide"}, {"id": "c", "title": "Cloud", "body": "unrelated"}, {"id": "d", "title": "cloudy", "body": "cache"}]
            original = deepcopy(records)
            self.assertEqual([r["id"] for r in DocumentService().search_documents(records, "CLOUD cache")], ["a", "b"])
            self.assertEqual(records, original)

        def test_empty_repeated_and_punctuation(self):
            from atlas.search import search
            records = [{"id": "a", "title": "alpha beta", "body": ""}, {"id": "b", "title": "alpha", "body": ""}]
            self.assertEqual(search(records, "!!!"), [])
            self.assertEqual([r["id"] for r in search(records, "alpha ALPHA,beta")], ["a"])
    """,
    "billing-rounding": """
        def test_half_up_and_exact_integer_arithmetic(self):
            from atlas.billing import prorated_cents
            for monthly, active, days in ((101, 1, 2), (100, 1, 3), (100, 2, 3), (99, 30, 30), (0, 0, 31), (9007199254740991, 6, 7), (9007199254740991, 999, 1000)):
                numerator = monthly * active
                expected = numerator // days + (2 * (numerator % days) >= days)
                self.assertEqual(prorated_cents(monthly, active, days), expected)

        def test_validation_and_zero(self):
            from atlas.billing import prorated_cents
            self.assertEqual(prorated_cents(100, 0, 31), 0)
            for args in ((-1, 1, 2), (10, 3, 2), (10, 0, 0), (1.2, 1, 2), (True, 1, 2)):
                with self.assertRaises(ValueError):
                    prorated_cents(*args)
    """,
    "idempotent-events": """
        def test_first_payload_and_sequence_win(self):
            from atlas.repository import Repository
            repository = Repository()
            first = repository.put_event("a", {"value": 1})
            duplicate = repository.put_event("a", {"value": 999})
            self.assertEqual(duplicate, first)
            self.assertEqual(repository.events["a"], first)
            self.assertEqual(repository.put_event("b", {})["sequence"], 2)
            self.assertEqual(repository.put_event("a", {})["sequence"], 1)

        def test_nested_defensive_copies(self):
            from atlas.repository import Repository
            repository = Repository()
            payload = {"items": [1]}
            event = repository.put_event("a", payload)
            payload["items"].append(2)
            event["payload"]["items"].append(3)
            duplicate = repository.put_event("a", {})
            self.assertEqual(duplicate["payload"], {"items": [1]})
            duplicate["payload"]["items"].append(4)
            self.assertEqual(repository.events["a"]["payload"], {"items": [1]})
    """,
}

TYPESCRIPT_CASES = {
    "ttl-boundary": """
        test("deadline and service", () => {
          const service = new DocumentService();
          service.cache.put("a", "old", { now: 100, ttl: 10 });
          assert.equal(service.cachedDocument("a", 109.999), "old");
          assert.equal(service.cachedDocument("a", 110), undefined);
          assert.equal(service.cache.entries.has("a"), false);
        });
        test("overwrite and zero TTL", () => {
          const cache = new TTLCache();
          cache.put("a", 1, { now: 0, ttl: 2 });
          cache.put("a", 2, { now: 1, ttl: 10 });
          assert.equal(cache.get("a", { now: 3 }), 2);
          assert.equal(cache.get("a", { now: 11 }), undefined);
          cache.put("zero", 1, { now: 0, ttl: 0 });
          assert.equal(cache.get("zero", { now: 0 }), undefined);
        });
    """,
    "lru-eviction": """
        test("successful read refreshes recency", () => {
          const cache = new TTLCache(2);
          cache.put("a", 1, { now: 0, ttl: 100 });
          cache.put("b", 2, { now: 0, ttl: 100 });
          assert.equal(cache.get("a", { now: 1 }), 1);
          cache.put("c", 3, { now: 2, ttl: 100 });
          assert.equal(cache.get("b", { now: 2 }), undefined);
          assert.equal(cache.get("a", { now: 2 }), 1);
          assert.equal(cache.entries.size, 2);
        });
        test("updates misses and expiration", () => {
          const cache = new TTLCache(2);
          cache.put("a", 1, { now: 0, ttl: 10 });
          cache.put("b", 2, { now: 0, ttl: 100 });
          assert.equal(cache.get("missing", { now: 1 }), undefined);
          cache.put("a", 9, { now: 1, ttl: 10 });
          cache.put("c", 3, { now: 2, ttl: 100 });
          assert.equal(cache.get("b", { now: 2 }), undefined);
          assert.equal(cache.get("a", { now: 5 }), 9);
          assert.equal(cache.get("a", { now: 12 }), undefined);
        });
    """,
    "cursor-pagination": """
        test("walk and no mutation", () => {
          const records = ["d", "a", "c", "b", "e"].map(id => ({ id }));
          const original = structuredClone(records), seen = [];
          let cursor;
          for (let i = 0; i < 10; i++) {
            const current = page(records, { cursor, limit: 2 });
            seen.push(...current.items.map(item => item.id));
            cursor = current.next_cursor;
            if (cursor === null) break;
          }
          assert.deepEqual(seen, ["a", "b", "c", "d", "e"]);
          assert.equal(cursor, null);
          assert.deepEqual(records, original);
        });
        test("deleted cursor and service", () => {
          assert.deepEqual(page([{ id: "a" }, { id: "d" }], { cursor: "b", limit: 1 }).items, [{ id: "d" }]);
          const service = new DocumentService();
          for (const key of ["b", "a", "c"]) service.repository.create(key, {});
          assert.deepEqual(service.listDocuments("b").items.map(item => item.id), ["c"]);
          for (const limit of [0, -1, 101]) assert.throws(() => page([], { limit }));
        });
    """,
    "optimistic-revision": """
        test("conflicts are atomic", () => {
          const repository = new Repository();
          repository.create("a", { value: 1 });
          repository.update("a", { value: 2 }, { expected_revision: 1 });
          for (const revision of [1, 0, 99]) {
            assert.throws(() => repository.update("a", { value: 99 }, { expected_revision: revision }), ConflictError);
            assert.deepEqual(repository.records.get("a"), { id: "a", body: { value: 2 }, revision: 2 });
          }
        });
        test("success and defensive copy", () => {
          const repository = new Repository();
          repository.create("a", {});
          const body = { items: [1] };
          const result = repository.update("a", body, { expected_revision: 1 });
          body.items.push(2); result.body.items.push(3);
          assert.deepEqual(repository.records.get("a").body, { items: [1] });
          assert.equal(result.revision, 2);
        });
    """,
    "scope-authorization": """
        test("exact and resource wildcard", () => {
          const service = new DocumentService();
          for (const scopes of [["docs:read"], ["docs:*"], ["other:write", "docs:read"]]) {
            assert.equal(service.authorized(scopes, "docs", "read"), true);
          }
        });
        test("partial and unrelated scopes denied", () => {
          for (const scope of ["", "read", "docs", "doc", "docs:rea", "*", "*:read", "doc:*", "docs:write", "archive:read"]) {
            assert.equal(canAccess([scope], "docs", "read"), false, scope);
          }
          assert.equal(canAccess([], "docs", "read"), false);
        });
    """,
    "storage-containment": """
        test("sibling prefix and absolute denied", () => {
          for (const key of ["../database/secret", "../data-backup/key", "../../etc/passwd", "/srv/data/absolute"]) {
            assert.throws(() => resolveUnder("/srv/data", key), undefined, key);
          }
        });
        test("normalization and service", () => {
          const service = new DocumentService();
          for (const [key, expected] of [["", "/srv/data"], [".", "/srv/data"], ["docs/../a/./b", "/srv/data/a/b"], ["docs..txt", "/srv/data/docs..txt"]]) {
            assert.equal(service.storageKey("/srv/data", key), expected);
          }
          assert.equal(service.storageKey("/srv/data/", "a"), "/srv/data/a");
        });
    """,
    "transitive-dependencies": """
        test("cycles diamonds and input", () => {
          const graph = { a: ["c", "b", "a"], b: ["d"], c: ["d", "e"], d: ["a"], e: ["leaf"] };
          const original = structuredClone(graph);
          assert.deepEqual(new DocumentService().dependenciesFor(graph, "a"), ["b", "c", "d", "e", "leaf"]);
          assert.deepEqual(graph, original);
        });
        test("missing and long chain", () => {
          assert.deepEqual(dependencies({}, "missing"), []);
          const graph = Object.fromEntries(Array.from({ length: 300 }, (_, i) => [String(i), [String(i + 1)]]));
          assert.deepEqual(dependencies(graph, "0"), Array.from({ length: 300 }, (_, i) => String(i + 1)).sort());
        });
    """,
    "selective-retry": """
        test("permanent error not retried", () => {
          let calls = 0; const error = new TypeError("permanent");
          assert.throws(() => runWithRetry(() => { calls++; throw error; }, 5), value => value === error);
          assert.equal(calls, 1);
        });
        test("temporary success exhaustion validation", () => {
          let calls = 0; const error = new TemporaryError("later");
          const operation = () => { calls++; if (calls < 3) throw error; return { ok: true }; };
          assert.deepEqual(runWithRetry(operation, 3), { ok: true });
          assert.equal(calls, 3); calls = 0;
          assert.throws(() => runWithRetry(operation, 2), value => value === error);
          assert.equal(calls, 2);
          assert.throws(() => runWithRetry(() => null, 0));
        });
    """,
    "boolean-config": """
        test("supported values and service", () => {
          const service = new DocumentService();
          for (const value of [true, "true", "  TRUE ", "1", "Yes", "ON"]) assert.equal(service.featureEnabled(value), true);
          for (const value of [false, "false", "  FALSE ", "0", "No", "OFF"]) assert.equal(service.featureEnabled(value), false);
          assert.equal(parseFlag(null, true), true);
          assert.equal(parseFlag(undefined), false);
        });
        test("invalid values rejected", () => {
          for (const value of [0, 1, 1.0, "", "truthy", [], {}, ["true"]]) assert.throws(() => parseFlag(value));
        });
    """,
    "and-search": """
        test("all tokens and no mutation", () => {
          const records = [{ id: "b", title: "Cloud", body: "CACHE docs" }, { id: "a", title: "cache cloud", body: "guide" }, { id: "c", title: "Cloud", body: "unrelated" }, { id: "d", title: "cloudy", body: "cache" }];
          const original = structuredClone(records);
          assert.deepEqual(new DocumentService().searchDocuments(records, "CLOUD cache").map(item => item.id), ["a", "b"]);
          assert.deepEqual(records, original);
        });
        test("empty repeated and punctuation", () => {
          const records = [{ id: "a", title: "alpha beta", body: "" }, { id: "b", title: "alpha", body: "" }];
          assert.deepEqual(search(records, "!!!"), []);
          assert.deepEqual(search(records, "alpha ALPHA,beta").map(item => item.id), ["a"]);
        });
    """,
    "billing-rounding": """
        test("half up and exact integer arithmetic", () => {
          for (const [monthly, active, days] of [[101, 1, 2], [100, 1, 3], [100, 2, 3], [99, 30, 30], [0, 0, 31], [9007199254740991, 6, 7], [9007199254740991, 999, 1000]]) {
            const numerator = BigInt(monthly) * BigInt(active), denominator = BigInt(days);
            const expected = Number(numerator / denominator + (2n * (numerator % denominator) >= denominator ? 1n : 0n));
            assert.equal(proratedCents(monthly, active, days), expected);
          }
        });
        test("validation and zero", () => {
          assert.equal(proratedCents(100, 0, 31), 0);
          for (const args of [[-1, 1, 2], [10, 3, 2], [10, 0, 0], [1.2, 1, 2], [true, 1, 2]]) assert.throws(() => proratedCents(...args));
        });
    """,
    "idempotent-events": """
        test("first payload and sequence win", () => {
          const repository = new Repository();
          const first = repository.putEvent("a", { value: 1 });
          assert.deepEqual(repository.putEvent("a", { value: 999 }), first);
          assert.deepEqual(repository.events.get("a"), first);
          assert.equal(repository.putEvent("b", {}).sequence, 2);
          assert.equal(repository.putEvent("a", {}).sequence, 1);
        });
        test("nested defensive copies", () => {
          const repository = new Repository(), payload = { items: [1] };
          const event = repository.putEvent("a", payload);
          payload.items.push(2); event.payload.items.push(3);
          const duplicate = repository.putEvent("a", {});
          assert.deepEqual(duplicate.payload, { items: [1] });
          duplicate.payload.items.push(4);
          assert.deepEqual(repository.events.get("a").payload, { items: [1] });
        });
    """,
}


def _python_oracle(slug: str) -> str:
    return (
        "import json, unittest\nfrom copy import deepcopy\n\nclass BehaviorTests(unittest.TestCase):\n"
        + textwrap.indent(_clean(PYTHON_CASES[slug]), "    ")
        + _clean("""

            if __name__ == "__main__":
                suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
                result = unittest.TextTestRunner(verbosity=2).run(suite)
                print("CORPUS_RESULT=" + json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)}))
                raise SystemExit(not result.wasSuccessful())
        """)
    )


def _typescript_oracle(slug: str, worktree: Path) -> str:
    imports = [
        ("cache", "TTLCache"),
        ("service", "DocumentService"),
        ("pagination", "page"),
        ("repository", "Repository, ConflictError"),
        ("security", "canAccess, resolveUnder"),
        ("graph", "dependencies"),
        ("retry", "runWithRetry, TemporaryError"),
        ("config", "parseFlag"),
        ("search", "search"),
        ("billing", "proratedCents"),
    ]
    header = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
    for module, symbols in imports:
        uri = (worktree / "src" / f"{module}.ts").resolve().as_uri()
        header += f"import {{ {symbols} }} from {json.dumps(uri)};\n"
    return header + "\n" + _clean(TYPESCRIPT_CASES[slug])


def _command(
    command: list[str], cwd: Path, stem: Path, env: dict[str, str] | None = None
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, text=True, timeout=60
        )
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as error:
        code = 124
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else error.stdout or ""
        stderr = (
            error.stderr.decode() if isinstance(error.stderr, bytes) else error.stderr or ""
        ) + "\nGrader timeout after 60 seconds."
    stem.with_suffix(".stdout.log").write_text(stdout, encoding="utf-8")
    stem.with_suffix(".stderr.log").write_text(stderr, encoding="utf-8")
    counts: dict[str, int] = {}
    marker = re.search(r"^CORPUS_RESULT=(.+)$", stdout, re.MULTILINE)
    if marker:
        counts = json.loads(marker.group(1))
    elif "--test" in command:
        for field in ("tests", "pass", "fail", "cancelled", "skipped"):
            match = re.search(rf"^# {field} (\d+)$", stdout, re.MULTILINE)
            if match:
                counts[field] = int(match.group(1))
    elif "unittest" in command:
        match = re.search(r"Ran (\d+) tests?", stderr)
        if match:
            counts["tests"] = int(match.group(1))
    return {
        "command": command,
        "exit_code": code,
        "counts": counts,
        "stdout_path": str(stem.with_suffix(".stdout.log")),
        "stderr_path": str(stem.with_suffix(".stderr.log")),
    }


def grade(task_id: str, worktree: Path, artifacts: Path) -> dict[str, Any]:
    """Grade source independently; never execute repository-defined test commands."""
    tasks = {task["id"]: task for task in task_definitions()}
    if task_id not in tasks:
        raise ValueError(f"unknown task: {task_id}")
    task = tasks[task_id]
    language, slug = task["language"], task["oracle_id"]
    worktree, artifacts = Path(worktree).resolve(), Path(artifacts).resolve()
    if artifacts == worktree or worktree in artifacts.parents:
        raise ValueError("grading artifacts must be outside the agent worktree")
    artifacts.mkdir(parents=True, exist_ok=True)
    baseline = _repository_files(language)
    source_prefix = "atlas/" if language == "python" else "src/"
    protected = []
    for relative, expected in baseline.items():
        if relative.startswith(source_prefix):
            continue
        target = worktree / relative
        actual = target.read_bytes() if target.is_file() else b""
        expected_bytes = expected.encode()
        protected.append(
            {
                "file": relative,
                "unchanged": actual == expected_bytes,
                "expected_sha256": hashlib.sha256(expected_bytes).hexdigest(),
                "actual_sha256": hashlib.sha256(actual).hexdigest(),
            }
        )
    environment = dict(os.environ)
    commands = []
    if language == "python":
        environment["PYTHONPATH"] = str(worktree)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        # A fresh interpreter for every invocation avoids cross-run module caches.
        oracle = artifacts / "held_out.py"
        oracle.write_text(_python_oracle(slug), encoding="utf-8")
        commands.append(
            _command([sys.executable, str(oracle)], worktree, artifacts / "behavior", environment)
        )
        commands.append(
            _command(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                worktree,
                artifacts / "smoke",
                environment,
            )
        )
    else:
        node = shutil.which("node")
        if node is None:
            raise RuntimeError("Node 22.18+ or 24 is required for native TypeScript tests")
        oracle = artifacts / "held_out.test.mjs"
        oracle.write_text(_typescript_oracle(slug, worktree), encoding="utf-8")
        commands.append(
            _command(
                [node, "--test", "--test-reporter=tap", str(oracle)],
                worktree,
                artifacts / "behavior",
                environment,
            )
        )
        commands.append(
            _command(
                [node, "--test", "--test-reporter=tap", "tests/smoke.test.mjs"],
                worktree,
                artifacts / "smoke",
                environment,
            )
        )
        compiler = os.environ.get("MEMGLIDE_BENCHMARK_TSC")
        if compiler is None:
            local = Path(__file__).resolve().parents[1] / "frontend/node_modules/typescript/bin/tsc"
            compiler = str(local) if local.is_file() else shutil.which("tsc")
        if compiler is None:
            commands.append(
                {
                    "command": ["tsc", "--project", "tsconfig.json"],
                    "exit_code": None,
                    "counts": {},
                    "unavailable_reason": "TypeScript compiler not installed",
                }
            )
        else:
            commands.append(
                _command(
                    [node, compiler, "--project", "tsconfig.json"],
                    worktree,
                    artifacts / "typecheck",
                    environment,
                )
            )
    tamper_free = all(item["unchanged"] for item in protected)
    passed = tamper_free and all(item["exit_code"] == 0 for item in commands)
    result = {
        "task_id": task_id,
        "corpus_version": CORPUS_VERSION,
        "passed": passed,
        "success": passed,
        "exit_code": 0 if passed else 1,
        "commands": commands,
        "test_count": sum(item["counts"].get("tests", 0) for item in commands),
        "protected_files_unchanged": tamper_free,
        "protected_files": protected,
        "grading_separation": "held-out files outside worktree; not cryptographically hidden",
    }
    (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _apply_reference_fix(task_id: str, destination: Path) -> None:
    """Corpus self-check only; never place reference fixes in task worktrees."""
    language = "python" if task_id.startswith("py-") else "typescript"
    slug = task_id[3:]
    task = next(item for item in task_definitions() if item["id"] == task_id)
    path = destination / task["target_files"][0]
    source = path.read_text()
    if language == "python":
        fixes = {
            "ttl-boundary": ("if now > expires:", "if now >= expires:"),
            "lru-eviction": (
                "        return value\n",
                "        self.entries.move_to_end(key)\n        return value\n",
            ),
            "cursor-pagination": ('item["id"] >= cursor', 'item["id"] > cursor'),
            "optimistic-revision": (
                'expected_revision > current["revision"]',
                'expected_revision != current["revision"]',
            ),
            "scope-authorization": (
                'scope in required or scope == resource + ":*"',
                'scope == required or scope == resource + ":*"',
            ),
            "storage-containment": (
                "if not candidate.startswith(root_path):",
                'if root_path != "/" and candidate != root_path and not candidate.startswith(root_path + "/"): ',
            ),
            "selective-retry": ("except Exception:", "except TemporaryError:"),
            "and-search": ("if score:", "if score == len(wanted):"),
            "billing-rounding": (
                "return (monthly_cents * active_days) // period_days",
                "numerator = monthly_cents * active_days\n    return numerator // period_days + int(2 * (numerator % period_days) >= period_days)",
            ),
            "idempotent-events": (
                "    def put_event(self, key, payload):\n",
                "    def put_event(self, key, payload):\n        if key in self.events:\n            return deepcopy(self.events[key])\n",
            ),
        }
        if slug == "transitive-dependencies":
            source = _clean("""
                def dependencies(graph, start):
                    seen, pending = {start}, list(graph.get(start, []))
                    while pending:
                        node = pending.pop()
                        if node in seen:
                            continue
                        seen.add(node)
                        pending.extend(graph.get(node, []))
                    return sorted(seen - {start})
            """)
        elif slug == "boolean-config":
            source = _clean("""
                def parse_flag(value, *, default=False):
                    if value is None:
                        return default
                    if isinstance(value, bool):
                        return value
                    if isinstance(value, str):
                        normalized = value.strip().lower()
                        if normalized in {"true", "1", "yes", "on"}:
                            return True
                        if normalized in {"false", "0", "no", "off"}:
                            return False
                    raise ValueError("invalid boolean flag")
            """)
        else:
            old, new = fixes[slug]
            assert old in source
            source = source.replace(old, new)
    else:
        fixes = {
            "ttl-boundary": ("options.now > entry.expires", "options.now >= entry.expires"),
            "lru-eviction": (
                "    return entry.value;",
                "    this.entries.delete(key);\n    this.entries.set(key, entry);\n    return entry.value;",
            ),
            "cursor-pagination": ("item.id >= options.cursor!", "item.id > options.cursor!"),
            "optimistic-revision": (
                "options.expected_revision > current.revision",
                "options.expected_revision !== current.revision",
            ),
            "scope-authorization": ("required.includes(scope)", "required === scope"),
            "storage-containment": (
                "if (!candidate.startsWith(root))",
                'root = root.replace(/\\/$/, "") || "/";\n  if (root !== "/" && candidate !== root && !candidate.startsWith(root + "/"))',
            ),
            "selective-retry": (
                "if (attempt === maxAttempts - 1) throw error;",
                "if (!(error instanceof TemporaryError) || attempt === maxAttempts - 1) throw error;",
            ),
            "and-search": ("item.score > 0", "item.score === wanted.size"),
            "billing-rounding": (
                "return Math.floor(monthlyCents * activeDays / periodDays);",
                "const numerator = BigInt(monthlyCents) * BigInt(activeDays), denominator = BigInt(periodDays);\n  return Number(numerator / denominator + (2n * (numerator % denominator) >= denominator ? 1n : 0n));",
            ),
            "idempotent-events": (
                "  putEvent(key: string, payload: unknown): Event {\n",
                "  putEvent(key: string, payload: unknown): Event {\n    const existing = this.events.get(key);\n    if (existing) return structuredClone(existing);\n",
            ),
        }
        if slug == "transitive-dependencies":
            source = _clean("""
                export function dependencies(graph: Record<string, string[]>, start: string): string[] {
                  const seen = new Set([start]), pending = [...(graph[start] ?? [])];
                  while (pending.length) {
                    const node = pending.pop()!;
                    if (seen.has(node)) continue;
                    seen.add(node);
                    pending.push(...(graph[node] ?? []));
                  }
                  return [...seen].filter(node => node !== start).sort();
                }
            """)
        elif slug == "boolean-config":
            source = _clean("""
                export function parseFlag(value: unknown, defaultValue = false): boolean {
                  if (value === undefined || value === null) return defaultValue;
                  if (typeof value === "boolean") return value;
                  if (typeof value === "string") {
                    const normalized = value.trim().toLowerCase();
                    if (["true", "1", "yes", "on"].includes(normalized)) return true;
                    if (["false", "0", "no", "off"].includes(normalized)) return false;
                  }
                  throw new Error("invalid boolean flag");
                }
            """)
        else:
            old, new = fixes[slug]
            assert old in source
            source = source.replace(old, new)
    path.write_text(source, encoding="utf-8")


def validate_corpus(destination: Path) -> dict[str, Any]:
    """Prove all baseline tasks fail and independently reference-fixed tasks pass."""
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    results = []
    for task in task_definitions():
        task_root = destination / task["id"]
        baseline_root, fixed_root = task_root / "baseline", task_root / "reference"
        build_repository(task["language"], baseline_root)
        build_repository(task["language"], fixed_root)
        baseline = grade(task["id"], baseline_root, task_root / "baseline_grade")
        _apply_reference_fix(task["id"], fixed_root)
        reference = grade(task["id"], fixed_root, task_root / "reference_grade")
        valid = (
            not baseline["passed"]
            and baseline["commands"][0]["exit_code"] != 0
            and reference["passed"]
        )
        results.append(
            {
                "task_id": task["id"],
                "baseline_failed": not baseline["passed"],
                "reference_passed": reference["passed"],
                "valid": valid,
                "baseline_grade": str(task_root / "baseline_grade/grade.json"),
                "reference_grade": str(task_root / "reference_grade/grade.json"),
            }
        )
    report = {
        "corpus_version": CORPUS_VERSION,
        "task_count": len(results),
        "valid": all(item["valid"] for item in results),
        "tasks": results,
    }
    (destination / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--write-manifest", type=Path)
    args = parser.parse_args()
    if args.write_manifest:
        args.write_manifest.write_text(
            json.dumps({"corpus_version": CORPUS_VERSION, "tasks": task_definitions()}, indent=2)
            + "\n"
        )
    if args.validate:
        report = validate_corpus(args.validate)
        print(json.dumps(report, indent=2))
        raise SystemExit(not report["valid"])
