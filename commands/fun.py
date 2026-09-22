"""Cog de diversión y letras (Sprint 12)."""

import discord
from discord import app_commands
from discord.ext import commands

from core import voice as voice_mgr
from music.queue import enqueue_tracks
from music.search import search_many, search_ytdlp
from music.trolls import ensure_trolls
from services.lyrics_service import get_lyrics, lyric_pages
from ui.views import EnqueueSelectView, PagerView
from utils.errors import MusicBotError, user_message


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="troll", description="Menú de canciones troll.")
    async def troll(self, interaction: discord.Interaction):
        troll_list = ensure_trolls()
        if not troll_list:
            return await interaction.response.send_message(
                "🎭 No hay trolls configurados (trolls.json).", ephemeral=True
            )

        async def on_pick(sel: discord.Interaction, index: int, troll: dict):
            await sel.response.defer(ephemeral=True)
            if interaction.user.voice is None:
                return await sel.edit_original_response(
                    content="🎧 Debes estar en un canal de voz."
                )
            tracks, _, _ = await search_ytdlp(troll["url"], 1, 0)
            if not tracks:
                return await sel.edit_original_response(content="❌ No se pudo resolver el troll.")
            try:
                vc = await voice_mgr.ensure_voice(interaction)
            except MusicBotError as e:
                return await sel.edit_original_response(content=user_message(e))
            enqueue_tracks(str(interaction.guild_id), interaction.user.display_name, tracks)
            await sel.edit_original_response(
                content=f"🎭 Troleo en camino: **{tracks[0].get('title')}**"
            )
            await voice_mgr.maybe_start_playback(
                str(interaction.guild_id), vc, interaction.channel, self.bot.loop
            )

        entries = [(t["name"], "", t) for t in troll_list]
        view = EnqueueSelectView(
            options=entries,
            requester_id=interaction.user.id,
            on_pick=on_pick,
            placeholder="🎭 Elige tu víctima…",
        )
        await interaction.response.send_message("🎭 **Menú troll:**", view=view, ephemeral=True)

    @app_commands.command(name="lyrics", description="Letra de lo que suena o de una búsqueda.")
    @app_commands.describe(consulta="Vacío = actual. O nombre de canción.")
    async def lyrics(self, interaction: discord.Interaction, consulta: str | None = None):
        await interaction.response.defer(ephemeral=True)
        if consulta:
            options = await search_many(consulta, n=1)
            if not options:
                return await interaction.followup.send("❌ Sin resultados.")
            title = options[0].get("title") or consulta
            artist = options[0].get("uploader")
        else:
            track = voice_mgr.NOW_PLAYING.get(str(interaction.guild_id))
            if not track:
                return await interaction.followup.send("🔇 No hay nada reproduciéndose.")
            title = track.get("title") or ""
            artist = track.get("uploader")

        text = await get_lyrics(title, artist)
        if not text:
            return await interaction.followup.send(f"❌ Sin letra disponible para **{title}**.")

        pages = lyric_pages(text)

        def render(page: int):
            embed = discord.Embed(
                title=f"🎤 {title}", description=pages[page - 1], color=discord.Color.purple()
            )
            embed.set_footer(text=f"Página {page}/{len(pages)}")
            return embed

        view = PagerView(total_pages=len(pages), render=render)
        await interaction.followup.send(embed=render(1), view=view)
