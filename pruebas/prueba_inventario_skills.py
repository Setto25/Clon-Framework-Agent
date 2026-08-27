#!/usr/bin/env python3
"""Comprueba que el inventario congelado coincida con las Skills presentes."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
INVENTARIADOR = RAIZ_FRAMEWORK / "scripts" / "inventariar_skills.py"
INVENTARIO_REGISTRADO = RAIZ_FRAMEWORK / "auditoria" / "inventario_skills.json"


class PruebasInventarioSkills(unittest.TestCase):
    """Verifica la reproducibilidad del inventario de solo lectura."""

    def test_inventario_registrado_esta_actualizado(self) -> None:
        """Confirma que la salida calculada coincida byte por byte con el registro."""
        entorno = dict(os.environ)
        entorno["PYTHONUTF8"] = "1"
        resultado = subprocess.run(
            [sys.executable, str(INVENTARIADOR)],
            cwd=RAIZ_FRAMEWORK,
            env=entorno,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertEqual(resultado.stdout, INVENTARIO_REGISTRADO.read_text(encoding="utf-8"))

    def test_huella_no_depende_de_lf_o_crlf(self) -> None:
        """Confirma que Git no cambie el inventario entre sistemas operativos."""
        contenido_lf = b"---\nname: ejemplo\ndescription: Prueba reproducible.\n---\n\n# Ejemplo\n"
        contenido_crlf = contenido_lf.replace(b"\n", b"\r\n")
        salidas: list[str] = []
        with tempfile.TemporaryDirectory(prefix="inventario-lineas-") as temporal:
            raiz_temporal = Path(temporal)
            for nombre, contenido in (("lf", contenido_lf), ("crlf", contenido_crlf)):
                raiz = raiz_temporal / nombre / "ejemplo"
                raiz.mkdir(parents=True)
                (raiz / "SKILL.md").write_bytes(contenido)
                resultado = subprocess.run(
                    [sys.executable, str(INVENTARIADOR), "--raiz", str(raiz.parent)],
                    cwd=RAIZ_FRAMEWORK,
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
                self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
                salidas.append(resultado.stdout)
        self.assertEqual(salidas[0], salidas[1])


if __name__ == "__main__":
    unittest.main()
