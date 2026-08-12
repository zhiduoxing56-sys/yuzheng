import type { TurnPresentationResponse } from "../types/contract";

interface Props {
  data: TurnPresentationResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

function JsonIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M8 3H5.8A1.8 1.8 0 0 0 4 4.8v14.4A1.8 1.8 0 0 0 5.8 21H8M16 3h2.2A1.8 1.8 0 0 1 20 4.8v14.4a1.8 1.8 0 0 1-1.8 1.8H16M9.5 8 7.2 12l2.3 4M14.5 8l2.3 4-2.3 4" />
  </svg>;
}

export function SemanticFrameJsonPanel({ data, loading, error, onRetry }: Props) {
  return <section className="decision-surface semantic-json-card" aria-labelledby="semantic-json-title">
    <div className="decision-section-heading">
      <span className="decision-heading-icon"><JsonIcon /></span>
      <h2 id="semantic-json-title">语义帧解析</h2>
      <span className={`semantic-json-status ${data ? "ready" : error ? "failed" : loading ? "loading" : "idle"}`}>
        {data ? "已解析" : error ? "读取失败" : loading ? "解析中" : "待解析"}
      </span>
    </div>
    {data ? <pre className="semantic-json-output" aria-label="语义帧 JSON"><code>{JSON.stringify(data.semantic_frame, null, 2)}</code></pre>
      : error ? <div className="decision-inline-state error" role="alert"><strong>语义帧暂时无法读取</strong><p>{error}</p><button type="button" onClick={onRetry}>重新读取</button></div>
        : <div className="decision-inline-state"><span className="semantic-placeholder-icon"><JsonIcon /></span><strong>{loading ? "正在读取语义帧" : "解析结果将显示在这里"}</strong><p>提交指令后，将原样展示后端返回的 JSON 结构。</p></div>}
  </section>;
}
