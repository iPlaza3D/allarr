from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import httpx

NS = {"torznab": "http://torznab.com/schemas/2015/feed"}
SPANISH = re.compile(r"\b(castellano|espa[nñ]ol|spanish|spa|esp|dual|es-es)\b", re.I)


def is_spanish(title: str) -> bool:
    return bool(SPANISH.search(title))


def parse(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    if root.tag == "error":
        raise ValueError(root.get("description", "Error Torznab"))
    results = []
    for item in root.iter("item"):
        attrs = {a.get("name"): a.get("value") for a in item.findall("torznab:attr", NS)}
        enc = item.find("enclosure")
        link = attrs.get("magneturl") or (enc.get("url") if enc is not None else "") or item.findtext("link") or ""
        title = item.findtext("title") or ""
        results.append({
            "title": title, "link": link,
            "size": int(attrs.get("size") or (enc.get("length") if enc is not None else 0) or 0),
            "seeders": int(attrs.get("seeders") or 0),
            "source": item.findtext("jackettindexer") or item.findtext("prowlarrindexer") or "torznab",
            "spanish": is_spanish(title),
        })
    return results


def search(url: str, apikey: str, query: str, media_type: str = "movie") -> list[dict]:
    if not url:
        return []
    t = "tvsearch" if media_type == "tv" else "movie"
    last: Exception | None = None
    # Muchos indexadores (p. ej. Wolfmax4k) solo soportan t=search
    for mode in (t, "search"):
        try:
            r = httpx.get(url, params={"t": mode, "q": query, "apikey": apikey}, timeout=60)
            r.raise_for_status()
            return parse(r.text)
        except (httpx.HTTPStatusError, ValueError) as e:
            last = e
    raise last
