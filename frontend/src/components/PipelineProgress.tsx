import type { PipelineEvent } from "../types/contract";
import { buildPipelineStageViews } from "../utils/pipelineStageMapper";

const statusLabels = { waiting: "等待", processing: "处理中", completed: "完成", review: "复核", blocked: "阻断", failed: "失败" } as const;

export function PipelineProgress({ events, processing }: { events: PipelineEvent[]; processing: boolean }) {
  const stages = buildPipelineStageViews(events, processing);
  return <section className="pipeline-progress" aria-label="实时处理流程">{stages.map((stage, index) => <div key={stage.key} className={`pipeline-step pipeline-${stage.status}`} title={stage.latestEvent?.summary}>
    <span className="pipeline-index">{String(index + 1).padStart(2, "0")}</span><strong>{stage.label}</strong><small>{statusLabels[stage.status]}</small>
  </div>)}</section>;
}
