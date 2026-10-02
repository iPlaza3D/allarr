from __future__ import annotations

from . import config
from .tmdb import TMDB


def build(start: str, end: str) -> list[dict]:
    """Estrenos del rango: todo lo que TMDB anuncia (esté o no en tu lista) más los episodios de tus series."""
    s = config.get_settings()
    tmdb = TMDB(s["tmdb_api_key"], s["language"])
    with config.conn() as c:
        mine = {(r["media_type"], r["tmdb_id"]) for r in c.execute("SELECT * FROM watchlist")}
        tracked_tv = [dict(r) for r in c.execute("SELECT * FROM watchlist WHERE media_type='tv'")]

    events, seen = [], set()

    def add(ev: dict) -> None:
        key = (ev["media_type"], ev["tmdb_id"], ev.get("season"), ev.get("episode"))
        if key in seen:
            return
        seen.add(key)
        ev["in_list"] = (ev["media_type"], ev["tmdb_id"]) in mine
        events.append(ev)

    # Episodios exactos de las series seguidas
    for row in tracked_tv:
        details = tmdb.details("tv", row["tmdb_id"])
        for sn in details["seasons"]:
            for e in tmdb.season(row["tmdb_id"], sn):
                if e["air_date"] and start <= e["air_date"] <= end:
                    add({"tmdb_id": row["tmdb_id"], "media_type": "tv", "title": row["title"], "year": row["year"],
                         "poster": row["poster"], "date": e["air_date"], "season": sn, "episode": e["episode"]})

    for mt in ("movie", "tv"):
        for n in tmdb.discover(mt, start, end):
            add(n)

    return sorted(events, key=lambda e: (e["date"], not e["in_list"], e["title"]))
