"""Tests de core/voice (check_same_voice) y utils/errors con fakes, sin Discord."""
import unittest
from types import SimpleNamespace

from core.voice import check_same_voice, get_lock
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


if __name__ == "__main__":
    unittest.main()
