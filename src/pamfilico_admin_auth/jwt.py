"""Admin JWT: HS256 token. Keep separate from any NextAuth JWE session token."""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from flask import request

from pamfilico_admin_auth.config import DEFAULT_CONFIG, AdminAuthConfig

logger = logging.getLogger(__name__)

# Re-exported so callers can reference the default header without importing config
ADMIN_TOKEN_HEADER = DEFAULT_CONFIG.token_header


@dataclass(frozen=True)
class AdminJwtClaims:
    """Claims stored in a valid admin access token."""

    sub: str
    role: str = "admin"


def admin_jwt_secret(config: AdminAuthConfig = DEFAULT_CONFIG) -> str:
    """Signing key for admin JWT. Reads env var named by config; dev-only fallback."""
    s = (os.environ.get(config.jwt_secret_env) or "").strip()
    if s:
        return s
    logger.warning(
        "%s is unset; using development-only default. Set %s for production.",
        config.jwt_secret_env,
        config.jwt_secret_env,
    )
    return config.default_dev_jwt_secret


def admin_login_username(config: AdminAuthConfig = DEFAULT_CONFIG) -> str:
    u = (os.environ.get(config.username_env) or "").strip()
    return u or config.default_username


def admin_login_password(config: AdminAuthConfig = DEFAULT_CONFIG) -> str:
    p = (os.environ.get(config.password_env) or "").strip()
    return p or config.default_password


def get_raw_admin_bearer_from_request(
    config: AdminAuthConfig = DEFAULT_CONFIG,
) -> Optional[str]:
    """
    Return the admin bearer token from the current Flask request.

    Precedence: the configured custom header (default ``ADMIN-TOKEN``), then the
    standard ``Authorization: Bearer <token>`` header.
    """
    from_header = request.headers.get(config.token_header, "").strip()
    if from_header:
        return from_header
    auth = request.headers.get("Authorization", "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return None


def create_admin_jwt(
    claims: AdminJwtClaims,
    ttl_seconds: Optional[int] = None,
    config: AdminAuthConfig = DEFAULT_CONFIG,
) -> str:
    """Mint a new HS256 admin access token. Default TTL comes from config (24h)."""
    ttl = ttl_seconds if ttl_seconds is not None else config.token_ttl_seconds
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": claims.sub,
        "role": claims.role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl)).timestamp()),
    }
    return jwt.encode(payload, admin_jwt_secret(config), algorithm="HS256")


def verify_admin_jwt(
    token: str,
    config: AdminAuthConfig = DEFAULT_CONFIG,
) -> AdminJwtClaims:
    """Validate an HS256 admin JWT. Raises ``jwt.PyJWTError`` on any failure."""
    if not token or not str(token).strip():
        raise jwt.InvalidTokenError("empty token")
    data = jwt.decode(
        str(token).strip(),
        admin_jwt_secret(config),
        algorithms=["HS256"],
        options={"require": ["exp", "iat", "sub", "role"]},
    )
    if data.get("role") != "admin":
        raise jwt.InvalidTokenError("invalid role")
    return AdminJwtClaims(sub=str(data["sub"]))
