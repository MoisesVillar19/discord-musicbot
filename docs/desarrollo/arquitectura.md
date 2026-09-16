# Arquitectura — MusicBot

> Estado a fecha del Sprint 0. Ver `sprints.md` para el plan de migración
> y `auditoria.md` para qué parte de los docs previos sigue vigente.

## 1. Arquitectura actual (Sprint 0, funciona)

Todo el flujo de Discord vive en `bot.py`; la búsqueda y la cola ya están
extraídas a `music/`. Es un monolito con dos módulos satélite: funciona,
pero `bot.py` mezcla UI (slash commands), voz (FFmpeg) y coordinación.

```text
Discord
   │
   ▼
bot.py  ── slash handlers (/play, /pause, /resume, /skip, /stop, /queue, /help)
   │         + play_next_song() + after_play + _ffmpeg_executable()
   │
   ├── music/search.py ── search_ytdlp(), resolve_stream_url() ──▶ yt-dlp
   │
   └── music/queue.py ── get_queue(), clear_queue() (deque por guild)
                            │
                            ▼
                    discord.FFmpegOpusAudio ──▶ canal de voz
```

| Módulo | Responsabilidad hoy | Estado |
|---|---|---|
| `bot.py` | Comandos slash, `play_next_song`, `after_play`, resolución FFmpeg, validación token | ⚠️ Hace demasiado; objetivo: solo UI |
| `config.py` | `DISCORD_TOKEN`, `BOT_NAME`, `FFMPEG_PATH`, `YTDLP_OPTIONS` | ✅ Estable, no tocar salvo añadir claves |
| `music/search.py` | `search_ytdlp()` (URL vs texto, playlists con start/limit, `ignoreerrors`), `resolve_stream_url()` | ✅ Estable; pendiente `extract_flat` (Sprint 3) |
| `music/queue.py` | `get_queue()`, `clear_queue()`; ítems `(audio_url, title, webpage_url)` con shim de compat 2-tuplas | ✅ Estable; pendiente migrar a `Track` dict (Sprint 1) |
| `commands/`, `core/`, `services/`, `ui/`, `utils/` | Solo `__init__.py` y stubs vacíos | 🟡 Reserva; se pueblan en Sprints 1–2 |

## 2. Arquitectura objetivo

```text
                        ┌──────────────┐
                        │    bot.py    │  registro de cogs + on_ready + errores globales
                        └──────┬───────┘
                               │ cogs
               ┌───────────────┼────────────────┐
               ▼               ▼                ▼
         commands/        commands/        commands/
         play, queue      control          help, nowplaying
         (UI Discord)     (pause/resume/   (embeds)
                          skip/stop)
               │               │                │
               ▼               ▼                ▼
         ┌────────────────────────────────────────────┐
         │               core/voice.py                │  UNICA capa que toca VoiceClient/FFmpeg:
         │  connect/move/disconnect, play_next,      │  locks por guild, guard after_play,
         │  skip/stop/disconnect, autodisconnect     │  resolve diferido, NOW_PLAYING
         └──────────┬───────────────────┬───────────┘
                    ▼                   ▼
            music/search.py       music/queue.py
            yt-dlp, flat,         Track dict, helpers
            validación URLs       (add/remove/move/shuffle/clear)
                    │                   │
                    ▼                   ▼
            services/ (lyrics,    ui/embeds.py (Now Playing,
            metadata)             queue paginada, search results)
                    │
                    ▼
            utils/ (validators, errors, logger)
```

### Reglas de dependencia (para no volver al monolito)

1. `bot.py` **no** importa `yt_dlp`, `FFmpeg` ni `VoiceClient` directamente.
2. `core/voice.py` es la **única** capa que toca voz/FFmpeg.
3. `music/` **no** importa `discord` (lógica pura, testeable).
4. `ui/` solo formatea datos → embeds/Views, no reproduce nada.
5. `commands/` (cogs) validan interacción → llaman a `core/` → responden.
6. `config.py` solo lee entorno; sin lógica.

## 3. Decisiones registradas (ADR breves)

### ADR-001 — Cola de 3-tuplas con shim, migración a `Track` dict en Sprint 1
- **Contexto:** `/play` guarda `(url, title, webpage_url)` pero `play_next_song` y
  `/queue` desempaquetaban 2 → `ValueError` (ver `refactorizacionV1.md` § "Problema detectado").
- **Decisión Sprint 0:** normalizar a 3-tuplas con `try/except ValueError` de compat.
- **Decisión Sprint 1:** migrar a `dict` (`diccionario.md` § Track) con helpers en
  `music/queue.py`. La API `get_queue/clear_queue` se mantiene, así que `bot.py`
  solo cambia los 2 sitios de desempaquetado.
- **Consecuencia:** añadir campos (duración, autor, thumbnail, solicitado_por)
  deja de romper el desempaquetado.

