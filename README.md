# pamfilico-admin-auth

Reusable admin auth for Pamfilico apps. Provides:

- **Python / Flask** — `@admin_authenticate` decorator + `build_admin_blueprint`
  factory. HS256 JWT, credentials from env vars, no admin DB table required.
- **React / Next.js** — `<AdminAuthProvider>`, `useAdminAuth()`,
  `<AdminProtectedRoute>`, typed `adminLogin` / `adminListUsers` helpers.

Extracted from the near-identical admin auth flows in bugbeamio, carfast, tourfast and
boatfast. Depends on [`pamfilico-flask-core`](https://github.com/pamfilico/flask-core)
for the response envelope and error handlers.

## Quickstart — Backend

```python
# app/__init__.py
from flask import Flask
from pamfilico_flask_core import init_errors
from pamfilico_admin_auth import build_admin_blueprint

from app.database.engine import DBsession   # your sessionmaker
from app.database.models import User        # your User model

app = Flask(__name__)
init_errors(app)

app.register_blueprint(
    build_admin_blueprint(user_model=User, get_db_session=DBsession),
    url_prefix="/api/v1",
)
```

```python
# Any protected route
from pamfilico_admin_auth import admin_authenticate, AdminAuthContext

@app.route("/api/v1/admin/reports")
@admin_authenticate
def reports(admin: AdminAuthContext):
    return {"sub": admin["sub"]}
```

### Environment variables

| Var | Purpose | Default |
|---|---|---|
| `ADMIN_JWT_SECRET` | HS256 signing key. **Set this in production.** | dev-only fallback (with warning) |
| `ADMIN_USERNAME` | Login username | **unset → login disabled** |
| `ADMIN_PASSWORD` | Login password | **unset → login disabled** |

If either `ADMIN_USERNAME` or `ADMIN_PASSWORD` is unset, the `POST /admin/login`
route responds `401 "Admin login is not configured"` — there are no baked-in
credentials. Apps that want a local dev default should set the env vars in
their local `.env` or pass an explicit `AdminAuthConfig(default_username=..., default_password=...)`.

Override via `AdminAuthConfig(jwt_secret_env="MY_SECRET", token_header="MY-APP-ADMIN-TOKEN", ...)`
when an app already uses app-specific names (e.g. tourfast's `TOURFAST_ADMIN_TOKEN`).

### Routes registered by `build_admin_blueprint`

- `POST /admin/login` — body `{username, password}` → `{data: {accessToken, tokenType, expiresIn}}`
- `GET  /admin/users?currentPage=1&pageSize=20&email_contains=` — paginated user list (protected)

## Quickstart — Frontend (React / Next.js)

```tsx
// app/admin/layout.tsx
"use client";
import { AdminAuthProvider } from "@pamfilico/admin-auth-react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminAuthProvider apiConfig={{ backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL! }}>
      {children}
    </AdminAuthProvider>
  );
}
```

```tsx
// app/admin/login/page.tsx
"use client";
import { useAdminAuth } from "@pamfilico/admin-auth-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Login() {
  const { login } = useAdminAuth();
  const router = useRouter();
  const [u, setU] = useState(""); const [p, setP] = useState("");
  return (
    <form onSubmit={async (e) => {
      e.preventDefault();
      const r = await login(u, p);
      if (r.ok) router.replace("/admin/users");
    }}>
      <input value={u} onChange={(e) => setU(e.target.value)} />
      <input value={p} onChange={(e) => setP(e.target.value)} type="password" />
      <button>Sign in</button>
    </form>
  );
}
```

Swap `sessionStorageAdapter` for `localStorageAdapter` (both exported) to persist the
token across tab reopen.

## Tests

Mirrors the `flask-collection` pattern: containerized integration stack **and**
host-runnable unit tests.

```bash
# Unit tests only (no docker)
poetry install
poetry run pytest tests/test_jwt.py tests/test_decorator.py -v

# Full integration (docker compose: Postgres + Flask test backend)
./run-tests.sh

# Also boot the Next.js test frontend (for manual browser testing / Playwright)
RUN_FRONTEND=1 ./run-tests.sh
```

## Package layout

```
pamfilico-admin-auth/
├── src/pamfilico_admin_auth/   # Python package
├── js/                         # @pamfilico/admin-auth-react source
├── tests/                      # pytest (unit + HTTP integration)
├── test-frontend/              # minimal Next.js demo app
├── Dockerfile.test             # test backend image
├── docker-compose.test.yml     # db + api (+ optional frontend)
└── run-tests.sh                # orchestrator
```

## License

MIT
