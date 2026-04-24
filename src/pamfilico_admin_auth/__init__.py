"""pamfilico-admin-auth - HS256 JWT admin auth for Flask + React apps.

Scope: authentication primitives only. Login route, JWT helpers, the
``@admin_authenticate`` decorator. User management / admin CRUD / broadcast and
other admin features are the consuming app's responsibility — protect them with
the decorator and wire them up however fits.
"""

from pamfilico_admin_auth.config import AdminAuthConfig
from pamfilico_admin_auth.jwt import (
    ADMIN_TOKEN_HEADER,
    AdminJwtClaims,
    create_admin_jwt,
    get_raw_admin_bearer_from_request,
    verify_admin_jwt,
)
from pamfilico_admin_auth.decorators import (
    AdminAuthContext,
    admin_authenticate,
)
from pamfilico_admin_auth.blueprint import build_admin_blueprint

__all__ = [
    "ADMIN_TOKEN_HEADER",
    "AdminAuthConfig",
    "AdminAuthContext",
    "AdminJwtClaims",
    "admin_authenticate",
    "build_admin_blueprint",
    "create_admin_jwt",
    "get_raw_admin_bearer_from_request",
    "verify_admin_jwt",
]
