#!/usr/bin/env python3
"""Reproduce el cierre falso observado en un consumidor Next.js."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.diagnosticar_tarea import descubrir_comprobaciones, diagnosticar
from scripts.validar_integridad_proyecto import validar_integridad


DOCUMENTOS: tuple[str, ...] = (
    "AGENTS.md", "PROJECT_STATE.md", "documentacion/INDICE_LECTURA_AGENTES.md",
    "documentacion/PLAN_DESARROLLO.md", "documentacion/DOCUMENTACION_TECNICA.md",
    "documentacion/GUIA_OPERACION.md", "documentacion/REGISTRO_CAMBIOS.md",
)


class PruebasIntegridadProyecto(unittest.TestCase):
    """Comprueba que las puertas no desaparezcan junto con el script npm."""

    def setUp(self) -> None:
        """Prepara un proyecto Next.js minimo sin ejecutar Node."""
        self.temporal = tempfile.TemporaryDirectory(prefix="integridad-proyecto-")
        self.raiz = Path(self.temporal.name)
        for relativa in DOCUMENTOS:
            ruta = self.raiz / relativa
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text("Contenido vigente.\n", encoding="utf-8")
        self.escribir_paquete({"build": "next build", "lint": "eslint ."})

    def tearDown(self) -> None:
        """Retira los archivos temporales al terminar."""
        self.temporal.cleanup()

    def escribir_paquete(self, scripts: dict[str, str], gestor: str = "pnpm@11.5.3") -> None:
        """Declara scripts y gestor sin instalar dependencias."""
        datos = {
            "packageManager": gestor,
            "dependencies": {"next": "16.3.5"},
            "scripts": scripts,
        }
        (self.raiz / "package.json").write_text(
            json.dumps(datos, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def test_bloquea_lint_eliminado_tras_un_fallo(self) -> None:
        """Rechaza la maniobra que hizo aprobar solo build en Web Scroll."""
        self.escribir_paquete({"build": "next build"})
        errores = validar_integridad(self.raiz)
        self.assertTrue(any("lint" in error for error in errores))

        with patch("scripts.diagnosticar_tarea.ejecutar_comprobacion") as ejecutar:
            ejecutar.return_value = {
                "identificador": "raiz:build", "tipo": "build", "modulo": "raiz",
                "directorio": ".", "comando": ["pnpm", "run", "build"],
                "obligatoria": True, "bloquea_cierre": True,
                "timeout_segundos": 300, "origen": "INFERIDO",
                "comando_texto": "pnpm run build", "estado": "APROBADO",
                "codigo_salida": 0, "duracion_segundos": 0.0, "evidencia": "",
            }
            resultado = diagnosticar(self.raiz)
        estados = {item["identificador"]: item["estado"] for item in resultado["verificaciones"]}
        self.assertEqual(estados["raiz:lint-ausente"], "NO_EJECUTADO")
        self.assertTrue(resultado["bloquea_cierre"])

    def test_utiliza_pnpm_declarado_en_lugar_de_npm(self) -> None:
        """Ejecuta los scripts inferidos con el gestor del proyecto."""
        (self.raiz / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        comprobaciones, _ = descubrir_comprobaciones(self.raiz)
        comandos = [item["comando"] for item in comprobaciones]
        self.assertIn(["pnpm", "run", "lint"], comandos)
        self.assertIn(["pnpm", "run", "build"], comandos)

    def test_rechaza_lockfiles_duplicados(self) -> None:
        """Bloquea un gestor ambiguo aunque existan scripts de calidad."""
        (self.raiz / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        (self.raiz / "package-lock.json").write_text("{}\n", encoding="utf-8")
        self.assertTrue(any("lockfiles" in error for error in validar_integridad(self.raiz)))

    def test_ignora_worktree_interno_de_otro_agente(self) -> None:
        """Evita tratar una copia de Kilo como modulo del proyecto principal."""
        otro = self.raiz / ".kilo" / "worktrees" / "copia"
        otro.mkdir(parents=True)
        (otro / "package.json").write_text(
            json.dumps({"dependencies": {"next": "16.3.5"}, "scripts": {"build": "next build"}}),
            encoding="utf-8",
        )
        (otro / "package-lock.json").write_text("{}\n", encoding="utf-8")
        (otro / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        self.assertEqual(validar_integridad(self.raiz), [])

    def test_exige_documentacion_en_cambio_de_codigo(self) -> None:
        """Detecta una entrega de codigo sin estado, plan y registro."""
        with patch("scripts.validar_integridad_proyecto.rutas_cambiadas", return_value={"src/app/page.jsx"}):
            errores = validar_integridad(self.raiz, "base")
        self.assertTrue(any("PROJECT_STATE.md" in error for error in errores))
        self.assertTrue(any("REGISTRO_CAMBIOS.md" in error for error in errores))

    def test_rechaza_contrato_que_omite_lint(self) -> None:
        """Impide que el manifiesto omita la puerta propia de Next.js."""
        contrato = {
            "version_contrato": 1,
            "modulos": [{"nombre": "frontend", "directorio": ".", "verificaciones": [
                {"identificador": "build", "tipo": "build", "comando": ["pnpm", "run", "build"],
                 "obligatoria": True, "bloquea_cierre": True, "timeout_segundos": 300}
            ]}],
            "documentos_obligatorios": list(DOCUMENTOS),
            "criterios_bloqueo": ["FALLIDO", "NO_EJECUTADO", "NO_DISPONIBLE"],
        }
        (self.raiz / "contrato_validacion.json").write_text(
            json.dumps(contrato, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.assertTrue(any("lint" in error for error in validar_integridad(self.raiz)))

        contrato["modulos"][0]["verificaciones"].append(
            {"identificador": "lint", "tipo": "lint", "comando": ["pnpm", "run", "lint"],
             "obligatoria": True, "bloquea_cierre": True, "timeout_segundos": 300}
        )
        (self.raiz / "contrato_validacion.json").write_text(
            json.dumps(contrato, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.escribir_paquete({"build": "next build"})
        self.assertTrue(any("script lint" in error for error in validar_integridad(self.raiz)))


if __name__ == "__main__":
    unittest.main()
