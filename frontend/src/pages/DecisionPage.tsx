import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { submitAudioCommand, submitMicrophoneCommand, submitTextCommand } from "../api/command";
import { executeTurn, getTurnPresentation, submitTurnInteraction } from "../api/turns";
import { InteractionModal } from "../components/InteractionModal";
import { RequestRoutingDisplay } from "../components/RequestRoutingDisplay";
import { CommandInputSwitcher, DecisionResultDisplay, SemanticFrameDisplay } from "../components/DecisionVisuals";
import type { AudioCommandResponse, ExecuteResult, ExecutionTokenView, InteractionAction, InteractionRequest, RegulationRationale, RequestRouting, SemanticFrame, TextCommandResponse, TurnPresentationResponse } from "../types/contract";
import type { CommandInputMode, DecisionResultView } from "../types/visualModels";

interface CurrentTurnData {
  turn_id: string;
  semantic_frame: SemanticFrame;
  request_routing?: RequestRouting | null;
  evidence_demand?: TurnPresentationResponse["evidence_demand"];
  regulation_rationale?: RegulationRationale | null;
}
interface BoundExecutionToken extends ExecutionTokenView { turnId: string; }
const MAX_WAV_SIZE_BYTES = 20 * 1024 * 1024;
const EMPTY_RESULT: DecisionResultView = { state: null, dimensions: ["C_sem", "C_cov", "C_trust", "C_jb", "C_nec"].map((dimension) => ({ id: dimension, dimension, detail: null })), score: null, reason: null };

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
  return { ...EMPTY_RESULT, state, reason: decision.explanations?.join("；") || decision.gate_reasons?.join("；") || null };
}

