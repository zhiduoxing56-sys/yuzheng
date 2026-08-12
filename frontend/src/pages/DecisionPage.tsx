import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { submitTextCommand } from "../api/command";
import { getTurnPresentation } from "../api/turns";
import { CommandInputSwitcher, DecisionResultDisplay, SemanticFrameDisplay } from "../components/DecisionVisuals";
import type { EvidenceDemandPresentation, SemanticFrame } from "../types/contract";
import type { CommandInputMode, DecisionResultView } from "../types/visualModels";

interface CurrentTurnData {
  turn_id: string;
  semantic_frame: SemanticFrame;
  evidence_demand: EvidenceDemandPresentation;
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
  const result = useMemo<DecisionResultView>(() => ({
    state: null,
    dimensions: ["C_sem", "C_cov", "C_trust", "C_jb", "C_nec"].map((dimension) => ({ id: dimension, dimension, detail: null })),
    score: null,
    reason: null,
  }), []);

  useEffect(() => {
    if (!turnId) {
      setCurrentTurn(null);
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
      setText(presentation.semantic_frame.raw_text);
      setFeedback(`已载入轮次 ${presentation.turn_id}`);
    }).catch((reason: unknown) => {
      if (controller.signal.aborted) return;
      setCurrentTurn(null);
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
      setCurrentTurn({
        turn_id: response.turn_id,
        semantic_frame: response.semantic_frame,
        evidence_demand: response.evidence_demand,
      });
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set("turn_id", response.turn_id);
      setSearchParams(nextParams, { replace: true });
      setFeedback(`语义帧解析完成，轮次 ${response.turn_id}`);
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

  return <div className="visual-page-frame decision-visual-page"><div className="decision-visual-layout">
    <div className="decision-visual-left">
      <CommandInputSwitcher mode={mode} text={text} audioFileName={audioFileName} recording={recording} busy={busy} feedback={feedback} hasError={hasError} onModeChange={changeMode} onTextChange={setText} onAudioChange={selectAudio} onRecordingToggle={() => setRecording((current) => !current)} onSubmit={submit} />
      <SemanticFrameDisplay frame={currentTurn?.semantic_frame || null} />
    </div>
    <DecisionResultDisplay result={result} />
  </div></div>;
}
