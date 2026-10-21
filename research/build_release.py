"""Build current paper/results ZIPs while retaining the prior v6 capsule.

Requires locally built PDFs and the original complete ZIP; makes no network or
model requests. The dated output directory is retained for download compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "research/paper"
RESULTS = ROOT / "research/results/router-v7-20261021"
OLD_SHA256 = "51e030257f7d07cda71f851a3e45fb136ec99a18408bb93bf77823fbae6eda6f"
CANDIDATE = "3c3f82b68778f6fb156394594bef3d6ec7118023"
DATE = (2026, 10, 21, 0, 0, 0)
SECTIONS = (
    "introduction", "related-work", "system", "methods", "development",
    "results", "limitations", "conclusion", "data-availability", "assistance",
)
PAPER_FILES = (
    "README.md", "manuscript.md", "supplement.md", "memglide-paper.tex",
    "memglide-supplement.tex", "references.bib", "acm-template.tex",
    "assemble.py", "assemble_supplement.py", "build.py", "create_figures.py",
    "break-long-code.lua", "typesetting.md", "requirements.txt",
    "publication-and-editorial-notes.md",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def member(archive: zipfile.ZipFile, name: str, data: bytes, hashes: dict) -> None:
    if name in hashes or name.startswith("/") or ".." in Path(name).parts:
        raise ValueError("Duplicate or unsafe archive member: " + name)
    entry = zipfile.ZipInfo(name, DATE)
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o100644 << 16
    archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    hashes[name] = hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous-zip", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "downloads/memglide-research-20261020")
    args = parser.parse_args()
    if sha256(args.previous_zip) != OLD_SHA256:
        raise SystemExit("Previous ZIP does not match its immutable public commitment")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for stem in ("paper", "supplement"):
        for ext in ("pdf", "md"):
            source = PAPER / (("memglide-" + stem + ".pdf") if ext == "pdf" else
                              ("manuscript.md" if stem == "paper" else "supplement.md"))
            shutil.copyfile(source, out / ("Memglide-" + stem + "." + ext))
        subprocess.run(["pdftotext", "-layout", str(out / ("Memglide-" + stem + ".pdf")),
                        str(out / ("Memglide-" + stem + ".txt"))], check=True)

    readme = """Memglide research revision: 21 October 2026

The main paper now reports the amended v7 comparison: 28 primary tasks,
112 sessions, plus 16 descriptive sessions on eight previously exposed tasks.
Observed API-equivalent cost is 4.84% lower; full workflow is 1.17% slower.
Both nominal 95% intervals include zero. Costs are token-price estimates,
not invoices; equal strict pass counts do not prove quality equivalence.

Open Memglide-paper.pdf and Memglide-supplement.pdf. Editable sources and the
portable results/reproduction instructions are under research/. All 128 current
numeric records are included; new native transcripts/private graders are not.
No account credentials, native runtime installation or provider backend is
included. Statistical reproduction and PDF builds make no model calls.

The complete ZIP also contains evaluated-source/ (exact candidate source) and
historical-v6/ (the unchanged contents of the previous complete ZIP, with its
separate 72-session study and older evidence capsule). These historical results
are not pooled with v7. The smaller paper-and-supplement ZIP omits those two
large historical/source directories. The dated download path is unchanged for
compatibility; its contents have been replaced with this revision.