### ADR-002 — `extract_flat` + resolución diferida (no choca con Sprint 0)
- **Contexto:** hoy la playlist se extrae completa antes de sonar la 1ª canción
  (lento, muchos warnings). `refactorizacionV1.md` propone `"extract_flat": "in_playlist"`.
- **Decisión:** viable y **complementaria**: el `resolve_stream_url()` del Sprint 0
  es exactamente la pieza "resolver audio solo al reproducir" que el flat necesita.
  El flat devuelve entradas ligeras (`webpage_url`, título aprox.); `core/voice.py`
  resuelve la URL directa justo antes de reproducir y usa `resolve_stream_url()` como fallback.
- **Restricción:** el flat **solo** aplica a playlists; `ytsearch:` y video único
  siguen con extracción completa (necesitan `url` y metadatos ya).

### ADR-003 — `core/voice.py` como única capa de voz (Sprint 2)
- **Contexto:** `play_next_song` + `after_play` + connect/disconnect viven en `bot.py`;
  `/stop` desde otro canal y `skip`/`stop` simultáneos causan estados inconsistentes
  (ver `algunos errores.md` §§ stop/FFmpeg/locks).
- **Decisión:** mover `play_next_song`, `after_play`, connect/move/disconnect,
  `GUILD_LOCKS`, `NOW_PLAYING` y validación de canal a `core/voice.py`.
  `bot.py` conserva solo handlers slash + `on_ready` + errores globales.
- **Consecuencia:** `/stop`, `/skip` y fin-de-cola comparten el mismo camino de
  apagado → se elimina la doble vía actual (handler vs `after_play`).

### ADR-004 — Nombre del bot configurable
- **Contexto:** docs iniciales usan "DJ Gilmer", el código usaba "DJ Huevito" fijo.
  Para un repo serio el nombre visible no debe estar hardcodeado.
- **Decisión:** `config.BOT_NAME` leído de `BOT_NAME` (default `"MusicBot"`).
  `/help` y futuros embeds lo usan. Cada despliegue pone el suyo en `.env`.

## 4. Mapa de migración (sin romper lo que funciona)

| Sprint | Qué se mueve/añade | Qué NO se toca | Red de seguridad |
|---|---|---|---|
| 1 | `Track` dict + helpers de cola + `BOT_NAME` + tests de `music/` | `play_next_song`, FFmpeg, voz | shim 3-tupla se retira solo al final del sprint |
| 2 | `core/voice.py` (mover tal cual + locks + validación canal + `/disconnect`) | `music/search.py` API, formato `Track` | handlers slash conservan firma y mensajes |
| 3 | `extract_flat` en playlists + validación URLs + límites | reproducción de video único/texto | `resolve_stream_url()` queda como fallback |
| 4 | Features UI (`nowplaying`, paginación, shuffle/remove/move) | núcleo voz/cola | cada comando en su cog, reversible por separado |
| 5 | Alters (registro dinámico) + `panel/` tkinter | lógica de comandos (solo se añade registro) | alters desactivables borrando `aliases.json` |

## 5. Alters + panel local (Sprint 5)

### Por qué así
Discord no soporta aliases en slash commands: cada nombre visible es un
`app_commands.Command` propio. El diseño es entonces: **una lógica, N registros**.

```text
aliases.json ──loader+validación──▶ [(canónico, [alters])] ──▶ bot.tree
        play ──▶ /play ──┐
                 /jugar ─┤──▶ _do_play() (o cog Play)
                 /rolita ┘
```

### ADR-005 — Alters solo slash, config local
- **Contexto:** se quiere `/[nombre de amigo]` como chiste (jugar:play) sin
  bifurcar lógica, y que cualquiera que clone el repo ponga los suyos.
- **Decisión:** alters solo slash; `aliases.json` local (gitignored) +
  `aliases.example.json` versionado; validación estricta al arrancar
  (minúsculas, `^[\w-]{1,32}$`, sin colisiones, máx ~10/comando).
- **Consecuencia:** cambiar un alter = editar + reiniciar + re-sync
  (global ~1h; con `GUILD_ID` en `.env`, sync por servidor instantáneo).

### ADR-006 — Panel desktop tkinter, sin web
- **Contexto:** un solo administrador, proyecto personal de bajo costo.
- **Decisión:** app de escritorio con `tkinter` (stdlib, cero dependencias).
  Un **perfil** = un token + su `aliases.json` + su `.env`; el panel gestiona
  un subproceso por perfil (start/stop/restart), editor de alters, editor
  `.env` (token enmascarado), visor de logs y botón re-sync. Sin IPC:
  panel y bot solo comparten archivos.
- **Consecuencia:** un perfil basta para N servidores (un token = un proceso).
  Dos procesos con el mismo token no coexisten (Discord desconecta al segundo);
  el panel lo advierte (CB-14). Multi-instancia real = varios perfiles con
  tokens distintos.
