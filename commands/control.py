"""Cog de control de reproducción (Sprint 12)."""

import discord
from discord import app_commands
from discord.ext import commands

from core import voice as voice_mgr
from core.guards import require_dj, require_voice
from music.queue import drop_first


class Control(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="skip", description="Salta la canción actual (opcional: varias).")
    @app_commands.describe(cantidad="Cuántas canciones saltar (default 1)")
    @require_voice
    @require_dj
    async def skip(self, interaction: discord.Interaction, cantidad: int = 1):
        await interaction.response.defer(ephemeral=True)

        vc = interaction.guild.voice_client
        if not (vc.is_playing() or vc.is_paused()):
            return await interaction.followup.send("No hay nada reproduciéndose.")

        cantidad = max(1, cantidad)
        async with voice_mgr.get_lock(str(interaction.guild_id)):
            # La actual la corta vc.stop(); además se descartan cantidad-1 en cola.
            drop_first(str(interaction.guild_id), cantidad - 1)
            vc.stop()
        msg = "⏭️ Canción omitida." if cantidad == 1 else f"⏭️ {cantidad} canciones omitidas."
        await interaction.followup.send(msg)

    @app_commands.command(name="pause", description="Pausa la canción que se está reproduciendo.")
    @require_voice
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client.is_playing():
            return await interaction.response.send_message(
                "Cri cri, no estoy reproduciendo nada ahora mismo."
            )
        voice_client.pause()
        await interaction.response.send_message("⏸️ Reproducción pausada!")

    @app_commands.command(name="resume", description="Reanuda la canción que se ha pausado.")
    @require_voice
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client.is_paused():
            return await interaction.response.send_message("Cri cri, no estoy pausado ahora mismo.")
        voice_client.resume()
        await interaction.response.send_message("▶️ Reproducción reanudada!")

    @app_commands.command(name="stop", description="Detiene la reproducción y limpia la cola.")
    @require_voice
    @require_dj
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        msg = await interaction.followup.send("⛔ Deteniendo reproducción...")
        vc = interaction.guild.voice_client
        await voice_mgr.stop_playback(str(interaction.guild_id), vc, clear=True)
        await msg.edit(content="⛔ Reproducción detenida.")

    @app_commands.command(
        name="disconnect", description="Desconecta al bot del canal de voz (conserva la cola)."
    )
    @require_voice
    @require_dj
    async def disconnect(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = interaction.guild.voice_client
        await voice_mgr.stop_playback(str(interaction.guild_id), vc, clear=False)
        await interaction.followup.send("👋 Desconectado. La cola se conserva.")
