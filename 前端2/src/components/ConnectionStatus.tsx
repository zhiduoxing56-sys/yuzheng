import type { ConnectionStatus } from "../types/contract";
import { StatusBadge } from "./StatusBadge";

const labels: Record<ConnectionStatus, string> = {
  disconnected: "已断开",
  connecting: "正在连接",
  connected: "已连接",
  reconnecting: "正在重连",
  failed: "连接失败",
};

export function ConnectionStatus({ status }: { status: ConnectionStatus }) {
  const tone = status === "connected" ? "success" : status === "reconnecting" || status === "connecting" ? "warning" : status === "failed" ? "danger" : "neutral";
  return <StatusBadge label={`实时 ${labels[status]}`} tone={tone} />;
}
