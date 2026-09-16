# 🎧 DJ Huevito — Avances del proyecto

## 📌 Estado actual

El bot de música de Discord se encuentra en proceso de refactorización para separar responsabilidades y facilitar la incorporación de nuevas funcionalidades.

La prioridad actual es mantener la funcionalidad existente mientras se reorganiza el código, antes de implementar las nuevas características.

---

# 🏗️ Refactorización

## Estructura inicial

El código principal estaba concentrado en:

```text
bot.py
```

Actualmente se comenzó a separar la lógica en módulos:

```text
MusicBot/
│
├── bot.py
├── config.py
│
├── music/
│   ├── queue.py
│   └── search.py
│
└── ...
```

La idea es continuar separando posteriormente la reproducción de audio y la gestión de voz.

---

# 🎵 `music/queue.py`

Se creó un sistema independiente para manejar las colas por servidor.

Actualmente contiene:

```python
from collections import deque

SONG_QUEUES = {}

def get_queue(guild_id: str) -> deque:
    if guild_id not in SONG_QUEUES:
        SONG_QUEUES[guild_id] = deque()
    return SONG_QUEUES[guild_id]

def clear_queue(guild_id: str):
    if guild_id in SONG_QUEUES:
        SONG_QUEUES[guild_id].clear()
```

## Funcionalidades

- Cola independiente para cada servidor.
- Crear automáticamente una cola si no existe.
- Limpiar la cola.
- Se eliminó la necesidad de manejar `SONG_QUEUES` directamente desde `bot.py`.

---

# 🔎 `music/search.py`

Se comenzó a mover la lógica relacionada con `yt-dlp` fuera de `bot.py`.

Actualmente `search_ytdlp()` se encarga de:

- Ejecutar yt-dlp de forma asíncrona.
- Buscar canciones.
- Procesar URLs.
- Detectar playlists.
- Obtener información de las canciones.
- Aplicar límites a las playlists.
- Permitir seleccionar desde qué posición de la playlist comenzar.
- Ignorar canciones no disponibles.

Conceptualmente:

```text
Usuario
   │
   ▼
/play
   │
   ▼
music.search
   │
   ▼
yt-dlp
   │
   ▼
Lista normalizada de tracks
```

---

# 📂 Playlists

Se añadió soporte para playlists.

El usuario puede utilizar:

```text
/play <playlist>
```

Y el bot puede agregar varias canciones a la cola.

También se planteó el uso de parámetros:

```text
/play <playlist> start:20 limit:30
```

Lo que significa:

- `start:20` → comenzar desde la canción #20.
- `limit:30` → agregar como máximo 30 canciones.

Se estableció un límite máximo para evitar cargar playlists excesivamente grandes.

---

# 📊 Información de playlists

Se implementó la idea de mostrar información adicional cuando se detecta una playlist.

Ejemplo:

```text
📂 Playlist detectada
➕ Agregadas 47 canciones
⚠️ 3 no disponibles
📌 Desde la #1 de 213
```

La información contempla:

- Cantidad de canciones agregadas.
- Cantidad de canciones no disponibles.
- Posición desde la que comenzó.
- Cantidad total de canciones de la playlist.

---

# ⚠️ Manejo de canciones no disponibles

Se detectó que las playlists pueden contener:

- Videos eliminados.
- Videos privados.
- Videos bloqueados.
- Videos no disponibles por región.

Se añadió:

```python
"ignoreerrors": True
```

para evitar que una canción no disponible provoque el fallo completo del comando.

La idea es:

```text
Playlist
   │
   ├── Canción válida → agregar
   ├── Canción válida → agregar
   ├── Video eliminado → ignorar
   ├── Canción válida → agregar
   └── Video privado → ignorar
```

---

# 🔊 Reproducción actual

La reproducción todavía se encuentra principalmente en `bot.py`.

Actualmente se utiliza:

```python
discord.FFmpegOpusAudio(...)
```

con opciones de reconexión:

```python
"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
```

Y:

```python
"-vn -c:a libopus -b:a 96k"
```

---

# ⏯️ Comandos implementados

Actualmente existen:

```text
/play
/pause
/resume
/skip
/stop
/queue
/help
```

## `/play`

Permite:

- Buscar canciones.
- Usar URLs.
- Agregar canciones a la cola.
- Detectar playlists.
- Agregar varias canciones de una playlist.
- Seleccionar posición inicial de playlist.
- Limitar cantidad de canciones.

---

## `/pause`

Pausa la canción actual.

---

## `/resume`

Reanuda una canción pausada.

---

## `/skip`

Salta la canción actual.

Se detectó posteriormente que necesita mejoras relacionadas con el canal de voz.

---

## `/stop`

