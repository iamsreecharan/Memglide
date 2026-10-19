"""Derived ignore rules can be reused only after fresh secured policy evidence."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter

import pathspec
import pytest
from test_preload import approved as approved
from test_preload import indexed

from memglide.integrations import preload
from memglide.security import paths as source_policy


def prepare(approved, context_format="compact-prefix", *, support=False):
    return preload.prepare_prompt(
        "Correct the calculation.", project_id="approved", db_path=approved[1],
        focus_paths=["src/code.py"], support_paths=["src/support.py"] if support else [],
        context_format=context_format,
    )


def compile_counter(monkeypatch):
    original = pathspec.GitIgnoreSpec.from_lines
    seen = []

    def compile(lines):
        lines = list(lines)
        seen.append(tuple(lines))
        return original(lines)

    monkeypatch.setattr(pathspec.GitIgnoreSpec, "from_lines", staticmethod(compile))
    return seen


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
@pytest.mark.parametrize("support", [False, True])
def test_current_rules_compile_once_but_policy_and_complete_source_are_read_twice(
    approved, monkeypatch, context_format, support,
):
    sources = {"src/code.py": "def calculate():\n    return 3\n"}
    if support:
        sources["src/support.py"] = "EXPECTED = 3\n"
    for path, content in sources.items():
        indexed(approved, path, content)
    (approved[0] / ".gitignore").write_text("*.tmp\n")
    compiled = compile_counter(monkeypatch)
    reads = Counter()
    original = source_policy.read_source

    def read(root, relative, maximum):
        reads[relative] += 1
        return original(root, relative, maximum)

    monkeypatch.setattr(source_policy, "read_source", read)
    result = prepare(approved, context_format, support=support)
    assert result["mode"] == "preloaded"
    assert len(compiled) == 1
    assert reads == Counter({".gitignore": 2, **{path: 2 for path in sources}})
    if context_format == "compact-prefix":
        envelope = json.loads(result["prompt"].removesuffix(preload.TASK_SEPARATOR + "Correct the calculation."))
    else:
        envelope = json.loads(result["prompt"].removeprefix("Correct the calculation.\n\n" + preload._EXPLANATION))
    assert {item["path"]: item["content"] for item in envelope["memglide_sources"]} == sources
    assert {item["path"]: item["sha256"] for item in result["files"]} == {
        path: hashlib.sha256(content.encode()).hexdigest() for path, content in sources.items()
    }


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
@pytest.mark.parametrize("change", ["content_restored_mtime", "new_root", "new_nested", "delete", "symlink"])
def test_policy_mutations_between_reads_never_release_source(
    approved, monkeypatch, tmp_path, context_format, change,
):
    indexed(approved, "src/code.py", "VALUE = 3\n")
    policy = approved[0] / ("src/.memglideignore" if change == "new_nested" else ".gitignore")
    if change not in {"new_root", "new_nested"}:
        policy.write_text("# old policy\n")
    outside = tmp_path / "outside-policy"
    outside.write_text("# outside evidence must not enter context\n")
    original = source_policy.read_source
    changed = False

    def read(root, relative, maximum):
        nonlocal changed
        result = original(root, relative, maximum)
        if relative == "src/code.py" and not changed:
            changed = True
            if change == "delete":
                policy.unlink()
            elif change == "symlink":
                policy.unlink()
                policy.symlink_to(outside)
            else:
                previous = policy.stat() if policy.exists() else None
                policy.write_text("# new policy\n")
                if change == "content_restored_mtime":
                    os.utime(policy, ns=(previous.st_atime_ns, previous.st_mtime_ns))
        return result

    monkeypatch.setattr(source_policy, "read_source", read)
    result = prepare(approved, context_format)
    assert changed and result["mode"] == "passthrough"
    assert result["prompt"] == "Correct the calculation." and result["files"] == []
    assert result["reason"] == ("source_unavailable" if change == "symlink" else "policy_changed")


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_identical_patterns_keep_their_own_ancestor_bases(approved, monkeypatch, context_format):
    indexed(approved, "src/code.py", "VALUE = 3\n")
    indexed(approved, "src/deep/blocked.py", "ALLOWED_NESTED = 1\n")
    indexed(approved, "src/blocked.py", "MUST_NOT_BE_DELIVERED = 1\n")
    for path in (approved[0] / ".gitignore", approved[0] / "src/.gitignore"):
        path.write_text("/blocked.py\n")
    compiled = compile_counter(monkeypatch)
    allowed = preload.prepare_prompt(
        "Inspect the nested implementation.", project_id="approved", db_path=approved[1],
        focus_paths=["src/code.py"], support_paths=["src/deep/blocked.py"], context_format=context_format,
    )
    assert allowed["mode"] == "preloaded" and len(compiled) == 1
    denied = preload.prepare_prompt(
        "Inspect the nested implementation.", project_id="approved", db_path=approved[1],
        focus_paths=["src/code.py"], support_paths=["src/blocked.py"], context_format=context_format,
    )
    assert denied["mode"] == "passthrough" and denied["reason"] == "source_excluded"
    assert "MUST_NOT_BE_DELIVERED" not in denied["prompt"]


@pytest.mark.parametrize("context_format", ["legacy", "compact-prefix"])
def test_nested_negation_and_empty_rule_sets_are_preserved(approved, monkeypatch, context_format):
    indexed(approved, "src/code.py", "VALUE = 3\n")
    (approved[0] / ".gitignore").write_text("*.py\n")
    (approved[0] / "src/.gitignore").write_text("!code.py\n")
    (approved[0] / "src/.memglideignore").write_text("")
    compiled = compile_counter(monkeypatch)
    result = prepare(approved, context_format)
    assert result["mode"] == "preloaded"
    assert Counter(compiled) == Counter({("*.py",): 1, ("!code.py",): 1, (): 1})


def test_compiled_rules_do_not_persist_between_requests(approved, monkeypatch):
    indexed(approved, "src/code.py", "VALUE = 3\n")
    (approved[0] / ".gitignore").write_text("*.tmp\n")
    compiled = compile_counter(monkeypatch)
    first, second = prepare(approved), prepare(approved)
    assert first["prompt"] == second["prompt"]
    assert len(compiled) == 2


@pytest.mark.parametrize("limit", ["entries", "utf8_bytes"])
def test_full_cache_compiles_current_policy_without_retaining_more(
    approved, monkeypatch, limit,
):
    indexed(approved, "src/code.py", "VALUE = 3\n")
    (approved[0] / ".gitignore").write_text("#x\n")
    cache = preload._CompiledPolicyCache()
    policies = [f"# unique policy {index}\n" for index in range(64)] if limit == "entries" else ["#" + "λ" * 31999 + "\n"]
    for content in policies:
        cache.retain(content, hashlib.sha256(content.encode()).hexdigest(), pathspec.GitIgnoreSpec.from_lines(content.splitlines()), len(content.encode()))
    compiled = compile_counter(monkeypatch)
    selection = preload._selection(approved[1].absolute(), "approved", ("src/code.py",))
    first = preload._eligible(selection, ("src/code.py",), compiled_policies=cache)
    second = preload._eligible(selection, ("src/code.py",), compiled_policies=cache)
    assert first == second and len(compiled) == 2
    assert cache.get("#x\n", hashlib.sha256(b"#x\n").hexdigest()) is None


def test_compiled_rule_lookup_requires_both_exact_source_and_digest():
    cache = preload._CompiledPolicyCache()
    source = "*.tmp\n"
    spec = pathspec.GitIgnoreSpec.from_lines(source.splitlines())
    cache.retain(source, "same-hash-for-test", spec, len(source.encode()))
    assert cache.get(source, "same-hash-for-test") is spec
    assert cache.get("*.py\n", "same-hash-for-test") is None
    assert cache.get(source, "different-hash-for-test") is None
