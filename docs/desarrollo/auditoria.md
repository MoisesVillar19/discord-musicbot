# Auditoría — contraste del README con los docs previos

> Compara el estado real del código (Sprint 0) con la trilogía de
> `docs/desarrollo/`: `primeros_pasos.md` → `algunos errores.md` →
> `refactorizacionV1.md`. Orden de lectura recomendado: ese mismo.
> Leyenda: ✅ hecho · 🟡 parcial/mitigado · 🔴 pendiente · ⬜ obsoleto.

## 1. `primeros_pasos.md` (idea inicial)

| Afirmación del doc | Estado real (S0) | Acción |
|---|---|---|
| Bot "DJ Gilmer", comandos y mensajes fijos | ⬜ Obsoleto: el código decía "DJ Huevito"; ahora `BOT_NAME` configurable (ADR-004) | Actualizar docs viejos solo si se releen; el nombre canónico del repo es **MusicBot** |
| Estructura `bot.py + .env + bin/ + venv/` | ⬜ Obsoleta: ya existe `config.py`, `music/queue.py`, `music/search.py` | No reescribir el doc (es histórico); la estructura vigente está en `arquitectura.md` §1 |
| `/play` con `ytsearch1:` primer resultado | 🟡 Parcial: `search_ytdlp()` usa `ytsearch:` + `default_search`, 1er resultado | Vigente en comportamiento; el detalle `ytsearch1:` es histórico |
| Cola `SONG_QUEUES` dict de `deque` por servidor | ✅ Hecho (`music/queue.py`) | — |
| `/pause`, `/resume`, `/skip`, `/stop`, `/queue`, `/help` | ✅ Hechos | — |
| `/queue` ephemeral | ✅ Hecho (se mantiene; paginación en S4) | — |
| Embed "Now Playing" básico | ✅ Hecho (título + color; sin duración/autor/thumbnail) | Enriquecer en S4 (depende de `Track` S1) |
| Roadmap "siguiente etapa": personalizar mensajes, duración, artista, enlace, `/nowplaying`, guardar canción actual, `/shuffle` | 🔴 Pendiente (casi todo) | Recogido en `roadmap.md` (S1–S4) |
| Roadmap "etapa futura": multi-resultados, paginación, botones, `/lyrics`, permisos DJ, historial, autodesconexión, nube | 🔴 Pendiente | Recogido en `roadmap.md` como backlog |
| `.bat` + `icono.ico` con detalle visual pendiente | 🟡 El `.bat` existe (ruta fija `D:\MusicBot`); icono en repo | Hacer el `.bat` portable (relativo) en S1 como tarea menor |
| `.gitignore` con `.env`, `venv/`, `__pycache__/` | ✅ Hecho (más `bin/`) | — |

## 2. `algunos errores.md` (fase debugging)

| Afirmación del doc | Estado real (S0) | Acción |
|---|---|---|
| `/stop` → `404 Unknown interaction` | ✅ Mitigado (`defer` + `followup` en `stop`) | Cierre definitivo en S2 (vía única de apagado en `core/voice.py`) |
| `ffmpeg process … has not terminated` | 🟡 Mitigado (apagado con `try/except` + `clear_queue`) | Cierre definitivo en S2 |
| `ytsearch1:` sobre URLs/playlists → `Downloading 0 items` → `IndexError` | ✅ Mitigado (detección URL vs texto, lista vacía → mensaje, `ignoreerrors`) | Cierre definitivo en S3 (flat + validación de URLs) |
| Links no compatibles (Reels/TikTok/etc.) sin validación | 🔴 Pendiente | S3: `utils/validators.py` + mensaje `❌ No puedo reproducir este enlace` |
| Validación "mismo canal de voz" | 🔴 Pendiente | S2: `require_same_voice()` aplicado a control + `play` |
| `asyncio.Lock` por servidor (`GUILD_LOCKS`) | 🔴 Pendiente | S2 |
| Protección `after_play()` tras `/stop` | 🟡 Parcial (guard + `clear_queue` en rama vacía) | Definitivo en S2 |
| `/disconnect` separado de `/stop` | 🔴 Pendiente | S2 (trivial una vez exista `core/voice.py`) |
| Autodisconnect al vaciarse la cola | ✅ Hecho | S2 añade: también al quedarse el canal vacío |
| Arquitectura propuesta (validación → guild state/lock → cola → yt-dlp → FFmpeg → playback) | 🟡 Es la base de `arquitectura.md` §2 | Adoptada con ajuste: `music/` sin dependencia de `discord` |

## 3. `refactorizacionV1.md` (refactor parcial)

