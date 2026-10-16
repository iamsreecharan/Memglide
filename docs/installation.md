# Installation and packaging

Install Python 3.11+, uv, Node.js 24.x at 24.15+ with npm (or 22.x at 22.22.2+), and Git through their official installation channels. These Node minimums match the locked frontend dependencies. The application does not require Docker, Redis, a cloud account, an API key, or an embedding model. The project pins Python and npm dependency versions with lockfiles.

## Linux, macOS, and WSL

Clone the repository into a directory you control, then run:

```sh
git clone https://github.com/iamsreecharan/Memglide.git
cd Memglide
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run python scripts/bundle_frontend.py
uv run memglide doctor
uv run memglide project add /absolute/path/to/approved/repository
uv run memglide serve
```

Open `http://127.0.0.1:8765`. Use an existing checkout when one is already provided; a cloud task is isolated and does not need a Git worktree. On WSL, keep repositories and the SQLite database on the Linux filesystem when possible. Run Codex and Memglide in the same WSL environment; Windows and WSL path formats are different.

To keep development state in an excluded local directory:

```sh
export MEMGLIDE_HOME="$PWD/.memglide"
uv run memglide doctor
```

Set the same variable for every process that should share that state, including the process launching your MCP client. Prefer an absolute path for persistent use.

## Windows PowerShell

Install native Python, uv, Node.js, and Git. Reopen PowerShell so the commands are on `PATH`.

```powershell
git clone https://github.com/iamsreecharan/Memglide.git
Set-Location Memglide
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run python scripts/bundle_frontend.py
$env:MEMGLIDE_HOME = Join-Path (Get-Location) ".memglide"
uv run memglide doctor
uv run memglide project add "C:\Users\you\code\approved-repository"
uv run memglide serve
```

The default database is in `.memglide` under the current user's home directory unless `MEMGLIDE_HOME` is set. Windows ACLs determine filesystem access; POSIX mode bits are not equivalent to a Windows access-control policy. Native Windows commands are documented for portability; see `PROGRESS.md` for the platforms actually exercised in this checkout.

## Build and install a local wheel

Build the frontend before packaging:

```sh
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run python scripts/bundle_frontend.py
uv build
uv tool install ./dist/memglide-0.1.0-py3-none-any.whl
memglide doctor
memglide serve
```

On PowerShell the same wheel command works with `./dist/…` paths. The wheel contains compiled frontend assets under `memglide/web`; Node/npm is required to build from source, not to run the built wheel. `scripts/bundle_frontend.py` replaces only that generated package directory and rejects symlinked build assets. No package publication is part of this workflow.

For an isolated installation test without changing your normal tool installation:

```sh
uv venv .local/package-test
uv pip install --python .local/package-test/bin/python ./dist/memglide-0.1.0-py3-none-any.whl
.local/package-test/bin/memglide doctor
```

On Windows replace `.local/package-test/bin/python` and `.local/package-test/bin/memglide` with `.local/package-test/Scripts/python.exe` and `.local/package-test/Scripts/memglide.exe`.

## Start and stop

`memglide serve` defaults to `127.0.0.1:8765`; use `--port 8766` for a local port conflict. Stop it with Ctrl+C. CLI and MCP operations can still use the database without a dashboard process. Watcher-based background indexing runs only while its owning service process is running; use `memglide project reindex PROJECT_ID` after offline edits. Source hashes are checked on retrieval even when a watcher has not observed a change.

Use `memglide cleanup` to remove expired sessions now. Use `memglide session clear SESSION_ID` for immediate session deletion, and `memglide project remove PROJECT_ID` to remove its registration/index and associated task records. These commands never delete source files.
