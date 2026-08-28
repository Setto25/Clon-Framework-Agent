#!/usr/bin/env python3
"""Comprueba que el inventario congelado coincida con las Skills presentes."""

from __future__ import annotations

import io
import importlib.util
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
INVENTARIADOR = RAIZ_FRAMEWORK / "scripts" / "inventariar_skills.py"
INVENTARIO_REGISTRADO = RAIZ_FRAMEWORK / "auditoria" / "inventario_skills.json"


def cargar_inventariador() -> object:
    """Carga el modulo para probar el orden independiente de la plataforma."""
    especificacion = importlib.util.spec_from_file_location("inventariador_pruebas", INVENTARIADOR)
    if especificacion is None or especificacion.loader is None:
        raise RuntimeError("No se pudo cargar scripts/inventariar_skills.py")
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


class PruebasInventarioSkills(unittest.TestCase):
    """Verifica la reproducibilidad del inventario de solo lectura."""

    def ejecutar_inventariador(self, raiz_skills: Path | None = None) -> subprocess.CompletedProcess[str]:
        """Ejecuta el inventariador sobre la raiz indicada o sobre la fuente local."""
        entorno = dict(os.environ)
        entorno["PYTHONUTF8"] = "1"
        argumentos = [sys.executable, str(INVENTARIADOR)]
        if raiz_skills is not None:
            argumentos.extend(["--raiz", str(raiz_skills)])
        return subprocess.run(
            argumentos,
            cwd=RAIZ_FRAMEWORK,
            env=entorno,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def extraer_skills_versionadas(self, destino: Path) -> None:
        """Extrae las Skills registradas en Git sin depender de la copia de trabajo."""
        resultado = subprocess.run(
            ["git", "archive", "--format=tar", "HEAD:plantilla/.agents/skills"],
            cwd=RAIZ_FRAMEWORK,
            check=False,
            capture_output=True,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout.decode("utf-8", errors="replace"))
        with tarfile.open(fileobj=io.BytesIO(resultado.stdout), mode="r:") as archivo_tar:
            for miembro in archivo_tar.getmembers():
                ruta_destino = (destino / miembro.name).resolve()
                self.assertTrue(
                    ruta_destino.is_relative_to(destino.resolve()),
                    f"Git archive contiene una ruta fuera del temporal: {miembro.name}",
                )
                if miembro.isdir():
                    ruta_destino.mkdir(parents=True, exist_ok=True)
                    continue
                self.assertTrue(miembro.isfile(), f"Git archive contiene un tipo no admitido: {miembro.name}")
                contenido = archivo_tar.extractfile(miembro)
                self.assertIsNotNone(contenido, f"Git archive no entrego contenido: {miembro.name}")
                ruta_destino.parent.mkdir(parents=True, exist_ok=True)
                ruta_destino.write_bytes(contenido.read() if contenido is not None else b"")

    def test_inventario_registrado_esta_actualizado(self) -> None:
        """Confirma que el contenido versionado coincida byte por byte con el registro."""
        with tempfile.TemporaryDirectory(prefix="inventario-versionado-") as temporal:
            raiz_temporal = Path(temporal)
            self.extraer_skills_versionadas(raiz_temporal)
            resultado = self.ejecutar_inventariador(raiz_temporal)
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

    def test_ordenamiento_usa_rutas_posix(self) -> None:
        """Ordena rutas con mayusculas de forma identica en cualquier plataforma."""
        modulo = cargar_inventariador()
        with tempfile.TemporaryDirectory(prefix="inventario-orden-") as temporal:
            raiz = Path(temporal)
            rutas = modulo.ordenar_rutas(
                raiz,
                [raiz / "zeta/archivo.md", raiz / "Alfa/archivo.md", raiz / "alfa/archivo.md"],
            )
        self.assertEqual([ruta for ruta, _ in rutas], ["Alfa/archivo.md", "alfa/archivo.md", "zeta/archivo.md"])


if __name__ == "__main__":
    unittest.main()
