"""Compare source references from Memglide with ordinary ripgrep search.

This reports retrieval evidence, never model token or cost savings.
Run: uv run python examples/smoke_compare.py /absolute/path/to/git-repo authenticate_user
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from memglide.service import Service


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("query", nargs="?", default="authenticate_user")
    args = parser.parse_args()
    rg = shutil.which("rg")
    if not rg:
        parser.error("ripgrep (rg) is required for the baseline comparison")
    repository = args.repository.resolve(strict=True)
    baseline = subprocess.run(
        [rg, "--json", "--fixed-strings", "--", args.query, "."],
        cwd=repository,
        text=True,
        capture_output=True,
        check=False,
    )
    if baseline.returncode not in {0, 1}:
        raise SystemExit(baseline.stderr.strip() or "ripgrep baseline failed")
    # Report locations only: raw baseline source might contain sensitive content
    # in files that Memglide deliberately excludes from its own index.
    baseline_references = []
    for line in baseline.stdout.splitlines():
        event = json.loads(line)
        if event["type"] == "match":
            data = event["data"]
            baseline_references.append(
                {
                    "path": data["path"].get("text", "<non-UTF-8 path>"),
                    "line": data["line_number"],
                }
            )
    # Keep this example's state in the current checkout, separate from user state.
    state_parent = Path(__file__).resolve().parents[1] / ".local"
    state_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="smoke-", dir=state_parent) as temporary:
        service = Service(Path(temporary) / "comparison.db")
        try:
            project = service.indexer.add_project(str(repository))
            session = service.memory.start_session(project["id"], args.query)
            search = service.indexer.search(project["id"], args.query)
            context = service.context.get_context(session["id"], args.query, level=2, budget=8000)
            print(
                json.dumps(
                    {
                        "query": args.query,
                        "ripgrep_matches": baseline_references,
                        "memglide_ranked_references": [
                            {
                                key: hit.get(key)
                                for key in ("path", "symbol", "start_line", "end_line", "reason")
                            }
                            for hit in search
                        ],
                        "selected_paths": sorted({item["path"] for item in context["items"]}),
                        "estimated_context_tokens": context["estimated_tokens"],
                        "passport_status": context["passport"]["status"],
                        "warnings": context["warnings"],
                        "interpretation": "Source-reference smoke comparison only; no model usage or savings measured.",
                    },
                    indent=2,
                )
            )
        finally:
            service.close()


if __name__ == "__main__":
    main()
