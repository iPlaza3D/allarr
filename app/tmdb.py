from __future__ import annotations

import httpx

BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w342"
BACKDROP = "https://image.tmdb.org/t/p/w780"
ORIGINAL = "https://image.tmdb.org/t/p/original"
IMG_PREFIX = "https://image.tmdb.org/t/p/"


class TMDB:
    def __init__(self, api_key: str, language: str = "es-ES"):
        self.key, self.lang = api_key, language
        self.region = language.split("-")[-1].upper() if "-" in language else "ES"

    def _get(self, path: str, **params) -> dict:
        if not self.key:
            raise ValueError("Falta la API key de TMDB")
        params.update(api_key=self.key, language=self.lang)
        r = httpx.get(f"{BASE}{path}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def normalize(item: dict, media_type: str | None = None) -> dict:
        date = item.get("release_date") or item.get("first_air_date") or ""
        poster = item.get("poster_path")
        backdrop = item.get("backdrop_path")
        return {
            "tmdb_id": item["id"],
            "media_type": media_type or item.get("media_type"),
            "title": item.get("title") or item.get("name") or "",
            "original_title": item.get("original_title") or item.get("original_name") or "",
            "year": date[:4],
            "overview": item.get("overview", ""),
            "poster": f"{IMG}{poster}" if poster else None,
            "backdrop": f"{BACKDROP}{backdrop}" if backdrop else None,
            "rating": item.get("vote_average"),
        }

    def search(self, query: str) -> list[dict]:
        data = self._get("/search/multi", query=query, include_adult="false")
        return [self.normalize(i) for i in data["results"] if i.get("media_type") in ("movie", "tv")]

    def trending(self, media_type: str = "movie") -> list[dict]:
        data = self._get(f"/trending/{media_type}/week")
        return [self.normalize(i, media_type) for i in data["results"]]

    def details(self, media_type: str, tmdb_id: int) -> dict:
        d = self._get(f"/{media_type}/{tmdb_id}")
        out = self.normalize(d, media_type)
        out["release_date"] = d.get("release_date") or ""
        out["genres"] = [g["name"] for g in d.get("genres", [])]
        out["runtime"] = d.get("runtime") or (d.get("episode_run_time") or [None])[0]
        out["tagline"] = d.get("tagline", "")
        out["seasons"] = [s["season_number"] for s in d.get("seasons", []) if s["season_number"] > 0]
        return out

    def collection_of(self, tmdb_id: int) -> dict | None:
        c = self._get(f"/movie/{tmdb_id}").get("belongs_to_collection")
        return {"id": c["id"], "name": c["name"]} if c else None

    def posters(self, media_type: str, tmdb_id: int) -> list[dict]:
        d = self._get(f"/{media_type}/{tmdb_id}/images", include_image_language="es,en,null")
        order = {"es": 0, None: 1}
        ps = sorted(d.get("posters", []), key=lambda p: (order.get(p.get("iso_639_1"), 2), -(p.get("vote_average") or 0)))
        return [{"poster": f"{IMG}{p['file_path']}", "full": f"{ORIGINAL}{p['file_path']}", "lang": p.get("iso_639_1") or ""}
                for p in ps[:40]]

    def season(self, tmdb_id: int, number: int) -> list[dict]:
        d = self._get(f"/tv/{tmdb_id}/season/{number}")
        return [{"episode": e["episode_number"], "air_date": e.get("air_date") or ""} for e in d.get("episodes", [])]

    def discover(self, media_type: str, start: str, end: str, pages: int = 3) -> list[dict]:
        """Estrenos del rango (películas: fecha en tu región; series: estreno de serie), por popularidad."""
        if media_type == "movie":
            params = {"region": self.region, "with_release_type": "2|3|4", "primary_release_date.gte": start,
                      "primary_release_date.lte": end}
        else:
            params = {"first_air_date.gte": start, "first_air_date.lte": end}
        out = []
        for page in range(1, pages + 1):
            d = self._get(f"/discover/{media_type}", sort_by="popularity.desc", page=page, **params)
            for i in d["results"]:
                n = self.normalize(i, media_type)
                n["date"] = i.get("release_date") or i.get("first_air_date") or ""
                out.append(n)
            if page >= d.get("total_pages", 1):
                break
        return [o for o in out if start <= o["date"] <= end]

    def popular(self, media_type: str) -> list[dict]:
        return [self.normalize(i, media_type) for i in self._get(f"/{media_type}/popular")["results"]]

    def upcoming(self) -> list[dict]:
        return [self.normalize(i, "movie") for i in self._get("/movie/upcoming", region=self.region)["results"]]
