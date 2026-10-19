"""Source-controlled identifier size must not cause suffix-rescanning work."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from memglide.core.query import tokens


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("HTTPRequest", ["http", "request"]),
        ("XMLHttpRequest", ["xml", "http", "request"]),
        ("APIResponse APIs URLSafeBase64", ["api", "response", "api", "url", "safe", "base64"]),
        ("customerID getHTTPURL", ["customer", "id", "get", "httpurl"]),
        ("caféDéjàVu HTTPServer", ["cafédéjàvu", "http", "server"]),
        ("JSON2XMLParser foo_bar", ["json2", "xml", "parser", "foo", "bar"]),
        ("AAaA aB2C", ["aa", "b2", "c"]),
        ("statuses aliases caches", ["status", "alias", "cache"]),
    ],
)
def test_identifier_boundaries_keep_normalized_search_terms(text, expected):
    assert tokens(text) == expected


def test_adversarial_acronyms_are_normalized_with_bounded_wall_time():
    # A process timeout makes a future quadratic regression fail safely rather
    # than tying up the suite. This is a resource control, not a speed benchmark.
    command = """
import json
from memglide.core.query import tokens
value = 'Q' * 500_000
result = tokens(value)
assert result == [value.lower()]
assert tokens(value + 'CacheEntry') == [value.lower(), 'cache', 'entry']
print(json.dumps({'characters': len(value), 'valid': True}))
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", command],
        capture_output=True, text=True, check=True, timeout=10,
    )
    assert json.loads(result.stdout) == {"characters": 500_000, "valid": True}
