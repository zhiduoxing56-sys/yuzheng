import type { AuditRecordView } from "../types/visualModels";
import { formatDateTime } from "../utils/formatters";

interface AuditRecordTableProps {
  records: AuditRecordView[];
  onRecordClick: (record: AuditRecordView) => void;
  onSemanticFrameClick: (record: AuditRecordView) => void;
}

function display(value: string | null) {
  return value?.trim() || "--";
}

export function AuditRecordTable({ records, onRecordClick, onSemanticFrameClick }: AuditRecordTableProps) {
  return <div className="visual-lined-table audit-record-table">
    <table>
      <thead><tr><th>时间</th><th>指令内容</th><th>语义帧详细结果</th><th>裁决结果</th><th>轮次编号</th></tr></thead>
      <tbody>{records.map((record) => <tr key={record.auditId} tabIndex={0} onClick={() => onRecordClick(record)} onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onRecordClick(record);
      }}>
        <td>{formatDateTime(record.createdAt)}</td><td>{display(record.rawText)}</td>
        <td>{record.semanticFrame ? <button type="button" className="audit-semantic-link" onClick={(event) => { event.stopPropagation(); onSemanticFrameClick(record); }}>查看详情</button> : "--"}</td>
        <td>--</td><td>{display(record.turnId)}</td>
      </tr>)}</tbody>
    </table>
  </div>;
}
