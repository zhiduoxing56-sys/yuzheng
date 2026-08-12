import { useCallback, useEffect, useRef, useState } from "react";
import { CommandInputPanel } from "../components/CommandInputPanel";
import { SafetyDecisionPanel } from "../components/SafetyDecisionPanel";
import { SemanticFrameJsonPanel } from "../components/SemanticFrameJsonPanel";
import {
  resolvePresentationOutcome,
  useCommandSubmission,
  type AudioSubmissionInput,
  type MicrophoneSubmissionInput,
  type TextSubmissionInput,
} from "../hooks/useCommandSubmission";
import { useHealthStatus } from "../hooks/useHealthStatus";
import { useTurnPresentation } from "../hooks/useTurnPresentation";
import { useSession } from "../stores/sessionStore";
import type { AdaptedCommandResponse } from "../adapters/commandResponseAdapter";

export function DecisionPage() {
  const { sessionId, activeTurnId, setActiveTurn } = useSession();
  const [viewTurnId, setViewTurnId] = useState<string | null>(activeTurnId);
  const [endToEndMs, setEndToEndMs] = useState<number | null>(null);
  const [latencyPending, setLatencyPending] = useState(false);
  const latencyStartedAtRef = useRef<number | null>(null);
  const health = useHealthStatus();
  const presentation = useTurnPresentation(viewTurnId);

  const onAccepted = useCallback((result: AdaptedCommandResponse) => {
    setActiveTurn(result.turnId, {
      instructionSummary: result.instructionSummary,
      decision: result.preliminaryDecision,
      createdAt: new Date().toISOString(),
    });
    setViewTurnId(result.turnId);
  }, [setActiveTurn]);

  const submission = useCommandSubmission({
    sessionId,
    backendAvailable: health.available,
    onAccepted,
    onBeforeSubmit: () => setViewTurnId(null),
  });

  const beginEndToEndMeasurement = useCallback(() => {
    latencyStartedAtRef.current = performance.now();
    setEndToEndMs(null);
    setLatencyPending(true);
  }, []);

  const submitText = useCallback(async (input: TextSubmissionInput) => {
    beginEndToEndMeasurement();
    await submission.submitText(input);
  }, [beginEndToEndMeasurement, submission.submitText]);

  const submitAudio = useCallback(async (input: AudioSubmissionInput) => {
    beginEndToEndMeasurement();
    await submission.submitAudio(input);
  }, [beginEndToEndMeasurement, submission.submitAudio]);

  const submitMicrophone = useCallback(async (input: MicrophoneSubmissionInput) => {
    beginEndToEndMeasurement();
    await submission.submitMicrophone(input);
  }, [beginEndToEndMeasurement, submission.submitMicrophone]);

  useEffect(() => {
    const outcome = resolvePresentationOutcome(
      submission.status,
      Boolean(presentation.data && presentation.data.turn_id === submission.immediateResult?.turnId),
      presentation.exhausted,
      presentation.error,
    );
    if (outcome === "completed") {
      submission.markCompleted();
      if (latencyStartedAtRef.current !== null) {
        setEndToEndMs(performance.now() - latencyStartedAtRef.current);
        latencyStartedAtRef.current = null;
        setLatencyPending(false);
      }
    } else if (outcome === "partial") {
      submission.markPartial();
      latencyStartedAtRef.current = null;
      setLatencyPending(false);
    } else if (outcome === "failed") {
      submission.markPresentationFailed(`最终展示读取失败：${presentation.error}`);
    }
  }, [
    presentation.data,
    presentation.error,
    presentation.exhausted,
    submission.immediateResult?.turnId,
    submission.markCompleted,
    submission.markPartial,
    submission.markPresentationFailed,
    submission.status,
  ]);

  useEffect(() => {
    if (submission.status !== "failed") return;
    latencyStartedAtRef.current = null;
    setLatencyPending(false);
  }, [submission.status]);

  const resultError = presentation.error;
  const retryPresentation = useCallback(() => {
    submission.retryPresentation();
    presentation.retry();
  }, [presentation.retry, submission.retryPresentation]);

  return <div className="decision-redesign">
    <main className="decision-workspace">
      <div className="decision-left-column">
        <CommandInputPanel
          sessionId={sessionId}
          status={submission.status}
          busy={submission.busy}
          error={submission.error}
          draftResetVersion={submission.immediateResult?.turnId}
          onSubmitText={submitText}
          onSubmitAudio={submitAudio}
          onSubmitMicrophone={submitMicrophone}
        />
        <SemanticFrameJsonPanel
          data={presentation.data}
          loading={presentation.loading || submission.busy}
          error={resultError}
          onRetry={retryPresentation}
        />
      </div>

      <SafetyDecisionPanel
        data={presentation.data}
        loading={presentation.loading}
        processing={submission.busy}
        error={resultError}
        onRetry={retryPresentation}
      />
    </main>

    <footer className="decision-runtime-footer">
      <div className={`runtime-status ${health.available ? "healthy" : health.loading ? "checking" : "unhealthy"}`}>
        <span aria-hidden="true" />
        <strong>{health.available ? "系统运行正常" : health.loading ? "状态检测中" : "系统运行异常"}</strong>
      </div>
      <div className="runtime-latency" title="从用户提交指令到最终持久化裁决结果在页面可用的实测时间">
        <span>端到端耗时：</span>
        <strong>{latencyPending ? "测量中…" : endToEndMs === null ? "—" : `${Math.round(endToEndMs)} ms`}</strong>
      </div>
    </footer>
  </div>;
}
