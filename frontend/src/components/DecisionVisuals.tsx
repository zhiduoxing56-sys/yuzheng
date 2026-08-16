import { useRef } from "react";
import type { ReactNode } from "react";
import type { SemanticFrame, SemanticIntent } from "../types/contract";
import type { CommandInputMode, DecisionResultView, DecisionVisualState } from "../types/visualModels";

const INPUT_TABS: Array<{ mode: CommandInputMode; label: string }> = [
  { mode: "text", label: "文本指令" },
  { mode: "audio", label: "音频上传" },
  { mode: "microphone", label: "麦克风采集" },
];

interface CommandInputSwitcherProps {
  mode: CommandInputMode;
  text: string;
  audioFileName: string;
  recording: boolean;
  busy: boolean;
  feedback: string | null;
  hasError: boolean;
  onModeChange: (mode: CommandInputMode) => void;
  onTextChange: (text: string) => void;
  onAudioChange: (file: File | null) => void;
  onRecordingToggle: () => void;
  onSubmit: () => void;
}

export function CommandInputSwitcher(props: CommandInputSwitcherProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  return <section className="decision-input-section" aria-labelledby="command-input-heading">
    <h1 id="command-input-heading" className="visual-gradient-title">指令输入</h1>
    <div className="decision-input-tabs" role="tablist" aria-label="指令输入方式">
      {INPUT_TABS.map((tab) => <button key={tab.mode} type="button" role="tab" aria-selected={props.mode === tab.mode} className={props.mode === tab.mode ? "is-active" : ""} onClick={() => props.onModeChange(tab.mode)}>{tab.label}</button>)}
    </div>
    <div className="decision-input-area">
      {props.mode === "text" && <textarea aria-label="文本指令" value={props.text} onChange={(event) => props.onTextChange(event.target.value)} />}
      {props.mode === "audio" && <button className="decision-file-picker" type="button" onClick={() => fileInputRef.current?.click()}>
        <span>{props.audioFileName || "选择音频文件"}</span>
        <input ref={fileInputRef} aria-label="WAV 音频文件" type="file" accept=".wav,audio/wav,audio/x-wav" onChange={(event) => props.onAudioChange(event.target.files?.[0] || null)} />
      </button>}
      {props.mode === "microphone" && <button className={`decision-microphone-control${props.recording ? " is-recording" : ""}`} type="button" aria-pressed={props.recording} disabled={props.busy} onClick={props.onRecordingToggle}>
        <span aria-hidden="true" className="microphone-symbol" /><strong>{props.recording ? "本机麦克风采集中…" : "采集 4 秒语音"}</strong>
      </button>}
    </div>
    {props.mode !== "microphone" && <button className="decision-submit-button" type="button" disabled={props.busy} onClick={props.onSubmit}>{props.busy ? "处理中…" : props.mode === "audio" ? "上传 WAV" : "提交指令"}</button>}
    {props.feedback && <p className={`decision-input-feedback${props.hasError ? " is-error" : ""}`} role={props.hasError ? "alert" : "status"}>{props.feedback}</p>}
  </section>;
}

export function formatSemanticValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "--";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function formatScore(value: number): string {
  return Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "--";
}

function formatList(values: string[]): string {
  return values.length ? values.join("、") : "--";
}

const RUNTIME_IDENTITY_LABEL: Record<NonNullable<SemanticIntent["runtime_identity"]>, string> = {
  FORMAL: "正式安全意图",
  KNOWN_NON_EXECUTABLE: "已识别、当前不可执行",
};

const DIRECTION_LABEL: Record<string, string> = {
  INCREASE: "升高", DECREASE: "降低", FORWARD: "向前", BACKWARD: "向后",
  UP: "向上", DOWN: "向下", OPEN: "开大", CLOSE: "关小",
};

function intentDisplayName(intent: SemanticIntent): string {
  return `${intent.action}${intent.target}`;
}

function controlValue(intent: SemanticIntent): string | null {
  const direction = intent.direction ? DIRECTION_LABEL[intent.direction] || intent.direction : null;
  if (direction && intent.value !== null && intent.value !== undefined) return `${direction} ${formatSemanticValue(intent.value)}`;
  return direction || (intent.value !== null && intent.value !== undefined ? formatSemanticValue(intent.value) : null);
}