export function DecisionPage() {
  const [mode, setMode] = useState<CommandInputMode>("text");
  const [text, setText] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [currentTurn, setCurrentTurn] = useState<CurrentTurnData | null>(null);
  const [result, setResult] = useState<DecisionResultView>(EMPTY_RESULT);
  const [tokens, setTokens] = useState<BoundExecutionToken[]>([]);
  const [execResults, setExecResults] = useState<Record<string, ExecuteResult>>({});
  const [execBusyTurnId, setExecBusyTurnId] = useState<string | null>(null);
  const [interaction, setInteraction] = useState<InteractionRequest | null>(null);
  const [clarificationBusy, setClarificationBusy] = useState(false);
  const [clarificationError, setClarificationError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const activeRequestRef = useRef<AbortController | null>(null);
  const turnId = searchParams.get("turn_id")?.trim() || null;

  const accept = useCallback((response: TextCommandResponse | AudioCommandResponse, message: string) => {
    const textResponse: TextCommandResponse | null = (response as AudioCommandResponse).input_type === "audio"
      ? (response as AudioCommandResponse).pipeline ?? null
      : response as TextCommandResponse;
    const frame = textResponse?.semantic_frame ?? response.semantic_frame;
    if (frame) {
      setCurrentTurn({ turn_id: response.turn_id, semantic_frame: frame, request_routing: textResponse?.request_routing ?? null, regulation_rationale: textResponse?.regulation_rationale ?? null });
      setText(frame.raw_text);
    }
    if (textResponse?.semantic_frame) {
      setTokens(tokensFor(textResponse));
      setResult(resultFor(textResponse));
    }
    setInteraction(response.interaction_request || textResponse?.interaction_request || null);
    const next = new URLSearchParams(searchParams); next.set("turn_id", response.turn_id); setSearchParams(next, { replace: true });
    setFeedback(`${message}，轮次 ${response.turn_id}`);
  }, [searchParams, setSearchParams]);

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
    }).catch(() => undefined);
    return () => controller.abort();
  }, [currentTurn?.turn_id, turnId]);

  const submit = useCallback(() => {
    const controller = new AbortController(); activeRequestRef.current?.abort(); activeRequestRef.current = controller;
    setBusy(true); setHasError(false); setFeedback("正在解析语义帧…");
    const request = mode === "text"
      ? submitTextCommand({ text: text.trim() }, controller.signal)
      : mode === "audio" && audioFile
        ? submitAudioCommand(audioFile, { audio_source: "browser_upload", speaker_zone: "driver", speaker_role: "driver" }, controller.signal)
        : submitMicrophoneCommand({ duration_seconds: 4, speaker_zone: "driver", speaker_role: "driver" }, controller.signal);
    void request.then((response) => { if (!controller.signal.aborted) accept(response, "语义帧解析完成"); })
      .catch((error: unknown) => { if (!controller.signal.aborted) { setHasError(true); setFeedback(error instanceof Error ? error.message : "指令提交失败"); } })
      .finally(() => { if (activeRequestRef.current === controller) { setBusy(false); setRecording(false); } });
  }, [accept, audioFile, mode, text]);

  const execute = useCallback(async (token: BoundExecutionToken, interactionId: string) => {
    setExecBusyTurnId(token.turnId);
    try { const value = await executeTurn(token.turnId, token.token, interactionId, token.intent_id || undefined); setExecResults((old) => ({ ...old, [token.turnId]: value })); }
    finally { setExecBusyTurnId(null); }
  }, []);

  const resolve = useCallback((action: InteractionAction, candidateId?: string, text?: string, parameters?: Record<string, unknown>) => {
    if (!interaction) return;
    setClarificationBusy(true); setClarificationError(null);
    void submitTurnInteraction(interaction.turn_id, { interaction_id: interaction.interaction_id, action, ...(candidateId ? { candidate_id: candidateId } : {}), ...(text ? { text } : {}), ...(parameters ? { parameters } : {}) }).then((response) => {
      if (action === "EXECUTE") { const token = tokens.find((item) => item.turnId === interaction.turn_id); if (!token) throw new Error("后端未提供可执行令牌"); return execute(token, interaction.interaction_id).then(() => setInteraction(null)); }
      if (response.command_result) accept(response.command_result, "复核完成");
      else setInteraction(null);
    }).catch((error: unknown) => setClarificationError(error instanceof Error ? error.message : "复核失败")).finally(() => setClarificationBusy(false));
  }, [accept, execute, interaction, tokens]);

  return <><div className="visual-page-frame decision-visual-page"><div className="decision-visual-layout">
    <div className="decision-visual-left">
      <CommandInputSwitcher mode={mode} text={text} audioFileName={audioFile?.name || ""} recording={recording} busy={busy} feedback={feedback} hasError={hasError} onModeChange={setMode} onTextChange={setText} onAudioChange={setAudioFile} onRecordingToggle={() => { setMode("microphone"); setRecording(true); submit(); }} onSubmit={submit} />
      <SemanticFrameDisplay frame={currentTurn?.semantic_frame || null} />
      {currentTurn?.evidence_demand?.intent_demands.some((item) => item.knowledge_augmented_types?.length) ? <div className="knowledge-augmented-block">
        {currentTurn.evidence_demand.intent_demands.map((intent) => intent.knowledge_augmented_types?.length ? <p key={intent.intent_id}><strong>📚 知识库追加（{intent.intent_id}）</strong>：{intent.knowledge_augmented_types.join("、")}{intent.knowledge_hits?.length ? <span> · 命中 {intent.knowledge_hits.map((hit) => hit.title ?? hit.node_id).join("；")}</span> : null}</p> : null)}
      </div> : null}
      {currentTurn?.regulation_rationale?.hits?.length ? <div className="regulation-rationale-block">
        <p><strong>📜 法规依据</strong></p>
        {currentTurn.regulation_rationale.hits.map((hit, index) => <p key={index}><span className="regulation-score">[{hit.score.toFixed(3)}]</span> {hit.standard_id} {hit.clause}：{hit.content?.slice(0, 90)}{hit.evidence_types?.length ? <span> · 证据：{hit.evidence_types.join("、")}</span> : null}</p>)}
      </div> : null}
      <RequestRoutingDisplay routing={currentTurn?.request_routing} />
    </div>
    <div className="decision-result-column"><div className="decision-child-detail-card">
      <DecisionResultDisplay result={result} />
      <section className="decision-execution-panel"><div className="decision-execution-actions">
        {tokens.length === 0 ? <button type="button" disabled className="decision-execution-button">无待确认执行</button> : <p>请在执行确认交互中确认执行。</p>}
      </div>{Object.values(execResults).map((entry) => <div key={entry.reason} className="decision-execution-result"><span>{entry.reason}</span></div>)}</section>
    </div></div>
  </div></div>{interaction ? <InteractionModal error={clarificationError} onSubmit={resolve} request={interaction} busy={clarificationBusy} /> : null}</>;
}
