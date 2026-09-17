# Importing libraries and modules
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from config import TOKEN, FFMPEG_PATH, YTDLP_OPTIONS, BOT_NAME, GUILD_ID
from music.queue import get_queue, clear_queue, peek_queue, shuffle_queue, remove_track, move_track
from utils.errors import MusicBotError, user_message
from utils.logger import log
from core import voice as voice_mgr

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN no encontrado. Crea un archivo .env con DISCORD_TOKEN=tu_token "
        "(ver .env.example)."
    )


# Setup of intents. Intents are permissions the bot has on the server
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot ready-up code
@bot.event
async def on_ready():
    if GUILD_ID:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        log.info("%s is online! (sync servidor %s)", bot.user, GUILD_ID)
    else:
        await bot.tree.sync()
        log.info("%s is online! (sync global)", bot.user)
    if not voice_mgr.ffmpeg_available():
        log.warning("FFmpeg no encontrado (ni %s ni PATH). No sonará nada.", FFMPEG_PATH)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    original = getattr(error, "original", error)
    log.exception("Error en /%s: %s", getattr(interaction.command, "name", "?"), original)
    try:
        msg = user_message(original)
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


@bot.event
async def on_voice_state_update(member, before, after):
    await voice_mgr.handle_voice_state_update(bot, member, before, after)


@bot.tree.command(name="skip")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
    except MusicBotError as e:
        return await interaction.followup.send(user_message(e))

    vc = interaction.guild.voice_client
    if not (vc.is_playing() or vc.is_paused()):
        return await interaction.followup.send("No hay nada reproduciéndose.")

    async with voice_mgr.get_lock(str(interaction.guild_id)):
        vc.stop()
    await interaction.followup.send("⏭️ Canción omitida.")



@bot.tree.command(name="pause", description="Pausa la canción que se está reproduciendo actualmente.")
async def pause(interaction: discord.Interaction):
    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
    except MusicBotError as e:
        return await interaction.response.send_message(user_message(e), ephemeral=True)

    voice_client = interaction.guild.voice_client

    # Check if something is actually playing
    if not voice_client.is_playing():
        return await interaction.response.send_message("Cri cri, no estoy reproduciendo nada ahora mismo.")
    
    # Pause the track
    voice_client.pause()
    await interaction.response.send_message("⏸️ Reproducción pausada!")


@bot.tree.command(name="resume", description="Reanuda la canción que se ha pausado.")
async def resume(interaction: discord.Interaction):
    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
    except MusicBotError as e:
        return await interaction.response.send_message(user_message(e), ephemeral=True)

    voice_client = interaction.guild.voice_client

    # Check if it's actually paused
    if not voice_client.is_paused():
        return await interaction.response.send_message("Cri cri, no estoy pausado ahora mismo.")
    
    # Resume playback
    voice_client.resume()
    await interaction.response.send_message("▶️ Reproducción reanudada!")


@bot.tree.command(name="stop", description="Detiene la reproducción y limpia la cola.")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
    except MusicBotError as e:
        return await interaction.followup.send(user_message(e))

    msg = await interaction.followup.send("⛔ Deteniendo reproducción...")

    vc = interaction.guild.voice_client
    await voice_mgr.stop_playback(str(interaction.guild_id), vc, clear=True)

    await msg.edit(content="⛔ Reproducción detenida.")


