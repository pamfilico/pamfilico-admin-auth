"""Factory that builds a Flask Blueprint with just the admin login route.

Auth only. User management (listing, filtering, pagination, etc.) is app-specific
and stays in the consuming app — that's why this blueprint takes no user model and
no DB session.
"""

import secrets

from flask import Blueprint, request
from marshmallow import ValidationError
from pamfilico_flask_core import standard_response

from pamfilico_admin_auth.config import DEFAULT_CONFIG, AdminAuthConfig
from pamfilico_admin_auth.jwt import (
    AdminJwtClaims,
    admin_login_password,
    admin_login_username,
    create_admin_jwt,
)
from pamfilico_admin_auth.schemas import AdminLoginDataSchema, AdminLoginLoadSchema


def _timing_safe_equal(a: str, b: str) -> bool:
    """Timing-safe string compare (returns False on type or length mismatch)."""
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    if len(a) != len(b):
        return False
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def build_admin_blueprint(
    config: AdminAuthConfig = DEFAULT_CONFIG,
    name: str = "pamfilico_admin_auth",
) -> Blueprint:
    """
    Build a Flask Blueprint exposing just ``POST /login``.

    The blueprint has **no internal url_prefix** — the caller picks the mount point
    via ``app.register_blueprint(bp, url_prefix="/api/v1/admin")``.

    Args:
        config: ``AdminAuthConfig`` controlling env var names / header / TTL.
        name: Blueprint name (default ``pamfilico_admin_auth``).

    The caller is responsible for any app-specific admin endpoints (user listing,
    email broadcasts, metrics, etc.). Protect those with ``@admin_authenticate``.
    """
    bp = Blueprint(name, __name__)

    @bp.route("/login", methods=["POST"])
    def admin_login():
        try:
            payload = AdminLoginLoadSchema().load(request.get_json() or {})
        except ValidationError as e:
            return standard_response(
                error=True,
                ui_message="Invalid request",
                data={"errors": e.messages},
                status_code=400,
            )
        u = admin_login_username(config)
        p = admin_login_password(config)
        # Fail closed when credentials are unconfigured — never accept an empty-string
        # login, even if the payload also sent empty strings.
        if not u or not p:
            return standard_response(
                data=None,
                error=True,
                ui_message="Admin login is not configured",
                status_code=401,
            )
        if not (
            _timing_safe_equal(payload["username"], u)
            and _timing_safe_equal(payload["password"], p)
        ):
            return standard_response(
                data=None, error=True, ui_message="Invalid credentials", status_code=401
            )
        token = create_admin_jwt(
            AdminJwtClaims(sub=payload["username"], role="admin"),
            config=config,
        )
        data = AdminLoginDataSchema().dump(
            {
                "accessToken": token,
                "tokenType": "Bearer",
                "expiresIn": config.token_ttl_seconds,
            }
        )
        return standard_response(data=data, ui_message="OK")

    return bp
