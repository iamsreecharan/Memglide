# Fresh cost-comparison corpus

10 held-out tasks: five Python and five TypeScript; four independent synthetic repositories. Four single-source fixes, four two-source integration fixes and two provided-source controls (one per language).

Full focus source ranges from 269 to 810 bytes, mean 491.3, median 410.0. All ten repository/focus sets are distinct. This remains small utility code, not evidence for large-repository or cross-session performance.

Two held-out behavioral tests outside each worktree, six protected existing smoke tests, strict TypeScript compile when applicable. Each integration requires fixes to two source files and each half-fix is independently rejected. Procedural oracle separation is not a sandbox.

Initial authored corpus and tasks JSON are preserved in corpus-initial-draft. Before final validation only formatting and the Two-tasks docstring were corrected in corpus; copied regression-test helper import was corrected from a prior corpus module. No behavioral oracle/reference correction.
