"""Tests de panel/config_store.py (roundtrip .env sin GUI)."""

import os
import tempfile
import unittest

from panel.config_store import read_env, write_env


class ConfigStoreTest(unittest.TestCase):
    def test_roundtrip_preserva(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, ".env")
            with open(path, "w", encoding="utf-8") as f:
                f.write("# comentario\nDISCORD_TOKEN=abc\n\nOTRA=1\n")
            write_env(path, {"BOT_NAME": "DJ", "DISCORD_TOKEN": "xyz"})
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("# comentario", content)
            self.assertIn("DISCORD_TOKEN=xyz", content)
            self.assertIn("OTRA=1", content)
            self.assertIn("BOT_NAME=DJ", content)
            self.assertEqual(read_env(path)["BOT_NAME"], "DJ")

    def test_sin_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, ".env")
            self.assertEqual(read_env(path), {})
            write_env(path, {"A": "1"})
            self.assertEqual(read_env(path), {"A": "1"})

    def test_valor_con_igual(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, ".env")
            write_env(path, {"K": "a=b=c"})
            self.assertEqual(read_env(path)["K"], "a=b=c")


if __name__ == "__main__":
    unittest.main()
