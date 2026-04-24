/**
 * Low-level fetch wrapper + typed API helpers. Matches the bugbeamio response envelope
 * (`{ data, pagination?, ui_message?, error? }`) but doesn't require it.
 */

export const DEFAULT_TOKEN_HEADER = "ADMIN-TOKEN";
export const DEFAULT_API_PREFIX = "/api/v1";

export interface AdminApiConfig {
  /** Backend origin, e.g. `http://localhost:5000`. No trailing slash required. */
  backendUrl: string;
  /** Path prefix prepended to all admin routes. Defaults to `/api/v1`. */
  apiPrefix?: string;
  /** Name of the HTTP header that carries the admin token. */
  tokenHeader?: string;
}

export interface AdminResponse<T = unknown> {
  ok: boolean;
  status: number;
  data: T;
}

function joinUrl(cfg: AdminApiConfig, path: string): string {
  const base = cfg.backendUrl.replace(/\/$/, "");
  const prefix = (cfg.apiPrefix ?? DEFAULT_API_PREFIX).replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}${prefix}${p}`;
}

export function adminHeaders(
  token: string | null,
  cfg: AdminApiConfig,
): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (token) h[cfg.tokenHeader ?? DEFAULT_TOKEN_HEADER] = token;
  return h;
}

export async function adminFetch<T = unknown>(
  cfg: AdminApiConfig,
  path: string,
  init: RequestInit = {},
  token: string | null = null,
): Promise<AdminResponse<T>> {
  const headers: Record<string, string> = {
    ...(adminHeaders(token, cfg) as Record<string, string>),
    ...((init.headers as Record<string, string>) ?? {}),
  };
  const r = await fetch(joinUrl(cfg, path), { ...init, headers });
  let body: unknown = {};
  try {
    body = await r.json();
  } catch {
    body = {};
  }
  return { ok: r.ok, status: r.status, data: body as T };
}

// ---------- typed helpers ----------
// Only auth-related endpoints live here. App-specific admin calls (users, broadcasts,
// reports, etc.) belong in the consuming app — use `adminFetch` directly for those.

export async function adminLogin(
  cfg: AdminApiConfig,
  body: { username: string; password: string },
) {
  return adminFetch(cfg, "/admin/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
