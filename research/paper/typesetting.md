# Typesetting and format provenance

The revised named preprint uses the official `acmart` class in
`manuscript,screen,nonacm` mode. It contains the supplied author name and email,
omits an unspecified affiliation and ORCID, and assigns no publisher DOI,
conference, acceptance date, or rights statement. The official class controls
font sizes, margins, spacing, captions, and bibliography typography.

The vendored class sources and bibliography style are in `vendor/acmart/`.
Their exact source commit and file hashes are recorded in
`vendor/acmart/source-provenance.json`. The class was extracted from its
documented `.dtx`/`.ins` sources. Its official development-source status is
recorded; the selected venue's production-template rules must be checked before
submission.

The preparation environment initially lacked the required Libertine,
Inconsolata, and newtx fonts. The complete required font packages were obtained
from an official Debian package through the environment's approved package
network. Package size and SHA-256 were checked against the official package
index before extraction. Only an isolated tree under `.local/paper-writing/`
was configured; no system fonts or default user configuration were changed.
The generic TeX `binhex` dependency was obtained and verified the same way.
The package provenance files accompany this note. No font substitution or
manual tightening of the class layout is used.

To build with a normal TeX installation, provide Pandoc, pdfLaTeX, BibTeX,
the class's documented dependencies, and the required font packages. On Debian,
the relevant TeX distributions include `texlive-latex-extra`,
`texlive-fonts-extra`, `texlive-plain-generic`, and `texlive-publishers`.
Install those through your normal package manager; the manuscript itself does
not install packages or change system configuration.

From the repository root, run:

```sh
python research/paper/build.py
```

The script writes the generated `.tex` sources and PDFs in this directory, and
typesetting logs and a build receipt in `.build/`. It uses the isolated font
tree if that preparation tree is present, otherwise the normal TeX search path.
Recorded experimental evidence and the analysis are independent of the PDF
build. Rebuilding a PDF does not run a coding model.

The unmodified class supplies a useful named preprint. An eventual submission
must use the chosen venue's required class options, page limit, anonymity rules,
metadata, and current AI-assistance policy.

The v7 numeric/figure dependencies are pinned in `requirements.txt`; the
portable results directory also provides its own statistical requirements.
The manuscript and supplement each have 16 pages in this revision. The
figure renderer reads the public v7 export and makes no model calls.
