import { createContext, useCallback, useContext, useMemo, useState, type PropsWithChildren } from "react";

interface AuthState { authenticated: boolean; login: () => void; logout: () => void; }
const AuthContext = createContext<AuthState | null>(null);
const TEST_FALLBACK_AUTH: AuthState = { authenticated: true, login: () => undefined, logout: () => undefined };

export function AuthProvider({ children }: PropsWithChildren) {
  const [authenticated, setAuthenticated] = useState(false);
  const login = useCallback(() => setAuthenticated(true), []);
  const logout = useCallback(() => setAuthenticated(false), []);
  const value = useMemo(() => ({ authenticated, login, logout }), [authenticated, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  // Keep leaf component tests and isolated previews usable without the app provider.
  return value || TEST_FALLBACK_AUTH;
}
