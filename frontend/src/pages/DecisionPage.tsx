import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { submitAudioCommand, submitMicrophoneCommand, submitTextCommand } from "../api/command";
import { executeTurn, getBayesianDiagnostic, getDecisionExplanation, getTurnPresentation, retryDecisionExplanation, submitTurnInteraction } from "../api/turns";
import { InteractionModal } from "../components/InteractionModal";
import { CommandInputSwitcher, DecisionResultDisplay, SemanticFrameDisplay } from "../components/DecisionVisuals";
import { useSession } from "../stores/sessionStore";
import type { AudioCommandResponse, BayesianIntentDiagnostic, ExecutionTokenView, InteractionAction, InteractionRequest, RequestRouting, SemanticFrame, TextCommandResponse, TurnPresentationResponse } from "../types/contract";
import type { CommandInputMode, DecisionExplanationView, DecisionResultView } from "../types/visualModels";

interface CurrentTurnData {
  turn_id: string;
  semantic_frame: SemanticFrame;
  request_routing?: RequestRouting | null;
  evidence_demand?: TurnPresentationResponse["evidence_demand"];
}
interface BoundExecutionToken extends ExecutionTokenView { turnId: string; }
type ExecutionMode = "NORMAL" | "REUSE" | "STATE_CHANGED";
interface ExecutionOutcome { state: "IDLE" | "PENDING" | "ACCEPTED" | "REJECTED"; reason: string | null; }
const MAX_WAV_SIZE_BYTES = 20 * 1024 * 1024;
const EMPTY_RESULT: DecisionResultView = { state: null, dimensions: ["C_sem", "C_cov", "C_trust", "C_jb", "C_nec"].map((dimension) => ({ id: dimension, dimension, detail: null })), score: null, reason: null };
const EMPTY_EXPLANATION: DecisionExplanationView = { status: "IDLE", text: null, retryable: false, facts: {} };
const EXPLANATION_POLL_INTERVAL_MS = 1_000;
const EXPLANATION_WAIT_LIMIT_MS = 30_000;

function tokensFor(response: TextCommandResponse): BoundExecutionToken[] {
  const tokens = response.decision?.execution_tokens || [];
  if (tokens.length) return tokens.map((token) => ({ ...token, turnId: response.turn_id }));
  const token = response.decision?.authorization_token;
  const intent = response.semantic_frame.intents?.[0];
  return token && intent ? [{ token, turnId: response.turn_id, intent_id: intent.intent_id, label: `${intent.action} ${intent.target}`, action: intent.action, target: intent.target, area: intent.area }] : [];
}

function resultFor(response: TextCommandResponse): DecisionResultView {
  const decision = response.decision;
  const state = decision.final_decision === "PASS" ? "pass" : decision.final_decision === "REVIEW" ? "review" : decision.final_decision === "BLOCK" ? "reject" : null;
  const assessment = decision.intent_safety_assessments?.[0];
  const score = assessment?.score;
  return {
    ...EMPTY_RESULT,
    state,
    score: decision.safety_score == null ? null : Number(decision.safety_score).toFixed(4),
    reason: decision.explanations?.join("；") || decision.gate_reasons?.join("；") || null,
    scoreDecision: decision.score_decision,
    finalDecision: decision.final_decision,
    gateBlocked: decision.gate_blocked,
    evidenceAlignment: assessment?.quality?.evidence_alignment_route || null,
    decisionSources: decision.decision_sources || [],
    mergeReason: decision.decision_merge_reason || null,
    dimensions: [
      { id: "C_sem", dimension: "语义清晰度", detail: score?.semantic_clarity == null ? null : Number(score.semantic_clarity).toFixed(4) },
      { id: "C_cov", dimension: "证据覆盖度", detail: assessment?.quality?.ecr == null ? null : Number(assessment.quality.ecr).toFixed(4) },
      { id: "C_trust", dimension: "证据可信度", detail: score?.evidence_trust == null ? null : Number(score.evidence_trust).toFixed(4) },
      { id: "C_jb", dimension: "越狱抑制能力", detail: score?.jailbreak_suppression == null ? null : Number(score.jailbreak_suppression).toFixed(4) },
      { id: "C_nec", dimension: "场景必要性", detail: score?.scene_necessity == null ? null : Number(score.scene_necessity).toFixed(4) },
    ],
  };
}

