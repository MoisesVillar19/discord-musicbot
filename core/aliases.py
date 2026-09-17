"""Alters configurables de slash commands (Sprint 5, D-01..D-03).

Discord no tiene aliases nativos: cada alter se registra como comando propio
que apunta al callback del canónico. La config vive en aliases.json (local,
gitignored); el repo trae aliases.example.json como plantilla.

Reglas: minúsculas, ^[\\w-]{1,32}$ (límite Discord), máx 5 por comando, sin
colisionar con canónicos ni entre sí. Los canónicos no se tocan.
"""
import json
import os
import re

ALIASES_FILE = "aliases.json"
ALIASES_EXAMPLE = "aliases.example.json"
MAX_ALIASES = 5

CANONICAL_COMMANDS = (
    "play", "pause", "resume", "skip", "stop", "disconnect",
    "queue", "nowplaying", "shuffle", "remove", "clear", "move", "help",
)

_NAME_RE = re.compile(r"^[\w-]{1,32}$")


class AliasError(ValueError):
    """Config de alters inválida: mensaje legible al arrancar."""


def default_aliases() -> dict:
    return {c: [] for c in CANONICAL_COMMANDS}


def load_aliases(path: str = ALIASES_FILE) -> dict:
    """Lee aliases.json (o {} si no existe) y lo valida. Lanza AliasError."""
    if not os.path.isfile(path):
        return default_aliases()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise AliasError(f"aliases.json inválido: {e}")
    if not isinstance(data, dict):
        raise AliasError("aliases.json debe ser un objeto {comando: [alters]}.")
    return validate_aliases(data)


def validate_aliases(data: dict) -> dict:
    cleaned = default_aliases()
    seen = set(CANONICAL_COMMANDS)
    for canonical, alters in data.items():
        if canonical not in CANONICAL_COMMANDS:
            raise AliasError(f"Comando base desconocido: '{canonical}'.")
        if not isinstance(alters, list):
            raise AliasError(f"'{canonical}' debe ser una lista de nombres.")
        if len(alters) > MAX_ALIASES:
            raise AliasError(f"'{canonical}' admite máx {MAX_ALIASES} alters.")
        unique = []
        for alt in alters:
            if not isinstance(alt, str):
                raise AliasError(f"Alter inválido en '{canonical}': debe ser texto.")
            a = alt.strip().lower()
            if not _NAME_RE.match(a):
                raise AliasError(
                    f"Alter inválido '{alt}': minúsculas, letras/números/_/-, máx 32.")
            if a in seen:
                raise AliasError(f"Alter '{a}' colisiona con otro comando o alter.")
            seen.add(a)
            unique.append(a)
        cleaned[canonical] = unique
    return cleaned


def save_aliases(data: dict, path: str = ALIASES_FILE) -> None:
    """Valida y guarda (lo usa el panel)."""
    cleaned = validate_aliases(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
        f.write("\n")
