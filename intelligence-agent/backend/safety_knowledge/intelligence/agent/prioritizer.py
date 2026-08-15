"""情报智能体 v3 —— Layer 6: Review Priority Scoring（P0/P1/P2）

设计要点（用户反馈 #2）：
  - 只决定"这条事故值不值得优先审核"，绝不参与车辆安全裁决
  - 与主裁决链的 SafetyScore（CBN）彻底分离
  - 输出：P0（优先人工审核）/ P1（普通审核）/ P2（低优先级归档）+ 理由

优先级函数：
  P = f(Severity, SourceAuthority, VoiceControllability, Novelty, Corroboration)
    P0：官方/权威来源 + SEV<=2 + 车控相关 + (NOVEL 或 PARTIAL_NOVEL) + 多源佐证
    P1：车控相关 + 官方确认 或 SEV<=3
    P2：其余（归档）
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

from safety_knowledge.intelligence.agent.analyzer import AnalysisResult
from safety_knowledge.intelligence.agent.novelty_engine import NoveltyResult
from safety_knowledge.intelligence.models import MappingStatus, ReviewPriority, SourceAuthority


@dataclass
class PriorityResult:
    priority: ReviewPriority
    reason: str
    score: float                      # 0-1（仅排序用）
    factors: dict[str, float]         # 各因素分解（可解释）


class ReviewPrioritizer:
    """Layer 6 实现。"""

    AUTHORITY_WEIGHT = {
        SourceAuthority.OFFICIAL_REGULATOR: 1.0,
        SourceAuthority.OEM_OFFICIAL: 0.8,
        SourceAuthority.GOVERNMENT: 0.6,
        SourceAuthority.MEDIA: 0.3,
        SourceAuthority.USER_REPORT: 0.1,
    }

    def prioritize(self, a: AnalysisResult, novelty: NoveltyResult, mapping_status: MappingStatus,
                   mapped_intents: list[str] | None = None) -> PriorityResult:
        # 因素分解
        f_severity = {1: 1.0, 2: 0.7, 3: 0.4, 4: 0.1}[a.severity]
        f_authority = self.AUTHORITY_WEIGHT[a.source_authority]
        has_voice_control = mapping_status == MappingStatus.MAPPED and bool(mapped_intents)
        f_voice = 1.0 if has_voice_control else 0.0
        f_novelty = {"KNOWN": 0.1, "PARTIAL_NOVEL": 0.5, "NOVEL": 1.0, "IRRELEVANT": 0.0}[novelty.label.value]
        f_corroboration = min(1.0, a.corroboration_count / 3.0)

        score = round(
            0.25 * f_severity + 0.20 * f_authority + 0.25 * f_voice +
            0.15 * f_novelty + 0.15 * f_corroboration, 4
        )

        # P0 判定
        p0_conditions = (
            f_severity >= 0.7                     # SEV<=2
            and f_authority >= 0.8                # 官方来源
            and has_voice_control                 # 车控相关
            and f_novelty >= 0.5                  # NOVEL/PARTIAL
            and f_corroboration >= 0.33           # 至少 2 源佐证（或 1 源官方召回+投诉）
        )
        if p0_conditions:
            return PriorityResult(
                priority=ReviewPriority.P0,
                reason=f"SEV{a.severity}+官方+车控+{novelty.label.value}+{a.corroboration_count}源",
                score=score,
                factors={"severity": f_severity, "authority": f_authority,
                         "voice": f_voice, "novelty": f_novelty, "corroboration": f_corroboration},
            )
        if has_voice_control and (f_authority >= 0.6 or f_severity >= 0.4):
            return PriorityResult(
                priority=ReviewPriority.P1,
                reason=f"车控相关（SEV{a.severity} {a.source_authority.value}）",
                score=score,
                factors={"severity": f_severity, "authority": f_authority,
                         "voice": f_voice, "novelty": f_novelty, "corroboration": f_corroboration},
            )
        return PriorityResult(
            priority=ReviewPriority.P2,
            reason=f"归档（SEV{a.severity} 无车控/低价值）",
            score=score,
            factors={"severity": f_severity, "authority": f_authority,
                     "voice": f_voice, "novelty": f_novelty, "corroboration": f_corroboration},
        )


if __name__ == "__main__":
    print("Review Prioritizer 加载成功（P0/P1/P2，仅排序不裁决）")
