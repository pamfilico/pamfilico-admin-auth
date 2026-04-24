/**
 * Pluggable token storage. Defaults to sessionStorage (session-scoped, cleared on tab
 * close — matches the bugbeamio behavior). Swap in localStorageAdapter for persistent
 * login across browser restarts.
 */

export interface TokenStorage {
  get(): string | null;
  set(token: string): void;
  clear(): void;
}

export const DEFAULT_STORAGE_KEY = "pamfilico_admin_jwt";

export function sessionStorageAdapter(key: string = DEFAULT_STORAGE_KEY): TokenStorage {
  return {
    get() {
      if (typeof window === "undefined") return null;
      return window.sessionStorage.getItem(key);
    },
    set(token) {
      if (typeof window === "undefined") return;
      window.sessionStorage.setItem(key, token);
    },
    clear() {
      if (typeof window === "undefined") return;
      window.sessionStorage.removeItem(key);
    },
  };
}

export function localStorageAdapter(key: string = DEFAULT_STORAGE_KEY): TokenStorage {
  return {
    get() {
      if (typeof window === "undefined") return null;
      return window.localStorage.getItem(key);
    },
    set(token) {
      if (typeof window === "undefined") return;
      window.localStorage.setItem(key, token);
    },
    clear() {
      if (typeof window === "undefined") return;
      window.localStorage.removeItem(key);
    },
  };
}

/** Convenience: default session-scoped storage under the default key. */
const defaultStorage = sessionStorageAdapter();

export function getAdminToken(): string | null {
  return defaultStorage.get();
}

export function setAdminToken(token: string): void {
  defaultStorage.set(token);
}

export function clearAdminToken(): void {
  defaultStorage.clear();
}
