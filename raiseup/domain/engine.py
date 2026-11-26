"""本地核算：量化率、职级差距、复盘完整度。"""

from __future__ import annotations

from .models import Achievement, Finding, Level, Readiness, Review
from .rules.level import check as level_check
from .rules.level import scope_counts
from .rules.quantify import check as quant_check
from .rules.quantify import counted
from .rules.star import check as star_check


def build(items: list[Achievement], level: Level | None, reviews: list[Review]) -> Readiness:
    r = Readiness(level=level, total=len(items), quantified=counted(items), scopes=scope_counts(items))
    findings: list[Finding] = []
    findings += quant_check(items)
    if level:
        findings += level_check(items, level)
    findings += star_check(reviews)
    r.findings = findings
    return r


def top(items: list[Achievement], n: int = 5) -> list[Achievement]:
    return sorted(items, key=lambda a: a.impact, reverse=True)[:n]
