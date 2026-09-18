# Plan de calidad y pendientes — MusicBot

> Estado: tests automáticos 64/64 en verde + CI verde. Este doc traza qué falta
> en cada frente: tests nuevos (Sprint 10), validación manual en Discord real
> y futuro declarado. Orden de ejecución al final.

## 1. Tests nuevos — Sprint 10 (IDs T-01…T-04)

| ID | Qué | Dónde | Criterio |
|---|---|---|---|
| T-01 | Unitarios extra: `.env` roundtrip, bordes de página (10/11/20), subdominios, historial tope | `tests/test_panel_config.py` (nuevo, vía `panel/config_store.py`), +casos en `test_queue/validators/embeds` | 80+ tests totales |
| T-02 | Handlers con fakes (`SimpleNamespace`): `/skip cantidad:3`, `/skip` sin nada, `/remove` inválido, canal distinto | `tests/test_handlers.py` (nuevo) + helper puro `_pick_track` | Sin gateway real |
| T-03 | Ruff + coverage en CI | `requirements-dev.txt`, `pyproject.toml`, job steps | `ruff` limpio, coverage ≥70% bloqueante |
| T-04 | Build Docker en CI (sin publicar) | Job `docker:` con buildx | Atrapa Dockerfile rotos |

Refactors mínimos para testear: `panel/config_store.py` (`read_env`/`write_env`
puras) y `_pick_track(options, index)` extraído de `PickView`.

## 2. Pendiente manual en Discord real (matriz `casos.md`)

No automatizable aquí; checklist para cuando tengas tiempo:

- [ ] CU-07: `/queue` con 150 canciones, navegar ⬅️/➡️ (S4 B-03).
- [ ] CU-09b: `/next` no muta, `/skip cantidad:2`, `/remove` (S6 B-11).
- [ ] CU-10: menú 5 opciones, elegir la 3 suena la 3; expira a los 60 s (S7).
- [ ] CU-11: keyword `trololo`, emboscada con `TROLL_CHANCE=1`, `/troll`, `/history` replay (S8).
- [ ] CB-05: `/stop` desde otro canal → rechazo (S2).
- [ ] CB-09/CU-05: `skip`+`stop` simultáneos, sin fantasma (S2).
- [ ] Consola del panel en vivo = `start_bot.bat` (S5.1 D-08).
- [ ] Alters ES sembrados (`/jugar`, `/cola`, `/siguiente`→`/next`) (S6).

## 3. Futuro declarado (no cambia el bot actual)

| ID | Ítem | Nota |
|---|---|---|
| B-10 | `/lyrics` | Spike previo: auth/límites/ToS (Genius/Musixmatch) |
| C-07 | Permisos DJ | Roles por comando, tras errores globales |
| Panel v2 | Perfiles múltiples, `customtkinter`, más ajustes | Ver `PANEL.md` |
| C-09 | Hosting 24/7 | Plan ideal en `futuro-hosting-247.md` |

## 4. Plan de acción (orden)

1. **S10-T01+T02** (código+tests) → unittest local en verde.
2. **S10-T03** (`ruff`, `coverage`, `requirements-dev.txt`) → verde local.
3. **S10-T04** (job docker) → push → run CI verde por API (tests + docker).
4. **Manual Discord** (§2) cuando tengas tiempo; marcar cada casilla aquí.
5. **Futuro** (§3) solo a pedido; B-10 arranca con spike, no con código.
