"""Publica los casos de uso mediante contratos MCP tipados."""

from __future__ import annotations

from mcp.server import MCPServer
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, ConfigDict, Field

from codigo_servidor.dominio import (
    ErrorAutorizacion,
    ErrorConflictoIdempotencia,
    ErrorEntrada,
    EstadoContador,
    ServicioContadores,
)
from codigo_servidor.identidades import ProveedorIdentidad


class SalidaContador(BaseModel):
    """Define la salida estructurada comun de las Tools."""

    model_config = ConfigDict(extra="forbid")

    contador_id: str
    valor: int
    operacion_id: str | None = None
    repetida: bool = False


def convertir_salida(estado: EstadoContador) -> SalidaContador:
    """Convierte el dominio en el contrato publico sin filtrar objetos internos."""
    return SalidaContador(
        contador_id=estado.contador_id,
        valor=estado.valor,
        operacion_id=estado.operacion_id,
        repetida=estado.repetida,
    )


def crear_servidor_mcp(
    servicio: ServicioContadores,
    identidades: ProveedorIdentidad,
    verificador_token: TokenVerifier | None = None,
    configuracion_auth: AuthSettings | None = None,
) -> MCPServer:
    """Crea el adaptador MCP con autenticacion HTTP opcional e inyectable."""
    servidor = MCPServer(
        name="piloto-contadores",
        version="0.1.0",
        token_verifier=verificador_token,
        auth=configuracion_auth,
    )

    @servidor.tool(name="consultar_contador", title="Consultar contador")
    def consultar_contador(
        contador_id: str = Field(min_length=1, max_length=64),
    ) -> SalidaContador:
        """Consulta el valor actual de un contador autorizado."""
        try:
            return convertir_salida(servicio.consultar(contador_id, identidades.obtener()))
        except (ErrorAutorizacion, ErrorEntrada) as error:
            raise ToolError(str(error)) from error

    @servidor.tool(name="incrementar_contador", title="Incrementar contador")
    def incrementar_contador(
        contador_id: str = Field(min_length=1, max_length=64),
        cantidad: int = Field(ge=1, le=100),
        clave_idempotencia: str = Field(min_length=1, max_length=128),
    ) -> SalidaContador:
        """Incrementa una sola vez mediante una clave idempotente."""
        try:
            estado = servicio.incrementar(
                contador_id,
                cantidad,
                clave_idempotencia,
                identidades.obtener(),
            )
            return convertir_salida(estado)
        except (ErrorAutorizacion, ErrorEntrada, ErrorConflictoIdempotencia) as error:
            raise ToolError(str(error)) from error

    return servidor
