"""Embeds y paginación (Sprint 4, B-02/B-03). Sin lógica de voz: solo formato."""

import discord

QUEUE_PER_PAGE = 10


def format_duration(seconds) -> str:
    if seconds is None:
        return "—"
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return "—"
    m, s = divmod(max(0, total), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def track_line(track: dict) -> str:
    title = track.get("title") or "Untitled"
    url = track.get("webpage_url")
    label = f"[{title}]({url})" if url else f"**{title}**"
    dur = format_duration(track.get("duration"))
    by = track.get("requested_by")
    suffix = f" · 🙋 {by}" if by else ""
    return f"🎵 {label} `⏱ {dur}`{suffix}"


def now_playing_embed(track: dict) -> discord.Embed:
    title = track.get("title") or "Untitled"
    url = track.get("webpage_url")
    desc = f"🎵 [{title}]({url})" if url else f"🎵 **{title}**"
    uploader = track.get("uploader")
    if uploader:
        desc += f"\n👤 {uploader}"
    desc += f"\n⏱ {format_duration(track.get('duration'))}"
    by = track.get("requested_by")
    if by:
        desc += f"\n🙋 Pedida por {by}"
    embed = discord.Embed(title="🎧 Now Playing", description=desc, color=discord.Color.green())
    thumb = track.get("thumbnail")
    if thumb:
        embed.set_thumbnail(url=thumb)
    return embed


def queue_pages(tracks: list) -> list:
    """Parte la cola en páginas de QUEUE_PER_PAGE; siempre ≥1 página."""
    return [tracks[i : i + QUEUE_PER_PAGE] for i in range(0, len(tracks), QUEUE_PER_PAGE)] or [[]]


def queue_page_embed(
    page_tracks: list, page: int, total_pages: int, total: int, offset: int
) -> discord.Embed:
    lines = [f"{offset + i}. {track_line(t)}" for i, t in enumerate(page_tracks, start=1)]
    desc = "\n".join(lines) if lines else "🎵 Cola vacía."
    embed = discord.Embed(title="🎶 Cola actual", description=desc, color=discord.Color.blurple())
    embed.set_footer(text=f"Página {page}/{total_pages} · {total} en cola")
    return embed
