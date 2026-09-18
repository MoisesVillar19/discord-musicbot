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


def validate_config(values: dict) -> dict:
    """Devuelve {campo: error} para valores inválidos (vacío = todo ok)."""
    errors = {}
    for key in ("GUILD_ID", "DJ_ROLE_ID"):
        v = (values.get(key) or "").strip()
        if v and not v.isdigit():
            errors[key] = "Debe ser un ID numérico o vacío."
    chance = (values.get("TROLL_CHANCE") or "").strip()
    if chance:
        try:
            if not 0.0 <= float(chance) <= 1.0:
                raise ValueError
        except ValueError:
            errors["TROLL_CHANCE"] = "Debe ser un número entre 0.0 y 1.0."
    timeout = (values.get("EMPTY_TIMEOUT") or "").strip()
    if timeout:
        if not timeout.isdigit() or int(timeout) < 15:
            errors["EMPTY_TIMEOUT"] = "Debe ser un entero ≥ 15 (segundos)."
    level = (values.get("LOG_LEVEL") or "").strip().upper()
    if level and level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        errors["LOG_LEVEL"] = "DEBUG, INFO, WARNING o ERROR."
    return errors
