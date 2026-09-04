"""Ejecuta una prueba de humo sobre Streamable HTTP autenticado."""

from __future__ import annotations

import asyncio
import socket

import httpx2
import uvicorn
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from codigo_servidor.aplicacion_http import crear_aplicacion
from codigo_servidor.configuracion import ConfiguracionServidor


def reservar_puerto() -> int:
    """Obtiene un puerto local disponible para la prueba aislada."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_local:
        socket_local.bind(("127.0.0.1", 0))
        return int(socket_local.getsockname()[1])


async def esperar_inicio(servidor: uvicorn.Server) -> None:
    """Espera un inicio acotado y falla si el proceso no queda disponible."""
    for _ in range(100):
        if servidor.started:
            return
        await asyncio.sleep(0.05)
    raise RuntimeError("El servidor HTTP no inicio dentro del plazo")


async def ejecutar() -> None:
    """Comprueba salud, rechazo anonimo y una invocacion MCP autenticada."""
    puerto = reservar_puerto()
    token = "token-piloto-local-12345678901234567890"
    url_base = f"http://127.0.0.1:{puerto}"
    aplicacion = crear_aplicacion(
        ConfiguracionServidor(
            token_bearer=token,
            url_emisor="https://autenticacion.invalid",
            url_recurso=f"{url_base}/mcp",
            hosts_permitidos=("127.0.0.1", "127.0.0.1:*"),
        )
    )
    configuracion_uvicorn = uvicorn.Config(
        aplicacion,
        host="127.0.0.1",
        port=puerto,
        log_level="error",
    )
    servidor = uvicorn.Server(configuracion_uvicorn)
    tarea_servidor = asyncio.create_task(servidor.serve())
    try:
        await esperar_inicio(servidor)
        async with httpx2.AsyncClient() as cliente_http:
            salud = await cliente_http.get(f"{url_base}/salud")
            assert salud.status_code == 200
            anonimo = await cliente_http.get(f"{url_base}/mcp")
            assert anonimo.status_code == 401
            invalido = await cliente_http.get(
                f"{url_base}/mcp",
                headers={"Authorization": "Bearer token-invalido"},
            )
            assert invalido.status_code == 401
            host_bloqueado = await cliente_http.get(
                f"{url_base}/mcp",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Host": "malicioso.invalid",
                },
            )
            assert host_bloqueado.status_code == 421
            cuerpo_excesivo = await cliente_http.post(
                f"{url_base}/mcp",
                headers={"Authorization": f"Bearer {token}"},
                content="x" * 1_048_577,
            )
            assert cuerpo_excesivo.status_code == 413

        async with httpx2.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=httpx2.Timeout(10.0, read=30.0),
            follow_redirects=True,
        ) as cliente_http_autenticado:
            transporte = streamable_http_client(
                f"{url_base}/mcp",
                http_client=cliente_http_autenticado,
            )
            async with Client(transporte) as cliente_mcp:
                listado = await cliente_mcp.list_tools()
                assert {tool.name for tool in listado.tools} == {
                    "consultar_contador",
                    "incrementar_contador",
                }
                resultado = await cliente_mcp.call_tool(
                    "incrementar_contador",
                    {
                        "contador_id": "remoto",
                        "cantidad": 5,
                        "clave_idempotencia": "humo-http-1",
                    },
                )
                assert resultado.structured_content is not None
                assert resultado.structured_content["valor"] == 5
                assert cliente_mcp.protocol_version == "2026-07-28"
    finally:
        servidor.should_exit = True
        await tarea_servidor


if __name__ == "__main__":
    asyncio.run(ejecutar())
