"""Unit tests: HS256 token creation, verification, tampering, header extraction."""

import jwt
import pytest
from flask import Flask

from pamfilico_admin_auth.jwt import (
    AdminJwtClaims,
    admin_jwt_secret,
    create_admin_jwt,
    get_raw_admin_bearer_from_request,
    verify_admin_jwt,
)


def test_create_and_verify_admin_jwt_roundtrip():
    token = create_admin_jwt(AdminJwtClaims(sub="theadmin", role="admin"), ttl_seconds=60)
    assert isinstance(token, str) and len(token) > 20
    claims = verify_admin_jwt(token)
    assert claims.sub == "theadmin"
    assert claims.role == "admin"


def test_verify_rejects_tampered_token():
    t = create_admin_jwt(AdminJwtClaims(sub="a", role="admin"))
    t2 = t[:-5] + "xxxxx"
    with pytest.raises(jwt.PyJWTError):
        verify_admin_jwt(t2)


def test_verify_rejects_empty_token():
    with pytest.raises(jwt.PyJWTError):
        verify_admin_jwt("")


def test_verify_rejects_wrong_role(monkeypatch):
    """A token minted with role != 'admin' must fail validation."""
    token = create_admin_jwt(AdminJwtClaims(sub="u", role="staff"))
    with pytest.raises(jwt.PyJWTError):
        verify_admin_jwt(token)


def test_verify_rejects_expired_token(monkeypatch):
    token = create_admin_jwt(AdminJwtClaims(sub="u", role="admin"), ttl_seconds=-10)
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_admin_jwt(token)


def test_secret_is_stable_within_process(monkeypatch):
    monkeypatch.delenv("ADMIN_JWT_SECRET", raising=False)
    assert admin_jwt_secret() == admin_jwt_secret()


def test_get_raw_bearer_from_admin_token_header():
    app = Flask(__name__)
    with app.test_request_context("/t", headers={"ADMIN-TOKEN": "abc123"}):
        assert get_raw_admin_bearer_from_request() == "abc123"


def test_get_raw_bearer_from_authorization_header():
    app = Flask(__name__)
    with app.test_request_context("/t", headers={"Authorization": "Bearer  xyz9"}):
        assert get_raw_admin_bearer_from_request() == "xyz9"


def test_get_raw_bearer_returns_none_when_absent():
    app = Flask(__name__)
    with app.test_request_context("/t"):
        assert get_raw_admin_bearer_from_request() is None
