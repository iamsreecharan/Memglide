"""FastAPI source fixture; optional audit import is intentionally unresolved."""

from fastapi import FastAPI, Header, HTTPException
from optional_audit_provider import record_login

from .auth import authenticate_user

app = FastAPI()


def configured_signing_key() -> bytes:
    """An application would inject its key through a secure runtime provider."""
    raise RuntimeError("This indexing fixture is not configured to run")


@app.get("/profile")
def profile(authorization: str = Header(default="")) -> dict[str, str]:
    user = authenticate_user(authorization, configured_signing_key())
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    record_login(user)
    return {"user": user}
