"""Ejecuta el recorrido HTTP contra un contenedor o servicio desplegado."""

from __future__ import annotations

import asyncio
import os

from pruebas.probar_http_local import probar_endpoint


def cargar_variable(nombre: str) -> str:
    """Obtiene una variable obligatoria sin incorporar valores predeterminados."""
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise RuntimeError(f"{nombre} debe estar configurada")
    return valor


async def ejecutar() -> None:
    """Valida el endpoint y la credencial entregados por el entorno."""
    url_base = cargar_variable("MCP_URL_PRUEBA").rstrip("/")
    token = cargar_variable("MCP_TOKEN_PRUEBA")
    await probar_endpoint(url_base, token)


if __name__ == "__main__":
    asyncio.run(ejecutar())
