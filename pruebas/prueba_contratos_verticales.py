#!/usr/bin/env python3
"""Comprueba que nueve regresiones verticales bloqueen el cierre."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.diagnosticar_tarea import diagnosticar


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "contratos-verticales"


class PruebasContratosVerticales(unittest.TestCase):
    """Ejecuta los contratos ficticios registrados por el proyecto."""

    def test_detecta_las_nueve_regresiones(self) -> None:
        """Impide que un build u otra puerta aislada oculte fallos entre capas."""
        resultado = diagnosticar(FIXTURE)
        self.assertEqual(resultado["cobertura"], "DECLARADA")
        self.assertEqual(resultado["total_fallos"], 9)
        self.assertTrue(resultado["bloquea_cierre"])
        self.assertEqual(resultado["verificaciones"][0]["estado"], "FALLIDO")
        self.assertNotEqual(resultado["verificaciones"][0]["codigo_salida"], 0)


if __name__ == "__main__":
    unittest.main()
