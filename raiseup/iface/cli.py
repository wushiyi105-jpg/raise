"""命令行：seed / readiness / draft / check / doctor / serve。"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.store import SqliteStore
from ..app.run import draft, readiness, script
from ..config import Settings
from ..config import settings as default_settings
from ..doctor import main as doctor_main

app = typer.Typer(help="晋升材料：先看证据", no_args_is_help=True)
console = Console()


def _settings(db: Path | None, port: int | None = None) -> Settings:
    s = default_settings.model_copy(deep=True)
    if db:
        s.db_path = db
    if port:
        s.port = port
    return s


def _store(settings: Settings) -> SqliteStore:
    return SqliteStore(settings.db_path)


@app.command()
def seed(db: Path = typer.Option(None)) -> None:
    """写入成果、职级、复盘稿。"""
    s = _settings(db)
    store = _store(s)
    data = json.loads(
        (Path(__file__).resolve().parents[2] / "data" / "seed.json").read_text(encoding="utf-8")
    )
    for a in data["achievements"]:
        store.add_achievement(a["text"], a.get("impact", 0.0), a.get("scope", "team"), a.get("quarter", ""))
    for lv in data["levels"]:
        store.add_level(lv["code"], lv["years"], lv["need_count"], lv["need_scope"])
    for r in data.get("reviews", []):
        store.add_review(r["story"], r.get("level", ""), r.get("sections", []))
    console.print(f"已写入 {len(data['achievements'])} 条成果、{len(data['levels'])} 个职级")


@app.command("readiness")
def readiness_cmd(level: str = typer.Option("", help="P6 这样"), db: Path = typer.Option(None)) -> None:
    """量化率、职级差距、复盘完整度。"""
    store = _store(_settings(db))
    r = readiness(store, level or None)
    console.print(f"量化 {r.quantified}/{r.total}（{r.ratio:.0%}），范围 {r.scopes}")
    for f in r.findings:
        console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")
    console.print(f"合计扣 {r.penalty_total} 分")




@app.command("draft")
def draft_cmd(level: str = typer.Option(""), db: Path = typer.Option(None)) -> None:
    """模型起草（无 key 时不编）。"""
    s = _settings(db)
    store = _store(s)
    text, notes = draft(store, s, level or None)
    if text:
        console.print(text)
    for n in notes:
        console.print(f"  [yellow]{n}[/]")
    if not text:
        console.print("模型没开，只看 readiness")




@app.command("check")
def check_cmd(text: str = typer.Option(..., help="要检查的谈薪/材料稿"), db: Path = typer.Option(None)) -> None:
    """检查稿子里的数字与措辞。"""
    store = _store(_settings(db))
    notes = script(store, text)
    if not notes:
        console.print("数字都能对上证据")
    for n in notes:
        console.print(f"  [yellow]{n}[/]")




@app.command()
def doctor(db: Path = typer.Option(None)) -> None:
    """四项体检。"""
    raise typer.Exit(code=doctor_main(_settings(db)))


@app.command()
def serve(port: int = typer.Option(None), db: Path = typer.Option(None)) -> None:
    """Web 界面。"""
    import uvicorn

    from .web import create_app

    s = _settings(db, port)
    uvicorn.run(create_app(s), host="127.0.0.1", port=s.port)


if __name__ == "__main__":
    app()
