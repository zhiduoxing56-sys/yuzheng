"""Source-Specific Analyzer —— 按来源类型分流的失效模式提取

目标：降低 UNKNOWN 率（当前 67.7% 基线）
  - RECALL          ：标准描述（现有正则，高精度）
  - COMPLAINT       ：口语化自由文本（增强英文口语正则）
  - CN/INVESTIGATION：中文正则（跨源泛化专项）
统一输出 AnalyzedIncident Schema（不改变下游）
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field

from safety_knowledge.intelligence.models import Consequence, FailureMode, OperatingCondition
from safety_knowledge.intelligence.agent.analyzer import AnalysisResult, IncidentAnalyzer

# ==================== 口语化 FailureMode 增强（COMPLAINT 专用） ====================

COMPLAINT_FM_RULES: list[tuple[str, FailureMode]] = [
    (r"\bsuddenly (accelerat|surge|take off|lurch)|突然加速|自动加速|自己加速", FailureMode.UNINTENDED_ACTIVATION),
    (r"accelerat(es|ed)? on (its own|itself|own)|加速踏板自己", FailureMode.UNCOMMANDED_MOVEMENT),
    (r"brakes? (suddenly|by itself|on its own)|自己刹车|自动刹车|突然制动", FailureMode.UNINTENDED_ACTIVATION),
    (r"won'?t (start|engage|release|stop)|无法启动|不能启动|无法解除", FailureMode.FAIL_TO_ACTIVATE),
    (r"failed? to (start|engage|stop|release|respond)", FailureMode.FAIL_TO_ACTIVATE),
    (r"keeps (turning off|stalling|dying)|熄火|突然熄火", FailureMode.LOSS_OF_FUNCTION),
    (r"randomly|at random|sometimes|occasionally|intermittently|时好时坏|间歇", FailureMode.INTERMITTENT_FAILURE),
    (r"delay|lag|滞后|延迟", FailureMode.DELAYED_RESPONSE),
    (r"jerky|jerk|shudder|顿挫|抖动|冲击", FailureMode.INCORRECT_STATE),
    (r"shuts off|stall|dead|断电|没反应", FailureMode.LOSS_OF_FUNCTION),
    (r"leak|滴油|漏油|漏液|渗油", FailureMode.LEAKAGE),
    (r"overheat|过热|高温", FailureMode.OVERHEATING),
    (r"loose|松动|脱落|松脱", FailureMode.LOOSE_CONNECTION),
    (r"smell|异味|臭味", FailureMode.LEAKAGE),
    (r"noise|异响|噪音|嗡嗡", FailureMode.INCORRECT_STATE),
    (r"warning light|故障灯|报警灯|仪表报警", FailureMode.INCORRECT_STATE),
    (r"stuck|卡住|卡死|失灵", FailureMode.FAIL_TO_ACTIVATE),
]

# ==================== 中文 FailureMode（CN/INVESTIGATION 专用） ====================

CN_FM_RULES: list[tuple[str, FailureMode]] = [
    (r"突然加速|自动加速|自行加速|非预期加速", FailureMode.UNINTENDED_ACTIVATION),
    (r"突然制动|自动刹车|自行刹车|非预期制动", FailureMode.UNINTENDED_ACTIVATION),
    (r"失灵|失效|无法工作|不能工作|功能丧失", FailureMode.LOSS_OF_FUNCTION),
    (r"无法启动|不能启动|无法激活|启动失败", FailureMode.FAIL_TO_ACTIVATE),
    (r"无法停止|无法停车|不能停车|制动失效", FailureMode.FAIL_TO_ACTIVATE),
    (r"间歇|时好时坏|偶发|偶尔|断续", FailureMode.INTERMITTENT_FAILURE),
    (r"延迟|滞后|响应慢", FailureMode.DELAYED_RESPONSE),
    (r"卡滞|卡死|卡住|顿挫|抖动", FailureMode.INCORRECT_STATE),
    (r"失控|失去控制", FailureMode.UNCOMMANDED_MOVEMENT),
    (r"数据损坏|数据丢失|存储故障", FailureMode.DATA_CORRUPTION),
    (r"认证绕过|未授权访问|安全漏洞|被入侵", FailureMode.AUTHENTICATION_BYPASS),
    (r"锈蚀|腐蚀|生锈", FailureMode.CORROSION),
    (r"装配不当|安装错误|未正确安装", FailureMode.IMPROPER_ASSEMBLY),
    (r"软件|固件|系统更新|OTA", FailureMode.SOFTWARE_DEFECT),
    (r"泄漏|渗漏|漏油|漏液|滴漏", FailureMode.LEAKAGE),
    (r"过热|高温|发热", FailureMode.OVERHEATING),
    (r"松动|松脱|脱落|紧固", FailureMode.LOOSE_CONNECTION),
    (r"性能下降|动力下降|加速无力", FailureMode.PERFORMANCE_DEGRADATION),
]

# ==================== 中文/口语 Consequence ====================

CN_CONS_RULES: list[tuple[str, Consequence]] = [
    (r"碰撞|撞车|追尾|事故|翻车", Consequence.COLLISION),
    (r"失控|失去控制", Consequence.LOSS_OF_CONTROL),
    (r"受伤|伤亡|死亡|人员伤害", Consequence.OCCUPANT_INJURY),
    (r"起火|自燃|燃烧|火灾", Consequence.FIRE),
    (r"无法停车|不能停车|停不下来", Consequence.FAILURE_TO_STOP),
    (r"偏离|跑偏|方向盘不正", Consequence.STEERING_DEVIATION),
    (r"视野|能见度|看不清", Consequence.REDUCED_VISIBILITY),
    (r"未授权|非法访问|泄露|隐私", Consequence.UNINTENDED_ACCESS),
]

# ==================== 中文 OperatingCondition ====================

CN_COND_RULES: list[tuple[str, OperatingCondition]] = [
    (r"夜间|晚上|夜晚|天黑", OperatingCondition.NIGHT),
    (r"雨天|下雨|暴雨|涉水", OperatingCondition.RAIN),
    (r"雾天|大雾|雾", OperatingCondition.FOG),
    (r"高速|高速公路", OperatingCondition.HIGH_SPEED),
    (r"低速|低速行驶", OperatingCondition.LOW_SPEED),
    (r"停车|静止|原地", OperatingCondition.STOPPED),
    (r"行驶中|驾驶中|行驶过程", OperatingCondition.MOVING),
    (r"充电|充电中", OperatingCondition.CHARGING),
    (r"自动驾驶|辅助驾驶|自动泊车", OperatingCondition.ADAS_ACTIVE),
]


class SourceSpecificAnalyzer:
    """按 source_type 分流的分析器（统一输出 AnalysisResult）。"""

    def __init__(self) -> None:
        self._base = IncidentAnalyzer()

    def analyze(self, cluster, source_types: list[str] | None = None) -> AnalysisResult:
        """增强分析：先跑基础分析，再按来源类型补强 FailureMode/Consequence/Condition。"""
        a = self._base.analyze(cluster)
        full = a.full_text().lower() if a.full_text() else ""
        if not full:
            return a

        # 判定来源类型（来自 cluster 的 source_ids）
        srcs = " ".join(source_types or [])
        is_cn = "CN" in srcs or bool(re.search(r"[\u4e00-\u9fff]", full))
        is_complaint = "COMPLAINT" in srcs

        # 补强 FailureMode
        base_fms = set(m.value for m in a.failure_modes)
        if FailureMode.UNKNOWN.value in base_fms or len(a.failure_modes) <= 1:
            if is_cn:
                rules = CN_FM_RULES
            elif is_complaint:
                rules = COMPLAINT_FM_RULES
            else:
                rules = COMPLAINT_FM_RULES  # 通用增强
            for pattern, mode in rules:
                if re.search(pattern, full, re.IGNORECASE):
                    if mode.value not in base_fms:
                        a.failure_modes.append(mode)
                        base_fms.add(mode.value)

        # 补强 Consequence（中文）
        base_cons = set(c.value for c in a.consequences)
        if is_cn:
            for pattern, cons in CN_CONS_RULES:
                if re.search(pattern, full, re.IGNORECASE) and cons.value not in base_cons:
                    a.consequences.append(cons)
                    base_cons.add(cons.value)

        # 补强 OperatingCondition（中文）
        base_conds = set(c.value for c in a.operating_conditions)
        if is_cn:
            for pattern, cond in CN_COND_RULES:
                if re.search(pattern, full, re.IGNORECASE) and cond.value not in base_conds:
                    a.operating_conditions.append(cond)
                    base_conds.add(cond.value)

        # 重新计算 severity（取最严重后果）
        sevs = [c.severity for c in a.consequences]
        new_sev = min(sevs, default=a.severity)
        if new_sev != a.severity:
            a.severity = new_sev
            a.severity_label = {1: "SEV1_伤亡失控", 2: "SEV2_碰撞火灾", 3: "SEV3_功能失效", 4: "SEV4_合规一般"}[new_sev]

        return a


if __name__ == "__main__":
    print("Source-Specific Analyzer 加载成功（COMPLAINT 口语正则 + CN 中文正则）")
