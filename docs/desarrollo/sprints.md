# Sprints — MusicBot

> Plan de trabajo por sprints. Estado, viabilidad y dependencias en `roadmap.md`;
> arquitectura y ADRs en `arquitectura.md`; aceptación en `casos.md`.
> Regla de oro: **cada sprint deja el bot funcionando** (matriz de `casos.md` § final).

## Sprint 0 — Estabilización ✅ HECHO
- Cola 3-tuplas + shim de compat (`bot.py`).
- `search_ytdlp()`: URL vs texto, `ytsearch:`, playlists con start/limit, `ignoreerrors`.
- `resolve_stream_url()` para entradas sin `url` directa.
- `_ffmpeg_executable()`: `bin/` local o PATH.
- Check de `DISCORD_TOKEN` al arrancar.
- `README` base + `docs/manuales/` + `.gitignore` + `.env.example`.
- **Deuda que deja:** shim temporal, sin locks, sin validación de canal, sin flat, sin `core/voice.py`.

## Sprint 1 — Datos y base testeable ✅ HECHO
**Objetivo:** estructura `Track` definitiva + cola con helpers + primera red de tests.
No se toca voz ni FFmpeg → riesgo mínimo (ver ADR-001).

- [x] A-01 Migrar cola a `Track` dict (`diccionario.md` §1); actualizar 2 sitios
      (`/queue`, `play_next_song`); **retirar shim**; `search.py` emite `Track`.
