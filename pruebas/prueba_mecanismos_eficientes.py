#!/usr/bin/env python3
"""Verifica que las herramientas eficientes reducen bytes entregados frente a lecturas completas."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


DEPENDENCIAS_DISPONIBLES = all(
    importlib.util.find_spec(modulo) is not None
    for modulo in ("openai", "google.genai", "fastapi", "httpx")
)

if DEPENDENCIAS_DISPONIBLES:
    from scripts.evaluar_desarrollo_web_gemini import ejecutar_herramienta
    from scripts.evaluar_desarrollo_web_qwen import (
        FIXTURE,
        ejecutar_herramienta_eficiente,
        preparar_contexto_herramientas_eficientes,
    )


def _bytes(resultado: dict) -> int:
    return len(json.dumps(resultado, ensure_ascii=False).encode("utf-8"))


@unittest.skipUnless(
    DEPENDENCIAS_DISPONIBLES,
    "Requiere openai, google-genai, FastAPI y httpx",
)
class PruebasMecanismosEficientes(unittest.TestCase):
    """Comprueba reduccion de bytes sin consumir credito de API."""

    def setUp(self) -> None:
        self._temporal = tempfile.mkdtemp(prefix="mecanismos-eficientes-")
        self.entorno = Path(self._temporal) / "aplicacion"
        shutil.copytree(FIXTURE, self.entorno)
        preparar_contexto_herramientas_eficientes(self.entorno)

    def tearDown(self) -> None:
        shutil.rmtree(self._temporal, ignore_errors=True)

    def test_buscar_texto_entrega_menos_bytes_que_lectura_completa(self) -> None:
        """buscar_texto debe devolver menos del 20% de bytes de una lectura sin limite."""
        resultado_completo = ejecutar_herramienta(
            self.entorno, "leer_archivo", {"ruta": "backend/contrato_contexto.py"}
        )
        resultado_busqueda, _, _ = ejecutar_herramienta_eficiente(
            self.entorno,
            "buscar_texto",
            {"ruta": "backend/contrato_contexto.py", "texto": "MARCADOR_API"},
        )
        self.assertLess(_bytes(resultado_busqueda), _bytes(resultado_completo) * 0.20)
        self.assertEqual(len(resultado_busqueda["coincidencias"]), 1)
        self.assertIn("MARCADOR_API", resultado_busqueda["coincidencias"][0]["fragmento"])

    def test_leer_lote_acotado_entrega_menos_bytes_que_cuatro_lecturas_completas(self) -> None:
        """leer_lote con cuatro rangos de 8 lineas debe ser menor al 10% de cuatro lecturas completas."""
        from scripts.evaluar_desarrollo_web_gemini import FIXTURE as _F
        archivos = ["backend/contrato_contexto.py", "interfaz/contrato_contexto.js",
                    "backend/aplicacion.py", "interfaz/aplicacion.js"]
        bytes_completos = sum(
            _bytes(ejecutar_herramienta(self.entorno, "leer_archivo", {"ruta": r}))
            for r in archivos
        )
        resultado_lote, truncadas, lotes = ejecutar_herramienta_eficiente(
            self.entorno,
            "leer_lote",
            {
                "lecturas": [
                    {"ruta": "backend/contrato_contexto.py", "inicio": 120, "limite": 8},
                    {"ruta": "interfaz/contrato_contexto.js", "inicio": 120, "limite": 8},
                    {"ruta": "backend/aplicacion.py", "inicio": 1, "limite": 8},
                    {"ruta": "interfaz/aplicacion.js", "inicio": 1, "limite": 8},
                ]
            },
        )
        self.assertEqual(lotes, 1)
        self.assertEqual(len(resultado_lote["lecturas"]), 4)
        self.assertLess(_bytes(resultado_lote), bytes_completos * 0.15)
        self.assertIn("MARCADOR_API", resultado_lote["lecturas"][0]["contenido"])
        self.assertIn("MARCADOR_INTERFAZ", resultado_lote["lecturas"][1]["contenido"])
        self.assertEqual(truncadas, 2)

    def test_leer_archivo_trunca_en_el_limite_declarado(self) -> None:
        """leer_archivo con limite=5 debe retornar exactamente 5 lineas y marcar truncado."""
        resultado, truncado, _ = ejecutar_herramienta_eficiente(
            self.entorno,
            "leer_archivo",
            {"ruta": "backend/contrato_contexto.py", "inicio": 1, "limite": 5},
        )
        self.assertTrue(truncado)
        self.assertEqual(len(resultado["contenido"].splitlines()), 5)
        self.assertEqual(resultado["limite"], 5)
        self.assertTrue(resultado["truncado"])

    def test_leer_archivo_sin_limite_trunca_en_ochenta_lineas(self) -> None:
        """El techo implicito de 80 lineas se aplica aunque el modelo no declare limite."""
        resultado, truncado, _ = ejecutar_herramienta_eficiente(
            self.entorno,
            "leer_archivo",
            {"ruta": "backend/contrato_contexto.py"},
        )
        self.assertTrue(truncado)
        self.assertEqual(len(resultado["contenido"].splitlines()), 80)
        self.assertTrue(resultado["truncado"])

    def test_buscar_texto_localiza_marcador_interfaz_en_js(self) -> None:
        """buscar_texto funciona en archivos .js y encuentra el segundo marcador."""
        resultado, _, _ = ejecutar_herramienta_eficiente(
            self.entorno,
            "buscar_texto",
            {"ruta": "interfaz/contrato_contexto.js", "texto": "MARCADOR_INTERFAZ"},
        )
        self.assertEqual(len(resultado["coincidencias"]), 1)
        self.assertIn("MARCADOR_INTERFAZ", resultado["coincidencias"][0]["fragmento"])


if __name__ == "__main__":
    unittest.main()
