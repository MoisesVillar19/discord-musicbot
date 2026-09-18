# Comandos — MusicBot

> Debes estar en un canal de voz para `/play`.
> Los canónicos están en inglés por convención; cada servidor tiene alters en
> español sembrados por defecto (`/jugar`→`/play`, `/cola`→`/queue`, …).
> Ver tu lista activa con `/help`. Nombres revisados en `../desarrollo/auditoria.md` §5.

## /play

```
/play song_query:<nombre o URL> [start:<n>] [limit:<n>]
```

- `song_query`: texto (`despacito`), URL de video o URL de playlist.
- `start`: desde qué posición de la playlist empezar (default 1).
- `limit`: cuántas agregar como máximo (default 100, tope 100).

Ejemplos:

```
/play song_query:bohemian rhapsody
/play song_query:https://www.youtube.com/watch?v=xyz
/play song_query:https://www.youtube.com/playlist?list=abc start:5 limit:20
```

Comportamiento:

- Texto libre → menú efímero con 5 resultados (autor + duración); eliges uno y
  recién ahí el bot entra a voz. Expira a los 60 s. Solo quien pidió puede elegir.
- Playlist → mensaje `📂 Playlist detectada` con agregadas / no disponibles / posición.
- URL de video → suena exactamente ese video.
- Si nada se está reproduciendo, empieza de inmediato; si no, queda en cola.

## /queue

Muestra la cola del servidor en embed paginado (10 por página, botones ⬅️/➡️,
se cierra a los 2 min). Efímero, solo tú lo ves.

## /nowplaying

Muestra la canción actual con título enlazado, autor, duración, miniatura y
quién la pidió. Si no hay nada: `🔇 No hay nada reproduciéndose.`

## /shuffle — /remove — /move — /clear

- `/shuffle`: mezcla la cola (requiere ≥2).
- `/remove posicion`: elimina la #N (base 1, ver `/queue`).
- `/move origen destino`: mueve la #origen a la #destino.
- `/clear`: vacía la cola; la canción actual sigue sonando.
- Requieren estar en el mismo canal que el bot.

## /pause — /resume — /skip — /next — /stop

- `/pause`: pausa lo actual. Si no estás en voz o no hay nada, avisa.
- `/resume`: reanuda si estaba pausado.
- `/skip [cantidad]`: corta la actual y avanza N (default 1).
- `/next`: muestra cuál sigue **sin saltar nada** (solo consulta).
- `/stop`: limpia la cola (`clear_queue`), detiene y desconecta al bot.
- `/disconnect`: solo desconecta; la cola se conserva para retomar con `/play`.

### Diferencias: skip vs next vs remove
| Comando | Corta la actual | Toca la cola | Reproduce algo |
|---|---|---|---|
| `/skip [n]` | ✅ | Descarta n-1 en cola | La siguiente |
| `/next` | ❌ | ❌ (solo lee) | ❌ |
| `/remove n` | ❌ | Elimina la #n sin sonar | ❌ |

## /troll — /history

- `/troll`: menú con las canciones troll (`trolls.json` local). También se
  activan escribiendo su keyword en `/play`, o por **emboscada**: con prob.
  `TROLL_CHANCE` (default 0.05, 0 = off) un `/play` por texto suena un meme
  al azar en vez de lo pedido. Solo aplica a texto, nunca a URLs.
- `/history` (alter `/historial`): últimas 20 reproducidas + menú para
  re-encolar (se resuelve audio fresco al sonar).

## /help

Muestra la ayuda corta en el canal.

## Notas técnicas

- Cola: `collections.deque` por `guild_id` en `music/queue.py`.
  Cada item es `(audio_url, title, webpage_url)`.
- Búsqueda: `music/search.py::search_ytdlp(query, max_tracks, start_index)`
  devuelve `(tracks, total, unavailable)`.
- Reproducción: `bot.py::play_next_song` hace `popleft()`, resuelve
  `audio_url` vía `resolve_stream_url(webpage_url)` si falta, y reproduce
  con `discord.FFmpegOpusAudio` + `after` que encola la siguiente.
- FFmpeg: `config.FFMPEG_PATH` (`bin/ffmpeg/ffmpeg.exe`) si existe,
  si no el del `PATH`.
