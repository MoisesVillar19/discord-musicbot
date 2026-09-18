"""Tests de handlers con fakes (sin gateway ni voz real)."""

import asyncio
import os
import tempfile
import unittest
from types import SimpleNamespace

# CWD aislado ANTES de importar bot (ensure_aliases crea aliases.json).
_ORIG_CWD = os.getcwd()
_TMP = tempfile.TemporaryDirectory()
os.chdir(_TMP.name)
os.environ.setdefault("DISCORD_TOKEN", "test-token")

import bot as botmod  # noqa: E402
from music.queue import SONG_QUEUES, get_queue  # noqa: E402


def _track(title):
    return {
        "title": title,
        "url": "http://a",
        "webpage_url": "http://p",
        "duration": 1,
        "uploader": None,
        "thumbnail": None,
        "requested_by": "x",
    }


class FakeResponse:
    def __init__(self):
        self.sent = []

    async def defer(self, **kwargs):
        pass

    async def send_message(self, content=None, **kwargs):
        self.sent.append(content)

    def is_done(self):
        return True


class FakeMsg:
    def __init__(self):
        self.edits = []

    async def edit(self, **kwargs):
        self.edits.append(kwargs)


class FakeFollowup:
    def __init__(self):
        self.sent = []
        self.calls = []
        self.msgs = []

    async def send(self, content=None, **kwargs):
        self.sent.append(content)
        self.calls.append(kwargs)
        msg = FakeMsg()
        self.msgs.append(msg)
        return msg


class FakeVC:
    def __init__(self, playing=True, channel="A"):
        self._playing = playing
        self.channel = channel
        self.stopped = 0
        self.disconnected = 0
        self.played = []

    def is_connected(self):
        return True

    def is_playing(self):
        return self._playing

    def is_paused(self):
        return False

    def stop(self):
        self.stopped += 1

    def pause(self):
        self._playing = False

    def resume(self):
        self._playing = True

    async def disconnect(self, **kwargs):
        self.disconnected += 1

    def play(self, source, after=None):
        self.played.append(source)


def _interaction(vc, channel="A", in_voice=True):
    guild = SimpleNamespace(voice_client=vc, id=1)
    user = SimpleNamespace(
        voice=SimpleNamespace(channel=channel) if in_voice else None, display_name="T", id=7
    )
    return SimpleNamespace(
        response=FakeResponse(),
        followup=FakeFollowup(),
        guild=guild,
        guild_id=1,
        user=user,
        channel=SimpleNamespace(),
    )


def run(coro):
    return asyncio.run(coro)


def callback(name):
    return botmod.bot.tree.get_command(name).callback


def tearDownModule():
    import logging

    logger = logging.getLogger("musicbot")
    for h in logger.handlers[:]:
        try:
            h.close()
        finally:
            logger.removeHandler(h)
    os.chdir(_ORIG_CWD)
    _TMP.cleanup()


class HandlersTest(unittest.TestCase):
    def setUp(self):
        SONG_QUEUES.clear()
        for t in ["A", "B", "C", "D"]:
            get_queue("1").append(_track(t))

    def test_skip_cantidad(self):
        vc = FakeVC(playing=True)
        inter = _interaction(vc)
        run(callback("skip")(inter, cantidad=3))
        self.assertEqual(vc.stopped, 1)
        self.assertEqual(len(get_queue("1")), 2)  # A cortada + B,C descartadas
        self.assertIn("3", inter.followup.sent[-1])

    def test_skip_sin_nada(self):
        inter = _interaction(FakeVC(playing=False))
        run(callback("skip")(inter))
        self.assertIn("No hay nada", inter.followup.sent[-1])

    def test_skip_otro_canal(self):
        inter = _interaction(FakeVC(playing=True), channel="B")
        run(callback("skip")(inter))
        self.assertIn("mismo canal", inter.followup.sent[-1])

    def test_remove_valido_e_invalido(self):
        inter = _interaction(FakeVC(playing=True))
        run(callback("remove")(inter, posicion=2))
        self.assertIn("Eliminada", inter.response.sent[-1])
        inter2 = _interaction(FakeVC(playing=True))
        run(callback("remove")(inter2, posicion=99))
        self.assertIn("inválida", inter2.response.sent[-1])

    def test_skip_sin_rol_dj(self):
        from unittest.mock import patch

        inter = _interaction(FakeVC(playing=True))
        with patch.object(botmod, "DJ_ROLE_ID", 999):
            run(callback("skip")(inter))
        self.assertIn("rol DJ", inter.followup.sent[-1])

    def test_lyrics_sin_nada(self):
        inter = _interaction(FakeVC(playing=False))
        run(callback("lyrics")(inter))
        self.assertIn("No hay nada", inter.followup.sent[-1])

    def test_lyrics_actual(self):
        from unittest.mock import AsyncMock, patch

        botmod.voice_mgr.NOW_PLAYING["1"] = _track("Song")
        try:
            inter = _interaction(FakeVC(playing=True))
            with patch("services.lyrics_service.get_lyrics", new=AsyncMock(return_value="l1\nl2")):
                run(callback("lyrics")(inter))
            self.assertIsNotNone(inter.followup.calls[-1].get("embed"))
        finally:
            botmod.voice_mgr.NOW_PLAYING.pop("1", None)

    def test_pick_track(self):
        opts = [_track("X"), _track("Y")]
        self.assertEqual(botmod._pick_track(opts, "1")["title"], "Y")
        self.assertIsNone(botmod._pick_track(opts, "9"))
        self.assertIsNone(botmod._pick_track(opts, "x"))


