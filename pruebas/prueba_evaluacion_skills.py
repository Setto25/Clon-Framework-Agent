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


def crear_ejecucion(
    variante: str, tokens: int, exito: bool = True, repeticion: int = 1
) -> dict[str, object]:
    """Construye una observacion minima con metricas explicitas."""
    return {
        "escenario": "revisar-repositorio",
        "repeticion": repeticion,
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
        """Declara un experimento historico que conserva eficacia y reduce tokens."""
        return {
            "version": 1,
            "skill": "optimizar-contexto",
            "criterios": {"margen_no_inferioridad": 0, "ahorro_minimo_tokens": 0.2},
            "ejecuciones": [
                crear_ejecucion("control", 900),
                crear_ejecucion("skill", 500),
            ],
        }

    def crear_experimento_sistema(self) -> dict[str, object]:
        """Declara las tres variantes que separan indice y Skill."""
        return {
            "version": 1,
            "skill": "optimizar-contexto",
            "criterios": {"margen_no_inferioridad": 0, "ahorro_minimo_tokens": 0.2},
            "ejecuciones": [
                crear_ejecucion("control_puro", 1000),
                crear_ejecucion("indice", 700),
                crear_ejecucion("skill", 500),
            ],
        }

    def crear_experimento_desarrollo(self) -> dict[str, object]:
        """Declara variantes para aislar seleccion y tamano del protocolo."""
        return {
            "version": 1,
            "skill": "optimizar-contexto",
            "criterios": {"margen_no_inferioridad": 0, "ahorro_minimo_tokens": 0.2},
            "ejecuciones": [
                crear_ejecucion("control_puro", 1000),
                crear_ejecucion("indice", 700),
                crear_ejecucion("skill_adaptativa", 500),
                crear_ejecucion("skill_extendida", 800),
                crear_ejecucion("extendido_compacto", 500),
            ],
        }

    def crear_experimento_desarrollo_autoritativo(self) -> dict[str, object]:
        """Declara la variante donde el indice fresco reemplaza el listado general."""
        return {
            "version": 1,
            "skill": "optimizar-contexto",
            "criterios": {"margen_no_inferioridad": 0, "ahorro_minimo_tokens": 0.2},
            "ejecuciones": [
                crear_ejecucion("control_puro", 1000),
                crear_ejecucion("indice_autoritativo", 600),
                crear_ejecucion("skill_adaptativa", 500),
                crear_ejecucion("skill_extendida", 800),
                crear_ejecucion("extendido_compacto", 500),
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

    def test_separa_ahorro_pareado_de_intentos_incompletos(self) -> None:
        """Evita presentar abandonos baratos como ahorro causal del tratamiento."""
        experimento = self.crear_experimento()
        experimento["ejecuciones"] = [
            crear_ejecucion("control", 100, exito=False, repeticion=1),
            crear_ejecucion("skill", 400, repeticion=1),
            crear_ejecucion("control", 200, exito=False, repeticion=2),
            crear_ejecucion("skill", 500, repeticion=2),
            crear_ejecucion("control", 900, repeticion=3),
            crear_ejecucion("skill", 600, repeticion=3),
        ]
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        informe = json.loads(resultado.stdout)
        self.assertFalse(informe["comparacion_ahorro_valida"])
        self.assertEqual(informe["pares_exitosos"], 1)
        self.assertAlmostEqual(informe["ahorro_tokens_pareados"], 0.3)
        self.assertAlmostEqual(informe["ahorro_tokens_por_exito"], 0.6)
        self.assertTrue(informe["observaciones"])

    def test_descompone_ahorro_total_indice_y_skill(self) -> None:
        """Distingue el beneficio del indice del aporte marginal de la Skill."""
        resultado = self.ejecutar(self.crear_experimento_sistema())
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        informe = json.loads(resultado.stdout)
        self.assertEqual(
            set(informe["variantes"]),
            {"control_puro", "indice", "skill"},
        )
        comparaciones = informe["comparaciones"]
        self.assertAlmostEqual(
            comparaciones["ahorro_indice_frente_control_puro"],
            1 - (800 / 1100),
        )
        self.assertAlmostEqual(
            comparaciones["ahorro_skill_frente_indice"],
            1 - (600 / 800),
        )
        self.assertAlmostEqual(
            comparaciones["ahorro_sistema_frente_control_puro"],
            1 - (600 / 1100),
        )

    def test_rechaza_experimento_de_tres_variantes_incompleto(self) -> None:
        """Impide atribuir al sistema una comparacion sin la variante intermedia."""
        experimento = self.crear_experimento_sistema()
        ejecuciones = experimento["ejecuciones"]
        self.assertIsInstance(ejecuciones, list)
        if isinstance(ejecuciones, list):
            experimento["ejecuciones"] = [
                ejecucion
                for ejecucion in ejecuciones
                if isinstance(ejecucion, dict) and ejecucion.get("variante") != "indice"
            ]
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("control_puro/indice/skill", resultado.stderr)

    def test_rechaza_si_el_indice_no_satisface_la_rubrica(self) -> None:
        """Exige eficacia tambien en la variante que aisla el preanalisis."""
        experimento = self.crear_experimento_sistema()
        ejecuciones = experimento["ejecuciones"]
        self.assertIsInstance(ejecuciones, list)
        if isinstance(ejecuciones, list) and isinstance(ejecuciones[1], dict):
            ejecuciones[1]["exito"] = False
            ejecuciones[1]["pruebas_aprobadas"] = False
        resultado = self.ejecutar(experimento)
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn("La variante con indice no satisface", resultado.stdout)

    def test_compara_seleccion_y_protocolo_compacto(self) -> None:
        """Separa el modo forzado del coste de cargar la Skill completa."""
        resultado = self.ejecutar(self.crear_experimento_desarrollo())
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        informe = json.loads(resultado.stdout)
        self.assertEqual(
            set(informe["variantes"]),
            {
                "control_puro",
                "indice",
                "skill_adaptativa",
                "skill_extendida",
                "extendido_compacto",
            },
        )
        comparaciones = informe["comparaciones"]
        self.assertAlmostEqual(
            informe["ahorro_tokens"],
            1 - (600 / 1100),
        )
        self.assertAlmostEqual(
            comparaciones["ahorro_sistema_adaptativo_frente_control_puro"],
            1 - (600 / 1100),
        )
        self.assertAlmostEqual(
            comparaciones["ahorro_skill_extendida_frente_adaptativa"],
            1 - (900 / 600),
        )
        self.assertAlmostEqual(
            comparaciones["ahorro_extendido_compacto_frente_skill_extendida"],
            1 - (600 / 900),
        )

    def test_compara_indice_autoritativo_sin_reinterpretar_el_v3(self) -> None:
        """Mantiene los informes v3 y distingue la nueva politica de herramienta."""
        resultado = self.ejecutar(self.crear_experimento_desarrollo_autoritativo())
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        informe = json.loads(resultado.stdout)
        self.assertIn("indice_autoritativo", informe["variantes"])
        self.assertAlmostEqual(
            informe["comparaciones"]["ahorro_indice_autoritativo_frente_control_puro"],
            1 - (700 / 1100),
        )


if __name__ == "__main__":
    unittest.main()
