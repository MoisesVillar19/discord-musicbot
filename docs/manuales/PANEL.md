# Panel local — MusicBot

App de escritorio (`panel.bat`) para administrar el bot sin tocar código.
Un solo administrador, todo local. v1: un bot; perfiles múltiples es mejora futura.

## Abrir

Doble clic en `panel.bat` (usa el venv de la carpeta). `start_bot.bat` sigue
disponible para correr el bot sin panel (headless).

## Pestañas

- **📋 Logs:** últimas 80 líneas de `logs/bot.log`, auto-refresh cada 2 s.
- **🎭 Alters:** un campo por comando base (coma = varios). Máx 5, minúsculas,
  sin colisionar. Los nombres base no aparecen como editables: no se tocan.
  Guardar escribe `aliases.json` → **reinicia el bot** para aplicar.
- **⚙️ Config:** `DISCORD_TOKEN` (oculto), `BOT_NAME`, `GUILD_ID`. Guarda en
  `.env` → reinicia para aplicar.

## Botones

- **▶ Iniciar / ⏹ Detener / ↻ Reiniciar:** el panel corre `bot.py` como
  subproceso en **consola propia** (mismo detalle en vivo que `start_bot.bat`,
  ver tu captura: login, gateway, `is online!`); el punto ● indica estado.
  Solo una instancia: Discord desconecta un segundo proceso con el mismo token.
  Hay toggle "mostrar consola": en desarrollo visible, en producción oculta
  (entonces el visor 📋 + `logs/bot.log` son la fuente de verdad).

## Primeros alters

1. Nada que copiar: al arrancar, el bot crea `aliases.json` solo desde la
   plantilla (o **↺ Restablecer** en el panel).
2. En **🎭 Alters**, pon p. ej. `jugar, rolita` en `/play`.
3. **Guardar** → **Reiniciar**.
4. Si tienes `GUILD_ID` en **⚙️ Config**, el `/jugar` aparece al instante;
   sin él, el sync global tarda hasta ~1 h.
5. `/help` lista los alters activos.
