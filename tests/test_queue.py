"""Tests de music/queue.py (lógica pura, sin mocks)."""
import unittest

from music.queue import (
    SONG_QUEUES,
    clear_queue,
    get_queue,
    move_track,
    peek_queue,
    queue_size,
    remove_track,
    shuffle_queue,
)


def _track(title):
    return {
        "title": title,
        "url": f"http://audio/{title}",
        "webpage_url": f"http://page/{title}",
        "duration": 180,
        "uploader": "Artista",
        "thumbnail": None,
        "requested_by": "tester",
    }


class QueueTest(unittest.TestCase):
    def setUp(self):
        SONG_QUEUES.clear()
        q = get_queue("g1")
        for t in ["A", "B", "C", "D"]:
            q.append(_track(t))

    def test_colas_independientes_por_guild(self):
        self.assertEqual(queue_size("g1"), 4)
        self.assertEqual(queue_size("g2"), 0)

    def test_clear(self):
        clear_queue("g1")
        self.assertEqual(queue_size("g1"), 0)

    def test_remove_medio(self):
        removed = remove_track("g1", 2)
        self.assertEqual(removed["title"], "B")
        self.assertEqual([t["title"] for t in peek_queue("g1")], ["A", "C", "D"])

    def test_remove_rango_invalido(self):
        self.assertIsNone(remove_track("g1", 0))
        self.assertIsNone(remove_track("g1", 5))
        self.assertEqual(queue_size("g1"), 4)

    def test_move_adelante(self):
        self.assertTrue(move_track("g1", 1, 4))
        self.assertEqual([t["title"] for t in peek_queue("g1")], ["B", "C", "D", "A"])

    def test_move_atras(self):
        self.assertTrue(move_track("g1", 4, 1))
        self.assertEqual([t["title"] for t in peek_queue("g1")], ["D", "A", "B", "C"])

    def test_move_misma_posicion(self):
        self.assertTrue(move_track("g1", 2, 2))
        self.assertEqual(queue_size("g1"), 4)

    def test_move_rango_invalido(self):
        self.assertFalse(move_track("g1", 1, 9))
        self.assertEqual(queue_size("g1"), 4)

    def test_shuffle_conserva_elementos(self):
        antes = sorted(t["title"] for t in peek_queue("g1"))
        self.assertTrue(shuffle_queue("g1"))
        despues = sorted(t["title"] for t in peek_queue("g1"))
        self.assertEqual(antes, despues)

    def test_shuffle_cola_corta(self):
        clear_queue("g1")
        get_queue("g1").append(_track("solo"))
        self.assertFalse(shuffle_queue("g1"))

    def test_peek_no_modifica(self):
        peek_queue("g1")
        self.assertEqual(queue_size("g1"), 4)


if __name__ == "__main__":
    unittest.main()
