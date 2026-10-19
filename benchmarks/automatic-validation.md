# Automatic source router: verification record

**1,907 distinct automated cases passed:** 1,880 Python, 24 frontend and three
production Chromium cases. Targeted runs overlap these counts. No native model
requests were made. [JSON](automatic-validation.json) records counts, failed
attempts and scopes; [the evidence ledger](evidence/automatic-v1/artifact-ledger.json)
hashes the retained raw receipts.

Executed from the repository root:

```sh
uv sync --frozen
npm --prefix frontend ci --no-audit --no-fund
uv run pytest -q --junitxml=.local/automatic-validation/full-python.xml
uv run ruff check .
uv run mypy src benchmarks/run_automatic.py benchmarks/corpus_automatic.py
npm --prefix frontend test -- --run --reporter=default --reporter=json --outputFile=../.local/automatic-validation/frontend-unit.json
PLAYWRIGHT_JSON_OUTPUT_NAME=/workspace/Memglide/.local/automatic-validation/frontend-browser-final.json npm --prefix frontend run e2e -- --reporter=list,json
uv run python scripts/bundle_frontend.py
uv run python -m build --wheel --outdir .local/automatic-validation/dist
```

The complete Python run passed in 846.438 seconds according to JUnit. Two upstream
Typer/Click deprecation warnings remain. Ruff passed, including new benchmark
code; immutable upstream fixtures and historical evidence are excluded from
formatting/lint repair. Mypy passed 29 source files. Production browser tests
use one worker, no retries and the existing timeouts.

A fresh virtual environment installed the new wheel with runtime constraints
exported from `uv.lock`. [The installed smoke script](evidence/automatic-v1/installed_smoke.py)
ran with isolated Python (`-I`) and passed nine checks: installed-wheel import,
path-free automatic complete source without session/memory creation, CLI help,
one controlled fake-Codex handoff and private report, optional memory preparation,
real default and agent MCP clients, loopback API/production SPA, and CLI doctor.
The fake executable is a local test fixture, not a model. The wheel SHA-256 and
installed receipt are retained in JSON.

New cases cover deterministic path-free discovery, generic/ambiguous tasks,
added/changed/deleted sources, stale/partial indexes, missing/replaced databases,
policy/settings races, ignores, secrets, symlink escapes, oversized bodies,
resource limits, exact already-supplied-source suppression, conservative excerpts,
malformed receipts, exact fallback and approval/budget/freeze guards. Existing
application, MCP, API, CLI and frontend cases remain unchanged.

Failed attempts are preserved rather than erased:

- Initial automatic adapter: 45 passed, one positive preload case conservatively
  bypassed during concurrent load. The precise bypass reason was unavailable;
  timeout causation is unproven. The unchanged 46-case rerun passed; the expanded
  62-case run and complete suite passed. Initial XML is retained.
- New launcher fixtures initially called nonexistent `Indexer.register`:
  93 passed, two failed. Corrected fixtures use `add_project`. A later concurrent
  run had 92 passes and three new subprocess timeouts at unchanged 20-second
  limits. Final serial 104 cases passed. Initial attempts exist only in tool
  transcripts; no XML was generated for those attempts.
- An excerpt fixture called nonexistent `Database.set_settings`: 70 passed,
  one failed. The fixture now uses parameterized settings SQL; final 74 and the
  complete suite passed. Initial output is transcript-only.
- Initial corpus TypeScript compiler flags were incompatible with TypeScript 7;
  Node16 module resolution corrected the grading setup. Final controls show 12
  baseline failures, 12 reference passes and 12 partial-fix failures. Those are
  grader controls, not native agent successes.
- Initial production browser run had two passes and one workflow timeout at the
  final empty-state check during concurrent checks. The trace/screenshot archive
  is retained. The serial rerun passed all three; timeout and test code were
  unchanged. Concurrency coincided with failure; the exact cause was not isolated.

After validation, the frozen offline probe ran once. Its **negative** result is
reported separately in [the assessment](automatic-assessment.md): C delivered
0/12 target scopes versus B 9/12 and had higher observed preparation overhead.
Passing regression tests is not evidence that this router improves agent cost.
No protected existing test was weakened, and no held-out policy was retuned.
