"""Integration tests (require docker compose test stack up).

Skip gracefully if the API isn't reachable so host-only pytest doesn't fail.
"""

import os

import pytest
import requests

API_URL = os.environ.get("ADMIN_AUTH_TEST_API_URL", "http://localhost:5098")


def _api_available() -> bool:
    try:
        return requests.get(f"{API_URL}/health", timeout=2).status_code == 200
    except Exception:
        return False


integration_required = pytest.mark.skipif(
    not _api_available(), reason="API required — run ./run-tests.sh"
)


def _admin_token() -> str:
    r = requests.post(
        f"{API_URL}/api/v1/admin/login",
        json={"username": "theadmin", "password": "thepassword"},
        timeout=5,
    )
    assert r.status_code == 200, r.text
    return r.json()["data"]["accessToken"]


# ---- login ----


@integration_required
def test_login_success():
    r = requests.post(
        f"{API_URL}/api/v1/admin/login",
        json={"username": "theadmin", "password": "thepassword"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["error"] is False
    assert body["data"]["accessToken"]
    assert body["data"]["tokenType"] == "Bearer"
    assert body["data"]["expiresIn"] == 86400


@integration_required
def test_login_bad_credentials():
    r = requests.post(
        f"{API_URL}/api/v1/admin/login",
        json={"username": "theadmin", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json()["error"] is True


@integration_required
def test_login_missing_fields():
    r = requests.post(f"{API_URL}/api/v1/admin/login", json={})
    assert r.status_code == 400


# ---- @admin_authenticate end-to-end ----


@integration_required
def test_protected_without_token_is_401():
    r = requests.get(f"{API_URL}/api/v1/admin/whoami")
    assert r.status_code == 401


@integration_required
def test_protected_with_invalid_token_is_401():
    r = requests.get(
        f"{API_URL}/api/v1/admin/whoami", headers={"ADMIN-TOKEN": "garbage"}
    )
    assert r.status_code == 401


@integration_required
def test_protected_with_valid_admin_token_header():
    token = _admin_token()
    r = requests.get(
        f"{API_URL}/api/v1/admin/whoami", headers={"ADMIN-TOKEN": token}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["sub"] == "theadmin"
    assert body["data"]["role"] == "admin"


@integration_required
def test_protected_with_bearer_header():
    token = _admin_token()
    r = requests.get(
        f"{API_URL}/api/v1/admin/whoami",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
