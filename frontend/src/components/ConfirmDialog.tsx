import type { ReactNode } from "react";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  children: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  pending?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  children,
  confirmLabel = "确认",
  cancelLabel = "取消",
  danger = false,
  pending = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null;
  return (
    <div className="dialog-backdrop" role="presentation">
      <section className="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
        <h2 id="dialog-title">{title}</h2>
        <div className="dialog-content">{children}</div>
        <div className="dialog-actions">
          <button type="button" className="secondary-button" disabled={pending} onClick={onCancel}>{cancelLabel}</button>
          <button type="button" className={danger ? "danger-button" : "primary-button"} disabled={pending} onClick={onConfirm}>
            {pending ? "提交中" : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
