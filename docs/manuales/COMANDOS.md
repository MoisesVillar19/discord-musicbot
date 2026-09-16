# Comandos — DJ Huevito

> Debes estar en un canal de voz para `/play`.

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

- Texto libre → se usa `ytsearch:` y se encola el primer resultado.
- Playlist → mensaje `📂 Playlist detectada` con agregadas / no disponibles / posición.
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

## /pause — /resume — /skip — /stop

- `/pause`: pausa lo actual. Si no estás en voz o no hay nada, avisa.
- `/resume`: reanuda si estaba pausado.
- `/skip`: corta la canción actual (`vc.stop()`); el `after` dispara la siguiente.
- `/stop`: limpia la cola (`clear_queue`), detiene y desconecta al bot.
- `/disconnect`: solo desconecta; la cola se conserva para retomar con `/play`.

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
