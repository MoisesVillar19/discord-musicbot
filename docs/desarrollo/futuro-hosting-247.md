# Futuro: bot 24/7 (hosting) — MusicBot

> Documento de planes ideales. **No afecta al bot actual ni es necesario ahora.**
> El desarrollo sigue local hasta cerrar el Sprint 9. Aquí queda la intención,
> las opciones y cómo se haría cada una cuando toque.

## Intención

Que el bot esté online 24/7 sin depender de tu PC encendida. Hoy vive mientras
la consola/`panel.bat` corre; si apagas, se cae. Nada del código actual lo
impide: el bot ya es un proceso único con config por entorno (`.env`), cola en
memoria y logs a archivo. Hacerlo 24/7 es un tema de **dónde corre**, no de
reescribir nada.

## Precondiciones (para no hacerlo antes de tiempo)

- Sprint 9 cerrado: CI en verde + `Dockerfile`/`compose.yml` probados.
- Token en variable de entorno (nunca en la imagen).
- `logs/` con rotación o volumen (hoy `FileHandler` simple: en 24/7 hay que
  rotar para que no crezca sin fin).

## Opciones

| Opción | Costo | Cómo se haría | Pros | Contras |
|---|---|---|---|---|
| Tu PC encendida | $0 | Estado actual (`panel.bat` o servicio Windows) | Cero setup | Se cae al apagar/suspender |
| Raspberry Pi en casa | ~$0 (solo hardware) | Docker ARM + `compose up -d` + auto-arranque | Silenciosa, tuya, 24/7 | Red doméstica (cortes de luz/internet) |
| Oracle Cloud Free Tier | $0 permanente | VM ARM 4c/24GB, Docker, `compose`, firewall UDP/TCP voz | Gratis real, siempre online | Pide tarjeta, setup manual, free tier puede cambiar |
| VPS barato (Hetzner/Contabo) | ~€4–6/mes | Igual que Oracle pero pagado | Simple, sin sorpresas, buen uptime | Costo mensual |
| Railway/Render free | $0 con límites | No recomendado | — | **Se duermen por inactividad: no sirven para bots** |

## Cómo sería el despliegue (común a VPS/Raspberry/Oracle)

1. Imagen Docker del repo (C-06): `python:3.11-slim` + `ffmpeg` por apt.
2. En el host: solo `compose.yml` + `.env` con `DISCORD_TOKEN` (y `BOT_NAME`).
3. `docker compose up -d` + `restart: unless-stopped` (auto-rearranque).
4. Logs: `docker logs` o volumen a `logs/` con rotación.
5. Actualizar: `git pull` + `docker compose up -d --build` (2 comandos).

## Criterio de decisión (cuándo mover)

- Seguir local mientras: un admin, pocos servidores, desarrollo activo.
- Mover cuando: el bot se use a diario y los cortes molesten, o quieras
  invitarlo a servidores ajenos con uptime serio.
- Recomendación: Raspberry si ya tienes una; si no, Oracle Free; VPS pago
  solo si quieres cero mantenimiento.

## Qué NO incluye este plan

- Cambios de código del bot (ya es compatible).
- Base de datos persistente (la cola es en memoria por diseño; si algún día se
  quiere cola persistente, es otro sprint, no hosting).
- Dominio/HTTPS (innecesario: el bot no expone web, solo sale a Discord).
