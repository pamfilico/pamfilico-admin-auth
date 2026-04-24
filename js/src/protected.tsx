"use client";

/**
 * AdminProtectedRoute — wraps a subtree, redirects unauthenticated users to a login
 * URL (default `/admin/login`). Renders a fallback while hydrating from storage.
 *
 * Framework-agnostic: takes an imperative `redirect` callback so you can plug in
 * Next's `router.replace`, React Router's `navigate`, or `window.location.assign`.
 */

import React, { useEffect } from "react";

import { useAdminAuth } from "./provider";

export interface AdminProtectedRouteProps {
  children: React.ReactNode;
  /** Called with the login path when the user is unauthenticated. Required. */
  redirect: (loginPath: string) => void;
  /** Path to redirect to. Defaults to `/admin/login`. */
  loginPath?: string;
  /** Rendered while the provider hydrates token state from storage. */
  fallback?: React.ReactNode;
}

export function AdminProtectedRoute({
  children,
  redirect,
  loginPath = "/admin/login",
  fallback = null,
}: AdminProtectedRouteProps) {
  const { isAuthenticated, isReady } = useAdminAuth();

  useEffect(() => {
    if (isReady && !isAuthenticated) redirect(loginPath);
  }, [isReady, isAuthenticated, redirect, loginPath]);

  if (!isReady || !isAuthenticated) return <>{fallback}</>;
  return <>{children}</>;
}
