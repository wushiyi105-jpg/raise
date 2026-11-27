"""命令行：seed / readiness / draft / check / doctor / serve。"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.llm import build_llm
from ..adapters.notify import WebhookNotifier
from ..adapters.store import SqliteStore
from ..app.run import PROMPT, draft, readiness, script
from ..app.selfreview import build_review
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


def _notify(settings: Settings, text: str) -> None:
    if not text or not settings.webhook_url:
        return
    ok = WebhookNotifier(settings.webhook_url).send(text)
    console.print(f"[dim]webhook {'ok' if ok else 'failed'}[/]")


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
    llm = build_llm(s.llm_base_url, s.llm_api_key, s.llm_model, PROMPT) if s.llm_enabled else None
    text, notes = draft(store, s, level or None, llm)
    body: list[str] = []
    if text:
        console.print(text)
        body.append(text)
    for n in notes:
        console.print(f"  [yellow]{n}[/]")
        body.append(n)
    if not text:
        line = "模型没开，只看 readiness"
        console.print(line)
        body.append(line)
    _notify(s, "\n".join(body))


@app.command()
def selfreview(
    level: str = typer.Option("P6", help="P5 / P6 / P7"),
    out: Path = typer.Option(None, help="输出 Markdown；不填打印到终端"),
) -> None:
    """一份能交上去的 STAR 自评稿 + 谈薪五阶段。"""
    try:
        body = build_review(level)
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=2) from exc
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        console.print(f"[green]已写出[/] {out}（{len(body.splitlines())} 行）")
    else:
        console.print(body)


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
