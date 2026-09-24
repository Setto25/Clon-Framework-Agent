#!/usr/bin/env python3
"""Comprueba el manifiesto tipado y su ejecucion sin shell."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.contrato_validacion import (
    Comprobacion,
    cargar_contrato,
    ejecutar_comprobacion,
)


class PruebasContratoValidacion(unittest.TestCase):
    """Rechaza contratos ambiguos antes de ejecutar comandos."""

    def setUp(self) -> None:
        """Prepara una raiz aislada con dos modulos validos."""
        self.temporal = tempfile.TemporaryDirectory(prefix="contrato-validacion-")
        self.raiz = Path(self.temporal.name)
        (self.raiz / "backend").mkdir()
        (self.raiz / "frontend").mkdir()

    def tearDown(self) -> None:
        """Elimina exclusivamente la raiz temporal del caso."""
        self.temporal.cleanup()

    def datos_validos(self) -> dict[str, object]:
        """Construye el contrato minimo usado por las variantes."""
        return {
            "version_contrato": 1,
            "modulos": [
                {
                    "nombre": "backend",
                    "directorio": "backend",
                    "verificaciones": [
                        {
                            "identificador": "pruebas",
                            "tipo": "unitarias",
                            "comando": ["python", "-m", "unittest"],
                            "obligatoria": True,
                            "bloquea_cierre": True,
                            "timeout_segundos": 30,
                        }
                    ],
                }
            ],
            "documentos_obligatorios": ["PROJECT_STATE.md"],
            "criterios_bloqueo": ["FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"],
        }

    def guardar(self, datos: dict[str, object]) -> Path:
        """Publica una variante JSON dentro del temporal."""
        ruta = self.raiz / "contrato_validacion.json"
        ruta.write_text(json.dumps(datos), encoding="utf-8")
        return ruta

    def test_carga_contrato_tipado_valido(self) -> None:
        """Acepta directorio, tipo, comando y timeout conocidos."""
        contrato = cargar_contrato(self.guardar(self.datos_validos()), self.raiz)
        self.assertEqual(contrato["modulos"][0]["directorio"], "backend")

    def test_rechaza_directorio_inexistente(self) -> None:
        """Impide ejecutar una puerta desde una ubicacion inventada."""
        datos = self.datos_validos()
        datos["modulos"][0]["directorio"] = "ausente"
        with self.assertRaisesRegex(ValueError, "no existe"):
            cargar_contrato(self.guardar(datos), self.raiz)

    def test_rechaza_ejecutable_desconocido(self) -> None:
        """Impide convertir el manifiesto en una entrada de shell arbitraria."""
        datos = self.datos_validos()
        datos["modulos"][0]["verificaciones"][0]["comando"] = ["desconocido", "--todo"]
        with self.assertRaisesRegex(ValueError, "ejecutable desconocido"):
            cargar_contrato(self.guardar(datos), self.raiz)

    def test_rechaza_comando_duplicado(self) -> None:
        """Impide contar dos veces la misma evidencia."""
        datos = self.datos_validos()
        repetida = dict(datos["modulos"][0]["verificaciones"][0])
        repetida["identificador"] = "pruebas-repetidas"
        datos["modulos"][0]["verificaciones"].append(repetida)
        with self.assertRaisesRegex(ValueError, "Comando duplicado"):
            cargar_contrato(self.guardar(datos), self.raiz)

    def test_distingue_ejecutable_no_disponible(self) -> None:
        """Registra ausencia de herramienta sin presentarla como fallo aprobado."""
        comprobacion = Comprobacion(
            identificador="lint",
            tipo="lint",
            modulo="backend",
            directorio="backend",
            comando=["ruff", "check", "."],
            obligatoria=True,
            bloquea_cierre=True,
            timeout_segundos=30,
            origen="DECLARADO",
        )
        with patch("scripts.contrato_validacion.shutil.which", return_value=None):
            resultado = ejecutar_comprobacion(self.raiz, comprobacion)
        self.assertEqual(resultado["estado"], "NO_DISPONIBLE")
        self.assertIsNone(resultado["codigo_salida"])


if __name__ == "__main__":
    unittest.main()
