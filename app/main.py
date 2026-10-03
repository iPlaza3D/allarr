from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import auto, config, services
from . import calendar as cal
from .synology import DownloadStation
from .tmdb import TMDB

app = FastAPI(title="allarr")
STATIC = Path(__file__).parent / "static"


def _tmdb() -> TMDB:
    s = config.get_settings()
    return TMDB(s["tmdb_api_key"], s["language"])


def _ds() -> DownloadStation:
    s = config.get_settings()
    return DownloadStation(s["ds_url"], s["ds_user"], s["ds_password"], s["ds_destination"])


def _guard(fn):
    try:
        return fn()
    except ValueError as e:
        raise HTTPException(400, str(e))
    except (httpx.HTTPError, RuntimeError, LookupError) as e:
        raise HTTPException(502, f"{type(e).__name__}: {e}")


@app.get("/api/settings")
def get_settings():
    return config.masked(config.get_settings())


@app.put("/api/settings")
def put_settings(values: dict):
    config.save_settings(values)
    return config.masked(config.get_settings())


@app.get("/api/search")
def search(q: str):
    return _guard(lambda: _tmdb().search(q))


@app.get("/api/discover/{row}")
def discover_row(row: str):
    rows = {
        "trending_movie": lambda t: t.trending("movie"),
        "trending_tv": lambda t: t.trending("tv"),
        "popular_movie": lambda t: t.popular("movie"),
        "popular_tv": lambda t: t.popular("tv"),
        "upcoming": lambda t: t.upcoming(),
    }
    if row not in rows:
        raise HTTPException(404, "Fila desconocida")
    return _guard(lambda: rows[row](_tmdb()))


@app.get("/api/details/{media_type}/{tmdb_id}")
def details(media_type: str, tmdb_id: int):
    if media_type not in ("movie", "tv"):
        raise HTTPException(400, "media_type inválido")
    return _guard(lambda: _tmdb().details(media_type, tmdb_id))


@app.get("/api/trending/{media_type}")
def trending(media_type: str):
    if media_type not in ("movie", "tv"):
        raise HTTPException(400, "media_type inválido")
    return _guard(lambda: _tmdb().trending(media_type))


class Item(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    year: str = ""
    poster: Optional[str] = None


@app.get("/api/calendar")
def calendar(start: str, end: str):
    try:
        d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "Fechas inválidas (YYYY-MM-DD)")
    if d1 < d0 or (d1 - d0).days > 62:
        raise HTTPException(400, "Rango inválido (máx. 62 días)")
    return _guard(lambda: cal.build(start, end))


@app.get("/api/watchlist")
def watchlist():
    with config.conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM watchlist ORDER BY added_at DESC")]


@app.post("/api/watchlist")
def add_watch(item: Item):
    with config.conn() as c:
        c.execute("INSERT OR IGNORE INTO watchlist (tmdb_id, media_type, title, year, poster) VALUES (?,?,?,?,?)",
                  (item.tmdb_id, item.media_type, item.title, item.year, item.poster))
    return {"ok": True}


@app.delete("/api/watchlist/{media_type}/{tmdb_id}")
def del_watch(media_type: str, tmdb_id: int):
    with config.conn() as c:
        c.execute("DELETE FROM watchlist WHERE tmdb_id=? AND media_type=?", (tmdb_id, media_type))
    return {"ok": True}


@app.get("/api/torrents")
def torrents(q: str, media_type: str = "movie"):
    return services.search_torrents(config.get_settings(), q, media_type)


class Grab(BaseModel):
    link: str
    title: str = "download"
    source: str = ""
    page: bool = False


@app.post("/api/grab")
def grab(g: Grab):
    return _guard(lambda: services.grab(config.get_settings(), g.link, g.title, g.source, g.page))


@app.post("/api/auto/run")
def auto_run():
    return _guard(lambda: auto.run_once())


@app.get("/api/downloads")
def downloads():
    def run():
        with _ds() as ds:
            return ds.list_tasks()
    return _guard(run)


@app.post("/api/downloads/{task_id}/{action}")
def download_action(task_id: str, action: str):
    if action not in ("pause", "resume", "delete"):
        raise HTTPException(400, "acción inválida")

    def run():
        with _ds() as ds:
            getattr(ds, action)(task_id)
        return {"ok": True}
    return _guard(run)


@app.get("/api/vpn")
def vpn_status():
    """IP pública vista a través del proxy VPN (comprobación de que el túnel funciona)."""
    s = config.get_settings()

    def run():
        with httpx.Client(proxy=s["vpn_proxy"], timeout=15) as c:
            return c.get("https://ipinfo.io/json").json()
    return _guard(run)


@app.on_event("startup")
def _start():
    auto.start_scheduler()


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
