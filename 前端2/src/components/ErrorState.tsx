interface ErrorStateProps {
  title?: string;
  description: string;
  onRetry?: () => void;
}

export function ErrorState({ title = "数据暂不可用", description, onRetry }: ErrorStateProps) {
  return (
    <section className="state-card error-state" role="alert">
      <div className="state-icon" aria-hidden="true">!</div>
      <h2>{title}</h2>
      <p>{description}</p>
      {onRetry && <button type="button" className="secondary-button" onClick={onRetry}>重新请求</button>}
    </section>
  );
}
