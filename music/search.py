"""Búsqueda de canciones/playlists con yt-dlp.

Soporta:
- URLs directas de YouTube (video o playlist)
- Texto libre (usa ytsearch automáticamente)
"""
import yt_dlp
import asyncio

from utils.validators import YOUTUBE_PLAYLIST, classify

YTDLP_BASE_OPTS = {
    "format": "bestaudio[abr<=96]/bestaudio",
    "quiet": True,
    "ignoreerrors": True,
    "no_warnings": True,
    "youtube_include_dash_manifest": False,
    "youtube_include_hls_manifest": False,
    # Necesario para que el texto libre funcione sin prefijo ytsearch:
    "default_search": "ytsearch",
}


def _extract(query, opts):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(query, download=False)


def _is_url(query: str) -> bool:
    q = query.strip().lower()
    return q.startswith("http://") or q.startswith("https://") or q.startswith("ytsearch")


def _track_from_entry(e: dict, flat: bool = False) -> dict | None:
    """Normaliza una entrada de yt-dlp al formato Track (ver docs/desarrollo/diccionario.md).

    Con flat=True (extract_flat de playlist) la entrada solo trae metadatos
    ligeros: `url` NO es reproducible (suele ser el id) y se descarta; el audio
    se resuelve al reproducir con resolve_stream_url(). `webpage_url` es la
    identidad estable.
    """
    if not e:
        return None
    url = None if flat else e.get("url")
    return {
        "title": e.get("title") or "Untitled",
        "url": url,  # puede ser None -> se resuelve al reproducir
        "webpage_url": e.get("webpage_url"),
        "duration": e.get("duration"),
        "uploader": e.get("uploader"),
        "thumbnail": e.get("thumbnail"),
        "requested_by": None,  # lo pone /play con el usuario de Discord
    }


async def search_ytdlp(query: str, max_tracks: int = 50, start_index: int = 0):
    """Devuelve (tracks, total, unavailable).

    - Si query es texto libre y no es URL, se busca con ytsearch.
    - Si es playlist, se aplica start_index + max_tracks.
    """
    loop = asyncio.get_running_loop()
    opts = YTDLP_BASE_OPTS.copy()

    is_url = _is_url(query)
    # Solo las URLs pueden ser playlists. El texto siempre es 1 resultado.
    opts["noplaylist"] = not is_url
    # Playlists en modo ligero: solo metadatos (título + webpage_url).
    # La 1ª canción suena sin esperar el análisis completo; el audio de cada
    # track se resuelve al reproducir (ver ADR-002). Solo URLs de playlist;
    # videos únicos y búsquedas siguen con extracción completa.
    if classify(query) == YOUTUBE_PLAYLIST:
        opts["extract_flat"] = "in_playlist"

    # Texto libre -> forzar búsqueda de 1 resultado para respuesta rápida.
    if not is_url:
        query = f"ytsearch:{query.strip()}"

    try:
        info = await loop.run_in_executor(None, lambda: _extract(query, opts))
    except Exception as e:
        print(f"[yt-dlp] Error: {e}")
        return [], 0, 0

    if not info:
        return [], 0, 0

    tracks: list[dict] = []

    # Playlist o resultado de búsqueda (ytsearch devuelve "entries")
    if "entries" in info:
        entries = list(info.get("entries") or [])
        # ytsearch: filtrar Nones y quedarse con el primero
        if not is_url:
            for e in entries:
                t = _track_from_entry(e)
                if t and (t["url"] or t["webpage_url"]):
                    return [t], 1, 0
            return [], 0, 0

        # Playlist real (entradas flat): paginar con start/limit
        total = len(entries)
        sliced = entries[start_index:start_index + max_tracks]
        unavailable = 0
        for e in sliced:
            t = _track_from_entry(e, flat=True)
            if t is None or not t["webpage_url"]:
                unavailable += 1
                continue
            tracks.append(t)
        return tracks, total, unavailable

    # Video único
    t = _track_from_entry(info)
    if t is None or (not t["url"] and not t["webpage_url"]):
        return [], 0, 0
    return [t], 1, 0


async def resolve_stream_url(webpage_url: str) -> tuple[str | None, str | None]:
    """Dada la página del video, devuelve (audio_url, title)."""
    if not webpage_url:
        return None, None
    loop = asyncio.get_running_loop()
    opts = YTDLP_BASE_OPTS.copy()
    opts["noplaylist"] = True
    try:
        info = await loop.run_in_executor(None, lambda: _extract(webpage_url, opts))
    except Exception as e:
        print(f"[yt-dlp] resolve error: {e}")
        return None, None
    if not info:
        return None, None
    return info.get("url"), info.get("title")
