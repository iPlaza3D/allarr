"""Bibliotecas locales (carpetas del NAS) enlazadas con TMDB para mostrar carátulas."""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

from . import config
from .tmdb import TMDB

KINDS = {
    "movies": "Películas",
    "movies_anim": "Películas de animación",
    "series": "Series",
    "series_anim": "Series de animación",
}
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


def scan(path: str, kind: str) -> list[str]:
    root = Path(path)
    if not root.is_dir():
        raise ValueError(f"La ruta no existe o no es una carpeta: {path}")
    names = []
    for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
        if p.name.startswith(".") or p.name in ("@eaDir", "#recycle"):
            continue
        if p.is_dir() or (media_type(kind) == "movie" and p.suffix.lower() in VIDEO):
            names.append(p.name)
    return names


def _lookup(tmdb: TMDB, mt: str, name: str) -> dict:
    with config.conn() as c:
        row = c.execute("SELECT data FROM lib_meta WHERE media_type=? AND name=?", (mt, name)).fetchone()
    if row:
        return json.loads(row["data"])
    title, year = clean(name)
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


def items(s: dict, kind: str, tmdb: TMDB) -> list[dict]:
    path = s[f"lib_{kind}"]
    if not path:
        return []
    mt = media_type(kind)
    names = scan(path, kind)
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(lambda n: _lookup(tmdb, mt, n), names))
