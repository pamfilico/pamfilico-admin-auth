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
    default_username: str = "theadmin"
    default_password: str = "thepassword"
    # Dev-only fallback. Production deployments MUST set the env var.
    default_dev_jwt_secret: str = "pamfilico-admin-jwt-devenv-insecure"


DEFAULT_CONFIG = AdminAuthConfig()