export function SemanticFrameDisplay({ frame }: { frame: SemanticFrame | null }) {
  return <section className="semantic-frame-section" aria-labelledby="semantic-frame-heading">
    <h2 id="semantic-frame-heading" className="visual-gradient-title">语义帧解析</h2>
    <div className="semantic-frame-container">
      {!frame && <p className="semantic-frame-empty">提交文本指令后显示正式多意图语义帧</p>}
      {frame && <>
        <dl className="semantic-frame-summary">
          <div><dt>原始指令</dt><dd>{formatSemanticValue(frame.raw_text)}</dd></div>
          <div><dt>规范化指令</dt><dd>{formatSemanticValue(frame.normalized_text)}</dd></div>
          <div><dt>语义状态</dt><dd>{formatSemanticValue(frame.semantic_status)}</dd></div>
          <div><dt>整体语义置信度</dt><dd>{formatScore(frame.semantic_confidence)}</dd></div>
          <div><dt>整体歧义度</dt><dd>{formatScore(frame.ambiguity_score)}</dd></div>
          <div><dt>复核原因</dt><dd>{formatList(frame.review_reasons)}</dd></div>
          <div><dt>未解析子句</dt><dd>{formatList(frame.unresolved_clauses)}</dd></div>
          <div><dt>安全信号</dt><dd>{formatList(frame.security_signals)}</dd></div>
        </dl>
        <div className="semantic-intent-list">
          {frame.intents.map((intent, occurrenceIndex) => <article className="semantic-intent-card" key={`${intent.clause_index}:${occurrenceIndex}:${intent.intent_id}`}>
            <h3>{intentDisplayName(intent)}</h3>
            <dl>
              <div><dt>子句索引</dt><dd>{formatSemanticValue(intent.clause_index)}</dd></div>
              <div><dt>子句</dt><dd>{formatSemanticValue(intent.clause_text)}</dd></div>
              <div><dt>意图编号</dt><dd>{formatSemanticValue(intent.intent_id)}</dd></div>
              <div><dt>运行身份</dt><dd>{intent.runtime_identity ? RUNTIME_IDENTITY_LABEL[intent.runtime_identity] : "--"}</dd></div>
              <div><dt>动作</dt><dd>{formatSemanticValue(intent.action)}</dd></div>
              <div><dt>对象</dt><dd>{formatSemanticValue(intent.target)}</dd></div>
              <div><dt>区域</dt><dd>{formatSemanticValue(intent.area)}</dd></div>
              {controlValue(intent) && <div><dt>控制参数</dt><dd>{controlValue(intent)}</dd></div>}
              {intent.direction && <div><dt>方向</dt><dd>{DIRECTION_LABEL[intent.direction] || intent.direction}</dd></div>}
              {intent.mode && <div><dt>模式</dt><dd>{formatSemanticValue(intent.mode)}</dd></div>}
              {intent.control_attribute && <div><dt>控制属性</dt><dd>{formatSemanticValue(intent.control_attribute)}</dd></div>}
              <div><dt>控制域</dt><dd>{formatSemanticValue(intent.control_domain)}</dd></div>
              <div><dt>风险等级</dt><dd>{formatSemanticValue(intent.risk_level)}</dd></div>
              <div><dt>风险标签</dt><dd>{formatList(intent.risk_tags)}</dd></div>
              <div><dt>语义置信度</dt><dd>{formatScore(intent.semantic_confidence)}</dd></div>
              <div><dt>歧义度</dt><dd>{formatScore(intent.ambiguity_score)}</dd></div>
            </dl>
          </article>)}
          {!frame.intents.length && <p className="semantic-frame-empty">当前语义帧没有可展示的子意图</p>}
        </div>
      </>}
    </div>
  </section>;
}

const DECISION_STATE_VIEW: Record<DecisionVisualState, { label: string; symbol: string; partial: boolean }> = {
  pass: { label: "通过", symbol: "✓", partial: false },
  review: { label: "人工复核", symbol: "✓", partial: true },
  reject: { label: "拒绝", symbol: "×", partial: false },
};

function display(value: string | null) {
  return value?.trim() || "--";
}

export function DecisionResultDisplay({ result, selector }: { result: DecisionResultView; selector?: ReactNode }) {
  const state = result.state ? DECISION_STATE_VIEW[result.state] : null;
  return <section className={`decision-result-section state-${result.state || "empty"}`} aria-labelledby="decision-result-heading">
    <div className="decision-result-heading-row">
      <h1 id="decision-result-heading" className="visual-gradient-title">裁决结果</h1>
      {selector}
    </div>
    <div className="decision-result-banner" role="status">
      {state && <span aria-hidden="true"><i className={state.partial ? "is-partial" : ""}>{state.symbol}</i></span>}
      <strong>{state?.label || "--"}</strong>
    </div>
    <div className="decision-dimension-table"><table><thead><tr><th>维度</th><th>细则</th></tr></thead>
      <tbody>{result.dimensions.map((row) => <tr key={row.id}><td>{row.dimension}</td><td>{display(row.detail)}</td></tr>)}</tbody>
    </table></div>
    <p className="decision-score">裁决得分： <strong>{display(result.score)}</strong></p>
    <div className="decision-reason"><h2>具体原因：</h2><div>{result.reason?.trim() || "暂无"}</div></div>
  </section>;
}
