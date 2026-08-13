from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT_DIR / "data/nlu/spec/intent_registry_unified_v1.yaml"
CARDS_PATH = ROOT_DIR / "挂靠/intent_cards_unified_v1.yaml"
ANCHOR_PATH = ROOT_DIR / "挂靠/intent_anchor_set_unified_v1.yaml"


def _load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"统一语义资产根节点必须为映射: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


class UnifiedSemanticRegistry:
    """The single production source of truth for all 149 semantic intents."""

    def __init__(
        self,
        registry_path: Path = REGISTRY_PATH,
        cards_path: Path = CARDS_PATH,
        anchor_path: Path = ANCHOR_PATH,
    ) -> None:
        self.registry_path = registry_path.resolve()
        self.cards_path = cards_path.resolve()
        self.anchor_path = anchor_path.resolve()
        self.document = _load_mapping(self.registry_path)
        raw_intents = self.document.get("intents")
        if not isinstance(raw_intents, list):
            raise RuntimeError("统一语义 Registry intents 必须为列表")
        self.intents: dict[str, dict[str, Any]] = {}
        for raw in raw_intents:
            if not isinstance(raw, dict):
                raise RuntimeError("统一语义 Intent 定义必须为映射")
            intent_id = str(raw.get("intent_id", "")).strip()
            if not intent_id or intent_id in self.intents:
                raise RuntimeError(f"统一语义 Registry 存在空或重复 intent_id: {intent_id}")
            identity = str(raw.get("runtime_identity", ""))
            if identity not in {"FORMAL", "KNOWN_NON_EXECUTABLE"}:
                raise RuntimeError(f"非法 runtime_identity: {intent_id}/{identity}")
            self.intents[intent_id] = dict(raw)
        statistics = self.document.get("statistics", {})
        identities = [item["runtime_identity"] for item in self.intents.values()]
        actual = {
            "intent_count": len(self.intents),
            "formal_count": identities.count("FORMAL"),
            "known_non_executable_count": identities.count("KNOWN_NON_EXECUTABLE"),
        }
        if actual != statistics or actual != {
            "intent_count": 149,
            "formal_count": 71,
            "known_non_executable_count": 78,
        }:
            raise RuntimeError(f"统一语义 Registry 数量错误: {actual}")
        self._validate_contract_references()
        self._validate_derived_indexes()

    def _validate_contract_references(self) -> None:
        fields = {
            "value_contract": "value_contracts",
            "mode_contract": "mode_contracts",
            "direction_contract": "direction_contracts",
            "conditional_slot_contract": "conditional_slot_contracts",
            "value_mapping_contract": "value_mapping_contracts",
        }
        for field, catalog_name in fields.items():
            catalog = self.document.get(catalog_name)
            if not isinstance(catalog, dict):
                raise RuntimeError(f"missing contract catalog: {catalog_name}")
            for intent_id, definition in self.intents.items():
                reference = definition.get(field)
                if reference and str(reference) not in catalog:
                    raise RuntimeError(f"unresolved {field}: {intent_id}/{reference}")

    def _validate_derived_indexes(self) -> None:
        registry_hash = _sha256(self.registry_path)
        cards = _load_mapping(self.cards_path)
        anchors = _load_mapping(self.anchor_path)
        for name, index in (("cards", cards), ("anchors", anchors)):
            if index.get("source_registry_sha256") != registry_hash:
                raise RuntimeError(f"{name} 与统一 Registry SHA256 不一致")
            if int(index.get("intent_count", 0)) != 149:
                raise RuntimeError(f"{name} intent_count 必须为 149")
        card_items = cards.get("intents")
        anchor_items = anchors.get("intents")
        if not isinstance(card_items, dict) or not isinstance(anchor_items, dict):
            raise RuntimeError("统一 cards/anchors intents 必须为映射")
        if set(card_items) != set(self.intents) or set(anchor_items) != set(self.intents):
            raise RuntimeError("统一 Registry、cards、anchors 的 ID 集合不一致")
        for intent_id, definition in self.intents.items():
            card = card_items[intent_id]
            group = anchor_items[intent_id]
            for field in (
                "runtime_identity",
                "canonical_action",
                "canonical_target",
                "control_attribute",
            ):
                if str(card.get(field)) != str(definition.get(field)):
                    raise RuntimeError(f"cards 字段与 Registry 不一致: {intent_id}/{field}")
            if group.get("runtime_identity") != definition["runtime_identity"]:
                raise RuntimeError(f"anchors runtime_identity 不一致: {intent_id}")
            if not isinstance(group.get("anchors"), list) or not group["anchors"]:
                raise RuntimeError(f"意图没有活跃锚点: {intent_id}")

        known_source = self.document.get("source_freezes", {}).get("known", {})
        known_path_value = known_source.get("path")
        if not isinstance(known_path_value, str):
            raise RuntimeError("unified Registry missing current Known freeze source")
        known_path = (ROOT_DIR / known_path_value).resolve()
        if _sha256(known_path) != known_source.get("sha256"):
            raise RuntimeError("current Known freeze SHA256 mismatch")
        known_freeze = _load_mapping(known_path)
        approved_active: dict[str, set[str]] = {}
        for item in known_freeze.get("known_non_executable_intents", []):
            active = [
                anchor["text"]
                for anchor in item.get("anchors", {}).get("historical_recovered", [])
            ] + [
                anchor["text"]
                for anchor in item.get("anchors", {}).get("human_generated_approved", [])
            ] + [
                anchor["text"]
                for anchor in item.get("anchors", {}).get(
                    "human_reclassified_from_quarantine", []
                )
            ]
            approved_active[str(item["intent_id"])] = {
                _normalize(str(text)) for text in active
            }
        for intent_id, definition in self.intents.items():
            if definition["runtime_identity"] != "KNOWN_NON_EXECUTABLE":
                continue
            actual_active = {
                _normalize(str(text)) for text in anchor_items[intent_id]["anchors"]
            }
            if actual_active != approved_active.get(intent_id, set()):
                raise RuntimeError(
                    f"Known active anchors do not match current approved freeze: {intent_id}"
                )

    def definition(self, intent_id: str) -> dict[str, Any]:
        try:
            return self.intents[intent_id]
        except KeyError as exc:
            raise RuntimeError(f"统一语义 Registry 不存在 intent_id: {intent_id}") from exc

    def runtime_identity(self, intent_id: str) -> str:
        return str(self.definition(intent_id)["runtime_identity"])

    def is_formal(self, intent_id: str) -> bool:
        return self.runtime_identity(intent_id) == "FORMAL"

    def is_known(self, intent_id: str) -> bool:
        return self.runtime_identity(intent_id) == "KNOWN_NON_EXECUTABLE"
