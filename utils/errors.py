"""Errores de dominio + mapa a mensajes de usuario (Sprint 2, A-13)."""


class MusicBotError(Exception):
    """Base de errores controlados: terminan en mensaje, nunca en crash."""


class WrongChannelError(MusicBotError):
    """El usuario no está en el mismo canal de voz que el bot."""


class NothingPlayingError(MusicBotError):
    """No hay nada sonando/pausado para el comando pedido."""


class NotConnectedError(MusicBotError):
    """El bot no está en ningún canal de voz."""


class NotDJError(MusicBotError):
    """El usuario no tiene el rol DJ requerido."""


USER_MESSAGES = {
    WrongChannelError: "❌ Debes estar en el mismo canal de voz que el bot.",
    NothingPlayingError: "🔇 No hay nada reproduciéndose.",
    NotConnectedError: "⚠️ No estoy en un canal de voz.",
    NotDJError: "❌ Necesitas el rol DJ para este comando.",
}


def check_dj(member, dj_role_id) -> None:
    """Lanza NotDJError si hay rol configurado y el miembro no lo tiene."""
    if not dj_role_id:
        return
    roles = getattr(member, "roles", []) or []
    if not any(getattr(r, "id", None) == dj_role_id for r in roles):
        raise NotDJError()


def user_message(error: BaseException) -> str:
    """Mensaje legible para cualquier error (controlado o no)."""
    for cls, msg in USER_MESSAGES.items():
        if isinstance(error, cls):
            return msg
    return f"⚠️ Algo falló: {type(error).__name__}. Inténtalo de nuevo."
