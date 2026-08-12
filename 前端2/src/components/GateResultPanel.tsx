import type { TurnPresentationResponse } from "../types/contract";

export function GateResultPanel({ data }: { data: TurnPresentationResponse | null }) {
  if (!data) return <section className="detail-section"><span className="eyebrow">SAFETY GATE</span><h2>安全门结果</h2><p className="empty-copy">暂无安全门数据</p></section>;
  const hits = data.gate_result.checks.filter((check) => check.hit);
  return <section className="detail-section"><div className="card-heading"><div><span className="eyebrow">SAFETY GATE</span><h2>安全门结果</h2></div><span className={`status-badge ${data.gate_result.blocked ? "status-danger" : "status-success"}`}>{data.gate_result.blocked ? "已阻断" : "已通过"}</span></div>
    {!hits.length ? <p className="success-copy">未命中阻断规则。</p> : <ul className="gate-list">{hits.map((check) => <li key={check.rule_id}><strong>{check.rule_name}</strong><span>{check.reason}</span><small>{check.rule_id} · {check.severity}</small></li>)}</ul>}
    {import.meta.env.DEV && <details><summary>开发模式：原始安全门字段</summary><pre>{JSON.stringify(data.gate_result, null, 2)}</pre></details>}
  </section>;
}
