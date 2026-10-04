"""Cliente mínimo de TheTVDB v4 para obtener títulos en castellano."""
from __future__ import annotations

import httpx

BASE = "https://api4.thetvdb.com/v4"
_tokens: dict[str, str] = {}


class TVDB:
    def __init__(self, api_key: str):
        self.key = api_key

    def _token(self) -> str:
        if not self.key:
            raise ValueError("Falta la API key de TheTVDB en Ajustes")
        if self.key not in _tokens:
            r = httpx.post(f"{BASE}/login", json={"apikey": self.key}, timeout=15)
            if r.status_code == 401:
                raise ValueError("La API key de TheTVDB no es válida")
            r.raise_for_status()
            _tokens[self.key] = r.json()["data"]["token"]
        return _tokens[self.key]

    def _get(self, path: str, **params) -> dict:
        for retry in (True, False):
            r = httpx.get(f"{BASE}{path}", params=params, headers={"Authorization": f"Bearer {self._token()}"}, timeout=15)
            if r.status_code == 401 and retry:
                _tokens.pop(self.key, None)  # token caducado
                continue
            r.raise_for_status()
            return r.json()
        return {}

    def spanish_title(self, media_type: str, query: str, year: str = "") -> str | None:
        """Título en castellano de la mejor coincidencia, o None si TheTVDB no la encuentra."""
        kind = "movie" if media_type == "movie" else "series"
        found = self._get("/search", query=query, type=kind).get("data") or []
        if not found:
            return None
        hit = next((f for f in found if year and str(f.get("year", "")) == year), found[0])
        tr = hit.get("translations")
        if isinstance(tr, dict) and tr.get("spa"):
            return tr["spa"]
        tid = hit.get("tvdb_id") or str(hit.get("id", "")).split("-")[-1]
        path = f"/{'movies' if kind == 'movie' else 'series'}/{tid}/translations/spa"
        try:
            name = (self._get(path).get("data") or {}).get("name")
        except httpx.HTTPStatusError:
            name = None  # sin traducción al castellano
        return name or hit.get("name")
