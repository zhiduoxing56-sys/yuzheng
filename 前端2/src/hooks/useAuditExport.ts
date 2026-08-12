import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../api/client";
import { exportAudit } from "../api/audits";
import { safeAuditExportFilename, sanitizeAuditExport } from "../utils/auditSanitizer";

export function useAuditExport(auditId: string | null) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadedAt, setDownloadedAt] = useState<Date | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    controllerRef.current?.abort();
    setLoading(false);
    setError(null);
    setDownloadedAt(null);
    return () => controllerRef.current?.abort();
  }, [auditId]);

  const download = useCallback(async () => {
    if (!auditId || loading) return;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    setError(null);
    try {
      const received = await exportAudit(auditId, controller.signal);
      if (controller.signal.aborted) return;
      const protectedPayload = sanitizeAuditExport(received);
      const blob = new Blob([JSON.stringify(protectedPayload, null, 2)], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = safeAuditExportFilename(auditId);
      link.click();
      URL.revokeObjectURL(url);
      setDownloadedAt(new Date());
    } catch (reason) {
      if (controller.signal.aborted || reason instanceof ApiError && reason.kind === "CANCELLED") return;
      setError(reason instanceof Error ? reason.message : "审计导出失败");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }, [auditId, loading]);

  return { loading, error, downloadedAt, download };
}
