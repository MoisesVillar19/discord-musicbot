# Diccionario de datos y glosario — MusicBot

> Referencia para los sprints. "Actual (S0)" = código tras el Sprint 0.
> "Objetivo" = lo que introduce cada sprint (ver `sprints.md`).

## 1. Track (canción en cola)

### Actual (S0): tupla de 3
```python
(audio_url, title, webpage_url)
# audio_url: str | None — URL directa de audio (None si vino de playlist flat / sin extraer)
# title: str
# webpage_url: str | None — página del video, se usa para resolver audio diferido
```
Compatibilidad: quedan aceptadas tuplas viejas de 2 `(audio_url, title)` vía
`try/except ValueError` en `/queue` y `play_next_song`. El shim se retira en el Sprint 1.

### Objetivo (Sprint 1): dict
```python
{
  "title": str,            # requerido
  "webpage_url": str,      # requerido — identidad estable del track
  "url": str | None,       # URL directa de audio (None hasta resolver)
  "duration": int | None,  # segundos
  "uploader": str | None,  # artista/canal
  "thumbnail": str | None, # para embeds (Sprint 4)
  "requested_by": str | None,  # "nombre#discriminator" o mention (Sprint 4)
}
```
Regla: `webpage_url` es la identidad; `url` es efímera (caduca) y **siempre**
puede re-resolverse con `resolve_stream_url(webpage_url)`.

## 2. Estructuras por servidor (guild)

| Estructura | Dónde | Actual (S0) | Objetivo |
|---|---|---|---|
| `SONG_QUEUES: dict[str, deque]` | `music/queue.py` | ✅ `get_queue()`, `clear_queue()` | + `remove()`, `move()`, `shuffle()`, `peek()` (S1) |
| `NOW_PLAYING: dict[str, Track]` | — (no existe) | ❌ el embed se envía y se olvida | Nuevo en S2 (`core/voice.py` lo escribe al empezar cada track; lo lee `/nowplaying` en S4) |
| `GUILD_LOCKS: dict[str, asyncio.Lock]` | — (no existe) | ❌ `skip`/`stop`/`play` concurrentes compiten | Nuevo en S2; toda mutación de voz/cola bajo lock del guild |

## 3. Variables de entorno (`.env`)

| Variable | Requerida | Default | Uso |
|---|---|---|---|
| `DISCORD_TOKEN` | Sí | — | `config.TOKEN`; sin ella el bot aborta con mensaje claro |
| `BOT_NAME` | No | `"MusicBot"` | Nombre visible en `/help` y embeds (ADR-004) |

## 4. Opciones yt-dlp

| Contexto | Opciones clave | Notas |
|---|---|---|
| Búsqueda texto (`ytsearch:`) | `noplaylist=True`, `default_search=ytsearch` | Extracción completa: 1er resultado con `url` + metadatos |
| Video único (URL) | `noplaylist=True`, `ignoreerrors=True` | Extracción completa |
| Playlist (URL) actual | `noplaylist=False`, `ignoreerrors=True` | ⚠️ Extrae TODO antes de sonar (lento) → Sprint 3 |
| Playlist objetivo (S3) | `+ extract_flat="in_playlist"` | Entradas ligeras; audio se resuelve al reproducir |
| `resolve_stream_url()` | `noplaylist=True` sobre `webpage_url` | Fallback permanente aunque haya flat |

## 5. Opciones FFmpeg

```python
before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
options        = "-vn -c:a libopus -b:a 96k"
executable     = config.FFMPEG_PATH si existe, si no el del PATH
```
`bot.py::_ffmpeg_executable()` (se traslada tal cual a `core/voice.py` en S2).

## 6. Errores conocidos (código → significado → estado)

| Síntoma | Causa | Estado |
|---|---|---|
| `ValueError: too many values to unpack (expected 2)` | Cola 3-tuplas vs desempaquetado de 2 | ✅ Mitigado S0 (shim); se elimina causa en S1 |
| `IndexError: list index out of range` (`tracks[0]`) | `ytsearch1:` sobre URL de playlist → `Downloading 0 items` | ✅ Mitigado S0 (detección URL vs texto + lista vacía → mensaje) |
| `404 Unknown interaction` en `/stop` | Responder tarde tras operación lenta | ✅ Mitigado S0 (`defer` + `followup`) |
| `ffmpeg process XXXX has not terminated…` | `stop`/`disconnect` con FFmpeg a medio corte | 🟡 Vigente; S2 unifica el apagado en `core/voice.py` |
| `No supported JavaScript runtime` (yt-dlp) | Falta runtime JS en la máquina | 🟡 Operativo, no código: instalar Node.js/Deno (S3) |
| `/stop` desde otro canal corta la fiesta | Sin validación de canal | 🔴 Pendiente → S2 (`require_same_voice`) |
| `skip` + `stop` simultáneos → estado raro | Sin locks por guild | 🔴 Pendiente → S2 (`GUILD_LOCKS`) |
| `after_play` sigue tras `/stop` | Dos vías de apagado | 🟡 Parcial S0 (guard + `clear_queue`); definitivo en S2 |

## 7. Glosario

- **Guild/servidor:** servidor de Discord; toda la reproducción es por guild.
- **Deque:** cola de doble extremo; `popleft()` saca la siguiente canción.
- **Self-deaf (`self_deaf=True`):** el bot entra ensordecido al canal (no escucha).
- **Defer/followup:** responder "estoy trabajando" para no superar los ~3 s de la interacción.
- **`after_play`:** callback que dispara la siguiente canción al terminar la actual.
- **Extract flat:** listar la playlist sin descargar metadatos de cada video.
- **Cog:** módulo de comandos de `discord.py` para no concentrar todo en `bot.py`.
- **Ephemeral:** mensaje visible solo para quien ejecutó el comando.
- **Track:** unidad de cola (hoy tupla, objetivo dict §1).
- **S0–S4:** Sprint 0 (hecho) a Sprint 4 (ver `sprints.md`).
