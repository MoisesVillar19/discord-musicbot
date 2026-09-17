# 🎧 MusicBot — Bot de música para Discord

Bot de música para Discord en Python: reproduce canciones y playlists de
YouTube con `/play`, cola independiente por servidor y controles de
pausa / resume / skip / stop.

## ✨ Funciones

- `/play <nombre o URL> [start] [limit]` — texto, video o playlist (hasta 100 por tanda).
- `/queue` — cola del servidor (mensaje ephemeral).
- `/pause`, `/resume`, `/skip`, `/stop` — controles de reproducción.
- `/help` — ayuda corta.
- Cola por servidor, autodisconnect al vaciarse la cola, embed Now Playing.
- El nombre visible se configura con `BOT_NAME` en `.env` (por defecto `MusicBot`).

## 🚀 Inicio rápido (Windows)

```bat
git clone https://github.com/MoisesVillar19/MusicBot.git
cd MusicBot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
venv\Scripts\python bot.py
```

En `.env` pon tu token (`DISCORD_TOKEN=…`, con el intent **Message Content**
activado) y opcionalmente `BOT_NAME=TuNombre`.

Guías completas:

- [`docs/manuales/INSTALACION.md`](docs/manuales/INSTALACION.md) — portal de Discord, FFmpeg, problemas comunes.
- [`docs/manuales/COMANDOS.md`](docs/manuales/COMANDOS.md) — referencia de comandos y notas técnicas.
- [`docs/manuales/PANEL.md`](docs/manuales/PANEL.md) — panel local y alters.

## 🧱 Estructura

```
MusicBot/
├── bot.py              # Comandos slash + coordinación de reproducción
├── config.py           # DISCORD_TOKEN, BOT_NAME, FFMPEG_PATH (desde .env)
├── music/
│   ├── queue.py        # Cola por servidor
│   └── search.py       # Búsqueda yt-dlp + resolución de audio
├── commands/ core/ services/ ui/ utils/  # Se pueblan por sprints (ver desarrollo)
├── requirements.txt
├── start_bot.bat       # Bot directo (headless)
├── panel.bat           # Panel local (start/stop, alters, config, logs)
├── panel/              # App tkinter del panel
├── aliases.example.json # Plantilla de alters (los tuyos van en aliases.json local)
├── .env.example
└── docs/
    ├── manuales/       # Instalación y comandos (usuario)
    └── desarrollo/     # Arquitectura, roadmap, sprints (contribuidor)
```

## 🗺️ Roadmap

Estado y próximos pasos (sprints 1–5: `Track` dict → `core/voice.py` → playlists
rápidas → experiencia → alters + panel local):

- [`docs/desarrollo/roadmap.md`](docs/desarrollo/roadmap.md)
- [`docs/desarrollo/sprints.md`](docs/desarrollo/sprints.md)
- [`docs/desarrollo/arquitectura.md`](docs/desarrollo/arquitectura.md)
- [`docs/desarrollo/casos.md`](docs/desarrollo/casos.md) (aceptación)
- [`docs/desarrollo/diccionario.md`](docs/desarrollo/diccionario.md) (datos y glosario)
- [`docs/desarrollo/auditoria.md`](docs/desarrollo/auditoria.md) (historia: qué quedó obsoleto y qué sigue pendiente)

## 🔒 Seguridad

- **Nunca subas `.env`** (ya está en `.gitignore`). Si un token se filtró, regenéralo.
- `bin/` (FFmpeg), `venv/` y `__pycache__/` tampoco se suben.

## 📄 Licencia

Uso personal/educativo. Revisa los Términos de YouTube y Discord antes de uso público.
