# pamfilico-admin-auth

**Scope: admin authentication. Not user management.** Login route + JWT verification +
a Flask decorator + React primitives. User lists, admin CRUD, dashboards — those are
the consuming app's job; protect them with `@admin_authenticate` and move on.

- **Python / Flask** — `@admin_authenticate` decorator, `build_admin_blueprint`
  (exposes `POST /login` only), JWT helpers. Depends on
  [`pamfilico-flask-core`](https://github.com/pamfilico/flask-core) for the response
  envelope and error handlers.
- **React / Next.js** — `<AdminAuthProvider>`, `useAdminAuth()`,
  `<AdminProtectedRoute>`, `adminFetch`, pluggable `sessionStorage` /
  `localStorage` token adapters.

Extracted from the near-identical admin auth flows in bugbeamio, carfast, tourfast
and boatfast.

## Quickstart — Backend

```python
# app/__init__.py
from flask import Flask
from pamfilico_flask_core import init_errors
from pamfilico_admin_auth import build_admin_blueprint

app = Flask(__name__)
init_errors(app)
app.register_blueprint(build_admin_blueprint(), url_prefix="/api/v1/admin")
```

```python
# any app-specific protected route
from pamfilico_admin_auth import admin_authenticate, AdminAuthContext

@app.route("/api/v1/admin/users")
@admin_authenticate
def list_users(admin: AdminAuthContext):
    # your app, your model, your serializer
    ...
```

### Environment variables

| Var | Purpose | Default |
|---|---|---|
| `ADMIN_JWT_SECRET` | HS256 signing key. **Set in production.** | dev-only fallback (with warning) |
| `ADMIN_USERNAME` | Login username | **unset → login disabled** |
| `ADMIN_PASSWORD` | Login password | **unset → login disabled** |

No baked-in credentials: `POST /admin/login` returns
`401 "Admin login is not configured"` when either env var is unset. Dev-mode
defaults are opt-in via `AdminAuthConfig(default_username=..., default_password=...)`.

Override env var names, token header, or TTL via `AdminAuthConfig` — useful for
tourfast's `TOURFAST_ADMIN_TOKEN` or apps that already ship a `JWT_SECRET_KEY`.

## Quickstart — Frontend (React / Next.js)

Install:

```bash
npm install github:pamfilico/pamfilico-admin-auth
```

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
      if (r.ok) router.replace("/admin");
    }}>
      <input value={u} onChange={(e) => setU(e.target.value)} />
      <input value={p} onChange={(e) => setP(e.target.value)} type="password" />
      <button>Sign in</button>
    </form>
  );
}
```

Use `adminFetch(apiConfig, path, init, token)` for any protected admin endpoint the
app defines. Swap `sessionStorageAdapter` for `localStorageAdapter` to persist across
tab reopen.

## Tests

Mirrors the `flask-collection` pattern: containerized integration stack **and**
host-runnable unit tests.

```bash
# Unit tests only (no docker)
poetry install
poetry run pytest tests/test_jwt.py tests/test_decorator.py -v

# Full integration (docker compose: just the Flask test backend)
./run-tests.sh

# Also boot the Next.js test frontend (for manual browser testing / Playwright)
RUN_FRONTEND=1 ./run-tests.sh
```

## Package layout

```
pamfilico-admin-auth/
├── src/pamfilico_admin_auth/   # Python package (auth only)
├── js/                         # @pamfilico/admin-auth-react source
├── tests/                      # pytest (unit + HTTP integration)
├── test-frontend/              # minimal Next.js demo app
├── package.json                # npm manifest at root → installable via github:
├── tsconfig.json               # tsc builds js/src → js/dist (runs on install via prepare)
├── Dockerfile.test             # test backend image
├── docker-compose.test.yml     # api (+ optional frontend)
└── run-tests.sh                # orchestrator
```

## License

MIT
