# 🎧 Discord Music Bot — Avances del Proyecto

## 📌 Estado actual

Bot de música para Discord desarrollado en **Python**, utilizando:

- `discord.py`
- `yt-dlp`
- `PyNaCl`
- `python-dotenv`
- `FFmpeg`

El bot ya fue configurado, conectado a Discord y probado exitosamente en un servidor.

---

# ✅ Funcionalidades implementadas

## 🎵 Reproducción

### `/play <canción>`

Permite buscar una canción mediante `yt-dlp` y reproducirla en el canal de voz.

Flujo:

```text
Usuario
   ↓
/play canción
   ↓
yt-dlp busca en YouTube
   ↓
Obtiene URL de audio
   ↓
FFmpeg procesa el audio
   ↓
Discord reproduce la canción
```

También permite agregar canciones a la cola si ya existe una reproducción activa.

---

## 📋 Sistema de cola

Se utiliza:

```python
SONG_QUEUES = {}
```

con `deque` para administrar las canciones pendientes.

Cada servidor tiene su propia cola.

Ejemplo:

```text
🎵 Reproduciendo:
In The End

📋 Cola:
1. Numb
2. Faint
3. Breaking the Habit
```

---

## ⏸️ Pausar

### `/pause`

Pausa la canción que está reproduciéndose.

---

## ▶️ Reanudar

### `/resume`

Continúa una canción que había sido pausada.

---

## ⏭️ Saltar

### `/skip`

Detiene la canción actual y permite que se reproduzca automáticamente la siguiente canción de la cola.

---

## ⛔ Detener

### `/stop`

Realiza:

- Detener reproducción.
- Vaciar la cola.
- Desconectar al bot del canal de voz.

---

## 📋 Ver cola

### `/queue`

Muestra las canciones pendientes del servidor.

Actualmente la lista se muestra como mensaje temporal (`ephemeral`), por lo que solamente la ve quien ejecuta el comando.

---

## ❓ Ayuda

### `/help`

Se agregó un comando personalizado que muestra los comandos principales.

Actualmente:

```text
🎧 Comandos de DJ Gilmer

▶ /play <canción> — Reproduce o agrega a la cola
⏸ /pause — Pausa la música
▶ /resume — Reanuda
⏭ /skip — Salta canción
⛔ /stop — Detiene todo
```

La ayuda puede mejorarse posteriormente con embeds, categorías y nuevos comandos.

---

# 🎨 Personalización

El bot ya comenzó a personalizarse para darle una identidad propia.

Actualmente se utiliza el nombre:

```text
DJ Gilmer
```

y posteriormente se pueden personalizar:

- Nombre del bot.
- Icono.
- Nombres de comandos.
- Mensajes.
- Emojis.
- Embeds.
- Colores.
- Footer.
- Nombre de la cola.
- Mensajes de reproducción.

---

# 🖼️ Embeds

Se comenzó a utilizar `discord.Embed` para mostrar la canción actualmente reproducida de una manera más visual.

Ejemplo conceptual:

```text
┌─────────────────────────────┐
│ 🎧 Now Playing              │
│                             │
│ 🎵 In The End              │
│                             │
│ ⏱ 3:36     📺 YouTube      │
│                             │
│ DJ Gilmer                   │
└─────────────────────────────┘
```

---

# 📊 Próxima mejora: metadatos

Se planea utilizar la información que ya proporciona `yt-dlp`.

Datos útiles:

```python
title
duration
uploader
webpage_url
```

### Información prevista

- 🎵 Nombre de la canción.
- ⏱ Duración.
- 👤 Artista/canal.
- 🔗 Enlace al video de YouTube.

La información podrá utilizarse tanto en `/play` como en el mensaje automático de **Now Playing**.

---

# 🎧 Próximo comando: `/nowplaying`

Objetivo:

Mostrar la canción que está sonando actualmente.

Ejemplo:

```text
🎧 Reproduciendo ahora

🎵 In The End
👤 Linkin Park
⏱ 3:36
📺 Ver en YouTube
```

Para esto será necesario guardar temporalmente la canción actual por servidor.

Posible estructura:

```python
NOW_PLAYING = {}
```

---

# 🔗 Enlaces de YouTube

Se quiere mostrar el enlace del video utilizado como fuente.

`yt-dlp` proporciona:

```python
webpage_url
```

Esto permitirá colocar en el embed algo como:

```text
📺 Ver en YouTube
```

sin tener que mostrar una URL larga.

---

# 🎛️ Alias / comandos personalizados

Se confirmó que es posible tener comandos alternativos para una misma función.

Ejemplo:

```text
/play
/rolita
```

Ambos podrían reproducir música, pero `/play` se mantendría como comando reconocible para usuarios nuevos.

Posibles nombres personalizados:

```text
/rolita
/temazo
/ponmusica
/dj
```

La idea es mantener los comandos estándar y agregar pocos comandos personalizados para evitar confusión.

---

# 🔮 Funcionalidades futuras

## 🔎 Búsqueda con múltiples resultados

Actualmente se utiliza:

```text
ytsearch1:
```

por lo que se obtiene únicamente el primer resultado.

Futuro:

```text
ytsearch5:
```

o una cantidad similar para mostrar varias opciones.

Ejemplo:

```text
🔎 Resultados para: "Te quiero"

1️⃣ Te Quiero — Hombres G
2️⃣ Te Quiero — Ricardo Arjona
3️⃣ Te Quiero — ...
4️⃣ Te Quiero — ...
5️⃣ Te Quiero — ...
```

El usuario podría seleccionar cuál reproducir.

---

## 📖 Paginación

