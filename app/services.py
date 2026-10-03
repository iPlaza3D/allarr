from __future__ import annotations

import httpx

from .synology import DownloadStation
from .wolfmax import Wolfmax


def search_torrents(s: dict, q: str, media_type: str = "movie") -> dict:
    results, errors = [], []
    if not s["wolfmax_url"]:
        return {"results": [], "errors": ["Falta la URL de Wolfmax4k en Ajustes"]}
    w = None
    try:
        w = Wolfmax(s["wolfmax_url"])
        results += w.search(q)
    except (httpx.HTTPError, ValueError) as e:
        errors.append(f"wolfmax4k: {e}")
    finally:
        if w:
            w.close()
    return {"results": results, "errors": errors}


def grab(s: dict, link: str, title: str = "download", source: str = "", page: bool = False) -> dict:
    content = None
    if source == "wolfmax4k":
        w = Wolfmax(s["wolfmax_url"])
        try:
            if page:
                link = w.resolve(link)
            if not link.startswith("magnet:"):
                content = w.fetch_torrent(link)
        finally:
            w.close()
    with DownloadStation(s["ds_url"], s["ds_user"], s["ds_password"], s["ds_destination"]) as ds:
        if content is not None:
            ds.add_torrent_file(title[:80] + ".torrent", content)
        else:
            ds.add_uri(link)
    return {"ok": True}
