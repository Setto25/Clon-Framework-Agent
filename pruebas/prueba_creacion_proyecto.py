#!/usr/bin/env python3
"""Comprueba el flujo publico de creacion sin modificar la plantilla fuente."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
CREADOR = RAIZ_FRAMEWORK / "scripts" / "crear_proyecto.py"
CONFIGURACION_EJEMPLO = RAIZ_FRAMEWORK / "ejemplos" / "configuracion_proyecto.ejemplo.json"
SKILLS_ORIGEN = RAIZ_FRAMEWORK / "plantilla" / ".agents" / "skills"


def ejecutar(argumentos: list[str], raiz: Path = RAIZ_FRAMEWORK) -> subprocess.CompletedProcess[str]:
    """Ejecuta un proceso con salida UTF-8 capturada."""
    entorno = dict(os.environ)
    entorno["PYTHONUTF8"] = "1"
    return subprocess.run(
        argumentos,
        cwd=raiz,
        env=entorno,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def calcular_huellas(raiz: Path) -> dict[str, str]:
    """Calcula las huellas SHA-256 de todos los archivos de una ruta."""
    return {
        archivo.relative_to(raiz).as_posix(): hashlib.sha256(archivo.read_bytes()).hexdigest()
        for archivo in sorted(raiz.rglob("*"))
        if archivo.is_file()
    }


class PruebasCreacionProyecto(unittest.TestCase):
    """Verifica los casos criticos del creador de proyectos."""

    temporal: tempfile.TemporaryDirectory[str]
    raiz_temporal: Path

    def setUp(self) -> None:
        """Crea un directorio aislado para cada prueba."""
        self.temporal = tempfile.TemporaryDirectory(prefix="agent-framework-pruebas-")
        self.raiz_temporal = Path(self.temporal.name)

    def tearDown(self) -> None:
        """Elimina la instancia aislada al terminar cada prueba."""
        self.temporal.cleanup()

    def crear_completo(self, nombre_directorio: str = "proyecto-completo") -> Path:
        """Crea una instancia completa mediante la configuracion publicada."""
        destino = self.raiz_temporal / nombre_directorio
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto de Prueba",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        return destino

    def test_crea_proyecto_completo_y_protege_entorno(self) -> None:
        """Confirma una instancia valida con Git, memoria y entorno protegido."""
        destino = self.crear_completo()
        verificador = destino / "scripts" / "verificar_memoria_proyecto.py"
        resultado_memoria = ejecutar([sys.executable, str(verificador), str(destino), "--json"], destino)
        self.assertEqual(resultado_memoria.returncode, 0, resultado_memoria.stdout + resultado_memoria.stderr)
        informe: object = json.loads(resultado_memoria.stdout)
        self.assertIsInstance(informe, dict)
        self.assertTrue(informe["valido"] if isinstance(informe, dict) else False)
        self.assertTrue((destino / ".git").is_dir())
        self.assertTrue((destino / ".env").is_file())
        resultado_ignorado = ejecutar(["git", "check-ignore", ".env"], destino)
        self.assertEqual(resultado_ignorado.returncode, 0, resultado_ignorado.stdout + resultado_ignorado.stderr)
        self.assertEqual(
            calcular_huellas(SKILLS_ORIGEN),
            calcular_huellas(destino / ".agents" / "skills"),
        )

    def test_rechaza_memoria_con_pendientes(self) -> None:
        """Confirma que una instancia provisional no se certifique como completa."""
        destino = self.raiz_temporal / "proyecto-pendiente"
        resultado_creacion = ejecutar(
            [sys.executable, str(CREADOR), str(destino), "Proyecto Pendiente", "--permitir-pendientes"]
        )
        self.assertEqual(resultado_creacion.returncode, 0, resultado_creacion.stdout + resultado_creacion.stderr)
        verificador = destino / "scripts" / "verificar_memoria_proyecto.py"
        resultado_memoria = ejecutar([sys.executable, str(verificador), str(destino), "--json"], destino)
        self.assertNotEqual(resultado_memoria.returncode, 0)
        informe: object = json.loads(resultado_memoria.stdout)
        self.assertIsInstance(informe, dict)
        pendientes = informe.get("pendientes_inicializacion") if isinstance(informe, dict) else None
        self.assertIsInstance(pendientes, dict)
        self.assertEqual(
            set(pendientes) if isinstance(pendientes, dict) else set(),
            {
                "DESCRIPCION_OBJETIVO",
                "LISTA_EXCLUIDOS",
                "LISTA_OBLIGATORIOS",
                "REGLAS_ARQUITECTURA",
                "SIGUIENTE_PASO",
                "ZONA_HORARIA",
            },
        )

    def test_limpia_temporal_cuando_falla_la_configuracion(self) -> None:
        """Confirma que un fallo no publique ni abandone una copia parcial."""
        destino = self.raiz_temporal / "proyecto-fallido"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Fallido",
                "--valor",
                "CLAVE_INEXISTENTE=valor",
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertFalse(destino.exists())
        temporales_huerfanos = list(self.raiz_temporal.glob(".proyecto-temporal-*"))
        self.assertEqual(temporales_huerfanos, [])

    def test_rechaza_sobrescribir_un_destino_existente(self) -> None:
        """Confirma que una segunda creacion no altere el proyecto existente."""
        destino = self.crear_completo()
        estado_antes = (destino / ".estado-plantilla.json").read_bytes()
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(destino),
                "Proyecto Repetido",
                "--configuracion",
                str(CONFIGURACION_EJEMPLO),
            ]
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual((destino / ".estado-plantilla.json").read_bytes(), estado_antes)


if __name__ == "__main__":
    unittest.main()
