"use client";

/**
 * AdminAuthProvider — React Context that exposes token state + login/logout helpers.
 *
 * Wrap your admin tree with this provider (configure the backend URL once) and then
 * use the `useAdminAuth()` hook inside pages to read `token`, call `login()`, etc.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import type { AdminApiConfig } from "./fetch";
import { adminLogin } from "./fetch";
import type { TokenStorage } from "./token";
import { sessionStorageAdapter } from "./token";

export interface AdminAuthProviderProps {
  children: React.ReactNode;
  /** Backend config — required so the provider can issue login requests. */
  apiConfig: AdminApiConfig;
  /** Token storage backend. Defaults to session storage. */
  storage?: TokenStorage;
}

interface AdminAuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  isReady: boolean;
  login: (
    username: string,
    password: string,
  ) => Promise<{ ok: boolean; status: number; message?: string }>;
  logout: () => void;
  apiConfig: AdminApiConfig;
}

const AdminAuthContext = createContext<AdminAuthContextValue | null>(null);

export function AdminAuthProvider({
  children,
  apiConfig,
  storage,
}: AdminAuthProviderProps) {
  const store = useMemo<TokenStorage>(
    () => storage ?? sessionStorageAdapter(),
    [storage],
  );

  const [token, setToken] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  // Hydrate from storage on mount (client-only).
  useEffect(() => {
    setToken(store.get());
    setIsReady(true);
  }, [store]);

  const login = useCallback(
    async (username: string, password: string) => {
      const resp = await adminLogin(apiConfig, { username, password });
      const body = resp.data as
        | { data?: { accessToken?: string }; ui_message?: string }
        | undefined;
      const t = body?.data?.accessToken;
      if (resp.ok && t) {
        store.set(t);
        setToken(t);
        return { ok: true, status: resp.status };
      }
      return {
        ok: false,
        status: resp.status,
        message: body?.ui_message ?? "Login failed",
      };
    },
    [apiConfig, store],
  );

  const logout = useCallback(() => {
    store.clear();
    setToken(null);
  }, [store]);

  const value = useMemo<AdminAuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      isReady,
      login,
      logout,
      apiConfig,
    }),
    [token, isReady, login, logout, apiConfig],
  );

  return (
    <AdminAuthContext.Provider value={value}>{children}</AdminAuthContext.Provider>
  );
}

export function useAdminAuth(): AdminAuthContextValue {
  const ctx = useContext(AdminAuthContext);
  if (!ctx) {
    throw new Error("useAdminAuth must be used inside <AdminAuthProvider>");
  }
  return ctx;
}
