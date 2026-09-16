import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Nombre visible del bot (mensajes, /help, embeds). En tu servidor local
# puedes poner "DJ Huevito" u otro; en el repo se deja neutro.
BOT_NAME = os.getenv("BOT_NAME", "MusicBot")

FFMPEG_PATH = "bin/ffmpeg/ffmpeg.exe"

YTDLP_OPTIONS = {
    "format": "bestaudio[abr<=96]/bestaudio",
    "noplaylist": True,
    "youtube_include_dash_manifest": False,
    "youtube_include_hls_manifest": False,
}
