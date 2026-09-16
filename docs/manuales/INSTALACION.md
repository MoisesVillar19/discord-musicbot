# Instalación detallada — MusicBot

## 1. Requisitos

- Windows 10/11, Python 3.11 o 3.12 (recomendado 3.11).
- FFmpeg: o bien en `PATH`, o bien en `bin/ffmpeg/ffmpeg.exe`.
- Token de bot de Discord con intent **Message Content** activado.

## 2. Crear el bot en Discord

1. Ve a https://discord.com/developers/applications → New Application.
2. Pestaña **Bot** → Reset Token → copia el token.
3. Activa **Message Content Intent** (Privileged Gateway Intents).
4. Pestaña **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`.
   - Permisos: View Channels, Send Messages, Embed Links, Connect, Speak.
5. Abre la URL generada e invita al bot a tu servidor.

## 3. Instalar el proyecto

```bat
git clone https://github.com/MoisesVillar19/MusicBot.git
cd MusicBot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

Contenido de `.env`:

```
DISCORD_TOKEN=tu_token_aqui
```

## 4. FFmpeg

Opción A (recomendada): instala FFmpeg y agrégalo al PATH.
Verifica con:

```bat
ffmpeg -version
```

Opción B (portable): descarga `ffmpeg.exe` y colócalo en:

```
bin/ffmpeg/ffmpeg.exe
```

El bot (`bot.py::_ffmpeg_executable`) prefiere el binario local si existe,
y si no, usa el del PATH. `bin/` está en `.gitignore` y no se sube a GitHub.

## 5. Ejecutar

```bat
venv\Scripts\activate
python bot.py
```

Deberías ver: `<tu_bot> is online!`

Alternativa: doble clic en `start_bot.bat`.

> Si `start_bot.bat` tiene una ruta fija (`D:\MusicBot`), edítalo o ejecútalo
> desde la carpeta del proyecto.

## 6. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `DISCORD_TOKEN no encontrado` | Falta `.env` | Copia `.env.example` → `.env` y pega el token |
| `Privileged intent ... message_content` | Intent apagado | Actívalo en el portal y reinicia el bot |
| No suena / error FFmpeg | Sin FFmpeg | Instala FFmpeg o pon `bin/ffmpeg/ffmpeg.exe` |
| `/play texto` dice "No se encontraron resultados" | yt-dlp desactualizado o bloqueo de YouTube | `pip install -U yt-dlp`, reintenta; prueba con URL directa |
| Comandos slash no aparecen | Falta `applications.commands` o sync pendiente | Reinvita con ese scope, espera unos minutos, reinicia Discord con Ctrl+R |
| `ValueError: too many values to unpack` | Versión vieja del bot | Actualiza: este bug ya está corregido (cola de 3 tuplas) |
