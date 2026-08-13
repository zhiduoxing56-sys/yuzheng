import { useCallback, useEffect, useRef, useState } from "react";
import { listAuditRecords } from "../api/auditRecords";
import { AuditDetailDialog } from "../components/AuditDetailDialog";
import { AuditRecordTable } from "../components/AuditRecordTable";
import type { AuditRecordView } from "../types/visualModels";

type AuditLoadState = "loading" | "success" | "empty" | "error";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function requiredString(value: unknown, field: string): string {
  if (typeof value !== "string") throw new Error(`审计列表响应缺少 ${field}`);
  return value;
}

/** Maps only the frozen audit-list fields used by this page. */
function mapAuditRecords(payload: unknown): AuditRecordView[] {
  if (!isRecord(payload) || !Array.isArray(payload.items)) throw new Error("审计列表响应格式无效");

  return payload.items.map((item, index) => {
    if (!isRecord(item)) throw new Error(`审计列表第 ${index + 1} 条记录格式无效`);
    return {
      auditId: requiredString(item.audit_id, "audit_id"),
      createdAt: requiredString(item.created_at, "created_at"),
      rawCommand: requiredString(item.raw_command, "raw_command"),
      finalDecision: requiredString(item.final_decision, "final_decision"),
      executionStatus: requiredString(item.execution_status, "execution_status"),
      reviewOccurred: item.review_occurred === true,
    };
  });
}

export function AuditsPage() {
  const [records, setRecords] = useState<AuditRecordView[]>([]);
  const [loadState, setLoadState] = useState<AuditLoadState>("loading");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAuditId, setSelectedAuditId] = useState<string | null>(null);
  const activeControllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);
  const inFlightRef = useRef(false);
  const hasSuccessfulLoadRef = useRef(false);

  const loadAudits = useCallback(() => {
    if (inFlightRef.current) return;

    activeControllerRef.current?.abort();
    const controller = new AbortController();
    const requestId = ++requestIdRef.current;
    activeControllerRef.current = controller;
    inFlightRef.current = true;
    setLoading(true);
    setError(null);

    void listAuditRecords(controller.signal).then((payload) => {
      if (requestId !== requestIdRef.current) return;
      const nextRecords = mapAuditRecords(payload);
      hasSuccessfulLoadRef.current = true;
      setRecords(nextRecords);
      setLoadState(nextRecords.length ? "success" : "empty");
    }).catch((requestError: unknown) => {
      if (controller.signal.aborted || requestId !== requestIdRef.current) return;
      const message = requestError instanceof Error ? requestError.message : "审计列表加载失败";
      setError(message);
      if (!hasSuccessfulLoadRef.current) setLoadState("error");
    }).finally(() => {
      if (requestId !== requestIdRef.current) return;
      inFlightRef.current = false;
      activeControllerRef.current = null;
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    loadAudits();
    return () => {
      requestIdRef.current += 1;
      activeControllerRef.current?.abort();
      activeControllerRef.current = null;
      inFlightRef.current = false;
    };
  }, [loadAudits]);

  const handleRecordClick = useCallback((record: AuditRecordView) => setSelectedAuditId(record.auditId), []);

  return <div className="visual-page-frame audit-records-page">
    <header className="audit-records-header"><h1 className="visual-gradient-title">审计记录</h1><button type="button" className={loading ? "is-refreshing" : ""} aria-label="刷新审计记录" disabled={loading} onClick={loadAudits}>{loading ? "加载中" : "刷新"}</button></header>
    {loadState === "loading" && <p className="audit-records-status" role="status">正在加载审计记录…</p>}
    {loadState === "empty" && <p className="audit-records-status" role="status">暂无审计记录</p>}
    {loadState === "error" && <p className="audit-records-status is-error" role="alert">审计记录加载失败：{error || "请稍后重试"}</p>}
    {error && loadState !== "error" && <p className="audit-records-status is-error" role="alert">刷新失败：{error}</p>}
    {loadState !== "error" && <AuditRecordTable records={records} onRecordClick={handleRecordClick} />}
    <AuditDetailDialog auditId={selectedAuditId} onClose={() => setSelectedAuditId(null)} />
  </div>;
}
