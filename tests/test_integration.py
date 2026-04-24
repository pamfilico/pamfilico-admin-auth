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
    body = r.json()
    assert body["error"] is True


@integration_required
def test_login_missing_fields():
    r = requests.post(f"{API_URL}/api/v1/admin/login", json={})
    assert r.status_code == 400


# ---- protected: /admin/users ----


@integration_required
def test_users_without_token_is_401():
    r = requests.get(f"{API_URL}/api/v1/admin/users")
    assert r.status_code == 401


@integration_required
def test_users_with_invalid_token_is_401():
    r = requests.get(
        f"{API_URL}/api/v1/admin/users", headers={"ADMIN-TOKEN": "garbage"}
    )
    assert r.status_code == 401


@integration_required
def test_users_list_default_pagination():
    token = _admin_token()
    r = requests.get(
        f"{API_URL}/api/v1/admin/users", headers={"ADMIN-TOKEN": token}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["error"] is False
    assert len(body["data"]) == 4
    assert body["pagination"]["currentPage"] == 1
    assert body["pagination"]["totalCount"] == 4


@integration_required
def test_users_list_with_page_size():
    token = _admin_token()
    r = requests.get(
        f"{API_URL}/api/v1/admin/users?currentPage=1&pageSize=2",
        headers={"ADMIN-TOKEN": token},
    )
    body = r.json()
    assert len(body["data"]) == 2
    assert body["pagination"]["pageSize"] == 2
    assert body["pagination"]["totalPages"] == 2
    assert body["pagination"]["nextPage"] == 2


@integration_required
def test_users_list_email_contains_filter():
    token = _admin_token()
    r = requests.get(
        f"{API_URL}/api/v1/admin/users?email_contains=example.com",
        headers={"ADMIN-TOKEN": token},
    )
    body = r.json()
    emails = {u["email"] for u in body["data"]}
    assert "alice@example.com" in emails
    assert "dave@elsewhere.org" not in emails


@integration_required
def test_users_list_bearer_header_works():
    token = _admin_token()
    r = requests.get(
        f"{API_URL}/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