Verify each extracted ZIP's members against CHECKSUMS.sha256. For the ZIP
file itself, use the SHA-256 in the adjacent download-manifest.json.
This is an AI-assisted preprint for author review, not an accepted publication.
"""
    (out / "READ-ME.txt").write_text(readme)
    (out / "DELIVERY-NOTE.txt").write_text(
        "This directory is published on GitHub. The two ZIPs replace the prior downloads.\n"
        "Use the raw GitHub links in README.md to download the complete file bytes.\n"
        "The complete ZIP uses Git LFS; a text pointer is not the downloadable archive.\n")
    files = {"READ-ME.txt": (out / "READ-ME.txt").read_bytes()}
    for stem in ("paper", "supplement"):
        for ext in ("pdf", "md", "txt"):
            n = "Memglide-" + stem + "." + ext
            files[n] = (out / n).read_bytes()
    for name in (*PAPER_FILES, *(s + ".md" for s in SECTIONS)):
        files["research/paper/" + name] = (PAPER / name).read_bytes()
    for pattern in ("figures/v7-*", "vendor/acmart/*", "history/*"):
        for path in sorted(PAPER.glob(pattern)):
            if path.is_file():
                files["research/paper/" + str(path.relative_to(PAPER))] = path.read_bytes()
    for path in sorted(RESULTS.iterdir()):
        if path.is_file():
            files["research/results/router-v7-20261021/" + path.name] = path.read_bytes()
    files["research/build_release.py"] = Path(__file__).read_bytes()
    with tempfile.TemporaryDirectory(prefix="memglide-release-") as temp:
        candidate = Path(temp) / "candidate.tar.gz"
        with candidate.open("wb") as stream:
            subprocess.run(["git", "archive", "--format=tar.gz", "--prefix=Memglide/", CANDIDATE],
                           cwd=ROOT, stdout=stream, check=True)
        for complete in (False, True):
            name = "Memglide-complete-research.zip" if complete else "Memglide-paper-and-supplement.zip"
            hashes: dict[str, str] = {}
            with zipfile.ZipFile(out / name, "w", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=6, allowZip64=True) as archive:
                for n, data in sorted(files.items()):
                    member(archive, n, data, hashes)
                if complete:
                    member(archive, "evaluated-source/Memglide-" + CANDIDATE[:7] + ".tar.gz",
                           candidate.read_bytes(), hashes)
                    with zipfile.ZipFile(args.previous_zip) as old:
                        for n in old.namelist():
                            member(archive, "historical-v6/" + n, old.read(n), hashes)
                lines = "".join(digest + "  " + n + "\n" for n, digest in sorted(hashes.items()))
                member(archive, "CHECKSUMS.sha256", lines.encode(), hashes)
            with zipfile.ZipFile(out / name) as archive:
                assert archive.testzip() is None
                assert set(archive.namelist()) == set(hashes)
                for n, digest in hashes.items():
                    assert hashlib.sha256(archive.read(n)).hexdigest() == digest, n
            print(name, (out / name).stat().st_size, sha256(out / name))
    manifest = {
        "release": "v7-amended-comparison-20261021",
        "primary_sessions": 112, "comparison_sessions": 128,
        "evaluated_candidate_commit": CANDIDATE,
        "original_analysis_sha256": "fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26",
        "historical_zip_sha256": OLD_SHA256,
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)}
                  for p in sorted(out.iterdir()) if p.is_file() and p.suffix in (".zip", ".pdf", ".md", ".txt")
                  and p.name != "README.md"},
    }
    (out / "download-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    rows = []
    for name in ("Memglide-paper-and-supplement.zip", "Memglide-complete-research.zip"):
        record = manifest["files"][name]
        rows.append(f"| {name} | {record['bytes']:,} | `{record['sha256']}` |")
    download_readme = """# Updated Memglide research downloads

This directory contains the **21 October 2026 v7 revision**. The dated path is
retained for compatibility; its former downloads have been replaced.

- [Revised paper](Memglide-paper.pdf)
- [Revised supplement](Memglide-supplement.pdf)
- [Paper, supplement, results and editable sources ZIP](https://github.com/iamsreecharan/Memglide/raw/refs/heads/main/downloads/memglide-research-20261020/Memglide-paper-and-supplement.zip)
- [Complete replacement research ZIP](https://github.com/iamsreecharan/Memglide/raw/refs/heads/main/downloads/memglide-research-20261020/Memglide-complete-research.zip)
- [All file sizes and checksums](download-manifest.json)

Both archives contain the revised PDFs, editable sources and all current
numeric results with offline reproduction code. The complete ZIP also includes
the exact evaluated candidate source and the previous complete release under
`historical-v6/`. Those historical results remain separate. New private graders,
complete new native transcripts, account credentials and installed runtimes
are not included.

The main comparison has 112 sessions on 28 tasks; 16 additional sessions on
exposed tasks remain descriptive. Observed token-price cost is 4.84% lower and
complete workflow is 1.17% slower. Both nominal intervals include zero; no joint
cost-and-speed superiority is established. Costs are estimates, not invoices.

## ZIP verification

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
""" + "\n".join(rows) + """

The complete ZIP uses Git LFS. Use the raw GitHub download link above;
a small text LFS pointer is not the archive. CRC and every member's SHA-256
were verified. Each ZIP contains `CHECKSUMS.sha256` for its payload members.
The old capsule's original files are preserved byte for byte.

The [previous release](https://github.com/iamsreecharan/Memglide/tree/525f92d5ed63dcffbe0c6164fe951117f854dfdd/downloads/memglide-research-20261020)
remains available in immutable Git history.
"""
    (out / "README.md").write_text(download_readme)
    print("Both ZIPs passed CRC, member-hash and exact historical-inclusion checks.")


if __name__ == "__main__":
    main()
