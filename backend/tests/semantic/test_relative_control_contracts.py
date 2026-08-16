from __future__ import annotations

from semantic_registry_v1.registry import UnifiedSemanticRegistry
from semantic_registry_v1.slots import resolve_slots


def test_hvac_temperature_preserves_absolute_and_relative_semantics() -> None:
    registry = UnifiedSemanticRegistry()
    definition = registry.definition("HVAC_SET_TEMPERATURE")

    absolute = resolve_slots("空调温度设为24摄氏度", definition, registry.document)
    decrease = resolve_slots("空调温度降低2摄氏度", definition, registry.document)
    increase = resolve_slots("空调温度升高2摄氏度", definition, registry.document)

    assert absolute.params == {"value": 24}
    assert decrease.params == {"value": 2, "direction": "DECREASE"}
    assert increase.params == {"value": 2, "direction": "INCREASE"}


def test_relative_temperature_without_magnitude_never_invents_value() -> None:
    registry = UnifiedSemanticRegistry()
    definition = registry.definition("HVAC_SET_TEMPERATURE")

    result = resolve_slots("空调再低一点", definition, registry.document)

    assert result.params == {"direction": "DECREASE"}
    assert result.missing_required == ("VALUE",)
