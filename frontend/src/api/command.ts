import { apiClient, type QueryValue } from "./client";
import type {
  AudioCommandResponse,
  AudioCommandQuery,
  MicrophoneCommandRequest,
  TextCommandRequest,
  TextCommandResponse,
} from "../types/contract";

/** Frozen public command endpoints. Microphone is a backend extension endpoint. */
export function submitTextCommand(request: TextCommandRequest, signal?: AbortSignal): Promise<TextCommandResponse> {
  return apiClient.post<TextCommandResponse>("/api/command/text", request, { signal, timeoutMs: 60_000 });
}

export function submitAudioCommand(audio: BodyInit, query: AudioCommandQuery = {}, signal?: AbortSignal): Promise<AudioCommandResponse> {
  return apiClient.postBytes<AudioCommandResponse>("/api/command/audio", audio, query as Record<string, QueryValue>, { signal, timeoutMs: 120_000 });
}

/** Backend extension: microphone capture is not part of the frozen public surface. */
export function submitMicrophoneCommand(request: MicrophoneCommandRequest, signal?: AbortSignal): Promise<AudioCommandResponse> {
  return apiClient.post<AudioCommandResponse>("/api/command/microphone", request, { signal, timeoutMs: 120_000 });
}
