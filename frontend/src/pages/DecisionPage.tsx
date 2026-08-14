import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { submitAudioCommand, submitCoordinatedTextCommand, submitMicrophoneCommand } from "../api/command";
import { executeTurn, getTurnPresentation, submitTurnClarification } from "../api/turns";
import { ClarificationModal } from "../components/ClarificationModal";
import { CommandInputSwitcher, DecisionResultDisplay, SemanticFrameDisplay } from "../components/DecisionVisuals";
import { useSession } from "../stores/sessionStore";
import type { AudioCommandResponse, ClarificationRequest, CoordinatedCommandChild, ExecuteResult, ExecutionTokenView, SemanticFrame, TextCommandResponse, TurnPresentationResponse } from "../types/contract";
import type { CommandInputMode, DecisionResultView } from "../types/visualModels";

interface CurrentTurnData {
  turn_id: string;
  semantic_frame: SemanticFrame;
}

interface BoundExecutionToken extends ExecutionTokenView {
  turnId: string;
}

function executionTokensFor(response: TextCommandResponse): BoundExecutionToken[] {
  const issuedTokens = response.decision?.execution_tokens || [];
  if (issuedTokens.length) {
    return issuedTokens.map((token) => ({ ...token, turnId: response.turn_id }));
  }
  const token = response.decision?.authorization_token;
  const intent = response.semantic_frame.intents?.[0];
  if (!token || !intent) return [];
  return [{
    token,
    turnId: response.turn_id,
    intent_id: intent.intent_id,
    label: `${intent.action} ${intent.target}`,
    action: intent.action,
    target: intent.target,
    area: intent.area,
  }];
}

const EMPTY_RESULT: DecisionResultView = {
  state: null,
  dimensions: ["C_sem", "C_cov", "C_trust", "C_jb", "C_nec"].map((dimension) => ({ id: dimension, dimension, detail: null })),
  score: null,
  reason: null,
};

function formatScoreDetail(value: number | null | undefined): string | null {
  if (value === null || value === undefined || !Number.isFinite(value)) return null;
  return `${(value * 100).toFixed(1)}%`;
}

function buildResultView(presentation: TurnPresentationResponse): DecisionResultView {
  const decision = presentation.decision_result;
  const score = presentation.score_result;
  if (!decision || !score) return EMPTY_RESULT;
  const dimensionValues = [
    score.semantic_clarity,
    score.evidence_support,
    score.evidence_trust,
    score.jailbreak_suppression,
    score.scene_necessity,
  ];
  const scored = dimensionValues.some((value) => value !== null && value !== undefined && Number.isFinite(value));
  const state: DecisionResultView["state"] = decision.final_decision === "PASS"
    ? "pass"
    : decision.final_decision === "REVIEW"
      ? "review"
      : decision.final_decision === "BLOCK"
        ? "reject"
        : null;
  return {
    state,
    dimensions: [
      { id: "C_sem", dimension: "C_sem", detail: formatScoreDetail(score.semantic_clarity) },
      { id: "C_cov", dimension: "C_cov", detail: formatScoreDetail(score.evidence_support) },
      { id: "C_trust", dimension: "C_trust", detail: formatScoreDetail(score.evidence_trust) },
      { id: "C_jb", dimension: "C_jb", detail: formatScoreDetail(score.jailbreak_suppression) },
      { id: "C_nec", dimension: "C_nec", detail: formatScoreDetail(score.scene_necessity) },
    ],
    score: scored ? formatScoreDetail(score.safety_score) : null,
    reason: decision.explanation?.trim() || decision.reasons?.join("、") || null,
  };
}

function asFiniteNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function commandScoreValues(response: TextCommandResponse) {
  const decision = response.decision;
  const firstIntentId = response.semantic_frame.intents?.[0]?.intent_id;
  const assessment = decision.intent_safety_assessments?.find((item) => item.intent_id === firstIntentId)
    || decision.intent_safety_assessments?.[0];
  if (assessment?.score) return assessment.score;

  const scoreFactors = decision.score_factors;
  if (!scoreFactors || typeof scoreFactors !== "object") return null;
  const fiveFactors = (scoreFactors as { five_factors?: unknown }).five_factors;
  if (!fiveFactors || typeof fiveFactors !== "object") return null;
  const factorValue = (name: string) => {
    const factor = (fiveFactors as Record<string, unknown>)[name];
    return factor && typeof factor === "object"
      ? asFiniteNumber((factor as { value?: unknown }).value)
      : null;
  };
  return {
    semantic_clarity: factorValue("Csem"),
    evidence_support: factorValue("Ccov"),
    evidence_trust: factorValue("Ctrust"),
    jailbreak_suppression: factorValue("Cjb"),
    scene_necessity: factorValue("Cnec"),
    safety_score: asFiniteNumber(decision.safety_score) ?? 0,
  };
}

function buildCommandResultView(response: TextCommandResponse): DecisionResultView {
  const decision = response.decision;
  const score = commandScoreValues(response);
  const state: DecisionResultView["state"] = decision.final_decision === "PASS"
    ? "pass"
    : decision.final_decision === "REVIEW"
      ? "review"
      : decision.final_decision === "BLOCK"
        ? "reject"
        : null;
  return {
    state,
    dimensions: [
      { id: "C_sem", dimension: "C_sem", detail: formatScoreDetail(score?.semantic_clarity) },
      { id: "C_cov", dimension: "C_cov", detail: formatScoreDetail(score?.evidence_support) },
      { id: "C_trust", dimension: "C_trust", detail: formatScoreDetail(score?.evidence_trust) },
      { id: "C_jb", dimension: "C_jb", detail: formatScoreDetail(score?.jailbreak_suppression) },
      { id: "C_nec", dimension: "C_nec", detail: formatScoreDetail(score?.scene_necessity) },
    ],
    score: formatScoreDetail(asFiniteNumber(decision.safety_score)),
    reason: decision.explanations?.join("、") || decision.gate_reasons?.join("、") || null,
  };
}

const MAX_WAV_SIZE_BYTES = 20 * 1024 * 1024;

