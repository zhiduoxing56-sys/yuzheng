import { Outlet } from "react-router-dom";
import { useHealthStatus } from "../hooks/useHealthStatus";
import { useSession } from "../stores/sessionStore";
import { StatusBadge } from "./StatusBadge";
import { TopNav } from "./TopNav";
import { VisualPageNav } from "./VisualPageNav";

function BackendHealthBadge() {
  const health = useHealthStatus();
  const label = health.loading
    ? "后端健康检查中"
    : health.available
      ? "后端健康"
      : "后端不可用";
  return <StatusBadge label={label} tone={health.available ? "success" : health.loading ? "warning" : "danger"} />;
}

export function VisualPageShell() {
  return <main className="visual-page-content">
    <VisualPageNav />
    <Outlet />
  </main>;
}

export function AppShell() {
  const { activeTurnId } = useSession();
  return (
    <div className="app-shell">
      <TopNav />
      <div className="shell-meta">
        <span>当前可写轮次：{activeTurnId || "尚未创建轮次"}</span>
        <BackendHealthBadge />
      </div>
      <main className="page-content"><Outlet /></main>
    </div>
  );
}
