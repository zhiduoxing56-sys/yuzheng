import type { ExecuteResult, ExecutionSubmissionStatus, HealthResponse, TurnPresentationResponse } from "../types/contract";
import type { ExecutionEligibility } from "../utils/executionMapper";
import { executionEnvironmentLabel, executionStatusLabel } from "../utils/executionMapper";
import { ConfirmDialog } from "./ConfirmDialog";

interface Props {
  presentation: TurnPresentationResponse | null;
  health: HealthResponse | null;
  eligibility: ExecutionEligibility;
  status: ExecutionSubmissionStatus;
  error: string | null;
  result: ExecuteResult | null;
  busy: boolean;
  confirmationOpen: boolean;
  onRequest: () => void;
  onConfirm: () => void;
  onCancel: () => void;
}

const executionLabels: Record<ExecutionSubmissionStatus, string> = {
  idle: "尚未执行", confirming: "等待高风险确认", submitting: "正在调用执行接口", reconciling: "正在核对后端结果",
  completed: "执行完成", failed: "执行未完成", uncertain: "结果待确认",
};

export function ExecutionPanel(props: Props) {
  const environment = executionEnvironmentLabel(props.health);
  return <section className="review-card execution-card">
    <div className="card-heading"><div><span className="eyebrow">HIGH-RISK EXECUTION</span><h2>车辆动作执行</h2></div><span className={`submission-status execution-${props.status}`}>{executionLabels[props.status]}</span></div>
    <p className="execution-risk">这是高风险扩展接口。执行前后均以后端完整复查和持久化状态为准。</p>
    <dl className="review-fact-grid compact-grid">
      <div><dt>动作 / 目标</dt><dd>{props.presentation ? `${props.presentation.semantic_frame.intents[0]?.action || "未知动作"} / ${props.presentation.semantic_frame.intents[0]?.target || "未知目标"}` : "未提供"}</dd></div>
      <div><dt>运行环境</dt><dd>{environment}</dd></div>
      <div><dt>历史执行状态</dt><dd>{executionStatusLabel(props.presentation?.execution.execution_status)}</dd></div>
      <div><dt>适配器</dt><dd>{props.presentation?.execution.adapter || props.health?.vehicle_adapter || "未提供"}</dd></div>
    </dl>
    {!props.eligibility.allowed && <ul className="execution-blockers">{props.eligibility.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>}
    {props.result && <div className={props.result.accepted ? "execution-result success" : "execution-result failure"}><strong>{props.result.accepted ? "后端接受执行" : "后端拒绝或执行失败"}</strong><p>{props.result.reason}</p>{props.result.execution && <small>{props.result.execution.adapter} · {props.result.execution.simulated ? "仿真结果" : "非仿真结果"} · {props.result.execution.status}</small>}</div>}
    {props.error && <p className="inline-error" role="alert">{props.error}</p>}
    <button type="button" className="danger-button full-width" disabled={!props.eligibility.allowed || props.busy} onClick={props.onRequest}>确认并调用后端执行接口</button>
    <ConfirmDialog open={props.confirmationOpen} title="高风险执行确认" confirmLabel="确认调用执行接口" danger pending={props.status === "submitting" || props.status === "reconciling"} onConfirm={props.onConfirm} onCancel={props.onCancel}>
      <p>将执行：{props.presentation?.semantic_frame.intents[0]?.action || "未知动作"} / {props.presentation?.semantic_frame.intents[0]?.target || "未知目标"}</p>
      <p>当前环境：{environment}</p>
      <p>该请求会触发后端执行前完整复查，并可能产生不可撤销的车辆动作。令牌消费后不可重用。</p>
    </ConfirmDialog>
  </section>;
}
