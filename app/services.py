from __future__ import annotations

import httpx

from . import torznab
from .synology import DownloadStation
from .wolfmax import Wolfmax


def search_torrents(s: dict, q: str, media_type: str = "movie") -> dict:
    results, errors = [], []
    try:
        results += torznab.search(s["torznab_url"], s["torznab_apikey"], q, media_type)
    except (httpx.HTTPError, ValueError) as e:
        errors.append(f"torznab: {e}")
    if s["wolfmax_url"]:
        w = None
        try:
            w = Wolfmax(s["wolfmax_url"], s["vpn_proxy"])
            results += w.search(q)
        except (httpx.HTTPError, ValueError) as e:
            errors.append(f"wolfmax4k: {e}")
        finally:
            if w:
                w.close()
    results = [r for r in results if r["spanish"]]
    results.sort(key=lambda r: r["seeders"], reverse=True)
    return {"results": results, "errors": errors}


def grab(s: dict, link: str, title: str = "download", source: str = "", page: bool = False) -> dict:
    content = None
    if source == "wolfmax4k":
        w = Wolfmax(s["wolfmax_url"], s["vpn_proxy"])
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
