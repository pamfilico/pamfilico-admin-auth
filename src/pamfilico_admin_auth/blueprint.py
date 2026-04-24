"""Factory that builds a Flask Blueprint with /admin/login + /admin/users routes."""

import secrets
from typing import Any, Callable, Optional, Type

from flask import Blueprint, request
from marshmallow import Schema, ValidationError
from pamfilico_flask_core import standard_response

from pamfilico_admin_auth.config import DEFAULT_CONFIG, AdminAuthConfig
from pamfilico_admin_auth.decorators import AdminAuthContext, admin_authenticate
from pamfilico_admin_auth.jwt import (
    AdminJwtClaims,
    admin_login_password,
    admin_login_username,
    create_admin_jwt,
)
from pamfilico_admin_auth.repository import AdminUserRepository
from pamfilico_admin_auth.schemas import (
    AdminLoginDataSchema,
    AdminLoginLoadSchema,
    AdminUserListQuerySchema,
    DefaultAdminUserListItemSchema,
)


def _timing_safe_equal(a: str, b: str) -> bool:
    """Timing-safe string compare (returns False on type or length mismatch)."""
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    if len(a) != len(b):
        return False
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def build_admin_blueprint(
    user_model: Type[Any],
    get_db_session: Callable[[], Any],
    config: AdminAuthConfig = DEFAULT_CONFIG,
    user_serializer: Optional[Schema] = None,
    name: str = "pamfilico_admin_auth",
) -> Blueprint:
    """
    Build a Flask Blueprint exposing ``POST /login`` and ``GET /users``.

    The blueprint has **no internal url_prefix** — the caller decides the mount point
    via ``app.register_blueprint(bp, url_prefix="/api/v1/admin")``. This matches
    Flask's convention and avoids the "blueprint self-prefix vs. register_blueprint
    prefix" override footgun.

    Args:
        user_model: SQLAlchemy model class for users (must expose ``id``, ``email``,
            ``created_at`` and ``last_updated`` columns).
        get_db_session: Callable returning a fresh SQLAlchemy ``Session``. The
            blueprint closes the session after each request.
        config: ``AdminAuthConfig`` controlling env var names / header / TTL.
        user_serializer: Optional Marshmallow ``Schema`` instance to serialize user
            rows. Defaults to :class:`DefaultAdminUserListItemSchema`.
        name: Blueprint name (default ``pamfilico_admin_auth``).
    """
    bp = Blueprint(name, __name__)
    serializer = user_serializer or DefaultAdminUserListItemSchema()

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

    @bp.route("/users", methods=["GET"])
    @admin_authenticate(config=config)
    def admin_list_users(admin: AdminAuthContext):
        try:
            q = AdminUserListQuerySchema().load(
                {
                    "currentPage": int(request.args.get("currentPage", 1) or 1),
                    "pageSize": int(request.args.get("pageSize", 20) or 20),
                    "email_contains": request.args.get("email_contains", "") or "",
                }
            )
        except (ValidationError, ValueError) as e:
            err_data = e.messages if isinstance(e, ValidationError) else str(e)
            return standard_response(
                data=err_data,
                error=True,
                ui_message="Invalid query",
                status_code=400,
            )
        session = get_db_session()
        try:
            repo = AdminUserRepository(session, user_model)
            rows, pagination = repo.paginate(
                current_page=q["currentPage"],
                page_size=q["pageSize"],
                email_contains=q.get("email_contains") or "",
            )
            data = (
                serializer.dump(rows, many=True)
                if hasattr(serializer, "dump")
                else [serializer(r) for r in rows]
            )
            return standard_response(data=data, pagination=pagination, ui_message="OK")
        finally:
            session.close()

    return bp
