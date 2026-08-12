import type { ReactNode } from "react";
import { EmptyState } from "../components/EmptyState";

interface PageScaffoldProps {
  eyebrow: string;
  title: string;
  description: string;
  routeValue?: string;
  children?: ReactNode;
}

export function PageScaffold({ eyebrow, title, description, routeValue, children }: PageScaffoldProps) {
  return (
    <div className="page-scaffold">
      <div className="page-heading">
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
        {routeValue && <code className="route-value">当前参数：{routeValue}</code>}
      </div>
      {children || <EmptyState title="暂无可展示数据" description="当前页面尚未收到后端记录，后续阶段将在真实接口返回后展示内容。" />}
    </div>
  );
}
