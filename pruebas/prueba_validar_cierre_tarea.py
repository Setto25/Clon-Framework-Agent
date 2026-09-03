#!/usr/bin/env python3
"""Comprueba la puerta distribuible de cierre para proyectos consumidores."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ_FRAMEWORK / "plantilla"
DOCUMENTOS_MINIMOS: tuple[str, ...] = (
    "PROJECT_STATE.md",
    "documentacion/PLAN_DESARROLLO.md",
    "documentacion/REGISTRO_CAMBIOS.md",
)


class PruebasValidarCierreTarea(unittest.TestCase):
    """Verifica que una tarea no cierre sin pruebas y evidencia declarada."""

    def setUp(self) -> None:
        """Prepara una copia aislada con memoria inicializada."""
        self.temporal = tempfile.TemporaryDirectory(prefix="cierre-tarea-")
        self.raiz = Path(self.temporal.name) / "proyecto"
        shutil.copytree(PLANTILLA, self.raiz)
        for ruta in (
            "AGENTS.md",
            "PROJECT_STATE.md",
            "documentacion/INDICE_LECTURA_AGENTES.md",
            "documentacion/PLAN_DESARROLLO.md",
            "documentacion/DOCUMENTACION_TECNICA.md",
            "documentacion/GUIA_OPERACION.md",
            "documentacion/REGISTRO_CAMBIOS.md",
        ):
            destino = self.raiz / ruta
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text("Contenido inicializado.\n", encoding="utf-8")
        (self.raiz / "modulo.py").write_text("valor = 1\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Elimina el proyecto temporal al terminar la comprobacion."""
        self.temporal.cleanup()

    def ejecutar(
        self, comando_prueba: str, documentos: Optional[list[str]] = None
    ) -> subprocess.CompletedProcess[str]:
        """Invoca la puerta con una tarea material minima y controlada."""
        argumentos = [
            sys.executable,
            str(self.raiz / "scripts" / "validar_cierre_tarea.py"),
            str(self.raiz),
            "--comando-prueba",
            comando_prueba,
            "--archivo-modificado",
            "modulo.py",
            "--guia-operacion-revisada",
            "--json",
        ]
        for documento in documentos if documentos is not None else list(DOCUMENTOS_MINIMOS):
            argumentos.extend(("--documento-actualizado", documento))
        return subprocess.run(
            argumentos,
            cwd=self.raiz,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_aprueba_prueba_y_evidencia_completas(self) -> None:
        """Aprueba solo despues de ejecutar una prueba y declarar los registros minimos."""
        resultado = self.ejecutar(f'{sys.executable} -c "print(\'OK\')"')
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertIsInstance(informe, dict)
        self.assertTrue(informe["valido"] if isinstance(informe, dict) else False)

    def test_rechaza_prueba_fallida(self) -> None:
        """Rechaza el cierre aunque los documentos esten declarados."""
        resultado = self.ejecutar(f'{sys.executable} -c "import sys; sys.exit(7)"')
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertTrue(any(error.startswith("Fallo la prueba") for error in informe["errores"]))

    def test_rechaza_registro_documental_incompleto(self) -> None:
        """Rechaza cuando falta una actualizacion documental minima declarada."""
        resultado = self.ejecutar(
            f'{sys.executable} -c "print(\'OK\')"',
            ["PROJECT_STATE.md", "documentacion/REGISTRO_CAMBIOS.md"],
        )
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertIn("documentacion/PLAN_DESARROLLO.md", informe["errores"][0])


if __name__ == "__main__":
    unittest.main()
