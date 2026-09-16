"""Validación de consultas de /play (Sprint 3, A-11).

Clasifica la entrada antes de llamar a yt-dlp para responder rápido y claro
en vez de dejar que falle la extracción (CB-01, CB-10).
"""
from urllib.parse import urlparse

YOUTUBE_DOMAINS = ("youtube.com", "youtu.be", "music.youtube.com")

TEXT = "text"
YOUTUBE_VIDEO = "youtube_video"
YOUTUBE_PLAYLIST = "youtube_playlist"
UNSUPPORTED_URL = "unsupported_url"


def _is_url(query: str) -> bool:
    q = query.strip().lower()
    return q.startswith("http://") or q.startswith("https://")


def _domain(netloc: str) -> str:
    netloc = netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def classify(query: str) -> str:
    """TEXT | YOUTUBE_VIDEO | YOUTUBE_PLAYLIST | UNSUPPORTED_URL."""
    q = query.strip()
    if not q or not _is_url(q):
        return TEXT
    try:
        parts = urlparse(q)
    except ValueError:
        return UNSUPPORTED_URL
    domain = _domain(parts.netloc or "")
    if not any(domain == d or domain.endswith("." + d) for d in YOUTUBE_DOMAINS):
        return UNSUPPORTED_URL
    path = parts.path.lower()
    if "list=" in (parts.query or "").lower():
        return YOUTUBE_PLAYLIST
    if path == "/playlist" or path.startswith("/playlist/"):
        return YOUTUBE_PLAYLIST
    return YOUTUBE_VIDEO


def unsupported_message() -> str:
    return "❌ No puedo reproducir este enlace. Solo YouTube (video, shorts o playlist) o nombre de canción."
