import type { PropsWithChildren } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { useHealthStatus } from "../hooks/useHealthStatus";
import { useSession } from "../stores/sessionStore";
import { StatusBadge } from "./StatusBadge";
import { TopNav } from "./TopNav";

function BackendHealthBadge() {
  const health = useHealthStatus();
  const label = health.loading
    ? "后端健康检查中"
    : health.available
      ? "后端健康"
      : "后端不可用";
  return <StatusBadge label={label} tone={health.available ? "success" : health.loading ? "warning" : "danger"} />;
}

export function AppShell({ children }: PropsWithChildren) {
  const { activeTurnId } = useSession();
  const location = useLocation();
  const realtimeEnabled = location.pathname === "/decision";
  return (
    <div className={`app-shell ${realtimeEnabled ? "decision-route-shell" : ""}`}>
      {realtimeEnabled
        ? <header className="decision-brand-bar"><strong>语证</strong></header>
        : <TopNav />}
      {!realtimeEnabled && <div className="shell-meta">
        <span>当前可写轮次：{activeTurnId || "尚未创建轮次"}</span>
        <BackendHealthBadge />
      </div>}
      <main className={realtimeEnabled ? "decision-page-content" : "page-content"}>{children || <Outlet />}</main>
    </div>
  );
}
