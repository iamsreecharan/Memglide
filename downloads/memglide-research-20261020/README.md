# Updated Memglide research downloads

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
| Memglide-paper-and-supplement.zip | 2,792,537 | `b4378b3256ea650e8f2568e7c96a63f90aeb5821cd0f6bef220f5630f9ef7e18` |
| Memglide-complete-research.zip | 117,965,887 | `5fb40ddbb47eabd34b3e6ed4f411e994bf76d3effb61243f1171cb98af46aa0d` |

The complete ZIP uses Git LFS. Use the raw GitHub download link above;
a small text LFS pointer is not the archive. CRC and every member's SHA-256
were verified. Each ZIP contains `CHECKSUMS.sha256` for its payload members.
The old capsule's original files are preserved byte for byte.

The [previous release](https://github.com/iamsreecharan/Memglide/tree/525f92d5ed63dcffbe0c6164fe951117f854dfdd/downloads/memglide-research-20261020)
remains available in immutable Git history.
