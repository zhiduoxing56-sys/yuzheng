import { apiClient, type QueryValue } from "./client";
import type {
  AudioCommandQuery,
  MicrophoneCommandRequest,
  TextCommandRequest,
} from "../types/contract";

/** Frozen public command endpoints. Microphone is a backend extension endpoint. */
export function submitTextCommand(request: TextCommandRequest, signal?: AbortSignal): Promise<unknown> {
  return apiClient.post<unknown>("/api/command/text", request, { signal, timeoutMs: 60_000 });
}

export function submitAudioCommand(audio: BodyInit, query: AudioCommandQuery = {}, signal?: AbortSignal): Promise<unknown> {
  return apiClient.postBytes<unknown>("/api/command/audio", audio, query as Record<string, QueryValue>, { signal, timeoutMs: 120_000 });
}

/** Backend extension: microphone capture is not part of the frozen public surface. */
export function submitMicrophoneCommand(request: MicrophoneCommandRequest, signal?: AbortSignal): Promise<unknown> {
  return apiClient.post<unknown>("/api/command/microphone", request, { signal, timeoutMs: 120_000 });
}
