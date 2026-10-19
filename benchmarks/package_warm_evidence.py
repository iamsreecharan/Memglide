"""Package explicit warm-v1 evidence after completion; never authenticate or run models.

Only allowlisted text, public frozen Git blobs and vetted fixture bundles enter
the archive. All original attempted/failed/unrun rows remain byte-identical.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import types
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from benchmarks.audit_warm import SafeRoot

ROOT = Path(__file__).resolve().parents[1]
FREEZE = "58ba0545187dbfb5270df246109bb81295718063"
SCANNER = "benchmarks/evidence/efficiency-v1/reproduction/publish_evidence.py.txt"
TOP = (
    "metadata.json",
    "plan.json",
    "state.json",
    "runs.json",
    "supplemental-runs.json",
    "final-response-schema.json",
    "report.json",
    "report.md",
)
RUN = (
    "attempt-start.json",
    "result.json",
    "prompt.txt",
    "command.json",
    "events.jsonl",
    "stderr.log",
    "final.json",
    "process-identity.json",
    "launch-grant.json",
    "preparation.json",
    "grade.json",
    "held_out.py",
    "held_out.test.mjs",
    "behavior.stdout.log",
    "behavior.stderr.log",
    "smoke.stdout.log",
    "smoke.stderr.log",
    "typecheck.stdout.log",
    "typecheck.stderr.log",
    "changes.patch",
    "git-status.txt",
    "untracked-files.json",
)
VALIDATION = (
    ".local/saas-efficiency/full-python.xml",
    ".local/saas-efficiency/full-python-final.xml",
    ".local/saas-efficiency/warm-runner-final.xml",
    ".local/saas-efficiency/targeted-final.xml",
    ".local/saas-efficiency/installed-smoke.json",
    ".local/saas-efficiency/warm-source-preflight.json",
    ".local/saas-efficiency/graph-probe.json",
    ".local/warm-corpus-validation/partial-tests.xml",
    ".local/warm-corpus-validation/partial-tests-final.xml",
    ".local/warm-corpus-validation/corpus-tests-final.xml",
    ".local/warm-corpus-validation/summary.json",
)
PUBLIC_FINAL = (
    "benchmarks/warm-study-assessment.md",
    "benchmarks/warm-study-assessment.json",
    "benchmarks/warm-study-review.md",
    "benchmarks/saas-efficiency-assessment.md",
    "benchmarks/saas-efficiency-assessment.json",
    "benchmarks/codex-warm-ab.json",
    "benchmarks/codex-warm-ab.md",
    "benchmarks/warm-integrity-audit.json",
    "benchmarks/warm-integrity-audit.md",
)
FORBIDDEN = {
    "auth.json",
    "codex-state",
    "native-state",
    "worktrees",
    "installed-env",
    "config.toml",
    "environment.json",
    "environ.json",
    ".env",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def git(*arguments: str) -> bytes:
    return subprocess.check_output(
        [
            "git",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.hooksPath=/dev/null",
            "-C",
            str(ROOT),
            *arguments,
        ],
        stderr=subprocess.PIPE,
    )


def name_ok(name: str) -> None:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or path.as_posix() != name
        or ".." in path.parts
        or "\\" in name
        or FORBIDDEN.intersection(path.parts)
        or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".tar", ".whl"}
    ):
        raise ValueError("Excluded archive member")


def package(
    study: Path,
    output: Path,
    manifest_path: Path,
    freeze: str,
    audit_path: Path = ROOT / "benchmarks/warm-integrity-audit.json",
    public_reports: tuple[str, ...] = PUBLIC_FINAL,
    extra_validation: tuple[str, ...] = (),
) -> dict[str, Any]:
    if not re.fullmatch(r"[a-f0-9]{40}", freeze):
        raise ValueError("Expected an explicit frozen Git commit")
    if (
        output.exists()
        or manifest_path.exists()
        or output.is_symlink()
        or manifest_path.is_symlink()
    ):
        raise ValueError("Archive and external manifest must be fresh")
    for path in (output, manifest_path):
        if any(p.is_symlink() for p in path.absolute().parents):
            raise ValueError("Output parent has a symlink")
    source = SafeRoot(ROOT)
    evidence = SafeRoot(study)
    report = evidence.json("report.json", 128_000_000)
    if not report["metadata"].get("finished_at"):
        raise ValueError("Study is not finished")
    if report["metadata"]["frozen_manifest"]["git_head"] != freeze:
        raise ValueError("Study source commit differs")
    audit = source.json(audit_path)
    if not audit.get("passed") or audit["coverage"]["planned_rows"] != len(report["runs"]):
        raise ValueError("Independent audit did not pass or has a different coverage")
    scanner_bytes = git("show", freeze + ":" + SCANNER)
    guard: Any = types.ModuleType("warm_pinned_publication_scanner")
    guard.__file__ = str(ROOT / SCANNER)
    sys.modules[guard.__name__] = guard
    exec(compile(scanner_bytes, guard.__file__, "exec"), guard.__dict__)
    guard.ROOT = ROOT
    guard.XML_FROZEN_COMMIT = freeze
    guard.XML_FIXTURES = None
    guard.XML_APPROVALS = {}
    members: dict[str, bytes] = {}
    origins: dict[str, dict[str, Any]] = {}
    read_identities: dict[str, str] = {}
    source_scan_exceptions: dict[str, Any] = {}

    def add(
        name: str,
        data: bytes,
        origin: dict[str, Any],
        *,
        xml_source: str | None = None,
        binary: bool = False,
    ) -> None:
        name_ok(name)
        if name in members:
            raise ValueError("Duplicate archive member")
        if binary:
            if any(p.search(data) for p in guard.SECRET_PATTERNS):
                raise ValueError("Potential credential in binary bundle")
        else:
            scan_path = ROOT / (xml_source or name)
            if (
                xml_source
                and xml_source.endswith(".xml")
                and any(p.search(data) for p in guard.SECRET_PATTERNS)
            ):
                guard.XML_APPROVALS[xml_source] = sha(data)
            scanned = data
            if name == "frozen-source/tests/test_security_storage.py":
                fixtures, source_sha = guard.frozen_fixture_literals()
                if sha(data) != source_sha:
                    raise ValueError("Synthetic fixture source differs from frozen AST")
                offsets = [0]
                for line in data.splitlines(keepends=True):
                    offsets.append(offsets[-1] + len(line))
                spans = [
                    (
                        offsets[n.lineno - 1] + n.col_offset,
                        offsets[n.end_lineno - 1] + n.end_col_offset,
                    )
                    for n in ast.walk(ast.parse(data))
                    if isinstance(n, ast.Constant)
                    and isinstance(n.value, str)
                    and n.end_lineno is not None
                    and n.end_col_offset is not None
                ]
                matches = [
                    match for pattern in guard.SECRET_PATTERNS for match in pattern.finditer(data)
                ]
                masked = bytearray(data)
                for match in matches:
                    if not any(
                        start <= match.start() and match.end() <= end for start, end in spans
                    ) or not any(match.group() in value for value in fixtures):
                        raise ValueError(
                            "Credential pattern outside frozen synthetic string literal"
                        )
                    masked[match.start() : match.end()] = b"_" * (match.end() - match.start())
                scanned = bytes(masked)
                source_scan_exceptions[name] = {
                    "frozen_commit": freeze,
                    "source_sha256": source_sha,
                    "matched_sha256": [sha(m.group()) for m in matches],
                    "original_bytes_preserved": True,
                    "all_other_bytes_scanned": True,
                }
            guard.scan_text_bytes(scan_path, scanned)
        members[name] = data
        origins[name] = origin

    def working(relative: str, destination: str) -> None:
        data = source.read(relative, 128_000_000)
        read_identities[relative] = sha(data)
        add(
            destination,
            data,
            {"kind": "original-working-artifact", "path": relative},
            xml_source=relative,
        )

    for name in TOP:
        data = evidence.read(name, 128_000_000)
        read_identities[str(evidence.root.relative_to(ROOT) / name)] = sha(data)
        add("study/" + name, data, {"kind": "original-study-artifact", "path": name})
    for directory in ("attempt-log", "groups"):
        folder = evidence.root / directory
        if folder.is_symlink():
            raise ValueError("Symlink evidence directory")
        for path in sorted(folder.glob("*.json")):
            relative = directory + "/" + path.name
            data = evidence.read(relative)
            read_identities[str(evidence.root.relative_to(ROOT) / relative)] = sha(data)
            add("study/" + relative, data, {"kind": "original-study-artifact", "path": relative})
    for row in report["runs"]:
        identifier = row["run_id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,160}", identifier):
            raise ValueError("Unsafe original identity")
        if not row.get("attempted"):
            continue
        for name in RUN:
            path = Path("runs") / identifier / name
            try:
                data = evidence.read(path, 64_000_000)
            except FileNotFoundError:
                continue
            read_identities[str(evidence.root.relative_to(ROOT) / path)] = sha(data)
            add(
                "study/" + path.as_posix(),
                data,
                {"kind": "original-run-artifact", "run_id": identifier, "path": name},
            )
    for public_path in public_reports:
        working(public_path, "reports/" + Path(public_path).name)
    for validation_path in (*VALIDATION, *extra_validation):
        working(validation_path, "validation/" + validation_path.removeprefix(".local/"))
    # Baseline/reference failures are calibration evidence, not native attempts.
    for task in report["tasks"]:
        for phase in ("baseline", "reference"):
            directory = Path(".local/warm-corpus-validation") / task["id"] / phase
            for name in RUN:
                if name not in {
                    "grade.json",
                    "held_out.py",
                    "held_out.test.mjs",
                    "behavior.stdout.log",
                    "behavior.stderr.log",
                    "smoke.stdout.log",
                    "smoke.stderr.log",
                    "typecheck.stdout.log",
                    "typecheck.stderr.log",
                }:
                    continue
                path = directory / name
                if (ROOT / path).exists():
                    working(
                        path.as_posix(),
                        "validation/corpus-initial/" + task["id"] + "/" + phase + "/" + name,
                    )
    frozen_names = set(report["metadata"]["frozen_manifest"]["files"])
    frozen_names.update(
        line
        for line in git("show", "--format=", "--name-only", freeze).decode().splitlines()
        if line
    )
    frozen_names.update({SCANNER, "tests/test_security_storage.py", "LICENSE"})
    frozen_records = {}
    for path in sorted(frozen_names):
        name_ok("frozen-source/" + path)
        data = git("show", freeze + ":" + path)
        expected = report["metadata"]["frozen_manifest"]["files"].get(path)
        if expected is not None and sha(data) != expected:
            raise ValueError("Frozen implementation source hash differs")
        add(
            "frozen-source/" + path,
            data,
            {"kind": "frozen-public-git-blob", "commit": freeze, "path": path},
        )
        frozen_records[path] = sha(data)
    # Keep post-study interpretation code distinct from the untouched runtime freeze.
    working("benchmarks/audit_warm.py", "post-study-auditor/benchmarks/audit_warm.py")
    for dependency in ("benchmarks/estimate_cost.py", "benchmarks/cost-pricing.json"):
        data = git("show", freeze + ":" + dependency)
        add(
            "post-study-auditor/" + dependency,
            data,
            {"kind": "frozen-public-audit-dependency", "commit": freeze, "path": dependency},
        )
    script = source.read("benchmarks/package_warm_evidence.py")
    add(
        "reproduction/package_warm_evidence.py",
        script,
        {"kind": "post-study-package-helper", "sha256": sha(script)},
    )
    bundles = []
    canonical_commits = {r["commit"] for r in report["metadata"]["repositories"].values()}
    with tempfile.TemporaryDirectory(prefix="warm-vetted-bundles-") as temporary:
        for task_id, repository in sorted(report["metadata"]["repositories"].items()):
            if (
                evidence.git(repository["path"], "rev-parse", "HEAD").decode().strip()
                != repository["commit"]
                or evidence.git(repository["path"], "rev-parse", "HEAD^{tree}").decode().strip()
                != repository["tree"]
                or evidence.git(repository["path"], "status", "--porcelain")
            ):
                raise ValueError("Fixture identity is not clean and exact")
            refs = (
                evidence.git(
                    repository["path"], "for-each-ref", "--format=%(objectname) %(refname)"
                )
                .decode()
                .splitlines()
            )
            reachable = set(
                evidence.git(repository["path"], "rev-list", "--all").decode().splitlines()
            )
            if (
                refs != [repository["commit"] + " refs/heads/benchmark"]
                or not reachable <= canonical_commits
            ):
                raise ValueError("Fixture has unexpected refs or noncanonical history")
            objects = (
                evidence.git(repository["path"], "rev-list", "--objects", "--all")
                .decode()
                .splitlines()
            )
            for item in objects:
                identifier = item.split(" ", 1)[0]
                kind = evidence.git(repository["path"], "cat-file", "-t", identifier).strip()
                if kind in {b"blob", b"commit"}:
                    data = evidence.git(repository["path"], "cat-file", "-p", identifier)
                    guard.scan_text_bytes(ROOT / "fixture-public-object.txt", data)
            bundle = Path(temporary) / (task_id + ".bundle")
            evidence.git(repository["path"], "bundle", "create", str(bundle), "--all")
            evidence.git(repository["path"], "bundle", "verify", str(bundle))
            data = bundle.read_bytes()
            add(
                "fixture-bundles/" + bundle.name,
                data,
                {
                    "kind": "vetted-author-generated-git-bundle",
                    "task_id": task_id,
                    "commit": repository["commit"],
                    "tree": repository["tree"],
                    "all_refs": refs,
                    "canonical_reachable_commits": sorted(reachable),
                    "decompressed_objects_scanned": len(objects),
                },
                binary=True,
            )
            bundles.append(
                {
                    "task_id": task_id,
                    "commit": repository["commit"],
                    "tree": repository["tree"],
                    "bundle": bundle.name,
                    "sha256": sha(data),
                    "objects_scanned": len(objects),
                }
            )
    readme = f"""# Memglide bounded warm-memory evidence

