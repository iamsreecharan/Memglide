# Experimental Python declaration excerpts

The normal source-only preload and automatic-selection path continue to supply
complete files. This separate experiment must be requested explicitly and is
disabled by default. It does not read or inject memory, invoke a model, run
indexed source, scan a repository, update an index, or write application state.

```python
from memglide.integrations.source_excerpts import prepare_symbol_excerpt

result = prepare_symbol_excerpt(
    "Review the boundary handling in total.",
    project_id="previously-approved-project-id",
    db_path="/absolute/path/to/memglide.db",
    source_path="src/totals.py",
    symbol="total",
    enabled=True,
    max_context_bytes=6000,
)
```

Use `result["prompt"]`; it is the exact input task on every decline. The result
reports a bypass reason, preparation wall/CPU time, exact source and unit hashes,
unit line ranges, added UTF-8 bytes, and a clearly labeled bytes/4 token proxy.
Hashes, ranges, and declaration names stay in private result metadata; the model
envelope carries the path, incomplete-file label, and exact declaration text.
The proxy is not model usage, avoided work, billed charges, or a savings claim.
`model_calls` is zero for this preparation operation only.

Accepted input is intentionally narrow: an approved, indexed, currently eligible
Python file of at most 64,000 bytes, with at most 4,000 AST nodes and 64 top-level
declarations. Its current secure-read hash must equal the indexed hash. The
module may contain an initial docstring, immutable scalar/tuple literal
constants, and undecorated synchronous top-level functions. Function definitions
must have no annotations, executable default arguments, nested definitions,
imports, classes, attribute access, mutation targets, dynamic calls, or unknown
global references. Unicode identifiers, duplicate bindings, shadowed supported
builtins, and overlapping top-level line ranges are declined. Ordinary string
contents retain their exact UTF-8 bytes, including CRLF line endings.

Selection includes the complete requested function and a statically resolved
closure of referenced local helpers and immutable constants, in original source
order. The entire closure must fit within four declarations and the complete
JSON envelope must fit the byte budget. Diamond dependencies and recursion do
not duplicate source. The module's other declarations are inspected too, so an
unselected definition with an executable default or opaque binding causes a
decline. Imports, including future imports, are currently declined.

Approval, repository settings, ancestor ignores, source-path safety, symlinks,
credential patterns, file-size policy, indexed hash, and live source hash are
checked through the existing secure source boundaries. Policy, indexed hash,
and source hash are checked again after preparation. Deletion, stale indexing,
replaced policies, missing state, changed source, uncertain dependencies, or an
over-budget envelope return the original task without partial excerpts. A
caller can separately invoke the existing complete-file preload if appropriate;
this API does not hide an automatic fallback behind its experimental label.

Every envelope says **experimental excerpts; incomplete file** and sets
`full_source=false`. Structural closure under a restricted language subset is
not proof that omitted documentation, callers, tests, or runtime relationships
are irrelevant to a coding task. Operators and supported builtin calls can also
dispatch through object behavior; this API makes no purity or semantic theorem
claim. Do not substitute these excerpts for complete source automatically.

Tests compare behavior only for controlled, test-owned functions, verify exact
ranges/hashes, and exercise conservative rejection and source-policy races.
There is no live-model evidence that this experiment reduces end-to-end tokens,
latency, or cost. Evaluate it separately against complete files before any
promotion; all failed and declined selections must remain in the comparison.
