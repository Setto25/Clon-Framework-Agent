#!/usr/bin/env python3
"""Comprueba el indice local compacto para cambios transversales."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.analizar_impacto import analizar_impacto
from scripts.validar_resultado_agente import RUTAS_ESENCIALES_MIGRACION


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
TERMINOS_ESCENARIO: list[str] = [
    "optimizar-contexto",
    "CORE_AUTOMATICO",
    "core automatico",
    "Skills opcionales",
]


class PruebasAnalisisImpacto(unittest.TestCase):
    """Verifica cobertura exhaustiva local con una salida acotada."""

    def setUp(self) -> None:
        """Crea un arbol pequeno con referencias y artefactos excluidos."""
        self.temporal = tempfile.TemporaryDirectory(prefix="analisis-impacto-")
        self.raiz = Path(self.temporal.name)
        (self.raiz / "scripts").mkdir()
        (self.raiz / "pruebas").mkdir()
        (self.raiz / "resultados").mkdir()
        (self.raiz / "scripts" / "catalogo.py").write_text(
            "CORE_AUTOMATICO = ('optimizar-contexto',)\n",
            encoding="utf-8",
        )
        (self.raiz / "pruebas" / "prueba_catalogo.py").write_text(
            "self.assertIn('OPTIMIZAR-CONTEXTO', catalogo)\n",
            encoding="utf-8",
        )
        (self.raiz / "resultados" / "salida.txt").write_text(
            "optimizar-contexto\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        """Elimina el arbol temporal despues de cada comprobacion."""
        self.temporal.cleanup()

    def test_agrupa_por_archivo_y_clasifica_sin_distinguir_mayusculas(self) -> None:
        """Agrupa coincidencias y conserva una muestra literal por ruta."""
        resultado = analizar_impacto(
            self.raiz,
            ["optimizar-contexto", "CORE_AUTOMATICO"],
        )
        archivos = {str(item["ruta"]): item for item in resultado["archivos"]}
        self.assertEqual(set(archivos), {"pruebas/prueba_catalogo.py", "scripts/catalogo.py"})
        self.assertEqual(archivos["pruebas/prueba_catalogo.py"]["categoria"], "pruebas")
        self.assertEqual(archivos["scripts/catalogo.py"]["categoria"], "codigo")
        self.assertIn(
            "OPTIMIZAR-CONTEXTO",
            archivos["pruebas/prueba_catalogo.py"]["fragmentos"][0]["texto"],
        )

    def test_excluye_resultados_generados(self) -> None:
        """Evita devolver artefactos que no forman parte de la fuente."""
        resultado = analizar_impacto(self.raiz, ["optimizar-contexto"])
        rutas = {str(item["ruta"]) for item in resultado["archivos"]}
        self.assertNotIn("resultados/salida.txt", rutas)
        self.assertEqual(resultado["archivos_examinados"], 2)

    def test_limita_archivos_y_fragmentos_sin_ocultar_el_total(self) -> None:
        """Marca truncamiento y conserva el total aun con una salida pequena."""
        resultado = analizar_impacto(
            self.raiz,
            ["optimizar-contexto"],
            maximo_archivos=1,
            maximo_fragmentos=0,
        )
        self.assertEqual(resultado["archivos_con_coincidencias"], 2)
        self.assertEqual(len(resultado["archivos"]), 1)
        self.assertTrue(resultado["truncado"])
        self.assertEqual(resultado["archivos"][0]["fragmentos"], [])

    def test_escenario_real_cubre_rutas_esenciales_con_indice_compacto(self) -> None:
        """Impide que el preanalisis pierda la cobertura exigida por la rubrica."""
        resultado = analizar_impacto(RAIZ_FRAMEWORK, TERMINOS_ESCENARIO)
        rutas = {str(item["ruta"]) for item in resultado["archivos"]}
        self.assertEqual(RUTAS_ESENCIALES_MIGRACION - rutas, set())
        self.assertFalse(resultado["truncado"])
        self.assertLessEqual(resultado["caracteres_serializados"], 10000)


if __name__ == "__main__":
    unittest.main()
