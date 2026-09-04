#!/usr/bin/env python3
"""Comprueba que el piloto MCP conserve sus fronteras y dependencias fijadas."""

from __future__ import annotations

import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
RAIZ_FIXTURE = RAIZ_FRAMEWORK / "pruebas" / "fixtures" / "servidor-mcp"


class PruebasFixtureServidorMcp(unittest.TestCase):
    """Verifica estructura portable sin cargar dependencias MCP en la suite base."""

    def test_conserva_componentes_y_version_bloqueada(self) -> None:
        """Exige codigo, pruebas, contenedor y lock reproducible."""
        rutas = {
            "pyproject.toml",
            "uv.lock",
            "Dockerfile",
            ".env.ejemplo",
            "codigo_servidor/dominio.py",
            "codigo_servidor/adaptador_mcp.py",
            "codigo_servidor/aplicacion_http.py",
            "codigo_servidor/entrada_http.py",
            "codigo_servidor/autenticacion.py",
            "pruebas/prueba_dominio.py",
            "pruebas/prueba_mcp.py",
            "pruebas/prueba_seguridad.py",
            "pruebas/probar_http_local.py",
        }
        for relativa in rutas:
            with self.subTest(ruta=relativa):
                self.assertTrue((RAIZ_FIXTURE / Path(relativa)).is_file())
        proyecto = (RAIZ_FIXTURE / "pyproject.toml").read_text(encoding="utf-8")
        bloqueo = (RAIZ_FIXTURE / "uv.lock").read_text(encoding="utf-8")
        self.assertIn('"mcp==2.1.1"', proyecto)
        self.assertIn('name = "mcp"', bloqueo)
        self.assertIn('version = "2.1.1"', bloqueo)

    def test_separa_dominio_transporte_y_perfiles_reemplazables(self) -> None:
        """Impide introducir MCP, HTTP o proveedor cloud dentro del dominio."""
        dominio = (RAIZ_FIXTURE / "codigo_servidor" / "dominio.py").read_text(encoding="utf-8")
        aplicacion = (
            RAIZ_FIXTURE / "codigo_servidor" / "aplicacion_http.py"
        ).read_text(encoding="utf-8")
        autenticacion = (
            RAIZ_FIXTURE / "codigo_servidor" / "autenticacion.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("from mcp", dominio)
        self.assertNotIn("starlette", dominio)
        self.assertNotIn("Cloud Run", dominio)
        self.assertIn("TransportSecuritySettings", aplicacion)
        self.assertIn("stateless_http=True", aplicacion)
        self.assertIn("TokenVerifier", autenticacion)
        self.assertNotIn("Cloud Run", aplicacion)


if __name__ == "__main__":
    unittest.main()
