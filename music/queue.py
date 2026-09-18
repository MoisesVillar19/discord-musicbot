"""Cola de reproducción por servidor.

Cada cola es un deque de Track (dict, ver docs/desarrollo/diccionario.md).
Posiciones públicas en comandos: base 1 (la #1 es la siguiente en sonar).
"""
import random
from collections import deque

SONG_QUEUES = {}


def get_queue(guild_id: str) -> deque:
    if guild_id not in SONG_QUEUES:
        SONG_QUEUES[guild_id] = deque()
    return SONG_QUEUES[guild_id]


def clear_queue(guild_id: str):
    if guild_id in SONG_QUEUES:
        SONG_QUEUES[guild_id].clear()


def queue_size(guild_id: str) -> int:
    return len(get_queue(guild_id))


def peek_queue(guild_id: str) -> list:
    """Copia de la cola sin modificarla (para mostrar/paginar)."""
    return list(get_queue(guild_id))


def drop_first(guild_id: str, n: int) -> int:
    """/skip N: descarta las N primeras (la actual la corta vc.stop()).
    Devuelve cuántas descartó."""
    q = get_queue(guild_id)
    dropped = 0
    for _ in range(max(0, n)):
        if not q:
            break
        q.popleft()
        dropped += 1
    return dropped


def remove_track(guild_id: str, pos: int):
    """Elimina la canción en posición pos (base 1). Devuelve el Track o None."""
    q = get_queue(guild_id)
    if pos < 1 or pos > len(q):
        return None
    # deque no soporta del por índice: rotar es O(1) por lado.
    q.rotate(-(pos - 1))
    track = q.popleft()
    q.rotate(pos - 1)
    return track


def move_track(guild_id: str, from_pos: int, to_pos: int) -> bool:
    """Mueve la canción from_pos a to_pos (base 1, posición final). False si rango inválido."""
    q = get_queue(guild_id)
    n = len(q)
    if not (1 <= from_pos <= n and 1 <= to_pos <= n):
        return False
    if from_pos == to_pos:
        return True
    items = list(q)
    track = items.pop(from_pos - 1)
    items.insert(to_pos - 1, track)
    q.clear()
    q.extend(items)
    return True


def shuffle_queue(guild_id: str) -> bool:
    """Mezcla la cola. False si tiene < 2 canciones."""
    q = get_queue(guild_id)
    if len(q) < 2:
        return False
    items = list(q)
    random.shuffle(items)
    q.clear()
    q.extend(items)
    return True
