"""FastAPI + Jinja2：证据台账。"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..adapters.store import SqliteStore
from ..app.run import readiness
from ..config import Settings
from ..domain.engine import top
from ..domain.rules.quantify import is_quantified
from ..domain.rules.star import missing

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


def create_app(settings: Settings, store: SqliteStore | None = None) -> FastAPI:
    app = FastAPI(title="Raise", version="1.0.0")
    store = store or SqliteStore(settings.db_path)

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, level: str = "") -> HTMLResponse:
        r = readiness(store, level or None)
        items = store.list_achievements()
        return TEMPLATES.TemplateResponse(
            request, "index.html",
            {"r": r, "items": items, "top": top(items, 4), "is_q": is_quantified,
             "reviews": [(x, missing(x)) for x in store.list_reviews()], "level": level, "levels": store.list_levels()},
        )

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "achievements": len(store.list_achievements())}

    return app


def app_factory(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        from ..config import settings as default_settings

        settings = default_settings
    return create_app(settings)
