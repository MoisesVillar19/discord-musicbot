"""Única capa que toca voz/FFmpeg (Sprint 2, ADR-003).

Toda mutación de voz/cola pasa por el lock del guild (A-05) y por una vía
única de apagado con guard de generación (A-08): un after_play viejo nunca
resucita la reproducción tras un /stop o /disconnect.
"""

import asyncio
import os
import shutil

import discord

from config import FFMPEG_PATH
from music.queue import clear_queue, get_queue, record_history
from utils.errors import NotConnectedError, WrongChannelError
from utils.logger import log

GUILD_LOCKS: dict = {}
NOW_PLAYING: dict = {}
_PLAY_GEN: dict = {}
_EMPTY_TASKS: dict = {}
LAST_TEXT: dict = {}

EMPTY_TIMEOUT = 120  # segundos solo antes de irse si el canal queda vacío


def get_lock(guild_id: str) -> asyncio.Lock:
    if guild_id not in GUILD_LOCKS:
        GUILD_LOCKS[guild_id] = asyncio.Lock()
    return GUILD_LOCKS[guild_id]


def _next_gen(guild_id: str) -> int:
    _PLAY_GEN[guild_id] = _PLAY_GEN.get(guild_id, 0) + 1
    return _PLAY_GEN[guild_id]


def _ffmpeg_executable():
    """Binario local si existe; si no, el del PATH (None = PATH)."""
    candidate = os.path.normpath(FFMPEG_PATH) if FFMPEG_PATH else ""
    if candidate and os.path.isfile(candidate):
        return candidate
    return None


def ffmpeg_available() -> bool:
    return _ffmpeg_executable() is not None or shutil.which("ffmpeg") is not None


def check_same_voice(voice_client, user_voice) -> None:
    """Valida control en el mismo canal. Lanza NotConnectedError/WrongChannelError."""
    if voice_client is None or not voice_client.is_connected():
        raise NotConnectedError()
    user_channel = getattr(user_voice, "channel", None) if user_voice else None
    if user_channel is None or user_channel != voice_client.channel:
        raise WrongChannelError()


async def ensure_voice(interaction) -> object:
    """Conecta (self-deaf) o mueve al bot al canal del usuario. Asume usuario en voz."""
    voice_channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    async with get_lock(str(interaction.guild_id)):
        if vc is None:
            vc = await voice_channel.connect(self_deaf=True)
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)
    return vc


async def _finish(guild_id: str, voice_client) -> None:
    """Apagado por fin de cola: desconecta y limpia estado (con lock)."""
    async with get_lock(guild_id):
        _next_gen(guild_id)
        NOW_PLAYING.pop(guild_id, None)
        LAST_TEXT.pop(guild_id, None)
        clear_queue(guild_id)
        try:
            if voice_client.is_connected():
                await voice_client.disconnect()
        except Exception as e:
            log.warning("disconnect error: %s", e)


async def stop_playback(guild_id: str, voice_client, clear: bool = True) -> None:
    """Vía única de apagado manual (/stop con clear, /disconnect sin clear)."""
    async with get_lock(guild_id):
        _next_gen(guild_id)
        NOW_PLAYING.pop(guild_id, None)
        if clear:
            clear_queue(guild_id)
            LAST_TEXT.pop(guild_id, None)
        try:
            if voice_client.is_playing() or voice_client.is_paused():
                voice_client.stop()
            if voice_client.is_connected():
                await voice_client.disconnect(force=True)
        except Exception as e:
            log.warning("stop error: %s", e)


