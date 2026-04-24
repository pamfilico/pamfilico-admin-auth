"""Configuration for admin auth — env var names, header name, token TTL."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdminAuthConfig:
    """
    Per-app configuration for admin auth.

    All fields have sensible defaults matching the original bugbeamio layout. Override
    `jwt_secret_env` / `token_header` when an app uses app-specific naming
    (e.g. tourfast uses `TOURFAST_ADMIN_TOKEN`).
    """

    jwt_secret_env: str = "ADMIN_JWT_SECRET"
    username_env: str = "ADMIN_USERNAME"
    password_env: str = "ADMIN_PASSWORD"
    token_header: str = "ADMIN-TOKEN"
    token_ttl_seconds: int = 86400  # 24 hours
    # No default credentials are shipped. If ADMIN_USERNAME / ADMIN_PASSWORD are unset,
    # login is disabled entirely — any login attempt returns 401. Apps that want a
    # dev-mode default should construct AdminAuthConfig with explicit values (they are
    # intentionally opt-in, never baked into the package).
    default_username: str = ""
    default_password: str = ""
    # Dev-only fallback for the JWT signing key. Production deployments MUST set the
    # env var. Kept non-empty so `verify_admin_jwt` never silently accepts unsigned
    # tokens when the env var is missing.
    default_dev_jwt_secret: str = "pamfilico-admin-jwt-devenv-insecure"


DEFAULT_CONFIG = AdminAuthConfig()
