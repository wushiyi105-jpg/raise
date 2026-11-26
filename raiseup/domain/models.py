"""领域对象：成果、职级、复盘稿。"""

from __future__ import annotations

from dataclasses import dataclass, field

STAR = ("S", "T", "A", "R")
STAR_LABEL = {"S": "情境", "T": "任务", "A": "动作", "R": "结果"}


@dataclass(frozen=True)
class Achievement:
    id: int
    text: str
    impact: float = 0.0
    scope: str = "team"
    quarter: str = ""


@dataclass(frozen=True)
class Level:
    id: int
    code: str
    years: int
    need_count: int
    need_scope: tuple[str, ...] = ("team",)


@dataclass(frozen=True)
class Review:
    id: int
    story: str
    level: str = ""
    sections: tuple[str, ...] = ()


@dataclass
class Finding:
    rule_id: str
    message: str
    penalty: int
    target: str = ""


@dataclass
class Readiness:
    level: Level | None = None
    quantified: int = 0
    total: int = 0
    scopes: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        return self.quantified / self.total if self.total else 0.0

    @property
    def penalty_total(self) -> int:
        return sum(f.penalty for f in self.findings)
