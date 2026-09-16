# 🎵 Discord Music Bot — Avances

## 📌 Descripción

Bot de música para Discord desarrollado en **Python**, utilizando:

* `discord.py`
* `yt-dlp`
* `FFmpeg`
* `asyncio`
* `python-dotenv`

El bot permite reproducir música desde YouTube mediante búsquedas o enlaces, administrar una cola de reproducción y controlar la reproducción mediante comandos slash.

---

# ✅ Funcionalidades implementadas

## 🎵 Reproducción

### `/play <canción>`

Permite:

* Buscar canciones mediante texto.
* Obtener el audio desde YouTube mediante `yt-dlp`.
* Conectarse automáticamente al canal de voz del usuario.
* Moverse al canal del usuario si el bot ya estaba conectado.
* Agregar canciones a una cola por servidor.
* Reproducir automáticamente la siguiente canción.

Ejemplo:

```text
/play un mamut chiquitito
```

---

## 📋 Cola de reproducción

Se utiliza un diccionario de colas independiente por servidor:

```python
SONG_QUEUES = {}
```

Cada servidor mantiene su propia `deque`.

Esto permite que diferentes servidores utilicen el bot simultáneamente sin compartir canciones.

### `/queue`

Muestra las canciones actualmente pendientes de reproducción.

Ejemplo:

```text
🎶 Current Queue:
1. Canción 1
2. Canción 2
3. Canción 3
```

---

# 🎛️ Controles de reproducción

## `/pause`

Pausa la canción actual.

Validaciones:

* El bot debe estar conectado.
* Debe existir una canción reproduciéndose.

---

## `/resume`

Reanuda una canción pausada.

Validaciones:

* El bot debe estar conectado.
* La reproducción debe estar pausada.

---

## `/skip`

Detiene la canción actual para pasar a la siguiente.

Pendiente de mejorar:

* Validar que el usuario esté en el mismo canal de voz.
* Manejar posibles ejecuciones simultáneas.
* Usar `defer()` + `followup` para mayor seguridad.

---

## `/stop`

Actualmente:

1. Comprueba que el bot esté conectado.
2. Limpia la cola del servidor.
3. Detiene la canción actual.
4. Desconecta al bot del canal.

```text
/stop
    ↓
Detener reproducción
    ↓
Limpiar cola
    ↓
Desconectar
```

### ⚠️ Problema detectado

Cuando se utilizó `/stop` desde otro canal de voz mientras el bot estaba reproduciendo en un canal diferente, apareció:

```text
discord.errors.NotFound:
404 Not Found (error code: 10062): Unknown interaction
```

La causa está relacionada con:

* Interacción de Discord que supera el tiempo permitido para responder.
* Detención/desconexión de FFmpeg.
* Ejecución simultánea de eventos.
* `after_play()` intentando continuar la cola después de un `/stop`.

### 🔧 Mejoras pendientes

* Añadir `interaction.response.defer()`.
* Utilizar `interaction.followup.send()`.
* Validar que el usuario esté en el mismo canal de voz que el bot.
* Implementar un `asyncio.Lock` por servidor.
* Evitar que `after_play()` continúe después de un `/stop`.

---

# 👋 `/disconnect`

### Estado: pendiente

Se plantea agregar un comando independiente:

```text
/disconnect
```

Su función sería únicamente desconectar al bot del canal de voz.

Diferencia propuesta:

| Comando       | Acción                             |
| ------------- | ---------------------------------- |
| `/skip`       | Salta la canción                   |
| `/pause`      | Pausa                              |
| `/resume`     | Reanuda                            |
| `/stop`       | Detiene + limpia cola + desconecta |
| `/disconnect` | Solo desconecta                    |
| Fin de cola   | Desconexión automática             |

---

# 🔄 Reproducción automática

Cuando termina una canción, `after_play()` llama a:

```python
play_next_song(...)
```

Esto permite continuar automáticamente con la siguiente canción de la cola.

Cuando la cola queda vacía:

```python
await voice_client.disconnect()
```

Por lo tanto, actualmente el bot se desconecta automáticamente al terminar toda la cola.

---

