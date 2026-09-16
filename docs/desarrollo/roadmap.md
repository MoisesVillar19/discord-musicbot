# Roadmap — MusicBot

> Backlog priorizado con viabilidad frente al código S0. Cada ítem indica
> dependencias y sprint. Detalle de ejecución en `sprints.md`;
> criterios de aceptación en `casos.md`.

## Leyenda
✅ hecho (S0) · 🟡 parcial · 🔴 pendiente · 🔬 spike (investigar antes de comprometer)

## Hitos

| Hito | Contenido | Estado |
|---|---|---|
| S0 Estabilización | Cola 3-tuplas, `ytsearch` texto, `resolve_stream_url`, FFmpeg portable, token check, docs base | ✅ Hecho |
| S1 Datos | `Track` dict, helpers de cola, `BOT_NAME`, tests `music/`, `.bat` portable | 🔴 Siguiente |
| S2 Voz robusta | `core/voice.py`, locks, validación canal, `/disconnect`, autodisconnect vacío | 🔴 |
| S3 Playlists rápidas | `extract_flat`, validación URLs, JS runtime, límites documentados | 🔴 |
| S4 Experiencia | `/nowplaying`, cola paginada, `shuffle/remove/move/clear`, embeds ricos | 🔴 |
| Futuro | multi-resultados, `/lyrics`, permisos DJ, historial, nube, Docker, CI | 🔬/🔴 |

## Backlog

### A. Núcleo (ordenado por dependencia)

| ID | Ítem | Estado | Depende de | Sprint | Viabilidad vs S0 |
|---|---|---|---|---|---|
| A-01 | `Track` dict + retirar shim 3-tupla | 🟡 | — | S1 | ✅ Superficie: 2 sitios (`/queue`, `play_next_song`); API `get_queue/clear_queue` intacta |
| A-02 | Helpers cola: `remove/move/shuffle/peek` + tests | 🔴 | A-01 | S1 | ✅ Lógica pura, sin tocar voz |
| A-03 | `BOT_NAME` configurable | ✅ | — | S0 | ✅ Hecho |
| A-04 | `core/voice.py` (mover `play_next_song` tal cual) | 🔴 | A-01 | S2 | ✅ Movimiento mecánico; firmas slash intactas |
| A-05 | `GUILD_LOCKS` en mutaciones voz/cola | 🔴 | A-04 | S2 | ✅ Aditivo, sin choque |
| A-06 | `require_same_voice` en control + `play` | 🔴 | A-04 | S2 | ✅ Aditivo; definir excepción `WrongChannel` en `utils/errors.py` |
| A-07 | `/disconnect` separado | 🔴 | A-04 | S2 | ✅ Trivial tras A-04 |
| A-08 | `after_play` con guard de generación + vía única de apagado | 🟡 | A-04 | S2 | ✅ Elimina la doble vía actual |
| A-09 | Autodisconnect con canal vacío (`on_voice_state_update` + timeout) | 🔴 | A-04 | S2 | ✅ Evento nuevo, no altera reproducción |
| A-10 | `extract_flat="in_playlist"` + resolver al reproducir | 🔴 | A-04 | S3 | ✅ Complementa `resolve_stream_url()` S0 (ADR-002); solo rama playlist |
| A-11 | Validación URLs (`utils/validators.py`): YouTube sí / resto mensaje claro | 🔴 | — | S3 | ✅ Aditivo antes de llamar a yt-dlp |
| A-12 | Runtime JS para yt-dlp (Node.js/Deno) + nota en manuales | 🔴 | — | S3 | ✅ Operativo, cero código |
| A-13 | Manejo global de errores (`on_app_command_error`) | 🔴 | A-06 | S2/S3 | ✅ Aditivo; mapa error→mensaje en `utils/errors.py` |

### B. Experiencia de usuario

| ID | Ítem | Estado | Depende de | Sprint | Notas |
|---|---|---|---|---|---|
| B-01 | `/nowplaying` (lee `NOW_PLAYING`) | 🔴 | A-04 | S4 | Requiere que voz escriba `NOW_PLAYING` (S2) |
| B-02 | Embed rico: duración, autor, thumbnail, link, solicitado_por | 🔴 | A-01 | S4 | Requiere `Track` dict |
| B-03 | `/queue` paginada (embed + botones ⬅️/➡️) | 🔴 | A-02 | S4 | `discord.ui.View`; independiente de voz |
| B-04 | `/shuffle` | 🔴 | A-02 | S4 | 1 línea sobre el helper |
| B-05 | `/remove <n>`, `/clear` | 🔴 | A-02 | S4 | Validar rango; mensajes claros |
| B-06 | `/move <origen> <destino>`, `/play … after:<n>` | 🔴 | A-02 | S4 | `after:` es azúcar sobre `move`/insert |
| B-07 | Comandos alias (`/rolita`…) | 🔴 | — | S4/Futuro | Mantener pocos; ver idea en `primeros_pasos.md` |
| B-08 | Canciones troll (`music/trolls.py`) | 🔴 | A-01 | Futuro | Mapeo búsqueda→URL fija; bajo valor, divertido |
| B-09 | Búsqueda multi-resultado (`ytsearch5` + select) | 🔴 | A-01 | Futuro | Select menu; moderado |
| B-10 | `/lyrics` (Genius/Musixmatch) | 🔬 | — | Futuro | Spike: auth, límites, ToS antes de prometer |

### C. Calidad y ops

| ID | Ítem | Estado | Sprint | Notas |
|---|---|---|---|---|
| C-01 | Tests `music/queue.py` (puros) | 🔴 | S1 | Sin mocks; primera red de seguridad |
| C-02 | Tests `music/search.py` (mock yt-dlp) | 🔴 | S1 | Mock `_extract` |
| C-03 | Logger a archivo (`utils/logger.py`) sustituyendo `print` | 🔴 | S2 | Testigos: voz y search |
| C-04 | `start_bot.bat` portable (ruta relativa) | 🔴 | S1 | Tarea menor |
| C-05 | Ruff + `py_compile` en CI | 🔴 | Futuro | Tras estabilizar imports |
| C-06 | Dockerfile + compose (VPS) | 🔴 | Futuro | FFmpeg vía apt, no `bin/` |
| C-07 | Permisos DJ / roles por comando | 🔴 | Futuro | Tras errores globales |
| C-08 | Historial por guild | 🔴 | Futuro | Tras `NOW_PLAYING` |
| C-09 | Hosting nube 24/7 | 🔴 | Futuro | Decisión de costo; local hasta S4 |

## Qué se declara obsoleto (no entra al roadmap)

- Nombre fijo "DJ Gilmer"/"DJ Huevito" → `BOT_NAME` (A-03, hecho).
- Estructura plana `bot.py`-todo → migración por sprints (`arquitectura.md`).
- `ytsearch1:` literal como única estrategia → `search_ytdlp()` actual.
- Idea "editar `.bat` en escritorio con icono" como distribución → instalador/ops
  serio en C-06; el `.bat` queda como arranque local (C-04).
