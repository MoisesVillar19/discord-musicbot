"""Lectura/escritura de .env como funciones puras (Sprint 10, T-01).

El panel las usa; los tests las verifican sin GUI.
"""


def read_env(path: str) -> dict:
    values = {}
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return values
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            values[k.strip()] = v.strip()
    return values


def write_env(path: str, values: dict) -> None:
    """Actualiza claves preservando comentarios, orden y líneas ajenas."""
    try:
        with open(path, encoding="utf-8") as f:
            old = f.readlines()
    except OSError:
        old = []
    seen = set()
    with open(path, "w", encoding="utf-8") as f:
        for line in old:
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k = s.split("=", 1)[0].strip()
                if k in values:
                    f.write(f"{k}={values[k].strip()}\n")
                    seen.add(k)
                    continue
            f.write(line)
        for key, val in values.items():
            if key not in seen:
                f.write(f"{key}={val.strip()}\n")
