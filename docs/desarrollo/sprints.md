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

## Sprint 1 — Datos y base testeable 🔴 SIGUIENTE
**Objetivo:** estructura `Track` definitiva + cola con helpers + primera red de tests.
No se toca voz ni FFmpeg → riesgo mínimo (ver ADR-001).

- [ ] A-01 Migrar cola a `Track` dict (`diccionario.md` §1); actualizar 2 sitios
      (`/queue`, `play_next_song`); **retirar shim**; `search.py` emite `Track`.
- [ ] A-02 Helpers en `music/queue.py`: `remove/move/shuffle/peek` (sin comandos aún).
- [ ] C-01/C-02 Tests: `music/queue.py` puros + `music/search.py` con mock de `_extract`.
- [ ] C-04 `start_bot.bat` portable (ruta relativa, sin `D:\` fijo).
- [ ] Revisar `music/playlist.py` y `music/trolls.py` vacíos: o se implementan
      (trolls → B-08 futuro) o se eliminan para no confundir.
- **Hecho cuando:** matriz `casos.md` en verde + `pytest` en verde + sin `try/except ValueError` de tuplas.

## Sprint 2 — Voz robusta
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

## Sprint 3 — Playlists rápidas y válidas
**Objetivo:** la 1ª canción suena ya; entradas inválidas → mensaje, nunca crash.

- [ ] A-10 `extract_flat="in_playlist"` solo en rama playlist; resolver audio al
      reproducir con `resolve_stream_url()` de fallback (ADR-002, CU-03).
- [ ] A-11 `utils/validators.py`: YouTube (video/playlist/shorts) sí; resto →
      `❌ No puedo reproducir este enlace.` (CB-01, CB-10).
- [ ] Aviso explícito de saltos (privado/eliminado/sin audio) sin cortar la cola (CB-02).
- [ ] A-12 Runtime JS (Node.js/Deno) instalado + nota en `docs/manuales/INSTALACION.md`.
- [ ] Documentar límites reales: `limit` máx, timeout de extracción, playlists gigantes.
- **Hecho cuando:** CU-03 con playlist 100+ suena la 1ª en segundos + CB-01/CB-02/CB-10 en verde.

## Sprint 4 — Experiencia
**Objetivo:** lo visible que pedían los docs iniciales. Todo depende de S1–S2 ya hechos.

- [ ] B-01 `/nowplaying` (embed con datos de `NOW_PLAYING`).
- [ ] B-02 Embed rico (duración, autor, thumbnail, link, solicitado_por) en Now Playing y `/play`.
- [ ] B-03 `/queue` paginada con botones (View); mantener modo ephemeral.
- [ ] B-04 `/shuffle` · B-05 `/remove`, `/clear` · B-06 `/move`, `/play … after:<n>`.
- [ ] B-07 Alias (`/rolita`…) — pocos, documentados; B-08 trolls si apetece.
- **Hecho cuando:** CU-07 con 150 canciones navegable + B-04–B-06 con validación de rango.

## Futuro (sin sprint asignado)
- B-09 multi-resultados con select · B-10 `/lyrics` (**spike previo**: auth/límites/ToS).
- C-05 CI (ruff+tests) · C-06 Docker · C-07 permisos DJ · C-08 historial · C-09 nube 24/7.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| S1: olvidar un desempaquetado de tupla | `grep` de `popleft()` + tests; la matriz CU-01–03 lo caza |
| S2: `after_play` en hilo + `bot.loop` tras mover | Mover tal cual primero, verificar CU-05/CB-09, luego añadir locks |
| S3: flat sin `duration` rompe embeds | Embed tolerante a `None` hasta S4 (B-02) |
| yt-dlp/YouTube cambian y rompen extracción | A-12 + `pip install -U yt-dlp` en manuales; error legible, no crash |
| Alcance: querer meter S4 en S2 | Regla: sin `Track` (S1) no hay embed rico; sin `voice.py` (S2) no hay `/disconnect` |
