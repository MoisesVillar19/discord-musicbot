"""Tests de core/aliases.py (validación pura)."""
import unittest

from core.aliases import (
    MAX_ALIASES,
    AliasError,
    default_aliases,
    load_aliases,
    validate_aliases,
)


class AliasesTest(unittest.TestCase):
    def test_default_vacio(self):
        d = default_aliases()
        self.assertEqual(d["play"], [])
        self.assertIn("help", d)

    def test_ok_normaliza_minusculas(self):
        d = validate_aliases({"play": ["Jugar", "  rolita "]})
        self.assertEqual(d["play"], ["jugar", "rolita"])

    def test_comando_desconocido(self):
        with self.assertRaises(AliasError):
            validate_aliases({"bailar": ["x"]})

    def test_colision_canonico(self):
        with self.assertRaises(AliasError):
            validate_aliases({"skip": ["play"]})

    def test_colision_entre_alters(self):
        with self.assertRaises(AliasError):
            validate_aliases({"play": ["rola"], "skip": ["rola"]})

    def test_nombre_invalido(self):
        for bad in ["Mi Rola!", "con espacio", "x" * 33, "", "UPPER name!"]:
            with self.assertRaises(AliasError, msg=bad):
                validate_aliases({"play": [bad]})

    def test_maximo(self):
        self.assertEqual(MAX_ALIASES, 5)
        with self.assertRaises(AliasError):
            validate_aliases({"play": [f"a{i}" for i in range(6)]})
        validate_aliases({"play": [f"a{i}" for i in range(5)]})  # ok

    def test_no_lista(self):
        with self.assertRaises(AliasError):
            validate_aliases({"play": "jugar"})

    def test_archivo_inexistente(self):
        d = load_aliases("no_existe.json")
        self.assertEqual(d["play"], [])

    def test_canonicos_protegidos(self):
        # validate solo acepta claves canónicas: no hay forma de renombrar la base
        d = validate_aliases({})
        self.assertEqual(set(d), set(default_aliases()))


if __name__ == "__main__":
    unittest.main()
