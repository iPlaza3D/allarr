from __future__ import annotations

import httpx

from . import torznab
from .synology import DownloadStation


def search_torrents(s: dict, q: str, media_type: str = "movie") -> dict:
    results, errors = [], []
    try:
        results += torznab.search(s["torznab_url"], s["torznab_apikey"], q, media_type)
    except (httpx.HTTPError, ValueError) as e:
        errors.append(f"torznab: {e}")
    if not s["torznab_url"]:
        errors.append("Falta la URL Torznab de Jackett en Ajustes")
    results = [r for r in results if r["spanish"]]
    results.sort(key=lambda r: r["seeders"], reverse=True)
    return {"results": results, "errors": errors}


def grab(s: dict, link: str, title: str = "download") -> dict:
    content = None
    if link.startswith("http"):
        # Jackett entrega el .torrent; lo subimos nosotros para que DS no dependa de la red de Jackett
        try:
            r = httpx.get(link, timeout=60, follow_redirects=True)
            r.raise_for_status()
            if r.content[:1] == b"d":
                content = r.content
        except httpx.HTTPError:
            pass
    with DownloadStation(s["ds_url"], s["ds_user"], s["ds_password"], s["ds_destination"]) as ds:
        if content is not None:
            ds.add_torrent_file(title[:80] + ".torrent", content)
        else:
            ds.add_uri(link)
    return {"ok": True}
