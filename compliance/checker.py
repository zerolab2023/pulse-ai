"""컴플라이언스 검사기 (fail-closed).

글 텍스트를 룰셋으로 훑어 위반 후보를 찾고, 최종 판정을 내린다.

판정(decision):
  - "BLOCK"  : block 규칙이 1건이라도 걸림 → 발행 불가. 사람 검토/수정 필요.
  - "REVIEW" : warn 규칙만 걸림 → 검토 후 발행.
  - "PASS"   : 아무것도 안 걸림 → 통과.

fail-closed 원칙: 확신이 없으면 통과시키지 않는다. block 우선.
이 검사는 1차 필터이며, 사전심의/의료인 감수를 대체하지 않는다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .rules import RULES, Rule


@dataclass
class Violation:
    category: str
    severity: str
    matched: str          # 실제로 걸린 텍스트 조각
    context: str          # 앞뒤 포함한 문맥(사람이 판단하기 쉽게)
    reason: str
    suggestion: str


@dataclass
class Report:
    decision: str                 # BLOCK | REVIEW | PASS
    violations: list[Violation] = field(default_factory=list)

    @property
    def block_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "block")

    @property
    def warn_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warn")


def _context(text: str, start: int, end: int, width: int = 20) -> str:
    a = max(0, start - width)
    b = min(len(text), end + width)
    snippet = text[a:b].replace("\n", " ")
    return f"...{snippet}..."


def check(text: str, rules: list[Rule] = RULES) -> Report:
    violations: list[Violation] = []
    for rule in rules:
        for m in re.finditer(rule.pattern, text, flags=re.IGNORECASE):
            violations.append(
                Violation(
                    category=rule.category,
                    severity=rule.severity,
                    matched=m.group(0),
                    context=_context(text, m.start(), m.end()),
                    reason=rule.reason,
                    suggestion=rule.suggestion,
                )
            )

    if any(v.severity == "block" for v in violations):
        decision = "BLOCK"
    elif violations:
        decision = "REVIEW"
    else:
        decision = "PASS"

    # block을 위로 정렬
    violations.sort(key=lambda v: 0 if v.severity == "block" else 1)
    return Report(decision=decision, violations=violations)
