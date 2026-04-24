"""Shared pytest fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_admin_env(monkeypatch):
    """
    Pin admin env vars per-test so they don't leak between tests. Individual tests
    can still override by calling monkeypatch.setenv themselves.
    """
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-secret-key-for-pamfilico-admin-auth")
    monkeypatch.setenv("ADMIN_USERNAME", "theadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "thepassword")
    yield