export function DecisionPage() {
  const { setCoordinatedTurnGroup, updateCoordinatedTurnChild } = useSession();
  const [mode, setMode] = useState<CommandInputMode>("text");
  const [text, setText] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [currentTurn, setCurrentTurn] = useState<CurrentTurnData | null>(null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [clarification, setClarification] = useState<ClarificationRequest | null>(null);
  const [clarificationBusy, setClarificationBusy] = useState(false);
  const [clarificationError, setClarificationError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const activeRequestRef = useRef<AbortController | null>(null);
  const clarificationRequestRef = useRef<AbortController | null>(null);
  const turnId = searchParams.get("turn_id")?.trim() || null;
  const [result, setResult] = useState<DecisionResultView>(EMPTY_RESULT);
  const [execTokens, setExecTokens] = useState<BoundExecutionToken[]>([]);
  const [execResults, setExecResults] = useState<Record<string, ExecuteResult>>({});
  const [execBusyTurnId, setExecBusyTurnId] = useState<string | null>(null);
  const [childResults, setChildResults] = useState<CoordinatedCommandChild[]>([]);
  const [selectedChildIndex, setSelectedChildIndex] = useState<number | null>(null);
  const [parentSecurityBlocked, setParentSecurityBlocked] = useState(false);
  const [clarificationChildIndex, setClarificationChildIndex] = useState<number | null>(null);

  useEffect(() => {
    if (!turnId) {
      clarificationRequestRef.current?.abort("turn cleared");
      clarificationRequestRef.current = null;
      setClarification(null);
      setClarificationBusy(false);
      setClarificationError(null);
      setCurrentTurn(null);
      setResult(EMPTY_RESULT);
      return;
    }
    if (currentTurn?.turn_id === turnId) return;
    const preserveCurrentClarification = currentTurn?.turn_id === turnId;
    clarificationRequestRef.current?.abort("turn changed");
    clarificationRequestRef.current = null;
    if (!preserveCurrentClarification) {
      setClarification(null);
    }
    setClarificationBusy(false);
    setClarificationError(null);
    const controller = new AbortController();
    activeRequestRef.current?.abort("turn changed");
    activeRequestRef.current = controller;
    setBusy(true);
    setHasError(false);
    setFeedback(`正在读取轮次 ${turnId}…`);
    void getTurnPresentation(turnId, controller.signal).then((presentation) => {
      if (controller.signal.aborted) return;
      setCurrentTurn({
        turn_id: presentation.turn_id,
        semantic_frame: presentation.semantic_frame,
      });
      setResult(buildResultView(presentation));
      setClarification((existing) => (
        presentation.decision_result?.final_decision === "REVIEW"
          ? (presentation.clarification_request || (preserveCurrentClarification ? existing : null))
          : null
      ));
      setText(presentation.semantic_frame.raw_text);
      setFeedback(`已载入轮次 ${presentation.turn_id}`);
    }).catch((reason: unknown) => {
      if (controller.signal.aborted) return;
      setCurrentTurn(null);
      setResult(EMPTY_RESULT);
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "轮次语义帧读取失败");
    }).finally(() => {
      if (activeRequestRef.current === controller) {
        activeRequestRef.current = null;
        setBusy(false);
      }
    });
    return () => controller.abort("decision page effect disposed");
  }, [turnId]);

  useEffect(() => () => {
    activeRequestRef.current?.abort("decision page disposed");
    clarificationRequestRef.current?.abort("decision page disposed");
  }, []);

  const changeMode = useCallback((nextMode: CommandInputMode) => {
    setMode(nextMode);
    setFeedback(null);
    setHasError(false);
    if (nextMode !== "microphone") setRecording(false);
  }, []);
  const selectAudio = useCallback((file: File | null) => {
    setAudioFile(file);
    setFeedback(null);
    setHasError(false);
  }, []);

  const acceptResponse = useCallback((response: TextCommandResponse | AudioCommandResponse, successMessage: string) => {
    setCoordinatedTurnGroup(null);
    setChildResults([]);
    setSelectedChildIndex(null);
    const frame = response.semantic_frame;
    if (frame) {
      setCurrentTurn({ turn_id: response.turn_id, semantic_frame: frame });
      setText(frame.raw_text);
    } else {
      setCurrentTurn(null);
    }
    const nestedClarification = (response as AudioCommandResponse).pipeline
      ?.clarification_request;
    setClarification(response.clarification_request || nestedClarification || null);
    setClarificationError(null);
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set("turn_id", response.turn_id);
    setSearchParams(nextParams, { replace: true });
    setFeedback(`${successMessage}，轮次 ${response.turn_id}`);
  }, [searchParams, setCoordinatedTurnGroup, setSearchParams]);

  const runAudioRequest = useCallback((request: (signal: AbortSignal) => Promise<AudioCommandResponse>, pendingMessage: string, successMessage: string) => {
    const controller = new AbortController();
    activeRequestRef.current?.abort("new audio command submitted");
    activeRequestRef.current = controller;
    setBusy(true);
    setHasError(false);
    setFeedback(pendingMessage);
    void request(controller.signal).then((response) => {
      if (controller.signal.aborted) return;
      acceptResponse(response, successMessage);
    }).catch((reason: unknown) => {
      if (controller.signal.aborted) return;
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "语音指令处理失败");
    }).finally(() => {
      if (activeRequestRef.current === controller) {
        activeRequestRef.current = null;
        setBusy(false);
        setRecording(false);
      }
    });
  }, [acceptResponse]);

  const captureMicrophone = useCallback(() => {
    setRecording(true);
    runAudioRequest(
      (signal) => submitMicrophoneCommand({ duration_seconds: 4, speaker_zone: "driver", speaker_role: "driver" }, signal),
      "正在调用本机麦克风采集 4 秒语音…",
      "本机语音处理完成",
    );
  }, [runAudioRequest]);

  const submit = useCallback(() => {
    if (mode === "audio") {
      if (!audioFile) {
        setHasError(true);
        setFeedback("请先选择 WAV 音频文件。");
        return;
      }
      if (!audioFile.name.toLowerCase().endsWith(".wav")) {
        setHasError(true);
        setFeedback("当前仅支持未压缩 PCM WAV 文件。");
        return;
      }
      if (audioFile.size === 0 || audioFile.size > MAX_WAV_SIZE_BYTES) {
        setHasError(true);
        setFeedback(audioFile.size === 0 ? "WAV 文件不能为空。" : "WAV 文件不能超过 20 MiB。");
        return;
      }
      runAudioRequest(
        (signal) => submitAudioCommand(audioFile, { audio_source: "browser_upload", speaker_zone: "driver", speaker_role: "driver" }, signal),
        "正在上传并处理 WAV 音频…",
        "WAV 音频处理完成",
      );
      return;
    }
    if (mode === "microphone") return;
    const commandText = text.trim();
    if (!commandText) {
      setHasError(true);
      setFeedback("请输入文本指令。");
      return;
    }
    const controller = new AbortController();
    activeRequestRef.current?.abort("new command submitted");
    activeRequestRef.current = controller;
    setBusy(true);
    setHasError(false);
    setFeedback("正在解析语义帧…");
    void submitCoordinatedTextCommand({ text: commandText }, controller.signal).then((response) => {
      if (controller.signal.aborted) return;
      setText(commandText);
      setExecResults({});
      setExecBusyTurnId(null);
      const children = response.mode === "MULTI" ? response.children : [];
      setChildResults(children);
      setSelectedChildIndex(children[0]?.clause_index ?? null);
      setCoordinatedTurnGroup(children.length ? {
        parentTurnId: response.parent_turn_id,
        children: children.map((child) => ({ clauseIndex: child.clause_index, clauseText: child.clause_text, turnId: child.turn_id })),
      } : null);
      setParentSecurityBlocked(response.blocked_by_parent_security);
      setClarificationChildIndex(null);
      setClarificationError(null);
      const nextParams = new URLSearchParams(searchParams);
      if (response.mode === "SINGLE" && response.children[0]) {
        const child = response.children[0].response;
        setExecTokens(executionTokensFor(child));
        setResult(buildCommandResultView(child));
        setCurrentTurn({ turn_id: child.turn_id, semantic_frame: child.semantic_frame });
        setClarification(child.clarification_request || null);
        nextParams.set("turn_id", child.turn_id);
        setSearchParams(nextParams, { replace: true });
      } else {
        setExecTokens([]);
        setCurrentTurn({ turn_id: response.parent_turn_id, semantic_frame: response.parent_frame });
        setResult(EMPTY_RESULT);
        setClarification(null);
      }
      setFeedback(response.blocked_by_parent_security
        ? "父级安全检查已阻止全部子句处理"
        : response.mode === "MULTI"
          ? `已按原始顺序完成 ${response.children.length} 个独立子轮次`
          : `语义帧解析完成，轮次 ${response.children[0]?.turn_id ?? response.parent_turn_id}`);
    }).catch((reason: unknown) => {
      if (controller.signal.aborted) return;
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "文本指令提交失败");
    }).finally(() => {
      if (activeRequestRef.current === controller) {
        activeRequestRef.current = null;
        setBusy(false);
      }
    });
  }, [audioFile, mode, runAudioRequest, searchParams, setCoordinatedTurnGroup, setSearchParams, text]);

  const execute = useCallback(async (executionTurnId: string, token: string, intentId?: string) => {
    if (!executionTurnId || !token) {
      setHasError(true);
      setFeedback("当前轮次没有可用的执行令牌。");
      return;
    }
    setExecBusyTurnId(executionTurnId);
    setHasError(false);
    setFeedback("正在执行车辆动作…");
    try {
      const result = await executeTurn(executionTurnId, token, intentId);
      setExecResults((existing) => ({ ...existing, [executionTurnId]: result }));
      setFeedback(result.accepted
        ? `执行成功 ✓ ${result.execution?.feedback ?? result.reason}`
        : `执行未接受：${result.reason}`);
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "执行失败");
    } finally {
      setExecBusyTurnId(null);
    }
  }, []);

  const resolveClarification = useCallback((candidateIds: string[] | null) => {
    if (!clarification || clarificationBusy) return;
    const capturedKey = `${clarification.turn_id}:${clarification.clarification_id}`;
    const controller = new AbortController();
    clarificationRequestRef.current?.abort("new clarification submitted");
    clarificationRequestRef.current = controller;
    setClarificationBusy(true);
    setClarificationError(null);
    const selected = candidateIds?.length
      ? (candidateIds.length === 1
        ? { clarification_id: clarification.clarification_id, candidate_id: candidateIds[0] }
        : { clarification_id: clarification.clarification_id, candidate_ids: candidateIds })
      : { clarification_id: clarification.clarification_id, resolution: "NONE_OF_ABOVE" as const };
    void submitTurnClarification(
      clarification.turn_id,
      selected,
      controller.signal,
    ).then((response) => {
      if (controller.signal.aborted) return;
      const currentKey = clarification
        ? `${clarification.turn_id}:${clarification.clarification_id}`
        : null;
      if (currentKey !== capturedKey) return;
      if (response.resolution === "NONE_OF_ABOVE") {
        setClarification(null);
        if (clarificationChildIndex === null) {
          setText("");
          setAudioFile(null);
          setRecording(false);
        }
        setClarificationChildIndex(null);
        setFeedback(clarificationChildIndex === null
          ? "本轮已结束，请重新说一条完整指令。"
          : "本次复核已结束；其余子句结果保持不变。请重新提交完整指令以开始新的安全轮次。");
        setHasError(false);
        return;
      }
      const child = response.command_result;
      if (!child || !response.child_turn_id) throw new Error("后端未返回确认后的 child turn");
      if (clarificationChildIndex !== null) {
        setChildResults((existing) => existing.map((item) => (
          item.clause_index === clarificationChildIndex
            ? { ...item, turn_id: child.turn_id, clause_text: child.semantic_frame.raw_text, response: child }
            : item
        )));
        updateCoordinatedTurnChild(clarificationChildIndex, { turnId: child.turn_id, clauseText: child.semantic_frame.raw_text });
        setClarification(child.clarification_request || null);
        setClarificationChildIndex(child.clarification_request ? clarificationChildIndex : null);
        setFeedback(`复核澄清已作为新的完整安全轮次处理：${child.turn_id}`);
        setHasError(false);
        return;
      }
      setCurrentTurn({ turn_id: child.turn_id, semantic_frame: child.semantic_frame });
      setText(child.semantic_frame.raw_text);
      setClarification(child.clarification_request || null);
      setExecTokens(executionTokensFor(child));
      setResult(buildCommandResultView(child));
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set("turn_id", child.turn_id);
      setSearchParams(nextParams, { replace: true });
      setFeedback(`已按用户确认重新运行完整安全流水线，轮次 ${child.turn_id}`);
      setHasError(false);
    }).catch((reason: unknown) => {
      if (controller.signal.aborted) return;
      setClarificationError(reason instanceof Error ? reason.message : "确认提交失败，请重试");
    }).finally(() => {
      if (clarificationRequestRef.current === controller) {
        clarificationRequestRef.current = null;
        setClarificationBusy(false);
      }
    });
  }, [clarification, clarificationBusy, clarificationChildIndex, searchParams, setSearchParams, updateCoordinatedTurnChild]);

  const selectedChild = childResults.find((child) => child.clause_index === selectedChildIndex) || childResults[0] || null;
  const visibleResult = selectedChild ? buildCommandResultView(selectedChild.response) : result;
  const visibleExecTokens = selectedChild ? executionTokensFor(selectedChild.response) : execTokens;
  const visibleTurnId = selectedChild?.turn_id || currentTurn?.turn_id || turnId;
  const visibleExecResult = visibleTurnId ? execResults[visibleTurnId] || null : null;
  const childSelector = childResults.length > 1 ? <label className="decision-child-selector">
    <span>当前子意图</span>
    <select
      aria-label="选择当前查看的子意图"
      value={selectedChild?.clause_index ?? ""}
      onChange={(event) => setSelectedChildIndex(Number(event.target.value))}
    >
      {childResults.map((child, index) => <option key={`${child.clause_index}:${child.turn_id}`} value={child.clause_index}>
        {`子意图 ${index + 1} · ${child.clause_text}`}
      </option>)}
    </select>
  </label> : null;

  return <><div className="visual-page-frame decision-visual-page"><div className="decision-visual-layout">
    <div className="decision-visual-left">
      <CommandInputSwitcher mode={mode} text={text} audioFileName={audioFile?.name || ""} recording={recording} busy={busy} feedback={feedback} hasError={hasError} onModeChange={changeMode} onTextChange={setText} onAudioChange={selectAudio} onRecordingToggle={captureMicrophone} onSubmit={submit} />
      <SemanticFrameDisplay frame={currentTurn?.semantic_frame || null} />
    </div>
    <div className="decision-result-column">
      <div className="decision-child-detail-card">
        <DecisionResultDisplay result={visibleResult} selector={childSelector} />
        <section className="decision-execution-panel">
        <div className="decision-execution-actions">
          {visibleExecTokens.length === 0 ? <button
            type="button"
            disabled
            className="decision-execution-button"
          >无执行令牌</button> : visibleExecTokens.map((executionToken) => <button
            key={executionToken.token}
            type="button"
            disabled={execBusyTurnId === executionToken.turnId}
            onClick={() => void execute(executionToken.turnId, executionToken.token, executionToken.intent_id || undefined)}
            className="decision-execution-button"
          >
            {execBusyTurnId === executionToken.turnId ? "执行中…" : executionToken.label ? `执行${executionToken.label}` : "执行车辆动作"}
          </button>)}
          {selectedChild?.response.clarification_request ? <button
            className="decision-child-review-button"
            disabled={clarificationBusy}
            onClick={() => {
              setClarificationChildIndex(selectedChild.clause_index);
              setClarification(selectedChild.response.clarification_request || null);
            }}
            type="button"
          >处理此子意图复核</button> : null}
        </div>
        {visibleExecResult && (
          <div className={`decision-execution-result${visibleExecResult.accepted ? " is-accepted" : " is-rejected"}`}>
            <strong>{visibleExecResult.accepted ? "执行成功" : "执行未接受"}</strong>
            <span>{visibleExecResult.reason}</span>
            {visibleExecResult.execution && <div>
              适配器 {visibleExecResult.execution.adapter} · 状态 {visibleExecResult.execution.status} · {visibleExecResult.execution.feedback}
            </div>}
          </div>
        )}
        </section>
      </div>
      {parentSecurityBlocked ? <section className="decision-child-results is-blocked" role="alert">
        父语义帧检测到安全信号，未创建任何子轮次，也未产生授权令牌。
      </section> : null}
    </div>
  </div></div>{clarification ? <ClarificationModal
    error={clarificationError}
    onNoneOfAbove={() => resolveClarification(null)}
    onSelect={resolveClarification}
    request={clarification}
    submitting={clarificationBusy}
  /> : null}</>;
}
