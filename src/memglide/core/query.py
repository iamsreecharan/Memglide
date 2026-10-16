"""Shared, deterministic lexical normalization for source and natural-language queries.

These rules deliberately stop short of semantic expansion: they split code identifiers
and normalize a small set of regular English plurals without guessing synonyms.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

INDEX_VERSION = 3

_STOP_WORDS = frozenset(
    "a an and are as at be been being by can could do does for from had has have how "
    "i if in into is it its of on or our should that the their then there these they "
    "this those to was we were what when where which while who why will with would "
    "you your find fix implement please ensure function functions file files handled".split()
)
_UNCHANGED_PLURALS = frozenset({"news", "series", "species"})


def _singular(word: str) -> str:
    if word in _UNCHANGED_PLURALS:
        return word
    exceptions = {
        "buses": "bus",
        "statuses": "status",
        "aliases": "alias",
        "caches": "cache",
        "headaches": "headache",
        "niches": "niche",
    }
    if word in exceptions:
        return exceptions[word]
    if len(word) > 5 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith(("sses", "xes", "zzes", "ches", "shes")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokens(text: str, *, normalize: bool = True, remove_stopwords: bool = True) -> list[str]:
    """Split acronym/camel/snake identifiers and prose using the same lexical rules.

    Intent classifiers can disable normalization and stop-word removal when a literal
    word (for example ``changes`` or ``we``) is part of their explicit grammar.
    """
    if normalize:
        text = re.sub(r"\b([A-Z]{2,})s\b", r"\1", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    words = re.findall(r"[^\W_]+", text.casefold())
    result = []
    for word in words:
        if remove_stopwords and word in _STOP_WORDS:
            continue
        result.append(_singular(word) if normalize else word)
    return result


def term_variants(word: str) -> tuple[str, ...]:
    """Regular surface forms for FTS, whose existing source index is not stemmed.

    Exact tokens, rather than arbitrary prefixes, prevent short query words from
    matching unrelated longer identifiers. The index separately stores split names.
    """
    variants = {word, word + "s"}
    if len(word) > 2 and word.endswith("y") and word[-2] not in "aeiou":
        variants.add(word[:-1] + "ies")
    if word.endswith(("s", "x", "z", "ch", "sh")):
        variants.add(word + "es")
    return tuple(sorted(variants))


def explicit_identifier(query: str, name: str, qualified_name: str) -> bool:
    """Whether prose explicitly identifies a declaration, beyond ordinary word overlap.

    Whole-query exact matches are handled separately by search. Single prose nouns
    such as ``Document`` are not strong evidence merely because a class shares the
    word; quoting, call syntax, qualification, or identifier casing makes intent clear.
    """
    folded = query.casefold()
    for identifier in {name, qualified_name}:
        if identifier.casefold() not in folded:
            continue
        escaped = re.escape(identifier)
        boundary = rf"(?<![\w$]){escaped}(?![\w$])"
        if not re.search(boundary, query, re.IGNORECASE):
            continue
        code_like = (
            "_" in identifier
            or "." in identifier
            or "$" in identifier
            or bool(re.search(r"[a-z0-9][A-Z]|[A-Z]{2}[a-z]", identifier))
        )
        quoted = "|".join(rf"{quote}{escaped}{quote}" for quote in ("`", '"', "'"))
        if code_like or re.search(rf"{quoted}|{boundary}\s*\(", query, re.IGNORECASE):
            return True
    return False


def explicit_path(query: str, path: str) -> bool:
    """Match complete path components or an explicitly written source filename.

    A substring such as ``cat`` inside ``catalog.py`` is lexical overlap at most,
    rather than an exact path reference deserving the strongest file-path weight.
    """
    source = PurePosixPath(path.casefold())
    folded = query.casefold()
    exact = folded.strip()
    if exact in {str(source), str(source.with_suffix("")), source.name, source.stem}:
        return True
    if exact in source.parts[:-1]:
        return True
    for candidate in {str(source), source.name}:
        if candidate not in folded:
            continue
        if "." not in candidate and "/" not in candidate:
            continue
        if re.search(r"(?<![\w./-])" + re.escape(candidate) + r"(?![\w./-])", folded):
            return True
    return False
