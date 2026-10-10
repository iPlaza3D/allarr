from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from typing import Optional

from . import config

COOKIE = "media-server-utility_session"
SESSION_SECONDS = 7 * 24 * 3600
MIN_PASSWORD = 8
_ITER = 200_000
_fails: dict = {}


def _init(c) -> None:
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt TEXT, pw_hash TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), _ITER).hex()


def has_users() -> bool:
    with config.conn() as c:
        _init(c)
        return c.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None


def create_user(username: str, password: str) -> None:
    salt = secrets.token_hex(16)
    with config.conn() as c:
        _init(c)
        c.execute("INSERT INTO users VALUES (?,?,?)", (username, salt, _hash(password, salt)))


def set_password(username: str, password: str) -> None:
    salt = secrets.token_hex(16)
    with config.conn() as c:
        _init(c)
        c.execute("UPDATE users SET salt=?, pw_hash=? WHERE username=?", (salt, _hash(password, salt), username))
        c.execute("DELETE FROM meta WHERE key='secret'")  # invalida las sesiones existentes


def verify(username: str, password: str) -> bool:
    with config.conn() as c:
        _init(c)
        row = c.execute("SELECT salt, pw_hash FROM users WHERE username=?", (username,)).fetchone()
    # Se calcula siempre el hash para no revelar si el usuario existe por tiempo de respuesta.
    salt = row["salt"] if row else "00" * 16
    ok = hmac.compare_digest(_hash(password, salt), row["pw_hash"] if row else "x")
    return bool(row) and ok


def _secret() -> bytes:
    with config.conn() as c:
        _init(c)
        row = c.execute("SELECT value FROM meta WHERE key='secret'").fetchone()
        if row:
            return bytes.fromhex(row["value"])
        val = secrets.token_hex(32)
        c.execute("INSERT INTO meta VALUES ('secret', ?)", (val,))
        return bytes.fromhex(val)


def make_token(username: str) -> str:
    body = base64.urlsafe_b64encode(f"{username}|{int(time.time()) + SESSION_SECONDS}".encode()).decode()
    sig = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def read_token(token: Optional[str]) -> Optional[str]:
    if not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    if not hmac.compare_digest(hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest(), sig):
        return None
    try:
        username, exp = base64.urlsafe_b64decode(body.encode()).decode().rsplit("|", 1)
    except Exception:
        return None
    return username if int(exp) > time.time() else None


def locked(ip: str) -> bool:
    n, first = _fails.get(ip, (0, 0.0))
    if n and time.time() - first > 300:
        _fails.pop(ip, None)
        return False
    return n >= 5


def register_fail(ip: str) -> None:
    n, first = _fails.get(ip, (0, time.time()))
    _fails[ip] = (n + 1, first)


def clear_fails(ip: str) -> None:
    _fails.pop(ip, None)
