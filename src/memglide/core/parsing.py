"""Non-executing structural extraction; unresolved references remain explicit."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any


@dataclass
class ParsedFile:
    language: str
    structural: bool = False
    symbols: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


def language_for(path: str) -> str:
    return {
        ".py": "python",
        ".pyi": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".ts": "typescript",
        ".mts": "typescript",
        ".cts": "typescript",
        ".tsx": "tsx",
    }.get(PurePosixPath(path).suffix.lower(), "text")


def parse_source(path: str, source: str) -> ParsedFile:
    language = language_for(path)
    try:
        if language == "python":
            return _python(source)
        if language in {"javascript", "typescript", "tsx"}:
            return _tree_sitter(language, source)
    except (RecursionError, MemoryError, ValueError, OverflowError):
        return ParsedFile(
            language,
            error="Structural parsing exceeded safe parser limits; filename/text search remains available",
        )
    return ParsedFile(language)


def parse_sources(sources: dict[str, str]) -> dict[str, ParsedFile]:
    """Batch native parsing in an isolated trusted worker, only for changed sources.

    Native grammar faults cannot kill CLI, MCP or the API. Completed line-oriented
    results survive a subsequent worker failure. Every omitted result is explicit.
    """
    result = {
        path: parse_source(path, source)
        for path, source in sources.items()
        if language_for(path) not in {"javascript", "typescript", "tsx"}
    }
    native = [(path, source) for path, source in sorted(sources.items()) if path not in result]
    batches: list[list[tuple[str, str]]] = []
    batch: list[tuple[str, str]] = []
    batch_bytes = 0
    for item in native:
        size = len(item[1].encode("utf-8"))
        if batch and (len(batch) >= 32 or batch_bytes + size > 4 * 1024 * 1024):
            batches.append(batch)
            batch = []
            batch_bytes = 0
        batch.append(item)
        batch_bytes += size
    if batch:
        batches.append(batch)
    for batch in batches:
        payload = "".join(json.dumps([path, source]) + "\n" for path, source in batch)
        output = ""
        error = "Tree-sitter worker returned incomplete evidence"
        try:
            completed = subprocess.run(
                [sys.executable, "-I", str(Path(__file__).resolve()), "--worker"],
                input=payload,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).resolve().parent,
            )
            output = completed.stdout
            if completed.returncode:
                error = f"Tree-sitter worker exited with status {completed.returncode}"
        except subprocess.TimeoutExpired as exc:
            output = (
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else exc.stdout or ""
            )
            error = "Tree-sitter worker exceeded its 30-second batch limit"
        except OSError:
            error = "Tree-sitter worker could not start"
        expected = {path for path, _ in batch}
        for line in output.splitlines():
            try:
                path, data = json.loads(line)
                if path in expected:
                    result[path] = ParsedFile(**data)
            except (TypeError, ValueError):
                continue
        for path in expected - result.keys():
            result[path] = ParsedFile(
                language_for(path),
                error=error
                + "; structural evidence unavailable; filename/text search remains available",
            )
    return result


def _python(source: str) -> ParsedFile:
    result = ParsedFile("python", True)
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError) as exc:
        result.structural = False
        result.error = f"Python parse error: {exc}"
        return result
    lines = source.splitlines()
    module_assignments: set[str] = set()

    def module_bindings(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            module_assignments.add(node.id)
        for child in ast.iter_child_nodes(node):
            module_bindings(child)

    module_bindings(tree)
    explicit_exports: set[str] | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            if isinstance(node.value, (ast.List, ast.Tuple)) and all(
                isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.value.elts
            ):
                explicit_exports = {
                    e.value
                    for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                }

    class Visitor(ast.NodeVisitor):
        scope: list[str] = []
        kinds: list[str] = []
        shadowed: list[set[str]] = []

        def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            self.definition(
                node, "method" if self.kinds and self.kinds[-1] == "class" else "function"
            )

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.definition(node, "class")

        def definition(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, kind: str
        ) -> None:
            qualified = ".".join([*self.scope, node.name])
            # AST's body locations safely identify multiline signatures without evaluating annotations.
            signature_end = node.body[0].lineno - 1 if node.body else node.lineno
            if signature_end < node.lineno:
                signature_end = node.lineno
            signature = " ".join(line.strip() for line in lines[node.lineno - 1 : signature_end])
            if len(signature) > 700:
                signature = signature[:700]
            # One-line definitions must not include their implementation in a signature.
            if len(lines) >= node.lineno and (node.body and node.body[0].lineno == node.lineno):
                signature = lines[node.lineno - 1][: node.body[0].col_offset].strip()
            exported = not self.scope and (
                node.name in explicit_exports
                if explicit_exports is not None
                else not node.name.startswith("_")
            )
            result.symbols.append(
                {
                    "name": node.name,
                    "qualified_name": qualified,
                    "kind": kind,
                    "signature": signature,
                    "start_line": min([node.lineno, *[d.lineno for d in node.decorator_list]]),
                    "end_line": node.end_lineno or node.lineno,
                    "exported": int(exported),
                }
            )
            bindings: set[str] = set()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                bindings.update(
                    a.arg for a in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                )
                if node.args.vararg:
                    bindings.add(node.args.vararg.arg)
                if node.args.kwarg:
                    bindings.add(node.args.kwarg.arg)
                for child in ast.walk(node):
                    if isinstance(child, ast.Name) and isinstance(child.ctx, (ast.Store, ast.Del)):
                        bindings.add(child.id)
            self.scope.append(node.name)
            self.kinds.append(kind)
            self.shadowed.append(bindings)
            for child in node.body:
                self.visit(child)
            self.shadowed.pop()
            self.kinds.pop()
            self.scope.pop()

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                ref = "import " + alias.name + (" as " + alias.asname if alias.asname else "")
                result.dependencies.append(
                    {
                        "kind": "import",
                        "reference": ref,
                        "source_symbol": ".".join(self.scope) or None,
                    }
                )

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            for alias in node.names:
                ref = f"from {'.' * node.level}{node.module or ''} import {alias.name}" + (
                    " as " + alias.asname if alias.asname else ""
                )
                result.dependencies.append(
                    {
                        "kind": "import",
                        "reference": ref,
                        "source_symbol": ".".join(self.scope) or None,
                    }
                )

        def visit_Call(self, node: ast.Call) -> None:
            try:
                reference = ast.unparse(node.func)
            except RecursionError:
                reference = "<complex call>"
            first = reference.split(".")[0]
            # Arguments and local assignments can shadow imported or module names.
            kind = (
                "call_unresolved"
                if first in module_assignments or any(first in names for names in self.shadowed)
                else "call"
            )
            result.dependencies.append(
                {
                    "kind": kind,
                    "reference": reference,
                    "source_symbol": ".".join(self.scope) or None,
                }
            )
            self.generic_visit(node)

    Visitor().visit(tree)
    return result


def import_parts(language: str, reference: str) -> tuple[str, str | None, str | None] | None:
    """Decode our canonical, non-executable import descriptions."""
    if language == "python":
        try:
            node = ast.parse(reference).body[0]
        except (SyntaxError, IndexError):
            return None
        if isinstance(node, ast.Import):
            alias = node.names[0]
            return alias.name, None, alias.asname or alias.name.split(".")[0]
        if isinstance(node, ast.ImportFrom):
            alias = node.names[0]
            return "." * node.level + (node.module or ""), alias.name, alias.asname or alias.name
        return None
    if reference.startswith("import:"):
        try:
            module, name, alias = json.loads(reference[7:])
            return module, name, alias
        except (ValueError, TypeError):
            return None
    return None


def _tree_sitter(language: str, source: str) -> ParsedFile:
    import tree_sitter
    import tree_sitter_javascript
    import tree_sitter_typescript

    grammar = (
        tree_sitter_javascript.language()
        if language == "javascript"
        else (
            tree_sitter_typescript.language_tsx()
            if language == "tsx"
            else tree_sitter_typescript.language_typescript()
        )
    )
    parser = tree_sitter.Parser(tree_sitter.Language(grammar))
    data = source.encode("utf-8")
    tree = parser.parse(data)
    result = ParsedFile(language, True)
    if tree.root_node.has_error:
        result.error = (
            "Tree-sitter found syntax errors; partial structural results require inspection"
        )

    def text(node: Any) -> str:
        return data[node.start_byte : node.end_byte].decode("utf-8")

    export_names: set[str] = set()
    for match in re.finditer(r"\bexport\s*\{([^}]+)\}", source):
        export_names.update(part.strip().split(" as ")[0] for part in match.group(1).split(","))

    def visit(
        node: Any,
        scope: list[str],
        source_symbol: str | None = None,
        exported: bool = False,
        shadowed: frozenset[str] = frozenset(),
    ) -> None:
        typ = node.type
        if typ == "export_statement":
            # export-from remains an explicit import relationship, including wildcard exports.
            src = node.child_by_field_name("source")
            if src:
                module = text(src)[1:-1]
                result.dependencies.append(
                    {
                        "kind": "export",
                        "reference": "import:" + json.dumps([module, "*", None]),
                        "source_symbol": source_symbol,
                    }
                )
            for child in node.named_children:
                visit(child, scope, source_symbol, True, shadowed)
            return
        if typ == "import_statement":
            src = node.child_by_field_name("source")
            if src:
                module = text(src)[1:-1]
                entries: list[tuple[str | None, str | None]] = []
                clause = next((c for c in node.named_children if c.type == "import_clause"), None)
                if clause:
                    for child in clause.named_children:
                        if child.type == "identifier":
                            entries.append(("default", text(child)))
                        elif child.type == "namespace_import":
                            ident = next(
                                (c for c in child.named_children if c.type == "identifier"), None
                            )
                            entries.append((None, text(ident) if ident else None))
                        elif child.type == "named_imports":
                            for item in child.named_children:
                                name = item.child_by_field_name("name")
                                alias = item.child_by_field_name("alias")
                                if name:
                                    entries.append(
                                        (text(name), text(alias) if alias else text(name))
                                    )
                for name, alias in entries or [(None, None)]:
                    result.dependencies.append(
                        {
                            "kind": "import",
                            "reference": "import:" + json.dumps([module, name, alias]),
                            "source_symbol": source_symbol,
                        }
                    )
            return
        definition_types = {
            "function_declaration": "function",
            "generator_function_declaration": "function",
            "class_declaration": "class",
            "abstract_class_declaration": "class",
            "method_definition": "method",
            "interface_declaration": "interface",
            "type_alias_declaration": "type",
            "enum_declaration": "enum",
        }
        kind = definition_types.get(typ)
        name_node = node.child_by_field_name("name") if kind else None
        body = node.child_by_field_name("body")
        variable_function = False
        if typ == "variable_declarator":
            value = node.child_by_field_name("value")
            if value and value.type in {
                "arrow_function",
                "function_expression",
                "generator_function",
            }:
                name_node = node.child_by_field_name("name")
                body = value.child_by_field_name("body")
                kind = "function"
                variable_function = True
        if kind and name_node:
            name = text(name_node)
            qualified = ".".join([*scope, name])
            signature_end = body.start_byte if body else node.end_byte
            signature = " ".join(data[node.start_byte : signature_end].decode("utf-8").split())[
                :700
            ]
            if (
                node.parent
                and node.parent.type == "export_statement"
                and re.match(r"export\s+default\b", text(node.parent))
            ):
                signature = "default " + signature
            result.symbols.append(
                {
                    "name": name,
                    "qualified_name": qualified,
                    "kind": kind,
                    "signature": signature,
                    "start_line": node.start_point.row + 1,
                    "end_line": node.end_point.row + 1,
                    "exported": int(exported or (not scope and name in export_names)),
                }
            )
            new_shadowed = set(shadowed)
            if kind in {"function", "method"}:
                parameters = node.child_by_field_name("parameters")
                if variable_function:
                    parameters = node.child_by_field_name("value").child_by_field_name("parameters")
                if parameters:
                    for item in parameters.named_children:
                        pattern = item.child_by_field_name("pattern") or item
                        if pattern.type == "identifier":
                            new_shadowed.add(text(pattern))
                if body:

                    def bindings(child: Any) -> None:
                        if child.type in {
                            "function_declaration",
                            "arrow_function",
                            "function_expression",
                            "class_declaration",
                        }:
                            return
                        if child.type == "variable_declarator":
                            ident = child.child_by_field_name("name")
                            if ident and ident.type == "identifier":
                                new_shadowed.add(text(ident))
                        for grandchild in child.named_children:
                            bindings(grandchild)

                    bindings(body)
            for child in node.named_children:
                if child != name_node:
                    visit(child, [*scope, name], qualified, False, frozenset(new_shadowed))
            return
        if typ in {"call_expression", "new_expression"}:
            fn = node.child_by_field_name("function") or node.child_by_field_name("constructor")
            if fn:
                reference = text(fn)
                kind = "call_unresolved" if reference.split(".")[0] in shadowed else "call"
                result.dependencies.append(
                    {"kind": kind, "reference": reference, "source_symbol": source_symbol}
                )
        for child in node.named_children:
            visit(child, scope, source_symbol, exported, shadowed)

    visit(tree.root_node, [])
    return result


def _worker() -> None:
    for line in sys.stdin:
        path, source = json.loads(line)
        result = parse_source(path, source)
        print(json.dumps([path, asdict(result)]), flush=True)


if __name__ == "__main__":
    if sys.argv[1:] != ["--worker"]:
        raise SystemExit("This module is a private parser worker")
    _worker()
