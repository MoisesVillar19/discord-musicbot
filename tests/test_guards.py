"""Tests de core/guards.py con fakes."""

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.guards import require_dj, require_voice


class FakeResponse:
    def __init__(self, done=False):
        self._done = done
        self.sent = []

    def is_done(self):
        return self._done

    async def send_message(self, content=None, **kwargs):
        self.sent.append(content)


class FakeFollowup:
    def __init__(self):
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append(content)


def _interaction(vc, user_voice="A", done=False):
    guild = SimpleNamespace(voice_client=vc)
    user = SimpleNamespace(
        voice=SimpleNamespace(channel=user_voice) if user_voice else None,
        roles=[],
    )
    return SimpleNamespace(
        response=FakeResponse(done), followup=FakeFollowup(), guild=guild, user=user
    )


def _vc(channel="A"):
    return SimpleNamespace(is_connected=lambda: True, channel=channel)


def run(coro):
    return asyncio.run(coro)


class GuardsTest(unittest.TestCase):
    def test_voice_pasa(self):
        @require_voice
        async def cmd(interaction):
            return "ok"

        self.assertEqual(run(cmd(_interaction(_vc()))), "ok")

    def test_voice_corta_otro_canal(self):
        @require_voice
        async def cmd(interaction):
            return "ok"

        inter = _interaction(_vc("A"), user_voice="B")
        run(cmd(inter))
        self.assertIn("mismo canal", inter.response.sent[-1])

    def test_voice_usa_followup_si_defer(self):
        @require_voice
        async def cmd(interaction):
            return "ok"

        inter = _interaction(_vc("A"), user_voice="B", done=True)
        run(cmd(inter))
        self.assertIn("mismo canal", inter.followup.sent[-1])
        self.assertEqual(inter.response.sent, [])

    def test_dj_abierto_sin_config(self):
        @require_dj
        async def cmd(interaction):
            return "ok"

        self.assertEqual(run(cmd(_interaction(_vc()))), "ok")

    def test_dj_rechaza(self):
        @require_dj
        async def cmd(interaction):
            return "ok"

        with patch("core.guards.DJ_ROLE_ID", 999):
            inter = _interaction(_vc())
            run(cmd(inter))
        self.assertIn("rol DJ", inter.response.sent[-1])

    def test_en_metodo_de_cog(self):
        class Cog:
            @require_voice
            async def cmd(self, interaction):
                return ("cog", self)

        cog = Cog()
        self.assertEqual(run(cog.cmd(_interaction(_vc())))[0], "cog")


if __name__ == "__main__":
    unittest.main()
