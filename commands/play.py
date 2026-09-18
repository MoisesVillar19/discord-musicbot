"""Cog /play (Sprint 12)."""

import discord
from discord import app_commands
from discord.ext import commands

from config import TROLL_CHANCE
from core import voice as voice_mgr
from music.queue import enqueue_tracks
from music.search import search_many, search_ytdlp
from music.trolls import ensure_trolls, match_keyword, roll_ambush
from ui.embeds import format_duration, track_line
from ui.views import EnqueueSelectView
from utils.validators import TEXT, UNSUPPORTED_URL, classify, unsupported_message


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="play", description="Reproduce una canción o playlist.")
    @app_commands.describe(
        song_query="Nombre o URL",
        start="Desde qué canción empezar (playlist)",
        limit="Cantidad máxima a agregar",
    )
    async def play(
        self, interaction: discord.Interaction, song_query: str, start: int = 1, limit: int = 100
    ):
        await interaction.response.defer()

        if interaction.user.voice is None:
            await interaction.followup.send("🎧 Debes estar en un canal de voz.")
            return

        # 🔒 Seguridad
        start = max(1, start)
        limit = min(max(1, limit), 100)
        start_index = start - 1

        # Validar antes de conectarse: URLs no-YouTube se rechazan sin entrar a voz.
        if classify(song_query) == UNSUPPORTED_URL:
            await interaction.followup.send(unsupported_message(), ephemeral=True)
            return

        # Texto libre -> keyword troll, emboscada o menú. Sin entrar a voz aún.
        if classify(song_query) == TEXT:
            troll_list = ensure_trolls()
            forced = match_keyword(song_query, troll_list)
            ambush = None if forced else roll_ambush(TROLL_CHANCE, troll_list)
            troll = forced or ambush
            if troll is not None:
                vc = await voice_mgr.ensure_voice(interaction)
                tracks, _, _ = await search_ytdlp(troll["url"], 1, 0)
                if not tracks:
                    await interaction.followup.send("❌ No se encontraron resultados.")
                    return
                enqueue_tracks(str(interaction.guild_id), interaction.user.display_name, tracks)
                note = (
                    f"🎭 ¡TROLEADO! Pediste **{song_query}** y suena **{tracks[0].get('title')}**."
                    if ambush
                    else f"🎭 **{tracks[0].get('title')}** (pedido por keyword)."
                )
                await interaction.followup.send(note)
                await voice_mgr.maybe_start_playback(
                    str(interaction.guild_id), vc, interaction.channel, self.bot.loop
                )
                return

            options = await search_many(song_query, n=5)
            if not options:
                await interaction.followup.send("❌ No se encontraron resultados.")
                return

            async def on_pick(sel: discord.Interaction, index: int, track: dict):
                if interaction.user.voice is None:
                    return await sel.response.send_message(
                        "🎧 Debes estar en un canal de voz.", ephemeral=True
                    )
                vc2 = await voice_mgr.ensure_voice(interaction)
                enqueue_tracks(str(interaction.guild_id), interaction.user.display_name, [track])
                await sel.response.edit_message(
                    content=f"🎵 Agregada: **{track.get('title')}**", view=None
                )
                await voice_mgr.maybe_start_playback(
                    str(interaction.guild_id), vc2, interaction.channel, self.bot.loop
                )

            entries = [
                (
                    t.get("title", "Untitled"),
                    f"{t.get('uploader') or 'YouTube'} · {format_duration(t.get('duration'))}",
                    t,
                )
                for t in options
            ]
            view = EnqueueSelectView(
                options=entries,
                requester_id=interaction.user.id,
                on_pick=on_pick,
                placeholder="🔎 Elige tu canción…",
                on_timeout_edit=(
                    interaction,
                    "⌛ Menú expirado. Usa /play de nuevo.",
                ),
            )
            lines = [f"{i}. {track_line(t)}" for i, t in enumerate(options, start=1)]
            await interaction.followup.send(
                "🔎 **Resultados para:** " + song_query + "\n" + "\n".join(lines),
                view=view,
                ephemeral=True,
            )
            return

        vc = await voice_mgr.ensure_voice(interaction)
        tracks, total, unavailable = await search_ytdlp(song_query, limit, start_index)

        if not tracks:
            await interaction.followup.send("❌ No se encontraron resultados.")
            return

        enqueue_tracks(str(interaction.guild_id), interaction.user.display_name, tracks)

        # 🎁 Mensaje bonus
        if total > 1:
            msg = f"📂 **Playlist detectada**\n➕ Agregadas **{len(tracks)}** canciones\n"
            if unavailable > 0:
                msg += f"⚠️ **{unavailable}** no disponibles\n"
            msg += f"📌 Desde la **#{start}** de **{total}**"
        else:
            msg = f"🎵 Agregada: **{tracks[0]['title']}**"

        await interaction.followup.send(msg)
        await voice_mgr.maybe_start_playback(
            str(interaction.guild_id), vc, interaction.channel, self.bot.loop
        )
