"""SQLite：achievements / levels / reviews / jobs。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Float, Integer, String, inspect, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker
from sqlalchemy.orm import Session as OrmSession

from ...domain.models import Achievement, Level, Review
from .base import Base, make_engine, make_session


class AchieveRow(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(300))
    impact: Mapped[float] = mapped_column(Float, default=0.0)
    scope: Mapped[str] = mapped_column(String(20), default="team")
    quarter: Mapped[str] = mapped_column(String(10), default="")


class LevelRow(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    years: Mapped[int] = mapped_column(Integer, default=3)
    need_count: Mapped[int] = mapped_column(Integer, default=6)
    need_scope: Mapped[str] = mapped_column(String(60), default="team")


class ReviewRow(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story: Mapped[str] = mapped_column(String(400))
    level: Mapped[str] = mapped_column(String(10), default="")
    sections: Mapped[str] = mapped_column(String(20), default="")


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idem_key: Mapped[str] = mapped_column(String(80), unique=True)


class SqliteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.engine = make_engine(self.path)
        self.session: sessionmaker[OrmSession] = make_session(self.engine)
        self.init_schema()

    def init_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def schema_ok(self) -> bool:
        return {"achievements", "levels", "reviews", "jobs"} <= set(inspect(self.engine).get_table_names())

    def summary(self) -> str:
        return f"{len(self.list_achievements())} 条成果、{len(self.list_reviews())} 份复盘"

    def add_achievement(self, text: str, impact: float = 0.0, scope: str = "team", quarter: str = "") -> int:
        if not text.strip():
            raise ValueError("成果不能为空")
        if impact < 0:
            raise ValueError("影响分不能为负")
        with self.session() as s:
            row = AchieveRow(text=text, impact=impact, scope=scope, quarter=quarter)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_achievements(self) -> list[Achievement]:
        with self.session() as s:
            rows = s.scalars(select(AchieveRow)).all()
        return [Achievement(r.id, r.text, float(r.impact), r.scope, r.quarter) for r in rows]

    def add_level(self, code: str, years: int, need_count: int, need_scope: list[str]) -> int:
        with self.session() as s:
            row = LevelRow(code=code, years=years, need_count=need_count, need_scope="|".join(need_scope))
            s.add(row)
            s.commit()
            return int(row.id)

    def level(self, code: str | None = None) -> Level | None:
        with self.session() as s:
            q = select(LevelRow)
            if code:
                q = q.where(LevelRow.code == code)
            row = s.scalars(q.order_by(LevelRow.id.desc())).first()
        if row is None:
            return None
        scopes = tuple(x for x in row.need_scope.split("|") if x)
        return Level(row.id, row.code, row.years, row.need_count, scopes)

    def list_levels(self) -> list[Level]:
        with self.session() as s:
            rows = s.scalars(select(LevelRow)).all()
        return [Level(r.id, r.code, r.years, r.need_count, tuple(x for x in r.need_scope.split("|") if x)) for r in rows]

    def add_review(self, story: str, level: str = "", sections: list[str] | None = None) -> int:
        with self.session() as s:
            row = ReviewRow(story=story, level=level, sections="".join(sections or []))
            s.add(row)
            s.commit()
            return int(row.id)

    def list_reviews(self) -> list[Review]:
        with self.session() as s:
            rows = s.scalars(select(ReviewRow)).all()
        return [Review(r.id, r.story, r.level, tuple(r.sections[i] for i in range(len(r.sections)))) for r in rows]

    def add_job(self, idem_key: str) -> bool:
        with self.session() as s:
            if s.scalars(select(JobRow).where(JobRow.idem_key == idem_key)).first():
                return False
            s.add(JobRow(idem_key=idem_key))
            s.commit()
            return True
