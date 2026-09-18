# Futuro: bot 24/7 (hosting) — MusicBot

> Documento de planes ideales. **No afecta al bot actual ni es necesario ahora.**
> El desarrollo sigue local. Aquí queda la intención, las opciones con detalle
> y el paso a paso para cuando toque (probablemente nunca la nube; la Pi sí).

## Intención

Que el bot esté online 24/7 sin depender de tu PC encendida. Hacerlo 24/7 es
un tema de **dónde corre**, no de reescribir nada: proceso único, config por
entorno, cola en memoria, logs a archivo.

## Precondiciones (para no hacerlo antes de tiempo)

- Sprint 9 cerrado ✅ (CI verde + `Dockerfile`/`compose.yml` probados).
- Token en variable de entorno (nunca en la imagen) ✅ (ya es así).
- `logs/` con rotación (pendiente menor: hoy `FileHandler` simple; en 24/7
  hay que rotar para que no crezca sin fin).

## Opciones comparadas

| Opción | Costo | Uptime | Esfuerzo | Veredicto |
|---|---|---|---|---|
| Tu PC encendida | $0 | Mientras no la apagues | Cero (actual) | Bien para desarrollo |
| Raspberry Pi en casa | ~€75–95 únicos, $0/mes | 24/7 salvo corte luz/internet | Medio (guía abajo) | **Recomendada si se compra hardware** |
| Oracle Cloud Free Tier | $0 permanente | Alto | Medio-alto (tarjeta + setup) | Alternativa $0 sin hardware |
| VPS barato | ~€4–6/mes | Alto | Bajo | Solo si quieres cero mantenimiento |
| Railway/Render free | $0 con límites | Malo (se duermen) | Bajo | **Descartados para bots** |

---

## Guía Raspberry Pi (paso a paso, para cuando se compre)

### 1. Para qué sirve aquí
Mini-PC de ~5W, silenciosa y sin ventilador, enchufada al router corriendo
`docker compose up -d` para siempre. El bot no cambia ni una línea.

### 2. Especificaciones
- **Modelo:** Pi 4 (2GB mínimo, **4GB ideal**) o Pi 5 (cualquiera). Pi 3B+ va
  justa con yt-dlp + FFmpeg en picos de extracción.
- **Por qué basta:** el bot es un proceso Python + FFmpeg a Opus; picos breves
  de CPU/RAM al extraer playlists. 2GB bien, 4GB cómodo.
- **Almacenamiento:** microSD 32GB clase A2 mínimo; **mejor SSD USB** (las SD
  se degradan con escrituras 24/7 de logs).
- **Red:** Ethernet al router ideal; WiFi suma latencia al audio.
- **SO:** Raspberry Pi OS Lite 64-bit (sin escritorio, ahorra ~500MB RAM).
- **Compatibilidad ARM64:** `python:3.11-slim` tiene imagen ARM oficial;
  `discord.py`, `PyNaCl` y `yt-dlp` tienen wheels ARM. El `compose.yml`
  funciona tal cual. Lo único x86-dependiente (`bin/ffmpeg.exe`) ya quedó
  fuera en el S9 (FFmpeg vía apt en la imagen).

### 3. Instalación (una sola vez)
```bash
# 1. Flashear Pi OS Lite 64-bit + habilitar SSH (Raspberry Pi Imager)
ssh pi@raspberrypi.local
# 2. Docker
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi  # re-login
# 3. Bot
git clone https://github.com/MoisesVillar19/discord-musicbot.git
cd discord-musicbot
cp .env.example .env && nano .env   # DISCORD_TOKEN, BOT_NAME, GUILD_ID vacío
docker compose up -d
docker compose logs -f              # ver arranque en vivo
```

### 4. Uso diario
```bash
docker compose logs -f              # consola remota (como start_bot.bat)
docker compose up -d --build        # actualizar tras git pull
docker compose down / up -d         # detener / arrancar
```

### 5. Fricción conocida: alters y panel
El panel tkinter corre en tu PC y edita los archivos **de tu PC**, no los de
la Pi. Opciones cuando toque:
- **A (simple):** editar `aliases.json`/`trolls.json`/`.env` por SSH (`nano`) o
  WinSCP, luego `docker compose restart`.
- **B (git):** repo privado con tus JSON locales; la Pi hace `git pull`.
- **C (futura):** panel v2 con despliegue remoto (ver `futuro-funciones.md`).

### 6. Costo realista
Pi 4 4GB (~€55–75) + fuente oficial (~€10) + SD 32GB (~€10) + case ≈
**€75–95 únicos**, ~€5–8/año de luz.

---

## Guía nube (documentada por si acaso; no se implementará por ahora)

### Oracle Cloud Free Tier ($0 permanente)
- VM Ampere ARM: 4 cores + 24GB RAM gratis (límite de cuenta free).
- Pasos: crear cuenta (pide tarjeta, no cobra) → instancia Ubuntu 22.04 ARM →
  abrir puertos (Discord solo necesita **salida**; sin puertos de entrada salvo
  tu SSH) → Docker + compose como en la Pi.
- Contras: setup manual, la free tier puede cambiar de condiciones, soporte nulo.

### VPS barato (~€4–6/mes: Hetzner, Contabo)
- Mismo despliegue que Oracle pero x86_64 (tu imagen ya es multi-uso; Docker
  la reconstruye para la arch del host).
- Pros: uptime serio, IP fija, cero mantenimiento. Contras: costo mensual para
  un proyecto personal.
- Cuándo tendría sentido: el bot en servidores ajenos con uptime comprometido.

### Por qué Railway/Render free no sirven
Ambos duermen el servicio por inactividad HTTP. Un bot de Discord mantiene una
conexión websocket permanente sin tráfico HTTP: lo duermen igual. Descartados.

---

## Qué NO incluye este plan

- Cambios de código del bot (ya es compatible).
- Base de datos persistente (cola en memoria por diseño; sería otro sprint).
- Dominio/HTTPS (el bot no expone web, solo sale a Discord).
