# Casos de uso y aceptación — MusicBot

> Cada caso: precondiciones → pasos → resultado esperado → estado S0.
> Los sprints toman los "criterios de aceptación" como definición de hecho.
> IDs de roadmap entre paréntesis.

## CU-01 Reproducir por texto (A-11, B-09)
- **Pre:** bot online, usuario en canal de voz.
- **Pasos:** `/play song_query:un mamut chiquitito`.
- **Esperado:** entra `self_deaf`, suena el 1er resultado, embed Now Playing.
- **S0:** ✅ (vía `ytsearch:`). **Falla si:** yt-dlp desactualizado → actualizar (manuales).

## CU-02 Reproducir URL de video
- **Pre:** igual que CU-01.
- **Pasos:** `/play song_query:https://www.youtube.com/watch?v=…`.
- **Esperado:** suena EXACTAMENTE ese video, no una búsqueda parecida.
- **S0:** ✅ (detección URL). **S3:** blindar "resultados incorrectos" (`refactorizacionV1.md` § evitar resultados incorrectos).

## CU-03 Playlist con paginación (A-10)
- **Pasos:** `/play song_query:<playlist> start:5 limit:20`.
- **Esperado:** `📂 Playlist detectada / ➕ 20 / ⚠️ N no disponibles / 📌 #5 de TOTAL`; la 1ª canción suena sin esperar al análisis completo.
- **S0:** 🟡 mensaje ✅, pero la 1ª canción espera el análisis completo (lento).
- **Aceptación S3:** tiempo hasta 1ª canción independiente del tamaño de la playlist.

## CU-04 Pause / resume
- **Pasos:** `/pause` → `/resume` (mismo canal).
- **Esperado:** pausa y reanuda; mensajes claros si no hay nada sonando.
- **S0:** ✅. **S2:** rechazar si el usuario está en otro canal.

## CU-05 Skip concurrente (A-05, A-08)
- **Pasos:** dos usuarios (mismo canal) mandan `/skip` a la vez; otro manda `/stop` a la vez.
- **Esperado:** un solo avance de cola; tras `/stop` NO suena nada más (`after_play` no resucita).
- **S0:** 🟡 funciona en secuencial; sin locks.
- **Aceptación S2:** 10 ráfagas `skip+stop` simultáneos sin excepción ni canción fantasma.

## CU-06 Stop y disconnect (A-07, A-08)
- **Pasos:** `/stop` durante reproducción → `/disconnect` con bot idle en canal.
- **Esperado:** stop limpia cola + desconecta; disconnect solo desconecta; sin `Unknown interaction`.
- **S0:** 🟡 stop ✅ con `defer`; `/disconnect` no existe.
- **Aceptación S2:** ambos <3 s de respuesta visible.

## CU-07 Ver cola (B-03)
- **Pasos:** encolar 150 canciones → `/queue`.
- **Esperado:** mensaje ≤2000 caracteres, truncado con "…y N más" (S0) → páginas con botones (S4).
- **S0:** ✅ truncado. **Aceptación S4:** navegar ⬅️/➡️ sin errores de interacción.

## CU-08 Help y nombre configurable (A-03)
- **Pasos:** `/help` con `BOT_NAME=DJ Local` en `.env`.
- **Esperado:** `🎧 Comandos de DJ Local`.
- **S0:** ✅.

## CU-09 Alters configurables (D-02, D-03)
- **Pre:** `aliases.json` con `{"play": ["jugar"], "skip": ["salta"]}`, bot sincronizado.
- **Pasos:** `/jugar song_query:…` → suena; `/salta` → avanza la cola; `/help` muestra los alters.
- **Esperado:** cada alter ejecuta exactamente la misma lógica que su canónico.
- **Aceptación S5:** CU-01–CU-07 pasan igual invocados por alter o por canónico.

## CU-09b Skip / Next / Remove (S6 B-11)
- **Pre:** sonando A, cola [B, C, D].
- `/next` → muestra B sin cambiar nada (A sigue, cola intacta).
- `/skip cantidad:2` → suena C (A cortada, B descartada).
- `/remove posicion:1` → elimina C sin que suene; sigue D.
- **Esperado:** cada uno muta (o no) exactamente lo de la tabla del manual.

## Casos borde (todos deben terminar en mensaje, nunca en crash)

