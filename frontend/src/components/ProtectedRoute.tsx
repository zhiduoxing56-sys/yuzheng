import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../stores/authStore";

export function ProtectedRoute() {
  const { authenticated } = useAuth();
  const location = useLocation();
  if (!authenticated) return <Navigate to="/login" replace state={{ from: `${location.pathname}${location.search}` }} />;
  return <Outlet />;
}
