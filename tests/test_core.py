from app.torznab import parse, is_spanish

XML = """<rss xmlns:torznab="http://torznab.com/schemas/2015/feed"><channel>
<item><title>Peli 2024 Castellano 1080p</title><link>http://x/a.torrent</link>
<torznab:attr name="seeders" value="12"/><torznab:attr name="size" value="100"/></item>
<item><title>Movie 2024 English</title><link>http://x/b.torrent</link></item></channel></rss>"""


def test_parse_and_spanish():
    r = parse(XML)
    assert r[0]["seeders"] == 12 and r[0]["spanish"] and not r[1]["spanish"]
    assert is_spanish("Serie Dual Español")


from app.auto import episode_of, pick


def test_episode_formats():
    assert episode_of("Serie S02E05 1080p") == (2, 5)
    assert episode_of("Serie 1x07") == (1, 7)
    assert episode_of("Serie - Temporada 1 [HDTV][Cap.105]") == (1, 5)
    assert episode_of("Serie [Cap.1005]") == (10, 5)


def test_pick():
    rs = [{"title": "Otra Serie Cap.101"}, {"title": "La Casa de Papel Cap.102"}]
    assert pick(rs, "La casa de papel", (1, 2)) is rs[1]
    assert pick(rs, "La casa de papel", (1, 3)) is None


def test_calendar_merges(monkeypatch, tmp_path):
    from app import calendar as cal, config
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    with config.conn() as c:
        c.execute("INSERT INTO watchlist (tmdb_id, media_type, title) VALUES (1,'movie','Mia')")

    class FakeTMDB:
        def __init__(self, *a): pass
        def discover(self, mt, s, e):
            return [{"tmdb_id": 1, "media_type": "movie", "title": "Mia", "date": "2026-10-10"},
                    {"tmdb_id": 2, "media_type": "movie", "title": "Otra", "date": "2026-10-10"}] if mt == "movie" else []
    monkeypatch.setattr(cal, "TMDB", FakeTMDB)
    r = cal.build("2026-10-01", "2026-10-31")
    assert [(x["title"], x["in_list"]) for x in r] == [("Mia", True), ("Otra", False)]


def _client(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from app import config
    from app.main import app
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "a.db")
    return TestClient(app)


def test_auth_flow(monkeypatch, tmp_path):
    c = _client(monkeypatch, tmp_path)
    assert c.get("/api/settings").status_code == 401
    assert c.get("/api/auth/status").json()["setup_needed"] is True
    assert c.post("/api/auth/setup", json={"username": "a", "password": "corta"}).status_code == 400
    assert c.post("/api/auth/setup", json={"username": "admin", "password": "claveSegura1"}).status_code == 200
    assert c.get("/api/settings").status_code == 200
    assert c.post("/api/auth/setup", json={"username": "x", "password": "otraClave123"}).status_code == 409
    c.post("/api/auth/logout")
    c.cookies.clear()
    assert c.get("/api/settings").status_code == 401
    assert c.post("/api/auth/login", json={"username": "admin", "password": "mala"}).status_code == 401
    assert c.post("/api/auth/login", json={"username": "admin", "password": "claveSegura1"}).status_code == 200
    assert c.post("/api/auth/password", json={"password": "claveSegura1", "new_password": "nuevaClave99"}).status_code == 200
    assert c.get("/api/settings").status_code == 200


def test_forged_cookie_rejected(monkeypatch, tmp_path):
    c = _client(monkeypatch, tmp_path)
    c.post("/api/auth/setup", json={"username": "admin", "password": "claveSegura1"})
    c.cookies.clear()
    c.cookies.set("allarr_session", "YWRtaW58OTk5OTk5OTk5OQ==.firma")
    assert c.get("/api/settings").status_code == 401


def test_lockout(monkeypatch, tmp_path):
    from app import auth
    auth._fails.clear()
    c = _client(monkeypatch, tmp_path)
    c.post("/api/auth/setup", json={"username": "admin", "password": "claveSegura1"})
    c.cookies.clear()
    codes = [c.post("/api/auth/login", json={"username": "admin", "password": "x"}).status_code for _ in range(6)]
    assert codes[-1] == 429
    auth._fails.clear()
