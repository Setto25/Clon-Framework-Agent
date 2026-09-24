#!/usr/bin/env python3
"""Conserva casos agenticos normales, ambiguos y fallidos como regresiones."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.evaluar_cierre_agente import evaluar_registro


RAIZ = Path(__file__).resolve().parent.parent
CASOS = RAIZ / "pruebas" / "casos_evaluacion_agente"
EVALUADOR = RAIZ / "scripts" / "evaluar_cierre_agente.py"


class PruebasEvaluacionCierreAgente(unittest.TestCase):
    """Comprueba la rubrica sin invocar un modelo ni registrar secretos."""

    def test_casos_conservan_resultado_esperado(self) -> None:
        """Evita que una regresion fallida se convierta accidentalmente en exito."""
        clasificaciones: set[str] = set()
        for ruta in sorted(CASOS.glob("*.json")):
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            clasificaciones.add(datos["clasificacion"])
            resultado = evaluar_registro(datos)
            observado = "APROBADO" if resultado["aprobado"] else "RECHAZADO"
            self.assertEqual(observado, datos["resultado_esperado"], ruta.name)
        self.assertEqual(clasificaciones, {"normal", "ambiguo", "fallido"})

    def test_suite_se_reproduce_con_un_comando(self) -> None:
        """Ejecuta todos los casos mediante la CLI documentable."""
        resultado = subprocess.run(
            [sys.executable, str(EVALUADOR), str(CASOS)],
            cwd=RAIZ,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertIn("normal-aprobado: APROBADO", resultado.stdout)
        self.assertIn("fallido-codigo-no-cero: RECHAZADO", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
