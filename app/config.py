from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("ALLARR_DB", "data/allarr.db"))

DEFAULTS = {
    "tmdb_api_key": os.getenv("TMDB_API_KEY", ""),
    "language": os.getenv("ALLARR_LANGUAGE", "es-ES"),
    "wolfmax_url": os.getenv("WOLFMAX_URL", ""),
    "auto_interval_min": os.getenv("AUTO_INTERVAL_MIN", "60"),
    "ds_url": os.getenv("DS_URL", ""),
    "ds_user": os.getenv("DS_USER", ""),
    "ds_password": os.getenv("DS_PASSWORD", ""),
    "ds_destination": os.getenv("DS_DESTINATION", ""),
    "lib_movies": os.getenv("LIB_MOVIES", ""),
    "lib_movies_anim": os.getenv("LIB_MOVIES_ANIM", ""),
    "lib_series": os.getenv("LIB_SERIES", ""),
    "lib_series_anim": os.getenv("LIB_SERIES_ANIM", ""),
}
SECRET_KEYS = {"tmdb_api_key", "ds_password"}


def conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    c.execute(
        """CREATE TABLE IF NOT EXISTS watchlist (
            tmdb_id INTEGER, media_type TEXT, title TEXT, year TEXT, poster TEXT,
            status TEXT DEFAULT 'wanted', added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tmdb_id, media_type))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS episodes (
            tmdb_id INTEGER, season INTEGER, episode INTEGER, status TEXT DEFAULT 'grabbed',
            PRIMARY KEY (tmdb_id, season, episode))"""
    )
    c.execute("CREATE TABLE IF NOT EXISTS lib_meta (media_type TEXT, name TEXT, data TEXT, PRIMARY KEY (media_type, name))")
    return c


def get_settings() -> dict:
    with conn() as c:
        stored = {r["key"]: r["value"] for r in c.execute("SELECT * FROM settings")}
    return {k: stored.get(k, v) for k, v in DEFAULTS.items()}


def save_settings(values: dict) -> None:
    with conn() as c:
        for k, v in values.items():
            if k not in DEFAULTS:
                continue
            if k in SECRET_KEYS and v in ("", "********"):
                continue
            c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (k, str(v)))


def masked(settings: dict) -> dict:
    return {k: ("********" if k in SECRET_KEYS and v else v) for k, v in settings.items()}
