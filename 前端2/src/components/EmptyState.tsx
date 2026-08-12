interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <section className="state-card empty-state" aria-live="polite">
      <div className="state-icon" aria-hidden="true">—</div>
      <h2>{title}</h2>
      <p>{description}</p>
    </section>
  );
}
