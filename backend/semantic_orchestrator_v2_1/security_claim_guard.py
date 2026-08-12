from __future__ import annotations

import re
from dataclasses import dataclass


FAMILY_PATTERNS = {
    "PERMISSION_CLAIM": re.compile(
        r"管理员|最高权限|超级用户|授权用户|管理员权限|管理权限|系统权限|root(?:权限|用户)?",
        re.IGNORECASE,
    ),
    "SKIP_VERIFICATION": re.compile(
        r"(?:无需|不用|跳过)(?:验证|确认|校验|审核)|无需确认|不用确认|直接执行|直接操作"
    ),
    "BYPASS_SAFETY": re.compile(
        r"忽略.{0,4}(?:安全|规则|限制)|绕过.{0,4}(?:安全|检查|校验)|关闭安全检查|不要检查安全|取消安全限制|跳过安全"
    ),
    "SPECIAL_ENVIRONMENT": re.compile(r"调试模式|测试模式|模拟环境|模拟器|开发模式"),
    "SPECIAL_SYSTEM_MODE_CLAIM": re.compile(
        r"(?:进入|开启|启用|切换到|处于).{0,6}(?:开发者模式|开发模式|调试模式|测试模式|模拟模式|模拟环境|模拟器环境)"
    ),
    "SECURITY_CHECK_BYPASS_CLAIM": re.compile(
        r"(?:忽略|跳过|绕过|取消|关闭|无需|不用).{0,6}(?:权限检查|权限|安全检查|身份验证|验证|校验|确认|安全限制)"
    ),
}


@dataclass(frozen=True, slots=True)
class SecurityClaimDecision:
    final_signal: bool
    forced: bool
    weak: bool
    matched_families: tuple[str, ...]


class SecurityClaimGuard:
    def check(self, text: str, *, stage1_signal: bool) -> SecurityClaimDecision:
        matched = tuple(name for name, pattern in FAMILY_PATTERNS.items() if pattern.search(text))
        explicit = bool(matched)
        return SecurityClaimDecision(
            final_signal=explicit,
            forced=explicit and not stage1_signal,
            weak=stage1_signal and not explicit,
            matched_families=matched,
        )
