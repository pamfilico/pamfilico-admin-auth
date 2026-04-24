"""Minimal Flask test server for pamfilico-admin-auth integration tests.

Exposes:
  GET  /health
  POST /api/v1/admin/login           (from build_admin_blueprint)
  GET  /api/v1/admin/whoami          (app-specific, protected via @admin_authenticate)

The /whoami route exists only to prove the decorator works end-to-end — the package
itself has no opinion on what protected routes an app ships.
"""

import os

from flask import Flask
from pamfilico_flask_core import init_errors

from pamfilico_admin_auth import (
    AdminAuthContext,
    admin_authenticate,
    build_admin_blueprint,
)

app = Flask(__name__)
init_errors(app)


@app.route("/health")
def health():
    return {"status": "ok"}


app.register_blueprint(build_admin_blueprint(), url_prefix="/api/v1/admin")


@app.route("/api/v1/admin/whoami", methods=["GET"])
@admin_authenticate
def admin_whoami(admin: AdminAuthContext):
    return {
        "success": True,
        "error": False,
        "data": {"sub": admin["sub"], "role": admin["role"]},
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
