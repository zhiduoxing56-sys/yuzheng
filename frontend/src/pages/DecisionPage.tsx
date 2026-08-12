import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { submitTextCommand } from "../api/command";
import { executeTurn, getTurnPresentation } from "../api/turns";
import { CommandInputSwitcher, DecisionResultDisplay, SemanticFrameDisplay } from "../components/DecisionVisuals";
import type { EvidenceDemandPresentation, ExecuteResult, SemanticFrame, TurnPresentationResponse } from "../types/contract";
import type { CommandInputMode, DecisionResultView } from "../types/visualModels";

interface CurrentTurnData {
  turn_id: string;
  semantic_frame: SemanticFrame;
  evidence_demand: EvidenceDemandPresentation;
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

export function DecisionPage() {
  const [mode, setMode] = useState<CommandInputMode>("text");
  const [text, setText] = useState("");
  const [audioFileName, setAudioFileName] = useState("");
  const [recording, setRecording] = useState(false);
  const [currentTurn, setCurrentTurn] = useState<CurrentTurnData | null>(null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const activeRequestRef = useRef<AbortController | null>(null);
  const turnId = searchParams.get("turn_id")?.trim() || null;
  const [result, setResult] = useState<DecisionResultView>(EMPTY_RESULT);
  const [execToken, setExecToken] = useState<string | null>(null);
  const [execResult, setExecResult] = useState<ExecuteResult | null>(null);
  const [execBusy, setExecBusy] = useState(false);

  useEffect(() => {
    if (!turnId) {
      setCurrentTurn(null);
      setResult(EMPTY_RESULT);
      return;
    }
    if (currentTurn?.turn_id === turnId) return;
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
        evidence_demand: presentation.evidence_demand,
      });
      setResult(buildResultView(presentation));
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

  useEffect(() => () => activeRequestRef.current?.abort("decision page disposed"), []);

  const changeMode = useCallback((nextMode: CommandInputMode) => {
    setMode(nextMode);
    setFeedback(null);
    setHasError(false);
    if (nextMode !== "microphone") setRecording(false);
  }, []);
  const selectAudio = useCallback((file: File | null) => setAudioFileName(file?.name || ""), []);
  const submit = useCallback(() => {
    if (mode !== "text") {
      setHasError(true);
      setFeedback("本轮只接入文本指令；音频与麦克风尚未连接。");
      return;
    }
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
  }, [mode, searchParams, setSearchParams, text]);

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

  return <div className="visual-page-frame decision-visual-page"><div className="decision-visual-layout">
    <div className="decision-visual-left">
      <CommandInputSwitcher mode={mode} text={text} audioFileName={audioFileName} recording={recording} busy={busy} feedback={feedback} hasError={hasError} onModeChange={changeMode} onTextChange={setText} onAudioChange={selectAudio} onRecordingToggle={() => setRecording((current) => !current)} onSubmit={submit} />
      <SemanticFrameDisplay frame={currentTurn?.semantic_frame || null} />
    </div>
    <DecisionResultDisplay result={result} />
    <div style={{ marginTop: "1rem" }}>
      <section style={{ background: "#0f1420", border: "1px solid #232b3b", borderRadius: 12, padding: "1rem 1.25rem" }}>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap" }}>
          <button
            type="button"
            disabled={execBusy || !execToken}
            onClick={() => void execute()}
            style={{
              background: execToken ? "#1b7cff" : "#2c3850",
              color: "#fff", border: "none", borderRadius: 8,
              padding: "0.5rem 1.1rem", cursor: execToken ? "pointer" : "not-allowed",
              fontWeight: 600, opacity: execToken ? 1 : 0.5,
            }}
          >
            {execBusy ? "执行中…" : execToken ? "执行车辆动作" : "无执行令牌"}
          </button>
          {execToken && <span style={{ color: "#5c6675", fontSize: "0.8rem" }}>令牌已签发，点击执行将把动作反映到 CARLA 车辆</span>}
        </div>
        {!execToken && <p style={{ color: "#5c6675", fontSize: "0.78rem", margin: "0.5rem 0 0" }}>本指令未签发执行令牌（可能是 REVIEW/BLOCK 或不在可执行白名单）。</p>}
        {execResult && (
          <div style={{
            marginTop: "0.75rem", padding: "0.6rem 0.8rem", borderRadius: 8, fontSize: "0.85rem",
            background: execResult.accepted ? "rgba(27,124,255,0.12)" : "rgba(220,60,60,0.15)",
            color: execResult.accepted ? "#7cc4ff" : "#ff8b8b",
          }}>
            <strong>{execResult.accepted ? "执行成功" : "执行未接受"}</strong>
            <span style={{ marginLeft: "0.5rem" }}>{execResult.reason}</span>
            {execResult.execution && <div style={{ marginTop: "0.3rem", color: "#aeb9cc" }}>
              适配器 {execResult.execution.adapter} · 状态 {execResult.execution.status} · {execResult.execution.feedback}
            </div>}
          </div>
        )}
        <p style={{ color: "#5c6675", fontSize: "0.78rem", margin: "0.6rem 0 0" }}>
          提示：如果执行被「签发后状态变化」拒绝，请先到「模拟器」页点「驻车/制动(0)」让车辆停稳，再重新提交执行。
        </p>
      </section>
    </div>
  </div></div>;
}
