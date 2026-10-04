"""Bibliotecas locales (carpetas del NAS) enlazadas con TMDB para mostrar carátulas."""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

from . import config
from .tmdb import IMG_PREFIX, TMDB

KINDS = {
    "movies": "Películas",
    "movies_anim": "Películas de animación",
    "series": "Series",
    "series_anim": "Series de animación",
}
SAGA_SUFFIX = " (Saga)"
VIDEO = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".wmv", ".ts", ".mpg", ".mpeg"}
YEAR_RE = re.compile(r"[\(\[\s._-]((?:19|20)\d{2})(?:[\)\]\s._-]|$)")
TAGS_RE = re.compile(
    r"[\[\(].*?[\)\]]|\b(2160p|1080p|720p|4k|bluray|bdrip|brrip|webrip|web-dl|hdtv|x264|x265|hevc|castellano|dual|latino)\b.*",
    re.I,
)


def media_type(kind: str) -> str:
    return "tv" if kind.startswith("series") else "movie"


def clean(name: str) -> tuple[str, str]:
    stem = name if "." not in name or Path(name).suffix.lower() not in VIDEO else Path(name).stem
    m = YEAR_RE.search(stem)
    year = m.group(1) if m else ""
    base = stem[: m.start()] if m else stem
    base = TAGS_RE.sub(" ", base).replace(".", " ").replace("_", " ")
    return re.sub(r"\s+", " ", base).strip(" -") or stem, year


def _entries(root: Path, kind: str, prefix: str = "") -> list[str]:
    names = []
    for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
        if p.name.startswith(".") or p.name in ("@eaDir", "#recycle"):
            continue
        if p.is_dir() and not prefix and media_type(kind) == "movie" and p.name.endswith(SAGA_SUFFIX):
            names += _entries(p, kind, p.name + "/")  # carpeta de saga: sus películas cuentan como elementos
        elif p.is_dir() or (media_type(kind) == "movie" and p.suffix.lower() in VIDEO):
            names.append(prefix + p.name)
    return names


def scan(path: str, kind: str) -> list[str]:
    root = Path(path)
    if not root.is_dir():
        raise ValueError(f"La ruta no existe o no es una carpeta: {path}")
    return _entries(root, kind)


def _lookup(tmdb: TMDB, mt: str, name: str) -> dict:
    with config.conn() as c:
        row = c.execute("SELECT data FROM lib_meta WHERE media_type=? AND name=?", (mt, name)).fetchone()
    if row:
        return json.loads(row["data"])
    title, year = clean(name.rsplit("/", 1)[-1])
    item = {"media_type": mt, "title": title, "year": year, "poster": None, "overview": "", "folder": name}
    try:
        res = [r for r in tmdb.search(title) if r["media_type"] == mt]
        if year:
            res = [r for r in res if r["year"] == year] or res
        if res:
            item = {**res[0], "folder": name}
        with config.conn() as c:
            c.execute("INSERT OR REPLACE INTO lib_meta VALUES (?,?,?)", (mt, name, json.dumps(item)))
    except (httpx.HTTPError, ValueError):
        pass  # sin cachear: se reintentará en la próxima carga
    return item


def _store(mt: str, item: dict) -> None:
    with config.conn() as c:
        c.execute("INSERT OR REPLACE INTO lib_meta VALUES (?,?,?)", (mt, item["folder"], json.dumps(item)))


def with_collection(tmdb: TMDB, item: dict) -> dict:
    """Añade la saga (belongs_to_collection) a una película identificada; se cachea con el resto de datos."""
    if item["media_type"] != "movie" or not item.get("tmdb_id") or "collection" in item:
        return item
    try:
        item = {**item, "collection": tmdb.collection_of(item["tmdb_id"])}
        _store("movie", item)
    except (httpx.HTTPError, ValueError):
        pass
    return item


def items(s: dict, kind: str, tmdb: TMDB, collections: bool = False) -> list[dict]:
    path = s[f"lib_{kind}"]
    if not path:
        return []
    mt = media_type(kind)
    names = scan(path, kind)

    def one(n: str) -> dict:
        it = _lookup(tmdb, mt, n)
        return with_collection(tmdb, it) if collections else it

    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(one, names))


def set_poster(kind: str, folder: str, poster: str, full: str, library_path: str, save_file: bool) -> dict:
    """Fija la carátula elegida; opcionalmente la guarda como poster.jpg dentro de la carpeta."""
    if not (poster.startswith(IMG_PREFIX) and full.startswith(IMG_PREFIX)):
        raise ValueError("Carátula no válida")
    mt = media_type(kind)
    with config.conn() as c:
        row = c.execute("SELECT data FROM lib_meta WHERE media_type=? AND name=?", (mt, folder)).fetchone()
    if not row:
        raise LookupError("Elemento no identificado todavía")
    item = {**json.loads(row["data"]), "poster": poster, "poster_custom": True}
    _store(mt, item)
    saved = None
    target = Path(library_path) / folder
    if save_file and target.is_dir():
        try:
            r = httpx.get(full, timeout=30)
            r.raise_for_status()
            (target / "poster.jpg").write_bytes(r.content)
            saved = True
        except (httpx.HTTPError, OSError):
            saved = False  # biblioteca de solo lectura o sin permisos
    return {"item": item, "saved_file": saved}


def fix(kind: str, folder: str, tmdb: TMDB, tmdb_id: int | None) -> dict:
    """Asigna manualmente el título de TMDB a una carpeta; sin tmdb_id borra la corrección."""
    mt = media_type(kind)
    if tmdb_id is None:
        with config.conn() as c:
            c.execute("DELETE FROM lib_meta WHERE media_type=? AND name=?", (mt, folder))
        return _lookup(tmdb, mt, folder)
    item = {**tmdb.details(mt, tmdb_id), "folder": folder}
    with config.conn() as c:
        c.execute("INSERT OR REPLACE INTO lib_meta VALUES (?,?,?)", (mt, folder, json.dumps(item)))
    return item
