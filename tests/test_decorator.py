"""Unit tests: @admin_authenticate decorator behavior against a minimal Flask app."""

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


class _FakeUser:
    __tablename__ = "users"
    id = None
    email = None
    created_at = None
    last_updated = None


class _FakeSession:
    def __call__(self):
        return self

    def query(self, *_args, **_kw):
        class _Q:
            def filter(self, *_a, **_k):
                return self

            def order_by(self, *_a, **_k):
                return self

            def offset(self, *_a, **_k):
                return self

            def limit(self, *_a, **_k):
                return self

            def count(self):
                return 0

            def all(self):
                return []

        return _Q()

    def close(self):
        pass


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


def test_login_disabled_when_credentials_unset(monkeypatch):
    """No baked-in defaults: login must 401 when env vars are blank."""
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    app = Flask(__name__)
    init_errors(app)
    app.register_blueprint(
        build_admin_blueprint(user_model=_FakeUser, get_db_session=_FakeSession()),
        url_prefix="/api/v1/admin",
    )

    resp = app.test_client().post(
        "/api/v1/admin/login", json={"username": "", "password": ""}
    )
    assert resp.status_code == 401
    assert "not configured" in resp.get_json()["ui_message"].lower()


def test_login_works_with_explicit_config_defaults(monkeypatch):
    """Apps can opt into local-dev defaults via AdminAuthConfig, never from the package."""
    # Conftest sets ADMIN_USERNAME / ADMIN_PASSWORD; clear them so the config defaults
    # are what actually get used here.
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    cfg = AdminAuthConfig(default_username="devadmin", default_password="devpass")

    app = Flask(__name__)
    init_errors(app)
    app.register_blueprint(
        build_admin_blueprint(
            user_model=_FakeUser, get_db_session=_FakeSession(), config=cfg
        ),
        url_prefix="/api/v1/admin",
    )

    resp = app.test_client().post(
        "/api/v1/admin/login", json={"username": "devadmin", "password": "devpass"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["accessToken"]
