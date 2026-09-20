"""Minimal in-memory rate limiter for auth endpoints.

Not distributed — fine for a single-instance demo deployment. Swap for a
Redis-backed limiter (the app already depends on REDIS_URL) if this ever
runs behind more than one worker process.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

# ip -> list of unix timestamps of recent attempts
_attempts: dict[str, list[float]] = defaultdict(list)

WINDOW_SECONDS = 60
MAX_ATTEMPTS = 10  # per window, per client IP, per guarded endpoint


def _client_ip(request: Request) -> str:
    # Respect a proxy header when present (Render/Railway/behind a LB),
    # falling back to the direct connection.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_rate_limit(request: Request, bucket: str) -> None:
    """Raise 429 if this client has exceeded the limit for `bucket`."""
    key = f"{bucket}:{_client_ip(request)}"
    now = time.time()
    window_start = now - WINDOW_SECONDS

    attempts = [t for t in _attempts[key] if t > window_start]
    if len(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please wait a minute and try again.",
        )

    attempts.append(now)
    _attempts[key] = attempts
