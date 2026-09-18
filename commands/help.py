"""Cog /help con alters activos (Sprint 12)."""

import discord
from discord import app_commands
from discord.ext import commands

from config import BOT_NAME
from core.aliases import get_aliases


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Ver comandos del bot")
    async def help(self, interaction: discord.Interaction):
        lines = [
            f"🎧 **Comandos de {BOT_NAME}**",
            "",
            "▶ /play <canción> — Reproduce o agrega a la cola",
            "⏸ /pause — Pausa la música",
            "▶ /resume — Reanuda",
            "⏭ /skip [n] — Salta n canciones · 🔜 /next — Ver cuál sigue",
            "🎶 /queue — Ver cola · 🎧 /nowplaying — Actual",
            "🔀 /shuffle · 🗑️ /remove · ↔️ /move · 🧹 /clear — Cola",
            "⛔ /stop — Detiene todo · 👋 /disconnect — Salir",
            "🎭 /troll — Menú troll · 📜 /history — Historial + replay",
            "🎤 /lyrics — Letra de lo que suena",
        ]
        active = [(c, a) for c, a in get_aliases().items() if a]
        if active:
            lines.append("")
            lines.append("🎭 **Alters:**")
            for canonical, alters in active:
                lines.append(f"· /{canonical}: " + ", ".join(f"/{a}" for a in alters))
        lines += ["", "🔥 ¡Disfruta la música!"]
        await interaction.response.send_message("\n".join(lines))
