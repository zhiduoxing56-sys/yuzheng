import { useCallback, useEffect, useRef, useState } from "react";
import { submitAudioCommand, submitMicrophoneCommand, submitTextCommand } from "../api/command";
import { adaptAudioCommandResponse, adaptTextCommandResponse, type AdaptedCommandResponse } from "../adapters/commandResponseAdapter";
import { MAX_AUDIO_FILE_SIZE_BYTES, MAX_AUDIO_FILE_SIZE_LABEL, SUPPORTED_AUDIO_EXTENSIONS } from "../constants";
import type { EvidenceObservationInput, SubmissionStatus, VehicleState } from "../types/contract";
import { clearCommandDraft, saveLastSubmission } from "../utils/commandSessionStorage";
import { invalidateTurnReads, readCache } from "../cache/readCache";

export interface CommonCommandInput {
  speakerZone: string;
  speakerRole: string;
}

export interface TextSubmissionInput extends CommonCommandInput {
  text: string;
  stateOverridesJson: string;
  evidenceOverridesJson: string;
}

export interface AudioSubmissionInput extends CommonCommandInput {
  file: File | null;
  audioSource: string;
  arrayChannel: string;
  channelIndex: string;
}

export interface MicrophoneSubmissionInput extends CommonCommandInput {
  durationSeconds: number;
  device: string;
  stateOverridesJson: string;
}

export function resolvePresentationOutcome(status: SubmissionStatus, hasMatchingData: boolean, exhausted: boolean, error: string | null): "completed" | "partial" | "failed" | null {
  if (status !== "waiting_presentation") return null;
  if (hasMatchingData) return "completed";
  if (exhausted) return "partial";
  if (error) return "failed";
  return null;
}

interface Options {
  sessionId: string;
  backendAvailable: boolean;
  onAccepted: (result: AdaptedCommandResponse) => void;
  onBeforeSubmit: () => void;
}

function parseObjectJson(value: string, label: string): Partial<VehicleState> | undefined {
  if (!value.trim()) return undefined;
  const parsed: unknown = JSON.parse(value);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error(`${label} 必须是 JSON 对象`);
  return parsed as Partial<VehicleState>;
}

function parseEvidenceJson(value: string): EvidenceObservationInput[] | undefined {
  if (!value.trim()) return undefined;
  const parsed: unknown = JSON.parse(value);
  if (!Array.isArray(parsed) || parsed.some((item) => !item || typeof item !== "object" || Array.isArray(item))) {
    throw new Error("evidence_overrides 必须是 JSON 对象数组");
  }
  return parsed as EvidenceObservationInput[];
}

function audioExtension(file: File): string {
  return file.name.split(".").pop()?.toLowerCase() || "";
}

