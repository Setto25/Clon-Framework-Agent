"""Comprueba autenticacion y configuracion sin abrir puertos."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from codigo_servidor.autenticacion import VerificadorBearerPersonal
from codigo_servidor.configuracion import ConfiguracionServidor


class PruebasSeguridad(unittest.IsolatedAsyncioTestCase):
    """Verifica credenciales y fallos seguros de configuracion."""

    async def test_verificador_acepta_solo_el_token_configurado(self) -> None:
        """Rechaza secretos distintos sin crear una identidad."""
        verificador = VerificadorBearerPersonal("token-valido-123456789012345678901")
        self.assertIsNone(await verificador.verify_token("token-invalido"))
        acceso = await verificador.verify_token("token-valido-123456789012345678901")
        self.assertIsNotNone(acceso)
        if acceso is None:
            raise AssertionError("El verificador rechazo el token configurado")
        self.assertEqual(acceso.subject, "propietario-piloto")
        self.assertEqual(set(acceso.scopes), {"contadores:leer", "contadores:escribir"})

    async def test_configuracion_rechaza_secreto_ausente(self) -> None:
        """Impide arrancar con la credencial vacia."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                ConfiguracionServidor.desde_entorno()

    async def test_configuracion_normaliza_hosts_explicitos(self) -> None:
        """Carga una lista acotada sin habilitar comodines implicitos."""
        entorno = {
            "MCP_TOKEN_BEARER": "token-valido-123456789012345678901",
            "MCP_HOSTS_PERMITIDOS": "mcp.ejemplo.test,mcp.ejemplo.test:*",
        }
        with mock.patch.dict(os.environ, entorno, clear=True):
            configuracion = ConfiguracionServidor.desde_entorno()
        self.assertEqual(
            configuracion.hosts_permitidos,
            ("mcp.ejemplo.test", "mcp.ejemplo.test:*"),
        )

    async def test_rotacion_rechaza_el_token_anterior(self) -> None:
        """Demuestra que sustituir el verificador revoca la credencial previa."""
        token_anterior = "token-anterior-123456789012345678901"
        token_nuevo = "token-nuevo-12345678901234567890123"
        verificador = VerificadorBearerPersonal(token_nuevo)
        self.assertIsNone(await verificador.verify_token(token_anterior))
        self.assertIsNotNone(await verificador.verify_token(token_nuevo))


if __name__ == "__main__":
    unittest.main()
