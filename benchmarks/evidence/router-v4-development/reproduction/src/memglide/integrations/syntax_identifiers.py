"""Private isolated Tree-sitter query-term worker; repository source is data."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path, PurePosixPath

MAX_PAYLOAD_BYTES = 13 * 1024 * 1024


def extract(sources: dict[str, str], query_terms: set[str]) -> dict[str, list[str]]:
    import tree_sitter
    import tree_sitter_javascript
    import tree_sitter_typescript

    from memglide.integrations.source_evidence import _lexical_terms

    identifier_kinds = {
        "identifier", "property_identifier", "type_identifier",
        "shorthand_property_identifier", "shorthand_property_identifier_pattern",
        "private_property_identifier",
    }
    opaque_kinds = {"comment", "regex", "string", "string_fragment", "template_chars", "jsx_text"}
    result = {}
    deadline = time.perf_counter() + 3.0
    visited = 0
    for path, source in sources.items():
        suffix = PurePosixPath(path).suffix.casefold()
        grammar = (
            tree_sitter_typescript.language_tsx() if suffix == ".tsx"
            else tree_sitter_typescript.language_typescript() if suffix == ".ts"
            else tree_sitter_javascript.language()
        )
        parser = tree_sitter.Parser(
            tree_sitter.Language(grammar),
            timeout_micros=min(200_000, max(1, int((deadline - time.perf_counter()) * 1_000_000))),
        )
        data = source.encode("utf-8")
        tree = parser.parse(data)
        if tree is None or tree.root_node.has_error or time.perf_counter() > deadline:
            raise ValueError("Syntax evidence unavailable")
        matched: set[str] = set()
        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            visited += 1
            if visited > 200_000 or (visited % 1024 == 0 and time.perf_counter() > deadline):
                raise ValueError("Syntax evidence limit")
            if node.is_missing or node.type == "ERROR":
                raise ValueError("Syntax evidence unavailable")
            if node.type in opaque_kinds:
                continue
            if node.type in identifier_kinds:
                matched.update(_lexical_terms(data[node.start_byte:node.end_byte].decode("utf-8"), query_terms))
            if visited + len(stack) + node.named_child_count > 200_000:
                raise ValueError("Syntax evidence limit")
            stack.extend(reversed(node.named_children))
        result[path] = sorted(matched)
    return result


def main() -> None:
    # Only the trusted application installation becomes importable. Neither
    # indexed repositories, cwd nor PYTHONPATH influence worker imports.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    payload = sys.stdin.buffer.read(MAX_PAYLOAD_BYTES + 1)
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise ValueError("Input limit")

    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate key")
            result[key] = value
        return result

    value = json.loads(payload, object_pairs_hook=unique)
    if not isinstance(value, dict) or set(value) != {"sources", "terms"}:
        raise ValueError("Invalid worker input")
    sources, terms = value["sources"], value["terms"]
    if (
        not isinstance(sources, dict) or not 1 <= len(sources) <= 24
        or not isinstance(terms, list) or len(terms) > 64
        or any(not isinstance(term, str) or not term or len(term) > 128 for term in terms)
        or len(set(terms)) != len(terms)
        or any(
            not isinstance(path, str) or len(path) > 4096
            or PurePosixPath(path).suffix.casefold() not in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}
            or not isinstance(source, str) for path, source in sources.items()
        )
        or sum(len(source.encode("utf-8")) for source in sources.values()) > 2 * 1024 * 1024
    ):
        raise ValueError("Invalid worker bounds")
    result = extract(sources, set(terms))
    print(json.dumps({"version": 1, "files": result}, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    if sys.argv[1:] != ["--worker"]:
        raise SystemExit("This module is a private syntax worker")
    main()
