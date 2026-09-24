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
        (self.raiz / "pruebas").mkdir()
        (self.raiz / "pruebas" / "prueba_modulo.py").write_text(
            "import unittest\n\n"
            "class PruebaModulo(unittest.TestCase):\n"
            "    def test_valor(self):\n"
            "        self.assertEqual(1, 1)\n",
            encoding="utf-8",
        )
        contrato = {
            "version_contrato": 1,
            "modulos": [
                {
                    "nombre": "raiz",
                    "directorio": ".",
                    "verificaciones": [
                        {
                            "identificador": "pruebas-proyecto",
                            "tipo": "unitarias",
                            "comando": ["python", "-m", "unittest", "discover", "-s", "pruebas", "-p", "prueba_*.py"],
                            "obligatoria": True,
                            "bloquea_cierre": True,
                            "timeout_segundos": 60,
                        }
                    ],
                }
            ],
            "documentos_obligatorios": list(DOCUMENTOS_MINIMOS),
            "criterios_bloqueo": ["FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"],
        }
        (self.raiz / "contrato_validacion.json").write_text(
            json.dumps(contrato, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

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

    def test_prevalidacion_habilita_documentacion_solo_si_aprueba(self) -> None:
        """Ejecuta las puertas antes de permitir cambios documentales de cierre."""
        resultado = subprocess.run(
            [
                sys.executable,
                str(self.raiz / "scripts" / "validar_cierre_tarea.py"),
                str(self.raiz),
                "--solo-verificaciones",
                "--json",
            ],
            cwd=self.raiz,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertTrue(informe["documentacion_habilitada"] if isinstance(informe, dict) else False)

    def test_prevalidacion_rechaza_next_sin_lint_aunque_otra_prueba_apruebe(self) -> None:
        """Conserva el bloqueo cuando un agente elimina lint del paquete."""
        (self.raiz / "package.json").write_text(
            json.dumps({"dependencies": {"next": "16.3.5"}, "scripts": {"build": "next build"}}),
            encoding="utf-8",
        )
        resultado = subprocess.run(
            [sys.executable, str(self.raiz / "scripts" / "validar_cierre_tarea.py"),
             str(self.raiz), "--solo-verificaciones", "--json"],
            cwd=self.raiz, check=False, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertTrue(any("lint-ausente" in error for error in informe["errores"]))

    def test_rechaza_operadores_de_shell(self) -> None:
        """Impide ocultar una prueba fallida detras de una cadena compuesta."""
        resultado = self.ejecutar(f'{sys.executable} -c "print(1)" && echo falso')
        self.assertEqual(resultado.returncode, 1, resultado.stdout + resultado.stderr)
        self.assertIn("operadores de shell", resultado.stderr)

    def test_fixture_vertical_bloquea_cierre_y_no_modifica_documentacion(self) -> None:
        """Conserva documentos abiertos cuando los nueve contratos fallan."""
        fixture = RAIZ_FRAMEWORK / "pruebas" / "fixtures" / "contratos-verticales"
        estado = (fixture / "PROJECT_STATE.md").read_bytes()
        resultado = subprocess.run(
            [
                sys.executable,
                str(self.raiz / "scripts" / "validar_cierre_tarea.py"),
                str(fixture),
                "--solo-verificaciones",
                "--json",
            ],
            cwd=self.raiz,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        informe: object = json.loads(resultado.stdout)
        self.assertFalse(informe["documentacion_habilitada"] if isinstance(informe, dict) else True)
        self.assertEqual((fixture / "PROJECT_STATE.md").read_bytes(), estado)


if __name__ == "__main__":
    unittest.main()
