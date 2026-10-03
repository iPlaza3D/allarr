"""Fuente Wolfmax4k. Si hay proxy configurado, todo el tráfico sale por él (útil si el ISP
bloquea el dominio); si no, conecta directamente."""
from __future__ import annotations

import re
from urllib.parse import quote, urljoin

import httpx

from .torznab import is_spanish

LINK_RE = re.compile(r'href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
TORRENT_RE = re.compile(r'''["\']((?:https?:)?//[^"\']+?\.torrent[^"\']*|magnet:\?[^"\']+)["\']''', re.I)
TAG_RE = re.compile(r"<[^>]+>")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


class Wolfmax:
    def __init__(self, base_url: str, proxy: str):
        if not base_url:
            raise ValueError("Falta la URL de Wolfmax4k")
        self.base = base_url.rstrip("/") + "/"
        self.client = httpx.Client(proxy=proxy or None, headers=UA, timeout=30, follow_redirects=True)

    def close(self) -> None:
        self.client.close()

    def search(self, query: str) -> list[dict]:
        r = self.client.get(urljoin(self.base, f"?s={quote(query)}"))
        r.raise_for_status()
        seen, out = set(), []
        for href, inner in LINK_RE.findall(r.text):
            title = re.sub(r"\s+", " ", TAG_RE.sub("", inner)).strip()
            url = urljoin(self.base, href)
            if not title or url in seen or not url.startswith(self.base):
                continue
            if query.lower().split()[0] in title.lower():
                seen.add(url)
                out.append({"title": title, "link": url, "size": 0, "seeders": 0,
                            "source": "wolfmax4k", "spanish": True, "page": True})
        return out[:30]

    def resolve(self, page_url: str) -> str:
        """Devuelve el enlace .torrent/magnet de la página de detalle."""
        r = self.client.get(page_url)
        r.raise_for_status()
        m = TORRENT_RE.search(r.text)
        if not m:
            raise LookupError("No se encontró enlace torrent en la página")
        link = m.group(1)
        return "https:" + link if link.startswith("//") else link

    def fetch_torrent(self, url: str) -> bytes:
        r = self.client.get(url)
        r.raise_for_status()
        return r.content
