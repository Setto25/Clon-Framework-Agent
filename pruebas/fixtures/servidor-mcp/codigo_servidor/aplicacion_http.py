"""Compone el servidor MCP como una aplicacion ASGI desplegable."""

from __future__ import annotations

from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import AnyHttpUrl
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from codigo_servidor.adaptador_mcp import crear_servidor_mcp
from codigo_servidor.autenticacion import VerificadorBearerPersonal
from codigo_servidor.configuracion import ConfiguracionServidor
from codigo_servidor.dominio import AlmacenContadoresMemoria, AutorizadorContadores, ServicioContadores
from codigo_servidor.identidades import ProveedorIdentidadHttp


def crear_aplicacion(configuracion: ConfiguracionServidor) -> Starlette:
    """Compone dominio, autenticacion, MCP y transporte sin acoplar sus contratos."""
    servicio = ServicioContadores(AlmacenContadoresMemoria(), AutorizadorContadores())
    autenticacion = AuthSettings(
        issuer_url=AnyHttpUrl(configuracion.url_emisor),
        resource_server_url=AnyHttpUrl(configuracion.url_recurso),
        required_scopes=["contadores:leer"],
    )
    servidor = crear_servidor_mcp(
        servicio=servicio,
        identidades=ProveedorIdentidadHttp(),
        verificador_token=VerificadorBearerPersonal(configuracion.token_bearer),
        configuracion_auth=autenticacion,
    )

    @servidor.custom_route("/salud", methods=["GET"])
    async def salud(_: Request) -> JSONResponse:
        """Informa vida del proceso sin revelar configuracion privada."""
        return JSONResponse({"estado": "disponible"})

    seguridad_transporte = TransportSecuritySettings(
        allowed_hosts=list(configuracion.hosts_permitidos),
        allowed_origins=[],
    )
    return servidor.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        max_request_body_size=configuracion.maximo_cuerpo_bytes,
        transport_security=seguridad_transporte,
    )
