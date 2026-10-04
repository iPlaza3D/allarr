"""Renombrado de las bibliotecas con títulos en castellano de TMDB o TheTVDB."""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

from . import config, library
from .auto import episode_of
from .tmdb import TMDB
from .tvdb import TVDB

PROVIDERS = ("tmdb", "tvdb")
ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize(name: str) -> str:
    name = re.sub(r"\s+", " ", ILLEGAL.sub(" ", name)).strip(" .")
    return name or "Sin título"


def _title(item: dict, provider: str, tvdb: TVDB | None) -> str:
    if provider == "tvdb":
        query = item.get("original_title") or item["title"]
        found = tvdb.spanish_title(item["media_type"], query, item.get("year", ""))
        if found:
            return found
    return item["title"]


def _episode_renames(folder: Path, title: str) -> list[dict]:
    out, seen = [], set()
    for f in sorted(folder.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in library.VIDEO or f.name.startswith("."):
            continue
        ep = episode_of(f.stem)
        if not ep:
            continue
        new = f.with_name(f"{title} - S{ep[0]:02d}E{ep[1]:02d}{f.suffix.lower()}")
        rel_old, rel_new = f.relative_to(folder).as_posix(), new.relative_to(folder).as_posix()
        if rel_old == rel_new:
            continue
        if rel_new in seen or new.exists():
            out.append({"old": rel_old, "new": rel_new, "conflict": True})
        else:
            out.append({"old": rel_old, "new": rel_new})
        seen.add(rel_new)
    return out


def _plan_one(s: dict, kind: str, name: str, provider: str, group: bool, tmdb: TMDB, tvdb: TVDB | None) -> dict:
    mt = library.media_type(kind)
    entry = {"kind": kind, "folder": name, "title": "", "new": name, "status": "same", "episodes": [], "error": ""}
    try:
        item = library._lookup(tmdb, mt, name)
        if not item.get("tmdb_id"):
            return {**entry, "status": "unidentified"}
        title = sanitize(_title(item, provider, tvdb))
        entry["title"] = title
        base = sanitize(f"{title} ({item['year']})" if item.get("year") else title)
        src = Path(s[f"lib_{kind}"]) / name
        new = base + (src.suffix.lower() if src.is_file() else "")
        if mt == "movie" and group:
            coll = (library.with_collection(tmdb, item).get("collection"))
            if coll:
                new = f"{sanitize(coll['name'])}{library.SAGA_SUFFIX}/{new}"
        if mt == "tv" and src.is_dir():
            entry["episodes"] = _episode_renames(src, title)
        entry["new"] = new
        dst = Path(s[f"lib_{kind}"]) / new
        if new != name and dst.exists() and dst.resolve() != src.resolve():
            entry["status"] = "conflict"
        elif new != name or entry["episodes"]:
            entry["status"] = "ok"
    except (httpx.HTTPError, ValueError, OSError) as e:
        entry.update(status="error", error=str(e))
    return entry


def plan(s: dict, kinds: list[str], provider: str, group_sagas: bool, tmdb: TMDB) -> list[dict]:
    if provider not in PROVIDERS:
        raise ValueError("Proveedor de renombrado desconocido")
    tvdb = TVDB(s["tvdb_api_key"]) if provider == "tvdb" else None
    if tvdb:
        tvdb._token()  # falla pronto y con mensaje claro si falta o no vale la clave
    out = []
    for kind in kinds:
        if not s[f"lib_{kind}"]:
            continue
        names = library.scan(s[f"lib_{kind}"], kind)
        with ThreadPoolExecutor(6) as ex:
            out += list(ex.map(lambda n: _plan_one(s, kind, n, provider, group_sagas, tmdb, tvdb), names))
    return out


def _move_meta(mt: str, old: str, new: str) -> None:
    with config.conn() as c:
        row = c.execute("SELECT data FROM lib_meta WHERE media_type=? AND name=?", (mt, old)).fetchone()
        if not row:
            return
        c.execute("DELETE FROM lib_meta WHERE media_type=? AND name=?", (mt, old))
        c.execute("INSERT OR REPLACE INTO lib_meta VALUES (?,?,?)", (mt, new, json.dumps({**json.loads(row["data"]), "folder": new})))


def apply(s: dict, entries: list[dict]) -> list[dict]:
    results = []
    for e in entries:
        root = Path(s[f"lib_{e['kind']}"])
        src = root / e["folder"]
        res = {"kind": e["kind"], "folder": e["folder"], "new": e["new"], "ok": True, "error": ""}
        try:
            for ep in e["episodes"]:
                if not ep.get("conflict"):
                    (src / ep["old"]).rename(src / ep["new"])
            if e["new"] != e["folder"]:
                dst = root / e["new"]
                dst.parent.mkdir(exist_ok=True)
                src.rename(dst)
                if src.parent != root and not any(src.parent.iterdir()):
                    src.parent.rmdir()  # carpeta de saga que se ha quedado vacía
                _move_meta(library.media_type(e["kind"]), e["folder"], e["new"])
        except OSError as x:
            res.update(ok=False, error=f"{x.strerror or x} (¿la biblioteca está montada en solo lectura?)")
        results.append(res)
    return results