function resultForPresentation(presentation: TurnPresentationResponse): DecisionResultView {
  const decision = presentation.decision_result;
  const assessment = decision.intent_safety_assessments?.[0];
  const score = assessment?.score || presentation.score_result;
  const state = decision.final_decision === "PASS" ? "pass" : decision.final_decision === "REVIEW" ? "review" : decision.final_decision === "BLOCK" ? "reject" : null;
  return {
    ...EMPTY_RESULT,
    state,
    score: decision.safety_score == null ? null : Number(decision.safety_score).toFixed(4),
    reason: decision.reasons?.join("；") || decision.explanation || null,
    scoreDecision: decision.score_decision,
    finalDecision: decision.final_decision,
    gateBlocked: presentation.gate_result.blocked,
    evidenceAlignment: assessment?.quality?.evidence_alignment_route || presentation.evidence.quality_metrics.evidence_alignment_route || null,
    decisionSources: decision.decision_sources || [],
    mergeReason: decision.decision_merge_reason || null,
    dimensions: [
      { id: "C_sem", dimension: "语义清晰度", detail: score.semantic_clarity == null ? null : Number(score.semantic_clarity).toFixed(4) },
      { id: "C_cov", dimension: "证据覆盖度", detail: presentation.evidence.quality_metrics.ecr == null ? null : Number(presentation.evidence.quality_metrics.ecr).toFixed(4) },
      { id: "C_trust", dimension: "证据可信度", detail: score.evidence_trust == null ? null : Number(score.evidence_trust).toFixed(4) },
      { id: "C_jb", dimension: "越狱抑制能力", detail: score.jailbreak_suppression == null ? null : Number(score.jailbreak_suppression).toFixed(4) },
      { id: "C_nec", dimension: "场景必要性", detail: score.scene_necessity == null ? null : Number(score.scene_necessity).toFixed(4) },
    ],
  };
}

