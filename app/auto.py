"""Descarga automática: películas ya estrenadas y episodios emitidos de las series de la lista."""
from __future__ import annotations

import logging
import re
import threading
import time
import unicodedata
from datetime import date

from . import config, services
from .tmdb import TMDB

log = logging.getLogger("media_server_utility.auto")
_lock = threading.Lock()

# S01E05, 1x05 y el formato habitual en castellano "Cap.105" / "Cap.1005"
EP_PATTERNS = [
    re.compile(r"s(\d{1,2})\s*e(\d{1,3})", re.I),
    re.compile(r"\b(\d{1,2})x(\d{2,3})\b", re.I),
    re.compile(r"cap(?:itulo)?\.?\s*(\d{1,2})(\d{2})\b", re.I),
]


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def episode_of(title: str):
    for p in EP_PATTERNS:
        m = p.search(title)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None


def pick(results: list[dict], title: str, episode=None):
    """Mejor resultado (más seeders) cuyo título coincide con la obra y, en series, con el episodio."""
    want = norm(title)
    for r in results:
        if want not in norm(r["title"]):
            continue
        if episode is not None and episode_of(r["title"]) != episode:
            continue
        return r
    return None


def _grab(s: dict, r: dict) -> None:
    services.grab(s, r["link"], r["title"])


def _movie(s: dict, tmdb: TMDB, row) -> None:
    d = tmdb.details("movie", row["tmdb_id"])
    if not d["release_date"] or d["release_date"] > date.today().isoformat():
        return
    best = pick(services.search_torrents(s, row["title"], "movie")["results"], row["title"])
    if best:
        _grab(s, best)
        with config.conn() as c:
            c.execute("UPDATE watchlist SET status='downloaded' WHERE tmdb_id=? AND media_type='movie'", (row["tmdb_id"],))


def _series(s: dict, tmdb: TMDB, row) -> None:
    today = date.today().isoformat()
    with config.conn() as c:
        have = {(r["season"], r["episode"]) for r in c.execute("SELECT * FROM episodes WHERE tmdb_id=?", (row["tmdb_id"],))}
    missing = []
    for sn in tmdb.details("tv", row["tmdb_id"])["seasons"]:
        for e in tmdb.season(row["tmdb_id"], sn):
            if e["air_date"] and e["air_date"] <= today and (sn, e["episode"]) not in have:
                missing.append((sn, e["episode"]))
    if not missing:
        return
    results = services.search_torrents(s, row["title"], "tv")["results"]
    for ep in missing:
        best = pick(results, row["title"], ep)
        if not best:
            continue
        _grab(s, best)
        with config.conn() as c:
            c.execute("INSERT OR IGNORE INTO episodes (tmdb_id, season, episode) VALUES (?,?,?)", (row["tmdb_id"], *ep))


def run_once() -> dict:
    if not _lock.acquire(blocking=False):
        return {"skipped": "ya en ejecución"}
    try:
        s = config.get_settings()
        tmdb = TMDB(s["tmdb_api_key"], s["language"])
        with config.conn() as c:
            rows = [dict(r) for r in c.execute("SELECT * FROM watchlist WHERE status='wanted'")]
        errors = []
        for row in rows:
            try:
                (_movie if row["media_type"] == "movie" else _series)(s, tmdb, row)
            except Exception as e:  # un título con fallo no debe frenar al resto
                log.warning("%s: %s", row["title"], e)
                errors.append(f"{row['title']}: {e}")
        return {"checked": len(rows), "errors": errors}
    finally:
        _lock.release()


def start_scheduler() -> None:
    def loop():
        while True:
            try:
                minutes = max(5, int(config.get_settings()["auto_interval_min"]))
            except ValueError:
                minutes = 60
            time.sleep(minutes * 60)
            try:
                run_once()
            except Exception:
                log.exception("auto run")

    threading.Thread(target=loop, daemon=True).start()
