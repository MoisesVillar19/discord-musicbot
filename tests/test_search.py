"""Tests de music/search.py con _extract mockeado (sin red)."""
import asyncio
import unittest
from unittest.mock import patch

import music.search as search


def _entry(title, url="http://audio/x", page="http://page/x"):
    return {
        "title": title,
        "url": url,
        "webpage_url": page,
        "duration": 200,
        "uploader": "Artista",
        "thumbnail": "http://thumb/x",
    }


def run(coro):
    return asyncio.run(coro)


class SearchTest(unittest.TestCase):
    def test_video_unico_url(self):
        with patch.object(search, "_extract", return_value=_entry("Solo")):
            tracks, total, unav = run(search.search_ytdlp("https://youtu.be/abc"))
        self.assertEqual(total, 1)
        self.assertEqual(tracks[0]["title"], "Solo")
        self.assertEqual(tracks[0]["uploader"], "Artista")
        self.assertIsNone(tracks[0]["requested_by"])

    def test_texto_usa_ytsearch_y_devuelve_primero(self):
        info = {"entries": [None, _entry("Hit")]}
        with patch.object(search, "_extract", return_value=info) as m:
            tracks, total, _ = run(search.search_ytdlp("mi cancion"))
        m.assert_called_once()
        self.assertTrue(m.call_args[0][0].startswith("ytsearch:"))
        self.assertEqual(len(tracks), 1)

    def test_playlist_paginada_start_limit(self):
        info = {"entries": [_entry(f"T{i}") for i in range(10)]}
        with patch.object(search, "_extract", return_value=info):
            tracks, total, unav = run(
                search.search_ytdlp("https://youtube.com/playlist?list=x",
                                    max_tracks=3, start_index=4)
            )
        self.assertEqual(total, 10)
        self.assertEqual([t["title"] for t in tracks], ["T4", "T5", "T6"])
        self.assertEqual(unav, 0)

    def test_playlist_cuenta_no_disponibles(self):
        info = {"entries": [_entry("Ok"), None, {"title": None}]}
        with patch.object(search, "_extract", return_value=info):
            tracks, total, unav = run(
                search.search_ytdlp("https://youtube.com/playlist?list=x")
            )
        # {"title": None} -> Untitled pero sin url ni page -> no disponible
        self.assertEqual([t["title"] for t in tracks], ["Ok"])
        self.assertEqual(unav, 2)

    def test_error_ytdlp_devuelve_vacio(self):
        with patch.object(search, "_extract", side_effect=Exception("boom")):
            self.assertEqual(run(search.search_ytdlp("https://youtu.be/x")), ([], 0, 0))

    def test_resolve_stream_url(self):
        with patch.object(search, "_extract", return_value=_entry("R", url="http://stream")):
            url, title = run(search.resolve_stream_url("http://page/x"))
        self.assertEqual((url, title), ("http://stream", "R"))

    def test_resolve_sin_url(self):
        self.assertEqual(run(search.resolve_stream_url("")), (None, None))

    def test_playlist_flat_url_no_reproducible(self):
        # Entradas flat: url es el id (no streamable) -> se descarta,
        # webpage_url se conserva para resolver al reproducir.
        flat = {"title": "Flat", "url": "abc123", "webpage_url": "http://page/abc",
                "duration": None, "uploader": None, "thumbnail": None}
        info = {"entries": [flat]}
        with patch.object(search, "_extract", return_value=info) as m:
            tracks, total, unav = run(
                search.search_ytdlp("https://youtube.com/playlist?list=x")
            )
        self.assertEqual(m.call_args[0][1].get("extract_flat"), "in_playlist")
        self.assertEqual(total, 1)
        self.assertIsNone(tracks[0]["url"])
        self.assertEqual(tracks[0]["webpage_url"], "http://page/abc")

    def test_video_unico_sin_flat(self):
        with patch.object(search, "_extract", return_value=_entry("V")) as m:
            run(search.search_ytdlp("https://youtu.be/abc"))
        self.assertNotIn("extract_flat", m.call_args[0][1])


if __name__ == "__main__":
    unittest.main()
