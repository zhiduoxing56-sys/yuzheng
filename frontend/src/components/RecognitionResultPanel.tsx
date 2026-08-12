import type { TurnPresentationResponse } from "../types/contract";
import { displayValue, formatPercent } from "../utils/formatters";

export function RecognitionResultPanel({ data }: { data: TurnPresentationResponse | null }) {
  return <section className="review-card">
    <span className="eyebrow">RECOGNITION</span><h2>识别与语义结果</h2>
    {!data ? <p className="empty-copy">暂无轮次展示。</p> : <dl className="review-fact-grid">
      <div><dt>输入方式</dt><dd>{data.input.input_type} / {data.input.input_source}</dd></div>
      <div><dt>原始转写</dt><dd>{displayValue(data.input.asr_raw_text)}</dd></div>
      <div><dt>规范化文本</dt><dd>{displayValue(data.input.normalized_text)}</dd></div>
      <div><dt>发声位置 / 角色</dt><dd>{data.input.speaker_zone} / {data.input.speaker_role}</dd></div>
      <div><dt>动作 / 目标</dt><dd>{data.semantic_frame.intents.map((item) => `${item.action} / ${item.target}`).join("；") || "未识别"}</dd></div>
      <div><dt>区域 / 风险</dt><dd>{data.semantic_frame.intents.map((item) => `${item.area || "未提供"} / ${item.risk_level}`).join("；") || "未提供"}</dd></div>
      <div><dt>语义可信度</dt><dd>{formatPercent(data.score_result.semantic_confidence)}</dd></div>
      <div><dt>输入可信度</dt><dd>{formatPercent(data.input.trust_score)}</dd></div>
    </dl>}
  </section>;
}
