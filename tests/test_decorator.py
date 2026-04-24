"""Unit tests: @admin_authenticate decorator + build_admin_blueprint login route."""

import pytest
from flask import Flask
from pamfilico_flask_core import init_errors

from pamfilico_admin_auth import (
    AdminAuthConfig,
    AdminAuthContext,
    AdminJwtClaims,
    admin_authenticate,
    build_admin_blueprint,
    create_admin_jwt,
)


@pytest.fixture
def app():
    app = Flask(__name__)
    init_errors(app)

    @app.route("/protected")
    @admin_authenticate
    def protected(admin: AdminAuthContext):
        return {"sub": admin["sub"], "role": admin["role"]}, 200

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_missing_token_returns_401(client):
    resp = client.get("/protected")
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"] is True
    assert "authentication required" in body["ui_message"].lower()


def test_invalid_token_returns_401(client):
    resp = client.get("/protected", headers={"ADMIN-TOKEN": "not-a-real-jwt"})
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"] is True


def test_expired_token_returns_401(client):
    token = create_admin_jwt(AdminJwtClaims(sub="u", role="admin"), ttl_seconds=-10)
    resp = client.get("/protected", headers={"ADMIN-TOKEN": token})
    assert resp.status_code == 401
    body = resp.get_json()
    assert "expired" in body["ui_message"].lower()


def test_valid_token_admin_token_header(client):
    token = create_admin_jwt(AdminJwtClaims(sub="theadmin", role="admin"))
    resp = client.get("/protected", headers={"ADMIN-TOKEN": token})
    assert resp.status_code == 200
    assert resp.get_json() == {"sub": "theadmin", "role": "admin"}


def test_valid_token_authorization_bearer_header(client):
    token = create_admin_jwt(AdminJwtClaims(sub="theadmin", role="admin"))
    resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["sub"] == "theadmin"


# ---- build_admin_blueprint (login-only) ----


def _mount_login_app(config: AdminAuthConfig = None) -> Flask:
    app = Flask(__name__)
    init_errors(app)
    bp = build_admin_blueprint(config=config) if config else build_admin_blueprint()
    app.register_blueprint(bp, url_prefix="/api/v1/admin")
    return app


def test_login_disabled_when_credentials_unset(monkeypatch):
    """No baked-in defaults: login must 401 when env vars are blank."""
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    resp = _mount_login_app().test_client().post(
        "/api/v1/admin/login", json={"username": "", "password": ""}
    )
    assert resp.status_code == 401
    assert "not configured" in resp.get_json()["ui_message"].lower()


def test_login_works_with_explicit_config_defaults(monkeypatch):
    """Apps can opt into local-dev defaults via AdminAuthConfig, never from the package."""
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    cfg = AdminAuthConfig(default_username="devadmin", default_password="devpass")

    resp = _mount_login_app(cfg).test_client().post(
        "/api/v1/admin/login", json={"username": "devadmin", "password": "devpass"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["accessToken"]


def test_login_bad_credentials_returns_401():
    resp = _mount_login_app().test_client().post(
        "/api/v1/admin/login", json={"username": "theadmin", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_missing_fields_returns_400():
    resp = _mount_login_app().test_client().post("/api/v1/admin/login", json={})
    assert resp.status_code == 400
