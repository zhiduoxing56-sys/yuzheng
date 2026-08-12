import { useCallback, useEffect, useMemo, useState } from "react";
import {
  EMPTY_EVIDENCE_LIST_FILTERS,
  filterEvidenceLayers,
  type EvidenceLayerModel,
  type EvidenceListFilterState,
} from "../utils/evidenceLayerAdapter";

export function useEvidenceFilters(turnId: string | null, model: EvidenceLayerModel | null) {
  const [filters, setFilters] = useState<EvidenceListFilterState>(EMPTY_EVIDENCE_LIST_FILTERS);

  useEffect(() => setFilters(EMPTY_EVIDENCE_LIST_FILTERS), [turnId]);

  const updateFilters = useCallback((patch: Partial<EvidenceListFilterState>) => {
    setFilters((current) => ({ ...current, ...patch }));
  }, []);
  const resetFilters = useCallback(() => setFilters(EMPTY_EVIDENCE_LIST_FILTERS), []);

  const layers = useMemo(() => model ? filterEvidenceLayers(model, filters) : [], [model, filters]);
  const visibleCount = useMemo(() => layers.reduce((total, layer) => total + layer.visibleCount, 0), [layers]);
  const totalCount = model?.layers.reduce((total, layer) => total + layer.nodes.length, 0) ?? 0;

  return { filters, updateFilters, resetFilters, layers, visibleCount, totalCount };
}