- [x] A-02 Helpers en `music/queue.py`: `remove/move/shuffle/peek` (sin comandos aún).
- [x] C-01/C-02 Tests: `music/queue.py` puros + `music/search.py` con mock de `_extract`.
- [x] C-04 `start_bot.bat` portable (ruta relativa, sin `D:\` fijo).
- [x] Revisar `music/playlist.py` y `music/trolls.py` vacíos: o se implementan
      (trolls → B-08 futuro) o se eliminan para no confundir.
- **Hecho cuando:** matriz `casos.md` en verde + tests en verde
  (`python -m unittest discover -s tests`, 18 tests, stdlib sin pytest)
  + sin `try/except ValueError` de tuplas.

## Sprint 2 — Voz robusta ✅ HECHO
**Objetivo:** un solo dueño de la voz (`core/voice.py`) + concurrencia + canal.
Movimiento mecánico primero, robustez después (ver ADR-003).

- [ ] A-04 Crear `core/voice.py`: mover `play_next_song`, `after_play`,
      `_ffmpeg_executable`, connect/move/disconnect; `bot.py` solo handlers.
- [ ] A-04 `NOW_PLAYING` por guild (lo escribe voz; lo leerá `/nowplaying` en S4).
- [ ] A-05 `GUILD_LOCKS`: `play/skip/stop/disconnect/next` bajo lock del guild.
- [ ] A-08 Guard de generación en `after_play` + vía única de apagado (CU-05, CB-09).
- [ ] A-06 `require_same_voice()` en `play/pause/resume/skip/stop` + error `WrongChannel` (CB-05).
- [ ] A-07 `/disconnect` (solo desconecta) distinto de `/stop`.
- [ ] A-09 Autodisconnect con canal vacío (`on_voice_state_update` + timeout 60–120 s).
- [ ] C-03 Logger a archivo (`utils/logger.py`) en voz+search (adiós `print`).
- [ ] A-13 Manejo global `on_app_command_error` (mapa en `utils/errors.py`).
- [ ] CB-08: validar FFmpeg al arrancar con mensaje legible.
- **Hecho cuando:** CU-05/CU-06/CB-05/CB-09 en verde bajo ráfagas simultáneas.

## Sprint 3 — Playlists rápidas y válidas ✅ HECHO
**Objetivo:** la 1ª canción suena ya; entradas inválidas → mensaje, nunca crash.

- [ ] A-10 `extract_flat="in_playlist"` solo en rama playlist; resolver audio al
      reproducir con `resolve_stream_url()` de fallback (ADR-002, CU-03).
- [ ] A-11 `utils/validators.py`: YouTube (video/playlist/shorts) sí; resto →
      `❌ No puedo reproducir este enlace.` (CB-01, CB-10).
- [ ] Aviso explícito de saltos (privado/eliminado/sin audio) sin cortar la cola (CB-02).
- [ ] A-12 Runtime JS (Node.js/Deno) instalado + nota en `docs/manuales/INSTALACION.md`.
- [ ] Documentar límites reales: `limit` máx, timeout de extracción, playlists gigantes.
- **Hecho cuando:** CU-03 con playlist 100+ suena la 1ª en segundos + CB-01/CB-02/CB-10 en verde.

## Sprint 4 — Experiencia ✅ HECHO
**Objetivo:** lo visible que pedían los docs iniciales. Todo depende de S1–S2 ya hechos.

- [ ] B-01 `/nowplaying` (embed con datos de `NOW_PLAYING`).
- [ ] B-02 Embed rico (duración, autor, thumbnail, link, solicitado_por) en Now Playing y `/play`.
- [ ] B-03 `/queue` paginada con botones (View); mantener modo ephemeral.
- [ ] B-04 `/shuffle` · B-05 `/remove`, `/clear` · B-06 `/move`, `/play … after:<n>`.
- [ ] B-07 Alias (`/rolita`…) — pocos, documentados; B-08 trolls si apetece.
- **Hecho cuando:** CU-07 con 150 canciones navegable + B-04–B-06 con validación de rango.

## Sprint 5 — Alters configurables + panel local ✅ HECHO
**Objetivo:** nombres propios (ej. `/jugar` → `play`) editables sin tocar código,
y arranque/configuración desde una app de escritorio local.
Depende de lógica compartida: idealmente cogs (S4), fallback funciones `_do_*`.

- [ ] D-01 Extraer callbacks compartidos (vía cogs S4 o `_do_*` en `bot.py`).
- [ ] D-02 `aliases.json` (local, gitignored) + `aliases.example.json` + loader con
      validación y errores legibles al arrancar.
- [ ] D-03 Registro dinámico: un `tree.command` por alter apuntando al callback
      canónico; `/help` lista alters activos.
- [ ] D-04 `GUILD_ID` opcional en `.env` → sync por servidor (instantáneo) para
      probar renombres sin esperar la propagación global (~1h).
- [ ] D-05 Panel `panel/` en tkinter (stdlib): perfiles (un perfil = un token),
      start/stop/restart del subproceso, editor de alters, editor `.env`
      (token enmascarado), visor de logs, botón re-sync. Comunicación solo por
      archivos; cambiar alters = guardar + reiniciar desde el panel.
- [ ] D-06 `panel.bat` + `icono.ico` + manual del panel en `docs/manuales/`.
- **Hecho cuando:** CU-09/CB-11–CB-14 en verde + bot arranca y se opera solo desde el panel.

## Sprint 5.1 — Seed + consola del panel 🔴 EN CURSO
**Objetivo:** cero fricción al clonar y consola visible en desarrollo.

- [x] D-07 `ensure_aliases()`: si falta `aliases.json`, crearlo desde
      `aliases.example.json` y seguir; botón "↺ Restablecer" en el panel.
      Test: arrancar sin archivo → se crea válido (CB-15).
- [x] D-08 El panel arranca el bot con **consola propia** (`CREATE_NEW_CONSOLE`):
      mismo detalle en vivo que `start_bot.bat` + toggle "mostrar consola".
      Producción = consola oculta, solo `logs/bot.log` (ver política abajo).
- **Hecho cuando:** clonar → `panel.bat` → Iniciar funciona sin copiar nada;
  la consola del bot muestra el log en vivo como en tu captura.

### Política consola vs archivo (dev vs prod)
- **Desarrollo (ahora):** consola siempre visible — `start_bot.bat` la abre, y el
  panel abre una propia por bot. El detalle en vivo manda para depurar.
- **Producción (luego):** consola oculta (toggle del panel), el bot escribe solo
  a `logs/bot.log` (rotar si crece; hoy `FileHandler` simple). La pestaña 📋
  del panel es entonces el visor principal.

## Sprint 6 — R-01 Revisión de nombres base ✅ HECHO
Veredicto en `auditoria.md` §5: los 13 canónicos se quedan en inglés
(convención + cortos + tutoriales); el español llega por alters ES sembrados
en `aliases.example.json` (el seed los instala solos). Regla futura: renombrar
= nombre viejo como alter de compatibilidad.
**Objetivo:** con los alters como red, cada comando queda con su nombre definitivo.
- [x] Repasar los 13 canónicos uno por uno (claridad, choques con alters, español).
- [x] Renombrar donde aplique → veredicto: ninguno; el español va por alters
      sembrados (`aliases.example.json` con 18 alters ES).
- [x] Actualizar `/help` (ya dinámico), `docs/manuales/COMANDOS.md`,
      `aliases.example.json` y justificar en `auditoria.md` §5.
- **Hecho cuando:** tabla nombre → decisión + motivo (auditoría §5), 51/51 tests.

### Adenda S6: `/skip` vs `/next` vs `/remove` ✅ HECHO
- `/skip [cantidad]` (helper `drop_first` + test), `/next` peek (nuevo canónico),
  tabla de diferencias en el manual, alter `siguiente`→`/next`.
- **Hecho cuando:** 54/54 tests + CU de cada uno en `casos.md`.

## Sprint 7 — Multi-resultados (B-09) ✅ HECHO
**Objetivo:** `/play <texto>` muestra 5 opciones con menú select en vez de
encolar a ciegas el 1er resultado.
- [x] `search_many()` con `ytsearch5` (5 entradas completas, no flat) + 2 tests.
- [x] Select efímero (timeout 60 s, solo el solicitante) → encola la elegida;
      el bot entra a voz recién al elegir (no al mostrar el menú).
- [x] Helpers `_enqueue`/`_maybe_start` compartidos entre URL y select.
- [x] CU-10 en `casos.md` + manual actualizado.
- **Hecho cuando:** elegir la opción 3 reproduce la 3 (no la 1). 56/56 tests.

## Sprint 8 — Trolls + historial (B-08, C-08) ✅ HECHO
- [x] `music/trolls.py` + `trolls.example.json` + seed + `TROLL_CHANCE` (default 0.05).
- [x] 3 modos: keyword exacta, emboscada solo-texto con aviso, `/troll` con menú.
- [x] Historial 20 por guild (`record_history` al sonar) + `/history` con replay
      (audio fresco) + alter `/historial`.
- [x] CU-11 + manual + panel (`TROLL_CHANCE` en Config).
- **Hecho cuando:** 64/64 tests + CU-11 verificado en Discord.
- [ ] `music/trolls.py`: mapa búsqueda→URL fija + test (sin red).
- [ ] Historial por guild (últimas 20, en memoria): lo escribe `core/voice.py`
      al terminar cada track; `/historial` lo muestra paginado como `/queue`.
- **Hecho cuando:** tests de mapeo + historial en verde.

## Sprint 9 — Ops: CI + Docker + nube (C-05, C-06, C-09) ✅ HECHO
- [x] C-05 `.github/workflows/ci.yml`: `py_compile` + `unittest` en 3.11/3.12
      por push/PR (sin token ni FFmpeg; todo mockeado).
- [x] C-06 `Dockerfile` (FFmpeg vía apt) + `compose.yml` (token por `env_file`)
      + `.dockerignore` + `docs/manuales/DOCKER.md`.
- [x] C-09 Plan ideal en `futuro-hosting-247.md` (local hasta nuevo aviso).
- **Hecho cuando:** push en verde en Actions + `docker compose up` suena música.
Ver explicación larga abajo (§ S9 en detalle).

## Sprint 10 — Calidad (T-01…T-04) ✅ HECHO
Detalle y pendientes en `plan-calidad.md`.
- [x] T-01 Unitarios extra (`panel/config_store.py` + bordes + historial + move).
- [x] T-02 Handlers con fakes (`test_handlers.py`: skip/remove/pause/stop/...) +
      `_pick_track` puro + voz (`stop_playback`, `_finish`, `play_next`).
      `bot.py` importable (guard `__main__`).
- [x] T-03 Ruff + coverage ≥70% (CI + local): `requirements-dev.txt`,
      `pyproject.toml`. 86 tests, ruff limpio, coverage 71%.
- [x] T-04 Job docker build en CI (sin publicar).
- **Hecho cuando:** 80+ tests, ruff limpio, coverage ≥70%, run verde (tests + docker).

## S9 en detalle — qué es cada pieza y por qué
### C-05 CI (GitHub Actions, gratis)
Cada push/PR levanta un Ubuntu limpio, instala Python + dependencias y corre
`py_compile` + `python -m unittest discover -s tests`. Si algo rompe, el push
sale en rojo antes de que lo pruebes a mano. No necesita FFmpeg ni token porque
los tests mockean red y voz. Costo: $0 (límites generosos en repos públicos).

### C-06 Docker (imagen reproducible)
`Dockerfile`: parte de `python:3.11-slim`, instala `ffmpeg` con apt (adiós
`bin/` de 300 MB), copia el código, `CMD ["python", "bot.py"]`. `compose.yml`
pasa el token sin exponerlo (`env_file: [.env]`). Sirve para: correr idéntico
en tu PC, en un VPS o en la nube; y para no "en mi máquina sí funciona".

### C-09 Nube 24/7 (opciones para proyecto personal)
| Opción | Costo aprox. | Notas |
|---|---|---|
| Tu PC encendida | $0 | Vale hoy; se cae si la apagas (estado actual) |
| Raspberry Pi en casa | ~$0 (hardware único) | Ideal personal: silenciosa, 24/7, Docker corre bien |
| Oracle Cloud Free Tier | $0 | VPS gratis permanente (ARM 4 cores); requiere tarjeta y setup |
| VPS barato (Hetzner/contabo) | ~€4–6/mes | Simple, Docker directo, sin sorpresas |
| Railway/Render free | $0 con límites | Se duermen por inactividad → **no sirven** para un bot 24/7 |
Recomendación: seguir local hasta cerrar S9; luego Raspberry u Oracle Free;
VPS de pago solo si quieres cero mantenimiento.

## Sprint 11 — Lyrics + DJ + logs ✅ HECHO
- [x] B-10 `/lyrics` (LRCLIB sin key, spike en vivo) + caché + paginado +
      `/lyrics [consulta]`; alter `/letra`.
- [x] C-07 `DJ_ROLE_ID`: `NotDJError` + `check_dj` en stop/skip/disconnect/
      shuffle/remove/clear/move; lectura siempre abierta; en panel y `.env.example`.
- [x] Logs con rotación (`RotatingFileHandler` 2MB × 5+1).
- [x] CU-12 + manual. **Hecho cuando:** 97/97 tests, coverage 72%, ruff limpio.

## Sprint 12 — Adelgazar main ✅ HECHO
- [x] A: `core/guards.py` (`@require_voice`, `@require_dj`) + 6 tests.
- [x] B: `ui/views.py` (`EnqueueSelectView`, `PagerView`) + 6 tests;
      `enqueue_tracks` en `music/queue.py`, `maybe_start_playback` en `core/voice.py`.
- [x] C: 5 Cogs (`commands/play|control|queue|fun|help.py`); `bot.py` 671→82
      (setup + eventos + alters + run). Tests adaptados (setup + binding).
- [x] D: 111/111 tests, ruff limpio, coverage 82%, docs.
- [x] Fix CI: check de `TOKEN` movido de import a runtime (el orden de imports
      en tests congelaba `TOKEN=None` sin `.env`).
- **Hecho cuando:** `bot.py` 82 líneas + cero try/except de guards + CI verde.

## Sprint 13 — Robustez producción ✅ HECHO
Del log real: video con edad + handshake 4017 + cascada Unknown interaction.
- [x] `VoiceConnectError`: `ensure_voice` falla rápido con mensaje amable
      (firewall/UDP/VPN) en vez de colgar 30 s.
- [x] Defer-first en los 3 menús (play/troll/history): ack inmediato, trabajo
      después, `edit_original_response`. Fin de la cascada 10062.
- [x] Cookies opcionales (`cookies.txt`, gitignored) + flag `age_restricted`:
      sin cookies se salta con aviso `🔞`, no se rompe la cola.
- [x] Manual: sección cookies + troubleshooting 4017.
- **Hecho cuando:** 114/114 tests, ruff limpio, CB-17/CB-18.

## Futuro (documentado, sin sprint asignado)
- `futuro-funciones.md`: B-10 `/lyrics` (spike LRCLIB primero), C-07 permisos
  DJ (`DJ_ROLE_ID`), panel v2 (ajustes, despliegue Pi, perfiles, customtkinter).
- `futuro-hosting-247.md`: guía Pi paso a paso + nube detallada (no se implementará
  por ahora).
- B-10 `/lyrics` (**spike previo**: auth/límites/ToS).
- C-07 permisos DJ.
- Panel v2: perfiles múltiples, tema moderno (`customtkinter`), más ajustes
  (volumen default, timeout autodisconnect, nivel de log).

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| S1: olvidar un desempaquetado de tupla | `grep` de `popleft()` + tests; la matriz CU-01–03 lo caza |
| S2: `after_play` en hilo + `bot.loop` tras mover | Mover tal cual primero, verificar CU-05/CB-09, luego añadir locks |
| S3: flat sin `duration` rompe embeds | Embed tolerante a `None` hasta S4 (B-02) |
| yt-dlp/YouTube cambian y rompen extracción | A-12 + `pip install -U yt-dlp` en manuales; error legible, no crash |
| Alcance: querer meter S4 en S2 | Regla: sin `Track` (S1) no hay embed rico; sin `voice.py` (S2) no hay `/disconnect` |
