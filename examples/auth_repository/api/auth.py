"""Authentication helpers with an injected key and no stored credentials."""

from __future__ import annotations

import hashlib
import hmac


def verify_token(token: str, signing_key: bytes) -> str | None:
    """Verify a signed opaque user identifier and return its subject."""
    subject, separator, signature = token.rpartition(".")
    if not separator or not subject:
        return None
    expected = hmac.new(signing_key, subject.encode(), hashlib.sha256).hexdigest()
    return subject if hmac.compare_digest(signature, expected) else None


def authenticate_user(authorization: str, signing_key: bytes) -> str | None:
    """Authenticate a Bearer header using the configured verification key."""
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer":
        return None
    return verify_token(token, signing_key)
