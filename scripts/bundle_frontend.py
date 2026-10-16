"""Copy the verified Vite production output into the Python package.

Run from any directory after `npm ci && npm run build` in frontend/.
This script only replaces the generated src/memglide/web directory.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def bundle() -> Path:
    repository = Path(__file__).resolve().parents[1]
    source = repository / "frontend" / "dist"
    destination = repository / "src" / "memglide" / "web"
    if not (source / "index.html").is_file():
        raise SystemExit(
            "Missing frontend/dist/index.html; run npm ci && npm run build in frontend."
        )
    if not any(source.rglob("*.js")):
        raise SystemExit(
            "The frontend build contains no JavaScript assets; rebuild frontend first."
        )
    if source.is_symlink() or any(path.is_symlink() for path in source.rglob("*")):
        raise SystemExit("Refusing to bundle symlinked build output.")
    if destination.is_symlink():
        raise SystemExit("Refusing to replace a symlinked package web directory.")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    print(f"Bundled production frontend in {destination.relative_to(repository)}")
    return destination


if __name__ == "__main__":
    bundle()
