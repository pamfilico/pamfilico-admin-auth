"""Unit tests: @admin_authenticate decorator behavior against a minimal Flask app."""

import json

import pytest
from flask import Flask
from pamfilico_flask_core import init_errors

from pamfilico_admin_auth import (
    AdminAuthContext,
    AdminJwtClaims,
    admin_authenticate,
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