Original frozen implementation: {freeze}.
The original cohort has {len(report["runs"])} assignments; {sum(bool(r.get("attempted")) for r in report["runs"])} were attempted.
Cohort: {study.name}. Failed, interrupted and unrun observations remain intact.
Measured outcomes and limitations appear in reports/. Missing usage is unknown, not zero;
partial coverage does not establish a universal cost or speed advantage.

`study/` preserves original JSON/log/receipt bytes. `reports/` contains final public report copies.
`frozen-source/` contains public Git blobs at the implementation freeze, including documentation
that still described the then-pending study. Current outcomes are in reports/, not those snapshots.
`validation/` contains
local tests and component receipts; intentional corpus baselines and the earlier failed test
are calibration/engineering evidence, never native benchmark results.
The final full Python XML includes only narrowly approved synthetic credential test-name
matches backed by the frozen public security test AST. That one public test source also
permits only matching credential-like bytes inside frozen string-literal AST spans.
The originals are preserved and every other byte was scanned.

There are 12 logical repositories and 36 independently frozen stage repositories.
`fixture-bundles/` includes all refs of each author-generated stage. Every reachable commit
must belong to the frozen canonical stage set; all reachable text blobs/commits are scanned
before bundling. No Git config, hooks, native-state or reflogs are copied.