async def play_next_song(voice_client, guild_id: str, channel, bot_loop) -> None:
    from music.search import resolve_stream_url

    queue = get_queue(guild_id)
    async with get_lock(guild_id):
        track = queue.popleft() if queue else None
    if track is None:
        await _finish(guild_id, voice_client)
        return
    audio_url = track.get("url")
    title = track.get("title") or "Untitled"
    webpage_url = track.get("webpage_url")
    LAST_TEXT[guild_id] = channel

    if not audio_url and webpage_url:
        audio_url, resolved = await resolve_stream_url(webpage_url)
        if resolved:
            title = resolved
            track["title"] = resolved

    if not audio_url:
        log.warning("Sin URL reproducible para '%s', saltando...", title)
        try:
            await channel.send(f"⚠️ Salté **{title}** (no disponible).")
        except Exception:
            pass
        if queue:
            await play_next_song(voice_client, guild_id, channel, bot_loop)
        else:
            await _finish(guild_id, voice_client)
        return

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn -c:a libopus -b:a 96k",
    }
    executable = _ffmpeg_executable()
    if executable:
        ffmpeg_options["executable"] = executable

    try:
        source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options)
    except Exception as e:
        log.warning("FFmpeg error con '%s': %s", title, e)
        if queue:
            await play_next_song(voice_client, guild_id, channel, bot_loop)
        else:
            await _finish(guild_id, voice_client)
        return

    gen = _PLAY_GEN.get(guild_id, 0)

    def after_play(error):
        if error:
            log.warning("Error playing %s: %s", title, error)
        if _PLAY_GEN.get(guild_id, 0) != gen:
            log.info("after_play obsoleto ignorado (gen %s)", gen)
            return
        try:
            coro = play_next_song(voice_client, guild_id, channel, bot_loop)
            asyncio.run_coroutine_threadsafe(coro, bot_loop)
        except RuntimeError as e:
            log.warning("after_play error: %s", e)

    NOW_PLAYING[guild_id] = track
    record_history(guild_id, track)
    voice_client.play(source, after=after_play)
    from ui.embeds import now_playing_embed

    asyncio.create_task(channel.send(embed=now_playing_embed(track)))


def _humans_in(channel, bot_user) -> int:
    return sum(1 for m in getattr(channel, "members", []) if not getattr(m, "bot", False))


async def _empty_watch(bot, guild_id: str) -> None:
    try:
        await asyncio.sleep(EMPTY_TIMEOUT)
        guild = bot.get_guild(int(guild_id)) if guild_id.isdigit() else None
        vc = guild.voice_client if guild else None
        if vc and vc.is_connected() and _humans_in(vc.channel, bot.user) == 0:
            log.info("Canal vacío %ss, desconectando (guild %s)", EMPTY_TIMEOUT, guild_id)
            channel = LAST_TEXT.get(guild_id)
            await stop_playback(guild_id, vc, clear=True)
            if channel is not None:
                try:
                    await channel.send("👋 Me fui porque el canal quedó vacío.")
                except Exception:
                    pass
    except asyncio.CancelledError:
        pass
    finally:
        _EMPTY_TASKS.pop(guild_id, None)


async def handle_voice_state_update(bot, member, before, after) -> None:
    """Autolimpieza y autodisconnect por canal vacío (A-09)."""
    # El propio bot desconectado: limpiar estado sin borrar cola (permite retomar).
    if member == bot.user and before.channel is not None and after.channel is None:
        guild_id = str(member.guild.id)
        task = _EMPTY_TASKS.pop(guild_id, None)
        if task:
            task.cancel()
        _next_gen(guild_id)
        NOW_PLAYING.pop(guild_id, None)
        return

    # Humano sale/entra: reevaluar si el bot quedó solo.
    guild = getattr(member, "guild", None)
    if guild is None:
        return
    vc = guild.voice_client
    if vc is None or not vc.is_connected():
        return
    guild_id = str(guild.id)
    if _humans_in(vc.channel, bot.user) == 0:
        if guild_id not in _EMPTY_TASKS:
            _EMPTY_TASKS[guild_id] = asyncio.create_task(_empty_watch(bot, guild_id))
    else:
        task = _EMPTY_TASKS.pop(guild_id, None)
        if task:
            task.cancel()
