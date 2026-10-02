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
