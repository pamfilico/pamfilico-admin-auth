export {
  DEFAULT_STORAGE_KEY,
  sessionStorageAdapter,
  localStorageAdapter,
  getAdminToken,
  setAdminToken,
  clearAdminToken,
} from "./token";
export type { TokenStorage } from "./token";

export {
  DEFAULT_TOKEN_HEADER,
  DEFAULT_API_PREFIX,
  adminHeaders,
  adminFetch,
  adminLogin,
  adminListUsers,
} from "./fetch";
export type {
  AdminApiConfig,
  AdminResponse,
  AdminListUsersParams,
} from "./fetch";

export { AdminAuthProvider, useAdminAuth } from "./provider";
export type { AdminAuthProviderProps } from "./provider";

export { AdminProtectedRoute } from "./protected";
export type { AdminProtectedRouteProps } from "./protected";
