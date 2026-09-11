from collections import deque

SONG_QUEUES = {}

def get_queue(guild_id: str) -> deque:
    if guild_id not in SONG_QUEUES:
        SONG_QUEUES[guild_id] = deque()
    return SONG_QUEUES[guild_id]

def clear_queue(guild_id: str):
    if guild_id in SONG_QUEUES:
        SONG_QUEUES[guild_id].clear()
