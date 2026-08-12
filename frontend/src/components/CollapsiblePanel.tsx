import type { PropsWithChildren } from "react";

export function CollapsiblePanel({ title, children, defaultOpen = false }: PropsWithChildren<{ title: string; defaultOpen?: boolean }>) {
  return <details className="collapsible-panel" open={defaultOpen}><summary>{title}</summary><div>{children}</div></details>;
}
