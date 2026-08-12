interface VisualSectionTabProps {
  children: string;
}

export function VisualSectionTab({ children }: VisualSectionTabProps) {
  return <h2 className="visual-section-tab"><span>{children}</span></h2>;
}
