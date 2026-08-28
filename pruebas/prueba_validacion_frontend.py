#!/usr/bin/env python3
"""Comprueba la validacion reproducible para un frontend Next.js anidado."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
VALIDADOR = RAIZ_FRAMEWORK / "scripts" / "validar_frontend_nextjs.py"


class PruebasValidacionFrontend(unittest.TestCase):
    """Verifica los requisitos estructurales sin instalar dependencias externas."""

    def ejecutar(self, proyecto: Path) -> subprocess.CompletedProcess[str]:
        """Ejecuta el validador en modo estructural y captura su salida."""
        return subprocess.run(
            [sys.executable, str(VALIDADOR), str(proyecto), "--solo-verificar"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_acepta_interfaz_con_los_tres_scripts_obligatorios(self) -> None:
        """Acepta una estructura frontend completa antes de invocar npm."""
        with tempfile.TemporaryDirectory(prefix="frontend-nextjs-prueba-") as temporal:
            proyecto = Path(temporal)
            interfaz = proyecto / "interfaz"
            interfaz.mkdir()
            (interfaz / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest run", "lint": "next lint", "build": "next build"}}),
                encoding="utf-8",
            )
            resultado = self.ejecutar(proyecto)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertIn("Frontend Next.js preparado", resultado.stdout)

    def test_rechaza_scripts_obligatorios_ausentes(self) -> None:
        """Rechaza un frontend que no declara su build reproducible."""
        with tempfile.TemporaryDirectory(prefix="frontend-nextjs-prueba-") as temporal:
            proyecto = Path(temporal)
            interfaz = proyecto / "interfaz"
            interfaz.mkdir()
            (interfaz / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest run", "lint": "next lint"}}),
                encoding="utf-8",
            )
            resultado = self.ejecutar(proyecto)
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("build", resultado.stderr)