@bot.tree.command(name="disconnect", description="Desconecta al bot del canal de voz (conserva la cola).")
async def disconnect(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
    except MusicBotError as e:
        return await interaction.followup.send(user_message(e))

    vc = interaction.guild.voice_client
    await voice_mgr.stop_playback(str(interaction.guild_id), vc, clear=False)

    await interaction.followup.send("👋 Desconectado. La cola se conserva.")


@bot.tree.command(name="play", description="Reproduce una canción o playlist.")
@app_commands.describe(
    song_query="Nombre o URL",
    start="Desde qué canción empezar (playlist)",
    limit="Cantidad máxima a agregar"
)
async def play(
    interaction: discord.Interaction,
    song_query: str,
    start: int = 1,
    limit: int = 100
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
    from utils.validators import UNSUPPORTED_URL, classify, unsupported_message

    if classify(song_query) == UNSUPPORTED_URL:
        await interaction.followup.send(unsupported_message(), ephemeral=True)
        return

    vc = await voice_mgr.ensure_voice(interaction)

    from music.search import search_ytdlp

    tracks, total, unavailable = await search_ytdlp(song_query, limit, start_index)


    if not tracks:
        await interaction.followup.send("❌ No se encontraron resultados.")
        return

    queue = get_queue(str(interaction.guild_id))

    requested_by = interaction.user.display_name
    for t in tracks:
        t["requested_by"] = requested_by
        queue.append(t)

    # 🎁 Mensaje bonus
    if total > 1:
        msg = (
        "📂 **Playlist detectada**\n"
        f"➕ Agregadas **{len(tracks)}** canciones\n"
         )

        if unavailable > 0:
            msg += f"⚠️ **{unavailable}** no disponibles\n"

        msg += f"📌 Desde la **#{start}** de **{total}**"
    else:
        msg = f"🎵 Agregada: **{tracks[0]['title']}**"

    await interaction.followup.send(msg)

    guild_id = str(interaction.guild_id)
    async with voice_mgr.get_lock(guild_id):
        start_now = not vc.is_playing() and not vc.is_paused()
    if start_now:
        await voice_mgr.play_next_song(vc, guild_id, interaction.channel, bot.loop)



@bot.tree.command(name="help", description="Ver comandos del bot")
async def help(interaction: discord.Interaction):
    lines = [
        f"🎧 **Comandos de {BOT_NAME}**",
        "",
        "▶ /play <canción> — Reproduce o agrega a la cola",
        "⏸ /pause — Pausa la música",
        "▶ /resume — Reanuda",
        "⏭ /skip — Salta canción",
        "🎶 /queue — Ver cola · 🎧 /nowplaying — Actual",
        "🔀 /shuffle · 🗑️ /remove · ↔️ /move · 🧹 /clear — Cola",
        "⛔ /stop — Detiene todo · 👋 /disconnect — Salir",
    ]
    active = [(c, a) for c, a in ALIASES.items() if a]
    if active:
        lines.append("")
        lines.append("🎭 **Alters:**")
        for canonical, alters in active:
            lines.append(f"· /{canonical}: " + ", ".join(f"/{a}" for a in alters))
    lines += ["", "🔥 ¡Disfruta la música!"]
    await interaction.response.send_message("\n".join(lines))
@bot.tree.command(name="queue", description="Muestra la cola de canciones actuales.")
async def queue(interaction: discord.Interaction):
    from ui.embeds import QUEUE_PER_PAGE, queue_page_embed, queue_pages

    tracks = peek_queue(str(interaction.guild_id))
    pages = queue_pages(tracks)

    class QueueView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.page = 1

        def _render(self):
            total_pages = len(pages)
            offset = (self.page - 1) * QUEUE_PER_PAGE
            return queue_page_embed(pages[self.page - 1], self.page,
                                    total_pages, len(tracks), offset)

        def _sync_buttons(self):
            self.prev_btn.disabled = self.page <= 1
            self.next_btn.disabled = self.page >= len(pages)

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def prev_btn(self, btn_interaction: discord.Interaction, button):
            self.page = max(1, self.page - 1)
            self._sync_buttons()
            await btn_interaction.response.edit_message(embed=self._render(), view=self)

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next_btn(self, btn_interaction: discord.Interaction, button):
            self.page = min(len(pages), self.page + 1)
            self._sync_buttons()
            await btn_interaction.response.edit_message(embed=self._render(), view=self)

    view = QueueView()
    view._sync_buttons()
    await interaction.response.send_message(embed=view._render(), view=view, ephemeral=True)


@bot.tree.command(name="nowplaying", description="Muestra la canción que está sonando.")
async def nowplaying(interaction: discord.Interaction):
    from ui.embeds import now_playing_embed

    track = voice_mgr.NOW_PLAYING.get(str(interaction.guild_id))
    if not track:
        return await interaction.response.send_message(
            "🔇 No hay nada reproduciéndose.", ephemeral=True)
    await interaction.response.send_message(embed=now_playing_embed(track), ephemeral=True)


def _need_voice(interaction):
    """Valida acceso a la cola; devuelve mensaje de error o None."""
    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
        return None
    except MusicBotError as e:
        return user_message(e)


@bot.tree.command(name="shuffle", description="Mezcla la cola.")
async def shuffle(interaction: discord.Interaction):
    err = _need_voice(interaction)
    if err:
        return await interaction.response.send_message(err, ephemeral=True)
    if shuffle_queue(str(interaction.guild_id)):
        await interaction.response.send_message("🔀 Cola mezclada.", ephemeral=True)
    else:
        await interaction.response.send_message("🎵 Nada que mezclar (menos de 2).", ephemeral=True)


@bot.tree.command(name="remove", description="Elimina una canción de la cola por su número.")
@app_commands.describe(posicion="Número de la canción en /queue (empieza en 1)")
async def remove(interaction: discord.Interaction, posicion: int):
    err = _need_voice(interaction)
    if err:
        return await interaction.response.send_message(err, ephemeral=True)
    track = remove_track(str(interaction.guild_id), posicion)
    if track is None:
        return await interaction.response.send_message(
            "❌ Posición inválida. Revisa /queue.", ephemeral=True)
    await interaction.response.send_message(
        f"🗑️ Eliminada: **{track.get('title', 'Untitled')}**", ephemeral=True)


@bot.tree.command(name="clear", description="Vacía la cola (sigue sonando la actual).")
async def clear(interaction: discord.Interaction):
    err = _need_voice(interaction)
    if err:
        return await interaction.response.send_message(err, ephemeral=True)
    clear_queue(str(interaction.guild_id))
    await interaction.response.send_message("🧹 Cola vaciada.", ephemeral=True)


@bot.tree.command(name="move", description="Mueve una canción a otra posición de la cola.")
@app_commands.describe(origen="Posición actual", destino="Posición destino")
async def move(interaction: discord.Interaction, origen: int, destino: int):
    err = _need_voice(interaction)
    if err:
        return await interaction.response.send_message(err, ephemeral=True)
    if move_track(str(interaction.guild_id), origen, destino):
        await interaction.response.send_message(
            f"↔️ Movida #{origen} → #{destino}.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "❌ Posiciones inválidas. Revisa /queue.", ephemeral=True)


# --- Alters configurables (Sprint 5, D-03) ---
# Cada alter es un slash command propio que reutiliza el callback del canónico.
from core.aliases import AliasError, load_aliases

try:
    ALIASES = load_aliases()
except AliasError as e:
    raise RuntimeError(f"Revisa aliases.json: {e}")

for _canonical, _alters in ALIASES.items():
    _base = bot.tree.get_command(_canonical)
    if _base is None:
        continue
    for _alt in _alters:
        if bot.tree.get_command(_alt) is not None:
            continue
        bot.tree.command(
            name=_alt,
            description=f"{_base.description} (alias de /{_canonical})",
        )(_base.callback)
        log.info("Alter registrado: /%s -> /%s", _alt, _canonical)


# Run the bot
bot.run(TOKEN)