| Afirmación del doc | Estado real (S0) | Acción |
|---|---|---|
| `music/queue.py` extraído | ✅ Hecho | S1 lo extiende (helpers + `Track`) |
| `music/search.py` extraído (playlists, start/limit, `ignoreerrors`, mensaje informativo) | ✅ Hecho | S3 lo extiende (flat, validación) |
| `/stop` con `defer`/`followup` | ✅ Hecho | — |
| Auto-deafen con `self_deaf=True` | ✅ Hecho | — |
| Bug tupla 2→3 (`ValueError`) con solución "pasar a dict Track" | 🟡 Mitigado S0 (shim 3-tupla); migración dict pendiente | **Sprint 1** (ADR-001) |
| Playlists procesadas completas antes de sonar (lento) → `extract_flat` + resolver al reproducir | 🔴 Pendiente (el `resolve_stream_url()` S0 es la mitad de la solución) | **Sprint 3** (ADR-002) |
| Warning JS runtime de yt-dlp | 🟡 Vigente, operativo | S3: instalar Node.js/Deno + nota en manuales |
| Arquitectura objetivo (`bot.py` UI + `search`/`queue`/`voice`) y "próximo paso: `core/voice.py`" | 🔴 Pendiente | **Sprint 2** (ADR-003) |
| Pendientes: Now Playing rico, trolls, `/remove`, `/move`, `/play after:`, `/lyrics`, multi-resultados, validación URLs, resultados incorrectos, comandos alternativos, errores globales, FFmpeg, JS runtime | 🔴 Pendientes | Todos recogidos en `roadmap.md` con sprint asignado |

## 4. Contraste con el README generado anteriormente

El README anterior era correcto en lo técnico pero inadecuado para `main`:

| Problema | Corrección aplicada |
|---|---|
| Sección "Qué se arregló" con 6 bugs detallados (historia, no producto) | Movida aquí (auditoría) + resumen de 1 línea; el detalle vive en `desarrollo/` |
| Roadmap genérico de 9 puntos sin priorizar ni dependencias | Sustituido por puntero a `roadmap.md` + `sprints.md` |
| Links rotos a `docs/COMANDOS.md` (los manuales se movieron a `docs/manuales/`) | Links corregidos |
| Nombre "DJ Huevito" hardcodeado en `/help` y docs | `BOT_NAME` configurable; repo neutro "MusicBot" |
| Estructura descrita como "carpetas vacías de reserva" sin plan | Puntero a `arquitectura.md` (quién puebla cada carpeta y cuándo) |

## 5. R-01 Revisión de nombres base (Sprint 6)

Veredicto: **los 13 canónicos se quedan en inglés**. Motivos: convención de
music bots (Groovy/Rythm la fijaron), nombres cortos sin tildes, coinciden con
tutoriales y con los docs existentes. El español llega por alters sembrados por
defecto en `aliases.example.json` (el seed los instala solos).

| Canónico | Decisión | Alters ES sembrados | Motivo |
|---|---|---|---|
| `/play` | Se queda | `jugar, rolita, pon` | Universal; `jugar` es el chiste interno |
| `/pause` | Se queda | `pausa` | Idéntico en ES/EN |
| `/resume` | Se queda | `sigue` | `reanudar` largo y con tilde potencial |
| `/skip` | Se queda | `salta, siguiente` | Estándar en bots |
| `/stop` | Se queda | `para` | `detener`/`parar` ambiguos; `para` corto |
| `/disconnect` | Se queda | `salir` | `leave`/`salir` equivalentes; se mantiene el documentado |
| `/queue` | Se queda | `cola` | `queue` aparece en todos los manuales |
| `/nowplaying` | Se queda | `np, sonando` | Largo pero estándar; `np` para uso rápido |
| `/shuffle` | Se queda | `mezclar` | Término musical estándar |
| `/remove` | Se queda | `quitar` | `remove N` + validación ya documentados |
| `/clear` | Se queda | `limpiar` | Corto; `limpiar` para ES |
| `/move` | Se queda | `mover` | Idéntico en ES/EN |
| `/help` | Se queda | `ayuda` | Convención Discord |

Regla a futuro: si un canónico se renombra, el nombre viejo queda como alter
de compatibilidad (no se rompe costumbre).

### Adenda S6: `/skip` vs `/next` vs `/remove`
Duda resuelta con semántica distinta por comando (no más sobrecarga en `/skip`):
- `/skip [cantidad]` (default 1): corta la actual + descarta cantidad-1 en cola.
- `/next` (nuevo, solo lectura): muestra la siguiente sin mutar nada.
- `/remove n`: elimina la #n sin que suene.
- El alter `siguiente` se mudó de `/skip` a `/next`, donde calza.

## 6. Conclusión de la auditoría

- **Nada de los 3 docs se contradice con el código S0** salvo el nombre y la
  estructura plana inicial (ambos históricos, no errores).
- **Lo "obsoleto" es solo lo ya superado** (estructura plana, `ytsearch1:` literal,
  nombre fijo). Se conserva como historia del proyecto.
- **Lo "pendiente" está todo capturado** en `roadmap.md` y planificado en `sprints.md`.
- **Riesgo principal heredado:** la trilogía propone 3 cambios grandes (Track, voice,
  flat) que tocan el núcleo. El orden S1→S2→S3 está diseñado para que cada uno
  deje el bot funcionando antes del siguiente (ver `arquitectura.md` §4).
