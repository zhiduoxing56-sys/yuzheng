"""CBN 子图注册：HEADLIGHT_OFF（关闭前照灯）"""
from __future__ import annotations

from causal_bayes.schemas import CptEntry, SafetyCpt


def headlight_off_cpt() -> SafetyCpt:
    return SafetyCpt(
        entries={
            "ambient_light": {
                "BRIGHT": CptEntry("ambient_light", "BRIGHT", "risk", 0.02, 1, 49, "白天无照明缺失风险"),
                "DIM": CptEntry("ambient_light", "DIM", "risk", 0.10, 3, 27, "黄昏/阴天(专家)"),
                "DARK": CptEntry("ambient_light", "DARK", "risk", 0.75, 15, 5, "夜间照明缺失风险(GB 7258)"),
            },
            "visibility": {
                "GOOD": CptEntry("visibility", "GOOD", "risk", 0.02, 1, 49, "能见度良好"),
                "MEDIUM": CptEntry("visibility", "MEDIUM", "risk", 0.08, 2, 23, "中等能见度(专家)"),
                "POOR": CptEntry("visibility", "POOR", "risk", 0.45, 9, 11, "低能见度(GB 7258)"),
            },
            "speed": {
                "LOW": CptEntry("speed", "LOW", "weight", 0.02, 1, 49, "停车/低速:风险不激活"),
                "MEDIUM": CptEntry("speed", "MEDIUM", "weight", 0.95, 95, 5, "行驶:风险全额激活(专家)"),
                "HIGH": CptEntry("speed", "HIGH", "weight", 0.96, 96, 4, "高速:风险激活(专家)"),
            },
            "headlight": {
                "ON": CptEntry("headlight", "ON", "weight", 1.0, 1, 1, "大灯开启→STATE_CHANGE"),
                "OFF": CptEntry("headlight", "OFF", "weight", 0.0, 1, 1, "大灯已关→NO_OP"),
            },
        }
    )


HEADLIGHT_OFF_EXPRESSIONS = [
    "关闭前照灯", "关闭大灯", "关闭近光灯", "关闭远光灯", "关闭自动大灯",
]


def graph_for(action_id: str) -> SafetyCpt:
    registry = {"HEADLIGHT_OFF": headlight_off_cpt}
    if action_id not in registry:
        raise KeyError(f"未注册的因果子图: {action_id}")
    return registry[action_id]()
