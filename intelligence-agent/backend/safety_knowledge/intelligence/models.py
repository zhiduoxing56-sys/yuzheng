"""情报收集智能体 v3 —— I1 数据模型 + I2 枚举体系

术语固定（防概念混淆）：
  - Physical Evidence    ：实时车辆物理信息（VEHICLE_SPEED=60km/h）
  - Trusted Knowledge Node：审核后的正式安全知识（L1-L2）
  - Candidate Risk Node  ：事故产生的候选风险知识（L5/PENDING_REVIEW）
  - Incident Record      ：原始事故/召回记录（不可变快照）

追溯链：CandidateNode → IncidentCluster → SourceRecord → RawSnapshot
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ==================== I2: 枚举体系 ====================

class FailureMode(str, Enum):
    """失效模式枚举（结构化事故分析）。"""
    UNINTENDED_ACTIVATION = "UNINTENDED_ACTIVATION"      # 非预期激活
    FAIL_TO_ACTIVATE = "FAIL_TO_ACTIVATE"                # 激活失败
    INTERMITTENT_FAILURE = "INTERMITTENT_FAILURE"        # 间歇性失效
    LOSS_OF_FUNCTION = "LOSS_OF_FUNCTION"                # 功能丧失
    DELAYED_RESPONSE = "DELAYED_RESPONSE"                # 响应延迟
    INCORRECT_STATE = "INCORRECT_STATE"                  # 状态错误
    UNCOMMANDED_MOVEMENT = "UNCOMMANDED_MOVEMENT"        # 非指令运动
    DATA_CORRUPTION = "DATA_CORRUPTION"                  # 数据损坏
    AUTHENTICATION_BYPASS = "AUTHENTICATION_BYPASS"      # 认证绕过
    CORROSION = "CORROSION"                              # 腐蚀
    IMPROPER_ASSEMBLY = "IMPROPER_ASSEMBLY"              # 装配不当
    SOFTWARE_DEFECT = "SOFTWARE_DEFECT"                  # 软件缺陷
    LEAKAGE = "LEAKAGE"                                  # 泄漏
    OVERHEATING = "OVERHEATING"                          # 过热
    LOOSE_CONNECTION = "LOOSE_CONNECTION"                # 连接松动
    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"  # 性能退化
    UNKNOWN = "UNKNOWN"                                  # 未明确

    @classmethod
    def from_text(cls, text: str) -> list["FailureMode"]:
        """正则提取（返回命中的枚举，保持顺序）。"""
        import re
        lowered = text.lower()
        hits = []
        rules = [
            (r"unintended|sudden|non.?expected", FailureMode.UNINTENDED_ACTIVATION),
            (r"fail\s*to (activate|engage|operate)|cannot (activate|start)|不会激活|无法激活", FailureMode.FAIL_TO_ACTIVATE),
            (r"intermittent|间歇|时好时坏", FailureMode.INTERMITTENT_FAILURE),
            (r"loss of (function|control)|功能丧失|失灵|失效", FailureMode.LOSS_OF_FUNCTION),
            (r"delay|延迟|滞", FailureMode.DELAYED_RESPONSE),
            (r"incorrect|wrong state|状态错误|错误状态|mis-?state", FailureMode.INCORRECT_STATE),
            (r"uncommanded|self-?mov|自行移动|非指令", FailureMode.UNCOMMANDED_MOVEMENT),
            (r"data corruption|corrupt|数据损坏", FailureMode.DATA_CORRUPTION),
            (r"auth.? bypass|认证绕过|bypass", FailureMode.AUTHENTICATION_BYPASS),
            (r"corrosion|锈蚀|腐蚀", FailureMode.CORROSION),
            (r"improper|not properly|未正确|不正确", FailureMode.IMPROPER_ASSEMBLY),
            (r"software|固件|软件", FailureMode.SOFTWARE_DEFECT),
            (r"leak|泄漏|渗漏", FailureMode.LEAKAGE),
            (r"overheat|过热", FailureMode.OVERHEATING),
            (r"loose|松动|脱落", FailureMode.LOOSE_CONNECTION),
            (r"degrad|性能下降|reduc", FailureMode.PERFORMANCE_DEGRADATION),
        ]
        for pattern, mode in rules:
            if re.search(pattern, lowered):
                hits.append(mode)
        return hits or [FailureMode.UNKNOWN]

    @classmethod
    def subtype(cls, text: str, family: "FailureMode") -> str:
        """G3：二级失效模式（Family → Subtype）。
        重点拆分 SOFTWARE_DEFECT，防止"都叫软件缺陷"被聚成同一类风险。"""
        import re
        lowered = text.lower()
        if family == FailureMode.SOFTWARE_DEFECT:
            rules = [
                (r"logic|逻辑|incorrect calculation|算错", "SOFTWARE_LOGIC_ERROR"),
                (r"timing|时序|timing", "SOFTWARE_TIMING_ERROR"),
                (r"state machine|状态机|state", "SOFTWARE_STATE_MACHINE_ERROR"),
                (r"update|upgrade|升级|ota", "SOFTWARE_UPDATE_FAILURE"),
                (r"sensor|sensing|感知|传感", "SOFTWARE_SENSOR_PROCESSING_ERROR"),
                (r"actuator|command|执行器|指令", "SOFTWARE_ACTUATOR_COMMAND_ERROR"),
                (r"communicat|通信|comm", "SOFTWARE_COMMUNICATION_ERROR"),
                (r"memory|存储|memory", "SOFTWARE_MEMORY_ERROR"),
                (r"display|显示|screen", "SOFTWARE_UI_ERROR"),
            ]
            for pattern, sub in rules:
                if re.search(pattern, lowered):
                    return sub
            return "SOFTWARE_GENERIC"
        return ""


class Consequence(str, Enum):
    """后果枚举（含危害等级权重）。"""
    OCCUPANT_INJURY = "OCCUPANT_INJURY"            # 乘员伤害
    LOSS_OF_CONTROL = "LOSS_OF_CONTROL"            # 失控
    UNINTENDED_ACCELERATION = "UNINTENDED_ACCELERATION"  # 非预期加速
    UNINTENDED_BRAKING = "UNINTENDED_BRAKING"      # 非预期制动
    COLLISION = "COLLISION"                        # 碰撞
    FIRE = "FIRE"                                  # 起火
    FAILURE_TO_STOP = "FAILURE_TO_STOP"            # 无法停车
    STEERING_DEVIATION = "STEERING_DEVIATION"      # 转向偏移
    REDUCED_VISIBILITY = "REDUCED_VISIBILITY"      # 视野降低
    UNINTENDED_ACCESS = "UNINTENDED_ACCESS"        # 非授权访问
    FMVSS_NONCOMPLIANCE = "FMVSS_NONCOMPLIANCE"    # 法规不合规
    COMPONENT_FAILURE = "COMPONENT_FAILURE"        # 部件失效
    UNKNOWN = "UNKNOWN"

    @property
    def severity(self) -> int:
        """危害等级 1（最高）- 4（最低）。"""
        return {
            Consequence.OCCUPANT_INJURY: 1, Consequence.LOSS_OF_CONTROL: 1,
            Consequence.UNINTENDED_ACCELERATION: 1, Consequence.UNINTENDED_BRAKING: 1,
            Consequence.COLLISION: 2, Consequence.FIRE: 2,
            Consequence.FAILURE_TO_STOP: 2, Consequence.STEERING_DEVIATION: 2,
            Consequence.REDUCED_VISIBILITY: 3, Consequence.UNINTENDED_ACCESS: 3,
            Consequence.COMPONENT_FAILURE: 3, Consequence.FMVSS_NONCOMPLIANCE: 4,
            Consequence.UNKNOWN: 4,
        }[self]

    @classmethod
    def from_text(cls, text: str) -> list["Consequence"]:
        import re
        lowered = text.lower()
        hits = []
        rules = [
            (r"injury|受伤|伤亡|death|死亡|occupant", Consequence.OCCUPANT_INJURY),
            (r"loss of control|失控", Consequence.LOSS_OF_CONTROL),
            (r"unintended accel|sudden accel|误加速|突然加速", Consequence.UNINTENDED_ACCELERATION),
            (r"unintended brake|误制动|突然制动", Consequence.UNINTENDED_BRAKING),
            (r"crash|collision|碰撞|撞车|accident", Consequence.COLLISION),
            (r"fire|自燃|起火|burn", Consequence.FIRE),
            (r"fail\s*to stop|无法停车|不能停车|not stop", Consequence.FAILURE_TO_STOP),
            (r"steer|偏离|deviation|pull", Consequence.STEERING_DEVIATION),
            (r"visibility|视野|能见度|illuminat", Consequence.REDUCED_VISIBILITY),
            (r"access|non.?authorized|未授权", Consequence.UNINTENDED_ACCESS),
            (r"noncompliance|not comply|不符合|comply", Consequence.FMVSS_NONCOMPLIANCE),
            (r"failure|故障|fail", Consequence.COMPONENT_FAILURE),
        ]
        for pattern, cons in rules:
            if re.search(pattern, lowered):
                hits.append(cons)
        return hits or [Consequence.UNKNOWN]


class OperatingCondition(str, Enum):
    """运行条件枚举（事故发生时的车辆状态）。"""
    NIGHT = "NIGHT"
    RAIN = "RAIN"
    FOG = "FOG"
    HIGH_SPEED = "HIGH_SPEED"
    LOW_SPEED = "LOW_SPEED"
    STOPPED = "STOPPED"
    PARKED = "PARKED"
    MOVING = "MOVING"
    CHARGING = "CHARGING"
    ADAS_ACTIVE = "ADAS_ACTIVE"
    MANUAL_DRIVING = "MANUAL_DRIVING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_text(cls, text: str) -> list["OperatingCondition"]:
        import re
        lowered = text.lower()
        hits = []
        rules = [
            (r"night|夜间|夜晚|dark", OperatingCondition.NIGHT),
            (r"rain|雨天|下雨|wet", OperatingCondition.RAIN),
            (r"fog|雾", OperatingCondition.FOG),
            (r"highway|high speed|高速", OperatingCondition.HIGH_SPEED),
            (r"low speed|低速", OperatingCondition.LOW_SPEED),
            (r"stop|静止|停车", OperatingCondition.STOPPED),
            (r"park|驻车|泊车", OperatingCondition.PARKED),
            (r"move|行驶|driving", OperatingCondition.MOVING),
            (r"charge|充电", OperatingCondition.CHARGING),
            (r"autonomous|self-?driving|自动驾驶|fsd|adas", OperatingCondition.ADAS_ACTIVE),
            (r"manual|人工|手动", OperatingCondition.MANUAL_DRIVING),
        ]
        for pattern, cond in rules:
            if re.search(pattern, lowered):
                hits.append(cond)
        return hits or [OperatingCondition.UNKNOWN]


class SourceAuthority(str, Enum):
    """来源权威等级（决定来源权重）。"""
    OFFICIAL_REGULATOR = "OFFICIAL_REGULATOR"      # 监管机构（NHTSA/DPAC）
    OEM_OFFICIAL = "OEM_OFFICIAL"                  # 主机厂官方
    GOVERNMENT = "GOVERNMENT"                      # 政府机构
    MEDIA = "MEDIA"                                # 专业媒体
    USER_REPORT = "USER_REPORT"                    # 用户报告/投诉


class ReviewPriority(str, Enum):
    """审核优先级（仅排序，不参与安全裁决）。"""
    P0 = "P0"   # 优先人工审核
    P1 = "P1"   # 普通审核
    P2 = "P2"   # 低优先级归档


class NoveltyLabel(str, Enum):
    KNOWN = "KNOWN"
    PARTIAL_NOVEL = "PARTIAL_NOVEL"
    NOVEL = "NOVEL"
    IRRELEVANT = "IRRELEVANT"


class MappingStatus(str, Enum):
    MAPPED = "MAPPED"
    ABSTAIN = "ABSTAIN"        # 无法映射到现有意图（本体覆盖缺口）


class ReviewVerdict(str, Enum):
    REJECT = "REJECT"
    MERGE = "MERGE"
    PROMOTE = "PROMOTE"


# ==================== I1: 数据模型 ====================

@dataclass(frozen=True, slots=True)
class SourceRecord:
    """原始事实快照（不可变）。"""
    source_id: str
    source_type: SourceAuthority
    retrieved_at: str
    url: str
    raw_title: str
    raw_content: str
    content_hash: str
    parser_version: str
    official_confirmed: bool = False


@dataclass
class IncidentCluster:
    """事故聚合单元：一个 Cluster = 同一事故的多源记录。"""
    cluster_id: str
    subject: str                       # 主题（如 尾灯间歇失效）
    component_family: str
    component_sub: str
    records: list[SourceRecord] = field(default_factory=list)
    corroboration_count: int = 1
    official_confirmed: bool = False

    def add_record(self, rec: SourceRecord) -> None:
        self.records.append(rec)
        self.corroboration_count = len(self.records)
        self.official_confirmed = self.official_confirmed or rec.official_confirmed


@dataclass
class AnalyzedIncident:
    """分析结果（Cluster → 结构化分析）。"""
    cluster_id: str
    subject: str
    components: list[str]
    capability_domains: list[str]
    failure_modes: list[FailureMode]
    operating_conditions: list[OperatingCondition]
    consequences: list[Consequence]
    severity: int                        # 1-4
    severity_label: str
    candidate_intents: list[str]         # 三路融合候选（可能为空）
    mapping_status: MappingStatus
    mapping_reasons: dict[str, list[str]]  # 各路贡献
    candidate_evidence: list[str]
    source_authority: SourceAuthority
    official_confirmed: bool
    corroboration_count: int
    novelty_label: NoveltyLabel
    novelty_score: float
    novelty_reasons: list[str]
    review_priority: ReviewPriority
    priority_reason: str
    provenance: list[str]                # 追溯链描述
    analysis_version: str = "v3.0"


@dataclass
class CandidateRiskNode:
    """候选风险知识节点（L5/PENDING_REVIEW，KnowledgeNode v2 Schema 对齐）。"""
    node_id: str
    title: str
    semantic_description: str
    canonical_action: str                # "" 表示 ABSTAIN/UNMAPPED
    conditions: list[str]
    required_evidence: list[str]
    optional_evidence: list[str]
    source: str
    trust_level: str = "L5"
    vector: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_knowledge_node(self) -> dict:
        """转 KnowledgeNode v2 字典。"""
        return {
            "node_id": self.node_id, "node_type": "候选风险",
            "title": self.title, "semantic_description": self.semantic_description,
            "canonical_action": self.canonical_action, "conditions": self.conditions,
            "required_evidence": self.required_evidence, "optional_evidence": self.optional_evidence,
            "source": self.source, "chapter": "", "clause": "",
            "trust_level": self.trust_level, "vector": self.vector, "metadata": self.metadata,
        }


@dataclass
class ReviewDecision:
    """人工审核决策（留痕）。"""
    cluster_id: str
    decision: ReviewVerdict
    reviewer: str
    reviewed_at: str
    reason: str
    merged_into: str | None = None        # MERGE 时指向目标 cluster_id
    promoted_node_id: str | None = None   # PROMOTE 时指向晋级后的 node_id
    version: str = "1.0"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