Detiene la reproducción, limpia la cola y desconecta al bot.

Se solucionó un problema donde Discord mostraba:

```text
404 Not Found
Unknown interaction
```

El problema estaba relacionado con que la operación de `stop` tardaba demasiado antes de responder a la interacción.

Se cambió el flujo para utilizar:

```python
await interaction.response.defer(ephemeral=True)
```

y posteriormente enviar/editar una respuesta mediante `followup`.

Actualmente `/stop`:

- Ejecuta la detención rápidamente.
- Limpia la cola.
- Desconecta al bot.
- Evita el error `Unknown interaction`.

Todavía existe un retraso visual en la respuesta de Discord, aunque la acción se ejecuta inmediatamente.

---

# 🔇 Auto-deafen

Se añadió la intención de que el bot entre ensordecido al canal de voz.

La forma correcta es conectar utilizando:

```python
await voice_channel.connect(self_deaf=True)
```

No se debe utilizar:

```python
await vc.edit(deafen=True)
```

porque `VoiceClient` no dispone de ese método.

---

# 🐛 Problema detectado con la estructura de la cola

Al comenzar a guardar más información por canción se pasó de:

```python
(audio_url, title)
```

a:

```python
(audio_url, title, webpage_url)
```

Sin embargo, `play_next_song()` todavía esperaba:

```python
audio_url, title = queue.popleft()
```

Esto produjo:

```text
ValueError: too many values to unpack (expected 2)
```

## Solución pendiente

Se considera conveniente pasar progresivamente de tuplas a una estructura de track más clara, por ejemplo:

```python
{
    "title": "...",
    "webpage_url": "...",
    "duration": ...
}
```

Esto permitirá agregar posteriormente:

- URL
- duración
- autor
- thumbnail
- posición
- usuario que añadió la canción
- etc.

sin romper el código cada vez que se añada un nuevo campo.

---

# ⚠️ Problema actual con playlists

Se detectó un problema importante:

Actualmente `yt-dlp` está procesando las canciones de la playlist de forma completa antes de comenzar la reproducción.

Esto provoca:

```text
Playlist
   │
   ├── analizar canción 1
   ├── analizar canción 2
   ├── analizar canción 3
   ├── analizar canción 4
   ├── ...
   └── analizar canción N
             │
             ▼
       comenzar reproducción
```

Por lo tanto aparecen muchos warnings en la consola antes de que comience la primera canción.

Esto genera una demora considerable.

---

# 🔧 Solución planteada para playlists

Se identificó que la búsqueda debería utilizar extracción plana para playlists:

```python
"extract_flat": "in_playlist"
```

De esta manera:

```text
Playlist
   │
   ▼
Obtener información ligera
   │
   ▼
Agregar canciones a la cola
   │
   ▼
Comenzar reproducción
   │
   ▼
Resolver audio SOLO de la canción actual
```

Esto permitirá evitar procesar completamente todas las canciones antes de reproducir la primera.

---

# ⚠️ Warning de JavaScript Runtime

yt-dlp actualmente muestra:

```text
No supported JavaScript runtime could be found.
```

Esto indica que YouTube está requiriendo cada vez más un runtime de JavaScript para determinadas partes de la extracción.

Por ahora:

- No es el principal problema del bot.
- Algunas extracciones todavía funcionan.
- Se deberá solucionar posteriormente instalando/configurando un runtime compatible.

---

# 🧠 Arquitectura objetivo

La arquitectura que se busca alcanzar progresivamente es:

```text
                    ┌──────────────┐
                    │    bot.py    │
                    │ Discord UI   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  search  │ │  queue   │ │   voice  │
        │          │ │          │ │          │
        │ yt-dlp   │ │  Cola    │ │ FFmpeg   │
        └──────────┘ └──────────┘ └──────────┘
```

## Responsabilidades

### `bot.py`

Debe encargarse principalmente de:

- Registrar comandos.
- Recibir interacciones de Discord.
- Validar permisos/canal.
- Mostrar mensajes.
- Llamar a los módulos correspondientes.

No debería contener toda la lógica interna de reproducción.

---

### `music/search.py`

Responsable de:

- yt-dlp.
- Búsquedas.
- URLs.
- Playlists.
- Metadata.
- Disponibilidad.
- Resolución de información.

---

### `music/queue.py`

Responsable de:

- Crear colas.
- Agregar canciones.
- Eliminar canciones.
- Reordenar canciones.
- Limpiar colas.
- Consultar posición.

---

### `core/voice.py`

Módulo que se implementará posteriormente.

Será responsable de:

