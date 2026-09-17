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
  subproceso; el punto ● indica estado. Solo una instancia: Discord desconecta
  un segundo proceso con el mismo token.

## Primeros alters

1. En **🎭 Alters**, pon p. ej. `jugar, rolita` en `/play`.
2. **Guardar** → **Reiniciar**.
3. Si tienes `GUILD_ID` en **⚙️ Config**, el `/jugar` aparece al instante;
   sin él, el sync global tarda hasta ~1 h.
4. `/help` lista los alters activos.
