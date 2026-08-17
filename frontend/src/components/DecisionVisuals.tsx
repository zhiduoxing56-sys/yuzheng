import { useRef } from "react";
import type { ReactNode } from "react";
import type { SemanticFrame, SemanticIntent } from "../types/contract";
import type { CommandInputMode, DecisionExplanationView, DecisionResultView, DecisionVisualState } from "../types/visualModels";

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
  const hasScalarValue = intent.value !== null && intent.value !== undefined && typeof intent.value !== "object";
  if (direction && hasScalarValue) return `${direction} ${formatSemanticValue(intent.value)}`;
  return direction || (hasScalarValue ? formatSemanticValue(intent.value) : null);
}

export function SemanticFrameDisplay({ frame }: { frame: SemanticFrame | null }) {
  return <section className="semantic-frame-section" aria-labelledby="semantic-frame-heading">
    <h2 id="semantic-frame-heading" className="visual-gradient-title">语义帧解析</h2>
    <div className="semantic-frame-container">
      {frame && <>
        <dl className="semantic-frame-summary">
          <div><dt>原始指令</dt><dd>{formatSemanticValue(frame.raw_text)}</dd></div>
          <div><dt>语义状态</dt><dd>{formatSemanticValue(frame.semantic_status)}</dd></div>
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

const DECISION_LABELS: Record<string, string> = {
  PASS: "允许执行",
  EVIDENCE_PASS: "允许执行",
  REVIEW: "需要人工复核",
  EVIDENCE_REVIEW: "需要人工复核",
  BLOCK: "拒绝执行",
  EVIDENCE_BLOCK: "拒绝执行",
  NOT_APPLICABLE: "不适用",
  NOT_REQUIRED: "不适用",
};

const DECISION_SOURCE_LABELS: Record<string, string> = {
  SAFETY_GATE: "硬性安全门",
  EVIDENCE_ALIGNMENT: "证据对齐",
  SAFETY_SCORE: "安全评分",
  RUNTIME_CAPABILITY: "运行能力约束",
  VOICE_TRUST: "语音可信约束",
  ZONE_PERMISSION: "区域权限约束",
  USER_REVIEW: "用户复核",
  LEGACY_COMPATIBILITY: "兼容记录",
};

function diagnosticDisplay(value: string | null) {
  return value?.trim() || "--";
}

function decisionDisplay(value: string | null | undefined): string {
  const normalized = value?.trim().toUpperCase();
  return normalized ? DECISION_LABELS[normalized] || "未识别状态" : "暂无结果";
}

function decisionSourceDisplay(value: string): string {
  return DECISION_SOURCE_LABELS[value.trim().toUpperCase()] || "未识别来源";
}

function mergeReasonDisplay(value: string | null | undefined): string {
  if (!value?.trim()) return "暂无原因";
  const aggregate = value.trim().match(/^Intent safety aggregate=([^;]+); top-level score is conservative projection from (\d+) occurrence assessments$/i);
  if (aggregate) return `各意图安全评价汇总为${decisionDisplay(aggregate[1])}；顶层评分采用 ${aggregate[2]} 个意图评价的保守投影`;
  const knownLabels = { ...DECISION_LABELS, ...DECISION_SOURCE_LABELS };
  const translated = value.trim()
    .replace(/Previously merged constraints preserve/gi, "先前合并的约束继续保持")
    .replace(/constrained final_decision to/gi, "将最终裁决限制为")
    .replace(/required REVIEW and conservative severity merge produced/gi, "要求人工复核，按保守严重度合并后得到")
    .replace(/EVIDENCE_ALIGNMENT passed/gi, "证据对齐通过")
    .replace(/final_decision equals/gi, "最终裁决等于")
    .replace(/from score_decision=/gi, "，原评分判断为")
    .replace(/score_decision=/gi, "评分判断=")
    .replace(/final_decision=/gi, "最终裁决=")
    .replace(/hit_rules=/gi, "命中规则=")
    .replace(/applied_constraints=/gi, "附加约束=")
    .replace(/preserved/gi, "保持不变")
    .replace(/produced/gi, "得到")
    .replace(/\bNONE\b/g, "无")
    .replace(/\bUNSPECIFIED\b/g, "未说明");
  return Object.entries(knownLabels).reduce(
    (text, [token, label]) => text.replace(new RegExp(`\\b${token}\\b`, "g"), label),
    translated,
  );
}

function recordValue(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function readableFacts(facts: Record<string, unknown> | undefined): Array<[string, string]> {
  if (!facts) return [];
  const runtime = recordValue(facts.key_runtime_state);
  const environment = recordValue(facts.environment);
  const gateRules = Array.isArray(facts.hit_safety_rules) ? facts.hit_safety_rules as Array<Record<string, unknown>> : [];
  const mandatory = recordValue(facts.mandatory_evidence);
  const execution = recordValue(facts.execution);
  const values: Array<[string, unknown]> = [
    ["车速", runtime.speed_kmh], ["挡位", runtime.gear], ["雨刮状态", runtime.wiper_state],
    ["前照灯状态", runtime.headlight_state], ["天气", environment.weather], ["道路状态", environment.road_condition],
    ["命中安全规则", gateRules.map((item) => item.rule).filter(Boolean).join("、")],
    ["缺失强制证据", Array.isArray(mandatory.missing_types) ? mandatory.missing_types.join("、") : null],
    ["执行结果", execution.result ? formatSemanticValue(execution.result) : null],
  ];
  return values.filter(([, value]) => value !== null && value !== undefined && value !== "" && value !== "--")
    .map(([label, value]) => [label, formatSemanticValue(value)]);
}

export function DecisionResultDisplay({ result, selector, explanation, onExplanationRetry }: { result: DecisionResultView; selector?: ReactNode; explanation?: DecisionExplanationView; onExplanationRetry?: () => void }) {
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
    <dl className="decision-primary-basis">
      <div><dt>安全门</dt><dd>{result.gateBlocked == null ? "暂无结果" : result.gateBlocked ? "已阻断" : "已通过"}</dd></div>
      <div><dt>证据对齐</dt><dd>{decisionDisplay(result.evidenceAlignment)}</dd></div>
      <div><dt>评分判断</dt><dd>{decisionDisplay(result.scoreDecision)}</dd></div>
    </dl>
    <div className="decision-reason"><h2>具体原因：</h2>
      <div className={`decision-reason-content is-${explanation?.status.toLowerCase() || "idle"}`}>
        {explanation?.status === "PENDING" ? <span className="decision-reason-spinner" role="status" aria-label="具体原因生成中" />
          : explanation?.status === "AVAILABLE" ? <span>{explanation.text}</span>
            : explanation?.status === "FAILED" ? <button type="button" className="decision-reason-retry" disabled={!explanation.retryable} onClick={onExplanationRetry}>重试</button>
              : <span>暂无</span>}
      </div>
    </div>
    {readableFacts(explanation?.facts).length > 0 && <details className="decision-diagnostic-score decision-fact-bundle"><summary>查看裁决依据</summary><dl>{readableFacts(explanation?.facts).map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></details>}
    <details className="decision-diagnostic-score"><summary>诊断评分（不覆盖安全门）</summary>
      <div className="decision-dimension-table"><table><thead><tr><th>维度</th><th>得分</th></tr></thead><tbody>{result.dimensions.map((row) => <tr key={row.id}><td>{row.dimension}</td><td>{diagnosticDisplay(row.detail)}</td></tr>)}</tbody></table></div>
      <p className="decision-score">五维安全评分： <strong>{diagnosticDisplay(result.score)}</strong></p>
    </details>
  </section>;
}
