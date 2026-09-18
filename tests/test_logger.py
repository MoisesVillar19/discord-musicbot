"""Tests de utils/logger.py (rotación, sin escribir 2 MB)."""

import logging
import tempfile
import unittest
from logging.handlers import RotatingFileHandler


class LoggerTest(unittest.TestCase):
    def test_rotating_activo(self):
        import utils.logger as L

        L._configured = False
        try:
            with tempfile.TemporaryDirectory() as tmp:
                lg = L.setup_logger("test-rot", log_dir=tmp)
                rots = [h for h in lg.handlers if isinstance(h, RotatingFileHandler)]
                self.assertEqual(len(rots), 1)
                self.assertEqual(rots[0].backupCount, L.LOG_BACKUPS)
                self.assertEqual(rots[0].maxBytes, L.LOG_MAX_BYTES)
                lg.info("hola")
                for h in lg.handlers[:]:
                    try:
                        h.close()
                    finally:
                        lg.removeHandler(h)
        finally:
            L._configured = True
            logging.getLogger("test-rot").handlers.clear()


if __name__ == "__main__":
    unittest.main()
