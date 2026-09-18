# Docker — MusicBot

Correr el bot idéntico en cualquier máquina (Sprint 9, C-06).

## Requisitos

Docker + plugin compose instalados. Un `.env` válido al lado del `compose.yml`
(`DISCORD_TOKEN=…`; el resto opcional). El `.env` **no** entra a la imagen.

## Uso

```bash
docker compose up -d --build   # construir y arrancar
docker compose logs -f         # ver logs en vivo
docker compose up -d --build   # actualizar tras git pull
docker compose down            # detener
```

El servicio re-arranca solo (`unless-stopped`). FFmpeg ya viene en la imagen
(vía apt): no necesitas `bin/` ni instalar nada en el host.

## Notas

- Los slash globales tardan ~1 h en propagar; para probar usa `GUILD_ID` en `.env`.
- `aliases.json` y `trolls.json` locales no entran a la imagen (van los
  ejemplos como seed y se autocrean al arrancar).
- Es la base del plan 24/7: ver `../desarrollo/futuro-hosting-247.md`.
