"""Logger a archivo (con rotación) + consola (Sprint 2 C-03, S11)."""

import logging
import os
from logging.handlers import RotatingFileHandler

_configured = False

LOG_MAX_BYTES = 2 * 1024 * 1024  # 2 MB por archivo
LOG_BACKUPS = 5  # bot.log + bot.log.1 ... bot.log.5


def setup_logger(
    name: str = "musicbot",
    level: int | None = None,
    log_dir: str = "logs",
) -> logging.Logger:
    global _configured
    logger = logging.getLogger(name)
    if level is None:
        level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logger.setLevel(level)
    if _configured:
        return logger
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    os.makedirs(log_dir, exist_ok=True)
    fh = RotatingFileHandler(
        os.path.join(log_dir, "bot.log"),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUPS,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    _configured = True
    return logger


log = setup_logger()
