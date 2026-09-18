"""Letras vía LRCLIB API libre (sin key). Sprint 11, B-10.

Spike validado en vivo: GET /api/get?track_name=&artist_name= devuelve
plainLyrics. Caché en memoria por (title, artist).
"""

import asyncio
import json
import urllib.parse
import urllib.request

API = "https://lrclib.net/api/get"
_CACHE: dict = {}


def _fetch(title: str, artist: str) -> dict | None:
    qs = urllib.parse.urlencode({"track_name": title, "artist_name": artist or ""})
    req = urllib.request.Request(f"{API}?{qs}", headers={"User-Agent": "MusicBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status != 200:
                return None
            return json.load(r)
    except Exception:
        return None


async def get_lyrics(title: str, artist: str | None = None) -> str | None:
    """Devuelve plainLyrics o None (sin letra / instrumental / error)."""
    key = ((title or "").strip().lower(), (artist or "").strip().lower())
    if key in _CACHE:
        return _CACHE[key]
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, lambda: _fetch(title, artist or ""))
    lyrics = (data or {}).get("plainLyrics") or None
    if lyrics and not lyrics.strip():
        lyrics = None
    _CACHE[key] = lyrics
    return lyrics


def lyric_pages(lyrics: str, per_page: int = 14) -> list:
    lines = [ln for ln in lyrics.split("\n")]
    return ["\n".join(lines[i : i + per_page]) for i in range(0, len(lines), per_page)] or [""]
