import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Nombre visible del bot (mensajes, /help, embeds). En tu servidor local
# puedes poner "DJ Huevito" u otro; en el repo se deja neutro.
BOT_NAME = os.getenv("BOT_NAME", "MusicBot")

# Servidor de desarrollo (opcional): si se define, los slash se sincronizan
# solo ahí y los cambios de nombres/alters aparecen al instante.
# Sin GUILD_ID el sync es global y tarda hasta ~1h en propagar.
_guild = os.getenv("GUILD_ID", "").strip()
GUILD_ID = int(_guild) if _guild.isdigit() else None

# Probabilidad (0.0-1.0) de emboscada troll en /play por texto. 0 = desactivado.
try:
    TROLL_CHANCE = min(1.0, max(0.0, float(os.getenv("TROLL_CHANCE", "0.05"))))
except ValueError:
    TROLL_CHANCE = 0.05

# Rol DJ (opcional): ID numérico del rol que puede usar comandos sensibles
# (stop, skip, disconnect, clear, remove, move). Vacío = sin restricción.
_dj = os.getenv("DJ_ROLE_ID", "").strip()
DJ_ROLE_ID = int(_dj) if _dj.isdigit() else None

FFMPEG_PATH = "bin/ffmpeg/ffmpeg.exe"

YTDLP_OPTIONS = {
    "format": "bestaudio[abr<=96]/bestaudio",
    "noplaylist": True,
    "youtube_include_dash_manifest": False,
    "youtube_include_hls_manifest": False,
}
