from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.core.config import load_yaml
from app.models.schemas import SecurityClass, SecurityClassInfo
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES


class EvidenceSecurityClassification:
    """Single reader for the authoritative index security-layering configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        layering = dict(config.get("security_layering", {}))
        self.security_classes = dict(layering.get("security_classes", {}))
        self.evidence_type_mapping = dict(layering.get("evidence_type_mapping", {}))
        self.unknown_type_strategy = str(
            layering.get("unknown_type_strategy", "UNCLASSIFIED_BASE_ONLY")
        )
        if set(self.evidence_type_mapping) != CANONICAL_EVIDENCE_TYPES:
            raise ValueError("security_layering evidence_type_mapping must cover the canonical catalog")
        for name, definition in self.security_classes.items():
            if "rank" not in definition or "node_layer_label" not in definition:
                raise ValueError(f"security class {name} lacks rank/node_layer_label")

    def info(self, evidence_type: str) -> SecurityClassInfo:
        mapping = dict(self.evidence_type_mapping.get(evidence_type, {}))
        if not mapping:
            return SecurityClassInfo(
                name=SecurityClass.UNCLASSIFIED,
                rank=None,
                report_label="Unclassified",
                node_layer_label="L0_UNCLASSIFIED",
                mapping_source=self.unknown_type_strategy,
            )
        name = SecurityClass(str(mapping["security_class"]))
        class_config = dict(self.security_classes[name.value])
        return SecurityClassInfo(
            name=name,
            rank=int(class_config["rank"]),
            report_label=str(class_config.get("report_label", name.value.title())),
            node_layer_label=str(class_config["node_layer_label"]),
            mapping_source=str(mapping["source"]),
        )


@lru_cache(maxsize=1)
def production_security_classification() -> EvidenceSecurityClassification:
    return EvidenceSecurityClassification(load_yaml("index.yaml"))
