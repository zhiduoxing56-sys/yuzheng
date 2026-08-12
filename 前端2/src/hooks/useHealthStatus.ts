import { useCallback, useEffect, useRef, useState } from "react";
import { getHealth } from "../api/system";
import { HEALTH_POLL_INTERVAL_MS } from "../constants";
import type { HealthResponse } from "../types/contract";

export function useHealthStatus() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<Date | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const refresh = useCallback(async () => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    try {
      const result = await getHealth(controller.signal);
      if (controller.signal.aborted) return;
      setData(result);
      setError(null);
      setLastUpdatedAt(new Date());
    } catch (reason) {
      if (controller.signal.aborted) return;
      setData(null);
      setError(reason instanceof Error ? reason.message : "后端服务不可用");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => { void refresh(); }, HEALTH_POLL_INTERVAL_MS);
    return () => {
      window.clearInterval(timer);
      controllerRef.current?.abort();
    };
  }, [refresh]);

  return {
    data,
    loading,
    error,
    lastUpdatedAt,
    available: data?.status === "ok" || data?.status === "healthy",
    refresh,
  };
}
