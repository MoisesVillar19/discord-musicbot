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
| S1 Datos | `Track` dict, helpers de cola, `BOT_NAME`, tests `music/`, `.bat` portable | ✅ Hecho |
| S2 Voz robusta | `core/voice.py`, locks, validación canal, `/disconnect`, autodisconnect vacío | ✅ Hecho |
| S3 Playlists rápidas | `extract_flat`, validación URLs, JS runtime, límites documentados | ✅ Hecho |
| S4 Experiencia | `/nowplaying`, cola paginada, `shuffle/remove/move/clear`, embeds ricos | ✅ Hecho |
| S5 Alters + panel | Alters configurables + panel local tkinter (perfiles, start/stop, logs) | ✅ Hecho |
| S5.1 Seed + consola | `ensure_aliases()`, botón restablecer, consola propia del panel | ✅ Hecho |
| S6 Nombres base | R-01: repaso y renombre de canónicos con alters de compatibilidad | ✅ Hecho |
| S7 Multi-resultados | `ytsearch5` + select (B-09) | ✅ Hecho |
| S8 Trolls + historial | `music/trolls.py` + `/historial` (B-08, C-08) | 🔴 |
| S9 Ops | CI + Docker + decisión nube (C-05, C-06, C-09) | 🔴 |
| Futuro | `/lyrics` (spike), permisos DJ, panel v2 | 🔬/🔴 |

## Backlog

### A. Núcleo (ordenado por dependencia)

| ID | Ítem | Estado | Depende de | Sprint | Viabilidad vs S0 |
|---|---|---|---|---|---|
| A-01 | `Track` dict + retirar shim 3-tupla | ✅ | — | S1 | ✅ Superficie: 2 sitios (`/queue`, `play_next_song`); API `get_queue/clear_queue` intacta |
| A-02 | Helpers cola: `remove/move/shuffle/peek` + tests | ✅ | A-01 | S1 | ✅ Lógica pura, sin tocar voz |
| A-03 | `BOT_NAME` configurable | ✅ | — | S0 | ✅ Hecho |
| A-04 | `core/voice.py` (mover `play_next_song` tal cual) | ✅ | A-01 | S2 | ✅ Movimiento mecánico; firmas slash intactas |
| A-05 | `GUILD_LOCKS` en mutaciones voz/cola | ✅ | A-04 | S2 | ✅ Aditivo, sin choque |
| A-06 | `require_same_voice` en control + `play` | ✅ | A-04 | S2 | ✅ Aditivo; definir excepción `WrongChannel` en `utils/errors.py` |
| A-07 | `/disconnect` separado | ✅ | A-04 | S2 | ✅ Trivial tras A-04 |
| A-08 | `after_play` con guard de generación + vía única de apagado | ✅ | A-04 | S2 | ✅ Elimina la doble vía actual |
| A-09 | Autodisconnect con canal vacío (`on_voice_state_update` + timeout) | ✅ | A-04 | S2 | ✅ Evento nuevo, no altera reproducción |
| A-10 | `extract_flat="in_playlist"` + resolver al reproducir | ✅ | A-04 | S3 | ✅ Complementa `resolve_stream_url()` S0 (ADR-002); solo rama playlist |
| A-11 | Validación URLs (`utils/validators.py`): YouTube sí / resto mensaje claro | ✅ | — | S3 | ✅ Aditivo antes de llamar a yt-dlp |
| A-12 | Runtime JS para yt-dlp (Node.js/Deno) + nota en manuales | ✅ | — | S3 | ✅ Operativo, cero código |
| A-13 | Manejo global de errores (`on_app_command_error`) | ✅ | A-06 | S2/S3 | ✅ Aditivo; mapa error→mensaje en `utils/errors.py` |

### B. Experiencia de usuario

| ID | Ítem | Estado | Depende de | Sprint | Notas |
|---|---|---|---|---|---|
| B-01 | `/nowplaying` (lee `NOW_PLAYING`) | ✅ | A-04 | S4 | Requiere que voz escriba `NOW_PLAYING` (S2) |
| B-02 | Embed rico: duración, autor, thumbnail, link, solicitado_por | ✅ | A-01 | S4 | Requiere `Track` dict |
| B-03 | `/queue` paginada (embed + botones ⬅️/➡️) | ✅ | A-02 | S4 | `discord.ui.View`; independiente de voz |
| B-04 | `/shuffle` | ✅ | A-02 | S4 | 1 línea sobre el helper |
| B-05 | `/remove <n>`, `/clear` | ✅ | A-02 | S4 | Validar rango; mensajes claros |
| B-06 | `/move <origen> <destino>`, `/play … after:<n>` | ✅ | A-02 | S4 | `after:` es azúcar sobre `move`/insert |
| B-11 | `/next` (peek) + `/skip [cantidad]` diferenciados | ✅ | A-02 | S6 | Tabla skip/next/remove en manual; alter `siguiente`→`/next` |
| B-07 | Comandos alias (`/rolita`…) | 🔴 | — | S4/Futuro | Mantener pocos; ver idea en `primeros_pasos.md` |
| B-08 | Canciones troll (`music/trolls.py`) | 🔴 | A-01 | S8 | Mapeo búsqueda→URL fija; bajo valor, divertido |
| B-09 | Búsqueda multi-resultado (`ytsearch5` + select) | ✅ | A-01 | S7 | Select efímero; voz recién al elegir |
| B-10 | `/lyrics` (Genius/Musixmatch) | 🔬 | — | Futuro | Spike: auth, límites, ToS antes de prometer |

