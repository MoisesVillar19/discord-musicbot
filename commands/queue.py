"""Cog de cola e historial (Sprint 12)."""

import discord
from discord import app_commands
from discord.ext import commands

from core import voice as voice_mgr
from core.guards import require_dj, require_voice
from music.queue import (
    clear_queue,
    get_history,
    move_track,
    peek_queue,
    remove_track,
    shuffle_queue,
)
from ui.embeds import QUEUE_PER_PAGE, now_playing_embed, queue_page_embed, queue_pages, track_line
from ui.views import EnqueueSelectView, PagerView


class Queue(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="queue", description="Muestra la cola de canciones actuales.")
    async def queue(self, interaction: discord.Interaction):
        tracks = peek_queue(str(interaction.guild_id))
        pages = queue_pages(tracks)

        def render(page: int):
            offset = (page - 1) * QUEUE_PER_PAGE
            return queue_page_embed(pages[page - 1], page, len(pages), len(tracks), offset)

        view = PagerView(total_pages=len(pages), render=render)
        await interaction.response.send_message(embed=render(1), view=view, ephemeral=True)

    @app_commands.command(name="nowplaying", description="Muestra la canción que está sonando.")
    async def nowplaying(self, interaction: discord.Interaction):
        track = voice_mgr.NOW_PLAYING.get(str(interaction.guild_id))
        if not track:
            return await interaction.response.send_message(
                "🔇 No hay nada reproduciéndose.", ephemeral=True
            )
        await interaction.response.send_message(embed=now_playing_embed(track), ephemeral=True)

    @app_commands.command(name="next", description="Muestra cuál suena después, sin saltar nada.")
    async def next_song(self, interaction: discord.Interaction):
        tracks = peek_queue(str(interaction.guild_id))
        if not tracks:
            return await interaction.response.send_message(
                "🔇 No hay siguiente: se acaba la cola.", ephemeral=True
            )
        await interaction.response.send_message(
            f"⏭ **Siguiente:**\n1. {track_line(tracks[0])}", ephemeral=True
        )

    @app_commands.command(name="shuffle", description="Mezcla la cola.")
    @require_voice
    @require_dj
    async def shuffle(self, interaction: discord.Interaction):
        if shuffle_queue(str(interaction.guild_id)):
            await interaction.response.send_message("🔀 Cola mezclada.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "🎵 Nada que mezclar (menos de 2).", ephemeral=True
            )

    @app_commands.command(
        name="remove", description="Elimina una canción de la cola por su número."
    )
    @app_commands.describe(posicion="Número de la canción en /queue (empieza en 1)")
    @require_voice
    @require_dj
    async def remove(self, interaction: discord.Interaction, posicion: int):
        track = remove_track(str(interaction.guild_id), posicion)
        if track is None:
            return await interaction.response.send_message(
                "❌ Posición inválida. Revisa /queue.", ephemeral=True
            )
        await interaction.response.send_message(
            f"🗑️ Eliminada: **{track.get('title', 'Untitled')}**", ephemeral=True
        )

    @app_commands.command(name="clear", description="Vacía la cola (sigue sonando la actual).")
    @require_voice
    @require_dj
    async def clear(self, interaction: discord.Interaction):
        clear_queue(str(interaction.guild_id))
        await interaction.response.send_message("🧹 Cola vaciada.", ephemeral=True)

    @app_commands.command(name="move", description="Mueve una canción a otra posición de la cola.")
    @app_commands.describe(origen="Posición actual", destino="Posición destino")
    @require_voice
    @require_dj
    async def move(self, interaction: discord.Interaction, origen: int, destino: int):
        if move_track(str(interaction.guild_id), origen, destino):
            await interaction.response.send_message(
                f"↔️ Movida #{origen} → #{destino}.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Posiciones inválidas. Revisa /queue.", ephemeral=True
            )

    @app_commands.command(name="history", description="Últimas canciones + re-encolar.")
    async def history(self, interaction: discord.Interaction):
        hist = get_history(str(interaction.guild_id))
        if not hist:
            return await interaction.response.send_message("📜 Historial vacío.", ephemeral=True)

        async def on_pick(sel: discord.Interaction, index: int, track: dict):
            if interaction.user.voice is None:
                return await sel.response.send_message(
                    "🎧 Debes estar en un canal de voz.", ephemeral=True
                )
            fresh = dict(track)
            fresh["url"] = None  # forzar resolución fresca al sonar
            vc = await voice_mgr.ensure_voice(interaction)
            from music.queue import enqueue_tracks

            enqueue_tracks(str(interaction.guild_id), interaction.user.display_name, [fresh])
            await sel.response.edit_message(
                content=f"🎵 Re-encolada: **{fresh.get('title')}**", view=None
            )
            await voice_mgr.maybe_start_playback(
                str(interaction.guild_id), vc, interaction.channel, self.bot.loop
            )

        entries = [(t.get("title", "Untitled"), "", t) for t in hist]
        view = EnqueueSelectView(
            options=entries,
            requester_id=interaction.user.id,
            on_pick=on_pick,
            placeholder="📜 Re-encolar…",
        )
        lines = [f"{i}. {track_line(t)}" for i, t in enumerate(hist, start=1)]
        await interaction.response.send_message(
            "📜 **Historial:**\n" + "\n".join(lines), view=view, ephemeral=True
        )
