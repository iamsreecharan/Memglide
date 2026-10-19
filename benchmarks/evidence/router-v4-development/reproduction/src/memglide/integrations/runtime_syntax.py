"""Private bounded syntax-role worker. Source is parsed as data, never imported.

Roles describe syntax, not compiler erasure or actual program execution. In
particular Python annotations and TypeScript enums can have runtime effects.
"""
from __future__ import annotations

import ast
import json
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

MAX_PAYLOAD_BYTES = 13 * 1024 * 1024
MAX_OUTPUT_BYTES = 1_000_000
MAX_NODES = 200_000
MAX_UNITS = 256
MAX_UNITS_PER_ROLE = 4
LANGUAGES = frozenset({".py", ".pyi", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"})


class _Work:
    def __init__(self, terms: set[str], query: str):
        self.terms = terms
        self.query = query
        self.deadline = time.perf_counter() + 3.0
        self.visited = 0

    def tick(self, pending: int = 0) -> None:
        self.visited += 1
        if self.visited + pending > MAX_NODES or time.perf_counter() > self.deadline:
            raise ValueError("Runtime syntax work limit")

    def matches(self, value: str) -> set[str]:
        from memglide.integrations.source_evidence import _lexical_terms
        return _lexical_terms(value, self.terms)

    def explicit(self, name: str) -> bool:
        from memglide.core.query import explicit_identifier
        return bool(name) and name in self.query and explicit_identifier(self.query, name, name)


def _unit(role: str, header: set[str] | None = None, explicit: bool = False) -> dict[str, Any]:
    return {"role": role, "code": set(), "header": set(header or ()), "docs": set(),
            "explicit": explicit}


def _pair(units: list[dict[str, Any]], work: _Work, name: str = "") -> tuple[int, int]:
    if len(units) + 2 > MAX_UNITS:
        raise ValueError("Runtime syntax unit limit")
    header = work.matches(name)
    explicit = work.explicit(name)
    runtime = len(units)
    units.extend([_unit("runtime", header, explicit), _unit("declaration", header, explicit)])
    return runtime, runtime + 1


def _python(source: str, path: str, work: _Work) -> list[dict[str, Any]]:
    tree = ast.parse(source)
    units: list[dict[str, Any]] = []
    runtime, declaration = _pair(units, work)
    # Role override is local to a subtree; annotations do not become body evidence.
    stack: list[tuple[ast.AST, int, int, bool]] = [(tree, runtime, declaration, False)]
    while stack:
        node, runtime, declaration, annotation = stack.pop()
        work.tick(len(stack))
        destination = declaration if annotation else runtime
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            runtime, declaration = _pair(units, work, node.name)
            if annotation:
                units[runtime]["role"] = "declaration"
            destination = runtime
            body = list(node.body)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                doc = body[0].value.value
                if isinstance(doc, str):
                    units[runtime]["docs"].update(work.matches(doc))
                    units[declaration]["docs"].update(work.matches(doc))
                    body = body[1:]
            stack.extend((item, runtime, declaration, annotation) for item in reversed(body))
            stack.extend((item, runtime, declaration, annotation) for item in node.decorator_list)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stack.append((node.args, runtime, declaration, annotation))
                if node.returns is not None:
                    stack.append((node.returns, runtime, declaration, True))
            else:
                stack.extend((item, runtime, declaration, annotation) for item in node.bases)
                stack.extend((item, runtime, declaration, annotation) for item in node.keywords)
            stack.extend((item, runtime, declaration, True) for item in getattr(node, "type_params", ()))
            continue
        if isinstance(node, ast.arg):
            matches = work.matches(node.arg)
            units[runtime]["header"].update(matches)
            units[declaration]["header"].update(matches)
            if node.annotation is not None:
                stack.append((node.annotation, runtime, declaration, True))
            continue
        if isinstance(node, ast.arguments):
            if node.vararg is not None:
                units[runtime]["code"].update(work.matches("positional argument"))
            if node.kwarg is not None:
                units[runtime]["code"].update(work.matches("keyword argument"))
        if isinstance(node, ast.AnnAssign):
            stack.append((node.target, runtime, declaration, annotation or node.value is None))
            stack.append((node.annotation, runtime, declaration, True))
            if node.value is not None:
                stack.append((node.value, runtime, declaration, annotation))
            continue
        if type(node).__name__ == "TypeAlias":  # Python 3.12 syntax, without a 3.11 dependency.
            stack.extend((item, runtime, declaration, True) for item in ast.iter_child_nodes(node))
            continue
        if isinstance(node, ast.If) and (
            isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
            or isinstance(node.test, ast.Attribute) and node.test.attr == "TYPE_CHECKING"
        ):
            stack.extend((item, runtime, declaration, True) for item in node.body)
            stack.extend((item, runtime, declaration, annotation) for item in node.orelse)
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Import declarations identify a dependency, not implementation behavior.
            for alias in node.names:
                units[declaration]["code"].update(work.matches(alias.name))
                if alias.asname:
                    units[declaration]["code"].update(work.matches(alias.asname))
            continue
        if isinstance(node, ast.Name):
            units[destination]["code"].update(work.matches(node.id))
        elif isinstance(node, ast.Attribute):
            units[destination]["code"].update(work.matches(node.attr))
        elif isinstance(node, ast.Constant):
            continue
        children = list(ast.iter_child_nodes(node))
        if work.visited + len(stack) + len(children) > MAX_NODES:
            raise ValueError("Runtime syntax node limit")
        stack.extend((child, runtime, declaration, annotation) for child in reversed(children))
    if path.casefold().endswith(".pyi"):
        for unit in units:
            unit["role"] = "declaration"
    return units


def _native(source: str, path: str, work: _Work) -> list[dict[str, Any]]:
    import tree_sitter
    import tree_sitter_javascript
    import tree_sitter_typescript

    suffix = PurePosixPath(path).suffix.casefold()
    grammar = (
        tree_sitter_typescript.language_tsx() if suffix == ".tsx"
        else tree_sitter_typescript.language_typescript() if suffix == ".ts"
        else tree_sitter_javascript.language()
    )
    parser = tree_sitter.Parser(tree_sitter.Language(grammar), timeout_micros=min(
        200_000, max(1, int((work.deadline - time.perf_counter()) * 1_000_000))))
    data = source.encode("utf-8")
    tree = parser.parse(data)
    if tree is None or tree.root_node.has_error:
        raise ValueError("Runtime syntax unavailable")
    identifiers = {"identifier", "property_identifier", "type_identifier",
                   "shorthand_property_identifier", "shorthand_property_identifier_pattern",
                   "private_property_identifier"}
    opaque = {"comment", "regex", "string", "string_fragment", "template_chars", "jsx_text"}
    declarations = {
        "type_alias_declaration", "interface_declaration", "type_annotation", "type_arguments",
        "type_parameters", "type_parameter", "ambient_declaration", "function_signature",
        "method_signature", "property_signature", "abstract_method_signature", "import_statement",
    }
    definitions = {"function_declaration", "generator_function_declaration", "method_definition",
                   "class_declaration", "abstract_class_declaration", "type_alias_declaration",
                   "interface_declaration", "variable_declarator", "enum_declaration",
                   "function_signature", "method_signature", "abstract_method_signature"}
    units: list[dict[str, Any]] = []
    runtime, declaration = _pair(units, work)
    # Header flag marks clean declaration names/parameter patterns, not source slices.
    stack = [(tree.root_node, runtime, declaration, False, False)]
    while stack:
        node, runtime, declaration, annotation, header = stack.pop()
        work.tick(len(stack))
        if node.is_missing or node.type == "ERROR":
            raise ValueError("Runtime syntax unavailable")
        if node.type in opaque:
            continue
        if node.type in definitions:
            name_node = node.child_by_field_name("name")
            name = data[name_node.start_byte:name_node.end_byte].decode() if name_node else ""
            runtime, declaration = _pair(units, work, name)
            if annotation or node.type in {"type_alias_declaration", "interface_declaration",
                                              "function_signature", "method_signature",
                                              "abstract_method_signature"}:
                units[runtime]["role"] = "declaration"
        annotation = annotation or node.type in declarations or node.type == "type_identifier"
        if node.type == "export_statement" and any(child.type == "type" for child in node.children):
            annotation = True
        destination = declaration if annotation else runtime
        if node.type in identifiers:
            matched = work.matches(data[node.start_byte:node.end_byte].decode("utf-8"))
            if header:
                units[runtime]["header"].update(matched)
                units[declaration]["header"].update(matched)
            else:
                units[destination]["code"].update(matched)
        if work.visited + len(stack) + node.named_child_count > MAX_NODES:
            raise ValueError("Runtime syntax node limit")
        name_node = node.child_by_field_name("name") if node.type in definitions else None
        pattern = node.child_by_field_name("pattern") if node.type in {
            "required_parameter", "optional_parameter", "rest_pattern"} else None
        for child in reversed(node.named_children):
            child_header = header or child == name_node or child == pattern
            # A parameter's type is never inherited as parameter-name evidence.
            if child.type in declarations or child.type == "type_identifier":
                child_header = False
            stack.append((child, runtime, declaration, annotation, child_header))
    if path.casefold().endswith(".d.ts"):
        for unit in units:
            unit["role"] = "declaration"
    return units


def extract(sources: dict[str, str], terms: set[str], query: str) -> dict[str, list[dict[str, Any]]]:
    work = _Work(terms, query)
    result = {}
    for path, source in sources.items():
        units = (_python(source, path, work) if PurePosixPath(path).suffix.casefold() in {".py", ".pyi"}
                 else _native(source, path, work))
        retained = []
        for role in ("runtime", "declaration"):
            choices = [unit for unit in units if unit["role"] == role]
            choices.sort(key=lambda unit: (
                -int(unit["explicit"]), -len(unit["code"]),
                -len(unit["code"] | unit["header"]), -len(unit["docs"])))
            retained.extend(choices[:MAX_UNITS_PER_ROLE])
        result[path] = [{key: sorted(value) if isinstance(value, set) else value
                         for key, value in unit.items()} for unit in retained]
    return result


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    payload = sys.stdin.buffer.read(MAX_PAYLOAD_BYTES + 1)
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise ValueError("Runtime syntax input limit")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate key")
            result[key] = value
        return result

    value = json.loads(payload, object_pairs_hook=unique)
    if not isinstance(value, dict) or set(value) != {"sources", "terms", "query"}:
        raise ValueError("Invalid runtime syntax input")
    sources, terms, query = value["sources"], value["terms"], value["query"]
    if (not isinstance(sources, dict) or not 1 <= len(sources) <= 24
        or not isinstance(terms, list) or len(terms) > 64
        or any(not isinstance(term, str) or not term or len(term) > 128 for term in terms)
        or len(set(terms)) != len(terms) or not isinstance(query, str) or len(query) > 4000
        or any(not isinstance(path, str) or not path or len(path) > 4096
               or PurePosixPath(path).suffix.casefold() not in LANGUAGES
               or not isinstance(source, str) for path, source in sources.items())
        or sum(len(source.encode("utf-8")) for source in sources.values()) > 2 * 1024 * 1024):
        raise ValueError("Invalid runtime syntax bounds")
    output = json.dumps({"version": 1, "files": extract(sources, set(terms), query)},
                        ensure_ascii=False, separators=(",", ":"))
    if len(output.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise ValueError("Runtime syntax output limit")
    print(output)


if __name__ == "__main__":
    if sys.argv[1:] != ["--worker"]:
        raise SystemExit("This module is a private syntax worker")
    main()
