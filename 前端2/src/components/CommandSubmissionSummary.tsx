import type { AdaptedCommandResponse } from "../adapters/commandResponseAdapter";
import type { LastSubmissionSummary } from "../utils/commandSessionStorage";
import { formatDateTime } from "../utils/formatters";

interface Props { immediate: AdaptedCommandResponse | null; restored: LastSubmissionSummary | null; partial: boolean; }

export function CommandSubmissionSummary({ immediate, restored, partial }: Props) {
  const item = immediate ? {
    text: immediate.instructionSummary,
    inputType: immediate.inputType,
    source: immediate.summarySource,
    turnId: immediate.turnId,
    preliminaryDecision: immediate.preliminaryDecision,
    submittedAt: null,
    action: immediate.action,
    target: immediate.target,
  } : restored ? { ...restored, action: null, target: null } : null;
  if (!item) return null;
  return <section className="restore-notice" aria-label="本轮提交指令">
    <strong>本轮提交指令（即时受理结果）</strong>
    <p>{item.text}</p>
    <small>{item.inputType === "text" ? "文本" : "音频/麦克风"} · 摘要来源：{item.source} · 初步裁决：{item.preliminaryDecision} · {item.turnId}{item.submittedAt ? ` · ${formatDateTime(item.submittedAt)}` : ""}</small>
    {item.action && item.target && <small>即时语义：{item.action} / {item.target}</small>}
    {partial && <p className="inline-error">指令已受理并产生新轮次，但最终展示记录尚未归档。刷新只会重新获取展示结果，不会重复提交指令。</p>}
  </section>;
}
