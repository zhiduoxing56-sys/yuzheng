import { useCallback, useEffect, useRef, useState } from "react";
import { getVehicleState } from "../api/system";
import type { VehicleState } from "../types/contract";

export function useVehicleState(refreshKey?: string | null) {
  const [data, setData] = useState<VehicleState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const refresh = useCallback(async () => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    try {
      const result = await getVehicleState(controller.signal);
      if (controller.signal.aborted) return;
      setData(result);
      setError(null);
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "车辆状态加载失败");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    return () => controllerRef.current?.abort();
  }, [refresh, refreshKey]);

  return { data, loading, error, refresh };
}
