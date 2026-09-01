#!/usr/bin/env python3
"""Comprueba la evaluacion pareada de eficacia y consumo de Skills."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
EVALUADOR = RAIZ_FRAMEWORK / "scripts" / "evaluar_eficacia_skills.py"


def crear_ejecucion(variante: str, tokens: int, exito: bool = True) -> dict[str, object]:
    """Construye una observacion minima con metricas explicitas."""
    return {
        "escenario": "revisar-repositorio",
        "repeticion": 1,
        "variante": variante,
        "exito": exito,
        "pruebas_aprobadas": exito,
        "tokens_entrada": tokens,
        "tokens_salida": 100,
        "llamadas_herramientas": 4,
        "duracion_segundos": 10,
        "reintentos": 0,
    }


class PruebasEvaluacionSkills(unittest.TestCase):
    """Verifica umbrales, pares y codigos de salida del evaluador."""

    def ejecutar(self, datos: dict[str, object]) -> subprocess.CompletedProcess[str]:
        """Ejecuta el evaluador con una entrada temporal UTF-8."""
        with tempfile.TemporaryDirectory(prefix="evaluacion-skills-") as temporal:
            entrada = Path(temporal) / "experimento.json"
            entrada.write_text(json.dumps(datos), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(EVALUADOR), str(entrada)],
                cwd=RAIZ_FRAMEWORK,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

    def crear_experimento(self) -> dict[str, object]:
        """Declara un experimento que conserva eficacia y reduce tokens."""
        return {
            "version": 1,
            "skill": "optimizar-contexto",
            "criterios": {"margen_no_inferioridad": 0, "ahorro_minimo_tokens": 0.2},
            "ejecuciones": [
                crear_ejecucion("control", 900),
                crear_ejecucion("skill", 500),
            ],
        }

    def test_aprueba_ahorro_sin_perdida_de_eficacia(self) -> None:
        """Aprueba cuando ambas variantes cumplen y la Skill usa menos tokens."""
        resultado = self.ejecutar(self.crear_experimento())
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertIsInstance(informe, dict)
        self.assertTrue(informe.get("aprobada") if isinstance(informe, dict) else False)

    def test_rechaza_ahorro_con_perdida_de_eficacia(self) -> None:
        """Rechaza una Skill barata que deja de satisfacer la tarea."""
        experimento = self.crear_experimento()
        experimento["ejecuciones"] = [
            crear_ejecucion("control", 900),
            crear_ejecucion("skill", 300, exito=False),
        ]
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn("inferior", resultado.stdout)

    def test_rechaza_ejecuciones_no_pareadas(self) -> None:
        """Impide comparar escenarios diferentes entre control y Skill."""
        experimento = self.crear_experimento()
        ejecuciones = experimento["ejecuciones"]
        self.assertIsInstance(ejecuciones, list)
        if isinstance(ejecuciones, list) and isinstance(ejecuciones[1], dict):
            ejecuciones[1]["escenario"] = "otro-escenario"
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("mismos escenarios", resultado.stderr)

    def test_rechaza_ahorro_si_ambas_variantes_fallan(self) -> None:
        """Impide aprobar por igualdad cuando ambas tasas de eficacia son cero."""
        experimento = self.crear_experimento()
        experimento["ejecuciones"] = [
            crear_ejecucion("control", 900, exito=False),
            crear_ejecucion("skill", 300, exito=False),
        ]
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        informe = json.loads(resultado.stdout)
        self.assertFalse(informe["aprobada"])
        self.assertIn("El control no satisface", resultado.stdout)
        self.assertIn("La Skill no satisface", resultado.stdout)

    def test_rechaza_si_control_falla_aunque_skill_apruebe(self) -> None:
        """Exige una linea base valida antes de atribuir una mejora al tratamiento."""
        experimento = self.crear_experimento()
        experimento["ejecuciones"] = [
            crear_ejecucion("control", 900, exito=False),
            crear_ejecucion("skill", 300),
        ]
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn("El control no satisface", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
