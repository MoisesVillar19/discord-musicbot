# Importing libraries and modules
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from config import TOKEN, FFMPEG_PATH, YTDLP_OPTIONS, BOT_NAME
from music.queue import get_queue, clear_queue

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN no encontrado. Crea un archivo .env con DISCORD_TOKEN=tu_token "
        "(ver .env.example)."
    )


def _ffmpeg_executable() -> str | None:
    """Devuelve el ejecutable de FFmpeg a usar, o None si va por PATH."""
    import os as _os

    # config.py usa "bin/ffmpeg/ffmpeg.exe" (relativo). Normalizar separadores.
    candidate = _os.path.normpath(FFMPEG_PATH) if FFMPEG_PATH else ""
    if candidate and _os.path.isfile(candidate):
        return candidate
    return None


# Setup of intents. Intents are permissions the bot has on the server
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot ready-up code
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!")


@bot.tree.command(name="skip")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    vc = interaction.guild.voice_client

    if not vc or not vc.is_connected():
        return await interaction.followup.send("No estoy en un canal de voz.")

    if not (vc.is_playing() or vc.is_paused()):
        return await interaction.followup.send("No hay nada reproduciéndose.")

    vc.stop()
    await interaction.followup.send("⏭️ Canción omitida.")



@bot.tree.command(name="pause", description="Pausa la canción que se está reproduciendo actualmente.")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if voice_client is None:
        return await interaction.response.send_message("Oe sanazo, no estoy en un canal de voz.")

    # Check if something is actually playing
    if not voice_client.is_playing():
        return await interaction.response.send_message("Cri cri, no estoy reproduciendo nada ahora mismo.")
    
    # Pause the track
    voice_client.pause()
    await interaction.response.send_message("⏸️ Reproducción pausada!")


@bot.tree.command(name="resume", description="Reanuda la canción que se ha pausado.")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if voice_client is None:
        return await interaction.response.send_message("Oe sanazo, no estoy en un canal de voz.")

    # Check if it's actually paused
    if not voice_client.is_paused():
        return await interaction.response.send_message("Cri cri, no estoy pausado ahora mismo.")
    
    # Resume playback
    voice_client.resume()
    await interaction.response.send_message("▶️ Reproducción reanudada!")


@bot.tree.command(name="stop", description="Detiene la reproducción y limpia la cola.")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    msg = await interaction.followup.send("⛔ Deteniendo reproducción...")

    vc = interaction.guild.voice_client
    if not vc:
        return await msg.edit(content="⚠️ No estoy en un canal de voz.")


    guild_id = str(interaction.guild_id)

    clear_queue(guild_id)

    try:
        if vc.is_playing() or vc.is_paused():
            vc.stop()

        await vc.disconnect(force=True)
    except Exception as e:
        print(f"Stop error: {e}")

    await msg.edit(content="⛔ Reproducción detenida.")


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

    voice_channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client

    if vc is None:
        vc = await voice_channel.connect(self_deaf=True)
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)

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


    if not vc.is_playing() and not vc.is_paused():
        await play_next_song(vc, str(interaction.guild_id), interaction.channel)



@bot.tree.command(name="help", description="Ver comandos del bot")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"""
🎧 **Comandos de {BOT_NAME}**

▶ /play <canción> — Reproduce o agrega a la cola
⏸ /pause — Pausa la música
▶ /resume — Reanuda
⏭ /skip — Salta canción
⛔ /stop — Detiene todo

🔥 ¡Disfruta la música!
        """
    )
@bot.tree.command(name="queue", description="Muestra la cola de canciones actuales.")
async def queue(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)

    q = get_queue(guild_id)

    if not q or len(q) == 0:
        await interaction.response.send_message("🎵 Tu cola está vacía.", ephemeral=True)
        return

    message = "🎶 **Cola actual:**\n"
    for idx, track in enumerate(q, start=1):
        # La cola guarda Track (dict)
        message += f"{idx}. {track.get('title', 'Untitled')}\n"
        # Límite de Discord: 2000 caracteres
        if len(message) > 1800:
            message += f"... y {len(q) - idx} más.\n"
            break

    await interaction.response.send_message(message, ephemeral=True)

async def play_next_song(voice_client, guild_id, channel):
    from music.search import resolve_stream_url

    queue = get_queue(guild_id)

    if queue:
        track = queue.popleft()
        audio_url = track.get("url")
        title = track.get("title") or "Untitled"
        webpage_url = track.get("webpage_url")

        # Si yt-dlp no dio URL directa (playlist/flat), resolverla ahora
        if not audio_url and webpage_url:
            audio_url, resolved_title = await resolve_stream_url(webpage_url)
            if resolved_title:
                title = resolved_title

        if not audio_url:
            print(f"[play] Sin URL reproducible para '{title}', saltando...")
            # Intentar con la siguiente en cola sin recursión infinita
            if queue:
                await play_next_song(voice_client, guild_id, channel)
            else:
                try:
                    if voice_client.is_connected():
                        await voice_client.disconnect()
                except Exception as e:
                    print(f"[play] disconnect error: {e}")
                finally:
                    clear_queue(guild_id)
            return

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -c:a libopus -b:a 96k",
        }
        executable = _ffmpeg_executable()
        if executable:
            ffmpeg_options["executable"] = executable
        # Si no hay bin local, discord.py usa ffmpeg del PATH.

        try:
            source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options)
        except Exception as e:
            print(f"[play] FFmpeg error con '{title}': {e}")
            if queue:
                await play_next_song(voice_client, guild_id, channel)
            return

        def after_play(error):
            if error:
                print(f"Error playing {title}: {error}")
            try:
                coro = play_next_song(voice_client, guild_id, channel)
                asyncio.run_coroutine_threadsafe(coro, bot.loop)
            except RuntimeError as e:
                print(f"[play] after_play error: {e}")

        voice_client.play(source, after=after_play)
        embed = discord.Embed(
            title="🎧 Now Playing",
            description=f"🎵 **{title}**",
            color=discord.Color.green()
        )

        asyncio.create_task(channel.send(embed=embed))
    else:
        try:
            if voice_client.is_connected():
                await voice_client.disconnect()
        except Exception as e:
            print(f"[play] disconnect error: {e}")
        finally:
            clear_queue(guild_id)


# Run the bot
bot.run(TOKEN)