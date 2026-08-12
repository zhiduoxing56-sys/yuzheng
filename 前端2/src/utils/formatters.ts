import type { DecisionLabel, EvidenceDemandStatus, ReviewAction } from "../types/contract";

const decisionLabels: Record<DecisionLabel, string> = {
  PASS: "允许执行",
  REVIEW: "需要复核",
  BLOCK: "安全阻断",
};

const reviewLabels: Record<ReviewAction, string> = {
  CONFIRM: "确认候选",
  CORRECT: "修正指令",
  CANCEL: "取消操作",
};

const evidenceLabels: Record<EvidenceDemandStatus, string> = {
  RETRIEVED: "已检索",
  MANDATORY_RECALLED: "强制召回",
  MISSING: "缺失",
  STALE: "已过期",
  CONFLICT: "存在冲突",
  TAMPERED: "完整性异常",
};

const stageLabels: Record<string, string> = {
  semantic: "语义解析",
  retrieval: "分层检索",
  evidence: "证据校验",
  decision: "安全裁决",
  review: "复核与审计",
};

export function decisionLabel(value?: string | null): string {
  return value && value in decisionLabels ? decisionLabels[value as DecisionLabel] : value || "暂无结果";
}

export function reviewActionLabel(value?: string | null): string {
  return value && value in reviewLabels ? reviewLabels[value as ReviewAction] : value || "暂无操作";
}

export function evidenceStatusLabel(value?: string | null): string {
  return value && value in evidenceLabels ? evidenceLabels[value as EvidenceDemandStatus] : value || "暂无状态";
}

export function stageLabel(value?: string | null): string {
  if (!value) return "未开始";
  return stageLabels[value] || value;
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "暂无时间";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}

export function formatPercent(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "暂无";
  return `${(value * 100).toFixed(1)}%`;
}

export function formatScore(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "暂无";
  return value.toFixed(3);
}

export function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "暂无数据";
  if (typeof value === "object") return "已返回结构化数据";
  return String(value);
}
