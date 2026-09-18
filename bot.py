# Importing libraries and modules
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from config import TOKEN, FFMPEG_PATH, YTDLP_OPTIONS, BOT_NAME, GUILD_ID, TROLL_CHANCE
from music.queue import get_queue, clear_queue, peek_queue, shuffle_queue, remove_track, move_track, drop_first
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


@bot.tree.command(name="skip", description="Salta la canción actual (opcional: varias).")
@app_commands.describe(cantidad="Cuántas canciones saltar (default 1)")
async def skip(interaction: discord.Interaction, cantidad: int = 1):
    await interaction.response.defer(ephemeral=True)

    try:
        voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
    except MusicBotError as e:
        return await interaction.followup.send(user_message(e))

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


@bot.tree.command(name="next", description="Muestra cuál suena después, sin saltar nada.")
async def next_song(interaction: discord.Interaction):
    from ui.embeds import track_line

    tracks = peek_queue(str(interaction.guild_id))
    if not tracks:
        return await interaction.response.send_message(
            "🔇 No hay siguiente: se acaba la cola.", ephemeral=True)
    await interaction.response.send_message(
        f"⏭ **Siguiente:**\n1. {track_line(tracks[0])}", ephemeral=True)



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
    from utils.validators import TEXT, UNSUPPORTED_URL, classify, unsupported_message

    if classify(song_query) == UNSUPPORTED_URL:
        await interaction.followup.send(unsupported_message(), ephemeral=True)
        return

    vc = None  # se conecta abajo (URL) o al elegir (menú texto)

    from music.search import search_many, search_ytdlp
    from utils.validators import TEXT
    from ui.embeds import format_duration, track_line

    # Texto libre -> keyword troll, emboscada o menú (S7 + S8). Sin entrar a voz aún.
    if classify(song_query) == TEXT:
        from music.trolls import ensure_trolls, match_keyword, roll_ambush

        troll_list = ensure_trolls()
        # 1) Keyword exacta: el troll pedido a propósito
        forced = match_keyword(song_query, troll_list)
        # 2) Emboscada: pediste X con ratio bajo y suena un meme
        ambush = None if forced else roll_ambush(TROLL_CHANCE, troll_list)
        troll = forced or ambush
        if troll is not None:
            vc = await voice_mgr.ensure_voice(interaction)
            tracks, _, _ = await search_ytdlp(troll["url"], 1, 0)
            if not tracks:
                await interaction.followup.send("❌ No se encontraron resultados.")
                return
            _enqueue(str(interaction.guild_id), interaction.user.display_name, tracks)
            note = ("🎭 ¡TROLEADO! Pediste "
                    f"**{song_query}** y suena **{tracks[0].get('title')}**."
                    if ambush else
                    f"🎭 **{tracks[0].get('title')}** (pedido por keyword).")
            await interaction.followup.send(note)
            await _maybe_start(interaction, vc)
            return

        options = await search_many(song_query, n=5)
        if not options:
            await interaction.followup.send("❌ No se encontraron resultados.")
            return

        class PickView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.select(
                placeholder="🔎 Elige tu canción…",
                options=[
                    discord.SelectOption(
                        label=t.get("title", "Untitled")[:100],
                        value=str(i),
                        description=(
                            f"{t.get('uploader') or 'YouTube'} · "
                            f"{format_duration(t.get('duration'))}"
                        )[:100],
                    )
                    for i, t in enumerate(options)
                ],
            )
            async def pick(self, sel: discord.Interaction, select):
                if sel.user.id != interaction.user.id:
                    return await sel.response.send_message(
                        "❌ Solo quien pidió puede elegir.", ephemeral=True)
                if interaction.user.voice is None:
                    return await sel.response.send_message(
                        "🎧 Debes estar en un canal de voz.", ephemeral=True)
                track = options[int(select.values[0])]
                vc2 = await voice_mgr.ensure_voice(interaction)
                _enqueue(str(interaction.guild_id),
                         interaction.user.display_name, [track])
                await sel.response.edit_message(
                    content=f"🎵 Agregada: **{track.get('title')}**", view=None)
                await _maybe_start(interaction, vc2)

            async def on_timeout(self):
                try:
                    await interaction.edit_original_response(
                        content="⌛ Menú expirado. Usa /play de nuevo.", view=None)
                except Exception:
                    pass

        lines = [f"{i}. {track_line(t)}" for i, t in enumerate(options, start=1)]
        await interaction.followup.send(
            "🔎 **Resultados para:** " + song_query + "\n" + "\n".join(lines),
            view=PickView(), ephemeral=True)
        return

    vc = await voice_mgr.ensure_voice(interaction)
    tracks, total, unavailable = await search_ytdlp(song_query, limit, start_index)


    if not tracks:
        await interaction.followup.send("❌ No se encontraron resultados.")
        return

    _enqueue(str(interaction.guild_id), interaction.user.display_name, tracks)

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

    await _maybe_start(interaction, vc)