export function DecisionPage() {
  const [mode, setMode] = useState<CommandInputMode>("text");
  const [text, setText] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [currentTurn, setCurrentTurn] = useState<CurrentTurnData | null>(null);
  const [result, setResult] = useState<DecisionResultView>(EMPTY_RESULT);
  const [explanation, setExplanation] = useState<DecisionExplanationView>(EMPTY_EXPLANATION);
  const [bayesian, setBayesian] = useState<BayesianIntentDiagnostic | null>(null);
  const [explanationAttempt, setExplanationAttempt] = useState(0);
  const [tokens, setTokens] = useState<BoundExecutionToken[]>([]);
  const [executionOutcome, setExecutionOutcome] = useState<ExecutionOutcome>({ state: "IDLE", reason: null });
  const [execBusyTurnId, setExecBusyTurnId] = useState<string | null>(null);
  const [interaction, setInteraction] = useState<InteractionRequest | null>(null);
  const [clarificationBusy, setClarificationBusy] = useState(false);
  const [clarificationError, setClarificationError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const { activeTurnId, setActiveTurn, pendingExecutionDemo, setPendingExecutionDemo } = useSession();
  const [executionMode, setExecutionMode] = useState<ExecutionMode>("NORMAL");
  const navigate = useNavigate();
  const activeRequestRef = useRef<AbortController | null>(null);
  const tokensRef = useRef<BoundExecutionToken[]>([]);
  const routeTurnId = searchParams.get("turn_id")?.trim() || null;
  const turnId = routeTurnId || activeTurnId || null;

  const accept = useCallback((response: TextCommandResponse | AudioCommandResponse, message: string) => {
    const textResponse: TextCommandResponse | null = (response as AudioCommandResponse).input_type === "audio"
      ? (response as AudioCommandResponse).pipeline ?? null
      : response as TextCommandResponse;
    const frame = textResponse?.semantic_frame ?? response.semantic_frame;
    if (frame) {
      setCurrentTurn({ turn_id: response.turn_id, semantic_frame: frame, request_routing: textResponse?.request_routing ?? null });
      setText(frame.raw_text);
    }
    if (textResponse?.semantic_frame) {
      const issuedTokens = tokensFor(textResponse);
      tokensRef.current = issuedTokens;
      setTokens(issuedTokens);
      setResult(resultFor(textResponse));
      setExecutionOutcome({ state: "IDLE", reason: null });
    }
    setInteraction(response.interaction_request || textResponse?.interaction_request || null);
    setActiveTurn(response.turn_id, {
      instructionSummary: frame?.raw_text || null,
      decision: textResponse?.decision?.final_decision || null,
      createdAt: new Date().toISOString(),
    });
    const next = new URLSearchParams(searchParams); next.set("turn_id", response.turn_id); setSearchParams(next, { replace: true });
    setFeedback(`${message}，轮次 ${response.turn_id}`);
  }, [searchParams, setActiveTurn, setSearchParams]);

  useEffect(() => {
    if (!routeTurnId && activeTurnId) {
      const next = new URLSearchParams(searchParams);
      next.set("turn_id", activeTurnId);
      setSearchParams(next, { replace: true });
    }
  }, [activeTurnId, routeTurnId, searchParams, setSearchParams]);

  useEffect(() => {
    if (!turnId || currentTurn?.turn_id === turnId) return;
    const controller = new AbortController(); activeRequestRef.current?.abort(); activeRequestRef.current = controller;
    void getTurnPresentation(turnId, controller.signal).then((presentation) => {
      if (controller.signal.aborted) return;
      setCurrentTurn({
        turn_id: presentation.turn_id,
        semantic_frame: presentation.semantic_frame,
        request_routing: presentation.request_routing,
        evidence_demand: presentation.evidence_demand,
      });
      setText(presentation.semantic_frame.raw_text); setInteraction(presentation.interaction_request || null);
      setResult(resultForPresentation(presentation));
      setActiveTurn(presentation.turn_id, {
        instructionSummary: presentation.semantic_frame.raw_text,
        decision: presentation.decision_result.final_decision,
        createdAt: presentation.created_at,
      });
    }).catch(() => undefined);
    return () => controller.abort();
  }, [currentTurn?.turn_id, setActiveTurn, turnId]);

  useEffect(() => {
    if (!turnId) { setExplanation(EMPTY_EXPLANATION); return; }
    const controller = new AbortController();
    const deadline = Date.now() + EXPLANATION_WAIT_LIMIT_MS;
    let timer: ReturnType<typeof setTimeout> | null = null;
    setExplanation({ status: "PENDING", text: null, retryable: false, facts: {} });
    const poll = async () => {
      try {
        const value = await getDecisionExplanation(turnId, controller.signal);
        if (controller.signal.aborted) return;
        if (value.status === "PENDING") {
          setExplanation({ status: "PENDING", text: null, retryable: false, facts: value.fact_bundle || {} });
        }
        if (value.status === "AVAILABLE") {
          setExplanation({ status: "AVAILABLE", text: value.explanation?.trim() || null, retryable: false, facts: value.fact_bundle || {} });
          return;
        }
        if (value.status === "FAILED") {
          setExplanation({ status: "FAILED", text: null, retryable: value.retryable, facts: value.fact_bundle || {} });
          return;
        }
      } catch {
        if (controller.signal.aborted) return;
      }
      if (Date.now() >= deadline) {
        setExplanation({ status: "FAILED", text: null, retryable: true, facts: {} });
        return;
      }
      timer = setTimeout(() => { void poll(); }, EXPLANATION_POLL_INTERVAL_MS);
    };
    void poll();
    return () => { controller.abort(); if (timer) clearTimeout(timer); };
  }, [explanationAttempt, turnId]);

  useEffect(() => {
    if (!turnId) { setBayesian(null); return; }
    const controller = new AbortController();
    setBayesian(null);
    void getBayesianDiagnostic(turnId, controller.signal)
      .then((response) => {
        if (!controller.signal.aborted) {
          setBayesian(response.diagnostics.find((item) => item.supported) || null);
        }
      })
      .catch(() => { if (!controller.signal.aborted) setBayesian(null); });
    return () => controller.abort();
  }, [turnId]);

  const submit = useCallback(() => {
    const controller = new AbortController(); activeRequestRef.current?.abort(); activeRequestRef.current = controller;
    setBusy(true); setHasError(false); setFeedback("正在解析语义帧…");
    const request = mode === "text"
      ? submitTextCommand({ text: text.trim(), speaker_zone: "driver", speaker_role: "driver" }, controller.signal)
      : mode === "audio" && audioFile
        ? submitAudioCommand(audioFile, { audio_source: "browser_upload", speaker_zone: "driver", speaker_role: "driver" }, controller.signal)
        : submitMicrophoneCommand({ duration_seconds: 4, speaker_zone: "driver", speaker_role: "driver" }, controller.signal);
    void request.then((response) => { if (!controller.signal.aborted) accept(response, "语义帧解析完成"); })
      .catch((error: unknown) => { if (!controller.signal.aborted) { setHasError(true); setFeedback(error instanceof Error ? error.message : "指令提交失败"); } })
      .finally(() => { if (activeRequestRef.current === controller) { setBusy(false); setRecording(false); } });
  }, [accept, audioFile, mode, text]);

  const execute = useCallback(async (token: BoundExecutionToken, interactionId: string) => {
    setExecBusyTurnId(token.turnId);
    setExecutionOutcome({ state: "PENDING", reason: null });
    try {
      const value = await executeTurn(token.turnId, token.token, interactionId, token.intent_id || undefined);
      setExecutionOutcome({ state: value.accepted ? "ACCEPTED" : "REJECTED", reason: value.reason || (value.accepted ? "车辆动作已执行" : "后端拒绝执行") });
      return value;
    } catch (error) {
      setExecutionOutcome({ state: "REJECTED", reason: error instanceof Error ? error.message : "执行请求被后端拒绝" });
      return null;
    }
    finally { setExecBusyTurnId(null); }
  }, []);

  const retryExplanation = useCallback(() => {
    if (!turnId) return;
    setExplanation({ status: "PENDING", text: null, retryable: false });
    void retryDecisionExplanation(turnId)
      .then((value) => {
        if (value.status === "FAILED") {
          setExplanation({ status: "FAILED", text: null, retryable: value.retryable });
          return;
        }
        if (value.status === "AVAILABLE") {
          setExplanation({ status: "AVAILABLE", text: value.explanation?.trim() || null, retryable: false });
          return;
        }
        setExplanationAttempt((current) => current + 1);
      })
      .catch(() => setExplanation({ status: "FAILED", text: null, retryable: true }));
  }, [turnId]);

  const resolve = useCallback((action: InteractionAction, candidateId?: string, text?: string, parameters?: Record<string, unknown>) => {
    if (!interaction) return;
    setClarificationBusy(true); setClarificationError(null);
    void submitTurnInteraction(interaction.turn_id, { interaction_id: interaction.interaction_id, action, ...(candidateId ? { candidate_id: candidateId } : {}), ...(text ? { text } : {}), ...(parameters ? { parameters } : {}) }).then((response) => {
      if (action === "EXECUTE") { const token = tokensRef.current.find((item) => item.turnId === interaction.turn_id); if (!token) throw new Error("后端未提供可执行令牌"); if (executionMode !== "NORMAL") { setPendingExecutionDemo({ turnId: token.turnId, token: token.token, interactionId: interaction.interaction_id, intentId: token.intent_id, label: token.label || "当前车辆操作" }); setInteraction(null); return; } return execute(token, interaction.interaction_id).then(() => setInteraction(null)); }
      if (response.command_result) accept(response.command_result, "复核完成");
      else setInteraction(null);
    }).catch((error: unknown) => setClarificationError(error instanceof Error ? error.message : "复核失败")).finally(() => setClarificationBusy(false));
  }, [accept, execute, executionMode, interaction, setPendingExecutionDemo]);
  const executeDemo = useCallback(() => {
    if (!pendingExecutionDemo) return;
    void execute({ token: pendingExecutionDemo.token, turnId: pendingExecutionDemo.turnId, intent_id: pendingExecutionDemo.intentId || "", label: pendingExecutionDemo.label, action: "", target: "", area: "unknown" }, pendingExecutionDemo.interactionId);
  }, [execute, pendingExecutionDemo]);

  return <><div className="visual-page-frame decision-visual-page"><div className="decision-visual-layout">
    <div className="decision-visual-left">
      <CommandInputSwitcher mode={mode} text={text} audioFileName={audioFile?.name || ""} recording={recording} busy={busy} feedback={feedback} hasError={hasError} onModeChange={setMode} onTextChange={setText} onAudioChange={setAudioFile} onRecordingToggle={() => { setMode("microphone"); setRecording(true); submit(); }} onSubmit={submit} />
      <SemanticFrameDisplay frame={currentTurn?.semantic_frame || null} />
    </div>
    <div className="decision-result-column"><div className="decision-child-detail-card">
      <DecisionResultDisplay result={result} explanation={explanation} bayesian={bayesian} onExplanationRetry={retryExplanation} />
      <section className="decision-execution-panel" aria-labelledby="execution-acceptance-heading"><h2 id="execution-acceptance-heading">执行验收</h2><div className="decision-execution-grid"><div className="decision-execution-modes">{([['NORMAL', '正常执行'], ['REUSE', '重复使用同一授权'], ['STATE_CHANGED', '签发后改变状态']] as const).map(([value, label]) => <button key={value} type="button" aria-pressed={executionMode === value} onClick={() => setExecutionMode(value)}>{label}</button>)}</div><div className="decision-execution-state">{pendingExecutionDemo?.turnId === turnId ? executionMode === 'STATE_CHANGED' ? '授权已签发，等待状态变化' : '授权已签发，等待执行' : tokens.length ? interaction ? '等待确认执行' : '等待授权签发' : '未签发授权'}</div><div className={`decision-execution-outcome is-${executionOutcome.state.toLowerCase()}`}>{executionOutcome.state === 'PENDING' ? '正在核验授权与当前状态…' : executionOutcome.state === 'ACCEPTED' ? <>已执行｜{executionOutcome.reason}</> : executionOutcome.state === 'REJECTED' ? <>已拒绝｜{executionOutcome.reason}</> : tokens.length ? '尚无执行结果' : '本轮未签发授权，无法执行所选测试'}</div></div>{pendingExecutionDemo?.turnId === turnId && <div className="decision-execution-actions">{executionMode === 'STATE_CHANGED' && <button type="button" className="decision-execution-button" onClick={() => navigate('/carla')}>前往模拟器修改状态</button>}<button type="button" className="decision-execution-button" disabled={execBusyTurnId === turnId} onClick={executeDemo}>{executionMode === 'REUSE' && executionOutcome.state === 'ACCEPTED' ? '再次执行同一授权' : '按原授权执行'}</button></div>}</section>
    </div></div>
  </div></div>{interaction ? <InteractionModal error={clarificationError} onSubmit={resolve} request={interaction} busy={clarificationBusy} executionDemoEnabled={executionMode !== "NORMAL"} onExecutionDemoEnabledChange={(enabled) => setExecutionMode(enabled ? "REUSE" : "NORMAL")} /> : null}</>;
}
