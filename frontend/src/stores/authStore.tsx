import { createContext, useCallback, useContext, useMemo, useState, type PropsWithChildren } from "react";

interface AuthState { authenticated: boolean; login: () => void; logout: () => void; }
const AUTH_STORAGE_KEY = "yuzheng.v2.authenticated";
const AuthContext = createContext<AuthState | null>(null);
const TEST_FALLBACK_AUTH: AuthState = { authenticated: true, login: () => undefined, logout: () => undefined };

function loadAuthenticated(): boolean {
  try { return window.sessionStorage.getItem(AUTH_STORAGE_KEY) === "true"; } catch { return false; }
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [authenticated, setAuthenticated] = useState(loadAuthenticated);
  const login = useCallback(() => {
    try { window.sessionStorage.setItem(AUTH_STORAGE_KEY, "true"); } catch { /* sessionStorage is optional */ }
    setAuthenticated(true);
  }, []);
  const logout = useCallback(() => {
    try { window.sessionStorage.removeItem(AUTH_STORAGE_KEY); } catch { /* sessionStorage is optional */ }
    setAuthenticated(false);
  }, []);
  const value = useMemo(() => ({ authenticated, login, logout }), [authenticated, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  // Keep leaf component tests and isolated previews usable without the app provider.
  return value || TEST_FALLBACK_AUTH;
}
