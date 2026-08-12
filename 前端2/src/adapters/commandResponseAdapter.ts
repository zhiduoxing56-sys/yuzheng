import type { DecisionLabel, InputType } from "../types/contract";
import { array, nonEmptyString, nullableString, record, stripSensitiveFields, string } from "./runtime";

export type SubmissionSummarySource = "用户原始输入" | "后端真实转写";

export interface AdaptedCommandResponse {
  turnId: string;
  inputType: InputType;
  instructionSummary: string;
  summarySource: SubmissionSummarySource;
  action: string;
  target: string;
  preliminaryDecision: DecisionLabel;
  auditId: string | null;
  safeResponse: unknown;
}

function decisionLabel(value: unknown, path: string): DecisionLabel {
  return string(value, path);
}

function common(raw: unknown, inputType: InputType) {
  const root = record(raw, "command");
  const turnId = nonEmptyString(root.turn_id, "command.turn_id");
  const decision = record(root.decision, "command.decision");
  const preliminaryDecision = decisionLabel(decision.final_decision ?? decision.decision, "command.decision.final_decision");
  const semantic = root.semantic_frame == null ? null : record(root.semantic_frame, "command.semantic_frame");
  const intents = semantic ? array(semantic.intents, "command.semantic_frame.intents") : [];
  const firstIntent = intents.length ? record(intents[0], "command.semantic_frame.intents[0]") : null;
  const action = firstIntent ? string(firstIntent.action, "command.semantic_frame.intents[0].action") : "后端未提供";
  const target = firstIntent ? string(firstIntent.target, "command.semantic_frame.intents[0].target") : "后端未提供";
  const audit = root.audit == null ? null : record(root.audit, "command.audit");
  const auditId = audit ? nullableString(audit.audit_id, "command.audit.audit_id") : null;
  return { root, turnId, inputType, preliminaryDecision, action, target, auditId, safeResponse: stripSensitiveFields(raw) };
}

export function adaptTextCommandResponse(raw: unknown, originalText: string): AdaptedCommandResponse {
  const base = common(raw, "text");
  return { ...base, instructionSummary: nonEmptyString(originalText, "request.text"), summarySource: "用户原始输入" };
}

export function adaptAudioCommandResponse(raw: unknown): AdaptedCommandResponse {
  const base = common(raw, "audio");
  const inputType = string(base.root.input_type, "command.input_type");
  if (inputType !== "audio") throw new Error("响应结构异常：command.input_type");
  const asr = base.root.asr_result == null ? null : record(base.root.asr_result, "command.asr_result");
  const pipeline = base.root.pipeline == null ? null : record(base.root.pipeline, "command.pipeline");
  const pipelineTranscription = pipeline?.transcription_result == null ? null : record(pipeline.transcription_result, "command.pipeline.transcription_result");
  const transcription = asr?.transcribed_text ?? asr?.text ?? pipelineTranscription?.transcribed_text ?? pipelineTranscription?.text;
  return { ...base, instructionSummary: nonEmptyString(transcription, "command.asr_result.transcribed_text"), summarySource: "后端真实转写" };
}
