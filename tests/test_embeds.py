"""Tests de ui/embeds.py (formato puro, sin Discord real)."""
import unittest

from ui.embeds import (
    QUEUE_PER_PAGE,
    format_duration,
    now_playing_embed,
    queue_page_embed,
    queue_pages,
    track_line,
)


def _track(i, by="DJ"):
    return {
        "title": f"T{i}",
        "url": "http://audio/x",
        "webpage_url": f"http://page/{i}",
        "duration": 125,
        "uploader": "Artista",
        "thumbnail": "http://thumb/x",
        "requested_by": by,
    }


class EmbedsTest(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(format_duration(125), "2:05")
        self.assertEqual(format_duration(3661), "1:01:01")
        self.assertEqual(format_duration(None), "—")
        self.assertEqual(format_duration("x"), "—")

    def test_track_line_completa(self):
        line = track_line(_track(1))
        self.assertIn("[T1](http://page/1)", line)
        self.assertIn("2:05", line)
        self.assertIn("DJ", line)

    def test_track_line_minima(self):
        line = track_line({"title": None, "webpage_url": None,
                           "duration": None, "requested_by": None})
        self.assertIn("Untitled", line)

    def test_now_playing_rico(self):
        e = now_playing_embed(_track(2))
        self.assertEqual(e.title, "🎧 Now Playing")
        self.assertIn("Artista", e.description)
        self.assertIn("2:05", e.description)
        self.assertIn("http://page/2", e.description)
        self.assertEqual(e.thumbnail.url, "http://thumb/x")

    def test_paginas(self):
        tracks = [_track(i) for i in range(25)]
        pages = queue_pages(tracks)
        self.assertEqual(len(pages), 3)
        self.assertEqual(len(pages[0]), QUEUE_PER_PAGE)
        e = queue_page_embed(pages[1], 2, 3, 25, QUEUE_PER_PAGE)
        self.assertIn("Página 2/3", e.footer.text)
        self.assertIn("11.", e.description)  # offset base 1

    def test_cola_vacia_una_pagina(self):
        pages = queue_pages([])
        self.assertEqual(pages, [[]])
        e = queue_page_embed([], 1, 1, 0, 0)
        self.assertIn("vacía", e.description)


if __name__ == "__main__":
    unittest.main()
