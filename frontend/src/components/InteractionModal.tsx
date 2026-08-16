import { useState, type ReactNode } from "react";
import type { InteractionAction, InteractionRequest } from "../types/contract";

/** A renderer only: interaction_type is authored by the backend. */
export function InteractionModal({ request, busy, error, onSubmit }: { request: InteractionRequest; busy: boolean; error: string | null; onSubmit: (action: InteractionAction, candidateId?: string, text?: string, parameters?: Record<string, unknown>) => void; }) {
  const [rephrasing, setRephrasing] = useState(false);
  const [text, setText] = useState("");
  const [parameter, setParameter] = useState("");
  const options = Array.isArray(request.payload.enum_values) ? request.payload.enum_values as string[] : [];
  const field = String(request.payload.missing_field || "parameter").toLowerCase();
  const reason = <><h2>{request.user_reason?.title}</h2><p>{request.user_reason?.description}</p><p>{request.canonical_operation || String(request.payload.original_instruction || "当前指令")}</p></>;
  const cancel = <button disabled={busy} onClick={() => onSubmit("CANCEL")} type="button">取消本次指令</button>;
  const rephrase = rephrasing ? <><input value={text} onChange={(event) => setText(event.target.value)} placeholder="重新表达指令" /><button disabled={busy || !text.trim()} onClick={() => onSubmit("REPHRASE", undefined, text)} type="button">提交重新表达</button></> : <button disabled={busy} onClick={() => setRephrasing(true)} type="button">重新表达</button>;
  let body: ReactNode;
  if (request.interaction_type === "MULTI_INTENT_SELECTION") body = <>{reason}<p>检测到多个车辆控制操作，请选择本次需要继续处理的操作。</p>{request.candidates.map((item) => <button key={item.candidate_id} disabled={busy} onClick={() => onSubmit("SELECT_CANDIDATE", item.candidate_id)} type="button">{item.display_text}</button>)}{cancel}</>;
  else if (request.interaction_type === "PARAMETER_COMPLETION") body = <>{reason}<p>缺失：{String(request.payload.field_label || field)}</p>{options.map((value) => <button key={value} disabled={busy} onClick={() => onSubmit("SUBMIT_PARAMETERS", undefined, undefined, { [field]: value })} type="button">{value}</button>)}{options.length === 0 && <><input value={parameter} onChange={(event) => setParameter(event.target.value)} placeholder={String(request.payload.field_label || "请输入参数")} /><button disabled={busy || !parameter.trim()} onClick={() => onSubmit("SUBMIT_PARAMETERS", undefined, undefined, { [field]: parameter.trim() })} type="button">提交参数</button></>}{cancel}</>;
  else if (request.interaction_type === "SEMANTIC_DISAMBIGUATION") body = <>{reason}{request.candidates.map((item) => <button key={item.candidate_id} disabled={busy} onClick={() => onSubmit("SELECT_CANDIDATE", item.candidate_id)} type="button">{item.display_text}</button>)}{rephrase}{cancel}</>;
  else if (request.interaction_type === "UNRESOLVED_VEHICLE_CONTROL") body = <>{reason}{rephrase}{cancel}</>;
  else if (request.interaction_type === "SAFETY_REVIEW") body = <>{reason}<button disabled={busy} onClick={() => onSubmit("CONFIRM")} type="button">确认继续</button>{cancel}</>;
  else body = <>{reason}<button disabled={busy} onClick={() => onSubmit("EXECUTE")} type="button">确认执行</button>{cancel}</>;
  return <div className="clarification-modal-backdrop"><section className="clarification-modal" role="dialog" aria-modal="true">{body}{error && <p className="clarification-error">{error}</p>}</section></div>;
}
