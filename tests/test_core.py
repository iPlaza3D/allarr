from app.library import clean


def test_clean_names():
    assert clean("Matrix (1999)") == ("Matrix", "1999")
    assert clean("Toy.Story.1995.1080p.BluRay.x264.mkv") == ("Toy Story", "1995")
    assert clean("Cosmos") == ("Cosmos", "")


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
    c.cookies.set("media-server-utility_session", "YWRtaW58OTk5OTk5OTk5OQ==.firma")
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


def test_torznab_wolfmax_is_spanish():
    from app.torznab import parse
    xml = """<rss xmlns:torznab="http://torznab.com/schemas/2015/feed"><channel>
<item><title>Renoir 2025 HDRip</title><jackettindexer>Wolfmax4K</jackettindexer><link>http://j/dl</link></item></channel></rss>"""
    assert parse(xml)[0]["spanish"]


def _lib(monkeypatch, tmp_path, kind="movies"):
    from app import config
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "r.db")
    root = tmp_path / "lib"
    root.mkdir()
    return root, {**config.DEFAULTS, f"lib_{kind}": str(root), "tvdb_api_key": "k"}


class FakeTMDB:
    def __init__(self, coll=None): self.coll = coll
    def search(self, q):
        return [{"tmdb_id": 7, "media_type": "movie", "title": "Matrix Recargada", "original_title": "The Matrix Reloaded",
                 "year": "2003", "poster": None, "overview": ""}]
    def collection_of(self, i): return self.coll


def test_rename_movie_with_saga(monkeypatch, tmp_path):
    from app import library, renamer
    root, s = _lib(monkeypatch, tmp_path)
    (root / "The.Matrix.Reloaded.2003.1080p").mkdir()
    t = FakeTMDB({"id": 1, "name": "Matrix: Colección"})
    e = renamer.plan(s, ["movies"], "tmdb", True, t)[0]
    assert e["status"] == "ok" and e["new"] == "Matrix Colección (Saga)/Matrix Recargada (2003)"
    r = renamer.apply(s, [e])
    assert r[0]["ok"] and (root / e["new"]).is_dir()
    assert library.scan(str(root), "movies") == [e["new"]]
    assert library._lookup(t, "movie", e["new"])["folder"] == e["new"]
    e2 = renamer.plan(s, ["movies"], "tmdb", False, t)[0]  # desagrupar
    renamer.apply(s, [e2])
    assert (root / "Matrix Recargada (2003)").is_dir() and not (root / "Matrix Colección (Saga)").exists()


def test_rename_series_episodes_tvdb(monkeypatch, tmp_path):
    from app import renamer
    root, s = _lib(monkeypatch, tmp_path, "series")
    d = root / "la.casa.de.papel.2017"
    (d / "Temporada 1").mkdir(parents=True)
    (d / "Temporada 1" / "lcdp.S01E02.720p.mkv").write_bytes(b"x")

    class T(FakeTMDB):
        def search(self, q):
            return [{"tmdb_id": 9, "media_type": "tv", "title": "La casa de papel", "original_title": "La casa de papel",
                     "year": "2017", "poster": None, "overview": ""}]

    class V:
        def __init__(self, k): pass
        def _token(self): return "t"
        def spanish_title(self, mt, q, year): return "La Casa de Papel: Serie"
    monkeypatch.setattr(renamer, "TVDB", V)
    e = renamer.plan(s, ["series"], "tvdb", False, T())[0]
    assert e["new"] == "La Casa de Papel Serie (2017)"
    assert e["episodes"][0]["new"] == "Temporada 1/La Casa de Papel Serie - S01E02.mkv"
    assert renamer.apply(s, [e])[0]["ok"]
    assert (root / e["new"] / "Temporada 1" / "La Casa de Papel Serie - S01E02.mkv").exists()


def test_rename_conflict_and_unidentified(monkeypatch, tmp_path):
    from app import renamer
    root, s = _lib(monkeypatch, tmp_path)
    (root / "Matrix.2003").mkdir()
    (root / "Matrix Recargada (2003)").mkdir()
    class Empty(FakeTMDB):
        def search(self, q): return []
    st = {e["folder"]: e["status"] for e in renamer.plan(s, ["movies"], "tmdb", False, FakeTMDB())}
    (root / "Desconocida").mkdir()
    assert {e["folder"]: e["status"] for e in renamer.plan(s, ["movies"], "tmdb", False, Empty())}["Desconocida"] == "unidentified"
    assert st["Matrix.2003"] == "conflict" and st["Matrix Recargada (2003)"] == "same"


def test_poster_rejects_foreign_url(monkeypatch, tmp_path):
    import pytest
    from app import library
    with pytest.raises(ValueError):
        library.set_poster("movies", "x", "http://evil/x.jpg", "http://evil/x.jpg", str(tmp_path), True)
