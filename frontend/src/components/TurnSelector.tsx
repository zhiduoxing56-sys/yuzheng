interface Props {
  currentTurnId: string;
  turnIds: string[];
  onChange: (turnId: string) => void;
}

export function TurnSelector({ currentTurnId, turnIds, onChange }: Props) {
  const options = [currentTurnId, ...turnIds.filter((id) => id !== currentTurnId)];
  return <label className="turn-selector">
    <span>轮次选择</span>
    <select value={currentTurnId} onChange={(event) => onChange(event.target.value)}>
      {options.map((turnId) => <option key={turnId} value={turnId}>{turnId}</option>)}
    </select>
  </label>;
}
