"""Tests de core/voice (checks, apagado y reproducción) con fakes."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import discord

import core.voice as V
from core.voice import check_same_voice, get_lock
from music.queue import HISTORY, SONG_QUEUES, get_history, get_queue
from utils.errors import (
    MusicBotError,
    NotConnectedError,
    NothingPlayingError,
    WrongChannelError,
    user_message,
)


def _vc(connected=True, channel="canal-A"):
    return SimpleNamespace(is_connected=lambda: connected, channel=channel)


def _user_voice(channel="canal-A"):
    return SimpleNamespace(channel=channel)


class SameVoiceTest(unittest.TestCase):
    def test_ok_mismo_canal(self):
        check_same_voice(_vc(), _user_voice())  # no lanza

    def test_bot_desconectado(self):
        with self.assertRaises(NotConnectedError):
            check_same_voice(None, _user_voice())
        with self.assertRaises(NotConnectedError):
            check_same_voice(_vc(connected=False), _user_voice())

    def test_otro_canal(self):
        with self.assertRaises(WrongChannelError):
            check_same_voice(_vc(channel="canal-A"), _user_voice("canal-B"))

    def test_usuario_sin_voz(self):
        with self.assertRaises(WrongChannelError):
            check_same_voice(_vc(), None)
        with self.assertRaises(WrongChannelError):
            check_same_voice(_vc(), SimpleNamespace(channel=None))

    def test_lock_por_guild_es_unico(self):
        self.assertIs(get_lock("g1"), get_lock("g1"))


class UserMessageTest(unittest.TestCase):
    def test_mapea_controlados(self):
        self.assertIn("mismo canal", user_message(WrongChannelError()))
        self.assertIn("canal de voz", user_message(NotConnectedError()))
        self.assertIn("nada", user_message(NothingPlayingError()))

    def test_inesperado_no_crudo(self):
        msg = user_message(RuntimeError("x"))
        self.assertIn("RuntimeError", msg)
        self.assertNotIn("x", msg.replace("RuntimeError", ""))
        self.assertTrue(isinstance(MusicBotError(), Exception))


def _track(title, url="http://audio"):
    return {
        "title": title,
        "url": url,
        "webpage_url": "http://page",
        "duration": 60,
        "uploader": "U",
        "thumbnail": None,
        "requested_by": "T",
    }


class FakeVC:
    def __init__(self):
        self.playing = False
        self.played = []
        self.stopped = 0
        self.disconnected = 0

    def is_connected(self):
        return True

    def is_playing(self):
        return self.playing

    def is_paused(self):
        return False

    def stop(self):
        self.stopped += 1
        self.playing = False

    async def disconnect(self, **kwargs):
        self.disconnected += 1

    def play(self, source, after=None):
        self.playing = True
        self.played.append(source)


class FakeChannel:
    def __init__(self):
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append((content, kwargs))


def run(coro):
    return asyncio.run(coro)


class VoiceOpsTest(unittest.TestCase):
    def setUp(self):
        SONG_QUEUES.clear()
        HISTORY.clear()
        V.NOW_PLAYING.clear()
        V.LAST_TEXT.clear()

    def test_stop_playback_limpia(self):
        get_queue("g").append(_track("A"))
        V.NOW_PLAYING["g"] = _track("A")
        vc = FakeVC()
        vc.playing = True
        run(V.stop_playback("g", vc, clear=True))
        self.assertEqual(len(get_queue("g")), 0)
        self.assertNotIn("g", V.NOW_PLAYING)
        self.assertEqual(vc.stopped, 1)
        self.assertEqual(vc.disconnected, 1)

    def test_disconnect_conserva_cola(self):
        get_queue("g").append(_track("A"))
        vc = FakeVC()
        run(V.stop_playback("g", vc, clear=False))
        self.assertEqual(len(get_queue("g")), 1)
        self.assertEqual(vc.disconnected, 1)

    def test_play_next_reproduce_y_registra(self):
        get_queue("g").append(_track("Hit"))
        vc, ch = FakeVC(), FakeChannel()
        with patch.object(discord, "FFmpegOpusAudio", return_value="SRC"):
            run(V.play_next_song(vc, "g", ch, None))
        self.assertEqual(vc.played, ["SRC"])
        self.assertEqual(len(ch.sent), 1)
        self.assertEqual(V.NOW_PLAYING["g"]["title"], "Hit")
        self.assertEqual(len(get_history("g")), 1)

    def test_play_next_resuelve_url(self):
        get_queue("g").append(_track("Flat", url=None))

        async def fake_resolve(page):
            return "http://stream", "Resuelto"

        vc, ch = FakeVC(), FakeChannel()
        with (
            patch.object(discord, "FFmpegOpusAudio", return_value="SRC"),
            patch("music.search.resolve_stream_url", new=fake_resolve),
        ):
            run(V.play_next_song(vc, "g", ch, None))
        self.assertEqual(vc.played, ["SRC"])
        self.assertEqual(V.NOW_PLAYING["g"]["title"], "Resuelto")

    def test_play_next_cola_vacia_termina(self):
        vc, ch = FakeVC(), FakeChannel()
        run(V.play_next_song(vc, "g", ch, None))
        self.assertEqual(vc.disconnected, 1)
        self.assertFalse(vc.played)


if __name__ == "__main__":
    unittest.main()
