"""端口：app 实际调用的方法集合，实现见 adapters。"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain.models import Achievement, Level, Review


@runtime_checkable
class StorePort(Protocol):
    def list_achievements(self) -> list[Achievement]: ...

    def level(self, code: str | None = None) -> Level | None: ...

    def list_reviews(self) -> list[Review]: ...


@runtime_checkable
class LLMPort(Protocol):
    def write(self, system: str, facts: str) -> str: ...
