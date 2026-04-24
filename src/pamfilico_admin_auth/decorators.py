"""Flask decorator: require a valid admin HS256 JWT on a route."""

import logging
from functools import wraps
from typing import Any, Callable, Optional, TypedDict, TypeVar, cast

import jwt
from pamfilico_flask_core import standard_response

from pamfilico_admin_auth.config import DEFAULT_CONFIG, AdminAuthConfig
from pamfilico_admin_auth.jwt import get_raw_admin_bearer_from_request, verify_admin_jwt

logger = logging.getLogger(__name__)


class AdminAuthContext(TypedDict):
    sub: str
    role: str


F = TypeVar("F", bound=Callable[..., Any])


def admin_authenticate(
    _f: Optional[F] = None,
    *,
    config: AdminAuthConfig = DEFAULT_CONFIG,
) -> Any:
    """
    Require a valid admin HS256 JWT. Injects ``admin: AdminAuthContext`` into kwargs.

    Works both bare (``@admin_authenticate``) and parameterized
    (``@admin_authenticate(config=my_config)``).
    """

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            raw = get_raw_admin_bearer_from_request(config)
            if not raw:
                return standard_response(
                    data=None,
                    error=True,
                    ui_message="Admin authentication required",
                    status_code=401,
                )
            try:
                claims = verify_admin_jwt(raw, config)
            except jwt.ExpiredSignatureError:
                return standard_response(
                    data=None,
                    error=True,
                    ui_message="Admin token expired",
                    status_code=401,
                )
            except jwt.PyJWTError as e:
                logger.info("admin jwt invalid: %s", e)
                return standard_response(
                    data=None,
                    error=True,
                    ui_message="Invalid admin token",
                    status_code=401,
                )
            admin: AdminAuthContext = {"sub": claims.sub, "role": claims.role}
            kwargs["admin"] = admin
            return f(*args, **kwargs)

        return cast(F, wrapper)

    # Bare form: @admin_authenticate
    if callable(_f):
        return decorator(_f)
    # Parameterized form: @admin_authenticate(config=...)
    return decorator