| # | Caso | Esperado | S0 |
|---|---|---|---|
| CB-01 | `/play` con URL de Instagram/TikTok | `❌ No puedo reproducir este enlace.` | 🔴 (S3 A-11) |
| CB-02 | `/play` video privado/eliminado | Se salta con aviso, sigue la cola | 🟡 (`ignoreerrors`; aviso explícito en S3) |
| CB-03 | `/play` playlist vacía | `❌ No se encontraron resultados.` sin `IndexError` | ✅ |
| CB-04 | `/play` sin estar en canal de voz | `🎧 Debes estar en un canal de voz.` | ✅ |
| CB-05 | `/stop` desde OTRO canal de voz | `❌ Debes estar en el mismo canal que el bot.` | 🔴 (S2 A-06) |
| CB-06 | Cola vacía + `/skip`, `/pause`, `/queue` | Mensaje acorde, sin excepción | ✅ |
| CB-07 | Sin `DISCORD_TOKEN` | Aborto con `DISCORD_TOKEN no encontrado…` | ✅ |
| CB-08 | Sin FFmpeg (ni `bin/` ni PATH) | Error legible, no traceback crudo | 🟡 (S2: validar al arrancar) |
| CB-09 | `/stop` y fin de canción a la vez | Una sola desconexión, cola limpia | 🟡 (S2 A-08) |
| CB-10 | Texto que parece URL (`youtube.com sin https`) | Se trata como búsqueda o se valida y avisa | 🔴 (S3 A-11) |
| CB-11 | `aliases.json` con nombre inválido (`Mi Rola!`, mayúsculas) | Arranque aborta con error legible, sin traceback crudo | 🔴 (S5 D-02) |
| CB-12 | Alter que colisiona (`"skip": ["play"]`) | Arranque aborta indicando la colisión | 🔴 (S5 D-02) |
| CB-13 | Renombrar un alter y re-sincronizar | Comando viejo desaparece, nuevo aparece (nota: global ~1h, guild instantáneo) | 🔴 (S5 D-04) |
| CB-14 | Arrancar segunda instancia con el mismo token | Segundo proceso no conecta / mensaje claro en el panel | 🔴 (S5 D-05) |
| CB-15 | Arrancar sin `aliases.json` | Se autocrea desde el ejemplo y el bot sigue (S5.1 D-07) | 🔴 |
| CB-16 | Consola del panel vs `start_bot.bat` | Mismo detalle en vivo en ambas; al ocultar consola todo sigue en `logs/bot.log` | 🔴 (S5.1 D-08) |

## CU-10 Multi-resultados (S7 B-09)
- **Pre:** bot online, usuario en voz.
- **Pasos:** `/play song_query:te quiero` → aparecen 5 opciones → elegir la 3.
- **Esperado:** suena la opción 3 (no la 1); el menú expira a los 60 s sin romper nada.

## CU-11 Trolls + historial (S8 B-08, C-08)
- `/play song_query:trololo` → suena el troll fijo (keyword).
- `/play <texto>` con `TROLL_CHANCE=1` → emboscada con aviso `🎭 ¡TROLEADO!`;
  con `TROLL_CHANCE=0` nunca; URLs nunca son emboscadas.
- `/troll` → menú, elegir suena. `/history` → lista 20 + re-encolar suena fresco.

## CU-12 Lyrics + DJ (S11 B-10, C-07)
- `/lyrics` sonando Bohemian Rhapsody → letra paginada de Queen.
- `/lyrics <texto>` y sin nada sonando → mensajes acordes.
- Con `DJ_ROLE_ID`: `/stop` sin rol → `❌ Necesitas el rol DJ`; con rol → pasa.
  Sin configurar → todo abierto.

## Matriz de prueba manual (pre-push de cada sprint)

1. CU-01 texto, CU-02 URL video, CU-03 playlist `start:2 limit:3`.
2. CB-03 playlist vacía, CB-04 sin canal, CB-06 cola vacía.
3. `/pause→/resume→/skip→/queue→/stop` en el mismo canal.
4. `/stop` durante reproducción + `/play` inmediato (sin fantasma).
5. `py_compile` de `bot.py config.py music/*.py core/*.py` si aplica.
6. `git status` limpio de secretos (`.env`, `venv/`, `bin/` fuera).