Verify every member with MEMBER-MANIFEST.json and the external manifest's ZIP SHA256 before use.
`git bundle verify fixture-bundles/<task-id>.bundle` checks a bundle inside a temporary Git repo.
`git clone fixture-bundles/<task-id>.bundle <destination>` restores that stage's original commit/tree.

For an exact auditor rerun, use a disposable environment with the original artifact layout
`{evidence.root}`. Copy `study/` contents there without modifying originals, and clone each
bundle into the repository path listed in study/metadata.json. Never overwrite a current study.
The original auditor at the runtime freeze remains in frozen-source/. Its initial audit
is retained even when an interrupted projection needs conservative post-study handling.
The separately pinned post-study-auditor/ version preserves raw observations while keeping
unattested complete-attempt usage/cost unknown; it does not change attempts or grades.
Run Python from post-study-auditor/:

    python -m benchmarks.audit_warm --report {evidence.root}/report.json --artifact-root {evidence.root} --output /tmp/warm-audit-rerun

Original records retain absolute paths. The auditor rejects pointers outside its explicit root;
use the original layout rather than rewriting result records or rehashing their ledger.
No authentication or model requests are required for these checks.

Excluded: native/Codex state, authentication, device-login codes, environment dumps, worktrees,
databases/WAL/SHM, untracked tar archives, installed environments, caches and live credentials.
Pattern scanning is a precaution, not proof that every possible secret format can be detected.
"""
    add("README.md", readme.encode(), {"kind": "package-instructions"})
    # Prove selected original working bytes did not change while the package was prepared.
    for relative, expected in read_identities.items():
        if sha(source.read(relative, 128_000_000)) != expected:
            raise ValueError("Selected original artifact changed during packaging")
    inventory = {
        "schema_version": 1,
        "implementation_commit": freeze,
        "native_model_requests_by_packager": 0,
        "original_study_coverage": audit["coverage"],
        "frozen_public_sources": frozen_records,
        "fixture_bundles": bundles,
        "synthetic_xml_scan_exceptions": guard.XML_SCAN_EXCEPTIONS,
        "synthetic_source_scan_exceptions": source_scan_exceptions,
        "files": [
            {"path": name, "bytes": len(data), "sha256": sha(data), "origin": origins[name]}
            for name, data in sorted(members.items())
        ],
    }
    inventory_bytes = encoded(inventory)
    add("MEMBER-MANIFEST.json", inventory_bytes, {"kind": "member-inventory-excluding-itself"})
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 19, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(members):
            raise ValueError("Archive CRC or membership verification failed")
        for name, data in members.items():
            if archive.read(name) != data:
                raise ValueError("Archive member differs from vetted bytes")
    result = {
        "schema_version": 1,
        "archive_path": str(output.relative_to(ROOT)),
        "archive_bytes": output.stat().st_size,
        "archive_sha256": sha(output.read_bytes()),
        "member_manifest_sha256": sha(inventory_bytes),
        "members": len(members),
        "uncompressed_bytes": sum(map(len, members.values())),
        "implementation_commit": freeze,
        "fixture_stage_bundles": len(bundles),
        "logical_sequences": 12,
        "original_study_coverage": audit["coverage"],
        "validation": {
            "all_selected_bytes_credential_pattern_scanned": True,
            "bundle_reachable_text_objects_scanned": True,
            "crc_and_exact_member_bytes_verified": True,
            "original_artifacts_unchanged": True,
        },
        "synthetic_xml_scan_exceptions": guard.XML_SCAN_EXCEPTIONS,
        "synthetic_source_scan_exceptions": source_scan_exceptions,
        "files": inventory["files"],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(encoded(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, default=ROOT / ".local/warm-v1")
    parser.add_argument("--freeze", default=FREEZE)
    parser.add_argument("--audit", type=Path, default=ROOT / "benchmarks/warm-integrity-audit.json")
    parser.add_argument(
        "--public-report",
        action="append",
        default=None,
        help="Explicit repository-relative public report path; repeated options replace the default v1 report list",
    )
    parser.add_argument(
        "--extra-validation",
        action="append",
        default=[],
        help="Additional explicit repository-relative offline verification receipt/source",
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "benchmarks/memglide-warm-evidence.zip"
    )
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "benchmarks/warm-evidence-manifest.json"
    )
    args = parser.parse_args()
    receipt = package(
        args.study.absolute(),
        args.output.absolute(),
        args.manifest.absolute(),
        args.freeze,
        args.audit.absolute(),
        tuple(args.public_report) if args.public_report is not None else PUBLIC_FINAL,
        tuple(args.extra_validation),
    )
    print(
        json.dumps(
            {
                key: receipt[key]
                for key in (
                    "archive_path",
                    "archive_bytes",
                    "archive_sha256",
                    "members",
                    "fixture_stage_bundles",
                )
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
