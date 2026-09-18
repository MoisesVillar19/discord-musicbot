"""Tests de music/trolls.py e historial (puros, sin red)."""
import os
import tempfile
import unittest

from music import trolls as T
from music.queue import HISTORY, get_history, record_history


def _track(title):
    return {"title": title, "url": "http://a", "webpage_url": "http://p",
            "duration": 1, "uploader": None, "thumbnail": None,
            "requested_by": "x"}


class TrollsTest(unittest.TestCase):
    def setUp(self):
        self.trolls = [
            {"name": "Rick", "url": "http://r", "keywords": ["rickroll"]},
            {"name": "Trolo", "url": "http://t", "keywords": ["trololo"]},
        ]

    def test_keyword_exacta(self):
        self.assertEqual(T.match_keyword("  RICKROLL ", self.trolls)["name"], "Rick")
        self.assertIsNone(T.match_keyword("rick", self.trolls))
        self.assertIsNone(T.match_keyword("", self.trolls))

    def test_ambush_cero_desactivado(self):
        self.assertIsNone(T.roll_ambush(0.0, self.trolls, rng=lambda: 0.0))

    def test_ambush_pegada_y_fallada(self):
        hit = T.roll_ambush(0.05, self.trolls, rng=lambda: 0.01)
        self.assertIn(hit["name"], ("Rick", "Trolo"))
        self.assertIsNone(T.roll_ambush(0.05, self.trolls, rng=lambda: 0.99))

    def test_ambush_sin_lista(self):
        self.assertIsNone(T.roll_ambush(1.0, [], rng=lambda: 0.0))

    def test_ensure_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "trolls.json")
            data = T.ensure_trolls(target, os.path.join(tmp, "nope.json"))
            self.assertEqual(data, [])
            self.assertTrue(os.path.isfile(target))

    def test_ejemplo_repo_valido(self):
        repo = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), T.TROLLS_EXAMPLE)
        data = T.load_trolls(repo)
        self.assertGreaterEqual(len(data), 1)
        for t in data:
            self.assertTrue(t["url"] and t["keywords"])


class HistoryTest(unittest.TestCase):
    def setUp(self):
        HISTORY.clear()

    def test_guarda_y_topea(self):
        for i in range(25):
            record_history("g1", _track(f"T{i}"))
        hist = get_history("g1")
        self.assertEqual(len(hist), 20)
        self.assertEqual(hist[0]["title"], "T5")
        self.assertEqual(hist[-1]["title"], "T24")

    def test_por_guild_y_copia(self):
        record_history("g1", _track("A"))
        self.assertEqual(get_history("g2"), [])
        hist = get_history("g1")
        hist.clear()
        self.assertEqual(len(get_history("g1")), 1)


if __name__ == "__main__":
    unittest.main()
