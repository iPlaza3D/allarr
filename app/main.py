from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import auth, auto, config, library, renamer, services
from . import calendar as cal
from .synology import DownloadStation
from .tmdb import TMDB
from .tvdb import TVDB

app = FastAPI(title="media-server-utility")
STATIC = Path(__file__).parent / "static"


@app.middleware("http")
async def require_login(request: Request, call_next):
    p = request.url.path
    if p.startswith("/api/") and not p.startswith("/api/auth/"):
        if not auth.read_token(request.cookies.get(auth.COOKIE)):
            return JSONResponse({"detail": "Sesión no iniciada"}, status_code=401)
    resp = await call_next(request)
    if not p.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-cache"
    return resp


class Credentials(BaseModel):
    username: str = ""
    password: str = ""
    new_password: str = ""


def _set_cookie(resp: Response, username: str) -> None:
    resp.set_cookie(auth.COOKIE, auth.make_token(username), max_age=auth.SESSION_SECONDS, httponly=True, samesite="lax")


@app.get("/api/auth/status")
def auth_status(request: Request):
    user = auth.read_token(request.cookies.get(auth.COOKIE))
    return {"setup_needed": not auth.has_users(), "authenticated": bool(user), "username": user}


@app.post("/api/auth/setup")
def auth_setup(c: Credentials, response: Response):
    if auth.has_users():
        raise HTTPException(409, "Ya existe una cuenta de administrador")
    name = c.username.strip()
    if not name or len(c.password) < auth.MIN_PASSWORD:
        raise HTTPException(400, f"Indica un usuario y una contraseña de al menos {auth.MIN_PASSWORD} caracteres")
    auth.create_user(name, c.password)
    _set_cookie(response, name)
    return {"ok": True}


@app.post("/api/auth/login")
def auth_login(c: Credentials, request: Request, response: Response):
    ip = request.client.host if request.client else "?"
    if auth.locked(ip):
        raise HTTPException(429, "Demasiados intentos. Espera unos minutos")
    if not auth.verify(c.username.strip(), c.password):
        auth.register_fail(ip)
        raise HTTPException(401, "Usuario o contraseña incorrectos")
    auth.clear_fails(ip)
    _set_cookie(response, c.username.strip())
    return {"ok": True}


@app.post("/api/auth/logout")
def auth_logout(response: Response):
    response.delete_cookie(auth.COOKIE)
    return {"ok": True}


@app.post("/api/auth/password")
def auth_password(c: Credentials, request: Request, response: Response):
    user = auth.read_token(request.cookies.get(auth.COOKIE))
    if not user:
        raise HTTPException(401, "Sesión no iniciada")
    if not auth.verify(user, c.password):
        raise HTTPException(400, "La contraseña actual no es correcta")
    if len(c.new_password) < auth.MIN_PASSWORD:
        raise HTTPException(400, f"La nueva contraseña debe tener al menos {auth.MIN_PASSWORD} caracteres")
    auth.set_password(user, c.new_password)
    _set_cookie(response, user)
    return {"ok": True}


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


@app.post("/api/grab")
def grab(g: Grab):
    return _guard(lambda: services.grab(config.get_settings(), g.link, g.title))


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


@app.post("/api/test/{target}")
def test_connection(target: str):
    s = config.get_settings()

    def run():
        if target == "tmdb":
            n = len(_tmdb().trending("movie"))
            return {"message": f"Conexión correcta con TMDB ({n} resultados en castellano)"}
        if target == "ds":
            with _ds() as ds:
                n = len(ds.list_tasks())
            return {"message": f"Conexión correcta con Download Station como «{s['ds_user']}» ({n} tareas visibles para este usuario)"}
        if target == "torznab":
            if not s["torznab_url"]:
                raise ValueError("Falta la URL Torznab")
            r = httpx.get(s["torznab_url"], params={"t": "caps", "apikey": s["torznab_apikey"]}, timeout=20)
            r.raise_for_status()
            return {"message": "Conexión correcta con Jackett"}
        if target == "tvdb":
            TVDB(s["tvdb_api_key"])._token()
            return {"message": "Conexión correcta con TheTVDB"}
        if target == "library":
            out = []
            for kind, label in library.KINDS.items():
                if s[f"lib_{kind}"]:
                    out.append(f"{label}: {len(library.scan(s[f'lib_{kind}'], kind))}")
            if not out:
                raise ValueError("No hay ninguna ruta configurada")
            return {"message": "Rutas correctas · " + " · ".join(out)}
        raise HTTPException(404, "Prueba desconocida")

    return _guard(run)


@app.get("/api/browse")
def browse(path: str = "/"):
    p = Path(path).resolve()
    if not p.is_dir():
        raise HTTPException(400, "No es una carpeta")
    try:
        dirs = sorted((d.name for d in p.iterdir() if d.is_dir() and not d.name.startswith((".", "@", "#"))), key=str.lower)
    except PermissionError:
        raise HTTPException(403, "Sin permiso para leer esta carpeta")
    return {"path": str(p), "parent": str(p.parent) if p != p.parent else None, "dirs": dirs}


class LibFix(BaseModel):
    folder: str
    tmdb_id: Optional[int] = None


@app.post("/api/library/{kind}/fix")
def library_fix(kind: str, f: LibFix):
    if kind not in library.KINDS:
        raise HTTPException(404, "Biblioteca desconocida")
    return _guard(lambda: library.fix(kind, f.folder, _tmdb(), f.tmdb_id))


class LibPoster(BaseModel):
    folder: str
    poster: str
    full: str
    save_file: bool = False


@app.post("/api/library/{kind}/poster")
def library_poster(kind: str, p: LibPoster):
    if kind not in library.KINDS:
        raise HTTPException(404, "Biblioteca desconocida")
    path = config.get_settings()[f"lib_{kind}"]
    return _guard(lambda: library.set_poster(kind, p.folder, p.poster, p.full, path, p.save_file))


@app.get("/api/posters/{media_type}/{tmdb_id}")
def posters(media_type: str, tmdb_id: int):
    if media_type not in ("movie", "tv"):
        raise HTTPException(400, "media_type inválido")
    return _guard(lambda: _tmdb().posters(media_type, tmdb_id))


class RenameReq(BaseModel):
    kinds: list[str]
    provider: str = "tmdb"
    group_sagas: bool = False
    apply: bool = False
    only: list[str] = []


@app.post("/api/library/rename")
def library_rename(r: RenameReq):
    if not r.kinds or any(k not in library.KINDS for k in r.kinds):
        raise HTTPException(404, "Biblioteca desconocida")
    s = config.get_settings()

    def run():
        entries = renamer.plan(s, r.kinds, r.provider, r.group_sagas, _tmdb())
        if not r.apply:
            return {"entries": entries}
        chosen = [e for e in entries if e["status"] == "ok" and f"{e['kind']}|{e['folder']}" in r.only]
        return {"results": renamer.apply(s, chosen)}
    return _guard(run)


@app.get("/api/library/{kind}")
def library_list(kind: str, collections: bool = False):
    if kind not in library.KINDS:
        raise HTTPException(404, "Biblioteca desconocida")
    return _guard(lambda: library.items(config.get_settings(), kind, _tmdb(), collections))


@app.on_event("startup")
def _start():
    auto.start_scheduler()


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
