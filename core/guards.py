"""Guards como decoradores (Sprint 12).

Eliminan los try/except repetidos en cada handler: el guard responde el
mensaje de error (vía followup si ya hubo defer, si no vía response) y corta.
Sirven para funciones sueltas y para métodos de Cog (functools.wraps
preserva la firma que inspecciona app_commands).
"""

import functools

from config import DJ_ROLE_ID
from core import voice as voice_mgr
from utils.errors import MusicBotError, check_dj, user_message


def _find_interaction(args, kwargs):
    """Primer arg con forma de Interaction (vale suelta o método de Cog)."""
    for a in list(args) + list(kwargs.values()):
        if hasattr(a, "guild") and hasattr(a, "user") and hasattr(a, "response"):
            return a
    raise TypeError("require_*: no se encontró interaction en los argumentos")


async def _deny(interaction, error: MusicBotError):
    msg = user_message(error)
    if interaction.response.is_done():
        return await interaction.followup.send(msg, ephemeral=True)
    return await interaction.response.send_message(msg, ephemeral=True)


def require_voice(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        interaction = _find_interaction(args, kwargs)
        try:
            voice_mgr.check_same_voice(interaction.guild.voice_client, interaction.user.voice)
        except MusicBotError as e:
            return await _deny(interaction, e)
        return await func(*args, **kwargs)

    return wrapper


def require_dj(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        interaction = _find_interaction(args, kwargs)
        try:
            check_dj(interaction.user, DJ_ROLE_ID)
        except MusicBotError as e:
            return await _deny(interaction, e)
        return await func(*args, **kwargs)

    return wrapper
