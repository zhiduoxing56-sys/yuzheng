import type { PipelineEvent } from "../types/contract";
import { stageLabel } from "./pipelineStageMapper";

export interface StageItem {
  key: string;
  label: string;
  status: string;
}

export function mapPipelineEventToStage(event: PipelineEvent): StageItem {
  return { key: event.stage, label: stageLabel(event.stage), status: event.status };
}

export function mapApiErrorMessage(message: string, errorCode?: string): string {
  const labels: Record<string, string> = {
    TURN_NOT_FOUND: "未找到指定轮次",
    AUDIT_NOT_FOUND: "未找到指定审计记录",
    NODE_NOT_FOUND: "未找到指定证据节点",
    CORRECTED_TEXT_REQUIRED: "修正指令不能为空",
    SELECTED_CANDIDATE_REQUIRED: "确认候选前必须选择一个有效候选",
    NO_PERSISTED_REVIEW_CANDIDATES: "当前轮次没有可确认的持久化候选",
    REVIEW_CANDIDATE_NOT_FOUND: "所选候选不存在或已不属于当前轮次",
    REVIEW_CANDIDATE_NOT_VALID: "所选候选未通过后端校验",
    TURN_ALREADY_FINALIZED: "当前轮次已经结束，不能重复操作",
    REVIEW_NOT_ALLOWED: "当前工作流不允许此复核操作",
  };
  return (errorCode && labels[errorCode]) || message || "请求未完成";
}
