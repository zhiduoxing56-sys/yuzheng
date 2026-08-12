import type { ApiErrorKind } from "../api/client";
import type { HealthResponse, TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";

export interface ExecutionEligibility {
  allowed: boolean;
  reasons: string[];
}

export function getExecutionEligibility(options: {
  turnId: string;
  presentation: TurnPresentationResponse | null;
  workflow: TurnWorkflowStatus | null;
  hasAuthorizationToken: boolean;
  writeBusy: boolean;
}): ExecutionEligibility {
  const { turnId, presentation, workflow, hasAuthorizationToken, writeBusy } = options;
  const reasons: string[] = [];
  if (!presentation || !workflow) return { allowed: false, reasons: ["后端状态尚未加载完整"] };
  if (workflow.current_turn_id !== turnId || presentation.turn_id !== turnId) reasons.push("当前地址不是工作流最新轮次");
  if (workflow.terminal) reasons.push("工作流已结束");
  if (workflow.status !== "AUTHORIZED") reasons.push("工作流尚未明确授权执行");
  if (workflow.token_status !== "ISSUED") reasons.push("授权令牌状态不是已签发");
  if (!presentation.authorization.token_issued) reasons.push("后端未记录授权签发");
  if (presentation.authorization.token_status !== "ISSUED") reasons.push("授权状态不可执行");
  if (!presentation.authorization.execution_allowed) reasons.push("后端未允许执行");
  if (presentation.authorization.consumed) reasons.push("授权已经使用");
  if (presentation.execution.execution_status !== "NOT_EXECUTED") reasons.push("当前轮次已有执行结果");
  if (!hasAuthorizationToken) reasons.push("本页面没有可恢复的一次性授权令牌");
  if (writeBusy) reasons.push("当前有写请求正在处理");
  return { allowed: reasons.length === 0, reasons };
}

export function executionEnvironmentLabel(health: HealthResponse | null): string {
  const adapterName = health?.vehicle_adapter;
  const adapter = adapterName?.toLowerCase();
  if (!adapter || !adapterName) return "后端未提供执行环境信息";
  if (adapter.includes("simulator")) return "仿真模式";
  if (adapter.includes("bench")) return "车机台架模式";
  if (adapter === "can" || adapter.includes("vehicle")) return "车辆接入模式";
  return `未知模式（${adapterName}）`;
}

export function executionStatusLabel(value?: string | null): string {
  const labels: Record<string, string> = {
    NOT_EXECUTED: "尚未执行",
    PENDING: "等待执行",
    EXECUTING: "正在执行",
    SUCCEEDED: "执行成功",
    FAILED: "执行失败",
    UNCERTAIN: "结果待确认",
  };
  return value ? labels[value] || value : "尚未执行";
}

export function requiresExecutionReconciliation(kind?: ApiErrorKind): boolean {
  return kind === "TIMEOUT" || kind === "NETWORK_UNAVAILABLE";
}

export function redactAuthorizationToken(message: string, authorizationToken?: string | null): string {
  return authorizationToken && message.includes(authorizationToken)
    ? message.split(authorizationToken).join("[授权信息已脱敏]")
    : message;
}
