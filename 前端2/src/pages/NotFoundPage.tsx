import { Link } from "react-router-dom";
import { PageScaffold } from "./PageScaffold";

export function NotFoundPage() {
  return (
    <PageScaffold eyebrow="404" title="页面不存在" description="当前地址没有对应的前端页面。">
      <div className="state-card empty-state"><Link className="primary-link" to="/decision">返回实时裁决</Link></div>
    </PageScaffold>
  );
}
