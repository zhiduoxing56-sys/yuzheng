import { NavLink, useLocation } from "react-router-dom";
import { useSession } from "../stores/sessionStore";
import { ConnectionStatus } from "./ConnectionStatus";
import { StatusBadge } from "./StatusBadge";

const primaryLinks = [
  { to: "/audits", label: "审计追踪" },
];

export function TopNav() {
  const { websocketStatus, sessionId, activeTurnId, newSession } = useSession();
  const location = useLocation();
  const realtimeEnabled = location.pathname === "/decision";
  return (
    <header className="top-nav">
      <div className="brand-lockup">
        <span className="brand-mark" aria-hidden="true">证</span>
        <div>
          <strong>语证</strong>
          <span>高风险车控指令裁决</span>
        </div>
      </div>
      <nav className="primary-nav" aria-label="主导航">
        <NavLink to="/decision" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>实时裁决</NavLink>
        <NavLink to={activeTurnId ? `/evidence/${encodeURIComponent(activeTurnId)}` : "/evidence"} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>分层证据</NavLink>
        {primaryLinks.map((link) => (
          <NavLink key={link.to} to={link.to} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            {link.label}
          </NavLink>
        ))}
        {activeTurnId ? <NavLink to={`/review/${encodeURIComponent(activeTurnId)}`} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>复核授权</NavLink> : <span className="nav-link" aria-disabled="true" title="提交指令后才可进入复核">复核授权</span>}
      </nav>
      <div className="nav-tools">
        {realtimeEnabled
          ? <ConnectionStatus status={websocketStatus} />
          : <StatusBadge label="当前页面未启用实时通道" tone="neutral" />}
        <details className="assist-menu">
          <summary>辅助菜单</summary>
          <div className="assist-menu-panel">
            <NavLink to="/demo">场景演示</NavLink>
            <NavLink to="/system">系统状态</NavLink>
            <button type="button" onClick={newSession}>新建会话</button>
            <small title={sessionId}>会话已保存</small>
          </div>
        </details>
      </div>
    </header>
  );
}
