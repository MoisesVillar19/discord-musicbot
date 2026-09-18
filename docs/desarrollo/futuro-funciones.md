# Futuro: funciones pendientes — MusicBot

> B-10 y C-07 ya implementados (Sprint 11). Queda: panel v2.

## B-10 `/lyrics` ✅ HECHO (S11)

**Idea:** `/lyrics` muestra la letra de lo que suena (lee `NOW_PLAYING`);
`/lyrics <texto>` busca una cualquiera.

**Spike (investigar primero, ~1 tarde):**
1. **Genius:** API gratis con token personal, pero **no devuelve la letra**
   (solo metadata + URL; el scraping viola sus ToS). Descartado como fuente.
2. **Musixmatch:** tiene letra, pero el plan gratis es para apps no comerciales
   con límites estrictos y requiere API key aprobada. Viable con límites.
3. **LRCLIB (recomendado para el spike):** API libre sin key
   (`https://lrclib.net/api/get?track_name=…&artist_name=…`), devuelve letra
   plana + sincronizada. Límites generosos y ToS permisivos.
4. ToS/YouTube: mostrar letras en Discord es uso personal; no redistribuir.

**Diseño si el spike sale bien:**
- `services/lyrics_service.py`: `get_lyrics(title, uploader)` con caché en
  memoria por `webpage_url` (evita repetir llamadas).
- `/lyrics`: embed paginado (las letras superan 2000 chars → reutilizar
  `queue_pages` o paginador propio, 10 líneas/página).
- `requested_by`/`NOW_PLAYING` ya existen: cero cambios de núcleo.
- Criterio: CU con 3 canciones conocidas + fallback `❌ Sin letra disponible`.

## C-07 Permisos DJ ✅ HECHO (S11)

**Idea:** que solo ciertos roles usen comandos sensibles (`/stop`, `/clear`,
`/remove`, `/skip`), el resto solo `/play`, `/queue`, `/nowplaying`.

**Diseño:**
- `.env`: `DJ_ROLE_ID` (ID del rol DJ; vacío = sin restricción, comportamiento actual).
- `utils/errors.py`: `NotDJError` + mensaje `❌ Necesitas el rol DJ.`
- Helper `require_dj(interaction)`: si `DJ_ROLE_ID` vacío → pasa; si no,
  comprueba `interaction.user` roles (en guild; en DM pasa).
- Aplicar en: `stop`, `clear`, `remove`, `move`, `skip`, `disconnect`.
  Lectura (`queue`, `nowplaying`, `next`, `history`, `help`) siempre abierta.
- Tests con fakes (roles como `SimpleNamespace(id=…)`) + fila en matriz manual.
- Criterio: sin `DJ_ROLE_ID` todo igual; con él, sin rol → rechazo limpio.

## Panel v2 ✅ HECHO (parcial)
Implementado: más ajustes (`LOG_LEVEL`, `EMPTY_TIMEOUT` cableados a logger y
voz), pestaña dashboard (uptime, reinicios, abrir logs/manual), validación de
config al guardar. Queda a futuro: despliegue remoto a Pi y perfiles múltiples
(solo si hay 2º bot) y `customtkinter` (solo si el look molesta).

## Hosting 24/7

Ver `futuro-hosting-247.md` (guía Pi paso a paso + nube detallada).
