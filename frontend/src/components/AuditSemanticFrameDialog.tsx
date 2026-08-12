import { SemanticFrameDisplay } from "./DecisionVisuals";
import type { SemanticFrame } from "../types/contract";

interface AuditSemanticFrameDialogProps {
  frame: SemanticFrame | null;
  onClose: () => void;
}

export function AuditSemanticFrameDialog({ frame, onClose }: AuditSemanticFrameDialogProps) {
  if (!frame) return null;

  return <div className="audit-semantic-dialog-backdrop" role="presentation" onMouseDown={onClose}>
    <section className="audit-semantic-dialog" role="dialog" aria-modal="true" aria-labelledby="audit-semantic-dialog-title" onMouseDown={(event) => event.stopPropagation()}>
      <div className="audit-semantic-dialog-header">
        <h2 id="audit-semantic-dialog-title">语义帧详细结果</h2>
        <button type="button" aria-label="关闭语义帧详细结果" onClick={onClose}>关闭</button>
      </div>
      <SemanticFrameDisplay frame={frame} />
    </section>
  </div>;
}
