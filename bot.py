# Punto de entrada delgado (Sprint 12): setup + eventos + registro.
# Los comandos viven en commands/*.py como Cogs; la voz en core/voice.py.
import discord
from discord.ext import commands

from commands.control import Control
from commands.fun import Fun
from commands.help import Help
from commands.play import Play
from commands.queue import Queue
from config import FFMPEG_PATH, GUILD_ID, TOKEN
from core.aliases import register_aliases
from utils.errors import user_message
from utils.logger import log
from core import voice as voice_mgr


class MusicBot(commands.Bot):
    async def setup_hook(self):
        await setup_bot(self)


# Setup of intents. Intents are permissions the bot has on the server
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = MusicBot(command_prefix="!", intents=intents)


async def setup_bot(bot: commands.Bot) -> None:
    """Registra cogs + alters. Idempotente (los tests la llaman directo)."""
    for cog_cls in (Play, Control, Queue, Fun, Help):
        if bot.get_cog(cog_cls.__name__) is None:
            await bot.add_cog(cog_cls(bot))
    register_aliases(
        bot.tree,
        on_register=lambda alt, canon: log.info("Alter registrado: /%s -> /%s", alt, canon),
    )


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


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN no encontrado. Crea un archivo .env con DISCORD_TOKEN=tu_token "
            "(ver .env.example)."
        )
    # Run the bot
    bot.run(TOKEN)