- Conectar al canal de voz.
- Mover el bot.
- Desconectar.
- Reproducir.
- FFmpeg.
- Detectar final de canción.
- Pasar automáticamente a la siguiente.
- Skip.
- Stop.
- Resolver el audio justo antes de reproducir.

---

# 🚧 Funcionalidades pendientes

## 🎵 Interfaz de reproducción

Agregar:

- Link de la canción en el título.
- Duración.
- Artista/autor.
- Thumbnail.
- Otros metadatos útiles.

Ejemplo objetivo:

```text
🎧 Now Playing

🎵 Faint
👤 Linkin Park
⏱️ 2:42

🔗 Ver canción
```

---

## 🧌 Canciones troll

Agregar canciones especiales como:

- Whistle
- Yeyeyeye / Trololo
- Never Gonna Give You Up
- Barra Metal
- Gary vs David

La idea es posteriormente crear un sistema para que determinadas búsquedas o comandos puedan activar estas canciones.

---

## 🗑️ Eliminar canciones de la cola

Ejemplo:

```text
/queue
```

y posteriormente:

```text
/remove 4
```

para eliminar la canción #4.

---

## 🔀 Reordenar la cola

Permitir:

```text
/move 8 2
```

para mover la canción #8 a la posición #2.

También se plantea permitir:

```text
/play <canción> after:3
```

para agregar una canción después de una canción específica de la cola.

---

## 📜 Letras

Agregar un comando como:

```text
/lyrics
```

o:

```text
/lyrics <canción>
```

Utilizando APIs como:

- Musixmatch
- Genius / LyricGenius

Se deberá revisar posteriormente disponibilidad, autenticación y condiciones de uso de cada API.

---

## 🎼 Mejoras de búsqueda

Posteriormente se puede implementar:

```text
/play <texto>
```

→ mostrar una lista de resultados.

Ejemplo:

```text
🔎 Resultados para: te quiero

1️⃣ Te Quiero — Hombres G
2️⃣ Te Quiero — Ricardo Arjona
3️⃣ Te Quiero — ...
4️⃣ Te Quiero — ...
5️⃣ Te Quiero — ...
```

Y permitir seleccionar una opción.

---

## 🔗 Validación de URLs

Objetivo:

Si el usuario proporciona un link no compatible:

```text
❌ No puedo reproducir este enlace.
```

Sin provocar crash.

---

## 🔄 Evitar resultados incorrectos

Actualmente puede ocurrir que:

```text
Usuario:
https://youtube.com/watch?v=...

Bot:
reproduce otro video
```

Se deberá mejorar la validación para que cuando el usuario proporcione una URL directa:

- Se respete el video solicitado.
- No se trate como una búsqueda de texto.
- Si el video no está disponible, se informe.
- No se busque automáticamente otro video.

---

# 🎯 Próximo paso recomendado

El siguiente paso de la refactorización es:

## `core/voice.py`

Mover desde `bot.py`:

```python
play_next_song()
```

y toda la lógica relacionada con:

- FFmpeg
- reproducción
- `VoiceClient`
- conexión
- desconexión
- callback `after_play`

Esto permitirá posteriormente solucionar de forma más limpia:

- retrasos de `/stop`
- `/skip`
- reproducción de playlists
- resolución tardía de audio
- procesos FFmpeg
- reproducción automática de la siguiente canción
- reordenamiento de cola

---

# 📌 Estado general

### Ya realizado

- [x] Refactor inicial de cola
- [x] `music/queue.py`
- [x] Refactor inicial de búsqueda
- [x] `music/search.py`
- [x] Búsqueda de canciones
- [x] URLs
- [x] Soporte inicial de playlists
- [x] Límite de canciones
- [x] Posición inicial de playlist
- [x] Ignorar canciones no disponibles
- [x] Mensaje informativo de playlist
- [x] `/play`
- [x] `/pause`
- [x] `/resume`
- [x] `/skip`
- [x] `/stop`
- [x] `/queue`
- [x] `/help`
- [x] Auto-deafen al conectar
- [x] Corrección del `Unknown interaction` de `/stop`

### En proceso

- [ ] Extracción plana de playlists
- [ ] Resolver audio únicamente al reproducir
- [ ] Estructura definitiva de `Track`
- [ ] `core/voice.py`

### Pendiente

- [ ] Mejor interfaz Now Playing
- [ ] Links de canciones
- [ ] Metadatos
- [ ] Canciones troll
- [ ] Eliminar canciones
- [ ] Mover canciones
- [ ] Letras
- [ ] Búsqueda con selección de resultados
- [ ] Validación de URLs
- [ ] Evitar resultados incorrectos
- [ ] Comandos alternativos
- [ ] Mejor manejo de errores
- [ ] Mejoras de FFmpeg
- [ ] Runtime JS para yt-dlp
