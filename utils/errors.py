"""Errores de dominio + mapa a mensajes de usuario (Sprint 2, A-13)."""


class MusicBotError(Exception):
    """Base de errores controlados: terminan en mensaje, nunca en crash."""


class WrongChannelError(MusicBotError):
    """El usuario no está en el mismo canal de voz que el bot."""


class NothingPlayingError(MusicBotError):
    """No hay nada sonando/pausado para el comando pedido."""


class NotConnectedError(MusicBotError):
    """El bot no está en ningún canal de voz."""


USER_MESSAGES = {
    WrongChannelError: "❌ Debes estar en el mismo canal de voz que el bot.",
    NothingPlayingError: "🔇 No hay nada reproduciéndose.",
    NotConnectedError: "⚠️ No estoy en un canal de voz.",
}


def user_message(error: BaseException) -> str:
    """Mensaje legible para cualquier error (controlado o no)."""
    for cls, msg in USER_MESSAGES.items():
        if isinstance(error, cls):
            return msg
    return f"⚠️ Algo falló: {type(error).__name__}. Inténtalo de nuevo."