def _enqueue(guild_id: str, display_name: str, tracks: list) -> None:
    """Encola tracks firmados por quien pidió (compartido /play + select)."""
    queue = get_queue(guild_id)
    for t in tracks:
        t["requested_by"] = display_name
        queue.append(t)


async def _maybe_start(interaction, vc) -> None:
    """Arranca la reproducción si no hay nada sonando."""
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
        "⏭ /skip [n] — Salta n canciones · 🔜 /next — Ver cuál sigue",
        "🎶 /queue — Ver cola · 🎧 /nowplaying — Actual",
        "🔀 /shuffle · 🗑️ /remove · ↔️ /move · 🧹 /clear — Cola",
        "⛔ /stop — Detiene todo · 👋 /disconnect — Salir",
        "🎭 /troll — Menú troll · 📜 /history — Historial + replay",
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


@bot.tree.command(name="troll", description="Menú de canciones troll.")
async def troll(interaction: discord.Interaction):
    from music.trolls import ensure_trolls

    troll_list = ensure_trolls()
    if not troll_list:
        return await interaction.response.send_message(
            "🎭 No hay trolls configurados (trolls.json).", ephemeral=True)

    class TrollView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @discord.ui.select(
            placeholder="🎭 Elige tu víctima…",
            options=[discord.SelectOption(label=t["name"][:100], value=str(i))
                     for i, t in enumerate(troll_list)],
        )
        async def pick(self, sel: discord.Interaction, select):
            if sel.user.id != interaction.user.id:
                return await sel.response.send_message(
                    "❌ Solo quien pidió puede elegir.", ephemeral=True)
            if interaction.user.voice is None:
                return await sel.response.send_message(
                    "🎧 Debes estar en un canal de voz.", ephemeral=True)
            from music.search import search_ytdlp

            troll = troll_list[int(select.values[0])]
            vc = await voice_mgr.ensure_voice(interaction)
            tracks, _, _ = await search_ytdlp(troll["url"], 1, 0)
            if not tracks:
                return await sel.response.send_message(
                    "❌ No se pudo resolver el troll.", ephemeral=True)
            _enqueue(str(interaction.guild_id), interaction.user.display_name, tracks)
            await sel.response.edit_message(
                content=f"🎭 Troleo en camino: **{tracks[0].get('title')}**", view=None)
            await _maybe_start(interaction, vc)

    await interaction.response.send_message(
        "🎭 **Menú troll:**", view=TrollView(), ephemeral=True)


@bot.tree.command(name="history", description="Últimas canciones + re-encolar.")
async def history(interaction: discord.Interaction):
    from music.queue import get_history
    from ui.embeds import track_line

    hist = get_history(str(interaction.guild_id))
    if not hist:
        return await interaction.response.send_message(
            "📜 Historial vacío.", ephemeral=True)

    class HistView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @discord.ui.select(
            placeholder="📜 Re-encolar…",
            options=[discord.SelectOption(
                label=t.get("title", "Untitled")[:100], value=str(i))
                for i, t in enumerate(hist)],
        )
        async def pick(self, sel: discord.Interaction, select):
            if sel.user.id != interaction.user.id:
                return await sel.response.send_message(
                    "❌ Solo quien pidió puede elegir.", ephemeral=True)
            if interaction.user.voice is None:
                return await sel.response.send_message(
                    "🎧 Debes estar en un canal de voz.", ephemeral=True)
            track = dict(hist[int(select.values[0])])
            track["url"] = None  # forzar resolución fresca al sonar
            vc = await voice_mgr.ensure_voice(interaction)
            _enqueue(str(interaction.guild_id), interaction.user.display_name, [track])
            await sel.response.edit_message(
                content=f"🎵 Re-encolada: **{track.get('title')}**", view=None)
            await _maybe_start(interaction, vc)

    lines = [f"{i}. {track_line(t)}" for i, t in enumerate(hist, start=1)]
    await interaction.response.send_message(
        "📜 **Historial:**\n" + "\n".join(lines), view=HistView(), ephemeral=True)


# --- Alters configurables (Sprint 5, D-03) ---
# Cada alter es un slash command propio que reutiliza el callback del canónico.
from core.aliases import AliasError, ensure_aliases

try:
    ALIASES = ensure_aliases()
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