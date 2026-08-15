import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell, VisualPageShell } from "./components/AppShell";
import { CarlaPage } from "./pages/CarlaPage";
import { DecisionPage } from "./pages/DecisionPage";
import { DemoPage } from "./pages/DemoPage";
import { SystemPage } from "./pages/SystemPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { LoginPage } from "./pages/LoginPage";
import { ProtectedRoute } from "./components/ProtectedRoute";

const EvidencePage = lazy(() => import("./pages/EvidencePage").then((module) => ({ default: module.EvidencePage })));
const ReviewPage = lazy(() => import("./pages/ReviewPage").then((module) => ({ default: module.ReviewPage })));
const AuditsPage = lazy(() => import("./pages/AuditsPage").then((module) => ({ default: module.AuditsPage })));
const AuditDetailPage = lazy(() => import("./pages/AuditDetailPage").then((module) => ({ default: module.AuditDetailPage })));

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/decision" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
      <Route element={<VisualPageShell />}>
        <Route path="/decision" element={<DecisionPage />} />
        <Route path="/evidence" element={<Suspense fallback={<div className="loading-state"><span className="loading-dot" />正在加载证据页面……</div>}><EvidencePage /></Suspense>} />
        <Route path="/evidence/:turnId" element={<Suspense fallback={<div className="loading-state"><span className="loading-dot" />正在加载证据页面……</div>}><EvidencePage /></Suspense>} />
        <Route path="/audits" element={<Suspense fallback={<div className="loading-state"><span className="loading-dot" />正在加载审计列表…</div>}><AuditsPage /></Suspense>} />
        <Route path="/carla" element={<CarlaPage />} />
      </Route>
      <Route element={<AppShell />}>
        <Route path="/review/:turnId" element={<Suspense fallback={<div className="loading-state"><span className="loading-dot" />正在加载复核页面……</div>}><ReviewPage /></Suspense>} />
        <Route path="/audits/:auditId" element={<Suspense fallback={<div className="loading-state"><span className="loading-dot" />正在加载审计详情…</div>}><AuditDetailPage /></Suspense>} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="/system" element={<SystemPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
