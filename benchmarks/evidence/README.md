# Archived benchmark evidence

Generated run directories are kept out of the active source tree. This removes
thousands of logs and copied source files from ordinary browsing without
rewriting the study record or Git history.

- [Original evidence at pre-cleanup main commit 8acc8af](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks/evidence)
- [Original reports and other benchmark artifacts](https://github.com/iamsreecharan/Memglide/tree/8acc8af/benchmarks)
- [Latest paper, findings and verified downloads](../../research/README.md)

To recover an older artifact from a full clone, use its original path:

```sh
git show 8acc8af:benchmarks/router-v4-assessment.md > /tmp/router-v4-assessment.md
git archive 8acc8af benchmarks/evidence | tar -x -C /your/archive/directory
```

Create the destination first. The archive command restores historical files
into that directory; it does not run them. Files may contain untrusted source.
The complete paper ZIP includes the final study and included predecessors,
while Git history remains the recovery source for all older tracked evidence.
New run output belongs under `.local/`, in a separate immutable artifact when
published, rather than back in this source directory.
