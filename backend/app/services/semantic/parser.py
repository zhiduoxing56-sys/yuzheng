from __future__ import annotations

import re
from typing import Any

from app.models.schemas import SemanticFrame


UNKNOWN = "unknown"


class SemanticFrameParser:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def normalize(self, text: str) -> str:
        normalized = re.sub(r"[\s，。！？、,.!?]", "", text.strip().lower())
        replacements = self.config.get("normalization_replacements", {})
        for source in sorted(replacements, key=len, reverse=True):
            normalized = normalized.replace(source, str(replacements[source]))
        for filler in self.config.get("filler_words", []):
            normalized = normalized.replace(str(filler), "")
        return normalized

    @staticmethod
    def _match_term(text: str, mapping: dict[str, list[str]], prefer_last: bool = False) -> str:
        matches: list[tuple[int, int, str]] = []
        for canonical, terms in mapping.items():
            for term in terms:
                position = text.find(term)
                if position >= 0:
                    matches.append((len(term), position, canonical))
        if not matches:
            return UNKNOWN
        key = (lambda item: (item[1], item[0])) if prefer_last else (lambda item: (item[0], -item[1]))
        return max(matches, key=key)[2]

    def _context_claims(self, text: str) -> dict[str, Any]:
        claims: dict[str, Any] = {}
        for claim, patterns in self.config.get("context_claim_patterns", {}).items():
            matched = [pattern for pattern in patterns if pattern in text]
            if matched:
                claims[claim] = {"claimed": True, "matched_text": matched}
        return claims

    def parse(self, turn_id: str, text: str) -> SemanticFrame:
        normalized = self.normalize(text)
        # 复合声明中前面的“进入模拟器模式”是上下文声明，最后的动词才是车控动作。
        action = self._match_term(normalized, self.config.get("actions", {}), prefer_last=True)
        target = self._match_term(normalized, self.config.get("targets", {}))
        area = self._match_term(normalized, self.config.get("areas", {}))

        domain = UNKNOWN
        for name, targets in self.config.get("domains", {}).items():
            if target in targets:
                domain = name
                break

        vague = any(word in normalized for word in self.config.get("vague_pronouns", []))
        ambiguity = 0.0
        confidence = 1.0
        if action == UNKNOWN:
            ambiguity += 0.45
            confidence -= 0.35
        if target == UNKNOWN:
            ambiguity += 0.45
            confidence -= 0.25
        if vague and target == UNKNOWN:
            ambiguity += 0.20
            confidence -= 0.10

        profile_key = f"{action}|{target}"
        profiles = self.config.get("risk_profiles", {})
        profile = profiles.get(profile_key, profiles.get("default", {}))
        return SemanticFrame(
            turn_id=turn_id,
            raw_text=text,
            normalized_text=normalized,
            action=action,
            target=target,
            area=area,
            control_domain=domain,
            semantic_confidence=max(0.0, min(1.0, confidence)),
            ambiguity_score=max(0.0, min(1.0, ambiguity)),
            risk_level=str(profile.get("level", "R1")),
            risk_tags=list(profile.get("tags", [])),
            context_claims=self._context_claims(normalized),
        )
