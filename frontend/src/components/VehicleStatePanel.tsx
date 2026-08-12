import type { SemanticFrame, VehicleState } from "../types/contract";
import { formatVehicleStateValue, relevantVehicleStateEntries, vehicleStateAvailabilityMessage, vehicleStateLabel } from "../utils/vehicleStateMapper";

interface Props { data: VehicleState | null; semanticFrame: SemanticFrame | null; loading: boolean; error: string | null; onRefresh: () => void; }

function StateGrid({ entries }: { entries: [keyof VehicleState, unknown][] }) {
  return <dl className="state-grid">{entries.map(([key, value]) => <div key={key}><dt>{vehicleStateLabel(key)}</dt><dd>{formatVehicleStateValue(key, value)}</dd></div>)}</dl>;
}

export function VehicleStatePanel({ data, semanticFrame, loading, error, onRefresh }: Props) {
  void semanticFrame;
  const entries = data ? relevantVehicleStateEntries(data, null) : [];
  const availabilityMessage = vehicleStateAvailabilityMessage(null);
  return <section className="decision-card vehicle-panel"><div className="card-heading"><div><span className="eyebrow">VEHICLE</span><h2>相关车辆状态</h2></div><button className="secondary-button compact" onClick={onRefresh} disabled={loading}>刷新</button></div>
    {loading && !data && <p className="loading-copy">正在读取车辆状态……</p>}
    {error && <p className="inline-error">{error}</p>}
    {data && entries.length > 0 && <StateGrid entries={entries} />}
    {data && entries.length === 0 && <p className="empty-copy">{availabilityMessage || "相关车辆状态暂未采集。"}</p>}
  </section>;
}