# 🎧 FFmpeg

Se utiliza:

```python
discord.FFmpegOpusAudio(...)
```

Configuración actual:

```python
ffmpeg_options = {
    "before_options":
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options":
        "-vn -c:a libopus -b:a 96k",
}
```

FFmpeg se utiliza directamente desde:

```text
bin\ffmpeg\ffmpeg.exe
```

### ⚠️ Problema observado

En algunas operaciones aparecen mensajes:

```text
ffmpeg process XXXX has not terminated. Waiting to terminate...
```

Esto ocurre principalmente cuando se detiene una reproducción o se desconecta el bot.

No necesariamente significa que FFmpeg haya provocado el crash, pero debe manejarse mejor para evitar estados inconsistentes.

---

# 🔎 YouTube / yt-dlp

Actualmente las búsquedas utilizan:

```python
query = "ytsearch1: " + song_query
```

Esto funciona para:

```text
/play nombre de canción
```

Por ejemplo:

```text
/play música ascensor
/play un mamut chiquitito
```

---

# ⚠️ Problema con URLs y playlists

Se detectó que:

```python
ytsearch1:
```

no debe utilizarse directamente para procesar URLs de YouTube.

Ejemplo problemático:

```text
/play https://www.youtube.com/watch?v=xxxxx&list=xxxxx
```

El resultado puede ser:

```text
Downloading 0 items
```

y posteriormente:

```python
first_track = tracks[0]
```

produce:

```text
IndexError: list index out of range
```

### 🔧 Solución planteada

Diferenciar:

1. Búsqueda por texto.
2. URL de video.
3. URL de playlist.

Ejemplo conceptual:

```python
if is_url(song_query):
    results = await search_ytdlp_async(song_query, ydl_options)
else:
    results = await search_ytdlp_async(
        "ytsearch1:" + song_query,
        ydl_options
    )
```

---

# 🚫 Manejo de enlaces no compatibles

También se detectó que el bot puede recibir enlaces que no están pensados para reproducirse mediante el sistema actual.

Ejemplos:

* Instagram Reels
* TikTok
* Facebook Reels
* Otros enlaces no compatibles
* URLs inválidas
* Videos sin audio disponible

### 🔧 Mejora pendiente

Implementar una validación antes de enviar la consulta a `yt-dlp`.

Conceptualmente:

```text
Usuario
   ↓
/play
   ↓
¿Es texto?
 ├── Sí → ytsearch1
 │
 └── No → ¿URL compatible?
              ├── Sí → yt-dlp
              └── No → Mensaje de error
```

Además, envolver la extracción con:

```python
try:
    ...
except Exception:
    ...
```

para evitar que una entrada inválida provoque una excepción no controlada.

---

# 🛡️ Manejo de errores

## Objetivo

El bot no debería cerrarse por errores provocados por entradas del usuario.

Casos que deben manejarse:

* Búsqueda sin resultados.
* URL inválida.
* Playlist vacía.
* Video eliminado.
* Video privado.
* Video sin audio.
* Plataforma no compatible.
* Error de `yt-dlp`.
* Error de FFmpeg.
* Usuario fuera de un canal de voz.
* Bot no conectado.
* Usuario en otro canal de voz.
* Cola vacía.
* Ejecución simultánea de comandos.

---

# 🔒 Control por canal de voz

### Mejora pendiente

Actualmente un usuario puede ejecutar comandos aunque se encuentre en otro canal de voz.

Ejemplo:

```text
Canal A
👤 Usuario 1
🤖 Bot reproduciendo

Canal B
👤 Usuario 2
/stop
```

Esto puede generar conflictos.

### Comportamiento deseado

Los comandos de control deberían comprobar:

```text
¿Usuario está en un canal?
        ↓
¿Es el mismo canal que el bot?
        ↓
      Sí → Ejecutar
      No → Rechazar
```

Mensaje sugerido:

```text
❌ Debes estar en el mismo canal de voz que el bot.
```

---

# 🔐 Prevención de condiciones de carrera

### Mejora pendiente

Implementar un `asyncio.Lock` por servidor:

```python
GUILD_LOCKS = {}
```

