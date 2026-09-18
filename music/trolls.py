"""Canciones troll (Sprint 8, B-08).

Tres modos: emboscada aleatoria en /play (ratio bajo, configurable),
keyword exacta y comando /troll. Lista en trolls.json (local) con
trolls.example.json como semilla.
"""
import json
import os
import random

TROLLS_FILE = "trolls.json"
TROLLS_EXAMPLE = "trolls.example.json"


def default_trolls() -> list:
    return []


def _clean_entry(e) -> dict | None:
    if not isinstance(e, dict):
        return None
    url = (e.get("url") or "").strip()
    if not url:
        return None
    keywords = [k.strip().lower() for k in (e.get("keywords") or []) if k.strip()]
    return {"name": e.get("name") or "Troll", "url": url, "keywords": keywords}


def ensure_trolls(path: str = TROLLS_FILE, example: str = TROLLS_EXAMPLE) -> list:
    if not os.path.isfile(path):
        if os.path.isfile(example):
            with open(example, encoding="utf-8") as f:
                seed = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(seed)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_trolls(), f)
    return load_trolls(path)


def load_trolls(path: str = TROLLS_FILE) -> list:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [t for t in (_clean_entry(e) for e in data) if t]


def match_keyword(query: str, trolls: list) -> dict | None:
    """Keyword exacta (insensible a mayúsculas) -> troll fijo."""
    q = query.strip().lower()
    for t in trolls:
        if q and q in t["keywords"]:
            return t
    return None


def roll_ambush(chance: float, trolls: list, rng=random.random) -> dict | None:
    """Sorteo de emboscada: con prob. chance devuelve un troll al azar."""
    if not trolls or chance <= 0:
        return None
    if rng() < chance:
        return random.choice(trolls)
    return None
