#!/usr/bin/env python3
"""Comprueba la actualizacion conservadora de proyectos generados."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.estado_proyecto import cargar_rutas_gestionadas


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
CREADOR = RAIZ_FRAMEWORK / "scripts" / "crear_proyecto.py"
AGREGADOR_SKILLS = RAIZ_FRAMEWORK / "scripts" / "agregar_skills.py"
ACTUALIZADOR = RAIZ_FRAMEWORK / "scripts" / "actualizar_proyecto.py"
CONFIGURACION = RAIZ_FRAMEWORK / "ejemplos" / "configuracion_proyecto.ejemplo.json"


def ejecutar(argumentos: list[str]) -> subprocess.CompletedProcess[str]:
    """Ejecuta una CLI del framework con salida UTF-8."""
    entorno = dict(os.environ)
    entorno["PYTHONUTF8"] = "1"
    return subprocess.run(
        argumentos,
        cwd=RAIZ_FRAMEWORK,
        env=entorno,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class PruebasActualizacionProyecto(unittest.TestCase):
    """Verifica reemplazos seguros, conflictos y ausencia de escrituras parciales."""

    temporal: tempfile.TemporaryDirectory[str]
    proyecto: Path

    def setUp(self) -> None:
        """Crea una instancia completa con huellas administradas."""
        self.temporal = tempfile.TemporaryDirectory(prefix="actualizacion-proyecto-")
        self.proyecto = Path(self.temporal.name) / "proyecto"
        resultado = ejecutar(
            [
                sys.executable,
                str(CREADOR),
                str(self.proyecto),
                "Proyecto Actualizable",
                "--configuracion",
                str(CONFIGURACION),
            ]
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)

    def tearDown(self) -> None:
        """Elimina la instancia temporal de la prueba."""
        self.temporal.cleanup()

    def cargar_estado(self) -> dict[str, object]:
        """Carga el estado generado como objeto mutable."""
        datos: object = json.loads(
            (self.proyecto / ".estado-plantilla.json").read_text(encoding="utf-8")
        )
        self.assertIsInstance(datos, dict)
        return datos if isinstance(datos, dict) else {}

    def guardar_estado(self, estado: dict[str, object]) -> None:
        """Guarda una variante controlada del estado de prueba."""
        (self.proyecto / ".estado-plantilla.json").write_text(
            json.dumps(estado, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_actualiza_archivo_no_modificado_desde_su_huella(self) -> None:
        """Reemplaza una version anterior cuando coincide con la base registrada."""
        relativa = ".agents/skills/optimizar-contexto/SKILL.md"
        archivo = self.proyecto / Path(relativa)
        contenido_anterior = b"---\nname: optimizar-contexto\ndescription: Version anterior.\n---\n"
        archivo.write_bytes(contenido_anterior)
        estado = self.cargar_estado()
        huellas = estado.get("huellas_gestionadas")
        self.assertIsInstance(huellas, dict)
        if isinstance(huellas, dict):
            huellas[relativa] = hashlib.sha256(contenido_anterior).hexdigest()
        estado["version_framework"] = "0.2.0-alpha.10"
        self.guardar_estado(estado)

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        fuente = (
            RAIZ_FRAMEWORK
            / "plantilla"
            / ".agents"
            / "skills"
            / "optimizar-contexto"
            / "SKILL.md"
        )
        self.assertEqual(archivo.read_bytes(), fuente.read_bytes())
        actualizado = self.cargar_estado()
        self.assertEqual(actualizado.get("version_framework"), "0.2.0-alpha.18")

    def test_bloquea_cambio_local_sin_mutar_estado(self) -> None:
        """Detiene toda la actualizacion cuando un archivo administrado diverge."""
        archivo = self.proyecto / ".agents" / "skills" / "optimizar-contexto" / "SKILL.md"
        archivo.write_text("cambio local", encoding="utf-8")
        estado_antes = (self.proyecto / ".estado-plantilla.json").read_bytes()
        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn("cambios locales", resultado.stdout)
        self.assertEqual((self.proyecto / ".estado-plantilla.json").read_bytes(), estado_antes)
        self.assertEqual(archivo.read_text(encoding="utf-8"), "cambio local")

    def test_bloquea_referencia_mcp_modificada_localmente(self) -> None:
        """Protege una referencia instalada antes de actualizar el framework."""
        agregado = ejecutar(
            [
                sys.executable,
                str(AGREGADOR_SKILLS),
                str(self.proyecto),
                "--skill",
                "desarrollar-servidores-mcp",
            ]
        )
        self.assertEqual(agregado.returncode, 0, agregado.stdout + agregado.stderr)
        archivo = (
            self.proyecto
            / ".agents"
            / "skills"
            / "stacks"
            / "ia-llm"
            / "skills"
            / "desarrollar-servidores-mcp"
            / "referencias"
            / "arquitectura_servidor.md"
        )
        archivo.write_text("cambio local", encoding="utf-8")
        estado_antes = (self.proyecto / ".estado-plantilla.json").read_bytes()

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])

        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn("cambios locales", resultado.stdout)
        self.assertEqual((self.proyecto / ".estado-plantilla.json").read_bytes(), estado_antes)
        self.assertEqual(archivo.read_text(encoding="utf-8"), "cambio local")

    def test_agrega_script_nuevo_y_registra_su_huella(self) -> None:
        """Incorpora una dependencia nueva declarada por el contrato."""
        relativa = "scripts/generar_indice_contexto.py"
        archivo = self.proyecto / Path(relativa)
        archivo.unlink()
        estado = self.cargar_estado()
        huellas = estado.get("huellas_gestionadas")
        self.assertIsInstance(huellas, dict)
        if isinstance(huellas, dict):
            huellas.pop(relativa, None)
        estado["version_framework"] = "0.2.0-alpha.10"
        self.guardar_estado(estado)

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertTrue(archivo.is_file())
        actualizado = self.cargar_estado()
        huellas_actualizadas = actualizado.get("huellas_gestionadas")
        self.assertIsInstance(huellas_actualizadas, dict)
        if isinstance(huellas_actualizadas, dict):
            self.assertIn(relativa, huellas_actualizadas)

    def test_agrega_puerta_ci_y_script_sin_sobrescribir_el_proyecto(self) -> None:
        """Actualiza una instancia anterior con la puerta estatica administrada."""
        rutas = (
            "scripts/validar_integridad_proyecto.py",
            ".github/workflows/validacion-proyecto.yml",
        )
        estado = self.cargar_estado()
        huellas = estado.get("huellas_gestionadas")
        self.assertIsInstance(huellas, dict)
        for relativa in rutas:
            (self.proyecto / Path(relativa)).unlink()
            if isinstance(huellas, dict):
                huellas.pop(relativa, None)
        estado["version_framework"] = "0.2.0-alpha.17"
        self.guardar_estado(estado)

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        huellas_actualizadas = self.cargar_estado().get("huellas_gestionadas")
        self.assertIsInstance(huellas_actualizadas, dict)
        for relativa in rutas:
            self.assertTrue((self.proyecto / Path(relativa)).is_file())
            if isinstance(huellas_actualizadas, dict):
                self.assertIn(relativa, huellas_actualizadas)

    def test_agrega_puente_claude_ausente_y_sus_adaptadores(self) -> None:
        """Migra una instancia anterior hacia el descubrimiento nativo de Claude."""
        relativa = "CLAUDE.md"
        (self.proyecto / relativa).unlink()
        for adaptador in (self.proyecto / ".claude" / "skills").glob("*/SKILL.md"):
            adaptador.unlink()
            adaptador.parent.rmdir()
        raiz_adaptadores = self.proyecto / ".claude" / "skills"
        raiz_adaptadores.rmdir()
        (self.proyecto / ".claude").rmdir()
        estado = self.cargar_estado()
        huellas = estado.get("huellas_gestionadas")
        self.assertIsInstance(huellas, dict)
        if isinstance(huellas, dict):
            huellas.pop(relativa, None)
            for ruta in list(huellas):
                if ruta.startswith(".claude/skills/"):
                    huellas.pop(ruta)
        estado["version_framework"] = "0.2.0-alpha.13"
        self.guardar_estado(estado)

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertTrue((self.proyecto / relativa).is_file())
        adaptadores = list((self.proyecto / ".claude" / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(adaptadores), 4)
        huellas_actualizadas = self.cargar_estado().get("huellas_gestionadas")
        self.assertIsInstance(huellas_actualizadas, dict)
        if isinstance(huellas_actualizadas, dict):
            self.assertIn(relativa, huellas_actualizadas)
            self.assertIn(
                ".claude/skills/optimizar-contexto/SKILL.md",
                huellas_actualizadas,
            )

    def test_agrega_referencia_nueva_de_skill_y_registra_su_huella(self) -> None:
        """Incorpora archivos progresivos sin sobrescribir contenido local."""
        relativa = ".agents/skills/optimizar-contexto/referencias/modo_extendido.md"
        archivo = self.proyecto / Path(relativa)
        archivo.unlink()
        estado = self.cargar_estado()
        huellas = estado.get("huellas_gestionadas")
        self.assertIsInstance(huellas, dict)
        if isinstance(huellas, dict):
            huellas.pop(relativa, None)
        self.guardar_estado(estado)

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertTrue(archivo.is_file())
        huellas_actualizadas = self.cargar_estado().get("huellas_gestionadas")
        self.assertIsInstance(huellas_actualizadas, dict)
        if isinstance(huellas_actualizadas, dict):
            self.assertIn(relativa, huellas_actualizadas)

    def test_bloquea_script_preexistente_sin_huella(self) -> None:
        """Protege un archivo local que coincide con una nueva ruta administrada."""
        relativa = "scripts/generar_indice_contexto.py"
        archivo = self.proyecto / Path(relativa)
        archivo.write_text("contenido local", encoding="utf-8")
        estado = self.cargar_estado()
        huellas = estado.get("huellas_gestionadas")
        self.assertIsInstance(huellas, dict)
        if isinstance(huellas, dict):
            huellas.pop(relativa, None)
        self.guardar_estado(estado)

        resultado = ejecutar([sys.executable, str(ACTUALIZADOR), str(self.proyecto)])
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn("existe sin huella administrada", resultado.stdout)
        self.assertEqual(archivo.read_text(encoding="utf-8"), "contenido local")

    def test_contrato_v2_conserva_rutas_historicas_para_adopcion(self) -> None:
        """Permite migrar una instancia anterior a la fuente unica del contrato v3."""
        contrato = self.proyecto / "configuracion_plantilla.json"
        datos: object = json.loads(contrato.read_text(encoding="utf-8"))
        self.assertIsInstance(datos, dict)
        if not isinstance(datos, dict):
            raise AssertionError("El contrato de prueba no es un objeto")
        datos["version_contrato"] = 2
        datos.pop("archivos_gestionados", None)
        contrato.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        rutas = cargar_rutas_gestionadas(self.proyecto)
        self.assertEqual(
            rutas,
            [
                "configuracion_plantilla.json",
                "scripts/inicializar_proyecto.py",
                "scripts/inicializar_proyecto.sh",
                "scripts/verificar_memoria_proyecto.py",
            ],
        )


if __name__ == "__main__":
    unittest.main()
