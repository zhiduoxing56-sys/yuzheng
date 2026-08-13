import type { AuditRecordView } from "../types/visualModels";
import { formatDateTime } from "../utils/formatters";

interface AuditRecordTableProps {
  records: AuditRecordView[];
  onRecordClick: (record: AuditRecordView) => void;
}

export function AuditRecordTable({ records, onRecordClick }: AuditRecordTableProps) {
  return <div className="visual-lined-table audit-record-table">
    <table>
      <thead><tr><th>时间</th><th>原始指令</th><th>最终裁决</th><th>执行结果</th><th>是否复核</th><th>操作</th></tr></thead>
      <tbody>{records.map((record) => <tr key={record.auditId} tabIndex={0} onClick={() => onRecordClick(record)} onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onRecordClick(record);
      }}>
        <td>{formatDateTime(record.createdAt)}</td><td>{record.rawCommand}</td>
        <td>{record.finalDecision}</td><td>{record.executionStatus}</td><td>{record.reviewOccurred ? "是" : "否"}</td>
        <td><button type="button" className="audit-semantic-link" onClick={(event) => { event.stopPropagation(); onRecordClick(record); }}>查看详情</button></td>
      </tr>)}</tbody>
    </table>
  </div>;
}