Para búsquedas con muchos resultados se quiere implementar un sistema por páginas.

Ejemplo:

```text
🔎 Resultados — Página 1/3

1️⃣ Canción A
2️⃣ Canción B
3️⃣ Canción C
4️⃣ Canción D
5️⃣ Canción E

⬅️ Anterior     ➡️ Siguiente
```

Esto probablemente utilizará:

```python
discord.ui.View
discord.ui.Button
```

---

## 🎤 Letras de canciones

Se planteó agregar un comando:

```text
/lyrics
```

que permita consultar la letra de la canción actual o buscar la letra de una canción.

Esta función queda pendiente porque requiere integrar una fuente/API de letras y revisar sus límites y condiciones de uso.

---

## 🔀 Shuffle

Se considera agregar:

```text
/shuffle
```

para mezclar aleatoriamente las canciones pendientes de la cola.

Ejemplo:

```text
📋 Cola original:

1. A
2. B
3. C
4. D

        ↓ /shuffle

🔀 Cola mezclada:

1. C
2. A
3. D
4. B
```

---

# 🏠 Ejecución del bot

Actualmente el bot se ejecuta localmente.

Comando:

```bash
python bot.py
```

o mediante un archivo `.bat`.

Mientras el proceso esté ejecutándose, el bot permanece conectado a Discord.

Si se cierra la terminal/proceso, el bot se desconecta.

---

# 🖥️ Acceso directo

Se creó un `.bat` para facilitar el arranque del bot sin tener que abrir manualmente VS Code.

La idea es poder ejecutar:

```text
DJ Gilmer Bot.bat
```

desde el escritorio.

También se personalizó el acceso directo con un archivo:

```text
icono.ico
```

El icono tuvo problemas de calidad en algunos tamaños del acceso directo de Windows, por lo que queda como detalle visual pendiente de perfeccionar.

---

# 🔐 Seguridad

El token del bot se almacena en:

```text
.env
```

Ejemplo:

```env
DISCORD_TOKEN=TU_TOKEN
```

El archivo `.env` **no debe compartirse ni subirse a GitHub**.

Se recomienda agregar:

```text
.env
venv/
__pycache__/
```

al `.gitignore`.

---

# 📁 Estructura actual del proyecto

```text
discord-music-bot/
│
├── bot.py
├── .env
├── requirements.txt
│
├── bin/
│   └── ffmpeg/
│       └── ffmpeg.exe
│
└── venv/
```

---

# 📦 Dependencias

Instaladas mediante:

```bash
pip install discord.py python-dotenv yt-dlp PyNaCl
```

Dependencias principales:

| Dependencia | Función |
|---|---|
| `discord.py` | Comunicación con Discord y comandos |
| `python-dotenv` | Lectura segura del `.env` |
| `yt-dlp` | Búsqueda y extracción de audio |
| `PyNaCl` | Soporte para conexiones de voz |
| `FFmpeg` | Procesamiento/transmisión del audio |

---

# 🧭 Roadmap

## 🟢 Completado

- [x] Crear aplicación/bot en Discord Developer Portal.
- [x] Configurar permisos necesarios.
- [x] Invitar bot al servidor.
- [x] Crear proyecto Python.
- [x] Crear entorno virtual.
- [x] Instalar dependencias.
- [x] Configurar `.env`.
- [x] Configurar FFmpeg.
- [x] Conectar bot a Discord.
- [x] `/play`
- [x] Sistema de cola.
- [x] `/pause`
- [x] `/resume`
- [x] `/skip`
- [x] `/stop`
- [x] `/queue`
- [x] `/help`
- [x] Embeds básicos.
- [x] Prueba real de reproducción.
- [x] Crear método de ejecución mediante `.bat`.

## 🟡 Siguiente etapa

- [ ] Mejorar `/help`.
- [ ] Personalizar todos los mensajes al español.
- [ ] Personalizar nombres de comandos.
- [ ] Mejorar embeds.
- [ ] Mostrar duración.
- [ ] Mostrar artista/canal.
- [ ] Mostrar enlace de YouTube.
- [ ] Implementar `/nowplaying`.
- [ ] Guardar correctamente la canción actualmente reproducida.
- [ ] Agregar `/shuffle`.

## 🔵 Etapa futura

- [ ] Búsqueda con múltiples resultados.
- [ ] Selección interactiva de canciones.
- [ ] Paginación.
- [ ] Botones de navegación.
- [ ] `/lyrics`.
- [ ] Mejoras visuales.
- [ ] Control de permisos para comandos de DJ.
- [ ] Mejor manejo de errores.
- [ ] Historial de canciones.
- [ ] Autodesconexión después de cierto tiempo sin usuarios.
- [ ] Posible alojamiento en la nube.

---

# 💡 Idea general del bot

El objetivo no es solamente tener un bot que reproduzca música, sino construir un pequeño **DJ de Discord personalizado**, manteniendo comandos reconocibles para los usuarios y agregando funciones propias.

Concepto:

```text
                 🎧 DJ GILMER
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    🎵 Música       📋 Cola       🎛️ Control
       │              │              │
     /play          /queue       /pause
     /rolita        /shuffle     /resume
                    /nowplaying  /skip
                                  /stop

                 🔮 Futuro
                    │
          ┌─────────┼─────────┐
          ↓         ↓         ↓
       🔎 Buscar  🎤 Letras  📖 Páginas
       resultados
```

## 📝 Nota

Este documento representa el estado del proyecto hasta la implementación del sistema básico de reproducción, cola, controles, `/queue`, `/help` y embeds.

Las funcionalidades marcadas como **futuras** todavía no forman parte del código actual.
