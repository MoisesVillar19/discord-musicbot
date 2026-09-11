# 🎧 DJ Huevito — MusicBot de Discord

Bot de música para Discord en Python: reproduce canciones y playlists de YouTube con `/play`, cola por servidor, controles de pausa / resume / skip / stop.

## ✨ Funciones

- `/play <nombre o URL> [start] [limit]` — reproduce o encola. Acepta texto libre (usa `ytsearch`), video o playlist.
- `/queue` — muestra la cola actual del servidor.
- `/pause`, `/resume`, `/skip`, `/stop` — controles de reproducción.
- `/help` — lista de comandos.
- Cola independiente por servidor (`music/queue.py`).
- Resolución diferida de URL de audio para playlists (no se cae si un video no trae `url` directa).

## 🧱 Estructura

```
MusicBot/
├── bot.py              # Punto de entrada + comandos slash
├── config.py           # Lee DISCORD_TOKEN (.env) y rutas de FFmpeg
├── music/
│   ├── queue.py        # Cola por guild (deque)
│   └── search.py       # Búsqueda yt-dlp + resolve_stream_url
├── commands/ core/ services/ ui/ utils/  # Reservado para futura modularización
├── requirements.txt
├── start_bot.bat       # Arranque rápido en Windows
├── .env.example        # Plantilla (copiar a .env)
└── docs/               # Documentación extra
```

> Los comandos viven hoy en `bot.py`. Las carpetas `commands/`, `core/`, `services/`, `ui/`, `utils/` están vacías como reserva para cuando quieras separar en cogs.

## 🚀 Instalación (Windows)

1. Instala **Python 3.11+** y **FFmpeg** (o deja el `bin/ffmpeg/ffmpeg.exe` local).
   - Si FFmpeg está en el `PATH`, el bot lo usa automáticamente.
   - Si no, coloca `ffmpeg.exe` en `bin/ffmpeg/ffmpeg.exe` (ver `config.py`).
2. Clona el repo:
   ```bat
   git clone https://github.com/MoisesVillar19/MusicBot.git
   cd MusicBot
   ```
3. Crea entorno virtual e instala dependencias:
   ```bat
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Configura el token:
   ```bat
   copy .env.example .env
   notepad .env
   ```
   Pega tu token: `DISCORD_TOKEN=...`
   - Activa el intent **Message Content** en el [portal de Discord](https://discord.com/developers/applications).
5. Ejecuta:
   ```bat
   venv\Scripts\python bot.py
   ```
   o doble clic en `start_bot.bat`.

## 🤖 Invitar el bot a tu servidor

1. En el portal de desarrollador → OAuth2 → URL Generator.
2. Marca `bot` + `applications.commands`, permisos: Connect, Speak, Send Messages, Embed Links.
3. Abre la URL generada e invita al bot. Luego usa `/play` en un canal de voz.

## 📖 Comandos

| Comando | Descripción | Ejemplo |
|---|---|---|
| `/play <query>` | Reproduce o encola | `/play despacito`, `/play https://youtu.be/...` |
| `/play <playlist> [start] [limit]` | Playlist paginada (máx 100) | `/play <url_playlist> start:5 limit:20` |
| `/queue` | Ver cola | `/queue` |
| `/pause` / `/resume` | Pausar / reanudar | — |
| `/skip` | Saltar canción | — |
| `/stop` | Detener + limpiar cola + salir | — |
| `/help` | Ayuda | — |

Detalles y solución de problemas: ver [`docs/COMANDOS.md`](docs/COMANDOS.md) y [`docs/INSTALACION.md`](docs/INSTALACION.md).

## 🛠️ Qué se arregló (vs versión rota)

La versión anterior se rompía por:

1. **Tupla inconsistente en la cola** — `/play` guardaba `(url, title, webpage_url)` (3 elementos) pero `/queue` y `play_next_song` desempaquetaban 2 → `ValueError: too many values to unpack`. Ahora todo usa 3 elementos con compatibilidad hacia atrás.
2. **Búsqueda por texto no funcionaba** — `yt_dlp.extract_info("despacito")` sin `ytsearch`/`default_search` no devolvía nada. Ahora `music/search.py` detecta URL vs texto y usa `ytsearch:` automáticamente.
3. **Videos sin `url` directa tumbaban la reproducción** — en playlists algunas entradas vienen sin stream. Ahora se guarda `webpage_url` y `play_next_song` la resuelve con `resolve_stream_url()`, saltando la canción si es imposible.
4. **Doble diccionario de colas** — `bot.py` tenía su propio `SONG_QUEUES` y `music/queue.py` otro; al terminar se limpiaba el equivocado. Ahora solo se usa `music/queue.py` + `clear_queue()`.
5. **FFmpeg hardcodeado a Windows** — `executable="bin\\ffmpeg\\ffmpeg.exe"` reventaba si no existía. Ahora `_ffmpeg_executable()` usa el binario local si existe y si no, el FFmpeg del `PATH`.
6. **Sin validación de token** — `bot.run(None)` daba un error críptico. Ahora falla con mensaje claro si falta `DISCORD_TOKEN`.

## 🗺️ Qué falta / ideas de mejora

- [ ] Pasar comandos a **Cogs** (`commands/play.py`, `commands/queue.py`, …) y borrar código duplicado.
- [ ] `/nowplaying`, `/volume`, `/loop`, `/shuffle`, `/remove`, `/clear`.
- [ ] Auto-salir del canal cuando queda vacío (evento `on_voice_state_update`).
- [ ] Paginación con botones en `/queue` (embed + Next/Prev).
- [ ] Logging a archivo (`utils/logger.py`) en vez de `print`.
- [ ] Manejo de errores global (`on_command_error` / `on_app_command_error`).
- [ ] Tests básicos de `music/queue.py` y `music/search.py` (mock de yt-dlp).
- [ ] Docker + `docker-compose.yml` para deploy en VPS.
- [ ] CI con GitHub Actions (`py_compile` + `ruff`).

## 🔒 Seguridad

- **Nunca subas `.env`** (contiene tu token). Ya está en `.gitignore`.
- Si tu token se filtró alguna vez: regenéralo en el portal de Discord.
- `bin/` (ffmpeg ~300 MB) tampoco se sube; cada quien lo instala local.

## 📄 Licencia

Uso personal/educativo. Revisa los Términos de YouTube y Discord antes de uso público.
