"""Source-only fixture tests used to discover related test evidence."""

from api.auth import authenticate_user, verify_token


def test_reject_unsigned_token() -> None:
    assert verify_token("unsigned", bytes(range(32))) is None


def test_reject_non_bearer_header() -> None:
    assert authenticate_user("Basic ignored", bytes(range(32))) is None
