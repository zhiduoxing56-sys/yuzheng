import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { submitAudioCommand, submitMicrophoneCommand, submitTextCommand } from "../api/command";
import { executeTurn, getTurnPresentation, submitTurnClarification } from "../api/turns";
import { ClarificationModal } from "../components/ClarificationModal";
import { CommandInputSwitcher, DecisionResultDisplay, SemanticFrameDisplay } from "../components/DecisionVisuals";
import type { AudioCommandResponse, ClarificationRequest, ExecuteResult, SemanticFrame, TextCommandResponse, TurnPresentationResponse } from "../types/contract";
import type { CommandInputMode, DecisionResultView } from "../types/visualModels";

interface CurrentTurnData {
  turn_id: string;
  semantic_frame: SemanticFrame;
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
    score: formatScoreDetail(score.safety_score),
    reason: decision.explanation?.trim() || decision.reasons?.join("、") || null,
  };
}

const MAX_WAV_SIZE_BYTES = 20 * 1024 * 1024;

export function DecisionPage() {
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
  const [execToken, setExecToken] = useState<string | null>(null);
  const [execResult, setExecResult] = useState<ExecuteResult | null>(null);
  const [execBusy, setExecBusy] = useState(false);

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
  }, [searchParams, setSearchParams]);

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
    void submitTextCommand({ text: commandText }, controller.signal).then((response) => {
      if (controller.signal.aborted) return;
      setText(commandText);
      setExecToken((response.decision as { authorization_token?: string | null } | undefined)?.authorization_token ?? null);
      setExecResult(null);
      setCurrentTurn({
        turn_id: response.turn_id,
        semantic_frame: response.semantic_frame,
      });
      setClarification(response.clarification_request || null);
      setClarificationError(null);
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set("turn_id", response.turn_id);
      setSearchParams(nextParams, { replace: true });
      setFeedback(`语义帧解析完成，轮次 ${response.turn_id}${execToken ? "" : ""}`);
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
  }, [audioFile, mode, runAudioRequest, searchParams, setSearchParams, text]);

  const execute = useCallback(async () => {
    if (!turnId || !execToken) {
      setHasError(true);
      setFeedback("当前轮次没有可用的执行令牌。");
      return;
    }
    setExecBusy(true);
    setHasError(false);
    setFeedback("正在执行车辆动作…");
    try {
      const result = await executeTurn(turnId, execToken);
      setExecResult(result);
      setFeedback(result.accepted
        ? `执行成功 ✓ ${result.execution?.feedback ?? result.reason}`
        : `执行未接受：${result.reason}`);
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "执行失败");
    } finally {
      setExecBusy(false);
    }
  }, [turnId, execToken]);

  const resolveClarification = useCallback((candidateId: string | null) => {
    if (!clarification || clarificationBusy) return;
    const capturedKey = `${clarification.turn_id}:${clarification.clarification_id}`;
    const controller = new AbortController();
    clarificationRequestRef.current?.abort("new clarification submitted");
    clarificationRequestRef.current = controller;
    setClarificationBusy(true);
    setClarificationError(null);
    void submitTurnClarification(
      clarification.turn_id,
      candidateId
        ? { clarification_id: clarification.clarification_id, candidate_id: candidateId }
        : { clarification_id: clarification.clarification_id, resolution: "NONE_OF_ABOVE" },
      controller.signal,
    ).then((response) => {
      if (controller.signal.aborted) return;
      const currentKey = clarification
        ? `${clarification.turn_id}:${clarification.clarification_id}`
        : null;
      if (currentKey !== capturedKey) return;
      if (response.resolution === "NONE_OF_ABOVE") {
        setClarification(null);
        setText("");
        setAudioFile(null);
        setRecording(false);
        setFeedback("本轮已结束，请重新说一条完整指令。");
        setHasError(false);
        return;
      }
      const child = response.command_result;
      if (!child || !response.child_turn_id) throw new Error("后端未返回确认后的 child turn");
      setCurrentTurn({ turn_id: child.turn_id, semantic_frame: child.semantic_frame });
      setText(child.semantic_frame.raw_text);
      setClarification(child.clarification_request || null);
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
  }, [clarification, clarificationBusy, searchParams, setSearchParams]);

  return <><div className="visual-page-frame decision-visual-page"><div className="decision-visual-layout">
    <div className="decision-visual-left">
      <CommandInputSwitcher mode={mode} text={text} audioFileName={audioFile?.name || ""} recording={recording} busy={busy} feedback={feedback} hasError={hasError} onModeChange={changeMode} onTextChange={setText} onAudioChange={selectAudio} onRecordingToggle={captureMicrophone} onSubmit={submit} />
      <SemanticFrameDisplay frame={currentTurn?.semantic_frame || null} />
    </div>
    <div className="decision-result-column">
      <DecisionResultDisplay result={result} />
      <section className="decision-execution-panel">
        <div className="decision-execution-actions">
          <button
            type="button"
            disabled={execBusy || !execToken}
            onClick={() => void execute()}
            className="decision-execution-button"
          >
            {execBusy ? "执行中…" : execToken ? "执行车辆动作" : "无执行令牌"}
          </button>
          {execToken && <span>令牌已签发，点击执行将把动作反映到 CARLA 车辆</span>}
        </div>
        {!execToken && <p className="decision-execution-note">本指令未签发执行令牌（可能是 REVIEW/BLOCK 或不在可执行白名单）。</p>}
        {execResult && (
          <div className={`decision-execution-result${execResult.accepted ? " is-accepted" : " is-rejected"}`}>
            <strong>{execResult.accepted ? "执行成功" : "执行未接受"}</strong>
            <span>{execResult.reason}</span>
            {execResult.execution && <div>
              适配器 {execResult.execution.adapter} · 状态 {execResult.execution.status} · {execResult.execution.feedback}
            </div>}
          </div>
        )}
        <p className="decision-execution-hint">
          提示：如果执行被「签发后状态变化」拒绝，请先到「模拟器」页点「驻车/制动(0)」让车辆停稳，再重新提交执行。
        </p>
      </section>
    </div>
  </div></div>{clarification ? <ClarificationModal
    error={clarificationError}
    onNoneOfAbove={() => resolveClarification(null)}
    onSelect={resolveClarification}
    request={clarification}
    submitting={clarificationBusy}
  /> : null}</>;
}