Esto evitará problemas cuando varios usuarios ejecuten simultáneamente:

```text
/skip
/stop
/play
/disconnect
```

Especialmente mientras FFmpeg está terminando una reproducción.

---

# 📊 Estado actual

| Funcionalidad                    | Estado                          |
| -------------------------------- | ------------------------------- |
| `/play`                          | ✅ Implementado                  |
| Búsqueda YouTube                 | ✅ Implementado                  |
| Reproducción FFmpeg              | ✅ Implementado                  |
| Cola por servidor                | ✅ Implementado                  |
| `/pause`                         | ✅ Implementado                  |
| `/resume`                        | ✅ Implementado                  |
| `/skip`                          | ⚠️ Funciona / requiere robustez |
| `/stop`                          | ⚠️ Funciona / requiere robustez |
| `/queue`                         | ✅ Implementado                  |
| `/help`                          | ✅ Implementado                  |
| Auto siguiente canción           | ✅ Implementado                  |
| Auto-disconnect al terminar cola | ✅ Implementado                  |
| `/disconnect`                    | 🔧 Pendiente                    |
| Soporte URL YouTube              | 🔧 Pendiente                    |
| Soporte playlists                | 🔧 Pendiente                    |
| Validación de URLs               | 🔧 Pendiente                    |
| Manejo de Reels/TikTok/etc.      | 🔧 Pendiente                    |
| Manejo global de errores         | 🔧 Pendiente                    |
| Validación de canal de voz       | 🔧 Pendiente                    |
| Locks por servidor               | 🔧 Pendiente                    |
| Protección de `after_play()`     | 🔧 Pendiente                    |

---

# 🚀 Próximos pasos recomendados

## 1. 🛡️ Robustez

Prioridad alta:

* Manejo global de excepciones.
* Validación de resultados de `yt-dlp`.
* Manejo de URLs inválidas.
* Evitar `IndexError`.
* Evitar `Unknown interaction`.
* Protección de `after_play()`.

## 2. 🎧 Control de canales

Implementar:

* Validación del canal del usuario.
* `/disconnect`.
* Posiblemente auto-disconnect cuando no quedan usuarios.

## 3. 📋 Mejorar la cola

Agregar posteriormente:

* `/queue` paginado.
* `/remove <posición>`.
* `/clear`.
* `/shuffle`.

## 4. 🎵 Mejorar `/play`

Agregar:

* URLs de YouTube.
* Playlists.
* Shorts.
* Mejor detección de contenido no compatible.
* Límite de canciones por playlist.
* Información de duración.

## 5. 🎨 Mejorar interfaz

El mensaje de reproducción podría mostrar:

```text
🎧 NOW PLAYING

🎵 Nombre de la canción
⏱️ 03:42

🔗 YouTube

━━━━━━━━━━━━━━
👤 Solicitado por: Usuario
```

Posteriormente se puede agregar:

* duración
* miniatura
* enlace del video
* progreso
* posición en cola

---

# 🧠 Arquitectura actual

```text
Discord
   │
   ▼
Slash Commands
   │
   ├── /play
   │      │
   │      ▼
   │   yt-dlp
   │      │
   │      ▼
   │   SONG_QUEUES
   │      │
   │      ▼
   │    FFmpeg
   │
   ├── /pause
   ├── /resume
   ├── /skip
   ├── /stop
   ├── /queue
   └── /help
```

### Próxima arquitectura

```text
Discord
   │
   ▼
Command Validation
   │
   ├── Voice Channel Check
   ├── URL Validation
   └── Error Handling
   │
   ▼
Guild State / Lock
   │
   ▼
Queue Manager
   │
   ▼
yt-dlp
   │
   ▼
FFmpeg
   │
   ▼
Playback Manager
   │
   ├── Next Song
   ├── Skip
   ├── Stop
   └── Disconnect
```

---

# 📌 Objetivo del proyecto

Convertir el bot actual en un **music bot estable para uso continuo en servidores de Discord**, evitando que entradas inválidas, errores de YouTube/yt-dlp, FFmpeg o acciones simultáneas de usuarios provoquen el cierre del bot.