class FakeChannel:
    def __init__(self):
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append((content, kwargs))


class ExtendedHandlersTest(unittest.TestCase):
    def setUp(self):
        SONG_QUEUES.clear()
        for t in ["A", "B"]:
            get_queue("1").append(_track(t))

    def _voc(self, playing=False):
        vc = FakeVC(playing=playing)
        inter = _interaction(vc)
        inter.channel = FakeChannel()
        return inter, vc

    def test_pause_resume(self):
        inter, vc = self._voc(playing=True)
        run(callback("pause")(inter))
        self.assertIn("pausada", inter.response.sent[-1])
        inter2, _ = self._voc(playing=False)
        run(callback("resume")(inter2))
        self.assertIn("pausado", inter2.response.sent[-1])

    def test_pause_otro_canal(self):
        inter = _interaction(FakeVC(playing=True), channel="B")
        run(callback("pause")(inter))
        self.assertIn("mismo canal", inter.response.sent[-1])

    def test_stop_limpia_y_desconecta(self):
        inter, vc = self._voc(playing=True)
        run(callback("stop")(inter))
        self.assertEqual(len(get_queue("1")), 0)
        self.assertEqual(vc.disconnected, 1)
        self.assertIn("detenida", inter.followup.msgs[0].edits[-1]["content"])

    def test_disconnect_conserva_cola(self):
        inter, vc = self._voc(playing=True)
        run(callback("disconnect")(inter))
        self.assertEqual(len(get_queue("1")), 2)
        self.assertEqual(vc.disconnected, 1)

    def test_queue_nowplaying_next(self):
        inter, _ = self._voc()
        run(callback("queue")(inter))
        self.assertTrue(inter.response.sent)
        inter2, _ = self._voc()
        run(callback("nowplaying")(inter2))
        self.assertIn("nada", inter2.response.sent[-1])
        inter3, _ = self._voc()
        run(callback("next")(inter3))
        self.assertIn("Siguiente", inter3.response.sent[-1])

    def test_shuffle_clear_move(self):
        inter, _ = self._voc()
        run(callback("shuffle")(inter))
        self.assertIn("mezclada", inter.response.sent[-1])
        run(callback("clear")(inter))
        self.assertEqual(len(get_queue("1")), 0)
        inter2, _ = self._voc()
        run(callback("move")(inter2, origen=1, destino=5))
        self.assertIn("inválidas", inter2.response.sent[-1])

    def test_play_url_encola_y_arranca(self):
        from unittest.mock import AsyncMock, patch

        async def fake_search(q, limit, start):
            return [_track("URL")], 1, 0

        started = {}

        async def fake_next(vc, gid, channel, loop):
            started["yes"] = True

        inter, vc = self._voc(playing=False)
        with (
            patch("music.search.search_ytdlp", new=fake_search),
            patch.object(botmod.voice_mgr, "ensure_voice", new=AsyncMock(return_value=vc)),
            patch.object(botmod.voice_mgr, "play_next_song", new=fake_next),
        ):
            run(callback("play")(inter, song_query="https://youtu.be/abc"))
        self.assertIn("Agregada", inter.followup.sent[-1])
        self.assertTrue(started.get("yes"))


if __name__ == "__main__":
    unittest.main()
