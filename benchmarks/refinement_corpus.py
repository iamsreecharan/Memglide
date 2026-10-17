"""Locked, procedural retrieval holdout with complete source-body judgments.

This module only writes and validates text fixtures. It never imports or executes
the indexed repositories. The manifest is visible, so separation is procedural.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks/refinement_holdout.json"
MANIFEST_SHA256 = "04e0825f818ebafcb037cddad2396e7df12203d5891e588c34afadf3bc10d37c"

DOMAINS = {
    "media": {
        "noun": "broadcast licence",
        "record": "programme",
        "gate": "territory",
        "limit": 48,
        "reason": "A broadcast licence cannot be released outside its permitted territory.",
    },
    "appointments": {
        "noun": "clinic appointment hold",
        "record": "appointment",
        "gate": "clinician",
        "limit": 24,
        "reason": "A clinic hold needs its assigned clinician before it can be released.",
    },
    "specimens": {
        "noun": "laboratory specimen",
        "record": "sample",
        "gate": "consent",
        "limit": 72,
        "reason": "A laboratory specimen needs recorded consent before release.",
    },
    "deployments": {
        "noun": "production deployment approval",
        "record": "rollout",
        "gate": "reviewer",
        "limit": 12,
        "reason": "A production deployment needs an assigned reviewer before release.",
    },
}

PROTOCOL = {
    "version": 1,
    "candidate_policies": ["current", "legacy"],
    "legacy_revision": "39e8df30565783a686270f8a6f422e56e41e3776",
    "ranking_freeze_required_before_first_evaluation": True,
    "default_repeats": 2,
    "context_level": 2,
    "context_budget": 8000,
    "candidate_limit": 100,
    "candidate_order": "Rotate by query and reverse on repeat two; retain every run.",
    "common_packer": "Same installed context engine, project settings and fixture for both rankers.",
    "session_state": "Fresh empty session for every query/candidate/repeat; no stored memories.",
    "caches": "Shared warm operating-system/SQLite caches, no flush or cold-cache claim.",
    "timing": "Current-process CPU and wall time, search and context separately; no model calls.",
    "percentile": "Nearest-rank p95 over retained successful observations; median p50.",
    "context_size": "Measured compact UTF-8 JSON bytes and engine planning estimate; not model usage.",
    "complete_body": (
        "Union of returned source intervals must contain every expected line, and each "
        "line must match the immutable fixture. A symbol name or graph reference is insufficient."
    ),
    "required_dependencies": (
        "Two direct helper implementations required by each primary body; imports, runtime/library "
        "semantics and transitive type declarations are outside this declared completeness judgment."
    ),
    "precision": (
        "Unique returned source files in required or optional-positive paths divided by all "
        "returned source files. Exhaustive judgments apply only to this designed fixture task scope; "
        "an unjudged file is not automatically irrelevant in a real coding task."
    ),
    "selection": (
        "Both current and legacy are eligible. Production selection must use development evidence; "
        "this fresh holdout validates the frozen choice and must not be used to tune it. Report all "
        "complete-body/dependency failures and precision, size, p50/p95 tradeoffs without hiding runs."
    ),
    "source_safety": "Write/read/parse fixture text only; never execute, import or test indexed source.",
}


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _python_sources(domain: str, details: dict[str, Any]) -> dict[str, str]:
    noun, gate, limit = details["noun"], details["gate"], details["limit"]
    return {
        "service.py": (
            f'"""Current {noun} lifecycle implementation."""\n\n'
            "from .policy import can_release, extension_deadline, may_revoke\n"
            "from .store import load_record, save_record, remove_record\n\n\n"
            "def release(records: dict, key: str, actor: str) -> dict:\n"
            f'    """Release this {noun} after its domain gate."""\n'
            "    record = load_record(records, key)\n"
            "    if not can_release(record, actor):\n"
            f'        raise ValueError("{details["reason"]}")\n'
            '    result = {**record, "status": "released", "actor": actor}\n'
            "    return save_record(records, key, result)\n\n\n"
            "def extend(records: dict, key: str, hours: int) -> dict:\n"
            f'    """Extend the {noun} while preserving its maximum lifetime."""\n'
            "    record = load_record(records, key)\n"
            "    deadline = extension_deadline(record, hours)\n"
            '    result = {**record, "deadline": deadline}\n'
            "    return save_record(records, key, result)\n\n\n"
            "def revoke(records: dict, key: str, actor: str) -> dict:\n"
            f'    """Withdraw the active {noun}; never remove a completed record."""\n'
            "    record = load_record(records, key)\n"
            "    if not may_revoke(record, actor):\n"
            '        raise ValueError("Completed or differently owned record cannot be revoked")\n'
            "    return remove_record(records, key)\n"
        ),
        "policy.py": (
            f'"""Decision rules for the {noun}, not transport or reporting."""\n\n'
            "def can_release(record: dict, actor: str) -> bool:\n"
            f'    """Validate the {gate} requirement and lifecycle state."""\n'
            f'    gate = record.get("{gate}")\n'
            '    return bool(actor and gate and record.get("status") == "pending")\n\n\n'
            "def extension_deadline(record: dict, hours: int) -> int:\n"
            f'    """Clamp a {noun} extension to {limit} hours after creation."""\n'
            "    if hours < 0:\n"
            '        raise ValueError("Extension must not be negative")\n'
            '    current = int(record["deadline"])\n'
            f'    maximum = int(record["created"]) + {limit}\n'
            "    return min(current + hours, maximum)\n\n\n"
            "def may_revoke(record: dict, actor: str) -> bool:\n"
            f'    """Require the same owner for active {noun} withdrawal."""\n'
            '    active = record.get("status") in {"pending", "released"}\n'
            '    return bool(active and actor and record.get("owner") == actor)\n'
        ),
        "store.py": (
            f'"""In-memory {noun} records used by the current domain service."""\n\n'
            "def load_record(records: dict, key: str) -> dict:\n"
            '    """Read one record and fail clearly when it does not exist."""\n'
            "    if key not in records:\n"
            '        raise KeyError("Record does not exist: " + key)\n'
            "    return dict(records[key])\n\n\n"
            "def save_record(records: dict, key: str, value: dict) -> dict:\n"
            '    """Write a detached record copy and return another detached copy."""\n'
            "    records[key] = dict(value)\n"
            "    return dict(records[key])\n\n\n"
            "def remove_record(records: dict, key: str) -> dict:\n"
            '    """Remove an existing record and expose the previous detached value."""\n'
            "    previous = dict(records[key])\n"
            "    del records[key]\n"
            "    return previous\n"
        ),
    }


def _typescript_sources(domain: str, details: dict[str, Any]) -> dict[str, str]:
    noun, gate, limit = details["noun"], details["gate"], details["limit"]
    return {
        "service.ts": (
            f"// Current {noun} lifecycle implementation.\n"
            'import { canRelease, extensionDeadline, mayRevoke } from "./policy";\n'
            'import { loadRecord, saveRecord, removeRecord } from "./store";\n'
            'import type { RecordValue } from "./types";\n\n'
            "export function release(records: Map<string, RecordValue>, key: string, actor: string): RecordValue {\n"
            f"  // Release this {noun} after its domain gate.\n"
            "  const record = loadRecord(records, key);\n"
            "  if (!canRelease(record, actor)) {\n"
            f'    throw new Error("{details["reason"]}");\n'
            "  }\n"
            '  const result = { ...record, status: "released", actor };\n'
            "  return saveRecord(records, key, result);\n"
            "}\n\n"
            "export function extend(records: Map<string, RecordValue>, key: string, hours: number): RecordValue {\n"
            f"  // Extend the {noun} while preserving its maximum lifetime.\n"
            "  const record = loadRecord(records, key);\n"
            "  const deadline = extensionDeadline(record, hours);\n"
            "  const result = { ...record, deadline };\n"
            "  return saveRecord(records, key, result);\n"
            "}\n\n"
            "export function revoke(records: Map<string, RecordValue>, key: string, actor: string): RecordValue {\n"
            f"  // Withdraw the active {noun}; never remove a completed record.\n"
            "  const record = loadRecord(records, key);\n"
            "  if (!mayRevoke(record, actor)) {\n"
            '    throw new Error("Completed or differently owned record cannot be revoked");\n'
            "  }\n"
            "  return removeRecord(records, key);\n"
            "}\n"
        ),
        "policy.ts": (
            f"// Decision rules for the {noun}, not transport or reporting.\n"
            'import type { RecordValue } from "./types";\n\n'
            "export function canRelease(record: RecordValue, actor: string): boolean {\n"
            f"  // Validate the {gate} requirement and lifecycle state.\n"
            f"  const gate = record.{gate};\n"
            '  return Boolean(actor && gate && record.status === "pending");\n'
            "}\n\n"
            "export function extensionDeadline(record: RecordValue, hours: number): number {\n"
            f"  // Clamp a {noun} extension to {limit} hours after creation.\n"
            '  if (hours < 0) throw new Error("Extension must not be negative");\n'
            "  const current = record.deadline;\n"
            f"  const maximum = record.created + {limit};\n"
            "  return Math.min(current + hours, maximum);\n"
            "}\n\n"
            "export function mayRevoke(record: RecordValue, actor: string): boolean {\n"
            f"  // Require the same owner for active {noun} withdrawal.\n"
            '  const active = record.status === "pending" || record.status === "released";\n'
            "  return Boolean(active && actor && record.owner === actor);\n"
            "}\n"
        ),
        "store.ts": (
            f"// In-memory {noun} records used by the current domain service.\n"
            'import type { RecordValue } from "./types";\n\n'
            "export function loadRecord(records: Map<string, RecordValue>, key: string): RecordValue {\n"
            "  const value = records.get(key);\n"
            '  if (!value) throw new Error("Record does not exist: " + key);\n'
            "  return { ...value };\n"
            "}\n\n"
            "export function saveRecord(records: Map<string, RecordValue>, key: string, value: RecordValue): RecordValue {\n"
            "  records.set(key, { ...value });\n"
            "  return { ...value };\n"
            "}\n\n"
            "export function removeRecord(records: Map<string, RecordValue>, key: string): RecordValue {\n"
            "  const previous = { ...records.get(key)! };\n"
            "  records.delete(key);\n"
            "  return previous;\n"
            "}\n"
        ),
        "types.ts": (
            f"// Shared {noun} shape; its declaration is optional supporting evidence.\n"
            "export interface RecordValue {\n"
            "  status: string; created: number; deadline: number; owner: string; actor?: string;\n"
            f"  {gate}?: string;\n"
            "}\n"
        ),
    }


def body_label(path: str, source: str, symbol: str, language: str) -> dict[str, Any]:
    """Find a complete top-level fixture function without executing source."""
    lines = source.splitlines()
    prefix = f"def {symbol}(" if language == "python" else f"export function {symbol}("
    start = next(index for index, line in enumerate(lines) if line.startswith(prefix))
    if language == "python":
        end = start + 1
        while end < len(lines) and (not lines[end] or lines[end].startswith(" ")):
            end += 1
        while end > start and not lines[end - 1]:
            end -= 1
    else:
        end = start + 1
        while end < len(lines) and lines[end] != "}":
            end += 1
        end += 1
    return {
        "path": path,
        "symbol": symbol,
        "start_line": start + 1,
        "end_line": end,
        "text": "\n".join(lines[start:end]),
    }


def build_manifest() -> dict[str, Any]:
    repositories: dict[str, Any] = {}
    queries = []
    for language, extension in (("python", "py"), ("typescript", "ts")):
        name = f"meridian-{language}-refinement-v1"
        files: dict[str, str] = {
            "README.md": (
                "# Meridian operations\n\nFour independent domains share deliberately ambiguous "
                "release, extend and revoke operation names. Current source is under src/. "
                "Historical exports, read models and user guides do not drive lifecycle decisions.\n"
            )
        }
        if language == "python":
            files["src/__init__.py"] = (
                'raise RuntimeError("Index source text; never import this fixture")\n'
            )
        for domain, details in DOMAINS.items():
            sources = (
                _python_sources(domain, details)
                if language == "python"
                else _typescript_sources(domain, details)
            )
            if language == "python":
                files[f"src/{domain}/__init__.py"] = '"""Domain package; fixture text only."""\n'
            for filename, source in sources.items():
                files[f"src/{domain}/{filename}"] = source
            noun, gate = details["noun"], details["gate"]
            prompts = {
                "release": (
                    f"Find the current code that releases a {noun}. I need the entire operation, "
                    f"the {gate} eligibility rule it calls, and its record-loading implementation. "
                    "The similarly named operations in other domains are unrelated."
                ),
                "extend": (
                    f"In src/{domain}/service.{extension}, inspect extend and its policy calculation: "
                    f"a {noun} extension must stay within the maximum lifetime. Include the complete "
                    "method, deadline helper, and persistence helper bodies so the update can be reviewed."
                ),
                "revoke": (
                    f"Where is ownership checked when withdrawing an active {noun}? Retrieve the "
                    "current revoke implementation, its ownership decision, and the actual removal "
                    "helper. Completed records must be protected. Documentation and test names alone "
                    "will not show the behavior."
                ),
            }
            policy_symbols = {
                "release": "can_release" if language == "python" else "canRelease",
                "extend": "extension_deadline" if language == "python" else "extensionDeadline",
                "revoke": "may_revoke" if language == "python" else "mayRevoke",
            }
            store_symbols = {
                "release": "load_record" if language == "python" else "loadRecord",
                "extend": "save_record" if language == "python" else "saveRecord",
                "revoke": "remove_record" if language == "python" else "removeRecord",
            }
            for action, prompt in prompts.items():
                primary = f"src/{domain}/service.{extension}"
                policy = f"src/{domain}/policy.{extension}"
                store = f"src/{domain}/store.{extension}"
                optional = [f"src/{domain}/types.ts"] if language == "typescript" else []
                queries.append(
                    {
                        "id": f"meridian-{language}-{domain}-{action}",
                        "repository": name,
                        "language": language,
                        "domain": domain,
                        "prompt": prompt,
                        "primary_target": primary,
                        "required_files": [primary, policy, store],
                        "optional_relevant_files": optional,
                        "judgment_scope": "exhaustive_for_declared_fixture_implementation_task",
                        "primary_body": body_label(primary, files[primary], action, language),
                        "required_dependency_bodies": [
                            body_label(policy, files[policy], policy_symbols[action], language),
                            body_label(store, files[store], store_symbols[action], language),
                        ],
                        "dependency_scope": "two_declared_direct_helpers_not_all_runtime_dependencies",
                    }
                )
                files[f"docs/{domain}/{action}.md"] = (
                    f"# {noun}: {action}\n\n{prompt}\n\n"
                    f"User guide for the {noun}: release, extend and revoke. The {gate} "
                    "decision belongs to current source. This page has no executable implementation.\n"
                )
            for component in (
                "audit",
                "calendar",
                "export",
                "dashboard",
                "history",
                "metrics",
                "notifications",
                "presentation",
                "receipts",
                "routing",
                "summary",
                "translations",
            ):
                comment = (
                    f"Read-only {noun} {component}; displays release extend revoke status, ownership, "
                    f"maximum lifetime and {gate}, but cannot change records."
                )
                if language == "python":
                    source = (
                        f'"""{comment}"""\n\n'
                        "def release(record: dict) -> str:\n"
                        '    """Presentation label only; no lifecycle behavior."""\n'
                        f'    return "{component}: released " + str(record.get("status", "unknown"))\n\n\n'
                        "def extend(record: dict) -> str:\n"
                        '    """Render the current deadline without extending it."""\n'
                        '    return str(record.get("deadline", "unknown"))\n\n\n'
                        "def revoke(record: dict) -> str:\n"
                        '    """Render the owner without removing any stored record."""\n'
                        '    return str(record.get("owner", "unknown"))\n'
                    )
                else:
                    source = (
                        f"// {comment}\n"
                        "export function release(record: { status: string }): string {\n"
                        f'  return "{component}: released " + record.status;\n'
                        "}\n"
                        "export function extend(record: { deadline: number }): string {\n"
                        "  return String(record.deadline);\n"
                        "}\n"
                        "export function revoke(record: { owner: string }): string {\n"
                        "  return record.owner;\n"
                        "}\n"
                    )
                files[f"src/{domain}/views/{component}.{extension}"] = source
            files[f"legacy/{domain}.{extension}"] = (
                ("# " if language == "python" else "// ")
                + f"Retired {noun} release extend revoke implementation. Not imported by current source.\n"
                + (
                    "def release(value):\n    return value\n\ndef extend(value):\n    return value\n\ndef revoke(value):\n    return value\n"
                    if language == "python"
                    else "export function release(value: unknown) { return value; }\nexport function extend(value: unknown) { return value; }\nexport function revoke(value: unknown) { return value; }\n"
                )
            )
            files[f"tests/{domain}_spec.{extension}"] = (
                ("# " if language == "python" else "// ")
                + f"Regression descriptions: {noun}; release eligibility {gate}, extend maximum lifetime, revoke ownership.\n"
                + (
                    'def test_release_extend_revoke():\n    """Only fixture test descriptions; never run indexed source."""\n    assert True\n'
                    if language == "python"
                    else 'export const testNames = ["release eligibility", "extend maximum lifetime", "revoke ownership"];\n'
                )
            )
        repositories[name] = {
            "language": language,
            "files": dict(sorted(files.items())),
            "file_count": len(files),
            "source_utf8_bytes": sum(len(source.encode()) for source in files.values()),
        }
    return {
        "schema_version": 1,
        "name": "Meridian procedural retrieval holdout v1",
        "creation_policy": (
            "Authored independently of Atlas/Orion task prompts and frozen before any candidate "
            "evaluation. Visible synthetic fixtures with paired language structure are a procedural "
            "holdout, not a secret test or a representative sample of production repositories."
        ),
        "protocol": PROTOCOL,
        "protocol_sha256": canonical_digest(PROTOCOL),
        "repositories": repositories,
        "queries": queries,
    }


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest["protocol_sha256"] != canonical_digest(manifest["protocol"]):
        raise ValueError("Protocol digest does not match")
    identifiers = [query["id"] for query in manifest["queries"]]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Query IDs must be unique")
    for repository in manifest["repositories"].values():
        for path in repository["files"]:
            relative = Path(path)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Fixture path escapes repository")
    for query in manifest["queries"]:
        files = manifest["repositories"][query["repository"]]["files"]
        if set(query["required_files"]) - set(files):
            raise ValueError("Required file missing from fixture")
        for label in [query["primary_body"], *query["required_dependency_bodies"]]:
            expected = "\n".join(
                files[label["path"]].splitlines()[label["start_line"] - 1 : label["end_line"]]
            )
            if not label["text"] or expected != label["text"]:
                raise ValueError("Body label differs from source")


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != MANIFEST_SHA256:
        raise ValueError("Fresh holdout changed after lock; create a new disclosed version")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    return manifest


def write_repository(manifest: dict[str, Any], name: str, destination: Path) -> None:
    validate_manifest(manifest)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Repository destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    for relative, source in manifest["repositories"][name]["files"].items():
        target = destination / relative
        if not target.resolve().is_relative_to(destination.resolve()):
            raise ValueError("Fixture path escapes repository")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