export function useCommandSubmission({ sessionId, backendAvailable, onAccepted, onBeforeSubmit }: Options) {
  const [status, setStatus] = useState<SubmissionStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [immediateResult, setImmediateResult] = useState<AdaptedCommandResponse | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => () => controllerRef.current?.abort(), []);

  const run = useCallback(async (request: (signal: AbortSignal) => Promise<unknown>, adapt: (raw: unknown) => AdaptedCommandResponse) => {
    setStatus("validating");
    setError(null);
    if (!backendAvailable) {
      setStatus("failed");
      setError("后端当前不可用，请等待健康状态恢复或手动刷新");
      return;
    }
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    onBeforeSubmit();
    setStatus("submitting");
    try {
      setStatus("processing");
      const result = adapt(await request(controller.signal));
      if (controller.signal.aborted) return;
      invalidateTurnReads(result.turnId);
      readCache.invalidatePrefix("audits:");
      setImmediateResult(result);
      clearCommandDraft(sessionId);
      saveLastSubmission(sessionId, {
        text: result.instructionSummary,
        inputType: result.inputType,
        source: result.summarySource,
        turnId: result.turnId,
        submittedAt: new Date().toISOString(),
        preliminaryDecision: result.preliminaryDecision,
      });
      setStatus("waiting_presentation");
      onAccepted(result);
    } catch (reason) {
      if (controller.signal.aborted) return;
      setStatus("failed");
      setError(reason instanceof Error ? reason.message : "指令处理失败");
    }
  }, [backendAvailable, onAccepted, onBeforeSubmit, sessionId]);

  const submitText = useCallback(async (input: TextSubmissionInput) => {
    try {
      const text = input.text.trim();
      if (!text) throw new Error("指令文本不能为空");
      const state_overrides = parseObjectJson(input.stateOverridesJson, "state_overrides");
      const evidence_overrides = parseEvidenceJson(input.evidenceOverridesJson);
      await run((signal) => submitTextCommand({
        text,
        speaker_zone: input.speakerZone,
        speaker_role: input.speakerRole,
        session_id: sessionId,
        ...(state_overrides ? { state_overrides } : {}),
        ...(evidence_overrides ? { evidence_overrides } : {}),
      }, signal), (raw) => adaptTextCommandResponse(raw, text));
    } catch (reason) {
      setStatus("failed");
      setError(reason instanceof SyntaxError ? "高级参数不是有效 JSON" : reason instanceof Error ? reason.message : "输入校验失败");
    }
  }, [run, sessionId]);

  const submitAudio = useCallback(async (input: AudioSubmissionInput) => {
    try {
      if (!input.file) throw new Error("请先选择音频文件");
      if (input.file.size > MAX_AUDIO_FILE_SIZE_BYTES) throw new Error(`音频文件不能超过 ${MAX_AUDIO_FILE_SIZE_LABEL}`);
      if (!SUPPORTED_AUDIO_EXTENSIONS.includes(audioExtension(input.file) as typeof SUPPORTED_AUDIO_EXTENSIONS[number])) {
        throw new Error(`仅支持 ${SUPPORTED_AUDIO_EXTENSIONS.join("、")} 音频文件`);
      }
      const channelIndex = input.channelIndex.trim() ? Number(input.channelIndex) : undefined;
      if (channelIndex !== undefined && (!Number.isInteger(channelIndex) || channelIndex < 0)) throw new Error("channel_index 必须是非负整数");
      await run((signal) => submitAudioCommand(input.file!, {
        audio_source: input.audioSource.trim() || "browser_upload",
        speaker_zone: input.speakerZone,
        speaker_role: input.speakerRole,
        array_channel: input.arrayChannel.trim() || undefined,
        channel_index: channelIndex,
        session_id: sessionId,
      }, signal), adaptAudioCommandResponse);
    } catch (reason) {
      setStatus("failed");
      setError(reason instanceof Error ? reason.message : "音频输入校验失败");
    }
  }, [run, sessionId]);

  const submitMicrophone = useCallback(async (input: MicrophoneSubmissionInput) => {
    try {
      if (input.durationSeconds < 0.5 || input.durationSeconds > 15) throw new Error("采集时长必须在 0.5 到 15 秒之间");
      const state_overrides = parseObjectJson(input.stateOverridesJson, "state_overrides");
      const rawDevice = input.device.trim();
      const device = rawDevice === "" ? null : /^\d+$/.test(rawDevice) ? Number(rawDevice) : rawDevice;
      await run((signal) => submitMicrophoneCommand({
        duration_seconds: input.durationSeconds,
        device,
        speaker_zone: input.speakerZone,
        speaker_role: input.speakerRole,
        session_id: sessionId,
        ...(state_overrides ? { state_overrides } : {}),
      }, signal), adaptAudioCommandResponse);
    } catch (reason) {
      setStatus("failed");
      setError(reason instanceof SyntaxError ? "state_overrides 不是有效 JSON" : reason instanceof Error ? reason.message : "麦克风参数校验失败");
    }
  }, [run, sessionId]);

  const markCompleted = useCallback(() => setStatus("completed"), []);
  const markPartial = useCallback(() => setStatus("partial"), []);
  const markPresentationFailed = useCallback((message: string) => { setStatus("failed"); setError(message); }, []);
  const retryPresentation = useCallback(() => { setStatus("waiting_presentation"); setError(null); }, []);
  const reset = useCallback(() => { setStatus("idle"); setError(null); setImmediateResult(null); }, []);
  const busy = ["validating", "submitting", "processing", "waiting_presentation"].includes(status);

  return { status, error, busy, immediateResult, submitText, submitAudio, submitMicrophone, markCompleted, markPartial, markPresentationFailed, retryPresentation, reset };
}
