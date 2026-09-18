"""Tests de services/lyrics_service.py (fetch mockeado)."""

import asyncio
import unittest

import services.lyrics_service as L


def run(coro):
    return asyncio.run(coro)


class LyricsTest(unittest.TestCase):
    def setUp(self):
        L._CACHE.clear()

    def test_ok_y_cache(self):
        calls = []

        def fake_fetch(title, artist):
            calls.append((title, artist))
            return {"plainLyrics": "la\nli\nlu"}

        L._fetch_backup = getattr(L, "_fetch", None)
        L._fetch = fake_fetch
        try:
            self.assertEqual(run(L.get_lyrics("T", "A")), "la\nli\nlu")
            self.assertEqual(run(L.get_lyrics("T", "A")), "la\nli\nlu")
            self.assertEqual(len(calls), 1)  # segunda fue caché
        finally:
            L._fetch = L._fetch_backup

    def test_sin_letra(self):
        L._fetch_backup = getattr(L, "_fetch", None)
        L._fetch = lambda t, a: {"plainLyrics": "   "}
        try:
            self.assertIsNone(run(L.get_lyrics("X", "Y")))
        finally:
            L._fetch = L._fetch_backup

    def test_error_red(self):
        L._fetch_backup = getattr(L, "_fetch", None)
        L._fetch = lambda t, a: None
        try:
            self.assertIsNone(run(L.get_lyrics("X", "Y")))
        finally:
            L._fetch = L._fetch_backup

    def test_paginas(self):
        lyrics = "\n".join(f"l{i}" for i in range(30))
        pages = L.lyric_pages(lyrics, per_page=14)
        self.assertEqual(len(pages), 3)
        self.assertTrue(pages[0].startswith("l0"))


if __name__ == "__main__":
    unittest.main()
