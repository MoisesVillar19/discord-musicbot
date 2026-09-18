"""Logger a archivo + consola (Sprint 2, C-03)."""

import logging
import os

_configured = False


def setup_logger(name: str = "musicbot", level: int = logging.INFO) -> logging.Logger:
    global _configured
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if _configured:
        return logger
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    os.makedirs("logs", exist_ok=True)
    fh = logging.FileHandler(os.path.join("logs", "bot.log"), encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    _configured = True
    return logger


log = setup_logger()