### C. Calidad y ops

| ID | Ítem | Estado | Sprint | Notas |
|---|---|---|---|---|
| C-01 | Tests `music/queue.py` (puros) | ✅ | S1 | Sin mocks; primera red de seguridad |
| C-02 | Tests `music/search.py` (mock yt-dlp) | ✅ | S1 | Mock `_extract` |
| C-03 | Logger a archivo (`utils/logger.py`) sustituyendo `print` | ✅ | S2 | Testigos: voz y search |
| C-04 | `start_bot.bat` portable (ruta relativa) | ✅ | S1 | Tarea menor |
| C-05 | `py_compile` + `unittest` en CI (Actions) | 🔴 | S9 | Sin FFmpeg ni token (tests mockean) |
| C-06 | Dockerfile + compose (VPS) | 🔴 | S9 | FFmpeg vía apt, no `bin/` |
| C-07 | Permisos DJ / roles por comando | 🔴 | Futuro | Tras errores globales |
| C-08 | Historial por guild (`/historial`) | 🔴 | S8 | Tras `NOW_PLAYING` |
| C-09 | Hosting nube 24/7 (decisión, plan ideal futuro) | 🔴 | S9 | Ver `futuro-hosting-247.md`; no necesario ahora |

### D. Alters configurables + panel local (solo admin local, sin web)

> Decisión: alters **solo slash** (consistente con los 7 comandos actuales),
> panel **app de escritorio tkinter** (cero dependencias, un solo administrador),
> nombres reales **solo en local** (`aliases.json` en `.gitignore`).
> Discord no tiene aliases nativos: cada alter es un slash command registrado
> que apunta a la misma lógica. Un bot = un proceso = N servidores;
> multi-instancia solo para bots distintos (ver `arquitectura.md` §5).

| ID | Ítem | Estado | Depende de | Sprint | Notas |
|---|---|---|---|---|---|
| D-01 | Extraer lógica compartida (`_do_play`, `_do_skip`, …) o cogs | ✅ | S4 (cogs) o fallback | S5 | Prerrequisito: canonical + alters comparten callback |
| D-02 | `aliases.json` local + `aliases.example.json` + loader con validación | ✅ | D-01 | S5 | Minúsculas, `^[\w-]{1,32}$`, sin colisiones, máx 5/comando |
| D-03 | Registro dinámico de slash por alter + `/help` dinámico | ✅ | D-02 | S5 | Límite 100 comandos globales; sobra para alters |
| D-04 | `GUILD_ID` opcional para sync instantáneo en desarrollo | ✅ | D-03 | S5 | Los comandos globales tardan ~1h en propagar |
| D-05 | Panel tkinter: perfiles, start/stop/restart, editor alters, editor `.env`, logs, re-sync | ✅ | D-03 | S5 | v1 simple: un bot local (perfiles múltiples → futuro); 1 perfil basta para N servidores |
| D-06 | `panel.bat` + reutilizar `icono.ico` + manual del panel | ✅ | D-05 | S5 | — |
| D-07 | `ensure_aliases()`: autocrear `aliases.json` + botón restablecer | ✅ | D-02 | S5.1 | Clonar → correr sin copiar nada |
| D-08 | Panel abre consola propia del bot + toggle (dev visible, prod oculta) | ✅ | D-05 | S5.1 | Mismo detalle en vivo que `start_bot.bat` |

### R. Revisión post-sprints
| ID | Ítem | Estado | Sprint | Notas |
|---|---|---|---|---|
| R-01 | Revisión de nombres base canónicos | ✅ | S6 | Veredicto: se quedan en inglés; ES por alters (auditoría §5)

## Qué se declara obsoleto (no entra al roadmap)

- Nombre fijo "DJ Gilmer"/"DJ Huevito" → `BOT_NAME` (A-03, hecho).
- Estructura plana `bot.py`-todo → migración por sprints (`arquitectura.md`).
- `ytsearch1:` literal como única estrategia → `search_ytdlp()` actual.
- Idea "editar `.bat` en escritorio con icono" como distribución → instalador/ops
  serio en C-06; el `.bat` queda como arranque local (C-04).
