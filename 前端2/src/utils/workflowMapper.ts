import type { AuthorizationTokenStatus, TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";

const workflowLabels: Record<string, string> = {
  REVIEW_REQUIRED: "等待人工复核",
  AUTHORIZED: "授权已签发",
  EXECUTED: "执行完成",
  TERMINATED: "工作流已终止",
  CANCELLED: "已取消",
  PASS: "裁决通过",
  REVIEW: "需要复核",
  BLOCK: "安全阻断",
};

const tokenLabels: Record<AuthorizationTokenStatus, string> = {
  ISSUED: "已签发",
  CONSUMED: "已使用",
  EXPIRED: "已过期",
  REVOKED: "已撤销",
  REJECTED: "已拒绝",
};

export function workflowStatusLabel(value?: string | null): string {
  return value ? workflowLabels[value] || value : "暂无状态";
}

export function tokenStatusLabel(value?: AuthorizationTokenStatus | string | null): string {
  return value ? tokenLabels[value as AuthorizationTokenStatus] || value : "未签发";
}

export function isCurrentTurnWritable(turnId: string, presentation: TurnPresentationResponse | null, workflow: TurnWorkflowStatus | null): boolean {
  return Boolean(
    presentation
    && workflow
    && presentation.turn_id === turnId
    && workflow.current_turn_id === turnId
    && !workflow.terminal
    && workflow.status === "REVIEW_REQUIRED"
    && presentation.review.status === "REQUIRED"
    && presentation.decision_result.review_required,
  );
}
